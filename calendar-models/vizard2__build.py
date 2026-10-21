"""Vizard rebuild: line-range splices on the last compiling Vizard.pine, each range checked by its first and last line."""
import re, sys
SRC = '/home/claude/hm/Vizard.pine'
L = open(SRC, encoding='utf-8').read().split('\n')
F = lambda n: open(f'/home/claude/hm/vizard2/frag/{n}', encoding='utf-8').read().rstrip('\n').split('\n')
def line(n): return L[n - 1]
# ranges (1-based, inclusive) → new lines; each checked by a prefix of its first and last line
edits = []
def rng(a, b, first, last, new):
    assert line(a).startswith(first), (a, line(a)[:80])
    assert line(b).startswith(last), (b, line(b)[:80])
    edits.append((a, b, new))
cone = [l for l in L[741:746]]                                    # CONE comment + CONE_NQ (2 lines) + CONE_ES (2 lines)
assert cone[0].startswith('// Shock cone') and cone[1].startswith('CONE_NQ') and cone[3].startswith('CONE_ES'), cone[0][:40]
vzt = [line(752), line(753), line(754)]
assert vzt[0].startswith('var string VZT_GF') and vzt[1].startswith('var string VZT_Q') and vzt[2].startswith('var string VZT_CE')
stages = []
for l in F('05_stages.pine'):
    if l == '@@CONE@@': stages += cone
    elif l == '@@VZT@@': stages += vzt
    else: stages.append(l)
rng(5, 17, '// Vizard · Models 9–10', '// Concepts: ICT', F('01_header.pine'))
rng(42, 66, 'grpK = "Event clock', 'fdRoot  = input.string', F('02_inputs.pine'))
rng(72, 76, 'grpV    = "FOMC stages card"', 'sgN     = input.int', F('03_grpV.pine'))
rng(300, 305, 'chkRows(int k', 'chkMax(bool es)', [])
rng(395, 401, '// Higher-timeframe requests', '[moH, moL] = request.security', F('04_requests.pine'))
rng(479, 479, '    rthC := close', '    rthC := close', ['    rthC := close', '// the month so far, today included (the month-to-date high and low)', 'float mHi = math.max(nz(mtH, tdH), tdH)', 'float mLo = math.min(nz(mtL, tdL), tdL)'])
rng(669, 669, 'cFd = #5c6bc0', 'cFd = #5c6bc0', ['fdMv(int k, float lo) => (k == 0 ? "hold " : k < 0 ? "cut " : "hike ") + fdRng(lo, k)', 'cFd = cAcF'])
rng(671, 705, '// ═', '', [])
rng(706, 919, '// ═', '', stages)
rng(1005, 1005, 'bool clkGo', 'bool clkGo', ['bool clkGo = clkOn and clkTF'])
rng(1033, 1033, 'bool  ckTop', 'bool  ckTop', ['bool  ckTop = (showCk and ckOn == "Indicator pane" and str.startswith(ckPos, "Top")) or (showMap and str.startswith(mapPos, "Top"))'])
rng(1103, 1183, '// ═', '            TK.merge_cells(1, tkO, 3, tkO)', F('06_cards.pine'))
rng(1247, 1271, 'zoneOf(float h', '    tcQ(t, 4, r, na(h)', F('07_zone.pine'))
rng(1325, 1325, '        if showEv and evMode == "Tally"', '        if showEv', ['        if showEv'])
rng(1349, 1349, '        string tTip', '        string tTip', [line(1349).replace('" " + TAL_NAME + " days, oldest → newest: "', '" " + TAL_NAME + " days" + since + ", oldest → newest: "')])
rng(1351, 1403, '        if showEv and not na(TS) and rEv >= 0', '', F('08_event.pine'))
rng(1539, 1569, '        if showFd and not na(TS) and rFd >= 0', '    true', F('09_fed.pine'))
rng(1572, 1789, 'drawLast3() =>', 'drawLast4()', F('10_map_stages.pine'))
assert 'since + ", oldest' in edits[-5][2][0] if False else True
edits.sort()
for (a1, b1, _), (a2, b2, _) in zip(edits, edits[1:]):
    assert b1 < a2, ('overlap', a1, b1, a2)
out = []; k = 1
for a, b, new in edits:
    out += L[k - 1:a - 1]; out += new; k = b + 1
out += L[k - 1:]
s = '\n'.join(out)
assert 'since + ", oldest' in s
open('/home/claude/hm/vizard2/Vizard.pine', 'w', encoding='utf-8').write(s)
print('lines', len(out))
