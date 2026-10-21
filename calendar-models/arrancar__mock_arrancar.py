"""Mock: Arrancar in its own pane under NQ1! daily, 12 Oct 2026.
Lines (left of the last bar): each upcoming meeting's expected rate, day by day, from CME's own FedWatch history
(FedMeetingHistory_20261012.csv; the script computes the same lines from CBOT ZQ). Ahead of the last bar: one column per
meeting with a block per target range shaded by its odds, from CME's conditional table on 12 Oct 2026 (which the
script's ZQ steps reproduce within 0.06 pp), the expected path, and the Fed's dot-plot medians (16 Sep 2026 SEP).
  python3 mock_fedmap.py out.png"""
import sys, numpy as np, pandas as pd, matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from matplotlib.colors import to_rgb
plt.rcParams['font.family'] = 'DejaVu Sans'
MONO = 'DejaVu Sans Mono'
BG, TX, SUB, MU, NEU, HOT = '#0e1117', '#e6e9ef', '#9aa3b5', '#5d6476', '#3a3f4b', '#ff8a65'
GH = '#ab47bc'; UPC, DNC = '#089981', '#f23645'
LINES = ['#e040fb', '#ba68c8', '#9575cd', '#7986cb', '#64b5f6', '#4dd0e1']
E = pd.read_pickle('exp_mid.pkl')                         # CME expected mid rate per meeting, daily
D = pd.read_pickle('/home/claude/hm/days_NQ.pkl'); D = D[D.anchor == 'TD'].set_index('tday').sort_index()
D = D[(D.index >= '2025-10-13') & (D.index <= '2026-10-09')]
lo0 = 3.75
B = ['375-400', '400-425', '425-450', '450-475', '475-500', '500-525', '525-550', '550-575']
C = {'28 OCT': [78.4, 21.6], '09 DEC': [12.3, 69.5, 18.2], '27 JAN': [6.9, 44.5, 40.6, 7.9], '17 MAR': [1.8, 16.9, 43.5, 31.9, 5.8],
     '28 APR': [1.1, 11.1, 33.2, 36.4, 15.9, 2.3], '09 JUN': [0.6, 6.9, 23.8, 35.1, 24.6, 8.1, 1.0], '28 JUL': [0.5, 5.9, 21.2, 33.3, 26.2, 10.6, 2.1, 0.1],
     '15 SEP': [0.5, 5.1, 18.8, 31.4, 27.3, 13.1, 3.4, 0.4], '27 OCT': [0.5, 5.0, 18.5, 31.1, 27.4, 13.4, 3.6, 0.5], '08 DEC': [0.6, 5.5, 19.0, 31.0, 26.9, 13.0, 3.5, 0.5]}
YEAR = {'28 OCT': 2026, '09 DEC': 2026}
SEP = {2026: 4.125, 2027: 4.125}
mids = lo0 + 0.125 + 0.25 * np.arange(8)
base = 3.878                                              # rate now (start of the 28 Oct meeting month, from the ZQ prices)
n = len(D)
fig = plt.figure(figsize=(17, 10.4), dpi=100, facecolor=BG)
ax1 = fig.add_axes([0.03, 0.60, 0.92, 0.32], facecolor=BG)
ax2 = fig.add_axes([0.03, 0.06, 0.92, 0.52], facecolor=BG, sharex=ax1)
for ax in (ax1, ax2):
    ax.yaxis.tick_right(); ax.tick_params(colors=MU, labelsize=8); ax.grid(color='#1a1f2b', lw=0.6)
    for s_ in ax.spines.values(): s_.set_color('#1c2130')
for i, (t, r) in enumerate(D.iterrows()):
    c = UPC if r.C >= r.O else DNC
    ax1.plot([i, i], [r.L, r.H], color=c, lw=0.7); ax1.add_patch(Rectangle((i - .35, min(r.O, r.C)), .7, max(abs(r.C - r.O), 1), fc=c, ec=c, lw=0.3))
ax1.text(0.003, 0.96, 'NQ1! · 1D · CME', transform=ax1.transAxes, color=SUB, fontsize=9, va='top')
# history lines
Ex = E.reindex(D.index, method='ffill')
for j, col in enumerate(E.columns[:6]):
    ax2.plot(range(n), Ex[col].values, color=LINES[j], lw=2 if j == 0 else 1.1)
x0, gx = n + 8, 10
ks = list(C.keys())
xR = x0 + gx * (len(ks) - 1) + 6
ax2.add_patch(Rectangle((max(0, n - 300), lo0), xR - max(0, n - 300), 0.25, fc=TX, alpha=0.07, ec='none'))
ax2.text(max(0, n - 300) + 1, lo0 + 0.01, 'target now 375–400', color=MU, fontsize=7.5, va='bottom')
grad = lambda p: tuple(np.array(to_rgb(GH)) * min(1, p / 0.6) + np.array(to_rgb(BG)) * (1 - min(1, p / 0.6)))
path_x, path_y = [n - 1], [base]
ymin = lo0
for j, k in enumerate(ks):
    xc = x0 + gx * j; P = np.array(C[k]) / 100
    for b_, p in enumerate(P):
        if p < 0.01: continue
        yl = lo0 + 0.25 * b_
        ax2.add_patch(Rectangle((xc - 4, yl), 8, 0.25, fc=grad(p), ec=BG, lw=1))
        if p >= 0.04: ax2.text(xc, yl + 0.125, f'{100 * p:.0f}%', color='#ffffff' if p >= 0.3 else TX, fontsize=7, ha='center', va='center', family=MONO)
    m = float((P * mids[:len(P)]).sum() / P.sum())
    path_x.append(xc); path_y.append(m)
    ax2.plot(xc, m, 'o', color=TX, ms=4, zorder=6)
ax2.plot(path_x, path_y, color=TX, lw=2, alpha=0.85, zorder=5)
for j, k in enumerate(ks):
    yr = 2026 if j < 2 else 2027; eoy = (j == 1) or (j == len(ks) - 1)
    xc = x0 + gx * j; mm = path_y[j + 1]
    txt = f'{k}\n{100 * (mm - base):+.0f}bp'
    if eoy:
        s = SEP[yr]; ax2.plot(xc + 5, s, 'D', color='#ffffff', ms=7, zorder=7)
        txt += f'\nFed {s:.3f}\nmkt {100 * (mm - s):+.0f}bp'
    ax2.text(xc, lo0 - 0.04, txt.replace('-', '−'), color=LINES[j] if j < 6 else SUB, fontsize=7.4, ha='center', va='top')
ax2.text(x0, lo0 + 0.25 * 8 + 0.05, '28 OCT · HOLD 78%', color=TX, fontsize=9.5, ha='center', va='bottom', weight='bold',
         bbox=dict(boxstyle='round,pad=0.35', fc=NEU, ec='none'))
ax2.text(max(0, n - 300), lo0 + 0.25 * 8 + 0.05, 'ARRANCAR · lines: each meeting\'s expected rate, bar by bar · blocks: odds of each target range per meeting · ◆ the Fed\'s dots (SEP 16 Sep 2026)',
         color=MU, fontsize=8, va='bottom')
ax2.set_xlim(-2, xR + 22); ax2.set_ylim(2.8, lo0 + 0.25 * 8 + 0.18)
ticks = [i for i, t in enumerate(D.index) if t.day <= 7 and t.dayofweek == 0][::2]
ax2.set_xticks(ticks); ax2.set_xticklabels([D.index[i].strftime('%b %y') for i in ticks], color=MU, fontsize=8)
plt.setp(ax1.get_xticklabels(), visible=False)
fig.text(0.03, 0.965, 'Arrancar (new indicator): the Fed path the market prices, its history, and the Fed\'s own dots', color=TX, fontsize=13, weight='bold')
fig.text(0.03, 0.942, 'Own pane under NQ1! daily, 12 Oct 2026. Lines: CME FedWatch history per meeting (the script builds them live from CBOT ZQ). Blocks: CME\'s conditional odds on 12 Oct, which the script\'s ZQ steps reproduce within 0.06 pp. TradingView rendering will differ.', color=MU, fontsize=8.3)
plt.savefig(sys.argv[1], dpi=100, facecolor=BG); print(sys.argv[1])
