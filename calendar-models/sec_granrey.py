# ───────────────────────────────────────────── Gran Rey Cero (7–8) · CPI
IND['Gran Rey Cero'] = dict(ck=['CPI'], ckmap=dict(CPI=0), rel='510', file='Gran_Rey_Cero', short='Gran Rey', ghost='#e53935', keys=['CPI'], header='''// Gran Rey Cero (王虚の閃光) · Models 7–8: CPI days (released 08:30 ET).
// The model's own structure on the chart: stage 1 (the dealing range built in the hour before the release, the structure
// the release tests), yesterday's RTH close, the first side of the dealing range taken after the release, the 08:50 line
// between the release push and stage 2, the 08:30–09:00 range (shaded on CPI days, lighter on the day after) and every
// CPI 08:30 candle kept and extended to the right, labelled wild / average / quiet against past CPI candles.''',
sinputs='''relLenI = input.string("1 min", "08:30 candle", options = ["1 min", "5 min", "15 min"], group = grpS, inline = "s2", tooltip = "The CPI release candle kept and extended to the right. On a chart above this timeframe the bar holding 08:30 is used. Wild / average / quiet = top / middle / bottom third of CPI release candles of the same length since 2018, as a share of ADR20.", display = display.none)
relKeep = input.int(6, "keep last", minval = 1, maxval = 30, group = grpS, inline = "s2", display = display.none)
showWin = input.bool(true, "08:30–09:00 boxes", group = grpS, inline = "s3", display = display.none)
showYC  = input.bool(true, "Yesterday's RTH close", group = grpS, inline = "s3", display = display.none)
showNot = input.bool(true, "Other-day notes", group = grpS, inline = "s3", tooltip = "'nothing to see here folks' at 08:30 on days that are neither a CPI day nor the day after one.", display = display.none)''',
own='''ownProfile(int tk, int pk, int today) =>
    bool now = CP.includes(tk)
    int  rf  = na(tk) ? today : math.max(tk, today)
    [0, now, now ? tk : nextOf(CP, rf)]
ownNext(int today) =>
    int n1 = nextOf(CP, today)
    ["CPI 08:30", n1, "then", na(n1) ? na : nextOf(CP, addDays(n1, 1))]''',
struct='''bool gCPI = CP.includes(calK)
bool gAft = CP.includes(tdPK) and not gCPI                   // the trading day after a CPI day
bool gOn  = showStr and recent
bool wkd  = dayofweek(time, TZ) >= 2 and dayofweek(time, TZ) <= 6
var float drH = na
var float drL = na
var int   drK = na
var int   swp = 0
string swTip = "First side of the stage 1 dealing range (07:30–08:30) taken after the release. The day's bigger move (from 08:30) went the same way " + (isES ? "67% of the time vs 56% on normal days, but only 53% in 2025–26 (71% in 2018–24)." : "70% of the time vs 56% on normal days, and 71% in 2025–26.")
// stage 1: the dealing range built in the hour before the release, plus yesterday's RTH close
if gOn and gCPI
    if mod >= 450 and mod < 510
        if drK != calK
            drK := calK
            drH := high
            drL := low
            swp := 0
            if showYC and not na(rthC)
                line.new(keyAt(calK, 450), rthC, keyAt(calK, 974), rthC, xloc = xloc.bar_time, color = color.new(cLvl, 25), style = line.style_dotted, width = 1)
                label.new(keyAt(calK, 974), rthC, "yday RTH close", xloc = xloc.bar_time, color = #00000000, textcolor = color.new(cLvl, 15), style = label.style_label_left, size = size.tiny, tooltip = "Yesterday's RTH close (16:14 bar): the gap the release opens against.")
        else
            drH := math.max(drH, high)
            drL := math.min(drL, low)
    if drK == calK and mod >= 510 and (mod[1] < 510 or calK != calK[1])
        line.new(keyAt(calK, 450), drH, keyAt(calK, 974), drH, xloc = xloc.bar_time, color = cLvl, width = 1, style = line.style_dashed)
        line.new(keyAt(calK, 450), drL, keyAt(calK, 974), drL, xloc = xloc.bar_time, color = cLvl, width = 1, style = line.style_dashed)
        label.new(keyAt(calK, 450), drH, "stage 1 · DR high", xloc = xloc.bar_time, color = #00000000, textcolor = cLvl, style = label.style_label_lower_left, size = size.tiny, tooltip = "Stage 1: the dealing range built in the hour before the 08:30 release (07:30–08:30 ET). This is the structure the release tests.")
        label.new(keyAt(calK, 450), drL, "stage 1 · DR low", xloc = xloc.bar_time, color = #00000000, textcolor = cLvl, style = label.style_label_upper_left, size = size.tiny, tooltip = "Stage 1: the dealing range built in the hour before the 08:30 release (07:30–08:30 ET). This is the structure the release tests.")
    if drK == calK and mod >= 510 and mod < 975 and swp == 0 and not na(drH)
        if low < drL
            swp := -1
            label.new(bar_index, low, "1st sweep ▼", color = #00000000, textcolor = cLvl, style = label.style_label_up, size = size.tiny, tooltip = swTip)
        else if high > drH
            swp := 1
            label.new(bar_index, high, "1st sweep ▲", color = #00000000, textcolor = cLvl, style = label.style_label_down, size = size.tiny, tooltip = swTip)
    if mod <= 530 and mod + tfM > 530
        line.new(keyAt(calK, 530), close, keyAt(calK, 530), close + syminfo.mintick, xloc = xloc.bar_time, extend = extend.both, color = color.new(cLvl, 60), style = line.style_dotted)
    if rthSt and not na(gapCE)
        line.new(time, gapCE, keyAt(calK, 974), gapCE, xloc = xloc.bar_time, color = color.new(cLvl, 20), style = line.style_dotted)
        label.new(keyAt(calK, 974), gapCE, "gap 50%", xloc = xloc.bar_time, color = #00000000, textcolor = cLvl, style = label.style_label_left, size = size.tiny, tooltip = "RTH gap 50% = (yesterday's RTH close + 09:30 open) ÷ 2")
// the 08:30–09:00 range: shaded on CPI days, lighter on the day after
var box   wBx = na
var label wLb = na
var int   wK  = na
bool inW = mod < 540 and mod + tfM > 510
if gOn and showWin and (gCPI or gAft) and inW and wkd
    if wK != calK
        wK  := calK
        wBx := box.new(keyAt(calK, 510), high, keyAt(calK, 540), low, xloc = xloc.bar_time, border_color = color.new(cGh, gCPI ? 35 : 70), border_width = 1, bgcolor = color.new(cGh, gCPI ? 78 : 92))
        wLb := gAft ? label.new(keyAt(calK, 510), high, "you just missed me folks", xloc = xloc.bar_time, color = #00000000, textcolor = color.new(cGh, 25), style = label.style_label_lower_left, size = size.tiny, tooltip = "The trading day after a CPI day. Tested 2018–26: it went the same way as the CPI day " + (isES ? "46% ±10 of the time (any day → next day 49%)" : "44% ±10 of the time (any day → next day 48%)") + ", so no continuation edge showed up.") : na
    else
        wBx.set_top(math.max(wBx.get_top(), high))
        wBx.set_bottom(math.min(wBx.get_bottom(), low))
        if not na(wLb)
            wLb.set_y(wBx.get_top())
if gOn and showNot and not gCPI and not gAft and wkd and mod <= 510 and mod + tfM > 510
    label.new(bar_index, high, "nothing to see here folks", color = #00000000, textcolor = color.new(cMu, 20), style = label.style_label_down, size = size.tiny)
// every CPI 08:30 candle, kept and extended to the right like NWOG / NDOG
var array<box>   RCB = array.new<box>()
var array<label> RCT = array.new<label>()
var float rcH = na
var float rcL = na
var int   rcK = na
int  rcLen = relLenI == "1 min" ? 1 : relLenI == "5 min" ? 5 : 15
bool inRC  = tfM <= rcLen ? (mod >= 510 and mod < 510 + rcLen) : (mod <= 510 and mod + tfM > 510)
if gCPI and inRC
    if rcK != calK
        rcK := calK
        rcH := high
        rcL := low
    else
        rcH := math.max(rcH, high)
        rcL := math.min(rcL, low)
if markEv and gCPI and rcK == calK and not inRC and inRC[1]
    int   eff = math.max(rcLen, tfM)
    float q1  = eff <= 1 ? (isES ? 0.161 : 0.146) : eff <= 5 ? (isES ? 0.209 : 0.202) : (isES ? 0.234 : 0.235)
    float q2  = eff <= 1 ? (isES ? 0.400 : 0.369) : eff <= 5 ? (isES ? 0.470 : 0.432) : (isES ? 0.504 : 0.464)
    float xr  = tdO * ADRtd > 0 ? (rcH - rcL) / (tdO * ADRtd) : na
    string cat = na(xr) ? "" : xr >= q2 ? " · wild" : xr < q1 ? " · quiet" : " · average"
    for b in RCB                                              // older CPI candles fade back, the latest stays strong
        b.set_bgcolor(color.new(cGh, 93))
        b.set_border_color(color.new(cGh, 55))
    for t in RCT
        t.set_textcolor(color.new(cGh, 35))
    RCB.push(box.new(keyAt(calK, 510), rcH, time, rcL, xloc = xloc.bar_time, border_color = color.new(cGh, 15), border_width = 1, bgcolor = color.new(cGh, 86)))
    RCT.push(label.new(time, (rcH + rcL) / 2, "CPI " + str.format_time(keyTime(calK), "dd/MM", TZ) + cat, xloc = xloc.bar_time, color = #00000000, textcolor = cGh, style = label.style_label_left, size = size.small, tooltip = "CPI 08:30 candle (" + str.tostring(eff) + " min): " + pf(rcH - rcL) + " pts = " + (na(xr) ? "—" : str.tostring(xr, "0.00") + "× ADR20") + ". CPI release candles of this length since 2018: bottom third under " + str.tostring(q1, "0.00") + "× (quiet), top third over " + str.tostring(q2, "0.00") + "× (wild). A normal day's 08:30 candle of the same length is about " + (eff <= 1 ? "1/9" : eff <= 5 ? "1/5" : "1/4") + " the size of a CPI one (medians)."))
    if RCB.size() > relKeep
        RCB.shift().delete()
        RCT.shift().delete()
if RCB.size() > 0
    for b in RCB
        b.set_right(time)
    for t in RCT
        t.set_x(time)''', last='')

