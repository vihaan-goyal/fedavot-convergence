# FED-CVaR-AVG (arXiv:2309.14176, "Federated Learning Under Restricted User
# Availability") vs FedAVOT, run in THEIR setting rather than ours.
#
# Their setup, ported from github.com/PeriklisTheodoropoulos/risk-aware-FL
# ("script for Mnist.py"):
#   * N = 30 users, MNIST.  The 27 most-available users share digits 0-7; the 3 least
#     available users hold digits 8,9 EXCLUSIVELY.
#   * A Random Access Model (RAM) relays R = users_per_round user models to the server
#     each round.  Their published value is R = 1: the server simply broadcasts the one
#     selected user's (theta, t) as the new global model -- there is no aggregation.
#   * Local objective per user (their Algorithm 1):
#       G_i(theta,t) = (1-g) t + ((1-g)/a) [f_i(theta) - t]_+ + g f_i(theta)
#     giving gradient scaling coef = ((1-g)/a) 1{f_i > t} + g on theta, and
#     t <- t - eta_t (1-g)(1 - 1{f_i > t}/a).
#   * Metric: overall test accuracy AND accuracy on the rare users' exclusive patterns.
#
# The point of the sweep over R: at R = 1 the FedAVOT transport has no degrees of
# freedom (a singleton batch's normalized weight is 1), so FedAVOT is exactly
# FedAvg-relay and only CVaR can move anything.  As R grows the transport gains room
# and, once R >= 6 here, can hit the uniform target p_i = 1/N exactly (feasibility
# p_i <= pi_i; see scripts/ram_feasibility_diagnostic.py).  So the two mechanisms are
# not competing -- they act on different axes (across rounds vs within a round), and
# which one wins is decided by R.
#
# Deviations from their code, all noted so they can be defended on the call:
#   * model: multinomial logistic regression on 64 PCA features, not their (128,128)
#     MLP.  Keeps the comparison convex and lets us run a full grid x 3 seeds in numpy.
#   * H local FULL-BATCH steps on SAMPLES_PER_USER examples instead of minibatch epochs.
#   * their user_probs is unseeded np.random.rand(30); we fix the seed whose tail
#     matches the probabilities quoted in their Table 1 (0.0107/0.0078/0.0053).
import numpy as np
import matplotlib.pyplot as plt
import time
import sys

# ================================================================
# Config
# ================================================================
NUM_USERS = 30
N_RARE = 3                       # their k = int(K*0.1)
RARE_DIGITS = [8, 9]             # their label_subset_2
FREQ_DIGITS = [0, 1, 2, 3, 4, 5, 6, 7]   # their label_subset_1
RAM_SEED = 2517                  # tail matches their Table 1 (see diagnostic script)

RELAY_SIZES = [1, 3, 6]          # their users_per_round, generalized
CVAR_CONFIGS = [(0.3, 0.3), (0.1, 0.1)]   # (alpha, gamma): their MNIST setting, their best
NEUTRAL = (1.0, 1.0)             # alpha = gamma = 1 reduces Algorithm 1 to FedAvg

PCA_DIM = 64
SAMPLES_PER_USER = 256
ROUNDS = 1500
LOCAL_STEPS = 5                  # their H
LR = 0.1
LR_T = 0.01                      # their eta_t : eta_theta ratio is 1:10
SEEDS = [0, 1, 2]
EVAL_EVERY = 10
TAIL = 300                       # rounds averaged for the final numbers
MC_SUBSETS = 200_000
FIT_ITERS = 400
FIT_TOL = 1e-10
CAP = 1e6                        # divergence guard on the loss

if "--smoke" in sys.argv:        # fast shape/learning check, not a result
    ROUNDS, SEEDS, EVAL_EVERY, TAIL = 100, [0], 10, 50
    RELAY_SIZES, CVAR_CONFIGS = [1, 6], [(0.1, 0.1)]
    MC_SUBSETS = 50_000


# ================================================================
# RAM + transport (duplicated from ram_feasibility_diagnostic.py, repo convention)
# ================================================================
def make_ram_probs(n, seed):
    rng = np.random.RandomState(seed)
    probs = rng.rand(n)
    probs = probs / probs.sum()
    return probs[np.argsort(probs)[::-1]]          # descending; last N_RARE = rarest


def draw_subsets(r, n, k, samples, rng):
    out = np.empty((samples, k), dtype=np.int64)
    done = 0
    while done < samples:
        b = min(50_000, samples - done)
        g = rng.gumbel(size=(b, n)) + np.log(r)[None, :]
        out[done:done+b] = np.argpartition(-g, min(k, n-1), axis=1)[:, :k]
        done += b
    return out


def subset_weights(log_u, draws):
    ls = log_u[draws]
    ls = ls - ls.max(axis=1, keepdims=True)
    e = np.exp(ls)
    return e / e.sum(axis=1, keepdims=True)


def fit_transport(p, draws, n, iters=FIT_ITERS, tol=FIT_TOL):
    """Enumeration-free masked IPFP: the plan has product form, so it is fixed by the
    N-vector log u with w_i(S) = softmax_S(log u).  Runs in log space because log u
    diverges for starved users under infeasibility."""
    m = draws.shape[0]
    flat = draws.ravel()
    log_p = np.log(p)
    log_u = np.zeros(n)
    p_hat, row_err, prev = np.zeros(n), np.inf, np.inf
    for _ in range(iters):
        w = subset_weights(log_u, draws)
        p_hat = np.bincount(flat, weights=w.ravel(), minlength=n) / m
        row_err = np.max(np.abs(p_hat - p))
        if row_err < tol or abs(prev - row_err) < 1e-15:
            break
        prev = row_err
        log_u += log_p - np.log(np.maximum(p_hat, 1e-300))
        log_u -= log_u.mean()
    return log_u, p_hat, row_err


# ================================================================
# Data: their heterogeneous split
# ================================================================
def load_data():
    d = np.load("data/mnist_cache.npz")
    Xtr, ytr = d["X_train"].astype(np.float64) / 255.0, d["y_train"]
    Xte, yte = d["X_test"].astype(np.float64) / 255.0, d["y_test"]
    mu = Xtr.mean(axis=0)
    Xtr -= mu; Xte -= mu
    # PCA (top PCA_DIM components of the training set)
    cov = Xtr.T @ Xtr / Xtr.shape[0]
    evals, evecs = np.linalg.eigh(cov)
    V = evecs[:, -PCA_DIM:][:, ::-1]
    Xtr, Xte = Xtr @ V, Xte @ V
    s = Xtr.std(axis=0)
    Xtr /= s; Xte /= s
    # bias feature
    Xtr = np.hstack([Xtr, np.ones((Xtr.shape[0], 1))])
    Xte = np.hstack([Xte, np.ones((Xte.shape[0], 1))])
    return Xtr, ytr, Xte, yte


def split_users(Xtr, ytr, rng):
    """27 frequent users draw from digits 0-7, 3 rare users from digits 8,9."""
    freq_idx = np.where(np.isin(ytr, FREQ_DIGITS))[0]
    rare_idx = np.where(np.isin(ytr, RARE_DIGITS))[0]
    rng.shuffle(freq_idx); rng.shuffle(rare_idx)
    Xu = np.empty((NUM_USERS, SAMPLES_PER_USER, Xtr.shape[1]))
    yu = np.empty((NUM_USERS, SAMPLES_PER_USER), dtype=np.int64)
    n_freq = NUM_USERS - N_RARE
    for i in range(n_freq):
        sel = freq_idx[i*SAMPLES_PER_USER:(i+1)*SAMPLES_PER_USER]
        Xu[i], yu[i] = Xtr[sel], ytr[sel]
    for j in range(N_RARE):
        sel = rare_idx[j*SAMPLES_PER_USER:(j+1)*SAMPLES_PER_USER]
        Xu[n_freq+j], yu[n_freq+j] = Xtr[sel], ytr[sel]
    return Xu, yu


# ================================================================
# Model: multinomial logistic regression, all users trained in parallel
# ================================================================
N_CLASS = 10


def softmax(z):
    z = z - z.max(axis=-1, keepdims=True)
    e = np.exp(z)
    return e / e.sum(axis=-1, keepdims=True)


def local_train(theta, Xu, Yu1h, t, alpha, gamma, steps=LOCAL_STEPS):
    """One round of local training for ALL users from the same broadcast theta.
    Returns (W, t_new, f0) where f0 is each user's loss at the broadcast point.
    alpha == 1 and gamma == 1 both reduce this to plain FedAvg local training."""
    n, S, _ = Xu.shape
    W = np.repeat(theta[None, :, :], n, axis=0)
    tv = t.copy()
    f0 = None
    for _ in range(steps):
        P = softmax(np.einsum('nsd,ndc->nsc', Xu, W))
        f = -np.log(np.maximum((P * Yu1h).sum(axis=-1), 1e-300)).mean(axis=1)
        if f0 is None:
            f0 = f
        active = (f > tv).astype(float)
        coef = (1.0 - gamma) / alpha * active + gamma
        grad = np.einsum('nsd,nsc->ndc', Xu, (P - Yu1h)) / S
        W = W - LR * coef[:, None, None] * grad
        tv = tv - LR_T * (1.0 - gamma) * (1.0 - active / alpha)
    return W, tv, f0


def evaluate(theta, Xte, yte, rare_mask):
    pred = np.einsum('sd,dc->sc', Xte, theta).argmax(axis=1)
    return (pred == yte).mean(), (pred[rare_mask] == yte[rare_mask]).mean()


def train_loss(theta, Xu, Yu1h, p):
    P = softmax(np.einsum('nsd,dc->nsc', Xu, theta))
    f = -np.log(np.maximum((P * Yu1h).sum(axis=-1), 1e-300)).mean(axis=1)
    return float(p @ f), f


# ================================================================
# Setup
# ================================================================
r = make_ram_probs(NUM_USERS, RAM_SEED)
p = np.full(NUM_USERS, 1.0 / NUM_USERS)
rare_users = np.arange(NUM_USERS - N_RARE, NUM_USERS)

Xtr, ytr, Xte, yte = load_data()
rare_mask = np.isin(yte, RARE_DIGITS)
DIM = Xtr.shape[1]
print(f"data: {Xtr.shape[0]} train / {Xte.shape[0]} test, {DIM-1} PCA dims + bias; "
      f"rare digits {RARE_DIGITS} = {rare_mask.sum()} test samples")
print(f"RAM: 3 rarest availabilities {np.sort(r)[:3].round(4)} "
      f"(their Table 1: 0.0107/0.0078/0.0053)\n")

# transport plan (and inclusion probabilities, for the HT baseline) per relay size
plans, PI = {}, {}
for R in RELAY_SIZES:
    draws = draw_subsets(r, NUM_USERS, R, MC_SUBSETS, np.random.RandomState(1))
    log_u, p_hat, err = fit_transport(p, draws, NUM_USERS)
    plans[R] = log_u
    PI[R] = np.bincount(draws.ravel(), minlength=NUM_USERS) / draws.shape[0]
    infeas = (p > p_hat + 1e-6).sum()
    print(f"R={R}: IPFP row_err {err:.1e}, ||p-p_hat||_1 = {np.abs(p-p_hat).sum():.4f}, "
          f"{infeas} users under target, rare-user achieved weight "
          f"{p_hat[rare_users].mean():.4f} (target {1/NUM_USERS:.4f})")
print()

METHODS = ('fedavg_relay', 'fedcvar_relay', 'fedavot', 'fedavot_cvar', 'ht_relay')
# FedAVOT is dashed because at R=1 it coincides exactly with FedAvg-relay and would
# otherwise hide it.  scripts/ram_replot.py rebuilds these figures from the saved npz.
STYLE = {'fedavg_relay': ("FedAvg (RAM relay)", "tab:orange", "-"),
         'fedcvar_relay': ("FED-CVaR-AVG (theirs)", "tab:purple", "-"),
         'fedavot': ("FedAVOT", "tab:blue", "--"),
         'fedavot_cvar': ("FedAVOT + CVaR", "tab:green", "-"),
         'ht_relay': ("Horvitz--Thompson relay", "tab:brown", "-")}

# The Horvitz--Thompson baseline is the unbiased-but-unbounded importance correction,
# theta <- theta + sum_{i in S} (p_i/pi_i)(theta_i - theta).  Unlike the transport it DOES
# have something to do at R=1 (it rescales across rounds instead of within a round) --
# at the price of weights above 1 exactly when p_i > pi_i.

results = {}     # (R, alpha, gamma, method) -> dict of per-seed final metrics
curves = {}      # (R, alpha, gamma, method) -> (seeds, n_eval, 3) array
full_curves = []

t_start = time.time()
for seed in SEEDS:
    rng = np.random.RandomState(seed)
    Xu, yu = split_users(Xtr, ytr, rng)
    Yu1h = np.eye(N_CLASS)[yu]
    draw_seq = draw_subsets(r, NUM_USERS, max(RELAY_SIZES), ROUNDS,
                            np.random.RandomState(1000 + seed))

    # full-participation reference (p-weighted average over all users), once per seed
    theta_f = np.zeros((DIM, N_CLASS))
    fc = []
    for rd in range(ROUNDS):
        W, _, _ = local_train(theta_f, Xu, Yu1h, np.zeros(NUM_USERS), 1.0, 1.0)
        theta_f = np.einsum('n,ndc->dc', p, W)
        if rd % EVAL_EVERY == 0:
            acc, racc = evaluate(theta_f, Xte, yte, rare_mask)
            fc.append((acc, racc, train_loss(theta_f, Xu, Yu1h, p)[0]))
    full_curves.append(fc)
    print(f"[seed {seed}] FedAvg(full): acc {np.mean([c[0] for c in fc[-TAIL//EVAL_EVERY:]]):.4f} "
          f"rare {np.mean([c[1] for c in fc[-TAIL//EVAL_EVERY:]]):.4f}")

    def run(methods, R, alpha, gamma, sub_seq, w_seq):
        """Train the given methods for ROUNDS rounds on this seed's identical draws."""
        theta = {m: np.zeros((DIM, N_CLASS)) for m in methods}
        tvec = {m: np.zeros(NUM_USERS) for m in methods}
        dead = {m: False for m in methods}
        hist = {m: [] for m in methods}
        for rd in range(ROUNDS):
            S, wS = sub_seq[rd], w_seq[rd]
            for m in methods:
                if dead[m]:
                    if rd % EVAL_EVERY == 0:
                        hist[m].append((0.0, 0.0, CAP))
                    continue
                risk = m in ('fedcvar_relay', 'fedavot_cvar')
                a, g = (alpha, gamma) if risk else (1.0, 1.0)
                W, tnew, _ = local_train(theta[m], Xu, Yu1h, tvec[m], a, g)
                if m == 'ht_relay':
                    ht = p[S] / PI[R][S]                  # unbiased, not convex
                    theta[m] = theta[m] + np.einsum('r,rdc->dc', ht,
                                                    W[S] - theta[m][None, :, :])
                    tvec[m] = np.full(NUM_USERS, tnew[S].mean())
                elif m in ('fedavg_relay', 'fedcvar_relay'):
                    theta[m] = W[S].mean(axis=0)          # RAM relay / uniform over batch
                    tvec[m] = np.full(NUM_USERS, tnew[S].mean())
                else:
                    theta[m] = np.einsum('r,rdc->dc', wS, W[S])   # transport weights
                    tvec[m] = np.full(NUM_USERS, float(wS @ tnew[S]))
                if rd % EVAL_EVERY == 0:
                    tl, _ = train_loss(theta[m], Xu, Yu1h, p)
                    if not np.isfinite(tl) or tl > CAP:
                        dead[m] = True
                        hist[m].append((0.0, 0.0, CAP))
                    else:
                        acc, racc = evaluate(theta[m], Xte, yte, rare_mask)
                        hist[m].append((acc, racc, tl))
        for m in methods:
            curves.setdefault((R, alpha, gamma, m), []).append(hist[m])
        msg = " | ".join(
            f"{m}: acc {np.mean([h[0] for h in hist[m][-TAIL//EVAL_EVERY:]]):.4f} "
            f"rare {np.mean([h[1] for h in hist[m][-TAIL//EVAL_EVERY:]]):.4f}"
            for m in methods)
        print(f"[seed {seed}] R={R} a={alpha} g={gamma} :: {msg}  "
              f"({time.time()-t_start:.0f}s)")

    for R in RELAY_SIZES:
        sub_seq = draw_seq[:, :R]
        w_seq = subset_weights(plans[R], sub_seq)
        # risk-neutral group: alpha = gamma = 1 makes the CVaR methods identical to these
        run(('fedavg_relay', 'fedavot', 'ht_relay'), R, *NEUTRAL, sub_seq, w_seq)
        for (alpha, gamma) in CVAR_CONFIGS:
            run(('fedcvar_relay', 'fedavot_cvar'), R, alpha, gamma, sub_seq, w_seq)

# ================================================================
# Summary
# ================================================================
def tail_mean(key, col):
    c = np.array(curves[key])[:, -TAIL//EVAL_EVERY:, col]
    return c.mean(), c.mean(axis=1).std()


fullm = np.array(full_curves)[:, -TAIL//EVAL_EVERY:, :]
print("\n" + "=" * 96)
print(f"RESULTS: MNIST, {NUM_USERS} users, 3 rare users hold digits {RARE_DIGITS} "
      f"exclusively; {ROUNDS} rounds, {len(SEEDS)} seeds, tail-{TAIL} mean")
print(f"FedAvg(full participation) reference: overall acc {fullm[:,:,0].mean():.4f}, "
      f"rare-digit acc {fullm[:,:,1].mean():.4f}")
print("=" * 96)
def cell(key):
    o, _ = tail_mean(key, 0)
    rr, _ = tail_mean(key, 1)
    tl, _ = tail_mean(key, 2)
    return "DIVERGED".rjust(21) if tl >= CAP else f"{o:9.4f} / {rr:9.4f}"


print(f"{'R':>3} {'alpha':>6} {'gamma':>6} | " + " | ".join(f"{m:>21}" for m in METHODS))
print("(cells: overall acc / rare-digit acc; the two risk-neutral columns do not depend "
      "on alpha,gamma)")
for R in RELAY_SIZES:
    for (a, g) in CVAR_CONFIGS:
        cells = [cell((R, *NEUTRAL, 'fedavg_relay')), cell((R, a, g, 'fedcvar_relay')),
                 cell((R, *NEUTRAL, 'fedavot')), cell((R, a, g, 'fedavot_cvar')),
                 cell((R, *NEUTRAL, 'ht_relay'))]
        print(f"{R:>3} {a:>6} {g:>6} | " + " | ".join(cells))

np.savez(f"data/ram_cvar_vs_fedavot_{ROUNDS}rounds.npz",
         relay_sizes=np.array(RELAY_SIZES), cvar_configs=np.array(CVAR_CONFIGS),
         seeds=np.array(SEEDS), eval_every=EVAL_EVERY, r=r,
         full=np.array(full_curves),
         **{f"R{R}_a{a}_g{g}_{m}": np.array(v)
            for (R, a, g, m), v in curves.items()})

# ================================================================
# Figure: one column per relay size, rare-digit accuracy on top, overall below
# ================================================================
x = np.arange(0, ROUNDS, EVAL_EVERY)
fig, axes = plt.subplots(2, len(RELAY_SIZES), figsize=(5.2*len(RELAY_SIZES), 8),
                         sharex=True)
for col, R in enumerate(RELAY_SIZES):
    # for each risk-aware method show its best (alpha, gamma) by rare-digit accuracy
    best = {m: max(CVAR_CONFIGS, key=lambda cg: tail_mean((R, *cg, m), 1)[0])
            for m in ('fedcvar_relay', 'fedavot_cvar')}
    for row, (ylab, ci) in enumerate((("Rare-digit test accuracy (8,9)", 1),
                                      ("Overall test accuracy", 0))):
        ax = axes[row, col]
        ax.plot(x, np.array(full_curves)[:, :, ci].mean(axis=0), color="tab:red",
                lw=1.6, label="FedAvg (full participation)")
        for m in METHODS:
            risk = m in ('fedcvar_relay', 'fedavot_cvar')
            a, g = best[m] if risk else NEUTRAL
            c = np.array(curves[(R, a, g, m)])[:, :, ci].mean(axis=0)
            label, color, ls = STYLE[m]
            if risk:
                label += f" (α={a}, γ={g})"
            ax.plot(x, c, color=color, lw=1.5, ls=ls, label=label)
        ax.set_ylabel(ylab if col == 0 else "")
        ax.grid(alpha=0.3)
        if row == 0:
            ax.set_title(f"RAM relays R = {R} user{'s' if R > 1 else ''}/round"
                         + ("  (their published setting)" if R == 1 else ""))
            if R == 1:
                ax.annotate("FedAVOT $\\equiv$ FedAvg here:\na singleton batch has one\n"
                            "transport weight, and it is 1",
                            xy=(0.03, 0.04), xycoords="axes fraction", ha="left",
                            va="bottom", fontsize=8.5, color="tab:blue",
                            bbox=dict(boxstyle="round", fc="white", ec="tab:blue",
                                      alpha=0.85))
        if row == 1:
            ax.set_xlabel("Round")
        if col == 0 and row == 0:
            ax.legend(fontsize=8, loc="lower right")
fig.suptitle("FED-CVaR-AVG vs FedAVOT in the restricted-availability setting of "
             "arXiv:2309.14176\n(MNIST, 30 users, 3 rarest users hold digits 8 and 9 "
             "exclusively)", fontsize=13)
fig.tight_layout()
fig.savefig(f"figures/ram_cvar_vs_fedavot_{ROUNDS}rounds.png", dpi=140,
            bbox_inches="tight")
fig.savefig(f"figures/ram_cvar_vs_fedavot_{ROUNDS}rounds.pdf", bbox_inches="tight")
print(f"\nsaved figures/ram_cvar_vs_fedavot_{ROUNDS}rounds.png/.pdf "
      f"and data/ram_cvar_vs_fedavot_{ROUNDS}rounds.npz")
