"""Domain Expansion v10 mock (built on the v9 mock helpers) on NQ1! 5-minute, Fri 9 Oct 2026 (CBDR only; London expanded up; the London low was the domain low).
Light chart, chart text black, cards on the Dark card theme: the setup that hid the card text in v8.
(A) live at 03:40 ET: pre-London range (00:00–00:59, lines to 02:00, CE), domain range, SD lines, break mark, London card.
(B) 11:15 ET: London done; London high / low carried to 11:00; labels that meet at 05:00 kept off each other's lines;
    FOLLOW row; recent sessions. Values computed the way Domain_Expansion_Indicator.pine computes them.
python3 mock_de9.py A.png B.png"""
import sys, json
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

OUTA = sys.argv[1]
BG, MU, GRID = '#ffffff', '#9aa1b2', '#eef1f6'
CHT = '#000000'                                   # chart text colour (the user's black)
CB, CT, CS = '#161a23', '#d1d4dc', '#8a93a6'      # card body / text / sub on the Dark card theme
UP, DN = '#089981', '#f23645'
PLC = '#2962ff'
TIERC = {3: '#ff6d00', 2: '#ffb300', 1: '#00acc1', 0: '#787b86'}
TIERN = {3: 'BOTH', 2: 'COILED', 1: 'CBDR', 0: 'NEITHER'}
lum = lambda h: 0.299 * int(h[1:3], 16) + 0.587 * int(h[3:5], 16) + 0.114 * int(h[5:7], 16)
hdrTx = lambda h: '#131722' if lum(h) > 165 else '#ffffff'
P = json.load(open('/home/claude/dx/lon_pine.json'))
T = {k: np.array([float(x) for x in v.split(',')]) for k, v in P.items()}
R = pd.read_pickle('/home/claude/dx/lon_rows.pkl')
R = R[R.sym == 'NQ'].copy()
R['tier'] = np.where((R.coil <= 0.2) & (R.cbR >= 5), 3, np.where(R.coil <= 0.2, 2, np.where(R.cbR >= 5, 1, 0)))
DAY = pd.Timestamp('2026-10-09')
r = R[R.tday == DAY].iloc[0]
b = pd.read_pickle('/home/claude/kyw/bars_NQ_all.pkl')
g = b[b.tday == DAY].set_index('ts')
D0 = DAY.normalize()
at = lambda h, m: D0 + pd.Timedelta(hours=h, minutes=m)
stamp = lambda t: t.strftime('%H:%M %m/%d')
dr = g[(g.index >= at(2, 0)) & (g.index < at(2, 30))]
dH, dL = dr.High.max(), dr.Low.min(); rD = dH - dL
dHt, dLt = dr.High.idxmax(), dr.Low.idxmin()
tier = int(r.tier); tc = TIERC[tier]
coil, cbR, atr = r.coil, r.cbR, r.atr
coiled = coil <= 0.2
lrE = 1.794 * rD ** 0.497 * atr ** 0.437
pr = g[(g.index >= at(0, 0)) & (g.index < at(1, 0))]
pH, pL = pr.High.max(), pr.Low.min(); pCE = (pH + pL) / 2
pHt, pLt = pr.High.idxmax(), pr.Low.idxmin()
SDS = (2.0, 2.5, 3.0, 4.0)


def tbl(a, ncol, pos, col):
    p = max(0.0, min(9.0, pos)); i0 = int(np.floor(p)); i1 = min(9, i0 + 1); f = p - i0
    return a[i0 * ncol + col] * (1 - f) + a[i1 * ncol + col] * f


def bucket(d):
    return 0 if d < 0.25 else 1 if d < 0.5 else 2 if d < 1 else 3 if d < 2 else 4


def chart(ax, x):
    for s_ in ax.spines.values():
        s_.set_visible(False)
    ax.set_facecolor(BG); ax.yaxis.tick_right(); ax.tick_params(axis='y', colors=MU, labelsize=8.5); ax.tick_params(axis='x', length=0)
    ax.grid(color=GRID, lw=0.7, zorder=0)
    for i, (t, q) in enumerate(x.iterrows()):
        c = UP if q.Close >= q.Open else DN
        ax.plot([i, i], [q.Low, q.High], color=c, lw=0.8, zorder=4)
        ax.add_patch(Rectangle((i - 0.33, min(q.Open, q.Close)), 0.66, max(abs(q.Close - q.Open), 0.25), fc=c, ec=c, lw=0.2, zorder=5))
    ticks = [i for i, t in enumerate(x.index) if t.minute == 0]
    ax.set_xticks(ticks); ax.set_xticklabels([x.index[i].strftime('%H:%M') for i in ticks], color=MU, fontsize=8.5)


def label(ax, xv, y, txt, where='mid', col=CHT, fs=7.3):
    """Pine label: style_label_left (centred on the level), lower_left (text above it), upper_left (text below it)"""
    off = {'mid': 0, 'above': rD * 0.05, 'below': -rD * 0.05}[where]
    ax.text(xv + 0.4, y + off, txt, color=col, fontsize=fs, va={'mid': 'center', 'above': 'bottom', 'below': 'top'}[where], zorder=8, clip_on=True)


def away(y, other, above, pre=False):
    return 'above' if (y > other or (y == other and ((not above) if pre else above))) else 'below'


def card(fig, x0, y0, rows, head, pill, col, w=0.33):
    lh = 0.026
    ht = hdrTx(col)
    fig.patches.append(Rectangle((x0, y0 - lh), w, lh, transform=fig.transFigure, fc=col, ec='none', zorder=10))
    fig.text(x0 + 0.006, y0 - lh / 2, head, color=ht, fontsize=8.6, family='DejaVu Sans Mono', va='center', weight='bold', zorder=11)
    fig.patches.append(Rectangle((x0 + w - 0.062, y0 - lh + 0.004), 0.056, lh - 0.008, transform=fig.transFigure,
                                 fc='#131722' if lum(col) > 165 else '#ffffff', ec='none', zorder=11))
    fig.text(x0 + w - 0.034, y0 - lh / 2, pill, color=col, fontsize=8, family='DejaVu Sans Mono', va='center', ha='center', weight='bold', zorder=12)
    for k, (a, bb, cc, hl) in enumerate(rows):
        yy = y0 - lh * (k + 2)
        fig.patches.append(Rectangle((x0, yy), w, lh, transform=fig.transFigure, fc=CB, ec='none', zorder=10))
        fig.text(x0 + 0.006, yy + lh / 2, a, color=CS, fontsize=8.2, family='DejaVu Sans Mono', va='center', zorder=11)
        fig.text(x0 + 0.055, yy + lh / 2, bb, color=col if hl else CT, fontsize=8.2, family='DejaVu Sans Mono', va='center', zorder=11)
        fig.text(x0 + w - 0.006, yy + lh / 2, cc, color=col if hl else CT, fontsize=8.2, family='DejaVu Sans Mono', va='center', ha='right', zorder=11)
    fig.patches.append(Rectangle((x0, y0 - lh * (len(rows) + 1)), w, lh * (len(rows) + 1), transform=fig.transFigure, fc='none', ec=col, lw=1, zorder=12))


def history(fig, upto, x0=0.635, y0=0.42, w=0.33):
    H = R[R.tday <= upto].tail(10).iloc[::-1]
    lh = 0.024
    cols = [0.006, 0.135, 0.19, 0.268, 0.324]
    fig.patches.append(Rectangle((x0, y0 - lh), w, lh, transform=fig.transFigure, fc='#5e35b1', ec='none', zorder=10))
    res = [(1 if (d.up >= 2 and d.up >= d.dn) else -1 if (d.dn >= 2 and d.dn > d.up) else 0) for _, d in H.iterrows()]
    fig.text(x0 + 0.006, y0 - lh / 2, 'LONDON   last 10', color='#ffffff', fontsize=8.4, family='DejaVu Sans Mono', va='center', weight='bold', zorder=11)
    fig.text(x0 + w - 0.006, y0 - lh / 2, f'{sum(v != 0 for v in res)}/10 expanded', color='#ffffff', fontsize=8.4, family='DejaVu Sans Mono', va='center', ha='right', zorder=11)
    hdr = ['day', 'tier', '05:00', 'furthest', 'range']
    body = [[f'{d.tday:%a %d}', TIERN[int(d.tier)], '▲ ✓' if rv == 1 else '▼ ✓' if rv == -1 else '✗',
             ('▲ ' if d.up >= d.dn else '▼ ') + f'{max(d.up, d.dn, 0):.1f} SD', f'{d.lr:.0f} pts'] for (_, d), rv in zip(H.iterrows(), res)]
    for k, row in enumerate([hdr] + body):
        yy = y0 - lh * (k + 2)
        fig.patches.append(Rectangle((x0, yy), w, lh, transform=fig.transFigure, fc=CB, ec='none', zorder=10))
        for j, v in enumerate(row):
            if k == 0:
                colr = CS
            else:
                tcI = TIERC[int(H.iloc[k - 1].tier)]
                colr = tcI if j == 1 else (tcI if res[k - 1] != 0 else CS) if j == 2 else CT
            fig.text(x0 + cols[j], yy + lh / 2, v, color=colr, fontsize=8, family='DejaVu Sans Mono', va='center', ha='left' if j == 0 else 'right', zorder=11)
    fig.patches.append(Rectangle((x0, y0 - lh * (len(H) + 2)), w, lh * (len(H) + 2), transform=fig.transFigure, fc='none', ec='#787b86', lw=1, zorder=12))


def prelondon(ax, ix, x02):
    """00:00–00:59 range, lines from 00:00 to 02:00, dashed once traded through after 01:00; labels at 02:00 kept off the domain lines"""
    a = ix(at(0, 0))
    after = g[(g.index >= at(1, 0)) & (g.index < at(2, 0))]
    dom = [dH, dL, (dH + dL) / 2] + [dH + k * rD for k in SDS] + [dL - k * rD for k in SDS]
    for y, nm, t, above, watch, ls, al in ((pH, 'Pre-London high', pHt, True, True, '-', 1), (pL, 'Pre-London low', pLt, False, True, '-', 1),
                                           (pCE, 'Pre-London CE', at(0, 0), True, False, ':', 0.7)):
        hit = watch and ((after.High >= y).any() if above else (after.Low <= y).any())
        ax.plot([a, x02], [y, y], color=PLC, lw=1, ls='--' if hit else ls, alpha=al, zorder=3)
        near = [d for d in dom if abs(d - y) <= 0.25 * rD]
        where = away(y, min(near, key=lambda d: abs(d - y)), above, pre=True) if near else 'mid'
        label(ax, x02, y, nm, where)
    return dom



# ── v10 at 11:15 on 1-minute: notes on; the tier note moved below the range after the up-break; the break label at its candle;
#    the 05:00 note (with the follow-through) above the London high, box to the left of 05:00
NOW = at(11, 15)
x = g[(g.index >= at(1, 30)) & (g.index < NOW)]
ix = lambda t: float(np.searchsorted(x.index, t))
n = len(x)
fig = plt.figure(figsize=(18, 10.4), dpi=100, facecolor=BG)
ax = fig.add_axes([0.02, 0.05, 0.60, 0.85])
for s_ in ax.spines.values():
    s_.set_visible(False)
ax.set_facecolor(BG); ax.yaxis.tick_right(); ax.tick_params(axis='y', colors=MU, labelsize=8.5); ax.tick_params(axis='x', length=0)
ax.grid(color=GRID, lw=0.7, zorder=0)
for i, (t, q) in enumerate(x.iterrows()):
    c = UP if q.Close >= q.Open else DN
    ax.plot([i, i], [q.Low, q.High], color=c, lw=0.5, zorder=4)
    ax.plot([i, i], [q.Open, q.Close], color=c, lw=1.1, zorder=5, solid_capstyle='butt')
ticks = [i for i, t in enumerate(x.index) if t.minute == 0]
ax.set_xticks(ticks); ax.set_xticklabels([x.index[i].strftime('%H:%M') for i in ticks], color=MU, fontsize=8.5)
x00, x02, x5, x11 = 0, ix(at(2, 0)), ix(at(5, 0)), ix(at(11, 0))
# pre-London lines from 00:00 (off the left edge) to 02:00
after = g[(g.index >= at(1, 0)) & (g.index < at(2, 0))]
dom = [dH, dL, (dH + dL) / 2] + [dH + k * rD for k in SDS] + [dL - k * rD for k in SDS]
for y, nm, above, watch, ls, al in ((pH, 'Pre-London high', True, True, '-', 1), (pL, 'Pre-London low', False, True, '-', 1), (pCE, 'Pre-London CE', True, False, ':', 0.7)):
    hit = watch and ((after.High >= y).any() if above else (after.Low <= y).any())
    ax.plot([x00, x02], [y, y], color=PLC, lw=1, ls='--' if hit else ls, alpha=al, zorder=3)
    near = [d for d in dom if abs(d - y) <= 0.25 * rD]
    label(ax, x02, y, nm, away(y, min(near, key=lambda d: abs(d - y)), above, pre=True) if near else 'mid')
ax.add_patch(Rectangle((x02, dL), ix(at(2, 30)) - x02, rD, fc=tc, alpha=0.12, ec='none', zorder=1))
ax.axvspan(ix(at(2, 30)), ix(at(2, 50)), color=tc, alpha=0.10, lw=0)
lon = g[(g.index >= at(2, 0)) & (g.index < at(5, 0))]
post = g[(g.index >= at(2, 30)) & (g.index < at(5, 0))]
lH5, lL5 = lon.High.max(), lon.Low.min()
DOM = [(dH, f'{stamp(dHt)} Domain high', '-', True, True, 1), (dL, f'{stamp(dLt)} Domain low', '-', False, True, 1),
       ((dH + dL) / 2, f'{stamp(at(2, 0))} Domain 0.5', ':', True, False, 0.6)] + \
      [(dH + k * rD, f'+{k:.1f} SD' + (' · expansion' if k == 2 else ''), ':', True, True, 0.55) for k in SDS] + \
      [(dL - k * rD, f'−{k:.1f} SD' + (' · expansion' if k == 2 else ''), ':', False, True, 0.55) for k in SDS]
for y, lab, ls, above, watch, al in DOM:
    hit = watch and ((post.High >= y).any() if above else (post.Low <= y).any())
    ax.plot([x02, x5], [y, y], color=tc, lw=1.1 if ls == '-' else 0.9, ls='--' if hit else ls, alpha=al, zorder=3)
    others = [d[0] for d in DOM if d[0] != y] + [lH5, lL5]
    near = [o for o in others if abs(o - y) <= 0.25 * rD]
    label(ax, x5, y, lab, away(y, min(near, key=lambda o: abs(o - y)), above) if near else 'mid')
ny = g[(g.index >= at(5, 0)) & (g.index < at(11, 0))]
tH = ny.index[ny.High > lH5]; tL = ny.index[ny.Low < lL5]
nyHt = tH[0] if len(tH) else None; nyLt = tL[0] if len(tL) else None
for y, nm, taken in ((lH5, 'London high', nyHt), (lL5, 'London low', nyLt)):
    ax.plot([x5, x11], [y, y], color=tc, lw=2, ls='--' if taken is not None else '-', zorder=3)
    label(ax, x11, y, f'{nm} · taken {taken:%H:%M}' if taken is not None else f'{nm} · not taken by 11:00', fs=7.8)
xu = ix(at(3, 0))
ax.axvline(xu, color='#9e9e9e', lw=0.8, ls=':', zorder=2)
NB = dict(boxstyle='round,pad=0.3', fc=tc, alpha=0.2, ec='none')
# notes
ex = g[(g.index >= at(2, 30)) & (g.index < at(2, 50))]
fb = ex[(ex.High > dH) | (ex.Low < dL)].index[0]
bUp = ex.loc[fb].High > dH
both = bUp and ex.loc[fb].Low < dL
bTx = ('Both sides ' if both else '▲ Break ' if bUp else '▼ Break ') + f'{fb:%H:%M}'
fy = ex.loc[fb].High if bUp else ex.loc[fb].Low
ax.annotate(bTx, (ix(fb), fy), xytext=(0, 9 if bUp else -9), textcoords='offset points', ha='center', va='bottom' if bUp else 'top',
            color=CHT, fontsize=7.4, bbox=NB, zorder=9, arrowprops=dict(arrowstyle='-', color=tc, lw=0.8))
atrP = rD / coil
tierTx = f'◆ Domain Expansion: CBDR only · 2 SD odds ~35%\nCoil {coil:.2f} ({rD:.0f} ÷ {atrP:.0f} pts) ✗\nCBDR {cbR * rD:.0f} pts · {cbR:.1f} ranges ✓'
yT, vaT, offT = (min(dL, pL), 'top', -9) if bUp else (max(dH, pH), 'bottom', 9)   # beyond the pre-London range (its labels sit at 02:00)
ax.annotate(tierTx, (ix(at(2, 30)), yT), xytext=(0, offT), textcoords='offset points', ha='center', va=vaT, color=CHT, fontsize=7.4, bbox=NB, zorder=9,
            arrowprops=dict(arrowstyle='-', color=tc, lw=0.8))
c5 = lon.Close.iloc[-1]
up5, dn5 = (post.High.max() - dH) / rD, (dL - post.Low.min()) / rD
resV = 1 if (up5 >= 2 and up5 >= dn5) else -1 if (dn5 >= 2 and dn5 > up5) else 0
far5 = lambda p: 'inside the range' if dL <= p <= dH else (f'{(p - dH) / rD:.2f} SD ({100 * (p - dH) / dH:.2f}%) above' if p > dH else f'{(dL - p) / rD:.2f} SD ({100 * (dL - p) / dL:.2f}%) below')
c7 = g[g.index < at(7, 0)].Close.iloc[-1]
resTx = (('✓ Domain Expansion ▲' if resV == 1 else '✓ Domain Expansion ▼' if resV == -1 else '✗ No expansion') +
         f'\nextreme {max(up5, dn5):.2f} SD ' + ('above' if up5 >= dn5 else 'below') + f' · close {far5(c5)}' +
         f'\nLondon {lH5 - lL5:.0f} pts · {(lH5 - lL5) / r.adr:.2f} ADR\nFollow-through 07:00 · close {far5(c7)}')
yR, vaR, offR = (lL5, 'top', -6) if not bUp else (lH5, 'bottom', 6)
ax.annotate(resTx, (x5, yR), xytext=(-2, offR), textcoords='offset points', ha='right', va=vaR, color=CHT, fontsize=7.4, bbox=NB, zorder=9,
            arrowprops=dict(arrowstyle='-', color=tc, lw=0.8))
lo, hi = x.Low.min(), x.High.max()
ax.set_xlim(-2, n + 150); ax.set_ylim(lo - (hi - lo) * 0.06, hi + (hi - lo) * 0.22)
s7 = (c7 - dH) / rD if c7 > dH else -(dL - c7) / rD if c7 < dL else 0
ftTx = 'close inside the range' if s7 == 0 else f'close {abs(s7):.2f} SD ' + ('above' if s7 > 0 else 'below')
resSD = max(up5, 0) if up5 >= dn5 else -dn5
rows = [('RESULT', '▲ expansion' if resV == 1 else '▼ expansion' if resV == -1 else 'no expansion', ('▲ ' if resSD >= 0 else '▼ ') + f'{abs(resSD):.1f} SD', resV != 0),
        ('RANGE', f'London {lH5 - lL5:.0f} pts', f'{(lH5 - lL5) / r.adr:.2f} ADR', False),
        ('FOLLOW', ftTx, '07:00', False),
        ('NY HIGH', f'{lH5:,.2f}', f'taken {nyHt:%H:%M}' if nyHt is not None else 'not taken', nyHt is not None),
        ('NY LOW', f'{lL5:,.2f}', f'taken {nyLt:%H:%M}' if nyLt is not None else 'not taken', nyLt is not None)]
card(fig, 0.635, 0.885, rows, ('✓' if resV else '✗') + ' DOMAIN EXPANSION   LONDON DONE · 11:15 ET', TIERN[tier], tc)
history(fig, DAY)
fig.text(0.02, 0.955, 'Domain Expansion v10 · NQ1! 1-minute, Fri 9 Oct 2026, 11:15 ET: notes back on, breakout label at its candle, follow-through joined to the 05:00 note',
         color='#131722', fontsize=12.5, weight='bold')
fig.text(0.02, 0.928, 'After the up-break at ' + f'{fb:%H:%M}' + ' the 02:30 tier note moved below the domain and pre-London ranges; the 05:00 note sits on the other side, above the London high and left of 05:00. '
         'NQ 1-minute data; TradingView rendering will differ.', color='#5d6476', fontsize=9)
plt.savefig(OUTA, dpi=100, facecolor=BG); plt.close(fig)
print(dict(break_=bTx, resTx=resTx, ft=ftTx))
