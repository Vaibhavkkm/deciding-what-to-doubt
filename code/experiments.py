"""Numerical experiments for the reading report.

Reproduces, on a controlled synthetic benchmark, the behaviour of the main
detection ideas in the reading list: Grubbs' test (1969) and the modified
z-score of Iglewicz and Hoaglin (1993).

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

x_true = make_station(12)
x = x_true.copy()
truth = {}          # fault class -> boolean mask
idx = np.arange(N)

# isolated spikes: 14 points, 3 to 8 K, random sign
spike_idx = rng.choice(idx[(idx > 300) & (idx < N - 300)], 14, replace=False)
spike_idx.sort()
spike_amp = rng.uniform(3.0, 8.0, 14) * rng.choice([-1, 1], 14)
x[spike_idx] += spike_amp
m = np.zeros(N, bool); m[spike_idx] = True; truth["spike"] = m

# step change: +2.5 K for 36 h starting day 20 (radiation-shield fault)
s0 = 20 * 288; s1 = s0 + 36 * 12
x[s0:s1] += 2.5
m = np.zeros(N, bool); m[s0:s1] = True; truth["step"] = m

# exact flatline: 6 h frozen at the entry value, day 8
f0 = 8 * 288 + 60; f1 = f0 + 72
x[f0:f1] = x[f0]
m = np.zeros(N, bool); m[f0:f1] = True; truth["flat_exact"] = m

# dithered flatline: stuck sensor whose last digit still moves, day 24
g0 = 24 * 288 + 100; g1 = g0 + 72
x[g0:g1] = x[g0] + rng.uniform(-0.02, 0.02, 72)
m = np.zeros(N, bool); m[g0:g1] = True; truth["flat_dither"] = m

# calibration drift: linear ramp to +2.2 K over days 12 to 16
d0 = 12 * 288; d1 = 16 * 288
x[d0:d1] += np.linspace(0, 2.2, d1 - d0)
m = np.zeros(N, bool); m[d0:d1] = True; truth["drift"] = m

any_fault = np.zeros(N, bool)
for v in truth.values():
    any_fault |= v

# three clean neighbour stations for the spatial check
nbr = np.stack([make_station(21, 0.8), make_station(22, -0.6), make_station(23, 0.3)])


# ----------------------------------------------------------------------
# 2. Detectors
# ----------------------------------------------------------------------
def grubbs_crit(n, alpha=0.05):
    """Two-sided critical value from the exact t-quantile formula."""
    from scipy import stats
    t = stats.t.ppf(1 - alpha / (2 * n), n - 2)
    return (n - 1) / np.sqrt(n) * np.sqrt(t**2 / (n - 2 + t**2))

def grubbs_iterative(v, alpha=0.05, max_out=50):
    """Grubbs' test applied one observation at a time (as commonly misused)."""
    v = v.astype(float); keep = np.ones(len(v), bool)
    flagged = []
    for _ in range(max_out):
        vv = v[keep]
        mu, sd = vv.mean(), vv.std(ddof=1)
        g = np.abs(vv - mu) / sd
        j = np.argmax(g)
        if g[j] > grubbs_crit(len(vv), alpha):
            orig = np.where(keep)[0][j]
            flagged.append(orig); keep[orig] = False
        else:
            break
    out = np.zeros(len(v), bool); out[flagged] = True
    return out

def gesd(v, r_max, alpha=0.05):
    """Generalized ESD (Rosner 1983): decide the number of outliers afterwards."""
    from scipy import stats
    v = v.astype(float); n = len(v)
    keep = np.ones(n, bool); cand = []; R = []; lam = []
    for i in range(1, r_max + 1):
        vv = v[keep]
        mu, sd = vv.mean(), vv.std(ddof=1)
        g = np.abs(vv - mu) / sd
        j = np.argmax(g)
        cand.append(np.where(keep)[0][j]); R.append(g[j])
        ni = n - i + 1
        p = 1 - alpha / (2 * ni)
        tq = stats.t.ppf(p, ni - 2)
        lam.append((ni - 1) * tq / np.sqrt((ni - 2 + tq**2) * ni))
        keep[cand[-1]] = False
    k = 0
    for i in range(r_max):
        if R[i] > lam[i]:
            k = i + 1
    out = np.zeros(n, bool); out[cand[:k]] = True
    return out

def modified_z(v):
    med = np.median(v)
    mad = np.median(np.abs(v - med))
    return 0.6745 * (v - med) / mad if mad > 0 else np.zeros(len(v))

def rolling_modz(v, w):
    """Centred rolling modified z-score, MAD guarded at zero."""
    half = w // 2
    out = np.zeros(len(v))
    med = np.empty(len(v)); mad = np.empty(len(v))
    for i in range(len(v)):
        a, b = max(0, i - half), min(len(v), i + half + 1)
        win = v[a:b]
        med[i] = np.median(win)
        mad[i] = np.median(np.abs(win - med[i]))
    dev = v - med
    nz = mad > 0
    out[nz] = 0.6745 * dev[nz] / mad[nz]
    return out
