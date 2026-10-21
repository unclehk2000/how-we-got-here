"""Vizard's Fed card: live FOMC odds from CBOT 30-day fed funds futures (ZQ), the same steps as CME FedWatch.
Blocks are dropped into core.pine at %FEDIN% (inputs), %FEDREQ% (requests and trackers, global scope),
%FEDDRAW% (shared values and the Full card, inside the last-bar block) and %FEDDRAWM% (the Mobile row)."""

FEDIN = '''grpF    = "Fed odds · 30-day fed funds futures"
showFd  = input.bool(true, "Fed card", group = grpF, inline = "f0", tooltip = "Odds for the next FOMC meetings from CBOT 30-day fed funds futures, worked out with the same steps as CME FedWatch. Full layout: its own card under DXY. Mobile: one row.", display = display.none)
fdRoot  = input.string("CBOT:ZQ", "Contracts", group = grpF, inline = "f0", tooltip = "TradingView prefix of the monthly 30-day fed funds contracts (CBOT:ZQZ2026 = Dec 2026). Seventeen months are loaded, from last month on. Without a CBOT data subscription TradingView delays them.", display = display.none)
sepAs   = input.string("16 Sep 2026", "Fed dots as of", group = grpF, inline = "f1", display = display.none)
sepY    = input.int(2026, "from", minval = 2025, maxval = 2035, group = grpF, inline = "f1", display = display.none)
sep1    = input.float(4.125, "Year-end medians", step = 0.125, group = grpF, inline = "f2", display = display.none)
sep2    = input.float(4.125, "", step = 0.125, group = grpF, inline = "f2", display = display.none)
sep3    = input.float(3.875, "", step = 0.125, group = grpF, inline = "f2", tooltip = "The Fed's dot plot: median year-end federal funds rate in the latest Summary of Economic Projections, for the first year and the two after (midpoint of the target range). Defaults read off the 16 Sep 2026 dot plot: 4.125 (2026), 4.125 (2027), 3.875 (2028). Update after each SEP (March, June, September, December). The Fed map sets them beside the market's path.", display = display.none)'''

FEDREQ = '''
// ═══════════════════════════════════════════════════════════════ Fed odds (CBOT 30-day fed funds futures)
// The same steps as CME FedWatch. A ZQ contract settles to 100 − the month's average effective fed funds rate. A decision
// takes effect the next day, so a meeting on day d of an N-day month splits it d / N − d (chaining rule: see fdRates). (end − start) ÷ 25bp gives the odds of the two nearest move sizes, and later meetings combine as a
// probability tree. Checked on CME's own FedWatch page for 12 Oct 2026 (ZQ prices and odds for eight meetings): within
// 0.06 percentage points everywhere.
// Seventeen calendar months from the one before the last bar's month, fixed when the script loads, so the same contracts
// are requested on every bar.
FDN = 17
var int fdY = year(last_bar_time, TZ)
var int fdM = month(last_bar_time, TZ)
fdYM(int i) =>
    int t = fdY * 12 + fdM - 2 + i
    [int(math.floor(t / 12)), t % 12 + 1]
fdTk(int i) =>
    [y, m] = fdYM(i)
    fdRoot + str.substring("FGHJKMNQUVXZ", m - 1, m) + str.tostring(y)
fdDim(int y, int m) => m == 2 ? (y % 4 == 0 ? 29 : 28) : m == 4 or m == 6 or m == 9 or m == 11 ? 30 : 31
fdDay(int y, int m) =>
    int d = 0
    for k in FO
        if int(k / 10000) == y and int(k / 100) % 100 == m
            d := k % 100
    d
string fdTf = timeframe.isintraday ? timeframe.period : "D"
float z0 = request.security(fdTk(0), fdTf, close, ignore_invalid_symbol = true)
float z1 = request.security(fdTk(1), fdTf, close, ignore_invalid_symbol = true)
float z2 = request.security(fdTk(2), fdTf, close, ignore_invalid_symbol = true)
float z3 = request.security(fdTk(3), fdTf, close, ignore_invalid_symbol = true)
float z4 = request.security(fdTk(4), fdTf, close, ignore_invalid_symbol = true)
float z5 = request.security(fdTk(5), fdTf, close, ignore_invalid_symbol = true)
float z6 = request.security(fdTk(6), fdTf, close, ignore_invalid_symbol = true)
float z7 = request.security(fdTk(7), fdTf, close, ignore_invalid_symbol = true)
float z8 = request.security(fdTk(8), fdTf, close, ignore_invalid_symbol = true)
float z9 = request.security(fdTk(9), fdTf, close, ignore_invalid_symbol = true)
float z10 = request.security(fdTk(10), fdTf, close, ignore_invalid_symbol = true)
float z11 = request.security(fdTk(11), fdTf, close, ignore_invalid_symbol = true)
float z12 = request.security(fdTk(12), fdTf, close, ignore_invalid_symbol = true)
float z13 = request.security(fdTk(13), fdTf, close, ignore_invalid_symbol = true)
float z14 = request.security(fdTk(14), fdTf, close, ignore_invalid_symbol = true)
float z15 = request.security(fdTk(15), fdTf, close, ignore_invalid_symbol = true)
float z16 = request.security(fdTk(16), fdTf, close, ignore_invalid_symbol = true)
array<float> fdZ = array.from(z0, z1, z2, z3, z4, z5, z6, z7, z8, z9, z10, z11, z12, z13, z14, z15, z16)
// end-of-day prices of the last six trading days (FDN per day, oldest first), and the 13:59 prices on a decision day
var array<float> fdH   = array.new<float>()
var array<float> fd14  = array.new<float>(FDN, na)
var int          fd14K = na
if tdSt and not na(z2[1])
    for v in array.from(z0[1], z1[1], z2[1], z3[1], z4[1], z5[1], z6[1], z7[1], z8[1], z9[1], z10[1], z11[1], z12[1], z13[1], z14[1], z15[1], z16[1])
        fdH.push(v)
    while fdH.size() > 6 * FDN
        fdH.shift()
if FO.includes(calK) and mod >= 840 and (mod[1] < 840 or calK[1] != calK)
    fd14  := array.from(z0[1], z1[1], z2[1], z3[1], z4[1], z5[1], z6[1], z7[1], z8[1], z9[1], z10[1], z11[1], z12[1], z13[1], z14[1], z15[1], z16[1])
    fd14K := calK

// the grid's calendar, worked out once: meeting day (0 = none), days in the month, meeting key (yyyymmdd)
var array<int> FMD = array.new<int>()
var array<int> FND = array.new<int>()
var array<int> FKY = array.new<int>()
if barstate.isfirst
    for i = 0 to FDN - 1
        [y, m] = fdYM(i)
        int d = fdDay(y, m)
        FMD.push(d)
        FND.push(fdDim(y, m))
        FKY.push(y * 10000 + m * 100 + d)
// start and end rate (%) of every meeting month in the grid, and the grid's meeting keys
// CME's chaining (checked on its 12 Oct 2026 screen to 0.06 pp): the end rate comes from the next month (its average when
// it has no meeting, else its start solved from its own contract, chained back from the next month without a meeting);
// the start is the prior month's average when that month has no meeting, else solved from the meeting month itself
fdRates(array<float> Z) =>
    array<float> A = array.new<float>(FDN, na)
    for i = 0 to FDN - 1
        if Z.size() > i
            float p = Z.get(i)
            A.set(i, na(p) ? na : 100.0 - p)
    array<float> S  = array.new<float>(FDN, na)
    array<float> E  = array.new<float>(FDN, na)
    array<float> SS = array.new<float>(FDN, na)
    for i = FDN - 1 to 0
        int   d = FMD.get(i)
        float a = A.get(i)
        if d > 0 and not na(a)
            float en = na
            if i < FDN - 1
                en := FMD.get(i + 1) == 0 ? A.get(i + 1) : SS.get(i + 1)
            if not na(en)
                E.set(i, en)
                SS.set(i, (a * FND.get(i) - en * (FND.get(i) - d)) / d)
    for i = 0 to FDN - 1
        int   d = FMD.get(i)
        float a = A.get(i)
        if d > 0 and not na(a)
            float st = SS.get(i)
            if i > 0
                if FMD.get(i - 1) == 0 and not na(A.get(i - 1))
                    st := A.get(i - 1)
            S.set(i, st)
            if na(E.get(i)) and not na(st) and FND.get(i) > d
                E.set(i, (a * FND.get(i) - st * d) / (FND.get(i) - d))
    [S, E, FKY]
// one meeting: the two nearest move sizes (in 25bp steps) and their odds
fdNode(float dl) =>
    float st = dl / 0.25
    float k  = math.floor(math.abs(st))
    float r  = math.abs(st) - k
    int   sg = st >= 0 ? 1 : -1
    [int(sg * k), int(sg * (k + 1)), 1.0 - r, r]
// the tree: odds over the total change (−20 … +20 steps) after one more meeting
fdStep(array<float> p, float dl) =>
    [k1, k2, w1, w2] = fdNode(dl)
    array<float> q = array.new<float>(41, 0.0)
    for x = 0 to 40
        float v = p.get(x)
        if v > 0
            int a = x + k1
            int b = x + k2
            if a >= 0 and a <= 40
                q.set(a, q.get(a) + v * w1)
            if b >= 0 and b <= 40
                q.set(b, q.get(b) + v * w2)
    q
// the next (up to) four meetings: keys, expected rate after each (%), the most likely total step and its odds, the next
// meeting's two outcomes and odds, the current target range's lower bound and the rate now
fdCalc(array<float> Z, int today, bool after) =>
    [S, E, KY] = fdRates(Z)
    array<int>   K  = array.new<int>()
    array<float> EA = array.new<float>()
    array<int>   MK = array.new<int>()
    array<float> MP = array.new<float>()
    float base = na
    float lo0  = na
    int   k1   = na
    int   k2   = na
    float w1   = na
    float w2   = na
    array<float> P = array.new<float>(41, 0.0)
    P.set(20, 1.0)
    for i = 0 to FDN - 1
        int ky = KY.get(i)
        if ky % 100 > 0 and (ky > today or (ky == today and not after)) and K.size() < 4
            float s = S.get(i)
            float e = E.get(i)
            if na(s) or na(e)
                break
            if K.size() == 0
                base := s
                lo0  := math.floor((s + 0.0001) / 0.25) * 0.25
                [a1, a2, b1, b2] = fdNode(e - s)
                k1 := a1
                k2 := a2
                w1 := b1
                w2 := b2
            P := fdStep(P, e - s)
            int   bk = 20
            float bp = 0.0
            for x = 0 to 40
                if P.get(x) > bp
                    bp := P.get(x)
                    bk := x
            K.push(ky)
            EA.push(e)
            MK.push(bk - 20)
            MP.push(bp)
    [K, EA, MK, MP, k1, k2, w1, w2, lo0, base]
fdWord(int k) => na(k) ? "—" : k == 0 ? "hold" : k < 0 ? "cut " + str.tostring(-25 * k) : "hike " + str.tostring(25 * k)
fdRng(float lo0, int k) => na(lo0) or na(k) ? "—" : str.tostring((lo0 + 0.25 * k) * 100, "0") + "–" + str.tostring((lo0 + 0.25 * (k + 1)) * 100, "0")
fdOdd(int k, int a1, int a2, float b1, float b2) => na(k) or na(a1) ? na : (k == a1 ? b1 : 0.0) + (k == a2 ? b2 : 0.0)
fdSg(float v, string f) => na(v) ? "—" : (v >= 0 ? "+" : "−") + str.tostring(math.abs(v), f)
fdDate(int k) => str.upper(str.format_time(keyTime(k), "dd MMM", TZ))
cFd = #5c6bc0

// ═══════════════════════════════════════════════════════════════ Fed map (indicator pane)
// Lines: the expected rate after each upcoming meeting (as of the last bar), bar by bar over the chart's recent history.
bool fmOn = paneV == "Fed map"
var array<int> FMI = array.new<int>()
if barstate.isfirst
    int tk0 = dateKey(last_bar_time)
    for i = 0 to FDN - 1
        if FMD.get(i) > 0 and FKY.get(i) >= tk0 and FMI.size() < 6
            FMI.push(i)
fmAt(array<float> E, int j) => FMI.size() > j ? E.get(FMI.get(j)) : na
float fm1 = na
float fm2 = na
float fm3 = na
float fm4 = na
float fm5 = na
float fm6 = na
if fmOn and last_bar_index - bar_index < 3000
    [fmS, fmE, fmK] = fdRates(fdZ)
    fm1 := fmAt(fmE, 0)
    fm2 := fmAt(fmE, 1)
    fm3 := fmAt(fmE, 2)
    fm4 := fmAt(fmE, 3)
    fm5 := fmAt(fmE, 4)
    fm6 := fmAt(fmE, 5)
plot(fm1, "Fed map · next meeting", color = #e040fb, linewidth = 2, style = plot.style_linebr, display = display.pane)
plot(fm2, "Fed map · meeting 2", color = #ba68c8, linewidth = 1, style = plot.style_linebr, display = display.pane)
plot(fm3, "Fed map · meeting 3", color = #9575cd, linewidth = 1, style = plot.style_linebr, display = display.pane)
plot(fm4, "Fed map · meeting 4", color = #7986cb, linewidth = 1, style = plot.style_linebr, display = display.pane)
plot(fm5, "Fed map · meeting 5", color = #64b5f6, linewidth = 1, style = plot.style_linebr, display = display.pane)
plot(fm6, "Fed map · meeting 6", color = #4dd0e1, linewidth = 1, style = plot.style_linebr, display = display.pane)
var array<box>      FMB = array.new<box>()
var array<label>    FMT = array.new<label>()
var array<line>     FML = array.new<line>()
var array<polyline> FMP = array.new<polyline>()
'''

FEDDRAW = '''
    // ── Fed card (CME FedWatch steps on CBOT ZQ): shared values for both layouts
    bool fdEv  = FO.includes(today)
    bool fdAft = fdEv and mod >= 840
    [fK, fE, fMK, fMP, fk1, fk2, fw1, fw2, fLo, fBase] = fdCalc(fdZ, today, fdAft)
    int  fdHn = fdH.size()
    array<float> fdZ1 = fdHn >= FDN ? fdH.slice(fdHn - FDN, fdHn) : array.new<float>()
    array<float> fdZ5 = fdHn >= 5 * FDN ? fdH.slice(fdHn - 5 * FDN, fdHn - 4 * FDN) : array.new<float>()
    [yK, yE, yMK, yMP, yk1, yk2, yw1, yw2, yLo, yBase] = fdCalc(fdZ1, today, fdAft)
    [wK, wE, wMK, wMP, wk1, wk2, ww1, ww2, wLo, wBase] = fdCalc(fdZ5, today, fdAft)
    bool  fOk  = fK.size() > 0
    int   kA   = na(fw1) ? na : fw1 >= fw2 ? fk1 : fk2
    int   kB   = na(fw1) ? na : fw1 >= fw2 ? fk2 : fk1
    float pA   = na(fw1) ? na : math.max(fw1, fw2)
    float pB   = na(fw1) ? na : math.min(fw1, fw2)
    float dA   = 100 * (pA - fdOdd(kA, yk1, yk2, yw1, yw2))
    float dB   = 100 * (pB - fdOdd(kB, yk1, yk2, yw1, yw2))
    float mv5  = fOk and wE.size() > 0 ? 100 * (fE.get(0) - wE.get(0)) : na
    // decision day after 14:00: what was decided, the surprise against 13:59 pricing and how the next meeting repriced
    bool  fDone = fdAft and fd14K == today
    int   fDec  = na
    float fSur  = na
    float fPx   = na
    float fPr   = na
    int   fNx   = na
    if fDone
        [S1, E1, KY1] = fdRates(fd14)
        [S2, E2, KY2] = fdRates(fdZ)
        int iT = KY1.indexof(today)
        if iT >= 0
            if not na(E2.get(iT)) and not na(S2.get(iT))
                fDec := int(math.round((E2.get(iT) - S2.get(iT)) / 0.25))
            if not na(E1.get(iT)) and not na(S1.get(iT))
                [c1, c2, q1, q2] = fdNode(E1.get(iT) - S1.get(iT))
                fPr := fdOdd(fDec, c1, c2, q1, q2)
            fSur := 100 * (E2.get(iT) - E1.get(iT))
            if iT < FDN - 1
                for i = iT + 1 to FDN - 1
                    if KY2.get(i) % 100 > 0 and na(fNx)
                        fNx := KY2.get(i)
                        fPx := 100 * (E2.get(i) - E1.get(i))
    string fPill = fDone ? "DECIDED" : not fOk ? "NO DATA" : str.upper(fdWord(kA)) + " " + p0(pA)
    color  fPbg  = fDone or not fOk or kA == 0 ? cNeu : kA < 0 ? cCold : cHot
    color  fPfg  = fDone or not fOk or kA == 0 ? cTx : #ffffff
    string fTip  = "Odds for the next FOMC meetings from CBOT 30-day fed funds futures, with the same steps as CME FedWatch: each contract settles to 100 − the month's average effective fed funds rate; the month after a meeting (or before it) anchors the rate after (or before) the decision, which takes effect the next day; the change ÷ 25bp gives the odds of the two nearest moves, combined across meetings as a probability tree. Checked against CME's own FedWatch page for 12 Oct 2026: all eight meetings within 0.06 percentage points. A live readout, not yet a tested signal: rows that held on NQ / ES come once the ZQ history is tested. TradingView delays CBOT data without a subscription."
    string pTip  = "Expected rate after this meeting against the rate now (bp), the most likely target range by then and its odds (probability tree over the meetings in between). Right: change since yesterday's close, bp."
'''

FEDDRAW_FULL = '''
    if showFd and not na(TS) and rFd >= 0
        int r0 = rFd
        cardHead(TS, r0, cFd, dot + " FED · " + (fOk ? "FOMC " + fdDate(fK.get(0)) : "no ZQ data"), fTip, fPill, fPfg, fPbg)
        cardSub(TS, r0 + 1, cFd, "FedWatch steps on CBOT ZQ · now " + (fOk ? fdRng(fLo, 0) : "—"), "odds", "1d")
        string oTip = "The next meeting's two outcomes: the expected change ÷ 25bp sits between two move sizes, and its distance to each is the odds. Right: change since yesterday's close, in percentage points."
        cardRow(TS, r0 + 2, cFd, "NEXT", false, fOk ? fdWord(kA) + (kA == 0 ? " at " : " → ") + fdRng(fLo, kA) : "—", fOk ? p0(pA) : "—", na(dA) ? "—" : fdSg(dA, "0"), oTip)
        cardRow(TS, r0 + 3, cFd, "", false, fOk ? fdWord(kB) + (kB == 0 ? " at " : " → ") + fdRng(fLo, kB) : "", fOk ? p0(pB) : "", na(dB) ? "" : fdSg(dB, "0"), oTip, cMu)
        for j = 1 to 3
            if j < fK.size()
                float cb = 100 * (fE.get(j) - fBase)
                float d1 = j < yE.size() ? 100 * (fE.get(j) - yE.get(j)) : na
                cardRow(TS, r0 + 3 + j, cFd, fdDate(fK.get(j)), false, fdRng(fLo, fMK.get(j)) + " most likely · " + p0(fMP.get(j)), fdSg(cb, "0") + "bp", fdSg(d1, "0.0"), pTip)
            else
                cardRow(TS, r0 + 3 + j, cFd, "", false, "", "", "", "")
        if fDone
            cardRow(TS, r0 + 7, cFd, "14:00", false, "decided " + fdWord(fDec) + " · priced " + (na(fPr) ? "—" : p0(fPr)) + " at 13:59", fdSg(fSur, "0.0") + "bp", na(fNx) ? "" : str.upper(str.format_time(keyTime(fNx), "MMM", TZ)) + " " + fdSg(fPx, "0.0"), "Decision day. Surprise = change in the expected rate after today's meeting from 13:59 to now (the classic fed funds futures surprise). Right: how the next meeting's expected rate moved since 13:59, bp.", math.abs(nz(fSur)) >= 5 ? cHot : cTx)
        else if fdEv
            cardRow(TS, r0 + 7, cFd, "TODAY", false, "statement 14:00 · priced " + fdWord(kA) + " " + (na(pA) ? "—" : p0(pA)), "", "", "Decision day: the statement lands at 14:00 ET, the press conference at 14:30. After 14:00 this row shows the surprise against the 13:59 pricing.")
        else
            cardRow(TS, r0 + 7, cFd, "5D", false, "next meeting's expected rate, 5 days", fdSg(mv5, "0.0") + "bp", "", "Change in the expected rate after the next meeting over the last five trading days (bp). Up = cuts priced out or hikes priced in.")
'''

FEDDRAWM = '''        if showFd and mFd >= 0
            string mTx = fDone ? "surprise " + fdSg(fSur, "0.0") + "bp" : not fOk ? "no ZQ data" : str.format_time(keyTime(fK.get(0)), "d MMM", TZ) + " " + fdWord(kA)
            string mVl = fDone ? (na(fNx) ? "—" : str.format_time(keyTime(fNx), "MMM", TZ) + " " + fdSg(fPx, "0")) : fOk ? p0(pA) : "—"
            string mTip = fTip + (fOk ? " Now " + fdRng(fLo, 0) + "; next meeting " + fdDate(fK.get(0)) + ": " + fdWord(kA) + " " + p0(pA) + ", " + fdWord(kB) + " " + p0(pB) + (fK.size() > 1 ? "; by " + fdDate(fK.get(fK.size() - 1)) + " " + fdSg(100 * (fE.get(fE.size() - 1) - fBase), "0") + "bp, most likely " + fdRng(fLo, fMK.get(fMK.size() - 1)) + " (" + p0(fMP.get(fMP.size() - 1)) + ")" : "") + "." : "")
            cardRow(TM, mFd, cFd, "FED", false, mTx, mVl, "", mTip, fDone and math.abs(nz(fSur)) >= 5 ? cHot : cTx)
            tc(TM, 4, mFd, fDone ? "DONE" : str.upper(fdWord(kA)), fPfg, fPbg, mTip, text.align_center, true)
'''

MAPX = '''
// ── Fed map, drawn ahead of the last bar: a column per meeting, a block per target range shaded by its odds, the
// expected path through them, the Fed's dot-plot medians at each year's last meeting
if barstate.islast
    for b in FMB
        b.delete()
    for t in FMT
        t.delete()
    for l in FML
        l.delete()
    for p in FMP
        p.delete()
    FMB.clear()
    FMT.clear()
    FML.clear()
    FMP.clear()
    if fmOn
        int  today = calK
        bool aft   = FO.includes(today) and mod >= 840
        [S, E, KY] = fdRates(fdZ)
        array<int> up = array.new<int>()
        for i = 0 to FDN - 1
            int ky = KY.get(i)
            if ky % 100 > 0 and (ky > today or (ky == today and not aft)) and not na(S.get(i)) and not na(E.get(i)) and up.size() < 10
                up.push(i)
        if up.size() == 0
            FMT.push(label.new(bar_index, close, "Fed map: no CBOT ZQ data on this chart", style = label.style_label_left, color = #00000000, textcolor = cMu, size = size.small))
        else
            float base = S.get(up.get(0))
            float lo0  = math.floor((base + 0.0001) / 0.25) * 0.25
            int   x0   = bar_index + 8
            int   gx   = 10
            int   xL   = math.max(0, bar_index - 300)
            int   xR   = x0 + gx * (up.size() - 1) + 6
            FMB.push(box.new(xL, lo0 + 0.25, xR, lo0, border_color = #00000000, bgcolor = color.new(cTx, 92), text = "target now " + fdRng(lo0, 0), text_color = cMu, text_size = size.tiny, text_halign = text.align_left, text_valign = text.align_bottom))
            array<chart.point> pts = array.new<chart.point>()
            pts.push(chart.point.from_index(bar_index, base))
            array<float> P = array.new<float>(41, 0.0)
            P.set(20, 1.0)
            float yMin = lo0
            float yMax = lo0 + 0.25
            for j = 0 to up.size() - 1
                int i  = up.get(j)
                int xc = x0 + gx * j
                P := fdStep(P, E.get(i) - S.get(i))
                for x = 0 to 40
                    float p = P.get(x)
                    if p >= 0.01
                        float yl = lo0 + 0.25 * (x - 20)
                        FMB.push(box.new(xc - 4, yl + 0.25, xc + 4, yl, border_color = cBg, border_width = 1, bgcolor = color.from_gradient(p, 0.0, 0.6, color.new(cGh, 88), color.new(cGh, 0)), text = p >= 0.04 ? str.tostring(100 * p, "0") + "%" : "", text_color = p >= 0.3 ? #ffffff : cTx, text_size = size.tiny))
                        yMin := math.min(yMin, yl)
                        yMax := math.max(yMax, yl + 0.25)
                pts.push(chart.point.from_index(xc, E.get(i)))
            FMP.push(polyline.new(pts, curved = false, line_color = color.new(cTx, 15), line_width = 2))
            for j = 0 to up.size() - 1
                int    i   = up.get(j)
                int    xc  = x0 + gx * j
                int    yr  = int(KY.get(i) / 10000)
                bool   eoy = j == up.size() - 1 ? int(KY.get(i) / 100) % 100 == 12 : false
                if j < up.size() - 1
                    eoy := int(KY.get(up.get(j + 1)) / 10000) != yr
                float  sep = yr == sepY ? sep1 : yr == sepY + 1 ? sep2 : yr == sepY + 2 ? sep3 : na
                bool   dot_ = eoy and not na(sep)
                color  lc  = j == 0 ? #e040fb : j == 1 ? #ba68c8 : j == 2 ? #9575cd : j == 3 ? #7986cb : j == 4 ? #64b5f6 : j == 5 ? #4dd0e1 : cSub
                FMT.push(label.new(xc, E.get(i), "", color = cTx, style = label.style_circle, size = size.tiny, tooltip = fdDate(KY.get(i)) + ": expected " + str.tostring(E.get(i), "0.000") + "% · " + fdSg(100 * (E.get(i) - base), "0") + "bp from now"))
                if dot_
                    FMT.push(label.new(xc + 5, sep, "", style = label.style_diamond, color = #ffffff, size = size.small, tooltip = "Fed dot plot (SEP " + sepAs + "): median end-" + str.tostring(yr) + " rate " + str.tostring(sep, "0.000") + "%"))
                FMT.push(label.new(xc, yMin - 0.02, fdDate(KY.get(i)) + "\\n" + fdSg(100 * (E.get(i) - base), "0") + "bp" + (dot_ ? "\\nFed " + str.tostring(sep, "0.000") + "\\nmkt " + fdSg(100 * (E.get(i) - sep), "0") + "bp" : ""), style = label.style_label_up, color = #00000000, textcolor = lc, size = size.tiny, tooltip = dot_ ? "White diamond: the Fed's dot plot (SEP " + sepAs + "), median year-end " + str.tostring(yr) + " rate " + str.tostring(sep, "0.000") + "%. The market prices " + str.tostring(E.get(i), "0.000") + "% after the " + fdDate(KY.get(i)) + " meeting, " + fdSg(100 * (E.get(i) - sep), "0") + "bp " + (E.get(i) >= sep ? "above" : "below") + " the Fed's own median." : "Date colour = this meeting's line on the left."))
            [k1, k2, w1, w2] = fdNode(E.get(up.get(0)) - S.get(up.get(0)))
            int   kA = w1 >= w2 ? k1 : k2
            float pA = math.max(w1, w2)
            FMT.push(label.new(x0, yMax + 0.02, fdDate(KY.get(up.get(0))) + " · " + str.upper(fdWord(kA)) + " " + p0(pA), style = label.style_label_down, color = kA == 0 ? cNeu : kA < 0 ? cCold : cHot, textcolor = kA == 0 ? cTx : #ffffff, size = size.small, tooltip = "Next meeting: " + fdWord(k1) + " " + p0(w1) + ", " + fdWord(k2) + " " + p0(w2) + "."))
            FMT.push(label.new(xL, yMax + 0.02, "FED MAP · lines: each meeting's expected rate, bar by bar · blocks: odds of each target range per meeting · white ◆: the Fed's dots (SEP " + sepAs + ")", style = label.style_label_lower_left, color = #00000000, textcolor = cMu, size = size.tiny, tooltip = "From CBOT 30-day fed funds futures with CME FedWatch's steps (checked on CME's own page for 12 Oct 2026: within 0.06 pp). TradingView delays CBOT data without a subscription."))
'''
HEAD = """if barstate.islast
    int    today = calK
    string dot   = barstate.isrealtime ? (beat % 2 == 0 ? "●" : "○") : "◆"
"""
# its own last-bar block (Pine caps the size of a single if block)
EXTRA = HEAD + FEDDRAW.lstrip('\n') + FEDDRAW_FULL + "    if mob and not na(TM)\n" + FEDDRAWM
PANEIN = '''paneV  = input.string("Event clock", "Pane", options = ["Event clock", "Fed map"], group = grpK, tooltip = "Event clock: today's running range against this event's days.\\nFed map: the Fed path the market prices. Lines: each upcoming FOMC meeting's expected rate, bar by bar, so you can watch it reprice (on a decision day, live through 14:00 and the press conference). Ahead of the last bar: one column per meeting, a block for each target range with its odds, the expected path through them, and the Fed's own dot-plot medians for comparison. From CBOT 30-day fed funds futures with CME FedWatch's steps.", display = display.none)'''
EXTRA = EXTRA + MAPX
FED = dict(fedin=FEDIN, fedreq=FEDREQ, extra=EXTRA, panein=PANEIN)
