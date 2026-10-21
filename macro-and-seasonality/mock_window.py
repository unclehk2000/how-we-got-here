"""Gran Rey Cero: the 08:30–09:00 window lines, shading and day wording. NQ1! 2-minute, light theme, 06:00–11:00 ET.
Left: a CPI day (Wed 12 Aug 2026). Right: a normal day (Fri 9 Oct 2026). Defaults: blue lines width 3, wording Normal
size, 15% of ADR20 above the trading day's high. Prices are NQ 1-minute data."""
import sys, numpy as np, pandas as pd, matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
sys.path.insert(0, '/home/claude/hm'); from events import CPI
plt.rcParams['font.family'] = 'DejaVu Sans'
DPI = 110
BG, GRID, SUB, TX = '#ffffff', '#f0f3fa', '#787b86', '#131722'
UP, DN = '#089981', '#f23645'
GH, LVL, BLUE = '#e53935', '#ffb300', '#2962ff'
def A(c, t):
    c = c.lstrip('#'); return tuple(int(c[i:i + 2], 16) / 255 for i in (0, 2, 4)) + (1 - t / 100,)
b = pd.read_pickle('/home/claude/t3/bars_NQ_all.pkl')
D = pd.read_pickle('/home/claude/hm/days_NQ.pkl'); TDD = D[D.anchor == 'TD'].set_index('tday')
TD = sorted(pd.Timestamp(t) for t in b.tday.unique()); CPIS = set(pd.Timestamp(d) for d in CPI)

def panel(ax, day, title):
    day = pd.Timestamp(day); prev = TD[TD.index(day) - 1]
    at = lambda m: day + pd.Timedelta(minutes=m)
    tdb = b[b.tday == day]
    x = tdb[(tdb.ts >= at(360)) & (tdb.ts < at(660))].set_index('ts').resample('2min').agg(dict(Open='first', High='max', Low='min', Close='last')).dropna()
    T = x.index; n = len(x)
    X = lambda ts: float(np.interp(np.datetime64(ts, 'm').astype(np.int64), T.values.astype('datetime64[m]').astype(np.int64), np.arange(n)))
    isCPI = day in CPIS
    # window shading and lines (drawn first, behind the candles)
    xa, xb = X(at(510)), X(at(540))
    ax.axvspan(xa - .5, xb - .5, color=A(BLUE, 82 if isCPI else 95), lw=0, zorder=0)
    for xv in (xa - .5, xb - .5): ax.axvline(xv, color=A(BLUE, 0 if isCPI else 70), lw=3, zorder=1)
    for i, (ts, r) in enumerate(x.iterrows()):
        c = UP if r.Close >= r.Open else DN
        ax.plot([i, i], [r.Low, r.High], color=c, lw=.8, zorder=3)
        ax.add_patch(Rectangle((i - .35, min(r.Open, r.Close)), .7, max(abs(r.Close - r.Open), .25), color=c, zorder=3))
    fs = 7
    if isCPI:
        pr = tdb[(tdb.ts >= at(450)) & (tdb.ts < at(510))]; drH, drL = pr.High.max(), pr.Low.min()
        rthC = b[(b.tday == prev) & (b.hm == 1614)].Close.iloc[0]
        xs = X(at(450)); xe = n - 1
        for yv in (drH, drL): ax.plot([xs, xe], [yv, yv], ls='--', color=LVL, lw=1, zorder=4)
        ax.text(xs, drH, 'stage 1 · DR high', color=LVL, fontsize=fs, va='bottom')
        ax.text(xs, drL, 'stage 1 · DR low', color=LVL, fontsize=fs, va='top')
        ax.plot([xs, xe], [rthC, rthC], ls=':', color=A(LVL, 25), lw=1); ax.text(xe + .5, rthC, 'yday RTH close', color=A(LVL, 15), fontsize=fs, va='center')
        w = tdb[(tdb.ts >= at(510)) & (tdb.ts < at(540))]
        ax.add_patch(Rectangle((xa - .5, w.Low.min()), xb - xa, w.High.max() - w.Low.min(), fc=A(GH, 78), ec=A(GH, 35), lw=1, zorder=2))
        ax.axvline(X(at(530)) - .5, color=A(LVL, 60), ls=':', lw=1)
        post = tdb[tdb.ts >= at(510)]
        for _, r in post.iterrows():
            if r.Low < drL: ax.annotate('1st sweep ▼', (X(r.ts.floor('2min')), r.Low), xytext=(0, -4), textcoords='offset points', ha='center', va='top', color=LVL, fontsize=fs); break
            if r.High > drH: ax.annotate('1st sweep ▲', (X(r.ts.floor('2min')), r.High), xytext=(0, 4), textcoords='offset points', ha='center', va='bottom', color=LVL, fontsize=fs); break
        o930 = tdb[tdb.hm == 930].Open.iloc[0]; gce = (rthC + o930) / 2
        ax.plot([X(at(570)), xe], [gce, gce], ls=':', color=A(LVL, 20), lw=1); ax.text(xe + .5, gce, 'gap 50%', color=LVL, fontsize=fs, va='center')
        r1 = tdb[tdb.hm == 830]
        ax.add_patch(Rectangle((xa - .5, r1.Low.min()), xe - xa, r1.High.max() - r1.Low.min(), fc=A(GH, 86), ec=A(GH, 15), lw=1, zorder=2))
        ax.text(xe + .5, (r1.High.max() + r1.Low.min()) / 2, 'CPI 12/08 · wild', color=GH, fontsize=7.5, va='center')
    # the day's wording: over the window, 15% of ADR20 above the trading day's high (as of 11:00)
    trd = b[(b.tday == day) & (b.ts < at(660))]
    tdH, tdL = trd.High.max(), trd.Low.min(); O = TDD.loc[day].O; adr = TDD.loc[day].adr
    off = O * adr * .15; y = tdH + off
    word = 'CPI day · here we go folks' if isCPI else 'nothing to see here folks'
    ax.annotate(word, (X(at(525)) - .5, y), xytext=(0, 3), textcoords='offset points', ha='center', va='bottom', color=BLUE, fontsize=9.5, zorder=8)
    lo = x.Low.min(); hi = max(x.High.max(), y); sp = hi - lo
    ax.set_ylim(lo - sp * .06, hi + sp * .14); ax.set_xlim(-2, n + 14)
    for s_ in ax.spines.values(): s_.set_color('#e0e3eb')
    ax.yaxis.tick_right(); ax.tick_params(labelsize=7.5, colors=SUB, length=0); ax.grid(color=GRID, lw=1)
    ticks = [i for i, ts in enumerate(T) if ts.minute == 0 or (ts.hour == 8 and ts.minute == 30)]
    ax.set_xticks(ticks); ax.set_xticklabels([T[i].strftime('%H:%M') for i in ticks])
    ax.text(.008, .985, title, transform=ax.transAxes, fontsize=8.5, color=SUB, va='top')
    print(day.date(), 'tdH', tdH, 'label y', round(y, 2), 'off', round(off, 2))

fig = plt.figure(figsize=(2400 / DPI, 900 / DPI), dpi=DPI, facecolor=BG)
a1 = fig.add_axes([0.012, 0.08, 0.465, 0.86], facecolor=BG); a2 = fig.add_axes([0.512, 0.08, 0.465, 0.86], facecolor=BG)
panel(a1, '2026-08-12', 'NQ1! · 2 · CME   Gran Rey Cero   Wed 12 Aug 2026 (CPI day), 06:00–11:00 ET, mock')
panel(a2, '2026-10-09', 'NQ1! · 2 · CME   Gran Rey Cero   Fri 09 Oct 2026 (normal day), 06:00–11:00 ET, mock')
fig.text(.5, .015, 'Defaults: 08:30 / 09:00 lines blue, width 3 · window shaded (strong on CPI days, faint otherwise) · day wording Normal size, 15% of ADR20 above the day\'s high, rising with it',
         ha='center', fontsize=8.5, color=SUB)
fig.savefig(sys.argv[1], dpi=DPI, facecolor=BG); print(sys.argv[1])
