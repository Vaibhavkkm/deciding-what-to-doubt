"""Figures for the reading report. Reads bench.npz produced by
experiments.py, so figures can be regenerated without re-running the battery."""
import json
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

INK = "#0b0b0b"; INK2 = "#52514e"; MUTED = "#898781"
GRID = "#e1e0d9"; BASE = "#c3c2b7"; SURF = "#ffffff"
S1, S2, S3, S4, S5, S6 = "#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#008300"
CRIT = "#d03b3b"; GOOD = "#0ca30c"

plt.rcParams.update({
    "font.family": "DejaVu Sans", "font.size": 8.5,
    "axes.edgecolor": BASE, "axes.labelcolor": INK2, "axes.titlecolor": INK,
    "axes.titlesize": 9.5, "axes.titleweight": "semibold",
    "axes.spines.top": False, "axes.spines.right": False,
    "xtick.color": MUTED, "ytick.color": MUTED,
    "xtick.labelsize": 8, "ytick.labelsize": 8,
    "grid.color": GRID, "grid.linewidth": 0.6,
    "legend.frameon": False, "legend.fontsize": 8,
    "figure.facecolor": SURF, "axes.facecolor": SURF,
    "savefig.dpi": 300, "savefig.bbox": "tight", "savefig.facecolor": SURF,
})

d = np.load("bench.npz")
FIG = "../figures/"
days = d["t_hours"] / 24.0

# ----------------------------------------------------------------- fig 1
fig, ax = plt.subplots(figsize=(6.6, 2.6))
ax.plot(days, d["x"], color=S1, lw=0.45)
for key, lab in [("seg_step", "step"), ("seg_flat", "flatline"),
                 ("seg_dither", "dithered flatline"), ("seg_drift", "drift")]:
    a, b = d[key]
    ax.axvspan(days[a], days[b - 1], color=CRIT, alpha=0.14, lw=0)
    ax.annotate(lab, xy=((days[a] + days[b - 1]) / 2, 21.6), ha="center",
                fontsize=7.5, color=CRIT)
ax.scatter(days[d["spike_idx"]], d["x"][d["spike_idx"]], s=11, zorder=3,
           facecolor="none", edgecolor=CRIT, lw=0.9, label="injected spikes")
ax.set_xlabel("day"); ax.set_ylabel("air temperature ($^\circ$C)")
ax.set_title("The benchmark series: 30 days at 5 min with five fault classes injected")
ax.set_xlim(0, 30); ax.grid(axis="y")
ax.legend(loc="lower left", handletextpad=0.4)
fig.savefig(FIG + "fig_series.png"); plt.close(fig)

print("figures written")
