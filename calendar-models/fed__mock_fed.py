"""Mock: Vizard's Fed card on NQ1! 5-minute, Thu 23 Oct 2025 at 15:01 ET (six days before the 29 Oct cut).
Every value on the card is computed with fedwatch.tree() from CME's own FedWatch output at that minute (the intraday
sample), the same numbers the Pine card would show from the ZQ prices behind it. The sample is one snapshot, so the
1-day and 5-day change columns are blank. Left: Full layout (event card switched off). Right: the
Mobile row.   python3 mock_fed.py out.png"""
import sys, json, numpy as np, pandas as pd, matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, FancyBboxPatch
from fedwatch import tree
plt.rcParams['font.family'] = 'DejaVu Sans'
MONO = 'DejaVu Sans Mono'
BG, BODY, BODY2, NEU = '#0e1117', '#161a23', '#1c2130', '#3a3f4b'
TX, SUB, MU = '#e6e9ef', '#9aa3b5', '#5d6476'
COLD, CFD, LVL = '#64b5f6', '#5c6bc0', '#ffb300'
UPC, DNC = '#089981', '#f23645'

# ── card values from the CME sample
raw = open('/mnt/user-data/uploads/CVOL EOD Rest API sample/FedWatch Intraday Forecasts/FedWatch Intraday Forecasts.json').read().strip()
J = json.loads(('{"' + raw + '\n]}').replace('ratetRange', 'rateRange'))['payload']
lo0 = 4.00
deltas, prevE = [], 0.0
for m in J:
    E = sum(round((r['lowerRt'] / 100 - lo0) / .25) * r['probability'] for r in m['rateRange'])
    deltas.append(.25 * (E - prevE)); prevE = E
dist = tree(deltas)
rngs = lambda k: f'{(lo0 + .25 * k) * 100:.0f}–{(lo0 + .25 * (k + 1)) * 100:.0f}'
word = lambda k: 'hold' if k == 0 else (f'cut {-25 * k}' if k < 0 else f'hike {25 * k}')
d0 = dist[0]; ks = sorted(((d0[20 + k], k) for k in range(-20, 21) if d0[20 + k] > 0), reverse=True)
(pA, kA), (pB, kB) = ks[0], ks[1]
dates = [pd.Timestamp(m['meetingDt']) for m in J]
cum = np.cumsum(deltas) * 100
rows = [('NEXT', f'{word(kA)} → {rngs(kA)}', f'{pA * 100:.0f}%', '—', TX),
        ('', f'{word(kB)} at {rngs(kB)}' if kB == 0 else f'{word(kB)} → {rngs(kB)}', f'{pB * 100:.0f}%', '—', MU)]
for j in (1, 2, 3):
    k = int(np.argmax(dist[j])) - 20
    rows.append((dates[j].strftime('%d %b').upper(), f'{rngs(k)} most likely · {dist[j].max() * 100:.0f}%', f'{cum[j]:+.0f}bp'.replace('-', '−'), '—', TX))
rows.append(('5D', "next meeting's expected rate, 5 days", '—', '', TX))
print('card:', kA, pA, kB, pB, [(r[0], r[1], r[2]) for r in rows[2:5]])

# ── chart
b = pd.read_pickle('/home/claude/t3/bars_NQ_all.pkl')
x = b[(b.ts >= '2025-10-22 18:00') & (b.ts <= '2025-10-23 15:00')].set_index('ts').resample('5min').agg(dict(Open='first', High='max', Low='min', Close='last')).dropna()
fig = plt.figure(figsize=(16, 8.6), dpi=100, facecolor=BG)
ax = fig.add_axes([0.02, 0.07, 0.66, 0.86], facecolor=BG)
n = len(x)
for i, (t, r) in enumerate(x.iterrows()):
    c = UPC if r.Close >= r.Open else DNC
    ax.plot([i, i], [r.Low, r.High], color=c, lw=0.8, zorder=2)
    ax.add_patch(Rectangle((i - .35, min(r.Open, r.Close)), .7, max(abs(r.Close - r.Open), 0.5), fc=c, ec=c, lw=0.5, zorder=3))
lo, hi = x.Low.min(), x.High.max(); pad = (hi - lo) * 0.08
ax.set_xlim(-2, n + 55); ax.set_ylim(lo - pad, hi + (hi - lo) * 0.95)
ticks = [i for i, t in enumerate(x.index) if t.minute == 0 and t.hour % 3 == 0]
ax.set_xticks(ticks); ax.set_xticklabels([x.index[i].strftime('%H:%M') for i in ticks], color=MU, fontsize=8)
ax.yaxis.tick_right(); ax.tick_params(axis='y', colors=MU, labelsize=8); ax.tick_params(axis='x', length=0)
for s_ in ax.spines.values(): s_.set_visible(False)
ax.grid(color='#1c2130', lw=0.6)
ax.text(0, hi + (hi - lo) * 0.88, 'NQ1! · 5 · CME   Vizard', color=SUB, fontsize=9, va='top')
ax.axhline(x.Close.iloc[-1], color='#2962ff', lw=0.7, ls=':', zorder=1)

# ── Full card, top right of the price chart (drawn in figure coordinates)
COLW = [0.006, 0.052, 0.205, 0.058, 0.075]          # stripe · key · wording · value · side
X0 = 0.66 - sum(COLW) - 0.006; RH = 0.032; Y0 = 0.905
def cell(xa, y, w, txt, fg, bg, bold=False, ha='left', size=8.6):
    fig.add_artist(Rectangle((xa, y - RH), w, RH, transform=fig.transFigure, fc=bg, ec=BG, lw=0.6))
    if txt:
        tx = xa + (0.004 if ha == 'left' else w / 2)
        fig.text(tx, y - RH / 2, txt, color=fg, fontsize=size, family=MONO, weight='bold' if bold else 'normal', ha=ha, va='center')
def row(y, cells):
    xa = X0
    for w, c in zip(COLW, cells):
        if c is not None: cell(xa, y, w, *c)
        xa += w
y = Y0
# header: stripe · title over key..value · pill
cell(X0, y, COLW[0], '', None, CFD)
cell(X0 + COLW[0], y, sum(COLW[1:4]), '◆ FED · FOMC 29 OCT', '#ffffff', CFD, True)
cell(X0 + sum(COLW[:4]), y, COLW[4], f'{word(kA).upper()} {pA * 100:.0f}%', '#ffffff', COLD, True, 'center')
y -= RH
row(y, [('', None, CFD), ('', MU, BODY2), (f'FedWatch steps on CBOT ZQ · now {rngs(0)}', MU, BODY2), ('odds', MU, BODY2, False, 'center'), ('1d', MU, BODY2, False, 'center')])
for k_, lab, v, sd, vfg in rows:
    y -= RH
    row(y, [('', None, CFD), (k_, MU, BODY, False, 'center', 7.6), (lab, TX, BODY), (v, vfg, BODY, True, 'center'), (sd, MU, BODY, False, 'center')])
fig.text(X0, y - RH - 0.012, 'Values: CME FedWatch sample, 23 Oct 2025 15:01 ET. 1d / 5D blank: the sample is one snapshot.', color=MU, fontsize=7.4, va='top')

# ── phone with the Mobile card (event rows collapsed, then the Fed row)
px = fig.add_axes([0.71, 0.04, 0.27, 0.92], facecolor=BG); px.axis('off'); px.set_xlim(0, 1); px.set_ylim(0, 1)
px.add_patch(FancyBboxPatch((0.03, 0.01), 0.94, 0.98, boxstyle='round,pad=0,rounding_size=0.06', fc='#05070b', ec='#2a2f3a', lw=2))
px.add_patch(Rectangle((0.07, 0.05), 0.86, 0.9, fc=BG, ec='none'))
px.text(0.10, 0.925, 'NQ1! · 5', color=SUB, fontsize=8)
MW = [0.012, 0.11, 0.37, 0.12, 0.13]; mx0 = 0.93 - sum(MW); mh = 0.034
def mrow(y, cells):
    xa = mx0
    for w, c in zip(MW, cells):
        if c is not None:
            t, fg, bg = c[:3]; bold = len(c) > 3 and c[3]; ha = c[4] if len(c) > 4 else 'left'
            px.add_patch(Rectangle((xa, y - mh), w, mh, fc=bg, ec=BG, lw=0.6))
            if t: px.text(xa + (0.008 if ha == 'left' else w / 2), y - mh / 2, t, color=fg, fontsize=7.2, family=MONO, weight='bold' if bold else 'normal', ha=ha, va='center')
        xa += w
my = 0.89
mrow(my, [('', None, '#ab47bc'), None, None, None, ('IN 5D', '#ffffff', '#3a3f4b', True, 'center')])
px.add_patch(Rectangle((mx0 + MW[0], my - mh), sum(MW[1:4]), mh, fc='#ab47bc', ec=BG, lw=0.6)); px.text(mx0 + MW[0] + 0.008, my - mh / 2, '◆ VIZARD · FOMC D1 · NQ1!', color='#ffffff', fontsize=7.2, family=MONO, weight='bold', va='center')
for i in range(3):
    my -= mh
    mrow(my, [('', None, '#ab47bc'), ('NOW' if i == 0 else '✓' if i else '', MU, BODY, False, 'center'), ('· · ·', MU, BODY), ('', TX, BODY), ('', TX, BODY)])
my -= mh + 0.008
mrow(my, [('', None, CFD), ('FED', MU, BODY, False, 'center'), (f"29 Oct {word(kA)}", TX, BODY), (f'{pA * 100:.0f}%', TX, BODY, True, 'center'), (word(kA).upper(), '#ffffff', COLD, True, 'center')])
px.annotate('Mobile: one Fed row.\nTap / hover: next meeting\'s two outcomes\nand the path to ' + dates[3].strftime('%d %b'), xy=(mx0 + 0.3, my - mh), xytext=(0.12, my - 0.16), color=SUB, fontsize=7.6,
            arrowprops=dict(arrowstyle='-', color=MU, lw=0.8))
fig.text(0.02, 0.965, 'Vizard · Fed card (new): FOMC odds from CBOT 30-day fed funds futures, CME FedWatch steps', color=TX, fontsize=12, weight='bold')
fig.text(0.02, 0.94, 'Full layout (event card off for the mock)   ·   Mobile layout on the right   ·   no PO3 candles, VIX or DXY cards in Vizard   ·   TradingView rendering will differ', color=MU, fontsize=8.5)
plt.savefig(sys.argv[1], dpi=100, facecolor=BG); print(sys.argv[1])
