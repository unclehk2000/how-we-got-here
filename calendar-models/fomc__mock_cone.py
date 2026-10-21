"""Mock: Vizard's statement shock cone on NQ1! 5-minute, Wed 16 Sep 2026 (the 25bp hike), as it stands at 16:15 ET.
Bands from cone.json (FOMC days 2018–26, 50% and 80% of the max distance from the 14:00 open by each 5 minutes), scaled by
the day's ADR20 (completed days) from days_NQ.pkl, the way the script scales them.   python3 mock_cone.py out.png"""
import sys, json, numpy as np, pandas as pd, matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Polygon
plt.rcParams['font.family'] = 'DejaVu Sans'
BG, TX, MU, GH, LVL = '#0e1117', '#e6e9ef', '#6b7385', '#ab47bc', '#ffb300'
UPC, DNC = '#089981', '#f23645'
C = json.load(open('cone.json'))['NQ']
D = pd.Timestamp('2026-09-16')
b = pd.read_pickle('/home/claude/t3/bars_NQ_all.pkl').set_index('ts')
x = b[(b.index >= D + pd.Timedelta(hours=11)) & (b.index < D + pd.Timedelta(hours=16, minutes=30))].resample('5min').agg(dict(Open='first', High='max', Low='min', Close='last')).dropna()
adr = pd.read_pickle('/home/claude/hm/days_NQ.pkl'); adr = adr[adr.anchor == 'TD'].set_index('tday').adr.loc[D]
o14 = float(b.loc[D + pd.Timedelta(hours=14), 'Open']); o30 = float(b.loc[D + pd.Timedelta(hours=14, minutes=30), 'Open'])
a = adr * o14
idx = lambda t: int(np.searchsorted(x.index, t))
i14 = idx(D + pd.Timedelta(hours=14))
fig = plt.figure(figsize=(16, 8.6), dpi=100, facecolor=BG)
ax = fig.add_axes([0.02, 0.07, 0.92, 0.84], facecolor=BG)
for i, (t, r) in enumerate(x.iterrows()):
    c = UPC if r.Close >= r.Open else DNC
    ax.plot([i, i], [r.Low, r.High], color=c, lw=0.8, zorder=4)
    ax.add_patch(Rectangle((i - .35, min(r.Open, r.Close)), .7, max(abs(r.Close - r.Open), 0.5), fc=c, ec=c, lw=0.4, zorder=5))
ks = np.arange(27); xs = i14 + ks + 1                         # step k ends at 14:05 + 5k
def band(u, d, al, ec):
    up = [(i14, o14)] + [(xx, o14 + v * a) for xx, v in zip(xs, u)]
    dn = [(xx, o14 - v * a) for xx, v in zip(xs[::-1], d[::-1])] + [(i14, o14)]
    ax.add_patch(Polygon(up + dn, closed=True, fc=GH, alpha=al, ec=ec, lw=0.8, zorder=2))
band(C['u80'], C['d80'], 0.10, GH); band(C['u50'], C['d50'], 0.16, 'none')
ax.text(xs[-1] + 0.5, o14 + C['u80'][-1] * a, ' 80% of FOMC days', color=GH, fontsize=8, va='bottom')
ax.text(xs[-1] + 0.5, o14 + C['u50'][-1] * a, ' 50%', color=GH, fontsize=8, va='center')
ax.text(xs[-1] + 0.5, o14 - C['d80'][-1] * a, ' 80%', color=GH, fontsize=8, va='top')
ax.axvspan(i14 - .5, idx(D + pd.Timedelta(hours=14, minutes=30)) - .5, color='#2962ff', alpha=0.10, lw=0)
ax.axvspan(idx(D + pd.Timedelta(hours=14, minutes=30)) - .5, idx(D + pd.Timedelta(hours=16, minutes=15)) - .5, color='#2962ff', alpha=0.05, lw=0)
n = len(x)
ax.plot([i14, n + 10], [o14, o14], color=GH, lw=1.1); ax.text(n + 10.5, o14, f'14:00 open {o14:.2f}', color=GH, fontsize=7.5, va='center')
i30 = idx(D + pd.Timedelta(hours=14, minutes=30))
ax.plot([i30, n + 10], [o30, o30], color=GH, lw=1, ls='--', alpha=0.7); ax.text(n + 10.5, o30, f'14:30 open {o30:.2f}', color=GH, fontsize=7.5, va='center', alpha=0.85)
hi = max(x.High.max(), o14 + C['u80'][-1] * a); lo = min(x.Low.min(), o14 - C['d80'][-1] * a)
ax.set_xlim(-1, n + 22); ax.set_ylim(lo - (hi - lo) * 0.06, hi + (hi - lo) * 0.1)
ax.yaxis.tick_right(); ax.tick_params(axis='y', colors=MU, labelsize=8); ax.tick_params(axis='x', length=0)
tk = [i for i, t in enumerate(x.index) if t.minute == 0]
ax.set_xticks(tk); ax.set_xticklabels([x.index[i].strftime('%H:%M') for i in tk], color=MU, fontsize=8)
for s_ in ax.spines.values(): s_.set_visible(False)
ax.grid(color='#1a1f2b', lw=0.6, zorder=0)
ax.text(i14, hi + (hi - lo) * 0.05, 'statement', color=GH, fontsize=8, ha='center')
c16 = float(x.Close[x.index < D + pd.Timedelta(hours=16, minutes=15)].iloc[-1])
fig.text(0.02, 0.965, 'Vizard · statement shock cone (new) · NQ1! · 5 · Wed 16 Sep 2026 (the 25bp hike) at 16:15 ET', color=TX, fontsize=12.5, weight='bold')
fig.text(0.02, 0.935, f'Bands: how far price had gone from the 14:00 open by each 5 minutes on past FOMC days (2018–26, n {C["n"]}), inner 50%, outer 80%, '
         f'scaled by the day\'s ADR20 ({adr * 100:.2f}% = {a:.0f} pts). Live it runs a few minutes ahead of price.', color=MU, fontsize=8.5)
plt.savefig(sys.argv[1], dpi=100, facecolor=BG)
print(sys.argv[1], f'o14 {o14} adr {adr:.4f} a {a:.1f} up80 end {o14 + C["u80"][-1] * a:.1f} dn80 end {o14 - C["d80"][-1] * a:.1f} close16 {c16} high {x.High.max()} low {x.Low.min()}')
