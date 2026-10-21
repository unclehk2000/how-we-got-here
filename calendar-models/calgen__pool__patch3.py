"""Desgarrón v3: dealing-range fix (na key compare), pre-release range → 07:00–09:00 dealing range on the break, structure
inputs, longer release window, anchored NFP marker, ATH CE into the next session's 11:00, Grimmjow (narrow) findings."""
P = '/home/claude/hm/calgen/Desgarron.pine'
S = open(P, encoding='utf-8').read()
def rep(old, new, n=1):
    global S
    c = S.count(old)
    assert c == n, (c, old[:140])
    S = S.replace(old, new)
def cut(a, b, new):
    global S
    i = S.index(a); j = S.index(b, i)
    S = S[:i] + new + S[j:]

# ── inputs: model structure
cut('cLvl    = input.color(#ffb300, "Levels"', '\ngrpK = "Event clock', '''cLvl    = input.color(#ffb300, "Levels", group = grpS, inline = "s1", display = display.none)
cGh     = input.color(#ff7043, "Model", group = grpS, inline = "s1", display = display.none)
lblI    = input.string("Tiny", "Labels", options = ["Tiny", "Small", "Normal"], group = grpS, inline = "s1", display = display.none)
offI    = 12
showDR0 = input.bool(true, "Pre-release range 07:00–08:29", group = grpS, inline = "d0", display = display.none)
cDR0    = input.color(#90a4ae, "", group = grpS, inline = "d0", display = display.none)
stDR0   = input.string("Dashed", "", options = ["Solid", "Dashed", "Dotted"], group = grpS, inline = "d0", tooltip = "Drawn live from 07:00 and fixed at 08:29. When the release takes one of its sides it stops at that bar and the 07:00–09:00 dealing range takes over.", display = display.none)
showDR  = input.bool(true, "Dealing range 07:00–09:00", group = grpS, inline = "d1", display = display.none)
cDR     = input.color(#ffb300, "", group = grpS, inline = "d1", display = display.none)
stDR    = input.string("Solid", "", options = ["Solid", "Dashed", "Dotted"], group = grpS, inline = "d1", display = display.none)
wDR     = input.int(1, "", minval = 1, maxval = 4, group = grpS, inline = "d1", tooltip = "Created when the release breaks the pre-release range (at 09:00 if it never does): drawn from 07:00, it follows the high and low until 09:00, then stays fixed.", display = display.none)
drEq    = input.bool(true, "50%", group = grpS, inline = "d2", display = display.none)
drFill  = input.bool(false, "Fill", group = grpS, inline = "d2", display = display.none)
drEnd   = input.string("16:14", "Ranges run to", options = ["11:00", "16:14", "17:00"], group = grpS, inline = "d2", display = display.none)
relEnd  = input.string("09:00", "Release window 08:30 →", options = ["08:45", "08:50", "09:00", "09:30"], group = grpS, inline = "w0", display = display.none)
cHands  = input.color(color.new(#f23645, 85), "", group = grpS, inline = "w0", tooltip = "Shades the release on NFP days. Model 6's hands-off window is 08:30–08:45; 09:00 covers the half hour that adds +0.14 ADR to the day's range.", display = display.none)
showWO  = input.bool(true, "Week open, 08:30 / 08:50 opens", group = grpS, inline = "o0", display = display.none)
showGap = input.bool(true, "RTH gap", group = grpS, inline = "o0", tooltip = "The week's open (Sunday 18:00) and, on NFP days, the open of the 08:30 and 08:50 candles, carried right of price. RTH gap: the prior 16:14 close and the gap's 50%, from 09:30.", display = display.none)
showATH = input.bool(true, "ATH", group = grpS, inline = "s2", display = display.none)
cAth    = input.color(#ab47bc, "", group = grpS, inline = "s2", display = display.none)
stAth   = input.string("Solid", "", options = ["Solid", "Dashed", "Dotted"], group = grpS, inline = "s2", display = display.none)
showCE  = input.bool(true, "08:30 CE to", group = grpS, inline = "s3", display = display.none)
ceEnd   = input.string("Next session 11:00", "", options = ["17:00", "Next session 11:00"], group = grpS, inline = "s3", tooltip = "ATH: the all-time high, drawn from the day it was set and carried right of price. CE: on NFP days at 08:30, the consequent encroachment (50%) between the ATH and the 08:29 close, carried to 17:00 or into the next session (Monday after a Friday release) to 11:00. Its label gives how often pooled NFP days touched it by then at that distance.", display = display.none)
''')
rep('grpH    = "HYDRA findings (indicator pane, beside the clock)"', 'grpH    = "Grimmjow: HYDRA findings (indicator pane)"')
rep('showHy  = input.bool(true, "Findings", group = grpH', 'showHy  = input.bool(true, "Grimmjow", group = grpH')
rep('crdSz = crdSzI == "Tiny" ? size.tiny : crdSzI == "Small" ? size.small : size.normal', '''crdSz = crdSzI == "Tiny" ? size.tiny : crdSzI == "Small" ? size.small : size.normal
lbSz  = lblI == "Small" ? size.small : lblI == "Normal" ? size.normal : size.tiny
lsOf(string s) => s == "Solid" ? line.style_solid : s == "Dotted" ? line.style_dotted : line.style_dashed
int relM = relEnd == "08:45" ? 525 : relEnd == "08:50" ? 530 : relEnd == "09:30" ? 570 : 540
int drEM = drEnd == "11:00" ? 660 : drEnd == "17:00" ? 1020 : 974''')

# ── na-safe day keys: `na != calK` is false in Pine, so these ranges never started
rep('''    if p7K != calK
        p7K := calK''', '''    if nz(p7K) != calK
        p7K := calK''')

# ── ATH CE: runs to 17:00 or the next session's 11:00; hit tracked to its end
rep('''var int   ceHT = na
bool at830''', '''var int   ceHT = na
var int   ceXE = na                                                     // when the CE line ends
nxtTd(int k) => addDays(k, dowOf(k) == dayofweek.friday ? 3 : 1)
bool at830''')
rep('''    ceHT := na
    cxP := p_''', '''    ceHT := na
    ceXE := ceEnd == "17:00" ? keyAt(calK, 1020) : keyAt(nxtTd(calK), 660)
    cxP := p_''')
rep('''if vzK == calK and not na(ceV) and na(ceHT) and mod >= 510 and mod < 1020 and high >= ceV
    ceHT := time
ceOdds(float x) => na(x) ? "—" : x <= 0.5 ? "79%" : x <= 1 ? "23%" : x <= 2 ? "1%" : "0%"''',
'''if not na(ceV) and na(ceHT) and not na(ceXE) and time < ceXE and high >= ceV
    ceHT := time
// touched by 17:00 / by the next session's 11:00, pooled NFP days, by the CE's distance at 08:29 (ADR)
ceOdds(float x) => na(x) ? "—" : ceEnd == "17:00" ? (x <= 0.5 ? "79%" : x <= 1 ? "23%" : x <= 2 ? "1%" : "0%") : (x <= 0.5 ? "83%" : x <= 1 ? "31%" : x <= 2 ? "6%" : "0%")''')
rep('drawn from 08:30 to 17:00. Touched by 17:00 on pooled NFP days, by its distance at 08:29: ≤ 0.5 ADR 79% (n 63; 2018–24 91%, 2025–26 50%; NQ 88, ES 75, RTY 73) · 0.5–1 ADR 23% (n 26) · 1–2 ADR 1% (n 71) · > 2 ADR 0% (n 133).',
    'drawn from 08:30 to 17:00 or into the next session to 11:00 (the Monday after a Friday release). Touched on pooled NFP days, by its distance at 08:29, by 17:00 / by the next session\'s 11:00: ≤ 0.5 ADR 79% / 83% (n 63; next-session odds 2018–24 91%, 2025–26 61%; NQ 88, ES 79, RTY 82) · 0.5–1 ADR 23% / 31% (n 26) · 1–2 ADR 1% / 6% (n 71) · > 2 ADR 0% / 0% (n 133).')

# ── model structure on the price chart
cut('bool cNFP = NP.includes(calK)', '// NFP day: the 08:30 and 08:50 opens to the RTH close', '''bool cNFP = NP.includes(calK)
bool cOn  = showStr and recent and cNFP
int  drE  = keyAt(calK, drEM)
// the 07:00–08:59 high and low (the dealing range)
var float drH = na
var float drL = na
var int   drK = na
if cNFP and mod >= 420 and mod < 540
    if nz(drK) != calK
        drK := calK
        drH := high
        drL := low
    else
        drH := math.max(drH, high)
        drL := math.min(drL, low)
// pre-release range 07:00–08:29, drawn live; it stops where the release breaks it (or at 09:00)
var int   d0K = na
var bool  d0On = false
var line  d0H = na
var line  d0L = na
var label d0T = na
var label d0B = na
if cOn and showDR0 and p7K == calK and mod >= 420 and mod < 510
    if nz(d0K) != calK
        d0K  := calK
        d0On := true
        d0H  := line.new(keyAt(calK, 420), p7H, time, p7H, xloc = xloc.bar_time, color = cDR0, style = lsOf(stDR0), force_overlay = true)
        d0L  := line.new(keyAt(calK, 420), p7L, time, p7L, xloc = xloc.bar_time, color = cDR0, style = lsOf(stDR0), force_overlay = true)
        string t0 = "Pre-release range 07:00–08:29, drawn live. The first side the release takes after 08:30 became the bigger side of the day on 59% of pooled NFP days (79% with VIX > 10% under its average, 74% after an up week, 46% after a flat week). " + VZT_FS
        d0T  := label.new(keyAt(calK, 420), p7H, "pre-NFP high", xloc = xloc.bar_time, color = #00000000, textcolor = cDR0, style = label.style_label_lower_left, size = lbSz, tooltip = t0, force_overlay = true)
        d0B  := label.new(keyAt(calK, 420), p7L, "pre-NFP low", xloc = xloc.bar_time, color = #00000000, textcolor = cDR0, style = label.style_label_upper_left, size = lbSz, tooltip = t0, force_overlay = true)
    else
        d0H.set_y1(p7H)
        d0H.set_y2(p7H)
        d0L.set_y1(p7L)
        d0L.set_y2(p7L)
        d0T.set_y(p7H)
        d0B.set_y(p7L)
// the dealing range 07:00–09:00: created when the release breaks the pre-release range (at 09:00 if it never does), drawn
// from 07:00, following the high and low until 09:00, then fixed
var int   dK2 = na
var line  dLH = na
var line  dLL = na
var line  dLE = na
var box   dBx = na
var label dTH = na
var label dTL = na
if cOn and showDR and drK == calK and nz(dK2) != calK and ((vzK == calK and fsd != 0) or mod >= 540)
    dK2 := calK
    int    x0 = keyAt(calK, 420)
    string tD = "NFP dealing range 07:00–09:00 ET: created when the release broke the 07:00–08:29 range" + (fsd == 0 ? " (it did not by 09:00)" : " at " + str.format_time(fsT, "HH:mm", TZ)) + ", following the high and low to 09:00, then fixed."
    dLH := line.new(x0, drH, time, drH, xloc = xloc.bar_time, color = cDR, style = lsOf(stDR), width = wDR, force_overlay = true)
    dLL := line.new(x0, drL, time, drL, xloc = xloc.bar_time, color = cDR, style = lsOf(stDR), width = wDR, force_overlay = true)
    dLE := drEq ? line.new(x0, (drH + drL) / 2, time, (drH + drL) / 2, xloc = xloc.bar_time, color = color.new(cDR, 35), style = line.style_dotted, force_overlay = true) : na
    dBx := drFill ? box.new(x0, drH, time, drL, xloc = xloc.bar_time, border_color = #00000000, bgcolor = color.new(cDR, 92), force_overlay = true) : na
    dTH := label.new(keyAt(calK, 540), drH, "DR high", xloc = xloc.bar_time, color = #00000000, textcolor = cDR, style = label.style_label_lower_left, size = lbSz, tooltip = tD, force_overlay = true)
    dTL := label.new(keyAt(calK, 540), drL, "DR low", xloc = xloc.bar_time, color = #00000000, textcolor = cDR, style = label.style_label_upper_left, size = lbSz, tooltip = tD, force_overlay = true)
if dK2 == calK
    if mod < 540
        dLH.set_y1(drH)
        dLH.set_y2(drH)
        dLL.set_y1(drL)
        dLL.set_y2(drL)
        dTH.set_y(drH)
        dTL.set_y(drL)
        if not na(dLE)
            dLE.set_y1((drH + drL) / 2)
            dLE.set_y2((drH + drL) / 2)
        if not na(dBx)
            dBx.set_top(drH)
            dBx.set_bottom(drL)
    if time <= drE
        dLH.set_x2(time)
        dLL.set_x2(time)
        if not na(dLE)
            dLE.set_x2(time)
        if not na(dBx)
            dBx.set_right(time)
if d0On and d0K == calK
    d0On := dK2 != calK and time <= drE
    d0H.set_x2(time)
    d0L.set_x2(time)
if cOn
    if at830 and showATH and showCE and not na(ceV)
        string ceTp = "ATH CE " + pf(ceV) + " = (ATH " + pf(ceAt) + " + 08:29 close) ÷ 2, " + str.tostring(ceDA, "0.00") + " ADR above price at 08:29: touched by " + (ceEnd == "17:00" ? "17:00" : "the next session's 11:00") + " on " + ceOdds(ceDA) + " of pooled NFP days at that distance. " + VZT_CE
        trimL(line.new(time, ceV, ceXE, ceV, xloc = xloc.bar_time, color = cAth, width = 1, style = line.style_dashed, force_overlay = true), ceXE)
        trimT(label.new(ceXE, ceV, "ATH CE " + ceOdds(ceDA), xloc = xloc.bar_time, color = #00000000, textcolor = cAth, style = label.style_label_left, size = lbSz, tooltip = ceTp, force_overlay = true), ceXE)
    if mod <= 530 and mod + tfM > 530
        line.new(keyAt(calK, 530), close, keyAt(calK, 530), close + syminfo.mintick, xloc = xloc.bar_time, extend = extend.both, color = color.new(cLvl, 60), style = line.style_dotted, force_overlay = true)
    if showGap and rthSt and not na(gapPC)
        trimL(line.new(time, gapPC, keyAt(calK, 974), gapPC, xloc = xloc.bar_time, color = color.new(cLvl, 40), style = line.style_dotted, force_overlay = true), keyAt(calK, 974))
        trimL(line.new(time, gapCE, keyAt(calK, 974), gapCE, xloc = xloc.bar_time, color = color.new(cLvl, 20), style = line.style_dotted, force_overlay = true), keyAt(calK, 974))
        trimT(label.new(keyAt(calK, 974), gapCE, "gap 50%", xloc = xloc.bar_time, color = #00000000, textcolor = cLvl, style = label.style_label_left, size = lbSz, tooltip = "RTH gap 50% = (prior 16:14 close + 09:30 open) ÷ 2. NFP days filled the full gap less often than normal days (NQ 54% vs 63%, ES 53% vs 62%).", force_overlay = true), keyAt(calK, 974))
// the release marker: a flag above the release push, tied by a stem to the 08:30 open; it rises with price until 09:00
var int   nfK = na
var label nfL = na
var line  nfV = na
if cOn and markEv and mod <= 510 and mod + tfM > 510
    float yT = high + 0.3 * ADRtd * tdO
    nfK := calK
    nfV := line.new(time, open, time, yT, xloc = xloc.bar_time, color = color.new(cGh, 25), style = line.style_dotted, width = 1, force_overlay = true)
    nfL := label.new(time, yT, "NFP 08:30 · " + pf(open), xloc = xloc.bar_time, color = cGh, textcolor = #ffffff, style = label.style_label_down, size = lbSz == size.tiny ? size.small : lbSz, tooltip = "Employment Situation release, 08:30 ET " + str.format_time(time, "dd MMM yyyy", TZ) + ". The stem runs down to the 08:30 open, " + pf(open) + ".", force_overlay = true)
else if nfK == calK and mod > 510 and mod < 540 and high + 0.3 * ADRtd * tdO > nfL.get_y()
    nfL.set_y(high + 0.3 * ADRtd * tdO)
    nfV.set_y2(high + 0.3 * ADRtd * tdO)
bgcolor(cOn and mod >= 510 and mod < relM ? cHands : na, title = "NFP release window", force_overlay = true)
''')

# ── labels and ATH line style (right of price)
rep('''"week open " + pf(wkOp), color = #00000000, textcolor = cLvl, style = label.style_label_left, size = size.tiny''', '''"week open " + pf(wkOp), color = #00000000, textcolor = cLvl, style = label.style_label_left, size = lbSz''')
rep('''RL.push(line.new(athNT, athN, time + offI * timeframe.in_seconds() * 1000, athN, xloc = xloc.bar_time, color = cAth, width = 1, force_overlay = true))''',
    '''RL.push(line.new(athNT, athN, time + offI * timeframe.in_seconds() * 1000, athN, xloc = xloc.bar_time, color = cAth, width = 1, style = lsOf(stAth), force_overlay = true))''')
i = S.index('"ATH " + pf(athN) + " · −"'); j = S.index('\n', i); seg = S[i:j]
assert 'size = size.tiny' in seg; S = S[:i] + seg.replace('size = size.tiny', 'size = lbSz') + S[j:]
for lab in ('"08:30 open " + pf(s1O)', '"08:50 open " + pf(s2O)'):
    i = S.index(lab); j = S.index('\n', i); seg = S[i:j]
    assert 'size = size.tiny' in seg; S = S[:i] + seg.replace('size = size.tiny', 'size = lbSz') + S[j:]

# ── tally: the week's range includes today's (the weekly request can lag on replay)
rep('zi == 0 ? wH : mHi, zi == 0 ? wL : mLo', 'zi == 0 ? math.max(nz(wH, tdH), tdH) : mHi, zi == 0 ? math.min(nz(wL, tdL), tdL) : mLo', 2)

# ── Grimmjow: the findings table, narrower
rep('''            tg  += (uMo == 0 ? "MO↑" : "MO↓") + str.tostring(VS.get(48 + uMo), "0.00") + " "''', '''            tg  += (uMo == 0 ? "MO↑ " : "MO↓ ")
            tgN += (uMo == 0 ? "MO↑ " : "MO↓ ") + str.tostring(VS.get(48 + uMo), "0.00") + " · "''')
rep('''            tg  += (uVg == 0 ? "VIX↑" : "VIX↓") + str.tostring(VS.get(51 + uVg), "0.00") + " "''', '''            tg  += (uVg == 0 ? "VIX↑ " : "VIX↓ ")
            tgN += (uVg == 0 ? "VIX↑ " : "VIX↓ ") + str.tostring(VS.get(51 + uVg), "0.00") + " · "''')
rep('''            tg  += (uWg == 0 ? "WK↑" : "WK↓") + str.tostring(VS.get(54 + uWg), "0.00") + " "''', '''            tg  += (uWg == 0 ? "WK↑ " : "WK↓ ")
            tgN += (uWg == 0 ? "WK↑ " : "WK↓ ") + str.tostring(VS.get(54 + uWg), "0.00") + " · "''')
rep('''            tg  += "<PDL1.29 "''', '''            tg  += "<PDL "
            tgN += "<PDL 1.29 · "''')
rep('''            tg  += "18↓1.20 "''', '''            tg  += "18↓ "
            tgN += "18↓ 1.20 · "''')
rep('''        string tg  = ""
        int    bg_''', '''        string tg  = ""
        string tgN = ""
        int    bg_''')
rep('''string agT = "Range after 08:30 in ADR for each held size group active today (all NFP days 0.95):''', '''string agT = "Active today: " + (tgN == "" ? "none" : tgN) + " Range after 08:30 in ADR for each held size group active today (all NFP days 0.95):''')
rep('''        bool   ceF = stS and not na(ceV)''', '''        bool   ceF = not na(ceV) and not na(ceXE) and time < ceXE''')
rep('''        string ceS = ceF ? (na(ceHT) ? (mod >= 1020 ? "missed" : "open") : "hit " + str.format_time(ceHT, "HH:mm", TZ)) : "at 08:30"''',
    '''        string ceS = ceF ? (na(ceHT) ? "open" : "hit " + str.format_time(ceHT, dateKey(ceHT) == calK ? "HH:mm" : "EEE HH:mm", TZ)) : "at 08:30"''')
rep('''        string fsX = fsd == 0 ? (stS ? "none yet" : "from 08:30") : fsd == 2 ? "both, one bar" : (fsd == 1 ? "▲ high " : "▼ low ") + str.format_time(fsT, "HH:mm", TZ)''',
    '''        string fsX = fsd == 0 ? (stS ? "no break yet" : "break from 08:30") : fsd == 2 ? "both sides, one bar" : "break " + (fsd == 1 ? "▲ " : "▼ ") + str.format_time(fsT, "HH:mm", TZ)''')
cut('            cardHead(TH, r, cHy, dot + " HYDRA · NFP · NQ+ES+RTY"', '            if stS\n                tcQ(TH, 4, r + 8', '''            cardHead(TH, r, cHy, dot + " GRIMMJOW · NFP", VZT_HY, str.tostring(nH) + " ✓", cHy, #ffffff)
            cardSub(TH, r + 1, cHy, "NQ+ES+RTY · ADR " + sgP(a), "today", "base")
            cardWide(TH, r + 2, cHy, "SIDE", "none held: size the day", VZT_HY, cSub)
            cardRow(TH, r + 3, cHy, "RANGE", vh(18 + 2 * z), "after 08:30 · " + zWd(z), sgP(eR), "all " + sgP(0.95 * a), "Range after 08:30 for today's month position (" + zWd(z) + "): median " + sgP(eR) + ", 80% " + sgP(VS.get(19 + 2 * z) * a) + " pts. " + VZT_MON + " " + VZT_E)
            cardRow(TH, r + 4, cHy, "SIZE+", tg != "", tg == "" ? "none active" : tg, "", "", agT)
            tcQ(TH, 3, r + 4, agr, agr == "BIGGER" or agr == "SMALLER" ? #ffffff : cTx, agr == "BIGGER" ? cHot : agr == "SMALLER" ? cCold : cNeu, agT, text.align_center, true)
            cardRow(TH, r + 5, cHy, "H/L", hlH(xi), "after 08:30 · " + xn, hl(xi), "H75 L64", "New day high (H) / low (L) after 08:30 for today's most specific group (" + xn + "); all NFP days H75 L64. " + VZT_18 + " " + VZT_PD + " " + VZT_MON)
            cardRow(TH, r + 6, cHy, "CE", ceH, na(ceX) ? "at the ATH" : pf(ceX) + " · " + str.tostring(ceD, "0.0") + " ADR", ceOdds(ceD), ceS, VZT_CE, nz(ceD, 9) <= 0.5 ? cHot : na, ceF and not na(ceHT) ? cOk : na)
            cardRow(TH, r + 7, cHy, "1ST", fsH, fsX, fsR, fsW, VZT_FS)
            cardRow(TH, r + 8, cHy, "DXY1", true, "S1 BIG ≥ 0.42 → other", "82%", "vs 53%", VZT_DR)
            cardRow(TH, r + 9, cHy, "DXY2", true, "S2 BIG ≥ 0.22 → other", "71%", "vs 59%", VZT_DR)
''')
rep('''cardRow(TH, r + 10, cHy, "08:30+", true, "08:30–09:00 adds · typ +" + sgP(0.14 * a) + " pts",''', '''cardRow(TH, r + 10, cHy, "08:30", true, "→09:00 adds · typ " + sgP(0.14 * a),''')
rep('cardHead(TH, r, cHy, dot + " HYDRA · NFP", VZT_HY', 'cardHead(TH, r, cHy, dot + " GRIMMJOW", VZT_HY')
rep('cardRow(TH, r + 2, cHy, "H / L", hlH(xi)', 'cardRow(TH, r + 2, cHy, "H/L", hlH(xi)')
rep('''cardRow(TH, r + 5, cHy, in2 ? "DXY S2" : "DXY S1", true, "BIG → other way " + (in2 ? "71%" : "82%"), "", "", VZT_DR)''',
    '''cardRow(TH, r + 5, cHy, in2 ? "DXY2" : "DXY1", true, "BIG → other way", in2 ? "71%" : "82%", "", VZT_DR)''')
rep('var string VZT_HY = "HYDRA on NQ + ES + RTY pooled:', 'var string VZT_HY = "Grimmjow: the HYDRA findings for NFP day. HYDRA on NQ + ES + RTY pooled:')
open(P, 'w', encoding='utf-8').write(S)
print('ok', len(S.split('\n')))
