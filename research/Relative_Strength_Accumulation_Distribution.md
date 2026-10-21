# Relative Strength Analysis — Accumulation & Distribution
### Core Concepts + Application to Equity Indices

---

## The Core Framework

The US Dollar Index (DXY) is treated as the "leader" that sets the tone for a broader basket of related markets. The general rule of thumb:

- **Dollar rallying** → should pressure the related basket lower
- **Dollar falling** → should lift the related basket higher

But not every market in the basket obeys that relationship equally — and that unevenness is the actual edge. The method is about finding which specific markets are quietly disobeying the "expected" relationship *before* the dollar actually turns.

---

## Spotting Institutional Accumulation / Distribution

**Accumulation (bullish divergence):**
A market fails to make a new low even while the dollar is still making new highs. That refusal to follow the dollar lower is read as evidence that large buyers are already absorbing supply — a divergence from what the dollar-driven relationship implies.

**Distribution (bearish divergence):**
The mirror case — a market fails to make a new high while the dollar is still falling.

**Why this matters:** institutional order flow is large enough to actually halt or reverse a market's expected reaction to the dollar. Retail-sized participation generally isn't. So the divergence itself is treated as a fingerprint of size stepping in.

---

## Leadership vs. Sympathy Moves

Once the dollar actually reverses, not everything in the basket reacts the same way:

- **Leadership markets** — the ones that showed the divergence *before* the dollar turned — tend to move first, fastest, and furthest. Larger directional candles, shallow pullbacks, prior highs/lows breaking easily.
- **Sympathy markets** — everything else in the same sector — may still move in the same direction, but later, slower, and with less follow-through. They're riding the coattails of the leader, not driving the move themselves.

**Practical implication:** the leadership issue is the higher-quality trade. A sympathy move can still be profitable, but it's a lower-conviction, lower-magnitude version of the same idea.

---

## The Workflow

1. Break the basket into sector groups (in the original context: grains, livestock, foods, fibers, financials, currencies, metals, energy)
2. Watch each group for which member(s) are diverging from what the dollar's current move implies
3. When the dollar reverses, prioritize the divergent ("leadership") names for entries — they carry the strongest evidence of prior accumulation/distribution
4. Expect the non-divergent names in the same group to lag or underperform, even if they move in the same general direction

---

## Application to Equity Indices — Ranking by Contrarian Reliability

Applying the same "does it diverge from what DXY implies" lens to equity indices (NQ, ES, RTY, YM), ranked from most to least reliably **inverse** to stock indices:

### 1. DXY (Dollar Index) — strongest, most direct
Historically the cleanest inverse relationship to US equities, especially the Nasdaq. A strong dollar tightens financial conditions and pressures multinational/tech earnings; a weak dollar is broadly supportive. This is the most direct transfer of the framework above — same mechanism, just substituting equity indices for the commodity basket.

### 2. Gold — real but conditional
Inversely correlated during risk-off / flight-to-safety regimes, but can move *with* equities during broad reflation or weak-dollar rallies. Less dependable as a clean inverse than DXY — the relationship flips depending on the macro regime.

### 3. Long-duration Treasuries / yields — inverse via the rate channel
Rising yields typically pressure equity valuations (especially growth-heavy Nasdaq), but the relationship depends on *why* yields are rising — growth optimism (weak/no inverse correlation) vs. inflation fear (stronger inverse correlation).

### 4. Crude Oil — weakest, most regime-dependent
Sometimes moves with equities (demand/growth optimism), sometimes against (oil-shock or inflation-scare regimes pressure both stocks and consumer spending simultaneously).

---

## ES / NQ as an In-Sector Leadership Pair

The DXY-vs-basket relationship above is a **cross-asset** divergence (currency vs. commodities). ES and NQ are a different case — they're two members of the *same* sector (US equity indices), normally moving in close lockstep. That changes how the leadership/sympathy read applies:

**Within-pair divergence, not basket divergence.** Instead of watching NQ or ES against DXY, the signal here is watching them against *each other*. When both indices are trending the same direction but one **fails to confirm** — makes a lower high or higher low while the other pushes to a fresh extreme — that's the leadership/weakness tell, read the same way the original framework reads a commodity failing to follow the dollar.

**Sympathetic decline (ES/NQ version):** one index makes a genuine new low (leadership weakness) while the other lags — makes a shallower low, or doesn't confirm the break — but still drifts lower "in sympathy" with the leader, without producing its own independent supply. The lagging index is the weaker short here, same logic as the video's weaker commodities riding a leader's downside.

**Sympathetic increase (ES/NQ version):** same idea in reverse — one index (commonly NQ, given its higher beta from mega-cap tech concentration) pushes to a fresh high while the other confirms only partially or lags, still being pulled up in sympathy rather than showing independent buying pressure.

**Practical read for a NQ-focused approach:** NQ is typically the higher-beta, faster-moving leg of the pair due to its concentration in a handful of large-cap tech names. That means:
- If **NQ leads** (makes the new high/low first, ES lags) → consistent with NQ's usual higher-beta character, lower information value as a standalone divergence signal
- If **ES leads and NQ lags/fails to confirm** → a more unusual, higher-information divergence, since it runs against NQ's normal higher-beta tendency — this is the more interesting signal to flag, as it suggests something specific to tech/growth positioning (not just broad market beta) is holding NQ back or pushing it ahead

**Caveat:** this section is conceptual, not yet tested against real data — the current dataset only contains NQ, not ES. If ES OHLC is added alongside the existing NQ dataset, this divergence pattern (does NQ confirm every ES swing high/low, and vice versa) could be tested the same rigorous way the time-of-day patterns were: real touch/no-touch counts, confidence intervals, the works.

---

## Natural Extension for NQ/DXY Work
