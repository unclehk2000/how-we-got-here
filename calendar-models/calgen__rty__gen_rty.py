"""RTY (Russell 2000 E-mini) built-in data for Desgarrón: the event clock (NFP and normal days, same layout as CK_NQ) and the
NFP tally records. Validated by running the same code on NQ and comparing with Desgarrón's CK_NQ."""
import sys, re, json, numpy as np, pandas as pd
sys.path.insert(0, '/home/claude/hm/hydra_cal')
import common as CM
P92 = "!#$%&'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[]^_`abcdefghijklmnopqrstuvwxyz{|}~"
QS = [0.10, 0.25, 0.50, 0.75, 0.90]; NS = 46
def clock(sym):
    G = CM.days(sym); D = CM.ctx(sym); T = CM.day_type(D.index)
    rows = []
    for d in D.index:
        if d not in G or T[d] not in (1, 6): continue
        g = G[d]; m = g['m']
        if len(m) < 1000 or m[0] > 5: continue
        A = D.adr.loc[d]
        if not A > 0: continue
        O = g['O'][0]; hi = np.maximum.accumulate(g['H']); lo = np.minimum.accumulate(g['L']); cl = g['C']
        slot = m // 30; R = np.full(NS, np.nan); N = np.full(NS, np.nan)
        for j in range(NS):
            idx = np.where(slot <= j)[0]
            if len(idx): k = idx[-1]; R[j] = (hi[k] - lo[k]) / A; N[j] = (cl[k] - O) / A
        rows.append(dict(d=d, t=T[d], R=R, N=N, fin=R[-1]))
    P = pd.DataFrame(rows); out = []; ns = {}
    for t in (1, 6):
        x = P[P.t == t]; Rm = np.vstack(x.R.values); Nm = np.vstack(x.N.values); sh = Rm / x.fin.values[:, None]
        for M_ in (Rm, Nm):
            for q in QS: out += list(np.nanquantile(M_, q, axis=0))
        out += list(np.nanmedian(sh, axis=0)); ns[t] = len(x)
    return [int(round(v * 1000)) for v in out], ns
def unpack(s): return [P92.index(s[2 * i]) * 92 + P92.index(s[2 * i + 1]) - 2000 for i in range(len(s) // 2)]
def pack(vals): return ''.join(P92[(v + 2000) // 92] + P92[(v + 2000) % 92] for v in vals)
if __name__ == '__main__':
    S = open('/home/claude/hm/calgen/Desgarron.pine', encoding='utf-8').read()
    blk = re.search(r'(?m)^CK_NQ\s*=\s*"[^"]*"(?:\n\s+\+\s*"[^"]*")*', S).group(0)
    ref = unpack(''.join(re.findall(r'"([^"]*)"', blk)))
    nq, nsq = clock('NQ')
    for nm, i in (('NFP R med 09:00', 0 * 506 + 2 * 46 + 29), ('NFP R med 16:00', 2 * 46 + 43), ('Normal R med 09:00', 506 + 2 * 46 + 29), ('NFP share 09:00', 460 + 29)):
        print(f'{nm}: Desgarrón {ref[i]} · recomputed {nq[i]}')
    print('NQ mean abs diff', np.mean(np.abs(np.array(ref) - np.array(nq))), 'n', nsq)
    rty, ns = clock('RTY')
    print('RTY days', ns, 'values', len(rty))
    e = pack(rty); parts = [e[i:i + 180] for i in range(0, len(e), 180)]
    ck = ['CK_RTY = "' + parts[0] + '"'] + [f'     + "{p}"' for p in parts[1:]]
    # tally
    G = CM.days('RTY'); D = CM.ctx('RTY'); idx = list(D.index); recs = []
    for i, d in enumerate(idx):
        if d not in CM.NP or d not in G: continue
        g = CM.Day(G[d]); td = int(np.sign(D.C_TD.loc[d] - D.O.loc[d]))
        ro, rc = g.o(9, 30), g.c(16, 14)
        rth = int(np.sign(rc - ro)) if np.isfinite(ro) and np.isfinite(rc) else 0
        pc = np.nan
        if i > 0 and idx[i - 1] in G: pc = CM.Day(G[idx[i - 1]]).c(16, 14)
        gap = f'{ro - pc:.1f}' if np.isfinite(ro) and np.isfinite(pc) else ''
        gp = f'{(ro / pc - 1) * 100:.3f}' if gap else ''
        recs.append(f'{d:%Y%m%d},{td},{rth},{gap},{gp}')
    body = ';'.join(recs); chunks = []; cur = ''
    for r in recs:
        if len(cur) + len(r) > 200: chunks.append(cur); cur = ''
        cur += r + ';'
    chunks.append(cur.rstrip(';'))
    tal = ['TAL_RTY = "' + chunks[0] + '"'] + [f'     + "{c}"' for c in chunks[1:]]
    end = f'TAL_END_RTY = {idx[-1]:%Y%m%d}'
    print(len(recs), 'NFP records, last', recs[-1], end)
    json.dump(dict(ck=ck, tal=tal, end=end, n=ns), open('/home/claude/hm/calgen/rty/rty.json', 'w'))
