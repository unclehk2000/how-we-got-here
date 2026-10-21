"""Feature / target tables for the three studies, one row per event day, NQ and ES.
  nfp  · NFP release days, snapshot 08:29 (Cero, Model 6)
  wk   · NFP week Mon–Thu (Vizard's day type 5), snapshot 09:29 (Hollow, Model 11)
  fa   · the day after FOMC, snapshot 09:29 (Hollow, Model 12)"""
import numpy as np, pandas as pd, sys
from common import *
sg = lambda x: np.sign(x)
def ce_targets(g, D, i, c, preH, A):
    """the ATH at 08:29 (prior ATH or today's high so far) and the 50% between it and the 08:29 price; touched after 08:30?"""
    ath = max(D.ATHp.iloc[i], preH); ce = (ath + c) / 2
    hR, _ = g.rng(M(8, 30), M(16, 15)); hD, _ = g.rng(M(8, 30), M(17, 0))
    return dict(ath=ath, ce=ce, ceDist=(ce - c) / A, ceRTH=float(hR >= ce) if ath > c else np.nan, ceDay=float(hD >= ce) if ath > c else np.nan,
                athRTH=float(hR >= ath) if ath > c else np.nan)
def build(sym):
    G = days(sym); D = ctx(sym); T = day_type(D.index)
    idx = list(D.index); rows = {'nfp': [], 'wk': [], 'fa': []}
    for i, d in enumerate(idx):
        if i < 25 or i + 1 >= len(idx) or d not in G or idx[i - 1] not in G: continue
        g = Day(G[d]); gp = Day(G[idx[i - 1]])
        if not g.full(): continue
        A = D.adr.iloc[i]
        if not A > 0: continue
        nx = idx[i + 1]; gn = Day(G[nx]) if nx in G else None
        pc = gp.c(16, 14)                                           # prior RTH close
        o930, c1614, c1059 = g.o(9, 30), g.c(16, 14), g.c(10, 59)
        if np.isnan(o930) or np.isnan(c1614): continue
        rH, rL = g.rng(M(9, 30), M(16, 15))
        nAM = (gn.c(10, 59) - gn.o(9, 30)) / A if gn is not None else np.nan
        nRng = (D.H.iloc[i + 1] - D.L.iloc[i + 1]) / A
        typ = T[d]
        if typ == 1:                                                 # ── NFP day, snapshot 08:29
            c0829 = g.c(8, 29); pH, pL = g.rng(0, M(8, 30))
            if np.isnan(c0829): continue
            f = common_feats(D, i, c0829, pH, pL, d)
            aH, aL = g.rng(0, M(3, 0)); dH, dL = g.rng(M(7, 0), M(8, 30))
            wk0 = d - pd.Timedelta(days=d.dayofweek); wk = D[(D.index >= wk0) & (D.index < d)]
            WO = wk.O.iloc[0] if len(wk) else g.O[0]
            o830, c849, o850, c929 = g.o(8, 30), g.c(8, 49), g.o(8, 50), g.c(9, 29)
            qH, qL = g.rng(M(8, 30), M(16, 15))
            s1, s2 = (c849 - o830) / A, (c929 - o850) / A
            up_, dn_ = (qH - c0829) / A, (c0829 - qL) / A
            # first side of the 07:00–08:29 range taken after 08:30
            s = (g.m >= M(8, 30)) & (g.m < M(16, 15)); hi_t = np.argmax(g.H[s] > dH) if (g.H[s] > dH).any() else 10 ** 6
            lo_t = np.argmax(g.L[s] < dL) if (g.L[s] < dL).any() else 10 ** 6
            first = 0 if hi_t == lo_t == 10 ** 6 else (1 if hi_t < lo_t else -1)
            r = dict(tday=d, sym=sym, **f, asiaRng=(aH - aL) / A, lonMove=(c0829 - g.c(2, 59)) / A, preRng=(pH - pL) / A, preMove=(c0829 - g.O[0]) / A,
                     drRng=(dH - dL) / A, drPos=(c0829 - dL) / (dH - dL) if dH > dL else np.nan, wkMove=(c0829 - WO) / A,
                     thuDir=sg(D.C_TD.iloc[i - 1] - D.O.iloc[i - 1]), pdRngRel=(D.PDH.iloc[i] - D.PDL.iloc[i]) / A,
                     s1=s1, s2=s2, am=(c1059 - o930) / A, rth=(c1614 - o930) / A, post=(c1614 - c0829) / A, postRng=(qH - qL) / A,
                     newHi=float(qH > pH), newLo=float(qL < pL), drHi=float(qH > dH), drLo=float(qL < dL), first=first,
                     firstWon=float(first != 0 and sg(up_ - dn_) == first), y_upSide=float(up_ > dn_), nAM=nAM, nRng=nRng,
                     y_cont=float(s1 * s2 > 0), y_againstWk=float(sg(c1614 - c0829) == -sg(c0829 - WO)), gap=(o930 - pc) / A,
                     **ce_targets(g, D, i, c0829, pH, A))
            rows['nfp'].append(r)
        if typ in (3, 5):                                            # ── snapshot 09:29 (NFP week Mon–Thu, day after FOMC)
            c0929 = g.c(9, 29); oH, oL = g.rng(0, M(9, 30))
            f = common_feats(D, i, c0929, oH, oL, d)
            gap = (o930 - pc)
            gfill = float((gap > 0 and rL <= pc) or (gap < 0 and rH >= pc)) if gap != 0 else np.nan
            amH, amL = g.rng(M(9, 30), M(11, 0)); ce = pc + gap / 2; q4 = pc + 0.75 * gap
            ce50 = float((gap > 0 and amL <= ce) or (gap < 0 and amH >= ce)) if gap != 0 else np.nan
            s10H, s10L = g.rng(M(9, 30), M(10, 0))
            ce10 = float((gap > 0 and s10L <= ce) or (gap < 0 and s10H >= ce)) if gap != 0 else np.nan
            q4h = float(not ((gap > 0 and amL <= q4) or (gap < 0 and amH >= q4))) if gap != 0 else np.nan
            stH, stL = g.rng(M(16, 15), M(17, 0))
            base = dict(tday=d, sym=sym, **f, onRng=(oH - oL) / A, onMove=(c0929 - g.O[0]) / A, gap=gap / A, gapAbs=abs(gap) / A,
                        am=(c1059 - o930) / A, rth=(c1614 - o930) / A, rthRng=(rH - rL) / A, newHi=float(rH > oH), newLo=float(rL < oL),
                        gapFill=gfill, ce50=ce50, ce10=ce10, q4held=q4h, settle=(g.c(16, 59) - g.o(16, 15)) / A, settleRng=(stH - stL) / A,
                        nAM=nAM, nRng=nRng, dayRng=(D.H.iloc[i] - D.L.iloc[i]) / A, y_amCont=float(sg(c1059 - o930) == sg(c1614 - c1059)),
                        y_upSide=float((rH - c0929) > (c0929 - rL)))
            if typ == 5:
                wk0 = d - pd.Timedelta(days=d.dayofweek); wk = D[(D.index >= wk0) & (D.index < d)]
                WO = wk.O.iloc[0] if len(wk) else g.O[0]
                fri = D[(D.index < wk0)]; fc = fri.C_TD.iloc[-1] if len(fri) else np.nan
                rows['wk'].append(dict(base, wkMove=(c0929 - WO) / A, nwog=(WO - fc) / A, nwogFilled=float((WO > fc and min(f['price'], D[(D.index >= wk0) & (D.index < d)].L.min() if len(wk) else oL, oL) <= fc) or (WO < fc and max(D[(D.index >= wk0) & (D.index < d)].H.max() if len(wk) else oH, oH) >= fc)),
                                       dToNFP=min([(x - d).days for x in NP if x > d] or [9])))
            else:                                                    # day after FOMC: the FOMC day's own numbers
                gf = gp; fA = D.adr.iloc[i - 1]
                fo14, fc1429, fo1430, fc1614, fc1359 = gf.o(14, 0), gf.c(14, 29), gf.o(14, 30), gf.c(16, 14), gf.c(13, 59)
                fH, fL = D.H.iloc[i - 1], D.L.iloc[i - 1]
                rows['fa'].append(dict(base, fS1=(fc1429 - fo14) / fA, fS2=(fc1614 - fo1430) / fA, fPost=(fc1614 - fc1359) / fA,
                                       fRng=(fH - fL) / fA, fClosePos=(D.C_TD.iloc[i - 1] - fL) / (fH - fL) if fH > fL else np.nan,
                                       fSep=float(idx[i - 1].month in (3, 6, 9, 12)), takeFH=float(rH > fH), takeFL=float(rL < fL),
                                       takeFHday=float(D.H.iloc[i] > fH), takeFLday=float(D.L.iloc[i] < fL),
                                       y_contF=float(sg(c1614 - o930) == sg(fc1614 - fc1359)), y_contS2=float(sg(c1059 - o930) == sg(fc1614 - fo1430))))
    out = {}
    for k, v in rows.items():
        F = pd.DataFrame(v).set_index('tday')
        for t in ('s1', 's2', 'am', 'rth', 'post', 'nAM', 'settle'):
            if t in F: F['y_' + t] = (F[t] > 0).astype(float).where(F[t].notna())
        for t in ('s1', 's2', 'am', 'rth', 'settle'):
            if t in F: F['m_' + t] = F[t].abs()
        F.to_pickle(f'/home/claude/hm/hydra_cal/{k}_{sym}.pkl'); out[k] = F
        print(sym, k, len(F), 'days', F.index.min().date(), '→', F.index.max().date(), '| train', (F.index.year <= 2024).sum(), 'test', (F.index.year >= 2025).sum())
    return out
if __name__ == '__main__':
    for s in sys.argv[1:] or ('NQ', 'ES'): build(s)
