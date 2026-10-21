"""RTY clock (NFP week Mon–Thu, day after FOMC, normal days; Hollow's CK layout) and day-after-FOMC tally, validated on NQ."""
import sys, re, json, numpy as np, pandas as pd
sys.path.insert(0, '/home/claude/hm/hydra_cal'); sys.path.insert(0, '/home/claude/hm/calgen/rty')
import common as CM
from gen_rty import P92, QS, NS, unpack, pack
def clock(sym, types):
    G = CM.days(sym); D = CM.ctx(sym); T = CM.day_type(D.index); rows = []
    for d in D.index:
        if d not in G or T[d] not in types: continue
        g = G[d]; m = g['m']
        if len(m) < 1000 or m[0] > 5: continue
        A = D.adr.loc[d]
        if not A > 0: continue
        O = g['O'][0]; hi = np.maximum.accumulate(g['H']); lo = np.minimum.accumulate(g['L']); cl = g['C']
        slot = m // 30; R = np.full(NS, np.nan); N = np.full(NS, np.nan)
        for j in range(NS):
            idx = np.where(slot <= j)[0]
            if len(idx): k = idx[-1]; R[j] = (hi[k] - lo[k]) / A; N[j] = (cl[k] - O) / A
        rows.append(dict(t=T[d], R=R, N=N, fin=R[-1]))
    P = pd.DataFrame(rows); out = []; ns = {}
    for t in types:
        x = P[P.t == t]; Rm = np.vstack(x.R.values); Nm = np.vstack(x.N.values); sh = Rm / x.fin.values[:, None]
        for M_ in (Rm, Nm):
            for q in QS: out += list(np.nanquantile(M_, q, axis=0))
        out += list(np.nanmedian(sh, axis=0)); ns[t] = len(x)
    return [int(round(v * 1000)) for v in out], ns
S = open('/home/claude/hol/Hollow.pine', encoding='utf-8').read()
ref = unpack(''.join(re.findall(r'"([^"]*)"', re.search(r'(?m)^CK_NQ\s*=\s*"[^"]*"(?:\n\s+\+\s*"[^"]*")*', S).group(0))))
nq, nsq = clock('NQ', (5, 3, 6))
print('NQ check: len', len(ref), len(nq), 'mean abs diff', np.mean(np.abs(np.array(ref) - np.array(nq))), nsq)
for nm, i in (('NFPwk R med 10:00', 2 * 46 + 31), ('FOMC+1 R med 10:00', 506 + 2 * 46 + 31), ('Normal R med 16:00', 1012 + 2 * 46 + 43)):
    print(f'  {nm}: Hollow {ref[i]} · recomputed {nq[i]}')
rty, ns = clock('RTY', (5, 3, 6)); print('RTY', ns)
e = pack(rty); parts = [e[i:i + 180] for i in range(0, len(e), 180)]
ck = ['CK_RTY = "' + parts[0] + '"'] + [f'     + "{p}"' for p in parts[1:]]
G = CM.days('RTY'); D = CM.ctx('RTY'); idx = list(D.index); recs = []
FO = set(CM.FO)
for i, d in enumerate(idx):
    if i == 0 or idx[i - 1] not in FO or d not in G: continue
    g = CM.Day(G[d]); td = int(np.sign(D.C_TD.loc[d] - D.O.loc[d]))
    ro, rc = g.o(9, 30), g.c(16, 14)
    rth = int(np.sign(rc - ro)) if np.isfinite(ro) and np.isfinite(rc) else 0
    pc = CM.Day(G[idx[i - 1]]).c(16, 14) if idx[i - 1] in G else np.nan
    gap = f'{ro - pc:.1f}' if np.isfinite(ro) and np.isfinite(pc) else ''
    gp = f'{(ro / pc - 1) * 100:.3f}' if gap else ''
    recs.append(f'{d:%Y%m%d},{td},{rth},{gap},{gp}')
chunks = []; cur = ''
for r in recs:
    if len(cur) + len(r) > 200: chunks.append(cur); cur = ''
    cur += r + ';'
chunks.append(cur.rstrip(';'))
tal = ['TAL_RTY = "' + chunks[0] + '"'] + [f'     + "{c}"' for c in chunks[1:]]
print(len(recs), 'day-after-FOMC records, last', recs[-1])
json.dump(dict(ck=ck, tal=tal, end=f'TAL_END_RTY = {idx[-1]:%Y%m%d}', n=ns), open('/home/claude/hol/rty/rty_hollow.json', 'w'))
