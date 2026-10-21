"""Vizard's FOMC stages: chart drawings (week open, 14:00 / 14:30 opens, snapshots, RTH-gap octants over NY AM) and the
stages card (past-N stage tallies, live moves against the 3-year average, next-day NY AM, gaps, NQ / ES against DXY).
Numbers come from fomc/fomc_stats.py (fomc_stats.json, rec_NQ.pkl, rec_ES.pkl)."""
import json, numpy as np, pandas as pd

J = json.load(open('/home/claude/hm/fomc/fomc_stats.json'))
RS, DX = J['res'], J['dxy']
REC = {s: pd.read_pickle(f'/home/claude/hm/fomc/rec_{s}.pkl') for s in ('NQ', 'ES')}


def q(s):
    return '"' + s.replace('"', "'") + '"'


def pc(x):
    return f'{100 * x:.0f}%'


def per(s, key, src=None):
    r = (src or RS)[s][key]
    return r['all'], r['A'], r['B'], r['held']


def recs(s):
    R = REC[s]; out = []
    for d, r in R.iterrows():
        f = lambda v: '' if pd.isna(v) else (f'{round(v * 4) / 4:g}')
        out.append(f"{d:%Y%m%d},{f(r.s1)},{f(r.s2)},{f(r.rth)},{round(r.o930):d},{f(r.amN)}")
    return out, int(R.index.max().strftime('%Y%m%d'))


def wrap(items, per_line=6):
    rows = [';'.join(items[i:i + per_line]) for i in range(0, len(items), per_line)]
    return '"' + (';"\n     + "').join(rows) + '"'


def rec_block():
    lines = ['// Built-in FOMC records (1-minute data): date, stage 1, stage 2 and RTH move (pts), 09:30 open, next day\'s NY AM move (pts)']
    for s in ('NQ', 'ES'):
        items, end = recs(s)
        lines.append(f'VZ_{s} = {wrap(items)}')
        lines.append(f'VZ_END_{s} = {end}')
    return '\n'.join(lines)


def both(fn):
    """Pine expression choosing the ES or the NQ version of a string. Long texts that differ only in their numbers (and the
    symbol) become one shared template filled at load time, so the text is embedded once instead of twice."""
    es, nq = fn("ES"), fn("NQ")
    if es == nq:
        return q(es)
    if len(es) > 150:
        import re as _re
        pat = r'(\d+(?:\.\d+)?|\bES\b|\bNQ\b)'
        pe, pn = _re.split(pat, es), _re.split(pat, nq)
        if len(pe) == len(pn) and all(pe[i] == pn[i] for i in range(0, len(pe), 2)) and '{' not in es and '|' not in es + nq:
            skel, ve, vn = [], [], []
            for i, (a, b) in enumerate(zip(pe, pn)):
                if i % 2 == 0 or a == b:
                    skel.append(a)
                else:
                    skel.append('{%d}' % len(ve)); ve.append(a); vn.append(b)
            return f'fillT({q("".join(skel))}, isES ? {q("|".join(ve))} : {q("|".join(vn))})'
    return f'isES ? {q(es)} : {q(nq)}'


def vb(fn):
    return f'isES ? {"true" if fn("ES") else "false"} : {"true" if fn("NQ") else "false"}'


# ── texts per symbol
def t_stage(s, k, win, name):
    a, A, B, h = per(s, k + '_up')
    z = RS[s][k + '_abs']
    return (f"{name} = {win}. Arrows: the last N FOMC days, oldest → newest (▲ closed the window higher). 2018–26 it closed higher on "
            f"{pc(a['p'])} of {a['n']} FOMC days vs {pc(a['pb'])} of ordinary days (2018–24 {pc(A['p'])}, 2025–26 {pc(B['p'])}); "
            f"no lean held (p {a['pv']:.2f}). Middle: today's {name.lower()} so far. Right: the average size of {name.lower()} over the last "
            f"3 years of FOMC days, at today's price. Size is what held: FOMC {name.lower()} runs ×{z['all']['ratio']:.2f} an ordinary day's "
            f"same window (2018–24 ×{z['A']['ratio']:.2f}, 2025–26 ×{z['B']['ratio']:.2f}).")


def t_rth(s):
    a, A, B, h = per(s, 'rth_up'); z = RS[s]['rth_abs']; am = RS[s]['am_abs']
    return (f"RTH = 09:30 open → 16:14 close. FOMC days closed RTH higher {pc(a['p'])} of {a['n']} vs {pc(a['pb'])} on ordinary days "
            f"(2018–24 {pc(A['p'])}, 2025–26 {pc(B['p'])}, p {a['pv']:.2f}): a small down lean that did not pass the test. RTH size ×{z['all']['ratio']:.2f} "
            f"(2025–26 ×{z['B']['ratio']:.2f}); the NY AM before the release ran ×{am['all']['ratio']:.2f} of an ordinary NY AM (held), so the "
            f"move is saved for 14:00. Right: average |RTH move| over the last 3 years at today's price.")


def t_next(s, k, name):
    a, A, B, h = per(s, 'nx_' + k); r = RS[s]['nx_' + k]
    return (f"Next day's NY AM (09:30 → 11:00) closed the same way as {name} on {pc(a['p'])} of {a['n']} FOMC days "
            f"(2018–24 {pc(A['p'])}, 2025–26 {pc(B['p'])}). Index = that rate ÷ what the up-drift alone would give "
            f"({pc(r['expected'])}: carry-charge markets drift up, so matches are judged against the two up-rates, not 50%) × 100 = "
            f"{r['index']:.0f}; same windows on ordinary days give {r['index_base']:.0f}. 100 = no information. "
            + ("No continuation lean held." if r['index'] < 110 else ""))


def t_gap(s):
    a, A, B, h = per(s, 'gap_fill'); b14 = RS[s]['gap_fill14']['all']
    return (f"FOMC morning RTH gap (prior 16:14 close → 09:30 open) traded back through the prior close by 16:14 on {pc(a['p'])} of "
            f"{a['n']} FOMC days vs {pc(a['pb'])} on ordinary days (2018–24 {pc(A['p'])} vs {pc(A['pb'])}, 2025–26 {pc(B['p'])} vs {pc(B['pb'])}"
            f"{'; held' if h else ''}). Before 14:00 only {pc(b14['p'])} vs {pc(b14['pb'])}: the extra fills come after the statement. "
            f"Don't expect the morning gap to stay open.")


def t_q(s):
    a, A, B, h = per(s, 'nx_q')
    return (f"Day after FOMC: its own RTH gap split into eighths; the open-side quarter is the quarter next to the 09:30 open (the top "
            f"quarter of a gap up, the bottom of a gap down). NY AM never traded back past it on {pc(a['p'])} of {a['n']} days vs "
            f"{pc(a['pb'])} on ordinary days (2018–24 {pc(A['p'])} vs {pc(A['pb'])}, 2025–26 {pc(B['p'])} vs {pc(B['pb'])}"
            f"{'; held' if h else '; did not hold in both periods'}). Still a minority outcome: most days retrace past it.")


def t_ce(s):
    a, A, B, h = per(s, 'nx_ce')
    return (f"Day after FOMC: NY AM traded to its gap's 50% on {pc(a['p'])} of {a['n']} days vs {pc(a['pb'])} on ordinary days "
            f"(2018–24 {pc(A['p'])} vs {pc(A['pb'])}, 2025–26 {pc(B['p'])} vs {pc(B['pb'])}, p {a['pv']:.2f}{'; held' if h else '; not held'}). "
            f"Less mean reversion than usual, but it still taps more often than not.")


def t_dx(s, k, win):
    a, A, B, h = per(s, k, DX); c = DX[s].get(k + '_cond')
    return (f"{win}: {s} moved the other way to DXY futures on {pc(a['p'])} of {a['n']} FOMC days vs {pc(a['pb'])} on ordinary days "
            f"(Jan 2023 – Aug 2026; 2023–24 {pc(A['p'])}, 2025–26 {pc(B['p'])}{'; held' if h else '; p %.2f, not held' % a['pv']}). "
            + (f"{s} rose in {pc(c['up_when_dx_dn'])} of the windows where DXY fell (n {c['n_dn']}) and {pc(c['up_when_dx_up'])} where it rose "
               f"(n {c['n_up']}). " if c else "")
            + "Same window: it describes how the stage moves, it does not forecast it. Live: today's DXY and "
            + f"{'ES' if s == 'ES' else 'NQ'} in the same window.")


V = lambda s, key, src=None: pc((src or RS)[s][key]['all']['p'])
VB = lambda s, key, src=None: pc((src or RS)[s][key]['all']['pb'])
H = lambda s, key, src=None: (src or RS)[s][key]['held']

CONST = '\n'.join([
    '// long ES / NQ texts: one template, the numbers that differ filled in once at load ({0}, {1}, … ← the |-separated values)',
    'fillT(string t, string v) =>',
    '    string out = t',
    '    array<string> p = str.split(v, "|")',
    '    for i = 0 to p.size() - 1',
    '        out := str.replace_all(out, "{" + str.tostring(i) + "}", p.get(i))',
    '    out',
    rec_block(),
    '// Shock cone: typical distance from the 14:00 open by 5-minute step to 16:15 (ADR20 ×1000): up 50% · up 80% · down 50% · down 80%, FOMC days 2018–26',
    'CONE_NQ = "130,153,159,169,169,169,188,214,237,259,264,267,284,306,306,306,306,306,310,310,312,318,325,326,345,361,361;258,287,287,374,380,381,381,402,451,510,526,542,554,562,562,562,571,571,572,572,572,572,572,577,577,613,632;104,115,125,131,142,156,169,172,175,175,205,218,227,228,239,239,239,243,251,265,265,297,314,314,319,354,358;267,291,324,327,336,336,404,481,488,521,541,585,585,585,585,601,601,620,673,700,703,719,746,796,826,835,835"',
    'CONE_ES = "145,150,152,181,181,188,197,218,272,281,305,305,310,310,310,310,310,310,315,315,315,315,315,327,327,327,330;300,329,353,365,365,365,375,410,443,516,532,536,563,621,629,640,671,678,683,683,683,683,683,683,683,683,683;122,134,141,152,160,160,168,190,212,215,218,221,232,233,257,257,279,292,332,348,371,377,377,378,394,394,394;274,291,321,352,358,358,404,451,507,552,589,620,636,643,652,685,728,728,764,787,828,874,891,923,965,965,965"',
    f'var string VZT_S1 = {both(lambda s: t_stage(s, "s1", "14:00 open → 14:29 close (the statement)", "Stage 1"))}',
    f'var string VZT_S2 = {both(lambda s: t_stage(s, "s2", "14:30 open → 16:14 close (press conference to the RTH close)", "Stage 2"))}',
    f'var string VZT_R  = {both(t_rth)}',
    f'var string VZT_N1 = {both(lambda s: t_next(s, "s1", "stage 1"))}',
    f'var string VZT_N2 = {both(lambda s: t_next(s, "s2", "stage 2"))}',
    f'var string VZT_GF = {both(t_gap)}',
    f'var string VZT_Q  = {both(t_q)}',
    f'var string VZT_CE = {both(t_ce)}',
    f'var string VZT_X1 = {both(lambda s: t_dx(s, "s1", "Stage 1 (14:00–14:30)"))}',
    f'var string VZT_X2 = {both(lambda s: t_dx(s, "s2", "Stage 2 (14:30–16:14)"))}',
    f'var string VZT_XD = {both(lambda s: t_dx(s, "day", "Trading day (18:00 → 17:00)"))}',
    f'VZV_N1 = {both(lambda s: V(s, "nx_s1"))}',
    f'VZI_N1 = {both(lambda s: "%.0f" % RS[s]["nx_s1"]["index"])}',
    f'VZV_N2 = {both(lambda s: V(s, "nx_s2"))}',
    f'VZE_N1 = {both(lambda s: pc(RS[s]["nx_s1"]["expected"]))}',
    f'VZE_N2 = {both(lambda s: pc(RS[s]["nx_s2"]["expected"]))}',
    f'VZI_N2 = {both(lambda s: "%.0f" % RS[s]["nx_s2"]["index"])}',
    f'VZV_GF = {both(lambda s: V(s, "gap_fill"))}',
    f'VZB_GF = {both(lambda s: VB(s, "gap_fill"))}',
    f'VZH_GF = {vb(lambda s: H(s, "gap_fill"))}',
    f'VZV_Q  = {both(lambda s: V(s, "nx_q"))}',
    f'VZB_Q  = {both(lambda s: VB(s, "nx_q"))}',
    f'VZH_Q  = {vb(lambda s: H(s, "nx_q"))}',
    f'VZV_CE = {both(lambda s: V(s, "nx_ce"))}',
    f'VZB_CE = {both(lambda s: VB(s, "nx_ce"))}',
    f'VZH_CE = {vb(lambda s: H(s, "nx_ce"))}',
    f'VZV_X1 = {both(lambda s: V(s, "s1", DX))}',
    f'VZB_X1 = {both(lambda s: VB(s, "s1", DX))}',
    f'VZH_X1 = {vb(lambda s: H(s, "s1", DX))}',
    f'VZV_X2 = {both(lambda s: V(s, "s2", DX))}',
    f'VZB_X2 = {both(lambda s: VB(s, "s2", DX))}',
    f'VZH_X2 = {vb(lambda s: H(s, "s2", DX))}',
    f'VZV_XD = {both(lambda s: V(s, "day", DX))}',
    f'VZB_XD = {both(lambda s: VB(s, "day", DX))}',
    f'VZH_XD = {vb(lambda s: H(s, "day", DX))}',
])

SINPUTS = '''showWO  = input.bool(true, "Week open, 14:00 and 14:30 opens", group = grpS, inline = "s2", tooltip = "The week's open (Sunday 18:00) and, on FOMC days, the open of the 14:00 and 14:30 candles, each extended to the right of price. On the day after FOMC the two FOMC lines stay up.", display = display.none)
showSnp = input.bool(true, "Snapshots", group = grpS, inline = "s2", tooltip = "Fixed labels on FOMC days, printed once and left where they were: at 14:00, price against the 09:30 open and the week open; at 14:30, stage 1's move and the same two distances. Needs a chart of 30 minutes or less.", display = display.none)
showOct = input.bool(true, "RTH gap octants over NY AM", group = grpS, inline = "s3", tooltip = "FOMC day and the day after: the RTH gap (prior 16:14 close → 09:30 open) in eighths from 09:30 to 11:00, the 50% line bold and the quarter next to the open shaded.", display = display.none)
cOq     = input.color(color.new(#26a69a, 78), "Open-side quarter", group = grpS, inline = "s3", display = display.none)
showCone = input.bool(true, "Statement shock cone", group = grpS, inline = "s4", tooltip = "FOMC day, from the 14:00 open to 16:15: how far price had travelled by each 5 minutes on past FOMC days (2018–26), up and down separately, scaled to today's ADR20. Inner band: half of FOMC days stayed inside; outer band: 80%. Price outside the outer band = a bigger reaction than 4 in 5 past statements by that time. Before 14:00 a faint preview sits at the current price.", display = display.none)'''

INPUTS = '''grpV    = "FOMC stages card"
showSg  = input.bool(true, "Stages card", group = grpV, inline = "v0", tooltip = "Stage 1 (14:00–14:30, the statement) and stage 2 (14:30–16:14, press conference to the RTH close) on the last N FOMC days, today's moves against the last 3 years, the next day's NY AM, the RTH gaps, and same-window moves against DXY. Mobile layout: a compact version.", display = display.none)
sgOn    = input.string("Price chart", "", options = ["Price chart", "Indicator pane"], group = grpV, inline = "v0", display = display.none)
sgPos   = input.string("Bottom right", "", options = ["Top left", "Top center", "Top right", "Middle left", "Middle right", "Bottom left", "Bottom center", "Bottom right"], group = grpV, inline = "v0", display = display.none)
sgN     = input.int(12, "Last N FOMC days", minval = 4, maxval = 60, group = grpV, display = display.none)'''

GLOBALS = '''
// ═══════════════════════════════════════════════════════════════ FOMC stages (Vizard)
// Stage 1 = 14:00 open → 14:29 close (the statement); stage 2 = 14:30 open → 16:14 close (press conference to the RTH close).
%CONST%
var array<int>   VBd  = array.new<int>()
var array<float> VBs1 = array.new<float>()
var array<float> VBs2 = array.new<float>()
var array<float> VBr  = array.new<float>()
var array<float> VBo  = array.new<float>()
var array<float> VBn  = array.new<float>()
if barstate.isfirst
    for rec in str.split(isES ? VZ_ES : VZ_NQ, ";")
        array<string> f = str.split(rec, ",")
        if f.size() >= 6
            VBd.push(int(str.tonumber(f.get(0))))
            VBs1.push(str.tonumber(f.get(1)))
            VBs2.push(str.tonumber(f.get(2)))
            VBr.push(str.tonumber(f.get(3)))
            VBo.push(str.tonumber(f.get(4)))
            VBn.push(str.tonumber(f.get(5)))
int  vzEnd = isES ? VZ_END_ES : VZ_END_NQ
bool vzF   = FO.includes(calK)
bool vzP   = FO.includes(tdPK) and tdK == calK                   // the day after an FOMC day
// the week's open
var int   wkX  = na
var float wkOp = na
if ta.change(time("W")) != 0
    wkX  := bar_index
    wkOp := open
// stage prices on the FOMC day (and DXY at the same moments)
var int   vzK  = na
var float s14O = na
var int   s14X = na
var float s30O = na
var int   s30X = na
var float s1C  = na
var float s2C  = na
var float x14  = na
var float x30  = na
var float x1C  = na
var float x2C  = na
bool at14 = vzF and mod >= 840 and mod < 870 and (mod[1] < 840 or calK[1] != calK) and nz(vzK) != calK
if at14
    vzK  := calK
    s14O := open
    s14X := bar_index
    x14  := dxL[1]
    s30O := na
    s30X := na
    s1C  := na
    s2C  := na
    x30  := na
    x1C  := na
    x2C  := na
bool at30 = vzK == calK and na(s30O) and mod >= 870 and mod < 975
if at30
    s30O := open
    s30X := bar_index
    s1C  := close[1]
    x30  := dxL[1]
    x1C  := dxL[1]
if vzK == calK and not na(s30O) and na(s2C) and mod >= 975
    s2C := close[1]
    x2C := dxL[1]
// NY AM (09:30 → 11:00) of every RTH day, and the gap events on the FOMC day and the day after
var float amH = na
var float amL = na
var float amC = na
var int   gfT = na
var int   ceT = na
var int   qbT = na
if rthSt
    amH := high
    amL := low
    amC := na
    gfT := na
    ceT := na
    qbT := na
else if mod >= 570 and mod < 660
    amH := math.max(amH, high)
    amL := math.min(amL, low)
if mod >= 660 and mod < 975 and na(amC) and tgKey == calK
    amC := close[1]
if vzF and tgKey == calK and mod >= 570 and mod < 975 and na(gfT) and not na(gapPC) and rthO != gapPC
    if (rthO > gapPC and low <= gapPC) or (rthO < gapPC and high >= gapPC)
        gfT := time
if vzP and tgKey == calK and mod >= 570 and mod < 660 and not na(gapPC) and rthO != gapPC
    float g_  = rthO - gapPC
    float ce_ = gapPC + 0.5 * g_
    float q_  = gapPC + 0.75 * g_
    if na(ceT) and (g_ > 0 ? low <= ce_ : high >= ce_)
        ceT := time
    if na(qbT) and (g_ > 0 ? low <= q_ : high >= q_)
        qbT := time
// the chart's own FOMC records (used for meetings after the built-in ones end)
var array<int>   LVd  = array.new<int>()
var array<float> LVs1 = array.new<float>()
var array<float> LVs2 = array.new<float>()
var array<float> LVr  = array.new<float>()
var array<float> LVo  = array.new<float>()
var array<float> LVn  = array.new<float>()
if vzK == calK and not na(s2C) and tgKey == calK and not na(rthO) and (LVd.size() == 0 or LVd.last() != calK)
    LVd.push(calK)
    LVs1.push(s1C - s14O)
    LVs2.push(s2C - s30O)
    LVr.push(s2C - rthO)
    LVo.push(rthO)
    LVn.push(na)
if vzP and not na(amC) and LVd.size() > 0 and LVd.last() == tdPK and na(LVn.last())
    LVn.set(LVn.size() - 1, amC - rthO)
// the stages card's table
var table TV  = na
var int   tvO = 0
SGR = layI == "Mobile" ? 7 : 15
if barstate.isfirst and showSg
    tvO := sgPos == "Top left" or sgPos == "Top center" or (sgPos == "Top right" and sgOn == "Indicator pane") ? 1 : 0
    if sgOn == "Price chart"
        TV := table.new(posOf(sgPos), 5, SGR + tvO, bgcolor = #00000000, frame_width = 0, border_width = 0, force_overlay = true)
    else
        TV := table.new(posOf(sgPos), 5, SGR + tvO, bgcolor = #00000000, frame_width = 0, border_width = 0)
    if tvO == 1
        TV.cell(0, 0, "", height = sgOn == "Price chart" ? 3.5 : 7.0, bgcolor = #00000000)
        TV.merge_cells(0, 0, 4, 0)
    TV.merge_cells(1, tvO, 3, tvO)
var array<float> CN = parseMilli(isES ? CONE_ES : CONE_NQ)
cnAt(int sr, int k) => CN.get(sr * 27 + k)
// one band of the shock cone as a closed shape, from 14:00 to step kEnd (5-minute steps), around price o (ADR a in price)
coneBand(int dk, float o, float a, int su, int sd, int kEnd, color fc, color lc) =>
    array<chart.point> pts = array.new<chart.point>()
    pts.push(chart.point.from_time(keyAt(dk, 840), o))
    for k = 0 to kEnd
        pts.push(chart.point.from_time(keyAt(dk, 845 + 5 * k), o + cnAt(su, k) * a))
    for k = kEnd to 0
        pts.push(chart.point.from_time(keyAt(dk, 845 + 5 * k), o - cnAt(sd, k) * a))
    polyline.new(pts, curved = false, closed = true, xloc = xloc.bar_time, line_color = lc, fill_color = fc, force_overlay = true)
var array<polyline> VPC = array.new<polyline>()
vzSg(float v) => na(v) ? "—" : (v >= 0 ? "+" : "−") + str.tostring(math.abs(v), format.mintick)
vzAr(float v) => na(v) or v == 0 ? "·" : v > 0 ? "▲" : "▼"
// live same-window read against DXY: ⇄ other way, ⇉ same way
xs(float d, float n) => na(d) or na(n) or d == 0 or n == 0 ? "" : " · today DXY " + vzAr(d) + str.tostring(math.abs(d), "0.00") + "% " + symR + " " + vzAr(n) + (math.sign(d) != math.sign(n) ? " ⇄" : " ⇉")
'''

STRUCT = '''
// FOMC day: the 14:00 and 14:30 opens to the RTH close, and fixed snapshots of the displacement at 14:00 and 14:30
if vOn and showWO and at14
    line.new(time, open, keyAt(calK, 974), open, xloc = xloc.bar_time, color = color.new(cGh, 15), width = 1)
if vOn and showWO and at30
    line.new(time, open, keyAt(calK, 974), open, xloc = xloc.bar_time, color = color.new(cGh, 35), width = 1, style = line.style_dashed)
if vOn and showSnp and at14 and tgKey == calK and not na(rthO)
    label.new(bar_index - 1, open, "14:00\\n" + vzSg(open - rthO) + " vs 09:30\\n" + vzSg(open - wkOp) + " vs week open", color = color.new(cGh, 25), textcolor = #ffffff, style = label.style_label_right, size = size.tiny, tooltip = "Snapshot at the statement (14:00 open), fixed: distance from today's 09:30 open and from the week's open (Sunday 18:00).")
if vOn and showSnp and at30 and tgKey == calK and not na(rthO) and not na(s14O)
    label.new(bar_index, low, "14:30 · S1 " + vzSg(close[1] - s14O) + "\\n" + vzSg(open - rthO) + " vs 09:30\\n" + vzSg(open - wkOp) + " vs week open", color = color.new(cGh, 45), textcolor = #ffffff, style = label.style_label_up, size = size.tiny, tooltip = "Snapshot at the press conference (14:30 open), fixed: stage 1's move (14:00 → 14:29 close), and the distance from today's 09:30 open and from the week's open.")
// FOMC day: the full shock cone, drawn once the day's 16:15 bar prints
if vOn and showCone and vzK == calK and not na(s14O) and not na(ADRtd) and mod >= 975 and mod[1] < 975
    coneBand(calK, s14O, ADRtd * s14O, 1, 3, 26, color.new(cGh, 91), color.new(cGh, 72))
    coneBand(calK, s14O, ADRtd * s14O, 0, 2, 26, color.new(cGh, 85), #00000000)
// FOMC day and the day after: the RTH gap in eighths over NY AM, 50% bold, the quarter next to the open shaded
if vOn and showOct and rthSt and (vF or vzP) and not na(gapPC) and rthO != gapPC
    float gp = rthO - gapPC
    int   te = keyAt(calK, 660)
    line  l6 = na
    line  l8 = na
    for k = 0 to 8
        line l = line.new(time, gapPC + gp * k / 8, te, gapPC + gp * k / 8, xloc = xloc.bar_time, color = k == 4 ? cLvl : k >= 6 ? color.new(cOq, 10) : color.new(cLvl, k == 0 ? 30 : 65), style = k == 4 ? line.style_dashed : line.style_dotted, width = k == 4 ? 2 : 1)
        if k == 6
            l6 := l
        if k == 8
            l8 := l
    linefill.new(l6, l8, cOq)
    label.new(te, gapPC + gp * 0.875, "open-side ¼", xloc = xloc.bar_time, color = #00000000, textcolor = color.new(cOq, 0), style = label.style_label_left, size = size.tiny, tooltip = vzP ? VZT_Q : "The quarter of this morning's RTH gap next to the 09:30 open. " + VZT_GF)
    label.new(te, gapPC + gp * 0.5, "gap 50%", xloc = xloc.bar_time, color = #00000000, textcolor = cLvl, style = label.style_label_left, size = size.tiny, tooltip = vzP ? VZT_CE : VZT_GF)
bgcolor(vOn and showOct and (vF or vzP) and mod >= 570 and mod < 660 ? color.new(cOq, math.min(100, color.t(cOq) + 14)) : na, title = "NY AM, FOMC day and the day after")'''

LAST = '''
    // the shock cone, live on the FOMC day: from 14:00 it runs a few minutes ahead of price; before 14:00 a faint preview
    for p in VPC
        p.delete()
    VPC.clear()
    if showCone and vzF and not na(ADRtd)
        if vzK == calK and not na(s14O) and mod < 975
            int kE = math.min(26, int((mod - 840) / 5) + 2)
            VPC.push(coneBand(calK, s14O, ADRtd * s14O, 1, 3, kE, color.new(cGh, 91), color.new(cGh, 72)))
            VPC.push(coneBand(calK, s14O, ADRtd * s14O, 0, 2, kE, color.new(cGh, 85), #00000000))
            RT.push(label.new(keyAt(calK, 845 + 5 * kE), s14O + cnAt(1, kE) * ADRtd * s14O, "80% of FOMC days", xloc = xloc.bar_time, color = #00000000, textcolor = color.new(cGh, 20), style = label.style_label_lower_left, size = size.tiny, tooltip = "By " + hhmm(845 + 5 * kE) + " ET, 80% of FOMC days (2018–26) had gone no further than this above the 14:00 open, and the inner band held half of them. Scaled by today's ADR20."))
        else if mod >= 570 and mod < 840
            VPC.push(coneBand(calK, close, ADRtd * close, 1, 3, 26, color.new(cGh, 95), color.new(cGh, 82)))
    // week open, and the FOMC day's 14:00 and 14:30 opens, extended to the right of price
    if showWO and not na(wkX) and not na(wkOp)
        RL.push(line.new(math.max(wkX, bar_index - 4900), wkOp, xd, wkOp, color = color.new(cLvl, 15), style = line.style_dashed))
        RT.push(label.new(bar_index + 2, wkOp, "week open " + pf(wkOp), color = #00000000, textcolor = cLvl, style = label.style_label_left, size = size.tiny))
    if showWO and (vzF or (vzP and vzK == tdPK)) and not na(s14X) and bar_index - s14X < 4900
        RL.push(line.new(s14X, s14O, xd, s14O, color = color.new(cGh, 15)))
        RT.push(label.new(bar_index + 2, s14O, "14:00 open " + pf(s14O), color = #00000000, textcolor = cGh, style = label.style_label_left, size = size.tiny))
        if not na(s30X)
            RL.push(line.new(s30X, s30O, xd, s30O, color = color.new(cGh, 35), style = line.style_dashed))
            RT.push(label.new(bar_index + 2, s30O, "14:30 open " + pf(s30O), color = #00000000, textcolor = color.new(cGh, 25), style = label.style_label_left, size = size.tiny))'''

CARD = '''
    // ── FOMC stages card: records newest first (the chart's own after the built-in ones end, then built-in)
    array<int>   Rd = array.new<int>()
    array<float> R1 = array.new<float>()
    array<float> R2 = array.new<float>()
    array<float> RR = array.new<float>()
    array<float> RO = array.new<float>()
    array<float> RN = array.new<float>()
    if LVd.size() > 0
        for i = LVd.size() - 1 to 0
            if LVd.get(i) > vzEnd
                Rd.push(LVd.get(i))
                R1.push(LVs1.get(i))
                R2.push(LVs2.get(i))
                RR.push(LVr.get(i))
                RO.push(LVo.get(i))
                RN.push(LVn.get(i))
    if VBd.size() > 0
        for i = VBd.size() - 1 to 0
            Rd.push(VBd.get(i))
            R1.push(VBs1.get(i))
            R2.push(VBs2.get(i))
            RR.push(VBr.get(i))
            RO.push(VBo.get(i))
            RN.push(VBn.get(i))
    int    nR  = math.min(sgN, Rd.size())
    int    nSq = math.min(nR, mob ? 8 : 12)
    string sq1 = ""
    string sq2 = ""
    string sq3 = ""
    int u1 = 0
    int u2 = 0
    int u3 = 0
    int dn1 = 0
    int dn2 = 0
    int dn3 = 0
    if nR > 0
        for i = 0 to nR - 1
            if i < nSq
                sq1 := vzAr(R1.get(i)) + sq1
                sq2 := vzAr(R2.get(i)) + sq2
                sq3 := vzAr(RR.get(i)) + sq3
            u1  += R1.get(i) > 0 ? 1 : 0
            u2  += R2.get(i) > 0 ? 1 : 0
            u3  += RR.get(i) > 0 ? 1 : 0
            dn1 += R1.get(i) < 0 ? 1 : 0
            dn2 += R2.get(i) < 0 ? 1 : 0
            dn3 += RR.get(i) < 0 ? 1 : 0
    // average size over the last 3 years of FOMC days, as % of the 09:30 open, at today's price
    float sa1 = 0.0
    float sa2 = 0.0
    float sa3 = 0.0
    float saN = 0.0
    int   k3  = 0
    int   kN  = 0
    if Rd.size() > 0
        for i = 0 to Rd.size() - 1
            if Rd.get(i) >= today - 30000 and RO.get(i) > 0
                sa1 += math.abs(R1.get(i)) / RO.get(i)
                sa2 += math.abs(R2.get(i)) / RO.get(i)
                sa3 += math.abs(RR.get(i)) / RO.get(i)
                k3  += 1
                if not na(RN.get(i))
                    saN += math.abs(RN.get(i)) / RO.get(i)
                    kN  += 1
    bool  tdOk = tgKey == calK and not na(rthO) and mod >= 570
    float vRef = tdOk ? rthO : close
    float av1  = k3 > 0 ? sa1 / k3 * vRef : na
    float av2  = k3 > 0 ? sa2 / k3 * vRef : na
    float av3  = k3 > 0 ? sa3 / k3 * vRef : na
    float avN  = kN > 0 ? saN / kN * vRef : na
    // today, live
    float sv1  = vzK == calK and not na(s14O) ? (na(s1C) ? close : s1C) - s14O : na
    float sv2  = vzK == calK and not na(s30O) ? (na(s2C) ? close : s2C) - s30O : na
    float svR  = vzF and tdOk ? (mod < 975 ? close : rthC) - rthO : na
    float amNw = vzP and tdOk ? (na(amC) ? close : amC) - rthO : na
    float dv1  = vzK == calK and not na(x14) and x14 > 0 ? ((na(x1C) ? dxL : x1C) / x14 - 1) * 100 : na
    float dv2  = vzK == calK and not na(x30) and x30 > 0 ? ((na(x2C) ? dxL : x2C) / x30 - 1) * 100 : na
    float dvD  = not na(dxTdO) and dxTdO > 0 and not na(dxL) ? (dxL / dxTdO - 1) * 100 : na
    float nqD  = close - tdO
    string nwT = ""
    float  nwV = na
    float  nwA = na
    if vzF and tdOk
        nwT := mod < 840 ? "RTH so far (before 14:00)" : mod < 870 ? "stage 1" : mod < 975 ? "stage 2" : "RTH"
        nwV := math.abs(mod < 840 ? close - rthO : mod < 870 ? sv1 : mod < 975 ? sv2 : svR)
        nwA := mod < 870 and mod >= 840 ? av1 : mod >= 870 and mod < 975 ? av2 : av3
    else if vzP and tdOk
        nwT := "NY AM (day after)"
        nwV := math.abs(amNw)
        nwA := avN
    float  nwX = na(nwV) or na(nwA) or nwA <= 0 ? na : nwV / nwA
    int    nxF = nextOf(FO, today)
    int    ddF = na(nxF) ? na : inDays(nxF, today)
    string sgPill = vzF ? "FOMC TODAY" : vzP ? "DAY AFTER" : na(ddF) ? "—" : "FOMC IN " + str.tostring(ddF) + "D"
    color  sgPbg  = vzF ? #ffffff : vzP ? cNeu : color.new(#000000, 55)
    color  sgPfg  = vzF ? cGh : vzP ? cTx : #ffffff
    // live notes for the rate rows
    bool   lastIsY = Rd.size() > 0 and Rd.get(0) == tdPK
    string nN1 = vzP and not na(amNw) and lastIsY ? " · today " + vzAr(amNw) + (math.sign(amNw) == math.sign(R1.get(0)) ? " with" : " against") : ""
    string nN2 = vzP and not na(amNw) and lastIsY ? " · today " + vzAr(amNw) + (math.sign(amNw) == math.sign(R2.get(0)) ? " with" : " against") : ""
    string nGF = vzF and tdOk and not na(gapPC) ? (not na(gfT) ? " · today filled " + str.format_time(gfT, "HH:mm", TZ) : " · today open, " + pf(math.abs(close - gapPC)) + " to go") : ""
    string nQ  = vzP and tdOk and not na(gapPC) ? (not na(qbT) ? " · today broke " + str.format_time(qbT, "HH:mm", TZ) : mod < 660 ? " · today holding" : " · today held ✓") : ""
    string nCE = vzP and tdOk and not na(gapPC) ? (not na(ceT) ? " · today tapped " + str.format_time(ceT, "HH:mm", TZ) : mod < 660 ? " · today not yet" : " · today missed ✓") : ""
    string nX1 = xs(dv1, sv1)
    string nX2 = xs(dv2, sv2)
    string nXD = xs(dvD, nqD)
    color  cU  = cDisc
    color  cD  = cPrem
    if showSg and not na(TV) and not mob
        int r0 = tvO
        cardHead(TV, r0, cGh, dot + " VIZARD · FOMC STAGES · " + symTag, "Stage 1 = 14:00 → 14:30 (statement), stage 2 = 14:30 → 16:14 (press conference to the RTH close). Arrows: the last " + str.tostring(nR) + " FOMC days, oldest → newest. Today's moves are live; the 3-year averages scale each past day's move to today's price. Rate rows: 2018–26 on " + symR + " 1-minute data (DXY rows Jan 2023 – Aug 2026); a green key held in both halves.", sgPill, sgPfg, sgPbg)
        cardSub(TV, r0 + 1, cGh, "last " + str.tostring(nR) + " FOMC days · oldest → newest", "today", "3y avg")
        cardRow(TV, r0 + 2, cGh, "14:00", false, sq1 + "  ▲" + str.tostring(u1) + " ▼" + str.tostring(dn1), vzSg(sv1), na(av1) ? "—" : "±" + pf(av1), VZT_S1, na(sv1) ? cTx : sv1 >= 0 ? cU : cD)
        cardRow(TV, r0 + 3, cGh, "14:30", false, sq2 + "  ▲" + str.tostring(u2) + " ▼" + str.tostring(dn2), vzSg(sv2), na(av2) ? "—" : "±" + pf(av2), VZT_S2, na(sv2) ? cTx : sv2 >= 0 ? cU : cD)
        cardRow(TV, r0 + 4, cGh, "RTH", false, sq3 + "  ▲" + str.tostring(u3) + " ▼" + str.tostring(dn3), vzSg(svR), na(av3) ? "—" : "±" + pf(av3), VZT_R, na(svR) ? cTx : svR >= 0 ? cU : cD)
        cardRow(TV, r0 + 5, cGh, "NOW", false, na(nwX) ? "next FOMC " + (na(nxF) ? "—" : whenTxt(nxF, today)) : gauge(nwX) + " " + nwT, na(nwX) ? "" : x2(nwX), na(nwX) ? "" : "of avg", "Today's live displacement against the average for the same window over the last 3 years of FOMC days (full battery = an average-size move). Before 14:00: the move from 09:30 against a full FOMC RTH; 14:00–14:30 stage 1; 14:30–16:14 stage 2; after 16:14 the RTH move; the day after: NY AM against past day-after NY AMs.", na(nwX) ? cTx : nwX >= 1 ? cHot : cTx)
        cardSub(TV, r0 + 6, cGh, "2018–26 · green key = held in both halves", "FOMC", "other / exp")
        cardRow(TV, r0 + 7, cGh, "AM=S1", false, "next NY AM went with stage 1 · idx " + VZI_N1 + nN1, VZV_N1, "exp " + VZE_N1, VZT_N1)
        cardRow(TV, r0 + 8, cGh, "AM=S2", false, "next NY AM went with stage 2 · idx " + VZI_N2 + nN2, VZV_N2, "exp " + VZE_N2, VZT_N2)
        cardRow(TV, r0 + 9, cGh, "GAP", VZH_GF, "morning gap filled by 16:14" + nGF, VZV_GF, VZB_GF, VZT_GF)
        cardRow(TV, r0 + 10, cGh, "¼ +1", VZH_Q, "day after: NY AM held the open-side ¼" + nQ, VZV_Q, VZB_Q, VZT_Q)
        cardRow(TV, r0 + 11, cGh, "50% +1", VZH_CE, "day after: NY AM tapped the gap 50%" + nCE, VZV_CE, VZB_CE, VZT_CE)
        cardRow(TV, r0 + 12, cDxc, "⇄ 14:00", VZH_X1, "stage 1 other way to DXY" + nX1, VZV_X1, VZB_X1, VZT_X1)
        cardRow(TV, r0 + 13, cDxc, "⇄ 14:30", VZH_X2, "stage 2 other way to DXY" + nX2, VZV_X2, VZB_X2, VZT_X2)
        cardRow(TV, r0 + 14, cDxc, "⇄ DAY", VZH_XD, "trading day other way to DXY" + nXD, VZV_XD, VZB_XD, VZT_XD)
    if showSg and not na(TV) and mob
        int r0 = tvO
        cardHead(TV, r0, cGh, dot + " STAGES · " + symTag, "Vizard's FOMC stages, compact. Hover a row for the full read.", vzF ? "TODAY" : vzP ? "+1 DAY" : na(ddF) ? "—" : str.tostring(ddF) + "D", sgPfg, sgPbg)
        cardRow(TV, r0 + 1, cGh, "S1", false, sq1 + " " + str.tostring(u1) + "/" + str.tostring(dn1), vzSg(sv1), na(av1) ? "—" : "±" + pf(av1), VZT_S1, na(sv1) ? cTx : sv1 >= 0 ? cU : cD)
        cardRow(TV, r0 + 2, cGh, "S2", false, sq2 + " " + str.tostring(u2) + "/" + str.tostring(dn2), vzSg(sv2), na(av2) ? "—" : "±" + pf(av2), VZT_S2, na(sv2) ? cTx : sv2 >= 0 ? cU : cD)
        cardRow(TV, r0 + 3, cGh, "NOW", false, na(nwX) ? "next " + (na(nxF) ? "—" : fmtDay(nxF)) : gauge5(nwX) + " " + (vzP ? "NY AM" : mod < 840 ? "pre-14" : mod < 870 ? "S1" : mod < 975 ? "S2" : "RTH"), na(nwX) ? "" : x2(nwX), "", "Today's live displacement against the 3-year FOMC average for the same window.", na(nwX) ? cTx : nwX >= 1 ? cHot : cTx)
        cardRow(TV, r0 + 4, cGh, "AM", false, "=S1 " + VZV_N1 + " · =S2 " + VZV_N2 + (vzP ? nN1 : ""), "", "", VZT_N1 + " " + VZT_N2)
        if vzP
            cardRow(TV, r0 + 5, cGh, "¼ +1", VZH_Q, "held " + VZV_Q + " vs " + VZB_Q + nQ, "", "", VZT_Q)
        else
            cardRow(TV, r0 + 5, cGh, "GAP", VZH_GF, "fills " + VZV_GF + " vs " + VZB_GF + nGF, "", "", VZT_GF)
        string mX = vzK == calK and mod >= 840 ? (mod < 870 ? nX1 : nX2) : ""
        cardRow(TV, r0 + 6, cDxc, "DXY", VZH_X1 and VZH_X2, mX != "" ? str.replace_all(mX, " · today ", "") : "other way S1 " + VZV_X1 + " · S2 " + VZV_X2, "", "", VZT_X1 + " " + VZT_X2)
'''

# its own last-bar block (Pine caps the size of a single if block)
CARD_BLOCK = """if barstate.islast
    int    today = calK
    string dot   = barstate.isrealtime ? (beat % 2 == 0 ? "●" : "○") : "◆"
""" + CARD.lstrip('\n')
