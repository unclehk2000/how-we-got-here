"""Pine 'high / low in' logic run at 1-minute resolution on RTY 2025–26, with the v12 constants (NQ+ES variance profile,
kappa 0.655) and with an RTY variance profile. Same port as emul_ext.py. Also prints the NQ+ES variance profile by period
next to RTY's, to show whether RTY's earlier finish is structural."""
import os, sys; sys.path[:0] = [os.path.dirname(os.path.dirname(os.path.abspath(__file__)))]; from config import *
from common import *
VREM12 = np.array([0.968,0.952,0.930,0.906,0.892,0.883,0.869,0.855,0.835,0.802,0.776,0.757,0.734,0.707,0.634,0.528,0.412,0.332,0.271,0.206,0.135,0.031,0.0])
rw = pd.read_pickle('rty_rw.pkl'); VR = rw['vR']; KR = rw['kR']
def ncdf(x):
    z = np.abs(x); t = 1 / (1 + 0.2316419 * z)
    p = 1 - 0.3989422804 * np.exp(-0.5 * z * z) * t * (0.319381530 + t * (-0.356563782 + t * (1.781477937 + t * (-1.821255978 + t * 1.330274429))))
    return np.where(x >= 0, p, 1 - p)
S = pd.read_pickle('slots2_RTY.pkl'); D = pd.read_pickle('F_RTY.pkl'); D['har'] = wf_har(D)
days = S.index[S.index.year >= 2025]
b = pd.read_pickle('bars_RTY_all.pkl'); b = b[b.tday.isin(days)].sort_values('ts').reset_index(drop=True).join(D.har, on='tday')
g = b.groupby('tday', sort=False)
b['tO'] = g.Open.transform('first'); b['tHi'] = g.High.cummax(); b['tLo'] = g.Low.cummin()
b['futH'] = g.High.transform(lambda x: x[::-1].cummax()[::-1].shift(-1)); b['futL'] = g.Low.transform(lambda x: x[::-1].cummin()[::-1].shift(-1))
b['yH'] = (b.futH.isna() | (b.futH <= b.tHi)).astype(int); b['yL'] = (b.futL.isna() | (b.futL >= b.tLo)).astype(int)
jN = ((b.ts.dt.hour - 18) % 24).values; fN = np.minimum(1.0, (b.ts.dt.minute.values + 1) / 60)
b['hh'] = b.ts.dt.hour * 2 + (b.ts.dt.minute >= 30)
def run(VREM, KAP, tag):
    vr = np.where(jN > 22, 0.0, np.where(jN == 0, 1 - (1 - VREM[0]) * fN, VREM[np.clip(jN - 1, 0, 22)] + (VREM[np.clip(jN, 0, 22)] - VREM[np.clip(jN - 1, 0, 22)]) * fN))
    sg = KAP * np.exp(b.har.values) * np.sqrt(np.maximum(vr, 1e-12))
    pH = np.where(vr <= 1e-6, 1.0, 2 * ncdf(100 * (b.tHi - b.Close) / b.tO / sg) - 1); pL = np.where(vr <= 1e-6, 1.0, 2 * ncdf(100 * (b.Close - b.tLo) / b.tO / sg) - 1)
    L = pd.concat([pd.DataFrame({'hh': b.hh, 'P': pH, 'y': b.yH, 'side': 'H'}), pd.DataFrame({'hh': b.hh, 'P': pL, 'y': b.yL, 'side': 'L'})]).dropna()
    L['B'] = L.groupby(['side', 'hh']).y.transform('mean')
    rth = L.hh.between(19, 31)                               # 09:30–15:59
    sk = lambda m: 100 * (1 - ((L.y - L.P) ** 2)[m].mean() / ((L.y - L.B) ** 2)[m].mean())
    print(f'{tag}: {len(b):,} minute bars · skill vs base rate {sk(L.index == L.index):.1f}% (09:30–16:00 {sk(rth):.1f}%) · '
          f'high side predicted {L[L.side == "H"].P.mean() * 100:.1f}% / actual {L[L.side == "H"].y.mean() * 100:.1f}% · low side {L[L.side == "L"].P.mean() * 100:.1f}% / {L[L.side == "L"].y.mean() * 100:.1f}%')
    L['bin'] = pd.cut(L.P, [-1e-9, .1, .2, .3, .4, .5, .6, .7, .8, .9, .95, 1.0])
    c = L.groupby('bin', observed=True).agg(pred=('P', 'mean'), act=('y', 'mean'))
    print('   calibration (predicted / actual %): ' + ' '.join(f'{r.pred * 100:.0f}/{r.act * 100:.0f}' for _, r in c.iterrows()))
    cr = L[rth].groupby(pd.cut(L[rth].P, [-1e-9, .2, .4, .6, .8, 1.0]), observed=True).agg(pred=('P', 'mean'), act=('y', 'mean'))
    print('   09:30–16:00 only: ' + ' '.join(f'{r.pred * 100:.0f}/{r.act * 100:.0f}' for _, r in cr.iterrows()))
run(VREM12, 0.655, 'RTY 2025–26 · v12 constants (NQ+ES variance profile, κ 0.655)')
run(VR, KR, f'RTY 2025–26 · RTY variance profile, κ {KR:.3f}')
# is RTY's earlier finish structural? NQ+ES vs RTY by period, share still to come at 11:00 / 12:00 / 13:00 / 14:00 / 15:00
H30 = {s: pd.read_pickle(f'slots30_{s}.pkl') for s in ['NQ', 'ES', 'RTY']}
def vprof(S):
    lc = np.log(S[[f'c{k}' for k in range(46)]].values); r = np.diff(np.c_[np.zeros(len(S)), lc], axis=1); return np.nanmean(r ** 2, axis=0)
rem = lambda v: (1 - np.cumsum(v) / v.sum())[1::2]
print('\nshare still to come at 11:00 12:00 13:00 14:00 15:00')
for a, z in [(2018, 2020), (2021, 2022), (2023, 2024), (2025, 2026)]:
    yr = lambda S: S[(S.index.year >= a) & (S.index.year <= z)]
    ne = rem(np.mean([vprof(yr(H30[s])) for s in ['NQ', 'ES']], axis=0)); r = rem(vprof(yr(H30['RTY'])))
    print(f'  {a}–{str(z)[2:]}  NQ+ES ' + ' '.join(f'{ne[j]:.2f}' for j in [16, 17, 18, 19, 20]) + '   RTY ' + ' '.join(f'{r[j]:.2f}' for j in [16, 17, 18, 19, 20]))
