"""Mocks of the rebuilt Vizard (NQ1! 5-minute). Card values are computed the way the script computes them, from NQ 1-minute
bars, the HYDRA FOMC tables, DXY futures (5-minute) and CME's ZQ prices of 12 Oct 2026.
  1) FOMC day Wed 29 Jul 2026, 15:30 ET: tally card (top right), stages card (bottom left), Full layout.
  2) Fri 9 Oct 2026, 15:00 ET: tally, Fed and stages cards on the price chart; the pane with the event clock and the
     Fed map side by side.
  3) Mobile layout, FOMC day 29 Jul 2026, 15:30 ET.
  python3 mock_v2.py out1.png out2.png out3.png"""
import sys, re, json, datetime as dt, numpy as np, pandas as pd, matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
sys.path.insert(0, '/home/claude/hm/fed')
import fedwatch as FW
plt.rcParams['font.family'] = 'DejaVu Sans'
MONO = 'DejaVu Sans Mono'
BG, BODY, BODY2, NEU = '#0e1117', '#161a23', '#1c2130', '#3a3f4b'
TX, SUB, MU = '#e6e9ef', '#9aa3b5', '#5d6476'
HOT, COLD, OK, WARN, PREM, DISC = '#ff8a65', '#64b5f6', '#66bb6a', '#ff5252', '#ef5350', '#66bb6a'
GH, LVL, DXC, OQ, CFD = '#ab47bc', '#ffb300', '#00897b', '#26a69a', '#5c6bc0'
HTHI, HTLO, MAPH, MAPC = '#5c6bc0', '#1f2338', '#283593', '#ffb300'
UPC, DNC = '#089981', '#f23645'
DPI, FW_IN = 100, 18.0

S = open('/home/claude/hm/vizard2/Vizard.pine', encoding='utf-8').read()
FO = [dt.date(int(x[:4]), int(x[4:6]), int(x[6:])) for x in re.findall(r'20\d{6}', S[S.index('S_FOMC'):S.index('S_CPI')])]
VS = [float(v) for v in re.search(r'var array<float> VS = parseStats\(isES \? "[^"]+" : "([^"]+)"', S).group(1).split(',')]
TAL = [r.split(',') for r in re.search(r'TAL_NQ = "(.*?)"\nTAL_END', S, re.S).group(1).replace('"\n     + "', '').split(';')]
TAL = [(int(r[0]), int(r[1]), int(r[2]), float(r[3]) if len(r) > 3 and r[3] else np.nan) for r in TAL if len(r) >= 3]

b = pd.read_pickle('/home/claude/kyw/bars_NQ_all.pkl')
CTX = pd.read_pickle('/home/claude/hm/senbon/ctx_NQ.pkl')
FN = pd.read_pickle('/home/claude/hm/hydra_fomc/fomc_NQ.pkl')
DXN = pd.read_pickle('/home/claude/hm/hydra_fomc/dxy_NQ.pkl')
CK = json.load(open('/home/claude/hm/clock.json'))['NQ']
m1 = b.set_index('ts')

# ── formatting helpers (the script's)
pc = lambda v: '—' if v is None or not np.isfinite(v) else f'{100 * v:.0f}%'
sgn = lambda v, f='{:.0f}': '—' if v is None or not np.isfinite(v) else ('+' if v >= 0 else '−') + f.format(abs(v))
ar = lambda v: '·' if v is None or not np.isfinite(v) or v == 0 else ('▲' if v > 0 else '▼')
x2 = lambda v: f'{v:.2f}×'
def gauge(f, n=10):
    k = 0 if f is None or not np.isfinite(f) else int(round(min(1, max(0, f)) * n)); return '█' * k + '░' * (n - k)
def octbar(o): return ''.join('█' if i == o else '░' for i in range(1, 9))
def octof(px, h, l): return None if h <= l else min(8, int(np.floor((px - l) / (h - l) * 8)) + 1)
def meter(p):
    k = int(round(max(0, min(100, p)) / 10)); return '─' * k + '●' + '─' * (10 - k)

# ── card renderer: TradingView table cells, monospace, widths from the longest text in each column
def draw_card(fig, rows, x, y, corner='tl', fs=8.0, RH=0.0215, ax_w=None):
    cw = fs * 0.602 / 72 * DPI / (FW_IN * DPI)                      # one monospace character, figure fraction
    w = [0, 0, 0, 0]
    for r in rows:
        if r['k'] == 'row': w = [max(w[0], len(r['key'])), max(w[1], len(r['txt'])), max(w[2], len(r['val'])), max(w[3], len(r['right']))]
        if r['k'] == 'sub': w = [w[0], max(w[1], len(r['txt'])), max(w[2], len(r['a1'])), max(w[3], len(r['a2']))]
    for r in rows:
        if r['k'] == 'head':
            w[3] = max(w[3], len(r['pill']))
            if len(r['title']) > w[0] + w[1] + w[2] + 2: w[1] = len(r['title']) - w[0] - w[2] - 2
        if r['k'] == 'wide' and len(r['txt']) > w[1] + w[2] + w[3] + 2: w[1] = len(r['txt']) - w[2] - w[3] - 2
    CW = [0.0018] + [(n + 1.6) * cw for n in w]
    W, H = sum(CW), RH * len(rows)
    x0 = x if corner[1] == 'l' else x - W
    yt = y if corner[0] == 't' else y + H
    def cell(c0, c1, yy, txt, fg, bg, bold=False, ha='center'):
        xa = x0 + sum(CW[:c0]); ww = sum(CW[c0:c1 + 1])
        fig.add_artist(Rectangle((xa, yy - RH), ww, RH, transform=fig.transFigure, fc=bg, ec=BG, lw=0.5, zorder=20))
        if txt:
            fig.text(xa + (0.6 * cw if ha == 'left' else ww / 2), yy - RH / 2, txt, color=fg, fontsize=fs, family=MONO, weight='bold' if bold else 'normal', ha=ha, va='center', zorder=21)
    yy = yt
    for r in rows:
        cell(0, 0, yy, '', None, r['col'])
        if r['k'] == 'head':
            cell(1, 3, yy, r['title'], '#ffffff', r['col'], True, 'left'); cell(4, 4, yy, r['pill'], r['pfg'], r['pbg'], True)
        elif r['k'] == 'sub':
            cell(1, 1, yy, '', MU, BODY2); cell(2, 2, yy, r['txt'], MU, BODY2, False, 'left'); cell(3, 3, yy, r['a1'], MU, BODY2); cell(4, 4, yy, r['a2'], MU, BODY2)
        elif r['k'] == 'wide':
            cell(1, 1, yy, r['key'], MU, BODY); cell(2, 4, yy, r['txt'], r.get('fg', TX), BODY, False, 'left')
        else:
            h = r.get('held', False)
            cell(1, 1, yy, r['key'], '#ffffff' if h else MU, OK if h else BODY, h)
            cell(2, 2, yy, r['txt'], TX, BODY, False, 'left')
            p3 = r.get('pill3'); p4 = r.get('pill')
            if p3: cell(3, 3, yy, p3[0], p3[1], p3[2], True)
            else: cell(3, 3, yy, r['val'], r.get('vfg') or TX, BODY, True)
            if p4: cell(4, 4, yy, p4[0], p4[1], p4[2], True)
            else: cell(4, 4, yy, r['right'], r.get('rfg') or MU, BODY)
        yy -= RH
    return x0, yt - H, W, H

def H_(col, title, pill, pfg, pbg): return dict(k='head', col=col, title=title, pill=pill, pfg=pfg, pbg=pbg)
def S_(col, txt, a1, a2): return dict(k='sub', col=col, txt=txt, a1=a1, a2=a2)
def R_(col, key, txt, val='', right='', held=False, vfg=None, rfg=None, pill=None, pill3=None):
    return dict(k='row', col=col, key=key, txt=txt, val=val, right=right, held=held, vfg=vfg, rfg=rfg, pill=pill, pill3=pill3)
def W_(col, key, txt, fg=TX): return dict(k='wide', col=col, key=key, txt=txt, fg=fg)

def candles(ax, x):
    for i, (t, r_) in enumerate(x.iterrows()):
        c = UPC if r_.Close >= r_.Open else DNC
        ax.plot([i, i], [r_.Low, r_.High], color=c, lw=0.7, zorder=3)
        ax.add_patch(Rectangle((i - .35, min(r_.Open, r_.Close)), .7, max(abs(r_.Close - r_.Open), 0.5), fc=c, ec=c, lw=0.3, zorder=4))
def style(ax, x, title, every=2):
    ax.set_facecolor(BG); ax.yaxis.tick_right(); ax.tick_params(axis='y', colors=MU, labelsize=8); ax.tick_params(axis='x', length=0)
    for s_ in ax.spines.values(): s_.set_visible(False)
    ax.grid(color='#1a1f2b', lw=0.6, zorder=0)
    ticks = [i for i, t in enumerate(x.index) if t.minute == 0 and t.hour % every == 0]
    ax.set_xticks(ticks); ax.set_xticklabels([x.index[i].strftime('%H:%M') for i in ticks], color=MU, fontsize=8)
    if title: ax.text(0.005, 0.985, title, transform=ax.transAxes, color=SUB, fontsize=9, va='top', zorder=30)
def bars5(t0, t1): return m1[(m1.index >= t0) & (m1.index <= t1)].resample('5min').agg(dict(Open='first', High='max', Low='min', Close='last')).dropna()

# ── DXY futures, 5-minute (CT → ET), one contract per trading day, ADR20 per day (as in the HYDRA DXY study)
X = pd.read_csv('/mnt/user-data/uploads/DXY_2023_2026_5min_continuous.csv')
X['ts'] = pd.to_datetime(X.Date + ' ' + X.Time) + pd.Timedelta(hours=1); X = X.sort_values('ts')
X['tday'] = (X.ts + pd.Timedelta(hours=6)).dt.normalize()
DXD = {}
for td, g in X.groupby('tday'):
    c = g.Contract.value_counts().index[0]; g = g[g.Contract == c]
    if len(g) >= 150: DXD[td] = g.set_index('ts')
dd_ = sorted(DXD); dxday = pd.DataFrame({'H': [DXD[d].High.max() for d in dd_], 'L': [DXD[d].Low.min() for d in dd_]}, index=pd.DatetimeIndex(dd_))
dxday['a20'] = (dxday.H - dxday.L).rolling(20).mean().shift(1)

# ════════════════════════════════════════════════ state on an FOMC day at 15:29 (bar closed)
def fomc_state(D, hh=15, mm=29):
    T = pd.Timestamp(D); at = lambda h, m: T + pd.Timedelta(hours=h, minutes=m)
    g = b[b.tday == T].set_index('ts'); now = at(hh, mm)
    px = lambda t, c='Close': float(g.loc[t, c])
    f = FN.loc[T]; c = CTX.loc[T]; A = float(f.adr)
    c59 = float(f.price)
    p, m, s = float(f.moPos), float(f.dMO), float(f.preMove)
    d = (c59 - c.PDH) / A if c59 > c.PDH else (c59 - c.PDL) / A if c59 < c.PDL else 0.0
    xdx = float(DXN.loc[T].dx_4w)
    o14, c1429, o1430, cl = px(at(14, 0), 'Open'), px(at(14, 29)), px(at(14, 30), 'Open'), px(now)
    sv1, sv2 = c1429 - o14, cl - o1430
    dx = DXD[T]; a20 = float(dxday.a20.loc[T])
    dxo = lambda h, m_: float(dx.Open[dx.index >= at(h, m_)].iloc[0])
    dxc = lambda h, m_: float(dx.Close[dx.index + pd.Timedelta(minutes=5) <= at(h, m_)].iloc[-1])
    dv1 = (dxc(14, 30) - dxo(14, 0)) / a20; dv2 = (dxc(hh, mm + 1) - dxo(14, 30)) / a20
    gp = b[b.tday == T - pd.Timedelta(days=1)].set_index('ts')
    pcl = float(gp.Close[gp.index <= at(-24 + 16, 14)].iloc[-1]) if len(gp) else np.nan
    rthO = px(at(9, 30), 'Open')
    day = g[(g.index >= at(9, 30)) & (g.index <= now)]
    gfT = day[day.Low <= pcl].index.min() if pcl < rthO else day[day.High >= pcl].index.min()
    return dict(T=T, g=g, now=now, A=A, c59=c59, p=p, m=m, d=d, s=s, x=xdx, sep=T.month in (3, 6, 9, 12), MO=float(c.MO), PDH=float(c.PDH), PDL=float(c.PDL),
                o14=o14, o1430=o1430, cl=cl, sv1=sv1, sv2=sv2, dv1=dv1, dv2=dv2, pcl=pcl, rthO=rthO, gfT=gfT, in2=True, st=True)

def zIdx(p): return 1 if p is None or not np.isfinite(p) else 2 if p >= 0.75 else 0 if p <= 0.25 else 1
ZW = ['DISC', 'MID', 'PREM']
def dx_pill(dv, sv, thr):
    if not (np.isfinite(dv) and np.isfinite(sv)) or dv == 0 or sv == 0: return ('—', TX, BODY)
    big, oth = abs(dv) >= thr, np.sign(dv) != np.sign(sv)
    return (('⇄' if oth else '⇉') + (' BIG' if big else ''), '#ffffff' if big else TX, (OK if oth else WARN) if big else NEU)
def hl(i): return f'H{VS[i]:.0f} L{VS[i + 1]:.0f}'

def stages_rows(st, fz, vzF, pill, mobile=False):
    A, p, m, d, s, x = st['A'], st['p'], st['m'], st['d'], st['s'], st['x']
    z = zIdx(p); oc = None if not np.isfinite(p) else min(8, int(np.floor(p * 8)) + 1)
    mo3 = 0 if m > 1 else 2 if m < -1 else 1
    pg = 0 if d > 0 else 2 if d < 0 else 1
    sg = 0 if s > 0.4 else 2 if s < -0.4 else 1
    sep = st['sep']
    e1, e2 = VS[0 if sep else 2] * A, VS[4 + 2 * z] * A
    pdT = f'above PDH {sgn(d * A)}' if pg == 0 else f'below PDL {sgn(d * A)}' if pg == 2 else 'inside prior day'
    d4 = '' if not np.isfinite(x) else 'S2▲' + ('27%' if x > 0 else '65%')
    zc = [DISC, NEU, PREM][z]
    rows = []
    if not mobile:
        rows += [H_(GH, '◆ FOMC STAGES · NQ1!', pill[0], pill[1], pill[2]),
                 S_(GH, 'SETUP AT 13:59' if fz else 'SETUP · LIVE', 'ADR', ''),
                 R_(GH, 'MONTH', f'{octbar(oc)} {pc(p)}', '', '', pill=(ZW[z], TX if z == 1 else '#ffffff', zc)),
                 R_(GH, 'MO', f'vs month open {sgn(m * A)}', sgn(m, '{:.1f}'), '', pill=(['OVER', 'NEAR', 'UNDER'][mo3], TX if mo3 == 1 else '#ffffff', [HOT, NEU, COLD][mo3])),
                 R_(GH, 'PD', pdT, '' if pg == 1 else sgn(d, '{:.1f}'), hl(16 + 2 * pg), rfg=SUB),
                 R_(GH, '18:00', f'since 18:00 {sgn(s * A)}', sgn(s, '{:.1f}'), hl(22 + 2 * sg), vfg=[DISC, None, PREM][sg], rfg=SUB),
                 R_(DXC, 'DXY 4W', f'DXY 4 weeks {ar(x)}', sgn(x, '{:.1f}'), d4, rfg=SUB),
                 S_(GH, f'EXPECT · ADR {A:.0f}', 'med', '80%'),
                 R_(GH, 'S1', '14:00–14:30' + (' · SEP' if sep else ''), f'±{e1:.0f}', f'±{VS[1 if sep else 3] * A:.0f}'),
                 R_(GH, 'S2', f'14:30–16:14 · {ZW[z]}', f'±{e2:.0f}', f'±{VS[5 + 2 * z] * A:.0f}'),
                 R_(GH, 'RANGE', f'after 14:00 · {ZW[z]}', f'{VS[10 + 2 * z] * A:.0f}', f'{VS[11 + 2 * z] * A:.0f}'),
                 R_(GH, 'EDGE', 'none held on NQ')]
        if vzF:
            r1, r2 = abs(st['sv1']) / e1, abs(st['sv2']) / e2
            lt = lambda sv, dv: f'{sgn(sv)} · DXY {ar(dv)}{abs(dv):.2f}'
            gfT = st['gfT']
            rows += [S_(DXC, 'LIVE · vs DXY', '×typ', 'DXY'),
                     R_(GH, 'S1', lt(st['sv1'], st['dv1']), x2(r1), vfg=HOT if r1 >= 1 else None, pill=dx_pill(st['dv1'], st['sv1'], 0.25)),
                     R_(GH, 'S2', lt(st['sv2'], st['dv2']), x2(r2), vfg=HOT if r2 >= 1 else None, pill=dx_pill(st['dv2'], st['sv2'], 0.5)),
                     R_(DXC, 'DXY ⇄', 'big DXY → other way', '85%', '73%', held=True),
                     R_(GH, 'GAP', 'gap ' + (f'filled {gfT:%H:%M}' if pd.notna(gfT) else f'open · {abs(st["cl"] - st["pcl"]):.0f} to go'), '74%', '61%', held=True)]
    else:
        rows += [H_(GH, '◆ STAGES · NQ1!', pill[0], pill[1], pill[2]),
                 R_(GH, 'MO', f'{octbar(oc)} {ZW[z]}', sgn(m, '{:.1f}'), pc(p), vfg=[HOT, None, COLD][mo3]),
                 R_(GH, 'EXP', f'S1 ±{e1:.0f} S2 ±{e2:.0f}', f'{VS[10 + 2 * z] * A:.0f}', 'rng'),
                 R_(GH, 'PD', ('> PDH ' if pg == 0 else '< PDL ' if pg == 2 else 'in PD ') + hl(16 + 2 * pg), '' if pg == 1 else sgn(d, '{:.1f}'), '')]
        if vzF:
            r2 = abs(st['sv2']) / e2; gfT = st['gfT']
            rows += [R_(GH, 'S2', f'{sgn(st["sv2"])} · DXY {ar(st["dv2"])}{abs(st["dv2"]):.2f}', x2(r2), pill=dx_pill(st['dv2'], st['sv2'], 0.5)),
                     R_(DXC, 'DXY', 'big → other way', '85%', '', held=True),
                     R_(GH, 'GAP', f'filled {gfT:%H:%M}' if pd.notna(gfT) else 'open', '74%', '61%', held=True)]
        else:
            rows += [R_(DXC, 'DXY 4W', f'DXY 4w {ar(x)} {d4}', sgn(x, '{:.1f}'), '')]
    return rows

def tally_rows(T, now, wk0, mo0, mobile=False, clock=None):
    rec = [r for r in TAL if r[0] < int(T.strftime('%Y%m%d'))][-12:]
    up, dn = sum(r[1] > 0 for r in rec), sum(r[1] < 0 for r in rec)
    ru, rd = sum(r[2] > 0 for r in rec), sum(r[2] < 0 for r in rec)
    gaps = [r[3] for r in rec if np.isfinite(r[3])]; gu = sum(g_ > 0 for g_ in gaps)
    gav, gab = np.mean(gaps), np.mean(np.abs(gaps))
    cl = float(m1.Close[m1.index <= now].iloc[-1])
    def zone(key, t0):
        y = m1[(m1.index >= t0) & (m1.index <= now)]; h, l = y.High.max(), y.Low.min(); o = octof(cl, h, l)
        z = 'PREM' if o >= 7 else 'DISC' if o <= 2 else 'EQ'
        return R_(GH, key, f'{octbar(o)} O{o}', '', f'−{h - cl:.0f}', pill3=(z, TX if z == 'EQ' else '#ffffff', PREM if z == 'PREM' else DISC if z == 'DISC' else NEU))
    nf = next(d for d in FO if d >= T.date()); nd = (nf - T.date()).days
    pNow = nf == T.date(); pill = 'TODAY' if pNow else f'IN {(nf - dt.timedelta(days=1) - T.date()).days}D'
    head = H_(GH, '◆ VIZARD · ' + ('FOMC' if pNow else 'FOMC D1') + ' · NQ1!', pill, GH if pNow else '#ffffff', '#ffffff' if pNow else '#2b2f39')
    if not mobile:
        return [head, S_(GH, 'last 12 FOMC days', '▲', '▼'),
                R_(GH, 'DAY', f'{gauge(up / (up + dn))} {pc(up / (up + dn))}', str(up), str(dn), vfg=DISC, rfg=PREM),
                R_(GH, 'RTH', f'{gauge(ru / (ru + rd))} {pc(ru / (ru + rd))}', str(ru), str(rd), vfg=DISC, rfg=PREM),
                R_(GH, 'GAP', f'avg gap · ▲{gu}/{len(gaps)}', sgn(gav, '{:.1f}'), f'±{gab:.1f}'),
                zone('WEEK', wk0), zone('MONTH', mo0),
                W_(GH, 'NEXT', f'FOMC {nf:%d %b}' + (' · today' if pNow else f' · {nd}d'))]
    return [head, clock, R_(GH, 'DAY', f'last 12 {gauge(up / (up + dn), 5)}', f'▲{up}', f'▼{dn}', vfg=DISC, rfg=PREM),
            R_(GH, 'GAP', f'avg · ▲{gu}/{len(gaps)}', sgn(gav, '{:.1f}'), f'±{gab:.1f}'), zone('WK', wk0), zone('MO', mo0)]

def chart_fomc(ax, st, x):
    T = st['T']; idx = lambda t: int(np.searchsorted(x.index, t)); at = lambda h, m: T + pd.Timedelta(hours=h, minutes=m)
    n = len(x); i930, i1100, i1400, i1430 = idx(at(9, 30)), idx(at(11, 0)), idx(at(14, 0)), idx(at(14, 30))
    ax.axvspan(i930 - .5, i1100 - .5, color=OQ, alpha=0.05, lw=0)
    ax.axvspan(i1400 - .5, i1430 - .5, color='#2962ff', alpha=0.10, lw=0); ax.axvspan(i1430 - .5, n + 3, color='#2962ff', alpha=0.06, lw=0)
    gp = st['rthO'] - st['pcl']
    for k in range(9):
        y = st['pcl'] + gp * k / 8
        ax.plot([i930, i1100], [y, y], color=LVL if k <= 4 else OQ, lw=2 if k == 4 else 0.8, ls='--' if k == 4 else ':', alpha=1 if k in (4, 6, 8) else 0.45, zorder=2)
    ax.fill_between([i930, i1100], st['pcl'] + gp * 0.75, st['rthO'], color=OQ, alpha=0.2, lw=0, zorder=1)
    candles(ax, x)
    xd = n + 14
    ax.plot([i1400, xd], [st['o14']] * 2, color=GH, lw=1.1, zorder=5); ax.text(n + 1, st['o14'], f' 14:00 open {st["o14"]:.2f}', color=GH, fontsize=7.5, va='bottom')
    ax.plot([i1430, xd], [st['o1430']] * 2, color=GH, lw=1, ls='--', alpha=0.8, zorder=5); ax.text(n + 1, st['o1430'], f' 14:30 open {st["o1430"]:.2f}', color=GH, fontsize=7.5, va='top')

# ════════════════ 1) FOMC day, Full layout
st = fomc_state('2026-07-29')
T = st['T']; x = bars5(T + pd.Timedelta(hours=6), st['now'])
lo, hi = x.Low.min(), x.High.max()
fig = plt.figure(figsize=(FW_IN, 10.4), dpi=DPI, facecolor=BG)
ax = fig.add_axes([0.02, 0.05, 0.93, 0.86])
ax.set_xlim(-2, len(x) + 40); ax.set_ylim(lo - (hi - lo) * 0.95, hi + (hi - lo) * 0.25)
style(ax, x, 'NQ1! · 5 · CME   Vizard   ·   Wed 29 Jul 2026 · FOMC decision day · 15:30 ET')
chart_fomc(ax, st, x)
draw_card(fig, tally_rows(T, st['now'], pd.Timestamp('2026-07-26 18:00'), pd.Timestamp('2026-06-30 18:00')), 0.948, 0.905, 'tr')
draw_card(fig, stages_rows(st, True, True, ('TODAY', GH, '#ffffff')), 0.026, 0.06, 'bl')
fig.text(0.02, 0.957, 'Vizard rebuilt · FOMC day: the tally (top right) and the new stages card (bottom left): 13:59 setup → sizes to expect at today\'s ADR → the stages live against DXY', color=TX, fontsize=12.5, weight='bold')
fig.text(0.02, 0.935, 'Values from NQ 1-minute data, the HYDRA FOMC tables and DXY futures at 15:30 ET. The Fed card (own corner) is in mock 2: no ZQ prices for this date. TradingView rendering will differ.', color=MU, fontsize=8.5)
plt.savefig(sys.argv[1], dpi=DPI, facecolor=BG); plt.close(fig); print(sys.argv[1], {k: (round(v, 3) if isinstance(v, float) else v) for k, v in st.items() if k not in ('g',)})

# ════════════════ 2) Fri 9 Oct 2026 15:00: three cards + pane with the event clock and the Fed map
T2 = pd.Timestamp('2026-10-09'); now2 = T2 + pd.Timedelta(hours=14, minutes=59)
c2 = CTX.loc[T2]; A2 = float(c2.adr)
g2 = b[b.tday == T2].set_index('ts'); g2 = g2[g2.index <= now2]
cl2, tdO2, tdH2, tdL2 = float(g2.Close.iloc[-1]), float(g2.Open.iloc[0]), g2.High.max(), g2.Low.min()
mon = CTX[(CTX.index.year == 2026) & (CTX.index.month == 10) & (CTX.index < T2)]
mH, mL = max(mon.H.max(), tdH2), min(mon.L.min(), tdL2)
st2 = dict(A=A2, p=(cl2 - mL) / (mH - mL), m=(cl2 - c2.MO) / A2, s=(cl2 - tdO2) / A2, x=np.nan, sep=False,
           d=(cl2 - c2.PDH) / A2 if cl2 > c2.PDH else (cl2 - c2.PDL) / A2 if cl2 < c2.PDL else 0.0)
# Fed: CME's 12 Oct 2026 ZQ prices (one snapshot, so the 1-day and 5-day changes are blank)
P = {(2026, 10): 96.1163, (2026, 11): 96.0675, (2026, 12): 95.9125, (2027, 1): 95.8425, (2027, 2): 95.7475, (2027, 3): 95.6650,
     (2027, 4): 95.5575, (2027, 5): 95.4675, (2027, 6): 95.3925, (2027, 7): 95.3575, (2027, 8): 95.3225, (2027, 9): 95.3025, (2027, 10): 95.2825}
grid = [FW.month_add(2026, 9, k) for k in range(14)]
fr = FW.fedwatch([P.get(mm, float('nan')) for mm in grid], grid, FO, dt.date(2026, 10, 12), k_meet=8)
lo0, base = fr['lower0'], fr['base']; RW = fr['rows']
rngs = lambda k: f'{(lo0 + .25 * k) * 100:.0f}–{(lo0 + .25 * (k + 1)) * 100:.0f}'
d0 = RW[0]['dist']; ks = sorted(((d0[20 + k], k) for k in range(-20, 21) if d0[20 + k] > 0), reverse=True)
(pA, kA), (pB, kB) = ks[0], ks[1]
mv = lambda k: ('hold ' if k == 0 else 'cut ' if k < 0 else 'hike ') + rngs(k)
word = lambda k: 'hold' if k == 0 else (f'cut {-25 * k}' if k < 0 else f'hike {25 * k}')
fed = [H_(CFD, f'◆ FED · {RW[0]["meeting"]:%d %b}'.upper(), f'{word(kA).upper()} {pA * 100:.0f}%', TX, NEU if kA == 0 else HOT),
       S_(CFD, f'now {rngs(0)}', 'odds', '1d'),
       R_(CFD, 'NEXT', mv(kA), f'{pA * 100:.0f}%', '—'), R_(CFD, '', mv(kB), f'{pB * 100:.0f}%', '—', vfg=MU)]
for j in (1, 2, 3):
    dj = RW[j]['dist']; k = int(np.argmax(dj)) - 20
    fed.append(R_(CFD, f'{RW[j]["meeting"]:%d %b}'.upper(), f'{rngs(k)} {dj.max() * 100:.0f}%', sgn(RW[j]['cum_bp']) + 'bp', '—'))
fed.append(R_(CFD, '5D', 'next mtg, 5 days', '—', ''))

x = bars5(T2 - pd.Timedelta(hours=6), now2)          # 8 Oct 18:00 → 9 Oct 15:00
n = len(x); fut = 24
fig = plt.figure(figsize=(FW_IN, 12.6), dpi=DPI, facecolor=BG)
ax = fig.add_axes([0.02, 0.40, 0.93, 0.53]); ax2 = fig.add_axes([0.02, 0.04, 0.93, 0.345])
lo, hi = x.Low.min(), x.High.max()
ax.set_xlim(-2, n + fut + 18); ax.set_ylim(lo - (hi - lo) * 0.62, hi + (hi - lo) * 0.18)
style(ax, x, 'NQ1! · 5 · CME   Vizard   ·   Fri 9 Oct 2026 · 15:00 ET · next FOMC Wed 28 Oct', every=3)
candles(ax, x)
draw_card(fig, tally_rows(T2, now2, pd.Timestamp('2026-10-04 18:00'), pd.Timestamp('2026-09-30 18:00')), 0.948, 0.925, 'tr')
draw_card(fig, fed, 0.948, 0.735, 'tr')
draw_card(fig, stages_rows(st2, False, False, ('IN 19D', '#ffffff', '#2b2f39')), 0.026, 0.405, 'bl')
# pane: the event clock (today's running range against normal days, the next event's median dashed, yesterday faded)
ax2.set_facecolor(BG); ax2.yaxis.tick_right(); ax2.tick_params(axis='y', colors=MU, labelsize=8); ax2.tick_params(axis='x', length=0)
for s_ in ax2.spines.values(): s_.set_visible(False)
ax2.grid(color='#1a1f2b', lw=0.6, zorder=0)
i0 = int(np.searchsorted(x.index, T2 - pd.Timedelta(hours=6)))
scP = A2
Rn, Rp = np.array(CK['NORMAL']['R']), np.array(CK['PRE']['R'])
xs_ = [i0 + 6 * j for j in range(47)]
q = lambda R, k: [0.0] + list(R[k] * scP)
ax2.fill_between(xs_, q(Rn, 0), q(Rn, 4), color=SUB, alpha=0.10, lw=0); ax2.fill_between(xs_, q(Rn, 1), q(Rn, 3), color=SUB, alpha=0.16, lw=0)
ax2.plot(xs_, q(Rn, 2), color=SUB, lw=2); ax2.text(xs_[-1] + 1, Rn[2][-1] * scP + 0.04 * max(Rn[4][-1], Rp[4][-1]) * scP, f'Normal median {Rn[2][-1] * scP:.0f}', color=SUB, fontsize=7.5, va='center')
ax2.plot(xs_, q(Rp, 2), color=GH, lw=1, ls='--', alpha=0.8); ax2.text(xs_[-1] + 1, Rp[2][-1] * scP - 0.06 * max(Rn[4][-1], Rp[4][-1]) * scP, f'FOMC D1 (next) {Rp[2][-1] * scP:.0f}', color=GH, fontsize=7.5, va='center')
yy = x.iloc[i0:]; rngT = (yy.High.cummax() - yy.Low.cummin()).values
j_now = (now2 - (T2 - pd.Timedelta(hours=6))).total_seconds() / 1800
q25, q75 = np.interp(j_now, range(1, 47), Rn[1]) * scP, np.interp(j_now, range(1, 47), Rn[3]) * scP
stB = 'Above' if rngT[-1] > q75 else 'Below' if rngT[-1] < q25 else 'Inside'
ax2.plot(range(i0, i0 + len(rngT)), rngT, color={'Above': HOT, 'Below': COLD, 'Inside': TX}[stB], lw=2.6, zorder=5)
yp = b[b.tday == T2 - pd.Timedelta(days=1)].set_index('ts').resample('5min').agg(dict(High='max', Low='min')).dropna()
rp = (yp.High.cummax() - yp.Low.cummin()).values
ax2.plot(range(i0 - len(rp), i0), rp, color=SUB, lw=1, alpha=0.3)
for hh in (14 * 60, 14 * 60 + 30):
    ax2.axvline(i0 + (hh + 360) / 5, color=GH, ls=':', lw=0.8, alpha=0.3)
ax2.set_xlim(ax.get_xlim()); ax2.set_ylim(0, max(Rn[4][-1], Rp[4][-1]) * scP * 1.75)
ticks = [i for i, t in enumerate(x.index) if t.minute == 0 and t.hour % 3 == 0]
ax2.set_xticks(ticks); ax2.set_xticklabels([x.index[i].strftime('%H:%M') for i in ticks], color=MU, fontsize=8)
ax2.text(0.004, 0.975, 'Vizard  ·  event clock + Fed map', transform=ax2.transAxes, color=SUB, fontsize=8.5, va='top', zorder=30)
# clock card (pane, top right)
jB = min(45, int(np.ceil((j_now * 30 + 5) / 30)) - 1); fB = ((j_now * 30 + 5) - 30 * jB) / 30
ckAt = lambda R, k: (R[k][jB - 1] if jB > 0 else 0) + (R[k][jB] - (R[k][jB - 1] if jB > 0 else 0)) * fB
q10, q25b, q50, q75b, q90 = [ckAt(Rn, k) for k in range(5)]
vA = rngT[-1] / scP
def pctQ(v):
    if v < q10: return 5
    if v <= q25b: return 10 + 15 * (v - q10) / (q25b - q10)
    if v <= q50: return 25 + 25 * (v - q25b) / (q50 - q25b)
    if v <= q75b: return 50 + 25 * (v - q50) / (q75b - q50)
    if v <= q90: return 75 + 15 * (v - q75b) / (q90 - q75b)
    return 95
pcq = pctQ(vA); sh = (CK['NORMAL']['share'][jB - 1] + (CK['NORMAL']['share'][jB] - CK['NORMAL']['share'][jB - 1]) * fB)
dP = np.diff([0] + list(Rp[2])); bj = int(np.argmax(dP)); dN = np.diff([0] + list(Rn[2]))[bj]
hh_ = lambda j: f'{(18 * 60 + 30 * (j + 1)) // 60 % 24:02d}:{(30 * (j + 1)) % 60:02d}'
pillc = {'Above': ('▲ ABOVE', '#ffffff', HOT), 'Below': ('▼ BELOW', '#ffffff', COLD), 'Inside': ('● INSIDE', TX, NEU)}[stB]
clk = [H_(GH, '◆ VIZARD · CLOCK · 15:00 ET', 'NORMAL', '#ffffff', '#2b2f39'),
       R_(GH, 'NOW', f'range {rngT[-1]:.2f} pts', x2(vA), pill=pillc),
       R_(GH, 'vs Normal', f'{meter(pcq)} ≈P{pcq:.0f}', f'typ {x2(q50)}', ''),
       R_(GH, 'DONE', f'{gauge(sh)} {pc(sh)}', f'→ {rngT[-1] / sh:.0f}', 'pts'),
       R_(GH, 'BUSIEST', f'{hh_(bj - 1)}–{hh_(bj)}', f'+{x2(dP[bj])}', f'norm +{x2(dN)}', vfg=TX)]
pb = ax2.get_position()
draw_card(fig, clk, pb.x1 - 0.002, pb.y1 - 0.005, 'tr')
# the Fed map table (pane, top left)
def draw_map(fig, x0, y0, fs=8.0, RH=0.0215):
    cw = fs * 0.602 / 72 * DPI / (FW_IN * DPI)
    nc = len(RW); dist = np.array([r['dist'] for r in RW])
    xs = [k for k in range(41) if dist[:, k].max() * 100 >= 3.0]; xHi, xLo = max(xs + [20]), min(xs + [20]); xLo = max(xLo, xHi - 9)
    title = f'FED MAP · {RW[0]["meeting"]:%d %b} {word(kA)} {pA * 100:.0f}% · now {rngs(0)}'.upper().replace('NOW', 'now')
    rows = [[f'{rngs(k - 20)}' + (' ◀' if k == 20 else '  ') for k in range(xHi, xLo - 1, -1)]]
    W0 = max(len('vs DOTS'), max(len(s_) for s_ in rows[0])) + 1.6
    Wc = 6 + 1.6
    CW = [W0 * cw] + [Wc * cw] * nc
    if len(title) * cw + 1.6 * cw > sum(CW): CW[0] += len(title) * cw + 1.6 * cw - sum(CW)
    def cell(c0, c1, yy, txt, fg, bg, bold=False):
        xa = x0 + sum(CW[:c0]); ww = sum(CW[c0:c1 + 1])
        fig.add_artist(Rectangle((xa, yy - RH), ww, RH, transform=fig.transFigure, fc=bg, ec=BG, lw=0.8, zorder=20))
        if txt: fig.text(xa + ww / 2, yy - RH / 2, txt, color=fg, fontsize=fs, family=MONO, weight='bold' if bold else 'normal', ha='center', va='center', zorder=21)
    y = y0
    cell(0, nc, y, title, '#ffffff', MAPH, True); y -= RH
    cell(0, 0, y, 'RANGE', MU, BODY2)
    for j, r in enumerate(RW): cell(j + 1, j + 1, y, f'{r["meeting"]:%d %b}'.upper(), TX, BODY2, True)
    y -= RH
    import matplotlib.colors as mc
    hi_, lo_ = np.array(mc.to_rgb(HTHI)), np.array(mc.to_rgb(HTLO))
    for k in range(xHi, xLo - 1, -1):
        cur = k == 20
        cell(0, 0, y, rngs(k - 20) + (' ◀' if cur else '  '), MAPC if cur else TX, BODY2, cur)
        for j in range(nc):
            p = dist[j, k]; bx = dist[j, xLo:xHi + 1].max()
            if p >= 0.005:
                t = min(1, p / 0.7); bg = mc.to_hex(lo_ + (hi_ - lo_) * t)
                cell(j + 1, j + 1, y, f'{100 * p:.0f}', '#ffffff' if p >= 0.45 else TX, bg, p == bx)
            else:
                cell(j + 1, j + 1, y, '·', MU, BODY)
        y -= RH
    sep = {2026: 4.125, 2027: 4.125, 2028: 3.875}
    lab = ['EXP bp', 'Δ 1D', 'Δ 5D', 'vs DOTS']
    for li, L in enumerate(lab):
        cell(0, 0, y, L, MU, BODY2)
        for j, r in enumerate(RW):
            if li == 0: t, fg, bg, bd = sgn(r['cum_bp']), TX, BODY2, True
            elif li < 3: t, fg, bg, bd = '—', MU, BODY, False
            else:
                eoy = (RW[j + 1]['meeting'].year != r['meeting'].year) if j < nc - 1 else r['meeting'].month == 12
                t = sgn(100 * (r['end'] - sep[r['meeting'].year])) if eoy else ''; fg, bg, bd = TX, BODY, False
            cell(j + 1, j + 1, y, t, fg, bg, bd)
        y -= RH
draw_map(fig, pb.x0 + 0.004, pb.y1 - 0.03)
fig.text(0.02, 0.968, 'Vizard rebuilt · a normal day: three cards in their own corners; in the pane the event clock and the Fed map share the space', color=TX, fontsize=12.5, weight='bold')
fig.text(0.02, 0.948, 'NQ 1-minute data to 15:00 ET Fri 9 Oct. Fed card and Fed map: CME\'s ZQ prices of Mon 12 Oct (one snapshot, so the 1-day and 5-day changes show —). DXY futures file ends Jul 2026, so DXY 4W shows —.', color=MU, fontsize=8.5)
plt.savefig(sys.argv[2], dpi=DPI, facecolor=BG); plt.close(fig)
print(sys.argv[2], dict(p=round(st2['p'], 3), m=round(st2['m'], 2), d=round(st2['d'], 2), s=round(st2['s'], 2), A=A2, stB=stB, vA=round(vA, 2), pcq=round(pcq), q50=round(q50, 2)))

# ════════════════ 3) Mobile, FOMC day 29 Jul 15:30
FW_IN = 9.0
fig = plt.figure(figsize=(FW_IN, 11.0), dpi=DPI, facecolor=BG)
x = bars5(T + pd.Timedelta(hours=9), st['now'])
ax = fig.add_axes([0.03, 0.04, 0.86, 0.86])
lo, hi = x.Low.min(), x.High.max()
ax.set_xlim(-2, len(x) + 14); ax.set_ylim(lo - (hi - lo) * 1.05, hi + (hi - lo) * 0.85)
style(ax, x, 'NQ1! · 5 · Wed 29 Jul 2026 · 15:30 ET · Layout = Mobile', every=2)
chart_fomc(ax, st, x)
g = st['g']; tdO, gH, gL = float(g.Open.iloc[0]), g.High[g.index <= st['now']].max(), g.Low[g.index <= st['now']].min()
Rf = np.array(CK['FOMC']['R']); jn = (st['now'] - (T - pd.Timedelta(hours=6))).total_seconds() / 1800
vA = (gH - gL) / st['A']; q25, q75 = np.interp(jn, range(1, 47), Rf[1]), np.interp(jn, range(1, 47), Rf[3])
sB = 'ABOVE' if vA > q75 else 'BELOW' if vA < q25 else 'INSIDE'
clockrow = R_(GH, 'NOW', f'range {gH - gL:.0f}', x2(vA), '', pill=(sB, '#ffffff' if sB != 'INSIDE' else TX, HOT if sB == 'ABOVE' else COLD if sB == 'BELOW' else NEU))
draw_card(fig, tally_rows(T, st['now'], pd.Timestamp('2026-07-26 18:00'), pd.Timestamp('2026-06-30 18:00'), True, clockrow), 0.885, 0.895, 'tr', fs=7.6, RH=0.022)
draw_card(fig, stages_rows(st, True, True, ('TODAY', GH, '#ffffff'), True), 0.04, 0.045, 'bl', fs=7.6, RH=0.022)
fig.text(0.03, 0.962, 'Vizard rebuilt · Mobile: tally (top) and stages (bottom), each its own card', color=TX, fontsize=11.5, weight='bold')
fig.text(0.03, 0.943, 'Fed row (own corner) left out: no ZQ prices for this date. Full wording sits in the tooltips.', color=MU, fontsize=8)
plt.savefig(sys.argv[3], dpi=DPI, facecolor=BG); plt.close(fig); print(sys.argv[3])
