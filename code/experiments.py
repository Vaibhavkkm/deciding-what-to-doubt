"""Numerical experiments for the reading report.

Builds the controlled synthetic benchmark on which the detection ideas in
the reading list are compared.

Everything is seeded, so a re-run gives identical numbers and figures.
"""
import json
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

rng = np.random.default_rng(7)

# ----------------------------------------------------------------------
# Shared figure style (light surface, colourblind-safe categorical order)
# ----------------------------------------------------------------------
INK = "#0b0b0b"; INK2 = "#52514e"; MUTED = "#898781"
GRID = "#e1e0d9"; BASE = "#c3c2b7"; SURF = "#ffffff"
S1, S2, S3, S4, S5, S6 = "#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#008300"
CRIT = "#d03b3b"   # status colour reserved for injected faults

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

FIGDIR = "../figures"


# ----------------------------------------------------------------------
# 1. Synthetic benchmark: 30 days of 5-minute air temperature
# ----------------------------------------------------------------------
DT_MIN = 5
N = 30 * 24 * 60 // DT_MIN            # 8640 observations
t_hours = np.arange(N) * DT_MIN / 60.0

def smoothed_walk(r, amp, k=288):
    """A random walk smoothed with a k-sample boxcar and rescaled to +-amp."""
    w = np.cumsum(r.normal(0, 1, N))
    s = np.convolve(w, np.ones(k) / k, mode="same")
    return amp * (s - s.mean()) / np.abs(s - s.mean()).max()

def ar1(r, phi=0.85, sd=0.12):
    e = r.normal(0, sd, N)
    n = np.empty(N); n[0] = e[0]
    for i in range(1, N):
        n[i] = phi * n[i - 1] + e[i]
    return n

# regional weather shared by every station in the toy network
r_wx = np.random.default_rng(11)
diurnal = 12.0 + 5.0 * np.sin(2 * np.pi * (t_hours - 9.0) / 24.0)
weather = diurnal + smoothed_walk(r_wx, 3.0)

def make_station(seed, offset=0.0):
    """Shared weather + a small local deviation + AR(1) sensor noise."""
    r = np.random.default_rng(seed)
    return weather + smoothed_walk(r, 0.4) + ar1(r) + offset
