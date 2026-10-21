"""One panel per indicator: the top of its settings (the View section), read from each script."""
import re, matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Rectangle
BG, TX, MU, ED = '#1e1e1e', '#e8e8e8', '#8a8a8a', '#5a5a5a'
names = [('Desgarrón', '/home/claude/hm/calgen/Desgarron.pine', 'grpW'), ('Vizard', 'Vizard.pine', 'grpW'), ('Hollow', 'Hollow.pine', 'grpW'),
         ('Gran Rey Cero', 'Gran_Rey_Cero.pine', 'grpW'), ('Senbonzakura', 'Senbonzakura.pine', 'grpG'), ('Kyōka Suigetsu', 'Kyoka_Suigetsu.pine', 'gV'),
         ('Genjutsu Kai', 'Genjutsu_Kai.pine', 'gV'), ('Hueco Mundo', 'Hueco_Mundo.pine', 'gV'), ('OpenGaps', 'OpenGaps_NWOG_NDOG.pine', 'gV'),
         ('Domain Expansion', 'Domain_Expansion_Indicator.pine', 'g_D'), ('Byakugan', 'Byakugan_FPFVG.pine', 'g_D'), ('Kekkai', 'Kekkai_Barrier_Indicator.pine', 'g_D'),
         ('SB Map', 'Shikai_Bankai_Session_Map.pine', 'g_D')]
def rows(path, g):
    out = []
    for l in open(path, encoding='utf-8'):
        m = re.match(r'^\s*\w+\s*=\s*input\.(\w+)\((.*)\)\s*$', l.rstrip())
        if not m or f'group = {g}' not in l: continue
        kind, args = m.groups()
        defv = re.match(r'\s*("([^"]*)"|[^,]+)', args).group(0).strip()
        tit = re.findall(r'"([^"]*)"', args); title = tit[1] if kind in ('string',) and len(tit) > 1 else (tit[0] if tit else '')
        if kind == 'string': title = tit[1] if len(tit) > 1 else ''
        inl = 'inline =' in l and 'tooltip' not in l and kind != 'bool'
        out.append((kind, title, defv.strip('"'), 'tooltip =' in l))
    return out
fig = plt.figure(figsize=(18, 13.5), dpi=100, facecolor='#131313')
fig.text(0.012, 0.975, 'View at the top of every indicator · the first settings section, read from each script', color=TX, fontsize=15, weight='bold')
cols = 5
for k, (nm, path, g) in enumerate(names):
    r, c = divmod(k, cols)
    x0, y0, w, h = 0.012 + c * 0.197, 0.94 - (r + 1) * 0.31, 0.188, 0.295
    ax = fig.add_axes([x0, y0, w, h]); ax.set_xlim(0, 380); ax.set_ylim(560, 0); ax.axis('off')
    ax.add_patch(FancyBboxPatch((0, 0), 380, 560, boxstyle='round,pad=0,rounding_size=10', fc=BG, ec='#333'))
    ax.text(14, 28, nm, color=TX, fontsize=11.5, weight='bold', va='center')
    ax.text(14, 62, 'Inputs', color=TX, fontsize=9.5, weight='bold', va='center'); ax.text(75, 62, 'Style', color=TX, fontsize=9.5, va='center'); ax.text(125, 62, 'Visibility', color=TX, fontsize=9.5, va='center')
    ax.add_patch(Rectangle((0, 76), 380, 3, color='#4a4a4a')); ax.add_patch(Rectangle((0, 76), 52, 3, color='#ffffff'))
    ax.text(14, 104, 'VIEW', color=MU, fontsize=8, va='center')
    y = 104
    for kind, title, dv, tp in rows(path, g)[:10]:
        y += 42
        if kind == 'bool':
            ax.add_patch(FancyBboxPatch((14, y - 9), 18, 18, boxstyle='round,pad=0,rounding_size=3', fc='#f0f0f0' if dv == 'true' else BG, ec=ED))
            if dv == 'true': ax.text(23, y, '✓', color=BG, fontsize=8, ha='center', va='center', weight='bold')
            ax.text(40, y, title[:34], color=TX, fontsize=8.6, va='center')
        else:
            ax.text(14, y, title if title else '—', color=TX, fontsize=8.6, va='center')
            if kind == 'color':
                ax.add_patch(FancyBboxPatch((250, y - 14), 30, 28, boxstyle='round,pad=0,rounding_size=4', fc='#000000' if dv.startswith('#000001') else '#9e9e9e', ec=ED))
            else:
                ax.add_patch(FancyBboxPatch((200, y - 15), 128, 30, boxstyle='round,pad=0,rounding_size=6', fc=BG, ec=ED))
                ax.text(210, y, (dv[:15] + '…') if len(dv) > 16 else dv, color=TX, fontsize=8.2, va='center')
        if tp: ax.add_patch(plt.Circle((350, y), 8, color='#5a5a5a')); ax.text(350, y, 'i', color=BG, fontsize=6.5, ha='center', va='center', weight='bold')
plt.savefig('View_sections_mock.png', dpi=100, facecolor='#131313'); print('ok')
