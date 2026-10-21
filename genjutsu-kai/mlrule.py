import sys
src=open(sys.argv[1]).read().split('# ── render')[0]
sys.argv=['x','20250102']; exec(src)
out=[]
for ML_ in (0.0,0.02):
    ML=ML_; rows=[]
    for d in days:
        xx=m[m.dk==d]; xx=xx[(xx['mod']>=480)&(xx['mod']<1000)]
        for t in run(xx):
            for s,ih,ref,wb in t.ev: rows.append((d,t.k,s.st))
    E=pd.DataFrame(rows,columns=['d','k','st']); nd=len(days)
    for k,g in E.groupby('k'): print(f"ML {ML:.2f} {k}: {len(g)/nd:.2f}/day  held {(g.st==4).mean()*100:.0f}%  synced {(g.st==3).mean()*100:.0f}%",flush=True)
