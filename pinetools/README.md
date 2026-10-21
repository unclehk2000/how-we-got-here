# pinetools: size checks and fixes for the Pine v6 indicators

TradingView checks three size limits only at full compile ("Add to chart"). It doesn't publish how it counts any of them:

| Error | Message | What it measures |
|---|---|---|
| CE10117 | Compiled code contains too many tokens (limit 100,256) | the whole script's compiled form |
| CE10295 | The main body of the script is too long | the global scope |
| CE10205 | The if statement is too long | one `if` block |

## What we measured (14 Oct 2026)

- **Hollow v3** failed at **137,244** tokens. Desgarrón v3, Vizard, Gran Rey Cero (13 Oct) and Day of Week Profile compile.
- **Strings cost more than code.** About **1.2–1.45 tokens per string byte (UTF-8)**, against 0.3–1.2 per source token.
- **A string variable that holds a constant is copied into every use.** That covers `const`, `var` and plain globals built only from literals and never reassigned. Hollow's 20 pool tooltips (≈ 0.4–1.1k bytes each, used 2–10 times) were counted ≈ 45k bytes extra. That is the entire overflow.
- **Function calls are not inlined** (TradingView docs), and **library code doesn't count** toward the importing script.
- **Main body:** Gran Rey Cero v5 failed at an estimated 68k in its global scope; the 13 Oct version passed at 62k.
- **If block:** the pre-split Hollow `drawSh` block failed at an estimated 47k, while `drawSg` (≈ 41k) passed.

## Tools

| File | Use |
|---|---|
| `pine_size.py` | Estimates all three sizes and flags `ok` / `RISK` / `FAIL`. `--top N` lists the costliest string variables, `--ifs N` the largest if blocks, `--fns N` the largest functions. Run it before sending any script. |
| `pine_tips.py` | Fixes CE10117. It moves long constant strings used more than once into one runtime array: `var int X = txAdd("...")`, read with `TXA.get(X)`. Strings also used in `input()` keep a const for those uses. |
| `pine_hoist.py` | Fixes CE10295. It moves heavy one-off global work into functions: `var` loaders such as `var array<float> CK = parseMilli(...)` and `if barstate.isfirst/islast` blocks that don't reassign globals. |
| `pine_main.py` | Lists the global scope's heaviest statements. |
| `pine_funcs.py`, `pine_calls.py` | Per-function size and state, and call/argument counts. |
| `pine_flat.py` | For checking only. Pastes imported libraries into the importing script, prefixing their names by alias (`des.step1` becomes `des_step1`), so TradingView's checker can type-check Hueco Mundo and all four libraries together before they're published. |

Build hooks:
- `hol/pool/patch_hollow3.py` ends with `pine_tips.convert`.
- `hm/patch_grc_dr.py` ends with `pine_hoist.hoist(S, 5000)`.
- Desgarrón had `pine_tips` applied to its finished file.

## Semantic check without an account

The editor's light compile, `POST https://pine-facade.tradingview.com/pine-facade/translate_light?user_name=Guest&pine_id=00000000-0000-0000-0000-000000000000` with a form field `source`, returns type and scope errors. It runs fine as Guest. It does not check the three size limits.

This sandbox's shell can't reach it, but a browser tab on tradingview.com can. Load the file through a file input and `fetch` it with `credentials: 'omit'`.

## Hueco Mundo (14 Oct 2026)

The build scripts are in `hm_build/`:
- `pine2lib.py` turns a module into a library.
- `make_hm.py` builds the four libraries and the megazord.
- `checklib.py` and the `spec_*.json` files go with them.

Rebuild after any module change: `python3 make_hm.py`, then `pine_size.py` on each `HM_*.pine`.

TradingView found five bugs in the earlier libraries. They would have stopped them publishing, and `pine2lib.py` now handles each one:
- **CE10133:** a UDT field default must be a literal. Cfg defaults like `color.new(#f23645, 85)` are now written as `#f2364526` (alpha = 255 × (100 − t) / 100).
- **CE10085 / CE10088:** a global that is reassigned anywhere (`:=`, `+=`, ...) can't become a library `const`. It goes into State.
- **CE10123:** one-line functions (`f() => ...idxNm(0)...`) now get `hmS` / `hmC` / `hmF` injected into the calls in their body too.
- **CE10237** (seen only at full compile, after Save): an exported function must use every argument it declares. `pine2lib.py` now drops `hmS` / `hmC` / `hmF` from each step that doesn't use it. It records what each step takes in `export_args`, and `make_hm.py` calls each step with exactly those. `checklib.py` flags any exported argument that is never used.

- **CE10116** (full compile only): a function can use at most 254 "external elements". A type's `.new()` takes one parameter per field, and int, float, bool and color count 2, anything else 1. That matches TradingView's counts exactly: Desgarrón's State was 449, Gran Rey Cero's 446, Vizard's 329 and Hollow's 440. `pine2lib.py` now splits State into `StatePart1..n` of at most 200 elements each. State holds the parts (`hmS.s2.KP`), `newState()` builds one, and `make_hm.py` reaches state fields through `spath`.
- `pine_limits.py` checks CE10116 (types and function parameters), CE10237, plot counts and the number of request calls. Run it with `pine_size.py` before sending anything.

After that, all four libraries type-check with no errors, and so does the flattened Hueco Mundo (megazord plus the four libraries).

Limits checked against TradingView's published ones:
- request calls: 33 unique (max 40) and 53 tuple elements (max 127);
- plot counts: 9 (max 64);
- tables: one module's at a time, at most 7 (max 9);
- global variables: about 220 (max 1,000 per scope).

The one unknown is execution time (20 s on basic plans, 40 s otherwise, over all bars). Hueco Mundo runs four modules per bar. If it times out on a long 1-minute history, switching modules off is the lever.

Open question: the CE10116 message counts a script's inputs and request results as external elements too, so the main script may have the same 254 cap. Hueco Mundo's inputs and requests come to about 357 (147 inputs = 251, plus 53 request values = 106). `HM_probe.pine` holds exactly those inputs and requests and no libraries, so saving it in TradingView answers the question.
