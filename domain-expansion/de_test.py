"""Domain Expansion re-test (Oct 2026). NQ 1-min, 2018 + 2022-Aug 2026. Train 2018-24 / test 2025-26.
LOR = 02:00-02:29 ET. Entry window 02:30-02:49 (20 min). Exit at the 04:59 close (end of London). Cost 1 pt round trip.
Rules fixed before looking at results:
  A  stop-entry: first touch of LOR high (long) / low (short) inside the window, fill at the boundary (or the bar open if it gaps through)
  B  close-confirm: enter at the close of the first 1-min bar that closes beyond a boundary inside the window
  C  retest: after B confirms, limit at the broken boundary, filled only if price returns to it inside the window
  Stop = opposite LOR boundary for all three. Same-bar stop/target ambiguity -> stop (conservative).
  Octant filter (doc): long only if 02:29 close octant >= 0.625, short only if <= 0.375.
  Terminus target (doc): 1.84R beyond the broken boundary (1.39R if Asia's extreme in that direction was swept in the LOR, else 2.15R).
Benchmarks: always-long from the same entry time to 04:59 on the same days; symmetric race (+1R vs -1R from entry) vs 50%;
gambler's-ruin check for the octant table: a driftless walk hits the high first with probability = octant."""
import pandas as pd, numpy as np
b = pd.read_pickle('/home/claude/twin/bars_NQ.pkl').sort_values('ts')
COST = 1.0
rows = []
for d, x in b.groupby('tday'):
    lor = x[(x.hm >= 200) & (x.hm <= 229)]
    post = x[(x.hm >= 230) & (x.hm <= 459)]
    asia = x[(x.hm >= 2000) | (x.hm <= 0)]
    if len(lor) < 28 or len(post) < 140 or post.hm.iloc[0] != 230 or post.hm.iloc[-1] != 459 or len(asia) < 100:
        continue
    H, L = lor.High.max(), lor.Low.min(); R = H - L
    if R <= 0: continue
    c0 = lor.Close.iloc[-1]; octv = (c0 - L) / R
    tH = lor.ts[lor.High.idxmax()]; tL = lor.ts[lor.Low.idxmin()]
    aH, aL = asia.High.max(), asia.Low.min()
    asia_sw_up = H > aH; asia_sw_dn = L < aL
    o, h, l, c, hm = post.Open.values, post.High.values, post.Low.values, post.Close.values, post.hm.values
    n = len(post); win = hm <= 249
    # first boundary hit after 02:30 (any time to 04:59) for the octant check
    up_i = np.argmax(h > H) if (h > H).any() else n
    dn_i = np.argmax(l < L) if (l < L).any() else n
    first = 1 if up_i < dn_i else (-1 if dn_i < up_i else 0)
    rec = dict(tday=d, year=d.year, R=R, octv=octv, first=first, both_same=(up_i == dn_i and up_i < n),
               long_bench_0230=c[-1] - o[0])
    def run(i, side, entry, tgtR=None):
        """from bar i (entry bar), stop at opposite boundary, optional target, else exit 04:59 close"""
        stop = L if side > 0 else H
        tgt = None if tgtR is None else (H + tgtR * R if side > 0 else L - tgtR * R)
        for j in range(i, n):
            hit_stop = (l[j] <= stop) if side > 0 else (h[j] >= stop)
            hit_tgt = tgt is not None and ((h[j] >= tgt) if side > 0 else (l[j] <= tgt))
            if hit_stop:
                return side * (stop - entry) - COST, 'stop'
            if hit_tgt:
                return side * (tgt - entry) - COST, 'tgt'
        return side * (c[-1] - entry) - COST, 'time'
    def race(i, side, entry):
        up, dn = entry + R, entry - R
        for j in range(i + 1, n):
            u, w = h[j] >= up, l[j] <= dn
            if u and w: return np.nan
            if u: return 1.0 if side > 0 else 0.0
            if w: return 0.0 if side > 0 else 1.0
        return np.nan
    # A: stop-entry at first touch inside the window
    iu = np.argmax(win & (h > H)) if (win & (h > H)).any() else None
    idn = np.argmax(win & (l < L)) if (win & (l < L)).any() else None
    if iu is not None or idn is not None:
        if iu is not None and idn is not None and iu == idn:
            rec['A_amb'] = True
        else:
            if idn is None or (iu is not None and iu < idn):
                i, side, e = iu, 1, max(H, o[iu])
            else:
                i, side, e = idn, -1, min(L, o[idn])
            sw = asia_sw_up if side > 0 else asia_sw_dn
            pnl, how = run(i, side, e)
            pnlT, howT = run(i, side, e, 1.84)
            pnlA, _ = run(i, side, e, 1.39 if sw else 2.15)
            rec.update(A_side=side, A_pnl=pnl, A_how=how, A_pnlT=pnlT, A_howT=howT, A_pnlAsia=pnlA,
                       A_okOct=(octv >= 0.625) if side > 0 else (octv <= 0.375),
                       A_bench=c[-1] - e,  # always-long from the same price/time
                       A_race=race(i, side, e), A_mfe=(h[i:].max() - H) / R if side > 0 else (L - l[i:].min()) / R)
    # B: close-confirm
    cu = win & (c > H); cd = win & (c < L)
    ib = None
    if cu.any() or cd.any():
        iu2 = np.argmax(cu) if cu.any() else n; id2 = np.argmax(cd) if cd.any() else n
        ib, sideB = (iu2, 1) if iu2 < id2 else (id2, -1)
        pnl, how = run(ib + 1, sideB, c[ib]) if ib + 1 < n else (np.nan, 'none')
        rec.update(B_side=sideB, B_pnl=pnl, B_how=how, B_bench=c[-1] - c[ib], B_risk=abs(c[ib] - (L if sideB > 0 else H)),
                   B_okOct=(octv >= 0.625) if sideB > 0 else (octv <= 0.375), B_race=race(ib, sideB, c[ib]))
        # C: retest limit at the broken boundary inside the window
        lvl = H if sideB > 0 else L
        for j in range(ib + 1, n):
            if hm[j] > 249: break
            if (l[j] <= lvl) if sideB > 0 else (h[j] >= lvl):
                e = min(lvl, o[j]) if sideB > 0 else max(lvl, o[j])
                pnl, how = run(j, sideB, e)
                rec.update(C_side=sideB, C_pnl=pnl, C_how=how, C_bench=c[-1] - e,
                           C_okOct=(octv >= 0.625) if sideB > 0 else (octv <= 0.375))
                break
    rows.append(rec)
D = pd.DataFrame(rows); D['sp'] = np.where(D.year >= 2025, 'test', 'train')
D.to_pickle('/home/claude/byk/de_D.pkl')
print('days', len(D), D.groupby('sp').size().to_dict())
