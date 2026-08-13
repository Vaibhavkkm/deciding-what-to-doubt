"""Figures for the reading report. Reads bench.npz + results.json produced by
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
results = json.load(open("results.json"))
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

# ----------------------------------------------------------------- fig 2
fig, (a1, a2) = plt.subplots(1, 2, figsize=(6.6, 2.5))
a1.plot(d["ns"], d["th_crit"], color=S1, lw=1.6, label="exact formula")
a1.plot(d["ns"], d["mc_crit"], ls="none", marker="o", ms=3.6, mfc="none",
        mec=S2, mew=1.0, label="Monte Carlo, 20 000 draws")
a1.set_xlabel("sample size $n$"); a1.set_ylabel("critical value $G_{0.05}$")
a1.set_title("Grubbs critical values recomputed")
a1.grid(axis="y"); a1.legend(loc="lower right")

ms = d["mask_sample"]; n = len(ms)
xpos = np.arange(n)
a2.axhline(ms[:18].mean(), color=BASE, lw=0.8)
a2.scatter(xpos[:18], ms[:18], s=14, color=S1, label="inliers")
a2.scatter(xpos[18:], ms[18:], s=26, color=CRIT, marker="D",
           label="planted pair")
a2.text(0.03, 0.9, "iterated Grubbs: 0 flags (masked)\ngeneralized ESD: 2 flags",
        transform=a2.transAxes, fontsize=7.6, color=INK2, va="top")
a2.set_xlabel("observation index"); a2.set_ylabel("value")
a2.set_title("Masking: the pair hides itself")
a2.grid(axis="y"); a2.legend(loc="lower left", handletextpad=0.3)
fig.tight_layout(w_pad=2.0)
fig.savefig(FIG + "fig_grubbs.png"); plt.close(fig)

# ----------------------------------------------------------------- fig 3
fig, ax = plt.subplots(figsize=(6.6, 2.3))
ax.axhline(3.0, color=S2, lw=0.9, ls=(0, (4, 3)))
ax.axhline(3.5, color=S1, lw=0.9, ls=(0, (4, 3)))
ax.text(19.4, 3.08, "|z| = 3", color=S2, fontsize=7.5)
ax.text(19.4, 3.7, "|M| = 3.5", color=S1, fontsize=7.5)
ax.plot(xpos, np.abs(d["z_sc"]), marker="o", ms=3.4, lw=0.9, color=S2,
        label="classical z-score |z|")
ax.plot(xpos, np.abs(d["m_sc"]), marker="s", ms=3.4, lw=0.9, color=S1,
        label="modified z-score |M|")
ax.set_xlabel("observation index"); ax.set_ylabel("score")
ax.set_title("Same sample, two scores: the planted pair never reaches |z| = 3 "
             "yet clears |M| = 3.5 with room to spare")
ax.grid(axis="y"); ax.legend(loc="upper left")
fig.savefig(FIG + "fig_modz.png"); plt.close(fig)

# ----------------------------------------------------------------- fig 4
fig, (a1, a2) = plt.subplots(2, 1, figsize=(6.6, 4.0), sharex=True)
for w, col in [(7, S1), (25, S2), (97, S3)]:
    a1.plot(d["sweep_T"], d[f"fa{w}"], color=col, lw=1.5)
    a2.plot(d["sweep_T"], d[f"rec{w}"], color=col, lw=1.5, label=f"window {w}")
for a in (a1, a2):
    a.axvline(3.5, color=INK2, lw=0.8, ls=(0, (4, 3)))
    a.axvspan(30, 300, color=S4, alpha=0.12, lw=0)
    a.set_xscale("log")
a1.text(3.6, 5.4, "textbook 3.5", fontsize=7.5, color=INK2, rotation=0)
a1.text(90, 5.4, "operational range", fontsize=7.5, color=INK2, ha="center")
a1.set_ylabel("false alarms per day"); a1.grid(axis="y")
a1.set_title("Rolling modified z-score: the threshold trades false alarms "
             "against missed spikes")
a2.set_ylabel("spike recall (%)"); a2.set_xlabel("threshold on |M| (log scale)")
a2.grid(axis="y"); a2.legend(loc="lower left")
a2.set_xlim(d["sweep_T"][0], d["sweep_T"][-1] * 1.35)
fig.tight_layout(h_pad=1.0)
fig.savefig(FIG + "fig_thresholds.png"); plt.close(fig)

# ----------------------------------------------------------------- fig 5
classes = ["spike", "step", "flat_exact", "flat_dither", "drift"]
class_lab = ["spike", "step", "flatline\n(exact)", "flatline\n(dithered)", "drift"]
names = list(results.keys())
M = np.array([[results[nm][c] for c in classes] for nm in names])
fa = np.array([results[nm]["fa_per_day"] for nm in names])

fig, ax = plt.subplots(figsize=(6.6, 3.4))
seq = matplotlib.colors.LinearSegmentedColormap.from_list(
    "seq", ["#f3f7fd", "#cde2fb", "#86b6ef", "#3987e5", "#1c5cab", "#0d366b"])
im = ax.imshow(M, cmap=seq, vmin=0, vmax=100, aspect="auto")
for i in range(len(names)):
    for j in range(len(classes)):
        v = M[i, j]
        ax.text(j, i, f"{v:.0f}", ha="center", va="center", fontsize=7.6,
                color="white" if v > 55 else INK2)
    ax.text(len(classes) - 0.28, i, f"{fa[i]:.2f}", ha="left", va="center",
            fontsize=7.6, color=INK2, transform=ax.transData, clip_on=False)
ax.text(len(classes) - 0.28, -0.9, "false alarms\nper day", ha="left",
        va="center", fontsize=7.2, color=MUTED, clip_on=False)
ax.set_xticks(range(len(classes)), class_lab, fontsize=7.6)
ax.set_yticks(range(len(names)), names, fontsize=7.8)
ax.set_title("Share of faulty points flagged, by detector and fault class (%)")
ax.spines[:].set_visible(False)
ax.tick_params(length=0)
fig.savefig(FIG + "fig_detectors.png"); plt.close(fig)

# ----------------------------------------------------------------- fig 6
# citation trajectories, OpenAlex counts_by_year, accessed 19 Aug 2026
cby = {
    "Grubbs 1969": {2012: 171, 2013: 202, 2014: 208, 2015: 194, 2016: 197,
                    2017: 197, 2018: 206, 2019: 230, 2020: 170, 2021: 218,
                    2022: 164, 2023: 162, 2024: 177, 2025: 166},
    "Shafer et al. 2000": {2012: 11, 2013: 18, 2014: 13, 2015: 12, 2016: 15,
                           2017: 18, 2018: 8, 2019: 11, 2020: 7, 2021: 18,
                           2022: 15, 2023: 16, 2024: 3, 2025: 6},
    "Campbell et al. 2013": {2014: 2, 2015: 8, 2016: 7, 2017: 9, 2018: 16,
                             2019: 14, 2020: 7, 2021: 30, 2022: 10, 2023: 14,
                             2024: 2, 2025: 2},
    "Leigh et al. 2019": {2019: 10, 2020: 11, 2021: 22, 2022: 17, 2023: 25,
                          2024: 21, 2025: 15},
}
totals = {"Grubbs 1969": 3742, "Shafer et al. 2000": 288,
          "Campbell et al. 2013": 127, "Leigh et al. 2019": 133}
fig, (a1, a2) = plt.subplots(1, 2, figsize=(6.6, 2.5),
                             gridspec_kw={"width_ratios": [1.15, 1]})
a1.plot(sorted(cby["Grubbs 1969"]), [cby["Grubbs 1969"][y] for y in
        sorted(cby["Grubbs 1969"])], color=S1, lw=1.6)
a1.annotate("Grubbs 1969", xy=(2025.2, 166), color=S1, fontsize=7.6, va="center")
a1.set_ylim(0); a1.set_ylabel("citations per year"); a1.set_xlabel("year")
a1.set_title("A 1969 paper, still cited daily"); a1.grid(axis="y")
a1.set_xlim(2011.5, 2028.5)
a1.set_xticks([2012, 2016, 2020, 2024])
for nm, col in [("Shafer et al. 2000", S2), ("Campbell et al. 2013", S3),
                ("Leigh et al. 2019", S6)]:
    ys = sorted(cby[nm])
    a2.plot(ys, [cby[nm][y] for y in ys], color=col, lw=1.6)
    a2.annotate(nm.replace(" et al.", ""), xy=(ys[-1] + 0.2, cby[nm][ys[-1]]),
                color=col, fontsize=7.4, va="center")
a2.set_ylim(0); a2.set_xlabel("year"); a2.grid(axis="y")
a2.set_title("The applied line of the lineage")
a2.set_xlim(2011.5, 2029.5)
a2.set_xticks([2012, 2016, 2020, 2024])
fig.tight_layout(w_pad=2.0)
fig.savefig(FIG + "fig_citations.png"); plt.close(fig)

# ----------------------------------------------------------------- fig 7
# vertical milestone chart: evenly spaced rows, so labels can never collide
events = [
    (1852, "Peirce's criterion", 0), (1863, "Chauvenet's rejection rule", 0),
    (1936, "Pearson and Chandra Sekar analyse masking", 1),
    (1950, "Grubbs' sample criteria for outlying observations", 1),
    (1960, "Anscombe frames rejection rules as insurance", 1),
    (1969, "Grubbs' Technometrics procedures [core reading]", 1),
    (1974, "Hampel formalises MAD and robustness", 1),
    (1983, "Rosner's generalized ESD procedure", 1),
    (1988, "Gandin's complex quality control in NWP", 2),
    (1993, "Iglewicz and Hoaglin's modified z-score [core reading]", 1),
    (2000, "Shafer et al.: Oklahoma Mesonet QA [core reading]", 2),
    (2013, "Campbell et al.: streaming QA/QC [core reading]", 3),
    (2019, "Leigh et al.: anomaly detection framework [core reading]", 3),
    (2022, "PyHydroQC, SaQC: QC as reusable software", 3),
]
era_names = ["astronomy's rejection rules", "the statistics of outliers",
             "operational network QA", "streaming data and learning"]
era_cols = ["#cde2fb", "#9ec5f4", "#86b6ef", "#5598e7"]
fig, ax = plt.subplots(figsize=(6.6, 3.6))
nE = len(events)
for i, (y, lab, era) in enumerate(events):
    row = nE - 1 - i
    ax.scatter(0, row, s=42, color=era_cols[era], zorder=3,
               edgecolor=S1, linewidth=0.8)
    ax.text(-0.06, row, str(y), ha="right", va="center", fontsize=8.2,
            color=INK, fontweight="semibold")
    ax.text(0.06, row, lab, ha="left", va="center", fontsize=8.2, color=INK2)
ax.plot([0, 0], [-0.4, nE - 0.6], color=BASE, lw=1.0, zorder=1)
# era legend on the right
for j, (nm, c) in enumerate(zip(era_names, era_cols)):
    ax.scatter(1.58, nE - 1.2 - j * 1.15, s=42, color=c, edgecolor=S1,
               linewidth=0.8, clip_on=False)
    ax.text(1.63, nE - 1.2 - j * 1.15, nm, ha="left", va="center",
            fontsize=7.6, color=INK2)
ax.set_xlim(-0.28, 2.3); ax.set_ylim(-0.6, nE - 0.4)
ax.axis("off")
ax.set_title("From doubtful observations to streaming sensors: the lineage in "
             "fourteen steps", pad=10)
fig.savefig(FIG + "fig_timeline.png"); plt.close(fig)

print("figures written")
