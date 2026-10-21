import pandas as pd, numpy as np, json, sys
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from events import FOMC, CPI, NFP
DAY = pd.Timestamp(sys.argv[1]); CUT = sys.argv[2]; AN = 'TD'
T = pd.Timestamp(f'{DAY.date()} {CUT}')
b = pd.read_pickle('/home/claude/t3/bars_NQ_all.pkl'); b['mod'] = b.ts.dt.hour * 60 + b.ts.dt.minute
x = b[(b.tday == DAY) & (b.ts <= T)].reset_index(drop=True)
D = pd.read_pickle('days_NQ.pkl'); row = D[(D.anchor == AN) & (D.tday == DAY)].iloc[0]; adr = row.adr
TYPES = ['FOMC', 'NFP', 'CPI', 'POST', 'PRE', 'HOLLOW', 'NORMAL']
ST = [list(map(float, r.split(','))) for r in json.load(open('stats_rows.json'))['rows']['NQ_TD'].split(';')]
ty = TYPES.index(row.type); s = ST[ty]; sn = ST[6]
O = x.Open.iloc[0]; H = x.High.max(); L = x.Low.min(); C = x.Close.iloc[-1]
prev = b[(b.tday < DAY)]; pday = prev.tday.max(); pv = prev[prev.tday == pday]
rthC = pv[(pv['mod'] >= 570) & (pv['mod'] < 975)].Close.iloc[-1]; rth2C = pv[(pv['mod'] >= 570) & (pv['mod'] < 1020)].Close.iloc[-1]
o930 = x[x['mod'] == 570].Open.iloc[0]; ce1 = (rthC + o930) / 2; ce2 = (rth2C + o930) / 2
hr = x[x.ts >= T.floor('h')]; wk = b[(b.ts >= (DAY - pd.Timedelta(days=DAY.dayofweek)) - pd.Timedelta(hours=6)) & (b.ts <= T)]
bg = '#131722'; fg = '#d1d4dc'; gh = '#b388ff'; wkc = '#787b86'
fig, ax = plt.subplots(figsize=(19.2, 10.0), dpi=100); fig.patch.set_facecolor(bg); ax.set_facecolor(bg)
xs = x[x.ts >= T - pd.Timedelta(hours=7)].reset_index(drop=True); N = len(xs)
for i, r in xs.iterrows():
    col = '#089981' if r.Close >= r.Open else '#f23645'
    ax.plot([i, i], [r.Low, r.High], color=col, lw=0.6); ax.add_patch(Rectangle((i - 0.35, min(r.Open, r.Close)), 0.7, max(abs(r.Close - r.Open), 0.25), color=col, lw=0))
off, wid, gap = 12, 18, 9
def cand(x0, o, h, l, c, name, colu='#4caf50', cold='#2a2e39'):
    ax.plot([x0 + wid / 2] * 2, [l, h], color=wkc, lw=1)
    ax.add_patch(Rectangle((x0, min(o, c)), wid, max(abs(c - o), 0.5), facecolor=colu if c >= o else cold, edgecolor=wkc, lw=1))
    ax.text(x0 + wid / 2, l, name, color='#9aa3b5', fontsize=8, ha='center', va='top')
    for y, cc in ((h, '#9aa3b5'), (l, '#9aa3b5'), (o, '#5d6476')): ax.text(x0 + wid + 1, y, f'{y:,.2f}', color=cc, fontsize=7.5, va='center')
x0 = N + off; xg = x0 + wid + gap
cand(x0, O, H, L, C, 'DAY ' + DAY.strftime('%d %b'))
for y, a in ((O, .7), (H, .5), (L, .5)): ax.plot([-0.5, x0], [y, y], color=wkc, ls=':', lw=0.8, alpha=a)
hp = lambda q: O * (1 + q * adr); lp = lambda q: O * (1 - q * adr)
ax.add_patch(Rectangle((xg, hp(s[2])), wid, hp(s[4]) - hp(s[2]), facecolor=gh, alpha=0.15, edgecolor=gh, lw=0.8))
ax.add_patch(Rectangle((xg, lp(s[7])), wid, lp(s[5]) - lp(s[7]), facecolor=gh, alpha=0.15, edgecolor=gh, lw=0.8))
ax.plot([xg + wid / 2] * 2, [lp(s[6]), hp(s[3])], color=gh, ls=':', lw=2)
for y in (hp(s[3]), lp(s[6])): ax.plot([xg + 1, xg + wid - 1], [y, y], color=gh, lw=2); ax.text(xg + wid + 1, y, f'{y:,.2f}', color=gh, fontsize=7.5, va='center'); ax.plot([-0.5, xg], [y, y], color=gh, ls=':', lw=0.8, alpha=0.55)
ax.plot([xg, xg + wid], [O, O], color=gh, lw=2)
ax.text(xg + wid / 2, hp(s[4]), row.type if row.type != 'POST' else 'FOMC +1', color=gh, fontsize=10, ha='center', va='bottom')
for y, nm, al in ((ce1, 'CE1', 1), (ce2, 'CE2', .65)):
    ax.plot([xg - 1, xg + wid + 1], [y, y], color='#ffb300', ls='--', lw=1, alpha=al); ax.text(xg - 1.5, y, nm, color='#ffb300', fontsize=7, ha='right', va='center', alpha=al)
xh = xg + wid + 2 * gap
cand(xh, hr.Open.iloc[0], hr.High.max(), hr.Low.min(), hr.Close.iloc[-1], '1H'); xh += wid + gap
cand(xh, wk.Open.iloc[0], wk.High.max(), wk.Low.min(), wk.Close.iloc[-1], 'W')
ax.set_xlim(-2, xh + wid + 30)
lo_ = min(xs.Low.min(), lp(s[7]), wk.Low.min()); hi_ = max(xs.High.max(), hp(s[4]), wk.High.max()); pad = (hi_ - lo_) * 0.05
ax.set_ylim(lo_ - pad, hi_ + pad)
tk = list(range(0, N, 60)); ax.set_xticks(tk); ax.set_xticklabels([xs.ts.iloc[i].strftime('%H:%M') for i in tk], color=fg, fontsize=9)
ax.tick_params(colors=fg); [s_.set_color('#2a2e39') for s_ in ax.spines.values()]; ax.grid(color='#1e222d', lw=0.6); ax.yaxis.tick_right()
r_now = (H - L) / O / adr; uu = (H - O) / O / adr / s[3]; vv = (O - L) / O / adr / s[6]
bk = ['18–00', '00–02', '02–07', '07–09:30', '09:30–12', '12–17']
iH = int(np.argmax([s[12 + i] - sn[12 + i] for i in range(6)])); iL = int(np.argmax([s[18 + i] - sn[18 + i] for i in range(6)]))
names = {'FOMC': 'FOMC 14:00 · M9 Vizard', 'NFP': 'NFP 08:30 · M6 Cero', 'CPI': 'CPI 08:30 · M7/8 Gran Rey Cero', 'POST': 'Day after FOMC · M12 Full Bringer', 'PRE': 'FOMC day 1 · M10 Pesquisa', 'HOLLOW': 'NFP week · M11 Hollow', 'NORMAL': 'No tier-1 release'}
rows = [('◆ HUECO MUNDO   NQ   trading day ' + DAY.strftime('%a %d %b'), ''), ('today', names[row.type]),
        ('range', f'typical {s[10]:.2f}× ADR ({s[9]:.2f}×–{s[11]:.2f}×) · normal {sn[10]:.2f}×'),
        ('so far', f'{r_now:.2f}× ADR · reach used ▲{uu*100:.0f}% ▼{vv*100:.0f}%'),
        ('timing', f'high {bk[iH]} {s[12+iH]*100:.0f}% (normal {sn[12+iH]*100:.0f}%) · low {bk[iL]} {s[18+iL]*100:.0f}% ({sn[18+iL]*100:.0f}%)'),
        ('up-close', f'{s[1]*100:.0f}% of {int(s[0])} days · normal {sn[1]*100:.0f}%'), ('next', 'NFP 08:30 · Fri 02 Oct · in 16d'), ('', 'CPI 08:30 · Wed 14 Oct · in 28d'), ('', 'FOMC 14:00 · Wed 28 Oct · in 42d'),
        ('model', 'hover for notes'), ('dates loaded to 10 Dec 2027 · update once a year', '')]
y0 = 0.36
for i, (a_, b_) in enumerate(rows):
    yy = y0 - i * 0.024
    fig.text(0.03, yy, a_, color='#e6e9ef' if i == 0 else '#9aa3b5', fontsize=9, family='DejaVu Sans Mono', va='top', bbox=dict(fc='#171c28' if i == 0 else '#0e1117', ec='#262c3a', pad=2))
    fig.text(0.08, yy, b_, color='#e6e9ef', fontsize=9, family='DejaVu Sans Mono', va='top')
ax.set_title(f'Hueco Mundo mock · NQ 1m · {DAY.date()} at {CUT} ET · {row.type} · ADR20 {adr*100:.2f}% ({adr*O:,.0f} pts)', color=fg, fontsize=11, loc='left')
plt.tight_layout(); plt.savefig(f'mock_hm_{DAY.date()}.png', facecolor=bg); print('ok', row.type, adr, r_now, uu, vv)
