"""Trading-day ADR20 from daily bars (Kyōka's method) for the calendar indicators' clock, stages card and labels.
ADR20 used to come only from 15-minute bars, needing 15 complete trading days of them; a 1-minute chart (or Bar
Replay) often loads fewer, and the clock read "needs 15+ days of history". The daily request (the CME daily bar is the
18:00–17:00 trading day, unadjusted for rolls, like Kyōka's tkU) always has the history, so it is now the source for
the trading day. The 15-minute figure stays as the fallback and for Gran Rey Cero's NY-midnight and RTH anchors, whose
windows a daily bar can't represent.
Idempotent: python3 patch_adr_fallback.py file.pine [...]  (also importable: patch(S) -> S)"""
import re
import sys

MARK = '// ADR20 of the trading day from daily bars'


def patch(S):
    if MARK in S:
        return S
    m = re.search(r'^(\[ADR, ADRtd\]|ADRtd) = request\.security\(syminfo\.tickerid, "15", .*$', S, re.M)
    assert m, 'ADR request not found'
    add = ('\n' + MARK + ' (as Kyōka): a 1-minute chart or Bar Replay often loads fewer than the 15 days of\n'
           '// 15-minute bars the line above needs; the daily bars (the CME 18:00–17:00 trading day) always have them.\n'
           '// The 15-minute figure stays as the fallback' + (' and for the NY-midnight and RTH anchors.' if m.group(1).startswith('[') else '.') + '\n'
           'float adrD = request.security(ticker.modify(syminfo.tickerid, backadjustment = backadjustment.off), "D", ta.sma((high - low) / open, 20)[1], lookahead = barmerge.lookahead_on)\n'
           'ADRtd := na(adrD) ? ADRtd : adrD')
    if m.group(1).startswith('['):
        add += '\nADR := AN == 0 and not na(adrD) ? adrD : ADR'
    return S[:m.end()] + add + S[m.end():]


if __name__ == '__main__':
    for p in sys.argv[1:]:
        s = open(p, encoding='utf-8').read()
        open(p, 'w', encoding='utf-8').write(patch(s))
        print('patched', p)
