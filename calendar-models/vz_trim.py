"""Vizard only: no PO3 candles (Gran Rey Cero is the megazord's candle vehicle). Removes the daily model candle, the
weekly candle, their chips, price tags, day lines and inputs, the day-shape statistics that only fed the model candle,
the VIX sizing of the model, and the ADR request that only sized it."""
import re

def cut_lines(s, starts):
    L = s.split('\n'); out = []; hit = set()
    for l in L:
        k = next((p for p in starts if l.startswith(p)), None)
        if k: hit.add(k); continue
        out.append(l)
    miss = set(starts) - hit
    assert not miss, miss
    return '\n'.join(out)

def rep(s, old, new, n=1):
    assert s.count(old) == n, (old[:90], s.count(old)); return s.replace(old, new)

def nopo3(s):
    # header
    a = s.index('// Price chart: two PO3-style candles'); b = s.index('// Indicator pane: the event clock.')
    s = s[:a] + s[b:]
    s = rep(s, '// Candle idea after PO3-style HTF candle indicators; clock after Kyōka Suigetsu.', '// Clock after Kyōka Suigetsu.')
    # inputs
    s = cut_lines(s, ['showGh   = input.bool(', 'offDayI  = input.string(', 'showPL   = input.bool(', 'grpC = "PO3 candles"',
                      'showWk = input.bool(', 'showCh = input.bool(', 'chSzI  = input.string(', 'offI   = input.int(',
                      'widI   = input.int(', 'gapI   = input.int(', 'cUp    = input.color(', 'cDn    = input.color(',
                      'cWk    = input.color(', 'showPx = input.bool(', 'pxSzI  = input.string(', 'showLv = input.bool(',
                      'vixSize = input.bool(', 'pxSz  = pxSzI', 'chSz  = chSzI', 'sv(int ty, int f) =>',
                      'var array<float> ST = parseStats(', 'IVRV_NQ = ', 'IVRV_ES = '])
    return s

def nopo3_full(s):
    m = re.search(r'(?m)^cGh    = input\.color\((#[0-9a-fA-F]{6,8}), "Model", group = grpC, inline = "c2", display = display\.none\)\n', s)
    ghost = m.group(1)
    s = s[:m.start()] + s[m.end():]
    s = nopo3(s)
    # the model colour moves to the model-structure group; the extended lines end a fixed 12 bars right of price
    m = re.search(r'(?m)^cLvl    = input\.color\(.*$', s)
    s = s[:m.end()] + f'\ncGh     = input.color({ghost}, "Model", group = grpS, inline = "s1", display = display.none)\noffI    = 12' + s[m.end():]
    s = rep(s, 'tooltip = "Which day the daily candle and its model use.\\nTrading day: the CME daily candle, 18:00 → 17:00 ET.',
               'tooltip = "Which day counts as the event day for the cards.\\nTrading day: the CME day, 18:00 → 17:00 ET.')
    # day-shape statistics (model candle only)
    a = s.index('// Day shapes, ADR20 units'); b = s.index('// Event clock, trading day 18:00')
    s = s[:a] + s[b:]
    # ADR on the chosen day only sized the model candle; ADRtd (trading day) stays
    s = rep(s, '[ADR, ADRtd] = request.security(syminfo.tickerid, "15", [adrCalc(AN), adrCalc(0)])',
               'ADRtd = request.security(syminfo.tickerid, "15", adrCalc(0))')
    # helpers that only drew the candles
    for fn in ('pxR(int x, float y', 'pxL(int x, float y', 'drawCandle(int x, int w', 'chip(int x, float y'):
        a = s.index('\n' + fn) + 1
        b = a + 1
        L = s[a:].split('\n')
        n = 1
        while n < len(L) and L[n].startswith('    '): n += 1
        s = s[:a] + '\n'.join(L[n:])
    # the candle block of the main last-bar block
    a = s.index('    color  gc   = pNow ? cGh : color.new(cGh, 55)\n')
    b = s.index('    // ── cards\n')
    gone = s[a:b]
    s = s[:a] + s[b:]
    # nothing left may read what the candle block declared
    names = set(re.findall(r'(?m)^    (?:\w+\s+)?(\w+)\s+=(?!=)', gone)) | {'gc'}
    names -= {'today'}
    i0 = s.index('if barstate.islast\n    clearRight()')
    m = re.search(r'(?m)^\S', s[i0 + 20:])
    rest = s[i0:i0 + 20 + m.start()]
    code = re.sub(r'"(?:[^"\\\\]|\\\\.)*"', '""', rest)
    left = sorted(n for n in names if re.search(r'\b' + n + r'\b', code))
    assert not left, left
    for w in ('showGh', 'offDayI', 'showPL', 'showWk', 'showCh', 'widI', 'gapI', 'cUp', 'cDn', 'cWk', 'showPx', 'showLv', 'vixSize', 'pxSz', 'chSz', 'drawCandle', 'pxR(', 'pxL(', 'chip(', 'sv(', 'IVRV_'):
        assert not re.search(r'\b' + re.escape(w) + (r'' if w.endswith('(') or w.endswith('_') else r'\b'), s), w
    return s

def cut_block(s, header, indent_of_header=None):
    """remove a line starting with `header` (exact, including its indent) and every following line indented deeper"""
    i = s.index(header)
    assert i == 0 or s[i - 1] == '\n', header[:60]
    ind = len(header) - len(header.lstrip())
    L = s[i:].split('\n')
    n = 1
    while n < len(L) and (not L[n].strip() or len(L[n]) - len(L[n].lstrip()) > ind): n += 1
    while n > 1 and not L[n - 1].strip(): n -= 1
    return s[:i] + '\n'.join(L[n:])

def novxdx(s):
    """Vizard only: no generic VIX and DXY cards (identical in every megazord module). The DXY feed stays for the FOMC
    NQ-vs-DXY contrarian rows of the stages card."""
    s = rep(s, '// days with this week\'s and month\'s premium / discount octant), a VIX card and a DXY card with the macro reads that held.',
               '// days with this week\'s and month\'s premium / discount octant).')
    s = cut_lines(s, ['showVx  = input.bool(', 'showDx  = input.bool(', 'vixSym  = input.symbol(', 'ylSym   = input.symbol(',
                      '// · dx4 uses the [1] offset', '// · the daily VIX, DXY ATR and 10Y values', '//   (time_close ≤ the chart bar',
                      'float dx4 = request.security(', 'done(float v0, float v1, int tc)', '[vTC, vC0, vC1, vS0, vS1] = request.security(',
                      'float vixL = request.security(', '[dTC, dA0, dA1] = request.security(', '[yTC, yC0, yC1] = request.security(',
                      'float ylL = request.security(', 'float vPrev = done(', 'float vAvg  = done(', 'float dxAtr = done(', 'float ylPrev = done(',
                      'float dxDay = na(dxTdO)', 'var float dxHi = na', 'var float dxLo = na', 'cVx    = #', 'VX_N = 4', 'DX_N = 7',
                      'var int   rVx = -1', 'var int   rDx = -1', 'var int   mVx = -1', 'var int   mDx = -1'])
    s = rep(s, 'if tdSt or na(dxHi)\n    dxHi := dxL\n    dxLo := dxL\nelse if not na(dxL)\n    dxHi := math.max(dxHi, dxL)\n    dxLo := math.min(dxLo, dxL)\n', '')
    s = rep(s, 'grpM = "VIX · DXY · 10Y"', 'grpM = "DXY"')
    s = rep(s, 'dxySym  = input.symbol("TVC:DXY", "DXY", group = grpM, inline = "m1", display = display.none)',
               'dxySym  = input.symbol("TVC:DXY", "DXY", group = grpM, tooltip = "Read for the stages card\'s NQ-vs-DXY rows (other-way rate in each stage and over the day).", display = display.none)')
    s = rep(s, '(the weekly PO3 candle and the WEEK / MONTH', '(the WEEK / MONTH')
    # tooltips that listed the VIX and DXY cards
    s = rep(s, '"Full: the event, VIX and DXY cards on the price chart and the clock card, every row.\\nMobile: one narrow card for a phone screen. A header with the next or current event, a NOW row that reads the clock, the held rows (or the tally) in short form, and one line each for VIX and DXY. The clock card folds into the NOW row; the DXY range battery, the 4-week row and 10Y are left out."',
               '"Full: the event, Fed and stages cards on the price chart and the clock card, every row.\\nMobile: narrow cards for a phone screen. A header with the next or current event, a NOW row that reads the clock, the held rows (or the tally) in short form, and one line for the Fed. The clock card folds into the NOW row."')
    s = rep(s, '"The event, VIX and DXY cards stack in one corner of the price chart."', '"The cards stack in one corner of the price chart."')
    # card layout
    s = rep(s, '// rows or the tally in short form, then one row each for VIX and DXY after a thin gap.', '// rows or the tally in short form, then the Fed row after a thin gap.')
    s = rep(s, '        if (showVx or showDx or showFd) and r > o\n', '        if showFd and r > o\n')
    s = rep(s, '        if showVx\n            mVx := r\n            r += 1\n        if showDx\n            mDx := r\n            r += 1\n', '')
    s = rep(s, '(mVx > g or mDx > g or mFd > g)', 'mFd > g')
    s = rep(s, '        if showVx\n            r += r > o ? 1 : 0\n            rVx := r\n            r += VX_N\n        if showDx\n            r += r > o ? 1 : 0\n            rDx := r\n            r += DX_N\n', '')
    s = rep(s, 'array.from(rEv, rVx, rDx, rFd)', 'array.from(rEv, rFd)')
    # readings and cards
    a = s.index('    // VIX and DXY readings (both layouts)\n'); b = s.index('    bool   big = dOk and math.abs(net) >= bigL\n')
    b = s.index('\n', b) + 1
    s = s[:a] + s[b:]
    s = cut_block(s, '    // ── VIX card: only what held')
    s = cut_block(s, '    if showVx and not na(TS) and rVx >= 0')
    s = cut_block(s, '    // ── DXY card (last three years')
    s = cut_block(s, '    if showDx and not na(TS) and rDx >= 0')
    s = cut_block(s, '        if showVx and mVx >= 0')
    s = cut_block(s, '        if showDx and mDx >= 0')
    code = re.sub(r'"(?:[^"\\]|\\.)*"', '""', '\n'.join(l.split('//')[0] if '"' not in l else l for l in s.split('\n')))
    for w in ('showVx', 'showDx', 'vixSym', 'ylSym', 'vixL', 'vPrev', 'vAvg', 'dxAtr', 'ylPrev', 'ylL', 'dx4', 'dxHi', 'dxLo', 'dxDay', 'rVx', 'rDx', 'mVx', 'mDx', 'cVx', 'VX_N', 'DX_N', 'vOk', 'vsp', 'vch', 'bR', 'bA', 'vDn', 'dOk', 'bigL', 'done'):
        assert not re.search(r'\b' + w + r'\b', code), w
    return s

def comments(s):
    """comments that still described the candles or the VIX / DXY cards (comments never reach the compiled script)"""
    s = rep(s, '// bar and grow with it, so they never run through the candles on the right.', '// bar and grow with it.')
    s = rep(s, '═ PO3 candles (price chart, drawn on the last bar)', '═ Drawings right of price (rebuilt on the last bar)')
    s = rep(s, '// Price chart: one stacked table in a corner holding the event card, the VIX card and the DXY card. Each card is an',
               '// Price chart: one stacked table in a corner holding the event card and the Fed card. Each card is an')
    s = rep(s, '// the tally, then VIX and DXY in one row each. Every row keeps its full explanation in the tooltip.',
               '// the tally, then the Fed row. Every row keeps its full explanation in the tooltip.')
    return s
