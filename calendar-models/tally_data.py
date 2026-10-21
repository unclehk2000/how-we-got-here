"""Per-event-day records for the event card's tally mode, NQ and ES, 2018 → data end.
td  = trading-day close vs its 18:00 open (+1 / −1 / 0)
rth = 16:14 close vs 09:30 open (0 when missing)
gap = 09:30 open − prior trading day's 16:14 close, points (empty when either side is missing) and %.
Trading days come from the day tables; days the 1-minute files miss (NQ Jan–Feb 2026, 6–9 Apr 2026) fall back to the
daily continuous file for the trading-day direction and to whatever 1-minute bars exist for the RTH fields.
Also writes the VIX range-factor centring constants. Writes tally.json."""
import pandas as pd, numpy as np, json, sys
sys.path.insert(0, '/home/claude/hm')
from events import CPI, NFP, FOMC
OUT = {}
for root in ('NQ', 'ES'):
    b = pd.read_pickle(f'/home/claude/t3/bars_{root}_all.pkl'); b = b[['ts', 'Open', 'Close', 'tday', 'hm']]
    dl = pd.read_csv(f'/mnt/user-data/uploads/nq_es_rty_daily_task2_1/continuous/{root}_continuous.csv', parse_dates=['Date']).set_index('Date')
    D = pd.read_pickle(f'days_{root}.pkl'); T = D[D.anchor == 'TD'].set_index('tday')
    cal = b.ts.dt.normalize()
    r_open = b[(b.hm == 930) & (cal == b.tday)].groupby('tday').Open.first()
    r_close = b[(b.hm == 1614) & (cal == b.tday)].groupby('tday').Close.last()
    tdays = sorted(set(b.tday.unique()) | set(dl.index[dl.index >= '2018-01-01']))
    tdays = [pd.Timestamp(t) for t in tdays if pd.Timestamp(t).dayofweek < 5]
    prev = {tdays[i]: tdays[i - 1] for i in range(1, len(tdays))}
    end = min(b.tday.max(), dl.index.max())
    # agreement of the daily file's open → close direction with the 1-minute trading day, where both exist
    j = T[['O', 'C']].join(dl[['Open', 'Close']], how='inner')
    agree = (np.sign(j.C - j.O) == np.sign(j.Close - j.Open)).mean()
    print(f'{root}: daily file vs 1-minute trading-day direction agree on {agree * 100:.1f}% of {len(j)} days')
    sets = dict(CPI=set(CPI), NFP=set(NFP), FOMC=set(FOMC))
    tset = {t: i for i, t in enumerate(tdays)}
    sets['POST'] = {tdays[tset[pd.Timestamp(d)] + 1] for d in FOMC if pd.Timestamp(d) in tset and tset[pd.Timestamp(d)] + 1 < len(tdays)}
    R = OUT.setdefault(root, {})
    for ev, S in sets.items():
        recs = []
        for d in sorted(pd.Timestamp(x) for x in S):
            if d < pd.Timestamp('2018-01-02') or d > end: continue
            if d in T.index: td = int(np.sign(T.loc[d, 'C'] - T.loc[d, 'O']))
            elif d in dl.index: td = int(np.sign(dl.loc[d, 'Close'] - dl.loc[d, 'Open']))
            else: continue
            ro, rc = r_open.get(d, np.nan), r_close.get(d, np.nan)
            rth = int(np.sign(rc - ro)) if np.isfinite(ro) and np.isfinite(rc) else 0
            pc = r_close.get(prev.get(d), np.nan)
            gap = round(float(ro - pc), 2) if np.isfinite(ro) and np.isfinite(pc) else None
            gp = round(float((ro / pc - 1) * 100), 3) if gap is not None else None
            recs.append(dict(d=int(d.strftime('%Y%m%d')), td=td, rth=rth, gap=gap, gp=gp))
        R[ev] = recs
        last = recs[-12:]
        print(f'   {ev}: {len(recs)} days to {recs[-1]["d"]} · last 12 TD ▲{sum(r["td"] > 0 for r in last)} ▼{sum(r["td"] < 0 for r in last)} · gaps missing {sum(r["gap"] is None for r in recs)}')
    R['end'] = int(end.strftime('%Y%m%d'))
    # VIX range factor centring: training means (2018–24)
    M = pd.read_pickle(f'/home/claude/mac/macro_{root}.pkl'); M = M[M.year <= 2024]
    R['ivrv_mean'] = float(M.ivrv.mean()); R['vspike_mean'] = float(M.vspike.mean())
    print(f'   ivrv mean {R["ivrv_mean"]:.3f} · vspike mean {R["vspike_mean"]:.3f}')
json.dump(OUT, open('tally.json', 'w'))
