"""Garganta (RTH gaps) mocks from NQ 1-minute data, Fri 9 Oct 2026 at 11:00 ET, computed the way Garganta_RTH_Gaps.pine does.
(A) NQ1! 15-minute, 21 Sep → 9 Oct: the last 20 RTH gaps running right, the staircase (last 5: octants, ±1 / ±2 SD),
    quarters to 10 sessions, edges + CE after; news gaps (NFP 2 Oct, CPI 11 Sep) in the news colour; the card live.
(B) NQ1! 1-minute, 9 Oct 08:00–11:00: the same, close up.
python3 mock_garganta.py A.png B.png"""
import sys, json
import numpy as np, pandas as pd, matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
plt.rcParams['font.family'] = 'DejaVu Sans'
OUTA, OUTB = sys.argv[1], sys.argv[2]
BG, MU, GRID, CHT = '#ffffff', '#9aa1b2', '#eef1f6', '#131722'
CB, CT, CS = '#161a23', '#d1d4dc', '#8a93a6'
UP, DN = '#089981', '#f23645'
COLN, COLX = '#26a69a', '#ff9800'
T = json.load(open('/home/claude/rg/rg_tables.json'))
b = pd.read_pickle('/home/claude/kyw/bars_NQ_all.pkl')
b = b[b.tday <= '2026-10-09'].reset_index(drop=True)
NOW = pd.Timestamp('2026-10-09 11:00')
b = b[b.ts < NOW]
DAY = pd.Timestamp('2026-10-09')
ND = json.load(open('/home/claude/rg/news_dates.json'))
CPI, NFP = set(ND['cpi']), set(ND['nfp'])
# gaps from the bars: prior 16:14 close → 09:30 open (TradingView's B-ADJ chart keeps roll days; here the data is roll-adjusted)
o930 = b[b.hm == 930].drop_duplicates('tday').set_index('tday')
c1614 = b[b.hm == 1614].drop_duplicates('tday').set_index('tday')
days = list(o930.index)
G = []
for k in range(1, len(days)):
    td, pdy = days[k], days[k - 1]
    if pdy not in c1614.index:
        continue
    G.append(dict(day=td, O=o930.loc[td, 'Open'], C=c1614.loc[pdy, 'Close'], t0=o930.loc[td, 'ts']))
G = pd.DataFrame(G)
G['g'] = (G.O - G.C).abs()
G['avg20'] = G.g.shift(1).rolling(20).mean()
G = G.tail(21).reset_index(drop=True)          # the last 20 kept + room for averages
G = G.iloc[-20:].iloc[::-1].reset_index(drop=True)   # newest first
G['reg'] = [('CPI' if d.strftime('%Y%m%d') in CPI else 'NFP' if d.strftime('%Y%m%d') in NFP else '') for d in G.day]
after = lambda t0: b[b.ts >= t0]
st = []
for _, r in G.iterrows():
    a = after(r.t0)
    up = r.O > r.C
    ce = (r.O + r.C) / 2
    hitc = a[(a.Low <= ce)] if up else a[(a.High >= ce)]
    hitf = a[(a.Low <= r.C)] if up else a[(a.High >= r.C)]
    st.append((hitc.ts.iloc[0] if len(hitc) else None, hitf.ts.iloc[0] if len(hitf) else None))
G['ceT'] = [s[0] for s in st]
G['flT'] = [s[1] for s in st]
G['ceT'] = G.ceT.astype(object).where(G.ceT.notna(), None)
G['flT'] = G.flT.astype(object).where(G.flT.notna(), None)


def lum(h):
    return 0.299 * int(h[1:3], 16) + 0.587 * int(h[3:5], 16) + 0.114 * int(h[5:7], 16)


def draw(ax, x, ix, tlast, labels_x, fs):
    LBL = []
    A20 = G.iloc[0].avg20
    xr = len(x) - 1 + max(6, len(x) // 120)
    for i, r in G.iterrows():
        if r.g <= 0:
            continue
        base = COLX if r.reg else COLN
        al = 1.0 if i < 5 else 0.55 if i < 10 else 0.35
        if r.flT is not None:
            al *= 0.6
        x1 = max(ix(r.t0), -1)
        top, bot, g = max(r.O, r.C), min(r.O, r.C), r.g
        L = lambda y, ls='-', a=al, lw=1.0: ax.plot([x1, xr], [y, y], color=base, lw=lw, ls=ls, alpha=a, zorder=3)
        L(top); L(bot); L((top + bot) / 2, '--')
        if i < 5:
            ax.add_patch(Rectangle((x1, bot), xr - x1, g, fc=base, alpha=0.08 * (0.6 if r.flT is not None else 1), ec='none', zorder=1))
            for k in range(1, 8):
                if k != 4:
                    L(bot + k * g / 8, ':', al * (0.65 if k % 2 == 0 else 0.35), 0.8)
            for kk, ls in ((1, '--'), (2, ':')):
                L(top + kk * g, ls, al * 0.75, 0.9)
                L(bot - kk * g, ls, al * 0.75, 0.9)
        elif i < 10:
            L(bot + g / 4, ':', al * 0.65, 0.8); L(bot + 3 * g / 4, ':', al * 0.65, 0.8)
        if i < 5:
            s = ' · filled' if r.flT is not None else ' · CE' if r.ceT is not None else ''
            tx = f'RTH {r.day:%m/%d}' + (f' · {r.reg}' if r.reg else '') + s
            ce = (top + bot) / 2
            hit = [k for k, (y, _) in enumerate(LBL) if abs(y - ce) <= 0.1 * A20]
            if hit:
                LBL[hit[0]] = (LBL[hit[0]][0], LBL[hit[0]][1] + '\n' + tx)
            else:
                LBL.append((ce, tx))
    for y, tx in LBL:
        ax.text(labels_x, y, tx, color=CHT, fontsize=fs, va='center', zorder=8, clip_on=True, linespacing=1.3)


def candles(ax, x, w=0.66):
    for i, (t, q) in enumerate(x.iterrows()):
        c = UP if q.Close >= q.Open else DN
        ax.plot([i, i], [q.Low, q.High], color=c, lw=0.6, zorder=4)
        ax.add_patch(Rectangle((i - w / 2, min(q.Open, q.Close)), w, max(abs(q.Close - q.Open), 0.25), fc=c, ec=c, lw=0.2, zorder=5))


def card(fig, x0, y0, rows, head, pill, col, w=0.31):
    lh = 0.027
    ht = '#131722' if lum(col) > 165 else '#ffffff'
    fig.patches.append(Rectangle((x0, y0 - lh), w, lh, transform=fig.transFigure, fc=col, ec='none', zorder=10))
    fig.text(x0 + 0.006, y0 - lh / 2, head, color=ht, fontsize=8.6, family='DejaVu Sans Mono', va='center', weight='bold', zorder=11)
    fig.patches.append(Rectangle((x0 + w - 0.062, y0 - lh + 0.004), 0.056, lh - 0.008, transform=fig.transFigure, fc='#131722' if lum(col) > 165 else '#ffffff', ec='none', zorder=11))
    fig.text(x0 + w - 0.034, y0 - lh / 2, pill, color=col, fontsize=8, family='DejaVu Sans Mono', va='center', ha='center', weight='bold', zorder=12)
    for k, (a, bb, cc, hl) in enumerate(rows):
        yy = y0 - lh * (k + 2)
        fig.patches.append(Rectangle((x0, yy), w, lh, transform=fig.transFigure, fc=CB, ec='none', zorder=10))
        fig.text(x0 + 0.006, yy + lh / 2, a, color=CS, fontsize=8.2, family='DejaVu Sans Mono', va='center', zorder=11)
        fig.text(x0 + 0.06, yy + lh / 2, bb, color=col if hl else CT, fontsize=8.2, family='DejaVu Sans Mono', va='center', zorder=11)
        fig.text(x0 + w - 0.006, yy + lh / 2, cc, color=col if hl else CT, fontsize=8.2, family='DejaVu Sans Mono', va='center', ha='right', zorder=11)
    fig.patches.append(Rectangle((x0, y0 - lh * (len(rows) + 1)), w, lh * (len(rows) + 1), transform=fig.transFigure, fc='none', ec=col, lw=1, zorder=12))


# today's card at 11:00
r0 = G.iloc[0]
up = r0.O > r0.C
g = r0.g
a20 = r0.avg20
rr = g / a20
bk = 0 if rr < 0.5 else 1 if rr < 1 else 2 if rr < 1.5 else 3 if rr < 2.5 else 4
bkn = ['small', 'below avg', 'above avg', 'large', 'very large'][bk]
today = b[b.ts >= r0.t0]
top, bot = max(r0.O, r0.C), min(r0.O, r0.C)
u1 = today[today.High >= top + g].ts; s1 = today[today.Low <= bot - g].ts
c1 = {'up': T['c1_rth'][bk], 'dn': T['o1_rth'][bk]} if up else {'up': T['o1_rth'][bk], 'dn': T['c1_rth'][bk]}
px = b.Close.iloc[-1]
openG = G[G.flT.isna()].copy()
openG['ce'] = (openG.O + openG.C) / 2
ab = openG[openG.ce > px].sort_values('ce').head(1)
be = openG[openG.ce < px].sort_values('ce', ascending=False).head(1)
rows = [('GAP', ('▲ ' if up else '▼ ') + f'{g:,.2f} pts · {100 * g / r0.C:.2f}%', f'{rr:.1f}× · {bkn}', False),
        ('AVG', f'20 sessions · {a20:,.1f} pts', f'{100 * a20 / r0.C:.2f}%', False),
        ('CE', f'{(r0.O + r0.C) / 2:,.2f}', f'✓ hit {r0.ceT:%H:%M}' if r0.ceT is not None else 'by 16:14 —', r0.ceT is not None),
        ('FILL', f'{r0.C:,.2f}', f'✓ filled {r0.flT:%H:%M}' if r0.flT is not None else 'by 16:14 —', r0.flT is not None),
        ('±1 SD', '▲ ' + (f'✓ {u1.iloc[0]:%H:%M}' if len(u1) else f'{c1["up"]}%') + ' · ▼ ' + (f'✓ {s1.iloc[0]:%H:%M}' if len(s1) else f'{c1["dn"]}%'), 'by 16:14', False),
        ('5 SESS', f'fill {[97, 86, 80, 73, 63][bk]}% · CE {[98, 93, 89, 84, 78][bk]}%', 'staircase', False),
        ('ABOVE', f'CE {ab.ce.iloc[0]:,.2f}' if len(ab) else 'no open gap', f'{ab.day.iloc[0]:%m/%d}' if len(ab) else '', False),
        ('BELOW', f'CE {be.ce.iloc[0]:,.2f}' if len(be) else 'no open gap', f'{be.day.iloc[0]:%m/%d}' if len(be) else '', False)]
print(G[['day', 'O', 'C', 'g', 'reg', 'ceT', 'flT']].to_string())
print(rows)

# ── (A) 15-minute, 21 Sep → 9 Oct 11:00
x = b[b.ts >= '2026-09-20 18:00'].set_index('ts').resample('15min').agg(dict(Open='first', High='max', Low='min', Close='last')).dropna()
ix = lambda t: float(np.searchsorted(x.index, t))
fig = plt.figure(figsize=(18, 10.4), dpi=100, facecolor=BG)
ax = fig.add_axes([0.02, 0.05, 0.60, 0.85])
for s_ in ax.spines.values():
    s_.set_visible(False)
ax.set_facecolor(BG); ax.yaxis.tick_right(); ax.tick_params(axis='y', colors=MU, labelsize=8.5); ax.tick_params(axis='x', length=0)
ax.grid(color=GRID, lw=0.7, zorder=0)
candles(ax, x)
n = len(x)
draw(ax, x, ix, NOW, n + 7, 7.2)
ticks = [i for i, t in enumerate(x.index) if t.hour == 9 and t.minute == 30]
ax.set_xticks(ticks); ax.set_xticklabels([x.index[i].strftime('%a %d') for i in ticks], color=MU, fontsize=8.5)
lo, hi = x.Low.min(), x.High.max()
ax.set_xlim(-2, n * 1.16); ax.set_ylim(lo - (hi - lo) * 0.05, hi + (hi - lo) * 0.08)
card(fig, 0.655, 0.885, rows, 'RTH GAP   10/09 · 11:00 ET', 'NORMAL', COLN)
fig.text(0.02, 0.955, 'Garganta · RTH gaps mapped like NWOGs (NQ1! 15-minute, 21 Sep → Fri 9 Oct 2026, 11:00 ET)', color=CHT, fontsize=13, weight='bold')
fig.text(0.02, 0.928, 'The last 20 RTH gaps (16:14 close → 09:30 open) run right. Last 5: octants and ±1 / ±2 SD (the staircase). Sessions 6–10: quarters. Older: edges + CE. '
         'Orange = news day (NFP 2 Oct, CPI 11 Sep). Filled gaps fade. NQ 1-minute data; TradingView rendering will differ.', color='#5d6476', fontsize=9)
plt.savefig(OUTA, dpi=100, facecolor=BG); plt.close(fig)

# ── (B) 1-minute close up, 9 Oct 08:00–11:00
x = b[b.ts >= '2026-10-09 08:00'].set_index('ts')[['Open', 'High', 'Low', 'Close']]
ix = lambda t: float(np.searchsorted(x.index, t))
fig = plt.figure(figsize=(18, 10.4), dpi=100, facecolor=BG)
ax = fig.add_axes([0.02, 0.05, 0.60, 0.85])
for s_ in ax.spines.values():
    s_.set_visible(False)
ax.set_facecolor(BG); ax.yaxis.tick_right(); ax.tick_params(axis='y', colors=MU, labelsize=8.5); ax.tick_params(axis='x', length=0)
ax.grid(color=GRID, lw=0.7, zorder=0)
candles(ax, x, 0.6)
n = len(x)
draw(ax, x, ix, NOW, n + 7, 7.6)
ticks = [i for i, t in enumerate(x.index) if t.minute in (0, 30)]
ax.set_xticks(ticks); ax.set_xticklabels([x.index[i].strftime('%H:%M') for i in ticks], color=MU, fontsize=8.5)
lo, hi = x.Low.min(), x.High.max()
ax.set_xlim(-2, n + 45); ax.set_ylim(lo - (hi - lo) * 0.35, hi + (hi - lo) * 0.35)
card(fig, 0.655, 0.885, rows, 'RTH GAP   10/09 · 11:00 ET', 'NORMAL', COLN)
fig.text(0.02, 0.955, 'Garganta · close up on NQ1! 1-minute, Fri 9 Oct 2026, 08:00–11:00 ET: today\'s gap in its staircase', color=CHT, fontsize=13, weight='bold')
fig.text(0.02, 0.928, 'Today\'s gap ▲ 176 pts split into octants with ±1 / ±2 SD; the gaps of 10/08 and 10/07 sit around it. The card: size against the 20-session average, '
         'CE and fill with times, ±1 SD odds by 16:14, the staircase odds and the nearest open gaps. TradingView rendering will differ.', color='#5d6476', fontsize=9)
plt.savefig(OUTB, dpi=100, facecolor=BG); plt.close(fig)
