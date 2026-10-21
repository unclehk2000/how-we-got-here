"""Overnight liquidity vs the London expansion (NQ 1-min, 2018 + 2022-26; train <=2024, test 2025-26).
EQH/EQL: pivots left 10 / right 2 on the 18:00-02:29 bars; a new pivot within 0.03% of any earlier pivot (same side)
forms an equal-highs/lows zone; level = zone top (EQH) / bottom (EQL); swept once traded through after confirmation.
Also ordinary (single) pivots that are not part of an equal pair, as the placebo.
Peak-volume level: close of the highest-volume 1-min bar since 18:00 (LuxAlgo TPAL with sensitivity 0), read at 02:29.
Outcomes 02:30 -> 04:59: which levels get hit; first break side of the 02:00-02:29 range; London extreme side; 04:59 vs 02:29."""
import pandas as pd, numpy as np
b = pd.read_pickle('/home/claude/twin/bars_NQ.pkl').sort_values('ts')
import sys
L_, R_, THR = 10, 2, float(sys.argv[1]) if len(sys.argv) > 1 else 0.03
TAG = sys.argv[2] if len(sys.argv) > 2 else ""
lv_rows, day_rows = [], []
for d, x in b.groupby('tday'):
    on = pd.concat([x[x.hm >= 1800], x[x.hm <= 229]])
    post = x[(x.hm >= 230) & (x.hm <= 459)]
    lor = x[(x.hm >= 200) & (x.hm <= 229)]
    if len(on) < 400 or len(post) < 140 or len(lor) < 28 or post.hm.iloc[-1] != 459: continue
    h, l, v, c = on.High.values, on.Low.values, on.Volume.values, on.Close.values
    n = len(on); P = c[-1]
    H, Lr = lor.High.max(), lor.Low.min(); R = H - Lr
    if R <= 0: continue
    ph, pl = [], []          # (price, conf_idx)
    eqh, eql = [], []        # zones: [level, conf_idx, swept]
    singles_h, singles_l = [], []
    for i in range(L_, n - R_):
        win_h = h[i - L_: i + R_ + 1]
        if h[i] == win_h.max() and h[i] > h[i - L_: i].max() and h[i] >= h[i + 1: i + R_ + 1].max():
            conf = i + R_
            match = next((p for p in reversed(ph) if abs(h[i] - p[0]) / p[0] * 100 <= THR), None)
            if match: eqh.append([max(h[i], match[0]), conf])
            ph.append((h[i], conf))
        win_l = l[i - L_: i + R_ + 1]
        if l[i] == win_l.min() and l[i] < l[i - L_: i].min() and l[i] <= l[i + 1: i + R_ + 1].min():
            conf = i + R_
            match = next((p for p in reversed(pl) if abs(l[i] - p[0]) / p[0] * 100 <= THR), None)
            if match: eql.append([min(l[i], match[0]), conf])
            pl.append((l[i], conf))
    def unswept_high(lev, conf): return not (h[conf + 1:] > lev).any() if conf + 1 < n else True
    def unswept_low(lev, conf):  return not (l[conf + 1:] < lev).any() if conf + 1 < n else True
    eq_prices_h = {round(z[0], 4) for z in eqh}; eq_prices_l = {round(z[0], 4) for z in eql}
    ph_, pl_ = post.High.values, post.Low.values
    def first_hit(lev, up):
        idx = np.where(ph_ >= lev)[0] if up else np.where(pl_ <= lev)[0]
        return idx[0] if len(idx) else None
    act_eqh = [z[0] for z in eqh if z[0] > P and unswept_high(*z)]
    act_eql = [z[0] for z in eql if z[0] < P and unswept_low(*z)]
    for lev, conf in ph:
        if lev > P and unswept_high(lev, conf):
            isEq = any(abs(lev - z) / z * 100 <= THR for z in act_eqh)
            lv_rows.append(dict(tday=d, year=d.year, up=1, eq=isEq, dist=100 * (lev - P) / P, distR=(lev - P) / R, hit=first_hit(lev, True) is not None))
    for lev, conf in pl:
        if lev < P and unswept_low(lev, conf):
            isEq = any(abs(lev - z) / z * 100 <= THR for z in act_eql)
            lv_rows.append(dict(tday=d, year=d.year, up=0, eq=isEq, dist=100 * (P - lev) / P, distR=(P - lev) / R, hit=first_hit(lev, False) is not None))
    # peak-volume level (close of the max-volume bar since 18:00)
    k = int(np.argmax(v)); pvl = c[k]; pv_hm = on.hm.values[k]
    # outcomes
    iu = first_hit(H + 1e-9, True); idn = first_hit(Lr - 1e-9, False)
    brk = 0 if iu is None and idn is None else (1 if idn is None or (iu is not None and iu < idn) else -1)
    upX = (ph_.max() - H) / R; dnX = (Lr - pl_.min()) / R
    c5 = post.Close.values[-1]
    nu = min(act_eqh, default=np.nan); nd = max(act_eql, default=np.nan)
    day_rows.append(dict(tday=d, year=d.year, P=P, H=H, L=Lr, R=R, brk=brk, ext_dir=1 if upX >= dnX else -1, sd2=max(upX, dnX) >= 2,
                         ret=c5 - P, pvl=pvl, pv_hm=pv_hm, above_pvl=P > pvl, pvl_distR=(P - pvl) / R,
                         eqh_up=(nu - P) / R if not np.isnan(nu) else np.nan, eql_dn=(P - nd) / R if not np.isnan(nd) else np.nan,
                         octv=(P - Lr) / R))
LV = pd.DataFrame(lv_rows); DY = pd.DataFrame(day_rows)
for Z in (LV, DY): Z['sp'] = np.where(Z.year >= 2025, 'test', 'train')
LV.to_pickle(f'/home/claude/byk/de_LV{TAG}.pkl'); DY.to_pickle(f'/home/claude/byk/de_DY{TAG}.pkl')
print('levels', LV.shape, 'EQ share', round(LV['eq'].mean(), 3), '| days', len(DY))
