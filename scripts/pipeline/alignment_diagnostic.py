# Pre-training alignment diagnostic for the four sweep cells (Herlock's 2026-09-14 ask).
#
# For each (dataset, regime) cell the sweep already cached the transport plan
# (results/<sweep>/transport_<dataset>_<regime>_K3.npz: q, Wcols, pi, p, r). From it:
#
#   p_hat_i   = sum_j q_j * W[i, j]      expected per-round weight FedAVOT gives user i
#                                        (== p when IPFP converged; the stalled surrogate otherwise)
#   p_tilde_i = pi_i / K                 expected per-round weight of uniform-over-K averaging
#
# Criterion (paper Sec. 3): transport helps iff ||p - p_hat||_1 < ||p - p_tilde||_1.
# We report both norms, the predicted sign, the observed sign from summary.csv, and the exact
# loss floors F_p(theta*_w) each rule converges toward (closed-form LS on IMDb-Wiki; Newton
# weighted logistic on Adult), so bias and variance can be separated.
#
# No training. Runs in ~1 minute.  Usage: .venv/Scripts/python.exe scripts/pipeline/alignment_diagnostic.py
import os, sys, csv, statistics as st
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import run_experiments as RE

SWEEP = "results/2026-08-10_main_sweep"
OUT = "results/2026-09-14_alignment_diagnostic"
CELLS = [("adult", "feasible"), ("adult", "infeasible"), ("imdbwiki", "feasible"), ("imdbwiki", "infeasible")]

def floor_mse(data, w):
    X, y, S = data["X_all"], data["y_all"], data["S"]
    A = np.einsum('n,nsd,nse->de', w, X, X) / S
    b = np.einsum('n,nsd,ns->d', w, X, y) / S
    th = np.linalg.solve(A + 1e-9 * np.eye(data["D"]), b)
    return ((np.einsum('nsd,d->ns', X, th) - y) ** 2).mean(1)

def floor_ce(data, w, iters=60):
    X, y, S, D = data["X_all"], data["y_all"], data["S"], data["D"]
    th = np.zeros(D)
    for _ in range(iters):
        z = np.einsum('nsd,d->ns', X, th); s = 1 / (1 + np.exp(-z))
        g = np.einsum('n,nsd,ns->d', w, X, s - y) / S + 1e-6 * th
        H = np.einsum('n,ns,nsd,nse->de', w, s * (1 - s), X, X) / S + 1e-6 * np.eye(D)
        step = np.linalg.solve(H, g); th -= step
        if np.abs(step).max() < 1e-9: break
    z = np.einsum('nsd,d->ns', X, th)
    return (np.logaddexp(0, z) - y * z).mean(1)

def observed(dataset, regime):
    rows = [r for r in csv.DictReader(open(os.path.join(SWEEP, "summary.csv")))
            if r["dataset"] == dataset and r["regime"] == regime]
    m = lambda model: st.mean(float(r["overall_tail"]) for r in rows if r["model"] == model)
    return m("fedavot"), m("fedavg"), m("full")


def cell_marginals(transport_npz, N, K):
    """(p, pi, p_hat, p_tilde, infeasible-mass) from a cached transport plan."""
    z = np.load(transport_npz)
    p, pi, q, W = z["p"], z["pi"], z["q"], z["Wcols"]
    subs0 = np.array(RE.all_K_subsets_1based(N, K), dtype=np.int64) - 1
    p_hat = np.bincount(subs0.ravel(), weights=(q[:, None] * W).ravel(), minlength=N)
    return p, pi, p_hat, pi / K, float(p[p > pi].sum())

def cell_floors(data, p, p_hat, p_tilde):
    fl = floor_mse if data["task"] == "mse" else floor_ce
    return {name: float(p @ fl(data, w)) for name, w in
            [("fedavot", p_hat), ("fedavg", p_tilde / p_tilde.sum()), ("full", p)]}

def main():
    os.makedirs(OUT, exist_ok=True)
    args = RE.parse_args([])
    N, K = args.num_users, args.k
    loaded = {}
    out_rows = []
    print(f"{'cell':22s} {'#inf':>4} {'inf-mass':>8} {'|p-phat|':>8} {'|p-ptil|':>8} {'pred':>6} {'obs':>6} | "
          f"{'floor OT':>9} {'floor unif':>10} {'floor full':>10} | {'meas OT':>9} {'meas unif':>9} {'meas full':>9}")
    for ds, reg in CELLS:
        if ds not in loaded:
            loaded[ds] = RE.load_imdbwiki(args) if ds == "imdbwiki" else RE.load_adult(args)
        data = loaded[ds]
        z = np.load(os.path.join(SWEEP, f"transport_{ds}_{reg}_K{K}.npz"))
        p, pi, q, W = z["p"], z["pi"], z["q"], z["Wcols"]
        subs0 = np.array(RE.all_K_subsets_1based(N, K), dtype=np.int64) - 1
        p_hat = np.bincount(subs0.ravel(), weights=(q[:, None] * W).ravel(), minlength=N)
        p_til = pi / K
        l1_hat, l1_til = np.abs(p - p_hat).sum(), np.abs(p - p_til).sum()
        infeas = p > pi
        fl = floor_mse if data["task"] == "mse" else floor_ce
        F = {name: p @ fl(data, w) for name, w in [("ot", p_hat), ("unif", p_til / p_til.sum()), ("full", p)]}
        mo, mu, mf = observed(ds, reg)
        pred = "helps" if l1_hat < l1_til else "hurts"
        obs = "helps" if mo < mu else "hurts"
        print(f"{ds+'/'+reg:22s} {infeas.sum():4d} {p[infeas].sum():8.3f} {l1_hat:8.4f} {l1_til:8.4f} {pred:>6} {obs:>6} | "
              f"{F['ot']:9.4f} {F['unif']:10.4f} {F['full']:10.4f} | {mo:9.4f} {mu:9.4f} {mf:9.4f}")
        out_rows.append(dict(dataset=ds, regime=reg, n_infeasible=int(infeas.sum()), infeasible_mass=p[infeas].sum(),
                             l1_p_phat=l1_hat, l1_p_ptilde=l1_til, predicted=pred, observed=obs,
                             floor_fedavot=F["ot"], floor_uniform=F["unif"], floor_full=F["full"],
                             measured_fedavot=mo, measured_uniform=mu, measured_full=mf, ipfp_row_err=float(z["row_err"])))
        np.savez(os.path.join(OUT, f"marginals_{ds}_{reg}.npz"), p=p, pi=pi, p_hat=p_hat, p_tilde=p_til)
    with open(os.path.join(OUT, "alignment_diagnostic.csv"), "w", newline="") as f:
        wr = csv.DictWriter(f, fieldnames=list(out_rows[0])); wr.writeheader(); wr.writerows(out_rows)
    print(f"\nsaved {OUT}/alignment_diagnostic.csv and marginals_*.npz")

if __name__ == "__main__":
    main()
