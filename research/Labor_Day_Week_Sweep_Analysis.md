# Labor Day Week — Does the Following Week Take Out Both Its High and Low?

**Question tested: across every available year of data (2018, 2022, 2023, 2024, 2025 — 2026's Labor Day, September 7, falls after this dataset's coverage ends on August 20), what's the probability that the week immediately following the Labor Day week takes out *both* its RTH high and its RTH low?**

Labor Day week itself runs Tuesday–Friday only, since the Monday holiday carries no genuine RTH session (confirmed directly in the September 2022 case study, where that Monday showed only thin, partial Globex activity with no real close).

---

## Result: 1 of 5 years (20%)

| Year | Labor Day week H/L | Following week H/L | High swept | Low swept | **Both swept** |
|---|---|---|---|---|---|
| 2018 | 7650.00 / 7402.00 | 7585.25 / 7404.50 | No | No | No |
| **2022** | 12613.75 / 11930.00 | 12766.50 / 11866.50 | Yes | Yes | **Yes** |
| 2023 | 15586.75 / 15157.50 | 15517.75 / 15261.75 | No | No | No |
| 2024 | 19483.25 / 18428.00 | 19577.25 / 18497.25 | Yes | No | No |
| 2025 | 23902.00 / 23025.25 | 24159.00 / 23726.00 | Yes | No | No |

**Both extremes taken out: 1/5 = 20%, with a Wilson 95% confidence interval of roughly 3.6%–62.4%.** Labor Day happens once a year, so this is genuinely five independent observations, not a large-sample statistic — treat 20% as a real, honest data point rather than a settled probability.

---

## The more useful finding: a real asymmetry between the high and the low

Splitting "both" into its two components is more informative than the combined figure alone:

| | Swept the following week |
|---|---|
| **High alone** | **3/5 = 60%** |
| **Low alone** | **1/5 = 20%** |
| Both | 1/5 = 20% |

The high gets taken out considerably more often than the low. In a market that has spent most of this period in a multi-year uptrend, a new week nudging to a marginally higher high is a fairly unremarkable, close-to-default outcome. Actually reversing back through the *bottom* of the Labor Day week — taking out the low as well — is the rarer, more structurally significant event, and it has only happened once in the five years available.

---

## The one occurrence connects directly to an existing case study

2022 is both the only year both extremes were swept, and the year already documented in full detail in the September 2022 forensic case study. The Labor Day week that year was September 6–9 — the relief-rally week that pushed price to its eventual monthly high on September 12. The following week, which took out both the Labor Day week's high (12613.75) and low (11930.00), was CPI week — already independently documented in that case study's Section 4 as sweeping the identical prior-week levels, high first, on September 12, before the CPI release itself took the low.

This isn't a new, independent confirmation exactly — it's the same underlying event, found twice from two different angles — but the two analyses were built separately and arrived at the same numbers, which is at least a useful internal consistency check on both.

---
*Data: NQ 1-minute continuous futures, 2018/2022/2023/2024/2025. Labor Day week defined as the four trading days Tuesday–Friday following the holiday Monday; the following week as the subsequent Monday–Friday, using whichever trading days were actually available in each case.*
