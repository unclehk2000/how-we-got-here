"""Mocks of Hollow v3 on NQ1! 5-minute, values computed the way the script computes them from NQ 1-minute bars, DXY futures
and the pooled card data in Hollow.pine.
  1) The day after FOMC, Thu 18 Jun 2026 at 10:45 ET: FOMC high / low, gap octants, the stages card LIVE, Shirosaki live.
  2) NFP week, Tue 30 Jun 2026 at 09:05 ET: the NFP week's opening gap, the stages card SETUP / EXPECT, Shirosaki before
     the open.
  3) Mobile, the day after FOMC at 10:45.
  python3 mock_hollow3.py out1 out2 out3"""
import sys, re, numpy as np, pandas as pd
OUT = sys.argv[1:4]
src = open('/home/claude/hm/calgen/mock_cal.py', encoding='utf-8').read().split('# ═══════════ Cero state')[0]
sys.argv = ['x']; exec(src)
PS = open('/home/claude/hol/Hollow.pine', encoding='utf-8').read()
VS = [float(v) for v in re.search(r'var array<float> VS = parseStats\("([^"]+)"\)', PS).group(1).split(',')]
VH = re.search(r'\nVH = "([01]+)"', PS).group(1)
P92 = "!#$%&'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[]^_`abcdefghijklmnopqrstuvwxyz{|}~"
blk = re.search(r'(?m)^CK_NQ\s*=\s*"[^"]*"(?:\n\s+\+\s*"[^"]*")*', PS).group(0); ckS = ''.join(re.findall(r'"([^"]*)"', blk))
CKv = [(P92.index(ckS[2 * i]) * 92 + P92.index(ckS[2 * i + 1]) - 2000) / 1000 for i in range(len(ckS) // 2)]
ck = lambda i, m, k, j: CKv[i * 506 + m * 230 + k * 46 + j]
ckSh = lambda i, j: CKv[i * 506 + 460 + j]
GH, SH, DXC, LVL, OQ = '#26a69a', '#546e7a', '#78909c', '#ffb300', '#26a69a'
vh = lambda i: VH[i] == '1'; hlH = lambda i: vh(i) or vh(i + 1)
pcV = lambda i: '—' if VS[i] < 0 else f'{VS[i]:.0f}'
hl = lambda i: f'H{pcV(i)} L{pcV(i + 1)}'
fl = lambda i: f'FH{pcV(i)} FL{pcV(i + 1)}'
rg = lambda i: f'R{VS[i]:.2f}'
sgP = lambda v: '—' if v is None or not np.isfinite(v) else f'{v:.0f}'
zWd = lambda z: ['DISC', 'MID', 'PREM'][z]
ZBG = [DISC, NEU, PREM]

def state(T, now, F, isF):
    at = lambda h, m_: T + pd.Timedelta(hours=h, minutes=m_)
    g = b[b.tday == T].set_index('ts'); y = g[g.index <= now]; f = F.loc[T]; ctx = CTX.loc[T]; A = float(f.adr)
    cl = float(y.Close.iloc[-1]); tdO = float(y.Open.iloc[0]); tH, tL = y.High.max(), y.Low.min()
    gp_ = b[b.tday == T - pd.Timedelta(days=1)].set_index('ts'); pcl = float(gp_.Close[gp_.index <= at(-8, 14)].iloc[-1])
    st = now >= at(9, 30)
    mon = CTX[(CTX.index.year == T.year) & (CTX.index.month == T.month) & (CTX.index < T)]
    if st:
        c, h, l = float(f.price), y[y.index < at(9, 30)].High.max(), y[y.index < at(9, 30)].Low.min()
    else:
        c, h, l = cl, tH, tL
    mH, mL = max(mon.H.max() if len(mon) else h, h), min(mon.L.min() if len(mon) else l, l)
    s = dict(T=T, now=now, g=g, y=y, A=A, cl=cl, st=st, isF=isF, pcl=pcl, tH=tH, tL=tL, vix=float(f.vix), v=float(f.vixRel),
             p=(c - mL) / (mH - mL), m=(c - ctx.MO) / A, s=(c - tdO) / A, PDH=float(ctx.PDH), PDL=float(ctx.PDL))
    s['d'] = (c - s['PDH']) / A if c > s['PDH'] else (c - s['PDL']) / A if c < s['PDL'] else 0.0
    if st:
        rthO = float(g.loc[at(9, 30), 'Open']); s['rthO'] = rthO; gap = rthO - pcl; s['gap'] = gap / A
        rth = y[y.index >= at(9, 30)]; ce, q4 = pcl + gap / 2, pcl + 0.75 * gap; s['ce'] = ce
        hit = lambda lv, tE: next(iter((rth[rth.index < tE].index[rth[rth.index < tE].Low <= lv] if gap > 0 else rth[rth.index < tE].index[rth[rth.index < tE].High >= lv])), None)
        s['ceT'], s['gfT'], s['qbT'] = hit(ce, at(16, 15)), hit(pcl, at(16, 15)), hit(q4, at(11, 0))
        s['svA'] = (float(g.loc[at(10, 59), 'Close']) if now >= at(11, 0) else cl) - rthO; s['svR'] = cl - rthO
        s['dvA'] = dxm(T, at(9, 30), min(now + pd.Timedelta(minutes=1), at(11, 0))); s['dvR'] = dxm(T, at(9, 30), now + pd.Timedelta(minutes=1))
        s['rQ'] = rth.High.max() - rth.Low.min()
    else:
        s['gap'] = (cl - pcl) / A
    if isF:
        s['fPo'], s['fRg'], s['fA'] = float(f.fPost), float(f.fRng), float(CTX.adr.loc[T - pd.Timedelta(days=1)])
    return s

def groups(s):
    z = zIdx(s['p']); oc = min(8, int(np.floor(s['p'] * 8)) + 1)
    mo = 0 if s['m'] > 1 else 2 if s['m'] < -1 else 1; pg = 0 if s['d'] > 0 else 2 if s['d'] < 0 else 1
    sg = 0 if s['s'] > 0.4 else 2 if s['s'] < -0.4 else 1; gg = 0 if s['gap'] > 0.25 else 2 if s['gap'] < -0.25 else 1
    vg = 0 if s['v'] > 0.1 else 2 if s['v'] < -0.1 else 1
    return z, oc, mo, pg, sg, gg, vg

def gap_status(s):
    isF = s['isF']; dl = s['T'] + pd.Timedelta(hours=11 if isF else 10); now = s['now']
    if not s['st']: return 'from 09:30', 'from 09:30', 'from 09:30', None, None, None
    h = (('hit ' if s['ceT'] < dl else 'late ') + f"{s['ceT']:%H:%M}") if s['ceT'] is not None else 'open' if now < dl else 'missed'
    f_ = f"filled {s['gfT']:%H:%M}" if s['gfT'] is not None else 'open' if now < s['T'] + pd.Timedelta(hours=16, minutes=15) else 'missed'
    q = f"broke {s['qbT']:%H:%M}" if s['qbT'] is not None else 'holding' if now < s['T'] + pd.Timedelta(hours=11) else 'held'
    cH = OK if s['ceT'] is not None and s['ceT'] < dl else WARN if h == 'missed' or h.startswith('late') else None
    cF = OK if s['gfT'] is not None else WARN if f_ == 'missed' else None
    cQ = WARN if s['qbT'] is not None else OK if q == 'held' else None
    return h, f_, q, cH, cF, cQ

def stage_rows(s, mobile=False):
    z, oc, mo, pg, sg, gg, vg = groups(s); a = s['A']; st = s['st']; isF = s['isF']
    o = 58 if isF else 0; eA, eR = VS[o + 2 * z] * a, VS[o + 6 + 2 * z] * a
    zW = ['DISCOUNT', 'MIDDLE', 'PREMIUM'][z]; zfg = TX if z == 1 else '#ffffff'; zbg = ZBG[z]
    lvH, lvL = ('FOMC high', 'FOMC low') if isF else ('PDH', 'PDL')
    pdT = f'above {lvH} {sgs(s["d"] * a)}' if pg == 0 else f'below {lvL} {sgs(s["d"] * a)}' if pg == 2 else ('inside FOMC day' if isF else 'inside prior day')
    gpT = ('' if st else 'now ') + ('gap up ' if s['gap'] >= 0 else 'gap down ') + sgP(abs(s['gap']) * a)
    gpR = f'F{pcV(97 + gg)} ½{pcV(100 + gg)}' if isF else f'½{pcV(48 + gg)} F{pcV(51 + gg)}'
    gpHd = (vh(97 + gg) or vh(100 + gg)) if isF else (vh(48 + gg) or vh(51 + gg))
    vxT = f'VIX {s["vix"]:.1f} · {fds(100 * s["v"], "{:.0f}")}% vs 20d'
    fpI = 124 if s.get('fPo', 0) >= 0 else 126
    hS, fS, qS, cH, cF, cQ = gap_status(s)
    lt = lambda sv, dv: f'{sgs(sv)} · DXY {ar(dv)}{abs(dv):.2f}'
    ttl = 'FULL BRINGER · FOMC +1' if isF else 'HOLLOW · NFP WEEK'
    dayT = 'TODAY' if isF or s['T'].dayofweek < 4 else ''
    if not mobile:
        rows = [H_(GH, f'◆ {ttl} · NQ1! · {dayT}' + (' · 09:29' if st else ''), zW, zfg, zbg)]
        if isF:
            rows += [R_(GH, 'FOMC', f'14:00→16:14 {sgs(s["fPo"] * s["fA"])} · R{s["fRg"]:.1f}', fds(s['fPo']), fl(fpI), held=hlH(fpI), rfg=SUB),
                     R_(GH, 'MONTH', f'{octbar(oc)} O{oc}', pc(s['p']), fl(88 + 2 * z), held=hlH(88 + 2 * z), vfg=None if z == 1 else zbg, rfg=SUB)]
        else:
            rows += [R_(GH, 'MONTH', f'{octbar(oc)} O{oc}', pc(s['p']), hl(36 + 2 * z), held=hlH(36 + 2 * z) or vh(6 + 2 * z), vfg=None if z == 1 else zbg, rfg=SUB),
                     R_(GH, 'MO', f'vs month open {sgs(s["m"] * a)}', fds(s['m']), rg(42 + mo), held=vh(42 + mo), vfg=[HOT, None, COLD][mo], rfg=SUB)]
        rows += [R_(GH, 'PD', pdT, '' if pg == 1 else fds(s['d']), hl((76 if isF else 24) + 2 * pg), held=hlH((76 if isF else 24) + 2 * pg), rfg=SUB),
                 R_(GH, 'O/N', f'since 18:00 {sgs(s["s"] * a)}', fds(s['s']), hl((82 if isF else 30) + 2 * sg), held=hlH((82 if isF else 30) + 2 * sg), vfg=[DISC, None, PREM][sg], rfg=SUB),
                 R_(GH, 'GAP', gpT, fds(s['gap'], '{:.2f}'), gpR, held=gpHd, rfg=SUB),
                 R_(GH, 'VIX', vxT, '', rg((94 if isF else 45) + vg), held=vh((94 if isF else 45) + vg), rfg=SUB)]
        if st:
            rA = abs(s['svA']) / eA; rR = s['rQ'] / eR
            rows += [S_(DXC, 'LIVE · vs DXY', '×typ', 'DXY'),
                     R_(GH, 'NY AM', lt(s['svA'], s['dvA']), x2(rA), vfg=HOT if rA >= 1 else None, pill=dx_pill(s['dvA'], s['svA'], 99 if isF else 0.19)),
                     R_(GH, 'RTH', lt(s['svR'], s['dvR']), '', pill=dx_pill(s['dvR'], s['svR'], 0.52 if isF else 0.26)),
                     R_(GH, 'RANGE', f'since 09:30 {s["rQ"]:.0f} pts', x2(rR), f'med {eR:.0f}', vfg=HOT if rR >= 1 else None),
                     R_(GH, 'GAP', f'½ {hS} · F {fS}', f'{pcV((100 if isF else 48) + gg)}%', f'F{pcV((97 if isF else 51) + gg)}', held=gpHd)]
        else:
            rows += [S_(GH, f'EXPECT · {zWd(z)} · ADR {a:.0f}', 'med', '80%'),
                     R_(GH, 'NY AM', '09:30–11:00', f'±{eA:.0f}', f'±{VS[o + 1 + 2 * z] * a:.0f}', held=vh(o + 2 * z)),
                     R_(GH, 'RTH', 'RTH range', f'{eR:.0f}', f'{VS[o + 7 + 2 * z] * a:.0f}', held=vh(o + 6 + 2 * z))]
            if isF:
                rows += [R_(GH, 'NEXT', "next day's range", f'{VS[70 + 2 * z] * a:.0f}', f'{VS[71 + 2 * z] * a:.0f}', held=vh(70 + 2 * z)),
                         R_(GH, '¼', 'open-side ¼ held NY AM', f'{pcV(152 + gg)}%', f'all {pcV(168)}%', held=vh(152 + gg))]
            else:
                rows += [R_(GH, 'SETTLE', '16:15–17:00 range', f'{VS[12 + 2 * z] * a:.0f}', f'{VS[13 + 2 * z] * a:.0f}', held=vh(12 + 2 * z)),
                         R_(GH, 'NEXT', "next day's range", f'{VS[18 + 2 * z] * a:.0f}', f'{VS[19 + 2 * z] * a:.0f}', held=vh(18 + 2 * z))]
        return rows
    rows = [H_(GH, f'◆ {"FOMC +1" if isF else "NFP WEEK"} · NQ1!', zWd(z), zfg, zbg),
            R_(GH, 'MONTH', octbar(oc), pc(s['p']), fl(88 + 2 * z) if isF else hl(36 + 2 * z), held=hlH((88 if isF else 36) + 2 * z), vfg=None if z == 1 else zbg)]
    if st:
        rows += [R_(GH, 'RTH', lt(s['svR'], s['dvR']), '', pill=dx_pill(s['dvR'], s['svR'], 0.52 if isF else 0.26)),
                 R_(GH, 'GAP', f'½ {hS} · F {fS}', '', '', held=gpHd)]
    else:
        rows += [R_(GH, 'EXP', f'RTH {eR:.0f} · AM ±{eA:.0f}', f'{VS[o + 7 + 2 * z] * a:.0f}', '80%', held=vh(o + 6 + 2 * z)),
                 R_(GH, 'GAP', f'gap {fds(s["gap"], "{:.2f}")} {gpR}', '', '', held=gpHd)]
    rows.append(R_(GH, 'PD', ('> ' if pg == 0 else '< ' if pg == 2 else 'in ') + ('FOMC ' if isF else 'PD ') + hl((76 if isF else 24) + 2 * pg), '' if pg == 1 else fds(s['d']), '', held=hlH((76 if isF else 24) + 2 * pg)))
    return rows

def szT(i, lab, base):
    if not vh(i): return '', 0, 0
    return lab + ('↑ ' if VS[i] > base else '↓ '), int(VS[i] > base), int(VS[i] < base)

def sh_rows(s, mobile=False):
    z, oc, mo, pg, sg, gg, vg = groups(s); a = s['A']; st = s['st']; isF = s['isF']
    base = VS[165 if isF else 155]; zi = (64 if isF else 6) + 2 * z
    tg, bg_, sm_ = '', int(vh(zi) and VS[zi] > base), int(vh(zi) and VS[zi] < base)
    cand = [((94 if isF else 45) + vg, 'VIX', vg != 1)]
    if not isF: cand += [(42 + mo, 'MO', mo != 1), (115 + pg, 'PD', pg != 1), (118 + sg, 'O/N', sg != 1), (121 + gg, 'GAP', gg != 1)]
    for i, lab, on in cand:
        if on:
            t_, b1, s1 = szT(i, lab, base); tg += t_; bg_ += b1; sm_ += s1
    agr = 'BIGGER' if bg_ > 0 and sm_ == 0 else 'SMALLER' if sm_ > 0 and bg_ == 0 else 'MIXED' if bg_ > 0 else 'TYPICAL'
    agc = ('#ffffff', HOT) if agr == 'BIGGER' else ('#ffffff', COLD) if agr == 'SMALLER' else (TX, NEU)
    if isF: xi = 82 + 2 * sg if sg != 1 else 76 + 2 * pg if pg != 1 else 140 + 2 * gg if gg != 1 else 146 + 2 * z
    else: xi = 30 + 2 * sg if sg != 1 else 24 + 2 * pg if pg != 1 else 109 + 2 * gg if gg != 1 else 36 + 2 * z
    gLab = 'gap up' if gg == 0 else 'gap down' if gg == 2 else 'small gap'
    xn = 'O/N↑' if sg == 0 else 'O/N↓' if sg == 2 else ('>FOMC H' if isF else '>PDH') if pg == 0 else ('<FOMC L' if isF else '<PDL') if pg == 2 else gLab if gg != 1 else zWd(z)
    xB = f'H{pcV(163 if isF else 156)} L{pcV(164 if isF else 157)}'
    hS, fS, qS, cH, cF, cQ = gap_status(s)
    gB = lambda i, t: t if st else f'all {pcV(i)}%'
    dxR = dx_pill(s['dvR'], s['svR'], 0.52 if isF else 0.26) if st else None
    dxA = dx_pill(s['dvA'], s['svA'], 0.19) if st else None
    sub = S_(SH, f'NQ+ES+RTY · ADR {a:.0f}', 'today', 'base · live' if st else 'base')
    if not isF:
        nH = int(vh(zi)) + int(tg != '') + int(hlH(xi)) + int(vh(48 + gg)) + int(vh(51 + gg)) + int(vh(103 + gg)) + 2 + int(sg == 0)
        if not mobile:
            return [H_(SH, '◆ SHIROSAKI · NFP WEEK', f'{nH} ✓', SH, '#ffffff'), sub,
                    W_(SH, 'SIDE', 'O/N up: RTH up 69% vs 54% ✓' if sg == 0 else 'none held: size the day', OK if sg == 0 else SUB),
                    R_(SH, 'RANGE', f'RTH range · {zWd(z)}', f'{VS[zi] * a:.0f}', f'all {base * a:.0f}', held=vh(zi)),
                    R_(SH, 'SIZE+', tg if tg else 'none active', '', '', held=tg != '', pill3=(agr, agc[0], agc[1])),
                    R_(SH, 'H/L', f'after 09:30 · {xn}', hl(xi), xB, held=hlH(xi)),
                    R_(SH, '½ 10:00', f'{gLab} · 50% by 10:00', f'{pcV(48 + gg)}%', gB(158, hS), held=vh(48 + gg), rfg=cH),
                    R_(SH, 'FILL', f'{gLab} · filled by 16:14', f'{pcV(51 + gg)}%', gB(159, fS), held=vh(51 + gg), rfg=cF),
                    R_(SH, '¼ OPEN', f'{gLab} · held NY AM', f'{pcV(103 + gg)}%', gB(160, qS), held=vh(103 + gg), rfg=cQ),
                    R_(SH, 'DXY RTH', 'BIG ≥ 0.26 → other way', '70%', 'vs 42%', held=True, pill=dxR),
                    R_(SH, 'DXY AM', 'BIG ≥ 0.19 → other way', '60%', 'vs 54%', held=True, pill=dxA)]
        return [H_(SH, '◆ SHIROSAKI', f'{nH} ✓', SH, '#ffffff'),
                R_(SH, 'RANGE', f'{zWd(z)} {VS[zi] * a:.0f} pts', '', '', held=vh(zi), pill3=(agr, agc[0], agc[1])),
                R_(SH, 'H/L', f'after 09:30 · {xn}', hl(xi), '', held=hlH(xi)),
                R_(SH, '½', f'{gLab} · by 10:00', f'{pcV(48 + gg)}%', hS if st else '', held=vh(48 + gg), rfg=cH),
                R_(SH, 'FILL', f'{gLab} · by 16:14', f'{pcV(51 + gg)}%', fS if st else '', held=vh(51 + gg), rfg=cF),
                R_(SH, 'DXY', 'RTH BIG → other', '70%', '', held=True, pill=dxR)]
    fpI = 124 if s['fPo'] >= 0 else 126
    gi = 128 + 2 * gg if gg != 1 else fpI
    gn = 'gap up' if gg == 0 else 'gap down' if gg == 2 else '14:00→16:14 ' + ('▲' if s['fPo'] >= 0 else '▼')
    ri = 94 + vg if vg != 1 else zi
    nH = int(hlH(88 + 2 * z)) + int(hlH(gi)) + int(vh(ri)) + int(hlH(xi)) + int(vh(97 + gg)) + int(vh(100 + gg)) + int(vh(152 + gg)) + 1 + int(vg == 1)
    if not mobile:
        return [H_(SH, '◆ SHIROSAKI · FOMC +1', f'{nH} ✓', SH, '#ffffff'), sub,
                W_(SH, 'SIDE', 'VIX near avg: NY AM down 64% vs 42% ✓' if vg == 1 else 'none held: size the day', OK if vg == 1 else SUB),
                R_(SH, 'FH/FL', f'RTH takes · {zWd(z)}', fl(88 + 2 * z), f'FH{pcV(161)} FL{pcV(162)}', held=hlH(88 + 2 * z)),
                R_(SH, 'FH/FL', f'RTH takes · {gn}', fl(gi), '', held=hlH(gi)),
                R_(SH, 'RANGE', 'RTH range · ' + ('VIX high' if vg == 0 else 'VIX low' if vg == 2 else zWd(z)), f'{VS[ri] * a:.0f}', f'all {base * a:.0f}', held=vh(ri)),
                R_(SH, 'H/L', f'after 09:30 · {xn}', hl(xi), xB, held=hlH(xi)),
                R_(SH, 'FILL', f'{gLab} · filled by 16:14', f'{pcV(97 + gg)}%', gB(166, fS), held=vh(97 + gg), rfg=cF),
                R_(SH, '½ NY AM', f'{gLab} · 50% by 11:00', f'{pcV(100 + gg)}%', gB(167, hS), held=vh(100 + gg), rfg=cH),
                R_(SH, '¼ OPEN', f'{gLab} · held NY AM', f'{pcV(152 + gg)}%', gB(168, qS), held=vh(152 + gg), rfg=cQ),
                R_(SH, 'DXY RTH', 'BIG ≥ 0.52 → other way', '81%', 'vs 41%', held=True, pill=dxR)]
    return [H_(SH, '◆ SHIROSAKI', f'{nH} ✓', SH, '#ffffff'),
            R_(SH, 'FH/FL', gn, fl(gi), '', held=hlH(gi) or hlH(88 + 2 * z)),
            R_(SH, 'H/L', f'after 09:30 · {xn}', hl(xi), '', held=hlH(xi)),
            R_(SH, 'FILL', f'{gLab} · by 16:14', f'{pcV(97 + gg)}%', fS if st else '', held=vh(97 + gg), rfg=cF),
            R_(SH, '½', f'{gLab} · by 11:00', f'{pcV(100 + gg)}%', hS if st else '', held=vh(100 + gg), rfg=cH),
            R_(SH, 'DXY', 'RTH BIG → other', '81%', '', held=True, pill=dxR)]

def clock_card(s, pi, bN):
    y = s['y']; A = s['A']; rT = s['tH'] - s['tL']; vA = rT / A
    el = (s['now'] - (s['T'] - pd.Timedelta(hours=6))).total_seconds() / 60 + 1; jB = min(45, int(np.ceil(el / 30)) - 1); fB = (el - 30 * jB) / 30
    cka = lambda k: (ck(pi, 0, k, jB - 1) if jB > 0 else 0) + (ck(pi, 0, k, jB) - (ck(pi, 0, k, jB - 1) if jB > 0 else 0)) * fB
    q10, q25, q50, q75, q90 = [cka(k) for k in range(5)]
    stB = 'Above' if vA > q75 else 'Below' if vA < q25 else 'Inside'
    pq = 5 if vA < q10 else 10 + 15 * (vA - q10) / (q25 - q10) if vA <= q25 else 25 + 25 * (vA - q25) / (q50 - q25) if vA <= q50 else 50 + 25 * (vA - q50) / (q75 - q50) if vA <= q75 else 75 + 15 * (vA - q75) / (q90 - q75) if vA <= q90 else 95
    sh = (ckSh(pi, jB - 1) if jB > 0 else 0) + (ckSh(pi, jB) - (ckSh(pi, jB - 1) if jB > 0 else 0)) * fB
    d0 = [ck(pi, 0, 2, j) - (ck(pi, 0, 2, j - 1) if j else 0) for j in range(46)]; bj = 1 + int(np.argmax(d0[1:])); dn = ck(2, 0, 2, bj) - ck(2, 0, 2, bj - 1)
    hh_ = lambda j: f'{(18 * 60 + 30 * (j + 1)) // 60 % 24:02d}:{(30 * (j + 1)) % 60:02d}'
    pill = {'Above': ('▲ ABOVE', '#ffffff', HOT), 'Below': ('▼ BELOW', '#ffffff', COLD), 'Inside': ('● INSIDE', TX, NEU)}[stB]
    nowT = f'{s["now"] + pd.Timedelta(minutes=1):%H:%M}'
    return [H_(GH, f'◆ HOLLOW · CLOCK · {nowT} ET', bN.upper(), GH, '#ffffff'),
            R_(GH, 'NOW', f'range {rT:.2f} pts', x2(vA), pill=pill),
            R_(GH, 'vs ' + bN, f'{meter(pq)} ≈P{pq:.0f}', f'typ {x2(q50)}', '', vfg=HOT if stB == 'Above' else COLD if stB == 'Below' else None),
            R_(GH, 'DONE', f'{gauge(sh)} {pc(sh)}', f'→ {rT / sh:.0f}' if sh >= 0.25 else '—', 'pts'),
            R_(GH, 'BUSIEST', f'{hh_(bj - 1)}–{hh_(bj)}', f'+{x2(d0[bj])}', f'norm +{x2(dn)}', vfg=GH)], stB

def render(s, out, title, sub, t0, chartT, nxt, pi, bN, wk0, mobile=False):
    T, now, st, isF, A = s['T'], s['now'], s['st'], s['isF'], s['A']; at = lambda h, m_: T + pd.Timedelta(hours=h, minutes=m_)
    x = bars5(t0, now); n = len(x); fut = 30; W = 9.0 if mobile else FW_IN
    fig = plt.figure(figsize=(W, 13.2 if not mobile else 15.5), dpi=DPI, facecolor=BG)
    ax = fig.add_axes([0.02, 0.43, 0.92, 0.49]); ax2 = fig.add_axes([0.02, 0.04, 0.92, 0.365])
    lo, hi = x.Low.min(), x.High.max()
    if not isF:
        fri_ = m1[(m1.index < wk0)].Close.iloc[-1]; wo_ = float(m1.Open[m1.index >= wk0].iloc[0]); lo, hi = min(lo, fri_, wo_), max(hi, fri_, wo_)
    pad = hi - lo
    ax.set_xlim(-2, n + fut + (95 if not mobile else 30)); ax.set_ylim(lo - pad * (0.8 if not mobile else 1.0), hi + pad * 0.22)
    style(ax, x, chartT, every=2 if not mobile else 4)
    idx = lambda t: int(np.searchsorted(x.index, t)); xe = n + fut
    WO = float(m1.Open[m1.index >= wk0].iloc[0])
    ax.plot([0, xe], [WO, WO], color=LVL, lw=0.9, ls='--', alpha=0.85); ax.text(n + 1, WO, f' week open {WO:,.2f}', color=LVL, fontsize=7.5, va='bottom')
    if isF:
        F0 = T - pd.Timedelta(days=1); fp = b[b.tday == F0].set_index('ts'); rr = fp
        i18 = idx(T - pd.Timedelta(hours=6)); i1614 = idx(at(16, 14))
        for yv, lab in ((rr.High.max(), 'FOMC high'), (rr.Low.min(), 'FOMC low')):
            ax.plot([i18, n], [yv, yv], color=LVL, lw=1.1, ls='--'); ax.text(n + 1, yv, ' ' + lab, color=LVL, fontsize=7.5, va='center')
        i14 = idx(F0 + pd.Timedelta(hours=14))
        if 0 < i14 < n:
            o14 = float(x.Open.iloc[i14]); yF = x.High.iloc[i14:i14 + 6].max() + 0.3 * A
            ax.plot([i14, i14], [o14, yF], color=GH, lw=0.9, ls=':', alpha=0.8, zorder=7)
            ax.text(i14, yF, f'FOMC 14:00 · {o14:,.2f}', color='#ffffff', fontsize=8, ha='center', va='bottom', weight='bold', zorder=8, bbox=dict(boxstyle='round,pad=0.25', fc=GH, ec='none'))
        if st:
            i930, i1100 = idx(at(9, 30)), idx(at(11, 0)); gp = s['rthO'] - s['pcl']
            for k in range(9):
                yy = s['pcl'] + gp * k / 8
                ax.plot([i930, max(n, i930 + 1)], [yy, yy], color=LVL if k <= 5 else OQ, lw=2 if k == 4 else 0.8, ls='--' if k == 4 else ':', alpha=1 if k in (4, 6, 8) else 0.45, zorder=2)
            ax.fill_between([i930, n], s['pcl'] + gp * 0.75, s['rthO'], color=OQ, alpha=0.22, lw=0, zorder=1)
            ax.text(n + 1, s['pcl'] + gp * 0.875, ' open-side ¼', color=OQ, fontsize=7.5, va='center')
            ax.axvspan(i930 - .5, n - .5, color=OQ, alpha=0.05, lw=0)
            ax.text(n + 1, s['ce'], ' gap 50%', color=LVL, fontsize=7.5, va='center')
    else:
        # the NFP week's opening gap: Friday's last close and Sunday's open, midpoint, drawn to the release
        fri = m1[(m1.index < wk0)].Close.iloc[-1]; ce = (fri + WO) / 2
        for yv, ls, al in ((fri, ':', 0.6), (WO, ':', 0.6), (ce, '--', 1)):
            ax.plot([0, xe + 40], [yv, yv], color=LVL, lw=1.0, ls=ls, alpha=al)
        ax.text(xe + 1, ce, ' NWOG 50% → NFP Thu 08:30', color=LVL, fontsize=7.5, va='bottom')
        if st:
            i930 = idx(at(9, 30)); ax.plot([i930, n], [s['pcl']] * 2, color=LVL, lw=0.9, ls=':', alpha=0.7); ax.plot([i930, n], [s['ce']] * 2, color=LVL, lw=0.9, ls=':')
    candles(ax, x)
    bx = ax.get_position()
    for k_, (lab, col) in enumerate((('SELL', '#f23645'), ('BUY', '#2962ff'))):
        fig.add_artist(Rectangle((bx.x0 + 0.004 + k_ * (0.07 if not mobile else 0.13), bx.y1 - 0.045), 0.06 if not mobile else 0.11, 0.035, transform=fig.transFigure, fc=col, ec='none', alpha=0.85, zorder=25))
        fig.text(bx.x0 + 0.034 + k_ * (0.07 if not mobile else 0.13) + (0 if not mobile else 0.025), bx.y1 - 0.0275, lab, color='#ffffff', fontsize=9, weight='bold', ha='center', va='center', zorder=26)
    if not mobile:
        draw_card(fig, tally_card('Hollow', 'HOLLOW', 'FOMC +1', T, now, wk0, pd.Timestamp(f'{T.year}-{T.month:02d}-01') - pd.Timedelta(hours=6), 'TODAY' if isF else 'IN 51D', isF, nxt), 0.938, 0.915, 'tr')
        draw_card(fig, stage_rows(s), 0.026, 0.437, 'bl')
    else:
        globals()['FW_IN'] = W
        draw_card(fig, stage_rows(s, True), 0.03, 0.437, 'bl', fs=8.0, RH=0.0185)
    ax2.set_facecolor(BG); ax2.yaxis.tick_right(); ax2.tick_params(axis='y', colors=MU, labelsize=8); ax2.tick_params(axis='x', length=0)
    for s_ in ax2.spines.values(): s_.set_visible(False)
    ax2.grid(color='#1a1f2b', lw=0.6, zorder=0)
    i18 = idx(T - pd.Timedelta(hours=6)); xs_ = [i18 + 6 * j for j in range(47)]
    qq = lambda i, k: [0.0] + [ck(i, 0, k, j) * A for j in range(46)]
    ax2.fill_between(xs_, qq(pi, 0), qq(pi, 4), color=GH, alpha=0.10, lw=0); ax2.fill_between(xs_, qq(pi, 1), qq(pi, 3), color=GH, alpha=0.18, lw=0)
    ax2.plot(xs_, qq(pi, 2), color=GH, lw=2); ax2.plot(xs_, qq(2, 2), color=MU, lw=1, ls='--')
    ax2.text(xs_[-1] + 1, ck(pi, 0, 2, 45) * A, f' {bN} median {ck(pi, 0, 2, 45) * A:.0f}', color=GH, fontsize=7.5, va='center')
    ax2.text(xs_[-1] + 1, ck(2, 0, 2, 45) * A, f' Normal {ck(2, 0, 2, 45) * A:.0f}', color=MU, fontsize=7.5, va='center')
    xt = x[x.index >= T - pd.Timedelta(hours=6)]; rngT = (xt.High.cummax() - xt.Low.cummin()).values
    clk, stB = clock_card(s, pi, bN)
    ax2.plot(range(i18, i18 + len(rngT)), rngT, color={'Above': HOT, 'Below': COLD, 'Inside': TX}[stB], lw=2.6, zorder=5)
    ax2.set_xlim(ax.get_xlim()); ax2.set_ylim(0, ck(pi, 0, 4, 45) * A * 1.9)
    ticks = [i for i, t in enumerate(x.index) if t.minute == 0 and t.hour % (2 if not mobile else 4) == 0]
    ax2.set_xticks(ticks); ax2.set_xticklabels([x.index[i].strftime('%H:%M') for i in ticks], color=MU, fontsize=8)
    ax2.text(0.004, 0.985, 'Hollow  ·  event clock + Shirosaki', transform=ax2.transAxes, color=SUB, fontsize=8.5, va='top', zorder=30)
    pb = ax2.get_position()
    if not mobile:
        draw_card(fig, clk, pb.x1 - 0.002, pb.y1 - 0.03, 'tr')
        draw_card(fig, sh_rows(s), pb.x0 + 0.002, pb.y1 - 0.03, 'tl')
    else:
        draw_card(fig, sh_rows(s, True), pb.x0 + 0.004, pb.y1 - 0.025, 'tl', fs=8.0, RH=0.0185)
    fig.text(0.02, 0.975, title, color=TX, fontsize=12.5 if not mobile else 11, weight='bold')
    fig.text(0.02, 0.955, sub, color=MU, fontsize=8.5 if not mobile else 7.5)
    plt.savefig(out, dpi=DPI, facecolor=BG); plt.close(fig); globals()['FW_IN'] = 18.0; print(out)

TF = pd.Timestamp('2026-06-18'); sF = state(TF, TF + pd.Timedelta(hours=10, minutes=44), FA, True)
print('FOMC+1', {k: (round(v, 3) if isinstance(v, float) else v) for k, v in sF.items() if k not in ('g', 'y')}, groups(sF))
render(sF, OUT[0], 'Hollow v3 · the day after FOMC, Thu 18 Jun 2026, 10:45 ET: FOMC high / low carried, gap octants, stages card LIVE, Shirosaki',
       'NQ 1-minute data and DXY futures. The FOMC flag is tied to the 14:00 open. Stages card and Shirosaki pooled from NQ + ES + RTY. TradingView rendering will differ.',
       TF - pd.Timedelta(hours=19), 'NQ1! · 5 · CME   Hollow   ·   Thu 18 Jun 2026 · FOMC +1 · 10:45 ET', 'NFP week 29 Jun · 11d', 1, 'FOMC +1', TF - pd.Timedelta(days=4, hours=6))
TW = pd.Timestamp('2026-06-30'); sW = state(TW, TW + pd.Timedelta(hours=9, minutes=4), WK, False)
print('NFP wk', {k: (round(v, 3) if isinstance(v, float) else v) for k, v in sW.items() if k not in ('g', 'y')}, groups(sW))
render(sW, OUT[1], 'Hollow v3 · NFP week, Tue 30 Jun 2026, 09:05 ET: the week\'s opening gap drawn to the release, stages card SETUP / EXPECT, Shirosaki before the open',
       'NQ 1-minute data. Before 09:30 the GAP rows read the gap as if RTH opened now; the setup fixes at 09:29. TradingView rendering will differ.',
       TW - pd.Timedelta(hours=6), 'NQ1! · 5 · CME   Hollow   ·   Tue 30 Jun 2026 · NFP week (NFP Thu 2 Jul) · 09:05 ET', 'FOMC +1 30 Jul · 30d', 0, 'NFP week', TW - pd.Timedelta(days=2, hours=6))
render(sF, OUT[2], 'Hollow v3 · Mobile · 18 Jun 2026, 10:45 ET', 'Five-row stages card and six-row Shirosaki; the full wording stays in the tooltips.',
       TF - pd.Timedelta(hours=6), 'NQ1! · 5 · Hollow · FOMC +1 · 10:45', 'NFP week 29 Jun · 11d', 1, 'FOMC +1', TF - pd.Timedelta(days=4, hours=6), mobile=True)
