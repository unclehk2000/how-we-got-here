"""Pine data snippets for Cero and Hollow from the HYDRA calendar tables (card_stats.json, dxy_cal.json)."""
import json, numpy as np
S = json.load(open('/home/claude/hm/hydra_cal/card_stats.json')); X = json.load(open('/home/claude/hm/hydra_cal/dxy_cal.json'))
def f2(v): return 'nan' if v is None or not np.isfinite(v) else f'{v:.2f}'
def pc(v): return '-1' if v is None or not np.isfinite(v) else f'{100 * v:.0f}'
def raw_rate(R, col, grp, t):
    x = R[col][grp][t]; return x['v'] if x['n'] >= 5 else np.nan
def rate_any(ev, sym, col, grp, t):
    import pandas as pd
    import sys; sys.path.insert(0, '/home/claude/hm/hydra_cal')
    return None
def build_cero(sym):
    R = S['nfp'][sym]; vs, vh = [], []
    for t in ('m_s1', 'm_s2', 'm_am', 'postRng', 'nRng'):
        for z in range(3):
            med, p80, h = R[t][z]; vs += [f2(med), f2(p80)]; vh += ['1' if h['held'] else '0'] * 2
    for col, grps in (('pd3', ['above PDH', 'inside PD', 'below PDL']), ('strong', ['up >0.4 ADR since 18:00', 'flat', 'down >0.4 ADR']), ('mo3', ['discount', 'middle', 'premium'])):
        for g in grps:
            for t in ('newHi', 'newLo'):
                x = R[col][g][t]; vs.append(pc(x['v']) if x['n'] >= 6 else '-1'); vh.append('1' if x['held'] else '0')
    for col, grps in (('dmo3', ['over MO >1 ADR', 'within 1 ADR', 'under MO >1 ADR']), ('vix3', ['VIX >10% over its 20d avg', 'VIX near avg', 'VIX >10% under']), ('wk3', ['week up >0.5 ADR into NFP', 'week flat', 'week down >0.5 ADR'])):
        for g in grps:
            x = R[col][g]['postRng']; vs.append(f2(x['v'])); vh.append('1' if x['held'] else '0')
    assert len(vs) == 57 and len(vh) == 57
    return ','.join(vs), ''.join(vh)
def build_hollow(sym):
    W, F = S['wk'][sym], S['fa'][sym]; vs, vh = [], []
    for t in ('m_am', 'rthRng', 'settleRng', 'nRng'):
        for z in range(3):
            med, p80, h = W[t][z]; vs += [f2(med), f2(p80)]; vh += ['1' if h['held'] else '0'] * 2
    for col, grps in (('pd3', ['above PDH', 'inside PD', 'below PDL']), ('strong', ['up >0.4 ADR since 18:00', 'flat', 'down >0.4 ADR']), ('mo3', ['discount', 'middle', 'premium'])):
        for g in grps:
            for t in ('newHi', 'newLo'):
                x = W[col][g][t]; vs.append(pc(x['v'])); vh.append('1' if x['held'] else '0')
    for col, grps in (('dmo3', ['over MO >1 ADR', 'within 1 ADR', 'under MO >1 ADR']), ('vix3', ['VIX >10% over its 20d avg', 'VIX near avg', 'VIX >10% under'])):
        for g in grps:
            x = W[col][g]['rthRng']; vs.append(f2(x['v'])); vh.append('1' if x['held'] else '0')
    for t in ('ce10', 'gapFill'):
        for g in ['gap up >0.25 ADR', 'small gap', 'gap down >0.25 ADR']:
            x = W['gap3'][g][t]; vs.append(pc(x['v'])); vh.append('1' if x['held'] else '0')
    for g in ['Monday', 'Tuesday', 'Wednesday', 'Thursday']:
        x = W['dow3'][g]['ce10']; vs.append(pc(x['v'])); vh.append('1' if x['held'] else '0')
    assert len(vs) == 58
    for t in ('m_am', 'rthRng', 'nRng'):
        for z in range(3):
            med, p80, h = F[t][z]; vs += [f2(med), f2(p80)]; vh += ['1' if h['held'] else '0'] * 2
    for col, grps, ts in (('pd3', ['above PDH', 'inside PD', 'below PDL'], ('newHi', 'newLo')), ('strong', ['up >0.4 ADR since 18:00', 'flat', 'down >0.4 ADR'], ('newHi', 'newLo')),
                          ('mo3', ['discount', 'middle', 'premium'], ('takeFH', 'takeFL'))):
        for g in grps:
            for t in ts:
                x = F[col][g][t]; vs.append(pc(x['v']) if x['n'] >= 6 else '-1'); vh.append('1' if x['held'] else '0')
    for g in ['VIX >10% over its 20d avg', 'VIX near avg', 'VIX >10% under']:
        x = F['vix3'][g]['rthRng']; vs.append(f2(x['v'])); vh.append('1' if x['held'] else '0')
    for t in ('gapFill', 'ce50'):
        for g in ['gap up >0.25 ADR', 'small gap', 'gap down >0.25 ADR']:
            x = F['gap3'][g][t]; vs.append(pc(x['v'])); vh.append('1' if x['held'] else '0')
    assert len(vs) == 103, len(vs)
    return ','.join(vs), ''.join(vh)
OUT = {'cero': {s: build_cero(s) for s in ('NQ', 'ES')}, 'hollow': {s: build_hollow(s) for s in ('NQ', 'ES')}}
json.dump(OUT, open('data.json', 'w'), indent=1)
for m in OUT:
    for s in OUT[m]: print(m, s, OUT[m][s][1], OUT[m][s][0][:120])
