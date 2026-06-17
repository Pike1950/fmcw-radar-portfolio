"""
beat_vs_range.py - SDD Figure 5-2: beat frequency vs target range

FMCW maps range to a beat frequency: f_beat = 2*R*S/c, where S is the chirp
slope (B/T_chirp). At the design slope of 250 GHz/s this is 1.667 kHz per metre,
so the 50 m design point lands at ~83 kHz, well under the 128 kHz Nyquist of the
256 kSPS sampler. The line reaches Nyquist near 77 m, the unambiguous-range
ceiling for the real-sampled span.

Outputs: beat_vs_range.svg + .png
Run:     python beat_vs_range.py
"""
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

# FMCW dark-theme palette (matches the SDD HTML theme)
BG = "#0f1216"; PANEL = "#14181e"; FG = "#e6e8eb"; MUTED = "#9aa3ad"; GRID = "#2a2f3a"
BLUE = "#60a5fa"; AMBER = "#fbbf24"; RED = "#f87171"; GREEN = "#4ade80"

c = 2.998e8            # m/s
S = 250e9             # chirp slope, Hz/s (250 MHz / 1 ms)
fs = 256e3            # sample rate, Hz
fny = fs / 2          # Nyquist, 128 kHz

R = np.linspace(0, 85, 500)
fbeat = 2 * R * S / c / 1e3        # kHz
R_design = 50.0
f_design = 2 * R_design * S / c / 1e3   # 83.3 kHz
R_max = fny * c / (2 * S)          # 76.8 m at Nyquist

fig, ax = plt.subplots(figsize=(8.0, 4.2), facecolor=BG)
ax.set_facecolor(PANEL)
ax.plot(R, fbeat, color=BLUE, lw=2.4, label="f_beat = 2RS/c  (1.67 kHz/m)")

# Nyquist ceiling
ax.axhline(fny / 1e3, color=RED, lw=1.4, ls=(0, (5, 4)))
ax.text(2, fny / 1e3 + 3, "Nyquist 128 kHz (256 kSPS)", color=RED, fontsize=9, va="bottom")

# max unambiguous range
ax.axvline(R_max, color=MUTED, lw=1.0, ls=":")
ax.text(R_max - 1.5, 20, "~77 m max\nunambiguous", color=MUTED, fontsize=8.5, ha="right")

# design point
ax.plot([R_design], [f_design], "o", color=AMBER, ms=8, zorder=5)
ax.annotate("50 m -> 83 kHz\n(design)", xy=(R_design, f_design),
            xytext=(R_design - 23, f_design + 22), color=AMBER, fontsize=9,
            arrowprops=dict(arrowstyle="->", color=AMBER, lw=1.2))

ax.set_xlim(0, 85); ax.set_ylim(0, 150)
ax.set_xlabel("target range (m)", color=FG, fontsize=10.5)
ax.set_ylabel("beat frequency (kHz)", color=FG, fontsize=10.5)
ax.set_title("Beat frequency vs target range  (slope 250 GHz/s)", color=FG, fontsize=11.5)
ax.grid(True, alpha=0.35, color=GRID, lw=0.5)
ax.tick_params(colors=FG)
for s in ax.spines.values():
    s.set_color(GRID)
ax.legend(loc="lower right", facecolor=PANEL, edgecolor=GRID, labelcolor=FG, fontsize=9)

fig.tight_layout()
here = os.path.dirname(os.path.abspath(__file__))
fig.savefig(os.path.join(here, "beat_vs_range.svg"), facecolor=BG, edgecolor="none")
fig.savefig(os.path.join(here, "beat_vs_range.png"), facecolor=BG, edgecolor="none", dpi=150)
plt.close(fig)
print(f"design {R_design} m -> {f_design:.1f} kHz ; max unambiguous {R_max:.1f} m ; wrote beat_vs_range.svg + .png")
