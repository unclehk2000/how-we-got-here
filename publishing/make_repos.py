# -*- coding: utf-8 -*-
"""Build one GitHub-ready folder per indicator, plus the publish scripts, under /home/claude/gh/github_repos."""
import os, re, shutil, csv
import readmes as RM
OUT = '/mnt/user-data/outputs'
ROOT = '/home/claude/gh/github_repos'
LIC = '/root/.local/share/uv/tools/black/lib/python3.13/site-packages/pathspec-1.1.1.dist-info/licenses/LICENSE'
ACR = {'CPI', 'NFP', 'FOMC', 'DXY', 'CL', 'RTH', 'ETH', 'SD', 'ICT', 'NY', 'NQ', 'ES', 'RTY', 'VIX', 'FVG', 'CE', 'ATH', 'ADR',
       'PO3', 'AM', 'PM', 'US', 'NWOG', 'NDOG', 'SMT', 'CISD', 'EQ', 'C2', 'C3', 'C4', 'HTF', 'ATR', 'CBDR', 'OR', 'MPL'}

PROPER = {'FED': 'Fed', 'LONDON': 'London', 'ASIA': 'Asia', 'YORK': 'York', 'TRADINGVIEW': 'TradingView'}

# slug, display name, GitHub description (ASCII), .pine files [(src, dst)], readme source, images [(src, dst)]
REPOS = [
    ('hado-99', 'Hadō 99', 'Hado 99: DXY / oil macro regime card and the C2 to C3 Fractal Model with tested odds, for NQ, ES and RTY. TradingView Pine Script v6.',
     [('Hado_99.pine', 'Hado_99.pine')], ('tv', 'Hado_99_TradingView_description.txt'),
     ['Hado99_1m15m_Desktop.png', 'Hado99_1H1D_Desktop.png', 'Hado99_Mobile.png']),
    ('gran-rey-cero', 'Gran Rey Cero', 'Gran Rey Cero: CPI day model for NQ and ES, with tested odds. TradingView Pine Script v6.',
     [('Gran_Rey_Cero.pine', 'Gran_Rey_Cero.pine')], ('tv', 'Gran_Rey_Cero_TradingView_description.txt'),
     ['GranRey_v6_CPI_ext_mock.png', 'GranRey_v5_CPI_structure_mock.png', 'GranRey_mobile_mock.png']),
    ('kyoka-suigetsu', 'Kyōka Suigetsu', 'Kyoka Suigetsu: range clock, weekday / hour / month distributions and expected range for NQ, ES and RTY. TradingView Pine Script v6.',
     [('Kyoka_Suigetsu.pine', 'Kyoka_Suigetsu.pine')], ('md', RM.KYOKA),
     ['Kyoka_RTY_v13_mock.png', 'DayOfWeek/range_clock_mockup.png']),
    ('senbonzakura', 'Senbonzakura', 'Senbonzakura: close probability curves on the price chart and the Fed path, for NQ, ES and RTY. TradingView Pine Script v6.',
     [('Senbonzakura.pine', 'Senbonzakura.pine')], ('tv', 'Senbonzakura_TradingView_description.txt'),
     ['Senbonzakura_full_mock.png', 'Senbonzakura_mock.png', 'Senbonzakura_mobile_mock.png']),
    ('desgarron', 'Desgarrón', 'Desgarron: NFP day model for NQ, ES and RTY, with tested odds. TradingView Pine Script v6.',
     [('Desgarron.pine', 'Desgarron.pine')], ('tv', 'Desgarron_TradingView_description.txt'),
     ['Desgarron_v3_1030_mock.png', 'Desgarron_v3_0704_mock.png', 'Desgarron_v3_mobile_mock.png']),
    ('vizard', 'Vizard', 'Vizard: FOMC day model for NQ and ES, with the Fed card and Fed map. TradingView Pine Script v6.',
     [('Vizard.pine', 'Vizard.pine')], ('tv', 'Vizard_TradingView_description.txt'),
     ['Vizard_v2_FOMC_day_mock.png', 'Vizard_v2_pane_and_cards_mock.png', 'Vizard_Fed_card_mock.png', 'Vizard_v2_mobile_mock.png']),
    ('hollow', 'Hollow', 'Hollow: NFP week and day-after-FOMC model for NQ, ES and RTY. TradingView Pine Script v6.',
     [('Hollow.pine', 'Hollow.pine')], ('tv', 'Hollow_TradingView_description.txt'),
     ['Hollow_v3_FOMC1_mock.png', 'Hollow_v3_NFPweek_mock.png', 'Hollow_v3_mobile_mock.png']),
    ('benihime', 'Benihime', 'Benihime: RTH gap map for NQ, ES and RTY, laid out like NWOGs, with tested fill odds and a news regime. TradingView Pine Script v6.',
     [('Benihime_RTH_Gaps.pine', 'Benihime_RTH_Gaps.pine')], ('tv', 'Benihime_TradingView_description.txt'),
     ['Benihime_RTH_1m.png', 'Benihime_ETH_1m.png', 'Benihime_RTH_5m_20gaps.png']),
    ('shikai-bankai-session-map', 'Shikai / Bankai Session Map', 'Shikai / Bankai Session Map: overnight midpoint, session candles and Asia / London levels for NQ, ES and RTY. TradingView Pine Script v6.',
     [('Shikai_Bankai_Session_Map.pine', 'Shikai_Bankai_Session_Map.pine')], ('md', RM.SB),
     ['SB2_Desktop_Shikai_1m.png', 'SB2_Desktop_Bankai_1m.png', 'SB3_Asia_levels_1m.png', 'SB2_Mobile_1m.png']),
    ('byakugan', 'Byakugan', 'Byakugan: the 7-9 AM range and the first presented FVG for NQ and ES. TradingView Pine Script v6.',
     [('Byakugan_FPFVG.pine', 'Byakugan_FPFVG.pine')], ('md', RM.BYAKUGAN),
     ['Byakugan_to_present_mock.png']),
    ('sogyo', 'Sōgyo', 'Sogyo: the RTH gap twin midpoints (CE1 / CE2 zone) with a graded card. TradingView Pine Script v6.',
     [('Sogyo.pine', 'Sogyo.pine')], ('md', RM.SOGYO),
     ['Sogyo_mock.png']),
    ('opengaps', 'OpenGaps · NWOG / NDOG', 'OpenGaps: New Week and New Day Opening Gaps with C.E., quadrants and Event Horizon; indicator and Pine library. TradingView Pine Script v6.',
     [('OpenGaps_NWOG_NDOG.pine', 'OpenGaps_NWOG_NDOG.pine'), ('OpenGaps_library.pine', 'OpenGaps_library.pine')], ('md', RM.OPENGAPS),
     []),
    ('genjutsu-kai', 'Genjutsu Kai', 'Genjutsu Kai: NQ / ES SMT divergences drawn as trendlines with a ghost of the sister market and sync odds. TradingView Pine Script v6.',
     [('Genjutsu_Kai.pine', 'Genjutsu_Kai.pine')], ('md', RM.GENJUTSU),
     [('/home/claude/gk/mock_v2_20250121_ml02.png', 'Genjutsu_Kai_mock.png')]),
    ('kekkai-barrier', 'Kekkai Barrier', 'Kekkai Barrier: session walls, sweeps and shifts, with day / week / month levels. TradingView Pine Script v6.',
     [('Kekkai_Barrier_Indicator.pine', 'Kekkai_Barrier_Indicator.pine')], ('md', RM.KEKKAI),
     []),
    ('domain-expansion', 'Domain Expansion', 'Domain Expansion: the London expansion model (domain range, overnight ATR and CBDR qualifier) with a London card. TradingView Pine Script v6.',
     [('Domain_Expansion_Indicator.pine', 'Domain_Expansion_Indicator.pine')], ('md', RM.DE),
     ['DE_v10_1min_1115.png', 'DE_v9_live_0340.png']),
    ('hueco-mundo', 'Hueco Mundo', 'Hueco Mundo: the NFP, CPI and FOMC models (Desgarron, Gran Rey Cero, Vizard, Hollow) in one indicator, as Pine libraries. TradingView Pine Script v6.',
     [('Hueco_Mundo.pine', 'Hueco_Mundo.pine'), ('HM_Desgarron.pine', 'libraries/HM_Desgarron.pine'), ('HM_GranRey.pine', 'libraries/HM_GranRey.pine'),
      ('HM_Vizard.pine', 'libraries/HM_Vizard.pine'), ('HM_Hollow.pine', 'libraries/HM_Hollow.pine')], ('hm', 'Hueco_Mundo_TradingView_description.txt'),
     ['Hueco_Mundo_follow_mock.png', 'Hueco_Mundo_settings_mock.png']),
]


def heading(t):
    words = t.split()
    out = []
    for i, w in enumerate(words):
        core = re.sub(r'[^A-Za-z0-9ŌÓĀ]', '', w)
        if core.upper() in ACR or re.fullmatch(r'[0-9]+', core or 'x'):
            out.append(w)
        elif core.upper() in PROPER:
            out.append(w.replace(core, PROPER[core.upper()]))
        else:
            lw = w.lower()
            out.append(lw[:1].upper() + lw[1:] if i == 0 else lw)
    s = ' '.join(out)
    return s.replace('(indicator pane)', '(indicator pane)')


def bb2md(lines):
    """TradingView BBCode description lines → Markdown."""
    md = []
    prev = ''
    for raw in lines:
        l = raw.rstrip()
        m = re.match(r'^\[b\]█\s*(.+?)\[/b\]$', l.strip())
        if m:
            md += ['', '## ' + heading(m.group(1)), '']
            prev = ''
            continue
        l = re.sub(r'\[b\](.*?)\[/b\]', r'**\1**', l)
        l = re.sub(r'\[i\](.*?)\[/i\]', r'*\1*', l)
        l = re.sub(r'^(\s*)• ', r'\1- ', l)
        l = re.sub(r'^(\s+)– ', r'\1- ', l)
        is_item = bool(re.match(r'^\s*(- |\d+\. )', l))
        is_sub = bool(re.match(r'^\s+(- |\d+\. )', l))
        if l.strip() == '':
            md.append('')
            prev = ''
            continue
        if prev != '':
            prev_item = bool(re.match(r'^\s*(- |\d+\. )', prev))
            if not is_item and not prev.startswith('|'):
                md.append('')                      # each loose text line is its own paragraph
            elif is_item and not is_sub and not prev_item:
                md.append('')
        md.append(l)
        prev = l
    s = '\n'.join(md)
    s = re.sub(r'\n{3,}', '\n\n', s).strip() + '\n'
    return s


def tv_desc(path):
    L = open(os.path.join(OUT, path), encoding='utf-8').read().split('\n')
    title = L[1].strip()
    k = next(i for i, l in enumerate(L) if l.startswith('──'))
    return title, bb2md(L[k + 1:])


def hm_desc(path):
    T = open(os.path.join(OUT, path), encoding='utf-8').read().split('\n')
    i = next(j for j, l in enumerate(T) if l.strip() == 'HUECO MUNDO')
    title = next(l for l in T[i:] if l.startswith('TITLE:'))[6:].strip()
    d = next(j for j in range(i, len(T)) if T[j].startswith('DESCRIPTION:'))
    body = bb2md(T[d + 1:])
    order = """## Publishing order on TradingView

Hueco Mundo imports four libraries, kept in `libraries/`. They must exist on TradingView before the indicator compiles.

1. Publish the four libraries from their `.pine` files: `HM_Desgarron`, `HM_GranRey`, `HM_Vizard`, `HM_Hollow` (Pine Editor → open the file → *Publish script* → *Library*).
   - A **public** script can only import **public** libraries. Publish them public if Hueco Mundo will be public.
2. Publish `Hueco_Mundo.pine`.
   - Its imports expect version 1 of each library (`Unclehk2000/HM_Hollow/1`).
   - After you update a library, raise its number in the four import lines at the top.
3. Changes to a module go into its own indicator (Desgarrón, Gran Rey Cero, Vizard, Hollow). The library is regenerated from it and republished as the next version.
"""
    return title, body + '\n' + order


def build():
    if os.path.exists(ROOT):
        shutil.rmtree(ROOT)
    os.makedirs(ROOT)
    rows = []
    for slug, name, desc, pines, src, imgs in REPOS:
        d = os.path.join(ROOT, slug)
        os.makedirs(d)
        for a, b in pines:
            dst = os.path.join(d, b)
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            shutil.copy2(os.path.join(OUT, a), dst)
        shown = []
        for im in imgs:
            a, b = (im if isinstance(im, tuple) else (os.path.join(OUT, im), os.path.basename(im)))
            os.makedirs(os.path.join(d, 'images'), exist_ok=True)
            shutil.copy2(a, os.path.join(d, 'images', b))
            shown.append(b)
        if src[0] == 'tv':
            title, body = tv_desc(src[1])
            tag = title.split(':', 1)[1].strip() if ':' in title else ''
        elif src[0] == 'hm':
            title, body = hm_desc(src[1])
            tag = title.split(':', 1)[1].strip()
        else:
            body = src[1]
            tag = desc.split(':', 1)[1].replace('TradingView Pine Script v6.', '').strip().rstrip('.')
            tag = tag[:1].upper() + tag[1:]
        main = [b for a, b in pines if '/' not in b]
        R = [f'# {name}', '', f'**{tag}**' if tag else '', '',
             'TradingView indicator, Pine Script v6. Open source under the Mozilla Public License 2.0.', '']
        if shown:
            R += [f'![{name}](images/{shown[0]})', '', '*Mock-up of how it looks on the chart.*', '']
        R += [body.strip(), '']
        R += ['## Add it to TradingView', '']
        if slug == 'hueco-mundo':
            R += ['Follow the publishing order above: the four libraries first, then `Hueco_Mundo.pine`.', '']
        else:
            R += ['1. In TradingView, open the **Pine Editor** (bottom panel).',
                  f'2. Copy the contents of `{main[0]}` into a new script.',
                  '3. **Save**, then **Add to chart**.', '']
            if slug == 'opengaps':
                R += ['`OpenGaps_library.pine` is only needed if you build your own indicator on the gap engine: publish it as a library, then `import` it.', '']
        if len(shown) > 1:
            R += ['## More screenshots', '']
            for s in shown[1:]:
                R += [f'![{s}](images/{s})', '']
        R += ['## License', '',
              'Mozilla Public License 2.0, see [LICENSE](LICENSE). © Unclehk2000.', '',
              '*Historical frequencies, not guarantees. Nothing here is financial advice.*', '']
        txt = '\n'.join(R)
        txt = re.sub(r'\n{3,}', '\n\n', txt)
        open(os.path.join(d, 'README.md'), 'w', encoding='utf-8').write(txt)
        shutil.copy2(LIC, os.path.join(d, 'LICENSE'))
        rows.append((slug, desc, name))
    with open(os.path.join(ROOT, 'repos.csv'), 'w', newline='', encoding='utf-8') as f:
        w = csv.writer(f)
        w.writerow(['slug', 'description'])
        for slug, desc, name in rows:
            w.writerow([slug, desc])
    return rows


if __name__ == '__main__':
    rows = build()
    for r in rows:
        print(r[0])
