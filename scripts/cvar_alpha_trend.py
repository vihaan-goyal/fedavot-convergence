# Trend figure for the CVaR study: final loss vs risk level alpha, INFEASIBLE regime.
# Built entirely from saved run data (grid npz + alpha=0.9 npz + alpha=0.3 5-seed npz),
# no retraining. Shows both aggregation schemes improving monotonically as the CVaR
# hinge is turned OFF (alpha -> 1): the gains were from uniform averaging, not CVaR.
import numpy as np
import matplotlib.pyplot as plt

TAIL = 500
grid = np.load("data/imdbwiki_cvar_grid_K3_4000rounds.npz")          # 3 seeds, gamma=0.3 series
a03  = np.load("data/imdbwiki_cvar_K3_4000rounds_curves.npz")        # 5 seeds, alpha=0.3
a09  = np.load("data/imdbwiki_cvar_a09_K3_4000rounds_curves.npz")    # 5 seeds, alpha=0.9

def tail_stats(curves):
    per_seed = [np.mean(c[-TAIL:]) for c in curves]
    return np.mean(per_seed), np.std(per_seed)

ALPHAS_GRID = [0.1, 0.2, 0.3, 0.5]
series = {}
for v in ('cvar_avot', 'cvar_unif'):
    xs, ys, es = [], [], []
    for a in ALPHAS_GRID:                                  # gamma=0.3 column of the grid
        o = grid[f"{v}_a{a}_g0.3_overall"]
        xs.append(a); ys.append(np.mean(o)); es.append(np.std(o))
    m, s = tail_stats(a09[v])                              # alpha=gamma=0.9 bookend
    xs.append(0.9); ys.append(m); es.append(s)
    series[v] = (xs, ys, es)

avot_m, avot_s = tail_stats(a09['avot'])                   # risk-neutral baselines (5 seeds)
full_m, _ = tail_stats(a09['full'])

fig, ax = plt.subplots(figsize=(8, 5.5))
ax.axhline(avot_m, color="tab:blue", lw=1.6, ls="--", label=f"FedAVOT (risk-neutral), {avot_m:.1f}")
ax.axhline(full_m, color="tab:red", lw=1.6, ls="--", label=f"FedAvg (full), {full_m:.1f}")
STYLE = {'cvar_avot': ("CVaR + transport aggregation", "tab:green"),
         'cvar_unif': ("CVaR + uniform aggregation", "tab:purple")}
for v, (label, color) in STYLE.items():
    xs, ys, es = series[v]
    ax.errorbar(xs, ys, yerr=es, marker="o", color=color, lw=1.8, capsize=3, label=label)
ax.set_xlabel("CVaR risk level α  (α→1 = risk-neutral; γ=0.3, last point α=γ=0.9)")
ax.set_ylabel(f"Final global p-weighted MSE (tail-{TAIL})")
ax.set_title("Infeasible IMDb-Wiki regime: turning CVaR OFF helps both schemes\n"
             "(more risk-aversion = worse; uniform averaging, not the hinge, is the win)")
ax.set_ylim(80, 132)
ax.grid(alpha=0.3); ax.legend(fontsize=9, loc="upper right")
fig.savefig("figures/imdbwiki_cvar_alpha_trend.png", dpi=140, bbox_inches="tight")
fig.savefig("figures/imdbwiki_cvar_alpha_trend.pdf", bbox_inches="tight")
print("saved figures/imdbwiki_cvar_alpha_trend.png")
