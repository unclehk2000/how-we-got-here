"""Check against CME FedWatch for 12 Oct 2026: ZQ prices and conditional meeting odds as shown on CME's page."""
import datetime as dt, re, numpy as np
import fedwatch as FW
S = open('/home/claude/hm/Vizard.pine').read()
FOMC = [dt.date(int(x[:4]), int(x[4:6]), int(x[6:])) for x in re.findall(r'20\d{6}', S[S.index('S_FOMC'):S.index('S_CPI')])]
P = {(2026, 10): 96.1163, (2026, 11): 96.0675, (2026, 12): 95.9125, (2027, 1): 95.8425, (2027, 2): 95.7475, (2027, 3): 95.6650,
     (2027, 4): 95.5575, (2027, 5): 95.4675, (2027, 6): 95.3925, (2027, 7): 95.3575, (2027, 8): 95.3225, (2027, 9): 95.3025, (2027, 10): 95.2825}
CME = {'2026-10-28': {375: 78.4, 400: 21.6}, '2026-12-09': {375: 12.3, 400: 69.5, 425: 18.2}, '2027-01-27': {375: 6.9, 400: 44.5, 425: 40.6, 450: 7.9},
       '2027-03-17': {375: 1.8, 400: 16.9, 425: 43.5, 450: 31.9, 475: 5.8}, '2027-04-28': {375: 1.1, 400: 11.1, 425: 33.2, 450: 36.4, 475: 15.9, 500: 2.3},
       '2027-06-09': {375: 0.6, 400: 6.9, 425: 23.8, 450: 35.1, 475: 24.6, 500: 8.1, 525: 1.0}, '2027-07-28': {375: 0.5, 400: 5.9, 425: 21.2, 450: 33.3, 475: 26.2, 500: 10.6, 525: 2.1, 550: 0.1},
       '2027-09-15': {375: 0.5, 400: 5.1, 425: 18.8, 450: 31.4, 475: 27.3, 500: 13.1, 525: 3.4, 550: 0.4}}
g = [FW.month_add(2026, 9, k) for k in range(14)]
r = FW.fedwatch([P.get(m, float('nan')) for m in g], g, FOMC, dt.date(2026, 10, 12), k_meet=10)
mx = 0
for row in r['rows']:
    k = row['meeting'].isoformat()
    if k in CME:
        gap = max(abs(row['dist'][20 + round((lo / 100 - r['lower0']) / .25)] * 100 - p) for lo, p in CME[k].items()); mx = max(mx, gap)
        print(k, f"node {row['delta_bp']:+.2f}bp, largest gap {gap:.2f}pp")
print('all meetings: largest gap', round(mx, 2), 'pp (CME prints one decimal)')
