import re, sys
sig = {'cardRow': (9, 11), 'cardHead': (8, 8), 'cardSub': (6, 6), 'cardWide': (7, 7), 'tcQ': (6, 9), 'stripeQ': (3, 3), 'zoneRow': (7, 7), 'ctxOf': (3, 4), 'dxPill': (3, 3), 'liveTx': (2, 2), 'trimL': (2, 2), 'trimT': (2, 2), 'fdSg': (2, 2)}
def args(text, i):
    depth = 0; cur = ''; out = []; ins = None
    while i < len(text):
        ch = text[i]
        if ins:
            cur += ch
            if ch == ins: ins = None
        elif ch == '"': ins = '"'; cur += ch
        elif ch in '([': depth += 1; cur += ch
        elif ch in ')]':
            if depth == 0: out.append(cur); return out
            depth -= 1; cur += ch
        elif ch == ',' and depth == 0: out.append(cur); cur = ''
        else: cur += ch
        i += 1
for path in sys.argv[1:]:
    s = open(path).read(); bad = 0; lines = s.split('\n')
    for name, (lo, hi) in sig.items():
        for m in re.finditer(r'(?<![\w.])' + name + r'\(', s):
            ln = s[:m.start()].count('\n') + 1
            if re.match(r'^\s*' + name + r'\(.*=>', lines[ln - 1]): continue
            a = args(s, m.end())
            if not (lo <= len(a) <= hi): print(path, name, ln, len(a)); bad += 1
    print(path, 'arg problems', bad)
