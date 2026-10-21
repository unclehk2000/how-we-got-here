"""Event-day candle shapes for the PO3-style event candle. For each day: anchor open O, high H, low L, close C and the
times of H and L, for three anchors (trading day 18:00→16:59, NY midnight 00:00→16:59, RTH 09:30→16:14). Everything is
scaled by ADR20 = mean (H−L)/O of the previous 20 days on the same anchor (known before the day starts).
  u = (H−O)/O ÷ ADR   reach above the open      v = (O−L)/O ÷ ADR   reach below the open
  c = (C−O)/O ÷ ADR   close vs open             R = (H−L)/O ÷ ADR   range
Day types (priority): FOMC > NFP > CPI > day after FOMC > FOMC day 1 > NFP week Mon–Thu > normal."""
import pandas as pd, numpy as np, sys, json
from scipy import stats
from events import FOMC, CPI, NFP
ANCH = {'TD': None, 'MID': (0, 1020), 'RTH': (570, 975)}
BUCKETS = {'TD': [(1080, 1440), (0, 120), (120, 420), (420, 570), (570, 720), (720, 1020)],   # Asia 18–02 split at midnight
           'MID': [(0, 120), (120, 420), (420, 570), (570, 720), (720, 1020)],
           'RTH': [(570, 600), (600, 690), (690, 810), (810, 975)]}
BNAMES = {'TD': ['18–00', '00–02', '02–07', '07–09:30', '09:30–12', '12–17'], 'MID': ['00–02', '02–07', '07–09:30', '09:30–12', '12–17'],
          'RTH': ['09:30–10', '10–11:30', '11:30–13:30', '13:30–16:15']}
TYPES = ['FOMC', 'NFP', 'CPI', 'POST', 'PRE', 'HOLLOW', 'NORMAL']

def day_table(root):
    b = pd.read_pickle(f'/home/claude/t3/bars_{root}_all.pkl')
    b['mod'] = b.ts.dt.hour * 60 + b.ts.dt.minute
    rows = []
    for td, x in b.groupby('tday'):
        md = x['mod'].values
        rth = (md >= 570) & (md < 975)
        if rth.sum() < 380: continue
        for an, w in ANCH.items():
            if an == 'TD':
                sel = np.ones(len(x), bool); need = 1000
                if not ((md >= 1080).any()): continue
            else:
                sel = (md >= w[0]) & (md < w[1]) & (x.ts.dt.normalize().values == np.datetime64(td)); need = 0.94 * (w[1] - w[0])
            y = x[sel]
            if len(y) < need: continue
            H = y.High.values; L = y.Low.values; m_ = y['mod'].values
            iH = int(np.argmax(H)); iL = int(np.argmin(L))
            rows.append(dict(tday=td, anchor=an, O=y.Open.values[0], H=H[iH], L=L[iL], C=y.Close.values[-1], tH=int(m_[iH]), tL=int(m_[iL])))
    D = pd.DataFrame(rows)
    D['rng'] = (D.H - D.L) / D.O
    D = D.sort_values(['anchor', 'tday'])
    D['adr'] = D.groupby('anchor').rng.transform(lambda s: s.shift(1).rolling(20, min_periods=15).mean())
    for k, num in (('u', D.H - D.O), ('v', D.O - D.L), ('c', D.C - D.O), ('R', D.H - D.L)):
        D[k] = num / D.O / D.adr
    D['up'] = (D.C > D.O).astype(float)
    # day type
    tds = pd.DatetimeIndex(sorted(D.tday.unique()))
    nxt = {tds[i]: tds[i + 1] for i in range(len(tds) - 1)}
    post = {nxt[d] for d in FOMC if d in nxt}
    pre = {d - pd.Timedelta(days=1) for d in FOMC}
    hollow = set()
    for d in NFP:
        wk0 = d - pd.Timedelta(days=d.dayofweek)
        for k in range(d.dayofweek): hollow.add(wk0 + pd.Timedelta(days=k))
    sets = {'FOMC': set(FOMC), 'NFP': set(NFP), 'CPI': set(CPI), 'POST': post, 'PRE': pre, 'HOLLOW': hollow}
    def typ(d):
        for t in TYPES[:-1]:
            if d in sets[t]: return t
        return 'NORMAL'
    D['type'] = D.tday.map(typ)
    D['year'] = D.tday.dt.year
    D['root'] = root
    return D.dropna(subset=['adr'])

def summarise(D):
    out = {}
    for an in ANCH:
        for t in TYPES:
            x = D[(D.anchor == an) & (D.type == t)]
            if len(x) < 5: continue
            q = lambda s: [round(float(v), 3) for v in np.quantile(s, [0.25, 0.5, 0.75])]
            bH = [round(float(((x.tH - 0) >= a) .mean()), 3) for a, _ in []]
            def share(col):
                res = []
                for a, z in BUCKETS[an]:
                    res.append(round(float(((x[col] >= a) & (x[col] < z)).mean()), 3))
                return res
            out[f'{an}|{t}'] = dict(n=int(len(x)), pup=round(float(x.up.mean()), 3), u=q(x.u), v=q(x.v), c=q(x.c), R=q(x.R),
                                   hiB=share('tH'), loB=share('tL'))
    return out

if __name__ == '__main__':
    roots = sys.argv[1:] or ['NQ', 'ES']
    for root in roots:
        D = day_table(root); D.to_pickle(f'days_{root}.pkl')
        print(root, D.groupby(['anchor', 'type']).size().unstack(0).to_string())
