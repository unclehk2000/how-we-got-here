"""Put a View group at the top of every indicator's settings (Desgarrón / Kyōka style), hide inputs from the status line,
and make the first-generation scripts follow the chart theme."""
import re, sys
BANNER = '// ═══════════════════════════════════════════════════════════════ Inputs\n'
POS8 = '["Top left", "Top center", "Top right", "Middle left", "Middle right", "Bottom left", "Bottom center", "Bottom right"]'
class F:
    def __init__(s, name):
        s.name = name; s.S = open(f'{name}.pine', encoding='utf-8').read()
    def save(s): open(f'{s.name}.pine', 'w', encoding='utf-8').write(s.S)
    def rep(s, o, n, c=1):
        k = s.S.count(o); assert k == c, (s.name, k, o[:120]); s.S = s.S.replace(o, n)
    def take(s, prefix):
        L = s.S.split('\n'); i = [k for k, l in enumerate(L) if l.startswith(prefix)]
        assert len(i) == 1, (s.name, prefix, i); line = L.pop(i[0]); s.S = '\n'.join(L); return line
    def after(s, anchor, text):
        assert s.S.count(anchor) == 1, (s.name, anchor); s.S = s.S.replace(anchor, anchor + text)
def tip(line):
    m = re.search(r'tooltip = "((?:[^"\\]|\\.)*)"', line); return m.group(1) if m else ''
def view_block(g, rows):
    return f'{g} = "View"\n' + ''.join(r + '\n' for r in rows) + '\n'
def inp(var, call, g):
    return f'{var:<7} = {call.replace("@G", g)}'

# ── calendar family: Vizard, Hollow, Gran Rey Cero (same template as Desgarrón)
def calendar(name, paneOpts, paneTip, extra=None):
    f = F(name)
    old_on = f.take('clkOn  = input.bool(true, "Event clock"')
    old_met = f.take('clkMet = input.string("Range", "", options')
    old_lay = f.take('layI    = input.string("Full", "Layout"')
    old_sz = f.take('crdSzI  = input.string("Small", "Text"')
    old_th = f.take('themeI  = input.string("Auto", "Theme"')
    layTip = (tip(old_lay) or tip(old_th)).replace('Full: ', 'Desktop: ')
    if 'For a phone' not in layTip:
        layTip += ' For a phone, use a separate chart layout set to Mobile, since layouts sync across devices.'
    rows = [
        f'paneI   = input.string("{paneOpts[0]}", "Pane", options = [{", ".join(chr(34) + o + chr(34) for o in paneOpts)}], group = grpW, tooltip = "{paneTip}", display = display.none)',
        f'clkMet  = input.string("Range", "Clock measure", options = ["Range", "Net move"], group = grpW, tooltip = "{tip(old_met)}", display = display.none)',
        'themeI  = input.string("Auto", "Theme", options = ["Auto", "Dark", "Light"], group = grpW, tooltip = "Auto follows the chart background.", display = display.none)',
        f'layI    = input.string("Desktop", "Layout", options = ["Desktop", "Mobile"], group = grpW, tooltip = "{layTip}", display = display.none)',
        'crdSzI  = input.string("Small", "Card text", options = ["Tiny", "Small", "Normal"], group = grpW, display = display.none)']
    f.rep(BANNER, BANNER + view_block('grpW', rows))
    f.after('grpK = "Event clock (indicator pane)"\n', 'clkOn  = ' + ' or '.join(f'paneI == "{o}"' for o in paneOpts if 'clock' in o.lower()) + '\n')
    if extra: extra(f, old_th)
    f.save()
def viz_extra(f, old_th):
    f.take('showMap = input.bool(true, "Fed map"')
    f.after('grpP    = "Fed map (indicator pane, beside the clock)"\n', 'showMap = paneI == "Clock + Fed map" or paneI == "Fed map"\n')
    f.rep('mapPos  = input.string("Top left", "", options', 'mapPos  = input.string("Top left", "Position", options')
def grc_extra(f, old_th):
    f.rep('crdPos  = input.string("Top right", "Price-chart cards", options = ' + POS8 + ', group = grpR, inline = "r0", display = display.none)',
          'crdPos  = input.string("Top right", "Price-chart cards", options = ' + POS8 + ', group = grpR, tooltip = "' + tip(old_th) + '", display = display.none)')
calendar('Vizard', ['Clock + Fed map', 'Event clock', 'Fed map', 'Cards only'],
         "What the indicator pane shows. Event clock: today's running range (or net move) against FOMC days at the same time of day. Fed map: the heat table of the Fed path the market prices, from 30-day fed funds futures. Cards only: neither (the clock card stays where you put it).", viz_extra)
calendar('Hollow', ['Event clock', 'Cards only'],
         "What the indicator pane shows. Event clock: today's running range (or net move) against NFP-week days or the day after FOMC at the same time of day. Cards only: an empty pane for the cards you place there.")
calendar('Gran_Rey_Cero', ['Event clock', 'Cards only'],
         "What the indicator pane shows. Event clock: today's running range (or net move) against CPI days at the same time of day. Cards only: an empty pane for the clock card if you keep it there.", grc_extra)

# ── Senbonzakura: its first group becomes View
f = F('Senbonzakura')
old_lay = f.take('layI   = input.string("Full", "Layout"')
old_k = f.take('showK  = input.bool(true, "Kageyoshi')
old_s = f.take('showS  = input.bool(true, "Senkei')
old_th = f.take('themeI = input.string("Auto", "Theme"')
old_tx = f.take('txtI   = input.string("Small", "Text"')
rows = [
    'paneI  = input.string("Senkei · Fed path", "Pane", options = ["Senkei · Fed path", "Empty"], group = grpG, tooltip = "Senkei: the Fed path the market prices, meeting by meeting. Empty: keep only the curves on the price chart; the pane can then be made small.", display = display.none)',
    'themeI = input.string("Auto", "Theme", options = ["Auto", "Dark", "Light"], group = grpG, tooltip = "Auto follows the chart background.", display = display.none)',
    f'layI   = input.string("Desktop", "Layout", options = ["Desktop", "Mobile"], group = grpG, tooltip = "{tip(old_lay).replace("Full: ", "Desktop: ")}", display = display.none)',
    'txtI   = input.string("Small", "Text", options = ["Tiny", "Small", "Normal"], group = grpG, tooltip = "Mobile always uses tiny text.", display = display.none)',
    old_k.replace('"Kageyoshi · where today\'s close lands (price chart)"', '"Price chart: Kageyoshi (where today\'s close lands)"'),
    'showS  = paneI == "Senkei · Fed path"']
f.rep('grpG   = "Senbonzakura"\n', 'grpG   = "View"\n' + '\n'.join(rows) + '\n')
f.save()

# ── Genjutsu Kai and Hueco Mundo: Theme and card text up top
for name, gold, szPrefix in (('Genjutsu_Kai', 'gC', 'crdSzI  = input.string("Small", "", options = ["Tiny", "Small", "Normal"], group = gC'),
                             ('Hueco_Mundo', 'gT', 'crdSzI  = input.string("Small", "", options = ["Tiny", "Small", "Normal"], group = gT')):
    f = F(name)
    f.take(f'themeI  = input.string("Auto", "Theme", options = ["Auto", "Dark", "Light"], group = {gold}')
    f.take(szPrefix)
    rows = ['themeI  = input.string("Auto", "Theme", options = ["Auto", "Dark", "Light"], group = gV, tooltip = "Auto follows the chart background.", display = display.none)',
            'crdSzI  = input.string("Small", "Card text", options = ["Tiny", "Small", "Normal"], group = gV, display = display.none)']
    f.rep(BANNER, BANNER + view_block('gV', rows))
    f.save()

# ── OpenGaps: what is shown and the labels up top
f = F('OpenGaps_NWOG_NDOG')
old_show = f.take('showM  = input.string("All", "Show"')
old_lbl = f.take('lblI   = input.bool(true, "Labels"')
old_lsz = f.take('lblSzI = input.string("Small", "", options')
rows = [old_show.replace('group = gS', 'group = gV'), old_lbl.replace('group = gS', 'group = gV'), old_lsz.replace('group = gS', 'group = gV')]
f.rep(BANNER, BANNER + view_block('gV', rows))
f.save()

# ── first generation (Domain Expansion, Byakugan, Kekkai, Shikai / Bankai): the Drawing group becomes View at the top,
# a Theme input, colours left at their default follow the chart, every input off the status line, plain group names
THEME = '''// Theme: Auto follows the chart background; colours left at their default (#000001) follow it
bgLum  = 0.299 * color.r(chart.bg_color) + 0.587 * color.g(chart.bg_color) + 0.114 * color.b(chart.bg_color)
isDark = themeI == "Dark" or (themeI == "Auto" and bgLum < 128)
autoC(color c) => color.r(c) == 0 and color.g(c) == 0 and color.b(c) == 1
fgAuto = isDark ? #d1d4dc : #131722
'''
def firstgen(name, autos):
    f = F(name); L = f.S.split('\n')
    a = [k for k, l in enumerate(L) if l.startswith('var g_D = ')][0]
    b = a + 1
    while b < len(L) and ('group = g_D' in L[b]): b += 1
    blk = L[a:b]; del L[a:b]
    blk[0] = 'var g_D = "View"'
    blk.insert(1, 'themeI  = input.string("Auto", "Theme", options = ["Auto", "Dark", "Light"], group = g_D, tooltip = "Auto follows the chart background. Text and the colours left at their default follow it.")')
    blk = [l.replace('txtCol  = input.color(color.black, "Text colour", group = g_D)', 'txtColI = input.color(#000001, "Text colour", group = g_D, tooltip = "Left at the default it follows the theme; pick any colour to override.")') for l in blk]
    first = [k for k, l in enumerate(L) if l.startswith('var g_')][0]
    L[first:first] = blk + ['']
    S = '\n'.join(L)
    # colours with a black default follow the theme
    for var, call_old, call_new, derive in autos:
        assert S.count(call_old) == 1, (name, call_old); S = S.replace(call_old, call_new)
    lastIn = max(k for k, l in enumerate(S.split('\n')) if re.match(r'^\s*\w+\s*=\s*input(\.\w+)?\(', l))
    L = S.split('\n'); L[lastIn + 1:lastIn + 1] = [''] + (THEME + 'txtCol = autoC(txtColI) ? fgAuto : txtColI\n' + ''.join(d + '\n' for _, _, _, d in autos)).rstrip('\n').split('\n')
    S = '\n'.join(L)
    # plain group names and every input off the status line
    S = re.sub(r'(var g_\w+ = )"═+ (.*?) ═+"', r'\1"\2"', S)
    out = []
    for l in S.split('\n'):
        if re.match(r'^\s*\w+\s*=\s*input(\.\w+)?\(.*\)\s*$', l) and 'display =' not in l:
            l = l.rstrip(); l = l[:-1] + ', display = display.none)'
        out.append(l)
    f.S = '\n'.join(out); f.save()
firstgen('Domain_Expansion_Indicator', [])
firstgen('Kekkai_Barrier_Indicator', [])
firstgen('Byakugan_FPFVG', [('colCE', 'colCE    = input.color(color.black, "CE (50% of the gap)"', 'colCEI   = input.color(#000001, "CE (50% of the gap)"', 'colCE  = autoC(colCEI) ? fgAuto : colCEI')])
firstgen('Shikai_Bankai_Session_Map', [
    ('colCandle', 'colCandle   = input.color(color.black, "Candle colour"', 'colCandleI  = input.color(#000001, "Candle colour"', 'colCandle = autoC(colCandleI) ? fgAuto : colCandleI'),
    ('colVline', 'colVline    = input.color(color.new(color.black, 70), ""', 'colVlineI   = input.color(#000001, ""', 'colVline  = autoC(colVlineI) ? color.new(fgAuto, 70) : colVlineI'),
    ('tblBg', 'tblBg    = input.color(color.new(color.white, 10), "Background"', 'tblBgI   = input.color(#000001, "Background"', 'tblBg     = autoC(tblBgI) ? (isDark ? #161a23 : #f4f6f9) : tblBgI'),
    ('tblTxt', 'tblTxt   = input.color(color.black, "Text"', 'tblTxtI  = input.color(#000001, "Text"', 'tblTxt    = autoC(tblTxtI) ? fgAuto : tblTxtI'),
    ('tblBdr', 'tblBdr   = input.color(color.black, "Border"', 'tblBdrI  = input.color(#000001, "Border"', 'tblBdr    = autoC(tblBdrI) ? (isDark ? #2a2e39 : #d1d4dc) : tblBdrI')])
print('done')
