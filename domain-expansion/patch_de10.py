"""Domain Expansion v10 from v9 (DE_v9.pine → Domain_Expansion_Indicator.pine).
- text notes back on by default, every timeframe
- the first break is a text label at its candle again ("▲ Break 02:33"), as in v8
- the follow-through always joins the 05:00 note (one note: result + follow-through)
- placement so the notes stay off each other:
    tier note (02:30) starts above the domain range and moves below it when the first break is upward (or both sides),
    so it sits on the side away from the breakout label;
    it anchors beyond the pre-London range when that range's labels sit at 02:00;
    the 05:00 note goes on the other side from the tier note, beyond the London high (or low), box to the left of 05:00,
    clear of London's candles and of the line labels that start at 05:00"""
S = open('/home/claude/dx/DE_v9.pine').read()


def rep(old, new, n=1):
    global S
    c = S.count(old)
    assert c == n, (c, old[:90])
    S = S.replace(old, new)


# inputs
i = S.index('showBrk = input.bool(true, "Mark the first break in the window"')
j = S.index('\n', S.index('showNotes = input.bool(false, "Text notes on the chart"'))
S = S[:i] + (
    'showBrk = input.bool(true, "Mark the first break in the window", tooltip = "A label on the candle that first broke the domain range inside the execution window, e.g. ▲ Break 02:33.", group = g_E, display = display.none)\n'
    'showNotes = input.bool(true, "Text notes on the chart", tooltip = "Two notes a day: the tier at 02:30, and the result at 05:00 with the follow-through added at the end of its window. '
    'The tier note moves to the side away from the first break; the 05:00 note goes on the other side, beyond the London high or low and to the left of 05:00. '
    'That keeps them off each other, off the breakout label and off the line labels that start at 05:00. The London card shows the same.", group = g_E, display = display.none)') + S[j:]

# no small marks any more; aging back to the box rule
i = S.index('mkMark(bool up, color col) =>')
j = S.index('mkPL(int t0')
S = S[:i] + S[j:]
rep('                    bool mk = evLbl.get(i).get_text() == ""\n'
    '                    evLbl.get(i).set_color(ageMode == "Grey" ? color.new(agedCol, mk ? 40 : 85) : color.new(evCol.get(i), mk ? 50 : 90))',
    '                    evLbl.get(i).set_color(ageMode == "Grey" ? color.new(agedCol, 85) : color.new(evCol.get(i), 90))')

# mkEvent returns its label and takes a style
rep('mkEvent(float y, string txt, color col, bool above) =>\n'
    '    evLbl.push(label.new(time, y, txt, xloc = xloc.bar_time, style = above ? label.style_label_down : label.style_label_up, color = color.new(col, 80), textcolor = txtCol, size = tSize))\n'
    '    evDay.push(dayCount)\n'
    '    evCol.push(col)\n',
    'mkEvent(float y, string txt, color col, string st) =>\n'
    '    lb = label.new(time, y, txt, xloc = xloc.bar_time, style = st, color = color.new(col, 80), textcolor = txtCol, size = tSize)\n'
    '    evLbl.push(lb)\n'
    '    evDay.push(dayCount)\n'
    '    evCol.push(col)\n'
    '    lb\n')

# today's notes
rep('var string ftRes  = na      // the follow-through close against the range, for the card\n',
    'var string ftRes  = na      // the follow-through close against the range, for the card\n'
    'var label  tierLb = na      // today\'s notes: the tier (02:30) and the result (05:00)\n'
    'var label  resLb  = na\n'
    'var bool   tierUp = true    // the tier note sits above the domain range (false: below)\n')
rep('    ftRes   := na\n', '    ftRes   := na\n    tierLb  := na\n    resLb   := na\n    tierUp  := true\n')
rep('    if showNotes\n        mkEvent(dH, verdict + oddsTxt + "\\n" + f1Txt + "\\n" + cbTxt, tc, true)\n',
    '    if showNotes\n        tierLb := mkEvent(dH, verdict + oddsTxt + "\\n" + f1Txt + "\\n" + cbTxt, tc, label.style_label_down)\n')

# first break: text label at the candle; the tier note moves away from it
rep('    if showBrk\n'
    '        if showNotes\n'
    '            mkEvent(low < dL and not (high > dH) ? low : high, bTx + hhmm(time), qCol, not (low < dL and not (high > dH)))\n'
    '        else\n'
    '            mkMark(high > dH, qCol)\n',
    '    bool bUp = high > dH\n'
    '    if showBrk\n'
    '        mkEvent(bUp ? high : low, bTx + hhmm(time), qCol, bUp ? label.style_label_down : label.style_label_up)\n'
    '    if bUp\n'
    '        tierUp := false\n'
    '        if not na(tierLb)\n'
    '            tierLb.set_y(dL)\n'
    '            tierLb.set_style(label.style_label_up)\n')

# 05:00 note on the other side from the tier note, box to the left of 05:00
rep('    if showNotes\n'
    '        mkEvent(c5, head + "\\n" + exTxt + " · close " + farTxt(c5) + "\\nLondon " + str.tostring(math.round(lr)) + " pts" + adrTx, qCol, c5 >= (dH + dL) / 2)\n',
    '    if showNotes\n'
    '        resLb := mkEvent(tierUp ? lL5 : lH5, head + "\\n" + exTxt + " · close " + farTxt(c5) + "\\nLondon " + str.tostring(math.round(lr)) + " pts" + adrTx, qCol, tierUp ? label.style_label_upper_right : label.style_label_lower_right)\n')

# follow-through joins the 05:00 note
rep('    if showNotes\n'
    '        mkEvent(c7, "Follow-through " + hhmm(time) + " · close " + farTxt(c7), qCol, c7 >= (dH + dL) / 2)\n',
    '    if showNotes and not na(resLb)\n'
    '        resLb.set_text(resLb.get_text() + "\\nFollow-through " + hhmm(time) + " · close " + farTxt(c7))\n')


# the tier note clears the pre-London labels that sit at 02:00: it anchors beyond the pre-London range on its side
rep('var int   pT0 = na\n', 'var int   pT0 = na\nvar int   pDay = na     // the trading day whose pre-London range is in pH / pL\n')
rep('if showPL and not inPL and inPL[1] and inPLd and not na(pH) and pH > pL\n',
    'if not inPL and inPL[1] and not na(pH) and pH > pL\n'
    '    pDay := dayCount\n'
    'plClr() => showPL and not to05 and pDay == dayCount    // pre-London labels sit at 02:00 today\n'
    'if showPL and not inPL and inPL[1] and inPLd and not na(pH) and pH > pL\n')
rep('        tierLb := mkEvent(dH, verdict', '        tierLb := mkEvent(plClr() ? math.max(dH, pH) : dH, verdict')
rep('            tierLb.set_y(dL)\n', '            tierLb.set_y(plClr() ? math.min(dL, pL) : dL)\n')

assert 'mkMark' not in S
open('/home/claude/dx/Domain_Expansion_Indicator.pine', 'w').write(S)
print('ok', len(S.splitlines()))
