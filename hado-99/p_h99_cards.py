"""Hadō 99: two cards (Macro, Fractal), RANGE row on the macro card, DXY row on the fractal card (15m pair)."""
S = open('/home/claude/xa/H99_v1.pine').read()
L = S.split('\n')
def ln(a, b):          # 1-based inclusive line range
    return '\n'.join(L[a - 1:b])
macCalc = ln(612, 632)
fmRows = ln(651, 676)
macRows = ln(681, 695)
head = '\n'.join(L[:604])
def rep(a, b, n=1):
    global head
    assert head.count(a) == n, (head.count(a), a[:90]); head = head.replace(a, b)
# ── inputs: one switch and place per card
rep('''showCard = input.bool(true, "Card", inline = "cd", group = g_V, display = display.none)
cardPos  = input.string("Top right", "", options = ["Top left", "Top center", "Top right", "Middle left", "Middle right", "Bottom left", "Bottom center", "Bottom right"], inline = "cd", group = g_V, display = display.none)
''', '''showMac  = input.bool(true, "Macro card", inline = "cm", group = g_V, display = display.none)
macPos   = input.string("Top right", "", options = ["Top left", "Top center", "Top right", "Middle left", "Middle right", "Bottom left", "Bottom center", "Bottom right"], inline = "cm", group = g_V, tooltip = "Give the two cards different places.", display = display.none)
showFm   = input.bool(true, "Fractal card", inline = "cf", group = g_V, display = display.none)
fmPos    = input.string("Bottom right", "", options = ["Top left", "Top center", "Top right", "Middle left", "Middle right", "Bottom left", "Bottom center", "Bottom right"], inline = "cf", group = g_V, display = display.none)
''')
rep('''cardShow = input.string("Both", "Card shows", options = ["Both", "Fractal", "Macro"], group = g_V, display = display.none)
''', '')
rep('''layoutI  = input.string("Desktop", "Layout", options = ["Desktop", "Mobile"], group = g_V, tooltip = "Mobile folds the card to four rows in the narrower default font; the rest stays in the tooltips.", display = display.none)''',
    '''layoutI  = input.string("Desktop", "Layout", options = ["Desktop", "Mobile"], group = g_V, tooltip = "Mobile folds each card to four rows in the narrower default font; the rest stays in the tooltips.", display = display.none)''')
rep('''cSec   = isDark ? #1f2430 : #e6eaf0
''', '''cNeu   = isDark ? #2a2e39 : #c9ced8
''')
# ── data: range inputs ride on the existing daily requests; DXY 15-minute for the fractal card
rep('''iPrev = request.security(idxTk, "D", close[1], lookahead = barmerge.lookahead_on)
[oPrev, cl20] = request.security(clTk, "D", [close[1], math.log(close[1] / close[21]) * 100], lookahead = barmerge.lookahead_on, ignore_invalid_symbol = true)
[dMa, dPrev] = request.security(dxySym, "D", [ta.sma(close, maLen)[1], close[1]], lookahead = barmerge.lookahead_on, ignore_invalid_symbol = true)''',
'''// yesterday's move in daily standard deviations (20 days, yesterday included)
sdMove() =>
    float r = math.log(close / close[1])
    math.abs(r[1]) / ta.stdev(r, 20)[1]
[iPrev, adr20, yRat] = request.security(idxTk, "D", [close[1], ta.sma(high - low, 20)[1], (high[1] - low[1]) / ta.sma(high - low, 20)[2]], lookahead = barmerge.lookahead_on)
[oPrev, cl20, clZ] = request.security(clTk, "D", [close[1], math.log(close[1] / close[21]) * 100, sdMove()], lookahead = barmerge.lookahead_on, ignore_invalid_symbol = true)
[dMa, dPrev, dxZ] = request.security(dxySym, "D", [ta.sma(close, maLen)[1], close[1], sdMove()], lookahead = barmerge.lookahead_on, ignore_invalid_symbol = true)
// DXY across the last finished 15-minute candle, and the size of a typical 15-minute move (last ~1,300 candles)
[d15a, d15b, d15sd] = request.security(dxySym, "15", [close[1], close[2], ta.stdev(close / close[1] - 1, 1300)[1]], lookahead = barmerge.lookahead_on, ignore_invalid_symbol = true)''')
# today's range so far, from the chart
rep('''// ═══════════════════════════════════════════════════════════════════
// REGIME (from yesterday's closes)''', '''var float dayH = na
var float dayL = na
if timeframe.change("D") or na(dayH)
    dayH := high
    dayL := low
else
    dayH := math.max(dayH, high)
    dayL := math.min(dayL, low)

// ═══════════════════════════════════════════════════════════════════
// REGIME (from yesterday's closes)''')
# FS: the dollar across C2
rep('''    int    pLeft = na           // chart bars left in C4 when the swing was marked
''', '''    int    pLeft = na           // chart bars left in C4 when the swing was marked
    float  dChg  = na           // DXY across the C2 candle, %
    float  dz    = na           // the same in 15-minute standard deviations, signed: > 0 = the setup's way
''')
rep('''                    s.lvl  := bull ? cbL : csL
''', '''                    s.lvl  := bull ? cbL : csL
                    if fmP == 0 and not na(d15a) and not na(d15b) and d15sd > 0
                        s.dChg := (d15a / d15b - 1) * 100
                        s.dz   := (bull ? -1 : 1) * (d15a / d15b - 1) / d15sd
''')
# expected range for the day
rep('''toPtsOf(float pc, float base) => pc * base / 100''', '''toPtsOf(float pc, float base) => pc * base / 100
// range / ADR20 by yesterday's own range (< 1, 1–1.5, ≥ 1.5 × ADR20) and whether DXY or CL moved 2+ sd yesterday
rngMult(float yr, bool big) => yr < 1 ? (big ? 1.07 : 0.92) : yr < 1.5 ? (big ? 1.16 : 1.06) : (big ? 1.51 : 1.33)

drawCard(table t, string h0, string h1, string pill, color hc, color pTx, color pBg, string pTip, array<string> K, array<string> V, array<string> W, array<string> P, array<color> C, array<string> keepM, string fnt, bool mob) =>
    t.clear(0, 0, 2, 9)
    t.cell(0, 0, h0, text_color = hdrTx(hc), bgcolor = hc, text_size = cSz, text_halign = text.align_left, text_font_family = fnt)
    t.cell(1, 0, h1, text_color = hdrTx(hc), bgcolor = hc, text_size = cSz, text_halign = text.align_left, text_font_family = fnt)
    t.cell(2, 0, pill, text_color = pTx, bgcolor = pBg, text_size = cSz, text_halign = text.align_center, text_font_family = fnt, tooltip = pTip)
    int r = 1
    for [i, k] in K
        if (not mob or keepM.includes(k)) and r < 10
            color vc = C.get(i)
            t.cell(0, r, k, text_color = cSub, text_size = cSz, text_halign = text.align_left, bgcolor = cBody, text_font_family = fnt, tooltip = P.get(i))
            t.cell(1, r, V.get(i), text_color = na(vc) ? cTxt : vc, text_size = cSz, text_halign = text.align_left, bgcolor = cBody, text_font_family = fnt, tooltip = P.get(i))
            t.cell(2, r, W.get(i), text_color = na(vc) ? cTxt : vc, text_size = cSz, text_halign = text.align_right, bgcolor = cBody, text_font_family = fnt, tooltip = P.get(i))
            r += 1
    t.set_frame_color(color.new(hc, 30))''')
# new macro rows: RANGE after WATCH
macRows = macRows.replace('''        addRow(K, V, W, P, C, "DXY", pxS(dNow)''', '''        float mxZ  = math.max(nz(dxZ), nz(clZ))
        bool  bigM = mxZ >= 2
        float mult = na(yRat) ? na : rngMult(yRat, bigM)
        float expR = adr20 * mult
        float dayR = dayH - dayL
        string who = nz(dxZ) >= nz(clZ) ? "DXY" : "CL"
        string rv = na(expR) ? "—" : "≈ " + str.tostring(expR, "#,###") + " pts" + (mob ? "" : " (" + str.tostring(mult, "0.00") + "× ADR)") + (bigM ? " · after " + who + " " + str.tostring(mxZ, "0.0") + " sd" : "")
        string rw = na(expR) ? "" : str.tostring(dayR / expR * 100, "0") + "% used"
        addRow(K, V, W, P, C, "RANGE", rv, rw, "Today's range to expect, for sizing targets and stops: ADR20 (" + str.tostring(adr20, "#,###") + " pts) × the average range / ADR20 that followed a day like yesterday. Yesterday: the index ran " + str.tostring(yRat, "0.00") + "× its ADR20, DXY moved " + str.tostring(dxZ, "0.0") + " and CL " + str.tostring(clZ, "0.0") + " daily standard deviations. NQ + ES + RTY 2018–26 (6,500 days): by yesterday's own range (< 1, 1–1.5, ≥ 1.5× ADR20) the day ran 0.92 / 1.06 / 1.33× ADR20, and 1.07 / 1.16 / 1.51× after DXY or CL moved 2+ sd (1 day in 10): a big dollar or oil day adds 0.10–0.19× ADR20 beyond the index's own range (p < 0.01; held in 2018–24 and 2025–26 and on each symbol). The regime itself made no difference to the range, and DXY's overnight move added nothing to the New York session beyond the overnight range. So far today: " + str.tostring(dayR, "#,###") + " pts.", bigM ? regC : nc)
        addRow(K, V, W, P, C, "DXY", pxS(dNow)''')
# DXY row on the fractal card, after CISD
fmRows = fmRows.replace('''            if fmProjI and s.cisd and not na(s.pjHit)''', '''            if fmP == 0
                string dv = na(s.dz) ? "—" : (s.dz > 0.5 ? "with C2" : s.dz < -0.5 ? "against C2" : "flat") + " · " + (s.dChg >= 0 ? "▲ " : "▼ ") + str.tostring(math.abs(s.dChg), "0.00") + "%" + (mob ? "" : " (" + str.tostring(math.abs(s.dz), "0.0") + " sd)")
                string dw = na(s.dz) ? "" : s.dz > 0.5 ? (s.phase == 3 ? "hold +1.7 · take +1.3" : "hold +1.7") : "no edge"
                addRow(K, V, W, P, C, "DXY", dv, mob ? "" : dw, "DXY across the C2 candle (C1's close to C2's close), against its typical 15-minute move over the last ~2 weeks. All tested DXY betas are negative, so DXY down suits a bullish C2 and DXY up a bearish one. NQ + ES + RTY 2023–26 (93k C2s, DX futures 5-minute): when DXY moved the setup's way by more than 0.5 sd (1 C2 in 4), C2's " + (bl ? "low" : "high") + " held through C3 1.7 points more often and C3 took C2's " + hs + " 1.3 points more often, at the same close location (p < 0.01; held in 2023–24 and 2025–26 and on each symbol; the take effect was weaker in 2025–26). DXY moving against the setup changed nothing. A small edge: it adds to the odds above, it does not replace them. On daily candles neither DXY nor CL made a difference.", not na(s.dz) and s.dz > 0.5 ? sc : nc)
            if fmProjI and s.cisd and not na(s.pjHit)''')
fmRows = fmRows.replace('''            addRow(K, V, W, P, C, "C2", (bl ? "▲ " : "▼ ") + (mob ? "" : (bl ? "bull · " : "bear · ") + fmNm + " ")''', '''            addRow(K, V, W, P, C, "C2", (bl ? "▲ " : "▼ ") + (mob ? "" : (bl ? "bull · " : "bear · "))''')
fmRows = fmRows.replace(''' + " (both together, same day).''', ''' + " (both together, same day).''')
card = '''var table TM = na
var table TF = na
if barstate.islast
    bool   mob  = layoutI == "Mobile"
    string fnt  = mob ? font.family_default : font.family_monospace
    string tNow = str.format_time(time, mob ? "MM/dd HH:mm" : "MM/dd · HH:mm", tz) + (mob ? "" : " ET")
    color  nc   = na
    // ── MACRO CARD
    if showMac
        if na(TM)
            TM := table.new(posOf(macPos), 3, 10, border_width = 0, frame_width = 1, frame_color = color.gray)
''' + '\n'.join(('    ' + l) if l.strip() else l for l in macCalc.split('\n')) + '''
        array<string> K = array.new<string>()
        array<string> V = array.new<string>()
        array<string> W = array.new<string>()
        array<string> P = array.new<string>()
        array<color>  C = array.new<color>()
''' + macRows + '''
        string regTip = "WEAK $: DXY below its " + str.tostring(maLen) + "-day average, the index follows oil. STRONG $: above it, the dollar leads. OIL SHOCK: CL's front month " + str.tostring(backThr, "0") + "%+ a year above the second and CL up " + str.tostring(clThr, "0") + "%+ in 20 days; both turn against the index. From yesterday's closes. Share of days 2018–26: weak 42%, strong 52%, shock 6% (28% in 2026)."
        drawCard(TM, mob ? "MACRO" : "HADŌ 99 · MACRO", tNow, regNm, regC, regC, lumOf(regC) > 165 ? #131722 : #ffffff, regTip, K, V, W, P, C, array.from("WATCH", "RANGE", "DXY", "OIL"), fnt, mob)
    else if not na(TM)
        TM.delete()
        TM := na
    // ── FRACTAL CARD
    if showFm and fmAct
        if na(TF)
            TF := table.new(posOf(fmPos), 3, 10, border_width = 0, frame_width = 1, frame_color = color.gray)
        array<string> K = array.new<string>()
        array<string> V = array.new<string>()
        array<string> W = array.new<string>()
        array<string> P = array.new<string>()
        array<color>  C = array.new<color>()
''' + fmRows + '''
        FS    lst  = fss.size() > 0 ? fss.last() : na
        bool  live = not na(lst) and lst.phase > 0 and not lst.dead
        color hc   = live ? (lst.bull ? fmBull : fmBear) : cNeu
        string pill = fmNm + (fmTest ? "" : mob ? "*" : " · untested")
        string pTip = "C2 → C3 on " + fmNm + " candles. " + (fmTest ? "Odds tested on this pair (NQ + ES + RTY 2018–26)." : "This chart timeframe was not tested; the odds shown are from the " + (fmP == 0 ? "1-minute" : "1-hour") + " chart.") + " The header takes the colour of a live setup. The macro regime made no difference to these odds."
        drawCard(TF, mob ? "FRACTAL" : "HADŌ 99 · FRACTAL", tNow, pill, hc, live ? hc : cTxt, live ? (lumOf(hc) > 165 ? #131722 : #ffffff) : cBody, pTip, K, V, W, P, C, array.from("C2", "C3", "CISD", "PROTECT"), fnt, mob)
    else if not na(TF)
        TF.delete()
        TF := na
'''
# fmRows came from 'if fmAct and cardShow...' (4-space) whose body is at 8 spaces; macRows body at 8 spaces: both fit under the new 4-space ifs
S2 = head + '\n' + card
S2 = S2.replace('''// Two parts. MACRO:''', '''// Two cards. MACRO:''')
open('/home/claude/xa/Hado_99.pine', 'w').write(S2)
print('ok', len(S2.splitlines()))
