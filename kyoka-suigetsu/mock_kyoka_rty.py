"""Kyōka Suigetsu v13 on RTY1!, Fri 9 Oct 2026 at 11:00 ET (last full day in the RTY 1-minute data).
Range clock from the last 30 days, expected range (RTY fit), live projection (v13 pooled weights) and the
HIGH / LOW IN row with the RTY variance profile (v13) next to what v12 would have shown."""
import os, sys
sys.path[:0] = ['/home/claude/repo/kyoka-suigetsu-research', '/home/claude/repo/kyoka-suigetsu-research/task3']
os.environ['KYOKA_RAW'] = '/mnt/user-data/uploads'; os.environ['KYOKA_WORK'] = '/home/claude/kyw'
from common import *
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Polygon
from scipy.stats import norm
ar = {l.split('=')[0].split()[-1]: np.array([float(v) for v in l[l.index('(') + 1:l.rindex(')')].split(',')]) for l in open('/tmp/claude-0/v13_arrays.txt') if l.startswith('var array')}
VREM12 = ar['VREM']; VREMR = ar['VREMR']; KAP = 0.655
S = prep('RTY'); day = pd.Timestamp('2026-10-09'); i = S.index.get_loc(day)
base = S.iloc[i - 30:i]
R = base[[f'r{s}' for s in range(23)]].values
z = 1.2816; n = len(R); r1 = int(np.floor(n / 2 - z * np.sqrt(n) / 2)); r2 = int(np.ceil(n / 2 + z * np.sqrt(n) / 2)) - 1
Ss = np.sort(R, axis=0); q = {k: np.percentile(R, k, axis=0) for k in (10, 25, 50, 75, 90)}; zlo, zhi = Ss[r1], Ss[r2]
b = pd.read_pickle('bars_RTY_all.pkl'); x = b[b.tday == day].sort_values('ts').copy(); o = x.Open.iloc[0]
x['t'] = (x.ts - (day - pd.Timedelta(hours=6))).dt.total_seconds() / 3600.0
x = x[x.t < 17.0]                                                    # through 10:59 ET
rr = 100 * (x.High.cummax() - x.Low.cummin()) / o; tt = x.t.values + 1 / 60
ends = np.arange(1, 24); Xp = np.r_[0, ends]
itp = lambda arr, t: np.interp(t, Xp, np.r_[0, arr])
st = np.where(rr > itp(zhi, tt), 'A', np.where(rr < itp(zlo, tt), 'B', 'N'))
# expected range (walk-forward RTY fit) and the live projection at the end of the 10:00 hour (slot 16)
har = S.har.iat[i]; exp_pct = np.exp(har)
lrun = np.log(rr.values[-1]); pj = lrun - S['sh16'].iat[i]
W = {k: ar[k][16] for k in ar}
prj = {qq: np.exp(max(lrun, pj + W[f'PC{qq}'] + W[f'PW{qq}'] * (har - pj))) for qq in ('25', '50', '75')}
# chance the high / low is already in (end of the 10:00 hour: variance-left at index 16)
tHi, tLo, cl = x.High.max(), x.Low.min(), x.Close.iloc[-1]
def inn(V):
    sg = KAP * exp_pct * np.sqrt(V[16]); return [2 * norm.cdf(100 * d / o / sg) - 1 for d in (tHi - cl, cl - tLo)] + [sg / 100 * o]
h13, l13, s13 = inn(VREMR); h12, l12, s12 = inn(VREM12)
fut = b[(b.tday == day) & (b.ts > x.ts.iloc[-1])]
print(f'expected {exp_pct:.2f}% = {exp_pct / 100 * o:.1f} pts · range now {rr.values[-1]:.2f}% · projection median {prj["50"]:.2f}% '
      f'· high in v13 {h13 * 100:.0f}% (v12 {h12 * 100:.0f}%) · low in v13 {l13 * 100:.0f}% (v12 {l12 * 100:.0f}%) · '
      f'actual rest of day: new high {fut.High.max() > tHi} · new low {fut.Low.min() < tLo} · final range {100 * (max(tHi, fut.High.max()) - min(tLo, fut.Low.min())) / o:.2f}%')
BG, HD, BD, TX, SUB, MU = '#0e1117', '#171c28', '#262c3a', '#e6e9ef', '#9aa3b5', '#5d6476'
ORG, CYN, AMB, NEU, BAND, PUR = '#ff6d00', '#00acc1', '#ffb300', '#d1d4dc', '#5b6b8c', '#ab47bc'
fig = plt.figure(figsize=(15, 6.4), facecolor=BG)
ax = fig.add_axes([0.04, 0.09, 0.62, 0.83], facecolor=BG)
def band(up, dn, c, a): ax.add_patch(Polygon(np.c_[np.r_[Xp, Xp[::-1]], np.r_[np.r_[0, up], np.r_[0, dn][::-1]]], closed=True, fc=c, ec='none', alpha=a))
band(q[90], q[10], BAND, 0.16); band(q[75], q[25], BAND, 0.28); band(zhi, zlo, NEU, 0.30)
ax.plot(Xp, np.r_[0, q[50]], ls='--', lw=1.6, color=SUB)
col = {'A': ORG, 'B': CYN, 'N': NEU}
for k in range(1, len(tt)): ax.plot(tt[k - 1:k + 1], rr.values[k - 1:k + 1], color=col[st[k]], lw=2.6, solid_capstyle='round')
H = q[90][-1]
# expected (session end) and projected range markers
ax.plot([23, 23.6], [exp_pct] * 2, color=PUR, lw=2); ax.text(23.7, exp_pct, f'expected {exp_pct:.2f}%', color=PUR, fontsize=8, va='center')
ax.add_patch(Rectangle((23, prj['25']), 0.6, prj['75'] - prj['25'], fc=PUR, alpha=0.25, ec=PUR))
ax.plot([23, 23.6], [prj['50']] * 2, color=PUR, lw=1.2, ls=':'); ax.text(23.7, prj['50'], f'projected {prj["50"]:.2f}%', color=PUR, fontsize=8, va='center', alpha=0.9)
for a_, b_, nm, c, al in [(2, 6, 'Asia', BAND, .35), (8, 11, 'London', BAND, .45), (15.5, 17, 'NY AM', AMB, .45), (17.5, 19, 'Lunch', BAND, .3), (19.5, 22, 'NY PM', BAND, .45)]:
    ax.add_patch(Rectangle((a_, -0.16 * H), b_ - a_, 0.08 * H, fc=c, alpha=al, ec=BD)); ax.text((a_ + b_) / 2, -0.12 * H, nm, color=TX if nm == 'NY AM' else SUB, ha='center', va='center', fontsize=8)
tn = tt[-1]; vn = rr.values[-1]; mn = itp(q[50], tn)
pr = np.interp(vn, [itp(q[10], tn), itp(q[25], tn), mn, itp(q[75], tn), itp(q[90], tn)], [10, 25, 50, 75, 90])
lab = {'A': '▲ ABOVE', 'B': '▼ BELOW', 'N': '● NEUTRAL'}[st[-1]]
ax.axvline(tn, color=AMB, ls=':', lw=1, alpha=0.6)
ax.text(tn + 0.25, vn, f"{vn:.2f}% · {vn / 100 * o:.1f} pts · ≈P{pr:.0f}\n{lab} · 11:00", color=col[st[-1]], fontsize=9, va='center', family='monospace')
ax.text(0, max(q[90].max(), prj['75']) * 1.05, "KYŌKA SUIGETSU · RTY1! · range clock · last 30 days · neutral zone 80%", color=SUB, fontsize=8)
ax.set_xlim(-0.3, 28); ax.set_ylim(-0.2 * H, max(q[90].max(), prj['75']) * 1.12)
ax.set_xticks(range(0, 24, 3)); ax.set_xticklabels([f"{(18 + h) % 24:02d}" for h in range(0, 24, 3)], color=MU, fontsize=8)
ax.tick_params(axis='y', colors=MU, labelsize=8); [s_.set_color(BD) for s_ in ax.spines.values()]; ax.yaxis.tick_right()
cx = fig.add_axes([0.69, 0.09, 0.30, 0.83], facecolor=BG); cx.axis('off')
pts = lambda p: f'{p / 100 * o:.1f}'
rows = [("RANGE", f"{vn:.2f}% · {pts(vn)} pts", lab, col[st[-1]]),
        ("EXPECTED", f"{exp_pct:.2f}% · {pts(exp_pct)} pts", f"P25–75 {pts(exp_pct * np.exp(-0.25))}–{pts(exp_pct * np.exp(0.23))}", None),
        ("PROJECTED", f"{prj['50']:.2f}% · {pts(prj['50'])} pts", f"+{max(0, prj['50'] - vn) / 100 * o:.1f} pts to go", None),
        ("HIGH / LOW IN", f"H {h13 * 100:.0f}% · L {l13 * 100:.0f}%", f"σ left {s13:.1f} pts", None),
        ("  v12 (NQ/ES)", f"H {h12 * 100:.0f}% · L {l12 * 100:.0f}%", f"σ left {s12:.1f} pts", None)]
cx.add_patch(Rectangle((0, 0.9), 1, 0.08, fc=HD, ec=BD, transform=cx.transAxes)); cx.text(0.02, 0.94, "● KYŌKA SUIGETSU  RTY1! · Fri · 11:00 ET", color=AMB, fontsize=9, va='center', family='monospace', weight='bold', transform=cx.transAxes)
y = 0.86
for a_, b_, c_, pc in rows:
    cx.add_patch(Rectangle((0, y - 0.1), 1, 0.1, fc=BG, ec=BD, transform=cx.transAxes))
    cx.text(0.02, y - 0.05, a_, color=MU if a_.startswith('  ') else SUB, fontsize=8, va='center', family='monospace', transform=cx.transAxes)
    cx.text(0.33, y - 0.05, b_, color=MU if a_.startswith('  ') else TX, fontsize=8, va='center', family='monospace', transform=cx.transAxes)
    if pc:
        cx.add_patch(Rectangle((0.72, y - 0.095), 0.27, 0.09, fc=pc, ec='none', transform=cx.transAxes)); cx.text(0.855, y - 0.05, c_, color='#131722' if pc == NEU else 'white', fontsize=8, ha='center', va='center', family='monospace', weight='bold', transform=cx.transAxes)
    else:
        cx.text(0.70, y - 0.05, c_, color=SUB, fontsize=7.5, va='center', family='monospace', transform=cx.transAxes)
    y -= 0.1
cx.text(0.02, y - 0.05, "v13: RTY uses its own variance profile (more of\nits day is done by midday), so at 11:00 there is\nless volatility left and the high / low-in chances\nare higher than v12 gave. Mock-up from RTY\n1-minute data; TradingView rendering will differ.", color=MU, fontsize=7.3, va='top', transform=cx.transAxes)
plt.savefig(sys.argv[1], dpi=130, facecolor=BG); print(sys.argv[1])
