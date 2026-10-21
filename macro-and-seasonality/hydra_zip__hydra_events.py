"""HYDRA × Genjutsu Kai, step 1: replay Genjutsu Kai v2 (defaults: 30m + 60m + OR, grace 2 min, minimum lag 0.02%)
on NQ (chart) vs ES (sister), 1-minute ET, 2018-01 → 2026-08. For every SMT (the bar it is drawn) and every control
(the same window side where the sister confirmed before an SMT qualified: 'both took'), record causal features known at
the close of that bar, plus outcomes measured afterwards. Output: hydra_events.pkl"""
import pandas as pd, numpy as np, math, time
t_start = time.time()
GRACE, MINLAG = 2, 0.02
A = pd.read_pickle('/home/claude/t3/bars_NQ_all.pkl'); B = pd.read_pickle('/home/claude/t3/bars_ES_all.pkl')
B = B[B.tday <= B.tday.max() - pd.Timedelta(days=1)]          # last ES day may be partial
m = A[['ts', 'tday', 'Open', 'High', 'Low', 'Close', 'Volume']].merge(
    B[['ts', 'Open', 'High', 'Low', 'Close', 'Volume']], on='ts', how='left', suffixes=('A', 'B'))
m = m[m.tday <= B.tday.max()]
m['mod'] = m.ts.dt.hour * 60 + m.ts.dt.minute
F = pd.read_pickle('/home/claude/t2/F_NQ.pkl')
FD = pd.DataFrame(index=F.index)
FD['atr'] = F.atr14.shift(1); FD['rvol'] = F.rvol.shift(1); FD['carry'] = F.carry.shift(1); FD['dte'] = F.dte
for c in ['dow', 'mon', 'opex_day', 'opex_week', 'qopex_week', 'tom', 'pre_hol', 'post_hol', 'roll_week']: FD[c] = F[c]
FD['pdrng'] = F.rng.shift(1); FD['d5'] = F.rng.shift(1).rolling(5).mean()

def blockOf(k, md):
    if k == '30m': return md // 30
    if k == '60m': return (md - 30) // 60
    return -1 if md < 570 else 0 if md < 600 else 1 if md < 960 else 2
def blockStart(k, b):
    if k == '30m': return b * 30
    if k == '60m': return b * 60 + 30
    return 570 if b == 0 else 600 if b == 1 else 960
def isWindow(k, b): return b == 1 if k == 'OR' else 570 <= blockStart(k, b) < 960

def run_day(md, hA, lA, hB, lB):
    """Exact replay of the Pine v2 engine for one day. Returns SMT events and controls (indices into the day arrays)."""
    ev, ctl = [], []
    for k in ('30m', '60m', 'OR'):
        blk, cN, live = -999, 0, False
        c = r = None; S = {}
        for j in range(len(md)):
            b = blockOf(k, md[j])
            if b != blk:
                if live:
                    for isHi in (True, False):
                        s = S[isHi]
                        if s['st'] == 1 and (s['lag'] if s['lag'] is not None else 0) < MINLAG: s['st'] = 6
                        elif s['st'] in (1, 2):
                            if s['st'] == 1:
                                s['iGrad'] = j - 1; s['atEnd'] = True; s['lagG'] = s['lag']; s['lagMxG'] = s['lagMx']
                                s['mAg'], s['mBg'] = s['mA'], s['mB']; ev.append(s)
                            s['st'] = 4
                    live = False
                contig = (b == blk + 1) and cN > 0 and c is not None and not math.isnan(c['Hb']) and not math.isnan(c['Lb'])
                if isWindow(k, b) and contig:
                    r = dict(c); live = True
                    S = {isHi: dict(kind=k, hi=isHi, st=0, lead=0, iLead=None, iSync=None, mA=None, mB=None, lag=None,
                                    lagMx=None, ref=r, w0=j, wStart=blockStart(k, b), atEnd=False) for isHi in (True, False)}
                blk = b; cN = 1
                c = dict(Ha=hA[j], HaI=j, La=lA[j], LaI=j, Hb=hB[j], HbI=j, Lb=lB[j], LbI=j)
            else:
                if hA[j] > c['Ha']: c['Ha'], c['HaI'] = hA[j], j
                if lA[j] < c['La']: c['La'], c['LaI'] = lA[j], j
                if not math.isnan(hB[j]) and (math.isnan(c['Hb']) or hB[j] > c['Hb']): c['Hb'], c['HbI'] = hB[j], j
                if not math.isnan(lB[j]) and (math.isnan(c['Lb']) or lB[j] < c['Lb']): c['Lb'], c['LbI'] = lB[j], j
                cN += 1
            if live and md[j] < 960:
                for isHi in (True, False):
                    s = S[isHi]
                    refA = r['Ha'] if isHi else r['La']; refB = r['Hb'] if isHi else r['Lb']
                    if s['st'] <= 2:
                        vA = hA[j] if isHi else lA[j]
                        if s['mA'] is None or (vA > s['mA'] if isHi else vA < s['mA']): s['mA'] = vA
                        vB = hB[j] if isHi else lB[j]
                        if not math.isnan(vB) and (s['mB'] is None or (vB > s['mB'] if isHi else vB < s['mB'])): s['mB'] = vB
                    tA = s['mA'] is not None and (s['mA'] > refA if isHi else s['mA'] < refA)
                    tB = s['mB'] is not None and (s['mB'] > refB if isHi else s['mB'] < refB)
                    if s['st'] == 0:
                        if tA and tB:
                            s['st'] = 5; ctl.append(dict(kind=k, hi=isHi, lead=0, i=j, ref=r, w0=s['w0'], wStart=s['wStart'], iLead=j))
                        elif tA or tB:
                            s['st'] = 1; s['lead'] = 1 if tA else 2; s['iLead'] = j
                    if s['st'] in (1, 2) and s['mB'] is not None and refA > 0 and refB > 0:
                        s['lag'] = 100.0 * abs(s['mB'] / refB - s['mA'] / refA)
                        if s['lagMx'] is None or s['lag'] > s['lagMx']: s['lagMx'] = s['lag']
                    sis = tB if s['lead'] == 1 else tA
                    if s['st'] == 1:
                        if sis:
                            s['st'] = 5; ctl.append(dict(kind=k, hi=isHi, lead=s['lead'], i=j, ref=r, w0=s['w0'], wStart=s['wStart'], iLead=s['iLead']))
                        elif (md[j] + 1) - md[s['iLead']] > GRACE and (s['lag'] or 0) >= MINLAG:
                            s['st'] = 2; s['iGrad'] = j; s['lagG'] = s['lag']; s['lagMxG'] = s['lagMx']
                            s['mAg'], s['mBg'] = s['mA'], s['mB']; ev.append(s)
                    elif s['st'] == 2 and sis:
                        s['st'] = 3; s['iSync'] = j
    return ev, ctl

rows = []
days = sorted(m.tday.unique())
prevClose = prevRH = prevRL = None
smt_log = []
for di, td in enumerate(days):
    x = m[m.tday == td]
    md_all = x['mod'].values
    cA_all = x.CloseA.values
    # overnight (18:00 prev → 09:29) and premarket (07:00–09:29)
    on = x[(md_all >= 1080) | (md_all < 570)]; pm = x[(md_all >= 420) & (md_all < 570)]
    rth = x[(md_all >= 570) & (md_all < 975)]
    if len(rth) < 380 or rth.HighB.isna().mean() > 0.05 or len(on) < 600 or prevClose is None:
        if len(rth) > 0:
            prevClose = x.CloseA.values[-1]; prevRH, prevRL = rth.HighA.max(), rth.LowA.min()
        continue
    d = x[(md_all >= 480) & (md_all < 975)]
    # one continuous index over the whole session for sigma/momentum lookbacks
    xs = x.reset_index(drop=True)
    off = int(np.where((xs['mod'].values >= 480) & (xs['mod'].values < 975))[0][0])
    md = d['mod'].values; oA = d.OpenA.values; hA = d.HighA.values; lA = d.LowA.values; cA = d.CloseA.values
    hB = d.HighB.values; lB = d.LowB.values; cB = d.CloseB.values; vA = d.VolumeA.values; vB = d.VolumeB.values
    CA = xs.CloseA.values; CB = xs.CloseB.ffill().values
    rA1 = np.diff(np.log(CA), prepend=np.nan); rB1 = np.diff(np.log(CB), prepend=np.nan)
    i930 = int(np.argmax(md >= 570)); o930A = oA[i930]; o930B = d.OpenB.values[i930]
    onH, onL = on.HighA.max(), on.LowA.min(); pmH, pmL = pm.HighA.max(), pm.LowA.min()
    fd = FD.loc[td] if td in FD.index else None
    atrPct = fd.atr if fd is not None and not np.isnan(fd.atr) else np.nan
    atr = atrPct / 100.0 * o930A                     # ATR14 (prior day) in points
    ev, ctl = run_day(md, hA, lA, hB, lB)
    allev = [(e, 'smt') for e in ev] + [(c_, 'ctl') for c_ in ctl]
    smt_times = sorted([(e['iGrad'], e['hi'], e['st'], e.get('iSync')) for e in ev])
    iend = len(md) - 1                                   # 16:14 bar
    for e, typ in allev:
        j = e['iGrad'] if typ == 'smt' else e['i']
        if md[j] >= 960 or j >= iend: continue
        J = j + off                                      # index in session arrays
        isHi = e['hi']; s = 1 if isHi else -1; dd = -s     # take direction s, SMT trade direction dd
        r = e['ref']
        refA = r['Ha'] if isHi else r['La']; refB = r['Hb'] if isHi else r['Lb']
        sg1A = np.nanstd(rA1[max(1, J - 59):J + 1]); sg1B = np.nanstd(rB1[max(1, J - 59):J + 1])
        sgA = sg1A * math.sqrt(30); sgB = sg1B * math.sqrt(30)
        if not (sgA > 0 and sgB > 0): continue
        ent = cA[j]
        # targets on NQ: race to ±1σ30 and ±2σ30 from the close of the signal bar, until 16:14
        tg = {}
        for mult in (1, 2):
            up = ent * math.exp(mult * sgA); dn = ent * math.exp(-mult * sgA)
            res = np.nan
            for k_ in range(j + 1, iend + 1):
                hu = hA[k_] >= up; hd = lA[k_] <= dn
                if hu and hd: res = 0.5; break
                if hu: res = 1.0 if dd == 1 else 0.0; break
                if hd: res = 1.0 if dd == -1 else 0.0; break
            tg[f'rev{mult}'] = res
        k30 = min(j + 30, iend)
        tg['r30'] = float(np.clip(dd * math.log(cA[k30] / ent) / sgA, -6, 6))
        tg['reod'] = float(np.clip(dd * math.log(cA[iend] / ent) / sgA, -12, 12))
        tg['up30'] = float(math.log(cA[k30] / ent) / sgA)
        # leader/sister geometry at the signal bar
        leadNQ = 1 if e['lead'] == 1 else 0
        mAg = e.get('mAg', hA[j] if isHi else lA[j]); mBg = e.get('mBg', hB[j] if isHi else lB[j])
        if typ == 'ctl':
            seg = slice(e['w0'], j + 1)
            mAg = np.nanmax(hA[seg]) if isHi else np.nanmin(lA[seg]); mBg = np.nanmax(hB[seg]) if isHi else np.nanmin(lB[seg])
        overA = s * math.log(mAg / refA) / sgA; overB = s * math.log(mBg / refB) / sgB
        w0 = e['w0']
        lrw = s * math.log(cA[j] / oA[w0]) / sgA; srw = s * math.log(cB[j] / d.OpenB.values[w0]) / sgB if not np.isnan(cB[j]) else np.nan
        rth_seg = slice(i930, j + 1)
        rhi = np.nanmax(hA[rth_seg]); rlo = np.nanmin(lA[rth_seg])
        pre_hi = np.nanmax(hA[i930:w0]) if w0 > i930 else np.nan; pre_lo = np.nanmin(lA[i930:w0]) if w0 > i930 else np.nan
        dayExt = float((mAg > pre_hi) if isHi else (mAg < pre_lo)) if not np.isnan(pre_hi) else np.nan
        onExt = float(mAg > onH if isHi else mAg < onL)
        pdExt = float(mAg > prevRH if isHi else mAg < prevRL)
        rA = math.log(cA[j] / o930A); rB = math.log(cB[j] / o930B) if not np.isnan(cB[j]) else np.nan
        seg60 = slice(max(1, J - 59), J + 1)
        a60, b60 = rA1[seg60], rB1[seg60]; ok = ~(np.isnan(a60) | np.isnan(b60))
        corr60 = np.corrcoef(a60[ok], b60[ok])[0, 1] if ok.sum() > 20 else np.nan
        beta60 = np.cov(a60[ok], b60[ok])[0, 1] / np.var(b60[ok]) if ok.sum() > 20 else np.nan
        disp60 = np.nanstd(a60[ok] - b60[ok]) / sg1A if ok.sum() > 20 else np.nan
        segd = slice(i930 + off + 1, J + 1)
        ad, bd = rA1[segd], rB1[segd]; okd = ~(np.isnan(ad) | np.isnan(bd))
        corrD = np.corrcoef(ad[okd], bd[okd])[0, 1] if okd.sum() > 20 else np.nan
        sgDay = np.nanstd(rA1[i930 + off + 1:J + 1]) if J - (i930 + off) > 10 else np.nan
        v30A = np.nanmean(vA[max(i930, j - 29):j + 1]); vdA = np.nanmean(vA[i930:j + 1])
        v30B = np.nanmean(vB[max(i930, j - 29):j + 1]); vdB = np.nanmean(vB[i930:j + 1])
        prior = [t for t in smt_times if t[0] < j]
        done = [t for t in prior if (t[2] == 4 and False) or (t[3] is not None and t[3] <= j)]
        row = dict(tday=td, typ=typ, kind=e['kind'], hi=int(isHi), leadNQ=leadNQ, lead=e['lead'], tod=int(md[j]),
                   st=e['st'] if typ == 'smt' else 5, atEnd=int(e.get('atEnd', False)),
                   lag=e.get('lagG', np.nan) if typ == 'smt' else 100.0 * abs(mBg / refB - mAg / refA),
                   lagMx=e.get('lagMxG', np.nan) if typ == 'smt' else np.nan,
                   grace=int(md[j] - md[e['iLead']]) if e['iLead'] is not None else 0, winMin=int(md[j] - e['wStart']),
                   refA_pct=100 * (r['Ha'] - r['La']) / cA[j], refB_pct=100 * (r['Hb'] - r['Lb']) / cB[j] if not np.isnan(cB[j]) else np.nan,
                   refA_sig=math.log(r['Ha'] / r['La']) / sgA, overA=overA, overB=overB, overDiff=overA - overB,
                   lrw=lrw, srw=srw, dayExt=dayExt, onExt=onExt, pdExt=pdExt,
                   posDay=(cA[j] - rlo) / (rhi - rlo) if rhi > rlo else np.nan,
                   mom30=s * math.log(cA[j] / CA[max(0, J - 30)]) / sgA, mom5=s * math.log(cA[j] / CA[max(0, J - 5)]) / sgA,
                   momOpen=s * rA / sgA, relStr=s * (rA - rB) * 100 if not np.isnan(rB) else np.nan,
                   bothUp=float(np.sign(rA) == np.sign(rB)) if not np.isnan(rB) else np.nan,
                   gap=100 * math.log(o930A / prevClose), gapS=s * 100 * math.log(o930A / prevClose),
                   gap_atr=(o930A - prevClose) / atr, on_atr=(onH - onL) / atr, pm_atr=(pmH - pmL) / atr,
                   on_pos=(o930A - onL) / (onH - onL) if onH > onL else np.nan,
                   rng_atr=(rhi - rlo) / atr, pd_atr=fd.pdrng / atrPct if fd is not None else np.nan,
                   d5_atr=fd.d5 / atrPct if fd is not None else np.nan, atr_pct=atrPct,
                   sig30_pct=100 * sgA, rv_rel=sg1A / sgDay if sgDay and sgDay > 0 else np.nan,
                   corr60=corr60, corrD=corrD, beta60=beta60, disp60=disp60,
                   v30A=v30A / vdA if vdA > 0 else np.nan, v30B=v30B / vdB if vdB > 0 else np.nan,
                   distON=s * math.log((onH if isHi else onL) / cA[j]) / sgA, distPD=s * math.log((prevRH if isHi else prevRL) / cA[j]) / sgA,
                   nSmt=len(prior), nSameSide=sum(1 for t in prior if t[1] == isHi), nSyncd=len(done),
                   sinceSmt=int(md[j] - md[prior[-1][0]]) if prior else 999,
                   rvol=fd.rvol if fd is not None else np.nan, carry=fd.carry if fd is not None else np.nan,
                   dte=fd.dte if fd is not None else np.nan, dow=fd.dow if fd is not None else np.nan,
                   mon=fd.mon if fd is not None else np.nan)
        for c_ in ['opex_day', 'opex_week', 'qopex_week', 'tom', 'pre_hol', 'post_hol', 'roll_week']:
            row[c_] = fd[c_] if fd is not None else np.nan
        row.update(tg)
        row['held'] = (1.0 if e['st'] == 4 else 0.0 if e['st'] == 3 else np.nan) if typ == 'smt' else np.nan
        # after the window: race from the window's last bar (held SMTs and controls) or from the sync bar (synced SMTs)
        wl = 360 if e['kind'] == 'OR' else (30 if e['kind'] == '30m' else 60)
        wEnd = min(960, e['wStart'] + wl)
        jE = int(np.searchsorted(md, wEnd) - 1)
        jP = e['iSync'] if (typ == 'smt' and e['st'] == 3 and e.get('iSync') is not None) else jE
        row['wLeft'] = int(wEnd - md[j] - 1); row['jPostTod'] = int(md[jP])
        res = np.nan
        if jP < iend and jP >= j:
            JP = jP + off; sP = np.nanstd(rA1[max(1, JP - 59):JP + 1]) * math.sqrt(30); entP = cA[jP]
            up = entP * math.exp(sP); dn = entP * math.exp(-sP)
            for k_ in range(jP + 1, iend + 1):
                hu = hA[k_] >= up; hd = lA[k_] <= dn
                if hu and hd: res = 0.5; break
                if hu: res = 1.0 if dd == 1 else 0.0; break
                if hd: res = 1.0 if dd == -1 else 0.0; break
        row['revPost'] = res
        rows.append(row)
    # random-time baseline: 4 random RTH bars per day, race and 30m move (direction: long)
    rng_ = np.random.default_rng(di)
    jEnd = int(np.argmax(md >= 960)) if (md >= 960).any() else iend
    cand_ = np.arange(i930 + 15, jEnd)
    for j in (rng_.choice(cand_, 4, replace=False) if len(cand_) >= 4 else []):
        J = j + off; sg1A = np.nanstd(rA1[max(1, J - 59):J + 1]); sgA = sg1A * math.sqrt(30); ent = cA[j]
        up = ent * math.exp(sgA); dn = ent * math.exp(-sgA); res = np.nan
        for k_ in range(j + 1, iend + 1):
            hu = hA[k_] >= up; hd = lA[k_] <= dn
            if hu and hd: res = 0.5; break
            if hu: res = 1.0; break
            if hd: res = 0.0; break
        rows.append(dict(tday=td, typ='rand', tod=int(md[j]), rev1=res, up30=float(math.log(cA[min(j + 30, iend)] / ent) / sgA)))
    prevClose = x.CloseA.values[-1]; prevRH, prevRL = rth.HighA.max(), rth.LowA.min()
    if di % 250 == 0: print(f'{td.date()} {len(rows)} rows {time.time() - t_start:.0f}s', flush=True)
R = pd.DataFrame(rows); R['year'] = pd.DatetimeIndex(R.tday).year
R.to_pickle('hydra_events.pkl')
print('done', R.typ.value_counts().to_dict(), R.tday.nunique(), 'days', f'{time.time() - t_start:.0f}s')
