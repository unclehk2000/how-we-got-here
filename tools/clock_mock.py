"""Mock-up of the Range clock + status card from real NQ data (Fri 9 Oct 2026 at 11:00 ET, last-30-days baseline)."""
import pandas as pd, numpy as np, matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Polygon
F = pd.read_pickle('/home/claude/byk/dow_full.pkl').sort_values('tday').reset_index(drop=True)
b = pd.read_pickle('/home/claude/twin/bars_NQ_full.pkl')
SL = [18,19,20,21,22,23,0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16]
day = pd.Timestamp('2026-10-09'); i = F.index[F.tday == day][0]
base = F.iloc[i-30:i]
R = base[[f'r{s}' for s in SL]].values
z = 1.2816; n = len(R); r1 = int(np.floor(n/2 - z*np.sqrt(n)/2)); r2 = int(np.ceil(n/2 + z*np.sqrt(n)/2)) - 1
S = np.sort(R, axis=0)
q = {k: np.percentile(R, k, axis=0) for k in (10, 25, 50, 75, 90)}; zlo, zhi = S[r1], S[r2]
x = b[b.tday == day].copy(); o = x.Open.iloc[0]
x['t'] = (x.ts - (day - pd.Timedelta(hours=6))).dt.total_seconds() / 3600.0   # hours since 18:00
x = x[x.t <= 17.0]                                                            # up to 11:00 ET
rr = 100 * (x.High.cummax() - x.Low.cummin()) / o
tt = x.t.values
ends = np.arange(1, 24)
def interp(arr, t):
    xs = np.r_[0, ends]; ys = np.r_[0, arr]; return np.interp(t, xs, ys)
lo_t, hi_t = interp(zlo, tt), interp(zhi, tt)
st = np.where(rr > hi_t, 'A', np.where(rr < lo_t, 'B', 'N'))
fri = F.iloc[:i][F.iloc[:i].dow == 4].tail(30)
cH = np.array([(fri.hi_hr == h).sum() for h in SL]); cL = np.array([(fri.lo_hr == h).sum() for h in SL]); mx = max(cH.max(), cL.max())
BG, HD, BD, TX, SUB, MU = '#0e1117', '#171c28', '#262c3a', '#e6e9ef', '#9aa3b5', '#5d6476'
ORG, CYN, GRN, RED, AMB, NEU, BAND = '#ff6d00', '#00acc1', '#089981', '#f23645', '#ffb300', '#d1d4dc', '#5b6b8c'
fig = plt.figure(figsize=(15, 6.2), facecolor=BG)
ax = fig.add_axes([0.04, 0.08, 0.66, 0.84], facecolor=BG)
X = np.r_[0, ends]
def band(up, dn, c, a):
    ax.add_patch(Polygon(np.c_[np.r_[X, X[::-1]], np.r_[np.r_[0, up], np.r_[0, dn][::-1]]], closed=True, fc=c, ec='none', alpha=a))
band(q[90], q[10], BAND, 0.16); band(q[75], q[25], BAND, 0.28); band(zhi, zlo, NEU, 0.30)
ax.plot(X, np.r_[0, q[50]], ls='--', lw=1.6, color=SUB)
# earlier day faded
prev = b[b.tday == F.tday.iat[i-1]]; po = prev.Open.iloc[0]
pt = (prev.ts - (F.tday.iat[i-1] - pd.Timedelta(hours=6))).dt.total_seconds()/3600 - 23 - 1
# live line coloured by status
col = {'A': ORG, 'B': CYN, 'N': NEU}
for k in range(1, len(tt)):
    ax.plot(tt[k-1:k+1], rr.values[k-1:k+1], color=col[st[k]], lw=2.6, solid_capstyle='round')
H = q[90][-1]
h0, h1 = -0.26*H, -0.04*H
for j in range(23):
    if cH[j]: ax.add_patch(Rectangle((j, h0), 0.5, (h1-h0)*cH[j]/mx, fc=RED, alpha=0.15+0.8*cH[j]/mx, ec='none'))
    if cL[j]: ax.add_patch(Rectangle((j+0.5, h0), 0.5, (h1-h0)*cL[j]/mx, fc=GRN, alpha=0.15+0.8*cL[j]/mx, ec='none'))
for a_, b_, nm, c, al in [(2,6,'Asia',BAND,.35),(8,11,'London',BAND,.45),(15.5,17,'NY AM',AMB,.45),(17.5,19,'Lunch',BAND,.3),(19.5,22,'NY PM',BAND,.45)]:
    ax.add_patch(Rectangle((a_, -0.38*H), b_-a_, 0.08*H, fc=c, alpha=al, ec=BD)); ax.text((a_+b_)/2, -0.34*H, nm, color=TX if nm=='NY AM' else SUB, ha='center', va='center', fontsize=8)
tn = tt[-1]; vn = rr.values[-1]; mn = interp(q[50], tn)
ax.axvline(tn, color=AMB, ls=':', lw=1, alpha=0.6)
pr = np.interp(vn, [interp(q[10],tn), interp(q[25],tn), mn, interp(q[75],tn), interp(q[90],tn)], [10,25,50,75,90])
lab = {'A':'▲ ABOVE','B':'▼ BELOW','N':'● NEUTRAL'}[st[-1]]
ax.text(tn+0.25, vn, f"{vn:.2f}% · {vn/100*o:.0f} pts · ≈P{pr:.0f}\n{lab} · 11:00", color=col[st[-1]], fontsize=9, va='center', family='monospace')
ax.text(tn+0.25, mn - 0.06*H, f"typical by now {mn:.2f}%", color=SUB, fontsize=7.5, va='top')
ax.text(23.1, q[50][-1], f"typical day {q[50][-1]:.2f}% ≈ {q[50][-1]/100*o:.0f} pts", color=SUB, fontsize=7.5, va='center')
ax.text(23.1, q[75][-1], f"P75 {q[75][-1]:.2f}%", color=MU, fontsize=7.5, va='center'); ax.text(23.1, q[25][-1], f"P25 {q[25][-1]:.2f}%", color=MU, fontsize=7.5, va='center')
ax.text(0, q[90].max()*1.04, "RANGE CLOCK · typical path from the last 30 days · neutral zone 80%", color=SUB, fontsize=8)
ax.text(0, h1+0.01*H, f"hour of high ▮ low ▮ · last 30 Fridays", color=MU, fontsize=7)
ax.set_xlim(-0.3, 27.5); ax.set_ylim(-0.42*H, q[90].max()*1.10)
ax.set_xticks(range(0, 24, 3)); ax.set_xticklabels([f"{(18+h)%24:02d}" for h in range(0, 24, 3)], color=MU, fontsize=8)
ax.tick_params(axis='y', colors=MU, labelsize=8); [s.set_color(BD) for s in ax.spines.values()]
ax.yaxis.tick_right()
# status card mock
cx = fig.add_axes([0.73, 0.08, 0.26, 0.84], facecolor=BG); cx.axis('off')
atr = F.atr14.iat[i]; rp = vn/100*o
rows = [("RANGE", f"{vn:.2f}% · {rp:.0f} pts", lab, col[st[-1]]),
        ("  vs typical", "─"*int(round(pr/10)) + "●" + "─"*(10-int(round(pr/10))) + f" ≈P{pr:.0f}", f"typ {mn:.2f}%", None),
        ("ATR 14", f"{atr:.0f} pts · {100*atr/o:.2f}%", "█"*int(round(min(1,rp/atr)*10)) + "░"*(10-int(round(min(1,rp/atr)*10))) + f" {100*rp/atr:.0f}%", None),
        ("DAY", f"typical {q[50][-1]:.2f}% ≈ {q[50][-1]/100*o:.0f} pts", f"+{max(0, q[50][-1]/100*o - rp):.0f} pts to typical", None),
        ("HOUR", "10:00 ET", f"H {100*cH[16]/30:.0f}% · L {100*cL[16]/30:.0f}%", None),
        ("OCT", "month to date", "med +2.2% (16 yrs)", None),
        ("FRI", "range ×1.07 vs all days", "up 50%", None)]
cx.add_patch(Rectangle((0, 0.9), 1, 0.08, fc=HD, ec=BD, transform=cx.transAxes)); cx.text(0.02, 0.94, "● DOW PROFILE  NQ1! · Fri · 11:00 ET", color=AMB, fontsize=9, va='center', family='monospace', weight='bold', transform=cx.transAxes)
y = 0.86
for a_, b_, c_, pc in rows:
    cx.add_patch(Rectangle((0, y-0.1), 1, 0.1, fc=BG, ec=BD, transform=cx.transAxes))
    cx.text(0.02, y-0.05, a_, color=SUB, fontsize=8, va='center', family='monospace', transform=cx.transAxes)
    cx.text(0.25, y-0.05, b_, color=TX, fontsize=8, va='center', family='monospace', transform=cx.transAxes)
    if pc:
        cx.add_patch(Rectangle((0.72, y-0.095), 0.27, 0.09, fc=pc, ec='none', transform=cx.transAxes)); cx.text(0.855, y-0.05, c_, color='#131722' if pc == NEU else 'white', fontsize=8, ha='center', va='center', family='monospace', weight='bold', transform=cx.transAxes)
    else:
        cx.text(0.72, y-0.05, c_, color=SUB, fontsize=7.5, va='center', family='monospace', transform=cx.transAxes)
    y -= 0.1
cx.text(0.02, y-0.04, "mock-up from NQ data · TradingView rendering will differ", color=MU, fontsize=7, transform=cx.transAxes)
plt.savefig('/mnt/user-data/outputs/DayOfWeek/range_clock_mockup.png', dpi=130, facecolor=BG)
print('status', st[-1], 'range', round(vn, 2), 'median by now', round(mn, 2), 'pct', round(pr), 'typical day', round(q[50][-1], 2))
