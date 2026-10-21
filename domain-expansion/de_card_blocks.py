# Patch blocks for Domain Expansion v8 (exec'd by patch_de_card.py; uses rep(), s, P, POS8)

# ── 1. inputs, after the 08:00 UK open
rep('''colUK   = input.color(color.new(color.gray, 30), "", inline = "uk", group = g_E, display = display.none)
''', '''colUK   = input.color(color.new(color.gray, 30), "", inline = "uk", group = g_E, display = display.none)

var g_C = "London card"
showCard = input.bool(true, "London card", inline = "lc", group = g_C, tooltip = "02:00 to 17:00 ET. Live from 02:30: the domain range and today's tier, the expected London range and how much of it is done, the furthest SD so far, the live odds of 2 SD by 04:59, and how often the London high and low were already in at this point. After 05:00: the London result and the London high and low into New York.\\n\\nOdds: NQ + ES + RTY 1-minute 2018–26, 6,135 London sessions, steady in 2018–24 and 2025–26 and on each symbol. They are shown at the default settings they were measured on (domain 02:00–02:30, London to 05:00, 2 SD at the London extreme, coiled at 0.20, ATR of 5 overnights with true range) and hidden otherwise.", display = display.none)
cardPos  = input.string("Top right", "", options = @POS8@, inline = "lc", group = g_C, display = display.none)
cardSzI  = input.string("Small", "Card text", options = ["Tiny", "Small", "Normal"], group = g_C, display = display.none)
showHist = input.bool(true, "Recent London sessions", inline = "rh", group = g_C, tooltip = "One row per London session, newest first: tier, the result at 05:00, the furthest SD past the domain range (▲ above, ▼ below) and the London range (02:00–04:59) in points. Built from the chart's own history, so a 1-minute chart lists the days it has loaded.", display = display.none)
histPos  = input.string("Bottom right", "", options = @POS8@, inline = "rh", group = g_C, display = display.none)
histN    = input.int(10, "last", minval = 3, maxval = 30, inline = "rh", group = g_C, display = display.none)

var g_N = "London → New York"
showCarry = input.bool(true, "Carry the London high / low to 11:00 ET", group = g_N, tooltip = "The London high and low (02:00–04:59) drawn from 05:00 to 11:00 ET, each marked when it is taken.\\n\\nNQ + ES + RTY 2018–26: NY AM (09:30–10:59) took the London high on 66% of sessions and the low on 62%. By 11:00 (from 05:00): 75% and 71%. At least one of the two 99%, both 48%. Steady in 2018–24 and 2025–26 and on each symbol.", display = display.none)

var g_AL = "Alerts · one alert on \\"Any alert() function call\\" covers these"
alDR  = input.bool(true, "Domain range set (02:30), with the tier", group = g_AL, display = display.none)
alBrk = input.bool(true, "First break in the execution window", group = g_AL, display = display.none)
alExp = input.bool(true, "Expansion line reached", group = g_AL, display = display.none)
alEq  = input.bool(true, "Equal highs / lows swept", group = g_AL, display = display.none)
alRes = input.bool(true, "London result (05:00)", group = g_AL, display = display.none)
alNY  = input.bool(true, "London high / low taken before 11:00", group = g_AL, display = display.none)
'''.replace('@POS8@', POS8))

# ── 2. card styling helpers, after the label size
rep('''tSize = lblSize == "Tiny" ? size.tiny : lblSize == "Normal" ? size.normal : size.small
''', '''tSize = lblSize == "Tiny" ? size.tiny : lblSize == "Normal" ? size.normal : size.small
cSz   = cardSzI == "Tiny" ? size.tiny : cardSzI == "Normal" ? size.normal : size.small
cBody = isDark ? #161a23 : #f4f6f9
cSub  = isDark ? #8a93a6 : #5d6476
posOf(string p) =>
    switch p
        "Top left"      => position.top_left
        "Top center"    => position.top_center
        "Top right"     => position.top_right
        "Middle left"   => position.middle_left
        "Middle right"  => position.middle_right
        "Bottom left"   => position.bottom_left
        "Bottom center" => position.bottom_center
        => position.bottom_right
gauge(float f) =>
    int k = int(math.round(math.max(0.0, math.min(1.0, f)) * 8))
    str.repeat("█", k) + str.repeat("░", 8 - k)
pctI(float v) => na(v) ? "—" : str.tostring(math.round(v)) + "%"
''')

# ── 3. the card's data tables, after sdTicked()
rep('''sdTicked(float k) =>
    (sd10 and k == 1.0) or (sd15 and k == 1.5) or (sd20 and k == 2.0) or (sd25 and k == 2.5) or (sd30 and k == 3.0) or (sd40 and k == 4.0) or (sd50 and k == 5.0)
''', '''sdTicked(float k) =>
    (sd10 and k == 1.0) or (sd15 and k == 1.5) or (sd20 and k == 2.0) or (sd25 and k == 2.5) or (sd30 and k == 3.0) or (sd40 and k == 4.0) or (sd50 and k == 5.0)

// London card tables: NQ + ES + RTY 1-minute 2018–26, 6,135 sessions, split by coiled (domain range ÷ overnight ATR(5)
// at or below 0.20) or not. Rows = checkpoints 02:30, 02:45 … 04:45 ET, read between rows by time.
// LV: % that reached 2 SD past the domain range by 04:59, by the furthest SD so far (<0.5, 0.5–1, 1–1.5, 1.5–2).
// IN: % whose London high (or low) was already in, by price's distance from it in domain ranges (<0.25, 0.25–0.5,
// 0.5–1, 1–2, 2+). Highs and lows pooled (they read alike).
parsePct(string s) =>
    out = array.new<float>()
    for x in str.split(s, ",")
        out.push(str.tonumber(x))
    out
var array<float> LVO = parsePct("@LVO@")
var array<float> LVC = parsePct("@LVC@")
var array<float> INO = parsePct("@INO@")
var array<float> INC = parsePct("@INC@")
tblAt(array<float> a, int ncol, float pos, int col) =>
    float p  = math.max(0.0, math.min(9.0, pos))
    int   i0 = int(math.floor(p))
    int   i1 = math.min(9, i0 + 1)
    float f  = p - i0
    a.get(i0 * ncol + col) * (1 - f) + a.get(i1 * ncol + col) * f
'''.replace('@LVO@', P['LV_O']).replace('@LVC@', P['LV_C']).replace('@INO@', P['IN_O']).replace('@INC@', P['IN_C']))

# ── 4. ADR20 from daily bars (as Kyōka), for the 05:00 summary
rep('''[atrPct, atrPts, cbPts] = request.security(syminfo.tickerid, "15", nightCtx(), lookahead = barmerge.lookahead_on)
''', '''[atrPct, atrPts, cbPts] = request.security(syminfo.tickerid, "15", nightCtx(), lookahead = barmerge.lookahead_on)
// ADR20 of the trading day from daily bars (the CME 18:00–17:00 day), for the London summary
float adrD = request.security(ticker.modify(syminfo.tickerid, backadjustment = backadjustment.off), "D", ta.sma(high - low, 20)[1], lookahead = barmerge.lookahead_on)
''')

# ── 5. per-day flags, reset when the domain range is set; alert at 02:30
rep('''var float lonHi   = na
var float lonLo   = na
''', '''var float lonHi   = na
var float lonLo   = na
var bool  expHit  = true    // the expansion line reached today
var int   expT    = na
var int   eqHn    = 0       // equal-high / equal-low zones drawn today, and how many London swept
var int   eqLn    = 0
var int   eqHs    = 0
var int   eqLs    = 0
var int   lonDay  = na      // the trading day whose London has finished (05:00)
var float lH5     = na      // the London high / low at 05:00
var float lL5     = na
var int   nyHt    = na      // when New York took them
var int   nyLt    = na
var int   resV    = 0       // 05:00 result: 1 up · −1 down · 0 none
var float resSD   = na      // the furthest SD past the range, signed by side
''')
rep('''    brkDone := false
    lonHi   := high
    lonLo   := low
''', '''    brkDone := false
    lonHi   := high
    lonLo   := low
    expHit  := false
    expT    := na
    eqHn    := 0
    eqLn    := 0
    eqHs    := 0
    eqLs    := 0
''')
rep('''    mkEvent(dH, verdict + oddsTxt + "\\n" + f1Txt + "\\n" + cbTxt, tc, true)
''', '''    mkEvent(dH, verdict + oddsTxt + "\\n" + f1Txt + "\\n" + cbTxt, tc, true)
    if alDR
        alert(syminfo.ticker + " · Domain range set " + str.tostring(math.round(rD)) + " pts (" + str.tostring(dH, format.mintick) + " / " + str.tostring(dL, format.mintick) + ") · " + str.replace(verdict, "◆◆ ", "") + oddsTxt, alert.freq_once_per_bar)
''')
rep('''                        z = cand.remove(best)
                        cz = byTier ? tc : (isH ? colEQH : colEQL)
''', '''                        z = cand.remove(best)
                        cz = byTier ? tc : (isH ? colEQH : colEQL)
                        if isH
                            eqHn += 1
                        else
                            eqLn += 1
''')

# ── 6. first break: detected even with its label off, so the alert can fire
rep('''if showBrk and inEx and not brkDone and dDay == dayCount
    if high > dH and low < dL
        brkDone := true
        mkEvent(high, "Both sides " + hhmm(time), qCol, true)
    else if high > dH
        brkDone := true
        mkEvent(high, "▲ Break " + hhmm(time), qCol, true)
    else if low < dL
        brkDone := true
        mkEvent(low, "▼ Break " + hhmm(time), qCol, false)
''', '''if inEx and not brkDone and dDay == dayCount and (high > dH or low < dL)
    brkDone := true
    string bTx = high > dH and low < dL ? "Both sides " : high > dH ? "▲ Break " : "▼ Break "
    if showBrk
        mkEvent(low < dL and not (high > dH) ? low : high, bTx + hhmm(time), qCol, not (low < dL and not (high > dH)))
    if alBrk
        alert(syminfo.ticker + " · Domain Expansion · " + bTx + hhmm(time) + " ET of the domain range", alert.freq_once_per_bar)

// the expansion line reached (the line drawn at the SD or % needed, above or below)
if inLon and not inDR and dDay == dayCount and not expHit and not na(xUp) and (high >= xUp or low <= xDn)
    expHit := true
    expT   := time
    if alExp
        alert(syminfo.ticker + " · Domain Expansion · " + (high >= xUp ? "▲ " : "▼ ") + (modeSD ? sdTxtOf(expSD) : pctTxt(expPctE)) + " expansion line reached " + hhmm(time) + " ET", alert.freq_once_per_bar)
''')

# ── 7. the 05:00 result: worked out every day (label, alert, recent sessions, NY carry)
rep('''// result at the end of London
if showRes and lonEnd and dDay == dayCount and not na(rD)
    c5    = close[1]
    upX   = (lonHi - dH) / rD
    dnX   = (dL - lonLo) / rD
    isUp  = expMode == "SD at the London extreme" ? (upX >= expSD and upX >= dnX) : c5 >= xUp
    isDn  = expMode == "SD at the London extreme" ? (dnX >= expSD and dnX > upX) : c5 <= xDn
    exTxt = math.max(upX, dnX) <= 0 ? "stayed inside the range" : upX >= dnX ? "extreme " + sdTxtOf(upX) + " above" : "extreme " + sdTxtOf(dnX) + " below"
    head  = isUp ? "✓ Domain Expansion ▲" : isDn ? "✓ Domain Expansion ▼" : "✗ No expansion"
    mkEvent(c5, head + "\\n" + exTxt + " · close " + farTxt(c5), qCol, c5 >= (dH + dL) / 2)
''', '''// recent London sessions (newest last)
var array<int>   hK = array.new<int>()
var array<int>   hT = array.new<int>()
var array<int>   hR = array.new<int>()
var array<float> hS = array.new<float>()
var array<float> hP = array.new<float>()

// result at the end of London
if lonEnd and dDay == dayCount and not na(rD)
    c5    = close[1]
    upX   = (lonHi - dH) / rD
    dnX   = (dL - lonLo) / rD
    isUp  = expMode == "SD at the London extreme" ? (upX >= expSD and upX >= dnX) : c5 >= xUp
    isDn  = expMode == "SD at the London extreme" ? (dnX >= expSD and dnX > upX) : c5 <= xDn
    exTxt = math.max(upX, dnX) <= 0 ? "stayed inside the range" : upX >= dnX ? "extreme " + sdTxtOf(upX) + " above" : "extreme " + sdTxtOf(dnX) + " below"
    head  = isUp ? "✓ Domain Expansion ▲" : isDn ? "✓ Domain Expansion ▼" : "✗ No expansion"
    lonDay := dayCount
    lH5    := math.max(dH, lonHi)
    lL5    := math.min(dL, lonLo)
    nyHt   := na
    nyLt   := na
    resV   := isUp ? 1 : isDn ? -1 : 0
    resSD  := upX >= dnX ? math.max(upX, 0.0) : -dnX
    float lr = lH5 - lL5
    string adrTx = na(adrD) or adrD <= 0 ? "" : " · " + str.tostring(lr / adrD, "0.00") + " ADR"
    string eqTx  = eqHn + eqLn == 0 ? "" : " · EQH " + str.tostring(eqHs) + "/" + str.tostring(eqHn) + " EQL " + str.tostring(eqLs) + "/" + str.tostring(eqLn) + " swept"
    if showRes
        mkEvent(c5, head + "\\n" + exTxt + " · close " + farTxt(c5) + "\\nLondon " + str.tostring(math.round(lr)) + " pts" + adrTx + eqTx, qCol, c5 >= (dH + dL) / 2)
    if alRes
        alert(syminfo.ticker + " · London 05:00 · " + head + " · " + exTxt + " · range " + str.tostring(math.round(lr)) + " pts" + adrTx, alert.freq_once_per_bar)
    hK.push(time_tradingday)
    hT.push(tier)
    hR.push(resV)
    hS.push(resSD)
    hP.push(lr)
    if hK.size() > 30
        hK.shift()
        hT.shift()
        hR.shift()
        hS.shift()
        hP.shift()
    // the London high and low, carried to 11:00
    if showCarry
        color cc = byTier ? qCol : colRng
        lvH = Lv.new(line.new(time, lH5, time, lH5, xloc = xloc.bar_time, color = cc, style = line.style_solid, width = 2), label.new(time, lH5, "London high · NY AM 66% · by 11:00 75%", xloc = xloc.bar_time, style = label.style_label_left, color = #ffffff00, textcolor = txtCol, size = tSize, tooltip = "London high (02:00–04:59). NQ + ES + RTY 2018–26: NY AM (09:30–10:59) took it on 66% of sessions; by 11:00, 75%."), na, lH5, true, dayCount, false, true, true, "ny", cc)
        lvL = Lv.new(line.new(time, lL5, time, lL5, xloc = xloc.bar_time, color = cc, style = line.style_solid, width = 2), label.new(time, lL5, "London low · NY AM 62% · by 11:00 71%", xloc = xloc.bar_time, style = label.style_label_left, color = #ffffff00, textcolor = txtCol, size = tSize, tooltip = "London low (02:00–04:59). NQ + ES + RTY 2018–26: NY AM (09:30–10:59) took it on 62% of sessions; by 11:00, 71%."), na, lL5, false, dayCount, false, true, true, "ny", cc)
        store.push(lvH)
        store.push(lvL)
''')

# ── 8. every bar: New York lines run to 11:00; sweeps of equal highs / lows and of the London high / low are counted and alerted
rep('''nS = store.size()
if nS > 0''', '''inNYc = sessOn("0500-1100")
nS = store.size()
if nS > 0''')
rep('''        stopNow = lv.live and (lv.grp == "dr" or lv.grp == "eq") and not inLon''',
    '''        stopNow = lv.live and (((lv.grp == "dr" or lv.grp == "eq") and not inLon) or (lv.grp == "ny" and not inNYc))''')
rep('''            if lv.grp == "eq"
                lv.bx.set_right(time)''', '''            if lv.grp == "eq"
                lv.bx.set_right(time)''')
rep('''        if lv.watch and lv.live and not stopNow and not lv.hit and (lv.above ? (lv.grp == "eq" ? high > lv.y : high >= lv.y) : (lv.grp == "eq" ? low < lv.y : low <= lv.y))
            lv.hit := true
            if not na(lv.ln)
                lv.ln.set_style(line.style_dashed)
            if lv.grp == "eq"
                lv.bx.set_border_style(line.style_dashed)
                lv.bx.set_bgcolor(fade(lv.col))
                lv.lb.set_text(lv.lb.get_text() + " · swept " + hhmm(time))''', '''        bool strict = lv.grp == "eq" or lv.grp == "ny"
        if lv.watch and lv.live and not stopNow and not lv.hit and (lv.above ? (strict ? high > lv.y : high >= lv.y) : (strict ? low < lv.y : low <= lv.y))
            lv.hit := true
            if not na(lv.ln)
                lv.ln.set_style(line.style_dashed)
            if lv.grp == "eq"
                lv.bx.set_border_style(line.style_dashed)
                lv.bx.set_bgcolor(fade(lv.col))
                lv.lb.set_text(lv.lb.get_text() + " · swept " + hhmm(time))
                if lv.above
                    eqHs += 1
                else
                    eqLs += 1
                if alEq
                    alert(syminfo.ticker + " · London swept the overnight " + (lv.above ? "equal highs " : "equal lows ") + str.tostring(lv.y, format.mintick) + " at " + hhmm(time) + " ET", alert.freq_once_per_bar)
            if lv.grp == "ny"
                lv.lb.set_text((lv.above ? "London high" : "London low") + " · taken " + hhmm(time))
                if lv.above
                    nyHt := time
                else
                    nyLt := time
                if alNY
                    alert(syminfo.ticker + " · " + (lv.above ? "London high " : "London low ") + str.tostring(lv.y, format.mintick) + " taken at " + hhmm(time) + " ET", alert.freq_once_per_bar)''')

# ── 9. the London card and the recent-sessions table (drawn on the last bar)
s = s.rstrip('\n') + '''

// ═══════════════════════════════════════════════════════════════════
// LONDON CARD (02:00 → 17:00 ET) and RECENT LONDON SESSIONS
// ═══════════════════════════════════════════════════════════════════
int   mNow   = hour(time, tz) * 60 + minute(time, tz)
bool  defOn  = asset != "Custom" and drSess == "0200-0230" and lonSess == "0200-0500" and atrLen == 5 and useTR
bool  oddsOk = defOn and expMode == "SD at the London extreme" and expSD == 2.0 and coilMax == 0.20
bool  coiled = not na(coil) and coil <= 0.20
bH(float d) => d < 0.25 ? 0 : d < 0.5 ? 1 : d < 1.0 ? 2 : d < 2.0 ? 3 : 4
tierNm(int t) => t == 3 ? "BOTH" : t == 2 ? (modeSD ? "COILED" : "VOLATILE") : t == 1 ? "CBDR" : "NEITHER"
tierC(int t) => t == 3 ? colBoth : t == 2 ? colF1 : t == 1 ? colCB : colN
var table TC = na
var table TH = na
cRow(table t, int r, string k, string v, string w, string tip, color vc) =>
    t.cell(0, r, k, text_color = cSub, text_size = cSz, text_halign = text.align_left, bgcolor = cBody, text_font_family = font.family_monospace, tooltip = tip)
    t.cell(1, r, v, text_color = na(vc) ? txtCol : vc, text_size = cSz, text_halign = text.align_left, bgcolor = cBody, text_font_family = font.family_monospace, tooltip = tip)
    t.cell(2, r, w, text_color = na(vc) ? txtCol : vc, text_size = cSz, text_halign = text.align_right, bgcolor = cBody, text_font_family = font.family_monospace, tooltip = tip)
cHead(table t, string a, string b, string pill, color bg) =>
    t.cell(0, 0, a, text_color = #ffffff, bgcolor = bg, text_size = cSz, text_halign = text.align_left, text_font_family = font.family_monospace)
    t.cell(1, 0, b, text_color = #ffffff, bgcolor = bg, text_size = cSz, text_halign = text.align_left, text_font_family = font.family_monospace)
    t.cell(2, 0, pill, text_color = bg, bgcolor = #ffffff, text_size = cSz, text_halign = text.align_center, text_font_family = font.family_monospace)

if barstate.islast and showCard
    if na(TC)
        TC := table.new(posOf(cardPos), 3, 9, border_width = 0, frame_width = 1, frame_color = color.new(qCol, 30))
    TC.clear(0, 0, 2, 8)
    TC.set_frame_color(color.new(qCol, 30))
    bool today  = dDay == dayCount
    bool live   = today and inLon and not inDR
    bool done   = lonDay == dayCount and not inLon
    string nowT = hhmm(time) + " ET"
    if inDR
        float fH = dH
        float fL = dL
        cHead(TC, "◇ DOMAIN EXPANSION", "LONDON · " + nowT, "FORMING", color.gray)
        cRow(TC, 1, "RANGE", "forming · " + str.tostring(math.round(fH - fL)) + " pts so far", "to 02:29", "The domain range: 02:00–02:29 ET. The tier is checked at 02:30.", na)
        cRow(TC, 2, "ATR", na(atrPts) ? "overnight ATR warming up" : "overnight ATR " + str.tostring(math.round(atrPts)) + " pts", "", "Overnight ATR(" + str.tostring(atrLen) + "): average overnight (18:00 → 02:29) true range. Coiled = domain range ÷ this ≤ " + str.tostring(coilMax, "0.00") + ".", na)
    else if live
        float lHs  = math.max(dH, lonHi)
        float lLs  = math.min(dL, lonLo)
        float upS  = math.max(0.0, (lonHi - dH) / rD)
        float dnS  = math.max(0.0, (dL - lonLo) / rD)
        float far  = math.max(upS, dnS)
        float pos  = (mNow - 150) / 15.0
        float lrE  = defOn and not na(atrPts) ? 1.794 * math.pow(rD, 0.497) * math.pow(atrPts, 0.437) : na
        // the live odds of 2 SD by 04:59
        float p2   = not oddsOk ? na : far >= 2.0 ? 100.0 : pos < 1 and far < 0.5 ? (tier == 3 ? 63.0 : tier == 2 ? 47.0 : tier == 1 ? 39.0 : 19.0) : tblAt(coiled ? LVC : LVO, 4, pos, int(math.min(3, math.floor(far / 0.5))))
        // the London high / low already in
        float dHi  = (lHs - close) / rD
        float dLo  = (close - lLs) / rD
        float pHi  = defOn ? tblAt(coiled ? INC : INO, 5, pos, bH(dHi)) : na
        float pLo  = defOn ? tblAt(coiled ? INC : INO, 5, pos, bH(dLo)) : na
        cHead(TC, (tier == 3 ? "◆◆" : tier >= 1 ? "◆" : "◇") + " DOMAIN EXPANSION", "LONDON · " + nowT, tierNm(tier), qCol)
        string cTx = na(coil) ? "coil n/a" : "coil " + str.tostring(coil, "0.00") + (qualC ? " ✓" : " ✗")
        string bTx = na(cbPts) ? "CBDR n/a" : "CBDR " + str.tostring(cbPts / rD, "0.0") + "×" + (cbOK ? " ✓" : " ✗")
        cRow(TC, 1, "RANGE", str.tostring(math.round(rD)) + " pts · " + cTx, bTx, "Domain range 02:00–02:29 ET and the two factors checked at 02:30: coiled = range ÷ overnight ATR(" + str.tostring(atrLen) + ") ≤ " + str.tostring(coilMax, "0.00") + "; CBDR wide = the 14:00–20:00 range ≥ " + str.tostring(cbMult, "0.0") + " domain ranges. 2 SD at the London extreme, NQ + ES + RTY 2018–26: both 63% · coiled only 47% · CBDR only 39% · neither 19% (2025–26: 61 · 39 · 38 · 17).", na)
        cRow(TC, 2, "EXPECT", na(lrE) ? "London range —" : "London ≈ " + str.tostring(math.round(lrE)) + " pts", na(lrE) ? "" : str.tostring(math.round(lrE * 0.778)) + "–" + str.tostring(math.round(lrE * 1.293)), "Expected London range (02:00–04:59), from the domain range and the overnight ATR: 1.79 × range^0.50 × ATR^0.44 points, fitted on NQ + ES + RTY 2018–24. Middle half shown right. Checked on 2025–26: 48% of sessions landed in the middle half, R² 0.87; 2025–26 ranges ran about 6% under the estimate.", na)
        float lrNow = lHs - lLs
        cRow(TC, 3, "DONE", gauge(na(lrE) ? 0.0 : lrNow / lrE) + " " + str.tostring(math.round(lrNow)) + " pts", na(lrE) ? "" : pctI(100 * lrNow / lrE), "London range so far (02:00 → now) against the expected range. Past 100%, London has already done a typical session's work.", na)
        cRow(TC, 4, "SD", "▲ " + str.tostring(upS, "0.0") + " · ▼ " + str.tostring(dnS, "0.0"), "furthest", "The furthest price has gone past the domain range since 02:30, in domain ranges (SD), above and below.", na)
        cRow(TC, 5, "2 SD", expHit ? "✓ " + (modeSD ? sdTxtOf(expSD) : pctTxt(expPctE)) + " reached " + hhmm(expT) : "by 04:59", expHit ? "" : pctI(p2), "How often London went on to reach 2 SD past the domain range by 04:59, from this time and the furthest SD so far" + (coiled ? " (coiled days)" : " (days not coiled)") + ". At 02:30 it is the tier's rate. NQ + ES + RTY 2018–26, read between 15-minute checkpoints." + (oddsOk ? "" : " Shown only at the default settings."), expHit ? qCol : na)
        cRow(TC, 6, "HIGH", "London high " + str.tostring(dHi, "0.0") + " SD away", "in " + pctI(pHi), "How often the London high (02:00–04:59) was already in at this time, with price this far below it (in domain ranges). NQ + ES + RTY 2018–26." + (coiled ? " Coiled days." : " Days not coiled."), na)
        cRow(TC, 7, "LOW", "London low " + str.tostring(dLo, "0.0") + " SD away", "in " + pctI(pLo), "How often the London low (02:00–04:59) was already in at this time, with price this far above it (in domain ranges). NQ + ES + RTY 2018–26." + (coiled ? " Coiled days." : " Days not coiled."), na)
    else if done
        float lr = lH5 - lL5
        cHead(TC, (resV != 0 ? "✓" : "✗") + " DOMAIN EXPANSION", "LONDON DONE · " + nowT, tierNm(tier), qCol)
        cRow(TC, 1, "RESULT", resV == 1 ? "▲ expansion" : resV == -1 ? "▼ expansion" : "no expansion", (resSD >= 0 ? "▲ " : "▼ ") + str.tostring(math.abs(resSD), "0.0") + " SD", "The result at 05:00 by the measure in settings, and the furthest SD past the domain range.", resV != 0 ? qCol : na)
        cRow(TC, 2, "RANGE", "London " + str.tostring(math.round(lr)) + " pts", na(adrD) or adrD <= 0 ? "" : str.tostring(lr / adrD, "0.00") + " ADR", "London range 02:00–04:59 against ADR20 of the trading day (daily bars). NQ + ES + RTY 2018–26: median 0.24, middle half 0.18–0.34.", na)
        cRow(TC, 3, "SWEPT", eqHn + eqLn == 0 ? "no equal highs / lows" : "EQH " + str.tostring(eqHs) + "/" + str.tostring(eqHn) + " · EQL " + str.tostring(eqLs) + "/" + str.tostring(eqLn), "", "Overnight equal-high and equal-low zones drawn at 02:30 and how many London traded through.", na)
        cRow(TC, 4, "NY HIGH", str.tostring(lH5, format.mintick), na(nyHt) ? (mNow < 660 ? "open · 75%" : "not taken") : "taken " + hhmm(nyHt), "The London high, carried to 11:00. NQ + ES + RTY 2018–26: taken by 11:00 on 75% of sessions (NY AM 09:30–10:59: 66%).", na(nyHt) ? na : qCol)
        cRow(TC, 5, "NY LOW", str.tostring(lL5, format.mintick), na(nyLt) ? (mNow < 660 ? "open · 71%" : "not taken") : "taken " + hhmm(nyLt), "The London low, carried to 11:00. NQ + ES + RTY 2018–26: taken by 11:00 on 71% of sessions (NY AM 09:30–10:59: 62%).", na(nyLt) ? na : qCol)
    else
        cHead(TC, "◇ DOMAIN EXPANSION", "LONDON · " + nowT, "NEXT", color.gray)
        cRow(TC, 1, "NEXT", "domain range 02:00–02:29 ET", "", "The card goes live at 02:30, when the tier is checked.", na)
        int nh = hK.size()
        if nh > 0
            int  lr0 = hR.get(nh - 1)
            cRow(TC, 2, "LAST", str.format_time(hK.get(nh - 1), "EEE dd", tz) + " · " + tierNm(hT.get(nh - 1)), (lr0 == 1 ? "▲ ✓ " : lr0 == -1 ? "▼ ✓ " : "✗ ") + str.tostring(math.round(hP.get(nh - 1))) + " pts", "The last London session: tier, result and range.", na)
if barstate.islast and showHist and hK.size() > 0
    int nh = hK.size()
    int nr = math.min(histN, nh)
    if na(TH)
        TH := table.new(posOf(histPos), 5, 32, border_width = 0, frame_width = 1, frame_color = color.new(color.gray, 60))
    TH.clear(0, 0, 4, 31)
    int ex = 0
    for i = nh - nr to nh - 1
        ex += hR.get(i) != 0 ? 1 : 0
    TH.cell(0, 0, "LONDON", text_color = #ffffff, bgcolor = color.new(#5e35b1, 0), text_size = cSz, text_halign = text.align_left, text_font_family = font.family_monospace)
    TH.cell(1, 0, "last " + str.tostring(nr), text_color = #ffffff, bgcolor = color.new(#5e35b1, 0), text_size = cSz, text_halign = text.align_left, text_font_family = font.family_monospace)
    TH.cell(2, 0, "", bgcolor = color.new(#5e35b1, 0))
    TH.cell(3, 0, "", bgcolor = color.new(#5e35b1, 0))
    TH.cell(4, 0, str.tostring(ex) + "/" + str.tostring(nr) + " expanded", text_color = #ffffff, bgcolor = color.new(#5e35b1, 0), text_size = cSz, text_halign = text.align_right, text_font_family = font.family_monospace, tooltip = "Sessions that met the expansion measure in settings at 05:00. NQ + ES + RTY 2018–26 at 2 SD at the London extreme: 37% of all sessions.")
    hdr = array.from("day", "tier", "05:00", "furthest", "range")
    for c = 0 to 4
        TH.cell(c, 1, hdr.get(c), text_color = cSub, bgcolor = cBody, text_size = cSz, text_halign = c == 0 ? text.align_left : text.align_right, text_font_family = font.family_monospace)
    int r = 2
    for i = nh - 1 to nh - nr
        int   rv = hR.get(i)
        float sv = hS.get(i)
        color tcI = tierC(hT.get(i))
        TH.cell(0, r, str.format_time(hK.get(i), "EEE dd", tz), text_color = txtCol, bgcolor = cBody, text_size = cSz, text_halign = text.align_left, text_font_family = font.family_monospace)
        TH.cell(1, r, tierNm(hT.get(i)), text_color = tcI, bgcolor = cBody, text_size = cSz, text_halign = text.align_right, text_font_family = font.family_monospace)
        TH.cell(2, r, rv == 1 ? "▲ ✓" : rv == -1 ? "▼ ✓" : "✗", text_color = rv != 0 ? tcI : cSub, bgcolor = cBody, text_size = cSz, text_halign = text.align_right, text_font_family = font.family_monospace)
        TH.cell(3, r, (sv >= 0 ? "▲ " : "▼ ") + str.tostring(math.abs(sv), "0.0") + " SD", text_color = txtCol, bgcolor = cBody, text_size = cSz, text_halign = text.align_right, text_font_family = font.family_monospace)
        TH.cell(4, r, str.tostring(math.round(hP.get(i))) + " pts", text_color = txtCol, bgcolor = cBody, text_size = cSz, text_halign = text.align_right, text_font_family = font.family_monospace)
        r += 1
'''
