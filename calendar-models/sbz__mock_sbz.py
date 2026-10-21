"""Mocks: Senbonzakura (combined) on NQ1! daily as of the weekend of 10–11 Oct 2026 (last bar Fri 9 Oct).
Kageyoshi: the next session's close from Friday's close (market shut → 18:00 row), context-scaled, VXN 21.98 (8 Oct
close, FRED; 9 Oct not yet published). Senkei: CME FedWatch history per meeting and CME's 12 Oct conditional table.
Full layout and Mobile (Hakuteiken) layout."""
import sys, json, math, numpy as np, pandas as pd, matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Polygon, FancyBboxPatch
from matplotlib.colors import to_rgb
from scipy.stats import norm
plt.rcParams['font.family'] = 'DejaVu Sans'
MONO = 'DejaVu Sans Mono'
BG, TX, SUB, MU, NEU = '#0e1117', '#e6e9ef', '#9aa3b5', '#5d6476', '#3a3f4b'
CH, CI, CLV, GH = '#f06292', '#2962ff', '#ffb300', '#ab47bc'
UPC, DNC = '#089981', '#f23645'
LINES = ['#e040fb', '#ba68c8', '#9575cd', '#7986cb', '#64b5f6', '#4dd0e1']
QL = np.array([0.01, 0.025, 0.05, 0.1, 0.15, 0.2, 0.25, 0.3, 0.35, 0.4, 0.45, 0.5, 0.55, 0.6, 0.65, 0.7, 0.75, 0.8, 0.85, 0.9, 0.95, 0.975, 0.99])
R = json.load(open('/home/claude/hm/senbon/dist.json')); M = json.load(open('/home/claude/hm/senbon/ctx_model2.json'))
D = pd.read_pickle('/home/claude/hm/senbon/ctx_NQ.pkl')
day = pd.Timestamp('2026-10-09'); D = D[D.index <= day]
P = D.loc[day, 'C_TD']; adrU = D.rng.rolling(20).mean().loc[day]           # next session: ADR20 including Friday
pdh, pdl, mo = D.loc[day, 'H'], D.loc[day, 'L'], D.loc[day, 'MO']; ath = max(D.loc[day, 'ATHp'], D.loc[day, 'H'])
iv = 21.98
Q = np.array(M['sym']['NQ']['q_TD']) / 1000; F = np.array(R['NQ']['C_TD']['f']) / 1000
z = np.array([P > pdh, P < pdl, np.clip((mo - P) / adrU, 0, 3), np.clip((P - mo) / adrU, 0, 3), (ath - P) / adrU <= 0.5], float)
sCtx = float(np.exp(np.array(M['sym']['NQ']['beta'][M['blocks'][0]]) @ z))
row = Q[0]; med = row[11]
xs = list(P + adrU * (med + (row - med) * sCtx)); ps = list(QL)
xs = [xs[0] - 2 * (xs[1] - xs[0])] + xs + [xs[-1] + 2 * (xs[-1] - xs[-2])]; ps = [0.0] + ps + [1.0]
cdf = lambda v: float(np.interp(v, xs, ps)); qinv = lambda p: float(np.interp(p, ps, xs))
sg = iv / 100 / math.sqrt(252) * math.sqrt(F[0])
print(f'P {P} adrU {adrU:.1f} PDH {pdh} PDL {pdl} MO {mo} ATH {ath} z {z.round(2).tolist()} ctx ×{sCtx:.3f} sg {sg:.5f}')
# Senkei: CME data
E = pd.read_pickle('/home/claude/hm/fedmap/exp_mid.pkl')
C = {'28 OCT': [78.4, 21.6], '09 DEC': [12.3, 69.5, 18.2], '27 JAN': [6.9, 44.5, 40.6, 7.9], '17 MAR': [1.8, 16.9, 43.5, 31.9, 5.8],
     '28 APR': [1.1, 11.1, 33.2, 36.4, 15.9, 2.3], '09 JUN': [0.6, 6.9, 23.8, 35.1, 24.6, 8.1, 1.0], '28 JUL': [0.5, 5.9, 21.2, 33.3, 26.2, 10.6, 2.1, 0.1],
     '15 SEP': [0.5, 5.1, 18.8, 31.4, 27.3, 13.1, 3.4, 0.4], '27 OCT': [0.5, 5.0, 18.5, 31.1, 27.4, 13.4, 3.6, 0.5], '08 DEC': [0.6, 5.5, 19.0, 31.0, 26.9, 13.0, 3.5, 0.5]}
SEP = {2026: 4.125, 2027: 4.125}; lo0, base = 3.75, 3.878
WLV = 3                                                     # level line width setting shown in the mock

def frame(ax):
    ax.set_facecolor(BG); ax.yaxis.tick_right(); ax.tick_params(colors=MU, labelsize=7); ax.grid(color='#1a1f2b', lw=0.6)
    for s_ in ax.spines.values(): s_.set_color('#1c2130')

def kage(ax, Dv, n, off, length, nbin, mob, fs):
    lo = min(xs[1], P * math.exp(-2.326 * sg)); hi = max(xs[-2], P * math.exp(2.326 * sg))
    bw = math.ceil(max(0.25, (hi - lo) / nbin) / 0.25) * 0.25; b0 = math.floor(lo / bw) * bw; nb = int(math.ceil((hi - b0) / bw))
    pH = np.array([cdf(b0 + (i + 1) * bw) - cdf(b0 + i * bw) for i in range(nb)])
    pH = np.convolve(np.pad(pH, 2), np.array([1, 4, 6, 4, 1]) / 16, mode='valid')
    pI = np.array([norm.cdf(math.log((b0 + (i + 1) * bw) / P) / sg) - norm.cdf(math.log((b0 + i * bw) / P) / sg) for i in range(nb)])
    pmax = max(pH.max(), pI.max()); iMax = int(np.argmax(np.maximum(pH, pI)))
    x0 = n - 1 + off
    ys = b0 + (np.arange(nb) + 0.5) * bw
    d = np.exp(-0.5 * (np.log(ys / P) / sg) ** 2) / (math.sqrt(2 * math.pi) * sg * ys) * bw
    poly = [(x0, b0)] + [(x0 + round(v / pmax * length), y) for v, y in zip(d, ys)] + [(x0, b0 + nb * bw)]
    ax.add_patch(Polygon(poly, closed=True, fc=CI, alpha=0.15, ec='none')); ax.plot([p[0] for p in poly[1:-1]], [p[1] for p in poly[1:-1]], color=CI, lw=1.6)
    for i in range(nb):
        L = round(pH[i] / pmax * length)
        if L >= 1: ax.add_patch(Rectangle((x0, b0 + i * bw), L, bw, fc=CH, alpha=0.45, ec=CH, lw=0.6))
    ax.plot([n - 1, x0 + length + 2], [P, P], color=TX, alpha=0.5, lw=0.8, ls=':')
    h10, h25, h50, h75, h90 = (qinv(p) for p in (0.1, 0.25, 0.5, 0.75, 0.9)); i10, i90 = P * math.exp(-1.2816 * sg), P * math.exp(1.2816 * sg)
    ax.plot([x0 - 2, x0 - 2], [h10, h90], color=CH, alpha=0.65, lw=1); ax.plot([x0 - 2, x0 - 2], [h25, h75], color=CH, lw=3)
    ax.plot([x0, x0 + length], [h50, h50], color=CH, lw=0.9, ls='--'); ax.plot([x0 - 4, x0 - 4], [i10, i90], color=CI, alpha=0.7, lw=1.6)
    if not mob:
        ax.text(x0 - 2.6, h90, f'80% {h90:,.2f}', color=CH, fontsize=fs, ha='right', va='center'); ax.text(x0 - 2.6, h10, f'80% {h10:,.2f}', color=CH, fontsize=fs, ha='right', va='center')
        ax.text(x0 + length + 0.6, b0 + (iMax + 2.5) * bw, f'{pmax * 100:.1f}% per {bw:.2f}', color=SUB, fontsize=fs - 1, va='center')
    ax.text(x0 + length + 0.6, h50, f'{"med" if mob else "median"} {"+" if h50 >= P else "−"}{abs(h50 - P):.2f}', color=CH, fontsize=fs, va='center')
    lvT = []
    for nm, lv, ls in (('PDH', pdh, '--'), ('PDL', pdl, '--'), ('MO', mo, ':'), ('ATH', ath, '-')):
        up_ = lv >= P; ph = (1 - cdf(lv)) if up_ else cdf(lv); pi_ = (1 - norm.cdf(math.log(lv / P) / sg)) if up_ else norm.cdf(math.log(lv / P) / sg)
        od = f"{'▲' if up_ else '▼'}{100 * ph:.0f}{'/' if mob else ' / '}{100 * pi_:.0f}%"
        lvT.append(f'{nm} {lv:,.2f} {od}')
        if b0 <= lv <= b0 + nb * bw:
            ax.plot([x0 - 6, x0 + length], [lv, lv], color=CLV, lw=0.9 * WLV, ls=ls, alpha=0.85)
            ax.text(x0 - 6.6, lv, f'{nm} {od}', color=CLV, fontsize=fs, ha='right', va='center')
    ctx = ' · '.join(x for x in [('above PDH' if z[0] else ''), ('below PDL' if z[1] else ''), (f'{z[2]:.1f} ADR under MO' if z[2] > 0 else f'{z[3]:.1f} ADR over MO' if z[3] > 0 else ''), ('at the ATH' if z[4] else '')] if x) or 'inside PD range, at MO'
    if mob:
        hdr = (f'SBZ NQ · 17:00 next\nhist ▲{100 * (1 - cdf(P)):.0f}% · {h10:,.2f}–{h90:,.2f}\nimpl ×{(i90 - i10) / (h90 - h10):.1f} · ctx ×{sCtx:.2f}')
    else:
        hdr = (f"SENBONZAKURA · NQ · next session's close (17:00)\nhistorical  up {100 * (1 - cdf(P)):.0f}% · 80% {h10:,.2f} – {h90:,.2f}\n"
               f'implied (VXN {iv:.1f})  80% {i10:,.2f} – {i90:,.2f} · {(i90 - i10) / (h90 - h10):.1f}× wider\ncontext  width ×{sCtx:.2f} · {ctx}\n' + ' · '.join(lvT))
    ax.text(x0, b0 + nb * bw + bw, hdr, color=TX, fontsize=fs, family=MONO, va='bottom', ha='left', bbox=dict(boxstyle='round,pad=0.4', fc='#161a23', ec='#2a2f3a'))
    return b0, b0 + nb * bw, x0 + length

B = pd.read_pickle('/home/claude/kyw/bars_NQ_all.pkl')
B = B[(B.ts >= '2026-09-24 18:00') & (B.ts < '2026-10-09 17:00')].set_index('ts')
H1 = B[['Open', 'High', 'Low', 'Close']].resample('1h').agg({'Open': 'first', 'High': 'max', 'Low': 'min', 'Close': 'last'}).dropna()
H1['tday'] = B.tday.resample('1h').last().reindex(H1.index)
def candles(ax, Dv):
    for i, (t, r) in enumerate(Dv.iterrows()):
        c = UPC if r.Close >= r.Open else DNC
        ax.plot([i, i], [r.Low, r.High], color=c, lw=0.7); ax.add_patch(Rectangle((i - .35, min(r.Open, r.Close)), .7, max(abs(r.Close - r.Open), 1), fc=c, ec=c, lw=0.3))

def senkei(ax, Dv, n, nah, off, gx, hw, mob, fs):
    Ex = E.reindex(pd.DatetimeIndex(Dv.tday), method='ffill')
    for j, col in enumerate(E.columns[:6]): ax.plot(range(n), Ex[col].values, color=LINES[j], lw=1.8 if j == 0 else 1.0)
    ks = list(C.keys())[:nah]; x0 = n - 1 + off; xR = x0 + gx * (len(ks) - 1) + 6; xL = max(0, n - (60 if mob else 300))
    ax.add_patch(Rectangle((xL, lo0), xR - xL, 0.25, fc=TX, alpha=0.07, ec='none'))
    ax.text(xL + 0.5, lo0 + 0.01, ('' if mob else 'target now ') + '375–400', color=MU, fontsize=fs - 0.5, va='bottom')
    grad = lambda p: tuple(np.array(to_rgb(GH)) * min(1, p / 0.6) + np.array(to_rgb(BG)) * (1 - min(1, p / 0.6)))
    mids = lo0 + 0.125 + 0.25 * np.arange(8); px, py = [n - 1], [base]
    for j, k in enumerate(ks):
        xc = x0 + gx * j; Pp = np.array(C[k]) / 100
        for b_, p in enumerate(Pp):
            if p < 0.01: continue
            ax.add_patch(Rectangle((xc - hw, lo0 + 0.25 * b_), 2 * hw, 0.25, fc=grad(p), ec=BG, lw=0.8))
            if p >= (0.10 if mob else 0.04): ax.text(xc, lo0 + 0.25 * b_ + 0.125, f'{100 * p:.0f}%', color='#ffffff' if p >= 0.3 else TX, fontsize=fs - 1.5, ha='center', va='center', family=MONO)
        m = float((Pp * mids[:len(Pp)]).sum() / Pp.sum()); px.append(xc); py.append(m); ax.plot(xc, m, 'o', color=TX, ms=3, zorder=6)
    ax.plot(px, py, color=TX, lw=1.6, alpha=0.85, zorder=5)
    for j, k in enumerate(ks):
        yr = 2026 if j < 2 else 2027; eoy = (j == 1) or (k == '08 DEC'); xc = x0 + gx * j; mm = py[j + 1]
        if mob: txt = f'{k[3:]}\n{100 * (mm - base):+.0f}'
        else: txt = f'{k}\n{100 * (mm - base):+.0f}bp'
        if eoy:
            s = SEP[yr]; ax.plot(xc + hw + 1, s, 'D', color='#ffffff', ms=5 if mob else 6, zorder=7)
            txt += (f'\n◆{100 * (mm - s):+.0f}' if mob else f'\nFed {s:.3f}\nmkt {100 * (mm - s):+.0f}bp')
        ax.text(xc, lo0 - 0.04, txt.replace('-', '−'), color=LINES[j] if j < 6 else SUB, fontsize=fs - 1, ha='center', va='top')
    ax.text(x0, lo0 + 0.25 * 8 + 0.05, '28 OCT · HOLD 78%', color=TX, fontsize=fs + 0.5, ha='center', va='bottom', weight='bold', bbox=dict(boxstyle='round,pad=0.3', fc=NEU, ec='none'))
    if not mob:
        ax.text(xL, lo0 + 0.25 * 8 + 0.05, 'SENKEI · lines: each meeting\'s expected rate, bar by bar · blocks: odds of each target range per meeting · ◆ the Fed\'s dots (SEP 16 Sep 2026)', color=MU, fontsize=fs - 0.5, va='bottom')
    ax.set_ylim(2.8 if not mob else 3.2, lo0 + 0.25 * 8 + 0.2)
    return xR

def render(path, mob):
    nbars = 40 if mob else 115
    Dv = H1.tail(nbars); n = len(Dv)
    if mob:
        fig = plt.figure(figsize=(6.4, 12.4), dpi=110, facecolor='#05070b')
        fig.patches.append(FancyBboxPatch((0.03, 0.01), 0.94, 0.98, boxstyle='round,pad=0,rounding_size=0.05', transform=fig.transFigure, fc='none', ec='#2a2f3a', lw=2, zorder=10))
        ax1 = fig.add_axes([0.07, 0.43, 0.80, 0.47]); ax2 = fig.add_axes([0.07, 0.06, 0.80, 0.35], sharex=ax1)
        fs = 6.4; kx = kage
        fig.text(0.08, 0.925, 'NQ1! · 1h   Senbonzakura · Mobile (Hakuteiken)', color=SUB, fontsize=7.5)
    else:
        fig = plt.figure(figsize=(17, 11.5), dpi=100, facecolor=BG)
        ax1 = fig.add_axes([0.03, 0.42, 0.92, 0.50]); ax2 = fig.add_axes([0.03, 0.05, 0.92, 0.35], sharex=ax1)
        fs = 8
        fig.text(0.03, 0.965, 'Senbonzakura · Full layout: Kageyoshi (where the next close lands, price chart) + Senkei (the Fed path, pane)', color=TX, fontsize=13, weight='bold')
        fig.text(0.03, 0.942, 'NQ1! 1-hour, weekend of 10–11 Oct 2026. Curves: the script\'s maths on 2018–26 NQ data, next session from Friday\'s close; implied: VXN 21.98 (8 Oct, FRED). Pane: CME FedWatch daily values and its 12 Oct table. Level lines at width 3. TradingView will differ.', color=MU, fontsize=8.2)
    for ax in (ax1, ax2): frame(ax)
    candles(ax1, Dv)
    lo, hi, xk = kage(ax1, Dv, n, 3 if mob else 6, 26 if mob else 60, 24 if mob else 40, mob, fs)
    ax1.set_ylim(min(Dv.Low.min(), lo) - 60, max(Dv.High.max(), hi) + (330 if mob else 420))
    xs_ = senkei(ax2, Dv, n, 5 if mob else 10, 4 if mob else 8, 7 if mob else 10, 3 if mob else 4, mob, fs)
    ax1.set_xlim(-1, max(xk + (14 if mob else 30), xs_ + 4))
    plt.setp(ax1.get_xticklabels(), visible=False)
    tk = [i for i, t in enumerate(Dv.index) if t.hour == 9]
    ax2.set_xticks(tk); ax2.set_xticklabels([Dv.index[i].strftime('%a %d') for i in tk], color=MU, fontsize=7)
    plt.savefig(path, dpi=fig.dpi, facecolor=fig.get_facecolor()); plt.close(fig); print(path)
render(sys.argv[1], False); render(sys.argv[2], True)
