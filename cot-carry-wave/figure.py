import pandas as pd, numpy as np, matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt, sys
mkt=sys.argv[1] if len(sys.argv)>1 else 'NQ'
F=pd.read_pickle(f'F_{mkt}.pkl'); F=F[F.y.notna()|F.am.notna()]
t=F.index.to_timestamp(how='end')
lp=100*np.log1p(F.y.fillna(0)).cumsum().where(F.y.notna())
S,T1,T2,B1,B2,GR='#fcfcfb','#0b0b0b','#52514e','#2a78d6','#eb6834','#d9d8d4'
plt.rcParams.update({'font.size':9,'axes.edgecolor':GR,'axes.labelcolor':T2,'xtick.color':T2,'ytick.color':T2,'axes.facecolor':S,'figure.facecolor':S})
fig,ax=plt.subplots(3,1,figsize=(10,7.2),sharex=True,gridspec_kw={'height_ratios':[2.2,1,1]})
ax[0].plot(t,lp,color=B1,lw=1.6)
crest=F.px_w52_osc>0.92; trough=F.px_w52_osc<-0.92
ax[0].scatter(t[crest],lp[crest],marker='v',s=34,color=B2,zorder=3,label='price wave at crest (osc > 0.92)')
ax[0].scatter(t[trough],lp[trough],marker='^',s=34,color=T1,zorder=3,label='price wave at trough (osc < −0.92)')
ax[0].set_ylabel('cumulative log return, %'); ax[0].legend(frameon=False,loc='upper left',fontsize=8)
ax[0].set_title(f'{mkt} weekly: 52-week travelling-wave oscillators (causal fits, data to prior Friday)',loc='left',color=T1,fontsize=10)
for a,col,lab in [(ax[1],'px_w52_osc','price wave (52w)'),(ax[2],'am_w52_osc','asset-manager COT wave (52w)')]:
    a.plot(t,F[col],color=B1,lw=1.2); a.axhline(0,color=GR,lw=0.8)
    a.set_ylim(-1.15,1.15); a.set_yticks([-1,0,1]); a.set_ylabel(lab,fontsize=8)
for a in ax:
    a.grid(axis='y',color=GR,lw=0.5); [a.spines[s].set_visible(False) for s in ['top','right']]
fig.tight_layout(); fig.savefig(f'wave_{mkt}.png',dpi=150)
print('saved')
