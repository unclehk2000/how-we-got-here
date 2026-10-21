"""ES calibration and sensitivity. Ratio settings (coil, CBDR in ranges, SD) are scale-free; % settings are scaled by s.
s = ES/NQ volatility ratio (~0.74). Splits: 2023-24 / 2025-26 (ES history starts 2023)."""
import pandas as pd, numpy as np
A = pd.read_pickle('/home/claude/byk/de_assets.pkl')
def tiers(Z, f1, f2, tgt):
    out = {}
    for k, m in [('BOTH', f1 & f2), ('F1 only', f1 & ~f2), ('CBDR only', ~f1 & f2), ('NEITHER', ~f1 & ~f2)]:
        out[k] = f"{100*Z[tgt][m].mean():4.0f}% ({100*m.mean():3.0f}% of days)" if m.sum() >= 8 else f"  n<8 ({100*m.mean():3.0f}%)"
    return out
def show(sym, title, f1fn, f2fn, tgtfn):
    print(f"\n{sym} · {title}")
    Z0 = A[(A.sym == sym) & (A.year >= 2023)]
    for sp in ['pre-2025', '2025-26']:
        Z = Z0[Z0.sp == sp].copy(); Z['tgt'] = tgtfn(Z)
        r = tiers(Z, f1fn(Z), f2fn(Z), 'tgt')
        print(f"  {sp:8s} base {100*Z.tgt.mean():3.0f}% | " + ' | '.join(f"{k} {v}" for k, v in r.items()))
for sym in ['ES', 'NQ']:
    show(sym, 'SD mode, defaults (coil <= 0.20, CBDR >= 5 ranges, 2 SD at the London extreme)',
         lambda Z: Z.coil <= 0.20, lambda Z: Z.cbR >= 5, lambda Z: Z.xsd >= 2)
for s in [1.0, 0.75]:
    show('ES', f'% mode, NQ thresholds x {s} (ATR >= {1.0*s:.2f}%, CBDR >= {0.8*s:.2f}%, close >= {0.3*s:.3f}%)',
         lambda Z, s=s: Z.atr_pct >= 1.0 * s, lambda Z, s=s: Z.cb_pct >= 0.8 * s, lambda Z, s=s: Z.cpct >= 0.3 * s)
show('NQ', '% mode, NQ defaults (2023-26 only)', lambda Z: Z.atr_pct >= 1.0, lambda Z: Z.cb_pct >= 0.8, lambda Z: Z.cpct >= 0.3)

print('\n=== Sensitivity, ES, SD mode (2 SD at the London extreme): BOTH tier hit rate / share of days, 2023-24 | 2025-26')
E = A[(A.sym == 'ES')]
for c in [0.10, 0.15, 0.20, 0.25, 0.30]:
    line = f"  coil <= {c:.2f}:"
    for k in [4, 5, 6]:
        cell = []
        for sp in ['pre-2025', '2025-26']:
            Z = E[E.sp == sp]; m = (Z.coil <= c) & (Z.cbR >= k)
            cell.append(f"{100*(Z.xsd[m] >= 2).mean():3.0f}%/{100*m.mean():2.0f}%")
        line += f"  | CBDR>={k}: " + ' '.join(cell)
    print(line)
print('  NEITHER at the default (coil 0.20, CBDR 5):', ' '.join(f"{sp} {100*(E[E.sp==sp].xsd[(E[E.sp==sp].coil>0.2)&(E[E.sp==sp].cbR<5)]>=2).mean():.0f}%" for sp in ['pre-2025','2025-26']))
print('\n=== Sensitivity, ES, % mode: BOTH tier hit rate / share of days (close >= 0.225%), by scale s on ATR and CBDR thresholds')
for s in [0.60, 0.65, 0.70, 0.75, 0.80, 0.85, 1.00]:
    cell = []
    for sp in ['pre-2025', '2025-26']:
        Z = E[E.sp == sp]; m = (Z.atr_pct >= 1.0 * s) & (Z.cb_pct >= 0.8 * s); n = (Z.atr_pct < 1.0 * s) & (Z.cb_pct < 0.8 * s)
        cell.append(f"BOTH {100*(Z.cpct[m] >= 0.225).mean():3.0f}%/{100*m.mean():2.0f}% days, NEITHER {100*(Z.cpct[n] >= 0.225).mean():3.0f}%")
    print(f"  s = {s:.2f} (ATR {1.0*s:.2f}%, CBDR {0.8*s:.2f}%): " + ' | '.join(cell))
print('\n=== Expansion % threshold on ES: share of days that qualify as expansion days')
for p in [0.15, 0.20, 0.225, 0.25, 0.30]:
    print(f"  {p:.3f}%: " + ' '.join(f"{sp} {100*(E[E.sp==sp].cpct >= p).mean():.1f}%" for sp in ['pre-2025', '2025-26']) +
          f"   (NQ 0.30%: {100*(A[(A.sym=='NQ')&(A.year>=2023)].cpct >= 0.30).mean():.1f}%)")
# Auto scale: asset's own 1-year median overnight ATR % / NQ reference median (2018-2026)
ref = A[A.sym == 'NQ'].atr_pct.median()
print(f'\nNQ reference median overnight ATR (2018-2026): {ref:.3f}%')
for sym in ['ES', 'NQ']:
    Z = A[A.sym == sym].copy()
    Z['auto'] = Z.groupby('blk').atr_pct.transform(lambda s: s.shift(1).rolling(250, min_periods=120).median()) / ref
    print(f"  {sym}: auto scale median {Z.auto.median():.2f}, range (10-90%) {Z.auto.quantile(.1):.2f}-{Z.auto.quantile(.9):.2f}")
