# Slab Radar — Data-source evaluation (M0)

Status: **for approval** · researched 2026-10-02, benchmark set built 2026-10-06, time-sensitive facts refreshed 2026-10-29 · nothing signed up for, nothing paid.
Evidence and URLs for every claim live in `research/comp-sources.md`, `research/pop-and-grading.md`, `research/nflverse-and-infra.md`, `research/title-gold-set.md`. Labels: **VERIFIED** (primary source read or code run), **REPORTED** (secondary source), **UNVERIFIED** (inference/open).

## Bottom line

| Need | Primary | Fallback / audit | Status |
|---|---|---|---|
| Sold comps | **CardHedger API**: structured grade fields, `sale_type`, multi-marketplace, **joins on `gemrate_id` and cert** | **SoldComps** (Starter $9/mo): raw eBay rows with item URLs; recovers accepted Best Offer prices for ~50% of BO sales | **Benchmark not yet run.** Every sales endpoint needs a key or payment. Needs your approval (§3). |
| Active listings / supply | Comp source listings, if the chosen source exposes them | eBay Browse API (production access needs eBay Partner Network approval) | Defer to M2 |
| Pop / gem rate | **GemRate API** (`universal_gemrate_id`; PSA, Beckett, SGC, CGC) + your CSV exports | PSA Public API `GetPSASpecPopulation` (quota reportedly near zero) | API key is by request only. Price unknown |
| NFL usage | **nflverse via nflreadpy 0.1.5** | none needed | VERIFIED live through 2026 wk 7 (rechecked 2026-10-29) |
| Storage | **Cloudflare R2** | — | $0/mo at our size |

The single biggest risk: **eBay put sold search behind sign-in on 2026-07-22** (REPORTED, 3 sources). Every comp vendor ultimately depends on eBay data, so source recall can degrade silently. Mitigation (built in M2): store the weekly sales count per card per source, and raise an alert when it drops more than 50% week over week.

---

## 1. Sold-comp sources (PROMPT §3 dimensions)

| Source | Coverage | History | Grader/grade fields | Best Offer | Cost | Limits | ToS posture | Reliability |
|---|---|---|---|---|---|---|---|---|
| **CardHedger** | eBay, Fanatics, Heritage, "more"; `price_source` per sale (VERIFIED field) | Comps from 2020-07-01; daily price series > 1 yr (VERIFIED) | **Structured** `grader`, `grade` (PSA/BGS/SGC/CGC/CSG/HGA/Raw) (VERIFIED) | `sale_type` flags BO (VERIFIED); whether the price is the **accepted** amount: UNVERIFIED | x402 per call: comps **$0.02**, card-match $0.01, set-search $0 (VERIFIED). Subscription "from $49/mo" (REPORTED) | x402: 300 rpm light / 60 rpm heavy (VERIFIED) | Commercial API offered; redistribution terms unknown | Small vendor on Bubble.io; 48 endpoints, active development (VERIFIED spec) |
| **SoldComps** | eBay (8 sites) (VERIFIED) | 90 days (VERIFIED) | Title only; grade facet filter via `aspectFilter` | `hydrateBoa` swaps in accepted price, ~50% hit rate on ebay.com cards (VERIFIED vendor claim) | Free 100 req/mo; **$9 = 2,000**; $29 = 10,000 (VERIFIED) | 60 req/min, 240 items/request | **Scrapes eBay HTML**, bypassing the login wall; bars resale of raw data | Broke 2026-07-22 and 2026-08-18; fixed within days each time (VERIFIED changelog) |
| **The Card API** | eBay, Goldin, Lelands, SCP, Hakes, REA, TCGplayer (VERIFIED) | Lookback by tier: 3 d free / 14 d $9 / 30 d $49 / 90 d $199 (VERIFIED) | Grade fields only **~12% populated**; title otherwise (VERIFIED docs) | `listing_type = best_offer`; claims negotiated price (VERIFIED claim, not tested) | Free / $9 / $49 / $199 per month | Daily row allowance | Free tier: no persistent storage | New entrant; maturity unknown |
| Card Ladder | 30+ venues, ~20 yrs (REPORTED) | long | Structured filters in the UI | UI filter (REPORTED) | Pro $20/mo (REPORTED) | — | Personal use only (REPORTED). No public API; Cloudflare-walled | Collectors-owned since Dec 2021. **Our human ground truth** |
| 130point | eBay, Fanatics, Goldin, Heritage, MySlabs, Pristine (REPORTED) | unknown | Title only | **Shows accepted BO price** (REPORTED) | Free web | — | No API; `robots.txt` disallows `/api/`; Cloudflare 403 (VERIFIED) | Outage 2026-02-24 (REPORTED). Manual ground truth only |
| Apify eBay-sold actors | eBay | 90 d | Title only (one actor parses grades) | caffein.dev reports **list** price for BO (VERIFIED) | $0.70–$4.00 per 1k results | Apify | eBay User Agreement bans scrapers; some actors need your eBay cookie | 801 monthly users (caffein.dev) |
| PSA APR | PSA slabs only | long | PSA grade incl. qualifiers | unknown | Free web | — | **No sales API** (PSA Public API = cert/pop/order only, VERIFIED) | Cloudflare 403 |
| PriceCharting / SportsCardsPro | — | **Current values only, no sales** (VERIFIED) | Fixed grade slots | — | $49/mo | daily CSV | Purge data on cancel (VERIFIED) | Not a comp source |
| CardSight AI | eBay, Fanatics, COMC (VERIFIED homepage) | unknown | "by grading company and grade" (claim) | unknown | Free 750 calls/mo; $14.95 = 5k (VERIFIED) | 4 req/s | unknown | Unread docs; read them at M2 as a possible 3rd benchmark entrant |
| eBay official APIs | Finding/Shopping APIs decommissioned 2025-02-05; Marketplace Insights "not open to new users" (VERIFIED); Browse = active listings only (VERIFIED) | — | `conditionDescriptors` 27501/27502/27503 = grader/grade/cert (VERIFIED enum) | — | Free | 5,000 calls/day (REPORTED) | Production Buy API needs EPN approval (VERIFIED docs) | **Supply only**, if approved |

**Why CardHedger is primary.** It is the only source here with a sanctioned commercial API, structured grades (so no title parsing on the price path), and **`details-by-gemrate-id` / `comps-by-cert`**. That last point joins straight onto our `card_key`, and the `match_confidence` it returns routes to the Review Queue. At x402 rates a weekly run costs about $3. Three things it has not yet proven: that Best Offer prices are the accepted amounts, recall on low-pop parallels, and the redistribution terms. The benchmark decides the first two.

**Why SoldComps is the fallback, and why it stays off.** It is the only cheap source with real eBay item URLs and accepted-BO recovery, which makes it the right audit on CardHedger's matching. But it is eBay HTML scraping by proxy. Under CLAUDE.md it is an adapter of `kind=scraper`, **disabled by default**, flagged "SCRAPER (off)" in the UI, and kept out of cron unless you approve it. **So until you approve it, there is no automated fallback**: if CardHedger fails, comps degrade to stale data plus manual Card Ladder checks, and the UI shows the staleness.

**Rejected:** The Card API as primary (grades ~12% structured; a 90-day window costs $199/mo; it stays a possible third opinion for Goldin/REA). Apify actors (5–15× the cost, report list price on BO sales, eBay ToS risk). 130point via parse.bot (an unofficial wrapper, ~$100/mo). PriceCharting/SCP (no individual sales). PSA APR and Card Ladder (no API; Card Ladder remains the manual ground truth).

## 2. Benchmark — 20-card test set (PROMPT §3)

**Run status: not executed.** No comp source exposes sales without a key or payment, and every comp page I could reach without logging in was bot-walled (130point, PSA APR, Card Ladder, SCP all returned 403; eBay sold search requires login). I am not presenting "sales found" numbers I don't have. The one free signal is CardHedger `set-search` (VERIFIED, $0, 2026-10-02): **30-day sales of 21,740** for 2025 Prizm FB, **41,110** for 2025 Topps Chrome FB, **21,356** for 2025 Optic FB, and **8,849** for 2023 Prizm FB. That confirms coverage of the products, not of these cards.

**The set** is `fixtures/comps/benchmark_cards.csv`, generated by `scripts/research/build_benchmark_set.py`, which asserts a unique fixture match for every card:

| # | Card | PSA pop (gems/total) | Why |
|---|---|---|---|
| 1 | 2023 Prizm M. Wilson Silver #303 | — | spec; card no. REPORTED (COMC); no gemrate_id until a Wilson export |
| 2 | 2025 Prizm Shough Silver #327 | 27/152 | spec; **PSA-scoped id only** (F1) |
| 3 | Prizm Silver #429 (Rookie Variation) | 53/193 | spec; collides with #327 when a title has no card no. |
| 4 | Topps Chrome Refractor #398 | 62/221 | spec; 2025 co-flagship |
| 5 | Optic Holo #223 | 80/270 | spec; "Silver Holo" title hazard |
| 6 | Topps Chrome Football Leather Refractor #398 | 34/49 | spec numbered parallel (/150 REPORTED) |
| 7 | Prizm Autograph-Silver #327 | 124/257 | spec auto; collides with Silver #327 |
| 8 | Prizm Base #327 | 16/122 | Card Ladder id ≠ universal id (F2) |
| 9 | Prizm Lazer #327 | 146/319 | "Silver Lazer" hazard |
| 10 | Optic Base #223 | 92/224 | id mismatch (F2) |
| 11 | Topps Chrome Base #398 | 15/74 | Base vs Refractor split |
| 12 | Donruss Downtown #19 | 1,163/1,655 | highest pop; case hit |
| 13 | Donruss Rated Rookie #304 | 54/122 | cheap, high volume |
| 14 | Donruss Optic Preview Pink #304 | 49/209 | "Optic Preview" is Donruss |
| 15 | Mosaic Base #273 | 80/113 | Mosaic #273 vs #312 |
| 16 | Mosaic Reactive Purple #312 | 69/89 | second Mosaic RC number |
| 17 | Select Silver #41 | 50/144 | Select tier numbering |
| 18 | Donruss Autograph-Orange #304 | 48/137 | second auto |
| 19 | Prizm Blue Wave #327 | 54/78 | low pop: recall stress |
| 20 | Prizm Draft Picks Gold Ice #49 | 23/39 | pre-NFL; "Prizm" collision |

**Protocol** (each card × {Raw, PSA 9, PSA 10}, 90-day window, frozen on the run date):
- **Truth:** a hand count in a signed-in browser across eBay sold, 130point and Card Ladder (personal use). You or I in your browser session; about 2–3 h for 60 cells.
- **Recall** = matched ∩ truth / truth.
- **Precision** = (right card ∧ right grade) / returned.
- **Grade-parse accuracy:** title-only sources go through our parser.
- **BO accuracy:** |reported − accepted| on BO rows, with 130point as the accepted-price truth.
- **Cost:** $ per weekly run (§4).
- **Pass bar for primary:** recall ≥ 85% and precision ≥ 98% on the PSA 10 and PSA 9 cells for cards 1–7 (card 1 is the PROMPT §14 acceptance card), and BO prices accepted (not list) on ≥ 90% of BO rows.

**What running it costs** (needs approval): CardHedger x402 20 × card-match + 60 × comps ≈ **$1.40** (or its 7-day trial, REPORTED). SoldComps free tier: **$0**, inside 100 requests. The Card API: $9 Starter for a 14-day window compared like-for-like, or skip it. **Total ≈ $10.40** ($1.40 + $0 + $9), or $1.40 if The Card API is skipped.

## 3. Population / grading sources

| Source | What we get | Access | Notes |
|---|---|---|---|
| **GemRate API** | Per-card pop by grader and grade, cert lookup (Beckett subgrades when present), structured search. Daily refresh ~16:00–20:00 UTC; 1–2 day grading lag (VERIFIED) | `x-api-key`, **by request only**; price and quotas unpublished | **No TAG.** Basic plans exclude pop history, the change feed and catalogs, so we diff our own daily snapshots. GemRate counts **BGS 9.5 as a gem**: store per-grader label keys and compute "strict 10" and "gem" separately. 400/404 count against quota |
| GemRate CSV export (your exports) | Gems/Total per card + ids (F1–F5) | manual | **Open: are Gems/Total PSA-only?** Evidence leans PSA-only (`grader=psa` page scope, PSA-scoped Card Ladder ids) but is UNVERIFIED. One API call on #327 Silver settles it. Until confirmed, the CSV rate is displayed as "gem rate (GemRate export, scope unconfirmed)" — not as PSA 10 rate and not as all-grader gem rate. Confirming it is the first GemRate API call |
| PSA Public API | Cert, images, **`/pop/GetPSASpecPopulation/{specID}`** (VERIFIED in swagger) | PSA login token | **Daily cap unknown.** Reported 100/day early 2026, then ~1/day and "free tier killed" in June 2026 (REPORTED, forum). (My unauthenticated probe of `/publicapi/Help` returning 429 says nothing about token quota — not evidence.) **Cert verification budget:** OBSERVED crossovers need one cert lookup each — expected < 5/week from your log. Plan: you create a PSA token (Collectors Club status may matter); first call measures the real cap; budget = min(cap, 5)/day, queued, never retried within a day. Fallback if the cap is ~0: GemRate API `/certs/psa/{cert}` (same quota as pop), else manual entry with a screenshot URL. Pop endpoint is backup only |
| SGC / CGC / BGS / TAG web pops | Manual per-card lookups | web | beckett.com offline since ~2026-09-09; **TAG ToS forbids scraping** (VERIFIED). No scrapers for any of them |
| **TAG DIG (subgrades, score)** | Per-cert 1000-pt score, 8 subgrades, defects | **Manual entry only**: a form on the Card page (cert + values + DIG URL), stored with `source='manual_tag_dig'` | No API, GemRate has no TAG, ToS bars automation. Consequence: TAG cross-grade rows, TAG gem-killer stats and TAG score bands exist only for certs you enter; until then they show "no data (manual source)" rather than a model guess |

Grading inputs for `config/fees.yaml` (each with `effective_date` and `status`), as of 2026-10-02, **refreshed 2026-10-29 by web search (REPORTED unless noted)**:
- **PSA:** Value tiers still paused; no reopening date. PSA backlog tracker: 8.2M units on 2026-10-06 (from 9.0M on 09-22; reopening tied to ≤5M). Standard $59.99 (90–100 BD), Priority $79.99, Express $199.
- **BGS:** **conflicting.** News reports Base (with subgrades) $17.95 and Standard $34.95 reopened 2026-09-15 via a temporary form (100-card cap; no $14.95 no-subgrade Base, no Priority). But beckett.com itself showed Base/Standard paused on 2026-10-02 (VERIFIED then). Express $79.95 open either way. Mark `status: unverified` until a submission form is checked by hand.
- **SGC:** Standard $50 since 2026-09-02 (REPORTED).
- **CGC:** Bulk $17 through WalkThrough $300 (VERIFIED).
- **TAG:** **Value tier reopened ~2026-10-20/21 at $29.95, 10-card minimum, ~90 BD** (REPORTED, two sources disagree by a day; TAG says backlog ~99% cleared). Other tier prices conflict across sources (Base $39.95 / Standard $59.95 / Express $149.95 vs. the older Priority $149 / Walkthrough $299). Check taggrading.com by hand before entering.
- **PSA crossover** charges the full fee even below your minimum grade (VERIFIED, Wayback 2025-07-05). The cross-grade EV in plan §8 already assumes this.

## 4. Weekly-run cost (~150 card×grade pulls/week in season, incremental 10-day window)

| Item | $/month |
|---|---|
| CardHedger x402 (≈150 × $0.02/wk + one-time card-match) | ≈ $13 |
| SoldComps Starter (only if you enable the audit) | $9 |
| GemRate API | **unknown**: ask GemRate |
| R2, GitHub Actions, Vercel Hobby | $0 at this size (Hobby is non-commercial only) |
| Claude write-ups (Haiku 4.5, ~40 × ≤150 words, cached) | < $1 (estimate) |
| **Total, known items** | **≈ $13–23** + GemRate |

## 5. NFL data (nflverse)

nflreadpy 0.1.5 (polars). Canonical key `gsis_id`. `snap_counts` bridges through `load_players().pfr_id` (1,814/1,820 matched; the 6 unmatched go to a warning list). 2026 is live: weeks 1–7 complete in `player_stats`, `snap_counts` and `ff_opportunity` as of 2026-10-29 (byes visible: 30/28/28 teams in weeks 5–7); week 8 starts tonight. nflverse scheduled jobs start **4–6 h late** (VERIFIED run history), so a freshness gate runs before every ETL. Participation (routes) is **unavailable in-season** (`load_participation(2026)` raises).

One item in `research/nflverse-and-infra.md` "Open items" proposes prototyping route *estimates* from 2025 participation. That violates the hard rule (no routes, TPRR, YPRR, estimates or proxies) and is **dropped**.

Also worth deciding: nflverse overwrites the current season with stat corrections, so we store our own `as_of` snapshots per run. That's cheap, and it keeps "what we knew Tuesday" reproducible.

## 6. Adapter contract and switches

- Every source implements `CompAdapter` / `PopAdapter`, which declares `kind ∈ {api, licensed_feed, scraper}`, `enabled_by_default`, cost per call and rate limit.
- `config/sources.yaml` holds the on/off switch per source.
- Scrapers ship with `enabled: false`. Turning one on needs both the config edit and your approval (CLAUDE.md). The UI shows a red "SCRAPER (off)" chip.
- Raw responses are persisted to Parquet before parsing, so a vendor swap keeps history.
- x402 payments need a funded USDC wallet key in GitHub Actions secrets. If you prefer, the CardHedger subscription key avoids holding a wallet, at a higher cost.

## 7. Decisions needed from you

1. Approve the **~$10 benchmark**: CardHedger x402 ≈ $1.40 (or trial) + SoldComps free key + optional The Card API $9. You create the accounts; I run the harness. Plus 2–3 h of hand counts, by you, or by me in your browser session.
2. **x402 wallet vs CardHedger subscription** for production.
3. **Request a GemRate API key** and pricing (needed for pop deltas and cross-player gem priors).
4. **`card_key` fallback to the PSA-scoped id** (plan F1). This refines the CLAUDE.md key rule.
5. Keep SoldComps as a **disabled-by-default audit adapter**, or drop it.
