"""
range_resolution.py - SDD Figure 5-3: range resolution vs sweep bandwidth

Range resolution depends only on swept bandwidth: dR = c / (2B). The full 250 MHz
24 GHz ISM band gives 0.6 m, about an 8x improvement over the 30 MHz / 5 m of the
old 5.8 GHz mode. Resolution is carrier-independent; what the 24 GHz move buys is
the room to sweep 250 MHz inside an ISM allocation.

Outputs: range_resolution.svg + .png
Run:     python range_resolution.py
"""
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

BG = "#0f1216"; PANEL = "#14181e"; FG = "#e6e8eb"; MUTED = "#9aa3ad"; GRID = "#2a2f3a"
BLUE = "#60a5fa"; AMBER = "#fbbf24"; RED = "#f87171"; GREEN = "#4ade80"

c = 2.998e8
B = np.linspace(10e6, 260e6, 500)    # Hz
dR = c / (2 * B)                     # m

fig, ax = plt.subplots(figsize=(8.0, 4.2), facecolor=BG)
ax.set_facecolor(PANEL)
ax.plot(B / 1e6, dR, color=BLUE, lw=2.4, label="dR = c / 2B")

for Bx, col, lbl, dy in [(30e6, AMBER, "5.8 GHz mode:\n30 MHz -> 5.0 m", 0.4),
                          (250e6, GREEN, "this design:\n250 MHz -> 0.6 m", 0.7)]:
    y = c / (2 * Bx)
    ax.plot([Bx / 1e6], [y], "o", color=col, ms=8, zorder=5)
    ax.annotate(lbl, xy=(Bx / 1e6, y), xytext=(Bx / 1e6 + 8, y + dy),
                color=col, fontsize=9,
                arrowprops=dict(arrowstyle="->", color=col, lw=1.2))

ax.set_xlim(0, 260); ax.set_ylim(0, 6)
ax.set_xlabel("sweep bandwidth (MHz)", color=FG, fontsize=10.5)
ax.set_ylabel("range resolution (m)", color=FG, fontsize=10.5)
ax.set_title("Range resolution vs sweep bandwidth", color=FG, fontsize=11.5)
ax.grid(True, alpha=0.35, color=GRID, lw=0.5)
ax.tick_params(colors=FG)
for s in ax.spines.values():
    s.set_color(GRID)
ax.legend(loc="upper right", facecolor=PANEL, edgecolor=GRID, labelcolor=FG, fontsize=9)

fig.tight_layout()
here = os.path.dirname(os.path.abspath(__file__))
fig.savefig(os.path.join(here, "range_resolution.svg"), facecolor=BG, edgecolor="none")
fig.savefig(os.path.join(here, "range_resolution.png"), facecolor=BG, edgecolor="none", dpi=150)
plt.close(fig)
print(f"30 MHz -> {c/(2*30e6):.2f} m ; 250 MHz -> {c/(2*250e6):.2f} m ; wrote range_resolution.svg + .png")
