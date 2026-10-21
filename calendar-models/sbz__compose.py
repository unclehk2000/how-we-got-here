"""Senbonzakura (combined): Kageyoshi (close curves on the price chart, force_overlay) + Senkei (the Fed map, this pane),
Full or Mobile (Hakuteiken) layout. Built from the standalone Senbonzakura and Arrancar sources."""
import re, sys
sys.path.insert(0, '/home/claude/hm')
from cardq import P92
A = open('/home/claude/hm/arrancar/Arrancar.pine', encoding='utf-8').read()
K = open('/home/claude/hm/senbon/Senbonzakura.pine', encoding='utf-8').read()
def cut(s, a, b=None):
    i = s.index(a); j = s.index(b, i) if b else len(s)
    return s[i:j]
def rep(s, old, new, n=1):
    assert s.count(old) == n, (old[:90], s.count(old)); return s.replace(old, new)

HEAD = '''//@version=6
// This Source Code Form is subject to the terms of the Mozilla Public License 2.0 at https://mozilla.org/MPL/2.0/
// © Unclehk2000
//
// Senbonzakura · the distribution of what comes next, in two forms.
// Kageyoshi (price chart): where today's close is likely to land, as sideways curves right of price for ES, NQ and RTY.
//   Pink bars, historical: every trading day Jan 2018 – Oct 2026 (ES to Aug 2026) on 1-minute data, the close minus the
//   price at each half hour from 18:00, in units of the prior 20 days' average range (ADR20), scaled to today's ADR20 and
//   centred on the last price, so the curve narrows as the day runs out. Blue bell, options-implied: VIX (ES), VXN (NQ) or
//   RVX (RTY) ÷ √252 for one day, spread through the day by the share of the day's variance still ahead, lognormal.
//   Market structure: below the prior day's low or under the month's open the close usually lands further away; above
//   the prior day's high or at the all-time high, nearer. The historical curve's width is scaled by the effects that held
//   (p < 0.05, same side in 2018–24 and 2025–26); direction held nowhere, so the centre is never moved. PDH, PDL, the
//   month's open and the ATH are drawn across the curves with the odds of the close finishing beyond each.
//   Tested: built on 2018–24 and checked on 2025–26, the historical 80% band held 83–84% of closes; with context the
//   below-PDL days went from 73% to 79% (NQ) and 70% to 76% (ES). On ES the VIX curve ran 1.3–1.5× wider than what followed.
// Senkei (this pane): the Fed path the market prices, from CBOT 30-day fed funds futures (ZQ) with CME FedWatch's steps
//   (checked on CME's page for 12 Oct 2026: within 0.06 percentage points). Left of the last bar, the expected rate after
//   each of the next six meetings, bar by bar; right of it, a column per meeting with a block for each 25bp target range
//   shaded by its odds, the expected path, and the Fed's year-end dot-plot medians (◆).
// Layout: Full, or Mobile (Hakuteiken: every blade folded into one) for a phone screen.
// Keep up to date: FOMC dates are loaded to Dec 2027; the dot-plot inputs change with each SEP. TradingView delays CBOT
// data without a subscription. A map of how far things usually travel, not a call on direction. Part of the Hueco Mundo
// megazord. Written from scratch; Kageyoshi's idea after options probability-distribution tools.

indicator("Senbonzakura", "Senbon", overlay = false, precision = 3, max_boxes_count = 500, max_lines_count = 40, max_labels_count = 150, max_polylines_count = 6)

TZ = "America/New_York"

// ═══════════════════════════════════════════════════════════════ Inputs
grpG   = "Senbonzakura"
layI   = input.string("Full", "Layout", options = ["Full", "Mobile"], group = grpG, tooltip = "Full: every label, ten Fed meetings, long curves.\\nMobile (Hakuteiken): every blade folded into one for a phone screen. Shorter curves and fewer bins, five Fed meetings in narrower columns, short labels and a three-line header; the full wording stays in the tooltips.", display = display.none)
showK  = input.bool(true, "Kageyoshi · where today's close lands (price chart)", group = grpG, display = display.none)
showS  = input.bool(true, "Senkei · the Fed path (this pane)", group = grpG, tooltip = "Switch Senkei off to keep only the curves on the price chart; the pane then stays empty and can be made small.", display = display.none)
themeI = input.string("Auto", "Theme", options = ["Auto", "Dark", "Light"], group = grpG, inline = "g0", display = display.none)
txtI   = input.string("Small", "Text", options = ["Tiny", "Small", "Normal"], group = grpG, inline = "g0", tooltip = "Mobile always uses tiny text.", display = display.none)

grpF  = "Kageyoshi · forecast"
tgtI  = input.string("Trading day (17:00)", "Close", options = ["Trading day (17:00)", "RTH (16:14)"], group = grpF, tooltip = "Which close the curves forecast: the CME trading day's (the daily candle, 17:00 ET) or the RTH close (the 16:14 bar). Between the close and the next 18:00 open, and when the market is shut, the curves show the next session from the last price.", display = display.none)
showH = input.bool(true, "Historical (2018–26 data)", group = grpF, inline = "f1", display = display.none)
showI = input.bool(true, "Options-implied", group = grpF, inline = "f1", display = display.none)
ivES  = input.symbol("CBOE:VIX", "Implied vol: ES", group = grpF, inline = "f2", display = display.none)
ivNQ  = input.symbol("CBOE:VXN", "NQ", group = grpF, inline = "f2", display = display.none)
ivRTY = input.symbol("CBOE:RVX", "RTY", group = grpF, inline = "f2", tooltip = "30-day implied volatility indices for the S&P 500, the Nasdaq-100 and the Russell 2000. One day = the index ÷ √252, spread through the day by the share of the day's variance still ahead.", display = display.none)

grpC   = "Kageyoshi · market structure"
ctxOn  = input.bool(true, "Scale the historical curve by context", group = grpC, tooltip = "Where price sits against the prior day's high and low, the month's open and the all-time high changes how far the close usually lands, not which way: below the prior day's low or under the month's open the day runs wider, above the prior day's high or at the all-time high it runs narrower. Only effects that held (p < 0.05, same side in 2018–24 and 2025–26) are applied; the multiplier shows in the header.", display = display.none)
showLv = input.bool(true, "PDH · PDL · monthly open · ATH", group = grpC, inline = "c1", display = display.none)
cLv    = input.color(#ffb300, "", group = grpC, inline = "c1", display = display.none)
wLv    = input.int(1, "Width", minval = 1, maxval = 5, group = grpC, inline = "c1", tooltip = "Drawn across the curves when they fall inside them, each with the odds of the close finishing beyond it: historical / implied. Colour and line width (1–5) alongside.", display = display.none)

grpL  = "Kageyoshi · layout"
offI  = input.int(6, "Offset", minval = 1, maxval = 100, group = grpL, inline = "l0", display = display.none)
lenI  = input.int(60, "Length", minval = 10, maxval = 300, group = grpL, inline = "l0", display = display.none)
nBin  = input.int(40, "Bins", minval = 15, maxval = 80, group = grpL, inline = "l0", tooltip = "Offset: bars from the last bar to the curves' base. Length: bars from the base to the most likely bin. Bins: across the 1–99% range of both curves. Mobile caps them at 3, 26 and 24.", display = display.none)
showB = input.bool(true, "Bands and median", group = grpL, inline = "l1", display = display.none)
showT = input.bool(true, "Header", group = grpL, inline = "l1", display = display.none)
cH    = input.color(#f06292, "Historical", group = grpL, inline = "l2", display = display.none)
cI    = input.color(#2962ff, "Implied", group = grpL, inline = "l2", display = display.none)

grpZ     = "Senkei · contracts and map"
fdRoot   = input.string("CBOT:ZQ", "30-day fed funds futures", group = grpZ, tooltip = "TradingView prefix of the monthly contracts. The script adds the month code and year (e.g. CBOT:ZQX2026) and reads seventeen calendar months, starting with the one before the current month.", display = display.none)
nAhead   = input.int(10, "Meetings", minval = 2, maxval = 10, group = grpZ, inline = "m0", display = display.none)
minP     = input.float(1.0, "hide blocks under %", minval = 0.0, maxval = 10.0, step = 0.5, group = grpZ, inline = "m0", tooltip = "One column per upcoming meeting. A block per 25bp target range, shaded by its odds after that meeting (the probability tree through every meeting before it). Blocks under this share are left out. Mobile shows five meetings.", display = display.none)
mOff     = input.int(8, "Offset", minval = 2, maxval = 60, group = grpZ, inline = "m1", display = display.none)
mGap     = input.int(10, "Column spacing", minval = 6, maxval = 30, group = grpZ, inline = "m1", tooltip = "In bars: the first column's distance from the last bar, and the distance between columns.", display = display.none)
cCl      = input.color(#ab47bc, "Cloud", group = grpZ, inline = "m2", display = display.none)
showPct  = input.bool(true, "Odds in blocks", group = grpZ, inline = "m2", display = display.none)
showPath = input.bool(true, "Expected path", group = grpZ, inline = "m2", display = display.none)
showBand = input.bool(true, "Current target range", group = grpZ, inline = "m3", display = display.none)
showHL   = input.bool(true, "History lines, last", group = grpZ, inline = "m4", display = display.none)
hBars    = input.int(3000, "bars", minval = 100, maxval = 5000, group = grpZ, inline = "m4", tooltip = "Lines for the next six meetings (as of now), each worked out on every one of the last N bars from that bar's ZQ prices. A line's colour matches its date under the columns.", display = display.none)

grpD    = "Senkei · Fed dots (Summary of Economic Projections)"
showDot = input.bool(true, "Show", group = grpD, inline = "d0", display = display.none)
sepAs   = input.string("16 Sep 2026", "as of", group = grpD, inline = "d0", display = display.none)
sepY    = input.int(2026, "Year-end medians from", minval = 2025, maxval = 2035, group = grpD, inline = "d1", display = display.none)
sep1    = input.float(4.125, "", step = 0.125, group = grpD, inline = "d2", display = display.none)
sep2    = input.float(4.125, "", step = 0.125, group = grpD, inline = "d2", display = display.none)
sep3    = input.float(3.875, "", step = 0.125, group = grpD, inline = "d2", tooltip = "The median federal funds rate the Fed's officials project for the end of the first year, the next and the one after (the dot plot). Drawn as ◆ beside the last meeting of each year, with the market's gap to it under the column. Update after each SEP.", display = display.none)

// ═══════════════════════════════════════════════════════════════ Layout and theme
bool mob  = layI == "Mobile"
int  offK = mob ? math.min(offI, 3) : offI                       // Kageyoshi: offset, length, bins
int  lenK = mob ? math.min(lenI, 26) : lenI
int  binK = mob ? math.min(nBin, 24) : nBin
int  nAh  = mob ? math.min(nAhead, 5) : nAhead                   // Senkei: meetings, offset, spacing, column half-width
int  offS = mob ? math.min(mOff, 4) : mOff
int  gxS  = mob ? math.min(mGap, 7) : mGap
int  hwS  = mob ? 3 : 4
bgLum = 0.299 * color.r(chart.bg_color) + 0.587 * color.g(chart.bg_color) + 0.114 * color.b(chart.bg_color)
dark  = themeI == "Dark" or (themeI == "Auto" and bgLum < 128)
cTx   = dark ? #e6e9ef : #131722
cSub  = dark ? #9aa3b5 : #4a5163
cMu   = dark ? #5d6476 : #9aa1b2
cHot  = dark ? #ff8a65 : #d84315
cCold = dark ? #64b5f6 : #1565c0
cNeu  = dark ? #3a3f4b : #d1d4dc
cDot  = dark ? #ffffff : #131722
cBox  = dark ? #161a23 : #f4f6f9
txSz  = mob or txtI == "Tiny" ? size.tiny : txtI == "Small" ? size.small : size.normal
// one colour per upcoming meeting: Senkei's history lines and the dates under its columns
L1 = #e040fb
L2 = #ba68c8
L3 = #9575cd
L4 = #7986cb
L5 = #64b5f6
L6 = #4dd0e1
pf(float v) => str.tostring(v, format.mintick)
p0(float v) => str.tostring(v * 100, "0") + "%"
'''

# ── Kageyoshi: data, setup and helpers from the standalone script (no inputs, no theme)
kData = cut(K, '// ═══════════════════════════════════════════════════════════════ Data', '// ═══════════════════════════════════════════════════════════════ Helpers')
kData = kData.replace('═ Data\n', '═ Kageyoshi · data\n', 1)
kData = rep(kData, 'float  adr   = request.security(syminfo.tickerid, "D", ta.sma(high - low, 20)[1], lookahead = barmerge.lookahead_on)',
                   '[adr, adrT] = request.security(syminfo.tickerid, "D", [ta.sma(high - low, 20)[1], ta.sma(high - low, 20)], lookahead = barmerge.lookahead_on)   // adrT: with today, for the next session')
kHelp = cut(K, '// ═══════════════════════════════════════════════════════════════ Helpers', '// ═══════════════════════════════════════════════════════════════ The curves, right of the last bar')
kHelp = rep(kHelp, 'pf(float v) => str.tostring(v, format.mintick)\np0(float v) => str.tostring(v * 100, "0") + "%"\n', '')
kHelp = kHelp.replace('═ Helpers\n', '═ Kageyoshi · helpers\n', 1)
kDraw = cut(K, '// ═══════════════════════════════════════════════════════════════ The curves, right of the last bar')
kDraw = kDraw.replace('═ The curves, right of the last bar\n', '═ Kageyoshi · the curves, right of the last bar on the price chart\n', 1)
# only when Kageyoshi is on; Full / Mobile geometry
kDraw = rep(kDraw, '    float P   = close\n', '    float P   = close\n    float adrU = nextS and not na(adrT) ? adrT : adr                // the next session: ADR20 including today\n')
_i = kDraw.index('    float adrU =') + len('    float adrU = nextS and not na(adrT) ? adrT : adr')
kDraw = kDraw[:_i] + re.sub(r'\badr\b', 'adrU', kDraw[_i:])
kDraw = rep(kDraw, '    if hOk or iOk\n', '    if showK and (hOk or iOk)\n')
kDraw = rep(kDraw, '(hi - lo) / nBin)', '(hi - lo) / binK)')
kDraw = rep(kDraw, '        int x0 = bar_index + offI\n', '        int x0 = bar_index + offK\n')
kDraw = kDraw.replace('lenI', 'lenK')
# every drawing goes onto the price chart
for f in ('box.new(', 'line.new(', 'label.new(', 'polyline.new('):
    out, i = [], 0
    while True:
        k = kDraw.find(f, i)
        if k < 0: out.append(kDraw[i:]); break
        if k > 0 and (kDraw[k - 1].isalnum() or kDraw[k - 1] == '_'):   # 'line.new(' inside 'polyline.new('
            out.append(kDraw[i:k + len(f)]); i = k + len(f); continue
        j = k + len(f); d = 1
        while d:
            ch = kDraw[j]
            if ch == '"': j = kDraw.index('"', j + 1)
            elif ch == '(': d += 1
            elif ch == ')': d -= 1
            j += 1
        call = kDraw[k:j]
        out.append(kDraw[i:k] + call[:-1] + ', force_overlay = true)'); i = j
    kDraw = ''.join(out)
# mobile: short band / median / level labels, no per-bin label, three-line header
kDraw = rep(kDraw, '                ST.push(label.new(x0 - 2, h90, "80% " + pf(h90),', '                if not mob\n                    ST.push(label.new(x0 - 2, h90, "80% " + pf(h90),')
kDraw = rep(kDraw, '                ST.push(label.new(x0 - 2, h10, "80% " + pf(h10),', '                    ST.push(label.new(x0 - 2, h10, "80% " + pf(h10),')
kDraw = rep(kDraw, 'ST.push(label.new(x0 + lenK, h50, "median " + (h50 >= P ? "+" : "−") + pf(math.abs(h50 - P)),', 'ST.push(label.new(x0 + lenK, h50, (mob ? "med " : "median ") + (h50 >= P ? "+" : "−") + pf(math.abs(h50 - P)),')
kDraw = rep(kDraw, '                    string od  = (up_ ? "▲" : "▼") + (na(ph) ? "—" : str.tostring(ph * 100, "0")) + " / " + (na(pi_) ? "—" : str.tostring(pi_ * 100, "0")) + "%"',
                   '                    string od  = (up_ ? "▲" : "▼") + (na(ph) ? "—" : str.tostring(ph * 100, "0")) + (mob ? "/" : " / ") + (na(pi_) ? "—" : str.tostring(pi_ * 100, "0")) + "%"')
kDraw = rep(kDraw, '        ST.push(label.new(x0 + lenK, yM,', '        if not mob\n            ST.push(label.new(x0 + lenK, yM,')
kDraw = rep(kDraw, '''            ST.push(label.new(x0, b0 + nb * bw + bw, "SENBONZAKURA · " + symR + (own ? "" : " DATA") + " · " + whn + (hL == "" ? "" : "\\n" + hL) + (iL == "" ? "" : "\\n" + iL) + (cxL == "" ? "" : "\\n" + cxL) + (lvT == "" ? "" : "\\n" + lvT),''',
'''            string hdr  = "SENBONZAKURA · " + symR + (own ? "" : " DATA") + " · " + whn + (hL == "" ? "" : "\\n" + hL) + (iL == "" ? "" : "\\n" + iL) + (cxL == "" ? "" : "\\n" + cxL) + (lvT == "" ? "" : "\\n" + lvT)
            if mob
                string mW = (rth ? "16:14" : "17:00") + (nextS ? " next" : " " + str.tostring(int(left / 60)) + "h" + str.tostring(left % 60, "00"))
                hdr := "SBZ " + symR + " · " + mW + (hOk ? "\\nhist ▲" + p0(1 - cdfAt(xs, ps, P)) + " · " + pf(h10) + "–" + pf(h90) : "") + (iOk or (ctxOn and hOk) ? "\\n" + (iOk and hOk and h90 > h10 ? "impl ×" + str.tostring((i90 - i10) / (h90 - h10), "0.0") : iOk ? "impl " + pf(i10) + "–" + pf(i90) : "") + (ctxOn and hOk ? (iOk ? " · " : "") + "ctx ×" + str.tostring(sCtx, "0.00") : "") : "")
            ST.push(label.new(x0, b0 + nb * bw + bw, hdr,''')
# the "if not mob" wraps need the following continuation lines indented: fix the two label lines that moved under it
kDraw = kDraw.replace('''                if not mob
                    ST.push(label.new(x0 - 2, h90,''', '''                if not mob
                    ST.push(label.new(x0 - 2, h90,''')

# ── Senkei: from Arrancar
sData = cut(A, '// ═══════════════════════════════════════════════════════════════ FOMC decision days (ET)', '// ═══════════════════════════════════════════════════════════════ The map, right of the last bar')
sData = sData.replace('═ FOMC decision days (ET)\n', '═ Senkei · FOMC decision days (ET)\n', 1)
sData = rep(sData, 'p0(float v) => str.tostring(v * 100, "0") + "%"\n', '')
sData = sData.replace('═ The ZQ grid\n', '═ Senkei · the ZQ grid\n').replace("═ CME FedWatch's steps\n", "═ Senkei · CME FedWatch's steps\n").replace('═ History: the next six meetings, bar by bar\n', '═ Senkei · history: the next six meetings, bar by bar\n')
sData = rep(sData, 'if showH and last_bar_index - bar_index < hBars', 'if showS and showHL and last_bar_index - bar_index < hBars')
sMap = cut(A, '// ═══════════════════════════════════════════════════════════════ The map, right of the last bar')
sMap = sMap.replace('═ The map, right of the last bar\n', '═ Senkei · the map, right of the last bar in this pane\n', 1)
sMap = rep(sMap, 'up.size() < nAhead', 'up.size() < nAh')
sMap = rep(sMap, '    if up.size() == 0\n', '    if not showS\n        mapLo := na\n        mapHi := na\n    else if up.size() == 0\n')
sMap = rep(sMap, '"Arrancar: no " + fdRoot', '"Senkei: no " + fdRoot')
sMap = rep(sMap, 'int   x0   = bar_index + mOff', 'int   x0   = bar_index + offS')
sMap = rep(sMap, 'int   xL   = math.max(0, bar_index - 300)', 'int   xL   = math.max(0, bar_index - (mob ? 60 : 300))')
sMap = sMap.replace('mGap', 'gxS')
sMap = rep(sMap, 'text = "target now " + fdRng(lo0, 0)', 'text = (mob ? "" : "target now ") + fdRng(lo0, 0)')
sMap = rep(sMap, 'box.new(xc - 4, yl + 0.25, xc + 4, yl,', 'box.new(xc - hwS, yl + 0.25, xc + hwS, yl,')
sMap = rep(sMap, 'text = showPct and p >= 0.04 ?', 'text = showPct and p >= (mob ? 0.10 : 0.04) ?')
sMap = rep(sMap, 'MT.push(label.new(xc + 5, sep, "",', 'MT.push(label.new(xc + hwS + 1, sep, "",')
sMap = rep(sMap, 'MT.push(label.new(xc, yMin - 0.02, fdDate(ky) + "\\n" + fdSg(100 * (e - base), "0") + "bp" + (dot_ ? "\\nFed " + str.tostring(sep, "0.000") + "\\nmkt " + fdSg(100 * (e - sep), "0") + "bp" : ""),',
                 'MT.push(label.new(xc, yMin - 0.02, (mob ? str.upper(str.format_time(keyTime(ky), "MMM", TZ)) + "\\n" + fdSg(100 * (e - base), "0") + (dot_ ? "\\n◆" + fdSg(100 * (e - sep), "0") : "") : fdDate(ky) + "\\n" + fdSg(100 * (e - base), "0") + "bp" + (dot_ ? "\\nFed " + str.tostring(sep, "0.000") + "\\nmkt " + fdSg(100 * (e - sep), "0") + "bp" : "")),')
sMap = rep(sMap, '        MT.push(label.new(xL, yMax + 0.02, "ARRANCAR · lines:', '        if not mob\n            MT.push(label.new(xL, yMax + 0.02, "SENKEI · lines:')
sMap = rep(sMap, 'mapLo := yMin - 0.35', 'mapLo := yMin - (mob ? 0.3 : 0.35)')

kDraw = rep(kDraw, 'textcolor = cMu, size = size.tiny, tooltip = "Probability held by the most likely bin', 'textcolor = cSub, size = size.tiny, tooltip = "Probability held by the most likely bin')
kDraw = rep(kDraw, 'style = li == 2 ? line.style_dotted : li == 3 ? line.style_solid : line.style_dashed, width = 1,', 'style = li == 2 ? line.style_dotted : li == 3 ? line.style_solid : line.style_dashed, width = wLv,')
S = HEAD + '\n' + kData + kHelp + sData + sMap + '\n' + kDraw
S = S.replace('\n\n\n', '\n\n')
open('/home/claude/hm/sbz/Senbonzakura.pine', 'w', encoding='utf-8').write(S)
print(len(S.split('\n')), 'lines')
