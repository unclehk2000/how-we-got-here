import json, numpy as np, pandas as pd
C = pd.read_pickle('lon_ck.pkl')
C['tr'] = C.tday < '2025'
# (b) live odds of 2 SD by 04:59 given the furthest SD so far
sb = [0, 0.5, 1.0, 1.5, 2.0, 99]
C['sb'] = pd.cut(C.sofar, sb, right=False, labels=['<0.5', '0.5-1', '1-1.5', '1.5-2', '2+'])
t = C.pivot_table(index='ck', columns='sb', values='reach2', aggfunc='mean', observed=False)
n = C.pivot_table(index='ck', columns='sb', values='reach2', aggfunc='size', observed=False)
print('(b) P(2 SD by 04:59 | checkpoint, furthest SD so far)'); print(t.round(2)); print(n)
h1 = C[C.tr].pivot_table(index='ck', columns='sb', values='reach2', aggfunc='mean', observed=False)
h2 = C[~C.tr].pivot_table(index='ck', columns='sb', values='reach2', aggfunc='mean', observed=False)
print('max |half diff|', (h1 - h2).abs().max().round(2).to_dict())
# (c) high already in / low already in by distance (domain ranges) from the London extreme so far
db = [0, 0.25, 0.5, 1.0, 2.0, 99]
lab = ['<.25', '.25-.5', '.5-1', '1-2', '2+']
H = C[['tday', 'sym', 'ck', 'dHi', 'hiIn', 'tr']].rename(columns={'dHi': 'd', 'hiIn': 'inn'})
L = C[['tday', 'sym', 'ck', 'dLo', 'loIn', 'tr']].rename(columns={'dLo': 'd', 'loIn': 'inn'})
for nm, X in (('high', H), ('low', L)):
    X = X.copy(); X['db'] = pd.cut(X.d, db, right=False, labels=lab)
    tt = X.pivot_table(index='ck', columns='db', values='inn', aggfunc='mean', observed=False)
    print(f'\n(c) P({nm} already in | checkpoint, distance from the {nm} so far in domain ranges)'); print(tt.round(2))
HL = pd.concat([H, L]); HL['db'] = pd.cut(HL.d, db, right=False, labels=lab)
tt = HL.pivot_table(index='ck', columns='db', values='inn', aggfunc='mean', observed=False)
nn = HL.pivot_table(index='ck', columns='db', values='inn', aggfunc='size', observed=False)
a1 = HL[HL.tr].pivot_table(index='ck', columns='db', values='inn', aggfunc='mean', observed=False)
a2 = HL[~HL.tr].pivot_table(index='ck', columns='db', values='inn', aggfunc='mean', observed=False)
print('\npooled high+low'); print(tt.round(2)); print(nn.min().min(), 'min n'); print('max |half diff|', (a1 - a2).abs().max().round(2).to_dict())
for s in ('NQ', 'ES', 'RTY'):
    x = HL[HL.sym == s].pivot_table(index='ck', columns='db', values='inn', aggfunc='mean', observed=False)
    print(s, 'max |diff from pooled|', (x - tt).abs().max().max().round(2))
json.dump(dict(two_sd=t.round(3).to_dict(orient='index'), two_sd_n=n.to_dict(orient='index'), hl_in=tt.round(3).to_dict(orient='index'), hl_n=nn.to_dict(orient='index')),
          open('lon_tables.json', 'w'), default=float, indent=1)
