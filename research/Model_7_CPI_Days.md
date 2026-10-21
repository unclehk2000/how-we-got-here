# MODEL 7 — CPI Day Price Delivery
### A Milder Event Than NFP, Despite Sharing the Same Release Format
**42 CPI releases in the dataset (Jan 2023–Aug 2026), verified against the official BLS release schedule rather than assumed from a calendar rule. One date (Jan 13, 2026) fell outside the NQ dataset's coverage and was excluded. October 2025 data was never published due to the 2025 lapse in federal government appropriations — that gap is real and preserved here, not filled in.**

---

## Why This Needed Its Own Model, Not a Copy of Cero

CPI releases at 8:30 AM ET, the same slot as NFP, on a monthly cadence. The temptation is to assume it behaves like a smaller NFP and inherit Cero's disruption-based system wholesale. **The data doesn't support that.** Nearly every mechanism that defines Cero either weakens substantially or reverses outright on CPI days. This is reported as found, benchmarked directly against Cero's own numbers throughout, so the contrast is explicit rather than implied.

---

## Session Character — A Different Shape Entirely

| Session | CPI avg range vs. baseline | *(for reference: NFP's own figure)* |
|---|---|---|
| Asia | **124.5% — wider**, not quieter | *93.8% — quieter* |
| London | 88.8% — quieter | *86.2% — quieter* |
| NY AM (contains the release) | **106.5% — only modestly wider** | *120.0% — the clear disruption window* |
| NY Lunch | 113.3% — wider | *109.2%* |
| NY PM | 98.7% — essentially normal | *101.6%* |

**This is the clearest evidence that CPI is not a scaled-down NFP.** NFP shows a clean shape: quiet positioning before, a sharp NY AM spike, digestion after. CPI shows something else — Asia is actually *wider* than normal (positioning ahead of the print appears to happen earlier and more diffusely), London is quiet in both cases, and critically, **NY AM itself — the session containing the actual release — only widens modestly (106.5%) compared to NFP's outsized 120%.** Whatever volatility CPI generates is spread more evenly across the day rather than concentrated in one sharp window.

---

## Directional Character — More Frequently Up, But Smaller Moves

| | CPI | Baseline | *(NFP, for reference)* |
|---|---|---|---|
| Up-close frequency | **61.9%** | 55.2% | *63.2%* |
| Average net move | +11.8 | +8.0 | *−7.3* |
| **Average absolute displacement** | **119.6** | 152.3 | *~21% above baseline* |

The up-close frequency lean is real and lines up closely with NFP's own lean. **But the magnitude finding is the opposite of NFP's.** NFP days run meaningfully larger than a typical day. CPI days run meaningfully *smaller* — despite being, on paper, an equally significant scheduled release. A plausible read: CPI's headline number is more often close to consensus expectations than NFP's, so the realized surprise — and the resulting displacement — tends to be smaller on the median day, even though the up-close frequency still tilts positive.

---

## The Two-Stage Move — Present, But Weaker

| | CPI | *(NFP)* |
|---|---|---|
| Stage 2 (8:50–11:00) opposes Stage 1 (8:30–8:50) | 59.5% (CI 44.5–73.0%) | *65.8%* |

The reversal tendency is real and points the same direction as NFP's, but it's less pronounced and the confidence interval is wide enough that this shouldn't be leaned on as heavily as the NFP figure.

---

## The Gap Doesn't Get Suppressed the Way It Does on NFP

| | CPI | Baseline | *(NFP)* |
|---|---|---|---|
| Full RTH gap fill | 53.8% (CI 38.6–68.4%) | 58.1% | *37.8% vs. its own 57.8% baseline* |

**This is a large, important difference.** NFP suppresses gap-fill rates by roughly 20 percentage points relative to baseline — a real, structural effect. CPI's gap-fill rate sits within a few points of normal, well inside the confidence interval of the baseline itself. **Don't apply Cero's "expect the gap to stay open" rule to CPI days — it isn't supported here.**

---

## The Disruption Mechanic Does Not Transfer — This Is the Central Finding

This is where the contrast matters most, because it's the organizing principle of the entire Cero system, and it does not hold for CPI.

| | CPI | *(NFP)* |
|---|---|---|
| Week's direction (Mon–Thu) matches the release day's own direction | **52.5%** (CI 37.5–67.1%) — essentially no relationship | *42.9% — a real, opposing lean* |
| **Next day continues the release day's own direction** | **56.1%** (CI 41.0–70.1%) — **leans toward continuation** | *36.8% — leans strongly toward reversal* |

**NFP disrupts: it tends to move against the week's established direction, and its own move tends to get reversed the following session.** CPI shows neither pattern clearly — if anything, the second figure leans the *opposite* way, toward mild continuation rather than disruption. **This is the single most important reason not to import Cero's core framework onto CPI.** The organizing idea behind the entire NFP system — expect disruption, not continuation, at every timeframe — simply isn't supported by CPI's own data. Both intervals are wide at this sample size, but neither one replicates NFP's clear, three-way-confirmed lean.

---

## DXY on CPI Days — Also More Muted Than NFP

| | CPI | *(NFP)* |
|---|---|---|
| DXY RTH range vs. its own baseline | 116.6% | *139.4%* |
| Same-day NQ/DXY close in opposite directions (contrarian rate) | 57.1% (CI 42.2–70.9%) | *55.3%* |

DXY still reacts more than it does on an average day, but well below the scale of its NFP reaction. The contrarian relationship itself sits close to the general baseline in both cases — consistent with the earlier finding that this relationship doesn't sharpen much around scheduled releases generically, CPI included.

---

## Testing the Concepts From CPI-Specific Lecture Material

A separate set of lecture transcripts focused specifically on CPI recur on a few distinct ideas: that the first side of liquidity swept at the release signals the larger, "real" move will run the opposite way; that the gap between yesterday's close and today's open pulls price back within the opening range; and that the New Week Opening Gap functions as the primary gravitational reference through the week. Each was tested directly.

### "First side swept signals the opposite side is the real move" — does not hold, and may lean the other way
| | Result |
|---|---|
| Day's larger move favors the side OPPOSITE the one swept first | 42.9% (CI 29.1–57.8%) |

This is below chance, not above it. The claim — that the initial liquidity run is a decoy and the larger move develops toward the untouched side — isn't supported here. If anything, the point estimate leans toward the day's larger move continuing in the *same* direction as whichever side gets hit first, though the interval is wide enough that "no relationship either way" is the safest reading. Don't use the first sweep as a contrarian directional signal on CPI days.

### The opening-range gap pulls back less often within the first 30 minutes than lecture material suggests — and less than a normal day, too
| | Result |
|---|---|
| CPI: gap 50%-fill within the first 30 minutes (9:30–10:00) | 43.6% (CI 29.3–59.0%) |
| Baseline: same measure | 52.5% |

This sharpens the earlier full-day gap-fill finding in this document (53.8% vs. 58.1% baseline). **The gap fill CPI does eventually achieve mostly happens later than the opening half hour** — the suppression is concentrated in speed, not in whether the gap closes at all. Don't expect the fast pull-back to yesterday's close that the lecture material describes as typical; it happens on a minority of CPI days, and less often than on an ordinary day.

### NWOG is, once again, already resolved before the release — same pattern as NFP
| | Result |
|---|---|
| NWOG still unfilled as of the day before CPI | 16.0% (CI 6.4–34.7%) |
| Of those still open, touched on CPI day itself | n=4 — too small to use |

84% of the time, the week's opening gap has already closed before CPI even happens — nearly identical in spirit to the NFP finding (100% resolved by Thursday there). The remaining sample of genuinely "live" NWOGs going into a CPI release is too thin in this dataset to say anything reliable about what happens to them; that figure is reported as unusable rather than as a finding. The practical takeaway carries over from Cero: NWOG is a reference for earlier in the week, not typically a live target on the release day itself, for either event type.

---

## What This Means in Practice

1. **Do not apply Cero's system to CPI days.** The disruption mechanic — the central organizing idea of the NFP model — is not supported here. Week-direction and next-day continuation both point away from disruption, one of them (next-day) leaning mildly toward the opposite behavior.
2. **Expect a milder, more spread-out volatility profile, not a concentrated NY AM spike.** Asia is unusually wide, NY AM only modestly so — size and timing expectations calibrated to NFP will overstate what typically happens here.
3. **Don't expect the gap to stay open the way it does on NFP.** CPI's gap-fill behavior is close to an ordinary day's.
4. **The up-close lean is real and worth knowing (61.9%), but pair it with the magnitude finding** — displacement tends to be smaller than a typical day, not larger, so this is a frequency edge, not a size edge.
5. **Don't treat the first liquidity side swept as a contrarian signal for the day's larger move** — tested directly, it doesn't predict the opposite side, and may lean mildly the other way.
6. **Don't expect a fast pull-back to yesterday's close in the opening 30 minutes** — CPI fills this gap slower than an ordinary day, even though it mostly catches up by the close.
7. **NWOG is reference material for earlier in the week, not a live CPI-day target** — it's resolved before the release the large majority of the time.
8. **This is still a 42-event sample describing a genuinely distinct release type.** Treat every number here with the same caution applied throughout Cero — real, worth knowing, not a settled law.

---
*All confidence intervals are 95% Wilson score intervals. CPI dates verified directly against the BLS official release archive rather than derived from a calendar rule, including the confirmed publication gap for October 2025 data.*
