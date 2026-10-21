"""Event clock and tally records for RTY (and NQ as a check against the shipped CK_NQ), from the HYDRA calendar loaders.
Clock: running range and net move from the 18:00 open ÷ ADR20 (points) at the end of each half hour of the trading day,
q10/25/50/75/90 for NFP days and normal days, plus the median share of the final range. Packed as in Desgarrón (P92)."""
import numpy as np, pandas as pd, json, re, sys
import common as CM
P92 = "!#$%&'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[]^_`abcdefghijklmnopqrstuvwxyz{|}~"
QS = [0.10, 0.25, 0.50, 0.75, 0.90]
def build(sym):
    G = CM.days(sym); D = CM.ctx(sym); T = CM.day_type(D.index)
    rows = []
    for d in D.index:
        if d not in G or T[d] not in (1, 6): continue
        g = CM.Day(G[d]); A = D.adr.loc[d]
        if not g.full() or len(g.m) < 1000 or not A > 0: continue
        O = g.O[0]; hi = np.maximum.accumulate(g.H); lo = np.minimum.accumulate(g.L)
        k = np.searchsorted(g.m, 30 * (np.arange(46) + 1), side='left') - 1
        if (k < 0).any(): continue
        R = (hi[k] - lo[k]) / A; N = (g.C[k] - O) / A
        rows.append(dict(d=d, t=T[d], R=R, N=N, fin=R[-1]))
    P = pd.DataFrame(rows); res = {}
    for t, nm in ((1, 'NFP'), (6, 'NORMAL')):
        x = P[P.t == t]; Rm = np.vstack(x.R.values); Nm = np.vstack(x.N.values)
        res[nm] = dict(n=len(x), R=[np.quantile(Rm, q, axis=0) for q in QS], N=[np.quantile(Nm, q, axis=0) for q in QS],
                       share=np.median(Rm / x.fin.values[:, None], axis=0))
    vals = []
    for nm in ('NFP', 'NORMAL'):
        r = res[nm]
        for blk in r['R'] + r['N'] + [r['share']]:
            vals += [int(round(v * 1000)) for v in blk]
    assert len(vals) == 1012 and min(vals) > -2000 and max(vals) < 92 * 92 - 2000
    enc = ''.join(P92[(v + 2000) // 92] + P92[(v + 2000) % 92] for v in vals)
    # tally: trading day, RTH, gap
    recs = []; idx = list(D.index)
    for i, d in enumerate(idx):
        if d not in CM.NP or i == 0: continue
        td = int(np.sign(D.C_TD.loc[d] - D.O.loc[d]))
        ro = rc = pc = np.nan
        if d in G:
            g = CM.Day(G[d]); ro, rc = g.o(9, 30), g.c(16, 14)
        p = idx[i - 1]
        if p in G: pc = CM.Day(G[p]).c(16, 14)
        rth = int(np.sign(rc - ro)) if np.isfinite(ro) and np.isfinite(rc) else 0
        gap = f'{ro - pc:.1f}' if np.isfinite(ro) and np.isfinite(pc) else ''
        gp = f'{(ro / pc - 1) * 100:.3f}' if gap else ''
        recs.append(f"{d.strftime('%Y%m%d')},{td},{rth},{gap},{gp}")
    return res, vals, enc, recs, int(D.index[-1].strftime('%Y%m%d'))
out = {}
for sym in sys.argv[1:]:
    res, vals, enc, recs, end = build(sym)
    out[sym] = dict(enc=enc, recs=recs, end=end, n={k: v['n'] for k, v in res.items()})
    print(sym, 'NFP', res['NFP']['n'], 'normal', res['NORMAL']['n'], '| median NFP range at 09:00 (j 29)', round(res['NFP']['R'][2][29], 3), 'at 17:00', round(res['NFP']['R'][2][45], 3), '| normal 09:00', round(res['NORMAL']['R'][2][29], 3), '| tally', len(recs), recs[-2:])
json.dump(out, open('clock_rty.json', 'w'))
# check: decode the shipped NQ clock
S = open('/home/claude/hm/calgen/Desgarron.pine', encoding='utf-8').read()
m = re.search(r'(?m)^CK_NQ\s*=\s*"[^"]*"(?:\n\s+\+\s*"[^"]*")*', S); body = ''.join(re.findall(r'"([^"]*)"', m.group(0)))
v = [(P92.index(body[2 * i]) * 92 + P92.index(body[2 * i + 1]) - 2000) / 1000 for i in range(len(body) // 2)]
print('shipped CK_NQ: NFP median range 09:00', v[2 * 46 + 29], '17:00', v[2 * 46 + 45], '| normal 09:00', v[506 + 2 * 46 + 29])
