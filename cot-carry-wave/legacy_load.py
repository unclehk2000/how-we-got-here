import csv, pandas as pd, numpy as np
def load(years=('2018','2021','2026')):
    out=[]
    for y in years:
        f=f'/home/claude/cotrev/legacy/nq_{y}.txt'
        rd=list(csv.reader(open(f)))
        hdr=[r for r in rd if r and r[0]=='id'][0]
        for r in rd:
            if r and r[0].endswith('209742F') and len(r)>=len(hdr)-4:
                out.append(dict(zip(hdr,r)))
    d=pd.DataFrame(out)
    d['date']=pd.to_datetime(d.report_date_as_yyyy_mm_dd.str[:10])
    num=[c for c in d.columns if c not in('id','market_and_exchange_names','report_date_as_yyyy_mm_dd','yyyy_report_week_ww','contract_market_name','cftc_contract_market_code','cftc_market_code','cftc_region_code','cftc_commodity_code','commodity_name','contract_units','commodity','commodity_subgroup_name','commodity_group_name','futonly_or_combined','date')]
    for c in num: d[c]=pd.to_numeric(d[c],errors='coerce')
    return d.sort_values('date').drop_duplicates('date').reset_index(drop=True)
if __name__=='__main__':
    d=load()
    print(len(d))
    # integrity: change fields vs diffs (consecutive weeks only)
    pairs=[('open_interest_all','change_in_open_interest_all'),('comm_positions_long_all','change_in_comm_long_all'),
           ('comm_positions_short_all','change_in_comm_short_all'),('noncomm_positions_long_all','change_in_noncomm_long_all'),
           ('noncomm_positions_short_all','change_in_noncomm_short_all'),('nonrept_positions_long_all','change_in_nonrept_long_all'),
           ('nonrept_positions_short_all','change_in_nonrept_short_all')]
    gap=d.date.diff().dt.days
    ok=gap.between(5,9)
    tot=bad=0
    for lv,ch in pairs:
        diff=d[lv].diff()
        m=ok&d[ch].notna()
        tot+=m.sum(); bad+=(diff[m]!=d[ch][m]).sum()
        if (diff[m]!=d[ch][m]).any(): print(lv, d.loc[m&(diff!=d[ch]),['date',lv,ch]].head())
    print('change-field checks',tot,'mismatches',bad)
    # identities
    L=d.comm_positions_long_all+d.noncomm_positions_long_all+d.noncomm_postions_spread_all+d.nonrept_positions_long_all
    S=d.comm_positions_short_all+d.noncomm_positions_short_all+d.noncomm_postions_spread_all+d.nonrept_positions_short_all
    print('OI identity long',(L!=d.open_interest_all).sum(),'short',(S!=d.open_interest_all).sum())
    t=pd.read_csv('/mnt/user-data/outputs/COT_NQ_TFF_2015_2026.csv',parse_dates=['report_date'])
    m=d.merge(t,left_on='date',right_on='report_date')
    print('OI vs TFF matched',len(m),'mismatch',(m.open_interest_all!=m.open_interest).sum())
    d.to_pickle('legacy_nq.pkl'); m.to_pickle('legacy_tff_nq.pkl')
