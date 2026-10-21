"""Benihime v2 mocks from NQ 1-minute data, Fri 9 Oct 2026 at 11:00 ET, computed the way Benihime_RTH_Gaps.pine does:
gaps = prior 16:14 close → 09:30 open from 15-minute bars of the chart's session; touches per session (ETH sees overnight).
python3 mock_benihime2.py OUTDIR"""
import sys, json
import numpy as np, pandas as pd, matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
plt.rcParams['font.family'] = 'DejaVu Sans'
OUT = sys.argv[1]
BG, MU, GRID, CHT = '#ffffff', '#9aa1b2', '#eef1f6', '#131722'
CB, CT, CS = '#161a23', '#d1d4dc', '#8a93a6'
UP, DN = '#089981', '#f23645'
COLN, COLX, COLY = '#26a69a', '#ff9800', '#7e57c2'
T = json.load(open('/home/claude/rg/rg_tables.json'))
N1 = json.load(open('/home/claude/rg/news_dates.json'))
N2 = json.load(open('/home/claude/rg/news_dates2.json'))
MAJ = {'CPI': set(N1['cpi']), 'NFP': set(N1['nfp'])}
OTH = {'PPI': set(d.replace('-', '') for d in N2['ppi']), 'GDP': set(d.replace('-', '') for d in N2['gdp']),
       'PCE': set(d.replace('-', '') for d in N2['pce']), 'RETAIL': set(d.replace('-', '') for d in N2['rs'])}
NOW = pd.Timestamp('2026-10-09 11:00')
B = pd.read_pickle('/home/claude/kyw/bars_NQ_all.pkl')
B = B[(B.ts >= '2026-07-20') & (B.ts < NOW)].set_index('ts')


def tag(d):
    k = d.strftime('%Y%m%d')
    t = [n for n, s in MAJ.items() if k in s] + [n for n, s in OTH.items() if k in s]
    return ' · '.join(t), any(k in s for s in MAJ.values())


def gaps(session):
    b = B if session == 'ETH' else B[(B.hm >= 930) & (B.hm < 1615)]
    x = b.resample('15min').agg(dict(Open='first', High='max', Low='min', Close='last', tday='first')).dropna()
    G, c16, prev = [], None, None
    for t, r in x.iterrows():
        if prev is not None:
            tp, rp = prev
            if tp.hour * 60 + tp.minute <= 974 < tp.hour * 60 + tp.minute + 15:
                c16 = rp.Close
        if t.hour * 60 + t.minute == 570 and c16 is not None:
            G.append(dict(day=r.tday, t0=t, O=r.Open, C=c16)); c16 = None
        prev = (t, r)
    G = pd.DataFrame(G)
    G['g'] = (G.O - G.C).abs()
    G['avg20'] = G.g.shift(1).rolling(20).mean()
    G = G.iloc[::-1].reset_index(drop=True).head(20)
    ce, fl = [], []
    for _, r in G.iterrows():
        a = b[b.index >= r.t0]
        up = r.O > r.C; m = (r.O + r.C) / 2
        hc = a[a.Low <= m] if up else a[a.High >= m]
        hf = a[a.Low <= r.C] if up else a[a.High >= r.C]
        ce.append(hc.index[0] if len(hc) else None); fl.append(hf.index[0] if len(hf) else None)
    G['ceT'] = pd.Series(ce, dtype=object).values
    G['flT'] = pd.Series(fl, dtype=object).values
    G['tag'] = [tag(d)[0] for d in G.day]
    G['maj'] = [tag(d)[1] for d in G.day]
    return G, b


def lum(h):
    return 0.299 * int(h[1:3], 16) + 0.587 * int(h[3:5], 16) + 0.114 * int(h[5:7], 16)


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


def card_rows(G, b):
    r0 = G.iloc[0]
    up = r0.O > r0.C; g = r0.g; a20 = r0.avg20; rr = g / a20
    bk = 0 if rr < 0.5 else 1 if rr < 1 else 2 if rr < 1.5 else 3 if rr < 2.5 else 4
    today = b[b.index >= r0.t0]
    top, bot = max(r0.O, r0.C), min(r0.O, r0.C)
    u1 = today[today.High >= top + g].index; s1 = today[today.Low <= bot - g].index
    pu, pdn = (T['c1_rth'][bk], T['o1_rth'][bk]) if up else (T['o1_rth'][bk], T['c1_rth'][bk])
    cm = today[today.Low <= (r0.O + r0.C) / 2].index if up else today[today.High >= (r0.O + r0.C) / 2].index
    fm = today[today.Low <= r0.C].index if up else today[today.High >= r0.C].index
    px = b.Close.iloc[-1]
    o = G[[not pd.notna(v) for v in G.flT]].copy(); o['ce'] = (o.O + o.C) / 2
    ab = o[o.ce > px].sort_values('ce').head(1); be = o[o.ce < px].sort_values('ce', ascending=False).head(1)
    return [('GAP', ('▲ ' if up else '▼ ') + f'{g:,.2f} pts · {100 * g / r0.C:.2f}%', f'{rr:.1f}× · ' + ['small', 'below avg', 'above avg', 'large', 'very large'][bk], False),
            ('AVG', f'20 sessions · {a20:,.1f} pts', f'{100 * a20 / r0.C:.2f}%', False),
            ('CE', f'{(r0.O + r0.C) / 2:,.2f}', f'✓ hit {cm[0]:%H:%M}' if len(cm) else 'by 16:14 —', len(cm) > 0),
            ('FILL', f'{r0.C:,.2f}', f'✓ filled {fm[0]:%H:%M}' if len(fm) else 'by 16:14 —', len(fm) > 0),
            ('±1 SD', '▲ ' + (f'✓ {u1[0]:%H:%M}' if len(u1) else f'{pu}%') + ' · ▼ ' + (f'✓ {s1[0]:%H:%M}' if len(s1) else f'{pdn}%'), 'by 16:14', False),
            ('5 SESS', f'fill {[97, 86, 80, 73, 63][bk]}% · CE {[98, 93, 89, 84, 78][bk]}%', 'staircase', False),
            ('ABOVE', f'CE {ab.ce.iloc[0]:,.2f}' if len(ab) else 'no open gap', f'{ab.day.iloc[0]:%m/%d}' if len(ab) else '', False),
            ('BELOW', f'CE {be.ce.iloc[0]:,.2f}' if len(be) else 'no open gap', f'{be.day.iloc[0]:%m/%d}' if len(be) else '', False)]


def render(session, tf, start, fname, title, sub, ypad=0.3):
    G, b = gaps(session)
    x = b[b.index >= start][['Open', 'High', 'Low', 'Close']]
    if tf != '1min':
        x = x.resample(tf).agg(dict(Open='first', High='max', Low='min', Close='last')).dropna()
    ix = lambda t: float(np.searchsorted(x.index, t))
    n = len(x)
    fig = plt.figure(figsize=(18, 10.4), dpi=100, facecolor=BG)
    ax = fig.add_axes([0.02, 0.05, 0.60, 0.85])
    for s_ in ax.spines.values():
        s_.set_visible(False)
    ax.set_facecolor(BG); ax.yaxis.tick_right(); ax.tick_params(axis='y', colors=MU, labelsize=8.5); ax.tick_params(axis='x', length=0)
    ax.grid(color=GRID, lw=0.7, zorder=0)
    w = 0.6 if tf == '1min' else 0.66
    for i, (t, q) in enumerate(x.iterrows()):
        c = UP if q.Close >= q.Open else DN
        ax.plot([i, i], [q.Low, q.High], color=c, lw=0.6, zorder=4)
        ax.add_patch(Rectangle((i - w / 2, min(q.Open, q.Close)), w, max(abs(q.Close - q.Open), 0.25), fc=c, ec=c, lw=0.2, zorder=5))
    xr = n - 1 + max(6, n // 120)
    A20 = G.iloc[0].avg20
    LBL = []

    def place(y, tx, col):
        hit = [k for k, (yy, _, _) in enumerate(LBL) if abs(yy - y) <= 0.1 * A20]
        if hit:
            LBL[hit[0]] = (LBL[hit[0]][0], LBL[hit[0]][1] + '\n' + tx, LBL[hit[0]][2])
        else:
            LBL.append((y, tx, col))
    for i, r in G.iterrows():
        base = COLX if r.maj else COLY if r.tag else COLN
        al = 1.0 if i < 5 else 0.55 if i < 10 else 0.35
        if pd.notna(r.flT):
            al *= 0.6
        x1 = max(ix(r.t0), -1)
        top, bot, g = max(r.O, r.C), min(r.O, r.C), r.g
        L = lambda y, ls='-', a=al, lw=1.0: ax.plot([x1, xr], [y, y], color=base, lw=lw, ls=ls, alpha=a, zorder=3)
        L(top); L(bot); L((top + bot) / 2, '--')
        if i < 5:
            ax.add_patch(Rectangle((x1, bot), xr - x1, g, fc=base, alpha=0.08 * (0.6 if pd.notna(r.flT) else 1), ec='none', zorder=1))
            for k in range(1, 8):
                if k != 4:
                    L(bot + k * g / 8, ':', al * (0.65 if k % 2 == 0 else 0.35), 0.8)
            s = ' · filled' if pd.notna(r.flT) else ' · CE' if pd.notna(r.ceT) else ''
            place((top + bot) / 2, f'RTH {r.day:%m/%d}' + (f' · {r.tag}' if r.tag else '') + s, CHT)
        elif i < 10:
            L(bot + g / 4, ':', al * 0.65, 0.8); L(bot + 3 * g / 4, ':', al * 0.65, 0.8)
        # the SD staircase: the last 5, and release days while they stay on the chart; weekday on the ±2 SD
        if i < 5 or r.tag:
            L(top + g, (0, (6, 3)), al, 1.2); L(bot - g, (0, (6, 3)), al, 1.2)
            L(top + 2 * g, '-', al, 1.2); L(bot - 2 * g, '-', al, 1.2)
            dn = r.day.strftime('%a') + ('' if i < 5 else ' ' + r.day.strftime('%m/%d')) + (' ' + r.tag if r.tag else '')
            place(top + 2 * g, dn + ' +2 SD', base)
            place(bot - 2 * g, dn + ' −2 SD', base)
    for y, tx, col in LBL:
        ax.text(n + max(7, n // 110), y, tx, color=col, fontsize=7.4, va='center', zorder=8, clip_on=True, linespacing=1.3, weight='bold' if col != CHT else 'normal')
    if tf == '1min':
        if session == 'ETH':
            ticks = [i for i, t in enumerate(x.index) if t.minute == 0 and t.hour % 2 == 0]
            lab = [x.index[i].strftime('%H:%M') for i in ticks]
        else:
            ticks = [i for i, t in enumerate(x.index) if (t.minute == 0 and t.hour in (11, 13, 15)) or (t.hour == 9 and t.minute == 30)]
            lab = [x.index[i].strftime('%a %d') if x.index[i].hour == 9 else x.index[i].strftime('%H:%M') for i in ticks]
    else:
        ticks = [i for i, t in enumerate(x.index) if t.hour == 9 and t.minute == 30]
        lab = [x.index[i].strftime('%a %d') for i in ticks]
    ax.set_xticks(ticks); ax.set_xticklabels(lab, color=MU, fontsize=8)
    lo, hi = x.Low.min(), x.High.max()
    ax.set_xlim(-2, n * 1.24); ax.set_ylim(lo - (hi - lo) * ypad, hi + (hi - lo) * ypad)
    tg, mj = tag(G.iloc[0].day)
    card(fig, 0.655, 0.885, card_rows(G, b), 'BENIHIME   RTH GAP 10/09 · 11:00 ET', tg or 'NORMAL', COLX if mj else COLY if tg else COLN)
    fig.text(0.02, 0.955, title, color=CHT, fontsize=13, weight='bold')
    fig.text(0.02, 0.928, sub, color='#5d6476', fontsize=9)
    plt.savefig(f'{OUT}/{fname}', dpi=100, facecolor=BG); plt.close(fig)
    print(fname, G[['day', 'O', 'C', 'tag', 'ceT', 'flT']].head(8).to_string())


render('ETH', '1min', pd.Timestamp('2026-10-08 13:00'), 'Benihime_ETH_1m.png',
       'Benihime · ETH chart, NQ1! 1-minute: 8 Oct 13:00 → Fri 9 Oct 11:00 ET',
       'The RTH gap is the overnight move from the 16:14 close to the 09:30 open: today\'s ▲ 176-pt gap with its octants and ±1 / ±2 SD; 10/08 and 10/07 sit above. '
       'On an ETH chart, overnight trading counts toward CE and fills. NQ 1-minute data; TradingView rendering will differ.', 0.12)
render('RTH', '1min', pd.Timestamp('2026-10-07 09:30'), 'Benihime_RTH_1m.png',
       'Benihime · RTH chart, NQ1! 1-minute: 7 Oct → Fri 9 Oct 11:00 ET (regular trading hours only)',
       'With the overnight hidden, each gap is the jump between one session\'s 16:14 candle and the next 09:30 candle; the boxes start at that 09:30. '
       'On an RTH chart only RTH trading counts toward CE and fills. TradingView rendering will differ.', 0.08)
render('RTH', '5min', pd.Timestamp('2026-09-11 09:30'), 'Benihime_RTH_5m_20gaps.png',
       'Benihime · RTH chart, NQ1! 5-minute: the last 20 RTH gaps (11 Sep → 9 Oct 2026)',
       'Staircase (last 5 + release days): octants, ±1 SD dashed, ±2 SD solid with the weekday. Sessions 6–10: quarters; older: edges + CE. '
       'Orange = CPI / NFP; purple = PPI, GDP, PCE, retail. 18 Sep (roll day) missing from my data. TradingView rendering will differ.', 0.05)
