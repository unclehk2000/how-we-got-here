"""Pooled NQ + ES + RTY data block for Hollow v3: VS (170 values), VH and the tooltips."""
import json
W = json.load(open('/home/claude/hm/hydra_cal/card_pool_wk.json')); Fa = json.load(open('/home/claude/hm/hydra_cal/card_pool_fa.json'))
NW = json.load(open('/home/claude/hm/hydra_cal/nwog_pool.json'))
Z = ['discount', 'middle', 'premium']; PD = ['above PDH', 'inside PD', 'below PDL']; ST = ['up >0.4 ADR since 18:00', 'flat', 'down >0.4 ADR']
MO = ['over MO >1 ADR', 'within 1 ADR', 'under MO >1 ADR']; VX = ['VIX >10% over its 20d avg', 'VIX near avg', 'VIX >10% under']
GP = ['gap up >0.25 ADR', 'small gap', 'gap down >0.25 ADR']; DW = ['Monday', 'Tuesday', 'Wednesday', 'Thursday']
FP = ['FOMC 14:00→16:14 up', 'FOMC 14:00→16:14 down']; FC = ['FOMC closed top quarter', 'FOMC closed middle', 'FOMC closed bottom quarter']
BIN = ('newHi', 'newLo', 'gapFill', 'ce10', 'ce50', 'q4held', 'takeFH', 'takeFL', 'y_am', 'y_rth')
V, H = [], []
def val(x, t): return f'{100 * x["v"]:.0f}' if t in BIN else f'{x["v"]:.2f}'
def g(D, grp, labs, t):
    for lab in labs:
        x = D[grp][lab][t]
        V.append(val(x, t) if x['n'] >= 6 else '-1'); H.append(x['held'])
def sizes(D, ts):
    for t in ts:
        for z in range(3):
            a, b, h = D[t][z]; V.extend([f'{a:.2f}', f'{b:.2f}']); H.extend([h['held'], h['held']])
def hl(D, grp, labs):
    for lab in labs:
        for t in ('newHi', 'newLo'):
            x = D[grp][lab][t]; V.append(val(x, t) if x['n'] >= 6 else '-1'); H.append(x['held'])
# NFP week 0–57
sizes(W, ('m_am', 'rthRng', 'settleRng', 'nRng'))                  # 0–23
hl(W, 'pd3', PD); hl(W, 'strong', ST); hl(W, 'mo3', Z)               # 24–41
g(W, 'dmo3', MO, 'rthRng'); g(W, 'vix3', VX, 'rthRng')             # 42–47
g(W, 'gap3', GP, 'ce10'); g(W, 'gap3', GP, 'gapFill')               # 48–53
g(W, 'dow3', DW, 'ce10')                                             # 54–57
# day after FOMC 58–102
sizes(Fa, ('m_am', 'rthRng', 'nRng'))                                # 58–75
hl(Fa, 'pd3', PD); hl(Fa, 'strong', ST)                              # 76–87
for z in Z:                                                          # 88–93
    for t in ('takeFH', 'takeFL'):
        x = Fa['mo3'][z][t]; V.append(val(x, t)); H.append(x['held'])
g(Fa, 'vix3', VX, 'rthRng')                                          # 94–96
g(Fa, 'gap3', GP, 'gapFill'); g(Fa, 'gap3', GP, 'ce50')             # 97–102
# extras 103–154
g(W, 'gap3', GP, 'q4held'); g(W, 'gap3', GP, 'ce50')                # 103–108
hl(W, 'gap3', GP)                                                    # 109–114
g(W, 'pd3', PD, 'rthRng'); g(W, 'strong', ST, 'rthRng'); g(W, 'gap3', GP, 'rthRng')   # 115–123
for grp, labs in (('fp3', FP), ('gap3', GP), ('fc3', FC)):          # 124–139
    for lab in labs:
        for t in ('takeFH', 'takeFL'):
            x = Fa[grp][lab][t]; V.append(val(x, t)); H.append(x['held'])
hl(Fa, 'gap3', GP); hl(Fa, 'mo3', Z)                                 # 140–151
g(Fa, 'gap3', GP, 'q4held')                                          # 152–154
# bases 155–169
aw, af = W['all'], Fa['all']
for t in ('rthRng', 'newHi', 'newLo', 'ce10', 'gapFill', 'q4held'): V.append(f'{aw[t]:.2f}' if t == 'rthRng' else f'{100 * aw[t]:.0f}'); H.append(False)
for t in ('takeFH', 'takeFL', 'newHi', 'newLo', 'rthRng', 'gapFill', 'ce50', 'q4held', 'nRng'): V.append(f'{af[t]:.2f}' if t in ('rthRng', 'nRng') else f'{100 * af[t]:.0f}'); H.append(False)
assert len(V) == 170, len(V)
VS = ','.join(V); VH = ''.join('1' if h else '0' for h in H)
pc = lambda v: f'{100 * v:.0f}%'; f2 = lambda v: f'{v:.2f}'
def pv(p): return 'p < 0.001' if p < 0.001 else f'p {p:.3f}'
def held(D, grp, lab, t, nice, what):
    x = D[grp][lab][t]
    if not x['held']: return ''
    fm = pc if t in BIN else f2; (a1, b1), (a2, b2) = x['halves']; s = x['bysym']
    return f'✓ {nice}: {what} {fm(x["v"])} vs {fm(x["o"])} (2018–24 {fm(a1)} vs {fm(b1)}, 2025–26 {fm(a2)} vs {fm(b2)}; NQ {fm(s[0][0])} · ES {fm(s[1][0])} · RTY {fm(s[2][0])}; {pv(x["p"])})'
def heldAll(D, grp, labs, nices, tw):
    out = [held(D, grp, l, t, n, w) for l, n in zip(labs, nices) for t, w in tw]; out = [o for o in out if o]
    return ('Held: ' + '; '.join(out) + '.') if out else 'Nothing here held.'
def cnt(D, grp, lab): return D[grp][lab]['newHi']['n']
PW = f"NQ + ES + RTY pooled, {W['dates']} NFP-week Mon–Thu 2018–26 ({W['n']} symbol-days), read at 09:29. "
PF = f"NQ + ES + RTY pooled, {Fa['dates']} days after FOMC 2018–26 ({Fa['n']} symbol-days), read at 09:29. "
HL = (('newHi', 'new day high after 09:30'), ('newLo', 'new day low after 09:30'))
T = {}
T['WMON'] = PW + "By the month's position (bottom quarter = discount, top quarter = premium). Right: new day high (H) / new low (L) after 09:30. " + ' · '.join(f"{n} (n {cnt(W, 'mo3', z)}) H{pc(W['mo3'][z]['newHi']['v'])} L{pc(W['mo3'][z]['newLo']['v'])}" for z, n in zip(Z, Z)) + '. ' + heldAll(W, 'mo3', Z, Z, HL) + ' The EXPECT rows use this group.'
T['WMO'] = PW + "Over / under = more than 1 ADR from the month's open. Right: R = the RTH range, ADR. " + ' · '.join(f"{n} (n {cnt(W, 'dmo3', l)}) {f2(W['dmo3'][l]['rthRng']['v'])}" for l, n in zip(MO, ['over', 'within', 'under'])) + '. ' + heldAll(W, 'dmo3', MO, ['over', 'within', 'under'], (('rthRng', 'RTH range'),))
T['WPD'] = PW + "Against the prior day's high and low. Right: H / L after 09:30. " + ' · '.join(f"{n} (n {cnt(W, 'pd3', l)}) H{pc(W['pd3'][l]['newHi']['v'])} L{pc(W['pd3'][l]['newLo']['v'])}" for l, n in zip(PD, ['above PDH', 'inside', 'below PDL'])) + '. ' + heldAll(W, 'pd3', PD, ['above PDH', 'inside', 'below PDL'], HL)
T['W18'] = PW + "Overnight: the 18:00 open to 09:29, in ADR; strong = beyond ±0.4. Right: H / L after 09:30. " + ' · '.join(f"{n} (n {cnt(W, 'strong', l)}) H{pc(W['strong'][l]['newHi']['v'])} L{pc(W['strong'][l]['newLo']['v'])}" for l, n in zip(ST, ['up > 0.4', 'within', 'down > 0.4'])) + '. ' + heldAll(W, 'strong', ST, ['up > 0.4 ADR', 'within', 'down > 0.4 ADR'], HL)
T['WGP'] = PW + "RTH gap = 09:30 open − prior 16:14 close, in ADR. Right: ½ = the gap's 50% traded by 10:00, F = the whole gap filled by 16:14. " + ' · '.join(f"{n} (n {cnt(W, 'gap3', l)}) ½{pc(W['gap3'][l]['ce10']['v'])} F{pc(W['gap3'][l]['gapFill']['v'])}" for l, n in zip(GP, ['gap up > 0.25 ADR', 'smaller', 'gap down > 0.25 ADR'])) + '. ' + heldAll(W, 'gap3', GP, ['gap up', 'smaller', 'gap down'], (('ce10', 'gap 50% by 10:00'), ('gapFill', 'gap filled by 16:14')))
T['WVX'] = PW + "VIX's prior close against its 20-day average (±10%). Right: R = the RTH range, ADR. " + ' · '.join(f"{n} (n {cnt(W, 'vix3', l)}) {f2(W['vix3'][l]['rthRng']['v'])}" for l, n in zip(VX, ['over', 'near', 'under'])) + '. ' + heldAll(W, 'vix3', VX, ['VIX over', 'near', 'VIX under'], (('rthRng', 'RTH range'),))
T['WDY'] = PW + "The gap's 50% by 10:00 by weekday: " + ' · '.join(f"{d[:3]} (n {cnt(W, 'dow3', d)}) {pc(W['dow3'][d]['ce10']['v'])}" for d in DW) + '. ' + heldAll(W, 'dow3', DW, DW, (('ce10', 'gap 50% by 10:00'),))
def szs(D, t): return ' · '.join(f2(D[t][z][0]) for z in range(3)) + ' ADR (80%: ' + ' · '.join(f2(D[t][z][1]) for z in range(3)) + ')' + ((' — held for ' + ', '.join(Z[z] for z in range(3) if D[t][z][2]['held'])) if any(D[t][z][2]['held'] for z in range(3)) else '')
T['WE'] = PW + "Median and 80th percentile by the month's position (discount · middle · premium; n " + ' · '.join(str(cnt(W, 'mo3', z)) for z in Z) + f"), at today's ADR20. |NY AM| 09:30–11:00: {szs(W, 'm_am')}; RTH range: {szs(W, 'rthRng')}; settlement window 16:15–17:00 range: {szs(W, 'settleRng')}; next day's range: {szs(W, 'nRng')}. Sizes for stops and targets: which way it goes did not hold."
dw, df = W['dxy'], Fa['dxy']
T['WDR'] = (f"Index against DXY futures in the same window, Feb 2023 – Jul 2026, NQ + ES + RTY pooled. RTH 09:30–16:14: with DXY ≥ {dw['rth']['thr']:.2f} of its ADR20 (BIG) the index went the other way {pc(dw['rth']['big'])} "
            f"(n {dw['rth']['n']} on {dw['rth']['dates']} days; 2023–24 {pc(dw['rth']['h1'])}, 2025–26 {pc(dw['rth']['h2'])}; NQ {pc(dw['rth']['per']['NQ'])} · ES {pc(dw['rth']['per']['ES'])} · RTY {pc(dw['rth']['per']['RTY'])}; {pv(dw['rth']['p'])}; held) vs {pc(dw['rth']['small'])} when smaller. "
            f"NY AM: with DXY ≥ {dw['am']['thr']:.2f}, {pc(dw['am']['big'])} (2023–24 {pc(dw['am']['h1'])}, 2025–26 {pc(dw['am']['h2'])}; {pv(dw['am']['p'])}; held, barely) vs {pc(dw['am']['small'])}. It confirms the move, it does not call it.")
T['FMON'] = PF + "By the month's position. Right: how often RTH took the FOMC day's high (FH) and low (FL). " + ' · '.join(f"{z} (n {cnt(Fa, 'mo3', z)}) FH{pc(Fa['mo3'][z]['takeFH']['v'])} FL{pc(Fa['mo3'][z]['takeFL']['v'])}" for z in Z) + '. ' + heldAll(Fa, 'mo3', Z, Z, (('takeFH', 'took the FOMC high'), ('takeFL', 'took the FOMC low'))) + ' The EXPECT rows use this group.'
T['FPD'] = PF + "Against the FOMC day's high and low at 09:29. Right: H / L after 09:30. " + ' · '.join(f"{n} (n {cnt(Fa, 'pd3', l)}) H{pc(Fa['pd3'][l]['newHi']['v'])} L{pc(Fa['pd3'][l]['newLo']['v'])}" for l, n in zip(PD, ['above the FOMC high', 'inside', 'below the FOMC low'])) + '. ' + heldAll(Fa, 'pd3', PD, ['above the FOMC high', 'inside', 'below the FOMC low'], HL) + ' (Above the FOMC high at 09:29, RTH takes it by construction.)'
T['F18'] = PF + "Overnight after the decision: the 18:00 open to 09:29, in ADR. Right: H / L after 09:30. " + ' · '.join(f"{n} (n {cnt(Fa, 'strong', l)}) H{pc(Fa['strong'][l]['newHi']['v'])} L{pc(Fa['strong'][l]['newLo']['v'])}" for l, n in zip(ST, ['up > 0.4', 'within', 'down > 0.4'])) + '. ' + heldAll(Fa, 'strong', ST, ['up > 0.4 ADR', 'within', 'down > 0.4 ADR'], HL)
T['FGP'] = PF + "RTH gap = 09:30 open − FOMC day's 16:14 close, in ADR. Right: F = the whole gap filled by 16:14, ½ = its 50% traded in NY AM. " + ' · '.join(f"{n} (n {cnt(Fa, 'gap3', l)}) F{pc(Fa['gap3'][l]['gapFill']['v'])} ½{pc(Fa['gap3'][l]['ce50']['v'])}" for l, n in zip(GP, ['gap up > 0.25 ADR', 'smaller', 'gap down > 0.25 ADR'])) + '. ' + heldAll(Fa, 'gap3', GP, ['gap up', 'smaller', 'gap down'], (('gapFill', 'gap filled by 16:14'), ('ce50', 'gap 50% in NY AM')))
T['FVX'] = PF + "VIX's prior close against its 20-day average. Right: R = the RTH range, ADR. " + ' · '.join(f"{n} (n {cnt(Fa, 'vix3', l)}) {f2(Fa['vix3'][l]['rthRng']['v'])}" for l, n in zip(VX, ['over', 'near', 'under'])) + '. ' + heldAll(Fa, 'vix3', VX, ['VIX over', 'near', 'VIX under'], (('rthRng', 'RTH range'),))
T['FE'] = PF + "Median and 80th percentile by the month's position (discount · middle · premium; n " + ' · '.join(str(cnt(Fa, 'mo3', z)) for z in Z) + f"), at today's ADR20. |NY AM| 09:30–11:00: {szs(Fa, 'm_am')}; RTH range: {szs(Fa, 'rthRng')}; next day's range: {szs(Fa, 'nRng')}. Sizes for stops and targets: which way it goes did not hold."
T['FDR'] = (f"Index against DXY futures in the same window, Feb 2023 – Jul 2026, NQ + ES + RTY pooled. RTH 09:30–16:14: with DXY ≥ {df['rth']['thr']:.2f} of its ADR20 (BIG) the index went the other way {pc(df['rth']['big'])} "
            f"(n {df['rth']['n']} on {df['rth']['dates']} days; 2023–24 {pc(df['rth']['h1'])}, 2025–26 {pc(df['rth']['h2'])}; NQ {pc(df['rth']['per']['NQ'])} · ES {pc(df['rth']['per']['ES'])} · RTY {pc(df['rth']['per']['RTY'])}; {pv(df['rth']['p'])}; held) vs {pc(df['rth']['small'])} when smaller. "
            f"NY AM: {pc(df['am']['big'])} with a big DXY move ({pv(df['am']['p'])}; not held). It confirms the move, it does not call it.")
T['FP'] = PF + "The FOMC day's own afternoon, 14:00 → 16:14. Right: FH / FL = RTH took the FOMC high / low the next day. " + ' · '.join(f"{n} (n {cnt(Fa, 'fp3', l)}) FH{pc(Fa['fp3'][l]['takeFH']['v'])} FL{pc(Fa['fp3'][l]['takeFL']['v'])}" for l, n in zip(FP, ['up', 'down'])) + '. ' + heldAll(Fa, 'fp3', FP, ['afternoon up', 'afternoon down'], (('takeFH', 'took the FOMC high'), ('takeFL', 'took the FOMC low'))) + ' By where the FOMC day closed in its range: ' + ' · '.join(f"{n} FH{pc(Fa['fc3'][l]['takeFH']['v'])} FL{pc(Fa['fc3'][l]['takeFL']['v'])}" for l, n in zip(FC, ['top quarter', 'middle', 'bottom quarter'])) + '.'
T['Q'] = PF + "The open-side quarter: the quarter of the RTH gap next to the 09:30 open (the top quarter of a gap up, the bottom of a gap down). NY AM never traded back past it on " + ' · '.join(f"{n} {pc(Fa['gap3'][l]['q4held']['v'])}" for l, n in zip(GP, ['gap up', 'smaller gap', 'gap down'])) + f" of days ({pc(Fa['all']['q4held'])} overall). Still a minority outcome: most days retrace past it."
T['NW'] = f"NFP week's opening gap: the prior week's last close to Sunday's 18:00 open, drawn to the release. NQ + ES + RTY pooled 2018–26 ({NW['n']} NFP weeks): its midpoint traded by Monday's close {pc(NW['mon_nfp'])} (other weeks {pc(NW['mon_oth'])}, no difference) and by the release {pc(NW['rel'])}."
T['FH'] = f"FOMC day's RTH high and low, carried into the next day. NQ + ES + RTY pooled: the next RTH took the high on {pc(Fa['all']['takeFH'])} and the low on {pc(Fa['all']['takeFL'])} of days after FOMC; Shirosaki shows the odds for today's setup."
lines = [f'var array<float> VS = parseStats("{VS}")', f'VH = "{VH}"']
for k, v in T.items(): lines.append(f'var string VZT_{k} = "' + v.replace('"', "'") + '"')
open('/home/claude/hol/pool/hollow_pool.pine', 'w').write('\n'.join(lines) + '\n')
print(VS[:200]); print(VH); print(sum(len(v) for v in T.values()), 'tooltip chars')
for k in ('WE', 'FP', 'WDR', 'FDR'): print(k, T[k][:400])
