# Slab Radar — M0 Plan

Status: **draft for approval** (2026-10-02; F9 and fee facts refreshed 2026-10-29). Nothing below is production code yet.
Companion files: [`schema.sql`](schema.sql) (DDL, validated on DuckDB 1.5.6), [`data-sources.md`](data-sources.md) (source evaluation + recommendation), [`lessons.md`](lessons.md), `research/*.md` (raw subagent research with citations).

---

## 1. What M0 established (facts, not plans)

| # | Finding | Evidence | Consequence |
|---|---|---|---|
| F1 | GemRate export has **1,877 rows in three id states**: 322 rows carry a 40-hex **universal** id; **1,114 rows (6,957 slabs) have `gemrate_id=None` in the Universal Pop link** and carry only the PSA-scoped id inside the Card Ladder links — this includes the flagship **2025 Prizm Silver #327**; 441 rows have *all link columns empty* (every one Total ≤ 28, Σ = 964 slabs). Counts also contain thousands separators (`"1,655"`). | `fixtures/gemrate/tyler_shough.csv` profiled 2026-10-02, re-profiled 2026-10-06 | Proposed (**needs your OK**, it refines the CLAUDE.md key rule): `card_key` = universal id → else PSA-scoped (Card Ladder) id, flagged `psa_scoped_id_only` → else `sr_` + sha1(natural key), flagged `no_gemrate_id`. Reading the rule literally (universal only) would give the flagship card a synthetic key. The 441 no-id rows are Tier C by construction. Importer strips `,` before casting. Logged in `lessons.md`. |
| F2 | In **13 of the 322 rows that have both ids, the Card Ladder `gemRateId` ≠ the universal id** — including 2025 Prizm **Base #327** (Total 122), Optic Base #223 (224). | same | Store both (`gemrate_id`, `cardladder_gemrate_id`), flag `gemrate_id_mismatch`; comps are pulled with the Card Ladder id, pop with the GemRate id. GemRate docs (VERIFIED) say ids are **per grader** with one promoted to `universal_gemrate_id`; the Card Ladder links carry the PSA-scoped id, so a mismatch most likely means the universal id was promoted from another grader (inference, UNVERIFIED — confirm with one GemRate API call). |
| F3 | Gem Rate string mismatches `round(Gems/Total)` on 19/1,877 rows (e.g., 15/24 = 62.5% shown as "63%" but Python rounds half-to-even → 62). | same | Always recompute from counts (spec already says so); never compare to the string in tests except as a ±1 pp sanity check. |
| F4 | Fixture checks pass: Prizm Silver #327 = 27/152, #429 = 53/193, both separate rows with distinct ids; 32 multi-player rows (Name contains "/"); 5 blank Card #; Cat = Football 1,827 / Multi Sport 50; years 2021 (60), 2023 (2), 2024 (15), 2025 (1,798), 2026 (2). 32 cards have Total ≥ 100 (matches PROMPT). | same | Fixture tests in §14 are writable now. |
| F5 | Parallel-level gem-rate spread confirmed in data: 2025 Prizm #327 Pandora 95/132 (72%), Lazer 146/319 (46%), Silver 27/152 (18%); Donruss Downtown #19 1,163/1,655 (70%). 2025 Topps Chrome #398 Refractor 62/221 (28%). | same | Parallel-level priors are mandatory (§8). |
| F6 | Pre-NFL detection cannot be a manufacturer rule: GemRate "Set" strings include *Bowman University*, *Leaf*, *Sage*, *Onit … Nil*, *Wild Card*, *Panini … Collegiate*, *Onyx Vintage College* (≈140 rows). | same | `config/products.yaml` holds an explicit `pre_nfl: true` list by set-prefix; unknown sets default to `pre_nfl: null` → Review Queue. |
| F7 | Your reference repo (`groknflanalytics/nflanalytic`) defines **red zone (`yardline_100 <= 20`)**, the **offensive-play filter**, NGS concepts, and the **beta-binomial conjugate update** — but has **no definition** of target share, air-yards share, WOPR, snap share, or xFP. | grep over `wiki/` and `raw/AllChapters/` | Those use nflverse's own definitions (cited from nflverse source in `research/nflverse-and-infra.md`); each gets a wiki-style entry on the Methodology page and I propose adding them to the reference repo (your call). |
| F8 | No existing nflverse ETL was found except `~/Developer/nflanalytic/scripts/export_lite_data.py` (textbook export, nfl_data_py 0.3.3 — deprecated in favour of nflreadpy). | filesystem search | **Question for you** (§10): is there another ETL path I should reuse? |
| F9 | **2026 is live through week 7** (rechecked 2026-10-29). Michael Wilson (ARI WR, gsis 00-0038559) target share by week: wk1 0.189 (7 tgt), wk2 0.269 (7), **wk3 @SF 0.340 (17 of 50)**, **wk4 vs NYG 0.371 (13 of 35)**, wk5 0.152 (7), wk6 0.206 (7), wk7 0.182 (8). Peak *level* is now week 4; the biggest *spike* (last-1 vs season-to-date baseline, the §4.2 definition) is still week 3: +0.118 (0.340 vs 14/63 = 0.222) vs +0.097 for week 4 (0.371 vs 31/113 = 0.274). | nflreadpy live load 2026-10-02 and 2026-10-29 | Acceptance week = **2026 wk 3** (largest self-delta); the radar must also flag wk 4. The test asserts the spike definition, not "max share", so later weeks can't silently move it. Wilson has faded since (wk 5–7 ≤ 0.21), which makes this a useful TRIM/AVOID test case for the strategy engine too. |
| F10 | snap_counts has only `pfr_player_id`; bridging via `load_players().pfr_id` left 6/1,820 offensive rows unmatched. ffopportunity has ~25 rows/week with null player_id (team-level). Depth charts since 2025 are ESPN timestamped snapshots with **no week column**. | same | Unmatched snap rows → data-quality warning list, not dropped silently; ffopportunity nulls filtered; depth snapshot → week by latest `dt` before kickoff. |

Research subagent findings (comp sources, pop/grading, title gold-set, nflverse/infra) are summarized in `data-sources.md` and kept verbatim with citations in `docs/research/`.

---

## 2. Architecture

```
GitHub Actions (cron, UTC)                         Cloudflare R2 (private bucket)
┌─────────────────────────────────────┐            ┌─────────────────────────────┐
│ uv run slab-radar run --stage …     │──Parquet──▶│ warehouse/<table>/…parquet  │
│  nfl ▸ radar ▸ sales ▸ listings ▸   │──DuckDB──▶ │ warehouse/slab.duckdb       │
│  pop ▸ gem ▸ crossgrade ▸ killers ▸ │──JSON────▶ │ site/<run_id>/**.json       │
│  strategy ▸ writeups ▸ publish      │            │ site/LATEST  (pointer)      │
└───────────────┬─────────────────────┘            └──────────────┬──────────────┘
                │ deploy hook (POST)                              │ read at build (S3 API, secret)
                ▼                                                 ▼
        Vercel build: Next.js App Router ── static pages from JSON ── middleware Basic Auth on every path
                ▲                                    │
                │ GitHub Contents API (fine-grained  │ route handlers: /api/lookup (live comp adapter, cached),
                │ PAT, this repo, contents:rw only)  │ /api/crossover-log, /api/review (commit JSON files)
                └────────────────────────────────────┘
```

* **Store**: Parquet is the source of truth; `slab.duckdb` is rebuilt from Parquet each run (cheap at this size, avoids DuckDB-file write contention). Storage choice R2 vs Vercel Blob is justified in `data-sources.md §Infra`.
* **Site data**: the ETL writes one JSON per page (`week/{season}-{wk}.json`, `player/{gsis_id}.json`, `card/{card_key}.json`, `search-index.json`, `portfolio.json`, `review.json`, `methodology.json`). The Vercel build pulls `site/LATEST` with read-only R2 credentials and statically renders. Nothing sensitive is in a public bucket.
* **User writes** (crossover log, Review Queue decisions, pins): route handlers commit **one new file per event** under `data/inbox/{kind}/{ts}-{uuid}.json` (no read-modify-write → no SHA conflicts). The next ETL run ingests and archives them. Each commit would otherwise trigger a Vercel deploy (Hobby cap 100/day), so `vercel.json` gets an `ignoreCommand` that skips builds when only `data/inbox/**` changed. Holdings stay in `config/holdings.yaml` (edited by you, committed).
* **Auth**: Basic Auth in `proxy.ts` (Next 16 renamed `middleware.ts` → `proxy.ts`; `SITE_USER`/`SITE_PASS` env), constant-time compare, matcher covers all paths including `/_next/data` and `/api`. Footer: "Personal research tool — not financial advice."

### Repo layout

```
etl/                      Python 3.12, uv, polars, duckdb
  pyproject.toml
  src/slab_radar/
    cli.py                `slab-radar run --season --week --stage --dry-run --offline`
    pipeline.py           stage DAG, manifest, idempotency (season, week, stage, inputs_hash)
    store/                parquet io, R2 (S3 API) sync, duckdb build
    nfl/                  load (nflreadpy), transforms → fact_player_week, team context
    radar/                deltas, z-scores, signal model, breakout score
    cards/                gemrate_csv importer, catalog, tiers, products.yaml
    comps/adapters/       base.py (Protocol) + one module per source; scrapers disabled by default
    parse/                title parser (rules), llm_fallback.py, dictionaries/*.yaml
    market/               medians/CIs, Theil–Sen, outliers, price-lag
    pop/  gem/            pop deltas, hierarchical beta-binomial
    crossgrade/           observed, subgrade model, equipercentile, market-implied, combine, calibration
    killers/              limiting-factor attribution
    strategy/             playbooks, rules, sizing, EV
    writeup/              Claude client, number post-check, template fallback, cache
    publish/              JSON emit, deploy hook, digest markdown
  tests/                  pytest; fixtures/; golden JSON snapshots
web/                      Next.js (App Router, TS), reads prebuilt JSON
config/                   watchlist, holdings, bankroll, horizons, fees, selling_fees, shipping,
                          breakout_weights, thresholds, products, flagships, sources (adapters on/off)
knowledge/product_issues.yaml
fixtures/                 gemrate/, titles/, nflverse/ (frozen week for offline e2e), comps/
data/inbox/               commits from the site (crossover log, review decisions)
reports/                  {season}-wk{NN}.md digests
docs/                     plan, schema.sql, data-sources, methodology, runbook, lessons, research/
.github/workflows/        weekly.yml, thursday.yml, daily.yml (disabled), offseason.yml, ci.yml
```

---

## 3. Data model

Full DDL: [`schema.sql`](schema.sql) — 18 tables, executes cleanly on DuckDB 1.5.6. Decisions worth reviewing:

1. **`card_key`** = universal `gemrate_id` if present, else the PSA-scoped `cardladder_gemrate_id`, else `sr_<sha1(natural_key)>` (see F1; pending approval); `natural_key` = lower-cased, whitespace-collapsed `year|set|name|parallel|card_no`. When a later GemRate export supplies an id for an `sr_` card, **or a universal id appears for a card keyed on its PSA-scoped id** (they differ on 13/322 fixture rows, so this will happen), a `card_key_alias` remap is applied (append-only alias table, added at M2).
2. **Product vs subset**: GemRate's `Set` is "product + insert" (`Panini Prizm Rookie Gear`). The importer splits it with a product dictionary (`Panini Prizm` → product `Prizm`, subset `Rookie Gear`); unknown prefixes go to Review Queue rather than guessing.
3. **`is_rc` is never inferred** — the GemRate export has no RC column, so it stays NULL until a source provides it (card checklist/comp source). Flagship RC selection uses `config/flagships.yaml` (explicit card numbers), not `is_rc`.
4. **Grades** are `(grader, grade DECIMAL(4,1), grade_label)`; `grade_label` carries Pristine / Black Label / Perfect so SGC 10 ≠ SGC Pristine 10 and CGC Gem Mint 10 ≠ Pristine 10 ≠ Perfect 10 everywhere. Qualifiers (OC/ST/PD/MC/MK/OF) are a separate column; qualified grades are excluded from straight-grade stats and shown separately.
5. **Best offers**: `price_is_accepted` is explicit. A best-offer sale whose accepted price is unknown is kept for counts but excluded from price statistics (count shown as "n BO-unknown").
6. **`fact_player_week` is additive** (numerators and team denominators) so any window rate = Σnum/Σden.
7. **Marts** carry `provenance`, `n`, and interval columns — the UI cannot render a mart number without them (enforced by a TS type that requires `{value, provenance, n, lo, hi}`). Interval columns exist for every sampled estimate (medians, Theil–Sen slopes, volatility, multiples in `mart_card_multiple`, gem rates, cross-grade, breakout share posteriors in `share_posterior`). The one deliberate exception is `ask_last_spread`: a census of current asks, shown with n = active listings and "no interval (census)".

---

## 4. NFL metrics and Breakout Radar (math)

Sources: nflverse `player_stats` (weekly), `pbp` (red-zone splits, dropbacks, designed rushes), `snap_counts` (PFR), `nextgen_stats`, `ff_opportunity`, `injuries`, `depth_charts`, `schedules`, `players`. No participation data in-season → **no routes, TPRR, YPRR** (hard rule, enforced by a test that greps the metric registry).

### 4.1 Definitions (per game *g*, player *i*, team *T*)

| Metric | Formula | Source of definition |
|---|---|---|
| Snap share | offense_snaps_i / team_offense_snaps_T | PFR via nflverse (`offense_pct` = same ratio; we keep both components) |
| Target share (TS) | targets_i / team_targets_T | nflverse `player_stats.target_share` |
| Air-yards share (AYS) | receiving_air_yards_i / team **passer** air_yards_T (all pass attempts, incl. uncatchable/untargeted-receiver rows) | nflverse `air_yards_share` (nflfastR source). Recomputing with Σ receiver air yards as the denominator is off by up to 0.09 — so `team_air_yards` stores the passer-side sum |
| WOPR | 1.5·TS + 0.7·AYS | nflverse `wopr` (Hermsmeyer) |
| Carry share | carries_i / team_carries_T | pbp |
| RZ opportunity share | (rz20_targets_i + rz20_carries_i) / (team_rz20_targets + team_rz20_carries); 10-yd version likewise | pbp, `yardline_100 <= 20` / `<= 10` — reference repo *Red Zone Efficiency* cut |
| xFP | ffopportunity `total_fantasy_points_exp` (PPR) | nflverse ffopportunity — **this is an nflverse model output, labeled MODEL** |
| FP − xFP | fantasy_points_ppr − xFP | recorded − model |
| QB volume | dropbacks (pass attempts + sacks + scrambles), designed rushes (QB rushes − scrambles − kneels) | pbp (`qb_dropback`, `qb_scramble`, `qb_kneel`) |

**Window rates** (last 1, last 3, baseline) are always Σnumerator/Σdenominator over the player's *active games in the window* (games with ≥1 offensive snap). Byes contribute nothing; a DNP is not a zero-share game (it's absent) — documented on the Methodology page because it changes "trailing 3" semantics.

### 4.2 Deltas and z-scores

For metric *m*:
* **Self delta**: Δ_self = m(last k) − m(baseline), k ∈ {1, 3}. Baseline = season-to-date excluding the last-k window; if < 2 baseline games, prior season (same team only, else NULL).
* **z_self** = Δ_self / sd_i, where sd_i is the player's own week-to-week sd of m, shrunk toward the position-level sd: sd_i² = (n_i·s_i² + ν·s_pos²)/(n_i + ν), ν = 4 (config).
* **z_pos** = (m(last k) − median_pos,wk) / (1.4826·MAD_pos,wk) over players at the position passing the minimum-snap filter (default: ≥ 25% snap share in the window; config).

### 4.3 Signal vs noise (MODEL, shown with the probability, not a verdict)

Shares are binomial counts, so the radar reports **P(true share rose)**:
targets_i,window ~ Binomial(team_targets_window, θ_recent); targets_i,baseline ~ Binomial(team_targets_baseline, θ_base). Priors Beta(a_pos, b_pos) fit by method of moments to the position's per-player season shares (prior-season), posteriors conjugate (reference repo *Beta-Binomial Conversion*). Report P(θ_recent > θ_base) by 20,000-draw Monte Carlo (seeded) and the posterior means with 80% credible intervals. Same for carry share and RZ share. "Signal" badge when P ≥ 0.90 **and** the snap-share delta is non-negative; "Noise?" when P < 0.70.

### 4.4 TD-driven flag

`td_driven = (FP − xFP) ≥ max(6, 1.5·sd_pos(FP − xFP))` **and** z_self(xFP) < 1. Such weeks feed SELL_INTO_HYPE.

### 4.5 Context flags (recorded data only)

`vacated_opportunity` (a teammate at the same position with ≥ 15% TS or carry share in baseline is Out/IR per injuries), `depth_promotion` (depth-chart rank improved), `qb_change` (starting QB differs from previous game), `trade` (team changed). Each flag lists the teammate and their baseline share, so the vacated volume is shown, not estimated.

### 4.6 Breakout score

`score = Σ_m w_pos,m · clip(z_m, −3, 3) + Σ_f b_f·flag_f − p_td·td_driven`, with z_m = 0.5·z_self + 0.5·z_pos on the last-3 window, plus a last-1 term at lower weight. Defaults (config `breakout_weights.yaml`, versioned, shown on Methodology):

| Position | TS | AYS | WOPR | snap | carry | RZ | xFP | dropbacks | designed rush | last-1 weight |
|---|---|---|---|---|---|---|---|---|---|---|
| WR/TE | .20 | .15 | — | .15 | — | .10 | .25 | — | — | .15 |
| RB | .15 | — | — | .15 | .20 | .15 | .25 | — | — | .10 |
| QB | — | — | — | .10 | — | .10 | .30 | .25 | .15 | .10 |

(WOPR is displayed but not separately weighted — it's a linear combination of TS and AYS; double-counting avoided.) Weights are a starting point; M1 includes a 2024–2025 sanity backtest (does score_t predict next-4-week xFP/game better than last-week xFP alone?) and the result is reported either way.

---

## 5. Cards: catalog, comps, parsing

* **Catalog** from GemRate exports (importer spec as given; quirks F1–F3). Coverage tiers: **A** = watchlist players' cards with PSA pop ≥ `tier_a_min_pop` (default 100) or ≥ 5 sales/90d, plus pins; **B** = flagship RC(s) per `flagships.yaml` + base RC for the radar's top-N auto-discovered breakouts; **C** = catalog + pop only.
* **Comp adapters**: `class CompAdapter(Protocol): search(card: CardRef, grade: GradeFilter, since: date) -> Iterable[RawSale]; listings(...)`; each declares `kind ∈ {api, licensed_feed, scraper}`, `enabled_by_default` (scrapers: False), cost per call, rate limit. Disabled scrapers render a red "SCRAPER (off)" chip in the UI; enabling one requires editing `config/sources.yaml` *and* your approval (rule in CLAUDE.md).
* **Title parser**: ordered rules (normalize → exclusion screen → grader/grade/qualifier/subgrades → year → product (alias dict) → parallel (alias dict with explicit near-miss negatives) → card no. → serial/print run → player alias). Confidence = product of stage confidences; matching then requires a unique `dim_card` hit. **Ambiguity rule** (hard): no card no. + >1 card for (player, product, parallel) → `AMBIGUOUS`, Review Queue, never averaged. LLM fallback (small Claude model, JSON schema) only for confidence < 0.8 titles, and its output is re-validated by the same rules. Gold set ≥ 300 (stratified; seed + spec in `research/title-gold-set.md`); ship gate: precision ≥ 98% on card_key+grade **with the Wilson 95% lower bound reported** (at n = 300 and p̂ = 0.98, the lower bound is ≈ 0.957 — so the gate is "p̂ ≥ 0.98 *and* zero errors on the hard-negative stratum", and the CI is shown).
* **Outliers**: per card×grade, modified z = 0.6745·(log p − median)/MAD over a rolling 90-day window; |z| > 3.5 → `outlier_flag='mad'`. Shill/NPB heuristics: same item re-sold within 14 days at a > 30% higher price, or seller-bidder pattern when source exposes it. Flagged sales stay visible (struck-through) and are excluded from stats.

---

## 6. Market metrics (per card × grade)

* Medians with **distribution-free CIs** (order statistics: the 95% CI for the median uses ranks from Binomial(n, 0.5) quantiles); n always shown; no CI when n < 6 — at n = 5 even (min, max) covers only 93.75%, so 95% first exists at n = 6 (96.9%); intervals report their exact order-statistic coverage (display "n=3, median $X, no interval").
* **Trend slope**: Theil–Sen on (day, log price) over 30/90 days, reported as %/30 days with a bootstrap 80% interval.
* **Volatility**: 1.4826·MAD of residuals from a rolling median, in log units.
* **Multiples**: PSA10/PSA9 and PSA10/raw from 30-day medians (ratio CI by bootstrap).
* **Supply**: active listings count, lowest ask, ask/last-sale spread (from comp source or Browse API if approved).
* **Price lag** (MODEL): realized r = log(median_now / median_[signal week −1]) vs expected repricing E[r | score] from the event study. Gap = E[r|score] − r. Until the event study is calibrated, E[r|score] is NULL and the radar shows only realized r next to the score (no invented mapping).
* **Event study**: for 2023–2025 breakouts (score ≥ threshold), flagship RC PSA 10 / raw log-returns at +1/+2/+4/+8 weeks vs a market baseline (median of all tracked flagship RCs that week). Feasibility depends on comp history depth (Card Ladder has long history; 90-day feeds do not) — if history is insufficient we say so and start accumulating from the first run.

---

## 7. Population and gem rate

* Gem definitions per grader (spec §8) stored in `config/thresholds.yaml`; PSA 10 rate reported separately.
* Weekly pop deltas = submission velocity; source lag (GemRate ≈ 1–2 days) shown.
* **Hierarchical beta-binomial (empirical Bayes, three levels)**. For pool *P* (product × parallel × year, all players, 1/1s excluded) with cards j: g_j ~ Binomial(n_j, θ_j), θ_j ~ Beta(μ_P κ_P, (1−μ_P) κ_P). (μ_P, κ_P) are fit by maximizing the beta-binomial marginal likelihood with a penalty pulling μ_P toward the parent mean (product × year), which is fit the same way toward the global mean. A pool with < 3 cards or Σn < 100 uses its parent's (μ, κ) directly — and the UI states which level was used. Posterior for card j: Beta(μκ + g_j, (1−μ)κ + n_j − g_j); 95% equal-tailed credible interval. Raw rate is greyed when n < 30 and the shrunk estimate leads.
* Caveat surfaced in UI: GemRate pools only see cards that GemRate tracks; with one player's export we can fit only this player's parallels — **cross-player pools need multi-player exports or the GemRate API** (a data-source dependency, flagged in `data-sources.md`).

---

## 8. Cross-grade inference — P(PSA grade | other slab)

Methods (each a separate row, labeled):

1. **OBSERVED** — crossover outcomes (serial match on numbered cards, your log, CSV import; Phase 2 image hash, confirmation required). Estimate: Beta(1,1) + k/n, exact interval.
2. **MODEL — subgrade-conditioned**: limiting factor = min subgrade; centering compared to PSA's published 10 tolerance (value + URL in `config/grading_standards.yaml`; research confirms current wording). Model: P(PSA 10 | profile) = logistic on (min subgrade, centering margin to the PSA tolerance, count of sub-9.5 categories), fit on observed crossovers when n ≥ 30; before that, a documented rules table (e.g., any subgrade < 9.5 → P10 ≤ 0.15) with effective weight n_eff = 5.
3. **MODEL — equipercentile (weak)**: source grade g's quantile band [F_src(g⁻), F_src(g)] in the source grader's pop distribution for the same card is mapped onto PSA's distribution; P(PSA 10 | g) = overlap of that band with PSA 10's band / band width. Falls back to the product × parallel pool. n_eff = 2, and a UI note: "assumes graders rank copies identically and that the same copies go to both — both false; selection pushes the best copies to PSA."
4. **MARKET-IMPLIED**: p_mkt = (P_src + C − V_9 − q8·(V_8 − V_9)) / (V_10 − V_9) — derived from indifference P + C = p·V_10 + (1−p−q8)·V_9 + q8·V_8 (crack-and-resubmit; q8 is a MODEL input, so this row is labeled MARKET_IMPLIED with "uses MODEL q8"). Not combined; it's the comparator. For the min-grade crossover scenario (a miss keeps the original slab, full fee charged — VERIFIED PSA policy) the matching hurdle is p_cross = (P_src + C − V_cur) / (V_10 − V_cur), pure market values, labeled MARKET_IMPLIED. **Buy-to-cross flag**: p_combined − p_cross ≥ `crossgrade.margin` (default 0.10) **and observed n ≥ 5** (model pseudo-counts alone, n_eff 5 + 2, can never trigger it) and n_combined ≥ 10. Both hurdles are displayed.

**Combined estimate**: Beta(1 + Σ_m w_m·k_m, 1 + Σ_m w_m·(n_m − k_m)), where observed rows have w = 1 with their real n, and model rows enter as pseudo-counts n_eff·p_m. Calibration: Brier score and a reliability table versus OBSERVED outcomes on the Methodology page; until ≥ 30 outcomes exist the page says "uncalibrated".

**EV** (values net of selling fees from `config/selling_fees.yaml`):
* Cross with min 10: EV = p10·(V_10 − V_cur) − C; p* = C / (V_10 − V_cur).
* Buy-to-cross: EV = p10·V_10 + (1 − p10)·V_cur,resale − purchase − C.
* Raw-and-grade: Σ_g P(g)·V(g) − raw − C, where P(·) is the card's shrunk PSA distribution with adverse-selection haircut h applied multiplicatively (P'(10) = (1 − h)·P(10), h default 0.25, the removed mass moved to 9; never negative). The full grade distribution P(9), P(≤8) comes from per-grade pop (GemRate API `/cards/{id}/population` or PSA spec pop) — the CSV's Gems/Total alone cannot supply it, so raw-and-grade EV is unavailable for cards without per-grade pop and says so; tightened by the photo centering screen when available (Phase 2).
* C = grading fee (tier from `fees.yaml` with turnaround) + shipping + insurance + capital cost (annual rate × turnaround). Fee rows older than 30 days → warning banner.

---

## 9. Gem killers, strategy, write-ups, site, jobs

**Gem killers**: from every cert with subgrades/TAG DIG: limiting category share (ties split equally), front vs back where available; PSA qualifiers counted from titles and certs; `knowledge/product_issues.yaml` entries (source URL required; Claude-proposed hypotheses display UNVERIFIED). Plain-English summary is templated from numbers (no LLM).

**Strategy engine** (deterministic, `rules_version` stamped): inputs = radar row + market mart + gem + cross-grade + holdings + config. Each playbook is a pure function `eligible(ctx) -> Optional[Recommendation]`; priority order resolves the primary. Key rules as specified (turnaround vs hype half-life, licensing from `products.yaml`, low gem + high 10/9 multiple → PSA 9 / cross check, pop velocity up + flat demand → AVOID/TRIM, TD-driven → TRIM). Sizing: `min(max_pct·bankroll·conf_mult, liquidity_cap)` with conf_mult ∈ {1, 0.5, 0.25} and liquidity_cap = price × max(1, ⌊0.25·n_30d⌋); days-to-sell ≈ 30 / n_30d per copy. "What would change this call" = the nearest rule boundary (e.g., "TS < 18% for 2 weeks", "PSA 10 30-day median > $X").

**Write-ups**: watchlist + top N breakouts only; payload JSON → Claude (model id in config; I'll default to Haiku 4.5 for cost and keep Sonnet as an option) → ≤ 150 words; post-check extracts every number from text and requires it to appear in the payload (after the same rounding); one regeneration then template fallback; cached by sha256(payload ‖ prompt_version ‖ model).

**Site** (≤ 2 clicks to everything in PROMPT §2): This Week (radar table) → Player page (usage charts, strategy card, card tiers) → Card page. Search via a prebuilt fuse.js index (aliases, product and parallel abbreviations); multiple hits render side-by-side. Portfolio, Review Queue, Methodology, Digest. Dense dark theme, tabular numerals, sparklines, WCAG AA contrast, mobile layout.

**Jobs (UTC)**: Tue 15:17 weekly full run (freshness gate: all of the week's games incl. MNF in pbp; retry every 3 h up to 4×). Observed: nflverse scheduled jobs start 4–6 h late (ffopportunity's 05:45 cron ran 11:20; NGS's 07:00 ran 13:16), so 15:17 will sometimes hit the gate and retry at 18:17 — I recommend 16:17 but won't change your schedule without approval (§10 Q7), Thu 15:17 stat-correction + ffopportunity refresh + watchlist price/pop + strategy re-run, optional daily 13:07 (disabled), offseason monthly. Every workflow: `workflow_dispatch`, `concurrency: slab-radar-${{ season }}-${{ week }}`, idempotent stages keyed by (season, week, stage, inputs_hash), retries with exponential backoff, failure → GitHub issue with stage + log tail, manifest with row counts, quality gates (sales rows −50% w/w, radar row count, freshness) block publish.

---

## 10. Inputs I need from you (blocking M1 sign-off, not M0 review)

1. **Bankroll** (USD) and **max % per position**.
2. **Default horizon** (e.g., 4 weeks in-season / through season end / 12 months).
3. **Current holdings**: card, grader/grade, cert (if slabbed), qty, cost basis, purchase date. A YAML template is in `config/holdings.example.yaml`.
4. **Existing nflverse ETL**: is there a path to reuse? (I found only `~/Developer/nflanalytic/scripts/export_lite_data.py`, which uses the deprecated nfl_data_py.)
5. **Comp source decision** — see `data-sources.md`: the recommended primary needs a paid/business account, and the 20-card benchmark can't be run without trial keys. Approve requesting trial access (I won't sign up myself).
6. Approve or veto **R2** (vs Vercel Blob) and **Haiku 4.5** as the write-up model.
7. Schedule: keep Tue/Thu **15:17** UTC, or move to **16:17** given observed nflverse lag (`research/nflverse-and-infra.md` §A3)?
8. **`card_key` fallback** to the PSA-scoped Card Ladder id when the universal id is `None` (F1) — refines the CLAUDE.md key rule.
9. **Request a GemRate API key** + pricing (pop deltas, cross-player gem priors); and x402 wallet vs CardHedger subscription (`data-sources.md` §7).

## 11. Milestones (each ends with a stop for your review + independent code-review subagent)

| M | Deliverable | Done when (verifiable) |
|---|---|---|
| M0 | This plan, schema, CLAUDE.md, lessons.md, data-sources.md | your approval + inputs §10 |
| M1 | nflverse ETL → `fact_player_week`, team context; radar | 2024–2026 weeks loaded; formula tests vs nflverse columns (TS, AYS, WOPR identical to `player_stats` to 1e-9); Michael Wilson spike week found and on radar; offline fixture week passes |
| M2 | GemRate importer, catalog, adapter(s), parser + gold set, Card/Player pages, search | fixture tests (§14 of PROMPT, amended per F1–F2); gold-set precision ≥ 98% reported with CI |
| M3 | Pop snapshots, shrinkage, gem killers | shrinkage unit tests (closed-form check vs known posteriors; parent fallback) |
| M4 | Cross-grade (1a–c, 2, 3, 4), Review Queue, crossover log | EV/break-even/market-implied tests; equipercentile tests; round-trip commit test against a sandbox repo |
| M5 | Strategy, write-ups, portfolio, digest | playbook unit tests; number post-check tests; digest for a fixture week |
| M6 | Workflows, deploy, monitoring, runbook | dry-run workflow on `workflow_dispatch`; deliberate failure opens an issue; quality gate blocks a bad deploy |
| P2 | Image-hash crossover matching, CV centering | validated against TAG measured centering |
