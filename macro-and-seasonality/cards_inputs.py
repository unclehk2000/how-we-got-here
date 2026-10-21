"""Inputs for the rebuilt cards.
1. DXY battery: which 'how far along today' measure lines up with the contrarian rule (last 3 years, discovery /
   confirmation)? (a) |net move| ÷ 20-day average |net move| (the tested rule), (b) today's range ÷ ATR20 with the
   direction of the net move, (c) |net move| ÷ ATR20. DXY ATR20 typical size in points and %.
2. VIX vs its 20-day average: buckets over 2018–26 combined (and by period) for NQ / ES, share of days above ADR.
3. Per-event-day records for the tally mode (CPI, NFP, FOMC): trading-day and RTH close direction, RTH gap in points
   and % (09:30 open − prior 16:14 close).
4. Weekly / monthly octant of the trading-day open (where price starts inside this week's / month's range so far) on
   CPI days vs normal days: does premium / discount say anything about the close? (locator only unless it holds)
Writes cards_inputs.json and event_days_{NQ,ES}.csv."""
import pandas as pd, numpy as np, json
from scipy import stats
HM = '/home/claude/hm/'
W0, C0 = pd.Timestamp('2023-10-01'), pd.Timestamp('2025-10-01')
def wilson(k, n, z=1.96):
    if n == 0: return np.nan, np.nan
    p = k / n; d = 1 + z * z / n; c = (p + z * z / (2 * n)) / d; h = z * np.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return p, h
OUT = {}
# ── 1. DXY battery
f = pd.read_csv('/mnt/user-data/uploads/DXY_2023_2026_5min_continuous.csv')
f['ts'] = pd.to_datetime(f.Date + ' ' + f.Time) + pd.Timedelta(hours=1); f = f.sort_values('ts')
f['tday'] = (f.ts + pd.Timedelta(hours=6)).dt.normalize()
rows = []
for td, g in f.groupby('tday'):
    if td.dayofweek >= 5: continue
    c = g.Contract.value_counts().index[0]; g = g[g.Contract == c]
    if len(g) < 150: continue
    rows.append(dict(tday=td, o=g.Open.iloc[0], h=g.High.max(), l=g.Low.min(), c=g.Close.iloc[-1]))
DX = pd.DataFrame(rows).set_index('tday')
DX['net'] = DX.c - DX.o; DX['rng'] = DX.h - DX.l
DX['tr'] = np.maximum(DX.h, DX.c.shift(1)) - np.minimum(DX.l, DX.c.shift(1))
DX['atr'] = DX.tr.shift(1).rolling(20).mean(); DX['avgnet'] = DX.net.abs().shift(1).rolling(20).mean()
DX['a'] = DX.net.abs() / DX.avgnet; DX['b'] = DX.rng / DX.atr; DX['c_'] = DX.net.abs() / DX.atr
print(f'DXY ATR20 (last 3 years): median {DX.atr[DX.index >= W0].median():.3f} pts = {(DX.atr / DX.o)[DX.index >= W0].median() * 100:.2f}% · average |net move| {DX.avgnet[DX.index >= W0].median():.3f} pts = {(DX.avgnet / DX.atr)[DX.index >= W0].median():.2f}× ATR')
OUT['dxy'] = dict(atr_pts=float(DX.atr[DX.index >= W0].median()), atr_pct=float((DX.atr / DX.o)[DX.index >= W0].median()), net_over_atr=float((DX.avgnet / DX.atr)[DX.index >= W0].median()))
for root in ('NQ', 'ES'):
    D = pd.read_pickle(HM + f'days_{root}.pkl'); T = D[D.anchor == 'TD'].set_index('tday')
    K = T[['O', 'C']].join(DX, how='inner'); K = K[K.index >= W0]
    dr = np.sign(K.C - K.O); opp = (dr == -np.sign(K.net)).astype(float).where((dr != 0) & (K.net != 0))
    print(f'\n{root}: NQ-other-way by DXY measure (discovery Oct23–Sep25 | confirmation Oct25–Aug26 | all · other days)')
    res = {}
    for col, lab, ths in (('a', '|net| ÷ avg |net|', (1.0,)), ('b', 'range ÷ ATR20', (0.8, 1.0, 1.2)), ('c_', '|net| ÷ ATR20', (0.4, 0.5, 0.6))):
        for th in ths:
            e = (K[col] >= th) & opp.notna(); o = (K[col] < th) & opp.notna()
            s = []
            for m in (K.index < C0, K.index >= C0, K.index >= W0):
                k, n = int(opp[e & m].sum()), int((e & m).sum()); p, h = wilson(k, n)
                s.append((p, h, n, stats.binomtest(k, n, .5, alternative='greater').pvalue))
            print(f'   {lab:18s} ≥ {th:.1f}: {s[0][0] * 100:.0f}% (n{s[0][2]}, p {s[0][3]:.3f}) | {s[1][0] * 100:.0f}% (n{s[1][2]}, p {s[1][3]:.3f}) | {s[2][0] * 100:.1f}% ±{s[2][1] * 100:.0f} (n{s[2][2]}) · other {opp[o].mean() * 100:.0f}% · share of days {e.mean() * 100:.0f}%')
            res[f'{col}{th}'] = dict(disc=s[0][0], conf=s[1][0], all=s[2][0], moe=s[2][1], n=s[2][2], other=float(opp[o].mean()), share=float(e.mean()))
    OUT[f'dxy_{root}'] = res
# ── 2. VIX buckets, combined 2018–26
for root in ('NQ', 'ES'):
    M = pd.read_pickle(f'macro_{root}.pkl'); M = M.dropna(subset=['vspike'])
    s = M.vspike; rows = {}
    for lab, c in (('hot', s >= np.log(1.10)), ('normal', (s > np.log(0.90)) & (s < np.log(1.10))), ('calm', s <= np.log(0.90))):
        g = M[c]; rows[lab] = dict(R=float(g.R.median()), above=float((g.R > 1).mean()), n=int(len(g)),
                                   R_tr=float(g[g.year <= 2024].R.median()), R_te=float(g[g.year >= 2025].R.median()))
    g = M.dropna(subset=['vixChg']); dn = g.vixChg < 0
    rows['same_day'] = dict(up_if_vix_dn=float(g[dn].up.mean()), up_if_vix_up=float(g[~dn].up.mean()), n=int(len(g)))
    OUT[f'vix_{root}'] = rows
    print(f'\nVIX {root}: ' + ' · '.join(f'{k} {v["R"]:.2f}× ADR (above ADR {v["above"] * 100:.0f}%, n{v["n"]}; {v["R_tr"]:.2f} | {v["R_te"]:.2f})' for k, v in rows.items() if k != 'same_day') + f' · same day: up {rows["same_day"]["up_if_vix_dn"] * 100:.0f}% when VIX fell, {rows["same_day"]["up_if_vix_up"] * 100:.0f}% when it rose')
# ── 3. event-day records
for root in ('NQ', 'ES'):
    P = pd.read_pickle(HM + f'prof_{root}.pkl')
    D = pd.read_pickle(HM + f'days_{root}.pkl'); T = D[D.anchor == 'TD'].set_index('tday')
    E = T[T.type.isin(['CPI', 'NFP', 'FOMC'])][['type', 'O', 'C']].join(P[['rthO', 'rthC', 'prevRthC']], how='left')
    E['td'] = np.sign(E.C - E.O).astype(int); E['rth'] = np.sign(E.rthC - E.rthO).fillna(0).astype(int)
    E['gap'] = (E.rthO - E.prevRthC).round(2); E['gapPct'] = ((E.rthO / E.prevRthC - 1) * 100).round(3)
    E.to_csv(f'event_days_{root}.csv')
    for ty in ('CPI',):
        e = E[E.type == ty]; last12 = e.tail(12)
        print(f'\n{root} {ty}: {len(e)} days · last 12: TD ▲{(last12.td > 0).sum()} ▼{(last12.td < 0).sum()} · RTH ▲{(last12.rth > 0).sum()} ▼{(last12.rth < 0).sum()} · RTH gap mean {last12.gap.mean():+.1f} pts, mean |gap| {last12.gap.abs().mean():.1f} pts ({last12.gapPct.abs().mean():.2f}%)')
        print('   ' + ' '.join(f'{d:%y%m%d}:{"▲" if r.td > 0 else "▼"}{r.gap:+.0f}' for d, r in last12.iterrows()))
# ── 4. octant of the open within this week's / month's range so far, CPI vs normal days
b = None
for root in ('NQ',):
    D = pd.read_pickle(HM + f'days_{root}.pkl'); T = D[D.anchor == 'TD'].set_index('tday').sort_index()
    T['wk'] = T.index.to_period('W-FRI'); T['mo'] = T.index.to_period('M')
    # range so far = prior days of this week / month (before today's open), plus today's open
    for per, col in (('wk', 'oW'), ('mo', 'oM')):
        hi = T.groupby(per).H.transform(lambda x: x.shift(1).cummax()); lo = T.groupby(per).L.transform(lambda x: x.shift(1).cummin())
        hi = np.maximum(hi, T.O); lo = np.minimum(lo, T.O)
        T[col] = ((T.O - lo) / (hi - lo)).where(hi > lo)
    T['upd'] = (T.C > T.O).astype(float)
    print(f'\n{root}: trading-day up-close by where the open sits in the range so far (discount = bottom quarter, premium = top quarter)')
    res = {}
    for col, lab in (('oW', 'week'), ('oM', 'month')):
        for ty in ('CPI', 'NORMAL'):
            g = T[(T.type == ty)].dropna(subset=[col])
            for zone, c in (('discount', g[col] <= 0.25), ('middle', (g[col] > 0.25) & (g[col] < 0.75)), ('premium', g[col] >= 0.75)):
                k, n = int(g[c].upd.sum()), int(c.sum()); p, h = wilson(k, n)
                res[f'{lab}_{ty}_{zone}'] = dict(p=p, moe=h, n=n, R=float(g[c].R.median()))
            print(f'   {lab:5s} {ty:6s} ' + ' · '.join(f'{z} up {res[f"{lab}_{ty}_{z}"]["p"] * 100:.0f}% ±{res[f"{lab}_{ty}_{z}"]["moe"] * 100:.0f} (n{res[f"{lab}_{ty}_{z}"]["n"]}, range {res[f"{lab}_{ty}_{z}"]["R"]:.2f}×)' for z in ('discount', 'middle', 'premium')))
    OUT['octant_NQ'] = res
json.dump(OUT, open('cards_inputs.json', 'w'), indent=1, default=float)
