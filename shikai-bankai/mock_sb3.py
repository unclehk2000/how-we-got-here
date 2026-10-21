"""SB Map v3 mock: the Asia 25 / 37.5 / 50% levels from the range's last extreme (fixed while price trades inside the
range) against v2's body-based 25% / 50% (redrawn every bar). NQ 1-minute, Asia of Mon 28 Sep 2026, at 21:00 ET."""
import sys
import numpy as np, pandas as pd, matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
OUT = sys.argv[1]
B = pd.read_pickle('/home/claude/kyw/bars_NQ_all.pkl'); B['m'] = (B.hm // 100) * 60 + B.hm % 100
day = pd.Timestamp('2026-09-28'); now = pd.Timestamp('2026-09-27 21:00')
v = B[(B.ts >= '2026-09-27 16:30') & (B.ts < now)].reset_index(drop=True)
a = v[v.ts >= '2026-09-27 18:00']
H, L = a.High.max(), a.Low.min(); tH, tL = a.High.idxmax(), a.Low.idxmin()
O = a.Open.iloc[0]; R = H - L
down = tH < tL
lv = {k: (L + k * R if down else H - k * R) for k in (0.25, 0.375, 0.5)}
# v2: body-based, recomputed at every bar with that bar's close
i0 = a.index[0]
c = a.Close.values
bt, bb = np.maximum(O, c), np.minimum(O, c); br = bt - bb
v2_25 = np.where(br > 0, np.where(c >= O, bt - 0.25 * br, bb + 0.25 * br), (bt + bb) / 2)
v2_50 = (O + c) / 2
BG, FG, GRID = '#ffffff', '#131722', '#eef1f6'
C25, C375, C50 = '#2196f3', '#5c6bc0', '#ab47bc'
fig = plt.figure(figsize=(16, 8.4), dpi=115, facecolor=BG)
ax = fig.add_axes([0.02, 0.07, 0.93, 0.85]); ax.set_facecolor(BG)
for i, r in v.iterrows():
    col = '#089981' if r.Close >= r.Open else '#f23645'
    ax.plot([i, i], [r.Low, r.High], color=col, lw=0.6)
    ax.add_patch(Rectangle((i - 0.32, min(r.Open, r.Close)), 0.64, max(abs(r.Close - r.Open), 0.25), fc=col, ec=col, lw=0.3))
last = len(v) - 1
ax.axvline(i0, color=FG, alpha=0.25, lw=0.8)
ax.text(i0, 0.985, 'Asia', transform=ax.get_xaxis_transform(), ha='center', va='top', fontsize=7, color=FG, bbox=dict(fc=FG, alpha=0.12, ec='none', pad=1.5))
# v2's levels, as they were redrawn bar by bar
xs = np.arange(i0, i0 + len(a))
ax.plot(xs, v2_25, color=C25, lw=1, alpha=0.35, drawstyle='steps-post')
ax.plot(xs, v2_50, color=C50, lw=1, alpha=0.35, drawstyle='steps-post')
ax.text(i0 + 3, v2_50[5] + 6, 'v2: body 25% / 50%, redrawn on every bar', fontsize=7.4, color='#787b86')
# v3 lines from the session start to the last bar
for k, col, st, nm in ((0.25, C25, '-', '25%'), (0.375, C375, '--', '37.5%'), (0.5, C50, '-', '50%')):
    ax.plot([i0, last], [lv[k], lv[k]], color=col, lw=1.2, ls=st)
    ax.text(last + 1, lv[k], f'18:00 09/27 Asia {nm}', fontsize=7.6, color=col, va='center')
# Asia session candle right of price, with v3 ticks
xx = last + 32; cw = 4
bt0, bb0 = max(O, a.Close.iloc[-1]), min(O, a.Close.iloc[-1])
ax.add_patch(Rectangle((xx, bb0), cw, bt0 - bb0, fc=FG, alpha=0.15, ec='none')); ax.add_patch(Rectangle((xx, bb0), cw, bt0 - bb0, fc='none', ec=FG, lw=0.8))
ax.plot([xx + cw / 2] * 2, [bt0, H], color=FG, lw=0.8); ax.plot([xx + cw / 2] * 2, [L, bb0], color=FG, lw=0.8)
ax.annotate(f'Asia\n{H:.2f}', (xx + cw / 2, H), xytext=(0, 3), textcoords='offset points', ha='center', va='bottom', fontsize=6, color=FG, bbox=dict(fc=FG, alpha=0.1, ec='none', pad=1.2))
ax.annotate(f'{L:.2f}', (xx + cw / 2, L), xytext=(0, -3), textcoords='offset points', ha='center', va='top', fontsize=6, color=FG)
for k, col, nm in ((0.25, C25, '25%'), (0.375, C375, '37.5%'), (0.5, C50, '50%')):
    ax.plot([xx + cw, xx + cw + 6], [lv[k]] * 2, color=col, lw=1)
    ax.text(xx + cw + 6.5, lv[k], nm, fontsize=6, color=col, va='center')
ax.set_xlim(-2, xx + 30)
ax.set_ylim(L - R * 0.25, H + R * 0.35)
ax.yaxis.tick_right(); ax.tick_params(colors=FG, labelsize=7.6, length=0); ax.grid(color=GRID, lw=0.6)
for sp in ax.spines.values(): sp.set_color(GRID)
ticks = [i for i, r in v.iterrows() if r.ts.minute in (0, 30)]
ax.set_xticks(ticks); ax.set_xticklabels([v.ts[i].strftime('%H:%M') for i in ticks])
ttl = (f'SB Map v3 · NQ 1 min · Asia of Mon 28 Sep 2026 at 21:00 ET · high {H:.2f} ({a.ts[tH]:%H:%M}) first, low {L:.2f} ({a.ts[tL]:%H:%M}) later: '
       f'levels measured up from the low and fixed while price trades inside the range')
fig.text(0.02, 0.965, ttl, fontsize=10, color=FG, weight='bold')
fig.savefig(f'{OUT}/SB3_Asia_levels_1m.png', facecolor=BG)
print({k: round(x, 2) for k, x in lv.items()}, 'v2 25% moved over', round(v2_25.max() - v2_25.min(), 2), 'pts; 50% over', round(v2_50.max() - v2_50.min(), 2))
