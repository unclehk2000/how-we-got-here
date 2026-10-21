"""How many days light up under each version of the qualifier (share of days, and expansion rate on them)."""
import pandas as pd, numpy as np
exec(open('/mnt/user-data/outputs/Domain_Expansion/de_cbdr_modes.py').read().split("def table")[0])
F['coiled'] = F.coil <= 0.20; F['volatile'] = F.atr5 >= 1.0; F['cb5'] = F.cb_rng >= 5
rows = []
for sp in ['train', 'test']:
    Z = F[F.sp == sp]
    for name, m, tgt in [('ATR >= 1% (first version)', Z.volatile, 'exp'),
                         ('Coiled (SD version, before CBDR)', Z.coiled, 'sd2'),
                         ('BOTH: coiled + CBDR >= 5 ranges (now, SD mode)', Z.coiled & Z.cb5, 'sd2'),
                         ('At least one factor (now, SD mode)', Z.coiled | Z.cb5, 'sd2'),
                         ('BOTH: volatile + CBDR >= 0.80% (now, % mode)', Z.volatile & Z.cb, 'exp')]:
        rows.append(dict(split=sp, flag=name, days=f"{100*m.mean():.0f}%", hit=f"{100*Z[tgt][m].mean():.0f}%", rest=f"{100*Z[tgt][~m].mean():.0f}%"))
print(pd.DataFrame(rows).to_string(index=False))
