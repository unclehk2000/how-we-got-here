"""NY AM (09:30-10:59) Sōgyo dataset: pre-open context features + NY AM wall outcomes.
Times ET. tday D = session whose RTH is on date D (bars from 18:00 the evening before)."""
import pandas as pd, numpy as np, pickle, sys
def seg(x,a,b):                      # bars with hm in [a,b]
    return x[(x.hm>=a)&(x.hm<=b)]
def rng(x): return (x.High.max(),x.Low.min()) if len(x) else (np.nan,np.nan)
def race(h,l,c,i,O,T,Z,n):
    up=O>T
    for j in range(i+1,n):
        a=(h[j]>=O) if up else (l[j]<=O); t=(l[j]<=T) if up else (h[j]>=T)
        if a and t: return 0.5,1
        if a: return 1.0,1
        if t: return 0.0,1
    return (1.0 if (c[n-1]-Z)*(O-Z)>0 else 0.0),0
def build(m):
    b=pd.read_pickle(f'bars_{m}.pkl'); G={d:x for d,x in b.groupby('tday')}
    rth,paths=pickle.load(open(f'twin_{m}.pkl','rb')); S=pd.read_pickle(f'states_{m}.pkl')
    days=sorted(G); prev={days[i]:days[i-1] for i in range(1,len(days))}
    S['atr14']=S.rng.shift().rolling(14,min_periods=10).mean()
    out=[]
    for d,r in rth.iterrows():
        x=G[d]; p=prev.get(d)
        if p is None or p not in G or d not in S.index: continue
        xp=G[p]; O=r.O; Cm=(r.C1+r.C2)/2; gap=O-Cm
        if np.sign(O-r.C1)!=np.sign(O-r.C2) or abs(gap)/O<0.0010: continue
        g=np.sign(gap); Z=(r.CE1+r.CE2)/2; atr=S.atr14.get(d)
        if not np.isfinite(atr): continue
        f=dict(day=d,g=g,O=O,Z=Z,Cm=Cm,atr=atr)
        f['gap_atr']=abs(gap)/atr; f['gap_pct']=100*abs(gap)/O
        f['zone_w_atr']=abs(r.CE2-r.CE1)/atr
        f['settle_toward']=float(abs(r.C2-O)<abs(r.C1-O))
        # true day open
        t0=x[x.hm==0]; TDO=t0.Open.iloc[0] if len(t0) else np.nan
        f['open_vs_tdo']=g*(O-TDO)/atr                         # >0: open is further in the gap direction than TDO
        f['tdo_between']=float(np.isfinite(TDO) and (min(O,Z)<TDO<max(O,Z)))
        f['zone_tdo_dist']=abs(Z-TDO)/atr
        # CBDR 14:00-20:00 ET of the prior day
        cb=pd.concat([seg(xp,1400,1659),seg(x,1800,1959)]); ch,cl=rng(cb)
        f['cbdr_atr']=(ch-cl)/atr
        f['zone_in_cbdr']=float(cl<=Z<=ch)
        f['zone_cbdr_sd']=((Z-cl)/(ch-cl) if g<0 else (ch-Z)/(ch-cl)) if ch>cl else np.nan   # position of zone vs CBDR in CBDR units
        # Asia 20:00-23:59, London 02:00-04:59, pre-open 05:00-09:29, overnight 18:00-09:29
        ah,al=rng(seg(x,2000,2359)); lh,ll=rng(seg(x,200,459)); on=pd.concat([seg(x,1800,2359),seg(x,0,929)]); oh,ol=rng(on)
        pre=seg(x,0,929)
        f['asia_atr']=(ah-al)/atr; f['on_atr']=(oh-ol)/atr
        f['ldn_swept_asia_hi']=float(lh>ah); f['ldn_swept_asia_lo']=float(ll<al)
        prth=paths.get(p)
        if prth is None:
            pr=seg(xp,930,1614); PDH,PDL=rng(pr)
        else:
            q=prth[prth.index<=1614]; PDH,PDL=q.High.max(),q.Low.min()
        f['on_swept_pdh']=float(oh>PDH); f['on_swept_pdl']=float(ol<PDL)
        f['zone_in_prev_range']=float(PDL<=Z<=PDH); f['open_in_prev_range']=float(PDL<=O<=PDH)
        pz=seg(x,700,929); f['zone_traded_0700']=float(len(pz)>0 and (pz.Low.min()<=Z<=pz.High.max()))
        f['on_mid_dist']=abs(Z-(oh+ol)/2)/atr
        f['on_trend']=g*(pre.Close.iloc[-1]-on.Open.iloc[0])/atr if len(pre) and len(on) else np.nan
        b7=seg(x,700,929); f['b79_atr']=(b7.High.max()-b7.Low.min())/atr if len(b7) else np.nan
        f['b79_dir']=g*(b7.Close.iloc[-1]-b7.Open.iloc[0])/atr if len(b7) else np.nan
        # NDOG: prior 16:59 close -> 18:00 open
        o18=x[x.hm==1800]; ndo=o18.Open.iloc[0] if len(o18) else np.nan
        ndce=(r.C2+ndo)/2; f['ndog_atr']=abs(ndo-r.C2)/atr; f['zone_ndog_ce_dist']=abs(Z-ndce)/atr
        # NWOG: Friday 16:59 close -> Sunday 18:00 open of this week
        mon=[k for k in days if k<=d and k>=d-pd.Timedelta(days=d.weekday()) ]
        if mon:
            wk0=mon[0]; pk=prev.get(wk0)
            if pk is not None and pk in G:
                fc=G[pk][G[pk].hm==1659]; so=G[wk0][G[wk0].hm==1800]
                if len(fc) and len(so):
                    a,bb=fc.Close.iloc[0],so.Open.iloc[0]; nce=(a+bb)/2
                    f['nwog_atr']=abs(bb-a)/atr; f['zone_nwog_ce_dist']=abs(Z-nce)/atr
                    since=pd.concat([G[k] for k in days if wk0<=k<d]+[seg(x,1800,2359),seg(x,0,929)])
                    f['nwog_unfilled']=float(not ((since.Low<=a)&(since.High>=a)).any())
        f['prev_state']=S.prev_state.get(d); f['dow']=d.weekday()
        pn=S.net.get(p) if p in S.index else np.nan; f['prev_day_with_gap']=float(np.sign(pn)==g) if np.isfinite(pn) else np.nan
        k=seg(x,825,829); k2=seg(x,830,834)
        f['news830']=(k2.High.max()-k2.Low.min())/atr if len(k2) else np.nan       # 08:30-08:34 range in ATR units
        # ---- NY AM outcomes ----
        ny=paths[d]; hm=ny.index.values; n=(hm<=1059).sum(); h,l,c=ny.High.values,ny.Low.values,ny.Close.values
        for fr,tag in [(0.5,'z'),(0.375,'d375'),(0.625,'d625')]:
            L=O+fr*(Cm-O); T=O+2*fr*(Cm-O)
            mm=np.where((l[:n]<=L)&(h[:n]>=L))[0]
            f[f'{tag}_touch']=float(len(mm)>0)
            if len(mm):
                v,res=race(h,l,c,mm[0],O,T,L,n); f[f'{tag}_hold']=v; f[f'{tag}_resolved']=res
                if tag=='z':
                    f['touch_min']=mm[0]
                    # 5-min wall: no 5-min close beyond the far edge of the zone for the rest of NY AM
                    far=min(r.CE1,r.CE2) if g>0 else max(r.CE1,r.CE2)
                    cl5=c[4:n:5]; idx5=np.arange(4,n,5); after=cl5[idx5>mm[0]]
                    f['wall5']=float(not (((far-after)>0).any() if g>0 else ((after-far)>0).any())) if len(after) else np.nan
                    # foothold trade: limit at Z, stop at 0.75 level, target the open, exit 10:59
                    stop=O+0.75*(Cm-O); ent=Z; res_t=None
                    for j in range(mm[0]+1,n):
                        hs=(l[j]<=stop) if g>0 else (h[j]>=stop); ht=(h[j]>=O) if g>0 else (l[j]<=O)
                        if hs: res_t=g*(stop-ent); break
                        if ht: res_t=g*(O-ent); break
                    if res_t is None: res_t=g*(c[n-1]-ent)
                    f['trade_ret']=100*res_t/O; f['trade_R']=res_t/abs(ent-stop)
        f['nyam_long']=100*(c[n-1]-O)/O
        out.append(f)
    return pd.DataFrame(out).set_index('day')
if __name__=='__main__':
    for m in sys.argv[1:] or ['NQ','ES']:
        F=build(m); F.to_pickle(f'nyam_{m}.pkl')
        print(m,F.shape,'touched in NY AM %.1f%%'%(100*F.z_touch.mean()),'hold %.1f%%'%(100*F.z_hold.mean()))
