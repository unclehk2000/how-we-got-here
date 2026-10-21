"""Cero and Hollow rebuilt on the Vizard v2 template: the template's generic parts (data loaders, helpers, trackers,
requests, clock, card engine, tally, cardFlush) with each module's own profiles, clock data, model structure, stage
capture and stages card."""
import re, json, sys
T = open('/home/claude/hm/vizard2/Vizard.pine', encoding='utf-8').read().split('\n')
D = json.load(open('/home/claude/hm/calgen/data.json'))
P92 = "!#$%&'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[]^_`abcdefghijklmnopqrstuvwxyz{|}~"
FR = lambda n: open(f'/home/claude/hm/calgen/frag/{n}', encoding='utf-8').read().rstrip('\n').split('\n')
def idx(L, pred, start=0):
    for i in range(start, len(L)):
        if pred(L[i]): return i
    raise KeyError
def sec(L, title, start=0): return idx(L, lambda l: l.startswith('// ═') and title in l, start)
def splice(L, a, b, new):                       # replace L[a:b]
    return L[:a] + new + L[b:]
def rep1(L, old, new):
    hits = [i for i, l in enumerate(L) if l == old]; assert len(hits) == 1, (old[:60], len(hits))
    L[hits[0]:hits[0] + 1] = new if isinstance(new, list) else [new]; return L
def packCK(mod):
    s = open(f'/home/claude/hm/{mod}.pine', encoding='utf-8').read()
    out = []
    for name in ('CK_NQ', 'CK_ES'):
        m = re.search(r'(?m)^' + name + r'\s*=\s*"[^"]*"(?:\n\s+\+\s*"[^"]*")*', s)
        body = ''.join(re.findall(r'"([^"]*)"', m.group(0)))
        vals = [int(v) for v in re.split(r'[,;]', body) if v != '']
        e = ''.join(P92[(v + 2000) // 92] + P92[(v + 2000) % 92] for v in vals)
        parts = [e[i:i + 180] for i in range(0, len(e), 180)]
        out += [f'{name} = "' + parts[0] + '"'] + [f'     + "{p}"' for p in parts[1:]]
        print(mod, name, len(vals), 'values')
    return out
def profiles(mod):
    L = open(f'/home/claude/hm/{mod}.pine', encoding='utf-8').read().split('\n')
    a = idx(L, lambda l: l.startswith('pfName(int k) =>')); b = idx(L, lambda l: l.startswith('// ADR20, built'), a)
    blk = L[a:b]; out = []; skip = False
    for l in blk:
        if l.startswith('chkRows(') : skip = True; continue
        if skip and (l.startswith('    ') or l.startswith('chkMax(')): continue
        skip = False
        if l.startswith('IVRV_'): continue
        out.append(l)
    return out
def build(mod, name, NCK, REL, extra_tips=None):
    L = list(T)
    # 1 header and indicator
    a = 4; b = idx(L, lambda l: l.startswith('indicator('))
    L = splice(L, a, b - 1, FR(f'{mod}_header.pine'))
    i = idx(L, lambda l: l.startswith('indicator('))
    L[i] = L[i].replace('indicator("Vizard", "Vizard"', f'indicator("{name}", "{name}"')
    # 2 inputs
    a = idx(L, lambda l: l.startswith('grpE = "Event day"')); b = sec(L, 'Data')
    L = splice(L, a, b, FR(f'{mod}_inputs.pine'))
    # 3 clock data
    a = idx(L, lambda l: l.startswith('CK_NQ = ')); b = idx(L, lambda l: l == '', a)
    L = splice(L, a, b, packCK(name))
    # 4 profiles
    a = idx(L, lambda l: l.startswith('pfName(int k) =>')); b = idx(L, lambda l: l.startswith('// ADR20, built'), a)
    L = splice(L, a, b, profiles(name) + [''])
    # 5 Fed odds: out
    a = sec(L, 'Fed odds'); b = sec(L, 'FOMC stages (Vizard)')
    L = splice(L, a, b, [])
    # 6 stage globals
    a = sec(L, 'FOMC stages (Vizard)'); b = sec(L, 'Model structure on the price chart')
    st = []
    for l in FR(f'{mod}_stage.pine'):
        if '@@TIPS@@' in l: st += open(f'/home/claude/hm/calgen/tips_{mod}.pine', encoding='utf-8').read().rstrip('\n').split('\n')
        else:
            for k, v in (('@@VS_NQ@@', D[mod]['NQ'][0]), ('@@VS_ES@@', D[mod]['ES'][0]), ('@@VH_NQ@@', D[mod]['NQ'][1]), ('@@VH_ES@@', D[mod]['ES'][1])): l = l.replace(k, v)
            st.append(l)
    L = splice(L, a, b, st)
    # 7 model structure
    a = sec(L, 'Model structure on the price chart'); b = sec(L, 'Event clock (indicator pane)')
    L = splice(L, a, b, FR(f'{mod}_struct.pine') + [''])
    # 8 clock
    L = rep1(L, 'NCK = 3', f'NCK = {NCK}'); L = rep1(L, 'REL = "840,870"', f'REL = "{REL}"')
    L = rep1(L, 'bool  ckTop = (showCk and ckOn == "Indicator pane" and str.startswith(ckPos, "Top")) or (showMap and str.startswith(mapPos, "Top"))',
             'bool  ckTop = showCk and ckOn == "Indicator pane" and str.startswith(ckPos, "Top")')
    # 9 cards: no Fed card
    a = sec(L, 'Cards')
    L[a + 1:a + 4] = ['// Price chart: two cards, each its own table in its own corner: the event tally and the stages card. Each card is an',
                      '// accent stripe, a header bar with a status pill and a tinted body. The clock card (indicator pane by default) uses the',
                      '// same style. Five columns: stripe · key · wording · value · comparison.']
    L = [l for l in L if not (l.startswith('FD_N = ') or l == 'var table TF  = na' or l == 'var int   tfO = 0')]
    a = idx(L, lambda l: l == '    if showFd'); b = idx(L, lambda l: l == '    if showCk', a)
    L = splice(L, a, b, [])
    # 10 tally / clock card names, next-event text
    for i, l in enumerate(L):
        if '" VIZARD · ' in l: L[i] = l.replace('" VIZARD · ', f'" {name.upper()} · ')
    a = idx(L, lambda l: l.startswith('        string nxT  = ')); assert L[a + 1].startswith('        string nxTip = ')
    L = splice(L, a, a + 2, FR(f'{mod}_next.pine'))
    # 11 right-side drawings: the module's own; Fed card out
    a = idx(L, lambda l: l.startswith('drawLast1() =>')); b = idx(L, lambda l: l == 'drawLast2()', a)
    L = splice(L, a, b + 1, FR(f'{mod}_last1.pine'))
    # 12 Fed map out
    a = sec(L, 'Fed map (indicator pane)'); b = idx(L, lambda l: l == 'drawMap()', a)
    L = splice(L, a, b + 2, [])
    # 13 stages card
    a = sec(L, 'FOMC stages card (last bar)'); b = idx(L, lambda l: l == 'drawSg()', a)
    L = splice(L, a, b + 2, FR(f'{mod}_sg.pine'))
    s = '\n'.join(L)
    for bad in ('showFd', 'showMap', 'fdZ', 'cFd', 'paneV', 'VZT_GF', 'CONE_'):
        if bad in s: print('  leftover', bad, [l[:90] for l in L if bad in l][:3])
    open(f'/home/claude/hm/calgen/{name}.pine', 'w', encoding='utf-8').write(s)
    print(name, len(L), 'lines')
if __name__ == '__main__':
    for m in sys.argv[1:]:
        if m == 'cero': build('cero', 'Cero', 2, '510')
        if m == 'hollow': build('hollow', 'Hollow', 3, '')
