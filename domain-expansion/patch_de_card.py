"""Domain Expansion v8: London card, live odds, NY carry, recent sessions, alerts. Applies to DE_v7_before_card.pine."""
import json
P = json.load(open('/home/claude/dx/lon_pine.json'))
SRC = '/home/claude/dx/DE_v7_before_card.pine'
OUT = '/home/claude/dx/Domain_Expansion_Indicator.pine'
s = open(SRC, encoding='utf-8').read()


def rep(a, b, cnt=1):
    global s
    assert s.count(a) == cnt, (s.count(a), a[:90])
    s = s.replace(a, b)


POS8 = '["Top left", "Top center", "Top right", "Middle left", "Middle right", "Bottom left", "Bottom center", "Bottom right"]'
exec(open('/home/claude/dx/de_card_blocks.py', encoding='utf-8').read())
open(OUT, 'w', encoding='utf-8').write(s)
print('written', len(s.split('\n')), 'lines')
