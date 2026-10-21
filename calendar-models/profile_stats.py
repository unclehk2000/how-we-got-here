"""Model profiles on 2018–2026 (full), with 2018–24 vs 2025–26. Prints a readable report and saves prof_stats.json."""
import pandas as pd, numpy as np, json
from scipy import stats
OUT = {}; lines = []
def P_(*a):
    s = ' '.join(str(x) for x in a); print(s); lines.append(s)
def rate(s): s = s.dropna(); return (s.mean(), len(s))
def fmt(v): return '—' if v is None or not np.isfinite(v[0]) else f'{v[0]*100:.0f}% (n{v[1]})'
for root in ('NQ', 'ES'):
    P = pd.read_pickle(f'prof_{root}.pkl'); P['scale'] = P.adr * P.tdO
    for k in ('asia', 'london', 'nyam', 'lunch', 'pm', 'pre', 'stmt', 'presser', 'settle', 'rthR', 'nextR'): P[k + '_n'] = P[k] / P.scale
    P['net_n'] = (P.rthC - P.rthO) / P.scale
    S = {'full': P.year > 0, 'train': P.year <= 2024, 'test': P.year >= 2025}
    R = OUT.setdefault(root, {})
    def both(mask_fn, f):
        return {k: f(P[m & mask_fn(P)]) for k, m in S.items()}
    def sess(ty, base, cols):
        res = {}
        for k, m in S.items():
            a = P[m & ty(P)]; z = P[m & base(P)]
            res[k] = {c: float(a[c + '_n'].median() / z[c + '_n'].median()) for c in cols}
        return res
    NORM = lambda d: d.type == 'NORMAL'
    SES = ['asia', 'london', 'nyam', 'lunch', 'pm']
    P_('=' * 100); P_(root)
    for ty in ('NFP', 'CPI', 'FOMC', 'PRE', 'POST'):
        T = lambda d, ty=ty: d.type == ty
        s = sess(T, NORM, SES + (['pre', 'stmt', 'presser'] if ty == 'FOMC' else []) + ['settle'])
        R[ty] = dict(n={k: int((m & T(P)).sum()) for k, m in S.items()}, sess=s)
        P_(f'\n{ty}: n {R[ty]["n"]}')
        for k in ('full', 'train', 'test'): P_(f'   sessions {k:5s}: ' + ' · '.join(f'{c} {v*100:.0f}%' for c, v in s[k].items()))
        def stat(name, f, base=True):
            v = {k: f(P[m & T(P)]) for k, m in S.items()}; b = f(P[S['full'] & NORM(P)]) if base else None
            R[ty][name] = dict(v={k: [float(x[0]), x[1]] for k, x in v.items()}, base=[float(b[0]), b[1]] if b else None)
            P_(f'   {name:34s} full {fmt(v["full"])} · 2018–24 {fmt(v["train"])} · 2025–26 {fmt(v["test"])}' + (f' · normal {fmt(b)}' if b else ''))
        if ty in ('NFP', 'CPI'):
            stat('stage2 opposes stage1', lambda d: rate(pd.Series(np.where((d.s1 * d.s2) != 0, (np.sign(d.s1) != np.sign(d.s2)).astype(float), np.nan))))
            stat('next day continues', lambda d: rate(pd.Series(np.where((d.dir * d.nextDir) != 0, (d.dir == d.nextDir).astype(float), np.nan))))
            stat('gap full fill in RTH', lambda d: rate((d.tFill >= 0).astype(float).where(d.gapPct.notna())))
            stat('gap 50% by 10:00', lambda d: rate(((d.tCE >= 0) & (d.tCE < 600)).astype(float).where(d.gapPct.notna())))
            stat('RTH low in 09:30–10:00', lambda d: rate((d.tLr < 600).astype(float).where(d.tLr.notna())))
            stat('RTH high in 09:30–10:00', lambda d: rate((d.tHr < 600).astype(float).where(d.tHr.notna())))
            for w, lab in (('sb', '9:50–10:10 reverses the trend'), ('lun', '11:30–13:30 reverses the trend'), ('co', '15:15–15:45 reverses the trend')):
                stat(lab, lambda d, w=w: rate(d[f'{w}_rev']))
            if ty == 'CPI':
                stat('larger move opposite first sweep', lambda d: rate(pd.Series(np.where(d['first'].fillna(0) != 0, ((d['first'] == 1) & (d.bigUp == 0) | (d['first'] == -1) & (d.bigUp == 1)).astype(float), np.nan))))
        if ty == 'FOMC':
            stat('press conf. opposes statement', lambda d: rate(pd.Series(np.where((d.st * d.pr) != 0, (np.sign(d.st) != np.sign(d.pr)).astype(float), np.nan))))
            stat('gap full fill in RTH', lambda d: rate((d.tFill >= 0).astype(float).where(d.gapPct.notna())))
            stat('RTH high after 14:00', lambda d: rate((d.tHr >= 840).astype(float).where(d.tHr.notna())))
            stat('RTH low after 14:00', lambda d: rate((d.tLr >= 840).astype(float).where(d.tLr.notna())))
            stat('next day continues', lambda d: rate(pd.Series(np.where((d.dir * d.nextDir) != 0, (d.dir == d.nextDir).astype(float), np.nan))))
            # tight vs wide Asia: Asia range ÷ ADR at or below the normal-day median
            med = P[S['full'] & NORM(P)].asia_n.median()
            for k, m in S.items():
                a = P[m & T(P)]; t_ = a[a.asia_n <= med]; w_ = a[a.asia_n > med]
                R[ty].setdefault('asia', {})[k] = dict(tight=[float(t_.rthR_n.median()), len(t_)], wide=[float(w_.rthR_n.median()), len(w_)])
                P_(f'   asia tight/wide {k:5s}: RTH range ÷ ADR tight {t_.rthR_n.median():.2f} (n{len(t_)}) vs wide {w_.rthR_n.median():.2f} (n{len(w_)})')
            R[ty]['asiaMed'] = float(med)
            stat('RTH range ÷ ADR (median)', lambda d: (float(d.rthR_n.median()), len(d)), base=True)
            # full bringer: what the next day does with FOMC day's RTH high / low
            stat('next day takes FOMC high', lambda d: rate((d.nextH > d.rthH).astype(float).where(d.nextH.notna())), base=False)
            stat('next day takes FOMC low', lambda d: rate((d.nextL < d.rthL).astype(float).where(d.nextL.notna())), base=False)
            stat('next day takes both', lambda d: rate(((d.nextH > d.rthH) & (d.nextL < d.rthL)).astype(float).where(d.nextH.notna())), base=False)
            for k, m in S.items():
                a = P[m & T(P)].dropna(subset=['rthR_n', 'nextR_n']); medR = P[S['full'] & T(P)].rthR_n.median()
                hi = a[a.rthR_n > medR].nextR_n.median(); lo = a[a.rthR_n <= medR].nextR_n.median(); r_ = stats.spearmanr(a.rthR_n, a.nextR_n)[0]
                R[ty].setdefault('fb', {})[k] = dict(rho=float(r_), hi=float(hi), lo=float(lo), med=float(medR))
                P_(f'   FOMC range → next day {k:5s}: Spearman {r_:.2f} · next-day range ÷ ADR after a big FOMC day {hi:.2f} vs small {lo:.2f}')
            # normal-day baselines for the same "takes the high/low" logic
            b = P[S['full'] & NORM(P)]
            R[ty]['takeBase'] = [float((b.nextH > b.rthH).mean()), float((b.nextL < b.rthL).mean()), float(((b.nextH > b.rthH) & (b.nextL < b.rthL)).mean())]
            P_(f'   normal days: next day takes the high {R[ty]["takeBase"][0]*100:.0f}% · low {R[ty]["takeBase"][1]*100:.0f}% · both {R[ty]["takeBase"][2]*100:.0f}%')
        if ty == 'PRE':
            stat('decision day takes D1 high', lambda d: rate((d.nextTdH > d.tdH).astype(float).where(d.nextTdH.notna())), base=False)
            stat('decision day takes D1 low', lambda d: rate((d.nextTdL < d.tdL).astype(float).where(d.nextTdL.notna())), base=False)
            stat('decision day takes both', lambda d: rate(((d.nextTdH > d.tdH) & (d.nextTdL < d.tdL)).astype(float).where(d.nextTdH.notna())), base=False)
            b = P[S['full'] & NORM(P)]
            R[ty]['takeBase'] = [float((b.nextTdH > b.tdH).mean()), float((b.nextTdL < b.tdL).mean()), float(((b.nextTdH > b.tdH) & (b.nextTdL < b.tdL)).mean())]
            P_(f'   normal days: next day takes the high {R[ty]["takeBase"][0]*100:.0f}% · low {R[ty]["takeBase"][1]*100:.0f}% · both {R[ty]["takeBase"][2]*100:.0f}%')
            stat('RTH range ÷ ADR (median)', lambda d: (float(d.rthR_n.median()), len(d)), base=True)
        if ty == 'POST':
            stat('RTH range ÷ ADR (median)', lambda d: (float(d.rthR_n.median()), len(d)), base=True)
            stat('up-close', lambda d: rate(d.up), base=True)
    # Hollow by weekday, against normal days of the same weekday
    R['HOLLOW'] = {}
    for dw, nm in enumerate(['Mon', 'Tue', 'Wed', 'Thu']):
        T = lambda d, dw=dw: (d.type == 'HOLLOW') & (d.dow == dw); B = lambda d, dw=dw: (d.type == 'NORMAL') & (d.dow == dw)
        s = sess(T, B, SES + ['settle'])
        H = R['HOLLOW'][nm] = dict(n={k: int((m & T(P)).sum()) for k, m in S.items()}, sess=s)
        P_(f'\nHOLLOW {nm}: n {H["n"]}')
        for k in ('full', 'train', 'test'): P_(f'   sessions {k:5s}: ' + ' · '.join(f'{c} {v*100:.0f}%' for c, v in s[k].items()))
        for name, f in (('trend day (|net| ≥ ½ range)', lambda d: rate(d.trend)), ('up-close', lambda d: rate(d.up)),
                        ('net ÷ ADR (mean)', lambda d: (float(d.net_n.mean()), len(d))), ('NWOG CE touched by today', lambda d: rate(d.nwogHit)),
                        ('gap 50% by 10:00', lambda d: rate(((d.tCE >= 0) & (d.tCE < 600)).astype(float).where(d.gapPct.notna())))):
            v = {k: f(P[m & T(P)]) for k, m in S.items()}; b = f(P[S['full'] & B(P)])
            H[name] = dict(v={k: [float(x[0]), x[1]] for k, x in v.items()}, base=[float(b[0]), b[1]])
            if 'mean' in name: P_(f'   {name:34s} full {v["full"][0]:+.3f} · 2018–24 {v["train"][0]:+.3f} · 2025–26 {v["test"][0]:+.3f} · normal {b[0]:+.3f}')
            else: P_(f'   {name:34s} full {fmt(v["full"])} · 2018–24 {fmt(v["train"])} · 2025–26 {fmt(v["test"])} · normal {fmt(b)}')
json.dump(OUT, open('prof_stats.json', 'w'), indent=1)
open('prof_stats.txt', 'w').write('\n'.join(lines))
