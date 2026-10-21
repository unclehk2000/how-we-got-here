"""FedWatch-style meeting probabilities from 30-day fed funds futures (CBOT ZQ), the same steps the Pine card uses.

A ZQ contract settles to 100 − the month's average effective fed funds rate (EFFR). For each FOMC meeting month:
  · next month has no meeting → its average is the rate after the meeting (end); the start rate is solved from the
    meeting month's average;
  · else the prior month has no meeting → its average is the start rate; the end rate is solved;
  · else the start rate is the previous meeting month's end rate (chain), and the end rate is solved.
The decision takes effect the day after the meeting, so a meeting on day d of an N-day month splits it d / N − d.
The change (end − start) ÷ 25bp gives the odds of the two nearest move sizes; later meetings combine into a
probability tree (each meeting's two outcomes, paths summed by total change)."""
import calendar, datetime as dt
import numpy as np

STEP = 0.25


def month_add(y, m, k):
    t = y * 12 + (m - 1) + k
    return t // 12, t % 12 + 1


def meeting_day(fomc, y, m):
    for d in fomc:
        if d.year == y and d.month == m:
            return d.day
    return 0


def month_grid(today, n=10):
    """the n calendar months starting the month before today's"""
    return [month_add(today.year, today.month, i - 1) for i in range(n)]


def starts_ends(avg, grid, fomc):
    """avg[i] = 100 − ZQ price of month grid[i] (in %). CME's rule, checked on its 12 Oct 2026 screen: the month after a
    run of meeting months anchors the last meeting's end rate; working backward each meeting's start rate is solved from
    its own contract and is the previous meeting's end; the first meeting of a run starts at the anchor month before it
    (solved from its own contract instead when that contract is missing)."""
    n = len(grid)
    s = [np.nan] * n
    e = [np.nan] * n
    md = [meeting_day(fomc, y, m) for y, m in grid]
    for i in range(n - 1, -1, -1):
        d = md[i]
        if d == 0 or np.isnan(avg[i]) or i + 1 >= n:
            continue
        e_ = avg[i + 1] if md[i + 1] == 0 else s[i + 1]
        if np.isnan(e_):
            continue
        N = calendar.monthrange(*grid[i])[1]
        e[i] = e_
        s[i] = avg[i - 1] if i > 0 and md[i - 1] == 0 and not np.isnan(avg[i - 1]) else (avg[i] * N - e_ * (N - d)) / d
    return s, e, md


def node(delta):
    """two outcomes (in 25bp steps) and their odds for one meeting's expected change"""
    st = delta / STEP
    k = np.floor(abs(st))
    r = abs(st) - k
    sg = 1 if st >= 0 else -1
    return [(int(sg * k), 1 - r), (int(sg * (k + 1)), r)]


def tree(deltas, span=20):
    """cumulative distribution over total 25bp steps after each meeting"""
    p = np.zeros(2 * span + 1)
    p[span] = 1.0
    out = []
    for dlt in deltas:
        q = np.zeros_like(p)
        for (k, w) in node(dlt):
            if w <= 0:
                continue
            if k >= 0:
                q[k:] += w * p[:len(p) - k]
            else:
                q[:k] += w * p[-k:]
        p = q
        out.append(p.copy())
    return out


def fedwatch(prices, grid, fomc, today, after_statement=False, k_meet=4):
    """prices: ZQ prices for grid months. Returns the next k meetings with start / end, odds and cumulative path."""
    avg = [100.0 - p if p == p else np.nan for p in prices]
    s, e, md = starts_ends(avg, grid, fomc)
    up = []
    for i, (y, m) in enumerate(grid):
        d = md[i]
        if d == 0:
            continue
        day = dt.date(y, m, d)
        if day > today or (day == today and not after_statement):
            up.append(i)
    up = up[:k_meet]
    for j, i in enumerate(up):                     # stop at the first meeting the contracts can't price
        if np.isnan(s[i]) or np.isnan(e[i]):
            up = up[:j]; break
    if not up or np.isnan(s[up[0]]):
        return None
    base = s[up[0]]
    lower0 = np.floor((base + 1e-4) / STEP) * STEP
    deltas = [e[i] - s[i] for i in up]
    dist = tree(deltas)
    rows = []
    for j, i in enumerate(up):
        y, m = grid[i]
        rows.append(dict(meeting=dt.date(y, m, md[i]), start=s[i], end=e[i], delta_bp=100 * deltas[j],
                         cum_bp=100 * (e[i] - base), dist=dist[j]))
    return dict(lower0=lower0, base=base, rows=rows)


def rng(lower0, k):
    lo = lower0 + k * STEP
    return f'{lo * 100:.0f}–{(lo + STEP) * 100:.0f}'
