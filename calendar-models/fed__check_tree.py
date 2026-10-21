"""Check the probability tree against CME's own FedWatch output (sample of 23 Oct 2025, six meetings)."""
import json, numpy as np
from fedwatch import tree, rng
raw = open('/mnt/user-data/uploads/CVOL EOD Rest API sample/FedWatch Intraday Forecasts/FedWatch Intraday Forecasts.json').read().strip()
raw = '{"' + raw + '\n]}'                      # the sample file is cut at both ends
J = json.loads(raw.replace('ratetRange', 'rateRange'))['payload']
cur_lo = 4.00
deltas, prevE = [], 0.0
for mtg in J:
    P = {round((r['lowerRt'] / 100 - cur_lo) / 0.25): r['probability'] for r in mtg['rateRange']}
    E = sum(k * p for k, p in P.items())          # mean of the cumulative steps = sum of the nodes' means
    deltas.append(0.25 * (E - prevE)); prevE = E
dist = tree(deltas)
mx = 0
for j, mtg in enumerate(J):
    cells = []
    for r in mtg['rateRange']:
        k = round((r['lowerRt'] / 100 - cur_lo) / 0.25)
        mx = max(mx, abs(dist[j][20 + k] - r['probability']))
        cells.append(f"{rng(cur_lo, k)} {dist[j][20 + k]:.4f}/{r['probability']:.4f}")
    print(mtg['meetingDt'], f"node {100 * deltas[j]:+6.2f}bp |", ' '.join(cells))
print('largest gap, rebuilt vs CME, over every bucket:', f'{mx:.1e}')
