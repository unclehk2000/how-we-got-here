"""Gran Rey Cero: CPI-day structure upgrade.
- pre-CPI range 07:30–08:29 drawn live (like Desgarrón's pre-release range), ending where the release first takes a side
- the 08:30–09:00 CPI dealing range: high, low and CE, drawn live, then carried to the range end (17:00 by default)
- NQ · ES · RTY against their week open at 08:30 and 09:30, one readout under the release (Genjutsu-style)
- the CPI flag: a pill above the release, tied to the 08:30 open, in place of the floating day wording
- fixes: the stage-1 range, the window box and the 08:30 candle never drew (na != calK is false in Pine v6)
Reads backups_1013/Gran_Rey_Cero_before_dr.pine, writes Gran_Rey_Cero.pine."""
S = open('/home/claude/hm/backups_1013/Gran_Rey_Cero_before_dr.pine', encoding='utf-8').read()


def rep(o, n, c=1):
    global S
    k = S.count(o)
    assert k == c, (k, o[:120])
    S = S.replace(o, n)


def cut(a, b, new):
    global S
    i = S.index(a)
    j = S.index(b, i)
    S = S[:i] + new + S[j:]


POS = '["Solid", "Dashed", "Dotted"]'
# ── inputs: the model structure section
cut('cLvl    = input.color(#ffb300, "Levels", group = grpS, inline = "s1", display = display.none)\n', 'relLenI = input.string(',
    '''cLvl    = input.color(#ffb300, "Levels", group = grpS, inline = "s1", display = display.none)
lblI    = input.string("Tiny", "Labels", options = ["Tiny", "Small", "Normal"], group = grpS, inline = "s1", display = display.none)
showDR0 = input.bool(true, "Pre-CPI range 07:30–08:29", group = grpS, inline = "d0", display = display.none)
cDR0    = input.color(#90a4ae, "", group = grpS, inline = "d0", display = display.none)
stDR0   = input.string("Dashed", "", options = %s, group = grpS, inline = "d0", tooltip = "Stage 1: the hour before the release, drawn live from 07:30. It stops at the bar where the release first takes one of its sides (marked 1st sweep). The first side taken went on to be the day's bigger move from 08:30 on 70%% of NQ CPI days (67%% ES) vs 56%% on normal days.", display = display.none)
showDR  = input.bool(true, "CPI dealing range 08:30–09:00", group = grpS, inline = "d1", display = display.none)
cDR     = input.color(#ffb300, "", group = grpS, inline = "d1", display = display.none)
stDR    = input.string("Solid", "", options = %s, group = grpS, inline = "d1", display = display.none)
wDR     = input.int(1, "", minval = 1, maxval = 4, group = grpS, inline = "d1", tooltip = "The 08:30–09:00 high and low, drawn live through the window, then fixed at 09:00 and carried right to the end you pick.", display = display.none)
drEq    = input.bool(true, "CE (50%%)", group = grpS, inline = "d2", display = display.none)
drFill  = input.bool(false, "Fill", group = grpS, inline = "d2", display = display.none)
drExt   = input.bool(true, "±0.25", group = grpS, inline = "d2", display = display.none)
drEnd   = input.string("17:00", "Run to", options = ["11:00", "16:14", "17:00"], group = grpS, inline = "d2", tooltip = "17:00 = the end of the CME trading day.", display = display.none)
showWkO = input.bool(true, "NQ · ES · RTY vs week open at 08:30 and 09:30", group = grpS, tooltip = "One readout under the release: each index against its own week open (Sunday 18:00), at 08:30 and at the 09:30 open, the SMT idea behind Genjutsu Kai. Micro charts read MNQ · MES · M2K.", display = display.none)
''' % (POS, POS))
rep('showWin = input.bool(true, "08:30–09:00 high / low box"', 'showWin = input.bool(false, "08:30–09:00 box"')
cut('showNot = input.bool(true, "Day wording"', 'txCPI   = input.string(',
    '''showNot = input.bool(true, "CPI flag and day wording", group = grpS, inline = "s6", display = display.none)
cNote   = input.color(#e53935, "", group = grpS, inline = "s6", display = display.none)
noteSzI = input.string("Small", "", options = ["Tiny", "Small", "Normal", "Large", "Huge"], group = grpS, inline = "s6", display = display.none)
noteUp  = input.int(12, "height", minval = 0, maxval = 300, group = grpS, inline = "s6", tooltip = "CPI day: a flag above the release bar, tied by a stem to the 08:30 open; it rises with the release push to 09:00. The day after and other days get a quiet tag instead. Height = % of ADR20 above the bar's high. Leave a wording box empty to hide that day's tag.", display = display.none)
''')
rep('txCPI   = input.string("CPI day · here we go folks", "CPI day"', 'txCPI   = input.string("here we go folks", "CPI day"')

# ── helpers
rep('chSz  = chSzI == "Tiny" ? size.tiny : chSzI == "Small" ? size.small : size.normal\n',
    '''chSz  = chSzI == "Tiny" ? size.tiny : chSzI == "Small" ? size.small : size.normal
lbSz  = lblI == "Small" ? size.small : lblI == "Normal" ? size.normal : size.tiny
lsOf(string s) => s == "Solid" ? line.style_solid : s == "Dotted" ? line.style_dotted : line.style_dashed
''')

# ── requests: NQ · ES · RTY and their week opens, this contract family
rep('[moH, moL] = request.security(syminfo.tickerid, "M", [high, low], lookahead = barmerge.lookahead_on)\n',
    '''[moH, moL] = request.security(syminfo.tickerid, "M", [high, low], lookahead = barmerge.lookahead_on)
// NQ · ES · RTY (or MNQ · MES · M2K) with their week open, for the readout under the release: the chart's own contract
// month (NQ1! → ES1! · RTY1!, NQZ2026 → ESZ2026 · RTYZ2026); other symbols read the continuous minis
bool   famOk = syminfo.root == "NQ" or syminfo.root == "ES" or syminfo.root == "RTY" or syminfo.root == "MNQ" or syminfo.root == "MES" or syminfo.root == "M2K"
bool   famMc = syminfo.root == "MNQ" or syminfo.root == "MES" or syminfo.root == "M2K"
string famSx = famOk ? str.replace(syminfo.ticker, syminfo.root, "") : "1!"
string famPx = famOk ? syminfo.prefix : "CME_MINI"
idxNm(int i) => famMc ? (i == 0 ? "MNQ" : i == 1 ? "MES" : "M2K") : (i == 0 ? "NQ" : i == 1 ? "ES" : "RTY")
idxTk(int i) => famPx + ":" + idxNm(i) + famSx
wkOpenF() =>
    var float wo = na
    bool nw = ta.change(time("W")) != 0
    if nw or na(wo)
        wo := open
    [open, wo]
[nqO, nqW] = request.security(idxTk(0), timeframe.period, wkOpenF(), ignore_invalid_symbol = true)
[esO, esW] = request.security(idxTk(1), timeframe.period, wkOpenF(), ignore_invalid_symbol = true)
[ryO, ryW] = request.security(idxTk(2), timeframe.period, wkOpenF(), ignore_invalid_symbol = true)
''')

# ── structure: the pre-CPI range and the 1st sweep
cut('var float drH = na\n', '    if mod <= 530 and mod + tfM > 530\n', '''var float drH  = na
var float drL  = na
var int   drK  = na
var int   swp  = 0
var line  p0H  = na
var line  p0L  = na
var label p0Ht = na
var label p0Lt = na
int    drEndM = drEnd == "11:00" ? 660 : drEnd == "16:14" ? 974 : 1020
string swTip  = "First side of the pre-CPI range (07:30–08:29) taken after the release. The day's bigger move (from 08:30) went the same way " + (isES ? "67% of the time vs 56% on normal days, but only 53% in 2025–26 (71% in 2018–24)." : "70% of the time vs 56% on normal days, and 71% in 2025–26.")
// stage 1: the pre-CPI range, live from 07:30, plus yesterday's RTH close
if gOn and gCPI
    if mod >= 450 and mod < 510
        if nz(drK) != calK
            drK := calK
            drH := high
            drL := low
            swp := 0
            if showDR0
                p0H  := line.new(time, high, time, high, xloc = xloc.bar_time, color = cDR0, style = lsOf(stDR0), force_overlay = true)
                p0L  := line.new(time, low, time, low, xloc = xloc.bar_time, color = cDR0, style = lsOf(stDR0), force_overlay = true)
                p0Ht := label.new(time, high, "pre-CPI high", xloc = xloc.bar_time, color = #00000000, textcolor = cDR0, style = label.style_label_lower_left, size = lbSz, tooltip = swTip, force_overlay = true)
                p0Lt := label.new(time, low, "pre-CPI low", xloc = xloc.bar_time, color = #00000000, textcolor = cDR0, style = label.style_label_upper_left, size = lbSz, tooltip = swTip, force_overlay = true)
            if showYC and not na(rthC)
                trimL(line.new(keyAt(calK, 450), rthC, keyAt(calK, 974), rthC, xloc = xloc.bar_time, color = color.new(cLvl, 25), style = line.style_dotted, width = 1, force_overlay = true), keyAt(calK, 974))
                trimT(label.new(keyAt(calK, 974), rthC, "yday RTH close", xloc = xloc.bar_time, color = #00000000, textcolor = color.new(cLvl, 15), style = label.style_label_left, size = lbSz, tooltip = "Yesterday's RTH close (16:14 bar): the gap the release opens is measured from here.", force_overlay = true), keyAt(calK, 974))
        else
            drH := math.max(drH, high)
            drL := math.min(drL, low)
            if showDR0 and not na(p0H)
                p0H.set_y1(drH)
                p0H.set_y2(drH)
                p0L.set_y1(drL)
                p0L.set_y2(drL)
                p0Ht.set_y(drH)
                p0Lt.set_y(drL)
    // the range runs right until the release first takes one of its sides
    if showDR0 and drK == calK and not na(p0H) and swp == 0 and mod >= 450 and mod < drEndM
        p0H.set_x2(time)
        p0L.set_x2(time)
    if drK == calK and mod >= 510 and mod < 975 and swp == 0 and not na(drH)
        if low < drL
            swp := -1
            label.new(bar_index, drL, "1st sweep ▼", color = #00000000, textcolor = cDR0, style = label.style_label_upper_right, size = lbSz, tooltip = swTip, force_overlay = true)
        else if high > drH
            swp := 1
            label.new(bar_index, drH, "1st sweep ▲", color = #00000000, textcolor = cDR0, style = label.style_label_lower_right, size = lbSz, tooltip = swTip, force_overlay = true)
''')

# ── the 08:30–09:00 CPI dealing range, after the window lines (needs bgcolor first)
rep('''// the window's high / low box: CPI days, lighter on the day after''', '''// the 08:30–09:00 CPI dealing range: high, low and CE, live through the window, then carried right to the range end
var float    c3H  = na
var float    c3L  = na
var int      c3K  = na
var line     c3Hl = na
var line     c3Ll = na
var line     c3Cl = na
var linefill c3Fl = na
var label    c3Ht = na
var label    c3Lt = na
string c3Tip = "CPI dealing range: the 08:30–09:00 high and low. NQ + ES + RTY 1-minute, 102 CPI days 2018–26 (304 symbol-days) vs normal days: the window ran a median 0.37 ADR20 (80%: 0.77) vs 0.12. After 09:00, RTH took its high by 16:14 on 74% of CPI days (normal 89%), its low 70% (87%), both 48% (77%), all held. The RTH close: above it 37% · inside 28% · below 35% (normal 48 · 10 · 42). Its direction did not carry: RTH closed the 08:30–09:00 way 48%."
string x25Tip = "±0.25: a quarter of the 08:30–09:00 range beyond its high and low. How often RTH (09:00–16:14) reached them on CPI days, NQ + ES + RTY 1-minute, 103 days 2018–26 (307 symbol-days): +0.25 above the high 62% (normal days 83%) · −0.25 below the low 60% (83%) · either 90% (100%) · both 32% (67%). Once the high broke, it carried on to +0.25 83% (94%); once the low broke, to −0.25 85% (95%). All held in 2018–24 and 2025–26 and on NQ, ES and RTY, but 2025–26 ran lower: +0.25 45%, −0.25 53%. CPI ranges are wide, so their extensions are reached less often than a normal day's."
if gOn and gCPI and showDR and tfM <= 30 and mod >= 510 and mod < 540
    float ce_ = na
    if nz(c3K) != calK
        c3K  := calK
        c3H  := high
        c3L  := low
        ce_  := (c3H + c3L) / 2
        c3Hl := line.new(time, c3H, time, c3H, xloc = xloc.bar_time, color = cDR, style = lsOf(stDR), width = wDR, force_overlay = true)
        c3Ll := line.new(time, c3L, time, c3L, xloc = xloc.bar_time, color = cDR, style = lsOf(stDR), width = wDR, force_overlay = true)
        c3Cl := drEq ? line.new(time, ce_, time, ce_, xloc = xloc.bar_time, color = color.new(cDR, 25), style = line.style_dotted, force_overlay = true) : na
        c3Fl := drFill ? linefill.new(c3Hl, c3Ll, color.new(cDR, 92)) : na
        c3Ht := label.new(time, c3H, "CPI DR high", xloc = xloc.bar_time, color = #00000000, textcolor = cDR, style = label.style_label_lower_left, size = lbSz, tooltip = c3Tip, force_overlay = true)
        c3Lt := label.new(time, c3L, "CPI DR low", xloc = xloc.bar_time, color = #00000000, textcolor = cDR, style = label.style_label_upper_left, size = lbSz, tooltip = c3Tip, force_overlay = true)
    else
        c3H := math.max(c3H, high)
        c3L := math.min(c3L, low)
        ce_ := (c3H + c3L) / 2
        c3Hl.set_y1(c3H)
        c3Hl.set_y2(c3H)
        c3Ll.set_y1(c3L)
        c3Ll.set_y2(c3L)
        c3Ht.set_y(c3H)
        c3Lt.set_y(c3L)
        if not na(c3Cl)
            c3Cl.set_y1(ce_)
            c3Cl.set_y2(ce_)
    c3Hl.set_x2(time)
    c3Ll.set_x2(time)
    if not na(c3Cl)
        c3Cl.set_x2(time)
// at 09:00 the range is fixed and runs right; the CE's label gives how often CPI days traded back to it from here
if c3K == calK and mod >= 540 and (mod[1] < 540 or calK != calK[1]) and not na(c3Hl)
    int   te  = keyAt(calK, drEndM)
    float ce_ = (c3H + c3L) / 2
    float cd  = tdO * ADRtd > 0 ? math.abs(close[1] - ce_) / (tdO * ADRtd) : na
    string od = na(cd) ? "" : cd <= 0.1 ? " · 94%" : cd <= 0.2 ? " · 85%" : cd <= 0.4 ? " · 71%" : " · 39%"
    trimL(c3Hl, te)
    trimL(c3Ll, te)
    if not na(c3Cl)
        trimL(c3Cl, te)
        trimT(label.new(te, ce_, "CPI CE" + od, xloc = xloc.bar_time, color = #00000000, textcolor = cDR, style = label.style_label_left, size = lbSz, tooltip = "CE = the 08:30–09:00 range's 50%. How often RTH traded back to it after 09:00 (by 16:14) on CPI days, by its distance from the 08:59 close: within 0.1 ADR20 94% · 0.1–0.2 85% · 0.2–0.4 71% · beyond 0.4 39% (2018–24 / 2025–26: 94 / 95 · 87 / 70 · 74 / 56). Normal days within 0.2 ADR: 94% · 85%. Read it as distance: a near CE gets traded, a far one less often. Today: " + (na(cd) ? "—" : str.tostring(cd, "0.00") + " ADR20") + ".", force_overlay = true), te)
    // ±0.25 of the range beyond its high and low, from 08:30 to the range end
    if drExt
        float r25 = (c3H - c3L) * 0.25
        int   t0_ = keyAt(calK, 510)
        trimL(line.new(t0_, c3H + r25, te, c3H + r25, xloc = xloc.bar_time, color = color.new(cDR, 35), style = line.style_dashed, force_overlay = true), te)
        trimL(line.new(t0_, c3L - r25, te, c3L - r25, xloc = xloc.bar_time, color = color.new(cDR, 35), style = line.style_dashed, force_overlay = true), te)
        trimT(label.new(te, c3H + r25, "CPI DR +0.25 · 62%", xloc = xloc.bar_time, color = #00000000, textcolor = color.new(cDR, 15), style = label.style_label_left, size = lbSz, tooltip = x25Tip, force_overlay = true), te)
        trimT(label.new(te, c3L - r25, "CPI DR −0.25 · 60%", xloc = xloc.bar_time, color = #00000000, textcolor = color.new(cDR, 15), style = label.style_label_left, size = lbSz, tooltip = x25Tip, force_overlay = true), te)
// the window's high / low box: CPI days, lighter on the day after''')
rep('''    if wK != calK
        wK  := calK''', '''    if nz(wK) != calK
        wK  := calK''')
rep('''    if rcK != calK
        rcK := calK''', '''    if nz(rcK) != calK
        rcK := calK''')

# ── the CPI flag and the day's tag, and the week-open readout under the release
cut('// the day\'s wording, centred over the window', '// every CPI 08:30 candle, kept and extended', '''// the CPI flag: above the release bar, tied by a stem to the 08:30 open; it rises with the release push to 09:00. The day
// after and other days get a quiet tag (its wording box empty = none)
var label  wTx  = na
var line   wTs  = na
var int    wTxK = na
color  cPilM  = dark ? #2a2e39 : #e3e6ec
string noteTx = gCPI ? txCPI : gAft ? txAft : txOth
float  noteOf = (tdO * ADRtd > 0 ? tdO * ADRtd : tdH - tdL) * noteUp / 100.0
noteSz = noteSzI == "Tiny" ? size.tiny : noteSzI == "Small" ? size.small : noteSzI == "Normal" ? size.normal : noteSzI == "Large" ? size.large : size.huge
if gOn and showNot and wkd and (gCPI or noteTx != "") and mod <= 510 and mod + tfM > 510
    int    nx   = nextOf(CP, addDays(calK, 1))
NTIP_ORIGINAL
    float  yT   = high + noteOf
    wTxK := calK
    wTs  := gCPI ? line.new(time, open, time, yT, xloc = xloc.bar_time, color = color.new(cNote, 25), style = line.style_dotted, force_overlay = true) : na
    wTx  := label.new(time, yT, gCPI ? "CPI 08:30 · " + pf(open) + (noteTx == "" ? "" : "\\n" + noteTx) : (gAft ? "CPI +1 · " : "") + noteTx, xloc = xloc.bar_time, color = gCPI ? cNote : cPilM, textcolor = gCPI ? #ffffff : cSub, style = label.style_label_down, size = gCPI ? noteSz : size.tiny, tooltip = nTip, force_overlay = true)
else if wTxK == calK and mod < 540 and not na(wTx) and high + noteOf > wTx.get_y()
    wTx.set_y(high + noteOf)
    if not na(wTs)
        wTs.set_y2(high + noteOf)
// NQ · ES · RTY against their week open at 08:30 and at the 09:30 open: one readout under the release, held below the
// candles to 10:00
var label  gjL  = na
var int    gjK  = na
var string gj8  = ""
var float  gjY  = na
wkPct(float px, float wo) => na(px) or na(wo) or wo == 0 ? na : (px / wo - 1) * 100
wkCell(float p) => na(p) ? "   —    " : (p >= 0 ? "▲" : "▼") + str.tostring(math.abs(p), "0.00") + "%"
padR(string s, int n) => s + str.repeat(" ", math.max(0, n - str.length(s)))
gjRow(string tm) =>
    float a = wkPct(nqO, nqW)
    float b = wkPct(esO, esW)
    float c = wkPct(ryO, ryW)
    bool  ok = not (na(a) or na(b) or na(c))
    int   up = (nz(a) > 0 ? 1 : 0) + (nz(b) > 0 ? 1 : 0) + (nz(c) > 0 ? 1 : 0)
    float lo = math.min(nz(a, 1e9), nz(b, 1e9), nz(c, 1e9))
    string wk = not ok ? "" : lo == a ? idxNm(0) : lo == b ? idxNm(1) : idxNm(2)
    string tg = not ok ? "" : up == 3 ? "all ▲" : up == 0 ? "all ▼" : "SPLIT"
    padR(tm, 7) + padR(wkCell(a), 8) + " " + padR(wkCell(b), 8) + " " + padR(wkCell(c), 8) + " " + padR(tg, 5) + (wk == "" ? "" : " weak " + wk)
gjHead() => "vs week open\\n" + padR("", 7) + padR(idxNm(0), 8) + " " + padR(idxNm(1), 8) + " " + padR(idxNm(2), 8)
string gjTip = "Each index against its own week open (Sunday 18:00), in %, at the 08:30 release and the 09:30 open. SPLIT = they sit on different sides of their week opens, the SMT idea behind Genjutsu Kai; weak = the furthest below. NQ + ES + RTY 1-minute 2018–26: the index weakest at 08:30 was still the weakest at 16:14 on 71% of CPI days (the strongest still the strongest 78%), much as on any day (70%, 71%): relative strength carries through the day, CPI does not reset it. A split at 08:30 (29% of CPI days, 26% of others) usually stood: the odd one joined the others by 16:14 on 24% of CPI days (32% of others). A locator, not a direction call."
float gjOff = (tdO * ADRtd > 0 ? tdO * ADRtd : tdH - tdL) * 0.12
if gOn and gCPI and showWkO and mod <= 510 and mod + tfM > 510
    gjK := calK
    gj8 := gjRow("08:30")
    gjY := low - gjOff
    gjL := label.new(time, gjY, gjHead() + "\\n" + gj8, xloc = xloc.bar_time, color = color.new(dark ? #161a23 : #f4f6f9, 0), textcolor = cTx, style = label.style_label_up, size = lbSz == size.tiny ? size.small : lbSz, text_font_family = font.family_monospace, textalign = text.align_left, tooltip = gjTip, force_overlay = true)
else if gjK == calK and not na(gjL) and mod < 600
    if mod <= 570 and mod + tfM > 570
        gjL.set_text(gjHead() + "\\n" + gj8 + "\\n" + gjRow("09:30"))
    if low - gjOff < gjY
        gjY := low - gjOff
        gjL.set_y(gjY)
''')
# the 08:30 candle's label sits on its top edge, clear of the CE label at the right
import re as _re
_m = _re.search(r"RCT\.push\(label\.new\(time, \(rcH \+ rcL\) / 2, (.*?)style = label\.style_label_left", S)
assert _m
S = S.replace(_m.group(0), "RCT.push(label.new(time, rcH, " + _m.group(1) + "style = label.style_label_lower_left", 1)
import re
nt = re.search(r'\n(    string nTip = [^\n]*)\n', open('/home/claude/hm/backups_1013/Gran_Rey_Cero_before_dr.pine', encoding='utf-8').read()).group(1)
S = S.replace('NTIP_ORIGINAL', nt)
open('/home/claude/hm/Gran_Rey_Cero.pine', 'w', encoding='utf-8').write(S)
print('written', len(S.split('\n')), 'lines')

# ── split the last-bar block: Pine caps the size of one if block (CE10205), which matters once Hueco Mundo runs this
#    code inside library functions. Its shared values become globals set on the last bar; each part is its own block.
import sys as _sys
exec(open('/home/claude/hmz/pine2lib.py').read().split("if __name__ == '__main__':")[0])
S = open('/home/claude/hm/Gran_Rey_Cero.pine', encoding='utf-8').read()
Lx = S.split('\n')
i0 = next(k for k, l in enumerate(Lx) if l == 'if barstate.islast' and Lx[k + 1].strip() == 'clearRight()')
j0 = i0 + 1
while j0 < len(Lx) and (Lx[j0].strip() == '' or Lx[j0].startswith(' ')):
    j0 += 1
blk = Lx[i0 + 1:j0]
DRAW = ('if shM', 'if hasD', 'if showWk', 'if showCh', 'if showEv and not na(TS)', 'if showVx', 'if showDx', 'if mob and', 'if showCk')
TUP = {'pk': 'int', 'pNow': 'bool', 'pDay': 'int', 'n1t': 'string', 'n1k': 'int', 'n2t': 'string', 'n2k': 'int'}
DEF = {'int': 'na', 'float': 'na', 'bool': 'false', 'string': '""', 'color': 'na'}
gdecl, segs, cur, kind = [], [], [], 'val'
for l in blk:
    s = l.strip()
    if indent(l) == 4 and s and not s.startswith('//'):
        isDraw = s.startswith(DRAW) or s == 'clearRight()'
        if isDraw or kind == 'draw':
            if cur:
                segs.append(cur)
            cur, kind = [], ('draw' if isDraw else 'val')
        d = decl_of(code_of(l))
        if d and d[3] == '=':
            if TUPLE.match(code_of(l)):
                tmp = [n + '_' for n in d[0]]
                for n in d[0]:
                    gdecl.append('%s %s = %s' % (TUP[n], n, DEF[TUP[n]]))
                cur.append('    [' + ', '.join(tmp) + '] =' + l.split('=', 1)[1])
                cur += ['    %s := %s_' % (n, n) for n in d[0]]
                continue
            ty = d[2]
            gdecl.append('%s %s = %s' % (ty, d[0][0], DEF.get(ty, 'na')))
            cur.append('    %s :=%s' % (d[0][0], l.split('=', 1)[1]))
            continue
    cur.append(l)
if cur:
    segs.append(cur)
out = ['// The last bar\'s values the PO3 candles, the chips and the cards share, set on the last bar. Pine caps the size of one',
       '// if block (CE10205), so each part below is its own block.']
out += gdecl
for sg in segs:
    if not any(x.strip() and not x.strip().startswith('//') for x in sg):
        out += sg
        continue
    out.append('if barstate.islast')
    out += sg
S = '\n'.join(Lx[:i0] + out + Lx[j0:])
# the main body (CE10295): the data loaders and the first-bar tally parse move into functions
import sys as _sys
_sys.path.insert(0, '/home/claude/pinetools')
import pine_hoist, pine_size
_sys.path.insert(0, '/home/claude/hm')
import patch_adr_fallback
S = patch_adr_fallback.patch(S)
S = pine_hoist.hoist(S, 5000)
open('/home/claude/hm/Gran_Rey_Cero.pine', 'w', encoding='utf-8').write(S)
print('split the last-bar block into', len(segs), 'parts;', len(gdecl), 'shared values')
pine_size.report('/home/claude/hm/Gran_Rey_Cero.pine')
