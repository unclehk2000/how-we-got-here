"""Domain Expansion v9 from v8 (DE_v8.pine → Domain_Expansion_Indicator.pine).
- equal highs / lows and the overnight peak-volume level removed (inputs, drawings, card row, alert, result text)
- the cards get their own text colour from the card theme; "Chart text colour" now only colours labels on the chart
  and, left at its default, follows the chart background; card headers pick dark or white text by the tier colour
- text notes (02:30 tier, break, 05:00 result, follow-through) off by default: the card carries them; the first break
  becomes a small ▲ / ▼; the follow-through moves into the card (FOLLOW row)
- labels that meet at the same time keep their text off each other's lines: at 05:00 (domain, SD and pre-London labels
  against each other and the carried London high / low) and at 02:30 (pre-London labels against the domain lines)
- pre-London dealing range 00:00–00:59 ET with its CE, lines to 02:00 (default) or 05:00"""
import re

S = open('/home/claude/dx/DE_v8.pine').read()


def rep(old, new, n=1):
    global S
    c = S.count(old)
    assert c == n, (c, old[:90])
    S = S.replace(old, new)


def cut(a, b):
    """remove from the line starting with a up to (not including) the line starting with b"""
    global S
    i = S.index(a)
    j = S.index(b, i)
    S = S[:i] + S[j:]


# ── View inputs: card theme vs chart text
rep('themeI  = input.string("Auto", "Theme", options = ["Auto", "Dark", "Light"], group = g_D, tooltip = "Auto follows the chart background. Text and the colours left at their default follow it.", display = display.none)',
    'themeI  = input.string("Auto", "Card theme", options = ["Auto", "Dark", "Light"], group = g_D, tooltip = "The London card and the recent-sessions table. Auto follows the chart background. Their text always follows this theme, so it stays readable whatever chart text colour you pick.", display = display.none)')
rep('txtColI = input.color(#000001, "Text colour", group = g_D, tooltip = "Left at the default it follows the theme; pick any colour to override.", display = display.none)',
    'txtColI = input.color(#000001, "Chart text colour", group = g_D, tooltip = "The labels on the chart. Left at the default it follows the chart background; pick any colour to override. The cards keep their own text colour.", display = display.none)')

# ── pre-London dealing range inputs, after the domain range group
PL_TIP = ("The high, low and CE (midpoint) of 00:00–00:59 ET, drawn from 00:00 to the London open, or to 05:00. "
          "The high and low dash once price trades through them.\\n\\n"
          "NQ + ES + RTY 1-minute 2018–26, 5,526 sessions, at 00:00–01:00:\\n"
          "Before London (01:00–01:59): high taken 56%, low 51%, at least one 90%.\\n"
          "London (02:00–04:59): high 78%, low 73%, at least one 99.7%, both 52%.\\n"
          "CE: London traded through it on 75% of sessions. When price sat outside the range at 02:00 (52% of sessions), London came back to the CE 64% of the time.\\n"
          "Steady in 2018–24 and 2025–26 and on each symbol.\\n\\n"
          "The domain range formed inside the pre-London range on 8% of sessions. On those days, when not coiled, 2 SD odds were 37% against 26% (p 0.01, same side in both periods and on each symbol; 2025–26 has only 41 such days). Coiled days showed no difference. Not part of the tier.")
rep('var g_X = "Standard deviations (domain range multiples)"',
    'var g_P = "Pre-London dealing range"\n'
    'showPL   = input.bool(true, "Pre-London dealing range", inline = "pl", group = g_P, tooltip = "' + PL_TIP + '", display = display.none)\n'
    'colPL    = input.color(#2962ff, "", inline = "pl", group = g_P, display = display.none)\n'
    'plSess   = input.session("0000-0100", "Forms", group = g_P, display = display.none)\n'
    'plTo     = input.string("02:00 · London open", "Lines run to", options = ["02:00 · London open", "05:00 · end of London"], group = g_P, display = display.none)\n'
    'showPLce = input.bool(true, "CE (midpoint)", group = g_P, display = display.none)\n\n'
    'var g_X = "Standard deviations (domain range multiples)"')

# ── remove the liquidity and peak-volume groups
cut('var g_L = "Liquidity · overnight equal highs / lows"', 'var g_E = "Execution & result"')

# ── execution & result: notes off by default
rep('showBrk = input.bool(true, "Mark the first break in the window", group = g_E, display = display.none)\n'
    'showRes = input.bool(true, "Mark the result at the end of London", group = g_E, display = display.none)\n'
    'showFT  = input.bool(true, "Mark the follow-through at the end of its window", group = g_E, display = display.none)\n',
    'showBrk = input.bool(true, "Mark the first break in the window", tooltip = "A small ▲ / ▼ on the candle that first broke the domain range inside the execution window.", group = g_E, display = display.none)\n'
    'showNotes = input.bool(false, "Text notes on the chart", tooltip = "The tier at 02:30, the break, the result at 05:00 and the follow-through as text boxes on the chart. They can sit on price. Off: the London card carries all of them.", group = g_E, display = display.none)\n')

# ── alerts: no equal highs / lows
rep('alEq  = input.bool(true, "Equal highs / lows swept", group = g_AL, display = display.none)\n', '')

# ── colours: cards follow the card theme, chart text follows the chart background
rep('isDark = themeI == "Dark" or (themeI == "Auto" and bgLum < 128)\n'
    'autoC(color c) => color.r(c) == 0 and color.g(c) == 0 and color.b(c) == 1\n'
    'fgAuto = isDark ? #d1d4dc : #131722\n'
    'txtCol = autoC(txtColI) ? fgAuto : txtColI\n',
    'isDark = themeI == "Dark" or (themeI == "Auto" and bgLum < 128)                      // the cards\n'
    'autoC(color c) => color.r(c) == 0 and color.g(c) == 0 and color.b(c) == 1\n'
    'txtCol = autoC(txtColI) ? (bgLum < 128 ? #d1d4dc : #131722) : txtColI              // labels on the chart\n'
    'cTxt   = isDark ? #d1d4dc : #131722                                                // card text, from the card theme only\n'
    'lumOf(color c) => 0.299 * color.r(c) + 0.587 * color.g(c) + 0.114 * color.b(c)\n'
    'hdrTx(color c) => lumOf(c) > 165 ? #131722 : #ffffff                                // dark text on light tier colours\n')
rep('eqThrE  = eqThr * scale\n', '')

# ── sessions: drop the overnight flags (only the liquidity code used them); add the pre-London range
rep('inON  = sessOn(onSess)\nonBeg = inON and not inON[1]\n', '')
rep('drStart  = inDR and not inDR[1]\n',
    'to05  = plTo == "05:00 · end of London"\n'
    'inPL  = sessOn(plSess)\n'
    'inPLd = sessOn(str.substring(plSess, 0, 4) + (to05 ? "-0500" : "-0200"))   // the lines run from the range open to 02:00 or 05:00\n'
    'drStart  = inDR and not inDR[1]\n')

# ── marks: a small glyph for the first break
rep('// half as strong: transparency moves halfway to fully clear',
    'mkMark(bool up, color col) =>\n'
    '    evLbl.push(label.new(time, up ? high : low, "", xloc = xloc.bar_time, yloc = up ? yloc.abovebar : yloc.belowbar, style = up ? label.style_triangleup : label.style_triangledown, color = col, size = size.tiny))\n'
    '    evDay.push(dayCount)\n'
    '    evCol.push(col)\n\n'
    'mkPL(int t0, float y, color col, string st, string txt, bool above, bool watch, string tip) =>\n'
    '    lv = Lv.new(line.new(t0, y, time, y, xloc = xloc.bar_time, color = col, style = st, width = 1), label.new(time, y, txt, xloc = xloc.bar_time, style = label.style_label_left, color = #ffffff00, textcolor = txtCol, size = tSize, tooltip = tip), na, y, above, dayCount, false, true, watch, "pre", col)\n'
    '    store.push(lv)\n\n'
    '// a label\'s text moves above or below its line when another level sits close, so lines and labels that meet at the same time stay legible\n'
    'awayFrom(Lv a, float y) =>\n'
    '    a.lb.set_style(a.y > y or (a.y == y and (a.grp == "pre" ? not a.above : a.above)) ? label.style_label_lower_left : label.style_label_upper_left)\n\n'
    '// half as strong: transparency moves halfway to fully clear')
rep('                    evLbl.get(i).set_color(ageMode == "Grey" ? color.new(agedCol, 85) : color.new(evCol.get(i), 90))',
    '                    bool mk = evLbl.get(i).get_text() == ""\n'
    '                    evLbl.get(i).set_color(ageMode == "Grey" ? color.new(agedCol, mk ? 40 : 85) : color.new(evCol.get(i), mk ? 50 : 90))')

# ── remove the overnight liquidity section; add the pre-London range
PL_BLOCK = '''// ═══════════════════════════════════════════════════════════════════
// PRE-LONDON DEALING RANGE (00:00 → 01:00), lines to 02:00 or 05:00
// ═══════════════════════════════════════════════════════════════════
var float pH  = na
var float pL  = na
var int   pHt = na
var int   pLt = na
var int   pT0 = na
if inPL and not inPL[1]
    pH  := high
    pL  := low
    pHt := time
    pLt := time
    pT0 := time
else if inPL
    if high > pH
        pH  := high
        pHt := time
    if low < pL
        pL  := low
        pLt := time
if showPL and not inPL and inPL[1] and inPLd and not na(pH) and pH > pL
    string rngTx = "Pre-London dealing range " + hhmm(pT0) + "–" + hhmm(time) + " ET, " + str.tostring(math.round(pH - pL)) + " pts. "
    mkPL(pT0, pH, colPL, line.style_solid, "Pre-London high", true, true, rngTx + "High " + str.tostring(pH, format.mintick) + " at " + stampOf(pHt) + ". London (02:00–04:59) took it on 78% of sessions, NQ + ES + RTY 2018–26.")
    mkPL(pT0, pL, colPL, line.style_solid, "Pre-London low", false, true, rngTx + "Low " + str.tostring(pL, format.mintick) + " at " + stampOf(pLt) + ". London (02:00–04:59) took it on 73% of sessions, NQ + ES + RTY 2018–26.")
    if showPLce
        mkPL(pT0, (pH + pL) / 2, color.new(colPL, 30), line.style_dotted, "Pre-London CE", true, false, rngTx + "CE (midpoint) " + str.tostring((pH + pL) / 2, format.mintick) + ". London traded through it on 75% of sessions; 64% when price sat outside the range at 02:00.")

'''
i = S.index('// ═══════════════════════════════════════════════════════════════════\n// OVERNIGHT LIQUIDITY')
j = S.index('// ═══════════════════════════════════════════════════════════════════\n// DOMAIN RANGE (02:00')
S = S[:i] + PL_BLOCK + S[j:]

# ── per-day state: no equal-high / low counters; follow-through result for the card
rep('var int   eqHn    = 0       // equal-high / equal-low zones drawn today, and how many London swept\n'
    'var int   eqLn    = 0\n'
    'var int   eqHs    = 0\n'
    'var int   eqLs    = 0\n',
    'var string ftRes  = na      // the follow-through close against the range, for the card\n')
rep('    eqHn    := 0\n    eqLn    := 0\n    eqHs    := 0\n    eqLs    := 0\n', '    ftRes   := na\n')

# ── 02:30: the tier note only with notes on; no equal highs / lows or peak volume; pre-London labels off the domain lines
rep('    mkEvent(dH, verdict + oddsTxt + "\\n" + f1Txt + "\\n" + cbTxt, tc, true)\n',
    '    if showNotes\n'
    '        mkEvent(dH, verdict + oddsTxt + "\\n" + f1Txt + "\\n" + cbTxt, tc, true)\n')
cut('    // overnight equal highs / lows still unswept at 02:30', 'qCol = tier == 3')
rep('qCol = tier == 3 ? colBoth',
    '    // the pre-London labels at 02:00 sit where the domain lines start: keep their text off those lines\n'
    '    if showPL and not to05 and store.size() > 0\n'
    '        int nP = store.size()\n'
    '        for i = 0 to nP - 1\n'
    '            a = store.get(i)\n'
    '            if a.day == dayCount and a.grp == "pre"\n'
    '                float best = na\n'
    '                float bd   = 0.25 * rD\n'
    '                for j = 0 to nP - 1\n'
    '                    b = store.get(j)\n'
    '                    if b.day == dayCount and b.grp == "dr" and math.abs(b.y - a.y) <= bd\n'
    '                        bd   := math.abs(b.y - a.y)\n'
    '                        best := b.y\n'
    '                if not na(best)\n'
    '                    awayFrom(a, best)\n\n'
    'qCol = tier == 3 ? colBoth')

# ── first break: a small mark, or the text note
rep('    if showBrk\n'
    '        mkEvent(low < dL and not (high > dH) ? low : high, bTx + hhmm(time), qCol, not (low < dL and not (high > dH)))\n',
    '    if showBrk\n'
    '        if showNotes\n'
    '            mkEvent(low < dL and not (high > dH) ? low : high, bTx + hhmm(time), qCol, not (low < dL and not (high > dH)))\n'
    '        else\n'
    '            mkMark(high > dH, qCol)\n')

# ── 05:00 result: no equal highs / lows; note only with notes on; labels meeting at 05:00 keep clear of each other
rep('    string eqTx  = eqHn + eqLn == 0 ? "" : " · EQH " + str.tostring(eqHs) + "/" + str.tostring(eqHn) + " EQL " + str.tostring(eqLs) + "/" + str.tostring(eqLn) + " swept"\n'
    '    if showRes\n'
    '        mkEvent(c5, head + "\\n" + exTxt + " · close " + farTxt(c5) + "\\nLondon " + str.tostring(math.round(lr)) + " pts" + adrTx + eqTx, qCol, c5 >= (dH + dL) / 2)\n',
    '    if showNotes\n'
    '        mkEvent(c5, head + "\\n" + exTxt + " · close " + farTxt(c5) + "\\nLondon " + str.tostring(math.round(lr)) + " pts" + adrTx, qCol, c5 >= (dH + dL) / 2)\n'
    '    // labels that meet at 05:00 (domain, SD and pre-London levels, and the carried London high / low) keep their text off each other\n'
    '    int n5 = store.size()\n'
    '    for i = 0 to n5 - 1\n'
    '        a = store.get(i)\n'
    '        if a.day == dayCount and (a.grp == "dr" or (a.grp == "pre" and to05))\n'
    '            float best = na\n'
    '            float bd   = 0.25 * rD\n'
    '            for j = 0 to n5 - 1\n'
    '                b = store.get(j)\n'
    '                if j != i and b.day == dayCount and (b.grp == "dr" or (b.grp == "pre" and to05)) and math.abs(b.y - a.y) <= bd\n'
    '                    bd   := math.abs(b.y - a.y)\n'
    '                    best := b.y\n'
    '            if showCarry\n'
    '                if math.abs(lH5 - a.y) <= bd\n'
    '                    bd   := math.abs(lH5 - a.y)\n'
    '                    best := lH5\n'
    '                if math.abs(lL5 - a.y) <= bd\n'
    '                    best := lL5\n'
    '            if not na(best)\n'
    '                awayFrom(a, best)\n')

# ── follow-through: always read for the card; the note only with notes on
rep('if showFT and ftEnd and dDay == dayCount and not na(rD)\n'
    '    c7 = close[1]\n'
    '    mkEvent(c7, "Follow-through " + hhmm(time) + " · close " + farTxt(c7), qCol, c7 >= (dH + dL) / 2)\n',
    'if ftEnd and dDay == dayCount and not na(rD)\n'
    '    c7 = close[1]\n'
    '    float s7 = pastSD(c7)\n'
    '    ftRes := s7 == 0 ? "close inside the range" : "close " + sdTxtOf(math.abs(s7)) + (s7 > 0 ? " above" : " below")\n'
    '    if showNotes\n'
    '        mkEvent(c7, "Follow-through " + hhmm(time) + " · close " + farTxt(c7), qCol, c7 >= (dH + dL) / 2)\n')

# ── every bar: pre-London lines stop at 02:00 / 05:00; no equal-high / low zones
rep('        stopNow = lv.live and (((lv.grp == "dr" or lv.grp == "eq") and not inLon) or (lv.grp == "ny" and not inNYc))\n',
    '        stopNow = lv.live and ((lv.grp == "dr" and not inLon) or (lv.grp == "pre" and not inPLd) or (lv.grp == "ny" and not inNYc))\n')
rep('            if lv.grp == "eq"\n                lv.bx.set_right(time)\n', '')
rep('        if stopNow\n            lv.live := false\n',
    '        if stopNow\n'
    '            lv.live := false\n'
    '            if lv.grp == "ny" and not lv.hit\n'
    '                lv.lb.set_text((lv.above ? "London high" : "London low") + " · not taken by 11:00")\n')
rep('        // levels count as traded through on a touch; equal highs / lows only when price trades beyond them\n'
    '        bool strict = lv.grp == "eq" or lv.grp == "ny"\n',
    '        // levels count as traded through on a touch; the carried London high / low only when price trades beyond them\n'
    '        bool strict = lv.grp == "ny"\n')
i = S.index('            if lv.grp == "eq"\n                lv.bx.set_border_style')
j = S.index('            if lv.grp == "ny"\n                lv.lb.set_text')
S = S[:i] + S[j:]

# ── cards: own text colour; header text by tier colour; FOLLOW replaces SWEPT
rep('    t.cell(1, r, v, text_color = na(vc) ? txtCol : vc,', '    t.cell(1, r, v, text_color = na(vc) ? cTxt : vc,')
rep('    t.cell(2, r, w, text_color = na(vc) ? txtCol : vc,', '    t.cell(2, r, w, text_color = na(vc) ? cTxt : vc,')
rep('    t.cell(0, 0, a, text_color = #ffffff, bgcolor = bg,', '    t.cell(0, 0, a, text_color = hdrTx(bg), bgcolor = bg,')
rep('    t.cell(1, 0, b, text_color = #ffffff, bgcolor = bg,', '    t.cell(1, 0, b, text_color = hdrTx(bg), bgcolor = bg,')
rep('    t.cell(2, 0, pill, text_color = bg, bgcolor = #ffffff,', '    t.cell(2, 0, pill, text_color = bg, bgcolor = lumOf(bg) > 165 ? #131722 : #ffffff,')
rep('        cRow(TC, 3, "SWEPT", eqHn + eqLn == 0 ? "no equal highs / lows" : "EQH " + str.tostring(eqHs) + "/" + str.tostring(eqHn) + " · EQL " + str.tostring(eqLs) + "/" + str.tostring(eqLn), "", "Overnight equal-high and equal-low zones drawn at 02:30 and how many London traded through.", na)\n',
    '        string ftE = str.substring(ftSess, 5, 7) + ":" + str.substring(ftSess, 7, 9)\n'
    '        cRow(TC, 3, "FOLLOW", na(ftRes) ? "close at " + ftE + " ET" : ftRes, na(ftRes) ? "pending" : ftE, "Follow-through: the close at the end of its window (" + ftSess + " ET) against the domain range, in SD. Some expansions finish after London.", na)\n')
rep('text_color = txtCol, bgcolor = cBody', 'text_color = cTxt, bgcolor = cBody', 3)

assert 'eq' not in re.findall(r'grp == "(\w+)"', S)
for w in ('eqz', 'eqHn', 'pvLvl', 'showEQ', 'showPV', 'alEq', 'showRes', 'showFT', 'fgAuto', 'inON', 'onBeg'):
    assert not re.search(r'\b' + w + r'\b', S), w
open('/home/claude/dx/Domain_Expansion_Indicator.pine', 'w').write(S)
print('ok', len(S.splitlines()), 'lines')
