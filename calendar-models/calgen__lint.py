import re, sys
for path in sys.argv[1:]:
    s = open(path).read()
    code = []
    for line in s.split('\n'):
        out = ''; i = 0; ins = None
        while i < len(line):
            ch = line[i]
            if ins:
                if ch == '\\': i += 2; continue
                if ch == ins: ins = None
                i += 1; continue
            if ch in '"\'': ins = ch; out += ' S '; i += 1; continue
            if line.startswith('//', i): break
            out += ch; i += 1
        code.append(out)
    C = '\n'.join(code); C = re.sub(r'#[0-9a-fA-F]{6,8}', ' ', C)
    decl = set()
    decl |= set(re.findall(r'^\s*(?:var\s+|varip\s+)?(?:(?:float|int|bool|string|color|line|label|box|table|polyline|linefill)\s+|array<[\w.]+>\s+|matrix<\w+>\s+)?([A-Za-z_]\w*)\s*(?::)?=(?!=)', C, re.M))
    decl |= set(re.findall(r'^\s*([A-Za-z_]\w*)\s*\(.*\)\s*=>', C, re.M))
    for params in re.findall(r'^\s*[A-Za-z_]\w*\s*\((.*)\)\s*=>', C, re.M):
        for p in params.split(','):
            m = re.findall(r'([A-Za-z_]\w*)\s*(?:=.*)?$', p.strip())
            if m: decl.add(m[0])
    for t in re.findall(r'^\s*\[([^\]]+)\]\s*=', C, re.M): decl |= {x.strip() for x in t.split(',')}
    decl |= set(re.findall(r'\bfor\s+([A-Za-z_]\w*)\s*(?:=|in)', C))
    decl |= set(re.findall(r'^type\s+(\w+)', C, re.M))
    B = set('''if else for in to by while switch and or not true false na var varip int float bool string color line label box table polyline linefill array matrix chart time open high low close volume bar_index last_bar_index last_bar_time timenow syminfo timeframe barstate math str ta request input plot bgcolor indicator year month dayofmonth dayofweek hour minute timestamp size position text font extend xloc yloc display plot shape location format barmerge na nz max_bars_back time_tradingday S type method export import break continue series simple const'''.split())
    used = set(re.findall(r'(?<![\.\w])([A-Za-z_]\w*)\b(?!\s*=[^=])', C))
    miss = sorted(u for u in used if u not in decl and u not in B)
    # use-before-declare for top-level names (Pine needs declaration first)
    first_decl = {}
    for n, l in enumerate(code):
        m = re.match(r'^(?:var\s+|varip\s+)?(?:(?:float|int|bool|string|color|table)\s+|array<[\w.]+>\s+)?([A-Za-z_]\w*)\s*(?:\(.*\)\s*=>|=(?!=))', l)
        if m and m.group(1) not in first_decl: first_decl[m.group(1)] = n
        for t in re.findall(r'^\[([^\]]+)\]\s*=', l):
            for x in t.split(','): first_decl.setdefault(x.strip(), n)
    late = []
    for n, l in enumerate(code):
        if l.startswith(' ') or not l.strip(): continue
        for u in set(re.findall(r'(?<![\.\w])([A-Za-z_]\w*)\b', l)):
            if u in first_decl and first_decl[u] > n: late.append((n + 1, u))
    print(path, 'undeclared:', [m for m in miss if m != 'pts'], '| used before declared (top level):', late[:10])
# globals used inside a function body must be declared before the function
def fn_check(path):
    s = open(path).read().split('\n')
    code = []
    for line in s:
        out = ''; i = 0; ins = None
        while i < len(line):
            ch = line[i]
            if ins:
                if ch == '\\': i += 2; continue
                if ch == ins: ins = None
                i += 1; continue
            if ch in '"\'': ins = ch; out += ' S '; i += 1; continue
            if line.startswith('//', i): break
            out += ch; i += 1
        code.append(out)
    first = {}
    for n, l in enumerate(code):
        m = re.match(r'^(?:var\s+|varip\s+)?(?:(?:float|int|bool|string|color|table)\s+|array<[\w.]+>\s+)?([A-Za-z_]\w*)\s*(?:\(.*\)\s*=>|=(?!=))', l)
        if m and m.group(1) not in first: first[m.group(1)] = n
        for t in re.findall(r'^\[([^\]]+)\]\s*=', l):
            for x in t.split(','): first.setdefault(x.strip(), n)
    bad = []
    n = 0
    while n < len(code):
        m = re.match(r'^([A-Za-z_]\w*)\s*\((.*)\)\s*=>(.*)$', code[n])
        if m:
            params = {re.findall(r'([A-Za-z_]\w*)\s*(?:=.*)?$', p.strip())[0] for p in m.group(2).split(',') if p.strip() and re.findall(r'([A-Za-z_]\w*)\s*(?:=.*)?$', p.strip())}
            body = [m.group(3)]; k = n + 1
            while k < len(code) and (code[k].startswith(' ') or code[k] == ''):
                body.append(code[k]); k += 1
            for u in set(re.findall(r'(?<![\.\w])([A-Za-z_]\w*)\b', ' '.join(body))):
                if u in first and first[u] > n and u not in params: bad.append((n + 1, m.group(1), u))
            n = k
        else: n += 1
    print(path, 'functions using later globals:', bad[:12])
for p in sys.argv[1:]: fn_check(p)
