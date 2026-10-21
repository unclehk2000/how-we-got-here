"""Mocks of Desgarrón v2 on NQ1! 5-minute, NFP day Fri 2 Oct 2026, values computed the way the script computes them from NQ
1-minute bars, the HYDRA calendar tables and the pooled card data in Desgarron.pine.
  1) 07:04 ET (your replay moment): the dealing range forming live from 07:00, the ATH line, the stages card in SETUP /
     EXPECT, the pane with the clock and the findings table.
  2) 10:30 ET: the dealing range fixed, the 08:30 ATH CE (hit), the stages card LIVE, the findings live.
  3) Mobile layout at 10:30.
  python3 mock_desg2.py out1 out2 out3"""
import sys, re, json, numpy as np, pandas as pd
OUT = sys.argv[1:4]
src = open('/home/claude/hm/calgen/mock_cal.py', encoding='utf-8').read().split('# ═══════════ Cero state')[0]
sys.argv = ['x']; exec(src)
mod_tal['Desgarron'] = 'NFP'
PS = open('/home/claude/hm/calgen/Desgarron.pine', encoding='utf-8').read()
VS = [float(v) for v in re.search(r'var array<float> VS = parseStats\("([^"]+)"\)', PS).group(1).split(',')]
VH = re.search(r'\nVH = "([01]+)"', PS).group(1)
P92 = "!#$%&'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[]^_`abcdefghijklmnopqrstuvwxyz{|}~"
blk = re.search(r'(?m)^CK_NQ\s*=\s*"[^"]*"(?:\n\s+\+\s*"[^"]*")*', PS).group(0); ckS = ''.join(re.findall(r'"([^"]*)"', blk))
CKv = [(P92.index(ckS[2 * i]) * 92 + P92.index(ckS[2 * i + 1]) - 2000) / 1000 for i in range(len(ckS) // 2)]
ck = lambda i, m, k, j: CKv[i * 506 + m * 230 + k * 46 + j]
ckSh = lambda i, j: CKv[i * 506 + 460 + j]
GH, ATHC, HY, DR0 = '#ff7043', '#ab47bc', '#5e35b1', '#90a4ae'
vh = lambda i: VH[i] == '1'; hlH_ = lambda i: vh(i) or vh(i + 1)
pcV = lambda i: '—' if VS[i] < 0 else f'{VS[i]:.0f}'
hl = lambda i: f'H{pcV(i)} L{pcV(i + 1)}'
rg = lambda i: f'R{VS[i]:.2f}'
sgP = lambda v: '—' if v is None or not np.isfinite(v) else f'{v:.0f}'
zWd = lambda z: ['DISC', 'MID', 'PREM'][z]
ceOdds = lambda x: '—' if x is None or not np.isfinite(x) else '83%' if x <= 0.5 else '31%' if x <= 1 else '6%' if x <= 2 else '0%'
T = pd.Timestamp('2026-10-02'); at = lambda h, mi: T + pd.Timedelta(hours=h, minutes=mi)
g = b[b.tday == T].set_index('ts'); F = NFP.loc[T]; A = float(F.adr); C0 = CTX.loc[T]
mon = CTX[(CTX.index.year == 2026) & (CTX.index.month == 10) & (CTX.index < T)]
ATH0, ATH0d = 31151.5, pd.Timestamp('2026-10-01')
wk0 = pd.Timestamp('2026-09-27 18:00'); mo0 = pd.Timestamp('2026-09-30 18:00')
WO = float(m1.Open[m1.index >= wk0].iloc[0])
VIXc, VIXr = float(F.vix), float(F.vixRel)

def state(now):
    y = g[g.index <= now]; cl = float(y.Close.iloc[-1]); tdO = float(y.Open.iloc[0]); tH, tL = y.High.max(), y.Low.min()
    s = dict(now=now, y=y, cl=cl, tdO=tdO, tH=tH, tL=tL)
    st = now >= at(8, 30)
    if st:                                                   # fixed at 08:29
        c = float(F.price); pre = y[y.index < at(8, 30)]; h, l = pre.High.max(), pre.Low.min()
    else:
        c, h, l = cl, tH, tL
    mH, mL = max(mon.H.max(), h), min(mon.L.min(), l)
    s.update(st=st, c59=c, p=(c - mL) / (mH - mL), m=(c - C0.MO) / A, d=(c - C0.PDH) / A if c > C0.PDH else (c - C0.PDL) / A if c < C0.PDL else 0.0,
             s=(c - tdO) / A, w=(c - WO) / A, v=VIXr)
    athN = max(ATH0, tH); s['athN'] = athN; s['athTd'] = tH >= ATH0
    s['athT'] = y.High.idxmax() if s['athTd'] else ATH0d
    p7 = y[(y.index >= at(7, 0)) & (y.index < at(8, 30))]; s['p7H'], s['p7L'] = (p7.High.max(), p7.Low.min()) if len(p7) else (np.nan, np.nan)
    dr = y[(y.index >= at(7, 0)) & (y.index < at(9, 0))]; s['drH'], s['drL'] = dr.High.max(), dr.Low.min()
    if st:
        q = y[(y.index >= at(8, 30)) & (y.index < at(16, 15))]; s['qH'], s['qL'] = q.High.max(), q.Low.min()
        hit_u = q.index[q.High > s['p7H']]; hit_d = q.index[q.Low < s['p7L']]
        tu = hit_u[0] if len(hit_u) else None; td_ = hit_d[0] if len(hit_d) else None
        s['fsd'] = 0 if tu is None and td_ is None else (2 if tu == td_ else 1 if td_ is None or (tu is not None and tu < td_) else -1)
        s['fsT'] = tu if s['fsd'] == 1 else td_
        aC = max(ATH0, pre.High.max()); s['ceAt'] = aC; s['ceV'] = (aC + c) / 2; s['ceD'] = (s['ceV'] - c) / A
        hc = q.index[q.High >= s['ceV']]; s['ceHT'] = hc[0] if len(hc) else None
        px = lambda t, col='Close': float(g.loc[t, col])
        s['s1O'], s['s2O'], s['rthO'] = px(at(8, 30), 'Open'), px(at(8, 50), 'Open'), px(at(9, 30), 'Open')
        s['sv1'] = px(at(8, 49)) - s['s1O'] if now >= at(8, 50) else cl - s['s1O']
        s['sv2'] = (px(at(9, 29)) - s['s2O']) if now >= at(9, 30) else cl - s['s2O']
        s['svA'] = (px(at(10, 59)) if now >= at(11, 0) else cl) - s['rthO']
        to9 = y[y.index < at(9, 0)]; s['add'] = ((to9.High.max() - to9.Low.min()) - (pre.High.max() - pre.Low.min())) / A
    return s

def groups(s):
    z = zIdx(s['p']); oc = min(8, int(np.floor(s['p'] * 8)) + 1)
    mo3 = 0 if s['m'] > 1 else 2 if s['m'] < -1 else 1; pg = 0 if s['d'] > 0 else 2 if s['d'] < 0 else 1
    sg = 0 if s['s'] > 0.4 else 2 if s['s'] < -0.4 else 1; wg = 0 if s['w'] > 0.5 else 2 if s['w'] < -0.5 else 1
    vg = 0 if s['v'] > 0.1 else 2 if s['v'] < -0.1 else 1
    return z, oc, mo3, pg, sg, wg, vg
ZBG = [DISC, NEU, PREM]
def stage_rows(s, mobile=False):
    z, oc, mo3, pg, sg, wg, vg = groups(s); a = A; st = s['st']
    zW = ['DISCOUNT', 'MIDDLE', 'PREMIUM'][z]; zfg = TX if z == 1 else '#ffffff'; zbg = ZBG[z]
    e1, e2, eA, eR = VS[2 * z] * a, VS[6 + 2 * z] * a, VS[12 + 2 * z] * a, VS[18 + 2 * z] * a
    pdT = f'above PDH {sgs(s["d"] * a)}' if pg == 0 else f'below PDL {sgs(s["d"] * a)}' if pg == 2 else 'inside prior day'
    vxT = f'VIX {VIXc:.1f} · {fds(100 * s["v"], "{:.0f}")}% vs 20d'
    zH = hlH_(42 + 2 * z) or vh(18 + 2 * z)
    lt = lambda sv: f'{sgs(sv)} · DXY —'
    dash = ('—', TX, BODY)
    if not mobile:
        rows = [H_(GH, '◆ NFP STAGES · NQ1!', zW, zfg, zbg), S_(GH, ('SETUP AT 08:29 · ' if st else 'SETUP LIVE · ') + 'NFP TODAY', 'ADR', 'after'),
                R_(GH, 'MONTH', f'{octbar(oc)} O{oc}', pc(s['p']), hl(42 + 2 * z), held=zH, vfg=None if z == 1 else zbg, rfg=SUB),
                R_(GH, 'MO', f'vs month open {sgs(s["m"] * a)}', fds(s['m']), rg(48 + mo3), held=vh(48 + mo3), vfg=[HOT, None, COLD][mo3], rfg=SUB),
                R_(GH, 'PD', pdT, '' if pg == 1 else fds(s['d']), hl(30 + 2 * pg), held=hlH_(30 + 2 * pg), rfg=SUB),
                R_(GH, '18:00', f'since 18:00 {sgs(s["s"] * a)}', fds(s['s']), hl(36 + 2 * sg), held=hlH_(36 + 2 * sg), vfg=[DISC, None, PREM][sg], rfg=SUB),
                R_(GH, 'WEEK', f'week in {sgs(s["w"] * a)}', fds(s['w']), rg(54 + wg), held=vh(54 + wg), vfg=[DISC, None, PREM][wg], rfg=SUB),
                R_(GH, 'VIX', vxT, '', rg(51 + vg), held=vh(51 + vg), rfg=SUB)]
        if st:
            r1, r2 = abs(s['sv1']) / e1, abs(s['sv2']) / e2; rq = s['qH'] - s['qL']; rR = rq / eR
            rows += [S_(DXC, 'LIVE · vs DXY', '×typ', 'DXY'),
                     R_(GH, 'S1', lt(s['sv1']), x2(r1), vfg=HOT if r1 >= 1 else None, pill=dash),
                     R_(GH, 'S2', lt(s['sv2']), x2(r2), vfg=HOT if r2 >= 1 else None, pill=dash),
                     R_(GH, 'RANGE', f'since 08:30 {rq:.0f} pts', x2(rR), f'med {eR:.0f}', held=vh(18 + 2 * z), vfg=HOT if rR >= 1 else None)]
        else:
            rows += [S_(GH, f'EXPECT · {zWd(z)} · ADR {a:.0f}', 'med', '80%'),
                     R_(GH, 'RANGE', 'after 08:30', f'{eR:.0f}', f'{VS[19 + 2 * z] * a:.0f}', held=vh(18 + 2 * z)),
                     R_(GH, 'NY AM', '09:30–11:00', f'±{eA:.0f}', f'±{VS[13 + 2 * z] * a:.0f}', held=vh(12 + 2 * z)),
                     R_(GH, 'S1/S2', '08:30–08:50 / –09:30', f'±{e1:.0f}/{e2:.0f}', f'±{VS[1 + 2 * z] * a:.0f}/{VS[7 + 2 * z] * a:.0f}')]
        return rows
    rows = [H_(GH, '◆ NFP · NQ1!', zWd(z), zfg, zbg),
            R_(GH, 'MO', f'{octbar(oc)} {pc(s["p"])}', fds(s['m']), hl(42 + 2 * z), held=zH, vfg=[HOT, None, COLD][mo3])]
    if st:
        in2 = s['now'] >= at(8, 50); sv, e = (s['sv2'], e2) if in2 else (s['sv1'], e1); rq = s['qH'] - s['qL']
        rows += [R_(GH, 'S2' if in2 else 'S1', lt(sv), x2(abs(sv) / e), pill=dash),
                 R_(GH, 'RANGE', f'since 08:30 {rq:.0f}', x2(rq / eR), f'med {eR:.0f}', held=vh(18 + 2 * z))]
    else:
        rows += [R_(GH, 'EXP', f'range {eR:.0f} · AM ±{eA:.0f}', f'{VS[19 + 2 * z] * a:.0f}', '80%', held=vh(18 + 2 * z)),
                 R_(GH, 'PD', ('> PDH ' if pg == 0 else '< PDL ' if pg == 2 else 'in PD ') + hl(30 + 2 * pg), '', '', held=hlH_(30 + 2 * pg))]
    rows.append(R_(GH, 'WK·VX', f'wk {fds(s["w"])} · VIX {fds(100 * s["v"], "{:.0f}")}%', rg(54 + wg), rg(51 + vg), held=vh(54 + wg) or vh(51 + vg)))
    return rows

def find_rows(s, mobile=False):
    z, oc, mo3, pg, sg, wg, vg = groups(s); a = A; st = s['st']
    eR = VS[18 + 2 * z] * a
    tg, bg_, sm_ = '', int(z == 0), int(z == 2)
    if mo3 != 1: tg += ('MO↑ ' if mo3 == 0 else 'MO↓ '); bg_ += mo3 == 2; sm_ += mo3 == 0
    if vg != 1: tg += ('VIX↑ ' if vg == 0 else 'VIX↓ '); bg_ += vg == 0; sm_ += vg == 2
    if wg != 1: tg += ('WK↑ ' if wg == 0 else 'WK↓ '); bg_ += wg == 2; sm_ += wg == 0
    if pg == 2: tg += '<PDL '; bg_ += 1
    if sg == 2: tg += '18↓ '; bg_ += 1
    agr = 'BIGGER' if bg_ > 0 and sm_ == 0 else 'SMALLER' if sm_ > 0 and bg_ == 0 else 'MIXED' if bg_ > 0 else 'TYPICAL'
    agc = ('#ffffff', HOT) if agr == 'BIGGER' else ('#ffffff', COLD) if agr == 'SMALLER' else (TX, NEU)
    xi = 36 + 2 * sg if sg != 1 else 30 + 2 * pg if pg != 1 else 42 + 2 * z
    xn = '18:00↑' if sg == 0 else '18:00↓' if sg == 2 else '>PDH' if pg == 0 else '<PDL' if pg == 2 else zWd(z)
    if st: ceX, ceD = s['ceV'], s['ceD']; ceS = f'hit {s["ceHT"]:%H:%M}' if s['ceHT'] is not None else 'open'
    else: ceX = (s['athN'] + s['cl']) / 2; ceD = (ceX - s['cl']) / a; ceS = 'at 08:30'
    ceH = ceD <= 0.5 or ceD > 1
    fsR = '79%' if vg == 2 else '74%' if wg == 0 else '46%' if wg == 1 else '59%'
    fsH = vg == 2 or wg == 0 or wg == 1
    fsW = 'VIX low' if vg == 2 else 'week up' if wg == 0 else 'flat wk' if wg == 1 else 'all'
    fsX = ('no break yet' if st else 'break from 08:30') if not st or s['fsd'] == 0 else 'both sides, one bar' if s['fsd'] == 2 else 'break ' + ('▲ ' if s['fsd'] == 1 else '▼ ') + f'{s["fsT"]:%H:%M}'
    nH = int(vh(18 + 2 * z)) + int(tg != '') + int(hlH_(xi)) + int(ceH) + int(fsH) + 3
    dash = ('—', TX, BODY)
    if not mobile:
        rows = [H_(HY, '◆ GRIMMJOW · NFP', f'{nH} ✓', HY, '#ffffff'),
                S_(HY, f'NQ+ES+RTY · ADR {a:.0f}', 'today', 'base'),
                W_(HY, 'SIDE', 'none held: size the day', SUB),
                R_(HY, 'RANGE', f'after 08:30 · {zWd(z)}', f'{eR:.0f}', f'all {0.95 * a:.0f}', held=vh(18 + 2 * z)),
                R_(HY, 'SIZE+', tg if tg else 'none active', '', '', held=tg != '', pill3=(agr, agc[0], agc[1])),
                R_(HY, 'H/L', f'after 08:30 · {xn}', hl(xi), 'H75 L64', held=hlH_(xi)),
                R_(HY, 'CE', f'{ceX:,.2f} · {ceD:.1f} ADR', ceOdds(ceD), ceS, held=ceH, vfg=HOT if ceD <= 0.5 else None, rfg=OK if st and s['ceHT'] is not None else None),
                R_(HY, '1ST', fsX, fsR, fsW, held=fsH),
                R_(HY, 'DXY1', 'S1 BIG ≥ 0.42 → other', '82%', 'vs 53%', held=True, pill=dash if st else None),
                R_(HY, 'DXY2', 'S2 BIG ≥ 0.22 → other', '71%', 'vs 59%', held=True, pill=dash if st and s['now'] >= at(8, 50) else None),
                R_(HY, '08:30', f'→09:00 adds · typ {0.14 * a:.0f}', f"+{s['add'] * a:.0f}" if st else '—', '+' + x2(s['add']) if st else '+0.14×', held=True, vfg=HOT if st and s['add'] >= 0.14 else None)]
        return rows
    in2 = st and s['now'] >= at(8, 50)
    return [H_(HY, '◆ GRIMMJOW', f'{nH} ✓', HY, '#ffffff'),
            R_(HY, 'RANGE', f'{zWd(z)} {eR:.0f} pts', '', '', held=vh(18 + 2 * z), pill3=(agr, agc[0], agc[1])),
            R_(HY, 'H/L', f'after 08:30 · {xn}', hl(xi), '', held=hlH_(xi)),
            R_(HY, 'CE', f'{ceD:.1f} ADR · {ceS}', ceOdds(ceD), '', held=ceH),
            R_(HY, '1ST', fsX, fsR, '', held=fsH),
            R_(HY, 'DXY2' if in2 else 'DXY1', 'BIG → other way', '71%' if in2 else '82%', '', held=True, pill=dash if st else None)]

def clock_card(s):
    y = s['y']; scP = A; rT = s['tH'] - s['tL']; vA = rT / scP
    el = (s['now'] - (T - pd.Timedelta(hours=6))).total_seconds() / 60 + 1; jB = min(45, int(np.ceil(el / 30)) - 1); fB = (el - 30 * jB) / 30
    cka = lambda k: (ck(0, 0, k, jB - 1) if jB > 0 else 0) + (ck(0, 0, k, jB) - (ck(0, 0, k, jB - 1) if jB > 0 else 0)) * fB
    q10, q25, q50, q75, q90 = [cka(k) for k in range(5)]
    stB = 'Above' if vA > q75 else 'Below' if vA < q25 else 'Inside'
    pq = 5 if vA < q10 else 10 + 15 * (vA - q10) / (q25 - q10) if vA <= q25 else 25 + 25 * (vA - q25) / (q50 - q25) if vA <= q50 else 50 + 25 * (vA - q50) / (q75 - q50) if vA <= q75 else 75 + 15 * (vA - q75) / (q90 - q75) if vA <= q90 else 95
    sh = (ckSh(0, jB - 1) if jB > 0 else 0) + (ckSh(0, jB) - (ckSh(0, jB - 1) if jB > 0 else 0)) * fB
    d0 = [ck(0, 0, 2, j) - (ck(0, 0, 2, j - 1) if j else 0) for j in range(46)]; bj = int(np.argmax(d0)); dn = ck(1, 0, 2, bj) - ck(1, 0, 2, bj - 1)
    hh_ = lambda j: f'{(18 * 60 + 30 * (j + 1)) // 60 % 24:02d}:{(30 * (j + 1)) % 60:02d}'
    pill = {'Above': ('▲ ABOVE', '#ffffff', HOT), 'Below': ('▼ BELOW', '#ffffff', COLD), 'Inside': ('● INSIDE', TX, NEU)}[stB]
    nowT = f'{s["now"] + pd.Timedelta(minutes=1):%H:%M}'
    return [H_(GH, f'◆ DESGARRÓN · CLOCK · {nowT} ET', 'NFP DAY', GH, '#ffffff'),
            R_(GH, 'NOW', f'range {rT:.2f} pts', x2(vA), pill=pill),
            R_(GH, 'vs NFP', f'{meter(pq)} ≈P{pq:.0f}', f'typ {x2(q50)}', '', vfg=HOT if stB == 'Above' else COLD if stB == 'Below' else None),
            R_(GH, 'DONE', f'{gauge(sh)} {pc(sh)}', f'→ {rT / sh:.0f}' if sh >= 0.25 else '—', 'pts'),
            R_(GH, 'BUSIEST', f'{hh_(bj - 1)}–{hh_(bj)}', f'+{x2(d0[bj])}', f'norm +{x2(dn)}', vfg=GH)], stB

def render(s, out, title, sub, mobile=False):
    now = s['now']; st = s['st']
    x = bars5(T - pd.Timedelta(hours=6), now)
    n = len(x); fut = 30
    W = 9.0 if mobile else FW_IN
    globals()['FW_IN_SAVE'] = FW_IN
    fig = plt.figure(figsize=(W, 13.2 if not mobile else 15.5), dpi=DPI, facecolor=BG)
    ax = fig.add_axes([0.02, 0.43, 0.92, 0.49]); ax2 = fig.add_axes([0.02, 0.04, 0.92, 0.365])
    lo, hi = x.Low.min(), max(x.High.max(), s['athN']) + (0.45 * A if st else 0)
    pad = (hi - lo)
    ax.set_xlim(-2, n + fut + (95 if not mobile else 30)); ax.set_ylim(lo - pad * (0.75 if not mobile else 0.95), hi + pad * 0.22)
    style(ax, x, f'NQ1! · 5 · CME   Desgarrón   ·   Fri 2 Oct 2026 · NFP · {now + pd.Timedelta(minutes=1):%H:%M} ET', every=2 if not mobile else 3)
    idx = lambda t: int(np.searchsorted(x.index, t))
    xe = n + fut
    # week open
    ax.plot([0, xe], [WO, WO], color=LVL, lw=0.9, ls='--', alpha=0.85); ax.text(n + 1, WO, f' week open {WO:,.2f}', color=LVL, fontsize=7.5, va='bottom')
    # ATH right of price
    ax.plot([0 if not s['athTd'] else idx(s['athT']), xe], [s['athN']] * 2, color=ATHC, lw=1.2)
    athLab = f" ATH {s['athN']:,.2f} · −{s['athN'] - s['cl']:.0f}"
    ax.text(n + 1, s['athN'], athLab, color=ATHC, fontsize=7.5, va='bottom')
    i700 = idx(at(7, 0)); i900 = idx(at(9, 0))
    if now >= at(7, 0):
        brk = st and s['fsd'] != 0
        i0e = idx(s['fsT']) if brk else n
        for yv, lab, va in ((s['p7H'], 'pre-NFP high', 'bottom'), (s['p7L'], 'pre-NFP low', 'top')):
            ax.plot([i700, i0e], [yv, yv], color=DR0, lw=1, ls='--'); ax.text(i700, yv, lab, color=DR0, fontsize=7.5, va=va)
        if brk or now >= at(9, 0):
            for yv, lab, va in ((s['drH'], 'DR high', 'bottom'), (s['drL'], 'DR low', 'top')):
                ax.plot([i700, n], [yv, yv], color=LVL, lw=1.3); ax.text(min(i900, n), yv, lab, color=LVL, fontsize=7.5, va=va)
            ax.plot([i700, n], [(s['drH'] + s['drL']) / 2] * 2, color=LVL, lw=0.9, ls=':', alpha=0.65)
    if st:
        i830, i850 = idx(at(8, 30)), idx(at(8, 50))
        ax.axvspan(i830 - .5, min(i900, n) - .5, color='#f23645', alpha=0.15, lw=0); ax.axvline(i850 - .5, color=LVL, ls=':', lw=0.9, alpha=0.6)
        ax.plot([i830, n], [s['ceV']] * 2, color=ATHC, lw=1.1, ls='--'); ax.text(n + 1, s['ceV'], f" ATH CE {ceOdds(s['ceD'])}", color=ATHC, fontsize=7.5, va='top')
        if s['ceHT'] is not None:
            ih = idx(s['ceHT']); ax.plot(ih, s['ceV'], marker='o', ms=5, mfc='none', mec=ATHC, zorder=6)
        for i0, yv, lab, al, ls in ((i830, s['s1O'], '08:30 open', 1, '-'), (i850, s['s2O'], '08:50 open', 0.8, '--')):
            ax.plot([i0, xe], [yv, yv], color=GH, lw=1.0, ls=ls, alpha=al); ax.text(n + 1, yv, f' {lab} {yv:,.2f}', color=GH, fontsize=7.5, va='top' if lab.startswith('08:50') else 'bottom')
        rel = y_ = s['y'][(s['y'].index >= at(8, 30)) & (s['y'].index < at(9, 0))]
        yF = rel.High.max() + 0.3 * A
        ax.plot([i830, i830], [s['s1O'], yF], color=GH, lw=0.9, ls=':', alpha=0.8, zorder=7)
        ax.text(i830, yF, f"NFP 08:30 · {s['s1O']:,.2f}", color='#ffffff', fontsize=8, ha='center', va='bottom', weight='bold', zorder=8,
                bbox=dict(boxstyle='round,pad=0.25', fc=GH, ec='none'))
        if now >= at(9, 30):
            pcl = float(b[b.tday == T - pd.Timedelta(days=1)].set_index('ts').Close[lambda q_: q_.index <= at(-8, 14)].iloc[-1])
            i930 = idx(at(9, 30)); ax.plot([i930, n], [pcl] * 2, color=LVL, lw=0.9, ls=':', alpha=0.7); ax.plot([i930, n], [(pcl + s['rthO']) / 2] * 2, color=LVL, lw=0.9, ls=':')
            ax.text(n + 1, (pcl + s['rthO']) / 2, ' gap 50%', color=LVL, fontsize=7.5, va='center')
    candles(ax, x)
    # TradingView's order buttons at the top left of the price pane
    bx = ax.get_position()
    for k_, (lab, col) in enumerate((('SELL', '#f23645'), ('BUY', '#2962ff'))):
        fig.add_artist(Rectangle((bx.x0 + 0.004 + k_ * (0.07 if not mobile else 0.13), bx.y1 - 0.045), 0.06 if not mobile else 0.11, 0.035, transform=fig.transFigure, fc=col, ec='none', alpha=0.85, zorder=25))
        fig.text(bx.x0 + 0.034 + k_ * (0.07 if not mobile else 0.13) + (0 if not mobile else 0.025), bx.y1 - 0.0275, lab, color='#ffffff', fontsize=9, weight='bold', ha='center', va='center', zorder=26)
    # cards on the price chart
    if not mobile:
        draw_card(fig, tally_card('Desgarron', 'DESGARRÓN', 'NFP', T, now, wk0, mo0, 'TODAY', True, 'NFP 06 Nov · 35d'), 0.938, 0.915, 'tr')
        draw_card(fig, stage_rows(s), 0.026, 0.437, 'bl')
    else:
        globals()['FW_IN'] = W
        draw_card(fig, stage_rows(s, True), 0.03, 0.437, 'bl', fs=8.0, RH=0.0185)
    # pane: the event clock against NFP days, the normal-day median dashed
    ax2.set_facecolor(BG); ax2.yaxis.tick_right(); ax2.tick_params(axis='y', colors=MU, labelsize=8); ax2.tick_params(axis='x', length=0)
    for s_ in ax2.spines.values(): s_.set_visible(False)
    ax2.grid(color='#1a1f2b', lw=0.6, zorder=0)
    scP = A; xs_ = [6 * j for j in range(47)]
    qq = lambda i, k: [0.0] + [ck(i, 0, k, j) * scP for j in range(46)]
    ax2.fill_between(xs_, qq(0, 0), qq(0, 4), color=GH, alpha=0.10, lw=0); ax2.fill_between(xs_, qq(0, 1), qq(0, 3), color=GH, alpha=0.18, lw=0)
    ax2.plot(xs_, qq(0, 2), color=GH, lw=2); ax2.plot(xs_, qq(1, 2), color=MU, lw=1, ls='--')
    ax2.text(xs_[-1] + 1, ck(0, 0, 2, 45) * scP, f' NFP median {ck(0, 0, 2, 45) * scP:.0f}', color=GH, fontsize=7.5, va='center')
    ax2.text(xs_[-1] + 1, ck(1, 0, 2, 45) * scP, f' Normal {ck(1, 0, 2, 45) * scP:.0f}', color=MU, fontsize=7.5, va='center')
    rngT = (x.High.cummax() - x.Low.cummin()).values
    clk, stB = clock_card(s)
    ax2.plot(range(len(rngT)), rngT, color={'Above': HOT, 'Below': COLD, 'Inside': TX}[stB], lw=2.6, zorder=5)
    ax2.axvline(idx(at(8, 30)), color=GH, ls=':', lw=0.8, alpha=0.4)
    ax2.set_xlim(ax.get_xlim()); ax2.set_ylim(0, ck(0, 0, 4, 45) * scP * 1.75)
    ticks = [i for i, t in enumerate(x.index) if t.minute == 0 and t.hour % (2 if not mobile else 3) == 0]
    ax2.set_xticks(ticks); ax2.set_xticklabels([x.index[i].strftime('%H:%M') for i in ticks], color=MU, fontsize=8)
    ax2.text(0.004, 0.985, 'Desgarrón  ·  event clock + HYDRA findings', transform=ax2.transAxes, color=SUB, fontsize=8.5, va='top', zorder=30)
    pb = ax2.get_position()
    if not mobile:
        draw_card(fig, clk, pb.x1 - 0.002, pb.y1 - 0.03, 'tr')
        draw_card(fig, find_rows(s), pb.x0 + 0.002, pb.y1 - 0.03, 'tl')
    else:
        draw_card(fig, find_rows(s, True), pb.x0 + 0.004, pb.y1 - 0.025, 'tl', fs=8.0, RH=0.0185)
    fig.text(0.02, 0.975, title, color=TX, fontsize=12.5 if not mobile else 11, weight='bold')
    fig.text(0.02, 0.955, sub, color=MU, fontsize=8.5 if not mobile else 7.5)
    plt.savefig(out, dpi=DPI, facecolor=BG); plt.close(fig); globals()['FW_IN'] = 18.0; print(out)

s1 = state(at(7, 3))
z_, *_ = groups(s1)
print('07:04', {k: (round(v, 3) if isinstance(v, float) else v) for k, v in s1.items() if k in ('cl', 'p', 'm', 'd', 's', 'w', 'v', 'athN', 'drH', 'drL')})
render(s1, OUT[0], 'Desgarrón v3 · NFP day 2 Oct 2026, 07:04 ET (your replay): pre-release range live from 07:00, ATH carried right, Grimmjow findings',
       'NQ 1-minute data. The stages card is SETUP + EXPECT before 08:30 (12 rows, clear of the order buttons). The CE forms at 08:30; before that the findings row shows where it would sit now. TradingView rendering will differ.')
s2 = state(at(10, 29))
print('10:30', {k: (round(v, 3) if isinstance(v, float) else v) for k, v in s2.items() if k in ('c59', 'p', 'm', 'd', 's', 'w', 'ceV', 'ceD', 'ceHT', 'fsd', 'fsT', 'add', 'sv1', 'sv2', 'qH', 'qL', 'athN', 'athTd')})
render(s2, OUT[1], 'Desgarrón v3 · NFP day 2 Oct 2026, 10:30 ET: pre-release range broken at 08:30 → 07:00–09:00 dealing range, release window to 09:00, anchored NFP flag, ATH CE (hit)',
       'NQ 1-minute data. DXY cells show — because the DXY futures file ends in Jul 2026; on TradingView TVC:DXY fills them. TradingView rendering will differ.')
render(s2, OUT[2], 'Desgarrón v3 · Mobile · 2 Oct 2026, 10:30 ET', 'Five-row stages card and six-row findings; full wording stays in the tooltips.', mobile=True)
