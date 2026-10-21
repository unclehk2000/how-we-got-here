import json, re
P = '/home/claude/hm/calgen/Desgarron.pine'
S = open(P, encoding='utf-8').read()
def rep(old, new, n=1):
    global S
    c = S.count(old)
    assert c == n, (c, old[:120])
    S = S.replace(old, new)
# ── header
a = S.index('// On the price chart:'); b = S.index('// Release dates were checked')
S = S[:a] + '''// On the price chart: the 07:00–09:00 dealing range (drawn live from 07:00), the all-time high carried right of price
// and, at 08:30, the 50% (consequent encroachment) between the ATH and price, carried to 17:00; the 08:30–08:45 hands-off
// window, the 08:50 line, the RTH gap (prior 16:14 close and its 50%), the 08:30 and 08:50 opens carried right, and two
// cards, each in its own corner: the NFP tally and the NFP stages card (the 08:29 setup led by the month's premium /
// discount, the sizes NFP days with that setup made at today's ADR20, the release stages live against DXY).
// Indicator pane: the event clock, and the HYDRA findings table: what held on pooled NQ + ES + RTY NFP days for today's
// setup, in points at today's ADR20.
// Built for NQ / MNQ, ES / MES and RTY / M2K. The card figures are pooled across the three (99 releases, 293 symbol-days,
// 1-minute data Jan 2018 – Oct 2026); the clock and tally use each symbol's own data. A green key (✓) passed p < 0.05
// (errors clustered by release) and sat on the same side in 2018–24, in 2025–26 and on each of NQ, ES and RTY.
''' + S[b:]
# ── inputs
rep('''showWO  = input.bool(true, "Week open, 08:30 and 08:50 opens", group = grpS, tooltip = "The week's open (Sunday 18:00) and, on NFP days, the open of the 08:30 and 08:50 candles, each extended to the right of price.", display = display.none)
''', '''showWO  = input.bool(true, "Week open, 08:30 and 08:50 opens", group = grpS, tooltip = "The week's open (Sunday 18:00) and, on NFP days, the open of the 08:30 and 08:50 candles, each extended to the right of price.", display = display.none)
showATH = input.bool(true, "ATH and its 08:30 CE", group = grpS, inline = "s2", display = display.none)
cAth    = input.color(#ab47bc, "", group = grpS, inline = "s2", display = display.none)
ceAll   = input.bool(false, "CE every day", group = grpS, inline = "s2", tooltip = "The all-time high (completed daily bars plus today) is drawn from its day to the right of price. At 08:30 the 50% between the ATH and the 08:29 price (consequent encroachment) forms and runs to 17:00. Its touch odds were measured on NFP days; 'CE every day' draws it on other days too.", display = display.none)
''')
rep('''sgPos   = input.string("Bottom left", "", options = ["Top left", "Top center", "Top right", "Middle left", "Middle right", "Bottom left", "Bottom center", "Bottom right"], group = grpV, inline = "v0", display = display.none)
''', '''sgPos   = input.string("Bottom left", "", options = ["Top left", "Top center", "Top right", "Middle left", "Middle right", "Bottom left", "Bottom center", "Bottom right"], group = grpV, inline = "v0", display = display.none)
grpF    = "HYDRA findings (indicator pane)"
showFd  = input.bool(true, "Findings", group = grpF, inline = "f0", tooltip = "What held on pooled NQ + ES + RTY NFP days for today's setup, in points at today's ADR20: the size of the day, the new high / low odds after 08:30, the ATH CE, the first dealing-range side, the big-DXY rule and the 08:30–09:00 expansion. Green key = held. Make the pane taller to fit it.", display = display.none)
fdPos   = input.string("Top left", "", options = ["Top left", "Top center", "Top right", "Middle left", "Middle right", "Bottom left", "Bottom center", "Bottom right"], group = grpF, inline = "f0", display = display.none)
cFd     = input.color(#5c6bc0, "Accent", group = grpF, inline = "f0", display = display.none)
''')
# ── RTY data
R = json.load(open('/home/claude/hm/calgen/rty/rty.json'))
i = S.index('\nint  AN    =')
S = S[:i] + '\n' + '\n'.join(R['ck']) + S[i:]
rep('''bool isNQ  = syminfo.root == "NQ" or syminfo.root == "MNQ"
string symR   = isES ? "ES" : "NQ"                           // whose statistics the cards show
string symTag = isNQ or isES ? syminfo.root : syminfo.root + " (" + symR + " DATA)"''',
'''bool isNQ  = syminfo.root == "NQ" or syminfo.root == "MNQ"
bool isRTY = syminfo.root == "RTY" or syminfo.root == "M2K"
string symR   = isES ? "ES" : isRTY ? "RTY" : "NQ"           // whose clock and tally the cards show (the stage figures are pooled)
string symTag = isNQ or isES or isRTY ? syminfo.root : syminfo.root + " (" + symR + " DATA)"''')
rep('var array<float> CK = unpackMilli(isES ? CK_ES : CK_NQ)', 'var array<float> CK = unpackMilli(isES ? CK_ES : isRTY ? CK_RTY : CK_NQ)')
rep('TAL_END_ES = 20260828\n', 'TAL_END_ES = 20260828\n' + '\n'.join(R['tal']) + '\n' + R['end'] + '\n')
rep('''ckN(int k, bool es) =>
    switch k
        0 => es ? "98" : "98"
        1 => es ? "1416" : "1342"''', '''ckN(int k) =>
    switch k
        0 => isRTY ? "101" : "98"
        1 => isES ? "1416" : isRTY ? "1441" : "1342"''')
rep('ckN(ckI, isES)', 'ckN(ckI)'); rep('ckN(NCK - 1, isES)', 'ckN(NCK - 1)')
rep('int  talEnd = isES ? TAL_END_ES : isNQ ? TAL_END_NQ : 0', 'int  talEnd = isES ? TAL_END_ES : isNQ ? TAL_END_NQ : isRTY ? TAL_END_RTY : 0')
rep('string src = isES ? TAL_ES : isNQ ? TAL_NQ : ""', 'string src = isES ? TAL_ES : isNQ ? TAL_NQ : isRTY ? TAL_RTY : ""')
rep("(built-in history covers NQ / MNQ and ES / MES)", "(built-in history covers NQ / MNQ, ES / MES and RTY / M2K)")
rep('''(isNQ or isES ? "" : " This chart is "''', '''(isNQ or isES or isRTY ? "" : " This chart is "''')
rep('// built-in event-day records for the tally (NQ / MNQ and ES / MES; other symbols use the chart\'s own history)', '// built-in event-day records for the tally (NQ / MNQ, ES / MES and RTY / M2K; other symbols use the chart\'s own history)')
# ── ATH request
rep('''[dxA, dx20] = request.security(dxySym, "D", [ta.sma(high - low, 20)[1], close[20]], lookahead = barmerge.lookahead_on, ignore_invalid_symbol = true)
''', '''[dxA, dx20] = request.security(dxySym, "D", [ta.sma(high - low, 20)[1], close[20]], lookahead = barmerge.lookahead_on, ignore_invalid_symbol = true)
// the all-time high on completed daily bars, and the time of its day
athF() =>
    float m = ta.max(high)
    var int t = na
    if high >= m
        t := time
    [m[1], t[1]]
[athP, athT] = request.security(syminfo.tickerid, "D", athF(), lookahead = barmerge.lookahead_on)
''')
# ── trading-day high time, ATH now
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
    tdH := math.max(nz(tdH, high), high)''', '''var int   tdX  = na
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
    if high > tdH
        tdHT := time
    tdH := math.max(nz(tdH, high), high)''')
rep('''// the month so far, today included (the month-to-date high and low)''', '''// the all-time high so far (today's high once it is above the prior one) and when it was set
float athN  = math.max(nz(athP, tdH), tdH)
int   athNT = tdH >= nz(athP, tdH) ? tdHT : athT
// the month so far, today included (the month-to-date high and low)''')
open(P, 'w', encoding='utf-8').write(S)
print('ok', len(S))
