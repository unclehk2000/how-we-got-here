# Sanders, Boris & Manfredo (2004) — Replicated on NQ

**Source paper:** *Hedgers, funds, and small speculators in the energy futures markets*, Energy Economics 26, 425–445.

**Our data:**
- **Positioning:** CFTC Traders in Financial Futures (TFF), NASDAQ MINI, 2015–2026. Every value was verified against the CFTC's change fields.
- **Prices:** NQ 1-min, 2018 and 2022 – Aug 2026, giving 268 weekly observations.

**Groups.** The paper uses the Legacy report's groups (commercials, noncommercials, nonreporting). For equity index futures the CFTC publishes the TFF groups, so these stand in:

| Paper's group | Role | TFF stand-in |
|---|---|---|
| Noncommercials | Trend-following "funds" | Leveraged funds (LEV) |
| Commercials | Hedgers | Asset managers (AM), the largest institutional holders |

**Position measure:** PNL = (Long − Short) / (Long + Short), as in the paper's eq. 3.

**Timing.** The paper measures returns Tuesday close → Tuesday close and assumes the report is known on the Tuesday it describes. It is actually published on Friday. Every predictive test is therefore run twice: once with the paper's timing, and once from the first RTH open after the Friday release ("tradable").

## Results alongside the paper's

| Test | Paper (energy, 1992–99) | NQ (2018, 2022–26) |
|---|---|---|
| **Contemporaneous correlation** (Table 3) | Funds +0.19 to +0.29; commercials −0.23 to −0.32; all significant | Weekly change in AM net position vs same-week return: **+0.34**. LEV: **−0.34**. Levels +0.13 / −0.20. All significant (5% critical value 0.12) |
| **Do returns lead positions?** (Table 4) | Yes. Funds buy after rises; commercials sell | **Yes for AM:** Wald p = 0.0002, positive. Asset managers add after rising weeks. LEV p = 0.20 |
| **Do positions lead returns?** (Table 6) | No, apart from isolated crude-oil cases | **No.** AM p = 0.35, LEV p = 0.97. AIC picks 1 lag in both cases |
| **Extreme positions** (Table 8: bottom/top 20% of prior 3-year range) | No (pooled p 0.17–0.88) | **No.** AM F p = 0.66 (paper timing), 0.16 (tradable). LEV p = 0.38 and 0.29 |
| **Tradable timing** | Not tested; flagged in the conclusion as likely to weaken results further | No coefficient significant. AM level t 1.15, AM weekly change t 0.23, LEV level t 1.00, LEV weekly change t 0.52 |

**Conclusion:** NQ reproduces the paper's finding exactly. Positions follow returns; they do not lead them.

## Why COT looks predictive on a chart

The paper explains the illusion, and NQ shows it clearly. Take the rule "follow the asset managers' week-on-week change", and its mirror "fade leveraged funds":

| Rule | Matches the week the report describes (Tue→Tue) | Predicts the week after release |
|---|---|---|
| Follow AM WoW change | **62.7%** (n = 268, p < 0.0001) | **53.2%** (p 0.32) |
| Fade LEV WoW change | 56.7% (p 0.03) | 47.5% (p 0.46) |
| Always long | — | 54.8% |

The weekly change describes the move that has already happened, because asset managers add as price rises. Looking back at a chart, it seems to "confirm" direction about 63% of the time. Once the report is public, that information is used up: following the change is worse than simply being long.

This also explains why the earlier volatility result was positioning reflecting the market rather than leading it.

## Not replicated

- **Pooled SUR across markets** (paper Tables 5, 7, 9). This needs ES, RTY and YM positioning, which wasn't pulled.
- **Legacy-report groups.** Commercials, noncommercials and nonreporting can be fetched from the same CFTC source and verified the same way if a like-for-like replication is wanted.

Script: `sbm_replication.py`. It needs `hydra.py`, the NQ 1-min files, and `COT_NQ_TFF_2015_2026.csv`.
