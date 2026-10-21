"""Domain Expansion v8 mocks on NQ1! 5-minute, Wed 7 Oct 2026 (a coiled London that expanded down).
(A) live at 03:40 ET: domain range, SD lines, the London card live.  (B) 11:15 ET: London done, the London high / low carried
to 11:00 and the recent-sessions table. Values computed the way Domain_Expansion_Indicator.pine computes them.
python3 mock_de8.py A.png B.png"""
import sys, json
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

OUTA, OUTB = sys.argv[1], sys.argv[2]
BG, TX, SUB, MU, GRID, BODY = '#ffffff', '#131722', '#5d6476', '#9aa1b2', '#eef1f6', '#f4f6f9'
UP, DN = '#089981', '#f23645'
TIERC = {3: '#ff6d00', 2: '#ffb300', 1: '#00acc1', 0: '#787b86'}
TIERN = {3: 'BOTH', 2: 'COILED', 1: 'CBDR', 0: 'NEITHER'}
P = json.load(open('/home/claude/dx/lon_pine.json'))
T = {k: np.array([float(x) for x in v.split(',')]) for k, v in P.items()}
R = pd.read_pickle('/home/claude/dx/lon_rows.pkl')
R = R[R.sym == 'NQ'].copy()
R['tier'] = np.where((R.coil <= 0.2) & (R.cbR >= 5), 3, np.where(R.coil <= 0.2, 2, np.where(R.cbR >= 5, 1, 0)))
DAY = pd.Timestamp('2026-10-07')
r = R[R.tday == DAY].iloc[0]
b = pd.read_pickle('/home/claude/kyw/bars_NQ_all.pkl')
g = b[b.tday == DAY].set_index('ts')
D0 = DAY.normalize()
at = lambda h, m: D0 + pd.Timedelta(hours=h, minutes=m)
dr = g[(g.index >= at(2, 0)) & (g.index < at(2, 30))]
dH, dL = dr.High.max(), dr.Low.min(); rD = dH - dL
tier = int(r.tier); tc = TIERC[tier]
coil, cbR, atr = r.coil, r.cbR, r.atr
lrE = 1.794 * rD ** 0.497 * atr ** 0.437


def tbl(a, ncol, pos, col):
    p = max(0.0, min(9.0, pos)); i0 = int(np.floor(p)); i1 = min(9, i0 + 1); f = p - i0
    return a[i0 * ncol + col] * (1 - f) + a[i1 * ncol + col] * f


def bucket(d):
    return 0 if d < 0.25 else 1 if d < 0.5 else 2 if d < 1 else 3 if d < 2 else 4


def chart(ax, x, t_end):
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


def card(fig, x0, y0, rows, head, pill, col, w=0.30):
    lh = 0.026
    fig.patches.append(Rectangle((x0, y0 - lh), w, lh, transform=fig.transFigure, fc=col, ec='none', zorder=10))
    fig.text(x0 + 0.006, y0 - lh / 2, head, color='#ffffff', fontsize=8.6, family='DejaVu Sans Mono', va='center', weight='bold', zorder=11)
    fig.patches.append(Rectangle((x0 + w - 0.062, y0 - lh + 0.004), 0.056, lh - 0.008, transform=fig.transFigure, fc='#ffffff', ec='none', zorder=11))
    fig.text(x0 + w - 0.034, y0 - lh / 2, pill, color=col, fontsize=8, family='DejaVu Sans Mono', va='center', ha='center', weight='bold', zorder=12)
    for k, (a, bb, cc, hl) in enumerate(rows):
        yy = y0 - lh * (k + 2)
        fig.patches.append(Rectangle((x0, yy), w, lh, transform=fig.transFigure, fc=BODY, ec='none', zorder=10))
        fig.text(x0 + 0.006, yy + lh / 2, a, color=SUB, fontsize=8.2, family='DejaVu Sans Mono', va='center', zorder=11)
        fig.text(x0 + 0.055, yy + lh / 2, bb, color=col if hl else TX, fontsize=8.2, family='DejaVu Sans Mono', va='center', zorder=11)
        fig.text(x0 + w - 0.006, yy + lh / 2, cc, color=col if hl else TX, fontsize=8.2, family='DejaVu Sans Mono', va='center', ha='right', zorder=11)
    fig.patches.append(Rectangle((x0, y0 - lh * (len(rows) + 1)), w, lh * (len(rows) + 1), transform=fig.transFigure, fc='none', ec=col, lw=1, zorder=12))


def levels(ax, ix, x_end, show_lbl=True):
    a = ix(at(2, 0))
    ax.add_patch(Rectangle((a, dL), ix(at(2, 30)) - a, rD, fc=tc, alpha=0.12, ec='none', zorder=1))
    for y, lab, ls in ((dH, '02:12 Domain high', '-'), (dL, '02:04 Domain low', '-'), ((dH + dL) / 2, 'Domain 0.5', ':')):
        ax.plot([a, x_end], [y, y], color=tc, lw=1.1, ls=ls, zorder=3)
        if show_lbl:
            ax.text(x_end + 0.4, y, lab, color=TX, fontsize=7.5, va='center')
    for k in (2.0, 2.5, 3.0, 4.0):
        for sgn, base in ((1, dH), (-1, dL)):
            y = base + sgn * k * rD
            ax.plot([a, x_end], [y, y], color=tc, lw=0.9, ls=':', alpha=0.75, zorder=3)
            if show_lbl:
                ax.text(x_end + 0.4, y, ('+' if sgn > 0 else '−') + f'{k:.1f} SD' + (' · expansion' if k == 2.0 else ''), color=SUB, fontsize=7, va='center')


# ── (A) live at 03:40
NOW = at(3, 40)
x = g[(g.index >= at(0, 0)) & (g.index < NOW)].resample('5min').agg(dict(Open='first', High='max', Low='min', Close='last')).dropna()
ix = lambda t: float(np.searchsorted(x.index, t))
n = len(x)
fig = plt.figure(figsize=(18, 10.4), dpi=100, facecolor=BG)
ax = fig.add_axes([0.02, 0.05, 0.86, 0.85])
chart(ax, x, NOW)
xe = ix(at(5, 0))
levels(ax, ix, xe)
ax.axvspan(ix(at(2, 30)) - 0.5, ix(at(2, 50)) - 0.5, color=tc, alpha=0.10, lw=0)
post = g[(g.index >= at(2, 30)) & (g.index < NOW)]
lonHi, lonLo = post.High.max(), post.Low.min()
upS, dnS = max(0, (lonHi - dH) / rD), max(0, (dL - lonLo) / rD)
far = max(upS, dnS)
cl = post.Close.iloc[-1]
lHs, lLs = max(dH, lonHi), min(dL, lonLo)
pos = (3 * 60 + 40 - 150) / 15
coiled = coil <= 0.2
p2 = 100.0 if far >= 2 else tbl(T['LV_C' if coiled else 'LV_O'], 4, pos, int(min(3, far // 0.5)))
pHi = tbl(T['IN_C' if coiled else 'IN_O'], 5, pos, bucket((lHs - cl) / rD))
pLo = tbl(T['IN_C' if coiled else 'IN_O'], 5, pos, bucket((cl - lLs) / rD))
lrNow = lHs - lLs
first_brk = post[(post.High > dH) | (post.Low < dL)].index[0]
bdir = '▲' if post.loc[first_brk].High > dH else '▼'
ax.text(ix(first_brk), (post.loc[first_brk].Low - rD * 0.25) if bdir == '▼' else post.loc[first_brk].High + rD * 0.25, f'{bdir} Break {first_brk:%H:%M}', color=TX, fontsize=7.5, ha='center',
        bbox=dict(boxstyle='round,pad=0.25', fc=tc, alpha=0.25, ec='none'))
ax.text(ix(at(2, 30)), dH + rD * 3.5, f'◆ Domain Expansion: coiled only · 2 SD odds ~40%\nCoil {coil:.2f} ({rD:.0f} ÷ {atr:.0f} pts) ✓\nCBDR {cbR * rD:.0f} pts · {cbR:.1f} ranges ✗',
        color=TX, fontsize=7.5, va='bottom', bbox=dict(boxstyle='round,pad=0.3', fc=tc, alpha=0.2, ec='none'))
lo, hi = min(x.Low.min(), dL - 4.3 * rD), max(x.High.max(), dH + 4.3 * rD)
ax.set_xlim(-1, n + 30); ax.set_ylim(lo, hi)
g8 = lambda f: '█' * int(round(min(1, f) * 8)) + '░' * (8 - int(round(min(1, f) * 8)))
rows = [('RANGE', f'{rD:.0f} pts · coil {coil:.2f} ✓', f'CBDR {cbR:.1f}× ✗', False),
        ('EXPECT', f'London ≈ {lrE:.0f} pts', f'{lrE * 0.778:.0f}–{lrE * 1.293:.0f}', False),
        ('DONE', f'{g8(lrNow / lrE)} {lrNow:.0f} pts', f'{100 * lrNow / lrE:.0f}%', False),
        ('SD', f'▲ {upS:.1f} · ▼ {dnS:.1f}', 'furthest', False),
        ('2 SD', 'by 04:59', f'{p2:.0f}%', False),
        ('HIGH', f'London high {(lHs - cl) / rD:.1f} SD away', f'in {pHi:.0f}%', False),
        ('LOW', f'London low {(cl - lLs) / rD:.1f} SD away', f'in {pLo:.0f}%', False)]
card(fig, 0.62, 0.885, rows, '◆ DOMAIN EXPANSION   LONDON · 03:40 ET', TIERN[tier], tc, w=0.33)
fig.text(0.02, 0.955, 'Domain Expansion v8 · London card, live at 03:40 ET (NQ1! 5-minute, Wed 7 Oct 2026, a coiled day)', color=TX, fontsize=13, weight='bold')
fig.text(0.02, 0.928, 'NQ 1-minute data. The card reads the domain range, the expected London range, the furthest SD so far, the live odds of 2 SD by 04:59 and whether '
         'the London high / low is already in. Odds: NQ + ES + RTY 2018–26. TradingView rendering will differ.', color=SUB, fontsize=9)
plt.savefig(OUTA, dpi=100, facecolor=BG); plt.close(fig)
print('A', dict(rD=rD, coil=round(coil, 2), cbR=round(cbR, 2), lrE=round(lrE), lrNow=lrNow, up=round(upS, 2), dn=round(dnS, 2), p2=round(p2), pHi=round(pHi), pLo=round(pLo)))

# ── (B) 11:15: London done, carried into New York, recent sessions
NOW = at(11, 15)
x = g[(g.index >= at(1, 30)) & (g.index < NOW)].resample('5min').agg(dict(Open='first', High='max', Low='min', Close='last')).dropna()
ix = lambda t: float(np.searchsorted(x.index, t))
n = len(x)
fig = plt.figure(figsize=(18, 10.4), dpi=100, facecolor=BG)
ax = fig.add_axes([0.02, 0.05, 0.86, 0.85])
chart(ax, x, NOW)
x5 = ix(at(5, 0))
levels(ax, ix, x5, show_lbl=False)
lon = g[(g.index >= at(2, 0)) & (g.index < at(5, 0))]
lH5, lL5 = lon.High.max(), lon.Low.min()
x11 = ix(at(11, 0))
ny = g[(g.index >= at(5, 0)) & (g.index < at(11, 0))]
tH = ny.index[ny.High > lH5]; tL = ny.index[ny.Low < lL5]
for y, nm, tt, txt in ((lH5, 'London high', tH, 'NY AM 66% · by 11:00 75%'), (lL5, 'London low', tL, 'NY AM 62% · by 11:00 71%')):
    taken = tt[0] if len(tt) else None
    xs = ix(taken) if taken is not None else x11
    ax.plot([x5, xs], [y, y], color=tc, lw=2, zorder=3)
    if taken is not None:
        ax.plot([xs, x11], [y, y], color=tc, lw=2, ls='--', zorder=3)
    ax.text(x11 + 0.5, y, f'{nm} · taken {taken:%H:%M}' if taken is not None else f'{nm} · {txt}', color=TX, fontsize=8, va='center')
c5 = lon.Close.iloc[-1]
up5, dn5 = (lon[lon.index >= at(2, 30)].High.max() - dH) / rD, (dL - lon[lon.index >= at(2, 30)].Low.min()) / rD
isDn = dn5 >= 2 and dn5 > up5
ax.text(ix(at(3, 30)), lH5 + rD * 0.9, f'✓ Domain Expansion ▼\nextreme {dn5:.2f} SD below · close {(dL - c5) / rD:.2f} SD below\nLondon {lH5 - lL5:.0f} pts · {(lH5 - lL5) / r.adr:.2f} ADR',
        color=TX, fontsize=7.5, ha='center', va='bottom', bbox=dict(boxstyle='round,pad=0.3', fc=tc, alpha=0.2, ec='none'))
lo, hi = x.Low.min(), x.High.max()
ax.set_xlim(-1, n + 34); ax.set_ylim(lo - (hi - lo) * 0.05, hi + (hi - lo) * 0.25)
nyHt = tH[0] if len(tH) else None; nyLt = tL[0] if len(tL) else None
rows = [('RESULT', '▼ expansion', f'▼ {dn5:.1f} SD', True),
        ('RANGE', f'London {lH5 - lL5:.0f} pts', f'{(lH5 - lL5) / r.adr:.2f} ADR', False),
        ('SWEPT', 'EQH 0/1 · EQL 1/2', '', False),
        ('NY HIGH', f'{lH5:,.2f}', f'taken {nyHt:%H:%M}' if nyHt is not None else 'not taken', nyHt is not None),
        ('NY LOW', f'{lL5:,.2f}', f'taken {nyLt:%H:%M}' if nyLt is not None else 'not taken', nyLt is not None)]
card(fig, 0.62, 0.885, rows, '✓ DOMAIN EXPANSION   LONDON DONE · 11:15 ET', TIERN[tier], tc, w=0.33)
# recent London sessions (10, newest first)
H = R[R.tday <= DAY].tail(10).iloc[::-1]
x0, y0, w, lh = 0.62, 0.40, 0.33, 0.024
cols = [0.006, 0.135, 0.19, 0.268, 0.324]
fig.patches.append(Rectangle((x0, y0 - lh), w, lh, transform=fig.transFigure, fc='#5e35b1', ec='none', zorder=10))
ex = int(((H.mx >= 2.0)).sum())
fig.text(x0 + 0.006, y0 - lh / 2, 'LONDON   last 10', color='#ffffff', fontsize=8.4, family='DejaVu Sans Mono', va='center', weight='bold', zorder=11)
fig.text(x0 + w - 0.006, y0 - lh / 2, f'{ex}/10 expanded', color='#ffffff', fontsize=8.4, family='DejaVu Sans Mono', va='center', ha='right', zorder=11)
hdr = ['day', 'tier', '05:00', 'furthest', 'range']
for k, row in enumerate([hdr] + [[f'{d.tday:%a %d}', TIERN[int(d.tier)], ('▲ ✓' if d.up >= d.dn else '▼ ✓') if d.mx >= 2 else '✗',
                                  ('▲ ' if d.up >= d.dn else '▼ ') + f'{max(d.up, d.dn, 0):.1f} SD', f'{d.lr:.0f} pts'] for _, d in H.iterrows()]):
    yy = y0 - lh * (k + 2)
    fig.patches.append(Rectangle((x0, yy), w, lh, transform=fig.transFigure, fc=BODY, ec='none', zorder=10))
    for j, v in enumerate(row):
        colr = SUB if k == 0 else (TIERC[int(H.iloc[k - 1].tier)] if j in (1, 2) and (j == 1 or '✓' in v) else TX)
        fig.text(x0 + cols[j], yy + lh / 2, v, color=colr, fontsize=8, family='DejaVu Sans Mono', va='center', ha='left' if j == 0 else 'right', zorder=11)
fig.patches.append(Rectangle((x0, y0 - lh * (len(H) + 2)), w, lh * (len(H) + 2), transform=fig.transFigure, fc='none', ec='#b39ddb', lw=1, zorder=12))
fig.text(0.02, 0.955, 'Domain Expansion v8 · 11:15 ET: London done, its high and low carried into New York, and the last 10 London sessions', color=TX, fontsize=13, weight='bold')
fig.text(0.02, 0.928, 'NQ1! 5-minute, Wed 7 Oct 2026. London levels stop at 05:00; the London high / low run to 11:00 and are marked when taken. The table is built from the chart\'s own history. '
         'TradingView rendering will differ.', color=SUB, fontsize=9)
plt.savefig(OUTB, dpi=100, facecolor=BG); plt.close(fig)
print('B', dict(lH5=lH5, lL5=lL5, nyHt=str(nyHt), nyLt=str(nyLt), dn5=round(dn5, 2), ex=ex))
