"""Domain Expansion v9 mocks on NQ1! 5-minute, Fri 9 Oct 2026 (CBDR only; London expanded up; the London low was the domain low).
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

OUTA, OUTB = sys.argv[1], sys.argv[2]
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


# ── (A) live at 03:40
NOW = at(3, 40)
x = g[(g.index >= at(23, 30) - pd.Timedelta(days=1)) & (g.index < NOW)].resample('5min').agg(dict(Open='first', High='max', Low='min', Close='last')).dropna()
ix = lambda t: float(np.searchsorted(x.index, t))
n = len(x)
fig = plt.figure(figsize=(18, 10.4), dpi=100, facecolor=BG)
ax = fig.add_axes([0.02, 0.05, 0.60, 0.85])
chart(ax, x)
x02, xn = ix(at(2, 0)), n - 1
prelondon(ax, ix, x02)
ax.add_patch(Rectangle((x02 - 0.5, dL), ix(at(2, 30)) - x02, rD, fc=tc, alpha=0.12, ec='none', zorder=1))
ax.axvspan(ix(at(2, 30)) - 0.5, ix(at(2, 50)) - 0.5, color=tc, alpha=0.10, lw=0)
post = g[(g.index >= at(2, 30)) & (g.index < NOW)]
lonHi, lonLo = post.High.max(), post.Low.min()
for y, lab, ls, above, watch, al in [(dH, f'{stamp(dHt)} Domain high', '-', True, True, 1), (dL, f'{stamp(dLt)} Domain low', '-', False, True, 1),
                                     ((dH + dL) / 2, f'{stamp(at(2, 0))} Domain 0.5', ':', True, False, 0.6)] + \
        [(dH + k * rD, f'+{k:.1f} SD' + (' · expansion' if k == 2 else ''), ':', True, True, 0.55) for k in SDS] + \
        [(dL - k * rD, f'−{k:.1f} SD' + (' · expansion' if k == 2 else ''), ':', False, True, 0.55) for k in SDS]:
    hit = watch and ((post.High >= y).any() if above else (post.Low <= y).any())
    ax.plot([x02, xn], [y, y], color=tc, lw=1.1 if ls == '-' else 0.9, ls='--' if hit else ls, alpha=al, zorder=3)
    label(ax, xn, y, lab)
# 08:00 UK = 03:00 ET
xu = ix(at(3, 0))
ax.axvline(xu, color='#9e9e9e', lw=0.8, ls=':', zorder=2)
ax.text(xu, x.loc[at(3, 0)].High + rD * 0.15, '08:00 UK', color=CHT, fontsize=7, ha='center', va='bottom')
# first break in the execution window: a small mark
fb = post[(post.High > dH) | (post.Low < dL)].index[0]
upb = post.loc[fb].High > dH
fbx = ix(fb.floor('5min'))
ax.plot(fbx, (x.iloc[int(fbx)].High + rD * 0.18) if upb else (x.iloc[int(fbx)].Low - rD * 0.18), marker='^' if upb else 'v', color=tc, ms=6, zorder=7)
upS, dnS = max(0, (lonHi - dH) / rD), max(0, (dL - lonLo) / rD)
far = max(upS, dnS)
cl = post.Close.iloc[-1]
lHs, lLs = max(dH, lonHi), min(dL, lonLo)
pos = (3 * 60 + 40 - 150) / 15
p2 = 100.0 if far >= 2 else tbl(T['LV_C' if coiled else 'LV_O'], 4, pos, int(min(3, far // 0.5)))
pHi = tbl(T['IN_C' if coiled else 'IN_O'], 5, pos, bucket((lHs - cl) / rD))
pLo = tbl(T['IN_C' if coiled else 'IN_O'], 5, pos, bucket((cl - lLs) / rD))
lrNow = lHs - lLs
lo, hi = min(x.Low.min(), dL - 4.3 * rD), max(x.High.max(), dH + 4.3 * rD)
ax.set_xlim(-1, n + 20); ax.set_ylim(lo, hi)
g8 = lambda f: '█' * int(round(min(1, f) * 8)) + '░' * (8 - int(round(min(1, f) * 8)))
rows = [('RANGE', f'{rD:.0f} pts · coil {coil:.2f} ' + ('✓' if coiled else '✗'), f'CBDR {cbR:.1f}× ' + ('✓' if cbR >= 5 else '✗'), False),
        ('EXPECT', f'London ≈ {lrE:.0f} pts', f'{lrE * 0.778:.0f}–{lrE * 1.293:.0f}', False),
        ('DONE', f'{g8(lrNow / lrE)} {lrNow:.0f} pts', f'{100 * lrNow / lrE:.0f}%', False),
        ('SD', f'▲ {upS:.1f} · ▼ {dnS:.1f}', 'furthest', False),
        ('2 SD', 'by 04:59', f'{p2:.0f}%', False) if far < 2 else ('2 SD', f'✓ 2.0 SD reached {post.index[post.High >= dH + 2 * rD][0]:%H:%M}', '', True),
        ('HIGH', f'London high {(lHs - cl) / rD:.1f} SD away', f'in {pHi:.0f}%', False),
        ('LOW', f'London low {(cl - lLs) / rD:.1f} SD away', f'in {pLo:.0f}%', False)]
card(fig, 0.635, 0.885, rows, '◆ DOMAIN EXPANSION   LONDON · 03:40 ET', TIERN[tier], tc)
history(fig, DAY - pd.Timedelta(days=1))
fig.text(0.02, 0.955, 'Domain Expansion v9 · live at 03:40 ET (NQ1! 5-minute, Fri 9 Oct 2026): pre-London range, no text boxes, Dark cards on a light chart with black chart text',
         color='#131722', fontsize=12.5, weight='bold')
fig.text(0.02, 0.928, 'Pre-London range 00:00–00:59 with its CE, lines to 02:00. The first break is a small ▲. The cards take their text from the card theme, so black chart text no longer hides them. '
         'NQ 1-minute data; TradingView rendering will differ.', color='#5d6476', fontsize=9)
plt.savefig(OUTA, dpi=100, facecolor=BG); plt.close(fig)
print('A', dict(rD=rD, pH=pH, pL=pL, coil=round(coil, 3), cbR=round(cbR, 2), lrE=round(lrE), up=round(upS, 2), dn=round(dnS, 2), p2=round(p2), pHi=round(pHi), pLo=round(pLo), brk=str(fb)))

# ── (B) 11:15: London done, carried into New York
NOW = at(11, 15)
x = g[(g.index >= at(0, 0)) & (g.index < NOW)].resample('5min').agg(dict(Open='first', High='max', Low='min', Close='last')).dropna()
ix = lambda t: float(np.searchsorted(x.index, t))
n = len(x)
fig = plt.figure(figsize=(18, 10.4), dpi=100, facecolor=BG)
ax = fig.add_axes([0.02, 0.05, 0.60, 0.85])
chart(ax, x)
x02, x5, x11 = ix(at(2, 0)), ix(at(5, 0)), ix(at(11, 0))
prelondon(ax, ix, x02)
ax.add_patch(Rectangle((x02 - 0.5, dL), ix(at(2, 30)) - x02, rD, fc=tc, alpha=0.12, ec='none', zorder=1))
ax.axvspan(ix(at(2, 30)) - 0.5, ix(at(2, 50)) - 0.5, color=tc, alpha=0.10, lw=0)
lon = g[(g.index >= at(2, 0)) & (g.index < at(5, 0))]
post = g[(g.index >= at(2, 30)) & (g.index < at(5, 0))]
lH5, lL5 = lon.High.max(), lon.Low.min()
DOM = [(dH, f'{stamp(dHt)} Domain high', '-', True, True, 1), (dL, f'{stamp(dLt)} Domain low', '-', False, True, 1),
       ((dH + dL) / 2, f'{stamp(at(2, 0))} Domain 0.5', ':', True, False, 0.6)] + \
      [(dH + k * rD, f'+{k:.1f} SD' + (' · expansion' if k == 2 else ''), ':', True, True, 0.55) for k in SDS] + \
      [(dL - k * rD, f'−{k:.1f} SD' + (' · expansion' if k == 2 else ''), ':', False, True, 0.55) for k in SDS]
moved = []
for y, lab, ls, above, watch, al in DOM:
    hit = watch and ((post.High >= y).any() if above else (post.Low <= y).any())
    ax.plot([x02, x5], [y, y], color=tc, lw=1.1 if ls == '-' else 0.9, ls='--' if hit else ls, alpha=al, zorder=3)
    others = [d[0] for d in DOM if d[0] != y] + [lH5, lL5]
    near = [o for o in others if abs(o - y) <= 0.25 * rD]
    where = away(y, min(near, key=lambda o: abs(o - y)), above) if near else 'mid'
    if where != 'mid':
        moved.append(lab)
    label(ax, x5, y, lab, where)
ny = g[(g.index >= at(5, 0)) & (g.index < at(11, 0))]
tH = ny.index[ny.High > lH5]; tL = ny.index[ny.Low < lL5]
nyHt = tH[0] if len(tH) else None; nyLt = tL[0] if len(tL) else None
for y, nm, taken, txt in ((lH5, 'London high', nyHt, 'NY AM 66% · by 11:00 75%'), (lL5, 'London low', nyLt, 'NY AM 62% · by 11:00 71%')):
    ax.plot([x5, x11], [y, y], color=tc, lw=2, ls='--' if taken is not None else '-', zorder=3)
    label(ax, x11, y, f'{nm} · taken {taken:%H:%M}' if taken is not None else f'{nm} · not taken by 11:00', fs=7.8)
xu = ix(at(3, 0))
ax.axvline(xu, color='#9e9e9e', lw=0.8, ls=':', zorder=2)
fb = post[(post.High > dH) | (post.Low < dL)].index[0]
upb = post.loc[fb].High > dH
fbx = ix(fb.floor('5min'))
ax.plot(fbx, (x.iloc[int(fbx)].High + rD * 0.18) if upb else (x.iloc[int(fbx)].Low - rD * 0.18), marker='^' if upb else 'v', color=tc, ms=6, zorder=7)
lo, hi = x.Low.min(), x.High.max()
ax.set_xlim(-1, n + 30); ax.set_ylim(lo - (hi - lo) * 0.04, hi + (hi - lo) * 0.06)
up5, dn5 = (post.High.max() - dH) / rD, (dL - post.Low.min()) / rD
resV = 1 if (up5 >= 2 and up5 >= dn5) else -1 if (dn5 >= 2 and dn5 > up5) else 0
resSD = max(up5, 0) if up5 >= dn5 else -dn5
c7 = g[g.index < at(7, 0)].Close.iloc[-1]
s7 = (c7 - dH) / rD if c7 > dH else -(dL - c7) / rD if c7 < dL else 0
ftTx = 'close inside the range' if s7 == 0 else f'close {abs(s7):.2f} SD ' + ('above' if s7 > 0 else 'below')
rows = [('RESULT', '▲ expansion' if resV == 1 else '▼ expansion' if resV == -1 else 'no expansion', ('▲ ' if resSD >= 0 else '▼ ') + f'{abs(resSD):.1f} SD', resV != 0),
        ('RANGE', f'London {lH5 - lL5:.0f} pts', f'{(lH5 - lL5) / r.adr:.2f} ADR', False),
        ('FOLLOW', ftTx, '07:00', False),
        ('NY HIGH', f'{lH5:,.2f}', f'taken {nyHt:%H:%M}' if nyHt is not None else 'not taken', nyHt is not None),
        ('NY LOW', f'{lL5:,.2f}', f'taken {nyLt:%H:%M}' if nyLt is not None else 'not taken', nyLt is not None)]
card(fig, 0.635, 0.885, rows, ('✓' if resV else '✗') + ' DOMAIN EXPANSION   LONDON DONE · 11:15 ET', TIERN[tier], tc)
history(fig, DAY)
fig.text(0.02, 0.955, 'Domain Expansion v9 · 11:15 ET: the London low was the domain low; their labels no longer collide',
         color='#131722', fontsize=12.5, weight='bold')
fig.text(0.02, 0.928, 'At 05:00 a label within ¼ domain range of another level, or of the carried London high / low, moves its text off that line: here the domain low label '
         'sits under its line and +3.0 SD under the London high. FOLLOW replaces the equal-highs row. TradingView rendering will differ.', color='#5d6476', fontsize=9)
plt.savefig(OUTB, dpi=100, facecolor=BG); plt.close(fig)
print('B', dict(lH5=lH5, lL5=lL5, dL=dL, nyHt=str(nyHt), nyLt=str(nyLt), up5=round(up5, 2), resV=resV, ft=ftTx, moved=moved))
