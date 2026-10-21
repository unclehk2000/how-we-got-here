# ───────────────────────────────────────────── Cero (6) · NFP
IND['Cero'] = dict(short='Cero', ghost='#ff7043', keys=['NFP'], header='''// Cero (虚閃) · Model 6: NFP days (Employment Situation, released 08:30 ET).
// The model's own structure on the chart: the 07:00–09:00 dealing range, the 08:30–08:45 hands-off window, the 08:50
// line between the release push and the second stage, and the RTH gap (prior 16:14 close and its 50%).''',
own='''ownProfile(int tk, int pk, int today) =>
    bool now = NP.includes(tk)
    int  rf  = na(tk) ? today : math.max(tk, today)
    [0, now, now ? tk : nextOf(NP, rf)]
ownNext(int today) =>
    int n1 = nextOf(NP, today)
    ["NFP 08:30 · M6 Cero", n1, "NFP after that", na(n1) ? na : nextOf(NP, addDays(n1, 1))]''',
struct='''int  tfM  = math.max(1, int(timeframe.in_seconds() / 60))
bool cNFP = NP.includes(calK)
bool cOn  = showStr and recent and cNFP
var float drH = na
var float drL = na
var int   drK = na
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
        line.new(keyAt(calK, 420), drH, keyAt(calK, 974), drH, xloc = xloc.bar_time, color = cLvl, width = 1, style = line.style_dashed)
        line.new(keyAt(calK, 420), drL, keyAt(calK, 974), drL, xloc = xloc.bar_time, color = cLvl, width = 1, style = line.style_dashed)
        label.new(keyAt(calK, 420), drH, "DR high", xloc = xloc.bar_time, color = #00000000, textcolor = cLvl, style = label.style_label_lower_left, size = size.tiny, tooltip = "NFP dealing range 07:00–09:00 ET")
        label.new(keyAt(calK, 420), drL, "DR low", xloc = xloc.bar_time, color = #00000000, textcolor = cLvl, style = label.style_label_upper_left, size = size.tiny, tooltip = "NFP dealing range 07:00–09:00 ET")
    if mod <= 530 and mod + tfM > 530
        line.new(keyAt(calK, 530), close, keyAt(calK, 530), close + syminfo.mintick, xloc = xloc.bar_time, extend = extend.both, color = color.new(cLvl, 60), style = line.style_dotted)
    if rthSt and not na(gapPC)
        line.new(time, gapPC, keyAt(calK, 974), gapPC, xloc = xloc.bar_time, color = color.new(cLvl, 40), style = line.style_dotted)
        line.new(time, gapCE, keyAt(calK, 974), gapCE, xloc = xloc.bar_time, color = color.new(cLvl, 20), style = line.style_dotted)
        label.new(keyAt(calK, 974), gapCE, "gap 50%", xloc = xloc.bar_time, color = #00000000, textcolor = cLvl, style = label.style_label_left, size = size.tiny, tooltip = "RTH gap 50% = (prior 16:14 close + 09:30 open) ÷ 2. NFP days filled the full gap less often than normal days (" + (isES ? "53% vs 62%" : "54% vs 63%") + ").")
    if markEv and mod <= 510 and mod + tfM > 510
        label.new(bar_index, high, "NFP", color = #00000000, textcolor = cGh, style = label.style_label_down, size = size.tiny, tooltip = "NFP 08:30 ET " + str.format_time(time, "dd MMM yyyy", TZ))
bgcolor(cOn and mod >= 510 and mod < 525 ? cHands : na, title = "08:30–08:45 hands-off")''', last='')

# ───────────────────────────────────────────── Gran Rey Cero (7–8) · CPI
IND['Gran Rey Cero'] = dict(file='Gran_Rey_Cero', short='Gran Rey', ghost='#e53935', keys=['CPI'], header='''// Gran Rey Cero (王虚の閃光) · Models 7–8: CPI days (released 08:30 ET).
// The model's own structure on the chart: the 07:30–08:30 pre-release range and the first side of it taken after the
// release, the 08:30–08:45 hands-off window, the 08:50 line between the release push and the second stage, and the RTH
// gap (prior 16:14 close and its 50%).''',
own='''ownProfile(int tk, int pk, int today) =>
    bool now = CP.includes(tk)
    int  rf  = na(tk) ? today : math.max(tk, today)
    [0, now, now ? tk : nextOf(CP, rf)]
ownNext(int today) =>
    int n1 = nextOf(CP, today)
    ["CPI 08:30 · M7–8 Gran Rey Cero", n1, "CPI after that", na(n1) ? na : nextOf(CP, addDays(n1, 1))]''',
struct='''int  tfM  = math.max(1, int(timeframe.in_seconds() / 60))
bool gCPI = CP.includes(calK)
bool gOn  = showStr and recent and gCPI
var float drH = na
var float drL = na
var int   drK = na
var int   swp = 0
string swTip = "First side of the 07:30–08:30 range taken after the release. The day's bigger move (from 08:30) went the same way " + (isES ? "67% of the time vs 56% on normal days, but only 53% in 2025–26 (71% in 2018–24)." : "70% of the time vs 56% on normal days, and 71% in 2025–26.")
if gOn
    if mod >= 450 and mod < 510
        if drK != calK
            drK := calK
            drH := high
            drL := low
            swp := 0
        else
            drH := math.max(drH, high)
            drL := math.min(drL, low)
    if drK == calK and mod >= 510 and (mod[1] < 510 or calK != calK[1])
        line.new(keyAt(calK, 450), drH, keyAt(calK, 974), drH, xloc = xloc.bar_time, color = cLvl, width = 1, style = line.style_dashed)
        line.new(keyAt(calK, 450), drL, keyAt(calK, 974), drL, xloc = xloc.bar_time, color = cLvl, width = 1, style = line.style_dashed)
        label.new(keyAt(calK, 450), drH, "PR high", xloc = xloc.bar_time, color = #00000000, textcolor = cLvl, style = label.style_label_lower_left, size = size.tiny, tooltip = "CPI pre-release range 07:30–08:30 ET")
        label.new(keyAt(calK, 450), drL, "PR low", xloc = xloc.bar_time, color = #00000000, textcolor = cLvl, style = label.style_label_upper_left, size = size.tiny, tooltip = "CPI pre-release range 07:30–08:30 ET")
    if drK == calK and mod >= 510 and mod < 975 and swp == 0 and not na(drH)
        if low < drL
            swp := -1
            label.new(bar_index, low, "1st sweep ▼", color = #00000000, textcolor = cLvl, style = label.style_label_up, size = size.tiny, tooltip = swTip)
        else if high > drH
            swp := 1
            label.new(bar_index, high, "1st sweep ▲", color = #00000000, textcolor = cLvl, style = label.style_label_down, size = size.tiny, tooltip = swTip)
    if mod <= 530 and mod + tfM > 530
        line.new(keyAt(calK, 530), close, keyAt(calK, 530), close + syminfo.mintick, xloc = xloc.bar_time, extend = extend.both, color = color.new(cLvl, 60), style = line.style_dotted)
    if rthSt and not na(gapPC)
        line.new(time, gapPC, keyAt(calK, 974), gapPC, xloc = xloc.bar_time, color = color.new(cLvl, 40), style = line.style_dotted)
        line.new(time, gapCE, keyAt(calK, 974), gapCE, xloc = xloc.bar_time, color = color.new(cLvl, 20), style = line.style_dotted)
        label.new(keyAt(calK, 974), gapCE, "gap 50%", xloc = xloc.bar_time, color = #00000000, textcolor = cLvl, style = label.style_label_left, size = size.tiny, tooltip = "RTH gap 50% = (prior 16:14 close + 09:30 open) ÷ 2")
    if markEv and mod <= 510 and mod + tfM > 510
        label.new(bar_index, high, "CPI", color = #00000000, textcolor = cGh, style = label.style_label_down, size = size.tiny, tooltip = "CPI 08:30 ET " + str.format_time(time, "dd MMM yyyy", TZ))
bgcolor(gOn and mod >= 510 and mod < 525 ? cHands : na, title = "08:30–08:45 hands-off")''', last='')

