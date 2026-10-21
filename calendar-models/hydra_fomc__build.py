"""One row per FOMC decision day: what was knowable at 13:59 ET (features) and what followed (targets).
Trading days 18:00 → 17:00 ET, 1-minute front-month bars, ADR20 = mean high − low of the 20 prior trading days."""
import numpy as np, pandas as pd, re, sys
S_FOMC = open('/home/claude/hm/Vizard.pine', encoding='utf-8').read()
FO = sorted(set(pd.Timestamp(x) for x in re.findall(r'20\d{6}', S_FOMC[S_FOMC.index('S_FOMC'):S_FOMC.index('S_CPI')])))
vix = pd.read_csv('/home/claude/mac/vix_daily.csv', parse_dates=['DATE']).set_index('DATE').CLOSE
def build(sym):
    b = pd.read_pickle(f'/home/claude/kyw/bars_{sym}_all.pkl')
    hm = b.hm.values; b = b.assign(m=((hm // 100) * 60 + hm % 100 - 1080) % 1440)          # minutes after 18:00
    D = pd.read_pickle(f'/home/claude/hm/senbon/ctx_{sym}.pkl')                            # O H L C_TD adr MO PDH PDL ATHp per tday
    days = D.index
    G = {td: g for td, g in b.groupby('tday') if td in set(FO) or True}
    # RTH close (16:14) per day for gaps and trends
    rows = []
    M = lambda hh, mm: ((hh * 60 + mm) - 1080) % 1440
    for d in FO:
        if d not in D.index or d not in G: continue
        g = G[d]; mm = g.m.values
        def px_close(hh, mi):                                   # close of the bar at hh:mi (or last before)
            k = np.searchsorted(mm, M(hh, mi), side='right') - 1
            return g.Close.values[k] if k >= 0 else np.nan
        def px_open(hh, mi):
            k = np.searchsorted(mm, M(hh, mi), side='left')
            return g.Open.values[k] if k < len(mm) and mm[k] <= M(hh, mi) + 1 else np.nan
        if mm[0] > 5 or mm[-1] < 1375: continue
        i = D.index.get_loc(d)
        if i < 25 or i + 1 >= len(D): continue
        pv, nx = D.index[i - 1], D.index[i + 1]
        adr = D.adr.iloc[i]
        pre = g[mm < M(14, 0)]; on = g[mm < M(9, 30)]; am = g[(mm >= M(9, 30)) & (mm < M(12, 0))]; post = g[(mm >= M(14, 0)) & (mm <= M(16, 14))]
        o18 = g.Open.values[0]; c0929 = px_close(9, 29); o930 = px_open(9, 30); c1159 = px_close(11, 59); c1359 = px_close(13, 59)
        o1400 = px_open(14, 0); c1429 = px_close(14, 29); o1430 = px_open(14, 30); c1614 = px_close(16, 14)
        Hpre, Lpre = pre.High.max(), pre.Low.min()
        gp = G.get(pv); pc = np.nan
        if gp is not None:
            k = np.searchsorted(gp.m.values, M(16, 14), side='right') - 1; pc = gp.Close.values[k] if k >= 0 else np.nan
        # month and week so far (previous days of the period + today until 13:59)
        mon = D[(D.index.year == d.year) & (D.index.month == d.month) & (D.index < d)]
        mH = max(mon.H.max() if len(mon) else -np.inf, Hpre); mL = min(mon.L.min() if len(mon) else np.inf, Lpre)
        MO = D.MO.iloc[i]
        wk0 = d - pd.Timedelta(days=d.dayofweek)
        wk = D[(D.index >= wk0) & (D.index < d)]
        WO = wk.O.iloc[0] if len(wk) else o18
        wH = max(wk.H.max() if len(wk) else -np.inf, Hpre); wL = min(wk.L.min() if len(wk) else np.inf, Lpre)
        # next trading day NY AM and RTH
        gn = G.get(nx); o930n = c1059n = c1614n = np.nan
        if gn is not None:
            mn = gn.m.values
            kk = np.searchsorted(mn, M(9, 30), side='left'); o930n = gn.Open.values[kk] if kk < len(mn) else np.nan
            kk = np.searchsorted(mn, M(10, 59), side='right') - 1; c1059n = gn.Close.values[kk]
            kk = np.searchsorted(mn, M(16, 14), side='right') - 1; c1614n = gn.Close.values[kk]
        c5 = D.C_TD.iloc[i - 5]; c20 = D.C_TD.iloc[i - 20]
        vp = vix[vix.index < d]; vprev = vp.iloc[-1] if len(vp) else np.nan; vavg = vp.iloc[-20:].mean() if len(vp) >= 20 else np.nan
        A = adr
        r = dict(tday=d, sym=sym, adr=A, price=c1359,
                 # ── features, all known at 13:59
                 moPos=(c1359 - mL) / (mH - mL) if mH > mL else np.nan, dMO=(c1359 - MO) / A,
                 wkPos=(c1359 - wL) / (wH - wL) if wH > wL else np.nan, dWO=(c1359 - WO) / A,
                 pdPos=(c1359 - D.PDL.iloc[i]) / (D.PDH.iloc[i] - D.PDL.iloc[i]), pdRng=(D.PDH.iloc[i] - D.PDL.iloc[i]) / A,
                 pdDir=np.sign(D.C_TD.iloc[i - 1] - D.O.iloc[i - 1]),
                 dayPos=(c1359 - Lpre) / (Hpre - Lpre) if Hpre > Lpre else np.nan, preRng=(Hpre - Lpre) / A, preMove=(c1359 - o18) / A,
                 onRng=(on.High.max() - on.Low.min()) / A, onMove=(c0929 - o18) / A,
                 amRng=(am.High.max() - am.Low.min()) / A, amMove=(c1159 - o930) / A, lunMove=(c1359 - c1159) / A,
                 gap=(o930 - pc) / A, gapFilled=float(((o930 > pc) and (g[(mm >= M(9, 30)) & (mm < M(14, 0))].Low.min() <= pc)) or ((o930 < pc) and (g[(mm >= M(9, 30)) & (mm < M(14, 0))].High.max() >= pc))),
                 t5=(c1359 - c5) / A, t20=(c1359 - c20) / A, adrPct=A / c1359 * 100,
                 athDist=(max(D.ATHp.iloc[i], Hpre) - c1359) / A, vix=vprev, vixRel=vprev / vavg - 1 if vavg else np.nan,
                 sep=float(d.month in (3, 6, 9, 12)), dom=d.day,
                 # ── targets
                 s1=(c1429 - o1400) / A, s2=(c1614 - o1430) / A, post=(c1614 - c1359) / A,
                 postRng=(post.High.max() - post.Low.min()) / A,
                 upExt=(post.High.max() - c1359) / A, dnExt=(c1359 - post.Low.min()) / A,
                 newHi=float(post.High.max() > Hpre), newLo=float(post.Low.min() < Lpre),
                 nAM=(c1059n - o930n) / A, nRTH=(c1614n - o930n) / A)
        rows.append(r)
    F = pd.DataFrame(rows).set_index('tday')
    for k in ('s1', 's2', 'post', 'nAM', 'nRTH'): F['y_' + k] = (F[k] > 0).astype(float).where(F[k].notna())
    F['y_cont'] = ((F.s1 * F.s2) > 0).astype(float)
    F['y_nAMwithS2'] = ((F.nAM * F.s2) > 0).astype(float)
    F['y_nAMwithPost'] = ((F.nAM * F.post) > 0).astype(float)
    F['y_upSide'] = (F.upExt > F.dnExt).astype(float)
    F['m_s1'] = F.s1.abs(); F['m_s2'] = F.s2.abs()
    return F
if __name__ == '__main__':
    for s in ('NQ', 'ES'):
        F = build(s); F.to_pickle(f'/home/claude/hm/hydra_fomc/fomc_{s}.pkl')
        print(s, len(F), 'FOMC days', F.index.min().date(), '→', F.index.max().date(), '| train', (F.index.year <= 2024).sum(), 'test', (F.index.year >= 2025).sum())
        print(F[['moPos', 'dMO', 'pdPos', 'preRng', 's1', 's2', 'post', 'nAM']].describe().round(2).to_string())
