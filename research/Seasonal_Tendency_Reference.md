# Seasonal Tendency Analysis — Gold & Silver Reference Doc

---

## The Core Method

Seasonal tendency analysis overlays long-term historical price behavior against the calendar to identify whether a given market has a repeating tendency to rally or decline during specific stretches of the year.

**Dual-lookback cross-check:** the standard approach plots two lookback windows together — commonly a **15-year average** and a **40-year average** — for the same calendar period. When the shorter and longer lookback windows agree on direction, that agreement is treated as a stronger signal than either one alone. If they diverge from each other, the seasonal read is considered weaker or unreliable for that market/period.

**How it's meant to be used:** build a running list of seasonal expectations by month for each market you follow. At the start of each month, note what the seasonal tendency implies (bullish, bearish, or no strong tendency), then weigh that alongside your other analysis — positioning data, technical structure, macro context — rather than trading the seasonal read in isolation.

---

## Explicit Framing — What Seasonal Tendency Is NOT

This is worth stating as clearly as the method itself:

- **Not a standalone system.** Seasonal tendency is described as a "road map" — a normal expectation for price behavior during that time of year, not an absolute rule.
- **Not immune to override.** Fundamental factors (a drought creating a supply shock, a demand surge, a structural regime shift) can completely override a seasonal norm in any given year.
- **Not something to force.** If a market isn't behaving in line with its seasonal tendency, the correct response isn't to assume the tendency will "catch up" — it's to treat the divergence itself as new information (see below).
- **Validated by depth of study, not blind trust.** The method explicitly calls for checking the tendency against as much historical data as you can access — not just a handful of recent years — precisely because a shallow sample can look consistent by coincidence.

---

## The Real Signal: Divergence From the Seasonal Norm

The most information-dense part of this method isn't "the seasonal tendency happened" — it's **when it doesn't.**

If a market seasonally should be declining during a given stretch but instead holds firm or rallies, that's read as a sign of unusual underlying strength overriding the normal seasonal pull (and the mirror case for unexpected weakness during a seasonally bullish stretch). This is conceptually the same logic as an accumulation/distribution divergence — the market "should" be doing one thing based on a normal baseline, and its refusal to do so is itself the tradeable information.

**Practical rule of thumb from the source material:** if the seasonal tendency isn't showing up, ask what that implies — either the market is moving into a long-term consolidation (lower opportunity), or it's revealing a genuinely strong opposing force (higher-quality opportunity in the *other* direction than the seasonal norm would suggest).

---

## Gold & Silver: Testing the Seasonal Claims Against Real Data

The source material's specific seasonal read for gold and silver, in brief: both are framed primarily as **buy-side markets**, with the expected seasonal low forming in the **July–August** window. For gold specifically, the reasoning given ties back to physical demand mechanics — jewelry manufacturing and retail buildup ahead of the Christmas/New Year selling season requires gold to be mined, processed, and turned into finished product months in advance, which is offered as the underlying driver of a mid-summer low. Silver is treated similarly (July–August low), with an additional note that silver has historically been prone to entering a multi-year parabolic bull phase roughly once every 10–12 years, making its seasonal low-buying window a potentially higher-payoff setup when that larger cycle aligns.

**Below, that claim is tested directly against 16 years of actual monthly return data (2010–2025) for Gold Dec '26 and Silver Sep '26 contracts**, using one-sample t-tests per month rather than just eyeballing a heatmap of average returns.

### Gold — statistically the stronger seasonal case of the two metals

| Rank | Month | Avg return | t-stat | p-value | % positive years | Significance |
|---|---|---|---|---|---|---|
| 1 | **August** | +44.4 | 2.43 | **0.028** | 75% | ** |
| 2 | **January** | +40.0 | 2.14 | **0.049** | 62% | ** |
| 3 | April | +32.1 | 1.83 | 0.087 | 62% | * |
| 4 | October | +28.7 | 1.82 | 0.088 | 56% | * |
| — | July | +24.9 | 1.44 | 0.172 | 62% | not significant |

**Verdict on the "July/August low, buy-side market" claim, for gold:** partially supported, but the emphasis is off. **August is genuinely the single most statistically significant seasonal month for gold in this dataset** — that part holds up strongly (p=0.028, 75% of years positive). But **July itself is not statistically significant** (p=0.172) — the strength shows up concentrated in August, not spread across both months as "July–August" might imply. January is an equally strong, independently significant month that the seasonal framework above doesn't emphasize at all. So: real seasonal strength exists, but the calendar shape is narrower and slightly different than the general claim suggests.

### Silver — the claim is much weaker in the actual numbers

| Rank | Month | Avg return | t-stat | p-value | % positive years |
|---|---|---|---|---|---|
| 1 | July | +0.82 | 1.64 | 0.121 | 56% |
| 2 | October | +0.66 | 1.64 | 0.122 | **75%** |
| 3 | August | +0.77 | 1.43 | 0.174 | 50% |

**Verdict on silver:** **not one month in silver clears conventional statistical significance (p<0.05)**, including July and August. October is the most *consistent* month by hit-rate (75% of years positive) but the effect size is small relative to the noise. This doesn't mean the July/August framing is wrong in every individual year — it means that across 16 years, the signal isn't strong enough to statistically distinguish from random variation. Silver's seasonality, at least on this dataset, is real only in the weakest sense — a mild lean, not a dependable edge on its own.

### 2026 Year-to-Date — how this year is actually behaving

2026 has been a volatility outlier for both metals relative to the 15 prior years:
- **Silver:** March 2026 (-18.0%) and June 2026 (-16.2%) are both far outside the historical range for those months (prior worst March was -4.1%, prior worst June was -3.5%)
- **Gold:** March 2026 (-583.7) and June 2026 (-538.4) are similarly extreme — both roughly 3-5x larger than any prior March or June move in the 16-year sample
- **August 2026 so far:** Silver +10.5%, Gold +467.2 — both tracking **in the same direction as the historically significant August seasonal tendency**, which is at least directionally consistent, though the month isn't finished and one data point doesn't validate a pattern on its own

**Reading the divergence framework against 2026 specifically:** March and June 2026 are dramatic *departures* from seasonal norms in both metals (per the divergence-signal logic earlier in this doc) — under the method's own framing, that kind of extreme deviation from a normally quiet or moderate month is meant to be read as a signal of unusually strong underlying force overriding the seasonal baseline, not something to dismiss as noise. Given the magnitude in both metals simultaneously, this looks more like a shared macro driver (rates, dollar, risk sentiment) than metal-specific seasonal breakdown — worth checking against the DXY relationship material in the companion document rather than treating each metal's deviation in isolation.

### Bottom line ranking
1. **Gold, August** — the only genuinely strong, statistically defensible seasonal edge in this entire analysis
2. **Gold, January** — a real, independently significant effect the general "July/August" framing doesn't capture
3. **Gold, April & October** — marginal (p<0.10), worth noting but not strong on their own
4. **Silver, any month** — treat as a mild historical lean at best; none reach statistical significance, and 2026's extreme moves in March/June show how easily the normal pattern can be overwhelmed by non-seasonal forces
