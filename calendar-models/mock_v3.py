"""Gran Rey Cero mocks: NQ1! 5-minute, light theme, at 11:00 ET.
  python3 mock_v3.py 2026-08-12 GranRey_mock_CPI_day.png        (a CPI day)
  python3 mock_v3.py 2026-08-13 GranRey_mock_day_after.png      (the trading day after)
Everything drawn follows Gran_Rey_Cero.pine: card text is read from the script, prices from NQ 1-minute data,
DXY from the DXY futures file."""
import sys, re, json, numpy as np, pandas as pd, matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from events import CPI
plt.rcParams['font.family'] = 'DejaVu Sans'
MONO = 'DejaVu Sans Mono'
DPI = 110
# ── colours (light theme, script defaults)
BG, HD, BD, TX, SUB, MU = '#ffffff', '#eef1f6', '#d5dae4', '#131722', '#4a5163', '#9aa1b2'
WARN, HOT, COLD, OK, NEU = '#ff5252', '#d84315', '#1565c0', '#2e7d32', '#d1d4dc'
GH, LVL, UP, DN, WK, CUP, CDN = '#e53935', '#ffb300', '#089981', '#f23645', '#787b86', '#4caf50', '#131722'
def A(c, transp):                       # Pine color.new(c, transparency) → rgba
    c = c.lstrip('#'); return tuple(int(c[i:i + 2], 16) / 255 for i in (0, 2, 4)) + (1 - transp / 100,)

# ── text and stats straight from the generated script
PINE = open('Gran_Rey_Cero.pine', encoding='utf-8').read()
def strs(fn):
    i = PINE.index('\n' + fn + '(')
    return re.findall(r'"((?:[^"\\]|\\.)*)"', PINE[i:PINE.index('\n        =>', i)])
NAME = strs('pfName')[0]
SL = strs('pfSessLab')[0].split('|'); SV = [float(v) for v in strs('pfSessVal')[1].split('|')]
ROWS = [r.split('~') for r in strs('pfRows')[1].split('|')]
ODDS = [r.split('~') for r in strs('pfOdds')[3].split('|')]           # NQ, trading-day anchor
DXS = strs('pfDx')[1].split('|')
blk = PINE[PINE.index('NQ_TD  ='):PINE.index('NQ_MID')]
ST = [[float(v) for v in r.split(',')] for r in ''.join(re.findall(r'"([^"]*)"', blk)).split(';')]
sv = lambda t, i: ST[t][i]
CK = json.load(open('clock.json'))['NQ']
BUCK = ["18–00", "00–02", "02–07", "07–09:30", "09:30–12", "12–17"]
pf = lambda v: f'{v:,.2f}'.replace(',', '')
x2 = lambda v: f'{v:.2f}×'
p0 = lambda v: f'{v * 100:.0f}%'

b = pd.read_pickle('/home/claude/t3/bars_NQ_all.pkl')
D = pd.read_pickle('days_NQ.pkl'); TDD = D[D.anchor == 'TD'].set_index('tday')
CPIS = sorted(pd.Timestamp(d) for d in CPI); CPISET = set(CPIS)
TDAYS = sorted(pd.Timestamp(t) for t in b.tday.unique())
dx = pd.read_csv('/mnt/user-data/uploads/DXY_2023_2026_5min_continuous.csv')
dx['ts'] = pd.to_datetime(dx.Date + ' ' + dx.Time) + pd.Timedelta(hours=1); dx = dx.sort_values('ts').set_index('ts')

def nextCPI(d): return next((c for c in CPIS if c >= d), None)
def fmtDay(d): return d.strftime('%a %d %b')

def render(day, out):
    day = pd.Timestamp(day); k = TDAYS.index(day); prev = TDAYS[k - 1]
    start = prev + pd.Timedelta(hours=6); end = day + pd.Timedelta(hours=10, minutes=59)
    x1 = b[(b.ts >= start) & (b.ts <= end)]
    x5 = x1.set_index('ts').resample('5min').agg(dict(Open='first', High='max', Low='min', Close='last', tday='last')).dropna(subset=['Open'])
    n = len(x5); idx = np.arange(n); T = x5.index.values.astype('datetime64[m]').astype(np.int64)
    def X(ts):
        m = np.datetime64(pd.Timestamp(ts), 'm').astype(np.int64)
        return n - 1 + (m - T[-1]) / 5 if m > T[-1] else float(np.interp(m, T, idx))
    last = x5.index[-1]; xl = n - 1
    mod = lambda ts: ts.hour * 60 + ts.minute
    isCPI = day in CPISET
    # ── figure
    W, H = 2400, 1340
    fig = plt.figure(figsize=(W / DPI, H / DPI), dpi=DPI, facecolor=BG)
    ax = fig.add_axes([0.012, 0.335, 0.935, 0.635], facecolor=BG)
    bx = fig.add_axes([0.012, 0.035, 0.935, 0.285], facecolor=BG)
    for a_ in (ax, bx):
        for s_ in a_.spines.values(): s_.set_color(BD)
        a_.yaxis.tick_right(); a_.tick_params(labelsize=8, colors=SUB, length=0); a_.grid(color='#f0f3fa', lw=1)
    for i, (t, r) in enumerate(x5.iterrows()):
        c = UP if r.Close >= r.Open else DN
        ax.plot([i, i], [r.Low, r.High], color=c, lw=0.8, zorder=3)
        ax.add_patch(Rectangle((i - 0.33, min(r.Open, r.Close)), 0.66, max(abs(r.Close - r.Open), 0.25), color=c, zorder=3))
    txt = dict(fontsize=7, zorder=6)
    # ── structure for each trading day in view
    for d in [t for t in TDAYS if prev <= t <= day]:
        bars = x5[x5.tday == np.datetime64(d)]
        at = lambda m: d + pd.Timedelta(minutes=m)
        e = X(min(at(974), last))
        dPrev = TDAYS[TDAYS.index(d) - 1]
        gCPI = d in CPISET; gAft = dPrev in CPISET and not gCPI
        if gCPI:
            pr = bars[(bars.index >= at(450)) & (bars.index < at(510))]
            drH, drL = pr.High.max(), pr.Low.min()
            y = b[(b.tday == dPrev) & (b.hm == 1614)]
            rthC = y.Close.iloc[0]
            x0 = X(at(450))
            ax.plot([x0, e], [rthC, rthC], ls=':', color=A(LVL, 25), lw=1, zorder=4)
            ax.text(e + 0.6, rthC, 'yday RTH close', color=A(LVL, 15), va='center', **txt)
            for yv, lab, va in ((drH, 'stage 1 · DR high', 'bottom'), (drL, 'stage 1 · DR low', 'top')):
                ax.plot([x0, e], [yv, yv], ls='--', color=LVL, lw=1, zorder=4)
                ax.text(x0, yv + (6 if va == 'bottom' else -6), lab, color=LVL, va=va, ha='left', **txt)
            post = bars[(bars.index >= at(510)) & (bars.index < at(975))]
            for t, r in post.iterrows():
                if r.Low < drL:
                    ax.annotate('1st sweep ▼', (X(t), r.Low), xytext=(0, -6), textcoords='offset points', ha='center', va='top', color=LVL, **txt); break
                if r.High > drH:
                    ax.annotate('1st sweep ▲', (X(t), r.High), xytext=(0, 6), textcoords='offset points', ha='center', va='bottom', color=LVL, **txt); break
            if last >= at(530): ax.axvline(X(at(530)), color=A(LVL, 60), ls=':', lw=1, zorder=2)
            o930 = bars[bars.index >= at(570)]
            if len(o930) and last >= at(570):
                gce = (rthC + o930.Open.iloc[0]) / 2
                ax.plot([X(at(570)), e], [gce, gce], ls=':', color=A(LVL, 20), lw=1, zorder=4)
                ax.text(e + 0.6, gce, 'gap 50%', color=LVL, va='center', **txt)
        if (gCPI or gAft) and d.weekday() < 5:
            w = bars[(bars.index >= at(510)) & (bars.index < at(540))]
            if len(w):
                wT, wB = w.High.max(), w.Low.min(); xa, xb = X(at(510)), X(min(at(540), last + pd.Timedelta(minutes=5)))
                ax.add_patch(Rectangle((xa, wB), xb - xa, wT - wB, facecolor=A(GH, 78 if gCPI else 92), edgecolor=A(GH, 35 if gCPI else 70), lw=1, zorder=2))
                if gAft:
                    ax.text(xa, wT + 5, 'you just missed me folks', color=A(GH, 25), va='bottom', ha='left', fontsize=7.5, zorder=6)
        elif d.weekday() < 5:
            r = bars[bars.index == at(510)]
            if len(r):
                ax.annotate('nothing to see here folks', (X(at(510)), r.High.iloc[0]), xytext=(0, 7), textcoords='offset points', ha='center', va='bottom', color=A(MU, 20), fontsize=7.5, zorder=6)
    # every CPI 08:30 candle (5-minute chart → the 08:30 bar), last 6, extended to the latest bar
    keep = [c for c in CPIS if c <= day][-6:]
    rcs = []
    for c in keep:
        if c == day and last < c + pd.Timedelta(minutes=515): continue
        r = b[(b.tday == c) & (b.hm >= 830) & (b.hm < 835)]
        rcH, rcL = r.High.max(), r.Low.min(); tO = b[b.tday == c].Open.iloc[0]
        ad = TDD.adr.loc[c] if c in TDD.index else TDD.adr[TDD.index > c].iloc[0]
        xr = (rcH - rcL) / (tO * ad); cat = 'wild' if xr >= .432 else 'quiet' if xr < .202 else 'average'
        rcs.append((c, rcH, rcL, cat, xr))
    # ── PO3 slots
    O = TDD.loc[day].O; a = TDD.loc[day].adr; scP = O * a
    tdb = x5[x5.tday == np.datetime64(day)]
    dO, dH, dL, dC = tdb.Open.iloc[0], tdb.High.max(), tdb.Low.min(), tdb.Close.iloc[-1]
    wk0 = day - pd.Timedelta(days=day.weekday())
    wk = b[(b.tday >= wk0) & (b.ts <= end)]
    wO, wH, wL, wC = wk.Open.iloc[0], wk.High.max(), wk.Low.min(), wk.Close.iloc[-1]
    pNow = isCPI; gc = GH; ga = 0 if pNow else 55
    mR = sv(2, 10) * a * O; uS = sv(2, 3) / (sv(2, 3) + sv(2, 6)); mH = O + mR * uS; mL = O - mR * (1 - uS); mC = O * (1 + sv(2, 8) * a)
    offI, widI, gapI = 24, 8, 10; gw = widI + 6; xd = xl + offI; xc = xd + gw // 2; xw = xd + gw + gapI
    ax.add_patch(Rectangle((xd + 2, mL), gw - 4, mH - mL, facecolor=A(GH, 90 + ga * .1), edgecolor=A(GH, 40 + ga * .5), ls=':', lw=1, zorder=4))
    ax.add_patch(Rectangle((xd, min(O, mC)), gw, abs(mC - O), facecolor=A(GH, 70 + ga * .3), edgecolor=A(GH, ga), lw=1, zorder=4))
    for yv in (mH, mL):
        ax.plot([xd, xd + gw], [yv, yv], color=A(GH, ga), lw=2, zorder=5)
        ax.text(xd - 0.6, yv, pf(yv), color=A(GH, ga), ha='right', va='center', **txt)
    dX = X(tdb.index[0])
    for yv in (mH, mL): ax.plot([dX, xd], [yv, yv], ls=':', color=A(GH, 45 if pNow else 75), lw=1, zorder=2)
    for yv, al in ((dO, 30), (dH, 50), (dL, 50)): ax.plot([dX, xd], [yv, yv], ls=':', color=A(WK, al), lw=1, zorder=2)
    def candle(x0, w, o, h, l, c):
        ax.plot([x0 + w / 2] * 2, [l, h], color=WK, lw=1, zorder=5)
        ax.add_patch(Rectangle((x0, min(o, c)), w, max(abs(c - o), 0.5), facecolor=CUP if c >= o else CDN, edgecolor=WK, lw=1, zorder=5))
    candle(xd + 3, widI, dO, dH, dL, dC); candle(xw, widI, wO, wH, wL, wC)
    for yv in (dH, dL): ax.text(xd + gw + 0.6, yv, pf(yv), color=SUB, va='center', **txt)
    for yv in (wH, wL): ax.text(xw + widI + 0.6, yv, pf(yv), color=SUB, va='center', **txt)
    nx = nextCPI(day + pd.Timedelta(days=0 if pNow else 1))
    chipD = ['1D · CPI DAY' if pNow else f'1D · next CPI {fmtDay(nx)}', f'range {pf(dH - dL)}', f'model {pf(mR)}' + (f' · {p0((dH - dL) / mR)} filled' if pNow else '')]
    def chip(xc_, y, lines, above=True):
        ax.annotate('\n'.join(lines), (xc_, y), xytext=(0, 7 if above else -7), textcoords='offset points', ha='center', va='bottom' if above else 'top', fontsize=7.3, family=MONO, color=TX, zorder=8,
                    bbox=dict(boxstyle='round,pad=0.4,rounding_size=0.3', fc=BG, ec=BD, lw=0.8))
    chip(xc, max(dH, mH), chipD); chip(xw + widI / 2, wL, ['1W', f'range {pf(wH - wL)}'], above=False)
    # extended CPI candles (after the PO3 so the labels sit on top)
    lo = min(x5.Low.min(), mL, wL); hi = max(x5.High.max(), mH, wH)
    for i_, (c, rcH, rcL, cat, xr) in enumerate(rcs):
        if rcL > hi + 60 or rcH < lo - 60: continue
        newest = i_ == len(rcs) - 1
        xa = max(X(c + pd.Timedelta(minutes=510)), -5)
        ax.add_patch(Rectangle((xa, rcL), xl - xa, rcH - rcL, facecolor=A(GH, 86 if newest else 93), edgecolor=A(GH, 15 if newest else 55), lw=1, zorder=2))
        ax.text(xl + 0.6, (rcH + rcL) / 2, f'CPI {c:%d/%m} · {cat}', color=GH if newest else A(GH, 35), va='center', fontsize=8, zorder=7)
    span = hi - lo
    ax.set_ylim(lo - span * 0.10, hi + span * 0.30)
    ax.set_xticks([])
    # ── clock pane
    ckEv = isCPI; bi = 'CPI' if ckEv else 'NORMAL'; ri = 'NORMAL' if ckEv else 'CPI'
    ce = GH if ckEv else SUB; cR = MU if ckEv else A(GH, 25)
    t0 = day - pd.Timedelta(hours=6)
    xs = [X(t0)] + [X(t0 + pd.Timedelta(minutes=30 * (j + 1))) for j in range(46)]
    q = lambda nm, kk: np.array([0] + CK[nm]['R'][kk]) * scP
    bx.fill_between(xs, q(bi, 0), q(bi, 4), color=ce, alpha=.10, lw=0)
    bx.fill_between(xs, q(bi, 1), q(bi, 3), color=ce, alpha=.20, lw=0)
    bx.plot(xs, q(bi, 2), color=ce, lw=2)
    bx.plot(xs, q(ri, 2), color=cR, lw=1, ls='--')
    nm = lambda s: 'CPI' if s == 'CPI' else 'Normal'
    bx.text(xs[-1] + 0.6, q(bi, 2)[-1], f'{nm(bi)} median {pf(q(bi, 2)[-1])}', color=ce, fontsize=7, va='center')
    bx.text(xs[-1] + 0.6, q(ri, 2)[-1], f'{nm(ri)}{"" if ckEv else " (next)"} {pf(q(ri, 2)[-1])}', color=cR, fontsize=7, va='center')
    bx.axvline(X(day + pd.Timedelta(minutes=510)), color=A(GH, 30 if ckEv else 70), ls=':', lw=1)
    rr = []; hh = ll = None
    for i, (t, r) in enumerate(x5.iterrows()):
        if i == 0 or x5.tday.iloc[i] != x5.tday.iloc[i - 1]: hh, ll = r.High, r.Low
        hh = max(hh, r.High); ll = min(ll, r.Low); rr.append(hh - ll)
    rr = np.array(rr); td = x5.tday.values == np.datetime64(day)
    eEnd = min(1380, (mod(last) - 1080) % 1440 + 5); jB = min(45, max(0, int(np.ceil(eEnd / 30)) - 1)); fB = (eEnd - 30 * jB) / 30
    ckAt = lambda nm_, kk: (CK[nm_]['R'][kk][jB - 1] if jB else 0) + (CK[nm_]['R'][kk][jB] - (CK[nm_]['R'][kk][jB - 1] if jB else 0)) * fB
    v = rr[-1] / scP; q10, q25, q50, q75, q90 = [ckAt(bi, kk) for kk in range(5)]
    stB = 'Above' if v > q75 else 'Below' if v < q25 else 'Inside'
    liveC = {'Above': HOT, 'Below': COLD, 'Inside': TX}[stB]
    for dd in sorted(set(x5.tday.values)):
        m_ = x5.tday.values == dd
        if dd == np.datetime64(day): bx.plot(idx[m_], rr[m_], color=liveC, lw=2.6, zorder=5)
        else: bx.plot(idx[m_], rr[m_], color=SUB, alpha=.25, lw=1)
    bx.set_ylim(0, max(max(CK[bi]['R'][4][45], CK['NORMAL']['R'][4][45]) * scP * 1.75, rr.max() * 1.05))
    ticks = [i for i in range(n) if x5.index[i].minute == 0 and x5.index[i].hour % 3 == 0]
    bx.set_xticks(ticks); bx.set_xticklabels([x5.index[i].strftime('%H:%M') if x5.index[i].hour else x5.index[i].strftime('%d %b') for i in ticks])
    bx.text(0.004, 0.965, 'Gran Rey Cero · event clock', transform=bx.transAxes, fontsize=8, color=SUB, va='top')
    ax.text(0.004, 0.985, f'NQ1! · 5 · CME   Gran Rey Cero   ({fmtDay(day)} 11:00 ET, mock)', transform=ax.transAxes, fontsize=8.5, color=SUB, va='top')

    # ── cards (TradingView tables: monospace, 1 px borders, merged cells)
    ov = fig.add_axes([0, 0, 1, 1], facecolor='none'); ov.set_xlim(0, W); ov.set_ylim(H, 0); ov.axis('off')
    FS = 7.0; CW = FS * DPI / 72 * 0.602; RH = FS * DPI / 72 * 1.75; PAD = 5
    def card(rows, ncol, right, top, draw=True):
        # rows: list of lists of (text, fg, bg, bold, halign, span)
        wcol = [0.0] * ncol
        for row in rows:
            c = 0
            for cell in row:
                if cell[5] == 1: wcol[c] = max(wcol[c], len(cell[0]) * CW + 2 * PAD)
                c += cell[5]
        for row in rows:
            c = 0
            for cell in row:
                s = cell[5]
                if s > 1:
                    need = len(cell[0]) * CW + 2 * PAD; have = sum(wcol[c:c + s])
                    if need > have:
                        tot = sum(max(w, 1) for w in wcol[c:c + s])
                        for j in range(c, c + s): wcol[j] += (need - have) * max(wcol[j], 1) / tot
                c += s
        width = sum(wcol); x0 = right - width; y = top
        if not draw: return width
        for row in rows:
            c = 0; xx = x0
            for (t, fg, bg, bold, ha, s) in row:
                w = sum(wcol[c:c + s])
                ov.add_patch(Rectangle((xx, y), w, RH, facecolor=bg, edgecolor=BD, lw=0.8))
                tx = xx + PAD if ha == 'left' else xx + w / 2
                ov.text(tx, y + RH / 2 + 0.5, t, color=fg, fontsize=FS, family=MONO, weight='bold' if bold else 'normal', ha=ha, va='center')
                xx += w; c += s
            y += RH
        return x0, y
    pill = lambda g: (OK if g == '✓' else WARN if g == '✗' else NEU if g == '≈' else BG, TX if g == '≈' else '#ffffff')
    heat = lambda r: HOT if r >= 1.15 else A(HOT, 40) if r >= 1.05 else COLD if r <= .85 else A(COLD, 40) if r <= .95 else SUB
    # profile card
    dd = (nx - day).days
    cV = TX if pNow else SUB
    P = [[('◆ ' + NAME + ' · NQ', '#ffffff', GH, True, 'left', 7), ('TODAY' if pNow else ('TOMORROW' if dd == 1 else f'IN {dd}D'), GH if pNow else '#ffffff', '#ffffff' if pNow else A('#000000', 55), True, 'center', 1)],
         [('SESSION', MU, HD, False, 'left', 1)] + [(s_, SUB, HD, False, 'center', 1) for s_ in SL] + [('', MU, HD, False, 'left', 1)],
         [('vs normal', SUB, BG, False, 'left', 1)] + [(f'{r * 100:.0f}', heat(r), BG, True, 'center', 1) for r in SV] + [('%', MU, BG, False, 'center', 1)],
         [('', MU, HD, False, 'left', 1), ('MODEL · ODDS · 2018–26', MU, HD, False, 'left', 5), ('CPI', MU, HD, False, 'center', 1), ('normal', MU, HD, False, 'center', 1)]]
    def prow(g, lab, v_, b_, fg, key=None):
        bgc, fgc = pill(g) if key is None else (BG, MU)
        return [((g if key is None else key), fgc, bgc, key is None, 'center', 1), (lab, fg, BG, False, 'left', 5), (v_, fg, BG, True, 'center', 1), (b_, MU, BG, False, 'center', 1)]
    for g, lab, v_, b_, _ in ROWS[:5]: P.append(prow(g, lab, v_, b_, cV))
    for f_ in ODDS: P.append(prow(f_[0], f_[1], f_[2], f_[3], TX))
    tdStart = day - pd.Timedelta(hours=6)
    dxPrev = dx[dx.index < tdStart].Close.iloc[-1]; dxNow = dx[dx.index <= end].Close.iloc[-1]; dxDay = dxNow / dxPrev - 1
    up_ = dxDay >= 0
    P.append(prow('', f'today {"▲" if up_ else "▼"} {abs(dxDay) * 100:.2f}% → NQ up', DXS[0] if up_ else DXS[1], DXS[3] if up_ else DXS[4], TX, key='DXY'))
    P.append(prow('', f'range ÷ ADR20 ({pf(scP)} pts)', x2(sv(2, 10)), x2(sv(6, 10)), cV, key='RANGE'))
    iH = max(range(6), key=lambda i: sv(2, 12 + i) - sv(6, 12 + i)); iL = max(range(6), key=lambda i: sv(2, 18 + i) - sv(6, 18 + i))
    P.append(prow('', f'high in {BUCK[iH]} ET', p0(sv(2, 12 + iH)), p0(sv(6, 12 + iH)), cV, key='TIMING'))
    P.append(prow('', f'low in {BUCK[iL]} ET', p0(sv(2, 18 + iL)), p0(sv(6, 18 + iL)), cV, key=''))
    wkc = dx.Close.resample('W-FRI').last(); wkc = wkc[wkc.index < day]
    dx4 = wkc.iloc[-1] / wkc.iloc[-5] - 1
    mac = f'DXY 4wk {"▲" if dx4 >= 0 else "▼"} {abs(dx4) * 100:.1f}% → range ' + ('1.02× ADR (▼ 0.91×)' if dx4 >= 0 else '0.91× ADR (▲ 1.02×)') + ' · 10Y —'
    P.append([('MACRO', MU, BG, False, 'center', 1), (mac, HOT if dx4 >= 0 else COLD, BG, False, 'left', 7)])
    n1 = nextCPI(day); n2 = nextCPI(n1 + pd.Timedelta(days=1)); dn = (n1 - day).days
    P.append([('NEXT', MU, BG, False, 'center', 1), (f'CPI 08:30 · {fmtDay(n1)} · {"today" if dn == 0 else "tomorrow" if dn == 1 else f"in {dn}d"}  →  then {fmtDay(n2)}', TX, BG, False, 'left', 7)])
    P.append([('✓ held 2025–26 · ≈ no edge · ✗ faded · ± 95% · dates to 10 Dec 2027', MU, BG, False, 'left', 8)])

    # clock card
    nowT = '11:00'
    sh = (CK[bi]['share'][jB - 1] if jB else 0) + (CK[bi]['share'][jB] - (CK[bi]['share'][jB - 1] if jB else 0)) * fB
    pc = 5 if v < q10 else 10 + 15 * (v - q10) / (q25 - q10) if v <= q25 else 25 + 25 * (v - q25) / (q50 - q25) if v <= q50 else 50 + 25 * (v - q50) / (q75 - q50) if v <= q75 else 75 + 15 * (v - q75) / (q90 - q75) if v <= q90 else 95
    kk = int(round(min(100, max(0, pc)) / 10)); meter = '─' * kk + '●' + '─' * (10 - kk)
    pT = '<P10' if pc <= 5 else '>P90' if pc >= 95 else f'≈P{pc:.0f}'
    g10 = int(round(min(1, max(0, sh)) * 10)); gauge = '█' * g10 + '░' * (10 - g10)
    med = np.array(CK[('CPI')]['R'][2]); dif = np.diff(np.r_[0, med]); bj = int(np.argmax(dif))
    nmed = np.array(CK['NORMAL']['R'][2]); nD = np.diff(np.r_[0, nmed])[bj]
    hh_ = lambda m: f'{(m // 60) % 24:02d}:{m % 60:02d}'
    stepEnd = lambda j: (1080 + 30 * (j + 1)) % 1440
    sBg = HOT if stB == 'Above' else COLD if stB == 'Below' else NEU; sFg = TX if stB == 'Inside' else '#ffffff'
    pl = {'Above': '▲ ABOVE', 'Below': '▼ BELOW', 'Inside': '● INSIDE'}[stB]
    bN = nm(bi); fd = CK[bi]['R'][2][45]
    K = [[(f'◆ GRAN REY CERO · CLOCK · {nowT} ET', '#ffffff', GH, True, 'left', 2), ('CPI DAY' if ckEv else 'NORMAL', GH if ckEv else '#ffffff', '#ffffff' if ckEv else A('#000000', 55), True, 'center', 1)],
         [('NOW', MU, BG, False, 'left', 1), (f'range {pf(rr[-1])} pts · {x2(v)} ADR', TX, BG, True, 'left', 1), (pl, sFg, sBg, True, 'center', 1)],
         [(f'vs {bN}', MU, BG, False, 'left', 1), (f'{meter} {pT}', HOT if stB == 'Above' else COLD if stB == 'Below' else SUB, BG, False, 'left', 1), (f'typ {pf(q50 * scP)}', SUB, BG, False, 'center', 1)],
         [('DONE', MU, BG, False, 'left', 1), (f'{gauge} {p0(sh)} of the day\'s range', TX, BG, False, 'left', 1), (f'→ ≈ {pf(rr[-1] / sh)}' if sh >= .25 else '—', SUB, BG, False, 'center', 1)],
         [('FULL DAY', MU, BG, False, 'left', 1), (f'{CK[bi]["n"]} {bN} days: {x2(fd)} = {pf(fd * scP)} pts', TX, BG, False, 'left', 1), (f'norm {x2(CK["NORMAL"]["R"][2][45])}' if ckEv else '', SUB, BG, False, 'center', 1)],
         [('BUSIEST', MU, BG, False, 'left', 1), (f'CPI days {hh_(stepEnd(bj - 1))}–{hh_(stepEnd(bj))} · +{x2(dif[bj])} ADR', GH if ckEv else SUB, BG, False, 'left', 1), (f'norm +{x2(nD)}', SUB, BG, False, 'center', 1)]]
    axb = ax.get_position(); axW = (axb.x1 - axb.x0) * W
    cw_ = max(card(P, 8, 0, 0, draw=False), card(K, 3, 0, 0, draw=False)) + 70 + 40      # card + its inset + a little air
    B = xw + widI + 4; m = cw_ * B / (axW - cw_)                                          # right margin (bars) that fits the card
    ax.set_xlim(-2, B + m); bx.set_xlim(ax.get_xlim())
    card(P, 8, axb.x1 * W - 70, (1 - axb.y1) * H + 3)
    bxb = bx.get_position(); card(K, 3, bxb.x1 * W - 70, (1 - bxb.y1) * H + 0.07 * bxb.height * H)
    fig.savefig(out, dpi=DPI, facecolor=BG)
    print(out, dict(O=O, adr=a, mR=round(mR, 2), rng=dH - dL, stB=stB, v=round(v, 3), sh=round(sh, 3), dxDay=round(dxDay * 100, 3), dx4=round(dx4 * 100, 2), rcs=[(str(c.date()), cat, round(xr, 3)) for c, _, _, cat, xr in rcs]))

if __name__ == '__main__':
    render(sys.argv[1], sys.argv[2])
