"""Hueco Mundo mocks: (1) which module the cards and pane follow, trading day by trading day, Oct–Nov 2026, with each
module's look; (2) the settings. python3 mock_hm.py out_follow.png out_settings.png"""
import sys, re, datetime as dt
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Rectangle
from PIL import Image
OUT = sys.argv[1:3]
S = open('/home/claude/hm/Hollow.pine', encoding='utf-8').read()
def dates(name):
    i = S.index(name + ' ')
    j = S.index('\n', S.index('"', i))
    k = i
    blk = []
    for line in S[i:].split('\n'):
        if blk and not line.lstrip().startswith('+'):
            break
        blk.append(line)
    return sorted(dt.date(int(x[:4]), int(x[4:6]), int(x[6:])) for x in re.findall(r'20\d{6}', '\n'.join(blk)))
FO, CP, NP = dates('S_FOMC'), dates('S_CPI'), dates('S_NFP')
nextOf = lambda a, d: next((x for x in a if x >= d), None)
add = lambda d, n: d + dt.timedelta(days=n)
pdow = lambda d: (d.weekday() + 1) % 7 + 1          # Pine dayofweek: Sunday 1 … Saturday 7

def prevTD(d):
    p = add(d, -1)
    while p.weekday() >= 5:
        p = add(p, -1)
    return p

def hollowDay(k):
    dw = pdow(k)
    return 2 <= dw <= 5 and any(add(k, j) in NP for j in range(1, 7 - dw))

def nd_D(d): return d if d in NP else nextOf(NP, d)
def nd_G(d): return d if d in CP else nextOf(CP, d)
def nd_V(d):
    if d in FO or add(d, 1) in FO:
        return d
    f = nextOf(FO, d)
    f2 = f if add(f, -1) >= d else nextOf(FO, add(f, 1))
    return add(f2, -1)
def nd_H(d):
    if prevTD(d) in FO or hollowDay(d):
        return d
    n = nextOf(NP, add(d, 1))
    m = max(add(n, 2 - pdow(n)), d)
    f = nextOf(FO, d)
    p = add(f, 3 if pdow(f) == 6 else 1)
    return m if m <= p else p

MODS = [('Desgarrón', 'NFP day', '#ff7043', nd_D), ('Gran Rey Cero', 'CPI', '#e53935', nd_G),
        ('Vizard', 'FOMC day / day 1', '#ab47bc', nd_V), ('Hollow', 'NFP week / FOMC +1', '#26a69a', nd_H)]
BG, TX, SUB, MU, BODY = '#0e1117', '#e6e9ef', '#9aa3b5', '#5d6476', '#161a23'

days = [d for d in (add(dt.date(2026, 10, 12), i) for i in range(33)) if d.weekday() < 5]
fol = []
for d in days:
    ks = [(f(d), i) for i, (_, _, _, f) in enumerate(MODS)]
    best = min(ks)
    fol.append((best[1], best[0] == d, best[0]))

fig = plt.figure(figsize=(18, 13.2), dpi=100, facecolor=BG)
fig.text(0.02, 0.972, 'Hueco Mundo · which module the cards and pane follow, trading day by trading day (Oct–Nov 2026)', color=TX, fontsize=15, weight='bold')
fig.text(0.02, 0.952, 'The module whose day is today or comes next; ties go Desgarrón → Gran Rey Cero → Vizard → Hollow. Each module still draws its structure on its own days. "Cards follow" in View pins one module.',
         color=SUB, fontsize=9.5)
ax = fig.add_axes([0.02, 0.73, 0.96, 0.2]); ax.set_xlim(0, len(days)); ax.set_ylim(0, 3.4); ax.axis('off')
for i, (d, (mi, today, k)) in enumerate(zip(days, fol)):
    name, what, col, _ = MODS[mi]
    ax.add_patch(FancyBboxPatch((i + 0.06, 0.95), 0.88, 1.5, boxstyle='round,pad=0,rounding_size=0.08', fc=col if today else BODY, ec=col, lw=1.6))
    ax.text(i + 0.5, 2.18, d.strftime('%a'), color='#ffffff' if today else SUB, fontsize=8, ha='center', va='center')
    ax.text(i + 0.5, 1.86, d.strftime('%d %b'), color='#ffffff' if today else TX, fontsize=8.5, ha='center', va='center', weight='bold')
    ax.text(i + 0.5, 1.45, name.replace('Gran Rey Cero', 'G. Rey'), color='#ffffff' if today else col, fontsize=7.6, ha='center', va='center', weight='bold')
    ax.text(i + 0.5, 1.13, 'TODAY' if today else 'in %dd' % (k - d).days, color='#ffffff' if today else MU, fontsize=7.2, ha='center', va='center')
    ev = []
    if d in NP: ev.append('NFP')
    if d in CP: ev.append('CPI')
    if d in FO: ev.append('FOMC')
    if add(d, 1) in FO: ev.append('D1')
    if prevTD(d) in FO: ev.append('F+1')
    if prevTD(d) in CP and d not in CP: ev.append('CPI+1')
    if hollowDay(d) and d not in NP: ev.append('NFPwk')
    if ev:
        ax.text(i + 0.5, 0.62, ' · '.join(ev), color=TX, fontsize=7.4, ha='center', va='center')
ax.text(0, 3.05, 'Filled = the module\'s own day (its stages card reads TODAY). Outline = the next module\'s day, counting down. Bottom row: what the day is.', color=MU, fontsize=8.5)
thumbs = [('/mnt/user-data/outputs/Desgarron_v3_1030_mock.png', 0), ('/mnt/user-data/outputs/GranRey_v5_CPI_structure_mock.png', 1),
          ('/mnt/user-data/outputs/Vizard_v2_FOMC_day_mock.png', 2), ('/mnt/user-data/outputs/Hollow_v3_FOMC1_mock.png', 3)]
for j, (p, mi) in enumerate(thumbs):
    im = Image.open(p)
    w, h = im.size
    im = im.crop((0, int(0.07 * h), w, h))
    x0 = 0.02 + (j % 2) * 0.49; y0 = 0.37 - (j // 2) * 0.355
    a2 = fig.add_axes([x0, y0, 0.47, 0.32]); a2.imshow(im, aspect='auto'); a2.axis('off')
    name, what, col, _ = MODS[mi]
    fig.add_artist(Rectangle((x0, y0 + 0.32), 0.47, 0.022, transform=fig.transFigure, fc=col, ec='none'))
    fig.text(x0 + 0.006, y0 + 0.331, '%s · %s: what Hueco Mundo shows when it follows %s' % (name, what, name), color='#ffffff', fontsize=9.5, weight='bold', va='center')
plt.savefig(OUT[0], dpi=100, facecolor=BG); plt.close(fig); print(OUT[0])

# ── settings
BG2, TX2, MU2, BOX, ED = '#1e1e1e', '#e8e8e8', '#8a8a8a', '#1e1e1e', '#5a5a5a'
fig = plt.figure(figsize=(7.3, 15.8), dpi=100, facecolor=BG2)
ax = fig.add_axes([0, 0, 1, 1]); ax.set_xlim(0, 730); ax.set_ylim(1580, 0); ax.axis('off')
ax.text(20, 30, 'Hueco Mundo', color=TX2, fontsize=17, weight='bold', va='center'); ax.text(705, 30, '✕', color=TX2, fontsize=16, va='center', ha='center')
for x, t in ((20, 'Inputs'), (125, 'Style'), (215, 'Visibility')):
    ax.text(x, 85, t, color=TX2, fontsize=13.5, weight='bold' if t == 'Inputs' else 'normal', va='center')
ax.add_patch(Rectangle((0, 112), 730, 4, color='#4a4a4a')); ax.add_patch(Rectangle((0, 112), 88, 4, color='#ffffff'))
def sel(y, txt, w=170, x=475):
    ax.add_patch(FancyBboxPatch((x, y - 20), w, 40, boxstyle='round,pad=0,rounding_size=8', fc=BOX, ec=ED, lw=1.2))
    ax.text(x + 14, y, txt, color=TX2, fontsize=11.5, va='center'); ax.text(x + w - 18, y, '⌄', color=TX2, fontsize=12, va='center', ha='center')
def info(y, x=672):
    ax.add_patch(plt.Circle((x, y), 10, color='#5a5a5a')); ax.text(x, y, 'i', color=BG2, fontsize=9, ha='center', va='center', weight='bold')
def chk(y, t, x=20, on=True):
    ax.add_patch(FancyBboxPatch((x, y - 11), 22, 22, boxstyle='round,pad=0,rounding_size=4', fc='#f0f0f0' if on else BOX, ec='#8a8a8a'))
    if on:
        ax.text(x + 11, y, '✓', color=BG2, fontsize=12, ha='center', va='center', weight='bold')
    ax.text(x + 34, y, t, color=TX2, fontsize=12, va='center')
def head(y, t): ax.text(20, y, t, color=MU2, fontsize=10.5, va='center')
y = 160; head(y, 'VIEW')
for lab, val in (('Pane', 'Clock + findings'), ('Cards follow', 'Next event'), ('Clock measure', 'Range'), ('Theme', 'Auto'), ('Layout', 'Desktop'), ('Card text', 'Small')):
    y += 52; ax.text(20, y, lab, color=TX2, fontsize=12.5, va='center'); sel(y, val); info(y)
y += 70; head(y, 'MODULES')
for t in ('Desgarrón', 'Gran Rey Cero', 'Vizard', 'Hollow'):
    y += 40; chk(y, t); info(y)
y += 62; head(y, 'EVENT DAY')
y += 48; ax.text(20, y, 'Day', color=TX2, fontsize=12.5, va='center'); sel(y, 'Trading day (18:00)', 200); info(y)
y += 46; chk(y, 'Mark releases   and model structure for the last (days)  90')
y += 62; head(y, 'CARDS')
for t, v in (('Event tally', 'Top right   last 12'), ('Stages card', 'Price chart · Bottom left'), ('Clock card', 'Indicator pane · Top right')):
    y += 42; chk(y, t); ax.text(240, y, v, color=SUB, fontsize=11, va='center')
y += 42; ax.text(20, y, 'Findings table', color=TX2, fontsize=12.5, va='center'); sel(y, 'Top left'); info(y)
y += 62; head(y, 'EVENT CLOCK  ·  DATA')
y += 40; chk(y, '10–90 and 25–75 bands   ·   Reference path   ·   Earlier days, faded')
y += 40; ax.text(20, y, 'DXY TVC:DXY · VIX CBOE:VIX · 10Y TVC:US10Y · Fed funds CBOT:ZQ', color=TX2, fontsize=11, va='center'); info(y)
y += 62; head(y, 'ONE SECTION PER MODULE, AS IN ITS OWN INDICATOR')
for t in ('DESGARRÓN · MODEL STRUCTURE', 'GRAN REY CERO · MODEL STRUCTURE · PO3 CANDLES · CARDS', 'VIZARD · MODEL STRUCTURE · FED MAP · FED ODDS',
          'HOLLOW · MODEL STRUCTURE · SHIROSAKI'):
    y += 36; ax.text(36, y, t, color=TX2, fontsize=10.5, va='center')
ax.add_patch(Rectangle((0, 1500), 730, 1, color='#3a3a3a'))
ax.add_patch(FancyBboxPatch((20, 1515), 148, 46, boxstyle='round,pad=0,rounding_size=8', fc=BOX, ec=ED)); ax.text(42, 1538, 'Defaults  ⌄', color=TX2, fontsize=12, va='center')
ax.add_patch(FancyBboxPatch((500, 1515), 108, 46, boxstyle='round,pad=0,rounding_size=8', fc=BOX, ec='#e8e8e8')); ax.text(554, 1538, 'Cancel', color=TX2, fontsize=12, va='center', ha='center')
ax.add_patch(FancyBboxPatch((625, 1515), 85, 46, boxstyle='round,pad=0,rounding_size=8', fc='#f0f0f0', ec='none')); ax.text(667, 1538, 'Ok', color=BG2, fontsize=12, va='center', ha='center')
plt.savefig(OUT[1], dpi=100, facecolor=BG2); plt.close(fig); print(OUT[1])
for d, (mi, today, k) in zip(days, fol):
    print(d, MODS[mi][0], 'TODAY' if today else k)
