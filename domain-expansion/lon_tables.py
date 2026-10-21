"""Final tables for Domain Expansion's London card, split by coiled (domain range / overnight ATR(5) <= 0.20) or not.
Pooled NQ + ES + RTY 1-minute 2018–26. Prints Pine-ready strings and the stability checks."""
import json, numpy as np, pandas as pd
C = pd.read_pickle('lon_ck.pkl'); R = pd.read_pickle('lon_rows.pkl')
R['co'] = R.coil <= 0.20
C = C.merge(R[['sym', 'tday', 'co']], on=['sym', 'tday'])
C['tr'] = C.tday < '2025'
CK = [230, 245, 300, 315, 330, 345, 400, 415, 430, 445]
SB = [0, 0.5, 1.0, 1.5, 2.0]
DB = [0, 0.25, 0.5, 1.0, 2.0, 99]
out = {}
def tab(X, val, bins, col):
    X = X.copy()
    X['b'] = pd.cut(X[col], bins, right=False, labels=False)
    return X
for co in (False, True):
    S = C[C.co == co]
    # (b) live 2 SD odds
    X = S.copy(); X['b'] = pd.cut(X.sofar, SB + [99], right=False, labels=False)
    p = X.pivot_table(index='ck', columns='b', values='reach2', aggfunc='mean').reindex(index=CK, columns=range(4))
    n = X.pivot_table(index='ck', columns='b', values='reach2', aggfunc='size').reindex(index=CK, columns=range(4)).fillna(0)
    a1 = X[X.tr].pivot_table(index='ck', columns='b', values='reach2', aggfunc='mean').reindex(index=CK, columns=range(4))
    a2 = X[~X.tr].pivot_table(index='ck', columns='b', values='reach2', aggfunc='mean').reindex(index=CK, columns=range(4))
    # fill thin / empty cells (n < 30) with the next checkpoint-free fallback: same bucket, pooled over checkpoints ±15 min
    p = p.where(n >= 30)
    p = p.T.ffill().bfill().T if p.isna().any().any() else p
    print('coiled' if co else 'other', '(b) 2 SD odds'); print((p * 100).round(0)); print('min n used', n.where(n >= 30).min().min(), '| max half diff (n>=60):', ((a1 - a2).abs().where(n >= 60)).max().max().round(2))
    out[('b', co)] = p
    # (c) high / low already in
    H = S[['ck', 'dHi', 'hiIn', 'tr']].rename(columns={'dHi': 'd', 'hiIn': 'inn'})
    L = S[['ck', 'dLo', 'loIn', 'tr']].rename(columns={'dLo': 'd', 'loIn': 'inn'})
    Y = pd.concat([H, L]); Y['b'] = pd.cut(Y.d, DB, right=False, labels=False)
    q = Y.pivot_table(index='ck', columns='b', values='inn', aggfunc='mean').reindex(index=CK, columns=range(5))
    m = Y.pivot_table(index='ck', columns='b', values='inn', aggfunc='size').reindex(index=CK, columns=range(5)).fillna(0)
    b1 = Y[Y.tr].pivot_table(index='ck', columns='b', values='inn', aggfunc='mean').reindex(index=CK, columns=range(5))
    b2 = Y[~Y.tr].pivot_table(index='ck', columns='b', values='inn', aggfunc='mean').reindex(index=CK, columns=range(5))
    q = q.where(m >= 30)
    q = q.T.ffill().bfill().T if q.isna().any().any() else q
    print('(c) high/low already in'); print((q * 100).round(0)); print('max half diff (n>=60):', ((b1 - b2).abs().where(m >= 60)).max().max().round(2))
    out[('c', co)] = q
# Pine strings: rows by checkpoint, percentages as integers
def s(df):
    return ','.join(str(int(round(v * 100))) for v in df.values.flatten())
pine = {'LV_O': s(out[('b', False)]), 'LV_C': s(out[('b', True)]), 'IN_O': s(out[('c', False)]), 'IN_C': s(out[('c', True)])}
json.dump(pine, open('lon_pine.json', 'w'), indent=1)
for k, v in pine.items():
    print(k, len(v.split(',')), v[:80])
