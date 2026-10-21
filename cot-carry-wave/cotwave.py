import warnings; warnings.filterwarnings('ignore')
"""Weekly framing report: COT travelling-wave readings for NQ, ES, YM, RTY (+ price wave where prices exist).
Run after each Friday COT release: python3 cotwave.py"""
import pandas as pd, numpy as np
from panel import cot
from features import price_frame
from wave import fit
def reading(x,W,T):
    o=fit(np.asarray(x,float),W=W,Tgrid=T)
    th,Tp,A,r2,proj=o['theta'][-1],o['T'][-1],o['A'][-1],o['r2'][-1],o['proj'][-1]
    w=2*np.pi/Tp
    to_crest=((np.pi/2-th)%(2*np.pi))/w; to_trough=((3*np.pi/2-th)%(2*np.pi))/w
    stage=['rising, above mid','past crest, falling','falling, below mid','past trough, rising'][int(th//(np.pi/2))%4]
    return dict(period_w=str(int(Tp))+('*' if Tp in (min(T),max(T)) else ''),amp=round(A,2),phase_deg=int(np.degrees(th)),osc=round(np.sin(th),2),stage=stage,
                proj_1w=round(proj,2),wks_to_crest=round(to_crest,1),wks_to_trough=round(to_trough,1),fit_r2=round(r2,2))
rows=[]; last=None
for m in ['NQ','ES','YM','RTY']:
    c=cot(m); last=c.report_date.max()
    for g in ['am','lev']:
        rows.append(dict(mkt=m,series=('asset managers' if g=='am' else 'leveraged funds')+' net %OI',now=round(c[g+'_net'].iloc[-1],1),**reading(c[g+'_net'].values,52,range(8,53))))
    w=price_frame(m)
    if w is not None and w.lp_fit.notna().tail(52).all():
        rows.append(dict(mkt=m,series=f'price ({w.attrs["src"]}, to {w.index[-1].end_time.date()})',now=np.nan,**reading(w.lp_fit.values,52,range(8,53))))
R=pd.DataFrame(rows)
pd.set_option('display.width',220)
print(f'COT report as of {last.date()} (released the following Friday 15:30 ET)\n')
print(R.to_string(index=False)); print('* period sits on the edge of the search band: no clean cycle inside 8-52 weeks')
c=pd.read_csv('/mnt/user-data/outputs/COT_TFF_NQ_ES_RTY_YM_2015_2026.csv',parse_dates=['report_date'])
c['am']=(c.am_long-c.am_short)/c.open_interest*100
p=c.pivot(index='report_date',columns='market',values='am').dropna()
sp=p.NQ-p.RTY
print('\nNQ minus RTY asset-manager net %%OI: %.1f pts (52w range %.1f to %.1f; z vs 52w %.2f)'%(sp.iloc[-1],sp.tail(52).min(),sp.tail(52).max(),(sp.iloc[-1]-sp.tail(52).mean())/sp.tail(52).std()))
R.to_csv('cotwave_latest.csv',index=False)
