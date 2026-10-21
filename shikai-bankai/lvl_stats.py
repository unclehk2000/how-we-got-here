"""Range levels from the session's last extreme (25 / 37.5 / 50%): how often later trading reaches them.
London 02:00–04:59 → from 05:00; Asia 18:00–23:59 → from 00:00. NQ, ES, RTY 1-minute 2018–26."""
import pandas as pd, numpy as np
rows = []
for S in ('NQ', 'ES', 'RTY'):
    B = pd.read_pickle(f'/home/claude/kyw/bars_{S}_all.pkl')
    B['m'] = (B.hm // 100) * 60 + B.hm % 100
    for d, x in B.groupby('tday'):
        if x.Contract.nunique() > 1:
            continue
        for nm, a, b, after in (('London', 120, 300, 300), ('Asia', 1080, 1440, 0)):
            s = x[(x.m >= a) & (x.m < b)]
            if len(s) < 100:
                continue
            H, L = s.High.max(), s.Low.min()
            tH, tL = s.High.idxmax(), s.Low.idxmin()
            down = tH < tL or (tH == tL and s.Close.iloc[-1] < s.Open.iloc[0])
            R = H - L
            if R <= 0:
                continue
            if nm == 'London':
                aft = x[(x.m >= 300) & (x.m < 1020)]
            else:
                aft = x[(x.m < 1020) & (x.m < 1080)]
            a11 = aft[aft.m < 660]
            r = dict(sym=S, tday=d, sess=nm, down=down, R=R)
            for k in (0.25, 0.375, 0.5):
                lv = L + k * R if down else H - k * R
                hit = aft[(aft.High >= lv) & (aft.Low <= lv)]
                r[f't{k}'] = hit.index[0] if len(hit) else None
                r[f'h17_{k}'] = len(hit) > 0
                h11 = a11[(a11.High >= lv) & (a11.Low <= lv)]
                r[f'h11_{k}'] = len(h11) > 0
            # body 25% (old definition) for comparison
            o, c = s.Open.iloc[0], s.Close.iloc[-1]
            bt, bb = max(o, c), min(o, c); br = bt - bb
            q = (bt - 0.25 * br if c >= o else bb + 0.25 * br) if br > 0 else (bt + bb) / 2
            r['h17_body25'] = len(aft[(aft.High >= q) & (aft.Low <= q)]) > 0
            rows.append(r)
R = pd.DataFrame(rows)
R['half'] = np.where(R.tday < '2025-01-01', '18-24', '25-26')
R.to_pickle('/home/claude/sb/lvl_rows.pkl')
cols = ['h11_0.25', 'h11_0.375', 'h11_0.5', 'h17_0.25', 'h17_0.375', 'h17_0.5', 'h17_body25']
print(R.groupby('sess')[cols].mean().mul(100).round(1).to_string())
print(R.groupby(['sess', 'half'])[cols].mean().mul(100).round(1).to_string())
print(R.groupby(['sess', 'sym'])[cols].mean().mul(100).round(1).to_string())
print(R.groupby('sess').size())
