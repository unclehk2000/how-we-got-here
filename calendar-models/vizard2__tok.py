import re, sys
def measure(path):
    src = open(path).read()
    code_tokens = 0; str_chars = 0; nstr = 0
    for line in src.splitlines():
        # strip comments outside strings
        out = []; i = 0; s = line
        res = ''
        in_s = None
        j = 0
        while j < len(s):
            c = s[j]
            if in_s:
                if c == '\\': j += 2; continue
                if c == in_s: in_s = None
                j += 1; continue
            if c in '"\'':
                in_s = c; j += 1; continue
            if s.startswith('//', j):
                s = s[:j]; break
            j += 1
        strs = re.findall(r'"(?:[^"\\]|\\.)*"|\'(?:[^\'\\]|\\.)*\'', s)
        for x in strs: str_chars += len(x) - 2; nstr += 1
        t = re.sub(r'"(?:[^"\\]|\\.)*"|\'(?:[^\'\\]|\\.)*\'', ' S ', s)
        code_tokens += len(re.findall(r'[A-Za-z_][A-Za-z_0-9.]*|\d+\.?\d*(?:e-?\d+)?|==|!=|<=|>=|:=|=>|\+=|-=|[-+*/%<>=?:,()\[\]{}]', t))
    return code_tokens, str_chars, nstr, len(src.splitlines())
if __name__ == '__main__':
    for p in sys.argv[1:]:
        print(p, 'flat %d  strings %d  nstr %d  lines %d' % measure(p))
