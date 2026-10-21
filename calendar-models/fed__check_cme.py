"""Check the FedWatch steps against CME's own screenshot (12 Oct 2026): ZQ prices → conditional and aggregated odds.
Rule that matches CME: meetings come in runs of consecutive meeting months between non-meeting (anchor) months.
The month after a run anchors the last meeting's end rate; working backward, each meeting's start rate is solved from
its own contract and becomes the previous meeting's end rate; the first meeting of a run takes its start rate from the
anchor month before the run (its own contract is not used). If that anchor is missing (an expired contract), the start
rate is solved from the meeting month's own contract instead."""
import calendar, numpy as np, re, datetime as dt
from fedwatch import tree, rng
S = open('/home/claude/hm/Vizard.pine').read()
FOMC = [dt.date(int(x[:4]), int(x[4:6]), int(x[6:])) for x in re.findall(r'20\d{6}', S[S.index('S_FOMC'):S.index('S_CPI')])]
md = lambda y, m: next((d.day for d in FOMC if d.year == y and d.month == m), 0)
grid = [(2026, 9)] + [(2026, m) for m in (10, 11, 12)] + [(2027, m) for m in range(1, 11)]
P1 = [np.nan, 96.1163, 96.0675, 95.9125, 95.8425, 95.7475, 95.6650, 95.5575, 95.4675, 95.3925, 95.3575, 95.3225, 95.3025, 95.2825]
P2 = list(P1); P2[6] = 95.6625
def rates(P):
    A = [100 - p for p in P]; n = len(A)
    D = [md(*g) for g in grid]; N = [calendar.monthrange(*g)[1] for g in grid]
    s, e = [np.nan] * n, [np.nan] * n
    for i in range(n - 1, -1, -1):
        d = D[i]
        if not d or np.isnan(A[i]): continue
        if i + 1 < n and D[i + 1] == 0 and not np.isnan(A[i + 1]): e[i] = A[i + 1]
        elif i + 1 < n and D[i + 1] > 0 and not np.isnan(s[i + 1]): e[i] = s[i + 1]
        else: continue
        if i > 0 and D[i - 1] == 0 and not np.isnan(A[i - 1]): s[i] = A[i - 1]
        else: s[i] = (A[i] * N[i] - e[i] * (N[i] - d)) / d
    return s, e, D
CME_C = {'2026-10-28': [78.4, 21.6], '2026-12-09': [12.3, 69.5, 18.2], '2027-01-27': [6.9, 44.5, 40.6, 7.9], '2027-03-17': [1.8, 16.9, 43.5, 31.9, 5.8],
         '2027-04-28': [1.1, 11.1, 33.2, 36.4, 15.9, 2.3], '2027-06-09': [0.6, 6.9, 23.8, 35.1, 24.6, 8.1, 1.0], '2027-07-28': [0.5, 5.9, 21.2, 33.3, 26.2, 10.6, 2.1, 0.1]}
CME_A = {'2026-10-28': (0, 78.41), '2026-12-09': (1, 94.04), '2027-01-27': (1, 50.41), '2027-03-17': (2, 76.98), '2027-04-28': (2, 38.41), '2027-06-09': (3, 95.91), '2027-07-28': (3, 80.41)}
s, e, D = rates(P1)
idx = [i for i in range(len(grid)) if D[i] and not np.isnan(s[i])]
dl = [e[i] - s[i] for i in idx]; dist = tree(dl)
lo0 = 3.75
print('conditional (ours / CME), current range 375–400:')
mx = 0
for j, i in enumerate(idx):
    key = f'{grid[i][0]}-{grid[i][1]:02d}-{D[i]:02d}'
    if key not in CME_C: continue
    ours = [100 * dist[j][20 + k] for k in range(len(CME_C[key]))]
    mx = max(mx, max(abs(a - b) for a, b in zip(ours, CME_C[key])))
    print(f'  {key} node {100 * dl[j]:+6.2f}bp ', ' '.join(f'{a:5.1f}/{b:<5.1f}' for a, b in zip(ours, CME_C[key])))
print(f'  largest gap {mx:.2f} pp')
s, e, D = rates(P2); dl2 = [e[i] - s[i] for i in idx]; cum = np.cumsum(dl2)
print('aggregated (cumulative expected change → two nearest ranges):')
for j, i in enumerate(idx):
    key = f'{grid[i][0]}-{grid[i][1]:02d}-{D[i]:02d}'
    if key not in CME_A: continue
    st = cum[j] / 0.25; k = int(np.floor(st)); r = st - k
    p = {k: 1 - r, k + 1: r}
    kk, cme = CME_A[key]
    print(f'  {key} cum {100 * cum[j]:+6.2f}bp → {rng(lo0, kk)} {100 * p.get(kk, 0):6.2f}% (CME {cme:.2f}%)')
