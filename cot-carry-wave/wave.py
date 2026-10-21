"""Causal travelling-sinusoid fit.
At every week t, fit x[t-W+1..t] = c0 + c1*s + a*sin(w s) + b*cos(w s) by weighted least squares
(weights halve every h weeks back), scanning the period T over a grid and keeping the best fit.
Only data up to t is used, so the phase at t is tradable."""
import numpy as np
from numpy.lib.stride_tricks import sliding_window_view as swv

def fit(x, W=52, Tgrid=range(8,53), h=None, trend=True):
    x=np.asarray(x,float); n=len(x)
    out={k:np.full(n,np.nan) for k in ['T','A','theta','r2','osc','vel','proj']}
    if n<W: return out
    X=swv(x,W)                                    # (n-W+1, W) windows ending at t=W-1..n-1
    ok=~np.isnan(X).any(1)
    s=np.arange(W,dtype=float)
    wts=np.ones(W) if h is None else 0.5**((W-1-s)/h)
    base=[np.ones(W)]+([s/W] if trend else [])
    Bb=np.column_stack(base)
    # baseline (trend only) residual for R2 of the sinusoid part
    def wls(B):
        BW=B*wts[:,None]; M=np.linalg.pinv(B.T@BW); C=(X@BW)@M.T   # (m, k)
        R=X-C@B.T; return C,(R**2*wts).sum(1)
    _,ss0=wls(Bb)
    best=np.full(len(X),np.inf); bestT=np.zeros(len(X)); ba=np.zeros(len(X)); bb=np.zeros(len(X))
    for T in Tgrid:
        w=2*np.pi/T
        B=np.column_stack(base+[np.sin(w*s),np.cos(w*s)])
        C,ss=wls(B)
        m=ss<best; best[m]=ss[m]; bestT[m]=T; ba[m]=C[m,-2]; bb[m]=C[m,-1]
    w=2*np.pi/bestT
    A=np.hypot(ba,bb); phi=np.arctan2(bb,ba)
    theta=np.mod(w*(W-1)+phi,2*np.pi)
    r2=1-best/np.where(ss0>0,ss0,np.nan)
    idx=np.arange(W-1,n)
    for k,v in dict(T=bestT,A=A,theta=theta,r2=r2,osc=np.sin(theta),vel=np.cos(theta),
                    proj=A*(np.sin(theta+w)-np.sin(theta))).items():
        v=v.astype(float); v[~ok]=np.nan; out[k][idx]=v
    return out

if __name__=='__main__':
    # sanity: pure sine with noise -> recover period and phase
    rng=np.random.default_rng(0); t=np.arange(300); x=3*np.sin(2*np.pi*t/20+0.7)+0.05*t+rng.normal(0,0.5,300)
    o=fit(x,W=60,Tgrid=range(8,41))
    print('T median',np.nanmedian(o['T']),'r2',np.nanmedian(o['r2']).round(2))
    true=np.mod(2*np.pi*t/20+0.7,2*np.pi)
    err=np.angle(np.exp(1j*(o['theta']-true)))
    print('phase err median abs (rad)',np.nanmedian(np.abs(err)).round(3))
