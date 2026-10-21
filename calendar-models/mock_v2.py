"""Mock of the rebuilt Gran Rey Cero on NQ, CPI day 11 Sep 2026 at 11:00 ET, 5-minute chart, light theme."""
import pandas as pd, numpy as np, json, matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
plt.rcParams['font.family'] = 'DejaVu Sans'
CK = json.load(open('clock.json'))['NQ']; SH = json.load(open('stats_rows.json'))['rows']['NQ_TD'].split(';')
cpi = [float(v) for v in SH[2].split(',')]; nor = [float(v) for v in SH[6].split(',')]
b = pd.read_pickle('/home/claude/t3/bars_NQ_all.pkl')
D = pd.read_pickle('days_NQ.pkl'); TD = D[D.anchor == 'TD'].set_index('tday')
day = pd.Timestamp('2026-09-11'); prev = pd.Timestamp('2026-09-10')
x = b[b.tday.isin([prev, day])].copy()
x = x[x.ts <= pd.Timestamp('2026-09-11 10:59')]
x5 = x.set_index('ts').resample('5min', label='left').agg(dict(Open='first', High='max', Low='min', Close='last', tday='last')).dropna()
x5 = x5[x5.index >= pd.Timestamp('2026-09-10 12:00')]
n = len(x5); idx = np.arange(n)
td = x5.tday.values == np.datetime64(day)
O = x5.Open[td].iloc[0]; a = TD.loc[day].adr
dH = x5.High[td].max(); dL = x5.Low[td].min(); dC = x5.Close.iloc[-1]
wk = b[(b.tday >= pd.Timestamp('2026-09-08')) & (b.ts <= pd.Timestamp('2026-09-11 10:59'))]
wO, wH, wL, wC = wk.Open.iloc[0], wk.High.max(), wk.Low.min(), wk.Close.iloc[-1]
mR = cpi[10] * a * O; uS = cpi[3] / (cpi[3] + cpi[6]); mH = O + mR * uS; mL = O - mR * (1 - uS); mC = O * (1 + cpi[8] * a)
pv = 20
BG, TX, SUB, MU, BD = '#ffffff', '#131722', '#4a5163', '#9aa1b2', '#d5dae4'
GH = '#e53935'; UP, DN, WK = '#4caf50', '#131722', '#787b86'

fig = plt.figure(figsize=(16, 10.5), facecolor='#f0f3fa')
ax = fig.add_axes([0.04, 0.38, 0.86, 0.58], facecolor='#f0f3fa'); bx = fig.add_axes([0.04, 0.05, 0.86, 0.30], facecolor='#f0f3fa', sharex=ax)
for i, (t, r) in enumerate(x5.iterrows()):
    c = UP if r.Close >= r.Open else '#f23645'
    ax.plot([i, i], [r.Low, r.High], color=c, lw=0.8)
    ax.add_patch(Rectangle((i - 0.35, min(r.Open, r.Close)), 0.7, max(abs(r.Close - r.Open), 0.5), color=c))
# structure: CPI pre-release range 07:30–08:30, gap lines, 08:50 line, hands-off
pr = x[(x.tday == day) & (x.ts.dt.hour * 60 + x.ts.dt.minute >= 450) & (x.ts.dt.hour * 60 + x.ts.dt.minute < 510)]
tpos = lambda ts: np.searchsorted(x5.index.values, np.datetime64(ts))
i730, i830, i850, i930 = tpos('2026-09-11 07:30'), tpos('2026-09-11 08:30'), tpos('2026-09-11 08:50'), tpos('2026-09-11 09:30')
for y, lab in ((pr.High.max(), 'PR high'), (pr.Low.min(), 'PR low')):
    ax.plot([i730, n - 1], [y, y], ls='--', color='#ffb300', lw=1); ax.text(i730, y, lab, color='#ffb300', fontsize=7, va='bottom')
ax.axvspan(i830 - 0.5, i830 + 2.5, color='#f23645', alpha=0.10)
ax.axvline(i850, color='#ffb300', ls=':', lw=0.8, alpha=0.6)
ax.text(i830, x5.High.iloc[i830] + 25, 'CPI', color=GH, fontsize=7, ha='center')
# PO3 slots
widI, gapI, offI = 8, 10, 8; gw = widI + 6; xd = n - 1 + offI; xw = xd + gw + gapI
ax.add_patch(Rectangle((xd + 2, mL), gw - 4, mH - mL, facecolor=GH, alpha=0.10, edgecolor=GH, ls=':', lw=1))
ax.add_patch(Rectangle((xd, min(O, mC)), gw, abs(mC - O), facecolor=GH, alpha=0.30, edgecolor=GH, lw=1))
for y in (mH, mL): ax.plot([xd, xd + gw], [y, y], color=GH, lw=2)
for y in (mH, mL): ax.text(xd - 0.5, y, f'{y:,.2f}', color=GH, fontsize=7, ha='right', va='center')
def candle(x0, w, o, h, l, c):
    ax.plot([x0 + w / 2] * 2, [l, h], color=WK, lw=1)
    ax.add_patch(Rectangle((x0, min(o, c)), w, abs(c - o), facecolor=UP if c >= o else DN, edgecolor=WK, lw=1))
candle(xd + 3, widI, O, dH, dL, dC); candle(xw, widI, wO, wH, wL, wC)
for y in (dH, dL): ax.text(xd + gw + 0.5, y, f'{y:,.2f}', color=SUB, fontsize=7, va='center')
for y in (wH, wL): ax.text(xw + widI + 0.5, y, f'{y:,.2f}', color=SUB, fontsize=7, va='center')
st0 = np.where(td)[0][0]
for y, al in ((O, .7), (dH, .5), (dL, .5)): ax.plot([st0, xd], [y, y], ls=':', color=WK, alpha=al, lw=0.8)
for y in (mH, mL): ax.plot([st0, xd], [y, y], ls=':', color=GH, alpha=.55, lw=0.8)
def chip(xc, y, lines, above=True):
    ax.annotate('\n'.join(lines), (xc, y), xytext=(0, 8 if above else -8), textcoords='offset points', ha='center', va='bottom' if above else 'top', fontsize=7.5, family='DejaVu Sans Mono', color=TX,
                bbox=dict(boxstyle='square,pad=0.35', fc=BG, ec=BD))
chip(xd + gw / 2, max(dH, mH), ['1D · CPI DAY', f'range {dH - dL:,.2f} · ${(dH - dL) * pv:,.0f}', f'model {mR:,.2f} · ${mR * pv:,.0f} · {(dH - dL) / mR * 100:.0f}% filled'])
chip(xw + widI / 2, wL, ['1W', f'range {wH - wL:,.2f} · ${(wH - wL) * pv:,.0f}'], above=False)
ax.set_xlim(n - 230, n + 80); lo = min(x5.Low.iloc[-230:].min(), mL, wL); hi = max(x5.High.iloc[-230:].max(), mH, wH)
ax.set_ylim(lo - 120, hi + 140); ax.yaxis.tick_right(); ax.tick_params(labelsize=8, colors=SUB); ax.grid(alpha=.15)
ax.set_title('Gran Rey Cero · NQ1! · 5m · Fri 11 Sep 2026 11:00 ET (mock)', loc='left', fontsize=10, color=TX)
# profile card (simplified)
pc = ['◆ GRAN REY CERO   NQ   trading day Fri 11 Sep', 'today  M7–8 GRAN REY CERO · CPI 08:30', ' ✓ bigger move went the way of the 1st sweep: 70% (normal 56%)',
      ' ✓ 08:50–11:00 opposed 08:30–08:50: 59% (normal 51%)', ' ✗ RTH gap 50% filled by 10:00: 57% (normal 57%)', ' range  CPI typical 1.05× ADR (0.77–1.32) · normal 0.88×',
      ' macro  DXY 4wk ▲ +0.8% → days ran 1.02× ADR · 10Y …']
ax.text(0.005, 0.02, '\n'.join(pc), transform=ax.transAxes, fontsize=7.2, family='DejaVu Sans Mono', color=TX, va='bottom', bbox=dict(boxstyle='square,pad=0.5', fc=BG, ec=BD))
# ── clock pane: today's running range (points), earlier day faded, CPI bands, normal median
scP = O * a
el = np.array([((t.hour * 60 + t.minute - 1080) % 1440) for t in x5.index]) + 5
rr = []; ph = None
for k, (t, r) in enumerate(x5.iterrows()):
    if k == 0 or x5.tday.iloc[k] != x5.tday.iloc[k - 1]: hh, ll, oo = r.High, r.Low, r.Open
    hh = max(hh, r.High); ll = min(ll, r.Low); rr.append(hh - ll)
rr = np.array(rr)
bx.plot(idx[~td], rr[~td], color=SUB, alpha=.3, lw=1)
st = np.where(td)[0][0]
def pos_of_el(e): return st + (e - el[st] + 5) / 5.0
xs = [pos_of_el(0)] + [pos_of_el(30 * (j + 1)) for j in range(46)]
q = lambda t, k: [0] + [v * scP for v in CK[t]['R'][k]]
bx.fill_between(xs, q('CPI', 0), q('CPI', 4), color=GH, alpha=.10, lw=0)
bx.fill_between(xs, q('CPI', 1), q('CPI', 3), color=GH, alpha=.20, lw=0)
bx.plot(xs, q('CPI', 2), color=GH, lw=2); bx.plot(xs, q('NORMAL', 2), color=MU, lw=1, ls='--')
bx.text(xs[-1], q('CPI', 2)[-1], f' CPI median {q("CPI", 2)[-1]:,.2f}', color=GH, fontsize=7, va='center')
bx.text(xs[-1], q('NORMAL', 2)[-1], f' Normal {q("NORMAL", 2)[-1]:,.2f}', color=MU, fontsize=7, va='center')
# today's line coloured by status
jB = min(45, int(np.ceil(min(1380, el[-1]) / 30)) - 1); f = (min(1380, el[-1]) - 30 * jB) / 30
qi = lambda k: (CK['CPI']['R'][k][jB - 1] if jB > 0 else 0) + (CK['CPI']['R'][k][jB] - (CK['CPI']['R'][k][jB - 1] if jB > 0 else 0)) * f
v = rr[-1] / scP; stt = 'ABOVE' if v > qi(3) else 'BELOW' if v < qi(1) else 'INSIDE'
bx.plot(idx[td], rr[td], color={'ABOVE': '#d84315', 'BELOW': '#1565c0', 'INSIDE': TX}[stt], lw=2.5)
bx.axvline(pos_of_el(870), color=GH, ls=':', lw=1, alpha=.7)
bx.yaxis.tick_right(); bx.tick_params(labelsize=8, colors=SUB); bx.grid(alpha=.15); bx.set_ylim(0, max(q('CPI', 4)) * 1.15)
ticks = [k for k in range(n) if x5.index[k].minute == 0 and x5.index[k].hour % 3 == 0]
bx.set_xticks(ticks); bx.set_xticklabels([x5.index[k].strftime('%H:%M') for k in ticks])
bx.text(0.005, 0.97, 'Gran Rey Cero · event clock', transform=bx.transAxes, fontsize=8, color=SUB, va='top')
sh = (CK['CPI']['share'][jB - 1]) + (CK['CPI']['share'][jB] - CK['CPI']['share'][jB - 1]) * f
cc = [f'◆ GRAN REY CERO CLOCK · NQ · CPI day', f'now 11:00  range {rr[-1]:,.2f} pts · {v:.2f}× ADR · {"▲" if stt=="ABOVE" else "▼" if stt=="BELOW" else "●"} {stt}',
      f'typical   CPI days by 11:00: {qi(2) * scP:,.2f} (middle half {qi(1) * scP:,.2f} to {qi(3) * scP:,.2f})',
      f'done      CPI days had made {sh * 100:.0f}% of their range by now → today ≈ {rr[-1] / sh:,.2f} · ${rr[-1] / sh * pv:,.0f}',
      f'full day  CPI median {CK["CPI"]["R"][2][45]:.2f}× ADR = {CK["CPI"]["R"][2][45] * scP:,.2f} · normal {CK["NORMAL"]["R"][2][45]:.2f}×',
      f'busiest   CPI days: 08:30–09:00 adds 0.20× ADR to the median range (normal 0.02×)', f'paths from {CK["CPI"]["n"]} CPI days and {CK["NORMAL"]["n"]} normal days, 2018–26 · ADR20 {scP:,.2f} pts']
bx.text(0.005, 0.86, '\n'.join(cc), transform=bx.transAxes, fontsize=7.2, family='DejaVu Sans Mono', color=TX, va='top', ha='left', bbox=dict(boxstyle='square,pad=0.5', fc=BG, ec=BD))
for s_ in ('top', 'left', 'right', 'bottom'): ax.spines[s_].set_color(BD); bx.spines[s_].set_color(BD)
plt.setp(ax.get_xticklabels(), visible=False)
fig.savefig('mock_v2_cpi.png', dpi=110)
print('ok', O, a, mR, dH - dL, stt, v, sh)
