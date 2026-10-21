"""Vizard only: queue every card cell write and flush once at the end of the script.
Pine expands each user-function call into the compiled code (100,256-token cap, CE10117), and the card helpers were
called ~70 times; queued, the cell-writing code compiles once. Writes keep their original order."""
import re

NEW_HELPERS = '''// card cells are queued (one CRow per row / cell, in call order) and written by cardFlush() at the end of the script:
// Pine expands every helper call into the compiled code, so writing the cells in one place keeps Vizard under the token cap
type CRow
    table  t
    int    k
    int    r
    int    c   = 0
    color  col
    string s1  = ""
    string s2  = ""
    string s3  = ""
    string s4  = ""
    string tip = ""
    bool   b   = false
    color  f1
    color  f2
    string ha  = "left"
var CQ = array.new<CRow>()
cardHead(table t, int r, color col, string title, string tip, string pill, color pfg, color pbg) =>
    CQ.push(CRow.new(t, 1, r, 0, col, title, "", "", pill, tip, false, pfg, pbg))
cardSub(table t, int r, color col, string txt, string a1, string a2) =>
    CQ.push(CRow.new(t, 2, r, 0, col, "", txt, a1, a2))
// key is a ✓ pill when held, else a muted label; value in bold
cardRow(table t, int r, color col, string key, bool held, string lab, string v, string b, string tip, color vfg = na, color bfg = na) =>
    CQ.push(CRow.new(t, 0, r, 0, col, key, lab, v, b, tip, held, vfg, bfg))
cardWide(table t, int r, color col, string key, string txt, string tip, color fg) =>
    CQ.push(CRow.new(t, 3, r, 0, col, key, txt, "", "", tip, false, fg))
tcQ(table t, int c, int r, string s, color fg, color bg, string tip = "", string ha = text.align_left, bool b = false) =>
    CQ.push(CRow.new(t, 4, r, c, na, s, "", "", "", tip, b, fg, bg, ha))
stripeQ(table t, int r, color col) =>
    CQ.push(CRow.new(t, 5, r, 0, col))
'''

FLUSH = '''
// ═══ Write the queued card cells, in the order they were queued
cardFlush() =>
    if CQ.size() > 0
        for q in CQ
            table t = q.t
            int   r = q.r
            switch q.k
                0 =>
                    stripe(t, r, q.col)
                    tc(t, 1, r, q.s1, q.b ? #ffffff : cMu, q.b ? cOk : cBody, q.tip, text.align_center, q.b)
                    tc(t, 2, r, q.s2, cTx, cBody, q.tip)
                    tc(t, 3, r, q.s3, na(q.f1) ? cTx : q.f1, cBody, q.tip, text.align_center, true)
                    tc(t, 4, r, q.s4, na(q.f2) ? cMu : q.f2, cBody, q.tip, text.align_center)
                1 =>
                    stripe(t, r, q.col)
                    tc(t, 1, r, q.s1, #ffffff, q.col, q.tip, text.align_left, true)
                    tc(t, 4, r, q.s4, q.f1, q.f2, "", text.align_center, true)
                2 =>
                    stripe(t, r, q.col)
                    tc(t, 1, r, "", cMu, cBody2)
                    tc(t, 2, r, q.s2, cMu, cBody2)
                    tc(t, 3, r, q.s3, cMu, cBody2, "", text.align_center)
                    tc(t, 4, r, q.s4, cMu, cBody2, "", text.align_center)
                3 =>
                    stripe(t, r, q.col)
                    tc(t, 1, r, q.s1, cMu, cBody, "", text.align_center)
                    tc(t, 2, r, q.s2, q.f1, cBody, q.tip)
                4 =>
                    tc(t, q.c, r, q.s1, q.f1, q.f2, q.tip, q.ha, q.b)
                =>
                    stripe(t, r, q.col)
        CQ.clear()
    true
cardFlush()
'''

def queue_cards(s):
    a = s.index('cardHead(table t, int r, color col, string title')
    b = s.index('// text gauges for the monospace cells')
    old = s[a:b]
    for name in ('cardHead(', 'cardSub(', 'cardRow(', 'cardWide('):
        assert old.count('\n' + name) + old.startswith(name) == 1, name
    s = s[:a] + NEW_HELPERS + s[b:]
    # zone rows: stripe / tc → queued versions (helper bodies, 4-space indent)
    for fn in ('zoneRow(', 'zoneRowM('):
        i = s.index('\n' + fn) + 1
        j = s.index('\n', s.index('\n    tc(t, 4, r', i) + 1)
        body = s[i:j].replace('    stripe(t, r, col)', '    stripeQ(t, r, col)').replace('\n    tc(', '\n    tcQ(')
        s = s[:i] + body + s[j:]
    # direct overrides inside the drawing blocks (indent >= 8)
    s, n = re.subn(r'(?m)^( {8,})tc\(', r'\1tcQ(', s)
    assert n in (3, 5), n   # 3 once the VIX / DXY mobile rows are gone
    assert not re.search(r'(?m)^ {8,}stripe\(', s.split('cardFlush() =>')[0])
    return s.rstrip('\n') + '\n' + FLUSH

def rep(s, old, new, n=1):
    assert s.count(old) == n, (old[:90], s.count(old)); return s.replace(old, new)

def shrink(s):
    """More call-site cuts for the compiled-token cap: each removed call site removes one expanded copy of the function."""
    import re
    # A. the seventeen ZQ months: one dynamic request in a loop instead of seventeen call sites
    a = s.index('float z0 = request.security(fdTk(0)')
    b = s.index('\n', s.index('array<float> fdZ = array.from(z0')) + 1
    s = s[:a] + ('// the seventeen ZQ months, one dynamic request each (Pine v6 runs request.security() inside loops)\n'
                 '// each month\'s price on the previous bar (rolled back with the bar like any var)\n'
                 'var array<float> fdZp = array.new<float>(FDN, na)\n'
                 'array<float> fdZ = array.new<float>(FDN, na)\n'
                 'for i = 0 to FDN - 1\n'
                 '    fdZ.set(i, request.security(fdTk(i), fdTf, close, ignore_invalid_symbol = true))\n') + s[b:]
    zl = 'array.from(z0[1], z1[1], z2[1], z3[1], z4[1], z5[1], z6[1], z7[1], z8[1], z9[1], z10[1], z11[1], z12[1], z13[1], z14[1], z15[1], z16[1])'
    s = rep(s, 'if tdSt and not na(z2[1])\n    for v in ' + zl + '\n', 'if tdSt and not na(fdZp.get(2))\n    for v in fdZp\n')
    s = rep(s, '    fd14  := ' + zl + '\n    fd14K := calK\n', '    fd14  := fdZp.copy()\n    fd14K := calK\nfdZp := fdZ.copy()\n')
    assert not re.search(r'\bz(1[0-6]|[0-9])\[1\]', s)
    # B. week and month zone rows: one call site each for the Full and Mobile cards
    m = re.search(r'(?m)^( +)zoneRow\(TS, r0 \+ 5, cGh, "WEEK", wH, wL, "week"\)\n\1zoneRow\(TS, r0 \+ 6, cGh, "MONTH", moH, moL, "month"\)\n', s)
    ind = m.group(1)
    s = s[:m.start()] + (f'{ind}for zi = 0 to 1\n{ind}    zoneRow(TS, r0 + 5 + zi, cGh, zi == 0 ? "WEEK" : "MONTH", zi == 0 ? wH : moH, zi == 0 ? wL : moL, zi == 0 ? "week" : "month")\n') + s[m.end():]
    m = re.search(r'(?m)^( +)zoneRowM\(TM, r0 \+ 4, cGh, "WK", wH, wL, "week"\)\n\1zoneRowM\(TM, r0 \+ 5, cGh, "MO", moH, moL, "month"\)\n', s)
    ind = m.group(1)
    s = s[:m.start()] + (f'{ind}for zi = 0 to 1\n{ind}    zoneRowM(TM, r0 + 4 + zi, cGh, zi == 0 ? "WK" : "MO", zi == 0 ? wH : moH, zi == 0 ? wL : moL, zi == 0 ? "week" : "month")\n') + s[m.end():]
    # C. the shock cone's two layers: one call site each
    s = rep(s, '    coneBand(calK, s14O, ADRtd * s14O, 1, 3, 26, color.new(cGh, 91), color.new(cGh, 72))\n    coneBand(calK, s14O, ADRtd * s14O, 0, 2, 26, color.new(cGh, 85), #00000000)\n',
               '    for cb = 0 to 1\n        coneBand(calK, s14O, ADRtd * s14O, 1 - cb, 3 - cb, 26, color.new(cGh, cb == 0 ? 91 : 85), cb == 0 ? color.new(cGh, 72) : #00000000)\n')
    s = rep(s, '                VPC.push(coneBand(calK, s14O, ADRtd * s14O, 1, 3, kE, color.new(cGh, 91), color.new(cGh, 72)))\n                VPC.push(coneBand(calK, s14O, ADRtd * s14O, 0, 2, kE, color.new(cGh, 85), #00000000))\n',
               '                for cb = 0 to 1\n                    VPC.push(coneBand(calK, s14O, ADRtd * s14O, 1 - cb, 3 - cb, kE, color.new(cGh, cb == 0 ? 91 : 85), cb == 0 ? color.new(cGh, 72) : #00000000))\n')
    # D. yesterday's and last week's FedWatch: one fdCalc call site in a two-pass loop
    old = ('        [yK, yE, yMK, yMP, yk1, yk2, yw1, yw2, yLo, yBase] = fdCalc(fdZ1, today, fdAft)\n'
           '        [wK, wE, wMK, wMP, wk1, wk2, ww1, ww2, wLo, wBase] = fdCalc(fdZ5, today, fdAft)\n')
    new = ('        array<float> yE = array.new<float>()\n'
           '        array<float> wE = array.new<float>()\n'
           '        int   yk1 = na\n'
           '        int   yk2 = na\n'
           '        float yw1 = na\n'
           '        float yw2 = na\n'
           '        for pv = 0 to 1\n'
           '            [hK, hE, hMK, hMP, hk1, hk2, hw1, hw2, hLo, hBase] = fdCalc(pv == 0 ? fdZ1 : fdZ5, today, fdAft)\n'
           '            if pv == 0\n'
           '                yE  := hE\n'
           '                yk1 := hk1\n'
           '                yk2 := hk2\n'
           '                yw1 := hw1\n'
           '                yw2 := hw2\n'
           '            else\n'
           '                wE  := hE\n')
    s = rep(s, old, new)
    return s

P92 = ''.join(chr(c) for c in range(33, 127) if chr(c) not in '"\\')
assert len(P92) == 92

def pack(s):
    """Clock and cone data, generated (never hand-edited): two characters per value instead of 3–5 digits and a comma.
    Value v (×1000 of ADR20, −2000 … 6463) is stored as v + 2000 in base 92 over printable ASCII without " and \\."""
    def enc(v):
        u = v + 2000; assert 0 <= u < 92 * 92; return P92[u // 92] + P92[u % 92]
    for name in ('CK_NQ', 'CK_ES', 'CONE_NQ', 'CONE_ES'):
        m = re.search(r'(?m)^' + name + r'\s*=\s*"[^"]*"(?:\n\s+\+\s*"[^"]*")*', s)
        body = ''.join(re.findall(r'"([^"]*)"', m.group(0)))
        vals = [int(v) for v in re.split(r'[,;]', body) if v != '']
        e = ''.join(enc(v) for v in vals)
        parts = [e[i:i + 180] for i in range(0, len(e), 180)]
        new = f'{name} = "' + parts[0] + '"' + ''.join('\n     + "' + p + '"' for p in parts[1:])
        s = s[:m.start()] + new + s[m.end():]
    s = rep(s, 'var array<float> CK = parseMilli(isES ? CK_ES : CK_NQ)', 'var array<float> CK = unpackMilli(isES ? CK_ES : CK_NQ)')
    s = rep(s, 'var array<float> CN = parseMilli(isES ? CONE_ES : CONE_NQ)', 'var array<float> CN = unpackMilli(isES ? CONE_ES : CONE_NQ)')
    a = s.index('\nparseMilli(string s) =>') + 1
    s = s[:a] + ('// clock and cone data are packed two characters per value: (index in P92) × 92 + (index in P92) − 2000, then ÷ 1000\n'
                 'P92 = "' + P92 + '"\n'
                 'unpackMilli(string s) =>\n'
                 '    array<float> out = array.new<float>()\n'
                 '    for i = 0 to int(str.length(s) / 2) - 1\n'
                 '        out.push((str.pos(P92, str.substring(s, 2 * i, 2 * i + 1)) * 92 + str.pos(P92, str.substring(s, 2 * i + 1, 2 * i + 2)) - 2000) / 1000.0)\n'
                 '    out\n') + s[a:]
    return s
