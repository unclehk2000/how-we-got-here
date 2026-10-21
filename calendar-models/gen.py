"""Generate the four calendar indicators (Cero 6, Gran Rey Cero 7–8, Vizard 9–10, Hollow 11–12) from core.pine + per-model blocks."""
import json, re, numpy as np
from events import FOMC, CPI, NFP
J = json.load(open('prof_stats.json')); SH = json.load(open('stats_rows.json'))['rows']

def wrap(items, per, sep):
    ch = [sep.join(items[i:i + per]) for i in range(0, len(items), per)]
    return '"' + (sep + '"\n     + "').join(ch) + '"'
def dates_block():
    f = lambda S: [d.strftime('%Y%m%d') for d in S]
    last = max(FOMC.max(), CPI.max(), NFP.max()).strftime('%Y%m%d')
    return (f'S_FOMC = {wrap(f(FOMC), 8, ",")}\nS_CPI  = {wrap(f(CPI), 12, ",")}\nS_NFP  = {wrap(f(NFP), 12, ",")}\nLAST_DATE = {last}')
def shapes_block():
    return '\n'.join(f'{k:6s} = {wrap(v.split(";"), 1, ";")}' for k, v in SH.items())

# ── verdicts
def verdict(tr, te, base, thr):
    if tr is None or te is None or base is None or not np.isfinite(tr) or not np.isfinite(te): return '≈'
    d1, d2 = tr - base, te - base
    if abs(d1) < thr: return '≈'
    return '✓' if np.sign(d1) == np.sign(d2) and abs(d2) >= thr / 3 else '✗'
pc = lambda v: f'{v * 100:.0f}%'
def p2(p1, n1, p0, n0):
    k1, k0 = p1 * n1, p0 * n0; p = (k1 + k0) / (n1 + n0); se = np.sqrt(p * (1 - p) * (1 / n1 + 1 / n0))
    from scipy import stats as _st
    return float(2 * (1 - _st.norm.cdf(abs((p1 - p0) / se)))) if se > 0 else 1.0
def rate_row(st, label, doc='', invert=False, base=None, desc=''):
    v = st['v']; b = base if base is not None else st['base'][0]; nb = st['base'][1] if st.get('base') and len(st['base']) > 1 else 1000
    f = lambda x: (1 - x) if invert else x
    full, tr, te = f(v['full'][0]), f(v['train'][0]), f(v['test'][0]); bb = f(b) if base is None else b
    g = verdict(tr, te, bb, 0.03)
    pv = p2(full, v['full'][1], bb, nb)
    held = pv < 0.05 and np.sign(tr - bb) == np.sign(te - bb) and np.sign(tr - bb) == np.sign(full - bb)
    tip = (desc + ' ' if desc else '') + f'2018–24 {pc(tr)} (n{v["train"][1]}) · 2025–26 {pc(te)} (n{v["test"][1]}) · normal days {pc(bb)} · p {pv:.3f}' + (f' · {doc}' if doc else '')
    return f'{g}~{label}~{pc(full)}~{pc(bb)}~{tip}~{1 if held else 0}'
def ratio_row(st, label, doc='', base=None):
    v = st['v']; b = base if base is not None else st['base'][0]
    full, tr, te = v['full'][0], v['train'][0], v['test'][0]
    g = verdict(tr / b, te / b, 1.0, 0.05)
    return f'{g}~{label} ÷ ADR~{full:.2f}×~{b:.2f}×~2018–24 {tr:.2f}× · 2025–26 {te:.2f}× · normal days {b:.2f}× (medians, ÷ ADR20)' + (f' · {doc}' if doc else '') + '~0'
SESS_STD = [('asia', 'Asia', '20:00–00:00'), ('london', 'London', '02:00–05:00'), ('nyam', 'NY AM', '09:30–11:00'), ('lunch', 'Lunch', '11:30–13:00'), ('pm', 'PM', '13:30–16:00'), ('settle', 'Settle', '16:15–17:00')]
SESS_FOMC = [('asia', 'Asia', '20:00–00:00'), ('london', 'London', '02:00–05:00'), ('nyam', 'NY AM', '09:30–11:00'), ('pre', '13:30', '13:30–14:00 before the statement'), ('stmt', '14:00', '14:00–14:30 statement'), ('presser', '14:30', '14:30–16:14 press conference')]
def sess(prof, spec):
    lab = '|'.join(x[1] for x in spec)
    val = '|'.join(f'{prof["sess"]["full"][k]:.2f}' for k, _, _ in spec)
    tip = '|'.join(f'{l} {w}: {prof["sess"]["full"][k]*100:.0f}% of normal · 2018–24 {prof["sess"]["train"][k]*100:.0f}% · 2025–26 {prof["sess"]["test"][k]*100:.0f}%' for k, l, w in spec)
    return lab, val, tip

def profiles(root):
    R = J[root]; P = {}
    N, C, F, D1, PO, H = R['NFP'], R['CPI'], R['FOMC'], R['PRE'], R['POST'], R['HOLLOW']
    P['NFP'] = dict(name='M6 CERO · NFP 08:30', sess=sess(N, SESS_STD), rows=[
        rate_row(N['stage2 opposes stage1'], '08:50–11:00 opposed 08:30–08:50', 'Model 6 doc (2023–26): 66%'),
        rate_row(N['next day continues'], 'next RTH went the NFP RTH way', 'Model 6 doc: 37%'),
        rate_row(N['gap full fill in RTH'], 'RTH gap fully filled', 'Model 6 doc: 38% vs 58%'),
        rate_row(N['RTH low in 09:30–10:00'], 'RTH low set 09:30–10:00', 'Model 6 doc: 43% vs 32%'),
        rate_row(N['15:15–15:45 reverses the trend'], '15:15–15:45 reversed the day', 'Model 6 doc: 75% vs 52%')])
    P['CPI'] = dict(name='M7–8 GRAN REY CERO · CPI 08:30', sess=sess(C, SESS_STD), rows=[
        rate_row(C['larger move opposite first sweep'], 'bigger move = 1st sweep side', 'Model 7 doc: 57%', invert=True, desc='The first side of the 07:30–08:30 range taken after 08:30; the bigger of the moves from 08:30 went that way.'),
        rate_row(C['stage2 opposes stage1'], '08:50–11:00 opposed 08:30–08:50', 'Model 7 doc: 60%'),
        rate_row(C['gap 50% by 10:00'], 'RTH gap 50% filled by 10:00', 'Model 7 doc: 44% vs 53%'),
        rate_row(C['gap full fill in RTH'], 'RTH gap fully filled', 'Model 7 doc: 54% vs 58%'),
        rate_row(C['next day continues'], 'next RTH went the CPI RTH way', 'Model 7 doc: 56%')])
    P['FOMC'] = dict(name='M9 VIZARD · FOMC 14:00', sess=sess(F, SESS_FOMC), rows=[
        rate_row(F['RTH high after 14:00'], 'RTH high set after 14:00'),
        rate_row(F['RTH low after 14:00'], 'RTH low set after 14:00'),
        rate_row(F['press conf. opposes statement'], 'presser opposed the statement', 'Model 9 doc: 51%'),
        rate_row(F['gap full fill in RTH'], 'RTH gap fully filled', 'Model 9 doc: 73% vs 58%'),
        rate_row(F['next day continues'], 'next RTH went the FOMC RTH way', 'Model 9 doc: 56% (NY AM)')])
    tb = D1['takeBase']
    P['D1'] = dict(name='M10 PESQUISA · FOMC day 1', sess=sess(D1, SESS_STD), rows=[
        rate_row(D1['decision day takes D1 high'], 'FOMC day took day 1 high', 'any next day', base=tb[0]),
        rate_row(D1['decision day takes D1 low'], 'FOMC day took day 1 low', 'any next day', base=tb[1]),
        rate_row(D1['decision day takes both'], 'FOMC day took both', 'any next day', base=tb[2]),
        ratio_row(D1['RTH range ÷ ADR (median)'], 'day 1 RTH range')])
    fb = F['fb']; tbF = F['takeBase']
    P['POST'] = dict(name='M12 FULL BRINGER · day after FOMC', sess=sess(PO, SESS_STD), rows=[
        rate_row(F['next day takes FOMC high'], 'took FOMC day RTH high', 'Model 12 doc: 50%', base=tbF[0]),
        rate_row(F['next day takes FOMC low'], 'took FOMC day RTH low', 'Model 12 doc: 53%', base=tbF[1]),
        rate_row(F['next day takes both'], 'took both', 'Model 12 doc: 10%', base=tbF[2]),
        f'{verdict(fb["train"]["hi"] / fb["train"]["lo"], fb["test"]["hi"] / fb["test"]["lo"], 1.0, 0.05)}~range after a big FOMC day~{fb["full"]["hi"]:.2f}×~{fb["full"]["lo"]:.2f}×~Right column = after a small FOMC day (not normal days). Spearman {fb["full"]["rho"]:.2f} (2018–24 {fb["train"]["rho"]:.2f}, 2025–26 {fb["test"]["rho"]:.2f}) · big/small split at the median FOMC range · 2025–26 {fb["test"]["hi"]:.2f}× vs {fb["test"]["lo"]:.2f}× · Model 12 doc: r 0.52 on raw points~0',
        ratio_row(PO['RTH range ÷ ADR (median)'], 'RTH range')])
    for nm, full in (('Mon', 'Monday'), ('Tue', 'Tuesday'), ('Wed', 'Wednesday'), ('Thu', 'Thursday')):
        X = H[nm]
        net = X['net ÷ ADR (mean)']; nv = net['v']; nb = net['base'][0]
        P[nm] = dict(name=f'M11 HOLLOW · NFP week {full}', sess=sess(X, SESS_STD), rows=[
            rate_row(X['trend day (|net| ≥ ½ range)'], 'trend day (net ≥ ½ range)', 'Model 11 doc trend rates: Mon 58 · Tue 81 · Wed 75 · Thu 57%'),
            rate_row(X['up-close'], 'closed up', 'Model 11 doc: Mon 61 · Tue 64 · Wed 61 · Thu 49%'),
            f'{verdict(nv["train"][0], nv["test"][0], nb, 0.03)}~RTH net move ÷ ADR~{nv["full"][0]:+.2f}×~{nb:+.2f}×~2018–24 {nv["train"][0]:+.3f} · 2025–26 {nv["test"][0]:+.3f} · normal {nb:+.3f} (RTH close − open ÷ ADR, mean) · Model 11 doc: Wed +75 pts vs −4~0',
            rate_row(X['gap 50% by 10:00'], 'RTH gap 50% filled by 10:00'),
            rate_row(X['NWOG CE touched by today'], 'NWOG midpoint touched by today', 'Model 11 doc: 87% by Thursday vs 74%')])
    return P

def pine_switch(fn, args, keys, getter, default='""'):
    out = [f'{fn}({args}) =>', '    switch k']
    for i, k in enumerate(keys): out.append(f'        {i} => {getter(k)}')
    out.append(f'        => {default}')
    return '\n'.join(out)
def q(s): return '"' + s.replace('"', "'") + '"'
TYPE_ROW = dict(FOMC=0, NFP=1, CPI=2, POST=3, D1=4, Mon=5, Tue=5, Wed=5, Thu=5)   # row in the day-shape table
def profile_block(keys):
    NQ = profiles('NQ')
    b = [pine_switch('pfName', 'int k', keys, lambda k: q(NQ[k]['name'])),
         pine_switch('ownTy', 'int k', keys, lambda k: str(TYPE_ROW[k]), default='6')]
    return '\n'.join(b)

# ── event card: checklist rows (only what held) and the tally records
TAL = json.load(open('tally.json'))
CK_ROOT = json.load(open('clock.json'))
def held_rows(root, key):
    """generic checklist: profile rows that held (p < 0.05, same side in both periods) and the busiest half hour if it held"""
    rows = []
    for r in profiles(root)[key]['rows']:
        f = r.split('~')
        if len(f) >= 6 and f[5] == '1': rows.append('~'.join(f[1:5]))
    t = dict(NFP='NFP', CPI='CPI', FOMC='FOMC', D1='PRE', POST='POST', Mon='HOLLOW', Tue='HOLLOW', Wed='HOLLOW', Thu='HOLLOW')[key]
    C = CK_ROOT[root][t]; N = CK_ROOT[root]['NORMAL']
    med = np.diff(np.r_[0, C['R'][2]]); j = int(np.argmax(med)); tr = np.diff(np.r_[0, C['R50_train']])[j]; te = np.diff(np.r_[0, C['R50_test']])[j]
    nrm = np.diff(np.r_[0, N['R'][2]])[j]
    if j > 0 and tr > 2 * nrm and te > 2 * nrm:
        e = (1080 + 30 * (j + 1)) % 1440; s0 = (e - 30) % 1440
        hm = lambda m: f'{m // 60:02d}:{m % 60:02d}'
        rows.append(f'{hm(s0)}–{hm(e)} adds (× ADR)~+{med[j]:.2f}×~+{nrm:.2f}×~How much the median day range grows in this half hour: +{med[j]:.2f}× ADR (2018–24 +{tr:.2f}×, 2025–26 +{te:.2f}×) vs +{nrm:.2f}× on normal days.')
    return rows
def card_block(I):
    keys = I['keys']; out = []
    rows = {(k, r): (I['chk'][r] if 'chk' in I else held_rows(r, k)) for k in keys for r in ('NQ', 'ES')}
    out.append(pine_switch('chkRows', 'int k, bool es', keys, lambda k: f'es ? {q("|".join(rows[(k, "ES")]))} : {q("|".join(rows[(k, "NQ")]))}'))
    mx = lambda r: max(len(rows[(k, r)]) for k in keys)
    out.append(f'chkMax(bool es) => es ? {max(1, mx("ES"))} : {max(1, mx("NQ"))}')
    ev = I['tally']
    for r in ('NQ', 'ES'):
        recs = [f"{x['d']},{x['td']},{x['rth']},{'' if x['gap'] is None else x['gap']},{'' if x['gp'] is None else x['gp']}" for x in TAL[r][ev]]
        out.append(f'TAL_{r} = ' + wrap(recs, 8, ';'))
        out.append(f'TAL_END_{r} = {TAL[r]["end"]}')
    out.append(f'TAL_NAME = "{I["tally_name"]}"')
    out.append(I['talIs'])
    # VIX range-factor centring (training means)
    out.append(f'IVRV_NQ = {TAL["NQ"]["ivrv_mean"]:.4f}\nIVRV_ES = {TAL["ES"]["ivrv_mean"]:.4f}')
    return '\n'.join(out)

# ── event clock data and helpers
CKJ = json.load(open('clock.json'))
CK_LABEL = dict(FOMC='FOMC', NFP='NFP', CPI='CPI', POST='FOMC +1', PRE='FOMC D1', HOLLOW='NFP week', NORMAL='Normal')
def clock_block(types):
    out = []
    for root in ('NQ', 'ES'):
        chunks = []
        for t in types + ['NORMAL']:
            T = CKJ[root][t]
            blk = [T['R'][k] for k in range(5)] + [T['N'][k] for k in range(5)] + [T['share']]
            for i, row in enumerate(blk):
                assert len(row) == 46 and all(np.isfinite(v) for v in row), (root, t, i)
                chunks.append((','.join(str(int(round(v * 1000))) for v in row), i == len(blk) - 1))
        lines = []
        for n, (c, endT) in enumerate(chunks):
            last = n == len(chunks) - 1
            lines.append('"' + c + ('' if last else (';' if endT else ',')) + '"')
        out.append(f'CK_{root} = ' + '\n     + '.join(lines))
    return '\n'.join(out)
def clock_funcs(I):
    types = I['ck'] + ['NORMAL']
    b = [pine_switch('ownCk', 'int k', I['keys'], lambda k: str(I['ckmap'][k]), default='0'),
         pine_switch('ckName', 'int k', types, lambda t: q(CK_LABEL[t])),
         pine_switch('ckN', 'int k, bool es', types, lambda t: f'es ? "{CKJ["ES"][t]["n"]}" : "{CKJ["NQ"][t]["n"]}"')]
    return '\n'.join(b)

# ── odds rows: up-close (by anchor), closing against DXY, next day the same way; live DXY conditional rates
OD = json.load(open('odds.json'))
KEY_TYPE = dict(NFP='NFP', CPI='CPI', FOMC='FOMC', D1='PRE', POST='POST', Mon='HOLLOW', Tue='HOLLOW', Wed='HOLLOW', Thu='HOLLOW')
TYPE_LABEL = dict(NFP='NFP', CPI='CPI', FOMC='FOMC', PRE='FOMC day 1', POST='day-after-FOMC', HOLLOW='NFP-week')
ANCH_TXT = dict(TD='Trading day 18:00 → 16:59', MID='NY midnight 00:00 → 16:59', RTH='RTH 09:30 → 16:14')
pp = lambda r: f"{r['p']*100:.0f}%"
pm = lambda r: f"{r['p']*100:.0f}% ±{r['moe']*100:.0f}"
def odds_rows(root, key, an):
    t = KEY_TYPE[key]; T = OD[root][t]; lab = TYPE_LABEL[t]
    u = T[f'up_{an}']; d = T['dxy']; n = T['next']
    up = f"{u['g']}~closed up~{pm(u['r'])}~{pm(u['base'])}~{ANCH_TXT[an]}: closed above its open on {u['r']['n']} {lab} days 2018–26 (2018–24 {pp(u['tr'])}, 2025–26 {pp(u['te'])} n{u['te']['n']}) vs normal days {pm(u['base'])}. Difference p = {u['p']:.2f}. ± = 95% margin of error."
    dx = f"{d['g']}~closed against DXY~{pm(d['r'])}~{pm(d['base'])}~Trading-day direction of {root} opposite to DXY futures the same day, Feb 2023 – Aug 2026 ({d['r']['n']} {lab} days). Difference p = {d['p']:.2f}. ± = 95% margin of error."
    nx = f"{n['g']}~next day went the same way~{pm(n['r'])}~{pm(n['base'])}~The next trading day closed (open → close) the same way as this day: {n['r']['n']} {lab} days 2018–26 vs any day → next day {pm(n['base'])}. Difference p = {n['p']:.2f}. ✗ = differed in 2018–24 but flipped in 2025–26."
    return '|'.join([up, dx, nx]).replace('"', "'")
def dx_row(root, key):
    t = KEY_TYPE[key]; d = OD[root][t]['dxy']
    return '|'.join([pm(d['upUp']), pm(d['upDn']), TYPE_LABEL[t], pm(d['bUpUp']), pm(d['bUpDn'])])
def odds_block(keys):
    b = ['pfOdds(int k, bool es, int an) =>', '    switch k']
    for i, k in enumerate(keys):
        e = lambda r: ' : '.join(f'an == {j} ? "{odds_rows(r, k, a)}"' for j, a in enumerate(('TD', 'MID'))) + f' : "{odds_rows(r, k, "RTH")}"'
        b.append(f'        {i} => es ? ({e("ES")}) : ({e("NQ")})')
    b.append('        => "≈~—~—~—~|≈~—~—~—~|≈~—~—~—~"')
    b += ['pfDx(int k, bool es) =>', '    switch k']
    for i, k in enumerate(keys):
        b.append(f'        {i} => es ? "{dx_row("ES", k)}" : "{dx_row("NQ", k)}"')
    b.append('        => "—|—|—|—|—"')
    return '\n'.join(b)

IND = {}
from fed_blocks import FED
# ───────────────────────────────────────────── Cero (6) · NFP
IND['Cero'] = dict(tally='NFP', tally_name='NFP', talIs='talIs(int k, int pk) => NP.includes(k)', ck=['NFP'], ckmap=dict(NFP=0), rel='510', short='Cero', ghost='#ff7043', keys=['NFP'], header='''// Cero (虚閃) · Model 6: NFP days (Employment Situation, released 08:30 ET).
// The model's own structure on the chart: the 07:00–09:00 dealing range, the 08:30–08:45 hands-off window, the 08:50
// line between the release push and the second stage, and the RTH gap (prior 16:14 close and its 50%).''',
own='''ownProfile(int tk, int pk, int today) =>
    bool now = NP.includes(tk)
    int  rf  = na(tk) ? today : math.max(tk, today)
    [0, now, now ? tk : nextOf(NP, rf)]
ownNext(int today) =>
    int n1 = nextOf(NP, today)
    ["NFP 08:30", n1, "then", na(n1) ? na : nextOf(NP, addDays(n1, 1))]''',
struct='''bool cNFP = NP.includes(calK)
bool cOn  = showStr and recent and cNFP
var float drH = na
var float drL = na
var int   drK = na
if cOn
    if mod >= 420 and mod < 540
        if drK != calK
            drK := calK
            drH := high
            drL := low
        else
            drH := math.max(drH, high)
            drL := math.min(drL, low)
    if drK == calK and mod >= 540 and (mod[1] < 540 or calK != calK[1])
        line.new(keyAt(calK, 420), drH, keyAt(calK, 974), drH, xloc = xloc.bar_time, color = cLvl, width = 1, style = line.style_dashed)
        line.new(keyAt(calK, 420), drL, keyAt(calK, 974), drL, xloc = xloc.bar_time, color = cLvl, width = 1, style = line.style_dashed)
        label.new(keyAt(calK, 420), drH, "DR high", xloc = xloc.bar_time, color = #00000000, textcolor = cLvl, style = label.style_label_lower_left, size = size.tiny, tooltip = "NFP dealing range 07:00–09:00 ET")
        label.new(keyAt(calK, 420), drL, "DR low", xloc = xloc.bar_time, color = #00000000, textcolor = cLvl, style = label.style_label_upper_left, size = size.tiny, tooltip = "NFP dealing range 07:00–09:00 ET")
    if mod <= 530 and mod + tfM > 530
        line.new(keyAt(calK, 530), close, keyAt(calK, 530), close + syminfo.mintick, xloc = xloc.bar_time, extend = extend.both, color = color.new(cLvl, 60), style = line.style_dotted)
    if rthSt and not na(gapPC)
        line.new(time, gapPC, keyAt(calK, 974), gapPC, xloc = xloc.bar_time, color = color.new(cLvl, 40), style = line.style_dotted)
        line.new(time, gapCE, keyAt(calK, 974), gapCE, xloc = xloc.bar_time, color = color.new(cLvl, 20), style = line.style_dotted)
        label.new(keyAt(calK, 974), gapCE, "gap 50%", xloc = xloc.bar_time, color = #00000000, textcolor = cLvl, style = label.style_label_left, size = size.tiny, tooltip = "RTH gap 50% = (prior 16:14 close + 09:30 open) ÷ 2. NFP days filled the full gap less often than normal days (" + (isES ? "53% vs 62%" : "54% vs 63%") + ").")
    if markEv and mod <= 510 and mod + tfM > 510
        label.new(bar_index, high, "NFP", color = #00000000, textcolor = cGh, style = label.style_label_down, size = size.tiny, tooltip = "NFP 08:30 ET " + str.format_time(time, "dd MMM yyyy", TZ))
bgcolor(cOn and mod >= 510 and mod < 525 ? cHands : na, title = "08:30–08:45 hands-off")''', last='')

# ───────────────────────────────────────────── Gran Rey Cero (7–8) · CPI
IND['Gran Rey Cero'] = dict(chk=dict(NQ=['08:30 candle (× ADR)~0.27×~0.03×~Median 08:30 one-minute candle ÷ ADR20: 0.27× on CPI days vs 0.03× on normal days, about 9× (2018–24 8.4×, 2025–26 10.9×).',
                    '08:30–09:00 adds (× ADR)~+0.19×~+0.02×~How much the median day range grows in the 08:30–09:00 half hour: +0.19× ADR on CPI days (2018–24 +0.17×, 2025–26 +0.31×) vs +0.02× on normal days.',
                    '1st sweep side won~70%~56%~The first side of the 07:30–08:30 range taken after 08:30; the bigger of the moves from 08:30 went that way on 70% of CPI days vs 56% of normal days (2018–24 70% n79, 2025–26 71% n17, p 0.008).',
                    'VIX fell on the day~69%~55%~VIX closed below its prior close on 66 of 96 CPI days (2018–24 67%, 2025–26 76%) vs 55% of normal days, p 0.008: implied volatility tends to come out after the release.'],
              ES=['08:30 candle (× ADR)~0.25×~0.03×~Median 08:30 one-minute candle ÷ ADR20: 0.25× on CPI days vs 0.03× on normal days, about 9× (2018–24 7.7×, 2025–26 12.8×).',
                  '08:30–09:00 adds (× ADR)~+0.19×~+0.03×~How much the median day range grows in the 08:30–09:00 half hour: +0.19× ADR on CPI days (2018–24 +0.19×, 2025–26 +0.28×) vs +0.03× on normal days.',
                  'VIX fell on the day~68%~55%~VIX closed below its prior close on 67 of 98 CPI days (2018–24 67%, 2025–26 74%) vs 55% of normal days, p 0.010. (The 1st-sweep row held on NQ but faded on ES in 2025–26, so it is not shown here.)']),
    tally='CPI', tally_name='CPI', talIs='talIs(int k, int pk) => CP.includes(k)', ck=['CPI'], ckmap=dict(CPI=0), rel='510', file='Gran_Rey_Cero', short='Gran Rey', ghost='#e53935', keys=['CPI'], header='''// Gran Rey Cero (王虚の閃光) · Models 7–8: CPI days (released 08:30 ET).
// The model's own structure on the chart: stage 1 (the dealing range built in the hour before the release, the structure
// the release tests), yesterday's RTH close, the first side of the dealing range taken after the release, the 08:50 line
// between the release push and stage 2, the 08:30–09:00 window (full-height lines and shading every weekday, strongest on
// CPI days, with the day's wording held above price), the window's high / low box on CPI days and the day after, and every
// CPI 08:30 candle kept and extended to the right, labelled wild / average / quiet against past CPI candles.''',
sinputs='''relLenI = input.string("1 min", "08:30 candle", options = ["1 min", "5 min", "15 min"], group = grpS, inline = "s2", tooltip = "The CPI release candle kept and extended to the right. On a chart above this timeframe the bar holding 08:30 is used. Wild / average / quiet = top / middle / bottom third of CPI release candles of the same length since 2018, as a share of ADR20.", display = display.none)
relKeep = input.int(6, "keep last", minval = 1, maxval = 30, group = grpS, inline = "s2", display = display.none)
showWin = input.bool(true, "08:30–09:00 high / low box", group = grpS, inline = "s3", display = display.none)
showYC  = input.bool(true, "Yesterday's RTH close", group = grpS, inline = "s3", display = display.none)
winLn   = input.bool(true, "08:30 / 09:00 lines", group = grpS, inline = "s4", display = display.none)
cWinL   = input.color(#2962ff, "", group = grpS, inline = "s4", display = display.none)
winLW   = input.int(3, "width", minval = 1, maxval = 10, group = grpS, inline = "s4", display = display.none)
winBg   = input.bool(true, "Shade the window", group = grpS, inline = "s5", display = display.none)
winDays = input.string("Every weekday", "on", options = ["Every weekday", "CPI days and the day after", "CPI days"], group = grpS, inline = "s5", tooltip = "Full-height lines at 08:30 and 09:00 ET with the window shaded between them, in the line colour: strongest on CPI days, lighter on the day after, faint on other weekdays.", display = display.none)
showNot = input.bool(true, "Day wording", group = grpS, inline = "s6", display = display.none)
cNote   = input.color(#2962ff, "", group = grpS, inline = "s6", display = display.none)
noteSzI = input.string("Normal", "", options = ["Tiny", "Small", "Normal", "Large", "Huge"], group = grpS, inline = "s6", display = display.none)
noteUp  = input.int(15, "height", minval = 0, maxval = 300, group = grpS, inline = "s6", tooltip = "The day's wording sits over the 08:30–09:00 window, this far above the trading day's high (% of ADR20), and rises with the high through the day. Colour, size and wording are yours; leave a wording empty to hide it on that kind of day.", display = display.none)
txCPI   = input.string("CPI day · here we go folks", "CPI day", group = grpS, display = display.none)
txAft   = input.string("you just missed me folks", "Day after", group = grpS, display = display.none)
txOth   = input.string("nothing to see here folks", "Other days", group = grpS, display = display.none)''',
own='''ownProfile(int tk, int pk, int today) =>
    bool now = CP.includes(tk)
    int  rf  = na(tk) ? today : math.max(tk, today)
    [0, now, now ? tk : nextOf(CP, rf)]
ownNext(int today) =>
    int n1 = nextOf(CP, today)
    ["CPI 08:30", n1, "then", na(n1) ? na : nextOf(CP, addDays(n1, 1))]''',
struct='''bool gCPI = CP.includes(calK)
bool gAft = CP.includes(tdPK) and not gCPI                   // the trading day after a CPI day
bool gOn  = showStr and recent
bool wkd  = dayofweek(time, TZ) >= 2 and dayofweek(time, TZ) <= 6
var float drH = na
var float drL = na
var int   drK = na
var int   swp = 0
string swTip = "First side of the stage 1 dealing range (07:30–08:30) taken after the release. The day's bigger move (from 08:30) went the same way " + (isES ? "67% of the time vs 56% on normal days, but only 53% in 2025–26 (71% in 2018–24)." : "70% of the time vs 56% on normal days, and 71% in 2025–26.")
// stage 1: the dealing range built in the hour before the release, plus yesterday's RTH close
if gOn and gCPI
    if mod >= 450 and mod < 510
        if drK != calK
            drK := calK
            drH := high
            drL := low
            swp := 0
            if showYC and not na(rthC)
                line.new(keyAt(calK, 450), rthC, keyAt(calK, 974), rthC, xloc = xloc.bar_time, color = color.new(cLvl, 25), style = line.style_dotted, width = 1)
                label.new(keyAt(calK, 974), rthC, "yday RTH close", xloc = xloc.bar_time, color = #00000000, textcolor = color.new(cLvl, 15), style = label.style_label_left, size = size.tiny, tooltip = "Yesterday's RTH close (16:14 bar): the gap the release opens against.")
        else
            drH := math.max(drH, high)
            drL := math.min(drL, low)
    if drK == calK and mod >= 510 and (mod[1] < 510 or calK != calK[1])
        line.new(keyAt(calK, 450), drH, keyAt(calK, 974), drH, xloc = xloc.bar_time, color = cLvl, width = 1, style = line.style_dashed)
        line.new(keyAt(calK, 450), drL, keyAt(calK, 974), drL, xloc = xloc.bar_time, color = cLvl, width = 1, style = line.style_dashed)
        label.new(keyAt(calK, 450), drH, "stage 1 · DR high", xloc = xloc.bar_time, color = #00000000, textcolor = cLvl, style = label.style_label_lower_left, size = size.tiny, tooltip = "Stage 1: the dealing range built in the hour before the 08:30 release (07:30–08:30 ET). This is the structure the release tests.")
        label.new(keyAt(calK, 450), drL, "stage 1 · DR low", xloc = xloc.bar_time, color = #00000000, textcolor = cLvl, style = label.style_label_upper_left, size = size.tiny, tooltip = "Stage 1: the dealing range built in the hour before the 08:30 release (07:30–08:30 ET). This is the structure the release tests.")
    if drK == calK and mod >= 510 and mod < 975 and swp == 0 and not na(drH)
        if low < drL
            swp := -1
            label.new(bar_index, low, "1st sweep ▼", color = #00000000, textcolor = cLvl, style = label.style_label_up, size = size.tiny, tooltip = swTip)
        else if high > drH
            swp := 1
            label.new(bar_index, high, "1st sweep ▲", color = #00000000, textcolor = cLvl, style = label.style_label_down, size = size.tiny, tooltip = swTip)
    if mod <= 530 and mod + tfM > 530
        line.new(keyAt(calK, 530), close, keyAt(calK, 530), close + syminfo.mintick, xloc = xloc.bar_time, extend = extend.both, color = color.new(cLvl, 60), style = line.style_dotted)
    if rthSt and not na(gapCE)
        line.new(time, gapCE, keyAt(calK, 974), gapCE, xloc = xloc.bar_time, color = color.new(cLvl, 20), style = line.style_dotted)
        label.new(keyAt(calK, 974), gapCE, "gap 50%", xloc = xloc.bar_time, color = #00000000, textcolor = cLvl, style = label.style_label_left, size = size.tiny, tooltip = "RTH gap 50% = (yesterday's RTH close + 09:30 open) ÷ 2")
// the 08:30–09:00 window: full-height lines at 08:30 and 09:00 and the band between them, strongest on CPI days
bool  inW     = mod < 540 and mod + tfM > 510
bool  winShow = gOn and wkd and timeframe.isintraday and (winDays == "Every weekday" or gCPI or (gAft and winDays == "CPI days and the day after"))
color winC    = gCPI ? cWinL : gAft ? color.new(cWinL, 45) : color.new(cWinL, 70)
if winShow and winLn
    for m in array.from(510, 540)
        if mod <= m and mod + tfM > m
            line.new(keyAt(calK, m), close, keyAt(calK, m), close + syminfo.mintick, xloc = xloc.bar_time, extend = extend.both, color = winC, width = winLW)
bgcolor(winShow and winBg and inW ? color.new(cWinL, gCPI ? 82 : gAft ? 90 : 95) : na, title = "08:30–09:00 window", force_overlay = true)
// the window's high / low box: CPI days, lighter on the day after
var box   wBx = na
var int   wK  = na
if gOn and showWin and (gCPI or gAft) and inW and wkd
    if wK != calK
        wK  := calK
        wBx := box.new(keyAt(calK, 510), high, keyAt(calK, 540), low, xloc = xloc.bar_time, border_color = color.new(cGh, gCPI ? 35 : 70), border_width = 1, bgcolor = color.new(cGh, gCPI ? 78 : 92))
    else
        wBx.set_top(math.max(wBx.get_top(), high))
        wBx.set_bottom(math.min(wBx.get_bottom(), low))
// the day's wording, centred over the window and held above the trading day's high; it rises with the high all day
var label wTx  = na
var int   wTxD = na
string noteTx = gCPI ? txCPI : gAft ? txAft : txOth
float  noteOf = (tdO * ADRtd > 0 ? tdO * ADRtd : tdH - tdL) * noteUp / 100.0
noteSz = noteSzI == "Tiny" ? size.tiny : noteSzI == "Small" ? size.small : noteSzI == "Normal" ? size.normal : noteSzI == "Large" ? size.large : size.huge
if gOn and showNot and wkd and noteTx != "" and mod <= 510 and mod + tfM > 510
    int    nx   = nextOf(CP, addDays(calK, 1))
    string nTip = gCPI ? "CPI day: the release is at 08:30 ET. The 08:30–09:00 half hour adds a median " + (isES ? "+0.19× ADR20 to the day range vs +0.03×" : "+0.19× ADR20 to the day range vs +0.02×") + " on normal days." : gAft ? "The trading day after a CPI day. Tested 2018–26: it went the same way as the CPI day " + (isES ? "46% ±10 of the time (any day → next day 49%)" : "44% ±10 of the time (any day → next day 48%)") + ", so no continuation edge showed up." : "Not a CPI day: a normal day's 08:30 one-minute candle is about 1/9 the size of a CPI one (medians)." + (na(nx) ? "" : " Next CPI: " + fmtDay(nx) + ".")
    wTx  := label.new(keyAt(calK, 525), tdH + noteOf, noteTx, xloc = xloc.bar_time, color = #00000000, textcolor = cNote, style = label.style_label_down, size = noteSz, tooltip = nTip)
    wTxD := tdK
else if not na(wTx) and tdK == wTxD
    wTx.set_y(math.max(wTx.get_y(), tdH + noteOf))
// every CPI 08:30 candle, kept and extended to the right like NWOG / NDOG
var array<box>   RCB = array.new<box>()
var array<label> RCT = array.new<label>()
var float rcH = na
var float rcL = na
var int   rcK = na
int  rcLen = relLenI == "1 min" ? 1 : relLenI == "5 min" ? 5 : 15
bool inRC  = tfM <= rcLen ? (mod >= 510 and mod < 510 + rcLen) : (mod <= 510 and mod + tfM > 510)
if gCPI and inRC
    if rcK != calK
        rcK := calK
        rcH := high
        rcL := low
    else
        rcH := math.max(rcH, high)
        rcL := math.min(rcL, low)
if markEv and gCPI and rcK == calK and not inRC and inRC[1]
    int   eff = math.max(rcLen, tfM)
    float q1  = eff <= 1 ? (isES ? 0.161 : 0.146) : eff <= 5 ? (isES ? 0.209 : 0.202) : (isES ? 0.234 : 0.235)
    float q2  = eff <= 1 ? (isES ? 0.400 : 0.369) : eff <= 5 ? (isES ? 0.470 : 0.432) : (isES ? 0.504 : 0.464)
    float xr  = tdO * ADRtd > 0 ? (rcH - rcL) / (tdO * ADRtd) : na
    string cat = na(xr) ? "" : xr >= q2 ? " · wild" : xr < q1 ? " · quiet" : " · average"
    for b in RCB                                              // older CPI candles fade back, the latest stays strong
        b.set_bgcolor(color.new(cGh, 93))
        b.set_border_color(color.new(cGh, 55))
    for t in RCT
        t.set_textcolor(color.new(cGh, 35))
    RCB.push(box.new(keyAt(calK, 510), rcH, time, rcL, xloc = xloc.bar_time, border_color = color.new(cGh, 15), border_width = 1, bgcolor = color.new(cGh, 86)))
    RCT.push(label.new(time, (rcH + rcL) / 2, "CPI " + str.format_time(keyTime(calK), "dd/MM", TZ) + cat, xloc = xloc.bar_time, color = #00000000, textcolor = cGh, style = label.style_label_left, size = size.small, tooltip = "CPI 08:30 candle (" + str.tostring(eff) + " min): " + pf(rcH - rcL) + " pts = " + (na(xr) ? "—" : str.tostring(xr, "0.00") + "× ADR20") + ". CPI release candles of this length since 2018: bottom third under " + str.tostring(q1, "0.00") + "× (quiet), top third over " + str.tostring(q2, "0.00") + "× (wild). A normal day's 08:30 candle of the same length is about " + (eff <= 1 ? "1/9" : eff <= 5 ? "1/5" : "1/4") + " the size of a CPI one (medians)."))
    if RCB.size() > relKeep
        RCB.shift().delete()
        RCT.shift().delete()
if RCB.size() > 0
    for b in RCB
        b.set_right(time)
    for t in RCT
        t.set_x(time)''', last='')

# ───────────────────────────────────────────── Vizard (9–10)
IND['Vizard'] = dict(tally='FOMC', tally_name='FOMC', talIs='talIs(int k, int pk) => FO.includes(k)', ck=['FOMC', 'PRE'], ckmap=dict(FOMC=0, D1=1), rel='840,870', short='Vizard', ghost='#ab47bc', keys=['FOMC', 'D1'], header='''// Vizard · Models 9–10: the FOMC decision day (9 Vizard, statement 14:00, press conference 14:30 ET) and the meeting's
// first day (10 Pesquisa). The model's own structure on the chart: the statement and press-conference windows, the
// day-1 high and low carried into the decision day (live on day 1), and the RTH gap (prior 16:14 close and its 50%).''',
own='''ownProfile(int tk, int pk, int today) =>
    int  k   = 0
    bool now = false
    int  d   = na
    if FO.includes(tk)
        now := true
        d := tk
    else if FO.includes(addDays(tk, 1))
        k := 1
        now := true
        d := tk
    else
        int rf = na(tk) ? today : math.max(tk, today)
        int f  = nextOf(FO, rf)
        int f2 = na(f) ? na : addDays(f, -1) >= rf ? f : nextOf(FO, addDays(f, 1))
        k := 1
        d := na(f2) ? na : addDays(f2, -1)
    [k, now, d]
ownNext(int today) =>
    int f  = nextOf(FO, today)
    int f2 = na(f) ? na : addDays(f, -1) >= today ? f : nextOf(FO, addDays(f, 1))
    ["FOMC day 1", na(f2) ? na : addDays(f2, -1), "FOMC 14:00", f]''',
struct='''bool vF  = FO.includes(calK)
bool vOn = showStr and recent
if vOn and tdSt and FO.includes(tdK) and not na(ptdH)
    line.new(time, ptdH, keyAt(tdK, 1019), ptdH, xloc = xloc.bar_time, color = cLvl, width = 1, style = line.style_dashed)
    line.new(time, ptdL, keyAt(tdK, 1019), ptdL, xloc = xloc.bar_time, color = cLvl, width = 1, style = line.style_dashed)
    label.new(keyAt(tdK, 1019), ptdH, "D1 high", xloc = xloc.bar_time, color = #00000000, textcolor = cLvl, style = label.style_label_left, size = size.tiny, tooltip = "FOMC day 1 high (trading day). The decision day took it 67% of the time vs 56% for any next day.")
    label.new(keyAt(tdK, 1019), ptdL, "D1 low", xloc = xloc.bar_time, color = #00000000, textcolor = cLvl, style = label.style_label_left, size = size.tiny, tooltip = "FOMC day 1 low (trading day). The decision day took it 52% of the time vs 44% for any next day.")
if vOn and vF and mod <= 840 and mod + tfM > 840
    line.new(keyAt(calK, 840), close, keyAt(calK, 840), close + syminfo.mintick, xloc = xloc.bar_time, extend = extend.both, color = color.new(cLvl, 50), style = line.style_dotted)
    label.new(keyAt(calK, 840), high, "statement", xloc = xloc.bar_time, color = #00000000, textcolor = cGh, style = label.style_label_down, size = size.tiny)
if vOn and vF and mod <= 870 and mod + tfM > 870
    line.new(keyAt(calK, 870), close, keyAt(calK, 870), close + syminfo.mintick, xloc = xloc.bar_time, extend = extend.both, color = color.new(cLvl, 50), style = line.style_dotted)
    label.new(keyAt(calK, 870), high, "press conf.", xloc = xloc.bar_time, color = #00000000, textcolor = cGh, style = label.style_label_down, size = size.tiny)
if vOn and vF and rthSt and not na(gapPC)
    line.new(time, gapPC, keyAt(calK, 974), gapPC, xloc = xloc.bar_time, color = color.new(cLvl, 40), style = line.style_dotted)
    line.new(time, gapCE, keyAt(calK, 974), gapCE, xloc = xloc.bar_time, color = color.new(cLvl, 20), style = line.style_dotted)
    label.new(keyAt(calK, 974), gapCE, "gap 50%", xloc = xloc.bar_time, color = #00000000, textcolor = cLvl, style = label.style_label_left, size = size.tiny, tooltip = "RTH gap 50% = (prior 16:14 close + 09:30 open) ÷ 2. FOMC days filled the full gap 74% of the time vs 63%.")
bgcolor(vOn and vF and mod >= 840 and mod < 870 ? cWin : vOn and vF and mod >= 870 and mod < 975 ? color.new(cWin, math.min(100, color.t(cWin) + 4)) : na, title = "Statement and press conference")''',
last='''    if showStr and FO.includes(addDays(tdK, 1)) and not na(tdX)
        RL.push(line.new(tdX, tdH, xd, tdH, color = cLvl, style = line.style_dashed))
        RL.push(line.new(tdX, tdL, xd, tdL, color = cLvl, style = line.style_dashed))
        RT.push(label.new(tdX, tdH, "D1 high (live)", color = #00000000, textcolor = cLvl, style = label.style_label_lower_left, size = size.tiny, tooltip = "Today is FOMC day 1: its high and low carry into the decision day."))
        RT.push(label.new(tdX, tdL, "D1 low (live)", color = #00000000, textcolor = cLvl, style = label.style_label_upper_left, size = size.tiny))''')

IND['Vizard'].update(FED)
import fomc_blocks as VZ
_v = IND['Vizard']
_v['sinputs'] = VZ.SINPUTS
_v['fedin'] = _v['fedin'] + '\n' + VZ.INPUTS
_v['fedreq'] = _v['fedreq'] + VZ.GLOBALS.replace('%CONST%', VZ.CONST)
_v['struct'] = _v['struct'] + VZ.STRUCT
_v['lastx'] = 'if barstate.islast\n    int xd = bar_index + offI\n' + _v['last'].lstrip('\n') + VZ.LAST + '\n'
_v['last'] = ''
_v['extra'] = _v['extra'] + '\n' + VZ.CARD_BLOCK

# ───────────────────────────────────────────── Hollow (11–12)
IND['Hollow'] = dict(tally='POST', tally_name='day-after-FOMC', talIs='talIs(int k, int pk) => FO.includes(pk)', ck=['HOLLOW', 'POST'], ckmap=dict(Mon=0, Tue=0, Wed=0, Thu=0, POST=1), rel='', short='Hollow', ghost='#26a69a', keys=['Mon', 'Tue', 'Wed', 'Thu', 'POST'], header='''// Hollow · Models 11–12: Monday–Thursday of NFP week (11 Hollow) and the day after FOMC (12 Full Bringer).
// The model's own structure on the chart: the NFP week's opening gap (Friday close, Sunday open and its midpoint) drawn
// to the release, the 16:15–17:00 settlement window, FOMC day's RTH high and low carried into the next day, and the
// RTH gap (prior 16:14 close and its 50%).''',
own='''hollowDay(int k) =>
    int  dw = dowOf(k)
    bool h  = false
    if dw >= 2 and dw <= 5
        for j = 1 to 6 - dw
            if NP.includes(addDays(k, j))
                h := true
    h
hollowNext(int today) =>
    int n = nextOf(NP, addDays(today, 1))
    int m = na(n) ? na : math.max(addDays(n, 2 - dowOf(n)), today)
    int f = nextOf(FO, today)
    int p = na(f) ? na : addDays(f, dowOf(f) == 6 ? 3 : 1)
    [m, p]
ownProfile(int tk, int pk, int today) =>
    int  k   = 0
    bool now = false
    int  d   = na
    if FO.includes(pk)
        k := 4
        now := true
        d := tk
    else if hollowDay(tk)
        k := dowOf(tk) - 2
        now := true
        d := tk
    else
        [m, p] = hollowNext(na(tk) ? today : math.max(tk, today))
        k := nz(m, 99999999) <= nz(p, 99999999) ? 0 : 4
        d := k == 0 ? m : p
    [k, now, d]
ownNext(int today) =>
    [m, p] = hollowNext(today)
    ["NFP week", m, "day after FOMC", p]''',
struct='''bool hOn = showStr and recent
var int   tdTy = 6
var int   ptdK = na
var float nwC  = na
var float nwO  = na
if tdSt
    tdTy := dayType(tdK, ptdK)
    if dowOf(tdK) <= dowOf(nz(ptdK, tdK)) or na(ptdK)
        nwC := close[1]
        nwO := open
        int nfpK = na
        for j = 0 to 4
            if NP.includes(addDays(tdK, j)) and na(nfpK)
                nfpK := addDays(tdK, j)
        if hOn and not na(nfpK) and not na(nwC)
            int te = keyAt(nfpK, 510)
            float ce = (nwC + nwO) / 2
            line.new(time, nwC, te, nwC, xloc = xloc.bar_time, color = color.new(cLvl, 30), style = line.style_dotted)
            line.new(time, nwO, te, nwO, xloc = xloc.bar_time, color = color.new(cLvl, 30), style = line.style_dotted)
            line.new(time, ce, te, ce, xloc = xloc.bar_time, color = cLvl, style = line.style_dashed)
            label.new(te, ce, "NWOG 50%", xloc = xloc.bar_time, color = #00000000, textcolor = cLvl, style = label.style_label_left, size = size.tiny, tooltip = "NFP week opening gap: Friday's last close to Sunday's 18:00 open, drawn to the release. Its midpoint was touched by Monday's close about 88% of the time (normal weeks 86%).")
    if hOn and FO.includes(ptdK) and not na(rH)
        line.new(time, rH, keyAt(tdK, 974), rH, xloc = xloc.bar_time, color = cLvl, style = line.style_dashed)
        line.new(time, rL, keyAt(tdK, 974), rL, xloc = xloc.bar_time, color = cLvl, style = line.style_dashed)
        label.new(keyAt(tdK, 974), rH, "FOMC high", xloc = xloc.bar_time, color = #00000000, textcolor = cLvl, style = label.style_label_left, size = size.tiny, tooltip = "FOMC day's RTH high. The next day took it 62% of the time vs 55% for any next day.")
        label.new(keyAt(tdK, 974), rL, "FOMC low", xloc = xloc.bar_time, color = #00000000, textcolor = cLvl, style = label.style_label_left, size = size.tiny, tooltip = "FOMC day's RTH low. The next day took it 44% of the time vs 43% for any next day.")
    ptdK := tdK
if hOn and (tdTy == 5 or tdTy == 3) and rthSt and not na(gapPC)
    line.new(time, gapPC, keyAt(calK, 974), gapPC, xloc = xloc.bar_time, color = color.new(cLvl, 40), style = line.style_dotted)
    line.new(time, gapCE, keyAt(calK, 974), gapCE, xloc = xloc.bar_time, color = color.new(cLvl, 20), style = line.style_dotted)
    label.new(keyAt(calK, 974), gapCE, "gap 50%", xloc = xloc.bar_time, color = #00000000, textcolor = cLvl, style = label.style_label_left, size = size.tiny, tooltip = "RTH gap 50% = (prior 16:14 close + 09:30 open) ÷ 2")
if hOn and markEv and mod <= 510 and mod + tfM > 510 and NP.includes(calK)
    label.new(bar_index, high, "NFP", color = #00000000, textcolor = cGh, style = label.style_label_down, size = size.tiny, tooltip = "NFP 08:30 ET: the end of the Hollow week")
if hOn and markEv and mod <= 840 and mod + tfM > 840 and FO.includes(calK)
    label.new(bar_index, high, "FOMC", color = #00000000, textcolor = cGh, style = label.style_label_down, size = size.tiny, tooltip = "FOMC 14:00 ET: tomorrow is a Full Bringer day")
bgcolor(hOn and tdTy == 5 and mod >= 975 and mod < 1020 ? cWin : na, title = "Settlement window 16:15–17:00")''', last='')

def _split_args(inner):
    out, depth, cur, i = [], 0, '', 0
    while i < len(inner):
        ch = inner[i]
        if ch == '"':
            j = inner.index('"', i + 1); cur += inner[i:j + 1]; i = j + 1; continue
        if ch in '([': depth += 1
        if ch in ')]': depth -= 1
        if ch == ',' and depth == 0: out.append(cur.strip()); cur = ''
        else: cur += ch
        i += 1
    out.append(cur.strip()); return out
def trim(src):
    """wrap level lines / end labels that run to a later time today so they are cut at the latest bar (trimL / trimT)"""
    out, i = [], 0
    pat = re.compile(r'(?<![\w.(])(line\.new|label\.new)\(')
    while True:
        m = pat.search(src, i)
        if not m: out.append(src[i:]); break
        j = m.end(); depth = 1
        while depth:
            ch = src[j]
            if ch == '"': j = src.index('"', j + 1)
            elif ch == '(': depth += 1
            elif ch == ')': depth -= 1
            j += 1
        call = src[m.start():j]; args = _split_args(call[call.index('(') + 1:-1])
        if 'xloc = xloc.bar_time' in call and 'extend.both' not in call:
            call = (f'trimL({call}, {args[2]})' if m.group(1) == 'line.new' else f'trimT({call}, {args[0]})')
        out.append(src[i:m.start()] + call); i = j
    return ''.join(out)

def fo(src):
    """add force_overlay = true to every line.new / label.new / box.new / bgcolor call in a Pine block"""
    out, i = [], 0
    pat = re.compile(r'\b(line\.new|label\.new|box\.new|bgcolor)\(')
    while True:
        m = pat.search(src, i)
        if not m: out.append(src[i:]); break
        j = m.end(); depth = 1
        while depth:
            ch = src[j]
            if ch == '"':
                j = src.index('"', j + 1)
            elif ch == '(':
                depth += 1
            elif ch == ')':
                depth -= 1
            j += 1
        call = src[m.start():j]
        if 'force_overlay' not in call: call = call[:-1] + ', force_overlay = true)'
        out.append(src[i:m.start()] + call); i = j
    return ''.join(out)

def wrapfn(src, tag):
    """Pine caps the compiled size of the script's main body (CE10295): move each top-level last-bar block into its own
    function, called once per bar from the main body. Only for drawing blocks that never reassign a global with :="""
    chunks, cur = [], []
    for l in src.split('\n'):
        if l.startswith('if barstate.islast') and any(c.strip() and not c.lstrip().startswith('//') for c in cur):
            chunks.append(cur); cur = []
        cur.append(l)
    if any(c.strip() for c in cur): chunks.append(cur)
    out = []
    for n, c in enumerate(chunks, 1):
        while c and not c[-1].strip(): c.pop()
        body = '\n'.join(('    ' + l) if l.strip() else '' for l in c)
        out.append(f'{tag}{n}() =>\n{body}\n    true\n{tag}{n}()\n')
    return '\n'.join(out)

def wrap_clean(s, tag):
    """Wrap every remaining top-level `if barstate.islast` block that reassigns no global into a function (CE10295)."""
    L = s.split('\n'); out = []; i = 0; n = 0
    tdecl = r'(?:var\s+)?(?:(?:int|float|bool|string|color|label|line|box|table|polyline|linefill|array<\w+>|map<\w+,\s*\w+>)\s+)?'
    while i < len(L):
        if L[i] == 'if barstate.islast':
            j = i + 1
            while j < len(L) and (L[j].startswith((' ', '\t')) or not L[j].strip()): j += 1
            while not L[j - 1].strip(): j -= 1
            seg = L[i:j]; decl = set()
            for l in seg:
                m = re.match(r'^\s+' + tdecl + r'([A-Za-z_]\w*)\s*=(?!=)', l)
                if m: decl.add(m.group(1))
                m = re.match(r'^\s+\[([^\]]+)\]\s*=', l)
                if m: decl |= {x.strip() for x in m.group(1).split(',')}
                m = re.match(r'^\s+for\s+(?:\[([^\]]+)\]|(\w+))\s+(?:=|in)', l)
                if m: decl |= {x.strip() for x in (m.group(1) or m.group(2)).split(',')}
            mod = {m.group(1) for l in seg for m in re.finditer(r'([A-Za-z_]\w*)\s*(?::|\+|-|\*|/|%)=(?!=)', l)} - decl
            if not mod:
                n += 1
                out += [f'{tag}{n}() =>'] + [('    ' + l) if l.strip() else '' for l in seg] + ['    true', f'{tag}{n}()']
            else:
                out += seg
            i = j; continue
        out.append(L[i]); i += 1
    return '\n'.join(out)

core = open('core.pine').read()
for name, I in IND.items():
    s = core.replace('%HEADER%', I['header']).replace('%NAME%', name).replace('%SHORT%', I['short']).replace('%GHOST%', I['ghost'])
    s = s.replace('%DATES%', dates_block()).replace('%SHAPES%', shapes_block())
    s = s.replace('%PROFILES%', profile_block(I['keys']) + '\n' + card_block(I) + '\n' + clock_funcs(I) + '\n' + I['own']).replace('%STRUCT%', fo(trim(I['struct']))).replace('%LAST%', fo(I['last']))
    s = s.replace('%FEDIN%', I.get('fedin', 'showFd = false')).replace('%FEDREQ%', I.get('fedreq', '')).replace('%EXTRA%', wrapfn(fo(I.get('lastx', '')) + I.get('extra', ''), 'drawLast') if I.get('lastx') else fo(I.get('lastx', '')) + I.get('extra', '')).replace('%PANEIN%', I.get('panein', 'paneV = "Event clock"'))
    s = s.replace('%CLOCK%', clock_block(I['ck'])).replace('%CKT%', str(len(I['ck']) + 1)).replace('%REL%', I['rel']).replace('%SINPUTS%', I.get('sinputs', ''))
    assert '%' not in ''.join(l for l in s.split('\n') if '%' in l and ('%HEAD' in l or '%NAME' in l or '%STR' in l or '%PROF' in l or '%LAST' in l or '%DATES' in l or '%SHAPES' in l or '%CLOCK' in l or '%CKT' in l or '%REL' in l))
    # inputs that only some models use: drop them where nothing reads them, so the settings never show a dead control
    for ident in ('cWin', 'cHands'):
        if len(re.findall(r'\b' + ident + r'\b', s)) == 1:
            s = re.sub(r'\n' + ident + r' +=[^\n]*', '', s)
    if I.get('lastx'):
        from vz_trim import nopo3_full
        s = nopo3_full(s)
        from vz_trim import novxdx
        s = novxdx(s)
        from vz_trim import comments
        s = comments(s)
        s = wrap_clean(s, 'drawCore')
        from cardq import queue_cards
        s = queue_cards(s)
        from cardq import shrink
        s = shrink(s)
        from cardq import pack
        s = pack(s)
    open(f"{I.get('file', name)}.pine", 'w').write(s)
    print(name, len(s.split('\n')), 'lines')
