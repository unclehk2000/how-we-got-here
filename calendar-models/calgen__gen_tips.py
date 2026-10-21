"""Row tooltips for the Cero and Hollow stages cards, generated from the tested numbers (one string per symbol)."""
import json, numpy as np
S = json.load(open('/home/claude/hm/hydra_cal/card_stats.json')); X = json.load(open('/home/claude/hm/hydra_cal/dxy_cal.json'))
RATE = ('newHi', 'newLo', 'gapFill', 'ce10', 'ce50', 'q4held', 'takeFH', 'takeFL', 'firstWon', 'y_againstWk', 'y_contF', 'y_amCont')
NAME = {'newHi': 'new day high', 'newLo': 'new day low', 'gapFill': 'gap filled by 16:14', 'ce10': 'gap 50% by 10:00', 'ce50': 'gap 50% in NY AM', 'q4held': 'open-side ¼ held',
        'takeFH': 'took the FOMC high', 'takeFL': 'took the FOMC low', 'postRng': 'range after 08:30', 'rthRng': 'RTH range', 'm_am': '|NY AM|', 'settleRng': 'settlement range', 'nRng': "next day's range"}
def fm(t, v): return '—' if v is None or not np.isfinite(v) else (f'{100 * v:.0f}%' if t in RATE else f'{v:.2f}')
def heldtxt(lab, t, x, after=''):
    h = x['h']
    return f"✓ {lab}: {NAME.get(t, t)}{after} {fm(t, x['v'])} vs {fm(t, x['o'])} (2018–24 {fm(t, h[0])} vs {fm(t, h[1])}, 2025–26 {fm(t, h[2])} vs {fm(t, h[3])}; p {("< 0.001" if x["p"] < 0.001 else f"{x['p']:.3f}")})"
def row(R, col, groups, labels, tg, after=''):
    """'label (n) H.. L..' for each group, then the held details"""
    parts, held = [], []
    for g, lab in zip(groups, labels):
        d = R[col][g]; n = d[tg[0]]['n']
        vals = ' '.join(f"{('H' if t == 'newHi' else 'L' if t == 'newLo' else 'FH' if t == 'takeFH' else 'FL' if t == 'takeFL' else '')}{fm(t, d[t]['v'])}" if t in ('newHi', 'newLo', 'takeFH', 'takeFL') else fm(t, d[t]['v']) for t in tg)
        parts.append(f'{lab} (n {n}) {vals}')
        for t in tg:
            if d[t]['held']: held.append(heldtxt(lab, t, d[t], after))
    return ' · '.join(parts) + ('. Held: ' + '; '.join(held) + '.' if held else '. Nothing here held in both periods.')
def esq(s): return s.replace('"', "'")
def pine(name, f, var=True):
    a, b = f('ES'), f('NQ')
    return f'{"var string " if var else ""}{name} = isES ? "{esq(a)}" : "{esq(b)}"'
ZG, ZL = ['discount', 'middle', 'premium'], ['discount', 'middle', 'premium']
PG, PL = ['above PDH', 'inside PD', 'below PDL'], ['above PDH', 'inside', 'below PDL']
SG, SL = ['up >0.4 ADR since 18:00', 'flat', 'down >0.4 ADR'], ['up > 0.4 ADR', 'within', 'down > 0.4 ADR']
MG, ML = ['over MO >1 ADR', 'within 1 ADR', 'under MO >1 ADR'], ['over', 'within 1 ADR', 'under']
VG, VL = ['VIX >10% over its 20d avg', 'VIX near avg', 'VIX >10% under'], ['VIX > 10% over its 20-day average', 'near', '> 10% under']
lines = {'cero': [], 'hollow': []}
# ── Cero (NFP, snapshot 08:29)
C = lambda s: S['nfp'][s]
lines['cero'] += [
 pine('VZT_MON', lambda s: "NFP days 2018–26 by the month's position at 08:29 (bottom quarter = discount, top quarter = premium). Right: how often the day made a new high (H) and a new low (L) after 08:30. " + row(C(s), 'mo3', ZG, ZL, ['newHi', 'newLo'], ' after 08:30') + " The EXPECT rows use this group."),
 pine('VZT_MO', lambda s: "Over / under = more than 1 ADR from the month's open at 08:29. Right: R = the range after 08:30, ADR (median). " + row(C(s), 'dmo3', MG, ML, ['postRng'])),
 pine('VZT_PD', lambda s: "Against the prior trading day's high (PDH) and low (PDL) at 08:29. Right: new high (H) / new low (L) after 08:30. " + row(C(s), 'pd3', PG, PL, ['newHi', 'newLo'], ' after 08:30')),
 pine('VZT_18', lambda s: "Move from the 18:00 open to 08:29, in ADR; strong = beyond ±0.4. Right: new high (H) / new low (L) after 08:30. " + row(C(s), 'strong', SG, SL, ['newHi', 'newLo'], ' after 08:30')),
 pine('VZT_WK', lambda s: "The week into the release: Sunday's 18:00 open to 08:29 Friday, in ADR; up / down = beyond ±0.5. Right: R = the range after 08:30, ADR. " + row(C(s), 'wk3', ['week up >0.5 ADR into NFP', 'week flat', 'week down >0.5 ADR'], ['week up', 'flat', 'week down'], ['postRng']) + " A strong week into NFP came with a smaller reaction; a weak week with a bigger one."),
 pine('VZT_VX', lambda s: "VIX's prior close against its 20-day average. Right: R = the range after 08:30, ADR. " + row(C(s), 'vix3', VG, VL, ['postRng'])),
]
def esz(s, ev, ts, labs, rng):
    R = S[ev][s]; out = []
    for t, lab in zip(ts, labs):
        z = R[t]; hs = [ZL[i] for i in range(3) if z[i][2]['held']]
        out.append(f"{lab}: {' · '.join(f'{z[i][0]:.2f}' for i in range(3))} ADR (80%: {' · '.join(f'{z[i][1]:.2f}' for i in range(3))})" + (f" — held for {', '.join(hs)}" if hs else ''))
    return f"Median and 80th percentile of {rng}, by the month's position (discount · middle · premium; n {' · '.join(str(n) for n in R['zone_n'])}), at today's ADR20. " + '; '.join(out) + ". Sizes for stops and targets: which way it goes did not hold."
lines['cero'].append(pine('VZT_E', lambda s: esz(s, 'nfp', ['m_s1', 'm_s2', 'm_am', 'postRng', 'nRng'], ['|stage 1| 08:30–08:50', '|stage 2| 08:50–09:30', '|NY AM| 09:30–11:00', 'range after 08:30', "the next session's range (Monday)"], '97 NFP days 2018–26')))
def dxr(s, ev, w, lab, thr_lab):
    r = X[ev][s][w]
    return (f"{s} against DXY futures in the same window, {lab}, Feb 2023 – Jul 2026 (n {r['n']}): other way {100 * r['other']:.0f}% vs {100 * r['normal']:.0f}% on ordinary days. "
            f"With DXY ≥ {r['thr']:.2f} of its ADR20 ({thr_lab}): {100 * r['big']:.0f}% (n {r['nbig']}; 2023–24 {100 * r['bh1']:.0f}%, 2025–26 {100 * r['bh2']:.0f}%; p {r['pbig']:.3f}{'; held' if r['pbig'] < 0.05 and min(r['bh1'], r['bh2']) > 0.5 else ', not held'}) "
            f"vs {100 * r['small']:.0f}% when smaller; {s}'s own move ran {r['ixBig']:.2f} ADR vs {r['ixSmall']:.2f}. It confirms the move, it does not call it.")
lines['cero'].append(pine('VZT_DR', lambda s: dxr(s, 'nfp', 's1', 'stage 1 (08:30–08:50)', 'BIG') + " Stage 2 and NY AM: no DXY rule held (" + f"{100 * X['nfp'][s]['s2']['big']:.0f}% and {100 * X['nfp'][s]['am']['big']:.0f}% with a big DXY move)."))
# ── Hollow, NFP week (snapshot 09:29)
W = lambda s: S['wk'][s]
GG, GL = ['gap up >0.25 ADR', 'small gap', 'gap down >0.25 ADR'], ['gap up > 0.25 ADR', 'smaller', 'gap down > 0.25 ADR']
lines['hollow'] += [
 pine('VZT_WMON', lambda s: "NFP-week Mon–Thu 2018–26 by the month's position at 09:29. Right: new day high (H) / new low (L) after 09:30 (against the overnight high and low). " + row(W(s), 'mo3', ZG, ZL, ['newHi', 'newLo'], ' after 09:30') + " The EXPECT rows use this group."),
 pine('VZT_WMO', lambda s: "Over / under = more than 1 ADR from the month's open at 09:29. Right: R = the RTH range, ADR. " + row(W(s), 'dmo3', MG, ML, ['rthRng'])),
 pine('VZT_WPD', lambda s: "Against the prior day's high and low at 09:29. Right: new high (H) / new low (L) after 09:30. " + row(W(s), 'pd3', PG, PL, ['newHi', 'newLo'], ' after 09:30')),
 pine('VZT_W18', lambda s: "Overnight: the 18:00 open to 09:29, in ADR; strong = beyond ±0.4. Right: new high (H) / new low (L) after 09:30. " + row(W(s), 'strong', SG, SL, ['newHi', 'newLo'], ' after 09:30')),
 pine('VZT_WGP', lambda s: "RTH gap = 09:30 open − prior 16:14 close, in ADR. Right: ½ = the gap's 50% traded by 10:00, F = the whole gap filled by 16:14. " + row(W(s), 'gap3', GG, GL, ['ce10', 'gapFill'])),
 pine('VZT_WVX', lambda s: "VIX's prior close against its 20-day average. Right: R = the RTH range, ADR. " + row(W(s), 'vix3', VG, VL, ['rthRng'])),
 pine('VZT_WDY', lambda s: "Gap 50% traded by 10:00 by weekday of NFP week: " + row(W(s), 'dow3', ['Monday', 'Tuesday', 'Wednesday', 'Thursday'], ['Mon', 'Tue', 'Wed', 'Thu'], ['ce10']) + (" Against ordinary days (Model 11): Monday 59% vs 46% (2018–24 58%, 2025–26 61%; p 0.044; held)." if s == 'ES' else " Against ordinary days (Model 11): Tuesday 71% vs 58% (2018–24 71%, 2025–26 69%; p 0.040; held).")),
 pine('VZT_WE', lambda s: esz(s, 'wk', ['m_am', 'rthRng', 'settleRng', 'nRng'], ['|NY AM| 09:30–11:00', 'RTH range', 'settlement window 16:15–17:00 range', "next day's range"], f"{S['wk'][s]['n']} NFP-week Mon–Thu 2018–26")),
 pine('VZT_WDR', lambda s: dxr(s, 'wk', 'rth', 'RTH 09:30–16:14', 'BIG') + f" NY AM: {100 * X['wk'][s]['am']['big']:.0f}% with a big DXY move (n {X['wk'][s]['am']['nbig']}; p {X['wk'][s]['am']['pbig']:.3f}" + ("; held)." if s == 'ES' else ", not held).")),
]
# ── Hollow, the day after FOMC (snapshot 09:29)
Fx = lambda s: S['fa'][s]
lines['hollow'] += [
 pine('VZT_FMON', lambda s: "Days after FOMC 2018–26 by the month's position at 09:29. Right: how often RTH took the FOMC day's high (FH) and low (FL). " + row(Fx(s), 'mo3', ZG, ZL, ['takeFH', 'takeFL']) + " The EXPECT rows use this group."),
 pine('VZT_FPD', lambda s: "Against the FOMC day's high and low at 09:29. Right: new high (H) / new low (L) after 09:30 (against the overnight high and low). " + row(Fx(s), 'pd3', PG, ['above the FOMC high', 'inside', 'below the FOMC low'], ['newHi', 'newLo'], ' after 09:30')),
 pine('VZT_F18', lambda s: "Overnight after the decision: the 18:00 open to 09:29, in ADR. Right: new high (H) / new low (L) after 09:30. " + row(Fx(s), 'strong', SG, SL, ['newHi', 'newLo'], ' after 09:30')),
 pine('VZT_FGP', lambda s: "RTH gap = 09:30 open − FOMC day's 16:14 close, in ADR. Right: F = the whole gap filled by 16:14, ½ = its 50% traded in NY AM. " + row(Fx(s), 'gap3', GG, GL, ['gapFill', 'ce50'])),
 pine('VZT_FVX', lambda s: "VIX's prior close against its 20-day average. Right: R = the RTH range, ADR. " + row(Fx(s), 'vix3', VG, VL, ['rthRng'])),
 pine('VZT_FE', lambda s: esz(s, 'fa', ['m_am', 'rthRng', 'nRng'], ['|NY AM| 09:30–11:00', 'RTH range', "next day's range"], f"{S['fa'][s]['n']} days after FOMC 2018–26")),
 pine('VZT_FDR', lambda s: dxr(s, 'fa', 'rth', 'RTH 09:30–16:14', 'BIG')),
]
for m in lines:
    open(f'tips_{m}.pine', 'w').write('\n'.join(lines[m]) + '\n')
    print(m, sum(len(l) for l in lines[m]), 'chars')
print(open('tips_cero.pine').read()[:1500])
