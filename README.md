# How we got here

The working archive behind the **Hueco Mundo indicator set** (16 TradingView indicators) and the four tools that came out of building it. It holds the research, test, port, build, mock-up and publishing scripts (about 550 files, 6–21 Oct 2026) and 57 research write-ups.

Nothing here is needed to use the indicators. It is here to show how each number on a card was tested before it was shown, and what that process changed.

**No market data is included** (Barchart / CME data can't be redistributed). The scripts read their CSVs from paths in the original workspace (`/home/claude/...`, `/mnt/user-data/...`). To re-run one, point its data path at your own 1-minute files.

## How an indicator was made

Each indicator went through the same ten stages. The table lists what each stage improved, or the bug it caught.

| # | Stage | Where | What it improved |
|---|---|---|---|
| 1 | **Data prep.** 1-minute NQ, ES and RTY (plus DXY, CL, GC and others) 2018–26. One contract per CME trading day (the one with most volume), times in ET, trading day 18:00–17:00 | in each folder's loaders | No roll-day jumps in the tests, and sessions line up with the indicators' own clock |
| 2 | **The ✓ rule.** p < 0.05 with errors clustered by date, the same sign in 2018–24 and 2025–26, and on NQ, ES and RTY | [stats-kit](https://github.com/unclehk2000/stats-kit) | Several setups on one day stopped counting as independent evidence. Most claims failed, and only the survivors reached a card (see "What didn't survive") |
| 3 | **HYDRA.** Fish many candidate rules on 2018–24, then score them once on a locked 2025–26 test | [hydra](https://github.com/unclehk2000/hydra), `calendar-models/hydra_*` | Each card row has an out-of-sample number. A rule that only worked on the data it was found in was dropped |
| 4 | **Python ports of the Pine logic**, run bar by bar on the same data | `genjutsu-kai/pine_port.py`, `benihime/sim_engine.py`, `hado-99/fm_sim.py`, `kyoka-suigetsu/pine_emul*.py`, `calendar-models/port_check.py` | The card shows the numbers that were tested. Ports caught two bugs: **Benihime** read daily bars, which measured the 17:00 → 18:00 gap instead of the RTH gap (now 15-minute bars). **Hadō 99**'s protected swing was timed to C5 instead of C4; the re-test gave the corrected odds (49% held, 93% with ≤ 5 bars left) |
| 5 | **Generators and patchers.** Pine written by scripts, not by hand-editing 5–10k-line files | `calendar-models/gen.py`, `calgen__*`, `patch_*.py`, `vizard2__build.py`, `hueco-mundo/make_hm.py`, `pine2lib.py`, `hado-99/build_b58.py`, `p_h99_cards.py` | Tables are pasted from the test output, so a card can't drift from its research. A rebuild takes seconds |
| 6 | **Size and limit tools** | [pinetools](https://github.com/unclehk2000/pinetools) | Hollow v3 failed at 137,244 tokens (limit 100,256): long tooltips were counted up to ten times each. Now stored once, it compiles. Four libraries broke CE10116 (State had 329–449 elements, cap 254), so State is now split into parts. Five library errors that would have blocked publishing are fixed in `pine2lib.py` |
| 7 | **Compile check.** TradingView's light compile, run from a browser tab | `pinetools/tv_check.js` | Every published build had 0 errors and 0 warnings |
| 8 | **Mock-ups.** Desktop and mobile PNGs of each layout, before and after the Pine | `*/mock_*.py`, `ui/mock_views.py` → [mockup](https://github.com/unclehk2000/mockup) | Showed card rows covering price, so Hadō 99 got two separate cards. Layouts were settled before any Pine was written. The same renderer became a visual back-testing tool |
| 9 | **Settings rollout.** The View section was moved to the top of settings on every indicator | `ui/ui_view.py` | One consistent settings layout across the set |
| 10 | **Publishing.** One repo per indicator, plus a README and a TradingView description | `publishing/` | 16 public repos built from the same template |

## What didn't survive

These were tested and removed, or demoted to context only:

- **Macro direction.** DXY and CL move with NQ on the same day, but every lead-lag test was a coin flip: DXY's morning does not predict NQ's afternoon. The macro card now shows the regime and the range to expect, not a direction. Range ÷ ADR20 by yesterday's range (< 1 / 1–1.5 / ≥ 1.5 × ADR20):

  | | < 1 | 1–1.5 | ≥ 1.5 |
  |---|---|---|---|
  | normal day | 0.92 | 1.06 | 1.33 |
  | after a 2+ sd DXY or CL day | 1.07 | 1.16 | 1.51 |
- **Fractal C2 as a pattern.** Against other candles that closed in the same place, a C2 is not followed by more expansion (−1.6 / −3.2 points). What held is where C2 closes, its swept extreme (+1.7 / +3.4 points) and DXY moving the setup's way (+1.7 hold, +1.3 take).
- **Shikai's overnight midpoint as a magnet.** It is reached about as often as a level the same distance on the other side of the open. Shikai is now a confluence map.
- **Kekkai's Phase 3 trade statistics.** They failed a re-test, so the indicator draws walls, sweeps and shifts only.
- **Byakugan's raw bias** (the 0.5 premarket midpoint calling the close): 51%, a coin flip. Only the conditioned version (56.6% on bullish-bias days) is used.
- **HYDRA's direction head.** 50.0% hit against 53.0% for always-long (p 0.25). Rejected.
- **Benihime release gaps.** PPI, GDP, PCE and retail sales move price at 08:30 (1.8–3.6× a normal 08:30–08:34 range), but their RTH gaps were not reliably bigger. Only the CPI and NFP gaps are 1.4–1.5× the normal size.

## Folder map

| Folder | Files | Dates (2026) | What it is |
|---|---|---|---|
| `cot-carry-wave` | 27 | 6 Oct | COT positioning, the carry Markov model, the wave oscillator |
| `early-labs` | 8 | 6 Oct | first tests: ARDL, COT breadth, gap functional logit, direction audit |
| `shikai-bankai` | 14 | 9–16 Oct | Shikai / Bankai session map, midpoint re-test |
| `domain-expansion` | 38 | 9–14 Oct | Domain Expansion: opening-range model, card patches |
| `kekkai` | 4 | 9 Oct | Kekkai Barrier: walls and the Phase 3 re-test |
| `byakugan` | 5 | 9–14 Oct | Byakugan: 07:00–09:00 premarket bias |
| `sogyo` | 20 | 9–14 Oct | Sōgyo: RTH / RTH2 twin midpoints |
| `macro-and-seasonality` | 26 | 10–12 Oct | seasonality, DXY / CL / bonds against NQ, card mock-ups |
| `kyoka-suigetsu` | 85 | 10–12 Oct | Kyōka Suigetsu: tasks 2–3 on NQ, ES and RTY, day-of-week build, Pine emulators |
| `pinetools` | 9 | 10–14 Oct | the size and limit tools as first used |
| `genjutsu-kai` | 11 | 11 Oct | Genjutsu Kai: Pine port and HYDRA findings |
| `calendar-models` | 159 | 11–14 Oct | Desgarrón, Gran Rey Cero, Vizard, Hollow: release-day models (NFP, CPI, FOMC, NFP week), generators, checks |
| `hollow` | 6 | 14 Oct | Hollow v3 size fix |
| `hueco-mundo` | 14 | 14 Oct | Hueco Mundo: library build (`make_hm.py`, `pine2lib.py`) |
| `ui` | 2 | 14 Oct | View-section rollout, settings mock-ups |
| `benihime` | 15 | 14–15 Oct | Benihime: RTH gaps, simulator, mock-ups |
| `hado-99` | 42 | 15–16 Oct | Hadō 99: Fractal Model tests, DXY and CL builds, range regimes, card builds |
| `publishing` | 4 | 16 Oct | repo and README generators |
| `tools` | 3 | 11–21 Oct | `hydra.py`, `mockup.py`, `clock_mock.py` |
| `research` | 57 | 6–16 Oct | the write-ups (`Model_*.md` and others) and the 14 Oct update notes |

Subfolders were flattened with `__`: `calgen__mock_cal.py` was `calgen/mock_cal.py`. The final Pine scripts are in the indicator repos; Pine intermediates and backups are not included here.

## Repos

**Indicators:**
- [hado-99](https://github.com/unclehk2000/hado-99)
- [gran-rey-cero](https://github.com/unclehk2000/gran-rey-cero)
- [kyoka-suigetsu](https://github.com/unclehk2000/kyoka-suigetsu)
- [senbonzakura](https://github.com/unclehk2000/senbonzakura)
- [desgarron](https://github.com/unclehk2000/desgarron)
- [vizard](https://github.com/unclehk2000/vizard)
- [hollow](https://github.com/unclehk2000/hollow)
- [benihime](https://github.com/unclehk2000/benihime)
- [shikai-bankai-session-map](https://github.com/unclehk2000/shikai-bankai-session-map)
- [byakugan](https://github.com/unclehk2000/byakugan)
- [sogyo](https://github.com/unclehk2000/sogyo)
- [opengaps](https://github.com/unclehk2000/opengaps)
- [genjutsu-kai](https://github.com/unclehk2000/genjutsu-kai)
- [kekkai-barrier](https://github.com/unclehk2000/kekkai-barrier)
- [domain-expansion](https://github.com/unclehk2000/domain-expansion)
- [hueco-mundo](https://github.com/unclehk2000/hueco-mundo)

**Tools:**
- [hydra](https://github.com/unclehk2000/hydra): pre-market heads, tested walk-forward.
- [stats-kit](https://github.com/unclehk2000/stats-kit): the ✓ rule.
- [pinetools](https://github.com/unclehk2000/pinetools): Pine v6 size, limit and compile checks.
- [mockup](https://github.com/unclehk2000/mockup): chart mock-ups for visual back-testing.

## Licence

Mozilla Public License 2.0, see [LICENSE](LICENSE). © Unclehk2000. Research archive, not financial advice.
