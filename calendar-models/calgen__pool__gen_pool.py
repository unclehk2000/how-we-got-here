"""Pooled NQ + ES + RTY card data and tooltips for Desgarrón (from hydra_cal/card_pool.json, pool_extra.json)."""
import json
C = json.load(open('/home/claude/hm/hydra_cal/card_pool.json')); X = json.load(open('/home/claude/hm/hydra_cal/pool_extra.json'))
Z = ['discount', 'middle', 'premium']
f2 = lambda v: f'{v:.2f}'; pc = lambda v: f'{100 * v:.0f}%'
def pv(p): return 'p < 0.001' if p < 0.001 else f'p {p:.3f}'
vals, held = [], []
for t in ('m_s1', 'm_s2', 'm_am', 'postRng', 'nRng'):
    for z in range(3):
        a, b, h = C[t][z]; vals += [f2(a), f2(b)]; held += [h['held'], h['held']]
def hl(g, labs):
    for lab in labs:
        for t in ('newHi', 'newLo'):
            x = C[g][lab][t]; vals.append(f'{100 * x["v"]:.0f}' if x['n'] >= 6 else '-1'); held.append(x['held'])
PD = ['above PDH', 'inside PD', 'below PDL']; ST = ['up >0.4 ADR since 18:00', 'flat', 'down >0.4 ADR']
MO = ['over MO >1 ADR', 'within 1 ADR', 'under MO >1 ADR']; VX = ['VIX >10% over its 20d avg', 'VIX near avg', 'VIX >10% under']
WK = ['week up >0.5 ADR into NFP', 'week flat', 'week down >0.5 ADR']
hl('pd3', PD); hl('strong', ST); hl('mo3', Z)
for g, labs in (('dmo3', MO), ('vix3', VX), ('wk3', WK)):
    for lab in labs:
        x = C[g][lab]['postRng']; vals.append(f2(x['v'])); held.append(x['held'])
assert len(vals) == 57
VS = ','.join(vals); VH = ''.join('1' if h else '0' for h in held)
def heldTxt(g, lab, t, what, nice):
    x = C[g][lab][t]
    if not x['held']: return ''
    fm = pc if t not in ('postRng', 'nRng', 'm_am') else f2
    (a1, b1), (a2, b2) = x['halves']; s = x['bysym']
    return (f'✓ {nice}: {what} {fm(x["v"])} vs {fm(x["o"])} (2018–24 {fm(a1)} vs {fm(b1)}, 2025–26 {fm(a2)} vs {fm(b2)}; NQ {fm(s[0][0])} · ES {fm(s[1][0])} · RTY {fm(s[2][0])}; {pv(x["p"])})')
def grp(g, labs, nice, what_t):
    out = []
    for lab, nm in zip(labs, nice):
        for t, w in what_t:
            s = heldTxt(g, lab, t, w, nm)
            if s: out.append(s)
    return '; '.join(out) + '.' if out else 'none held.'
def n(g, lab): return C[g][lab]['newHi']['n']
HLW = (('newHi', 'new day high after 08:30'), ('newLo', 'new day low after 08:30'))
POOL = 'Pooled NQ + ES + RTY, 99 NFP releases 2018–26 (293 symbol-days). '
def hlrow(g, labs, nice):
    return ' · '.join(f'{nm} (n {n(g, lab)}) H{pc(C[g][lab]["newHi"]["v"])} L{pc(C[g][lab]["newLo"]["v"])}' for lab, nm in zip(labs, nice))
def rrow(g, labs, nice):
    return ' · '.join(f'{nm} (n {n(g, lab)}) {f2(C[g][lab]["postRng"]["v"])}' for lab, nm in zip(labs, nice))
T = {}
ZN = ['discount', 'middle', 'premium']
T['MON'] = (POOL + "By the month's position at 08:29 (bottom quarter = discount, top quarter = premium). Right: how often the day made a new high (H) and a new low (L) after 08:30. "
            + hlrow('mo3', Z, ZN) + '. Held: ' + grp('mo3', Z, ZN, HLW + (('postRng', 'range after 08:30 (ADR)'),)) + ' The EXPECT rows use this group.')
T['MO'] = (POOL + "Over / under = more than 1 ADR from the month's open at 08:29. Right: R = the range after 08:30, ADR (median). " + rrow('dmo3', MO, ['over', 'within 1 ADR', 'under'])
           + '. Held: ' + grp('dmo3', MO, ['over', 'within', 'under'], (('postRng', 'range after 08:30'),)))
T['PD'] = (POOL + "Against the prior trading day's high (PDH) and low (PDL) at 08:29. Right: new high (H) / new low (L) after 08:30. " + hlrow('pd3', PD, ['above PDH', 'inside', 'below PDL'])
           + '. Held: ' + grp('pd3', PD, ['above PDH', 'inside', 'below PDL'], HLW))
T['18'] = (POOL + "Move from the 18:00 open to 08:29, in ADR; strong = beyond ±0.4. Right: new high (H) / new low (L) after 08:30. " + hlrow('strong', ST, ['up > 0.4 ADR', 'within', 'down > 0.4 ADR'])
           + '. Held: ' + grp('strong', ST, ['up > 0.4 ADR', 'within', 'down > 0.4 ADR'], HLW))
T['WK'] = (POOL + "The week into the release: Sunday's 18:00 open to 08:29 Friday, in ADR; up / down = beyond ±0.5. Right: R = the range after 08:30, ADR. " + rrow('wk3', WK, ['week up', 'flat', 'week down'])
           + '. Held: ' + grp('wk3', WK, ['week up', 'flat', 'week down'], (('postRng', 'range after 08:30'),)) + ' A strong week into NFP came with a smaller reaction, a weak week with a bigger one.')
T['VX'] = (POOL + "VIX's prior close against its 20-day average (±10%). Right: R = the range after 08:30, ADR. " + rrow('vix3', VX, ['over', 'near', 'under'])
           + '. Held: ' + grp('vix3', VX, ['VIX > 10% over', 'near', '> 10% under'], (('postRng', 'range after 08:30'),)))
def sz(t): return ' · '.join(f2(C[t][z][0]) for z in range(3)) + ' ADR (80%: ' + ' · '.join(f2(C[t][z][1]) for z in range(3)) + ')' + (
    ' — held for ' + ', '.join(ZN[z] for z in range(3) if C[t][z][2]['held']) if any(C[t][z][2]['held'] for z in range(3)) else '')
T['E'] = (POOL + "Median and 80th percentile by the month's position (discount · middle · premium; n " + ' · '.join(str(n('mo3', z)) for z in Z) + "), at today's ADR20. "
          + f"|stage 1| 08:30–08:50: {sz('m_s1')}; |stage 2| 08:50–09:30: {sz('m_s2')}; |NY AM| 09:30–11:00: {sz('m_am')}; range after 08:30: {sz('postRng')}; the next session's range (Monday): {sz('nRng')}. Sizes for stops and targets: which way it goes did not hold.")
s1, s2, ad = X['s1'], X['s2'], X['add']
T['DR'] = (f"Index against DXY futures in the same window, Feb 2023 – Jul 2026, pooled NQ + ES + RTY. Stage 1 (08:30–08:50): with DXY ≥ {s1['thr']:.2f} of its ADR20 (BIG) the index went the other way "
           f"{pc(s1['big'])} (n {s1['n']} on {s1['dates']} releases; 2023–24 {pc(s1['h1'])}, 2025–26 {pc(s1['h2'])}; NQ {pc(s1['per']['NQ'])} · ES {pc(s1['per']['ES'])} · RTY {pc(s1['per']['RTY'])}; {pv(s1['p'])}; held) vs {pc(s1['small'])} when smaller. "
           f"Stage 2 (08:50–09:30): with DXY ≥ {s2['thr']:.2f} (BIG) {pc(s2['big'])} (n {s2['n']}; 2023–24 {pc(s2['h1'])}, 2025–26 {pc(s2['h2'])}; NQ {pc(s2['per']['NQ'])} · ES {pc(s2['per']['ES'])} · RTY {pc(s2['per']['RTY'])}; {pv(s2['p'])}; held) vs {pc(s2['small'])}. "
           "It confirms the stage, it does not call it.")
T['AD'] = (f"How much the day's range (from 18:00) grows from 08:30 to 09:00, in ADR20. NFP days, pooled: +{ad['nfp']:.2f}× at the median (mean +{ad['nfp_mean']:.2f}×) vs 0 on ordinary days (mean +{ad['norm_mean']:.2f}×) (2018–24 +{ad['h'][0]:.2f}×, 2025–26 +{ad['h'][1]:.2f}×; "
           f"NQ +{ad['per']['NQ']:.2f} · ES +{ad['per']['ES']:.2f} · RTY +{ad['per']['RTY']:.2f}; {pv(ad['p'])}; held). The release half hour does the day's work.")
fw = lambda g, lab: C[g][lab]['firstWon']
T['FS'] = (f"First side of the 07:00–08:29 range taken after 08:30, and whether it became the bigger side of the day (from the 08:29 price to the 16:14 high / low). All NFP days: {pc(C['all']['firstWon'])}. "
           f"Held: ✓ VIX > 10% under its average {pc(fw('vix3', VX[2])['v'])} vs {pc(fw('vix3', VX[2])['o'])} ({pv(fw('vix3', VX[2])['p'])}); ✓ week up > 0.5 ADR {pc(fw('wk3', WK[0])['v'])} vs {pc(fw('wk3', WK[0])['o'])} ({pv(fw('wk3', WK[0])['p'])}); "
           f"week flat {pc(fw('wk3', WK[1])['v'])}. Not held: a quiet night (18:00–08:29 range ≤ 0.36 ADR) 71% vs 53%, but 67% vs 68% in 2025–26. A coin-flip-plus, not a call.")
ce = C['ce4']
T['CE'] = ("The 50% between the all-time high and the 08:29 price, touched by 17:00? Pooled NFP days by the CE's distance from price at 08:29: "
           + ' · '.join(f"{k} ADR {pc(v['ceDay'])} (n {v['n']})" for k, v in ce.items())
           + f". Held: ✓ within 1 ADR of the ATH (CE ≤ 0.5 ADR away) {pc(C['ath3']['within 1 ADR of ATH']['ceDay']['v'])} vs 3% (NQ 88% · ES 75% · RTY 73%; 2025–26 50%). The ATH itself traded in RTH on {pc(C['all']['athRTH'])} of NFP days.")
T['DIR'] = ("HYDRA, pooled NQ + ES + RTY (240 training rows on 80 releases 2018–24, errors clustered by date; 406 heads × 18 targets; 20 shifted-target nulls; locked 2025–26 test plus the same sign on all three symbols). "
            "Direction: stage 1, stage 2, NY AM, RTH and 08:30→16:14 had no more survivors than the nulls (2 / 1 / 8 / 0 / 5 vs null means 6.5 / 8.6 / 2.6 / 3.9 / 7.5, NY AM null max 18); 1 of 283 heads held for 08:30→16:14, a chance count. "
            "What held: the size of the day (range after 08:30 32 heads, Monday 38, |NY AM| 7), new high 27 and new low 30 after 08:30, the ATH CE 28 and the first DR side 14. Whole net, 2025–26 AUC: new low 0.85, new high 0.83, CE 0.93, first side 0.70; directions 0.41–0.65.")
lines = [f'var array<float> VS = parseStats("{VS}")', f'VH = "{VH}"']
for k, v in T.items():
    lines.append(f'VZT_{k} = "' + v.replace('"', "'") + '"')
open('/home/claude/hm/calgen/pool/pool_block.pine', 'w').write('\n'.join(lines) + '\n')
print('\n'.join(l[:300] for l in lines)); print(sum(len(v) for v in T.values()), 'tooltip chars')
