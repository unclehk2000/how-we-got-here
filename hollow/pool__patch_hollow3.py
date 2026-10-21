"""Hollow v3: NQ + ES + RTY pooled data, RTY clock and tally, structure settings, anchored event flags, a compact stages
card led by the month's zone, and Shirosaki (the HYDRA findings pane). Reads Hollow_v2_src.pine."""
import json, re
S = open('/home/claude/hol/Hollow_v2_src.pine', encoding='utf-8').read()
POOL = open('/home/claude/hol/pool/hollow_pool.pine', encoding='utf-8').read()
# the tooltips' shared opening lines, once each
PW_ = "NQ + ES + RTY pooled, 329 NFP-week Mon–Thu 2018–26 (970 symbol-days), read at 09:29. "
PF_ = "NQ + ES + RTY pooled, 67 days after FOMC 2018–26 (196 symbol-days), read at 09:29. "
PD_ = "Index against DXY futures in the same window, Feb 2023 – Jul 2026, NQ + ES + RTY pooled. "
nP = POOL.count('"' + PW_), POOL.count('"' + PF_), POOL.count('"' + PD_)
POOL = POOL.replace('"' + PW_, 'PW + "').replace('"' + PF_, 'PF + "').replace('"' + PD_, 'PD + "')
POOL = 'var string PW = "' + PW_ + '"\nvar string PF = "' + PF_ + '"\nvar string PD = "' + PD_ + '"\n' + POOL
print('prefixes', nP)
assert POOL.count('"FOMC day\'s RTH high and low, carried into the next day.') == 1
POOL = POOL.replace('"FOMC day\'s RTH high and low, carried into the next day.', '"The FOMC day\'s high and low (its 18:00–17:00 session), carried into the next day.')
R = json.load(open('/home/claude/hol/rty/rty_hollow.json'))
POS8 = '["Top left", "Top center", "Top right", "Middle left", "Middle right", "Bottom left", "Bottom center", "Bottom right"]'
def rep(o, n, c=1):
    global S
    k = S.count(o); assert k == c, (k, o[:140]); S = S.replace(o, n)
def cut(a, b, new):
    global S
    i = S.index(a); j = S.index(b, i); S = S[:i] + new + S[j:]

# ── header
cut('// Hollow · Models 11–12', 'indicator("Hollow"', '''// Hollow · Models 11–12: Monday–Thursday of NFP week (11 Hollow) and the day after FOMC (12 Full Bringer).
// On the price chart: the NFP week's opening gap (the prior week's last close, Sunday's open and its midpoint) drawn to
// the release, the 16:15–17:00 settlement window, the FOMC day's RTH high and low carried into the next day, the RTH gap
// (prior 16:14 close and its 50%) and, the day after FOMC, that gap in eighths over NY AM with the open-side quarter
// shaded; NFP and FOMC flags tied to their opens. Two cards, each in its own corner: the day-after-FOMC tally and the
// stages card, which reads whichever of the two days is current or next, led by where price sits in the month's range.
// Indicator pane: the event clock, and Shirosaki, the HYDRA findings table: what held for today's setup, in points at
// today's ADR20.
// Built for NQ / MNQ, ES / MES and RTY / M2K. The stages card and Shirosaki are pooled across NQ, ES and RTY 1-minute
// data, Jan 2018 – Oct 2026 (329 NFP weeks, 67 days after FOMC); the clock and tally use the chart's own symbol. A green
// key (✓) held: p < 0.05 with errors clustered by date, the same side in 2018–24 and 2025–26 and on each symbol.
// Release dates were checked against the BLS and Federal Reserve schedules and are loaded to Dec 2027; update once a year.
// Clock after Kyōka Suigetsu. Written from scratch.
// Concepts: ICT (Michael J. Huddleston).

''')

# ── inputs
rep('''paneI   = input.string("Event clock", "Pane", options = ["Event clock", "Cards only"], group = grpW, tooltip = "What the indicator pane shows. Event clock: today's running range (or net move) against NFP-week days or the day after FOMC at the same time of day. Cards only: an empty pane for the cards you place there.", display = display.none)''',
    '''paneI   = input.string("Clock + Shirosaki", "Pane", options = ["Clock + Shirosaki", "Event clock", "Shirosaki", "Cards only"], group = grpW, tooltip = "What the indicator pane shows. Event clock: today's running range (or net move) against NFP-week days or the day after FOMC at the same time of day. Shirosaki: the HYDRA findings table for today's setup. Cards only: neither (the clock card stays where you put it).", display = display.none)''')
cut('cLvl    = input.color(#ffb300, "Levels"', '\ngrpK = "Event clock', f'''cLvl    = input.color(#ffb300, "Levels", group = grpS, inline = "s1", display = display.none)
cGh     = input.color(#26a69a, "Model", group = grpS, inline = "s1", display = display.none)
lblI    = input.string("Tiny", "Labels", options = ["Tiny", "Small", "Normal"], group = grpS, inline = "s1", display = display.none)
offI    = 12
showNW  = input.bool(true, "NFP week's opening gap", group = grpS, inline = "n0", display = display.none)
cNW     = input.color(#ffb300, "", group = grpS, inline = "n0", display = display.none)
stNW    = input.string("Dashed", "", options = ["Solid", "Dashed", "Dotted"], group = grpS, inline = "n0", tooltip = "The prior week's last close and Sunday's 18:00 open (dotted), with the midpoint, drawn to the NFP release.", display = display.none)
showFH  = input.bool(true, "FOMC high / low the day after", group = grpS, inline = "f0", display = display.none)
cFH     = input.color(#ffb300, "", group = grpS, inline = "f0", display = display.none)
stFH    = input.string("Dashed", "", options = ["Solid", "Dashed", "Dotted"], group = grpS, inline = "f0", tooltip = "The FOMC day's high and low (its 18:00–17:00 session), carried through the next day to 16:14. Shirosaki's FH / FL rows are how often the next RTH took them.", display = display.none)
showOct = input.bool(true, "Day after FOMC: gap octants over NY AM", group = grpS, inline = "s3", tooltip = "The day after FOMC: its RTH gap (FOMC day's 16:14 close → 09:30 open) in eighths from 09:30 to 11:00, the 50% line bold and the quarter next to the open shaded.", display = display.none)
cOq     = input.color(color.new(#26a69a, 78), "", group = grpS, inline = "s3", display = display.none)
showSet = input.bool(true, "NFP week: settlement window 16:15–17:00", group = grpS, inline = "w0", display = display.none)
cWin    = input.color(color.new(#2962ff, 90), "", group = grpS, inline = "w0", display = display.none)
showWO  = input.bool(true, "Week open", group = grpS, inline = "o0", display = display.none)
showGap = input.bool(true, "RTH gap", group = grpS, inline = "o0", tooltip = "The week's open (Sunday 18:00), carried right of price. RTH gap: the prior 16:14 close and the gap's 50% on Hollow days, from 09:30.", display = display.none)
''')
rep('grpK = "Event clock (indicator pane)"\nclkOn  = paneI == "Event clock"', 'grpK = "Event clock (indicator pane)"\nclkOn  = paneI == "Clock + Shirosaki" or paneI == "Event clock"')
rep('''sgPos   = input.string("Bottom left", "", options = ''' + POS8 + ''', group = grpV, inline = "v0", display = display.none)''',
    '''sgPos   = input.string("Bottom left", "", options = ''' + POS8 + ''', group = grpV, inline = "v0", display = display.none)
grpH    = "Shirosaki: HYDRA findings (indicator pane)"
showSh  = paneI == "Clock + Shirosaki" or paneI == "Shirosaki"
shPos   = input.string("Top left", "Position", options = ''' + POS8 + ''', group = grpH, inline = "h0", tooltip = "Shirosaki lists what held on pooled NQ + ES + RTY days for today's setup (NFP week Monday–Thursday or the day after FOMC), in points at today's ADR20, with the gap events live. Make the pane taller to fit it.", display = display.none)
cSh     = input.color(#546e7a, "Accent", group = grpH, inline = "h0", display = display.none)''')

# ── symbols, RTY clock and tally
rep('''bool isNQ  = syminfo.root == "NQ" or syminfo.root == "MNQ"
string symR   = isES ? "ES" : "NQ"                           // whose statistics the cards show
string symTag = isNQ or isES ? syminfo.root : syminfo.root + " (" + symR + " DATA)"''', '''bool isNQ  = syminfo.root == "NQ" or syminfo.root == "MNQ"
bool isRTY = syminfo.root == "RTY" or syminfo.root == "M2K"
string symR   = isES ? "ES" : isRTY ? "RTY" : "NQ"           // whose clock and tally the chart shows
string symTag = isNQ or isES or isRTY ? syminfo.root : syminfo.root + " (" + symR + " DATA)"''')
i = S.index('\nint  AN    ='); S = S[:i] + '\n' + '\n'.join(R['ck']) + S[i:]
rep('var array<float> CK = unpackMilli(isES ? CK_ES : CK_NQ)', 'var array<float> CK = unpackMilli(isES ? CK_ES : isRTY ? CK_RTY : CK_NQ)')
rep('TAL_END_ES = 20260828\n', 'TAL_END_ES = 20260828\n' + '\n'.join(R['tal']) + '\n' + R['end'] + '\n')
rep('''ckN(int k, bool es) =>
    switch k
        0 => es ? "324" : "323"
        1 => es ? "67" : "67"
        2 => es ? "1416" : "1342"''', f'''ckN(int k) =>
    switch k
        0 => isES ? "324" : isRTY ? "{R['n']['5']}" : "323"
        1 => isRTY ? "{R['n']['3']}" : "67"
        2 => isES ? "1416" : isRTY ? "{R['n']['6']}" : "1342"''')
rep('ckN(ckI, isES)', 'ckN(ckI)'); rep('ckN(NCK - 1, isES)', 'ckN(NCK - 1)')
rep('int  talEnd = isES ? TAL_END_ES : isNQ ? TAL_END_NQ : 0', 'int  talEnd = isES ? TAL_END_ES : isRTY ? TAL_END_RTY : isNQ ? TAL_END_NQ : 0')
rep('string src = isES ? TAL_ES : isNQ ? TAL_NQ : ""', 'string src = isES ? TAL_ES : isRTY ? TAL_RTY : isNQ ? TAL_NQ : ""')
rep('(built-in history covers NQ / MNQ and ES / MES).', '(built-in history covers NQ / MNQ, ES / MES and RTY / M2K).')
rep('''string hdT  = pfName(pk) + ". Recomputed on " + symR + " 1-minute data 2018–26." + (isNQ or isES ? "" : " This chart is " + syminfo.root + ": the figures are " + symR + "'s.")''',
    '''string hdT  = pfName(pk) + ". Clock and tally: " + symR + " 1-minute data 2018–26; stages card and Shirosaki: NQ + ES + RTY pooled." + (isNQ or isES or isRTY ? "" : " This chart is " + syminfo.root + ": the clock and tally are " + symR + "'s.")''')
rep('str.upper("Vizard") + " · CLOCK · "', '"HOLLOW · CLOCK · "')

# ── data: pooled numbers and tooltips
cut('// The stages card\'s statistics (HYDRA calendar study', 'bool hwF = ', '''// The stages card's and Shirosaki's statistics: NQ + ES + RTY pooled (329 NFP weeks, 67 days after FOMC), read at 09:29,
// in ADR20 of the trading day; −1 = too few days. Groups run up / middle / down in the order the code names them.
// NFP week 0–57: |NY AM|, RTH range, settlement range, next day's range by the month's position (median, 80th) · 24–41
//   new high / low after 09:30 by prior day, overnight, month · 42–47 RTH range by month's open, VIX · 48–53 gap 50% by
//   10:00, then filled by 16:14, by gap · 54–57 gap 50% by 10:00, Mon–Thu
// Day after FOMC 58–102: |NY AM|, RTH, next day by month · 76–87 new high / low by the FOMC day's range, overnight · 88–93
//   took the FOMC high / low by month · 94–96 RTH range by VIX · 97–102 gap filled, then its 50% in NY AM, by gap
// 103–123 NFP week: open-side ¼ held NY AM and gap 50% in NY AM by gap · new high / low by gap · RTH range by prior day,
//   overnight, gap · 124–154 day after: FOMC high / low by the FOMC afternoon, by gap, by the FOMC close · new high / low
//   by gap, by month · ¼ held by gap · 155–169 base rates of all such days
// VH: 1 where that figure held.
''' + POOL + '''vh(int i) => str.substring(VH, i, i + 1) == "1"
var string VZT_HD = "Hollow reads two days at the RTH open (09:29): Monday–Thursday of NFP week (Model 11) and the day after FOMC (Model 12, Full Bringer), led by where price sits in the month's range. SETUP: the month, its open, the prior day (the FOMC day's own range the day after), the overnight, the RTH gap and VIX (live, then fixed at 09:29). EXPECT: how far such days moved, at today's ADR20. LIVE (after 09:30): NY AM and RTH against DXY, the gap and the range since 09:30. Figures pooled from NQ, ES and RTY. Green key = held. No 09:29 feature called the day's direction."
VZT_LV = "Today so far (points from the 09:30 open) and DXY's move in the same window, in DXY's ADR20. ×typ = against the EXPECT median. ⇄ = the other way to DXY, ⇉ = the same way. BIG = DXY's move reached the size where the other-way rate applies (NFP week: 0.19 in NY AM, 0.26 over RTH; day after FOMC: 0.52 over RTH)."
VZT_SHW = "Shirosaki · NFP week. HYDRA on NQ + ES + RTY pooled (773 training rows on 258 days 2018–24, errors clustered by date; 406 heads × 15 targets; 20 shifted-target nulls; locked 2025–26 test (197 rows on 71 days) plus the same sign on each symbol). Direction: NY AM up, RTH up and the settlement window had no more survivors than their nulls (10 / 4 / 0 vs null means 14 / 19 / 4), and the whole net scored AUC 0.52–0.56 on 2025–26. Group tests: 3 of 44 direction tests passed the ✓ rule, about what chance gives with this many tries. SIDE shows the one that leans 60 / 40 or more: after an overnight up more than 0.4 ADR, RTH closed up 69% vs 54% (2018–24 70% vs 52%, 2025–26 65% vs 61%; NQ 73 · ES 66 · RTY 68; p 0.014; n 122 on 60 days). The other two are near a coin flip: NY AM up 56% vs 48% from the month's middle; RTH up 53% vs 64% after a flat overnight. What held: the gap (filled 33 heads, 50% by 10:00 30, in NY AM 30, open-side quarter 29), the RTH range 37, the next day 33, new high 29 and low 31 after 09:30, |NY AM| 12, the settlement range 11."
VZT_SHF = "Shirosaki · day after FOMC. HYDRA on NQ + ES + RTY pooled (159 training rows on 53 days 2018–24; 413 heads × 15 targets; locked 2025–26 test on 37 rows / 14 days plus each symbol). Direction: NY AM up had 0 survivors and RTH up 8 against a null maximum of 30; no direction head held in 2025–26. The whole net beat its null on NY AM up (AUC 0.71) and on NY AM going the stage-2 way (0.76), but on 14 days and with no single head behind it: unconfirmed. Group tests: 2 of 46 direction tests passed the ✓ rule, about what chance gives. SIDE shows the one that leans 60 / 40 or more: with VIX within 10% of its 20-day average, NY AM went down 64% vs 42% (2018–24 67% vs 40%, 2025–26 55% vs 53%, barely; NQ 63 · ES 63 · RTY 67; p 0.039; n 106 on 36 days). The other: inside the FOMC day's range at 09:29, NY AM up 54% vs 34%, near a coin flip. What held: RTH taking the FOMC high (31 heads) and low (15), new high after 09:30 (16), the gap fill (9) and its 50% in NY AM (4)."
''')
rep('''bool hwF = hollowDay(calK) and not FO.includes(tdPK)''', '''bool hwF = hollowDay(calK) and not FO.includes(tdPK)''')
# the open-side quarter is tracked on both days (Shirosaki), the octants are still drawn only the day after
rep('    if faF and na(qbT) and mod < 660 and (g_ > 0 ? low <= gapPC + 0.75 * g_ : high >= gapPC + 0.75 * g_)', '    if na(qbT) and mod < 660 and (g_ > 0 ? low <= gapPC + 0.75 * g_ : high >= gapPC + 0.75 * g_)')
rep('SGR = layI == "Mobile" ? 7 : 19', 'SGR = layI == "Mobile" ? 5 : 12')
rep('''    TV.merge_cells(1, tvO, 3, tvO)
''', '''    TV.merge_cells(1, tvO, 3, tvO)
// Shirosaki's table (indicator pane)
var table TH  = na
var int   thO = 0
HYR = layI == "Mobile" ? 6 : 11
if barstate.isfirst and showSh
    thO := str.startswith(shPos, "Top") ? 1 : 0
    TH  := table.new(posOf(shPos), 5, HYR + thO, bgcolor = #00000000, frame_width = 0, border_width = 0)
    if thO == 1
        TH.cell(0, 0, "", height = 7.0, bgcolor = #00000000)
        TH.merge_cells(0, 0, 4, 0)
    TH.merge_cells(1, thO, 3, thO)
    if layI != "Mobile"
        TH.merge_cells(2, thO + 2, 4, thO + 2)
''')
rep('bool  ckTop = showCk and ckOn == "Indicator pane" and str.startswith(ckPos, "Top")', 'bool  ckTop = (showCk and ckOn == "Indicator pane" and str.startswith(ckPos, "Top")) or (showSh and str.startswith(shPos, "Top"))')

# ── model structure on the price chart
cut('// ═══════════════════════════════════════════════════════════════ Model structure on the price chart', '// the day after FOMC: the RTH gap in eighths over NY AM', '''// ═══════════════════════════════════════════════════════════════ Model structure on the price chart
bool hOn = showStr and recent
var int   tdTy = 6
var int   ptdK = na
var float nwC  = na
var float nwO  = na
if tdSt
    tdTy := dayType(tdK, ptdK)
    if na(ptdK) or dowOf(tdK) <= dowOf(nz(ptdK, tdK))
        nwC := close[1]
        nwO := open
        int nfpK = na
        for j = 0 to 4
            if NP.includes(addDays(tdK, j)) and na(nfpK)
                nfpK := addDays(tdK, j)
        if hOn and showNW and not na(nfpK) and not na(nwC)
            int te = keyAt(nfpK, 510)
            float ce = (nwC + nwO) / 2
            trimL(line.new(time, nwC, te, nwC, xloc = xloc.bar_time, color = color.new(cNW, 40), style = line.style_dotted, force_overlay = true), te)
            trimL(line.new(time, nwO, te, nwO, xloc = xloc.bar_time, color = color.new(cNW, 40), style = line.style_dotted, force_overlay = true), te)
            trimL(line.new(time, ce, te, ce, xloc = xloc.bar_time, color = cNW, style = lsOf(stNW), force_overlay = true), te)
            trimT(label.new(te, ce, "NWOG 50%", xloc = xloc.bar_time, color = #00000000, textcolor = cNW, style = label.style_label_left, size = lbSz, tooltip = VZT_NW, force_overlay = true), te)
    if hOn and showFH and FO.includes(ptdK) and not na(ptdH)
        trimL(line.new(time, ptdH, keyAt(tdK, 974), ptdH, xloc = xloc.bar_time, color = cFH, style = lsOf(stFH), force_overlay = true), keyAt(tdK, 974))
        trimL(line.new(time, ptdL, keyAt(tdK, 974), ptdL, xloc = xloc.bar_time, color = cFH, style = lsOf(stFH), force_overlay = true), keyAt(tdK, 974))
        trimT(label.new(keyAt(tdK, 974), ptdH, "FOMC high", xloc = xloc.bar_time, color = #00000000, textcolor = cFH, style = label.style_label_left, size = lbSz, tooltip = VZT_FH, force_overlay = true), keyAt(tdK, 974))
        trimT(label.new(keyAt(tdK, 974), ptdL, "FOMC low", xloc = xloc.bar_time, color = #00000000, textcolor = cFH, style = label.style_label_left, size = lbSz, tooltip = VZT_FH, force_overlay = true), keyAt(tdK, 974))
    ptdK := tdK
if hOn and showGap and (tdTy == 5 or tdTy == 3) and rthSt and not na(gapPC)
    trimL(line.new(time, gapPC, keyAt(calK, 974), gapPC, xloc = xloc.bar_time, color = color.new(cLvl, 40), style = line.style_dotted, force_overlay = true), keyAt(calK, 974))
    trimL(line.new(time, gapCE, keyAt(calK, 974), gapCE, xloc = xloc.bar_time, color = color.new(cLvl, 20), style = line.style_dotted, force_overlay = true), keyAt(calK, 974))
    trimT(label.new(keyAt(calK, 974), gapCE, "gap 50%", xloc = xloc.bar_time, color = #00000000, textcolor = cLvl, style = label.style_label_left, size = lbSz, tooltip = "RTH gap 50% = (prior 16:14 close + 09:30 open) ÷ 2. " + (tdTy == 3 ? VZT_FGP : VZT_WGP), force_overlay = true), keyAt(calK, 974))
// the event flags: above the bar's high, tied by a stem to its open; they rise with price for half an hour
var int   mkK = na
var int   mkE = 0
var label mkL = na
var line  mkV = na
bool mkN = NP.includes(calK) and mod <= 510 and mod + tfM > 510
bool mkF = FO.includes(calK) and mod <= 840 and mod + tfM > 840
if hOn and markEv and (mkN or mkF)
    float yT = high + 0.3 * nz(ADRtd * tdO, 4 * (high - low))
    mkK := calK
    mkE := mkN ? 540 : 870
    mkV := line.new(time, open, time, yT, xloc = xloc.bar_time, color = color.new(cGh, 25), style = line.style_dotted, force_overlay = true)
    mkL := label.new(time, yT, (mkN ? "NFP 08:30 · " : "FOMC 14:00 · ") + pf(open), xloc = xloc.bar_time, color = cGh, textcolor = #ffffff, style = label.style_label_down, size = lbSz == size.tiny ? size.small : lbSz, tooltip = mkN ? "NFP release, 08:30 ET: the end of the Hollow week. The stem runs to the 08:30 open." : "FOMC statement, 14:00 ET: tomorrow is a Full Bringer day (Model 12). The stem runs to the 14:00 open.", force_overlay = true)
else if mkK == calK and mod < mkE and high + 0.3 * nz(ADRtd * tdO) > mkL.get_y()
    mkL.set_y(high + 0.3 * nz(ADRtd * tdO))
    mkV.set_y2(high + 0.3 * nz(ADRtd * tdO))
bgcolor(hOn and showSet and tdTy == 5 and mod >= 975 and mod < 1020 ? cWin : na, title = "Settlement window 16:15–17:00", force_overlay = true)

''')
rep('''    trimT(label.new(te, gapPC + gp * 0.875, "open-side ¼", xloc = xloc.bar_time, color = #00000000, textcolor = color.new(cOq, 0), style = label.style_label_left, size = size.tiny, tooltip = VZT_Q, force_overlay = true), te)''',
    '''    trimT(label.new(te, gapPC + gp * 0.875, "open-side ¼", xloc = xloc.bar_time, color = #00000000, textcolor = color.new(cOq, 0), style = label.style_label_left, size = lbSz, tooltip = VZT_Q, force_overlay = true), te)''')
rep('''RT.push(label.new(bar_index + 2, wkOp, "week open " + pf(wkOp), color = #00000000, textcolor = cLvl, style = label.style_label_left, size = size.tiny, force_overlay = true))''',
    '''RT.push(label.new(bar_index + 2, wkOp, "week open " + pf(wkOp), color = #00000000, textcolor = cLvl, style = label.style_label_left, size = lbSz, force_overlay = true))''')
# helpers for the new inputs
rep('crdSz = crdSzI == "Tiny" ? size.tiny : crdSzI == "Small" ? size.small : size.normal', '''crdSz = crdSzI == "Tiny" ? size.tiny : crdSzI == "Small" ? size.small : size.normal
lbSz  = lblI == "Small" ? size.small : lblI == "Normal" ? size.normal : size.tiny
lsOf(string s) => s == "Solid" ? line.style_solid : s == "Dotted" ? line.style_dotted : line.style_dashed''')

rep('tooltip = "Reads the current or next Hollow day: NFP week Monday–Thursday or the day after FOMC. SETUP: where price stands at 09:29 against the month, its open, the prior day (the FOMC day\'s range the day after), the overnight and the RTH gap, and VIX (live, then fixed at 09:29). EXPECT: how far such days moved in NY AM, RTH, the settlement window and the next day, at today\'s ADR20. LIVE: NY AM and RTH against DXY, the gap\'s 50%, and the day after FOMC the open-side quarter. Needs a chart of 30 minutes or less for the live rows."',
    'tooltip = "Reads the current or next Hollow day: NFP week Monday–Thursday or the day after FOMC. The header pill is where price sits in the month\'s range (discount = bottom quarter, premium = top quarter), the setup that sized these days most. SETUP (live, then fixed at 09:29): the month, its open (NFP week) or the FOMC afternoon (the day after), the prior day (the FOMC day\'s range the day after), the overnight, the RTH gap and VIX. EXPECT (before 09:30): how far such days moved, at today\'s ADR20. LIVE (after 09:30): NY AM and RTH against DXY, the range since 09:30, the gap\'s 50% and fill. Pooled from NQ, ES and RTY. Needs a chart of 30 minutes or less for the live rows."')
# the clock's busiest half hour: skip the first, which holds the opening range itself
rep("""            float bestD = -1.0
            int   bestJ = 0
            for j = 0 to 45""", """            float bestD = -1.0
            int   bestJ = 1
            for j = 1 to 45""")
# ── stages card and Shirosaki
cut('// ═══════════════════════════════════════════════════════════════ Hollow stages card (last bar)', '// ═══ Write the queued card cells', open('/home/claude/hol/pool/hollow_cards.pine', encoding='utf-8').read())
for gone in ('VZV_WR', 'VZT_WMON = isES', 'isES ? TAL_ES : isNQ', 'str.upper("Vizard")'):
    assert gone not in S, gone
# long tooltips: one runtime array instead of a constant folded into every use (CE10117, 137k tokens before)
import sys as _sys
_sys.path.insert(0, '/home/claude/pinetools')
import pine_tips, pine_size
_sys.path.insert(0, '/home/claude/hm')
import patch_adr_fallback
S = patch_adr_fallback.patch(S)
S = pine_tips.convert(S)
open('/home/claude/hol/Hollow.pine', 'w', encoding='utf-8').write(S)
print('written', len(S.split('\n')), 'lines')
pine_size.report('/home/claude/hol/Hollow.pine')
