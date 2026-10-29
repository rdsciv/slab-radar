# Build: Slab Radar — NFL usage × sports-card market tracker

Build a private web app for me (Ryan) that joins weekly NFL usage data (nflverse) with sports-card market data (sold comps, population reports, grading data) to find card investment opportunities as the season unfolds, and produces a concrete strategy per player every week via scheduled jobs.

Start in plan mode. Deliver a written plan, schema, and data-source evaluation for my approval before production code. Use subagents for parallel research (data sources, grading standards, title-parser gold set) and for an independent code review at each milestone. Keep `docs/lessons.md`: whenever I correct you or a test disproves an assumption, record the rule so it isn't repeated.

## 0. Context and constraints

- I'm data-fluent (Python, R, DuckDB, nflverse). Don't simplify the math; document it.
- NFL metric definitions: check my reference repo `~/Developer/warpy/groknflanalytics/nflanalytic` (wiki/code, wiki/concepts, SCHEMA.md) before defining any NFL metric, and reuse its formulas. If my existing nflverse ETL code is available locally, ask me for the path and reuse it rather than rebuilding.
- NFL stats must be recorded metrics only — no estimates or proxies. nflverse does not release participation (routes) in-season, so do not produce routes run, TPRR, or YPRR. Allowed: nflverse-data, nflreadpy, nflfastR pbp, PFR snap counts via nflverse, Next Gen Stats via nflverse, ffopportunity.
- Card-side numbers are often inferred. Label every number OBSERVED, MODEL, or MARKET-IMPLIED, with n and an interval. Never present a model output as an observation.
- Round to the precision the data supports: prices to whole dollars ($5 above $500), rates to whole percent, n shown next to every rate.
- Personal tool: private repo, whole site behind auth (middleware basic auth via env vars is fine). One-line "not financial advice" footer.
- At M0, ask me for: bankroll, max % per position, default horizon, and my current holdings.

## 1. Decisions already made

- Hosting: GitHub Actions for scheduled jobs; Next.js (App Router, TypeScript) on Vercel. ETL in Python 3.12 with uv, polars, DuckDB. Canonical store = Parquet + DuckDB file in object storage (choose Cloudflare R2 or Vercel Blob; justify). ETL emits prebuilt JSON per page and calls a Vercel deploy hook.
- Comp data source: undecided — you evaluate (Section 3) and recommend. Do not sign up or pay for anything.
- Strategy: deterministic rules engine decides actions, prices, and probabilities; the Claude API writes the rationale only.

## 2. What the product must answer in ≤2 clicks

Example: on Tuesday I see Michael Wilson had a big target week. I need:
1. His usage trend (targets, target share, air yards share, WOPR, snap share, expected fantasy points) and whether the spike is signal or noise.
2. What his 2023 Panini Prizm Silver RC sells for by grade (raw, PSA 9, PSA 10, SGC 9.5, SGC 10, BGS 9.5, CGC 10, TAG), with 30/90-day trend, sales count, and active supply.
3. Its gem rate (PSA 10 rate and all-grader gem rate) and population trend.
4. For non-PSA slabs: the inferred probability each would grade PSA 10 / PSA 9 on crossover.
5. Why copies fail to reach PSA 10 (centering / corners / edges / surface; front vs back).
6. A strategy: what to buy (grade/grader/raw), max entry, exit target and timing, thesis-break triggers, position size.

The system must also discover opportunities beyond my watchlist each week.

## 3. M0 — Data-source evaluation (stop for my approval)

Known state as of Oct 2026 — verify each:
- eBay Finding API (findCompletedItems) was decommissioned Feb 2025. Marketplace Insights API (sold data) is closed to new users. Browse API is active listings only and production access needs approval. No direct eBay HTML scraping in scheduled jobs.
- Sold comps: Card Ladder (eBay, Goldin, Fanatics Collect/PWCC, Heritage, more; business API; long history), The Card API (/sales; free tier 3-day lookback, paid 90-day), SoldComps (REST, ~90 days), 130point (no official API; exposes accepted best-offer prices), Apify actors, PSA Auction Prices Realized. Most eBay-derived feeds cap at ~90 days.
- Population / grading: GemRate (PSA, BGS, SGC, CGC pops, daily, 1–2 day pop lag; partner API), PSA pop (website only — the official PSA Public API is cert lookup only; check its daily call cap and budget calls), SGC/BGS/CGC/TAG pop pages, TAG DIG reports via public cert lookup (1000-pt TAG score, 8 front/back subgrades, defect annotations, centering measurements).
- Key finding from my GemRate export (`fixtures/gemrate/tyler_shough.csv`, already in this repo): every card has a stable 40-hex `gemrate_id`, and Card Ladder search accepts `gemRateId=<id>` (plus `&grade=g9` / `g10`). Use `gemrate_id` as the external canonical card key and evaluate the GemRate + Card Ladder pairing first.

Deliverable `docs/data-sources.md`: per source — coverage, history depth, grader/grade fields, best-offer handling, cost, rate limits, ToS posture, reliability. Benchmark the top 3 comp sources on a 20-card test set (2023 Prizm Michael Wilson Silver RC; Tyler Shough 2025 Prizm Silver #327 and #429; 2025 Topps Chrome Refractor #398; plus Optic Holo, a numbered parallel, an auto). Metrics: 90-day sales found vs. a hand-verified count, grade-parse accuracy, cost per weekly run. Recommend a primary and a fallback. Every source sits behind an adapter interface; scraper adapters are off by default and flagged in the UI.

## 4. Data model (propose final DDL in the plan)

- dim_player: gsis_id, name, pos, team, rookie season, draft round/pick, age, card-market name aliases.
- fact_player_week: additive components so any window rate is recomputed from sums — snaps, team snaps, targets, team targets, air yards, team air yards, receptions, yards, TDs, carries, team carries, inside-20/inside-10 targets and carries from pbp, ffopportunity expected fantasy points, NGS fields (separation, cushion, YAC over expected; rush yards over expected).
- fact_team_context_week: injuries, depth chart changes, starting QB, pass rate.
- dim_card: gemrate_id, year, manufacturer, product, subset, card_no (required), parallel, print run, variation, player_ids (multi-player cards link to each player with multi_player=true), is_rc (from source, never inferred from year), pre_nfl flag (college/NIL products such as Bowman University, Sage, Onit, Wild Card), category (Football / Multi Sport), license status from `config/products.yaml`.
- fact_sale: source, sale_id, date, price, sale type (auction / BIN / best offer accepted; store the true accepted price when known), title, grader, grade, qualifier (PSA OC/ST/PD/MC/MK/OF), subgrades, TAG score, cert no., serial no. (e.g., 23/99), image URL, card_key, match_confidence.
- fact_listing: active asks (Browse API if approved, else comp source) → supply and ask/last-sale spread.
- fact_pop_snapshot: card_key, grader, grade (incl. Pristine / Black Label distinctions), count, snapshot_date → weekly deltas.
- fact_grade_detail: per cert — grader, grade, subgrades (BGS always; CGC optional; TAG 8 subgrades + score + centering; PSA/SGC subgrade add-ons if present), defect notes.
- fact_crossover_obs: before grader/grade/subgrades, after grader/grade, card_key, evidence type (serial match / image-hash match / my log / import), confirmed flag.
- config/*.yaml: watchlist, holdings, bankroll and caps, horizons, grading fees and turnaround by grader/tier, selling fees, shipping, breakout weights, thresholds, `products.yaml` (license status per product-year with source URL), `flagships.yaml` (flagship RC per rookie class — the 2025 class has both Prizm Silver and Topps Chrome Refractor). Grading tier availability changes (some PSA and Beckett tiers were paused in Aug–Sep 2026): warn when any fee/turnaround entry is >30 days old.

GemRate CSV importer spec: UTF-8 BOM; first column blank; row 1 is a group header, row 2 is the real header (Cat, Year, Set, Name, Parallel, Card #, Gems, Total, Gem Rate, All PSA, PSA 9, PSA 10, Universal Pop, Recent Cert); numbers contain thousands commas; Gem Rate is a rounded string — recompute from Gems/Total; Card # can be blank; extract gemrate_id from the URLs; Gems/Total in this export appear to be PSA-only (Card Ladder links are PSA, Recent Cert is a PSA cert) — confirm and store as grader=PSA.

## 5. Title parsing and card matching (build carefully)

- Rules-first parser: year, product, subset, card number, parallel, print run, grader, grade, qualifiers, subgrade strings ("BGS 9.5 10/9.5/9.5/9.5"), SGC 10 vs SGC Pristine 10, CGC Gem Mint 10 vs Pristine 10, BGS Black Label, TAG scores.
- Ambiguity rule: if a title lacks the card number and the player has more than one card in that product×parallel (e.g., Shough 2025 Prizm Silver #327 and #429), the sale is AMBIGUOUS → Review Queue, never assigned or averaged.
- Hard exclusions: lots, reprints, customs, raw "PSA ready / gem?" hype titles, digital, wrong year, near-miss parallels (Silver vs Silver Wave / Hyper / Disco / colored; base vs Silver).
- LLM fallback (small Claude model, structured JSON) only for low-confidence titles, then rule-validated.
- Gold set ≥300 labeled titles; target ≥98% precision on card_key + grade. Below threshold → Review Queue.
- Outliers: rolling median + MAD per card×grade; flag suspected shill / non-paying-bidder relists; keep visible, excluded from stats.

## 6. Breakout Radar (NFL)

Weekly, for every QB/RB/WR/TE:
- Opportunity: snap share, target share, air yards share, WOPR, carry share, red-zone opportunity share, expected fantasy points; QBs: dropbacks, designed rushes, xFP.
- Deltas: last week and trailing 3 weeks vs. the player's own baseline and vs. position distribution (z-scores); minimum-snap filter.
- Context: vacated opportunity (teammate out/IR), depth chart promotion, QB change, trade.
- Signal quality: weight usage over efficiency and TDs. Flag TD-driven weeks (fantasy points well above xFP) as sell-into-hype candidates.
- Breakout score: weighted composite; weights in config; documented on the methodology page.

Card coverage tiers (to bound API cost — e.g., Shough has 1,877 graded variants but only 32 with PSA pop ≥100):
- Tier A (watchlist): all cards with PSA pop ≥ a config threshold or ≥5 sales in 90 days, plus anything I pin.
- Tier B (auto-discovered breakouts): flagship RC(s) from `flagships.yaml` + base RC.
- Tier C: catalog and pop only (no sales pulls) until promoted.

## 7. Market metrics (per card × grade)

Last sale; 7/30/90-day median; sales count; trend slope; volatility; active listings; lowest ask; ask/last-sale spread; PSA10/PSA9 and PSA10/raw multiples; and:
- Price lag: price change since the week before the signal vs. breakout score. High usage + small price move = buy window; price spike far above usage change = overshoot.
- Event study (if history allows): for 2023–2025 breakouts, flagship RC price moves over 1/2/4/8 weeks, to calibrate normal repricing. If history is insufficient, say so and start accumulating.

## 8. Gem rate and population

- Gem definitions: PSA 10; BGS 9.5, 10, Black Label; SGC 10 and Pristine 10; CGC 10 / Pristine / Perfect; TAG 10 / Pristine. Report the PSA 10 rate separately; it's the liquid grade.
- Pop by grade, weekly deltas (submission velocity = incoming supply), gem-rate trend.
- Hierarchical beta-binomial shrinkage. Prior: product × parallel × year across all players → product × year → global. Parallels inside one product differ a lot (Shough 2025 Prizm: Pandora 72%, Lazer 46%, Silver 18%; Optic Uptown 10% vs Downtown 70%), so never use a set-wide prior when a parallel-level one exists. Show credible intervals; grey out raw rates when n < 30 and lead with the shrunk estimate. 1/1s are excluded from priors.

## 9. Cross-grade inference — P(PSA grade | already graded elsewhere)

Per card, a table: rows = source grade (SGC 10, SGC Pristine 10, SGC 9.5, BGS 9.5 by subgrade profile, BGS 10 / Black Label, CGC 10 / Pristine, TAG score bands); columns = P(PSA 10), P(PSA 9), P(≤8), method, n, confidence, crossover EV, break-even probability. Methods, each labeled:

1. OBSERVED crossover outcomes:
   a. Serial-number match on numbered cards: the same serial seen under another grader, then as PSA.
   b. My crossover log: a form on the site that commits to the repo via the GitHub API (fine-grained token scoped to this repo's contents only).
   c. Optional CSV import of community-reported results.
   d. Phase 2: perceptual-hash matching of the cropped card front for non-numbered cards. Store hashes and URLs only, never images. Every match needs my confirmation in the Review Queue before it counts.
   PSA certs found anywhere are verified via the PSA cert API within its daily cap.
2. MODEL — subgrade-conditioned: compare subgrades and measured centering to PSA's current published 10 standard (store the tolerance and source URL in config; commonly cited ~55/45–60/40 front, 75/25 back — verify). The lowest subgrade is the limiting factor: BGS 9.5 with 10 centering and 9.5s elsewhere ranks well above BGS 9.5 with 9 centering. TAG measured centering compares directly.
3. MODEL — distribution linking (weak prior only): equipercentile mapping between graders' grade distributions for the same card, falling back to the product×parallel pool. Strong selection bias (best-looking copies go to PSA; crossover attempts are self-selected) — low weight; say so in the UI.
4. MARKET-IMPLIED: price of an SGC 9.5 as a crack-and-resubmit option: p_mkt = (P_SGC9.5 + C − V_PSA9 − q8·(V_PSA8 − V_PSA9)) / (V_PSA10 − V_PSA9), where C = fees + shipping + capital cost and q8 = modeled P(≤8). Flag a buy-to-cross opportunity when model p exceeds p_mkt by a config margin with adequate n.

Calibrate the combined estimate against OBSERVED outcomes as they accumulate (Brier score on the methodology page).

EV math (all values net of selling fees):
- Cross with PSA minimum grade 10 (card returns in its original slab on a miss; fee still charged): EV gain = p10 × (V_PSA10 − V_current) − C. Break-even p* = C / (V_PSA10 − V_current).
- Buy-to-cross: EV = p10 × V_PSA10 + (1 − p10) × V_current_resale − purchase − C.
- Raw-and-grade: Σ P(grade) × V(grade) − raw price − C. P(grade) from the PSA distribution with a configurable adverse-selection haircut (raw copies still for sale are worse on average), improved by the centering screen when photos allow.

## 10. Why cards miss PSA 10 ("Gem Killers")

Per card and per product×parallel:
- From every cert with subgrades or TAG DIG data: share of copies where each category is the limiting factor, split front/back where available.
- PSA qualifiers seen in titles/certs (OC, ST, PD, MC, MK, OF).
- `knowledge/product_issues.yaml`: known product issues (print lines, edge chipping on colored borders, centering runs), each with a source URL. Claude may propose hypotheses; they display as UNVERIFIED until data supports them.
- Phase 2: computer-vision centering from raw listing photos (border detection → L/R, T/B ratios front and back), labeled MODEL with error bars, validated against TAG measured centering.
- Plain-English summary per card, e.g., "PSA 10 rate 18% (n=152). Limiting factor in subgraded copies: back centering 48%, surface 27%. Raw buys: require ≤55/45 front and a clear back photo."

## 11. Strategy engine (watchlist players + top N auto-discovered breakouts)

Playbooks (one primary, optional secondary): BUY_PSA10 · BUY_RAW_AND_GRADE · BUY_OTHER_GRADER_TO_CROSS · BUY_PSA9_VALUE · BUY_LOW_POP_PARALLEL · HOLD · TRIM / SELL_INTO_HYPE · AVOID.

Each output: specific card(s) and grade, max entry price, exit target and window, thesis-break triggers (e.g., target share < X% for 2 straight weeks; injured teammate returns), EV with assumptions, position size (≤ configured % of bankroll), liquidity (days to sell from sales velocity), confidence, and "what would change this call."

Rules (tunable):
- Turnaround vs. hype half-life: in-season, when grading turnaround exceeds the expected hype window, prefer already-graded copies; raw-and-grade is mostly an offseason / long-hold play.
- Seasonality: measure in-season vs. offseason price behavior from the data; don't assume.
- Licensing: league/player licensing shifted across 2025–2026 (Panini's NFL license ended Mar 31, 2026; Topps/Fanatics football products exist for 2025 and 2026). Read license status from `products.yaml` and measure any licensed/unlicensed price gap from data.
- Low PSA 10 rate + large PSA10/PSA9 multiple → check whether PSA 9 is the better value or cross candidates exist.
- Rising pop velocity + flat demand → AVOID or TRIM.
- TD-driven spike with flat usage → TRIM / SELL_INTO_HYPE.

Claude API write-up: only for watchlist players + top N breakouts (N in config). Send the structured numeric payload; request a ≤150-word rationale + risks. Model ID in config. Post-check that every number in the text appears in the payload; on mismatch regenerate once, then fall back to a template. Cache by payload hash.

## 12. Website

- This Week: Breakout Radar (player, pos, team, usage deltas, breakout score, flagship RC price change, price-lag gap, action); filters by position, max price, action.
- Player page: weekly usage charts; cards by tier with comps by grade; strategy card; gem rate; cross-grade table; gem killers.
- Card page: price chart by grade; sales table (filter grader/grade/date; link to source listing); pop history; active listings; cross-grade table; gem killers.
- Search: fuzzy ("wilson prizm silver") → card page; if several cards match (e.g., two Silver card numbers), show both side by side. Untracked cards → serverless live lookup through the comp adapter, cached.
- Portfolio: holdings, cost basis, comp-based value, unrealized P/L, recommended action.
- Review Queue: ambiguous/low-confidence matches and crossover-match candidates (approve/reject).
- Methodology: every definition, formula, weight, source, freshness timestamp; calibration stats.
- Weekly digest (also committed as `reports/{season}-wk{NN}.md`): top 10 buys, top 5 trims, biggest price-lag gaps, cross-grade opportunities, data-quality warnings. In-app only; no email.
- Design: dense dark analytics theme, tabular numerals, sparklines, accessible contrast, usable on mobile.

## 13. Scheduled jobs (GitHub Actions, UTC)

nflverse timing: pbp and player stats update nightly after games, with stat corrections Wed–Thu; NGS nightly ~3–5 AM ET; snap counts and PFR advanced at 0/6/12/18 UTC; injuries/depth charts daily 07:00 UTC; check ffopportunity's in-season release cadence and handle lag. Use off-peak minutes — GitHub delays top-of-hour cron runs.

- Weekly full run — Tuesday 15:17 UTC: freshness check (all of the week's games incl. MNF present; else retry every 3h, up to 4×) → nflverse ETL → radar → sales + listings → pop snapshots → gem rate / cross-grade / gem killers → strategy → write-ups → JSON → deploy hook → digest.
- Thursday 15:17 UTC: stat-correction + ffopportunity refresh; price/pop update for watchlist and flagged players; re-run strategy.
- Optional daily 13:07 UTC (off by default): watchlist prices + active listings only.
- Season-aware: derive season/week from nflverse schedules; handle byes, Thu/Sat games, playoffs; offseason → monthly price/pop run.
- Reliability: workflow_dispatch on every job; concurrency group; idempotent by (season, week, stage); stage retries with backoff; on failure open a GitHub issue with stage + logs; run manifest with row counts; quality gates (e.g., block deploy if sales rows drop >50% week over week).
- Secrets in GitHub Actions / Vercel env: comp API key(s), ANTHROPIC_API_KEY, PSA API token, eBay keys, storage keys, deploy hook, site auth, scoped GitHub token. Never commit secrets.

## 14. Testing and verification

- Unit tests: title parser (gold set), grade/subgrade parser, ambiguity rule, EV / break-even / market-implied math, beta-binomial shrinkage, equipercentile mapping, NFL formulas vs. the reference repo.
- Fixture tests on `fixtures/gemrate/tyler_shough.csv`: imports 1,877 rows; recomputed rates match counts (e.g., Prizm Silver #327 = 27/152, #429 = 53/193) rather than the rounded strings; #327 and #429 stay separate cards; multi-player and pre-NFL rows are flagged; gemrate_id extracted for every row.
- End-to-end dry run on a fixture week with no network.
- Acceptance: find the 2026 week where Michael Wilson's target share spiked; he appears on the radar, and his 2023 Prizm Silver RC page shows comps by grade, gem rate with n, cross-grade table, gem killers, and a strategy card — reachable in ≤2 clicks from This Week.
- Backtest buy signals on 2024–2025 if history allows; report hit rates honestly, including when they don't beat chance.

## 15. Milestones (stop for my review after each)

M0 Plan, schema, `CLAUDE.md`, data-source evaluation, my bankroll/holdings inputs → wait for approval.
M1 nflverse ETL + Breakout Radar.
M2 Card catalog (GemRate import), sales adapter, title parser + gold set, Card/Player pages, search.
M3 Pop snapshots, gem rate with shrinkage, gem killers.
M4 Cross-grade inference (methods 1a–c, 2, 3, 4), Review Queue, crossover log.
M5 Strategy engine, write-ups, portfolio, weekly digest.
M6 Scheduled jobs, deploy, monitoring, `docs/runbook.md`.
Phase 2: image-hash crossover matching; computer-vision centering.

At each milestone: show what runs, what's tested, open issues, next step. Ask me before any paid signup, any schedule change, or enabling any scraper adapter.
