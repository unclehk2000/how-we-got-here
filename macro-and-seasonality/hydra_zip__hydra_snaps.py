"""Sync-odds data: every 5 minutes while an SMT is open (and at the bar it is drawn), snapshot the sister's distance to
its level from the CURRENT close, time left in the window, volatility and a few context heads; outcome = did the
sister take its level before the window ended. Output: hydra_snaps.pkl"""
import pandas as pd, numpy as np, math, time
src = open('hydra_events.py').read().split('rows = []')[0]
src = src.replace("    ev, ctl = [], []\n", "    ev, ctl = [], []\n    global SNAPS\n")
src = src.replace("                    elif s['st'] == 2 and sis:\n                        s['st'] = 3; s['iSync'] = j\n",
                  "                    elif s['st'] == 2 and sis:\n                        s['st'] = 3; s['iSync'] = j\n"
                  "                    if s['st'] == 2 and (j == s['iGrad'] or md[j] % 5 == 0): SNAPS.append((s, j, s['mA'], s['mB'], s['lag']))\n")
exec(src)
rows = []; days = sorted(m.tday.unique()); t0 = time.time()
for di, td in enumerate(days):
    x = m[m.tday == td]; md_all = x['mod'].values
    rth = x[(md_all >= 570) & (md_all < 975)]
    if len(rth) < 380 or rth.HighB.isna().mean() > 0.05: continue
    d = x[(md_all >= 480) & (md_all < 975)]; xs = x.reset_index(drop=True)
    off = int(np.where((xs['mod'].values >= 480) & (xs['mod'].values < 975))[0][0])
    md = d['mod'].values; hA = d.HighA.values; lA = d.LowA.values; cA = d.CloseA.values
    hB = d.HighB.values; lB = d.LowB.values; cB = d.CloseB.ffill().values
    CA = xs.CloseA.values; CB = xs.CloseB.ffill().values
    rA1 = np.diff(np.log(CA), prepend=np.nan); rB1 = np.diff(np.log(CB), prepend=np.nan)
    SNAPS = []
    run_day(md, hA, lA, hB, lB)
    for s, j, mA_, mB_, lag_ in SNAPS:
        J = j + off; isHi = s['hi']; sg = 1 if isHi else -1; r = s['ref']
        wl = 360 if s['kind'] == 'OR' else (30 if s['kind'] == '30m' else 60); wEnd = min(960, s['wStart'] + wl)
        left = wEnd - md[j] - 1
        if left <= 0: continue
        sisB = s['lead'] == 1
        refS = (r['Hb'] if isHi else r['Lb']) if sisB else (r['Ha'] if isHi else r['La'])
        refL = (r['Ha'] if isHi else r['La']) if sisB else (r['Hb'] if isHi else r['Lb'])
        cS = cB[j] if sisB else cA[j]; cL = cA[j] if sisB else cB[j]
        mS = mB_ if sisB else mA_; mL = mA_ if sisB else mB_
        r1S = rB1 if sisB else rA1; r1L = rA1 if sisB else rB1
        sgS = np.nanstd(r1S[max(1, J - 59):J + 1]); sgL = np.nanstd(r1L[max(1, J - 59):J + 1])
        sgSd = np.nanstd(r1S[max(1, J - 389):J + 1])
        if not (sgS > 0 and sgL > 0): continue
        a60, b60 = rA1[max(1, J - 59):J + 1], rB1[max(1, J - 59):J + 1]; ok = ~(np.isnan(a60) | np.isnan(b60))
        rows.append(dict(tday=td, sid=f'{td.date()}_{s["kind"]}_{int(isHi)}_{s["wStart"]}', kind=s['kind'], hi=int(isHi), leadNQ=int(sisB),
                         tod=int(md[j]), first=int(j == s['iGrad']), left=int(left), wl=wl,
                         gapNow=sg * math.log(refS / cS) / sgS, gapExt=sg * math.log(refS / mS) / sgS,
                         leadNow=sg * math.log(cL / refL) / sgL, leadExt=sg * math.log(mL / refL) / sgL,
                         lag=lag_, sgS=sgS, sgL=sgL, sgRel=sgS / sgSd if sgSd > 0 else np.nan,
                         corr60=np.corrcoef(a60[ok], b60[ok])[0, 1] if ok.sum() > 20 else np.nan,
                         sync=1.0 if s['st'] == 3 else 0.0 if s['st'] == 4 else np.nan))
    if di % 400 == 0: print(td.date(), len(rows), f'{time.time() - t0:.0f}s', flush=True)
S = pd.DataFrame(rows); S['year'] = pd.DatetimeIndex(S.tday).year
S.to_pickle('hydra_snaps.pkl'); print('done', len(S), S.sid.nunique(), 'SMTs', f'{time.time() - t0:.0f}s')
