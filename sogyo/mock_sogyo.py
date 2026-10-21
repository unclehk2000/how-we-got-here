"""Sōgyo mock, NQ1! 5-minute, Fri 2 Oct 2026 at 10:30 ET, light theme (as on your chart): the zone and prior closes, and the
restyled card (Desktop, with the Mobile card beside it). Values computed the way the script computes them."""
import numpy as np, pandas as pd, matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
plt.rcParams['font.family'] = 'DejaVu Sans'; MONO = 'DejaVu Sans Mono'
BG, TX, SUB, MU, BODY, BODY2, NEU = '#ffffff', '#131722', '#4a5163', '#9aa1b2', '#f4f6f9', '#e9edf3', '#d1d4dc'
OK, RED, HOT, ACC = '#2e7d32', '#d32f2f', '#d84315', '#1e88e5'
b = pd.read_pickle('/home/claude/kyw/bars_NQ_all.pkl'); m1 = b.set_index('ts')
hm = lambda s: s.index.hour * 60 + s.index.minute
T = pd.Timestamp('2026-10-02'); P = pd.Timestamp('2026-10-01'); now = T + pd.Timedelta(hours=10, minutes=29)
def rth(day):
    g = m1[(m1.index >= day + pd.Timedelta(hours=9, minutes=30)) & (m1.index < day + pd.Timedelta(hours=16, minutes=15))]; return g
c1 = float(rth(P).Close.iloc[-1]); g2 = m1[(m1.index >= P + pd.Timedelta(hours=9, minutes=30)) & (m1.index < P + pd.Timedelta(hours=17))]; c2 = float(g2.Close.iloc[-1])
O = float(m1.Open[m1.index >= T + pd.Timedelta(hours=9, minutes=30)].iloc[0])
on = m1[(m1.index >= P + pd.Timedelta(hours=18)) & (m1.index < T + pd.Timedelta(hours=9, minutes=30))]; onPts = on.High.max() - on.Low.min()
days = sorted(set(d for d in m1.index.normalize().unique() if d < T and d.dayofweek < 5))
rs = []
for d in days[::-1]:
    g = rth(d)
    if len(g) > 300: rs.append(g.High.max() - g.Low.min())
    if len(rs) == 14: break
atr = float(np.mean(rs))
ce1, ce2 = (c1 + O) / 2, (c2 + O) / 2; cm = (c1 + c2) / 2; gap = abs(O - cm); split = np.sign(O - c1) != np.sign(O - c2)
wide = abs(ce1 - ce2) / O * 100 >= 0.05
gA, oA = gap / atr, onPts / atr
ctx = 'SPLIT — skip' if split else 'RED — waypoint to fill' if gA > 0.68 else 'GREEN — valid confluence' if oA <= 0.45 else "NEUTRAL — don't weight"
cw = ctx.split(' ')[0]; pbg = {'GREEN': OK, 'RED': RED, 'SPLIT': '#ff9800', 'NEUTRAL': '#7e57c2'}[cw]
print(dict(c1=c1, c2=c2, O=O, ce1=ce1, ce2=ce2, gap=gap, onPts=onPts, atr=atr, gA=gA, oA=oA, ctx=ctx, wide=wide))
f = lambda x: f'{x:,.2f}'; fA = lambda x: f'{x:.2f}×'
DESK = [('head', '◆ SŌGYO · CE1 / CE2', cw, '#ffffff', pbg), ('sub', 'formed 09:30 10/02', 'pts', 'ATR'),
        ('row', 'CE1', '16:14 close ↔ 09:30', f(ce1), '', None, None), ('row', 'CE2', '16:59 close ↔ 09:30', f(ce2), '', None, None),
        ('row', 'WIDTH', 'zone' + (' · wide' if wide else ''), f(abs(ce1 - ce2)), f'{abs(ce1 - ce2) / O * 100:.2f}%', None, HOT if wide else None),
        ('row', 'GAP', '09:30 vs prior closes', f(gap), fA(gA), None, RED if gA > 0.68 else None),
        ('row', 'ON', 'overnight 18:00–09:29', f(onPts), fA(oA), None, OK if oA <= 0.45 else None),
        ('row', 'ATR', 'RTH ATR(14)', f(atr), 'red ' + f(0.68 * atr), None, None), ('wide', 'CTX', ctx, pbg)]
MOB = [('head', '◆ SŌGYO · CE1 / CE2', cw, '#ffffff', pbg), ('row', 'CE', f'{f(ce1)} / {f(ce2)}', f(abs(ce1 - ce2)), '', None, None),
       ('row', 'GAP·ON', f'{fA(gA)} · {fA(oA)}', '', '', None, None), ('wide', 'CTX', ctx, pbg)]
FW = 16.0; DPI = 100
def card(fig, rows, x, y, corner='tr', fs=8.4, RH=0.026):
    cw_ = fs * 0.602 / 72 * DPI / (FW * DPI); w = [0, 0, 0, 0]
    for r in rows:
        if r[0] == 'row': w = [max(w[0], len(r[1])), max(w[1], len(r[2])), max(w[2], len(r[3])), max(w[3], len(r[4]))]
        if r[0] == 'sub': w = [w[0], max(w[1], len(r[1])), max(w[2], len(r[2])), max(w[3], len(r[3]))]
    for r in rows:
        if r[0] == 'head':
            w[3] = max(w[3], len(r[2]))
            if len(r[1]) > w[0] + w[1] + w[2] + 2: w[1] = len(r[1]) - w[0] - w[2] - 2
        if r[0] == 'wide' and len(r[2]) > w[1] + w[2] + w[3] + 2: w[1] = len(r[2]) - w[2] - w[3] - 2
    CW = [0.0018] + [(n + 1.6) * cw_ for n in w]; W = sum(CW)
    x0 = x - W if corner[1] == 'r' else x; yy = y
    def cell(c0, c1, txt, fg, bg, bold=False, ha='center'):
        xa = x0 + sum(CW[:c0]); ww = sum(CW[c0:c1 + 1])
        fig.add_artist(Rectangle((xa, yy - RH), ww, RH, transform=fig.transFigure, fc=bg, ec=BG, lw=0.6, zorder=20))
        if txt: fig.text(xa + (0.6 * cw_ if ha == 'left' else ww / 2), yy - RH / 2, txt, color=fg, fontsize=fs, family=MONO, weight='bold' if bold else 'normal', ha=ha, va='center', zorder=21)
    for r in rows:
        cell(0, 0, '', None, ACC)
        if r[0] == 'head': cell(1, 3, r[1], '#ffffff', ACC, True, 'left'); cell(4, 4, r[2], r[3], r[4], True)
        elif r[0] == 'sub': cell(1, 1, '', MU, BODY2); cell(2, 2, r[1], MU, BODY2, False, 'left'); cell(3, 3, r[2], MU, BODY2); cell(4, 4, r[3], MU, BODY2)
        elif r[0] == 'wide': cell(1, 1, r[1], MU, BODY); cell(2, 4, r[2], r[3], BODY, True, 'left')
        else: cell(1, 1, r[1], MU, BODY); cell(2, 2, r[2], TX, BODY, False, 'left'); cell(3, 3, r[3], r[5] or TX, BODY, True); cell(4, 4, r[4], r[6] or MU, BODY)
        yy -= RH
    return x0, W
x = m1[(m1.index >= P + pd.Timedelta(hours=14)) & (m1.index <= now)].resample('5min').agg(dict(Open='first', High='max', Low='min', Close='last')).dropna()
fig = plt.figure(figsize=(FW, 9.6), dpi=DPI, facecolor=BG); ax = fig.add_axes([0.02, 0.06, 0.92, 0.84])
ax.set_facecolor(BG); ax.yaxis.tick_right(); ax.tick_params(axis='y', colors=SUB, labelsize=8); ax.tick_params(axis='x', length=0)
for s_ in ax.spines.values(): s_.set_visible(False)
ax.grid(color='#eef0f3', lw=0.7, zorder=0)
n = len(x); i930 = int(np.searchsorted(x.index, T + pd.Timedelta(hours=9, minutes=30)))
lo, hi = min(x.Low.min(), c1, c2), x.High.max(); pad = hi - lo
ax.set_xlim(-2, n + 70); ax.set_ylim(lo - pad * 0.12, hi + pad * 0.12)
ax.add_patch(Rectangle((i930, min(ce1, ce2)), n - i930, abs(ce1 - ce2), fc=(0.13, 0.59, 0.95, 0.3), ec='#2196f3', lw=1, zorder=2))
ax.text(n + 1, (ce1 + ce2) / 2, f' 09:30 10/02 Sōgyo{" (wide)" if wide else ""}  CE1 {ce1:,.2f} / CE2 {ce2:,.2f}', color=TX, fontsize=8, va='center')
ax.plot([i930, n], [c1, c1], color='#2196f3', lw=1, ls='--'); ax.text(n + 1, c1, ' RTH close 10/01', color=TX, fontsize=8, va='center')
ax.plot([i930, n], [c2, c2], color='#2196f3', lw=1, ls=':'); ax.text(n + 1, c2, ' RTH2 close 10/01', color=TX, fontsize=8, va='center')
for i, (t_, r_) in enumerate(x.iterrows()):
    c = '#089981' if r_.Close >= r_.Open else '#f23645'
    ax.plot([i, i], [r_.Low, r_.High], color=c, lw=0.7, zorder=3)
    ax.add_patch(Rectangle((i - .35, min(r_.Open, r_.Close)), .7, max(abs(r_.Close - r_.Open), 0.5), fc=c, ec=c, lw=0.3, zorder=4))
ticks = [i for i, t_ in enumerate(x.index) if t_.minute == 0 and t_.hour % 2 == 0]
ax.set_xticks(ticks); ax.set_xticklabels([x.index[i].strftime('%H:%M') for i in ticks], color=SUB, fontsize=8)
ax.text(0.005, 0.985, 'NQ1! · 5 · CME   Sōgyo   ·   Fri 2 Oct 2026 · 10:30 ET', transform=ax.transAxes, color=SUB, fontsize=9, va='top')
x0, W = card(fig, DESK, 0.935, 0.885, 'tr')
card(fig, MOB, x0 - 0.012, 0.885, 'tr')
fig.text(0.02, 0.955, 'Sōgyo · restyled card (Desktop right, Mobile left of it), View settings on top, light theme', color=TX, fontsize=12.5, weight='bold')
fig.text(0.02, 0.932, 'NQ 1-minute data. The ATR is read from 15-minute bars, so it is ready on a 1-minute chart. TradingView rendering will differ.', color=MU, fontsize=8.5)
plt.savefig('Sogyo_mock.png', dpi=DPI, facecolor=BG); print('ok')
