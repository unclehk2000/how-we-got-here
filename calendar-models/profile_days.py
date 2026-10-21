"""Per-day intraday features for the model profiles (NQ, ES), ET, CME trading days. Output: prof_{root}.pkl"""
import pandas as pd, numpy as np, sys, time
ROOTS = sys.argv[1:] or ['NQ', 'ES']
def first_touch(hi, lo, lvl, mods, a, b):
    """first minute in [a, b) where the bar range contains lvl"""
    sel = np.where((mods >= a) & (mods < b) & (hi >= lvl) & (lo <= lvl))[0]
    return int(mods[sel[0]]) if len(sel) else -1
for root in ROOTS:
    t0 = time.time()
    b = pd.read_pickle(f'/home/claude/t3/bars_{root}_all.pkl'); b['mod'] = b.ts.dt.hour * 60 + b.ts.dt.minute
    D = pd.read_pickle(f'days_{root}.pkl'); TD = D[D.anchor == 'TD'].set_index('tday')
    rows = []; prev = None; wk = {}
    for td, x in b.groupby('tday'):
        md = x['mod'].values; o = x.Open.values; h = x.High.values; l = x.Low.values; c = x.Close.values
        idx = {m: i for i, m in enumerate(md)}
        def rng(a, z):
            s = (md >= a) & (md < z) if a < z else ((md >= a) | (md < z))
            return (h[s].max() - l[s].min()) if s.sum() >= 0.8 * ((z - a) % 1440) else np.nan
        def px_open(m): return o[idx[m]] if m in idx else np.nan
        def px_close(m): return c[idx[m]] if m in idx else np.nan
        rth = (md >= 570) & (md < 975)
        r = dict(tday=td)
        if rth.sum() >= 380:
            rH = h[rth].max(); rL = l[rth].min(); r.update(rthO=px_open(570), rthC=px_close(974), rthH=rH, rthL=rL,
                tHr=int(md[rth][np.argmax(h[rth])]), tLr=int(md[rth][np.argmin(l[rth])]))
        r.update(tdO=o[0], tdH=h.max(), tdL=l.min(), tdC=c[-1], rth2C=px_close(1019))
        for nm, (a, z) in dict(asia=(1200, 1440), london=(120, 300), nyam=(570, 660), lunch=(690, 780), pm=(810, 960),
                               pre=(810, 840), stmt=(840, 870), presser=(870, 975), settle=(975, 1020)).items():
            r[nm] = rng(a, z)
        # windows and stages
        r['s1'] = px_close(529) - px_open(510); r['s2'] = px_close(659) - px_open(530)            # 8:30–8:50 vs 8:50–11:00
        r['st'] = px_close(869) - px_open(840); r['pr'] = px_close(974) - px_open(870)            # statement vs press conference
        for nm, (a, z) in dict(sb=(590, 610), lun=(690, 810), co=(915, 945)).items():             # 9:50–10:10, 11:30–13:30, 15:15–15:45
            pre_ = px_close(a - 1) - r.get('rthO', np.nan); mv = px_close(z - 1) - px_close(a - 1)
            r[f'{nm}_rev'] = float(np.sign(pre_) != np.sign(mv)) if (pre_ != 0 and mv != 0 and np.isfinite(pre_ * mv)) else np.nan
        # pre-release ranges: NFP dealing range 07:00–08:59, CPI pre-release 07:30–08:29
        for nm, (a, z) in dict(dr=(420, 540), pr=(450, 510)).items():
            s = (md >= a) & (md < z)
            r[f'{nm}H'] = h[s].max() if s.sum() > 0.8 * (z - a) else np.nan; r[f'{nm}L'] = l[s].min() if s.sum() > 0.8 * (z - a) else np.nan
        # first side of the CPI pre-release range taken after 08:30, and the larger move from 08:30 to 16:14
        s = (md >= 510) & (md < 975)
        if s.sum() > 300 and np.isfinite(r['prH']):
            hh, ll = h[s], l[s]; up = np.where(hh > r['prH'])[0]; dn = np.where(ll < r['prL'])[0]
            fu = up[0] if len(up) else 10 ** 9; fd = dn[0] if len(dn) else 10 ** 9
            r['first'] = 0 if fu == fd == 10 ** 9 else (1 if fu < fd else -1)
            o830 = px_open(510); r['bigUp'] = float((hh.max() - o830) > (o830 - ll.min()))
        if prev is not None and 'rthO' in r and np.isfinite(prev.get('rthC', np.nan)):
            pc, pc2, O = prev['rthC'], prev['rth2C'], r['rthO']
            r.update(prevRthC=pc, prevRthH=prev.get('rthH', np.nan), prevRthL=prev.get('rthL', np.nan), prevTdH=prev['tdH'], prevTdL=prev['tdL'])
            ce1 = (pc + O) / 2; ce2 = (pc2 + O) / 2 if np.isfinite(pc2) else ce1
            near = ce1 if abs(ce1 - O) <= abs(ce2 - O) else ce2
            r['gapPct'] = abs(O - pc) / pc * 100
            r['tCE'] = first_touch(h, l, ce1, md, 570, 975); r['tNear'] = first_touch(h, l, near, md, 570, 975)
            r['tFill'] = first_touch(h, l, pc, md, 570, 975)
        # NWOG: last close of the prior week vs the first open of this week; is its midpoint touched by this day's close?
        wkey = (td - pd.Timedelta(days=td.dayofweek)).date()
        if wkey not in wk and prev is not None:
            wk.clear(); wk[wkey] = dict(ce=(prev['tdC'] + o[0]) / 2, hit=False)
        if wkey in wk:
            W = wk[wkey]; W['hit'] = W['hit'] or bool(((h >= W['ce']) & (l <= W['ce'])).any()); r['nwogHit'] = float(W['hit'])
        rows.append(r); prev = r
    P = pd.DataFrame(rows).set_index('tday')
    P = P.join(TD[['type', 'adr', 'year']], how='inner')
    P['dow'] = P.index.dayofweek
    P['rthR'] = (P.rthH - P.rthL); P['trend'] = ((P.rthC - P.rthO).abs() / P.rthR >= 0.5).astype(float)
    P['up'] = (P.rthC > P.rthO).astype(float)
    P['nextDir'] = np.sign((P.rthC - P.rthO).shift(-1)); P['dir'] = np.sign(P.rthC - P.rthO)
    P['nextR'] = P.rthR.shift(-1); P['nextH'] = P.rthH.shift(-1); P['nextL'] = P.rthL.shift(-1)
    P['nextTdH'] = P.tdH.shift(-1); P['nextTdL'] = P.tdL.shift(-1)
    P['nextNyam'] = (P.rthO.shift(-1) - P.rthO.shift(-1))  # placeholder, replaced below
    P.to_pickle(f'prof_{root}.pkl'); print(root, len(P), f'{time.time() - t0:.0f}s')
