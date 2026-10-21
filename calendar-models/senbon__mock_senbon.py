"""Mock: Senbonzakura on ES1! 5-minute, Thu 27 Aug 2026 at 13:00 ET, trading-day close. Same maths as the script:
historical quantile row for the half hour (ADR20 units) around the last price, VIX prior close for the implied bell."""
import sys, json, math, numpy as np, pandas as pd, matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Polygon
from scipy.stats import norm
plt.rcParams['font.family'] = 'DejaVu Sans'
BG, TX, MU, SUB = '#0e1117', '#e6e9ef', '#8b93a5', '#5d6476'
CH, CI = '#f06292', '#2962ff'; UPC, DNC = '#089981', '#f23645'
R = json.load(open('/home/claude/hm/senbon/dist.json'))
M = json.load(open('/home/claude/hm/senbon/ctx_model2.json'))
CX = pd.read_pickle(f'/home/claude/hm/senbon/ctx_ES.pkl')
QL = np.array([0.01, 0.025, 0.05, 0.1, 0.15, 0.2, 0.25, 0.3, 0.35, 0.4, 0.45, 0.5, 0.55, 0.6, 0.65, 0.7, 0.75, 0.8, 0.85, 0.9, 0.95, 0.975, 0.99])
SYM, DAY, HM = 'ES', pd.Timestamp('2026-08-27'), (13, 0)
b = pd.read_pickle(f'/home/claude/kyw/bars_{SYM}_all.pkl')
D = pd.read_pickle(f'/home/claude/hm/senbon/days_{SYM}.pkl')
adr = D.loc[DAY, 'adr']
g = b[b.tday == DAY].copy(); g = g[g.ts < pd.Timestamp(DAY.date()) + pd.Timedelta(hours=HM[0], minutes=HM[1])]
g = g.set_index('ts')[['Open', 'High', 'Low', 'Close']].resample('5min').agg({'Open': 'first', 'High': 'max', 'Low': 'min', 'Close': 'last'}).dropna()
g = g[g.index >= pd.Timestamp(DAY.date()) + pd.Timedelta(hours=4)]
P = g.Close.iloc[-1]
vix = pd.read_csv('/home/claude/mac/vix_daily.csv', parse_dates=['DATE']).set_index('DATE').CLOSE
iv = vix[vix.index < DAY].iloc[-1]
e = (HM[0] * 60 + HM[1] - 1080) % 1440; tgtM = 1380
j = min(45, e // 30); tN = min(30 * (j + 1), tgtM); zN = 30 * (j + 1) >= tgtM; w = (e - 30 * j) / (tN - 30 * j)
Q = np.array(M['sym'][SYM]['q_TD']) / 1000; F = np.array(R[SYM]['C_TD']['f']) / 1000
row = Q[j] + ((0 if zN else Q[j + 1]) - Q[j]) * w
c = CX.loc[DAY]; pdh, pdl, mo = c.PDH, c.PDL, c.MO
dH = b[(b.tday == DAY) & (b.ts < pd.Timestamp(DAY.date()) + pd.Timedelta(hours=HM[0], minutes=HM[1]))].High.max()
ath = max(c.ATHp, dH)
z = np.array([P > pdh, P < pdl, np.clip((mo - P) / adr, 0, 3), np.clip((P - mo) / adr, 0, 3), (ath - P) / adr <= 0.5], float)
blk = 0 if j <= 17 else 1 if j <= 30 else 2 if j <= 35 else 3
beta = np.array(M['sym'][SYM]['beta'][M['blocks'][blk]])
sCtx = float(np.exp(beta @ z))
med = row[11]
xs = list(P + adr * (med + (row - med) * sCtx)); ps = list(QL)
print('context', dict(PDH=pdh, PDL=pdl, MO=mo, ATH=ath, z=z.tolist(), scale=round(sCtx, 3)))
xs = [xs[0] - 2 * (xs[1] - xs[0])] + xs + [xs[-1] + 2 * (xs[-1] - xs[-2])]; ps = [0.0] + ps + [1.0]
cdf = lambda v: float(np.interp(v, xs, ps))
qinv = lambda p: float(np.interp(p, ps, xs))
f = F[j] + ((0 if zN else F[j + 1]) - F[j]) * w
sg = iv / 100 / math.sqrt(252) * math.sqrt(f)
tick, nBin, lenI, offI = 0.25, 40, 60, 6
lo = min(xs[1], P * math.exp(-2.326 * sg)); hi = max(xs[-2], P * math.exp(2.326 * sg))
bw = math.ceil(max(tick, (hi - lo) / nBin) / tick) * tick; b0 = math.floor(lo / bw) * bw; nb = int(math.ceil((hi - b0) / bw))
pH = np.array([cdf(b0 + (i + 1) * bw) - cdf(b0 + i * bw) for i in range(nb)])
pI = np.array([norm.cdf(math.log((b0 + (i + 1) * bw) / P) / sg) - norm.cdf(math.log((b0 + i * bw) / P) / sg) for i in range(nb)])
# display smoothing of the historical bars: 1-4-6-4-1 over neighbouring bins (mass kept; bands use the exact CDF)
k5 = np.array([1, 4, 6, 4, 1]) / 16
pH = np.convolve(np.pad(pH, 2), k5, mode='valid')
pmax = max(pH.max(), pI.max()); iMax = int(np.argmax(np.maximum(pH, pI)))
h10, h25, h50, h75, h90 = (qinv(p) for p in (0.1, 0.25, 0.5, 0.75, 0.9))
i10, i90 = P * math.exp(-1.2816 * sg), P * math.exp(1.2816 * sg)
print(f'P {P} adr {adr:.2f} VIX {iv} f {f:.3f} sg {sg:.5f} bw {bw} nb {nb} | hist 80% {h10:.2f}–{h90:.2f} median {h50:.2f} up {1-cdf(P):.3f} | impl 80% {i10:.2f}–{i90:.2f} ratio {(i90-i10)/(h90-h10):.2f}')
print('actual close', D.loc[DAY, 'C_TD'])
n = len(g); x0 = n - 1 + offI
fig, ax = plt.subplots(figsize=(17, 9.6), dpi=100, facecolor=BG); ax.set_facecolor(BG)
for i, (t, r) in enumerate(g.iterrows()):
    c = UPC if r.Close >= r.Open else DNC
    ax.plot([i, i], [r.Low, r.High], color=c, lw=0.8); ax.add_patch(Rectangle((i - .35, min(r.Open, r.Close)), .7, max(abs(r.Close - r.Open), 0.1), fc=c, ec=c, lw=0.3))
# implied bell
ys = b0 + (np.arange(nb) + 0.5) * bw
d = np.exp(-0.5 * (np.log(ys / P) / sg) ** 2) / (math.sqrt(2 * math.pi) * sg * ys) * bw
poly = [(x0, b0)] + [(x0 + round(v / pmax * lenI), y) for v, y in zip(d, ys)] + [(x0, b0 + nb * bw)]
ax.add_patch(Polygon(poly, closed=True, fc=CI, alpha=0.15, ec='none'))
ax.plot([p[0] for p in poly[1:-1]], [p[1] for p in poly[1:-1]], color=CI, lw=2)
# historical bars
for i in range(nb):
    L = round(pH[i] / pmax * lenI)
    if L >= 1: ax.add_patch(Rectangle((x0, b0 + i * bw), L, bw, fc=CH, alpha=0.45, ec=CH, lw=0.8))
ax.plot([n - 1, x0 + lenI + 2], [P, P], color=TX, alpha=0.55, lw=0.9, ls=':')
ax.plot([x0 - 2, x0 - 2], [h10, h90], color=CH, alpha=0.65, lw=1); ax.plot([x0 - 2, x0 - 2], [h25, h75], color=CH, lw=4)
ax.plot([x0, x0 + lenI], [h50, h50], color=CH, lw=1, ls='--')
ax.plot([x0 - 4, x0 - 4], [i10, i90], color=CI, alpha=0.7, lw=2)
fs = 8.5
ax.text(x0 - 2.6, h90, f'80% {h90:,.2f}', color=CH, fontsize=fs, ha='right', va='center')
ax.text(x0 - 2.6, h10, f'80% {h10:,.2f}', color=CH, fontsize=fs, ha='right', va='center')
ax.text(x0 + lenI + 0.6, h50, f'median {"+" if h50 >= P else "−"}{abs(h50 - P):.2f}', color=CH, fontsize=fs, va='center')
LV = [('PDH', pdh, '--'), ('PDL', pdl, '--'), ('MO', mo, ':'), ('ATH', ath, '-')]
lvT = []
for nm, lv, ls in LV:
    up_ = lv >= P
    ph = (1 - cdf(lv)) if up_ else cdf(lv)
    pi_ = (1 - norm.cdf(math.log(lv / P) / sg)) if up_ else norm.cdf(math.log(lv / P) / sg)
    od = f"{'▲' if up_ else '▼'}{100 * ph:.0f} / {100 * pi_:.0f}%"
    lvT.append(f'{nm} {lv:,.2f} {od}')
    if b0 <= lv <= b0 + nb * bw:
        ax.plot([x0 - 6, x0 + lenI], [lv, lv], color='#ffb300', lw=1, ls=ls, alpha=0.85)
        ax.text(x0 - 6.6, lv, f'{nm} {od}', color='#ffb300', fontsize=8, ha='right', va='center')
ax.text(x0 + lenI + 0.6, b0 + (iMax + 0.5) * bw + 2 * bw, f'{pmax * 100:.1f}% per {bw:.2f}', color=MU, fontsize=7.5, va='center')
left = tgtM - e
hdr = (f'SENBONZAKURA · ES · close 17:00 · {left // 60}h {left % 60:02d}m left\n'
       f'historical  up {100 * (1 - cdf(P)):.0f}% · 80% {h10:,.2f} – {h90:,.2f}\n'
       f'implied (VIX {iv:.1f})  80% {i10:,.2f} – {i90:,.2f} · {(i90 - i10) / (h90 - h10):.1f}× wider\n'
       f'context  width ×{sCtx:.2f}' + (' · ' + ' · '.join(x for x in [('above PDH' if z[0] else ''), ('below PDL' if z[1] else ''), (f'{z[2]:.1f} ADR under MO' if z[2] > 0 else f'{z[3]:.1f} ADR over MO' if z[3] > 0 else ''), ('at the ATH' if z[4] else '')] if x) if z.any() else ' · inside PD range, at MO') + '\n' + ' · '.join(lvT))
ax.text(x0, b0 + nb * bw + bw, hdr, color=TX, fontsize=8.8, family='DejaVu Sans Mono', va='bottom', ha='left',
        bbox=dict(boxstyle='round,pad=0.45', fc='#161a23', ec='#2a2f3a'))
ax.set_xlim(-2, x0 + lenI + 26)
ylo, yhi = min(g.Low.min(), b0) - 2 * bw, b0 + nb * bw + 9 * bw
ax.set_ylim(ylo, yhi)
ax.yaxis.tick_right(); ax.tick_params(colors=SUB, labelsize=8); ax.grid(color='#1a1f2b', lw=0.6)
for s_ in ax.spines.values(): s_.set_color('#1c2130')
tk = [i for i, t in enumerate(g.index) if t.minute == 0 and t.hour % 1 == 0]
ax.set_xticks(tk); ax.set_xticklabels([g.index[i].strftime('%H:%M') for i in tk], color=SUB, fontsize=8)
ax.text(0.005, 0.985, 'ES1! · 5 · CME   Senbonzakura', transform=ax.transAxes, color=MU, fontsize=9, va='top')
fig.text(0.03, 0.965, 'Senbonzakura: where today\'s close is likely to land, with market structure (PDH · PDL · monthly open · ATH)', color=TX, fontsize=13, weight='bold')
fig.text(0.03, 0.94, f'ES1! 5-minute, Thu 27 Aug 2026 at 13:00 ET. Pink: 2018–26 ES days at this half hour, ×ADR20 {adr:.2f} pts. Blue: VIX prior close {iv:.2f} ÷ √252 × √({f:.2f} of the day still ahead). TradingView rendering will differ.', color=MU, fontsize=8.3)
fig.subplots_adjust(left=0.02, right=0.95, top=0.92, bottom=0.05)
plt.savefig(sys.argv[1], dpi=100, facecolor=BG); print(sys.argv[1])
