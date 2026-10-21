"""Shikai / Bankai Session Map v2 card overhaul (SB_v1.pine → Shikai_Bankai_Session_Map.pine).
- View first: card theme (cards) vs chart text colour (chart, follows the chart background), Layout Desktop / Mobile,
  card on/off, position (8 places), card text size. The old Stats table group is gone.
- the 25-row chart-history table (8 days on chart, 66.7% of 6 …) is replaced by a phased 3-column card with tested
  numbers (NQ + ES + RTY 1-minute 2018–26): midpoint and mirror (placebo) reach odds, live by time and distance in ADR20,
  London high / low taken, the London 25%, session ranges against typical, the regime as context. Mobile: 4 rows.
- mirror level drawn on the chart; prior-day state dropped (it did not hold against the placebo); ADR20 from daily bars.
Session candles, midpoint map, hot blocks, Bankai windows and markers are unchanged."""
import json, re

S = open('/home/claude/sb/SB_v1.pine').read()
T = json.load(open('/home/claude/sb/sb_tables.json'))


def rep(old, new, n=1):
    global S
    c = S.count(old)
    assert c == n, (c, old[:100])
    S = S.replace(old, new)


def cut(a, b, keep_b=True):
    global S
    i = S.index(a)
    j = S.index(b, i)
    S = S[:i] + S[j:]


POS = '["Top left", "Top center", "Top right", "Middle left", "Middle right", "Bottom left", "Bottom center", "Bottom right"]'
# ── View
rep('''themeI  = input.string("Auto", "Theme", options = ["Auto", "Dark", "Light"], group = g_D, tooltip = "Auto follows the chart background. Text and the colours left at their default follow it.", display = display.none)
lblSize = input.string("Small", "Text size", options = ["Tiny", "Small", "Normal"], group = g_D, display = display.none)
txtColI = input.color(#000001, "Text colour", group = g_D, tooltip = "Left at the default it follows the theme; pick any colour to override.", display = display.none)
''', '''themeI   = input.string("Auto", "Card theme", options = ["Auto", "Dark", "Light"], group = g_D, tooltip = "The card. Auto follows the chart background. Its text always follows this theme, so it stays readable whatever chart text colour you pick.", display = display.none)
layoutI  = input.string("Desktop", "Layout", options = ["Desktop", "Mobile"], group = g_D, tooltip = "Mobile folds the card to four rows in the narrower default font for a phone; the rest stays in the tooltips. Chart layouts sync across devices, so keep a separate chart layout for the phone.", display = display.none)
showCard = input.bool(true, "Card", inline = "cd", group = g_D, display = display.none)
cardPos  = input.string("Bottom left", "", options = ''' + POS + ''', inline = "cd", group = g_D, tooltip = "Bottom left keeps the card clear of the session candles, which sit right of price.", display = display.none)
cardSzI  = input.string("Small", "Card text", options = ["Tiny", "Small", "Normal"], group = g_D, display = display.none)
lblSize  = input.string("Small", "Chart text size", options = ["Tiny", "Small", "Normal"], group = g_D, display = display.none)
txtColI  = input.color(#000001, "Chart text colour", group = g_D, tooltip = "The labels on the chart. Left at the default it follows the chart background; pick any colour to override. The card keeps its own text colour.", display = display.none)
''')
rep('''avgLen    = input.int(20, "Prior-day state: average length (days)", minval = 2, group = g_L, display = display.none)
''', '''showMir   = input.bool(true, "Mirror level", inline = "mr", group = g_L, tooltip = "The same distance from the 09:30 open as the midpoint, on the other side of the open: the placebo the midpoint is tested against, and the carry foothold on discount opens (see the card's MIRROR row).", display = display.none)
colMir    = input.color(color.new(color.gray, 20), "", inline = "mr", group = g_L, display = display.none)
''')
cut('var g_T = "Stats table"', '// Theme: Auto follows')

# ── Theme: the card follows the card theme, the chart follows the chart background
rep('''isDark = themeI == "Dark" or (themeI == "Auto" and bgLum < 128)
autoC(color c) => color.r(c) == 0 and color.g(c) == 0 and color.b(c) == 1
fgAuto = isDark ? #d1d4dc : #131722
txtCol = autoC(txtColI) ? fgAuto : txtColI
colCandle = autoC(colCandleI) ? fgAuto : colCandleI
colVline  = autoC(colVlineI) ? color.new(fgAuto, 70) : colVlineI
tblBg     = autoC(tblBgI) ? (isDark ? #161a23 : #f4f6f9) : tblBgI
tblTxt    = autoC(tblTxtI) ? fgAuto : tblTxtI
tblBdr    = autoC(tblBdrI) ? (isDark ? #2a2e39 : #d1d4dc) : tblBdrI
''', '''isDark = themeI == "Dark" or (themeI == "Auto" and bgLum < 128)      // the card
autoC(color c) => color.r(c) == 0 and color.g(c) == 0 and color.b(c) == 1
fgAuto = bgLum < 128 ? #d1d4dc : #131722                              // the chart: follows the chart background
txtCol = autoC(txtColI) ? fgAuto : txtColI
colCandle = autoC(colCandleI) ? fgAuto : colCandleI
colVline  = autoC(colVlineI) ? color.new(fgAuto, 70) : colVlineI
cTxt  = isDark ? #d1d4dc : #131722
cBody = isDark ? #161a23 : #f4f6f9
cSub  = isDark ? #8a93a6 : #5d6476
lumOf(color c) => 0.299 * color.r(c) + 0.587 * color.g(c) + 0.114 * color.b(c)
hdrTx(color c) => lumOf(c) > 165 ? #131722 : #ffffff
''')

# ── prior-day state and the chart-history arrays go
cut('// ═══════════════════════════════════════════════════════════════════\n// PRIOR-DAY STATE', '// ═══════════════════════════════════════════════════════════════════\n// SESSION CANDLES')
cut('// ── Day history for the stats table', '// Shikai / Bankai day record')
rep('''var int   midT  = -1
var bool  mid11 = false
''', '''var int   midT  = -1
var bool  mid11 = false
var float sbMir = na      // the mirror: the midpoint's distance from the open, on the other side
var int   mirT  = -1
var int   lhT   = na      // London high / low taken after 05:00, and the London 25% traded
var int   llT   = na
var int   q25T  = na
''')
cut('var array<bool> hUp    = array.new<bool>()', 'trackS(Sess s, bool inS, bool sStart) =>')
# ADR20 of the trading day from daily bars (the CME 18:00–17:00 day)
rep('''lvl25(float o, float c) =>''', '''float adrD = request.security(ticker.modify(syminfo.tickerid, backadjustment = backadjustment.off), "D", ta.sma(high - low, 20)[1], lookahead = barmerge.lookahead_on)

lvl25(float o, float c) =>''')

# ── 09:30: mirror level
rep('''    sbT930 := time
    midT := -1
    mid11 := false
''', '''    sbT930 := time
    midT := -1
    mid11 := false
    sbMir := 2 * O - mid
    mirT := -1
''')
rep('''    midLv := mkLv(t0, mid, colMid, 2, line.style_solid, stampOf(time) + (isBankai ? " Bankai mid" : " Shikai mid"), "ON", up, "mid")
''', '''    midLv := mkLv(t0, mid, colMid, 2, line.style_solid, stampOf(time) + (isBankai ? " Bankai mid" : " Shikai mid"), "ON", up, "mid")
    if showMir
        mkLv(time, 2 * O - mid, colMir, 1, line.style_dotted, stampOf(time) + " mirror", "ON", not up, "mir")
''')
rep('''    if midT < 0 and tMid
        midT  := m
        mid11 := inNY
''', '''    if midT < 0 and tMid
        midT  := m
        mid11 := inNY
    if mirT < 0 and (sbUp ? low <= sbMir : high >= sbMir)
        mirT := m

// ── London high / low taken after 05:00, and the London 25% traded (from 05:00 to 16:59)
if onStart
    lhT  := na
    llT  := na
    q25T := na
if not na(sL.o) and sL.day == dayCount and not inCL and (inON or inShk)
    if na(lhT) and high > sL.h
        lhT := time
    if na(llT) and low < sL.l
        llT := time
    if na(q25T) and sL.c != sL.o and (sL.c > sL.o ? low <= lvl25(sL.o, sL.c) : high >= lvl25(sL.o, sL.c))
        q25T := time
''')

# ── chart labels at nearly the same price share one label (they printed over each other)
rep('''    string tag       // "mid", "lvl"
''', '''    string tag       // "mid", "lvl"
    string tx        // the label's own text (labels at nearly the same price are merged on the last bar)
''')
rep('''label.new(time, y, txt, xloc = xloc.bar_time, style = label.style_label_left, color = #ffffff00, textcolor = txtCol, size = tSize), y, above, kind, dayCount, false, true, tag)''',
    '''label.new(time, y, txt, xloc = xloc.bar_time, style = label.style_label_left, color = #ffffff00, textcolor = txtCol, size = tSize), y, above, kind, dayCount, false, true, tag, txt)''')
rep('''        r.lb.set_text(txt)
''', '''        r.lb.set_text(txt)
        r.tx    := txt
''')
rep('''var array<label> cLb = array.new<label>()
''', '''var array<label> cLb = array.new<label>()
var array<label> sLb = array.new<label>()     // session-line labels at the last bar, for the merge
var array<float> sLy = array.new<float>()
''')
rep('''        cLb.push(label.new(time, q, stampOf(s.t0) + " " + nm + " 25%", xloc = xloc.bar_time, style = label.style_label_left, color = #ffffff00, textcolor = col25, size = tSize))
''', '''        cLb.push(label.new(time, q, stampOf(s.t0) + " " + nm + " 25%", xloc = xloc.bar_time, style = label.style_label_left, color = #ffffff00, textcolor = col25, size = tSize))
        sLb.push(cLb.last())
        sLy.push(q)
''')
rep('''        cLb.push(label.new(time, h50, stampOf(s.t0) + " " + nm + " 50%", xloc = xloc.bar_time, style = label.style_label_left, color = #ffffff00, textcolor = col50, size = tSize))
''', '''        cLb.push(label.new(time, h50, stampOf(s.t0) + " " + nm + " 50%", xloc = xloc.bar_time, style = label.style_label_left, color = #ffffff00, textcolor = col50, size = tSize))
        sLb.push(cLb.last())
        sLy.push(h50)
''')
rep('''    while cLb.size() > 0
        cLb.pop().delete()
''', '''    while cLb.size() > 0
        cLb.pop().delete()
    sLb.clear()
    sLy.clear()
''')
rep('''    if showL
        drawSessLines(sL, "London")
''', '''    if showL
        drawSessLines(sL, "London")
    // labels within 2.5% of ADR20 of each other share one label, stacked, so they never print over each other
    float thr = 0.025 * nz(adrD, 0)
    array<float> mY = array.new<float>()
    array<label> mL = array.new<label>()
    for lv in store
        if lv.live and lv.day == dayCount
            placeLbl(lv.lb, lv.y, lv.tx, mY, mL, thr)
    for [j, l] in sLb
        placeLbl(l, sLy.get(j), l.get_text(), mY, mL, thr)
''')
rep('''drawCandle(Sess s, int x1, int x2, string nm, bool lvls) =>''', '''// a label prints on its own, or joins the label already within `thr` of it
placeLbl(label lb, float y, string tx, array<float> sY, array<label> sLs, float thr) =>
    int jm = -1
    for [j, yy] in sY
        if jm < 0 and math.abs(yy - y) <= thr
            jm := j
    if jm >= 0
        sLs.get(jm).set_text(sLs.get(jm).get_text() + "\\n" + tx)
        lb.set_text("")
    else
        lb.set_text(tx)
        sY.push(y)
        sLs.push(lb)

drawCandle(Sess s, int x1, int x2, string nm, bool lvls) =>''')

# ── the card replaces the stats table
i = S.index('// ═══════════════════════════════════════════════════════════════════\n// STATS TABLE')
S = S[:i] + open('/home/claude/sb/sb_card.pine').read()

tabs = '\n'.join(f'var array<float> {k} = parseNum("' + ','.join(str(x) for r in T[k] for x in r) + '")' for k in ('SHMA', 'SHMB', 'SHRA', 'SHRB', 'BKMA', 'BKMB', 'BKRA', 'BKRB', 'L11', 'L17'))
S = S.replace('__TABLES__', tabs)
for w in ('tblBg', 'tblTxt', 'tblBdr', 'hUp', 'hMidT', 'prevState', 'avgLen', 'lookback'):
    assert not re.search(r'\b' + w + r'\b', S), w
open('/home/claude/sb/Shikai_Bankai_Session_Map.pine', 'w').write(S)
print('ok', len(S.splitlines()))
