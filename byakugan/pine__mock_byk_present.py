"""Byakugan mock: first presented FVG with FVG length = "To the present", NQ1! 15-minute, the last four trading days to
Fri 9 Oct 2026 16:59 (the end of the data). FVGs found the way Byakugan_FPFVG.pine finds them, on 1-minute bars:
session 09:30-16:00, the first 3-candle wick gap completing within 30 minutes of the open.
python3 mock_byk_present.py out.png"""
import sys
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

OUT = sys.argv[1]
BG, TX, SUB, MU, GRID = '#131722', '#d1d4dc', '#9aa3b5', '#5d6476', '#1e222d'
UP, DN = '#089981', '#f23645'
BULL, BEAR, CE = (0.30, 0.69, 0.31), (0.94, 0.33, 0.31), '#d1d4dc'
b = pd.read_pickle('/home/claude/kyw/bars_NQ_all.pkl')
days = sorted(b.tday.unique())[-4:]
g = b[b.tday.isin(days)].set_index('ts')
x = g.resample('15min').agg(dict(Open='first', High='max', Low='min', Close='last')).dropna()
ix = lambda t: float(np.searchsorted(x.index, t))
n = len(x)


def fpfvg(day):
    d = b[(b.tday == day)].set_index('ts')
    s = d[(d.hm >= 930) & (d.hm < 1600)]
    t0 = s.index[0]
    for k in range(2, len(s)):
        if (s.index[k] - t0) >= pd.Timedelta(minutes=30):
            return None
        c, a = s.iloc[k], s.iloc[k - 2]
        if c.Low > a.High:
            return dict(t0=s.index[k - 2], top=c.Low, bot=a.High, bull=True, day=day)
        if c.High < a.Low:
            return dict(t0=s.index[k - 2], top=a.Low, bot=c.High, bull=False, day=day)
    return None


gaps = [f for f in (fpfvg(d) for d in days) if f]
fig = plt.figure(figsize=(18, 9.6), dpi=100, facecolor=BG)
ax = fig.add_axes([0.02, 0.06, 0.9, 0.82])
ax.set_facecolor(BG)
for s_ in ax.spines.values():
    s_.set_visible(False)
ax.yaxis.tick_right()
ax.tick_params(axis='y', colors=MU, labelsize=8.5)
ax.tick_params(axis='x', length=0)
ax.grid(color=GRID, lw=0.7, zorder=0)
lo, hi = x.Low.min(), x.High.max()
pad = (hi - lo) * 0.06
ax.set_xlim(-2, n + 22)
ax.set_ylim(lo - pad, hi + pad)
ticks = [i for i, t in enumerate(x.index) if t.hour in (0, 9, 16) and t.minute == 0 and i > 0]
ax.set_xticks(ticks)
ax.set_xticklabels([x.index[i].strftime('%a %H:%M' if x.index[i].hour == 9 else '%H:%M') for i in ticks], color=MU, fontsize=8)
for i, (t, r) in enumerate(x.iterrows()):
    c = UP if r.Close >= r.Open else DN
    ax.plot([i, i], [r.Low, r.High], color=c, lw=0.7, zorder=3)
    ax.add_patch(Rectangle((i - 0.33, min(r.Open, r.Close)), 0.66, max(abs(r.Close - r.Open), 0.5), fc=c, ec=c, lw=0.2, zorder=4))
xe = n - 1
for f in gaps:
    a = ix(f['t0'])
    col = BULL if f['bull'] else BEAR
    ax.add_patch(Rectangle((a, f['bot']), xe - a, f['top'] - f['bot'], fc=col + (0.28,), ec=col + (0.7,), lw=0.8, zorder=2))
    ce = (f['top'] + f['bot']) / 2
    ax.plot([a, xe], [ce, ce], color=CE, lw=0.9, ls=':', zorder=2)
    ax.text(xe + 0.6, f['top'], f['t0'].strftime('%H:%M %d/%m') + ' First presented', color=TX, fontsize=8, va='bottom')
    # where the other three settings would have stopped this day's box
    d = f['day']
    for (hh, mm, lab) in ((11, 0, 'cut-off 11:00'), (16, 0, 'session end 16:00'), (16, 59, "day's last candle 16:59")):
        t = pd.Timestamp(d) + pd.Timedelta(hours=hh, minutes=mm)
        xi = ix(t)
        ax.plot([xi, xi], [f['bot'], f['top']], color=SUB, lw=1.0, zorder=5)
    if f is gaps[0]:
        for (hh, mm, lab, up, ha) in ((11, 0, 'cut-off 11:00', True, 'center'), (16, 0, '16:00', True, 'right'), (16, 59, '16:59', False, 'left')):
            xi = ix(pd.Timestamp(d) + pd.Timedelta(hours=hh, minutes=mm))
            yv = f['top'] + (hi - lo) * 0.012 if up else f['bot'] - (hi - lo) * 0.012
            ax.text(xi, yv, lab, color=SUB, fontsize=7.5, ha=ha, va='bottom' if up else 'top')
fig.text(0.02, 0.955, 'Byakugan · first presented FVG, FVG length "To the present": every kept day\'s FVG and its CE run to the latest bar',
         color=TX, fontsize=13, weight='bold')
fig.text(0.02, 0.925, 'NQ1! 15-minute, Tue 6 – Fri 9 Oct 2026 (end of data). Ticks on each box mark where the other settings stop it: Byakugan cut-off (11:00), '
         'Until its session ends (16:00), To the day\'s last candle (16:59). TradingView rendering will differ.', color=SUB, fontsize=9)
plt.savefig(OUT, dpi=100, facecolor=BG)
print(OUT, [(f['t0'], f['bull'], round(f['top'] - f['bot'], 2)) for f in gaps])
