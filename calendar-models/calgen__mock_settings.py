import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Rectangle
BG, TX, MU, BOX, ED = '#1e1e1e', '#e8e8e8', '#8a8a8a', '#1e1e1e', '#5a5a5a'
fig = plt.figure(figsize=(7.3, 9.4), dpi=100, facecolor=BG)
ax = fig.add_axes([0, 0, 1, 1]); ax.set_xlim(0, 730); ax.set_ylim(940, 0); ax.axis('off')
ax.text(20, 30, 'Desgarrón', color=TX, fontsize=17, weight='bold', va='center'); ax.text(705, 30, '✕', color=TX, fontsize=16, va='center', ha='center')
for x, t in ((20, 'Inputs'), (125, 'Style'), (215, 'Visibility')): ax.text(x, 85, t, color=TX, fontsize=13.5, weight='bold' if t == 'Inputs' else 'normal', va='center')
ax.add_patch(Rectangle((0, 112), 730, 4, color='#4a4a4a')); ax.add_patch(Rectangle((0, 112), 88, 4, color='#ffffff'))
def sel(y, txt, w=150, x=495):
    ax.add_patch(FancyBboxPatch((x, y - 22), w, 44, boxstyle='round,pad=0,rounding_size=8', fc=BOX, ec=ED, lw=1.2))
    ax.text(x + 14, y, txt, color=TX, fontsize=12, va='center'); ax.text(x + w - 18, y, '⌄', color=TX, fontsize=12, va='center', ha='center')
def info(y, x=670): ax.add_patch(plt.Circle((x, y), 10, color='#5a5a5a')); ax.text(x, y, 'i', color=BG, fontsize=9, ha='center', va='center', weight='bold')
def chk(y, t, x=20):
    ax.add_patch(FancyBboxPatch((x, y - 12), 24, 24, boxstyle='round,pad=0,rounding_size=4', fc='#f0f0f0', ec='none')); ax.text(x + 12, y, '✓', color=BG, fontsize=11, ha='center', va='center', weight='bold')
    ax.text(x + 38, y, t, color=TX, fontsize=12.5, va='center')
y = 175; ax.text(20, y, 'VIEW', color=MU, fontsize=10.5, va='center')
for lab, val, inf in (('Pane', 'Clock + Gri…', True), ('Clock measure', 'Range', True), ('Theme', 'Auto', True), ('Layout', 'Desktop', True), ('Card text', 'Small', False)):
    y += 68; ax.text(20, y, lab, color=TX, fontsize=13, va='center'); sel(y, val)
    if inf: info(y)
y += 85; ax.text(20, y, 'EVENT DAY', color=MU, fontsize=10.5, va='center')
y += 60; ax.text(20, y, 'Day', color=TX, fontsize=13, va='center'); sel(y, 'Trading day …', 165, 80); info(y, 270)
y += 62; chk(y, 'Mark releases   and model structure for the last (days)'); ax.add_patch(FancyBboxPatch((580, y - 22), 120, 44, boxstyle='round,pad=0,rounding_size=8', fc=BOX, ec=ED)); ax.text(594, y, '90', color=TX, fontsize=12, va='center')
y += 85; ax.text(20, y, 'MODEL STRUCTURE', color=MU, fontsize=10.5, va='center')
y += 55; chk(y, "Draw the model's levels and windows")
ax.add_patch(Rectangle((0, 860), 730, 1, color='#3a3a3a'))
ax.add_patch(FancyBboxPatch((20, 875), 148, 48, boxstyle='round,pad=0,rounding_size=8', fc=BOX, ec=ED)); ax.text(42, 899, 'Defaults  ⌄', color=TX, fontsize=12.5, va='center')
ax.add_patch(FancyBboxPatch((500, 875), 108, 48, boxstyle='round,pad=0,rounding_size=8', fc=BOX, ec='#e8e8e8')); ax.text(554, 899, 'Cancel', color=TX, fontsize=12.5, va='center', ha='center')
ax.add_patch(FancyBboxPatch((625, 875), 85, 48, boxstyle='round,pad=0,rounding_size=8', fc='#f0f0f0', ec='none')); ax.text(667, 899, 'Ok', color=BG, fontsize=12.5, va='center', ha='center')
plt.savefig('mocks2/settings_view.png', dpi=100, facecolor=BG); print('ok')
