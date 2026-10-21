"""Mocks of Vizard's FOMC stages on NQ1! 5-minute.
  1) FOMC day, Wed 17 Jun 2026 at 15:30 ET (stage 2 running): week open, 14:00 / 14:30 opens extended, the two fixed
     snapshots, the RTH gap in eighths over NY AM, and the stages card (Full layout) at the bottom right.
  2) The day after, Thu 18 Jun 2026 at 11:00 ET: its own gap in eighths with the open-side quarter, and the card rows
     for the day after.
Card values are computed the way the script computes them: records from rec_NQ.pkl before the day, 3-year averages at
today's 09:30 open, live values from the 1-minute data, DXY from the DXY futures 5-minute file, rates from fomc_stats.json.
  python3 mock_stages.py out_day.png out_after.png"""
import sys, json, numpy as np, pandas as pd, matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
plt.rcParams['font.family'] = 'DejaVu Sans'
MONO = 'DejaVu Sans Mono'
BG, BODY, BODY2, NEU = '#0e1117', '#161a23', '#1c2130', '#3a3f4b'
TX, SUB, MU = '#e6e9ef', '#9aa3b5', '#5d6476'
HOT, OK, PREM, DISC = '#ff8a65', '#66bb6a', '#ef5350', '#66bb6a'
GH, LVL, DXC, OQ = '#ab47bc', '#ffb300', '#00897b', '#26a69a'
UPC, DNC = '#089981', '#f23645'
J = json.load(open('fomc_stats.json')); RS, DX = J['res']['NQ'], J['dxy']['NQ']
pc = lambda x: f'{100 * x:.0f}%'
sg = lambda v: '—' if v is None or np.isnan(v) else ('+' if v >= 0 else '−') + f'{abs(v):g}'
ar = lambda v: '·' if v == 0 or np.isnan(v) else ('▲' if v > 0 else '▼')
gauge = lambda f: '█' * int(round(min(1, max(0, f)) * 10)) + '░' * (10 - int(round(min(1, max(0, f)) * 10)))

b = pd.read_pickle('/home/claude/t3/bars_NQ_all.pkl')
T = pd.read_pickle('rth_NQ.pkl')
REC = pd.read_pickle('rec_NQ.pkl')
fx = pd.read_csv('/mnt/user-data/uploads/DXY_2023_2026_5min_continuous.csv'); fx['ts'] = pd.to_datetime(fx.Date + ' ' + fx.Time) + pd.Timedelta(hours=1)
fx = fx.sort_values('ts').set_index('ts')
D, D1 = pd.Timestamp('2026-06-17'), pd.Timestamp('2026-06-18')
at = lambda d, h, m: d + pd.Timedelta(hours=h, minutes=m)
m1 = b.set_index('ts')
px = lambda t, col='Close': float(m1.loc[t, col])
dx_at = lambda t: float(fx.Close[fx.index <= t].iloc[-1])           # DXY close of the last 5-minute bar at or before t

# ── state on 17 Jun at 15:30 (bar 15:29 closed)
now = at(D, 15, 29)
r = T.loc[D]; rthO, pcl = r.o930, r.pc
s14O, s1C, s30O = r.o1400, r.c1429, r.o1430
cl = px(now)
sv1, sv2, svR = s1C - s14O, cl - s30O, cl - rthO
wk0 = pd.Timestamp('2026-06-14 18:00'); wkOp = px(wk0, 'Open')
x14, x1C = dx_at(at(D, 13, 55)), dx_at(at(D, 14, 25)); xN = dx_at(at(D, 15, 25))
dxTdO = dx_at(pd.Timestamp('2026-06-16 17:55'))
tdO = px(pd.Timestamp('2026-06-16 18:00'), 'Open')
dv1, dv2, dvD, nqD = (x1C / x14 - 1) * 100, (xN / x1C - 1) * 100, (xN / dxTdO - 1) * 100, cl - tdO
day = m1[(m1.index >= at(D, 9, 30)) & (m1.index <= now)]
gfT = day[day.Low <= pcl].index.min() if pcl < rthO else day[day.High >= pcl].index.min()
R = REC[REC.index < D].iloc[::-1]
N = 12; L = R.iloc[:N]
seq = lambda col: ''.join(ar(v) for v in L[col].iloc[::-1])
cnt = lambda col: (int((L[col] > 0).sum()), int((L[col] < 0).sum()))
R3 = R[R.index >= D - pd.DateOffset(years=3)]
av = {k: float((R3[k].abs() / R3.o930).mean() * rthO) for k in ('s1', 's2', 'rth')}
avN = float((R3.amN.abs() / R3.o930).dropna().mean() * rthO)
nwX = abs(sv2) / av['s2']
def xs(d, n):
    return f" · today DXY {ar(d)}{abs(d):.2f}% NQ {ar(n)} " + ('⇄' if np.sign(d) != np.sign(n) else '⇉')
held = lambda key, src=RS: src[key]['held']
V = lambda key, src=RS: pc(src[key]['all']['p']); VB = lambda key, src=RS: pc(src[key]['all']['pb'])
rows = [
    ('head', '◆ VIZARD · FOMC STAGES · NQ1!', 'FOMC TODAY'),
    ('sub', f'last {N} FOMC days · oldest → newest', 'today', '3y avg'),
    (GH, '14:00', False, seq('s1') + '  ▲%d ▼%d' % cnt('s1'), sg(sv1), f'±{av["s1"]:.2f}', UPC if sv1 >= 0 else DNC),
    (GH, '14:30', False, seq('s2') + '  ▲%d ▼%d' % cnt('s2'), sg(sv2), f'±{av["s2"]:.2f}', UPC if sv2 >= 0 else DNC),
    (GH, 'RTH', False, seq('rth') + '  ▲%d ▼%d' % cnt('rth'), sg(svR), f'±{av["rth"]:.2f}', UPC if svR >= 0 else DNC),
    (GH, 'NOW', False, gauge(nwX) + ' stage 2', f'{nwX:.2f}×', 'of avg', HOT if nwX >= 1 else TX),
    ('sub', '2018–26 · green key = held in both halves', 'FOMC', 'other / exp'),
    (GH, 'AM=S1', False, f"next NY AM went with stage 1 · idx {RS['nx_s1']['index']:.0f}", V('nx_s1'), 'exp ' + pc(RS['nx_s1']['expected']), TX),
    (GH, 'AM=S2', False, f"next NY AM went with stage 2 · idx {RS['nx_s2']['index']:.0f}", V('nx_s2'), 'exp ' + pc(RS['nx_s2']['expected']), TX),
    (GH, 'GAP', held('gap_fill'), f'morning gap filled by 16:14 · today filled {gfT:%H:%M}', V('gap_fill'), VB('gap_fill'), TX),
    (GH, '¼ +1', held('nx_q'), 'day after: NY AM held the open-side ¼', V('nx_q'), VB('nx_q'), TX),
    (GH, '50% +1', held('nx_ce'), 'day after: NY AM tapped the gap 50%', V('nx_ce'), VB('nx_ce'), TX),
    (DXC, '⇄ 14:00', held('s1', DX), 'stage 1 other way to DXY' + xs(dv1, sv1), V('s1', DX), VB('s1', DX), TX),
    (DXC, '⇄ 14:30', held('s2', DX), 'stage 2 other way to DXY' + xs(dv2, sv2), V('s2', DX), VB('s2', DX), TX),
    (DXC, '⇄ DAY', held('day', DX), 'trading day other way to DXY' + xs(dvD, nqD), V('day', DX), VB('day', DX), TX),
]
print('17 Jun:', dict(sv1=sv1, sv2=sv2, svR=svR, av=av, nwX=round(nwX, 2), gfT=str(gfT), dv1=round(dv1, 3), dv2=round(dv2, 3), dvD=round(dvD, 3), nqD=nqD, wkOp=wkOp))


def card(fig, rows, X0, Y0, COLW, RH=0.026, fs=8.0):
    def cell(xa, y, w, txt, fg, bg, bold=False, ha='left'):
        fig.add_artist(Rectangle((xa, y - RH), w, RH, transform=fig.transFigure, fc=bg, ec=BG, lw=0.6))
        if txt:
            fig.text(xa + (0.004 if ha == 'left' else w / 2), y - RH / 2, txt, color=fg, fontsize=fs, family=MONO, weight='bold' if bold else 'normal', ha=ha, va='center')
    y = Y0
    for rw in rows:
        xa = X0
        if rw[0] == 'head':
            cell(xa, y, COLW[0], '', None, GH); cell(xa + COLW[0], y, sum(COLW[1:4]), rw[1], '#ffffff', GH, True)
            cell(xa + sum(COLW[:4]), y, COLW[4], rw[2], GH, '#ffffff', True, 'center')
        elif rw[0] == 'sub':
            cell(xa, y, COLW[0], '', None, GH); cell(xa + COLW[0], y, COLW[1], '', MU, BODY2)
            cell(xa + sum(COLW[:2]), y, COLW[2], rw[1], MU, BODY2); cell(xa + sum(COLW[:3]), y, COLW[3], rw[2], MU, BODY2, False, 'center')
            cell(xa + sum(COLW[:4]), y, COLW[4], rw[3], MU, BODY2, False, 'center')
        else:
            col, key, h, lab, v, side, vfg = rw
            cell(xa, y, COLW[0], '', None, col)
            cell(xa + COLW[0], y, COLW[1], key, '#ffffff' if h else MU, OK if h else BODY, h, 'center')
            cell(xa + sum(COLW[:2]), y, COLW[2], lab, TX, BODY)
            cell(xa + sum(COLW[:3]), y, COLW[3], v, vfg, BODY, True, 'center')
            cell(xa + sum(COLW[:4]), y, COLW[4], side, MU, BODY, False, 'center')
        y -= RH
    return y


def candles(ax, x):
    for i, (t, r_) in enumerate(x.iterrows()):
        c = UPC if r_.Close >= r_.Open else DNC
        ax.plot([i, i], [r_.Low, r_.High], color=c, lw=0.8, zorder=3)
        ax.add_patch(Rectangle((i - .35, min(r_.Open, r_.Close)), .7, max(abs(r_.Close - r_.Open), 0.5), fc=c, ec=c, lw=0.4, zorder=4))


def style(ax, x, lo, hi, title):
    ax.set_facecolor(BG); ax.yaxis.tick_right(); ax.tick_params(axis='y', colors=MU, labelsize=8); ax.tick_params(axis='x', length=0)
    for s_ in ax.spines.values(): s_.set_visible(False)
    ax.grid(color='#1a1f2b', lw=0.6, zorder=0)
    ticks = [i for i, t in enumerate(x.index) if t.minute == 0 and t.hour % 1 == 0 and t.hour % 2 == 0]
    ax.set_xticks(ticks); ax.set_xticklabels([x.index[i].strftime('%H:%M') for i in ticks], color=MU, fontsize=8)
    ax.text(0.005, 0.985, title, transform=ax.transAxes, color=SUB, fontsize=9, va='top')


def gap_octants(ax, iA, iB, pcl, o, oq_label=True):
    gp = o - pcl
    for k in range(9):
        y = pcl + gp * k / 8
        ax.plot([iA, iB], [y, y], color=LVL if k == 4 else (OQ if k >= 6 else LVL), lw=2 if k == 4 else 0.9,
                ls='--' if k == 4 else ':', alpha=1 if k in (4, 6, 8) else (0.7 if k == 0 else 0.45), zorder=2)
    ax.fill_between([iA, iB], pcl + gp * 6 / 8, pcl + gp, color=OQ, alpha=0.22, lw=0, zorder=1)
    ax.text(iB + 0.5, pcl + gp * 0.875, 'open-side ¼', color=OQ, fontsize=7.5, va='center')
    ax.text(iB + 0.5, pcl + gp * 0.5, 'gap 50%', color=LVL, fontsize=7.5, va='center')


# ════════ 1) FOMC day
x = m1[(m1.index >= at(D, 6, 0)) & (m1.index <= now)].resample('5min').agg(dict(Open='first', High='max', Low='min', Close='last')).dropna()
idx = lambda t: int(np.searchsorted(x.index, t))
fig = plt.figure(figsize=(18, 10.5), dpi=100, facecolor=BG)
ax = fig.add_axes([0.02, 0.06, 0.93, 0.84])
n = len(x); XR = n + 120
lo, hi = min(x.Low.min(), pcl, wkOp), max(x.High.max(), wkOp)
ax.set_xlim(-2, XR); ax.set_ylim(lo - (hi - lo) * 0.85, hi + (hi - lo) * 0.18)
style(ax, x, lo, hi, 'NQ1! · 5 · CME   Vizard   ·   Wed 17 Jun 2026 · FOMC decision day · 15:30 ET')
i930, i1100, i1400, i1430 = idx(at(D, 9, 30)), idx(at(D, 11, 0)), idx(at(D, 14, 0)), idx(at(D, 14, 30))
ax.axvspan(i930 - .5, i1100 - .5, color=OQ, alpha=0.06, lw=0)
ax.axvspan(i1400 - .5, i1430 - .5, color='#2962ff', alpha=0.10, lw=0); ax.axvspan(i1430 - .5, n + 9, color='#2962ff', alpha=0.06, lw=0)
gap_octants(ax, i930, i1100, pcl, rthO)
candles(ax, x)
xd = n + 24
ax.plot([0, xd], [wkOp, wkOp], color=LVL, lw=1, ls='--', alpha=0.85); ax.text(n + 2, wkOp, f' week open {wkOp:.2f}', color=LVL, fontsize=7.5, va='bottom')
ax.plot([i1400, xd], [s14O, s14O], color=GH, lw=1.1); ax.text(n + 2, s14O, f' 14:00 open {s14O:.2f}', color=GH, fontsize=7.5, va='bottom')
ax.plot([i1430, xd], [s30O, s30O], color=GH, lw=1, ls='--', alpha=0.75); ax.text(n + 2, s30O, f' 14:30 open {s30O:.2f}', color=GH, fontsize=7.5, va='top', alpha=0.85)
ax.text(i1400 - 1.2, s14O, f'14:00\n{sg(s14O - rthO)} vs 09:30\n{sg(s14O - wkOp)} vs week open', color='#ffffff', fontsize=7.2, ha='right', va='center',
        bbox=dict(boxstyle='round,pad=0.35', fc=GH, ec='none', alpha=0.75))
for ii, txt, al in [(i1430, f'14:30 · S1 {sg(sv1)}\n{sg(s30O - rthO)} vs 09:30\n{sg(s30O - wkOp)} vs week open', 0.55)]:
    yl = x.Low.iloc[ii] - (hi - lo) * 0.03
    ax.annotate(txt, xy=(ii, x.Low.iloc[ii]), xytext=(ii, yl), color='#ffffff', fontsize=7.2, ha='center', va='top',
                bbox=dict(boxstyle='round,pad=0.35', fc=GH, ec='none', alpha=al), arrowprops=dict(arrowstyle='-', color=GH, lw=0.8))
ax.text(i1400, hi + (hi - lo) * 0.1, 'statement', color=GH, fontsize=7.5, ha='center'); ax.text(i1430 + 6, hi + (hi - lo) * 0.1, 'press conf.', color=GH, fontsize=7.5)
COLW = [0.004, 0.045, 0.29, 0.05, 0.055]
X0 = 0.95 - sum(COLW) - 0.01
yb = card(fig, rows, X0, 0.06 + 0.026 * len(rows) + 0.012, COLW)
fig.text(0.02, 0.955, 'Vizard · FOMC stages (new): week open · 14:00 / 14:30 opens · fixed snapshots · RTH gap in eighths over NY AM · stages card', color=TX, fontsize=12.5, weight='bold')
fig.text(0.02, 0.93, 'Values computed from NQ 1-minute data and DXY futures as of 15:30 ET; the event and Fed cards (top right) are left out of the mock; no PO3 candles in Vizard. TradingView rendering will differ.', color=MU, fontsize=8.5)
plt.savefig(sys.argv[1], dpi=100, facecolor=BG); plt.close(fig); print(sys.argv[1])

# ════════ 2) the day after, 11:00
now1 = at(D1, 10, 59)
r1 = T.loc[D1]; o1, pc1 = r1.o930, r1.pc; g1 = o1 - pc1
x = m1[(m1.index >= at(D1, 7, 0)) & (m1.index <= now1)].resample('5min').agg(dict(Open='first', High='max', Low='min', Close='last')).dropna()
idx = lambda t: int(np.searchsorted(x.index, t))
am = m1[(m1.index >= at(D1, 9, 30)) & (m1.index <= now1)]
q75, ce = pc1 + 0.75 * g1, pc1 + 0.5 * g1
qbT = am[am.Low <= q75].index.min() if g1 > 0 else am[am.High >= q75].index.min()
ceT = am[am.Low <= ce].index.min() if g1 > 0 else am[am.High >= ce].index.min()
amNw = float(am.Close.iloc[-1]) - o1
yS1, yS2 = REC.loc[D].s1, REC.loc[D].s2
print('18 Jun:', dict(gap=g1, q75=q75, ce=ce, qbT=str(qbT), ceT=str(ceT), amNw=amNw))
fig = plt.figure(figsize=(15, 8.4), dpi=100, facecolor=BG)
ax = fig.add_axes([0.02, 0.07, 0.93, 0.82])
n = len(x); lo, hi = min(x.Low.min(), pc1), x.High.max()
ax.set_xlim(-2, n + 70); ax.set_ylim(lo - (hi - lo) * 0.62, hi + (hi - lo) * 0.12)
style(ax, x, lo, hi, 'NQ1! · 5 · CME   Vizard   ·   Thu 18 Jun 2026 · the day after FOMC · 11:00 ET')
i930, i1100 = idx(at(D1, 9, 30)), idx(at(D1, 11, 0))
ax.axvspan(i930 - .5, i1100 - .5, color=OQ, alpha=0.06, lw=0)
gap_octants(ax, i930, i1100, pc1, o1)
candles(ax, x)
ax.text(1, pc1, f'prior 16:14 close {pc1:.2f}', color=LVL, fontsize=7.5, va='bottom', alpha=0.8)
rows2 = [('head', '◆ VIZARD · FOMC STAGES · NQ1!', 'DAY AFTER'),
         (GH, 'AM=S1', False, f"next NY AM went with stage 1 · idx {RS['nx_s1']['index']:.0f} · today {ar(amNw)} " + ('with' if np.sign(amNw) == np.sign(yS1) else 'against'), V('nx_s1'), 'exp ' + pc(RS['nx_s1']['expected']), TX),
         (GH, 'AM=S2', False, f"next NY AM went with stage 2 · idx {RS['nx_s2']['index']:.0f} · today {ar(amNw)} " + ('with' if np.sign(amNw) == np.sign(yS2) else 'against'), V('nx_s2'), 'exp ' + pc(RS['nx_s2']['expected']), TX),
         (GH, '¼ +1', held('nx_q'), 'day after: NY AM held the open-side ¼' + (f' · today broke {qbT:%H:%M}' if pd.notna(qbT) else ' · today held ✓'), V('nx_q'), VB('nx_q'), TX),
         (GH, '50% +1', held('nx_ce'), 'day after: NY AM tapped the gap 50%' + (f' · today tapped {ceT:%H:%M}' if pd.notna(ceT) else ' · today missed ✓'), V('nx_ce'), VB('nx_ce'), TX)]
COLW = [0.005, 0.055, 0.34, 0.06, 0.065]
card(fig, rows2, 0.95 - sum(COLW) - 0.012, 0.07 + 0.03 * 5 + 0.02, COLW, RH=0.03, fs=8.4)
fig.text(0.02, 0.955, 'Vizard · the day after FOMC: its RTH gap in eighths over NY AM, open-side quarter shaded, and the day-after rows (excerpt of the stages card)', color=TX, fontsize=12, weight='bold')
fig.text(0.02, 0.93, 'Gap up 18 Jun: the open-side quarter is the top quarter (next to the 09:30 open). Values from NQ 1-minute data at 11:00 ET.', color=MU, fontsize=8.5)
plt.savefig(sys.argv[2], dpi=100, facecolor=BG); print(sys.argv[2])
