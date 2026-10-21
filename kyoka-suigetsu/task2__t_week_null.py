import os, sys; sys.path[:0] = [os.path.dirname(os.path.dirname(os.path.abspath(__file__)))]; from config import *
import pandas as pd, numpy as np
rng=np.random.default_rng(11)
W5=['Mon','Tue','Wed','Thu','Fri']
for s in ['NQ','ES','RTY']:
    D=pd.read_pickle(f'F_{s}.pkl'); D['wk']=D.index.to_period('W-FRI')
    D['pc']=D.ac.shift(1)
    D['r']=D.ac/D.pc; D['hr']=D.ah/D.pc; D['lr_']=D.al/D.pc
    D=D.dropna(subset=['r'])
    full=D.groupby('wk').filter(lambda x: len(x)==5 and list(x.dow)==[0,1,2,3,4])
    A=full[['r','hr','lr_']].values.reshape(-1,5,3)
    def stats_of(A):
        lvl=np.cumprod(A[:,:,0],axis=1); prev=np.concatenate([np.ones((len(A),1)),lvl[:,:-1]],axis=1)
        H=prev*A[:,:,1]; L=prev*A[:,:,2]
        hi=H.argmax(1); lo=L.argmin(1)
        hold=[]; holdl=[]
        for k in range(4):
            hold.append((H[:,:k+1].max(1)>=H[:,k+1:].max(1)).mean()); holdl.append((L[:,:k+1].min(1)<=L[:,k+1:].min(1)).mean())
        return np.bincount(hi,minlength=5)/len(hi), np.bincount(lo,minlength=5)/len(lo), np.array(hold), np.array(holdl)
    ah,al,hh,hl=stats_of(A)
    NH=[];NL=[];NHH=[];NHL=[]
    for _ in range(400):
        P=np.array([w[rng.permutation(5)] for w in A])
        a,b,c,d=stats_of(P); NH.append(a);NL.append(b);NHH.append(c);NHL.append(d)
    NH=np.mean(NH,0);NL=np.mean(NL,0);NHH=np.mean(NHH,0);NHL=np.mean(NHL,0)
    print(f'\n== {s}: actual vs shuffled-days null (same days, random order within the week) ==')
    print('  high day  actual: '+' '.join(f'{W5[i]} {100*ah[i]:4.1f}' for i in range(5)))
    print('            null  : '+' '.join(f'{W5[i]} {100*NH[i]:4.1f}' for i in range(5)))
    print('  low day   actual: '+' '.join(f'{W5[i]} {100*al[i]:4.1f}' for i in range(5)))
    print('            null  : '+' '.join(f'{W5[i]} {100*NL[i]:4.1f}' for i in range(5)))
    print('  high-so-far holds after Mon..Thu: actual '+' '.join(f'{100*v:.0f}%' for v in hh)+' | null '+' '.join(f'{100*v:.0f}%' for v in NHH))
    print('  low-so-far holds after Mon..Thu:  actual '+' '.join(f'{100*v:.0f}%' for v in hl)+' | null '+' '.join(f'{100*v:.0f}%' for v in NHL))
