"""Pine logic for 'high / low in', run at 1-minute resolution on the 2025–26 test days (NQ + ES), checked against what
actually happened later that day. Uses the Pine constants and a port of the Pine normal-CDF approximation."""
import os, sys; sys.path[:0] = [os.path.dirname(os.path.dirname(os.path.abspath(__file__)))]; from config import *
from common import *
from scipy.stats import norm
VREM=np.array([0.968,0.952,0.930,0.906,0.892,0.883,0.869,0.855,0.835,0.802,0.776,0.757,0.734,0.707,0.634,0.528,0.412,0.332,0.271,0.206,0.135,0.031,0.0]); KAPPA=0.655
def ncdf(x):
    z=np.abs(x); t=1/(1+0.2316419*z)
    p=1-0.3989422804*np.exp(-0.5*z*z)*t*(0.319381530+t*(-0.356563782+t*(1.781477937+t*(-1.821255978+t*1.330274429))))
    return np.where(x>=0,p,1-p)
xs=np.linspace(-6,6,20001); print('max |pine nCdf − exact|: %.2e'%np.abs(ncdf(xs)-norm.cdf(xs)).max())
out=[]
for s in ['NQ','ES']:
    S=pd.read_pickle(f'slots2_{s}.pkl'); D=pd.read_pickle(f'F_{s}.pkl'); D['har']=wf_har(D)
    days=S.index[S.index.year>=2025]
    b=pd.read_pickle(f'bars_{s}_all.pkl'); b=b[b.tday.isin(days)].sort_values('ts').reset_index(drop=True)
    b=b.join(D.har,on='tday')
    g=b.groupby('tday',sort=False)
    b['tO']=g.Open.transform('first'); b['tHi']=g.High.cummax(); b['tLo']=g.Low.cummin()
    # max / min of everything after this bar (same day)
    b['futH']=g.High.transform(lambda x:x[::-1].cummax()[::-1].shift(-1)); b['futL']=g.Low.transform(lambda x:x[::-1].cummin()[::-1].shift(-1))
    b['yH']=(b.futH.isna()|(b.futH<=b.tHi)).astype(int); b['yL']=(b.futL.isna()|(b.futL>=b.tLo)).astype(int)
    jN=((b.ts.dt.hour-18)%24).values; fN=np.minimum(1.0,(b.ts.dt.minute.values+1)/60)
    vr=np.where(jN>22,0.0,np.where(jN==0,1-(1-VREM[0])*fN,VREM[np.clip(jN-1,0,22)]+(VREM[np.clip(jN,0,22)]-VREM[np.clip(jN-1,0,22)])*fN))
    sg=KAPPA*np.exp(b.har.values)*np.sqrt(np.maximum(vr,1e-12))
    b['pH']=np.where(vr<=1e-6,1.0,2*ncdf(100*(b.tHi-b.Close)/b.tO/sg)-1); b['pL']=np.where(vr<=1e-6,1.0,2*ncdf(100*(b.Close-b.tLo)/b.tO/sg)-1)
    b['hh']=b.ts.dt.hour*2+(b.ts.dt.minute>=30); b['sym']=s
    out.append(b[['sym','tday','ts','hh','pH','pL','yH','yL']])
E=pd.concat(out)
L=pd.concat([E.rename(columns={'pH':'P','yH':'y'})[['sym','hh','P','y']],E.rename(columns={'pL':'P','yL':'y'})[['sym','hh','P','y']]])
L=L.dropna()
L['B']=L.groupby(['sym','hh']).y.transform('mean')    # base rate by half-hour, in-sample (generous to the baseline)
for s in ['NQ','ES']:
    d=L[L.sym==s]; print(f"{s}: {len(d)//2:,} minute bars · Brier base rate {((d.y-d.B)**2).mean():.4f} · Pine formula {((d.y-d.P)**2).mean():.4f} → {100*(1-((d.y-d.P)**2).mean()/((d.y-d.B)**2).mean()):.1f}% sharper")
L['bin']=pd.cut(L.P,[-1e-9,.1,.2,.3,.4,.5,.6,.7,.8,.9,.95,1.0])
c=L.groupby('bin',observed=True).agg(n=('y','size'),pred=('P','mean'),act=('y','mean'))
print('calibration, every minute 2025–26, NQ+ES (predicted % / actual %):'); print(' '.join(f'{r.pred*100:.0f}/{r.act*100:.0f}' for _,r in c.iterrows()))
E.to_pickle('emul_ext_rows.pkl')
