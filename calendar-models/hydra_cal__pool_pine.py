"""Pine data for Desgarrón from the pooled NQ + ES + RTY NFP study: the stages card's VS / VH arrays, the octant table and
the tooltips. Writes /home/claude/hm/calgen/frag/desg_pool.pine"""
import json
C = json.load(open('card_pool.json')); X = json.load(open('pool_extra.json')); F = json.load(open('dr_first.json'))
R = json.load(open('clock_rty.json'))
vs, vh = [], []
for st in ('m_s1', 'm_s2', 'm_am', 'postRng', 'nRng'):
    for z in range(3):
        med, p80, s = C[st][z]; vs += [f'{med:.2f}', f'{p80:.2f}']; vh += ['1' if s['held'] else '0', '0']
GR = dict(pd3=['above PDH', 'inside PD', 'below PDL'], strong=['up >0.4 ADR since 18:00', 'flat', 'down >0.4 ADR'], mo3=['discount', 'middle', 'premium'])
for g in ('pd3', 'strong', 'mo3'):
    for lab in GR[g]:
        for t in ('newHi', 'newLo'):
            x = C[g][lab][t]; vs.append(str(round(100 * x['v'])) if x['n'] >= 12 else '-1'); vh.append('1' if x['held'] else '0')
SZ = dict(dmo3=['over MO >1 ADR', 'within 1 ADR', 'under MO >1 ADR'], vix3=['VIX >10% over its 20d avg', 'VIX near avg', 'VIX >10% under'],
          wk3=['week up >0.5 ADR into NFP', 'week flat', 'week down >0.5 ADR'])
for g in ('dmo3', 'vix3', 'wk3'):
    for lab in SZ[g]:
        x = C[g][lab]['postRng']; vs.append(f"{x['v']:.2f}"); vh.append('1' if x['held'] else '0')
assert len(vs) == 57 and len(vh) == 57
oc = ';'.join(f"{C['oct'][str(o)]['n']},{C['oct'][str(o)]['postRng']:.2f},{round(100 * C['oct'][str(o)]['newHi'])},{round(100 * C['oct'][str(o)]['newLo'])}" for o in range(1, 9))
P = lambda v: f'{100 * v:.0f}%'
def held_txt(g, lab, stats=('postRng', 'newHi', 'newLo'), unit=None):
    out = []
    for t in stats:
        x = C[g][lab][t]
        if not x['held']: continue
        nm = dict(postRng='range after 08:30', newHi='new high after 08:30', newLo='new low after 08:30', m_am='|NY AM|', nRng="Monday's range", firstWon='first DR side won', ceDay='ATH CE touched')[t]
        f = (lambda v: f'{v:.2f}') if t in ('postRng', 'm_am', 'nRng') else P
        (a, b), (c, d) = x['halves']
        out.append(f"{nm} {f(x['v'])} vs {f(x['o'])} (2018–24 {f(a)} vs {f(b)}, 2025–26 {f(c)} vs {f(d)})")
    return '; '.join(out)
def grp_tip(g, labs, short):
    parts, held = [], []
    for lab, sh in zip(labs, short):
        x = C[g][lab]
        parts.append(f"{sh} (n {x['postRng']['n']}) R{x['postRng']['v']:.2f} H{P(x['newHi']['v'])} L{P(x['newLo']['v'])}")
        h = held_txt(g, lab)
        if h: held.append(f'✓ {sh}: {h}')
    return ' · '.join(parts) + '. Held: ' + ('; '.join(held) if held else 'none') + '.'
POOL = "NFP days 2018–26, NQ + ES + RTY pooled (293 symbol-days on 99 releases), read at 08:29, in ADR20. "
RULE = " ✓ = p < 0.05 with errors clustered by release date, the same side in 2018–24 and 2025–26, and on NQ, ES and RTY separately."
tips = {}
tips['VZT_MON'] = POOL + "By the month's position (bottom quarter = discount, top quarter = premium). R = range after 08:30, H / L = new day high / low after 08:30. " + grp_tip('mo3', GR['mo3'], ['discount', 'middle', 'premium']) + RULE
tips['VZT_MO'] = POOL + "Over / under = more than 1 ADR from the month's open. " + grp_tip('dmo3', SZ['dmo3'], ['over', 'within', 'under']) + RULE
tips['VZT_PD'] = POOL + "Against the prior day's high (PDH) and low (PDL). " + grp_tip('pd3', GR['pd3'], ['above PDH', 'inside', 'below PDL']) + RULE
tips['VZT_18'] = POOL + "Move from the 18:00 open to 08:29; strong = beyond ±0.4 ADR. " + grp_tip('strong', GR['strong'], ['up', 'within', 'down']) + RULE
tips['VZT_WK'] = POOL + "The week into the release (Sunday 18:00 open to 08:29 Friday); up / down = beyond ±0.5 ADR. " + grp_tip('wk3', SZ['wk3'], ['week up', 'flat', 'week down']) + " A strong week into NFP came with a smaller reaction, a weak week with a bigger one." + RULE
tips['VZT_VX'] = POOL + "VIX's prior close against its 20-day average (±10%). " + grp_tip('vix3', SZ['vix3'], ['over', 'near', 'under']) + RULE
def ex(st, nm):
    return f"{nm}: " + ' · '.join(f"{C[st][z][0]:.2f}" for z in range(3)) + " ADR (80%: " + ' · '.join(f"{C[st][z][1]:.2f}" for z in range(3)) + ")" + (" — held for " + ', '.join(w for z, w in enumerate(['discount', 'middle', 'premium']) if C[st][z][2]['held']) if any(C[st][z][2]['held'] for z in range(3)) else '')
tips['VZT_E'] = POOL + "Median and 80th percentile by the month's position (discount · middle · premium; n 66 · 101 · 126), at today's ADR20. " + '; '.join([ex('m_s1', '|stage 1| 08:30–08:50'), ex('m_s2', '|stage 2| 08:50–09:30'), ex('m_am', '|NY AM| 09:30–11:00'), ex('postRng', 'range after 08:30'), ex('nRng', "the next session's range (Monday)")]) + ". Sizes for stops and targets: no direction held."
d1, d2, ad = X['s1'], X['s2'], X['add']
tips['VZT_DR'] = (f"Index against DXY futures in the same window, Feb 2023 – Jul 2026, NQ + ES + RTY pooled. Stage 1 (08:30–08:50): with DXY ≥ {d1['thr']:.2f} of its ADR20 (BIG) the index went the other way {P(d1['big'])} "
                  f"(n {d1['n']} on {d1['dates']} releases; 2023–24 {P(d1['h1'])}, 2025–26 {P(d1['h2'])}; NQ {P(d1['per']['NQ'])}, ES {P(d1['per']['ES'])}, RTY {P(d1['per']['RTY'])}; p {d1['p']:.3f}) vs {P(d1['small'])} when smaller. "
                  f"Stage 2 (08:50–09:30): BIG ≥ {d2['thr']:.2f}: {P(d2['big'])} (n {d2['n']}; 2023–24 {P(d2['h1'])}, 2025–26 {P(d2['h2'])}; NQ {P(d2['per']['NQ'])}, ES {P(d2['per']['ES'])}, RTY {P(d2['per']['RTY'])}; p {d2['p']:.3f}) vs {P(d2['small'])}. "
                  "It confirms the stage, it does not call it.")
tips['VZT_AD'] = (f"How much the day's range (from 18:00) grows from 08:30 to 09:00, in ADR20. NFP days: +{ad['nfp']:.2f}× at the median vs +{ad['norm']:.2f}× on ordinary days "
                  f"(2018–24 +{ad['h'][0]:.2f}×, 2025–26 +{ad['h'][1]:.2f}×; NQ +{ad['per']['NQ']:.2f}, ES +{ad['per']['ES']:.2f}, RTY +{ad['per']['RTY']:.2f}; held). Value: today, live until 09:00 then fixed.")
q = F['preRng_narrow']; vu = C['vix3']['VIX >10% under']['firstWon']; wu = C['wk3']['week up >0.5 ADR into NFP']['firstWon']; wf = C['wk3']['week flat']['firstWon']
tips['VZT_FS'] = (f"First side of the pre-release range (07:00–08:29) taken after 08:30, and whether the day then reached further that way than the other (high vs low after 08:30, from 08:29). "
                  f"All NFP days: {P(C['all']['firstWon'])}. Held: ✓ quiet pre-release (range since 18:00 ≤ {q['cut'][0]:.2f} ADR, n {q['n']}) {P(q['won'])} vs {P(q['rest'])} (2018–24 {P(q['h1'])}, 2025–26 {P(q['h2'])}; p {q['p']:.3f}); "
                  f"✓ VIX > 10% under its average {P(vu['v'])} vs {P(vu['o'])}; ✓ week up > 0.5 ADR {P(wu['v'])} vs {P(wu['o'])}; flat week {P(wf['v'])} vs {P(wf['o'])} (held, lower). The first break is a lean, not a call: it was wrong on about 4 in 10 days.")
tips['VZT_CE'] = ("ATH CE = halfway between the all-time high and the 08:29 close, drawn from 08:30 to 17:00. Touched by 17:00 on pooled NFP days, by its distance at 08:29: ≤ 0.5 ADR 79% (n 63; 2018–24 91%, 2025–26 50%; NQ 88, ES 75, RTY 73) · "
                  "0.5–1 ADR 23% (n 26) · 1–2 ADR 1% (n 71) · > 2 ADR 0% (n 133). Within 0.5 ADR the ATH itself was taken by 17:00 on 56%. HYDRA: distance is the whole story (the whole-net AUC 0.93 on 2025–26 is the distance effect).")
tips['VZT_HY'] = ("HYDRA on NQ + ES + RTY pooled: 406 heads × 18 targets on 240 symbol-days (80 releases, 2018–24), errors clustered by date, Benjamini–Hochberg 10% against 20 shifted nulls; survivors tested on 2025–26 (53 symbol-days) and on each symbol. "
                  "Direction: stage 1, stage 2, RTH, 08:30 → 16:14 and day-against-the-week found no more survivors than their nulls; NY AM up found 8 against a null mean of 2.6 (max 18) and none held; 1 direction head of 283 survivors held in the test (chance level); the whole net's direction AUCs sat at the null's 95th percentile (0.62–0.65). Sizes and extremes: 177 of 283 held — the range after 08:30, |NY AM|, Monday's range, new high / low after 08:30, the ATH CE and the first DR side. "
                  "So the pane sizes the day and gives the odds that held; it does not call a side.")
out = ['// ── pooled NQ + ES + RTY card data (generated by hydra_cal/pool_pine.py)',
       f'var array<float> VS = parseStats("{",".join(vs)}")', f'VH = "{"".join(vh)}"', f'var array<float> OC = parseStats("{oc}")']
for k, v in tips.items():
    assert '"' not in v, k
    out.append(f'var string {k} = "{v}"')
out.append('CK_RTY = ' + '\n     + '.join('"' + R['RTY']['enc'][i:i + 180] + '"' for i in range(0, len(R['RTY']['enc']), 180)))
recs = R['RTY']['recs']
out.append('TAL_RTY = ' + '\n     + '.join('"' + ';'.join(recs[i:i + 8]) + (';' if i + 8 < len(recs) else '') + '"' for i in range(0, len(recs), 8)))
out.append(f"TAL_END_RTY = {R['RTY']['end']}")
open('/home/claude/hm/calgen/frag/desg_pool.pine', 'w', encoding='utf-8').write('\n'.join(out) + '\n')
print('VS', ','.join(vs)); print('VH', ''.join(vh)); print('OC', oc); print({k: len(v) for k, v in tips.items()}, 'RTY n', R['RTY']['n'])
