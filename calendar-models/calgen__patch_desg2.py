"""Desgarrón v2: live dealing range, ATH and its 08:30 CE, compact stages card led by the month's premium / discount,
HYDRA findings pane, NQ + ES + RTY pooled data, RTY clock and tally. Reads backups_1013/Desgarron_v1.pine."""
import re
S = open('/home/claude/hm/backups_1013/Desgarron_v1.pine', encoding='utf-8').read()
POOL = open('/home/claude/hm/calgen/frag/desg_pool.pine', encoding='utf-8').read()
def rep(old, new, n=1):
    global S
    c = S.count(old)
    assert c == n, (c, old[:120])
    S = S.replace(old, new)
def cut(a, b, new=''):
    """replace from the line starting with a up to (not including) the line starting with b"""
    global S
    i = S.index(a); j = S.index(b, i)
    S = S[:i] + new + S[j:]

# ── header
cut('// Desgarrón (豹王の爪)', 'indicator("Desgarrón"', '''// Desgarrón (豹王の爪) · Model 6: NFP days (Employment Situation, released 08:30 ET). Grimmjow's tearing claws: the
// release that tears into whoever is already positioned, Model 6's disruption idea.
// On the price chart: the 07:00–09:00 dealing range (drawn live from 07:00), the 08:30–08:45 hands-off window, the 08:50
// line, the RTH gap (prior 16:14 close and its 50%), the 08:30 and 08:50 opens, the all-time high carried right of price
// and, from 08:30, the consequent encroachment between the ATH and the 08:29 close to 17:00. Two cards: the NFP tally and
// the NFP stages card, led by where price sits in the month's range (discount / middle / premium).
// Indicator pane: the event clock (today's running range against NFP days) and the HYDRA findings table: what held for
// today's setup, in points at today's ADR20.
// Built for NQ / MNQ, ES / MES and RTY / M2K. The stages card and the findings are pooled across NQ, ES and RTY 1-minute
// data, Jan 2018 – Oct 2026 (293 symbol-days on 99 releases); the clock and tally use the chart's own symbol. A green key
// (✓) held: p < 0.05 with errors clustered by release date, the same side in 2018–24 and 2025–26 and on each symbol.
// Release dates were checked against the BLS and Federal Reserve schedules and are loaded to Dec 2027; update once a year.
// Clock after Kyōka Suigetsu. Written from scratch.
// Concepts: ICT (Michael J. Huddleston).

''')

# ── inputs
rep('''showWO  = input.bool(true, "Week open, 08:30 and 08:50 opens", group = grpS, tooltip = "The week's open (Sunday 18:00) and, on NFP days, the open of the 08:30 and 08:50 candles, each extended to the right of price.", display = display.none)''',
    '''showWO  = input.bool(true, "Week open, 08:30 and 08:50 opens", group = grpS, tooltip = "The week's open (Sunday 18:00) and, on NFP days, the open of the 08:30 and 08:50 candles, each extended to the right of price.", display = display.none)
showATH = input.bool(true, "ATH and its 08:30 CE", group = grpS, inline = "s2", display = display.none)
cAth    = input.color(#ab47bc, "", group = grpS, inline = "s2", tooltip = "The all-time high, drawn from the day it was set and carried right of price. On NFP days at 08:30: the consequent encroachment (50%) between the ATH and the 08:29 close, carried to 17:00; its tooltip gives how often pooled NFP days touched it at that distance.", display = display.none)''')
rep('''sgPos   = input.string("Bottom left", "", options = ["Top left", "Top center", "Top right", "Middle left", "Middle right", "Bottom left", "Bottom center", "Bottom right"], group = grpV, inline = "v0", display = display.none)''',
    '''sgPos   = input.string("Bottom left", "", options = ["Top left", "Top center", "Top right", "Middle left", "Middle right", "Bottom left", "Bottom center", "Bottom right"], group = grpV, inline = "v0", display = display.none)
grpH    = "HYDRA findings (indicator pane, beside the clock)"
showHy  = input.bool(true, "Findings", group = grpH, inline = "h0", display = display.none)
hyPos   = input.string("Top left", "", options = ["Top left", "Top center", "Top right", "Middle left", "Middle right", "Bottom left", "Bottom center", "Bottom right"], group = grpH, inline = "h0", tooltip = "What held on NFP days (NQ + ES + RTY pooled, 2018–26) for today's setup, in points at today's ADR20: the range after 08:30, whether the other size groups agree, which extreme the day is likely to make, the ATH CE odds, the first side of the pre-release range, the DXY rules for stages 1 and 2 and the 08:30–09:00 expansion. A green key = held. Shares the pane with the event clock.", display = display.none)
cHy     = input.color(#5e35b1, "Accent", group = grpH, inline = "h0", display = display.none)''')

# ── symbols, pooled data, RTY clock and tally
rep('''bool isNQ  = syminfo.root == "NQ" or syminfo.root == "MNQ"
string symR   = isES ? "ES" : "NQ"                           // whose statistics the cards show
string symTag = isNQ or isES ? syminfo.root : syminfo.root + " (" + symR + " DATA)"''',
    '''bool isNQ  = syminfo.root == "NQ" or syminfo.root == "MNQ"
bool isRTY = syminfo.root == "RTY" or syminfo.root == "M2K"
string symR   = isES ? "ES" : isRTY ? "RTY" : "NQ"           // whose clock and tally the chart shows
string symTag = isNQ or isES or isRTY ? syminfo.root : syminfo.root + " (" + symR + " DATA)"''')
rep('''var array<int>   FO = parseDates(S_FOMC)''', POOL + '''
var array<int>   FO = parseDates(S_FOMC)''')
rep('var array<float> CK = unpackMilli(isES ? CK_ES : CK_NQ)', 'var array<float> CK = unpackMilli(isES ? CK_ES : isRTY ? CK_RTY : CK_NQ)')
rep('''ckN(int k, bool es) =>
    switch k
        0 => es ? "98" : "98"
        1 => es ? "1416" : "1342"
        => ""''', '''ckN(int k) =>
    switch k
        0 => isRTY ? "100" : "98"
        1 => isES ? "1416" : isRTY ? "1430" : "1342"
        => ""''')
rep('ckN(ckI, isES)', 'ckN(ckI)')
rep('ckN(NCK - 1, isES)', 'ckN(NCK - 1)')
rep('int  talEnd = isES ? TAL_END_ES : isNQ ? TAL_END_NQ : 0', 'int  talEnd = isES ? TAL_END_ES : isRTY ? TAL_END_RTY : isNQ ? TAL_END_NQ : 0')
rep('string src = isES ? TAL_ES : isNQ ? TAL_NQ : ""', 'string src = isES ? TAL_ES : isRTY ? TAL_RTY : isNQ ? TAL_NQ : ""')
rep('(built-in history covers NQ / MNQ and ES / MES).', '(built-in history covers NQ / MNQ, ES / MES and RTY / M2K).')
rep('''string hdT  = pfName(pk) + ". Recomputed on " + symR + " 1-minute data 2018–26." + (isNQ or isES ? "" : " This chart is " + syminfo.root + ": the figures are " + symR + "'s.")''',
    '''string hdT  = pfName(pk) + ". Clock and tally: " + symR + " 1-minute data 2018–26; stages card and findings: NQ + ES + RTY pooled." + (isNQ or isES or isRTY ? "" : " This chart is " + syminfo.root + ": the clock and tally are " + symR + "'s.")''')
rep('str.upper("Vizard") + " · CLOCK · "', '"DESGARRÓN · CLOCK · "')
rep('NFP days filled the full gap less often than normal days (" + (isES ? "53% vs 62%" : "54% vs 63%") + ").', 'NFP days filled the full gap less often than normal days (NQ 54% vs 63%, ES 53% vs 62%).')

# ── ATH: highest daily high before today and the day it was set; today's high and its time
rep('''[dxA, dx20] = request.security(dxySym, "D", [ta.sma(high - low, 20)[1], close[20]], lookahead = barmerge.lookahead_on, ignore_invalid_symbol = true)''',
    '''[dxA, dx20] = request.security(dxySym, "D", [ta.sma(high - low, 20)[1], close[20]], lookahead = barmerge.lookahead_on, ignore_invalid_symbol = true)
// all-time high: the highest daily high of the completed days and the day it was set (today's high is added on the chart)
athD() =>
    float m = ta.max(high)
    var int t = na
    if high >= m
        t := time
    [m[1], t[1]]
[athP, athPT] = request.security(syminfo.tickerid, "D", athD(), lookahead = barmerge.lookahead_on)''')
rep('''var int   tdX  = na
var int   tdPK = na
if tdSt
    tdPK := tdK[1]
    ptdH := tdH
    ptdL := tdL
    tdO  := open
    tdH  := high
    tdL  := low
    tdX  := bar_index
else
    tdH := math.max(nz(tdH, high), high)
    tdL := math.min(nz(tdL, low), low)''', '''var int   tdX  = na
var int   tdPK = na
var int   tdHT = na
if tdSt
    tdPK := tdK[1]
    ptdH := tdH
    ptdL := tdL
    tdO  := open
    tdH  := high
    tdL  := low
    tdX  := bar_index
    tdHT := time
else
    if na(tdH) or high > tdH
        tdHT := time
    tdH := math.max(nz(tdH, high), high)
    tdL := math.min(nz(tdL, low), low)
bool  athTd = na(athP) or tdH >= athP
float athN  = athTd ? tdH : athP
int   athNT = athTd ? tdHT : athPT''')

# ── stages section: old per-symbol data out, pooled tooltips in
cut('// The stages card\'s statistics (HYDRA calendar study', 'vh(int i) =>', '''// The stages card's statistics (VS, VH, OC and the tooltips above): NQ + ES + RTY pooled, read at 08:29, in ADR20 of the
// trading day; −1 = too few days
//  0–29  |stage 1|, |stage 2|, |NY AM|, the range after 08:30, the next session's range: median and 80th percentile with
//        price in the month's discount (bottom quarter), middle, premium (top quarter)
//  30–35 new day high and low after 08:30 (%): above PDH, inside the prior day, below PDL
//  36–41 the same after a move since 18:00 above +0.4 ADR, within ±0.4, below −0.4
//  42–47 the same in the month's discount, middle, premium
//  48–56 the range after 08:30 (ADR): over / within / under 1 ADR from the month's open · VIX over / near / under its
//        20-day average (±10%) · the week into the release up / flat / down (±0.5 ADR)
// VH: 1 where that figure held. OC: per month octant 1–8, n · range after 08:30 · new high % · new low %
''')
cut('var string VZT_HD = ', 'bool vzF = NP.includes(calK)', '''var string VZT_HD = "The NFP release (08:30 ET), led by where price sits in the month's range: discount (bottom quarter), middle or premium (top quarter), the setup that sized NFP days most. SETUP: the month, its open, the prior day, the 18:00 open, the week into the release and VIX (live, then fixed at 08:29). EXPECT: how far NFP days with today's month position moved, at today's ADR20. LIVE (from 08:30): stages 1 and 2 against DXY and the range since 08:30. Figures: NQ + ES + RTY pooled, 2018–26 (293 symbol-days, 99 releases). Green key = held; every other figure describes. No 08:29 feature called the direction."
VZT_LV = "Today's stage so far (points from its open) and DXY's move in the same window, in DXY's ADR20. ×typ = against the EXPECT median. ⇄ = the other way to DXY, ⇉ = the same way. BIG = DXY has moved at least 0.42 (stage 1) or 0.22 (stage 2) of its ADR20, about its median release move: then the index went the other way 82% and 71% of the time (pooled, held). RANGE: the range since 08:30 against the median for today's month position."
VZT_MN = "ES, held: the next session's RTH (09:30 → 16:14, usually Monday) closed the same way as NFP day's RTH on 36% of 97 NFP days vs 48% after ordinary days (2018–24 35%, 2025–26 41%; p 0.025). Expect the Monday to undo, not extend."
''')

# pre-release range, first side, range since 08:30, ATH CE
rep('''bool at830 = vzF and tfM <= 30''', '''// pre-release range 07:00–08:29, the first side of it taken after 08:30, the range since 08:30, and the ATH CE fixed at 08:30
var int   p7K  = na
var float p7H  = na
var float p7L  = na
if vzF and mod >= 420 and mod < 510
    if p7K != calK
        p7K := calK
        p7H := high
        p7L := low
    else
        p7H := math.max(p7H, high)
        p7L := math.min(p7L, low)
var int   fsd  = 0                                                      // 1 high first · −1 low first · 2 both on one bar
var int   fsT  = na
var float qH   = na
var float qL   = na
var float ceV  = na
var float ceAt = na
var float ceDA = na
var int   ceHT = na
bool at830 = vzF and tfM <= 30''')
rep('''    k59 := calK
    cxP := p_''', '''    k59 := calK
    fsd  := 0
    fsT  := na
    qH   := na
    qL   := na
    ceAt := math.max(nz(athP, tdH[1]), tdH[1])
    ceV  := ceAt > close[1] ? (ceAt + close[1]) / 2 : na
    ceDA := a_ > 0 and not na(ceV) ? (ceV - close[1]) / a_ : na
    ceHT := na
    cxP := p_''')
rep('''if vzK == calK and na(amC) and mod >= 660 and tgKey == calK
    amC := close[1]''', '''if vzK == calK and na(amC) and mod >= 660 and tgKey == calK
    amC := close[1]
if vzK == calK and mod >= 510 and mod < 975
    qH := math.max(nz(qH, high), high)
    qL := math.min(nz(qL, low), low)
    if fsd == 0 and p7K == calK
        bool bu = high > p7H
        bool bd = low < p7L
        if bu or bd
            fsd := bu and bd ? 2 : bu ? 1 : -1
            fsT := time
if vzK == calK and not na(ceV) and na(ceHT) and mod >= 510 and mod < 1020 and high >= ceV
    ceHT := time
ceOdds(float x) => na(x) ? "—" : x <= 0.5 ? "79%" : x <= 1 ? "23%" : x <= 2 ? "1%" : "0%"''')
rep('SGR = layI == "Mobile" ? 7 : 20', 'SGR = layI == "Mobile" ? 5 : 12')
rep('''    TV.merge_cells(1, tvO, 3, tvO)
''', '''    TV.merge_cells(1, tvO, 3, tvO)
// the findings table (indicator pane)
var table TH  = na
var int   thO = 0
HYR = layI == "Mobile" ? 6 : 11
if barstate.isfirst and showHy
    thO := hyPos == "Top left" or hyPos == "Top center" or hyPos == "Top right" ? 1 : 0
    TH  := table.new(posOf(hyPos), 5, HYR + thO, bgcolor = #00000000, frame_width = 0, border_width = 0)
    if thO == 1
        TH.cell(0, 0, "", height = 7.0, bgcolor = #00000000)
        TH.merge_cells(0, 0, 4, 0)
    TH.merge_cells(1, thO, 3, thO)
    if layI != "Mobile"
        TH.merge_cells(2, thO + 2, 4, thO + 2)
''')

# ── dealing range drawn live from 07:00, ATH CE from 08:30
rep('''var int   drK = na
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
        trimL(line.new(keyAt(calK, 420), drH, keyAt(calK, 974), drH, xloc = xloc.bar_time, color = cLvl, width = 1, style = line.style_dashed, force_overlay = true), keyAt(calK, 974))
        trimL(line.new(keyAt(calK, 420), drL, keyAt(calK, 974), drL, xloc = xloc.bar_time, color = cLvl, width = 1, style = line.style_dashed, force_overlay = true), keyAt(calK, 974))
        trimT(label.new(keyAt(calK, 420), drH, "DR high", xloc = xloc.bar_time, color = #00000000, textcolor = cLvl, style = label.style_label_lower_left, size = size.tiny, tooltip = "NFP dealing range 07:00–09:00 ET", force_overlay = true), keyAt(calK, 420))
        trimT(label.new(keyAt(calK, 420), drL, "DR low", xloc = xloc.bar_time, color = #00000000, textcolor = cLvl, style = label.style_label_upper_left, size = size.tiny, tooltip = "NFP dealing range 07:00–09:00 ET", force_overlay = true), keyAt(calK, 420))''',
    '''var int   drK = na
var line  dLH = na
var line  dLL = na
var label dTH = na
var label dTL = na
if cOn
    // the dealing range is drawn from its first bar and follows the high and low until 09:00, then stays fixed to 16:14
    if mod >= 420 and mod < 540
        if drK != calK
            drK := calK
            drH := high
            drL := low
            dLH := trimL(line.new(time, drH, keyAt(calK, 974), drH, xloc = xloc.bar_time, color = cLvl, width = 1, style = line.style_dashed, force_overlay = true), keyAt(calK, 974))
            dLL := trimL(line.new(time, drL, keyAt(calK, 974), drL, xloc = xloc.bar_time, color = cLvl, width = 1, style = line.style_dashed, force_overlay = true), keyAt(calK, 974))
            dTH := label.new(time, drH, "DR high", xloc = xloc.bar_time, color = #00000000, textcolor = cLvl, style = label.style_label_lower_left, size = size.tiny, tooltip = "NFP dealing range 07:00–09:00 ET: drawn live from 07:00, fixed at 09:00. Its 07:00–08:29 part is the pre-release range the findings pane reads.", force_overlay = true)
            dTL := label.new(time, drL, "DR low", xloc = xloc.bar_time, color = #00000000, textcolor = cLvl, style = label.style_label_upper_left, size = size.tiny, tooltip = "NFP dealing range 07:00–09:00 ET: drawn live from 07:00, fixed at 09:00.", force_overlay = true)
        else
            drH := math.max(drH, high)
            drL := math.min(drL, low)
            dLH.set_y1(drH)
            dLH.set_y2(drH)
            dLL.set_y1(drL)
            dLL.set_y2(drL)
            dTH.set_y(drH)
            dTL.set_y(drL)
    if at830 and showATH and not na(ceV)
        string ceTp = "ATH CE " + pf(ceV) + " = (ATH " + pf(ceAt) + " + 08:29 close) ÷ 2, " + str.tostring(ceDA, "0.00") + " ADR above price at 08:29: touched by 17:00 on " + ceOdds(ceDA) + " of pooled NFP days at that distance. " + VZT_CE
        trimL(line.new(time, ceV, keyAt(calK, 1020), ceV, xloc = xloc.bar_time, color = cAth, width = 1, style = line.style_dashed, force_overlay = true), keyAt(calK, 1020))
        trimT(label.new(keyAt(calK, 1020), ceV, "ATH CE " + ceOdds(ceDA), xloc = xloc.bar_time, color = #00000000, textcolor = cAth, style = label.style_label_left, size = size.tiny, tooltip = ceTp, force_overlay = true), keyAt(calK, 1020))''')

# headroom also for the findings table at the top of the pane
rep('bool  ckTop = showCk and ckOn == "Indicator pane" and str.startswith(ckPos, "Top")',
    'bool  ckTop = (showCk and ckOn == "Indicator pane" and str.startswith(ckPos, "Top")) or (showHy and str.startswith(hyPos, "Top"))')

# ── ATH line right of price (last bar)
rep('''        if showWO and vzF and vzK == calK and not na(s1X) and bar_index - s1X < 4900''', '''        if showATH and not na(athN) and not na(athNT)
            float aA = ADRtd * tdO
            RL.push(line.new(athNT, athN, time + offI * timeframe.in_seconds() * 1000, athN, xloc = xloc.bar_time, color = cAth, width = 1, force_overlay = true))
            RT.push(label.new(bar_index + 2, athN, "ATH " + pf(athN) + " · " + (athTd ? "today" : str.format_time(athNT, "dd MMM yy", TZ)) + " · −" + str.tostring(athN - close, "0"), color = #00000000, textcolor = cAth, style = label.style_label_left, size = size.tiny, tooltip = "All-time high " + pf(athN) + ", set " + (athTd ? "today" : str.format_time(athNT, "dd MMM yyyy", TZ)) + " (highest daily high of the chart's history). Price is " + pf(athN - close) + " pts below it" + (aA > 0 ? " (" + str.tostring((athN - close) / aA, "0.00") + " ADR)" : "") + ". On NFP days the CE between it and the 08:29 close is drawn at 08:30.", force_overlay = true))
        if showWO and vzF and vzK == calK and not na(s1X) and bar_index - s1X < 4900''')

open('/home/claude/hm/calgen/Desgarron_v2_partial.pine', 'w', encoding='utf-8').write(S)
print('ok', len(S))

# ── stages card and findings pane (replaces the old stages card block)
NEW_SG = open('/home/claude/hm/calgen/frag/desg_sg2.pine', encoding='utf-8').read()
cut('// ═══════════════════════════════════════════════════════════════ NFP stages card (last bar)', '// ═══ Write the queued card cells', NEW_SG)
for gone in ('VZV_D1', 'VZB_D1', 'VZT_MON = isES', 'isES ? TAL_ES : isNQ'):
    assert gone not in S, gone
open('/home/claude/hm/calgen/Desgarron.pine', 'w', encoding='utf-8').write(S)
print('written', len(S.split('\n')), 'lines')
