"""Mocks of the rebuilt Cero and Hollow (NQ1! 5-minute), card values computed the way the scripts compute them, from NQ
1-minute bars, the HYDRA calendar tables and DXY futures (5-minute).
  1) Cero, NFP day Fri 5 Jun 2026 at 10:30 ET: tally (top right), NFP stages card (bottom left).
  2) Hollow, the day after FOMC, Thu 18 Jun 2026 at 10:45 ET: the gap octants, FOMC high / low, tally and stages card.
  3) Hollow, NFP week, Tue 30 Jun 2026 at 11:30 ET.
  4) Mobile: Cero on 5 Jun and Hollow on 18 Jun.
  python3 mock_cal.py out1 out2 out3 out4"""
import sys, re, json, datetime as dt, numpy as np, pandas as pd
OUTS = sys.argv[1:5]
src = open('/home/claude/hm/vizard2/mock_v2.py', encoding='utf-8').read().split('# ════════════════════════════════════════════════ state on an FOMC day')[0]
sys.argv = ['x']
exec(src)
D = json.load(open('/home/claude/hm/calgen/data.json'))
VSC = [float(v) for v in D['cero']['NQ'][0].split(',')]; VHC = D['cero']['NQ'][1]
VSH = [float(v) for v in D['hollow']['NQ'][0].split(',')]; VHH = D['hollow']['NQ'][1]
NFP = pd.read_pickle('/home/claude/hm/hydra_cal/nfp_NQ.pkl'); FA = pd.read_pickle('/home/claude/hm/hydra_cal/fa_NQ.pkl'); WK = pd.read_pickle('/home/claude/hm/hydra_cal/wk_NQ.pkl')
def tal(mod):
    s = open(f'/home/claude/hm/calgen/{mod}.pine', encoding='utf-8').read()
    body = re.search(r'TAL_NQ = "(.*?)"\nTAL_END', s, re.S).group(1).replace('"\n     + "', '')
    return [(int(r[0]), int(r[1]), int(r[2]), float(r[3]) if len(r) > 3 and r[3] else np.nan) for r in (x.split(',') for x in body.split(';')) if len(r) >= 3]
ZW = ['DISC', 'MID', 'PREM']
def zIdx(p): return 1 if p is None or not np.isfinite(p) else 2 if p >= 0.75 else 0 if p <= 0.25 else 1
def dx_pill(dv, sv, thr):
    if not (np.isfinite(dv) and np.isfinite(sv)) or dv == 0 or sv == 0: return ('—', TX, BODY)
    big, oth = abs(dv) >= thr, np.sign(dv) != np.sign(sv)
    return (('⇄' if oth else '⇉') + (' BIG' if big else ''), '#ffffff' if big else TX, (OK if oth else WARN) if big else NEU)
pcv = lambda VS, i: '—' if VS[i] < 0 else f'{VS[i]:.0f}'
hlx = lambda VS, i: f'H{pcv(VS, i)} L{pcv(VS, i + 1)}'
hv = lambda VH, i: VH[i] == '1'
hlh = lambda VH, i: hv(VH, i) or hv(VH, i + 1)
rgx = lambda VS, i: f'R{VS[i]:.2f}'
sgs = lambda v: '—' if v is None or not np.isfinite(v) else ('+' if v >= 0 else '−') + f'{abs(v):.0f}'
fds = lambda v, f='{:.1f}': '—' if v is None or not np.isfinite(v) else ('+' if v >= 0 else '−') + f.format(abs(v))
def tally_card(mod, name, label, T, now, wk0, mo0, pill, pNow, nxt, mobile=False, clock=None):
    rec = [r for r in tal(mod) if r[0] < int(T.strftime('%Y%m%d'))][-12:]
    up, dn = sum(r[1] > 0 for r in rec), sum(r[1] < 0 for r in rec); ru, rd = sum(r[2] > 0 for r in rec), sum(r[2] < 0 for r in rec)
    gaps = [r[3] for r in rec if np.isfinite(r[3])]; gu = sum(g_ > 0 for g_ in gaps); gav, gab = np.mean(gaps), np.mean(np.abs(gaps))
    cl = float(m1.Close[m1.index <= now].iloc[-1])
    def zone(key, t0):
        y = m1[(m1.index >= t0) & (m1.index <= now)]; h, l = y.High.max(), y.Low.min(); o = octof(cl, h, l)
        z = 'PREM' if o >= 7 else 'DISC' if o <= 2 else 'EQ'
        return R_(GH, key, f'{octbar(o)} O{o}', '', f'−{h - cl:.0f}', pill3=(z, TX if z == 'EQ' else '#ffffff', PREM if z == 'PREM' else DISC if z == 'DISC' else NEU))
    head = H_(GH, f'◆ {name} · {label} · NQ1!', pill, GH if pNow else '#ffffff', '#ffffff' if pNow else '#2b2f39')
    if not mobile:
        return [head, S_(GH, f'last 12 {mod_tal[mod]} days', '▲', '▼'),
                R_(GH, 'DAY', f'{gauge(up / (up + dn))} {pc(up / (up + dn))}', str(up), str(dn), vfg=DISC, rfg=PREM),
                R_(GH, 'RTH', f'{gauge(ru / (ru + rd))} {pc(ru / (ru + rd))}', str(ru), str(rd), vfg=DISC, rfg=PREM),
                R_(GH, 'GAP', f'avg gap · ▲{gu}/{len(gaps)}', fds(gav), f'±{gab:.1f}'), zone('WEEK', wk0), zone('MONTH', mo0), W_(GH, 'NEXT', nxt)]
    return [head, clock, R_(GH, 'DAY', f'last 12 {gauge(up / (up + dn), 5)}', f'▲{up}', f'▼{dn}', vfg=DISC, rfg=PREM),
            R_(GH, 'GAP', f'avg · ▲{gu}/{len(gaps)}', fds(gav), f'±{gab:.1f}'), zone('WK', wk0), zone('MO', mo0)]
mod_tal = {'Cero': 'NFP', 'Hollow': 'day-after-FOMC'}
def dxm(T, a, b):
    """DXY move from the open of the bar at a to the close of the last bar finished by b, in DXY ADR20"""
    x = DXD[T]; a20 = float(dxday.a20.loc[T])
    o = float(x.Open[x.index >= a].iloc[0]); c = float(x.Close[x.index + pd.Timedelta(minutes=5) <= b].iloc[-1])
    return (c - o) / a20
def clock_row(T, now, kind):
    g = b[b.tday == T].set_index('ts'); g = g[g.index <= now]; A = None
    R = np.array(CK[kind]['R']); jn = (now - (T - pd.Timedelta(hours=6))).total_seconds() / 1800
    return g, R, jn

# ═══════════ Cero state, NFP Fri 5 Jun 2026 at 10:29 (bar closed)
GH = '#ff7043'
T = pd.Timestamp('2026-06-05'); at = lambda h, m: T + pd.Timedelta(hours=h, minutes=m); now = at(10, 29)
g = b[b.tday == T].set_index('ts'); f = NFP.loc[T]; A = float(f.adr)
px = lambda t, c='Close': float(g.loc[t, c])
s1O, s1C, s2O, s2C, rthO, cl = px(at(8, 30), 'Open'), px(at(8, 49)), px(at(8, 50), 'Open'), px(at(9, 29)), px(at(9, 30), 'Open'), px(now)
sv1, sv2, svA = s1C - s1O, s2C - s2O, cl - rthO
dv1, dv2 = dxm(T, at(8, 30), at(8, 50)), dxm(T, at(8, 50), at(9, 30))
pre = g[g.index < at(8, 30)]; to9 = g[g.index < at(9, 0)]
add = ((to9.High.max() - to9.Low.min()) - (pre.High.max() - pre.Low.min())) / A
c59 = float(f.price); ctx = CTX.loc[T]
p, m, s, w, v = float(f.moPos), float(f.dMO), float(f.preMove), float(f.wkMove), float(f.vixRel)
d = (c59 - ctx.PDH) / A if c59 > ctx.PDH else (c59 - ctx.PDL) / A if c59 < ctx.PDL else 0.0
z = zIdx(p); oc = min(8, int(np.floor(p * 8)) + 1); mo3 = 0 if m > 1 else 2 if m < -1 else 1; pg = 0 if d > 0 else 2 if d < 0 else 1
sg = 0 if s > 0.4 else 2 if s < -0.4 else 1; wg = 0 if w > 0.5 else 2 if w < -0.5 else 1; vg = 0 if v > 0.1 else 2 if v < -0.1 else 1
VS, VH = VSC, VHC
e1, e2, eA = VS[2 * z] * A, VS[6 + 2 * z] * A, VS[12 + 2 * z] * A
pdT = f'above PDH {sgs(d * A)}' if pg == 0 else f'below PDL {sgs(d * A)}' if pg == 2 else 'inside prior day'
lt = lambda sv, dv: f'{sgs(sv)} · DXY {ar(dv)}{abs(dv):.2f}'
zc = [DISC, NEU, PREM][z]
CERO = [H_(GH, '◆ NFP STAGES · NQ1!', 'TODAY', GH, '#ffffff'), S_(GH, 'SETUP AT 08:29', 'ADR', 'after'),
        R_(GH, 'MONTH', f'{octbar(oc)} {pc(p)}', '', hlx(VS, 42 + 2 * z), held=hlh(VH, 42 + 2 * z), rfg=SUB, pill3=(ZW[z], TX if z == 1 else '#ffffff', zc)),
        R_(GH, 'MO', f'vs month open {sgs(m * A)}', fds(m), rgx(VS, 48 + mo3), held=hv(VH, 48 + mo3), vfg=[HOT, None, COLD][mo3], rfg=SUB),
        R_(GH, 'PD', pdT, '' if pg == 1 else fds(d), hlx(VS, 30 + 2 * pg), held=hlh(VH, 30 + 2 * pg), rfg=SUB),
        R_(GH, '18:00', f'since 18:00 {sgs(s * A)}', fds(s), hlx(VS, 36 + 2 * sg), held=hlh(VH, 36 + 2 * sg), vfg=[DISC, None, PREM][sg], rfg=SUB),
        R_(GH, 'WEEK', f'week in {sgs(w * A)}', fds(w), rgx(VS, 54 + wg), held=hv(VH, 54 + wg), vfg=[DISC, None, PREM][wg], rfg=SUB),
        R_(GH, 'VIX', f'VIX {f.vix:.1f} · {fds(100 * v, "{:.0f}")}% vs 20d', '', rgx(VS, 51 + vg), held=hv(VH, 51 + vg), rfg=SUB),
        S_(GH, f'EXPECT · ADR {A:.0f}', 'med', '80%'),
        R_(GH, 'S1', f'08:30–08:50 · {ZW[z]}', f'±{e1:.0f}', f'±{VS[1 + 2 * z] * A:.0f}', held=hv(VH, 2 * z)),
        R_(GH, 'S2', f'08:50–09:30 · {ZW[z]}', f'±{e2:.0f}', f'±{VS[7 + 2 * z] * A:.0f}', held=hv(VH, 6 + 2 * z)),
        R_(GH, 'NY AM', f'09:30–11:00 · {ZW[z]}', f'±{eA:.0f}', f'±{VS[13 + 2 * z] * A:.0f}', held=hv(VH, 12 + 2 * z)),
        R_(GH, 'RANGE', f'after 08:30 · {ZW[z]}', f'{VS[18 + 2 * z] * A:.0f}', f'{VS[19 + 2 * z] * A:.0f}', held=hv(VH, 18 + 2 * z)),
        R_(GH, 'NEXT', 'next session range', f'{VS[24 + 2 * z] * A:.0f}', f'{VS[25 + 2 * z] * A:.0f}', held=hv(VH, 24 + 2 * z)),
        S_(DXC, 'LIVE · vs DXY', '×typ', 'DXY'),
        R_(GH, 'S1', lt(sv1, dv1), x2(abs(sv1) / e1), vfg=HOT if abs(sv1) / e1 >= 1 else None, pill=dx_pill(dv1, sv1, 0.42)),
        R_(GH, 'S2', lt(sv2, dv2), x2(abs(sv2) / e2), vfg=HOT if abs(sv2) / e2 >= 1 else None, pill=dx_pill(dv2, sv2, 99)),
        R_(GH, 'NY AM', f'{sgs(svA)} pts', x2(abs(svA) / eA), vfg=HOT if abs(svA) / eA >= 1 else None),
        R_(DXC, 'DXY ⇄', 'big DXY → other way', '79%', '56%', held=True),
        R_(GH, '08:30+', '08:30–09:00 adds', '+' + x2(add), '+0.19×', held=True, vfg=HOT if add >= 0.19 else None)]
print('Cero 5 Jun:', dict(p=round(p, 2), m=round(m, 2), d=round(d, 2), s=round(s, 2), w=round(w, 2), v=round(v, 3), A=A, sv1=sv1, sv2=sv2, svA=svA, dv1=round(dv1, 2), dv2=round(dv2, 2), add=round(add, 2)))
x = bars5(at(6, 0), now)
fig = plt.figure(figsize=(FW_IN, 10.8), dpi=DPI, facecolor=BG)
ax = fig.add_axes([0.02, 0.05, 0.93, 0.86])
lo, hi = x.Low.min(), x.High.max()
ax.set_xlim(-2, len(x) + 40); ax.set_ylim(lo - (hi - lo) * 0.25, hi + (hi - lo) * 0.25)
style(ax, x, 'NQ1! · 5 · CME   Desgarrón   ·   Fri 5 Jun 2026 · NFP · 10:30 ET', every=1)
idx = lambda t: int(np.searchsorted(x.index, t)); n = len(x)
i700, i830, i845, i850, i900 = idx(at(7, 0)), idx(at(8, 30)), idx(at(8, 45)), idx(at(8, 50)), idx(at(9, 0))
dr = g[(g.index >= at(7, 0)) & (g.index < at(9, 0))]
ax.axvspan(i830 - .5, i845 - .5, color='#f23645', alpha=0.12, lw=0)
for yv, lab in ((dr.High.max(), 'DR high'), (dr.Low.min(), 'DR low')):
    ax.plot([i700, n + 2], [yv, yv], color=LVL, lw=1, ls='--', alpha=0.9); ax.text(i700, yv, lab, color=LVL, fontsize=7.5, va='bottom')
ax.axvline(i850 - .5, color=LVL, ls=':', lw=0.9, alpha=0.6)
pcl = float(b[b.tday == T - pd.Timedelta(days=1)].set_index('ts').Close[lambda s_: s_.index <= at(-8, 14)].iloc[-1])
ax.plot([idx(at(9, 30)), n + 2], [pcl, pcl], color=LVL, lw=0.9, ls=':', alpha=0.7); ax.plot([idx(at(9, 30)), n + 2], [(pcl + rthO) / 2] * 2, color=LVL, lw=0.9, ls=':')
ax.text(n + 3, (pcl + rthO) / 2, ' gap 50%', color=LVL, fontsize=7.5, va='center')
candles(ax, x)
for i0, yv, lab, al, ls in ((i830, s1O, '08:30 open', 1, '-'), (i850, s2O, '08:50 open', 0.8, '--')):
    ax.plot([i0, n + 14], [yv, yv], color=GH, lw=1.1, ls=ls, alpha=al); ax.text(n + 1, yv, f' {lab} {yv:.2f}', color=GH, fontsize=7.5, va='bottom')
ax.text(i830, hi + (hi - lo) * 0.12, 'NFP', color=GH, fontsize=8, ha='center')
nxtC = f'NFP 02 Jul · 27d'
draw_card(fig, tally_card('Cero', 'DESGARRÓN', 'NFP', T, now, pd.Timestamp('2026-05-31 18:00'), pd.Timestamp('2026-05-31 18:00'), 'TODAY', True, nxtC), 0.948, 0.905, 'tr')
draw_card(fig, CERO, 0.026, 0.06, 'bl')
fig.text(0.02, 0.957, 'Desgarrón (formerly Cero) · NFP day: the tally (top right) and the NFP stages card (bottom left): 08:29 setup → sizes at today\'s ADR → the release stages against DXY', color=TX, fontsize=12.5, weight='bold')
fig.text(0.02, 0.935, 'Values from NQ 1-minute data, the HYDRA calendar tables and DXY futures at 10:30 ET. No PO3 candles and no VIX / DXY cards in Desgarrón (Gran Rey Cero carries those). TradingView rendering will differ.', color=MU, fontsize=8.5)
plt.savefig(OUTS[0], dpi=DPI, facecolor=BG); plt.close(fig); print(OUTS[0])

# ═══════════ Hollow state, the day after FOMC, Thu 18 Jun 2026 at 10:44
GH, DXC = '#26a69a', '#78909c'
def hollow_state(T, hh, mm, F, isF):
    at = lambda h, m_: T + pd.Timedelta(hours=h, minutes=m_); now = at(hh, mm)
    g = b[b.tday == T].set_index('ts'); f = F.loc[T]; A = float(f.adr); ctx = CTX.loc[T]
    px = lambda t, c='Close': float(g.loc[t, c])
    rthO, cl = px(at(9, 30), 'Open'), px(now)
    amC = px(at(10, 59)) if now >= at(11, 0) else cl
    gp_ = b[b.tday == T - pd.Timedelta(days=1)].set_index('ts'); pcl = float(gp_.Close[gp_.index <= at(-8, 14)].iloc[-1])
    rth = g[(g.index >= at(9, 30)) & (g.index <= now)]; gap = rthO - pcl; ce = pcl + gap / 2; q4 = pcl + 0.75 * gap
    hit = lambda lv: (rth.index[rth.Low <= lv].min() if gap > 0 else rth.index[rth.High >= lv].min())
    st = dict(T=T, now=now, g=g, A=A, p=float(f.moPos), m=float(f.dMO), s=float(f.onMove), v=float(f.vixRel), vix=float(f.vix), gap=gap / A,
              c=float(f.price), PDH=float(ctx.PDH), PDL=float(ctx.PDL), rthO=rthO, cl=cl, svA=amC - rthO, svR=cl - rthO, pcl=pcl, ce=ce, q4=q4,
              ceT=hit(ce), gfT=hit(pcl), qbT=hit(q4) if now < at(11, 0) or True else None,
              dvA=dxm(T, at(9, 30), min(now + pd.Timedelta(minutes=1), at(11, 0))), dvR=dxm(T, at(9, 30), now + pd.Timedelta(minutes=1)))
    st['d'] = (st['c'] - st['PDH']) / A if st['c'] > st['PDH'] else (st['c'] - st['PDL']) / A if st['c'] < st['PDL'] else 0.0
    if isF: st.update(fPost=float(f.fPost), fRng=float(f.fRng), fA=float(CTX.adr.loc[T - pd.Timedelta(days=1)]))
    return st
def hollow_rows(st, isF, mobile=False):
    VS, VH = VSH, VHH; A = st['A']; p, m, d, s, v, g = st['p'], st['m'], st['d'], st['s'], st['v'], st['gap']
    z = zIdx(p); oc = min(8, int(np.floor(p * 8)) + 1); mo3 = 0 if m > 1 else 2 if m < -1 else 1; pg = 0 if d > 0 else 2 if d < 0 else 1
    sg = 0 if s > 0.4 else 2 if s < -0.4 else 1; gg = 0 if g > 0.25 else 2 if g < -0.25 else 1; vg = 0 if v > 0.1 else 2 if v < -0.1 else 1
    o = 58 if isF else 0; eA, eR = VS[o + 2 * z] * A, VS[o + 6 + 2 * z] * A
    lvH, lvL = ('FOMC high', 'FOMC low') if isF else ('PDH', 'PDL')
    pdT = f'above {lvH} {sgs(d * A)}' if pg == 0 else f'below {lvL} {sgs(d * A)}' if pg == 2 else ('inside FOMC day' if isF else 'inside prior day')
    gpT = ('gap up ' if g >= 0 else 'gap down ') + sgs(abs(g) * A)
    gpR = f'F{pcv(VS, 97 + gg)} ½{pcv(VS, 100 + gg)}' if isF else f'½{pcv(VS, 48 + gg)} F{pcv(VS, 51 + gg)}'
    gpH = (hv(VH, 97 + gg) or hv(VH, 100 + gg)) if isF else (hv(VH, 48 + gg) or hv(VH, 51 + gg))
    zc = [DISC, NEU, PREM][z]; T = st['T']; now = st['now']
    dl = T + pd.Timedelta(hours=11 if isF else 10)
    ceS = f'50% hit {st["ceT"]:%H:%M}' if pd.notna(st['ceT']) else (f'50% open · {abs(st["cl"] - st["ce"]):.0f} to go' if now < dl else ('50% missed in NY AM' if isF else '50% missed by 10:00'))
    lt = lambda sv, dv: f'{sgs(sv)} · DXY {ar(dv)}{abs(dv):.2f}'
    title = 'FULL BRINGER · FOMC +1' if isF else 'HOLLOW · NFP WEEK'
    if mobile:
        return [H_(GH, f'◆ {"FOMC +1" if isF else "NFP WEEK"} · NQ1!', 'TODAY', GH, '#ffffff'),
                R_(GH, 'MO', f'{octbar(oc)} {ZW[z]}', f'FH{pcv(VS, 88 + 2 * z)}' if isF else fds(m), pc(p), held=hlh(VH, (88 if isF else 36) + 2 * z)),
                R_(GH, 'EXP', f'AM ±{eA:.0f} RTH {eR:.0f}', '', '', held=hv(VH, o + 6 + 2 * z)),
                R_(GH, 'PD', ('> ' if pg == 0 else '< ' if pg == 2 else 'in ') + ('FOMC ' if isF else 'PD ') + hlx(VS, (76 if isF else 24) + 2 * pg), '' if pg == 1 else fds(d), '', held=hlh(VH, (76 if isF else 24) + 2 * pg)),
                R_(GH, 'GAP', f'gap {fds(g, "{:.2f}")} {gpR}', '', '', held=gpH),
                R_(GH, 'RTH', lt(st['svR'], st['dvR']), '', '', pill=dx_pill(st['dvR'], st['svR'], 0.52 if isF else 0.26)),
                R_(GH, '¼ +1', '¼ ' + (f'broke {st["qbT"]:%H:%M}' if pd.notna(st['qbT']) else 'holding'), '28%', '18%', held=True) if isF else R_(DXC, 'DXY', 'big → other way', '64%', '', held=True)]
    rows = [H_(GH, f'◆ {title} · NQ1!', 'TODAY', GH, '#ffffff'), S_(GH, 'SETUP AT 09:29', 'ADR', 'after')]
    if isF: rows.append(R_(GH, 'FOMC', f'14:00→16:14 {sgs(st["fPost"] * st["fA"])}', fds(st['fPost']), f'R{st["fRng"]:.1f}'))
    rows.append(R_(GH, 'MONTH', f'{octbar(oc)} {pc(p)}', '', f'FH{pcv(VS, 88 + 2 * z)} FL{pcv(VS, 89 + 2 * z)}' if isF else hlx(VS, 36 + 2 * z), held=hlh(VH, (88 if isF else 36) + 2 * z), rfg=SUB, pill3=(ZW[z], TX if z == 1 else '#ffffff', zc)))
    if not isF: rows.append(R_(GH, 'MO', f'vs month open {sgs(m * A)}', fds(m), rgx(VS, 42 + mo3), held=hv(VH, 42 + mo3), vfg=[HOT, None, COLD][mo3], rfg=SUB))
    rows += [R_(GH, 'PD', pdT, '' if pg == 1 else fds(d), hlx(VS, (76 if isF else 24) + 2 * pg), held=hlh(VH, (76 if isF else 24) + 2 * pg), rfg=SUB),
             R_(GH, 'O/N', f'since 18:00 {sgs(s * A)}', fds(s), hlx(VS, (82 if isF else 30) + 2 * sg), held=hlh(VH, (82 if isF else 30) + 2 * sg), vfg=[DISC, None, PREM][sg], rfg=SUB),
             R_(GH, 'GAP', gpT, fds(g, '{:.2f}'), gpR, held=gpH, rfg=SUB),
             R_(GH, 'VIX', f'VIX {st["vix"]:.1f} · {fds(100 * v, "{:.0f}")}% vs 20d', '', rgx(VS, (94 if isF else 45) + vg), held=hv(VH, (94 if isF else 45) + vg), rfg=SUB)]
    if not isF:
        dw = T.dayofweek
        rows.append(R_(GH, 'DAY', T.strftime('%A'), '', f'½{pcv(VS, 54 + dw)}', held=hv(VH, 54 + dw), rfg=SUB))
    rows += [S_(GH, f'EXPECT · ADR {A:.0f}', 'med', '80%'),
             R_(GH, 'NY AM', f'09:30–11:00 · {ZW[z]}', f'±{eA:.0f}', f'±{VS[o + 1 + 2 * z] * A:.0f}', held=hv(VH, o + 2 * z)),
             R_(GH, 'RTH', f'RTH range · {ZW[z]}', f'{eR:.0f}', f'{VS[o + 7 + 2 * z] * A:.0f}', held=hv(VH, o + 6 + 2 * z))]
    if not isF: rows.append(R_(GH, 'SETTLE', '16:15–17:00 range', f'{VS[12 + 2 * z] * A:.0f}', f'{VS[13 + 2 * z] * A:.0f}', held=hv(VH, 12 + 2 * z)))
    k = o + (12 if isF else 18) + 2 * z
    rows.append(R_(GH, 'NEXT', "next day's range", f'{VS[k] * A:.0f}', f'{VS[k + 1] * A:.0f}', held=hv(VH, k)))
    rA = abs(st['svA']) / eA
    rows += [S_(DXC, 'LIVE · vs DXY', '×typ', 'DXY'),
             R_(GH, 'NY AM', lt(st['svA'], st['dvA']), x2(rA), vfg=HOT if rA >= 1 else None, pill=dx_pill(st['dvA'], st['svA'], 99)),
             R_(GH, 'RTH', lt(st['svR'], st['dvR']), '', pill=dx_pill(st['dvR'], st['svR'], 0.52 if isF else 0.26)),
             R_(DXC, 'DXY ⇄', 'big DXY → other way', '93%' if isF else '64%', '31%' if isF else '45%', held=True)]
    if isF: rows.append(R_(GH, '¼ +1', '¼ ' + (f'broke {st["qbT"]:%H:%M}' if pd.notna(st['qbT']) else 'holding'), '28%', '18%', held=True))
    rows.append(R_(GH, 'GAP', ceS, f'{pcv(VS, (100 if isF else 48) + gg)}%', f'F {st["gfT"]:%H:%M}' if pd.notna(st['gfT']) else f'F{pcv(VS, (97 if isF else 51) + gg)}', held=gpH))
    return rows
def hollow_chart(st, isF, out, title, sub, every=1):
    T, now, g = st['T'], st['now'], st['g']; at = lambda h, m_: T + pd.Timedelta(hours=h, minutes=m_)
    x = bars5(at(-6, 0) if not isF else at(6, 0), now)
    fig = plt.figure(figsize=(FW_IN, 10.8), dpi=DPI, facecolor=BG)
    ax = fig.add_axes([0.02, 0.05, 0.93, 0.86])
    lo, hi = min(x.Low.min(), st['pcl']), max(x.High.max(), st['PDH'] if isF else x.High.max())
    ax.set_xlim(-2, len(x) + 40); ax.set_ylim(lo - (hi - lo) * 0.95, hi + (hi - lo) * 0.2)
    style(ax, x, title, every=every)
    idx = lambda t: int(np.searchsorted(x.index, t)); n = len(x); i930, i1100 = idx(at(9, 30)), idx(at(11, 0))
    gp = st['rthO'] - st['pcl']
    if isF:
        for k in range(9):
            y = st['pcl'] + gp * k / 8
            ax.plot([i930, i1100], [y, y], color=LVL if k <= 4 else OQ, lw=2 if k == 4 else 0.8, ls='--' if k == 4 else ':', alpha=1 if k in (4, 6, 8) else 0.45, zorder=2)
        ax.fill_between([i930, i1100], st['pcl'] + gp * 0.75, st['rthO'], color=OQ, alpha=0.2, lw=0, zorder=1)
        ax.text(i1100 + 0.5, st['pcl'] + gp * 0.875, 'open-side ¼', color=OQ, fontsize=7.5, va='center')
        ax.axvspan(i930 - .5, i1100 - .5, color=OQ, alpha=0.05, lw=0)
        fp = b[b.tday == T - pd.Timedelta(days=1)].set_index('ts'); rr = fp[(fp.index >= at(-24 + 9, 30)) & (fp.index <= at(-24 + 16, 14))]
        for yv, lab in ((rr.High.max(), 'FOMC high'), (rr.Low.min(), 'FOMC low')):
            if lo - (hi - lo) * 0.9 < yv < hi + (hi - lo) * 0.2:
                ax.plot([0, n + 2], [yv, yv], color=LVL, lw=1, ls='--'); ax.text(n + 3, yv, ' ' + lab, color=LVL, fontsize=7.5, va='center')
    else:
        ax.plot([i930, n + 2], [st['pcl']] * 2, color=LVL, lw=0.9, ls=':', alpha=0.7); ax.plot([i930, n + 2], [st['ce']] * 2, color=LVL, lw=0.9, ls=':')
        ax.text(n + 3, st['ce'], ' gap 50%', color=LVL, fontsize=7.5, va='center')
    candles(ax, x)
    rows = hollow_rows(st, isF)
    nxt = 'NFP week 29 Jun · 11d' if isF else 'FOMC +1 30 Jul · 30d'
    draw_card(fig, tally_card('Hollow', 'HOLLOW', 'FOMC +1' if isF else 'NFP week', T, now, T - pd.Timedelta(days=T.dayofweek + 1) + pd.Timedelta(hours=18), pd.Timestamp('2026-05-31 18:00'), 'TODAY', True, nxt), 0.948, 0.905, 'tr')
    draw_card(fig, rows, 0.026, 0.06, 'bl')
    fig.text(0.02, 0.957, sub[0], color=TX, fontsize=12.5, weight='bold'); fig.text(0.02, 0.935, sub[1], color=MU, fontsize=8.5)
    plt.savefig(out, dpi=DPI, facecolor=BG); plt.close(fig); print(out)
stF = hollow_state(pd.Timestamp('2026-06-18'), 10, 44, FA, True)
print('Hollow 18 Jun:', {k: (round(v, 3) if isinstance(v, float) else v) for k, v in stF.items() if k not in ('g',)})
hollow_chart(stF, True, OUTS[1], 'NQ1! · 5 · CME   Hollow   ·   Thu 18 Jun 2026 · the day after FOMC · 10:45 ET',
             ("Hollow rebuilt · the day after FOMC (Full Bringer, moved here from Vizard): gap octants, FOMC high / low, tally and stages card",
              "Values from NQ 1-minute data, the HYDRA calendar tables and DXY futures at 10:45 ET. No PO3 candles and no VIX / DXY cards in Hollow any more. TradingView rendering will differ."))
stW = hollow_state(pd.Timestamp('2026-06-30'), 11, 29, WK, False)
print('Hollow 30 Jun:', {k: (round(v, 3) if isinstance(v, float) else v) for k, v in stW.items() if k not in ('g',)})
hollow_chart(stW, False, OUTS[2], 'NQ1! · 5 · CME   Hollow   ·   Tue 30 Jun 2026 · NFP week (NFP Thu 2 Jul) · 11:30 ET',
             ("Hollow rebuilt · NFP week, Tuesday: the stages card in its NFP-week mode (setup → expect → NY AM and RTH against DXY)",
              "Values from NQ 1-minute data, the HYDRA calendar tables and DXY futures at 11:30 ET. TradingView rendering will differ."), every=2)

# ═══════════ Mobile: Cero (5 Jun) and Hollow (18 Jun) cards
FW_IN = 9.0
GH, DXC = '#ff7043', '#00897b'
fig = plt.figure(figsize=(FW_IN, 11.0), dpi=DPI, facecolor=BG)
fig.text(0.03, 0.962, 'Desgarrón and Hollow · Mobile cards', color=TX, fontsize=11.5, weight='bold')
fig.text(0.03, 0.943, 'Left column: Desgarrón on NFP day 5 Jun 2026, 10:30 ET. Right: Hollow the day after FOMC, 18 Jun 2026, 10:45 ET.', color=MU, fontsize=8)
z = zIdx(p)
CM = [H_(GH, '◆ NFP · NQ1!', 'TODAY', GH, '#ffffff'),
      R_(GH, 'MO', f'{octbar(oc)} {ZW[z]}', fds(m), pc(p), held=hlh(VHC, 42 + 2 * z), vfg=[HOT, None, COLD][mo3]),
      R_(GH, 'EXP', f'S1 ±{e1:.0f} AM ±{eA:.0f}', f'{VSC[18 + 2 * z] * A:.0f}', 'rng', held=hv(VHC, 18 + 2 * z)),
      R_(GH, 'PD', ('> PDH ' if pg == 0 else '< PDL ' if pg == 2 else 'in PD ') + hlx(VSC, 30 + 2 * pg), '' if pg == 1 else fds(d), '', held=hlh(VHC, 30 + 2 * pg)),
      R_(GH, 'S2', lt(sv2, dv2), x2(abs(sv2) / e2), pill=dx_pill(dv2, sv2, 99)),
      R_(DXC, 'DXY', 'big → other way', '79%', '', held=True),
      R_(GH, '08:30+', f'adds +{x2(add)}', '+0.19×', '', held=True)]
gC = b[b.tday == T].set_index('ts'); gC = gC[gC.index <= now]; Rn = np.array(CK['NFP']['R']); jn = (now - (T - pd.Timedelta(hours=6))).total_seconds() / 1800
vA = (gC.High.max() - gC.Low.min()) / A; q25, q75 = np.interp(jn, range(1, 47), Rn[1]), np.interp(jn, range(1, 47), Rn[3])
sB = 'ABOVE' if vA > q75 else 'BELOW' if vA < q25 else 'INSIDE'
clk = R_(GH, 'NOW', f'range {gC.High.max() - gC.Low.min():.0f}', x2(vA), '', pill=(sB, '#ffffff' if sB != 'INSIDE' else TX, HOT if sB == 'ABOVE' else COLD if sB == 'BELOW' else NEU))
draw_card(fig, tally_card('Cero', 'DESGARRÓN', 'NFP', T, now, pd.Timestamp('2026-05-31 18:00'), pd.Timestamp('2026-05-31 18:00'), 'TODAY', True, '', True, clk), 0.03, 0.91, 'tl', fs=7.4, RH=0.022)
draw_card(fig, CM, 0.03, 0.70, 'tl', fs=7.4, RH=0.022)
TF = stF['T']; nowF = stF['now']; gF = b[b.tday == TF].set_index('ts'); gF = gF[gF.index <= nowF]
RnF = np.array(CK['POST']['R']) if 'POST' in CK else Rn; jF = (nowF - (TF - pd.Timedelta(hours=6))).total_seconds() / 1800
vF = (gF.High.max() - gF.Low.min()) / stF['A']; sF = 'ABOVE' if vF > np.interp(jF, range(1, 47), RnF[3]) else 'BELOW' if vF < np.interp(jF, range(1, 47), RnF[1]) else 'INSIDE'
clkF = R_(GH, 'NOW', f'range {gF.High.max() - gF.Low.min():.0f}', x2(vF), '', pill=(sF, '#ffffff' if sF != 'INSIDE' else TX, HOT if sF == 'ABOVE' else COLD if sF == 'BELOW' else NEU))
GH, DXC = '#26a69a', '#78909c'
draw_card(fig, tally_card('Hollow', 'HOLLOW', 'FOMC +1', TF, nowF, TF - pd.Timedelta(days=TF.dayofweek + 1) + pd.Timedelta(hours=18), pd.Timestamp('2026-05-31 18:00'), 'TODAY', True, '', True, clkF), 0.52, 0.91, 'tl', fs=7.4, RH=0.022)
draw_card(fig, hollow_rows(stF, True, True), 0.52, 0.70, 'tl', fs=7.4, RH=0.022)
plt.savefig(OUTS[3], dpi=DPI, facecolor=BG); plt.close(fig); print(OUTS[3])
