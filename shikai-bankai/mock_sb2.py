"""Shikai / Bankai Session Map v2 mocks from NQ 1-minute data, computed the way Shikai_Bankai_Session_Map.pine does.
python3 mock_sb2.py OUTDIR"""
import sys, json
import numpy as np, pandas as pd, matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
plt.rcParams['font.family'] = 'DejaVu Sans'
OUT = sys.argv[1]
T = json.load(open('/home/claude/sb/sb_tables.json'))
B = pd.read_pickle('/home/claude/kyw/bars_NQ_all.pkl')
B = B[B.ts >= '2026-08-20'].reset_index(drop=True)
B['mm'] = B.ts.dt.hour * 60 + B.ts.dt.minute
D = B.groupby('tday').agg(H=('High', 'max'), L=('Low', 'min'))
D['adr'] = (D.H - D.L).rolling(20).mean().shift(1)
COLMID, COLL, COLS, COL25, COL50, COLHA, COLHL = '#ff9800', '#4caf50', '#f44336', '#2196f3', '#ab47bc', '#9c27b0', '#f44336'
CKS = [0, 15, 30, 45, 60, 90, 120, 180, 240, 300, 360, 420]
CKB = [0, 5, 10, 15, 20, 30, 45, 60, 75]
CKL = [300, 480, 570, 600, 630, 660, 720, 780, 840, 900, 960]


def tick(v):
    return np.floor(v / 0.25 + 0.5) * 0.25


def px(v):
    return '—' if v is None or (isinstance(v, float) and np.isnan(v)) else f'{tick(v):.2f}'


def hm(ts):
    return ts.strftime('%H:%M')


def pct(v):
    return '—' if np.isnan(v) else f'{int(np.floor(v + 0.5))}%'


def xs(v):
    return '—' if v is None or np.isnan(v) else f'{v:.1f}×'


def odds(tb, ck, nc, b, mins):
    flat = [x for r in tb for x in r]
    n = len(ck)
    if mins < ck[0]:
        return np.nan
    i = 0
    while i < n - 1 and ck[i + 1] <= mins:
        i += 1
    if i >= n - 1:
        return flat[(n - 1) * nc + b]
    f = (mins - ck[i]) / (ck[i + 1] - ck[i])
    return flat[i * nc + b] * (1 - f) + flat[(i + 1) * nc + b] * f


def distB(d):
    return 0 if d < 0.05 else 1 if d < 0.1 else 2 if d < 0.2 else 3 if d < 0.35 else 4


def lvl25(o, c):
    bt, bb = max(o, c), min(o, c)
    br = bt - bb
    return (bt - 0.25 * br if c >= o else bb + 0.25 * br) if br > 0 else (bt + bb) / 2


def regime(ah, al, lh, ll):
    return 'London engulfs Asia' if lh > ah and ll < al else 'Asia engulfs London' if ah >= lh and al <= ll else \
        'London partial up' if lh > ah else 'London partial down' if ll < al else 'Inside'


def sess(x, a, b):
    s = x[(x.mm >= a) & (x.mm < b)]
    if not len(s):
        return None
    return dict(o=s.Open.iloc[0], h=s.High.max(), l=s.Low.min(), c=s.Close.iloc[-1], t0=s.ts.iloc[0])


def state(day, now, bankai):
    x = B[(B.tday == day) & (B.ts < now)].copy()
    st = dict(x=x, day=day, bankai=bankai, last=x.ts.iloc[-1], mNow=int(x.mm.iloc[-1]), A=D.adr[day])
    on = x[(x.mm >= 1080) | (x.mm < 570)]
    st['oH'], st['oL'] = on.High.max(), on.Low.min()
    st['oHt'], st['oLt'] = on.ts[on.High.idxmax()], on.ts[on.Low.idxmin()]
    st['sA'], st['sAL'], st['sL'], st['sLN'], st['sN'] = sess(x, 1080, 1440), sess(x, 0, 120), sess(x, 120, 300), sess(x, 300, 480), sess(x, 480, 1020)
    st['close'] = x.Close.iloc[-1]
    st['today'] = (x.mm == 570).any()
    if st['today']:
        b930 = x[x.mm == 570].iloc[0]
        O = b930.Open
        mid = (st['oH'] + st['oL']) / 2
        up = mid > O
        st.update(O=O, mid=mid, up=up, mir=2 * O - mid, t930=b930.ts)
        r = x[(x.mm >= 570) & (x.mm < 1020)]
        h = r[r.High >= mid] if up else r[r.Low <= mid]
        st['midT'] = int((h.ts.iloc[0] - b930.ts).total_seconds() // 60) if len(h) else -1
        st['midTs'] = h.ts.iloc[0] if len(h) else None
        st['mid11'] = bool(len(h) and h.mm.iloc[0] < 660)
        h = r[r.Low <= st['mir']] if up else r[r.High >= st['mir']]
        st['mirT'] = int((h.ts.iloc[0] - b930.ts).total_seconds() // 60) if len(h) else -1
        st['mirTs'] = h.ts.iloc[0] if len(h) else None
    L = st['sL']
    st['lhT'] = st['llT'] = st['q25T'] = None
    if L is not None:
        a = x[(x.mm >= 300) & (x.mm < 1020)]
        h = a[a.High > L['h']]; l = a[a.Low < L['l']]
        st['lhT'] = h.ts.iloc[0] if len(h) else None
        st['llT'] = l.ts.iloc[0] if len(l) else None
        if L['c'] != L['o']:
            q = lvl25(L['o'], L['c'])
            qq = a[a.Low <= q] if L['c'] > L['o'] else a[a.High >= q]
            st['q25T'] = qq.ts.iloc[0] if len(qq) else None
    return st


def card_rows(st, mob):
    bk, mNow, A = st['bankai'], st['mNow'], st['A']
    today = st['today']
    endM, endT = (660, '11:00') if bk else (1020, '16:59')
    live = today and 570 <= mNow < endM
    L, Asia, N = st['sL'], st['sA'], st['sN']
    lonOK = L is not None and not (120 <= mNow < 300)
    midN = st['mid'] if today else (st['oH'] + st['oL']) / 2
    refO = st['O'] if today else st['close']
    upN = midN > refO
    dist = abs(midN - refO)
    dA = dist / A
    b = distB(dA)
    mins = max(0, mNow - 570) if today else 0
    hitOK = today and st['midT'] >= 0 and (not bk or st['mid11'])
    arrow = ' ▲ ' if upN else ' ▼ '
    pill = 'FORMING' if not today else '✓ MID' if hitOK else (('LONG' if st['up'] else 'SHORT') if live else 'OVER')
    hc = '#787b86' if not today else COLMID if hitOK else (COLL if st['up'] else COLS)
    hd0 = ('BANKAI' if mob else 'BANKAI · NY AM') if bk else ('SHIKAI' if mob else 'SHIKAI · ALL DAY')
    hd1 = st['last'].strftime('%m/%d %H:%M' if mob else '%m/%d · %H:%M') + ('' if mob else ' ET')
    R = []
    if not today:
        R.append(('ON', f"H {px(st['oH'])} · L {px(st['oL'])}", f"{px(st['oH'] - st['oL'])} pts", None))
    R.append(('MID', px(midN) + arrow + f'{dA:.2f} ADR', px(dist) + ('' if mob else ' pts'), None))
    pull = upN and dA >= 0.1
    R.append(('SIDE', 'discount · LONG into mid' if upN else 'premium · SHORT into mid', 'pull ✓' if pull else 'near · even' if upN else 'no pull', COLL if pull else None))
    tbs = (('BKMA' if upN else 'BKMB'), ('BKRB' if upN else 'BKRA')) if bk else (('SHMA' if upN else 'SHMB'), ('SHRB' if upN else 'SHRA'))
    ck = CKB if bk else CKS
    pM, pR = odds(T[tbs[0]], ck, 5, b, mins), odds(T[tbs[1]], ck, 5, b, mins)
    od = f'mid {pct(pM)} · mirror {pct(pR)}'
    if not today:
        R.append(('IF OPEN', od, endT if mob else 'by ' + endT, None))
    elif st['midT'] >= 0:
        hv = f"✓ mid {hm(st['midTs'])} · {st['midT']}" + ('m' if mob else ' min') + (((' late' if mob else f' (after {endT})')) if bk and not st['mid11'] else '')
        R.append(('REACH', hv, '' if mob else 'mirror ✓' if st['mirT'] >= 0 else ('mirror ' + pct(pR)) if live else '', COLMID if hitOK else None))
    else:
        R.append(('REACH', od if live else 'mid not reached', (endT if mob else 'by ' + endT) if live else '' if mob else 'mirror ✓' if st['mirT'] >= 0 else '', None))
    mirN = st['mir'] if today else 2 * refO - midN
    R.append(('MIRROR', px(mirN) + (' below' if upN else ' above'), ('✓ ' + hm(st['mirTs'])) if today and st['mirT'] >= 0 else '', None))
    if bk:
        inP, inS = 571 <= mNow < 581, 581 <= mNow < 600
        wOpen = live and not hitOK and (inP or inS)
        wv = ('09:31 / 09:41' if mob else 'windows 09:31 · 09:41') if not today else 'program over' if not live else 'mid reached · manage' if hitOK else \
            'primary → 09:41' if inP else 'secondary → 10:00' if inS else 'primary at 09:31' if mNow < 571 else 'entries closed'
        ww = 'stop ' + endT if not today else '' if not live else (f'{endM - mNow}m left' if mob else f'stop {endT} · {endM - mNow}m')
        R.append(('WINDOW', wv, ww, (COLL if st['up'] else COLS) if wOpen else None))
    endL = 660 if bk else 1020
    if lonOK:
        both = st['lhT'] is not None and st['llT'] is not None
        tb = T['L11' if bk else 'L17']
        pH, pL = odds(tb, CKL, 2, 0, mNow), odds(tb, CKL, 2, 1, mNow)
        hS = ((pct(pH) if mNow < endL else '✗') if mob else px(L['h'])) if st['lhT'] is None else '✓' if mob else '✓ ' + hm(st['lhT'])
        lS = ((pct(pL) if mNow < endL else '✗') if mob else px(L['l'])) if st['llT'] is None else '✓' if mob else '✓ ' + hm(st['llT'])
        lw = 'both ✓' if both else '' if mNow >= endL else ('' if mob else 'by ' + ('11:00 ' if bk else '16:59 ')) + \
            (pct(pH) if st['lhT'] is None else '✓') + ' / ' + (pct(pL) if st['llT'] is None else '✓')
        if mob:
            lw = '' if both or mNow >= endL else ('11:00' if bk else '16:59')
        R.append(('LONDON', f'H {hS} · L {lS}', lw, None))
        if L['c'] != L['o']:
            q = lvl25(L['o'], L['c'])
            R.append(('LDN 25%', ('bull · ' if L['c'] > L['o'] else 'bear · ') + px(q), 'untouched' if st['q25T'] is None else 'traded ✓ ' + hm(st['q25T']), None))
    else:
        R.append(('LONDON', 'forming 02:00–04:59', '', None))
    rA = (Asia['h'] - Asia['l']) / (0.26 * A) if Asia else np.nan
    rL = (L['h'] - L['l']) / (0.239 * A) if L else np.nan
    rN = (N['h'] - N['l']) / (0.794 * A) if N else np.nan
    R.append(('RANGES', f'A {xs(rA)} L {xs(rL)} NY {xs(rN)}' if mob else f'Asia {xs(rA)} · Ldn {xs(rL)} · NY {xs(rN)}', '' if mob else 'of typical', None))
    R.append(('REGIME', regime(Asia['h'], Asia['l'], L['h'], L['l']) if lonOK and Asia else 'after London (05:00)', 'context', None))
    if mob:
        keep = ('MID', 'IF OPEN', 'REACH', 'WINDOW', 'LONDON') if bk else ('MID', 'IF OPEN', 'REACH', 'LONDON', 'RANGES')
        R = [r for r in R if r[0] in keep]
    return (hd0, hd1, pill, hc), R


def lum(h):
    return 0.299 * int(h[1:3], 16) + 0.587 * int(h[3:5], 16) + 0.114 * int(h[5:7], 16)


def draw_card(fig, ax, head, rows, dark, fs, corner='bl', mono=True):
    """A Pine table: 3 columns sized to their longest text, header in the state colour."""
    hd0, hd1, pill, hc = head
    fam = 'DejaVu Sans Mono' if mono else 'DejaVu Sans'
    cBody, cTxt, cSub = ('#161a23', '#d1d4dc', '#8a93a6') if dark else ('#f4f6f9', '#131722', '#5d6476')
    W, H = fig.get_size_inches()
    rd = fig.canvas.get_renderer()

    def tw(s):
        t = fig.text(0, 0, s, fontsize=fs, family=fam)
        w_ = t.get_window_extent(rd).width / fig.dpi / W
        t.remove()
        return w_
    cw = 0.6 * fs / 72 / W
    lh = 1.75 * fs / 72 / H
    cols = [max(tw(hd0), *(tw(r[0]) for r in rows)), max(tw(hd1), *(tw(r[1]) for r in rows)), max(tw(pill), *(tw(r[2]) for r in rows))]
    wcol = [c + 1.6 * cw for c in cols]
    w = sum(wcol)
    bb = ax.get_position()
    x0 = bb.x1 - w - 0.006 if corner == 'tr' else bb.x0 + 0.004
    y0 = bb.y1 - 0.008 if corner == 'tr' else bb.y0 + 0.006 + lh * (len(rows) + 1)
    ht = '#131722' if lum(hc) > 165 else '#ffffff'
    fig.patches.append(Rectangle((x0, y0 - lh), w, lh, transform=fig.transFigure, fc=hc, ec='none', zorder=10))
    fig.text(x0 + 0.8 * cw, y0 - lh / 2, hd0, color=ht, fontsize=fs, family=fam, va='center', zorder=11)
    fig.text(x0 + wcol[0] + 0.8 * cw, y0 - lh / 2, hd1, color=ht, fontsize=fs, family=fam, va='center', zorder=11)
    pb = '#131722' if lum(hc) > 165 else '#ffffff'
    fig.patches.append(Rectangle((x0 + wcol[0] + wcol[1], y0 - lh), wcol[2], lh, transform=fig.transFigure, fc=pb, ec='none', zorder=10))
    fig.text(x0 + wcol[0] + wcol[1] + wcol[2] / 2, y0 - lh / 2, pill, color=hc, fontsize=fs, family=fam, va='center', ha='center', zorder=11)
    for k, (a, v, ww, c) in enumerate(rows):
        yy = y0 - lh * (k + 2)
        fig.patches.append(Rectangle((x0, yy), w, lh, transform=fig.transFigure, fc=cBody, ec='none', zorder=10))
        fig.text(x0 + 0.8 * cw, yy + lh / 2, a, color=cSub, fontsize=fs, family=fam, va='center', zorder=11)
        fig.text(x0 + wcol[0] + 0.8 * cw, yy + lh / 2, v, color=c or cTxt, fontsize=fs, family=fam, va='center', zorder=11)
        fig.text(x0 + w - 0.8 * cw, yy + lh / 2, ww, color=c or cTxt, fontsize=fs, family=fam, va='center', ha='right', zorder=11)
    fig.patches.append(Rectangle((x0, y0 - lh * (len(rows) + 1)), w, lh * (len(rows) + 1), transform=fig.transFigure, fc='none', ec=hc, lw=1, alpha=0.7, zorder=12))


def hot_block(x, a, b, blk=30):
    """the widest finished 30-minute block of a session window, as Pine's hotBlock: [mid, start, set-at time]."""
    s = x[(x.mm >= a) & (x.mm < b)] if a < b else x[(x.mm >= a) | (x.mm < b)]
    if not len(s):
        return None
    t0 = s.ts.iloc[0]
    k = ((s.ts - t0).dt.total_seconds() // (blk * 60)).astype(int)
    best = None
    ks = sorted(k.unique())
    for i, kk in enumerate(ks[:-1]):          # a block counts once the next one starts
        g = s[k == kk]
        r = g.High.max() - g.Low.min()
        if best is None or r > best[0]:
            nxt = s[k == ks[i + 1]].iloc[0]
            best = (r, (g.High.max() + g.Low.min()) / 2, g.ts.iloc[0], nxt.ts, nxt)
    return best


def chart(ax, st, t_from, dark, fs, mob):
    bg, fg, grid = ('#131722', '#d1d4dc', '#1e222d') if dark else ('#ffffff', '#131722', '#eef1f6')
    up_c, dn_c = '#089981', '#f23645'
    ax.set_facecolor(bg)
    x = st['x']
    v = x[x.ts >= t_from].reset_index(drop=True)
    idx = {t: i for i, t in enumerate(v.ts)}
    n = len(v)
    tx = lambda t: idx.get(t, -1 if t < v.ts.iloc[0] else n - 1)
    for i, r in v.iterrows():
        c = up_c if r.Close >= r.Open else dn_c
        ax.plot([i, i], [r.Low, r.High], color=c, lw=0.6, zorder=3)
        ax.add_patch(Rectangle((i - 0.32, min(r.Open, r.Close)), 0.64, max(abs(r.Close - r.Open), 0.25), fc=c, ec=c, lw=0.3, zorder=4))
    last = n - 1
    labels, slabels = [], []

    def lvl(t0, y, col, w, ls, txt, sess_line=False):
        ax.plot([max(tx(t0), -1), last], [y, y], color=col, lw=w, ls=ls, zorder=5)
        (slabels if sess_line else labels).append((y, txt, col if sess_line else fg))

    bk = st['bankai']
    stamp = lambda t: t.strftime('%H:%M %m/%d')
    # Bankai windows: shaded while the midpoint is untouched
    if bk and st['today']:
        for a, b2, al in ((571, 581, 0.15), (581, 600, 0.07)):
            ii = [i for i, r in v.iterrows() if a <= r.mm < b2 and (st['midTs'] is None or r.ts < st['midTs'])]
            if ii:
                ax.axvspan(ii[0] - 0.5, ii[-1] + 0.5, color='#4caf50', alpha=al, lw=0, zorder=1)
    # session open lines
    for m, nm in ((0, 'Asia→Ldn'), (120, 'London'), (300, 'Ldn→NY'), (480, 'NY')):
        hit = v[v.mm == m]
        if len(hit):
            i = hit.index[0]
            ax.axvline(i, color=fg, alpha=0.3, lw=0.8, zorder=2)
            ax.text(i, 0.985, nm, transform=ax.get_xaxis_transform(), ha='center', va='top', fontsize=fs - 1.5, color=fg,
                    bbox=dict(fc=fg, alpha=0.12, ec='none', pad=1.5), zorder=6)
    # hot blocks (Shikai)
    if not bk:
        for a, b2, nm, col in ((1200, 0, 'Asia', COLHA), (120, 300, 'London', COLHL)):
            hb = hot_block(x, a, b2)
            if hb:
                lvl(hb[2], hb[1], col, 1, '-', f'{stamp(hb[2])} {nm} hot-block mid')
    # Asia / London 25% and 50%
    for s, nm in ((st['sA'], 'Asia'), (st['sL'], 'London')):
        if s and not (nm == 'London' and 120 <= st['mNow'] < 300 and False):
            if s['c'] != s['o']:
                lvl(s['t0'], lvl25(s['o'], s['c']), COL25, 1, '-', f"{stamp(s['t0'])} {nm} 25%", True)
            lvl(s['t0'], (s['o'] + s['c']) / 2, COL50, 1, '-', f"{stamp(s['t0'])} {nm} 50%", True)
    if st['today']:
        lvl(st['oHt'], st['oH'], '#787b86', 1, '-', f"{stamp(st['oHt'])} ON high")
        lvl(st['oLt'], st['oL'], '#787b86', 1, '-', f"{stamp(st['oLt'])} ON low")
        hitN = st['midTs'] is not None
        t0 = min(st['oHt'], st['oLt'])
        lvl(t0, st['mid'], COLMID, 2, '--' if hitN else '-', f"{stamp(st['t930'])} {'Bankai' if bk else 'Shikai'} mid")
        lvl(st['t930'], st['mir'], '#787b86', 1, ':', f"{stamp(st['t930'])} mirror")
        i930 = tx(st['t930'])
        b930 = v.iloc[i930]
        up = st['up']
        y = b930.Low if up else b930.High
        ax.annotate('▲ Into mid: LONG' if up else '▼ Into mid: SHORT', (i930, y), xytext=(0, -9 if up else 9), textcoords='offset points',
                    ha='center', va='top' if up else 'bottom', fontsize=fs, color=fg, zorder=8,
                    bbox=dict(fc=COLL if up else COLS, alpha=0.25, ec='none', boxstyle='round,pad=0.25'), annotation_clip=True, clip_on=True)
        if hitN:
            ih = tx(st['midTs'])
            txt = (f"Bankai ✓ mid hit {hm(st['midTs'])} · {st['midT']} min" if bk else f"Shikai mid hit {hm(st['midTs'])} · {st['midT']} min")
            ax.annotate(txt, (ih, st['mid']), xytext=(0, 9 if not up else 9), textcoords='offset points', ha='center', va='bottom',
                        fontsize=fs, color=fg, zorder=8, bbox=dict(fc=COLMID, alpha=0.25, ec='none', boxstyle='round,pad=0.25'))
    # session candles, right of price
    cOff, cW, cSp = 15, 4, 6
    xx = last + cOff
    cc = fg
    for key, nm, lv in (('sA', 'Asia', True), ('sAL', 'Asia→Ldn', False), ('sL', 'London', True), ('sLN', 'Ldn→NY', False), ('sN', 'NY', True)):
        s = st[key]
        if s:
            bt, bb = max(s['o'], s['c']), min(s['o'], s['c'])
            xm = xx + cW / 2
            ax.add_patch(Rectangle((xx, bb), cW, max(bt - bb, 0.25), fc=cc, alpha=0.15, ec='none', zorder=4))
            ax.add_patch(Rectangle((xx, bb), cW, max(bt - bb, 0.25), fc='none', ec=cc, lw=0.8, zorder=4))
            ax.plot([xm, xm], [bt, s['h']], color=cc, lw=0.8, zorder=4)
            ax.plot([xm, xm], [s['l'], bb], color=cc, lw=0.8, zorder=4)
            ax.annotate(f"{nm}\n{px(s['h'])}", (xm, s['h']), xytext=(0, 3), textcoords='offset points', ha='center', va='bottom',
                        fontsize=fs - 1.8, color=cc, zorder=7, bbox=dict(fc=cc, alpha=0.1, ec='none', pad=1.2))
            ax.annotate(px(s['l']), (xm, s['l']), xytext=(0, -3), textcoords='offset points', ha='center', va='top', fontsize=fs - 1.8, color=cc, zorder=7)
            if lv:
                if bt > bb:
                    q = lvl25(s['o'], s['c'])
                    ax.plot([xx + cW, xx + cW + cSp], [q, q], color=COL25, lw=1, zorder=4)
                    ax.text(xx + cW + cSp, q, '25%', color=COL25, fontsize=fs - 1.8, va='center', zorder=7)
                h50 = (s['o'] + s['c']) / 2
                ax.plot([xx + cW, xx + cW + cSp], [h50, h50], color=COL50, lw=1, zorder=4)
                ax.text(xx + cW + cSp, h50, '50%', color=COL50, fontsize=fs - 1.8, va='center', zorder=7)
        xx += cW + cSp
    # level labels at the last bar (label_left), as the script draws them
    # store levels (creation order) then session lines; within 2.5% of ADR20 they share one stacked label
    thr = 0.025 * st['A']
    merged = []
    for y, t, c in labels + slabels:
        for m in merged:
            if abs(m[0] - y) <= thr:
                m[1] += '\n' + t
                break
        else:
            merged.append([y, t, c])
    for y, t, c in merged:
        ax.text(last + 1, y, t, fontsize=fs, color=c, va='center', ha='left', zorder=7, clip_on=True)
    ys = [v.Low.min(), v.High.max()] + [st[k]['h'] for k in ('sA', 'sAL', 'sL', 'sLN', 'sN') if st[k]] + [st[k]['l'] for k in ('sA', 'sAL', 'sL', 'sLN', 'sN') if st[k]]
    lo, hi = min(ys), max(ys)
    pad = (hi - lo) * 0.08
    ax.set_ylim(lo - pad, hi + pad * 2.6)
    ax.set_xlim(-2, last + cOff + 5 * (cW + cSp) + 10)
    ax.grid(color=grid, lw=0.6, zorder=0)
    ax.yaxis.tick_right()
    ax.tick_params(colors=fg, labelsize=fs, length=0)
    for sp in ax.spines.values():
        sp.set_color(grid)
    ticks = [i for i, r in v.iterrows() if r.mm % (60 if not mob else 30) == 0]
    ax.set_xticks(ticks)
    ax.set_xticklabels([hm(v.ts[i]) for i in ticks])


def desktop(day, now, t_from, bankai, dark, fname, title):
    st = state(pd.Timestamp(day), pd.Timestamp(now), bankai)
    bg = '#131722' if dark else '#ffffff'
    fig = plt.figure(figsize=(16, 8.4), dpi=115, facecolor=bg)
    ax = fig.add_axes([0.02, 0.06, 0.93, 0.86])
    chart(ax, st, pd.Timestamp(t_from), dark, 7.6, False)
    head, rows = card_rows(st, False)
    draw_card(fig, ax, head, rows, dark, 8.2, 'bl', True)
    fig.text(0.02, 0.965, title, fontsize=11, color='#d1d4dc' if dark else '#131722', weight='bold')
    fig.savefig(f'{OUT}/{fname}', facecolor=bg)
    plt.close(fig)
    return head, rows


def mobile(panels, fname):
    fig = plt.figure(figsize=(9.6, 9.4), dpi=120, facecolor='#e9ecf2')
    out = []
    for k, (day, now, t_from, bankai, cap) in enumerate(panels):
        st = state(pd.Timestamp(day), pd.Timestamp(now), bankai)
        x0 = 0.03 + k * 0.5
        fig.patches.append(Rectangle((x0 - 0.008, 0.03), 0.456, 0.89, transform=fig.transFigure, fc='#ffffff', ec='#131722', lw=6, zorder=0))
        ax = fig.add_axes([x0, 0.07, 0.38, 0.83])
        ax.set_zorder(2)
        # TradingView's Small on a phone: about 65 default-font characters across the chart pane
        fs = 0.38 * 9.6 * 72 / (65 * 0.55)
        chart(ax, st, pd.Timestamp(t_from), False, fs * 0.9, True)
        head, rows = card_rows(st, True)
        draw_card(fig, ax, head, rows, False, fs, 'bl', False)
        fig.text(x0 + 0.22, 0.945, cap, fontsize=9.5, color='#131722', ha='center', weight='bold')
        out.append((head, rows))
    fig.savefig(f'{OUT}/{fname}', facecolor='#e9ecf2')
    plt.close(fig)
    return out


if __name__ == '__main__':
    a = desktop('2026-10-07', '2026-10-07 11:15', '2026-10-07 07:30', False, False, 'SB2_Desktop_Shikai_1m.png',
                'Shikai · NQ 1 min · Wed 7 Oct 2026, 11:15 ET · Layout: Desktop · card theme Auto (light chart)')
    b = desktop('2026-10-08', '2026-10-08 09:50', '2026-10-08 07:00', True, True, 'SB2_Desktop_Bankai_1m.png',
                'Bankai · NQ 1 min · Thu 8 Oct 2026, 09:50 ET · Layout: Desktop · card theme Auto (dark chart)')
    c = mobile([('2026-10-07', '2026-10-07 12:30', '2026-10-07 10:45', False, 'Shikai · Wed 7 Oct 12:30 · mid reached'),
                ('2026-10-08', '2026-10-08 09:05', '2026-10-08 07:20', True, 'Bankai · Thu 8 Oct 09:05 · forming')], 'SB2_Mobile_1m.png')
    for h, r in [a, b] + c:
        print(h)
        for x in r:
            print('   ', x)
