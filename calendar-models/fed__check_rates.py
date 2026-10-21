"""Round trip: build ZQ prices from a known expected rate path, then recover each meeting's expected change."""
import calendar, datetime as dt, numpy as np, re
from fedwatch import *
S = open('/home/claude/hm/Vizard.pine').read()
FOMC = [dt.date(int(x[:4]), int(x[4:6]), int(x[6:])) for x in re.findall(r'20\d{6}', S[S.index('S_FOMC'):S.index('S_CPI')])]
true = {dt.date(2025, 10, 29): -0.2472, dt.date(2025, 12, 10): -0.2311, dt.date(2026, 1, 28): -0.1439,
        dt.date(2026, 3, 18): -0.1326, dt.date(2026, 4, 29): -0.0724, dt.date(2026, 6, 17): -0.1448,
        dt.date(2026, 7, 29): -0.05, dt.date(2026, 9, 16): -0.03, dt.date(2026, 10, 28): 0.0, dt.date(2026, 12, 9): -0.02}
def expected_rate(day, r0=4.09):
    return r0 + sum(v for k, v in true.items() if k < day)      # a decision on day d takes effect on d + 1
def prices(grid):
    out = []
    for y, m in grid:
        N = calendar.monthrange(y, m)[1]
        out.append(100 - np.mean([expected_rate(dt.date(y, m, d)) for d in range(1, N + 1)]))
    return out
for today, after in [(dt.date(2025, 10, 23), False), (dt.date(2025, 10, 29), True), (dt.date(2026, 4, 2), False), (dt.date(2026, 6, 17), False)]:
    g = month_grid(today)
    r = fedwatch(prices(g), g, FOMC, today, after_statement=after)
    errs = [abs(x['delta_bp'] - 100 * true[x['meeting']]) for x in r['rows']]
    print(today, 'after 14:00' if after else '', '| range now', rng(r['lower0'], 0), '|',
          ' '.join(f"{x['meeting']:%d%b} {x['delta_bp']:+.2f}" for x in r['rows']), f'| max error {max(errs):.1e} bp')
# expired prior-month contract: 3 Dec 2025, the Dec 10 meeting's usual anchor (November) is missing
today = dt.date(2025, 12, 3); g = month_grid(today); p = prices(g); p[0] = float('nan')
r = fedwatch(p, g, FOMC, today)
print(today, 'Nov contract missing |', ' '.join(f"{x['meeting']:%d%b} {x['delta_bp']:+.2f}" for x in r['rows']),
      f"| max error {max(abs(x['delta_bp'] - 100 * true[x['meeting']]) for x in r['rows']):.1e} bp")
