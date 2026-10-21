"""SB Map v3 (from SB_v2.pine): session 25 / 50% levels measured on the range from the last extreme (static while price
trades inside the range), an optional 37.5% level, and the London 25% card row on the same definition."""
S = open('/home/claude/sb/SB_v2.pine').read()

def rep(old, new, n=1):
    global S
    c = S.count(old)
    assert c == n, (c, old[:120])
    S = S.replace(old, new)

# ── inputs
rep('''show50tick  = input.bool(true, "50% tick (Asia, London, NY candles)", inline = "50t", group = g_SC, display = display.none)
mode50      = input.string("Body (open–close)", "50% of", options = ["Body (open–close)", "Range (high–low)"], inline = "50t", group = g_SC, display = display.none)
show50line  = input.bool(true, "Asia / London 50% lines on chart", inline = "50", group = g_SC, display = display.none)
col50       = input.color(#ab47bc, "", inline = "50", group = g_SC, display = display.none)
''', '''show375     = input.bool(true, "37.5% (lines and ticks)", inline = "375", group = g_SC, display = display.none)
col375      = input.color(#5c6bc0, "", inline = "375", group = g_SC, display = display.none)
show50tick  = input.bool(true, "50% tick (Asia, London, NY candles)", inline = "50t", group = g_SC, display = display.none)
show50line  = input.bool(true, "Asia / London 50% lines on chart", inline = "50", group = g_SC, display = display.none)
col50       = input.color(#ab47bc, "", inline = "50", group = g_SC, display = display.none)
lvlMode     = input.string("Range · from the last extreme", "25 / 37.5 / 50% of", options = ["Range · from the last extreme", "Body (open–close)"], group = g_SC, tooltip = "Range: retracement levels of the session's high–low, measured from whichever extreme came last. A session that made its high first and its low later is measured up from the low (25% = low + a quarter of the range). They move only when the session makes a new high or low, so they hold still while price trades inside the range.\\nBody: a share of the open–close body back from the close. It moves with every tick while the session is open.", display = display.none)
''')
# ── session: the time of the high and of the low
rep('''    int   t0
    int   day
''', '''    int   t0
    int   day
    int   tH       // time of the session high
    int   tL       // time of the session low
''')
rep('''        s.t0  := time
        s.day := dayCount
    else if inS and not na(s.o)
        s.h := math.max(s.h, high)
        s.l := math.min(s.l, low)
        s.c := close
''', '''        s.t0  := time
        s.day := dayCount
        s.tH  := time
        s.tL  := time
    else if inS and not na(s.o)
        if high > s.h
            s.h  := high
            s.tH := time
        if low < s.l
            s.l  := low
            s.tL := time
        s.c := close
''')
# ── levels
rep('''lvl25(float o, float c) =>
    bt = math.max(o, c)
    bb = math.min(o, c)
    br = bt - bb
    br > 0 ? (c >= o ? bt - 0.25 * br : bb + 0.25 * br) : (bt + bb) / 2

lvl50(float o, float h, float l, float c) => mode50 == "Range (high–low)" ? (h + l) / 2 : (o + c) / 2
''', '''isBody = lvlMode == "Body (open–close)"
// the session's leg: down when its high came first and its low later (body mode: closed below the open)
legDown(Sess s) => isBody ? s.c < s.o : (s.tH < s.tL or (s.tH == s.tL and s.c < s.o))
// k of the range back from the last extreme (k = 0.25, 0.375, 0.5); body mode: k of the body back from the close
lvlK(Sess s, float k) =>
    float out = na
    if isBody
        bt = math.max(s.o, s.c)
        bb = math.min(s.o, s.c)
        br = bt - bb
        out := br > 0 ? (s.c >= s.o ? bt - k * br : bb + k * br) : (bt + bb) / 2
    else
        out := legDown(s) ? s.l + k * (s.h - s.l) : s.h - k * (s.h - s.l)
    out
''')
# ── London 25% traded (touch, from 05:00)
rep('''    if na(q25T) and sL.c != sL.o and (sL.c > sL.o ? low <= lvl25(sL.o, sL.c) : high >= lvl25(sL.o, sL.c))
        q25T := time
''', '''    if na(q25T) and sL.h > sL.l and high >= lvlK(sL, 0.25) and low <= lvlK(sL, 0.25)
        q25T := time
''')
# ── candle ticks
rep('''    if lvls and show25tick and bt > bb
        q = lvl25(s.o, s.c)
        cLn.push(line.new(x2, q, x2 + cSpacing, q, xloc = xloc.bar_index, color = col25))
        cLb.push(label.new(x2 + cSpacing, q, "25%", xloc = xloc.bar_index, style = label.style_label_left, color = #ffffff00, textcolor = col25, size = size.tiny))
    if lvls and show50tick
        h50 = lvl50(s.o, s.h, s.l, s.c)
''', '''    if lvls and show25tick and s.h > s.l
        q = lvlK(s, 0.25)
        cLn.push(line.new(x2, q, x2 + cSpacing, q, xloc = xloc.bar_index, color = col25))
        cLb.push(label.new(x2 + cSpacing, q, "25%", xloc = xloc.bar_index, style = label.style_label_left, color = #ffffff00, textcolor = col25, size = size.tiny))
    if lvls and show375 and s.h > s.l
        q3 = lvlK(s, 0.375)
        cLn.push(line.new(x2, q3, x2 + cSpacing, q3, xloc = xloc.bar_index, color = col375))
        cLb.push(label.new(x2 + cSpacing, q3, "37.5%", xloc = xloc.bar_index, style = label.style_label_left, color = #ffffff00, textcolor = col375, size = size.tiny))
    if lvls and show50tick
        h50 = lvlK(s, 0.5)
''')
# ── session lines
rep('''    if show25line and math.max(s.o, s.c) > math.min(s.o, s.c)
        q = lvl25(s.o, s.c)
''', '''    if show25line and s.h > s.l
        q = lvlK(s, 0.25)
''')
rep('''    if show50line
        h50 = lvl50(s.o, s.h, s.l, s.c)
''', '''    if show375 and s.h > s.l
        q3 = lvlK(s, 0.375)
        cLn.push(line.new(s.t0, q3, time, q3, xloc = xloc.bar_time, color = col375, style = line.style_dashed))
        cLb.push(label.new(time, q3, stampOf(s.t0) + " " + nm + " 37.5%", xloc = xloc.bar_time, style = label.style_label_left, color = #ffffff00, textcolor = col375, size = tSize))
        sLb.push(cLb.last())
        sLy.push(q3)
    if show50line
        h50 = lvlK(s, 0.5)
''')
# ── card: the London 25% on the same definition
rep('''        if sL.c != sL.o
            float q = lvl25(sL.o, sL.c)
            addRow(K, V, W, P, C, "LDN 25%", (sL.c > sL.o ? "bull · " : "bear · ") + pxS(q), na(q25T) ? "untouched" : "traded ✓ " + hhmm(q25T), "The London 25%: a quarter of London's body back from its close. NY trades through it on 90–95% of days (NQ 2018–26), and closing back on London's side after a wick is a coin flip: a reference level, not a hold.", nc)
''', '''        if sL.h > sL.l
            float q = lvlK(sL, 0.25)
            string q25Tip = isBody ? "The London 25%: a quarter of London's body back from its close. NQ + ES + RTY 2018–26: reached after 05:00 by 16:59 on 96% of days. A reference level, not a hold." : "The London 25%: a quarter of London's high–low range back from its last extreme (" + (legDown(sL) ? "a down leg, so measured up from the low" : "an up leg, so measured down from the high") + "). NQ + ES + RTY 2018–26, after 05:00: the 25% was reached by 11:00 on 91% of days and by 16:59 on 94%; the 37.5% on 90% / 93%; the 50% on 86% / 90%. Steady in both periods and on every symbol. A reference level, not a hold."
            addRow(K, V, W, P, C, "LDN 25%", (legDown(sL) ? "down leg · " : "up leg · ") + pxS(q), na(q25T) ? "untouched" : "traded ✓ " + hhmm(q25T), q25Tip, nc)
''')
for w in ('lvl25', 'lvl50', 'mode50'):
    assert w not in S, w
open('/home/claude/sb/Shikai_Bankai_Session_Map.pine', 'w').write(S)
print('ok', len(S.splitlines()))
