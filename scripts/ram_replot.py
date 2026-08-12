# Rebuild the RAM-setting figure from the saved curves, without retraining
# (same pattern as scripts/cvar_alpha_trend.py).  Run ram_cvar_vs_fedavot.py first.
#
# The one plotting subtlety: at R = 1 FedAVOT and FedAvg-relay are the SAME run (a
# singleton batch has one transport weight and it is 1), so the two curves lie exactly
# on top of each other.  FedAVOT is drawn dashed so the coincidence is visible instead
# of looking like a missing curve.
import numpy as np
import matplotlib.pyplot as plt

ROUNDS = 1500
TAIL = 300
RELAY_SIZES = [1, 3, 6]
CVAR_CONFIGS = [(0.3, 0.3), (0.1, 0.1)]
NEUTRAL = (1.0, 1.0)
METHODS = ('fedavg_relay', 'fedcvar_relay', 'fedavot', 'fedavot_cvar', 'ht_relay')
STYLE = {'fedavg_relay': ("FedAvg (RAM relay)", "tab:orange", "-"),
         'fedcvar_relay': ("FED-CVaR-AVG (theirs)", "tab:purple", "-"),
         'fedavot': ("FedAVOT", "tab:blue", "--"),
         'fedavot_cvar': ("FedAVOT + CVaR", "tab:green", "-"),
         'ht_relay': ("Horvitz--Thompson relay", "tab:brown", "-")}

d = np.load(f"data/ram_cvar_vs_fedavot_{ROUNDS}rounds.npz")
EVAL_EVERY = int(d["eval_every"])
NEV = TAIL // EVAL_EVERY
full = d["full"]


def curve(R, a, g, m, col):
    return d[f"R{R}_a{a}_g{g}_{m}"][:, :, col].mean(axis=0)


def tail(R, a, g, m, col):
    return d[f"R{R}_a{a}_g{g}_{m}"][:, -NEV:, col].mean()


x = np.arange(0, ROUNDS, EVAL_EVERY)
fig, axes = plt.subplots(2, len(RELAY_SIZES), figsize=(5.2*len(RELAY_SIZES), 8),
                         sharex=True)
for col, R in enumerate(RELAY_SIZES):
    best = {m: max(CVAR_CONFIGS, key=lambda cg: tail(R, *cg, m, 1))
            for m in ('fedcvar_relay', 'fedavot_cvar')}
    for row, (ylab, ci) in enumerate((("Rare-digit test accuracy (8,9)", 1),
                                      ("Overall test accuracy", 0))):
        ax = axes[row, col]
        ax.plot(x, full[:, :, ci].mean(axis=0), color="tab:red", lw=1.6,
                label="FedAvg (full participation)")
        for m in METHODS:
            risk = m in ('fedcvar_relay', 'fedavot_cvar')
            a, g = best[m] if risk else NEUTRAL
            label, color, ls = STYLE[m]
            if risk:
                label += f" (α={a}, γ={g})"
            ax.plot(x, curve(R, a, g, m, ci), color=color, lw=1.5, ls=ls, label=label)
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
             "exclusively; 1500 rounds, 3 seeds)", fontsize=13)
fig.tight_layout()
fig.savefig(f"figures/2026-07-27_ram_study/ram_cvar_vs_fedavot_{ROUNDS}rounds.png", dpi=140,
            bbox_inches="tight")
fig.savefig(f"figures/2026-07-27_ram_study/ram_cvar_vs_fedavot_{ROUNDS}rounds.pdf", bbox_inches="tight")
print(f"saved figures/2026-07-27_ram_study/ram_cvar_vs_fedavot_{ROUNDS}rounds.png/.pdf")

# ---------------------------------------------------------------
# Companion figure: the two metrics disagree, and that is the whole story.
# Rare-group accuracy (their metric) vs p-weighted training loss (our objective).
# ---------------------------------------------------------------
fig2, axes2 = plt.subplots(1, 2, figsize=(12.5, 4.8))
Rs = np.array(RELAY_SIZES)
SERIES = [('fedavg_relay', NEUTRAL), ('fedcvar_relay', (0.1, 0.1)),
          ('fedavot', NEUTRAL), ('fedavot_cvar', (0.1, 0.1)), ('ht_relay', NEUTRAL)]
for ax, (ci, ylab, ttl) in zip(axes2, (
        (1, "Rare-digit test accuracy (8,9)", "Their metric: performance on the\nrare "
            "users' patterns  (higher is better)"),
        (2, "p-weighted training loss", "Our objective: $F_p$ with uniform $p$\n"
            "(lower is better)"))):
    for m, (a, g) in SERIES:
        label, color, ls = STYLE[m]
        if (a, g) != NEUTRAL:
            label += f" (α={a}, γ={g})"
        ax.plot(Rs, [tail(R, a, g, m, ci) for R in Rs], marker="o", color=color, ls=ls,
                lw=1.8, label=label)
    ax.axhline(full[:, -NEV:, ci].mean(), color="tab:red", ls=":", lw=1.8,
               label="FedAvg (full participation)")
    ax.axvline(6, color="tab:green", ls=":", lw=1.4)
    ax.annotate("transport\nfeasible", xy=(6, 0.98), xycoords=("data", "axes fraction"),
                ha="right", va="top", fontsize=8, color="tab:green")
    ax.set_xlabel("users relayed per round $R$"); ax.set_ylabel(ylab)
    ax.set_title(ttl, fontsize=11); ax.grid(alpha=0.3); ax.set_xticks(Rs)
axes2[0].legend(fontsize=8, loc="lower right")
fig2.suptitle("Adding CVaR helps the rare-group metric and hurts the p-weighted "
              "objective: both results are real", fontsize=12.5)
fig2.tight_layout()
fig2.savefig(f"figures/2026-07-27_ram_study/ram_metric_disagreement_{ROUNDS}rounds.png", dpi=140,
             bbox_inches="tight")
fig2.savefig(f"figures/2026-07-27_ram_study/ram_metric_disagreement_{ROUNDS}rounds.pdf", bbox_inches="tight")
print(f"saved figures/2026-07-27_ram_study/ram_metric_disagreement_{ROUNDS}rounds.png/.pdf")
