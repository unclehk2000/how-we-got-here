import pandas as pd, numpy as np
def day_slots(bars):
    b=bars[['tday','ts','High','Low','Open']].copy()
    b['h']=b.ts.dt.hour; b['slot']=(b.h-18)%24
    b=b[b.slot<=22]
    out=[]
    for td,x in b.groupby('tday'):
        if len(x)<600: continue
        o=x.Open.iloc[0]
        g=x.groupby('slot').agg(H=('High','max'),L=('Low','min'))
        g=g.reindex(range(23)).ffill()
        rh=g.H.cummax(); rl=g.L.cummin()
        r=((rh-rl)/o*100).values
        out.append([pd.Timestamp(td)]+list(r))
    S=pd.DataFrame(out,columns=['tday']+[f's{i}' for i in range(23)]).set_index('tday')
    S['final']=S.s22
    return S
if __name__=='__main__':
    for s,f in [('ES','/home/claude/twin/bars_ES.pkl'),('NQ','/home/claude/twin/bars_NQ_full.pkl')]:
        S=day_slots(pd.read_pickle(f)); S.to_pickle(f'slots_{s}.pkl'); print(s,len(S),S.index.min().date(),S.index.max().date())
