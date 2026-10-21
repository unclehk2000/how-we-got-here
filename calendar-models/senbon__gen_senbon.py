import json, math, sys
sys.path.insert(0, '/home/claude/hm')
from cardq import P92
R = json.load(open('/home/claude/hm/senbon/dist.json'))
M = json.load(open('/home/claude/hm/senbon/ctx_model2.json'))
def enc(v):
    if v is None or (isinstance(v, float) and math.isnan(v)): u = 8463
    else:
        u = int(round(v)) + 4000; assert 0 <= u < 8463, v
    return P92[u // 92] + P92[u % 92]
def lit(name, vals):
    e = ''.join(enc(v) for v in vals)
    parts = [e[i:i + 184] for i in range(0, len(e), 184)]
    return f'{name} = "' + parts[0] + '"' + ''.join('\n     + "' + p + '"' for p in parts[1:])
L = ['// Quantiles of (close − price at the half hour) ÷ ADR20, context-free (÷ the context multiplier around the median), for each half hour from 18:00 (46 rows × 23 levels: 1, 2.5, 5, 10,',
     '// 15 … 90, 95, 97.5, 99%), every trading day Jan 2018 – Oct 2026 (ES to Aug 2026), ×1000. F_: the share of the full trading',
     "// day's variance (mean squared return, 18:00 → 17:00 = 1000) still ahead at each half hour, for the implied curve."]
for s in ('NQ', 'ES', 'RTY'):
    for t, k in (('TD', 'C_TD'), ('RTH', 'C_RTH')):
        q = [v for row in M['sym'][s]['q_' + t] for v in row]          # context-free rows (location-scale model)
        assert len(q) == 46 * 23
        L.append(lit(f'Q_{s}_{t}', q))
for s in ('NQ', 'ES', 'RTY'):
    for t, k in (('TD', 'C_TD'), ('RTH', 'C_RTH')):
        L.append(lit(f'F_{s}_{t}', R[s][k]['f']))
L.append('// Context multipliers (log scale; 0 = did not hold): per block 18:00–03:00, 03:00–09:30, 09:30–12:00, 12:00–17:00 the five')
L.append("// effects above PDH, below PDL, per ADR under the month's open, per ADR over it, within 0.5 ADR of the ATH")
for s in ('NQ', 'ES', 'RTY'):
    b = [x for blk in M['blocks'] for x in M['sym'][s]['beta'][blk]]
    assert len(b) == 20
    L.append(f'var array<float> B_{s} = array.from(' + ', '.join(f'{x:.4f}' for x in b) + ')')
head = open('/home/claude/hm/senbon/head.pine').read()
body = open('/home/claude/hm/senbon/body.pine').read().replace('%DATA%', '\n'.join(L)).replace('%P92%', P92)
open('/home/claude/hm/senbon/Senbonzakura.pine', 'w').write(head + body)
print('ok', len((head + body).split('\n')), 'lines')
