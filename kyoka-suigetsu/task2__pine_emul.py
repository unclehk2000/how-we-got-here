# Python mirror of the Pine calendar + HAR logic, to check the indicator reproduces the research model
import os, sys; sys.path[:0] = [os.path.dirname(os.path.dirname(os.path.abspath(__file__)))]; from config import *
import pandas as pd, numpy as np, json, datetime as dt
def dow_pine(d): return (d.weekday()+1)%7+1          # Pine: 1=Sun … 7=Sat
def nthDow(y,m,wd,n):
    f=dow_pine(dt.date(y,m,1)); return 1+(wd-f+7)%7+7*(n-1)
def lastDow(y,m,wd,dim):
    l=dow_pine(dt.date(y,m,dim)); return dim-(l-wd+7)%7
def easter(y):
    a=y%19;b=y//100;c=y%100;d=b//4;e=b%4;f=(b+8)//25;g=(b-f+1)//3;h=(19*a+b-d-g+15)%30;i=c//4;k=c%4
    l=(32+2*e+2*i-h-k)%7;m=(a+11*h+22*l)//451;mo=(h+l-7*m+114)//31;dd=(h+l-7*m+114)%31+1
    return dt.date(y,mo,dd)
def isHol(d):
    y,m,dd=d.year,d.month,d.day; w=dow_pine(d)
    if not (2<=w<=6): return False
    gf=easter(y)-dt.timedelta(days=2); gfOpen=y in (2010,2012,2015,2023,2026)
    return ((m==1 and (dd==1 or (dd==2 and w==2))) or (m==1 and dd==nthDow(y,1,2,3)) or (m==2 and dd==nthDow(y,2,2,3))
        or (not gfOpen and d==gf) or (m==5 and dd==lastDow(y,5,2,31)) or (y>=2022 and m==6 and (dd==19 or (dd==18 and w==6) or (dd==20 and w==2)))
        or (m==7 and (dd==4 or (dd==3 and w==6) or (dd==5 and w==2))) or (m==9 and dd==nthDow(y,9,2,1)) or (m==11 and dd==nthDow(y,11,5,4))
        or (m==12 and (dd==25 or (dd==24 and w==6) or (dd==26 and w==2))))
def dayStep(d,s):
    t=d+dt.timedelta(days=s)
    while t.weekday()>=5: t+=dt.timedelta(days=s)
    return t
def nextTD(d):
    t=dayStep(d,1); g=0
    while isHol(t) and g<5: t=dayStep(t,1); g+=1
    return t
if __name__=='__main__':
    D=pd.read_pickle('F_NQ.pkl')
    idx=[x.date() for x in D.index]
    pre=pd.Series([int(isHol(dayStep(d,1))) for d in idx],index=D.index)
    post=pd.Series([int(isHol(dayStep(d,-1))) for d in idx],index=D.index)
    last=pd.Series([int(nextTD(d).month!=d.month) for d in idx],index=D.index)
    tom=((last==1)|(D.tdom<=3)).astype(int)
    opex=pd.Series([int(d.weekday()==4 and 15<=d.day<=21) for d in idx],index=D.index)
    for nm,a,b in [('pre_hol',pre,D.pre_hol),('post_hol',post,D.post_hol),('tom',tom,D.tom),('opex_day',opex,D.opex_day)]:
        mis=D.index[a!=b]
        print(f'{nm}: Pine-rule vs data mismatches {len(mis)} of {len(D)}', [x.date() for x in mis[:12]])
    # also: holidays by rule vs missing weekdays in the CME calendar
    bd=pd.bdate_range('2010-01-04','2026-10-09'); miss=set(bd.difference(D.index).date)
    rule=set(d.date() for d in bd if isHol(d.date()))
    print('rule-only (rule says closed, data has a row):',sorted(rule-miss)[:20])
    print('data-only (no row, rule says open):',sorted(miss-rule)[:20])
