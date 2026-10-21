"""HYDRA-style sift of macro candidates for the calendar indicators. Train 2018–24, locked test 2025–26.
A. Range: does a macro feature add to a day-range forecast beyond ADR20 + recent ranges + weekday + event days?
   Target log(trading-day range ÷ ADR20); OLS fit on 2018–24, scored out of sample on 2025–26 (R² vs the train mean).
B. Effect sizes in plain terms: median range ÷ ADR20 by feature tercile (cut-offs fixed on 2018–24), train and test.
C. Direction: trading-day up-close by feature state (expect nothing; reported so the card does not imply direction).
D. CPI days: VIX into and through the release.
Writes macro_tests.json."""
import pandas as pd, numpy as np, json
from scipy import stats
EV = ['FOMC', 'NFP', 'CPI', 'POST', 'PRE', 'HOLLOW']
def wilson(k, n, z=1.96):
    if n == 0: return np.nan, np.nan
    p = k / n; d = 1 + z * z / n; c = (p + z * z / (2 * n)) / d; h = z * np.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return p, h
def design(T, feats):
    X = pd.DataFrame(index=T.index)
    for k in (1, 2, 3): X[f'lR{k}'] = T[f'lR{k}']
    for d in range(1, 5): X[f'd{d}'] = (T.dow == d).astype(float)
    for e in EV: X[e] = (T.type == e).astype(float)
    for f in feats:
        if f == 'month':
            for m in range(2, 13): X[f'm{m}'] = (T.mon == m).astype(float)
        elif f == 'vixReg':
            for lo, hi, nm in ((15, 20, 'v15'), (20, 25, 'v20'), (25, 999, 'v25')): X[nm] = ((T.vix >= lo) & (T.vix < hi)).astype(float)
        elif f == 'dx4sign': X[f] = np.sign(T.dx4)
        elif f == 'y10sign': X[f] = np.sign(T.y10m)
        else: X[f] = T[f]
    X['c'] = 1.0
    return X
OUT = {}
for root in ('NQ', 'ES'):
    T = pd.read_pickle(f'macro_{root}.pkl'); T = T[T.R > 0].copy()
    tr = T.year <= 2024; te = T.year >= 2025
    print('=' * 100, f'\n{root}: train {tr.sum()} days · test {te.sum()} days')
    R = OUT.setdefault(root, {})
    # ── A. incremental out-of-sample R²
    def fit(feats, target='lR'):
        X = design(T, feats); ok = X.notna().all(1) & T[target].notna()
        a, b = ok & tr, ok & te
        beta, *_ = np.linalg.lstsq(X[a].values, T.loc[a, target].values, rcond=None)
        pred = X[b].values @ beta; y = T.loc[b, target].values
        r2 = 1 - ((y - pred) ** 2).sum() / ((y - T.loc[a, target].mean()) ** 2).sum()
        pin = X[a].values @ beta; yin = T.loc[a, target].values
        r2in = 1 - ((yin - pin) ** 2).sum() / ((yin - yin.mean()) ** 2).sum()
        return r2, r2in, dict(zip(X.columns, beta)), b.sum()
    base = fit([])
    print(f' A. range model (log TD range ÷ ADR20): base = 3 lags + weekday + event days · in-sample R² {base[1]:.3f} · out-of-sample 2025–26 R² {base[0]:.3f}')
    R['base'] = dict(oos=base[0], ins=base[1])
    cands = {'vix': 'VIX level (prior close)', 'ivrv': 'VIX-implied σ vs ADR20', 'vspike': 'VIX vs its 20-day mean', 'vrank': 'VIX 1-year percentile',
             'vixReg': 'VIX regime <15/15–20/20–25/25+', 'dx4': 'DXY 4-week change', 'dx4sign': 'DXY 4-week direction', 'dx1': 'DXY last-week change',
             'dvol': 'DXY 20-day vol vs its year', 'y10m': '10Y last-month change', 'y10sign': '10Y last-month direction', 'y10': '10Y level', 'month': 'month of year (range seasonality)'}
    R['add'] = {}
    for f, lab in cands.items():
        r2, r2in, beta, n = fit([f])
        coef = beta.get(f, np.nan) if f not in ('month', 'vixReg') else np.nan
        print(f'    + {lab:34s} OOS R² {r2:.3f} (Δ {r2 - base[0]:+.3f}) · in-sample Δ {r2in - base[1]:+.3f}' + ('' if np.isnan(coef) else f' · coef {coef:+.3f}'))
        R['add'][f] = dict(lab=lab, oos=r2, d_oos=r2 - base[0], d_ins=r2in - base[1], coef=None if np.isnan(coef) else coef)
    best = fit(['ivrv', 'vspike'])
    print(f'    + VIX-implied σ vs ADR20 and VIX spike together: OOS R² {best[0]:.3f} (Δ {best[0] - base[0]:+.3f})')
    allm = fit(['ivrv', 'vspike', 'dx4', 'dvol', 'y10m', 'month'])
    print(f'    + everything: OOS R² {allm[0]:.3f} (Δ {allm[0] - base[0]:+.3f})')
    R['vixBoth'] = best[0] - base[0]; R['all'] = allm[0] - base[0]
    # ── B. effect sizes by tercile (cut-offs from 2018–24)
    print(' B. median day range ÷ ADR20 by tercile (cut-offs on 2018–24) · 2018–24 | 2025–26')
    R['terc'] = {}
    for f in ('vix', 'ivrv', 'vspike', 'vrank', 'dx4', 'dvol', 'y10m'):
        q = T.loc[tr, f].quantile([1 / 3, 2 / 3]).values
        cut = lambda s: pd.cut(s, [-np.inf, q[0], q[1], np.inf], labels=['low', 'mid', 'high'])
        row = {}
        for nm, m in (('tr', tr), ('te', te)):
            g = T[m].groupby(cut(T.loc[m, f]), observed=True).R.median()
            row[nm] = [round(float(g.get(k, np.nan)), 3) for k in ('low', 'mid', 'high')]
        rho_tr = stats.spearmanr(T.loc[tr, f], T.loc[tr, 'R'], nan_policy='omit')[0]; rho_te = stats.spearmanr(T.loc[te, f], T.loc[te, 'R'], nan_policy='omit')[0]
        print(f'    {f:7s} cut {q[0]:+.3f} / {q[1]:+.3f} · {row["tr"]} | {row["te"]} · Spearman {rho_tr:+.2f} | {rho_te:+.2f}')
        R['terc'][f] = dict(cut=[float(q[0]), float(q[1])], **row, rho_tr=rho_tr, rho_te=rho_te)
    # VIX regimes in plain numbers
    print('    VIX regime (prior close): days · median range ÷ ADR20 · up-close, 2018–24 | 2025–26')
    R['reg'] = {}
    for lo, hi in ((0, 15), (15, 20), (20, 25), (25, 30), (30, 999)):
        s = []
        for nm, m in (('tr', tr), ('te', te)):
            g = T[m & (T.vix >= lo) & (T.vix < hi)]
            p, h = wilson(int(g.up.sum()), len(g))
            s.append(dict(n=len(g), R=float(g.R.median()) if len(g) else None, up=p, moe=h))
        lab = f'{lo}–{hi if hi < 999 else "+"}'
        print(f'      VIX {lab:6s} n {s[0]["n"]:4d} R {s[0]["R"] or 0:.2f} up {s[0]["up"] * 100 if s[0]["n"] else 0:.0f}% | n {s[1]["n"]:3d} R {s[1]["R"] or 0:.2f} up {(s[1]["up"] or 0) * 100:.0f}%')
        R['reg'][lab] = s
    # VIX-implied move calibration: realised trading-day range % ÷ (VIX/√252)
    imp = T.vix / np.sqrt(252) / 100
    ratio = T.rng / imp
    print(f'    realised day range ÷ VIX-implied daily σ: median {ratio[tr].median():.2f} (2018–24) | {ratio[te].median():.2f} (2025–26); by year ' + ' '.join(f'{y}:{ratio[T.year == y].median():.2f}' for y in sorted(T.year.unique())))
    a = np.log(T.rng); c1 = np.corrcoef(a[te], np.log(imp[te]))[0, 1]; c2 = np.corrcoef(a[te], np.log(T.adr[te]))[0, 1]
    print(f'    2025–26 correlation of log day range with log VIX-implied σ {c1:.3f} vs with log ADR20 {c2:.3f}')
    R['impl'] = dict(ratio_tr=float(ratio[tr].median()), ratio_te=float(ratio[te].median()), c_vix=c1, c_adr=c2,
                     q_tr=[float(x) for x in ratio[tr].quantile([.1, .25, .5, .75, .9])], q_te=[float(x) for x in ratio[te].quantile([.1, .25, .5, .75, .9])])
    # ── C. direction
    print(' C. trading-day up-close by state · 2018–24 | 2025–26')
    R['dir'] = {}
    for f, lab in (('dx4', 'DXY 4-week'), ('y10m', '10Y last month'), ('vspike', 'VIX vs 20-day mean'), ('dx1', 'DXY last week')):
        s = []
        for nm, m in (('tr', tr), ('te', te)):
            g = T[m].dropna(subset=[f]); u = g[g[f] > 0]; d = g[g[f] <= 0]
            pu, hu = wilson(int(u.up.sum()), len(u)); pd_, hd = wilson(int(d.up.sum()), len(d))
            s.append(dict(up_if_rise=pu, moe_r=hu, n_r=len(u), up_if_fall=pd_, moe_f=hd, n_f=len(d)))
        print(f'    {lab:20s} rose → up {s[0]["up_if_rise"] * 100:.0f}% fell → up {s[0]["up_if_fall"] * 100:.0f}% | rose {s[1]["up_if_rise"] * 100:.0f}% fell {s[1]["up_if_fall"] * 100:.0f}%')
        R['dir'][f] = s
    # same-day VIX direction vs NQ direction (describes the day)
    ok = T.dropna(subset=['vixChg'])
    for nm, m in (('2018–24', tr), ('2025–26', te)):
        g = ok[m.reindex(ok.index)]; vd = g.vixChg < 0
        print(f'    same day {nm}: NQ closed up on {g[vd].up.mean() * 100:.0f}% of VIX-down days (n{vd.sum()}) vs {g[~vd].up.mean() * 100:.0f}% of VIX-up days (n{(~vd).sum()})')
    # ── D. CPI days and VIX
    print(' D. VIX and CPI days')
    R['cpi'] = {}
    for ty in ('CPI', 'NFP', 'FOMC', 'NORMAL'):
        s = []
        for nm, m in (('tr', tr), ('te', te)):
            g = T[m & (T.type == ty)].dropna(subset=['vixChg'])
            k = int((g.vixChg < 0).sum()); p, h = wilson(k, len(g))
            s.append(dict(n=len(g), fell=p, moe=h, med=float(g.vixChg.median()) if len(g) else None))
        print(f'    {ty:6s} VIX fell on the day: {s[0]["fell"] * 100:.0f}% ±{s[0]["moe"] * 100:.0f} (n{s[0]["n"]}, median {s[0]["med"] * 100:+.1f}%) | {s[1]["fell"] * 100:.0f}% ±{s[1]["moe"] * 100:.0f} (n{s[1]["n"]}, median {s[1]["med"] * 100:+.1f}%)')
        R['cpi'][ty] = s
    # CPI-day range by VIX tercile and by pre-release VIX build (prior close ÷ 5 days earlier)
    T['vbuild'] = np.log(T.vix / T.vix.shift(5))
    for f in ('vix', 'vspike', 'vbuild'):
        g = T[T.type == 'CPI'].dropna(subset=[f])
        q = g[f].quantile([1 / 3, 2 / 3]).values; c = pd.cut(g[f], [-np.inf, q[0], q[1], np.inf], labels=['low', 'mid', 'high'])
        med = g.groupby(c, observed=True).R.median()
        rho, p = stats.spearmanr(g[f], g.R)
        rtr = stats.spearmanr(g[g.year <= 2024][f], g[g.year <= 2024].R)[0]; rte = stats.spearmanr(g[g.year >= 2025][f], g[g.year >= 2025].R)[0]
        print(f'    CPI range ÷ ADR20 by {f:6s} tercile {med.get("low"):.2f} / {med.get("mid"):.2f} / {med.get("high"):.2f} · Spearman {rho:+.2f} (p {p:.3f}; 2018–24 {rtr:+.2f}, 2025–26 {rte:+.2f}) n{len(g)}')
        R['cpi'][f'R_by_{f}'] = dict(t=[float(med.get(k)) for k in ('low', 'mid', 'high')], rho=rho, p=p, rtr=rtr, rte=rte)
json.dump(OUT, open('macro_tests.json', 'w'), indent=1, default=float)
