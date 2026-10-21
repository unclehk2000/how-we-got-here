import sys; sys.argv=['x','20250102']
exec(open('/tmp/claude-0/-home-claude/46420b5d-8899-592c-962a-4f205cf71b0c/scratchpad/mock_train.py').read().split('# ── render')[0])
rows=[]
for d in days:
    xx=m[m.dk==d]; xx=xx[(xx['mod']>=480)&(xx['mod']<1000)]
    for t in run(xx):
        for s,ih,ref,wb in t.ev: rows.append((d,t.k,s.st,s.lagP))
E=pd.DataFrame(rows,columns=['d','k','st','lag']); nd=E.d.nunique()
for k,g in E.groupby('k'):
    print(f"\n{k}: {len(g)/nd:.2f} SMTs/day · lag (final) percentiles %: "+' '.join(f"P{q}={g.lag.quantile(q/100):.3f}" for q in (10,25,50,75,90)))
    for th in (0.0,0.02,0.03,0.05,0.10):
        x=g[g.lag>=th]; print(f"   lag ≥ {th:.2f}%: {len(x)/nd:.2f}/day · held share {(x.st==4).mean()*100:.0f}%")
