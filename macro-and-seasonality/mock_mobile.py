"""Phone mocks of the Mobile card layout, NQ1! 5-minute, dark theme, 11:00 ET.
Left: Gran Rey Cero with Layout = Mobile. Right: the same morning in a Hueco Mundo megazord (concept): every module
collapses to one line, today's module expands, VIX and DXY appear once.
  python3 mock_mobile.py 2026-08-12 out.png
Card values are computed the way Gran_Rey_Cero.pine computes them: prices from NQ 1-minute data, clock from clock.json,
VIX from daily closes, DXY from the DXY futures 5-minute file."""
import sys, json, numpy as np, pandas as pd, matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, FancyBboxPatch
sys.path.insert(0, '/home/claude/hm'); from events import CPI, NFP, FOMC
plt.rcParams['font.family'] = 'DejaVu Sans'
MONO = 'DejaVu Sans Mono'
DPI = 100
# dark palette, exactly the script's
BG, BODY, BODY2, NEU = '#0e1117', '#161a23', '#1c2130', '#3a3f4b'
TX, SUB, MU = '#e6e9ef', '#9aa3b5', '#5d6476'
HOT, COLD, OK, PREM, DISC, WARN = '#ff8a65', '#64b5f6', '#66bb6a', '#ef5350', '#66bb6a', '#ff5252'
GH, LVL, WK, CUP, CDN = '#e53935', '#ffb300', '#787b86', '#4caf50', '#131722'
UPC, DNC = '#089981', '#f23645'                       # TradingView dark candles
VX, DXC = '#7e57c2', '#00897b'
MODS = dict(GRAN=('#e53935', 'Gran Rey', 'CPI'), CERO=('#ff7043', 'Cero', 'NFP'), VIZ=('#ab47bc', 'Vizard', 'FOMC'), HOL=('#26a69a', 'Hollow', 'NFP wk'))
def A(c, transp):
    c = c.lstrip('#'); return tuple(int(c[i:i + 2], 16) / 255 for i in (0, 2, 4)) + (1 - transp / 100,)
pf = lambda v: f'{v:.2f}'
x2 = lambda v: f'{v:.2f}×'
p0 = lambda v: f'{v * 100:.0f}%'
g5 = lambda f: '█' * int(round(min(1, max(0, f)) * 5)) + '░' * (5 - int(round(min(1, max(0, f)) * 5)))

b = pd.read_pickle('/home/claude/t3/bars_NQ_all.pkl')
D = pd.read_pickle('/home/claude/hm/days_NQ.pkl'); TDD = D[D.anchor == 'TD'].set_index('tday')
CK = json.load(open('/home/claude/hm/clock.json'))['NQ']
blk = open('/mnt/user-data/outputs/Gran_Rey_Cero.pine', encoding='utf-8').read()
import re
seg = blk[blk.index('NQ_TD  ='):blk.index('NQ_MID')]
ST = [[float(v) for v in r.split(',')] for r in ''.join(re.findall(r'"([^"]*)"', seg)).split(';')]
CPIS = sorted(pd.Timestamp(d) for d in CPI); TDAYS = sorted(pd.Timestamp(t) for t in b.tday.unique())
nxt = lambda arr, d: next((pd.Timestamp(x) for x in sorted(arr) if pd.Timestamp(x) >= d), None)

def data(day):
    day = pd.Timestamp(day); k = TDAYS.index(day); prev = TDAYS[k - 1]
    end = day + pd.Timedelta(hours=10, minutes=59); start = day + pd.Timedelta(hours=6)
    x1 = b[(b.ts >= day - pd.Timedelta(hours=6)) & (b.ts <= end)]
    x5 = x1.set_index('ts').resample('5min').agg(dict(Open='first', High='max', Low='min', Close='last', tday='last')).dropna(subset=['Open'])
    O = TDD.loc[day].O; a = TDD.loc[day].adr; scP = O * a
    tdb = x5[x5.tday == np.datetime64(day)]
    dO, dH, dL, dC = tdb.Open.iloc[0], tdb.High.max(), tdb.Low.min(), tdb.Close.iloc[-1]
    rr = dH - dL; v = rr / scP
    eEnd = min(1380, (11 * 60 - 1080) % 1440); jB = min(45, max(0, int(np.ceil(eEnd / 30)) - 1)); fB = (eEnd - 30 * jB) / 30
    ckAt = lambda nm, kk: (CK[nm]['R'][kk][jB - 1] if jB else 0) + (CK[nm]['R'][kk][jB] - (CK[nm]['R'][kk][jB - 1] if jB else 0)) * fB
    q25, q50, q75 = ckAt('CPI', 1), ckAt('CPI', 2), ckAt('CPI', 3)
    stB = 'Above' if v > q75 else 'Below' if v < q25 else 'Inside'
    vix = pd.read_csv('vix_daily.csv', parse_dates=['DATE']).set_index('DATE').CLOSE
    vPrev = vix[vix.index < day].iloc[-1]; vAvg = vix[vix.index < day].tail(20).mean(); vNow = vix.loc[day]
    vsp = vPrev / vAvg - 1; vch = vNow / vPrev - 1
    st = 'HOT' if vsp >= .10 else 'CALM' if vsp <= -.10 else 'NORMAL'
    bR = {'HOT': '1.27×', 'NORMAL': '0.91×', 'CALM': '0.70×'}[st]
    fx = pd.read_csv('/mnt/user-data/uploads/DXY_2023_2026_5min_continuous.csv'); fx['ts'] = pd.to_datetime(fx.Date + ' ' + fx.Time) + pd.Timedelta(hours=1)
    fx = fx.sort_values('ts'); fx['tday'] = (fx.ts + pd.Timedelta(hours=6)).dt.normalize()
    rows = []
    for td_, g in fx[(fx.tday < day) & (fx.tday >= day - pd.Timedelta(days=45))].groupby('tday'):
        g = g[g.Contract == g.Contract.value_counts().index[0]]
        rows.append(dict(tday=td_, h=g.High.max(), l=g.Low.min(), c=g.Close.iloc[-1]))
    DX = pd.DataFrame(rows).set_index('tday'); DX['tr'] = np.maximum(DX.h, DX.c.shift(1)) - np.minimum(DX.l, DX.c.shift(1))
    atr = DX.tr.tail(20).mean()
    g = fx[(fx.tday == day) & (fx.ts <= end)]; g = g[g.Contract == g.Contract.value_counts().index[0]]
    net = g.Close.iloc[-1] - g.Open.iloc[0]; netPct = net / g.Open.iloc[0]; big = abs(net) >= .5 * atr; fr = min(1, abs(net) / (.5 * atr))
    return dict(day=day, prev=prev, x5=x5, end=end, start=start, O=O, a=a, scP=scP, dO=dO, dH=dH, dL=dL, dC=dC, rr=rr, v=v, q25=q25, q50=q50, q75=q75,
                stB=stB, jB=jB, fB=fB, vNow=vNow, vch=vch, st=st, bR=bR, dxy=g.Close.iloc[-1], net=net, netPct=netPct, big=big, fr=fr, atr=atr)

def card_rows(d, mega=False):
    """[(cells)] with cells (text, fg, bg, bold, align, span); five columns like the script."""
    acc = lambda col: ('', col, col, False, 'left', 1)
    def head(col, title, pill, pfg, pbg): return [acc(col), (title, '#ffffff', col, True, 'left', 3), (pill, pfg, pbg, True, 'center', 1)]
    def row(col, key, lab, v_, s_, held=False, vfg=TX, sfg=MU, sbg=BODY, sbold=False):
        return [acc(col), (key, '#ffffff' if held else MU, OK if held else BODY, held, 'center', 1), (lab, TX, BODY, False, 'left', 1),
                (v_, vfg, BODY, True, 'center', 1), (s_, sfg, sbg, sbold, 'center', 1)]
    stB = d['stB']; sbg = HOT if stB == 'Above' else COLD if stB == 'Below' else NEU; sfg = TX if stB == 'Inside' else '#ffffff'
    now = row(GH, 'NOW', f'range {pf(d["rr"])}', x2(d['v']), stB.upper(), sfg=sfg, sbg=sbg, sbold=True)
    chk = [row(GH, '✓', '08:30 candle', '0.27×', '0.03×', True), row(GH, '✓', '08:30–09:00 adds', '+0.19×', '+0.02×', True),
           row(GH, '✓', '1st sweep won', '70%', '56%', True), row(GH, '✓', 'VIX fell', '69%', '55%', True)]
    st = d['st']; vfg = HOT if st == 'HOT' else COLD if st == 'CALM' else TX
    vix = row(VX, 'VIX', f'{d["vNow"]:.2f} {"▲" if d["vch"] >= 0 else "▼"}{abs(d["vch"]) * 100:.1f}%', d['bR'], 'NORM' if st == 'NORMAL' else st, vfg=vfg,
              sfg=TX if st == 'NORMAL' else '#ffffff', sbg=NEU if st == 'NORMAL' else HOT if st == 'HOT' else COLD, sbold=True)
    big = d['big']
    dxy = row(DXC, 'DXY', ('NQ other way 60%' if big else f'{g5(d["fr"])} {p0(d["fr"])}'), f'{"▲" if d["net"] >= 0 else "▼"}{abs(d["netPct"]) * 100:.2f}%', 'BIG' if big else 'USUAL',
              vfg=HOT if big else TX, sfg='#ffffff' if big else TX, sbg=HOT if big else NEU, sbold=True)
    gap = 'GAP'
    if not mega:
        return [head(GH, '● GRAN REY · CPI · NQ', 'TODAY', GH, '#ffffff'), now] + chk + [gap, vix, dxy]
    day = d['day']
    def coll(key, nm, ev, arr, extra=None):
        col, name, _ = MODS[key]
        n1 = extra if extra is not None else nxt(arr, day + pd.Timedelta(days=1)); dd = (n1 - day).days
        return [acc(col), (ev, MU, BODY, False, 'center', 1), (f'{name} · {MODS[key][2]}', SUB, BODY, False, 'left', 1), ('', TX, BODY, False, 'center', 1), (f'IN {dd}D', '#ffffff', A('#000000', 55), True, 'center', 1)]
    nfp = nxt(NFP, day + pd.Timedelta(days=1)); hol = nfp - pd.Timedelta(days=4)            # Monday of NFP week
    modhead = [acc(GH), ('M7', '#ffffff', GH, True, 'center', 1), ('Gran Rey · CPI', TX, BODY, True, 'left', 1), ('', TX, BODY, False, 'center', 1), ('TODAY', GH, '#ffffff', True, 'center', 1)]
    return ([head('#5c6bc0', '● HUECO MUNDO · NQ', 'CPI DAY', '#ffffff', GH), modhead, now] + chk +
            [coll('HOL', 'Hollow', 'M11', None, hol), coll('CERO', 'Cero', 'M6', NFP), coll('VIZ', 'Vizard', 'M9', FOMC), gap, vix, dxy])

def phone(fig, ov, bgax, X0, Y0, S, d, rows, title):
    """draw one phone: X0, Y0 top-left in canvas px; S = px per pt"""
    PWpt, PHpt = 390, 844
    W, H = PWpt * S, PHpt * S
    bgax.add_patch(FancyBboxPatch((X0 - 10 * S, Y0 - 10 * S), W + 20 * S, H + 20 * S, boxstyle=f'round,pad=0,rounding_size={44 * S}', fc='#2a2d34', ec='#3b3f48', lw=2))
    bgax.add_patch(FancyBboxPatch((X0, Y0), W, H, boxstyle=f'round,pad=0,rounding_size={36 * S}', fc=BG, ec='none'))
    t = lambda x, y, s, **k: ov.text(X0 + x * S, Y0 + y * S, s, **k)
    t(30, 26, '11:00', color=TX, fontsize=10.5 * S * .72, weight='bold', va='center')
    ov.add_patch(FancyBboxPatch((X0 + 140 * S, Y0 + 12 * S), 110 * S, 30 * S, boxstyle=f'round,pad=0,rounding_size={15 * S}', fc='#000000', ec='none'))
    t(346, 26, '▮▮▮ ▭', color=TX, fontsize=8 * S * .72, va='center', ha='right')
    # TradingView-style toolbar
    t(16, 68, 'NQ1!', color=TX, fontsize=12.5 * S * .72, weight='bold', va='center')
    t(64, 68, '· 5m ▾', color=SUB, fontsize=10.5 * S * .72, va='center')
    for i, ic in enumerate(['ƒx', '⧉', '⋯']): t(300 + i * 30, 68, ic, color=SUB, fontsize=11 * S * .72, va='center', ha='center')
    ov.plot([X0, X0 + W], [Y0 + 92 * S] * 2, color='#1f2430', lw=1)
    # chart and pane areas (pt): price pane 94–600, clock pane 604–735, time axis to 752; price scale 54 pt wide
    def axes(y0, y1):
        fx0 = (X0) / CW; fx1 = (X0 + (PWpt - 54) * S) / CW
        return fig.add_axes([fx0, 1 - (Y0 + y1 * S) / CH, fx1 - fx0, (y1 - y0) * S / CH], facecolor='none', zorder=5)
    ax = axes(94, 600); bx = axes(606, 735)
    for a_ in (ax, bx):
        for s_ in a_.spines.values(): s_.set_visible(False)
        a_.yaxis.tick_right(); a_.tick_params(labelsize=7.5 * S * .72, colors=SUB, length=0, pad=4); a_.grid(color='#1a1f2b', lw=.8)
    ov.plot([X0, X0 + W], [Y0 + 603 * S] * 2, color='#1f2430', lw=1)
    x5 = d['x5']; day = d['day']; vis = x5[x5.index >= d['start']]
    n = len(vis); T = vis.index
    Tm = T.values.astype('datetime64[m]').astype(np.int64)
    def X(ts):
        m = np.datetime64(pd.Timestamp(ts), 'm').astype(np.int64)
        return n - 1 + (m - Tm[-1]) / 5 if m > Tm[-1] else float(np.interp(m, Tm, np.arange(n)))
    for i, (ts, r) in enumerate(vis.iterrows()):
        c = UPC if r.Close >= r.Open else DNC
        ax.plot([i, i], [r.Low, r.High], color=c, lw=.9 * S / 2, zorder=3)
        ax.add_patch(Rectangle((i - .32, min(r.Open, r.Close)), .64, max(abs(r.Close - r.Open), .5), color=c, zorder=3))
    at = lambda m: day + pd.Timedelta(minutes=m)
    tdb = b[(b.tday == day)]
    pr = tdb[(tdb.ts >= at(450)) & (tdb.ts < at(510))]; drH, drL = pr.High.max(), pr.Low.min()
    rthC = b[(b.tday == d['prev']) & (b.hm == 1614)].Close.iloc[0]
    xe = n - 1; xa = X(at(450))
    for yv in (drH, drL): ax.plot([xa, xe], [yv, yv], ls='--', color=LVL, lw=1, zorder=4)
    ax.plot([xa, xe], [rthC, rthC], ls=':', color=A(LVL, 25), lw=1, zorder=4)
    fs = 6.5 * S * .72
    ax.text(xa, drH, 'stage 1 · DR high', color=LVL, fontsize=fs, va='bottom')
    ax.text(xa, drL, 'stage 1 · DR low', color=LVL, fontsize=fs, va='top')
    post = tdb[(tdb.ts >= at(510))]
    for _, r in post.iterrows():
        if r.Low < drL: ax.annotate('1st sweep ▼', (X(r.ts.floor('5min')), r.Low), xytext=(0, -4), textcoords='offset points', ha='center', va='top', color=LVL, fontsize=fs); break
        if r.High > drH: ax.annotate('1st sweep ▲', (X(r.ts.floor('5min')), r.High), xytext=(0, 4), textcoords='offset points', ha='center', va='bottom', color=LVL, fontsize=fs); break
    w = tdb[(tdb.ts >= at(510)) & (tdb.ts < at(540))]
    ax.add_patch(Rectangle((X(at(510)), w.Low.min()), X(at(540)) - X(at(510)), w.High.max() - w.Low.min(), fc=A(GH, 78), ec=A(GH, 35), lw=1, zorder=2))
    r830 = tdb[(tdb.hm >= 830) & (tdb.hm < 835)]
    ax.add_patch(Rectangle((X(at(510)), r830.Low.min()), xe - X(at(510)), r830.High.max() - r830.Low.min(), fc=A(GH, 86), ec=A(GH, 15), lw=1, zorder=2))
    ax.text(xe + .6, (r830.High.max() + r830.Low.min()) / 2, 'CPI 12/08', color=GH, fontsize=fs, va='center')
    o930 = tdb[tdb.hm == 930].Open.iloc[0]; gce = (rthC + o930) / 2
    ax.plot([X(at(570)), xe], [gce, gce], ls=':', color=A(LVL, 20), lw=1)
    # PO3: model candle + today, weekly
    O, a = d['O'], d['a']; mR = ST[2][10] * a * O; uS = ST[2][3] / (ST[2][3] + ST[2][6]); mH = O + mR * uS; mL = O - mR * (1 - uS); mC = O * (1 + ST[2][8] * a)
    offI, widI, gapI = 24, 8, 10; gw = widI + 6; xd = xe + offI; xw = xd + gw + gapI
    ax.add_patch(Rectangle((xd + 2, mL), gw - 4, mH - mL, fc=A(GH, 90), ec=A(GH, 40), ls=':', lw=1, zorder=4))
    ax.add_patch(Rectangle((xd, min(O, mC)), gw, abs(mC - O), fc=A(GH, 70), ec=GH, lw=1, zorder=4))
    for yv in (mH, mL): ax.plot([xd, xd + gw], [yv, yv], color=GH, lw=2, zorder=5)
    def candle(x0, w_, o, h, l, c):
        ax.plot([x0 + w_ / 2] * 2, [l, h], color=WK, lw=1, zorder=5)
        ax.add_patch(Rectangle((x0, min(o, c)), w_, max(abs(c - o), .5), fc=CUP if c >= o else CDN, ec=WK, lw=1, zorder=5))
    candle(xd + 3, widI, d['dO'], d['dH'], d['dL'], d['dC'])
    wk0 = day - pd.Timedelta(days=day.weekday()); wkb = b[(b.tday >= wk0) & (b.ts <= d['end'])]
    wO, wH, wL, wC = wkb.Open.iloc[0], wkb.High.max(), wkb.Low.min(), wkb.Close.iloc[-1]
    candle(xw, widI, wO, wH, wL, wC)
    ax.annotate(f'1D · CPI DAY\nrange {pf(d["rr"])}\nmodel {pf(mR)} · {p0(d["rr"] / mR)} filled', (xd + gw / 2, max(d['dH'], mH)), xytext=(0, 5), textcoords='offset points', ha='center', va='bottom',
                fontsize=fs, family=MONO, color=TX, zorder=8, bbox=dict(boxstyle='round,pad=0.35,rounding_size=0.3', fc=BG, ec='#262c3a', lw=.8))
    ax.annotate(f'1W\nrange {pf(wH - wL)}', (xw + widI / 2, wL), xytext=(0, -5), textcoords='offset points', ha='center', va='top', fontsize=fs, family=MONO, color=TX, zorder=8,
                bbox=dict(boxstyle='round,pad=0.35,rounding_size=0.3', fc=BG, ec='#262c3a', lw=.8))
    lo = min(vis.Low.min(), mL, wL); hi = max(vis.High.max(), mH, d['dH'], wH); sp = hi - lo
    loL = lo - sp * .04; Hy = (hi - loL) / .56
    ax.set_xlim(-1, xw + widI + 3); ax.set_ylim(loL, loL + Hy)
    ax.set_xticks([])
    # last price tag
    lp = vis.Close.iloc[-1]
    ov.add_patch(Rectangle((X0 + (PWpt - 54) * S, 0), 0, 0))
    yl = ax.transData.transform((0, lp))[1]
    # clock pane
    scP = d['scP']; t0 = day - pd.Timedelta(hours=6)
    full = x5
    xs = [X(t0 + pd.Timedelta(minutes=30 * (j + 1))) if t0 + pd.Timedelta(minutes=30 * (j + 1)) >= d['start'] else None for j in range(46)]
    xsj = [(j, xv) for j, xv in enumerate(xs) if xv is not None]
    J = [j for j, _ in xsj]; XV = [xv for _, xv in xsj]
    q = lambda kk: np.array([CK['CPI']['R'][kk][j] for j in J]) * scP
    jj = np.arange(len(J))
    # extend the bands past the last bar (the typical path for the rest of the day)
    later = [(j, xe + (j - J[-1]) * 6) for j in range(J[-1] + 1, 46)]
    J2 = J + [j for j, _ in later]; XV2 = XV + [x for _, x in later]
    q2 = lambda kk: np.array([CK['CPI']['R'][kk][j] for j in J2]) * scP
    bx.fill_between(XV2, q2(0), q2(4), color=GH, alpha=.10, lw=0); bx.fill_between(XV2, q2(1), q2(3), color=GH, alpha=.20, lw=0)
    bx.plot(XV2, q2(2), color=GH, lw=1.6)
    rr = []; hh = ll = None
    for i, (ts, r) in enumerate(full.iterrows()):
        if hh is None or full.tday.iloc[i] != full.tday.iloc[i - 1]: hh, ll = r.High, r.Low
        hh = max(hh, r.High); ll = min(ll, r.Low); rr.append(hh - ll)
    rr = pd.Series(rr, index=full.index)[full.index >= d['start']]
    liveC = HOT if d['stB'] == 'Above' else COLD if d['stB'] == 'Below' else TX
    bx.plot(np.arange(len(rr)), rr.values, color=liveC, lw=2.2, zorder=5)
    bx.axvline(X(at(510)), color=A(GH, 30), ls=':', lw=1)
    bx.set_xlim(ax.get_xlim()); bx.set_ylim(0, max(q2(4).max(), rr.max()) * 1.12)
    ticks = [i for i, ts in enumerate(T) if ts.minute == 0 and ts.hour % 2 == 0]
    bx.set_xticks(ticks); bx.set_xticklabels([T[i].strftime('%H:%M') for i in ticks])
    bx.text(.01, .93, 'Gran Rey · clock', transform=bx.transAxes, fontsize=fs, color=SUB, va='top')
    # legend (top left of the price pane), one line
    t(8, 106, 'NQ1! · 5 · CME', color=SUB, fontsize=7.5 * S * .72, va='center')
    # bottom bar
    ov.plot([X0, X0 + W], [Y0 + 760 * S] * 2, color='#1f2430', lw=1)
    for i, ic in enumerate(['⌂', '☆', '◔', '✎', '☰']): t(39 + i * 78, 790, ic, color=SUB if i != 2 else TX, fontsize=14 * S * .72, ha='center', va='center')
    ov.add_patch(FancyBboxPatch((X0 + 130 * S, Y0 + 826 * S), 130 * S, 5 * S, boxstyle=f'round,pad=0,rounding_size={2.5 * S}', fc='#e6e9ef', ec='none'))
    # the card: Top left, under a 3.5% spacer, text size Small (10 px)
    FONT = 10 * S; CWc = FONT * .602; RH = FONT * 1.55 + 4 * S; PAD = 4 * S; STR = 2.5 * S; GAP = 3 * S
    real = [r for r in rows if r != 'GAP']
    wcol = [STR, 0, 0, 0, 0]
    for r_ in real:
        c = 0
        for cell in r_:
            if cell[5] == 1 and c > 0: wcol[c] = max(wcol[c], len(cell[0]) * CWc + 2 * PAD)
            c += cell[5]
    for r_ in real:
        c = 0
        for cell in r_:
            if cell[5] > 1:
                need = len(cell[0]) * CWc + 2 * PAD; have = sum(wcol[c:c + cell[5]])
                if need > have: wcol[2] += need - have
            c += cell[5]
    cx0 = X0 + 4 * S; cy = Y0 + (94 + .035 * 506) * S
    for r_ in rows:
        if r_ == 'GAP': cy += GAP; continue
        c = 0; xx = cx0
        for (s_, fg, bg, bold, ha, spn) in r_:
            w_ = sum(wcol[c:c + spn])
            ov.add_patch(Rectangle((xx, cy), w_, RH, fc=bg, ec='none', zorder=20))
            if s_:
                tx = xx + PAD if ha == 'left' else xx + w_ / 2
                ov.text(tx, cy + RH / 2 + .5, s_, color=fg, fontsize=FONT * .72, family=MONO, weight='bold' if bold else 'normal', ha=ha, va='center', zorder=21)
            xx += w_; c += spn
        cy += RH
    cardW = sum(wcol)
    ov.text(X0 + W / 2, Y0 + H + 34 * S, title, color='#c9ced8', fontsize=11.5 * S * .72, ha='center', va='top', weight='bold')
    return cardW / S

if __name__ == '__main__':
    d = data(sys.argv[1])
    S = 2.0; PWpt, PHpt = 390, 844; M = 70
    global CW, CH
    CW = int(2 * PWpt * S + 3 * M + 40); CH = int(PHpt * S + 2 * M + 140)
    fig = plt.figure(figsize=(CW / DPI, CH / DPI), dpi=DPI, facecolor='#15171c')
    bgax = fig.add_axes([0, 0, 1, 1], facecolor='none', zorder=0); bgax.set_xlim(0, CW); bgax.set_ylim(CH, 0); bgax.axis('off')
    ov = fig.add_axes([0, 0, 1, 1], facecolor='none', zorder=10); ov.set_xlim(0, CW); ov.set_ylim(CH, 0); ov.axis('off')
    w1 = phone(fig, ov, bgax, M + 10, M, S, d, card_rows(d), 'Gran Rey Cero · Layout: Mobile')
    w2 = phone(fig, ov, bgax, 2 * M + 30 + PWpt * S, M, S, d, card_rows(d, mega=True), 'Hueco Mundo megazord · concept')
    ov.text(CW / 2, CH - 40, f'NQ1! 5m · Wed 12 Aug 2026 (CPI) at 11:00 ET · real prices · card text Small, position Top left · VIX from daily closes in the mock',
            color='#8a90a0', fontsize=13, ha='center', va='center')
    print('card widths (pt of a 390 pt screen):', round(w1), round(w2), {k: d[k] for k in ('stB', 'st', 'big', 'fr', 'v', 'q50')})
    fig.savefig(sys.argv[2], dpi=DPI, facecolor=fig.get_facecolor())
    print(sys.argv[2])
