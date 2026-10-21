# -*- coding: utf-8 -*-
"""Hand-written READMEs for the indicators that have no TradingView description yet (Markdown bodies, no title)."""

KYOKA = """**Kyōka Suigetsu** (鏡花水月, "Mirror Flower, Water Moon") is named for Sōsuke Aizen's zanpakutō, whose complete hypnosis rules what you perceive. This one works the other way: it shows what is actually typical for this hour, weekday and month, so the day you think you are seeing can be checked against the days that really happened.

It runs in its own pane, on the full trading day (18:00–17:00 ET).

## What it shows

- **Range clock:** today's running range (or net move from the 18:00 open) drawn live against the typical path for each hour of the trading day.
  - The typical path has a median, 25–75 and 10–90 bands, and a neutral zone (the uncertainty of the median).
  - Today's line is coloured by where it sits: above, inside or below the neutral zone.
  - Beneath it, the hour-of-high / low histogram and the session strip share the same time axis.
- **Distributions:** weekday columns, the hour-of-high / low profile and month-of-year seasonality, with every day or year as a dot.
- **Expected range:** today's range forecast from:
  - the last 1, 5 and 22 days' ranges, anchored to the past year;
  - yesterday's move;
  - inside days, holidays, opex Friday and the turn of the month.
  It was fitted on NQ, ES and RTY 2010–2026.
  - A live projection blends the forecast with the range made so far, hour by hour.
  - The chance today's high or low is already in comes from how far price is from them and how much of the day's volatility is still to come. Tested 2025–26 it was well calibrated, and 23–25% sharper than the plain base rate for the hour (NQ 25%, ES 23%, RTY 25%). It needs a chart of 60 minutes or lower.
- **Cards:**
  - **status:** range, ATR, expected and projected range, high / low in, net, hour, month, weekday;
  - **weekdays**, **months** and **hours**.

## How to use

- Built for CME index futures on continuous charts: **NQ1!**, **ES1!** and **RTY1!**. RTY uses its own profile.
- Intraday charts; the live projection and the high / low odds need 60 minutes or lower.

## Credits

- The distribution column layout was inspired by "Day Of Week Price Distribution" by LuxAlgo (CC BY-NC-SA 4.0).
- Written from scratch; no LuxAlgo code is used.
"""

SB = """**Shikai / Bankai Session Map** maps the overnight session onto the New York day.

- **Shikai:** the overnight midpoint as an all-day reference, to 16:59 ET.
- **Bankai:** the same midpoint inside a time-bound New York AM window, to 11:00 ET.

## What it draws

- **Session candles** for Asia, London and New York, drawn to the right of price (15–65 bars out).
- **The overnight midpoint** (18:00 → 09:30) and its **mirror**: the same distance from the 09:30 open on the other side, dotted.
- **Asia and London levels:** 25%, 37.5% and 50% of each session's range.
  - They are retracement levels of the high–low, measured from whichever extreme came last.
  - They change only when the session makes a new high or low.
  - The older body (open–close) method is still a setting.
- **Hot-block midpoints:** the midpoint of each session window's widest finished 30-minute block.
- **Bankai windows** (primary and secondary) and the entry markers.
- Labels within 2.5% of ADR20 of each other share one stacked label.

## The card

- **Header:** mode, date and time, and a pill:
  - FORMING before 09:30;
  - LONG / SHORT (the side into the midpoint);
  - ✓ MID once it is reached;
  - OVER when the window ends without it.
- **MID:** the overnight midpoint and its distance from the 09:30 open, in ADR20 and points.
- **SIDE:** discount (long into the mid) or premium (short into the mid), and whether the tested pull applies.
- **REACH:** the live odds of reaching the midpoint by 16:59 (Shikai) or 11:00 (Bankai), against its mirror; then the time it was reached.
- **MIRROR:** the same distance on the other side of the open.
- **WINDOW** (Bankai): primary or secondary window open, or entries closed, and the minutes to the hard stop.
- **LONDON:** the London high and low taken after 05:00, with times, and live odds for the ones not yet taken.
- **LDN 25%:** London's 25% level, traded or untouched, with the leg (up or down).
- **RANGES:** the Asia, London and New York ranges against a typical day's.
- **REGIME:** London against Asia, as context.
- Before 09:30 it shows the overnight range so far, and the odds if the session opened at the current price.

## What the tests showed

NQ, ES and RTY 1-minute data 2018–26 (6,344 days). Each held in 2018–24 and 2025–26 and on each symbol.

- **The midpoint overall:** reached about as often as its mirror (by 16:59, 76.5% vs 75.6%). It is not a magnet in general.
- **Discount opens** 0.1 ADR or more from the mid reached it 5–6 points more often than an equal level above the open:
  - by 11:00: 53% vs 47% (p 0.002);
  - by 16:59: 69% vs 64% (p 0.01).
- **Premium opens** show no pull.
- **The London high** is taken by 11:00 on 75% of days and by 16:59 on 83%. The low: 71% / 79%. Both: 48% / 62%.
- **London's 25% level** was reached by 11:00 on 91% of days and by 16:59 on 94% (after 05:00). The 37.5%: 90% / 93%. The 50%: 86% / 90%.

## Settings

**View** sits at the top:
- card theme;
- layout (Desktop / Mobile);
- card on/off and position;
- card text;
- chart text size and colour.

Then:
- **Mode** (Shikai or Bankai);
- **sessions**;
- **the midpoint map**;
- **hot-block midpoints**;
- **intraday markers**;
- **session candles**, including the 25 / 37.5 / 50% method and the 37.5% toggle.

## How to use

- Built for **NQ / MNQ**, **ES / MES** and **RTY / M2K** on intraday ETH charts (1-minute in the screenshots).
- If you also run Hadō 99, set Hadō 99's preview offset to 70 or more so its candles sit beyond these session candles.

*Historical frequencies, not guarantees.*
"""

BYAKUGAN = """**Byakugan** reads the 07:00–09:00 ET premarket range and the first presented fair value gap of the session.

## What it draws

**The 7–9 AM range** (07:00–09:00 ET):
- its high, low and midpoint (0.5);
- an optional shaded box;
- levels that run from the range open to the cut-off (11:00 ET by default).

**Extensions** in multiples of the range:
- 1.5, 2.0 and 2.5 in the direction of travel;
- −0.25, −0.5, −1.25 and −1.5 beyond the origin;
- your own custom levels.

**The 09:30 bias:** the open against the midpoint.

**The Asia / London target:** the Asia (20:00–00:00) or London (02:00–05:00) high or low in the bias direction, with its distance zone tagged on the label.

**The first presented FVG:** the first fair value gap of the session (09:30–16:00 by default) that completes within 30 minutes of the open. It is drawn with its CE (50%) and its reflection, the first opposite-direction FVG after it. The FVG can run to:
- the Byakugan cut-off (11:00);
- the session end (16:00);
- the trading day's last candle (16:59);
- the present.

## Settings

**View** sits at the top:
- theme;
- text size and colour;
- label date format and side;
- days to keep;
- how older days fade.

## How to use

- Built for **NQ / MNQ** and **ES / MES**, on intraday charts of 15 minutes or less.
- Theme: Auto follows the chart background. Any colour you pick overrides it.

## Credits

- First presented FVG concept: ICT (Michael J. Huddleston).
- Inspired by "ICT 1st Presented FVG" by tristanlee85; detection written from scratch here.
"""

SOGYO = """**Sōgyo** (双魚) is Model 13: the RTH gap's twin midpoints.

## What it draws

At 09:30 ET:
- **CE1** = (prior 16:14 close + 09:30 open) ÷ 2;
- **CE2** = (prior 16:59 close + 09:30 open) ÷ 2.

The zone between them is drawn and carried right.

## The card

The card reads the gap and the overnight range against the RTH ATR, and grades the zone:
- **GREEN:** valid confluence;
- **RED:** a waypoint to the fill;
- **SPLIT:** the open sits between the two closes, so skip;
- **NEUTRAL:** don't weight it.

**Rows:**
- CE1;
- CE2;
- zone width;
- gap and overnight range in ATR;
- the ATR, with the red threshold.

Every cell has a tooltip. The RTH ATR is read from 15-minute bars, so it works on a 1-minute chart and in Bar Replay.

## Settings

**View** sits at the top:
- theme;
- layout (Desktop / Mobile, a four-row card for a phone);
- card text;
- label text, label colour and date format.

The card can sit in any of eight places and has its own accent colour.

## Credits

- Concepts: ICT (Michael J. Huddleston), consequent encroachment of the RTH gap.
- Written from scratch.
"""

OPENGAPS = """**OpenGaps** maps opening gaps as ICT teaches them. The repo holds the indicator and the library it is built on.

## What it draws

- **NWOG (New Week Opening Gap):** Friday's 17:00 ET close to Sunday's 18:00 ET open.
- **NDOG (New Day Opening Gap):** the 17:00 ET close to the 18:00 ET reopen.
- Each gap shows its edges, its **consequent encroachment** (C.E., 50%) and optional quadrants.
- Each gap's label says whether price has reached the C.E. or filled the gap (traded back to the prior close) since it opened.
- **Event Horizon:** the midpoint of the space between the nearest NWOG above and below price.
- Older gaps fade, and filled ones fade further.
- Full trading day only (18:00–17:00 ET). Intraday charts.

## Files

- `OpenGaps_NWOG_NDOG.pine`: the indicator. It contains the gap engine, so it runs on its own.
- `OpenGaps_library.pine`: the same engine as a Pine library, for larger indicators.
  - Hold a `GapSet` with `var`.
  - Call `update()` on every bar.
  - Call `draw()` / `drawEH()` on the last bar.

## Settings

**View** sits at the top:
- Show (all gaps, or the nearest above and below);
- the labels and their size.

## Credits

- A Pine v6 port and rework of "ICT NWOG/NDOG" by fadizeidan (MPL 2.0).
- The concepts are taught by ICT, Michael J. Huddleston: New Week and New Day Opening Gaps, consequent encroachment and Event Horizon.
- Not affiliated with or endorsed by either.
"""

GENJUTSU = """**Genjutsu Kai** (幻術解, "Genjutsu Release") is named for the technique that breaks an illusion. A run on one index can be an illusion: a high or low taken that the other index refuses to confirm.

Genjutsu Kai compares your chart with its sister market (NQ ↔ ES by default) in the regular session.

## What it draws

- **Each SMT** (crack in correlation, ICT) as a trendline from the reference high or low to the new extreme.
- **A ghost** of the other market's move, scaled onto your chart.
- **The lag:** the gap at the end of the ghost, showing how far the trailing market (the sick sister) is behind, in points and %.
- **The outcome:** each SMT either syncs (the sister takes its level too, so the move continues on both) or holds to the end of its window (the divergence stood).
- **References:**
  - 30-minute ranges;
  - hourly ranges anchored to 09:30;
  - the opening range (09:30–10:00, checked to 16:00).
- SMTs are only checked in RTH, 09:30–16:00 ET.

## HYDRA heads

Fitted on NQ / ES 1-minute data 2018–24, with a locked test on 2025–26:
- **sync odds:** the chance the sick sister still takes its level before the window ends, from its distance, its volatility and the time left;
- **a roll-week flag.**

## How to use

- Pairs itself on continuous charts (NQ1! ↔ ES1!) and single-contract charts (NQZ2026 ↔ ESZ2026).
- **View** sits at the top of the settings: theme and card text.

## Credits

- SMT, sick sister and opening range concepts are taught by ICT (Michael J. Huddleston).
- The trendline idea is inspired by "SMT Divergences" by LuxAlgo (CC BY-NC-SA 4.0).
- Written from scratch; no LuxAlgo code is used. Not affiliated with or endorsed by either.
"""

KEKKAI = """**Kekkai Barrier** draws each session's walls, the sweeps of those walls, and the structural shifts that follow.

*A confluence map: it draws walls, sweeps and shifts. The Model 4 trade statistics did not survive a re-test, so the indicator makes no trade calls.*

## What it draws

**Session walls:** each session builds the walls the next one hunts. Times are ET and every session is a setting.

| Session | Default time | Role |
|---|---|---|
| Asia | 20:00–00:00 | builds London's walls |
| London | 02:00–05:00 | hunts Asia's walls |
| NY AM | 09:30–11:00 | hunts London's walls |
| NY Lunch | 11:30–13:00 | builds NY PM's walls |
| NY PM | 13:30–16:00 | hunts Lunch's walls |

- Walls run to the last candle, or until their hunt session ends.
- Optional wall midpoints.
- A **compression flag** when a session's range is under 75% of its own 20-session average.

**Day, week and month levels** (exchange day, 18:00 ET start):
- PDH / PDL;
- each day's high / low this week;
- today's high / low so far;
- week and month to date;
- previous week and month.

**Sweeps** are marked on:
- session walls;
- PDH / PDL;
- earlier days this week;
- the previous week and month.

**Shifts:** two consecutive 30-minute blocks (the length is a setting) printing a higher high and higher low (bull), or a lower low and lower high (bear). Each is marked with the sweep that came before it.

**Day-of-week labels** run along the bottom.

## Settings

**View** sits at the top:
- theme;
- text size and colour;
- label date format;
- wall length;
- days to keep;
- how older days fade.

## Credits

- Concepts: ICT (Michael J. Huddleston).
- Written from scratch.
"""

DE = """**Domain Expansion** is Model 1: the London expansion. The London opening range (the *domain*, 02:00–02:30 ET) is graded at 02:30. Its break is then tracked through London and carried into New York.

## What it draws

- **The domain range** (02:00–02:30): its high, low, midpoint and optional shading.
- **The qualifier at 02:30.** The tier comes from:
  - **coiled:** the domain range ÷ the overnight ATR (18:00–02:30) is small;
  - **volatile:** the overnight ATR is large against price;
  - **CBDR wide:** the 14:00–20:00 range is wide.
  The tier is Both / Coiled-or-volatile only / CBDR only / Neither. Every drawing can take the tier's colour.
- **The execution window** (02:30–02:50) and the first break in it, labelled at its candle (e.g. "▲ Break 02:33").
- **SD extensions** in domain-range multiples (1.0, 1.5, 2.0, 2.5, 3.0, 4.0, 5.0 and custom), and the expansion line.
- **The pre-London dealing range** (00:00–00:59): high, low and CE, drawn to 02:00 or 05:00.
- **The London high / low,** carried to 11:00 ET and marked when taken, or "not taken by 11:00".
- **Two text notes a day:** the tier at 02:30, and the 05:00 result with the follow-through (07:00).

## London card

Live from 02:30:
- the domain range and today's tier;
- the expected London range (02:00–04:59), its middle half, and how much of it is done;
- the furthest SD past the range so far;
- the live odds of 2 SD by 04:59;
- how often the London high and low were already in at this time, given price's distance from them.

After 05:00:
- the result;
- the London range against ADR20;
- the follow-through close (07:00);
- whether New York has taken the London high and low.

A second table lists the last 10 London sessions (3–30): tier, result at 05:00, furthest SD and range.

## What the tests showed

NQ, ES and RTY 1-minute data 2018–26: 6,135 London sessions, and 5,526 for the pre-London range. Each held in 2018–24 and 2025–26 and on each symbol.

- **NY AM** took the London high on 66% of sessions and the low on 62%. By 11:00: 75% and 71%.
- **London took the pre-London range's** high on 78% of sessions and its low on 73%:
  - at least one: 99.7%;
  - both: 52%.
- **London traded through the pre-London CE** on 75% of sessions, and on 64% when price sat outside the range at 02:00.
- **The expected range** was fitted on 2018–24 and checked on 2025–26: 48% of sessions landed inside the middle half (R² 0.87).
- Odds are shown only at the default settings they were measured on.

## Alerts

One alert on "Any alert() function call" covers all of these; each can be switched off:
- domain range set, with the tier;
- first break in the execution window;
- expansion line reached;
- the 05:00 result;
- London high or low taken before 11:00.

## Settings

**View** sits at the top:
- card theme;
- text size;
- chart text colour;
- label date format;
- days to keep;
- how older days fade.

The asset setting (NQ by default, or a custom scale) sets the thresholds for other markets.

## Credits

- Concepts: ICT (Michael J. Huddleston), including the CBDR and the London open.
- Written from scratch.

*Historical frequencies, not guarantees.*
"""
