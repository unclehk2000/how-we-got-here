"""Gran Rey Cero v5 structure mock: NQ1! 5-minute, CPI day Wed 12 Aug 2026, light theme, at 11:30 ET.
The pre-CPI range, the 08:30–09:00 CPI dealing range and its CE, the CPI flag and the NQ · ES · RTY week-open readout,
computed the way Gran_Rey_Cero.pine computes them from NQ / ES / RTY 1-minute data.
python3 mock_grc5.py out.png [dark]"""
import sys, numpy as np, pandas as pd, matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, FancyBboxPatch
plt.rcParams['font.family'] = 'DejaVu Sans'
OUT = sys.argv[1]
DARK = len(sys.argv) > 2 and sys.argv[2] == 'dark'
if DARK:
    BG, TX, SUB, MU, GRID, BODY = '#0e1117', '#e6e9ef', '#9aa3b5', '#5d6476', '#1a1f2b', '#161a23'
else:
    BG, TX, SUB, MU, GRID, BODY = '#ffffff', '#131722', '#4a5163', '#9aa1b2', '#eef1f6', '#f4f6f9'
UP, DN = '#089981', '#f23645'
GH, LVL, DR0, WINL = '#e53935', '#ffb300', '#90a4ae', '#2962ff'
T = pd.Timestamp('2026-08-12')
at = lambda h, m: T + pd.Timedelta(hours=h, minutes=m)
NOW = at(11, 29)
bars = {s: pd.read_pickle(f'/home/claude/kyw/bars_{s}_all.pkl') for s in ('NQ', 'ES', 'RTY')}
b = bars['NQ']
day = b.groupby('tday').agg(H=('High', 'max'), L=('Low', 'min'), O=('Open', 'first'))
ADR = float((day.H - day.L).rolling(20).mean().shift(1).loc[T])
g = b[b.tday == T].set_index('ts')
x = g[(g.index >= at(6, 0)) & (g.index <= NOW)].resample('5min').agg(dict(Open='first', High='max', Low='min', Close='last')).dropna()
n = len(x)
ix = lambda t: float(np.searchsorted(x.index, t))
fut = 150                                              # bars of room to the right (the lines run to 17:00)
fig = plt.figure(figsize=(18, 10.6), dpi=100, facecolor=BG)
ax = fig.add_axes([0.02, 0.05, 0.92, 0.85]); ax.set_facecolor(BG)
for s_ in ax.spines.values(): s_.set_visible(False)
ax.yaxis.tick_right(); ax.tick_params(axis='y', colors=MU, labelsize=8.5); ax.tick_params(axis='x', length=0)
ax.grid(color=GRID, lw=0.7, zorder=0)
lo, hi = x.Low.min(), x.High.max(); pad = hi - lo
ax.set_xlim(-2, n + 44); ax.set_ylim(lo - pad * 0.62, hi + pad * 0.42)
ticks = [i for i, t in enumerate(x.index) if t.minute == 0]
ax.set_xticks(ticks); ax.set_xticklabels([x.index[i].strftime('%H:%M') for i in ticks], color=MU, fontsize=8.5)
xe = n + 40
# 08:30 / 09:00 window lines and shading (CPI day)
i830, i900, i930 = ix(at(8, 30)), ix(at(9, 0)), ix(at(9, 30))
ax.axvspan(i830 - .5, i900 - .5, color=WINL, alpha=0.18, lw=0, zorder=1)
for xi_ in (i830 - .5, i900 - .5):
    ax.axvline(xi_, color=WINL, lw=3, zorder=2)
# yesterday's RTH close
pv = b[b.tday == T - pd.Timedelta(days=1)].set_index('ts')
yc = float(pv.Close[pv.index <= at(-8, 14)].iloc[-1])
ax.plot([ix(at(7, 30)), xe], [yc, yc], color=LVL, lw=1, ls=':', alpha=0.8)
ax.text(xe + 0.5, yc, ' yday RTH close', color=LVL, fontsize=8, va='center')
# pre-CPI range 07:30–08:29, live, ending at the first side taken after 08:30
pr = g[(g.index >= at(7, 30)) & (g.index < at(8, 30))]
pH, pL = pr.High.max(), pr.Low.min()
aft = g[(g.index >= at(8, 30)) & (g.index < at(16, 15))]
tu = aft.index[aft.High > pH]; td = aft.index[aft.Low < pL]
tu = tu[0] if len(tu) else None; td = td[0] if len(td) else None
sw = tu if td is None or (tu is not None and tu <= td) else td
sdir = 1 if sw == tu else -1
iE = ix(sw) if sw is not None else n
for yv, lab, va in ((pH, 'pre-CPI high', 'bottom'), (pL, 'pre-CPI low', 'top')):
    ax.plot([ix(at(7, 30)), iE], [yv, yv], color=DR0, lw=1.2, ls='--', zorder=3)
    ax.text(ix(at(7, 30)), yv, lab, color=DR0, fontsize=8, va=va)
if sw is not None:
    ax.text(iE - 0.6, pH if sdir > 0 else pL, '1st sweep ▲' if sdir > 0 else '1st sweep ▼', color=DR0, fontsize=8,
            ha='right', va='bottom' if sdir > 0 else 'top', weight='bold')
# CPI dealing range 08:30–09:00 and its CE, carried right to 17:00
w = g[(g.index >= at(8, 30)) & (g.index < at(9, 0))]
cH, cL = w.High.max(), w.Low.min(); ce = (cH + cL) / 2
c859 = float(w.Close.iloc[-1]); cd = abs(c859 - ce) / ADR
od = '94%' if cd <= 0.1 else '85%' if cd <= 0.2 else '71%' if cd <= 0.4 else '39%'
for yv, lab, va in ((cH, 'CPI DR high', 'bottom'), (cL, 'CPI DR low', 'top')):
    ax.plot([i830, xe], [yv, yv], color=LVL, lw=1.4, zorder=3)
    ax.text(i830, yv, lab, color=LVL, fontsize=8, va=va, weight='bold')
ax.plot([i830, xe], [ce, ce], color=LVL, lw=1.1, ls=':', zorder=3)
ax.text(xe + 0.5, ce, f' CPI CE · {od}', color=LVL, fontsize=8.5, va='center', weight='bold')
# ±0.25 of the range beyond its high and low
r25 = (cH - cL) * 0.25
for yv, lab in ((cH + r25, ' CPI DR +0.25 · 62%'), (cL - r25, ' CPI DR −0.25 · 60%')):
    ax.plot([i830, xe], [yv, yv], color=LVL, lw=1.0, ls='--', alpha=0.65, zorder=3)
    ax.text(xe + 0.5, yv, lab, color=LVL, fontsize=8, va='center', alpha=0.9)
# the 08:30 candle box (1-minute)
c1 = g.loc[at(8, 30)]
ax.add_patch(Rectangle((i830 - .45, c1.Low), xe - i830, c1.High - c1.Low, fc=GH, alpha=0.07, ec=GH, lw=0.8, zorder=1))
xr = (c1.High - c1.Low) / ADR
ax.text(xe + 0.5, c1.High, ' CPI 12/08 · ' + ('wild' if xr >= 0.369 else 'quiet' if xr < 0.146 else 'average'), color=GH, fontsize=8, va='bottom')
# RTH gap 50% from 09:30
ro = float(g.loc[at(9, 30), 'Open']); gce = (yc + ro) / 2
ax.plot([i930, xe], [gce, gce], color=LVL, lw=1, ls=':', alpha=0.9)
ax.text(xe + 0.5, gce, ' gap 50%', color=LVL, fontsize=8, va='center')
# candles
for i, (t, r) in enumerate(x.iterrows()):
    c = UP if r.Close >= r.Open else DN
    ax.plot([i, i], [r.Low, r.High], color=c, lw=0.8, zorder=4)
    ax.add_patch(Rectangle((i - .35, min(r.Open, r.Close)), .7, max(abs(r.Close - r.Open), 0.4), fc=c, ec=c, lw=0.3, zorder=5))
# the CPI flag: above the 08:30 bar, stem to the 08:30 open, risen with the push to 09:00
o830 = float(c1.Open)
yF = w.High.max() + 0.12 * ADR
ax.plot([i830, i830], [o830, yF], color=GH, lw=1, ls=':', zorder=6)
ax.text(i830, yF, f'CPI 08:30 · {o830:,.2f}\nhere we go folks', color='#ffffff', fontsize=9, ha='center', va='bottom', weight='bold', zorder=8,
        linespacing=1.35, bbox=dict(boxstyle='round,pad=0.35', fc=GH, ec='none'))
# NQ · ES · RTY vs their week open at 08:30 and 09:30
wk0 = T - pd.Timedelta(days=T.dayofweek + 1) + pd.Timedelta(hours=-6)    # Sunday 18:00
def pct(sym, t):
    bb = bars[sym]
    wo = float(bb[bb.ts >= wk0 + pd.Timedelta(hours=0)].Open.iloc[0])
    r = bb[bb.ts == t]
    return None if not len(r) else (float(r.Open.iloc[0]) / wo - 1) * 100
cell = lambda p: '   —    ' if p is None else ('▲' if p >= 0 else '▼') + f'{abs(p):.2f}%'
def row(tm, t):
    v = [pct(s, t) for s in ('NQ', 'ES', 'RTY')]
    ok = all(p is not None for p in v)
    up = sum(1 for p in v if p is not None and p > 0)
    tg = '' if not ok else 'all ▲' if up == 3 else 'all ▼' if up == 0 else 'SPLIT'
    wk = '' if not ok else ('NQ', 'ES', 'RTY')[int(np.argmin(v))]
    return f'{tm:<7}' + ' '.join(f'{cell(p):<8}' for p in v) + f' {tg:<5}' + (f' weak {wk}' if wk else ''), v
r8, v8 = row('08:30', at(8, 30)); r9, v9 = row('09:30', at(9, 30))
txt = 'vs week open\n' + ' ' * 7 + f'{"NQ":<8} {"ES":<8} {"RTY":<8}\n' + r8 + '\n' + r9
yR = g[(g.index >= at(8, 30)) & (g.index < at(10, 0))].Low.min() - 0.12 * ADR
ax.annotate('', (i830, yR + 0.04 * ADR), (i830, yR), arrowprops=dict(arrowstyle='-', color=SUB, lw=0))
ax.text(i830 - 1, yR, txt, color=TX, fontsize=8.6, family='DejaVu Sans Mono', ha='left', va='top', zorder=8, linespacing=1.4,
        bbox=dict(boxstyle='round,pad=0.45', fc=BODY, ec='#c9ced8' if not DARK else '#2a2e39'))
print('ADR', round(ADR, 1), 'pre', pH, pL, 'sweep', sw, sdir, 'DR', cH, cL, 'CE', ce, 'cd', round(cd, 3), od, 'wk', v8, v9)
fig.text(0.02, 0.965, 'Gran Rey Cero v6 · CPI day Wed 12 Aug 2026, 11:30 ET: the 08:30–09:00 CPI dealing range with its CE and ±0.25 extensions, pre-CPI range, CPI flag, NQ · ES · RTY vs week open',
         color=TX, fontsize=12.5, weight='bold')
fig.text(0.02, 0.942, 'NQ / ES / RTY 1-minute data, NQ1! 5-minute. Cards and PO3 candles unchanged (not drawn here). The readout gains its 09:30 row at the open; '
         'the flag and the readout stay clear of the candles. TradingView rendering will differ.', color=SUB, fontsize=9)
ax.text(0.004, 0.985, 'NQ1! · 5 · CME   Gran Rey Cero   ·   Wed 12 Aug 2026 · CPI · 11:30 ET', transform=ax.transAxes, color=SUB, fontsize=9, va='top')
plt.savefig(OUT, dpi=100, facecolor=BG); print(OUT)
