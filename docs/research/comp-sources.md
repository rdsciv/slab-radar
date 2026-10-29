# Comp sources — M0 research (sold comps for graded/raw NFL cards)

Accessed **2026-10-02** unless noted. No accounts created, no keys requested, nothing paid. Probes were one-off GETs/POSTs to public pages or documented free endpoints.

**Labels.** VERIFIED = read on the primary source page this session (URL given). REPORTED = secondary source (blog/forum/search snippet/third-party docs). UNVERIFIED = could not confirm; treat as a hypothesis. "unknown" = no source found.

**Headline (what changed since the brief was written):**
1. **eBay put sold/completed search behind sign-in on 2026-07-22** (REPORTED by 3 independent sources incl. SoldComps' own changelog). Every eBay-HTML-based source (Apify actors, SoldComps, 130point's eBay leg) is now running on a workaround or a user's cookie. This is the dominant risk in the whole category.
2. **CardHedger has a real, documented, multi-marketplace API with structured grade + sale_type fields, accepts GemRate IDs directly, and sells per-call access with no subscription ($0.01–$0.02/call via x402)** (VERIFIED from its OpenAPI spec + pricing JSON). It's the best fit for Slab Radar's `gemrate_id`-keyed catalog.
3. PriceCharting/SportsCardsPro API returns **current values only — no individual sales, no history** (VERIFIED). It can't be a comp source; at most a sanity check.
4. No official Card Ladder API was found. Card Ladder is Cloudflare-walled to automated fetches; an "enterprise API" is mentioned only by one blog post.

---

## 1. eBay official APIs — claim check

| Claim (user's "known state") | Verdict | Evidence |
|---|---|---|
| Finding API `findCompletedItems` decommissioned Feb 2025 | **REPORTED, consistent.** Finding + Shopping APIs decommissioned **2025-02-05**; `findCompletedItems` access had been restricted since 2020-10-15. | eBay community alert thread "Finding API and Shopping API to be decommissioned in 2025" (https://community.ebay.com/t5/Traditional-APIs-Search/Alert-Finding-API-and-Shopping-API-to-be-decommissioned-in-2025/m-p/34631345); Collectors Universe forum on the 2020-10-15 cutoff (https://forums.collectors.com/discussion/1045021/ebay-killing-api-access-for-sales-history-on-10-15). The eBay Q3-2024 newsletter page exists but was not fetched. |
| Marketplace Insights API (sold data, 90 days) closed to new users | **VERIFIED.** Quote: "The **Marketplace Insights API** is restricted and not open to new users at this time." | https://developer.ebay.com/api-docs/buy/static/ref-marketplace-supported.html |
| Browse API = active listings only | **VERIFIED (by scope).** The Browse overview describes search and getItem on *purchasable* items. It says to check `itemEndDate`/`estimatedAvailabilityStatus`, and that an item with a past end date "should not be pulled in". It has no sold/completed resource. | https://developer.ebay.com/api-docs/buy/static/api-browse.html |
| Browse production needs approval | **VERIFIED as written in eBay docs, but practice differs (UNVERIFIED for 2026).** The docs say: "The use of eBay's Buy APIs in production is intended for eBay partners only. You must apply for production access through the eBay Partner Network… no guarantee… will be approved." Process: (1) join EPN; (2) submit the Buy API Application with mocks and data flows; (3) EPN answers within 10 business days; (4) open a dev-support ticket "Buy API Production Access (eBay user ID)" with sandbox test instructions; (5) compliance review; (6) sign contracts, possibly an MNDA; (7) production access is enabled. Separately, many hobby developers report calling `item_summary/search` with a default production keyset. I did not confirm that this still works in 2026. | https://developer.ebay.com/api-docs/buy/static/buy-requirements.html |
| Default limit 5,000 calls/day | **REPORTED.** eBay staff on the forum: "the limit of 5000 API calls/day … applies to the application level as a whole." Increases come through the free **Application Growth Check**. The official limits page returned 403 to my fetch. | https://community.ebay.com/t5/eBay-APIs-Talk-to-your-fellow/About-API-limit-calls/td-p/34671615 ; https://developer.ebay.com/develop/get-started/api-call-limits (403) |
| Browse returns grader/grade/cert for cards | **Partly VERIFIED.** eBay defines structured trading-card condition descriptors: Professional Grader **27501** (PSA = 275010, BGS = 275013, CGC = 275015, …), Grade **27502**, Certification Number **27503** (free text). The Feed API has returned `conditionDescriptors` since v1_beta.35.0 (2023-07-11). That Browse `getItem` also returns `conditionDescriptors` and `localizedAspects` is REPORTED, not fetched (the type page returned 403). | https://developer.ebay.com/api-docs/user-guides/static/mip-user-guide/mip-enum-condition-descriptor-ids-for-trading-cards.html ; Feed release notes embedded in https://developer.ebay.com/api-docs/buy/browse/resources/item/methods/getItem.html |
| (new) eBay sold search now requires login | **REPORTED, 3 sources.** URLs with `LH_Sold=1`/`LH_Complete=1` 307-redirect logged-out users to signin.ebay.com, starting **2026-07-22** on all marketplaces. Scavio dates it to late August, and SoldComps logged a mobile login wall on Aug 18. I couldn't reproduce it myself because Akamai returned 403 to curl for both the sold and active searches. | https://www.openwebninja.com/blog/how-to-get-ebay-sold-and-completed-listings ; https://scavio.dev/blog/ebay-sold-listings-api-login-wall-2026 ; https://sold-comps.com/changelog |
| (new) eBay ToS on automation | **REPORTED.** The User Agreement bars "any robot, spider, scraper, data mining tools … or other automated means to access our Services for any purpose, except with the prior express permission of eBay". The 2026-01-20 update added a ban on LLM buy-for-me agents. | https://www.theregister.com/2026/01/22/ebay_updates_legalese_to_ban/ ; https://www.ebay.com/help/policies/member-behaviour-policies/user-agreement?id=4259 (not fetched) |
| (new) eBay's own Price Guide | **REPORTED.** Launched 2025-11-19 inside the eBay app (Scan Cards). It shows 2 years of eBay sales **including Best Offer accepted prices** plus PSA pop. There is no API. | https://sportscollectorsdigest.com/ebay-launches-new-digital-price-guide-for-sports-cards |

**Implication:** an official eBay route to sold data is closed to us. Browse is useful only for **supply** (active asks, lowest ask), and only if production access is granted or still works with default keys.

---

## 2. Source-by-source matrix

### 2a. Summary table

| Source | Coverage | History | Grade fields | Best Offer | Cost (public) | Limits | Auth | Query by canonical id? | ToS posture |
|---|---|---|---|---|---|---|---|---|---|
| **CardHedger** (api.cardhedger.com) | "eBay, Fanatics, Heritage Auctions, and more" (REPORTED marketing); `price_source` field per sale (VERIFIED) | `comps` reads sales **from 2020-07-01** onward; `prices-by-card` daily series, pageable back > 1 yr (VERIFIED) | **Structured**: `grade` ("PSA 10", "BGS 9.5", "Raw"), `grader`; PSA/BGS/SGC/CGC/CSG/HGA + Raw (VERIFIED) | `sale_type` = "Auction" / "Best Offer" (VERIFIED). Whether the price is the **accepted** amount: UNVERIFIED | **x402 pay-per-call, no account:** comps $0.020, card-match $0.010, prices-by-card $0.020, set-search $0.000 (VERIFIED). Subscription "from $49/mo" w/ 7-day trial (REPORTED; limits unknown) | x402: 300 rpm cheap / 60 rpm heavy per payer (VERIFIED). Subscription: "per-minute and per-day allowance" by tier (numbers unknown) | `X-API-Key` header, or x402 (USDC on Base) | **Yes: `details-by-gemrate-id`, `fmv-by-gemrate-id`**, plus `comps-by-cert` (VERIFIED). Own `card_id` (Bubble-style id) for `comps` | Commercial API offered; `sales-by-search` "Commercial Agreement Required". Redistribution terms: unknown |
| **SoldComps** (sold-comps.com) | eBay 8 sites (+ TCGplayer, Mercari, Poshmark betas) (VERIFIED) | "up to 90 days" (VERIFIED); `soldAfter`/`soldBefore` filters | **Title-only** + eBay sidebar `aspectFilter` (e.g. facet "Professional Grader"/"Grade") for filtering, not per-item fields (VERIFIED) | `bestOfferAccepted` boolean; **`hydrateBoa=true` replaces soldPrice with the accepted amount via eBay's Price Guide, "~50% hit rate on ebay.com cards"**, +1 request per call when ≥1 item hydrates (VERIFIED) | Free 100 req/mo; $9 = 2,000; $29 = 10,000; $79 = 50,000; one-time credit packs since 2026-08-31 (VERIFIED) | 60 req/min all plans; up to 240 items/request (VERIFIED) | API key (signup, no card) | No (keyword only) | Its ToS bars reselling raw data "as a standalone data product" (VERIFIED). **It scrapes eBay HTML**: its changelog has "Fix: sold listings gated behind eBay login" (Jul 22) and "a workaround that bypasses the login wall" (Aug 24), and it optionally forwards *your* eBay cookies (`X-eBay-Cookies`) |
| **The Card API** (thecardapi.com) | 7 platforms: eBay, Goldin, Lelands, SCP, Hakes, REA, TCGplayer (VERIFIED docs) | Lookback by tier: Free 3 d, Starter 14 d, Builder 30 d, Pro 90 d; "Unlimited Lookback" add-on $99/mo (VERIFIED) | `grader`/`grade`/`cert` fields exist but are **~12% populated**; otherwise title (VERIFIED docs) | `listing_type` ∈ auction/fixed_price/best_offer; marketing: "captures the actual negotiated price on Best Offer transactions" (VERIFIED claim, not tested) | Free $0 (5,000 rows/day); Starter $9; Builder $49; Pro $199 (VERIFIED) | Daily row allowance; ≤1,000 rows/request; resets 00:00 UTC; no per-minute limit stated (VERIFIED) | `x-market-api-key` header (401 without it, VERIFIED by probe) | Own **UCID** catalog ids (Catalog API is a $29 add-on and included in Pro). Sales are queried by `q` text | **Free tier: personal/non-commercial, no persistent storage.** Starter allows 500k stored records; no bulk re-exposure (VERIFIED /terms) |
| **Card Ladder** | 30+ platforms (eBay, Goldin, PWCC/Fanatics, Heritage, MySlabs, Pristine, Alt, …) "back to 2000" (REPORTED from Zendesk via search) | 20+ yrs (REPORTED) | Structured grade filters in the UI (REPORTED); the `gemRateId=<40-hex>&grade=g9\|g10` URL format is **VERIFIED from our local GemRate export** (`fixtures/gemrate/tyler_shough.csv` links) | UI filter by listing type "Best Offer" (REPORTED); accepted-vs-list price **UNVERIFIED** | Pro $20/mo or $200/yr since 2025-02-01 (REPORTED) | n/a | Web login | Yes, in the UI via `gemRateId` (no API) | ToS reportedly personal, non-commercial use only (REPORTED; cardladder.com/terms returned a Cloudflare 403). **No official public API found**; "enterprise API" claim comes from one blog (consignr.com, REPORTED/UNVERIFIED) |
| **130point** | eBay, Fanatics Collect (ex-PWCC), Goldin, Heritage, MySlabs, Pristine; ">15 million sold items" (REPORTED; App Store listing) | unknown | Title-only (REPORTED) | **Shows accepted Best Offer price** next to the struck-through list price (REPORTED, several guides). Mechanism unknown; a 2020 forum guess says 130point got eBay-approved data access (UNVERIFIED) | Web: free, no login (REPORTED). App: $9.99 / $14.99 / $24.99 per month (REPORTED, App Store) | n/a | none (web) | No | **No official API.** `robots.txt` has `Disallow: /api/` (VERIFIED). Site sits behind Cloudflare JS challenge (VERIFIED: 403). Reported outage 2026-02-24 ("missing most sales") |
| **Apify eBay-sold actors** | eBay only | ~90 days (eBay's window) | Title-only, except `vonsensey/ebay-trading-card-comps-scraper-api`, which parses grader/grade into fields (VERIFIED store listing) | caffein.dev: "soldPrice reflects the asking price for BOA items" (VERIFIED) → **list price, not accepted** | caffein.dev **$4.00/1k results on the FREE tier, $2.50/1k at GOLD+** (VERIFIED via Apify API); dami_studio $0.70/1k; tnodes $2.00/1k; vonsensey $0.008 → $0.0035 per listing; ebay-sold-lite $0.07 per query (VERIFIED) | Apify platform | Apify token | No | eBay UA bans scrapers. dami_studio **requires your eBay login cookie**; tnodes uses residential proxies plus TLS impersonation (VERIFIED from their docs) |
| **Apify 130point actors** | — | — | — | — | **None exist**: Apify Store API `search=130point` returns 0 actors (VERIFIED, `https://api.apify.com/v2/store?search=130point`) | — | — | — | Third-party wrapper **parse.bot** sells an unofficial 130point API: `search_sold_items` 5 credits/call, returns accepted price + `original_price` (REPORTED). Plans $0 (200 credits) / $30 (1,000) / $100 (5,000) / $300 (20,000) |
| **PSA APR** (psacard.com/auctionprices) | PSA-graded items only. Sources: eBay, Heritage, Goldin, Memory Lane… (REPORTED); "over 5 million auction results" (REPORTED) | long (unknown exact) | Structured **PSA grade** incl. half grades and qualifiers (REPORTED) | Mostly auctions; BIN often missing (REPORTED from forum). Accepted-BO handling unknown | Free web | n/a | n/a | PSA spec/cert (no API) | **No sales API.** The PSA Public API is cert lookup only (`GetByCertNumber`), bearer token from a PSA login (VERIFIED https://www.psacard.com/publicapi/documentation); a third-party report says 100 calls/day free (REPORTED). Web is Cloudflare-walled (VERIFIED 403) |
| **PriceCharting / SportsCardsPro** | Sports cards live on sportscardspro.com (pricecharting search links there, VERIFIED) | **API/CSV: "only support current item values… Historic prices and historic sales are not supported."** (VERIFIED) | Fixed price slots: `loose-price` = ungraded, `graded-price` = grade 9, `box-only-price` = 9.5, `manual-only-price` = **PSA 10**, `bgs-10-price`, `condition-17` = CGC 10, `condition-18` = SGC 10, etc. (VERIFIED) | unknown (methodology page 403) | **Legendary $49/mo** needed for API + daily CSV (VERIFIED on pricecharting.com/pricecharting-pro; SCP is the same company, SCP pricing page 403) | CSV regenerated every 24 h | `t=<40-char token>` | Own product id | "All data gathered from the API or CSV must be purged after your subscription has ended." (VERIFIED) |
| **Market Movers (Sports Card Investor)** | multi-marketplace (REPORTED) | unknown | UI | unknown | $9.99 / $24.99 / $49.99 per month (REPORTED) | — | app login | No | No API found (REPORTED). Card pages return 202-empty or 405 to fetchers (VERIFIED) |
| **CardSight AI** (cardsight.ai) | eBay, Fanatics Collect, COMC, "other public marketplaces" (VERIFIED homepage) | unknown | "organized by grading company and grade" (VERIFIED claim) | unknown | Free 750 calls/mo (4 req/s); $14.95 = 5k; $74.95 = 30k; $199.95 = 100k (VERIFIED) | as tiered | API key (signup) | unknown | unknown. Worth a docs read at M1 |
| **GemRate API** (api.gemrate.com) | pop/cert, not sales | — | — | — | unknown | unknown | `x-api-key` (VERIFIED docs) | Native `gemrate_id` | GemRate "integrates with Card Ladder for recent transactions" (REPORTED, slabnomics). This is where the CL `gemRateId` links come from |
| **Alt / Goldin / Fanatics Collect public results** | Own marketplace only | varies | Structured on Alt/Goldin lot pages (UNVERIFIED) | n/a (auctions) | free web | — | — | No | Alt: no public API (REPORTED). Apify scrapers exist for Goldin and Fanatics Collect (VERIFIED store listing). Not evaluated further: they're single-venue |

### 2b. Ownership / longevity signals

| Source | Signal | Label |
|---|---|---|
| Card Ladder | Acquired by **Collectors Universe** (PSA's parent) in **Dec 2021**. Collectors later also bought Beckett. CL says it stays grader-agnostic. | REPORTED (Sports Collectors Digest, Sports Collectors Daily, PSA article URL 403 to fetch) |
| CardHedger | Small vendor. Card ids like `1587446850514x2248…` are Bubble.io ids and set images come from a Bubble CDN, so the app is built on Bubble. Active development: 48 endpoints, OCR, x402, GemRate resolution with AI fallback. Claims "400M+ sales indexed", "99.9% uptime". | VERIFIED (spec), marketing REPORTED |
| SoldComps | Ships weekly (changelog Apr–Oct 2026). Broke on the eBay login wall Jul 22 and on the mobile wall Aug 18, then recovered each time. That's both resilience and fragility. | VERIFIED changelog |
| The Card API | New entrant. Has an MCP server, UCID catalog of 16.6M cards, Enterprise tier "signed within a week". | VERIFIED site; maturity unknown |
| 130point | Operated by "130 Point Pty Ltd" (App Store). Intermittent errors reported. | REPORTED |
| eBay-sold Apify actors | caffein.dev has 801 monthly users and 3,592 total, modified 2026-09-15. Most others have 1–16 monthly users. | VERIFIED (Apify API) |

---

## 3. Can we join on our canonical id?

Our `card_key` = `gemrate_id`, and we also keep `cardladder_gemrate_id` (plan F1/F2).

| Source | Path from `gemrate_id` → sales | Notes |
|---|---|---|
| CardHedger | `POST /v1/cards/details-by-gemrate-id {gemrate_id}` → `card_id` → `POST /v1/cards/comps {card_id, grade:"PSA 10", count≤100, include_raw_prices}` | Resolution order: direct ID, then cert cache, then GemRate population API, then AI `card-match` fallback. Returns `card_source` + `match_confidence`. "grader-specific or universal" GemRate ids are accepted, which may absorb plan F2 (CL id ≠ universal id). **`details-by-gemrate-id` is not in the x402 list**, so via x402 it's `card-match` ($0.01, text) instead. VERIFIED spec |
| Card Ladder | `app.cardladder.com/search?gemRateId=<id>&grade=g9|g10` (UI) | VERIFIED as a URL format from our fixture; not fetchable (Cloudflare) |
| Everyone else | keyword → title parse → our matcher | Collisions are real (next section) |

**Collision cases confirmed in our own GemRate fixture** (these will break any text-only source):
- 2025 Prizm Shough **#327 Silver Prizm** (total pop 152, id `a9aa80f1…`) vs **#327 Autograph-Silver Prizm** (257, `0ffb1e94…`): same number, same parallel word.
- **#429 Silver Prizm** (193, `4ef3d29d…`) is a *Rookie Variation*, a different card from #327.
- 2023 Prizm Michael Wilson **#303** Silver vs **#303 Silver Prizm Autographs** (COMC lists both under #303; REPORTED via search). eBay titles also use "Silver Lazer" for a different #327 parallel (REPORTED).

---

## 4. Card-number verification for the test set

| Card | Number | Label | Source |
|---|---|---|---|
| 2023 Panini Prizm Michael Wilson (Rookies) Silver | **#303** | REPORTED | COMC catalog "2023 Panini Prizm - [Base] #303 - Rookies - Michael Wilson" (search result), several eBay titles, SCI page title |
| 2025 Prizm Tyler Shough Silver | **#327** and **#429** (Rookie Variation) | **VERIFIED** (local) | `fixtures/gemrate/tyler_shough.csv` |
| 2025 Topps Chrome Tyler Shough Refractor | **#398** is Shough's | **VERIFIED** (local) | fixture row "Topps Chrome / Refractor / 398 / total 221 / gemRateId fffa14d5…"; eBay titles agree |
| 2025 Donruss Optic Tyler Shough Holo | **#223** | VERIFIED (local) | fixture (total 270, id `4bb867c1…`) |
| Numbered parallel (suggested): 2025 Topps Chrome Shough Football Leather Refractor #398, /150 | #398 VERIFIED; "/150" REPORTED (eBay title) | fixture total 49 |
| Auto (suggested): 2025 Prizm Shough Autograph-Silver #327 | VERIFIED (local) | fixture total 257. It doubles as the collision stressor |

---

## 5. Benchmark feasibility (20 cards × top-3 sources)

**Benchmark design:** For each of the 20 cards and each grade (Raw, PSA 9, PSA 10), compare sales the source returns for the last 90 days against a hand-verified count. The hand count is done by a human in a signed-in browser across eBay sold, 130point and Card Ladder (personal use, which is ToS-safe). Metrics:
- recall = found ∩ truth / truth
- precision = correct-card ∩ correct-grade / found
- grade-parse accuracy
- BO-price accuracy: |reported − accepted| on Best Offer rows
- $ per weekly run

### 5a. What can be benchmarked with no signup

| Source | No-signup, automated | Needs key/payment |
|---|---|---|
| CardHedger | **`set-search` is $0.000 and works unauthenticated.** Probed on 2026-10-02 (VERIFIED): 2025 Panini Prizm Football **21,740** 30-day sales; 2025 Topps Chrome Football **41,110**; 2025 Donruss Optic Football **21,356**; 2023 Panini Prizm Football **8,849**. `card-match` returns **HTTP 402** with an x402 challenge for $0.01 (not paid). Public card pages (cardhedger.com/public_card_prices/…) are a JS shell with no data in the HTML. | Every sales endpoint. Either x402 (USDC wallet, ≈ **$1.40** for the full 20×3 run, see 5b) or a trial key |
| SoldComps | Docs, changelog and terms only | Free key gives 100 req/mo. That covers the 60-pull benchmark plus BOA hydration with ~40 to spare |
| The Card API | `/api/v1/market/platforms` → **401** "Missing x-market-api-key" (VERIFIED) | Free key = 3-day window only, which is useless for 90-day recall. A 90-day test needs Pro $199 for one month, or Starter $9 + Unlimited Lookback $99 |
| 130point | **Blocked**: Cloudflare 403 for curl and WebFetch on `/`, `/sales/`, `/terms/` | No API; hand-verification in a browser only |
| PSA APR | **Blocked**: Cloudflare 403 on `/auctionprices` and the search URL | Browser-only |
| SportsCardsPro | **Blocked**: Cloudflare 403 on product pages and `/api-documentation` | $49 Legendary. Current values only, so it can't produce a "90-day sales found" figure anyway |
| PriceCharting | Reachable (200), but sports cards route to SportsCardsPro: the search for "michael wilson 2023 prizm silver" returned no football product links | — |
| Sports Card Investor / Market Movers | Card pages return 202 with an empty body (curl) and 405 (WebFetch) | app login |
| eBay (sold, active, /p/ product page) | curl gets Akamai **403** on both sold and active search. WebFetch on `ebay.com/p/6089762859` (Shough #327 Silver) showed **53 active listings** (asks from $5 raw to $1,500–$3,500 PSA 10) and **no sold section** | — |
| Card Ladder | Cloudflare 403 on cardladder.com, /pricing, /terms, and the Zendesk help center | Pro login |

**Observed sold prices for the 2023 Prizm Wilson Silver #303 and 2025 Prizm Shough Silver #327:** **none could be fetched first-hand.** Every no-login comp page was bot-walled. The only figures seen are third-party search snippets, which I'm not counting as observations: a Shough #327 Silver raw sale at "$39.99 on 2026-04-28", and Wilson #303 Silver *Auto* raw "$18 on 2026-02-27" (likely mislabelled). Neither is usable.

### 5b. Minimal paid/trial footprint to run the real benchmark (needs Ryan's approval)

| Source | Cheapest way to run 20 cards × 3 grades on a 90-day window | Est. cost |
|---|---|---|
| CardHedger | x402: 20 × `card-match` ($0.01) + 60 × `comps` with `include_raw_prices` ($0.02) | **≈ $1.40** + wallet setup; or the 7-day trial (REPORTED) |
| SoldComps | Free tier: 20 keyword pulls (one per card; grade parsed from titles) + ≤20 BOA hydrations. Or 60 if using `aspectFilter` per grade | **$0** (100 req/mo free) |
| The Card API | Pro 1 month (90-day window) | **$199**. Defer it, or benchmark on a 14-day window with Starter ($9) and compare like-for-like |

---

## 6. Weekly-run cost model (~150 card×grade pulls/week in season ≈ 650/mo)

Assumption: comps are stored incrementally in our Parquet store, so a weekly run only needs the last ~10 days of new sales. A one-time 90-day backfill happens at onboarding.

| Source | Calls per weekly run | Plan needed | $/month | $/weekly run |
|---|---|---|---|---|
| **CardHedger (x402)** | 150 × comps $0.02 (+ card-match $0.01 once per new card, cached) | none | ≈ $13 | **≈ $3.00** |
| CardHedger (subscription) | same | "from $49/mo" (REPORTED; quota unknown) | $49+ | ≈ $11.30 |
| **SoldComps** | ~60 cards × 1 req (240 items covers all grades) + ≤60 BOA hydrations → ≤120/wk ≈ 520/mo. Per-grade `aspectFilter` → ≤300/wk ≈ 1,300/mo | Starter $9 (2,000/mo) | $9 | **≈ $2.10** |
| The Card API | ~60–150 `q` queries/wk; rows ≪ 10k/day | Starter $9 (14-day window; storage of 500k records allowed). Backfill: Pro $199 × 1 mo | $9 (+$199 once) | ≈ $2.10 |
| Apify caffein.dev | ~60 queries × ~60 results ≈ 3,600–9,000 results/wk at $4.00/1k (FREE tier) | Apify plan | $60–155 | $14–36 |
| parse.bot → 130point | 150 × 5 credits = 750/wk ≈ 3,250/mo | Developer $100 (5,000 credits) | $100 | ≈ $23 |
| Card Ladder | manual only | Pro $20 | $20 | n/a (manual) |
| SportsCardsPro | 1 CSV/day | Legendary $49 | $49 | $11.30. **Values, not sales** |

---

## 7. Recommendation

**Benchmark these three:** CardHedger, SoldComps, The Card API (14-day window). Ground truth comes from hand counts in a signed-in browser (eBay sold + 130point + Card Ladder Pro, personal use).

**Primary: CardHedger.** Reasons:
- It's the only source with a documented, sanctioned commercial API.
- Grade and grader come back as structured fields, so we don't parse titles.
- It has `sale_type` and `price_source` (multi-marketplace).
- **It joins directly on `gemrate_id` and certs**, which is our canonical key, and it reports `match_confidence` that feeds the Review Queue.
- At x402 rates the weekly run costs about $3 with no subscription lock-in.

Open questions the benchmark must answer:
1. Is a "Best Offer" price the accepted amount or the list price? UNVERIFIED. Test it against 130point and SoldComps `hydrateBoa` on the same item URLs.
2. How good is recall on low-pop parallels? The `card-match` AI fallback may conflate #327 Silver with Auto-Silver.
3. What are the subscription quota and redistribution terms? Unknown. Ask CardHedger before any non-personal use.

**Fallback / audit feed: SoldComps** (Starter, $9/mo):
- It gives raw per-listing eBay data with real item URLs.
- `hydrateBoa` returns accepted Best Offer prices (~50% hit rate, per vendor).
- `aspectFilter` can pin the grader and grade facets.
- Use it to audit CardHedger's matching weekly and as hot-swap coverage.

It must be modelled as `kind = scraper` and **disabled by default**, per CLAUDE.md ("No direct eBay HTML scraping in scheduled jobs"). It *is* eBay HTML scraping by proxy, so enabling it in cron needs Ryan's explicit approval.

**Not recommended:**
- **The Card API as primary.** Only ~12% of rows have structured grades, it's a new vendor, and a 90-day window costs $199/mo. Keep it as a third opinion for Goldin/REA coverage.
- **Apify eBay actors.** They cost 5–15× more, report list price rather than accepted price on Best Offer sales, and carry eBay ToS risk.
- **130point via parse.bot.** It's an unofficial wrapper over a Cloudflare-walled site, has no API, and costs ~$100/mo.
- **SportsCardsPro / PriceCharting.** No individual sales.
- **PSA APR.** No API, and PSA-only.
- **Card Ladder.** No API; keep it as the human ground-truth UI.

### Main risks
1. **eBay data access is getting tighter**: the 2026-07-22 login wall, the 2026-01-20 anti-bot UA change, and the Marketplace Insights closure. Every source ultimately depends on eBay data. A vendor that loses its pipeline can silently degrade recall, so track weekly sales-count per card per source and alert on drops.
2. **Best Offer price truth**: Best Offer is common in card categories (SoldComps docs), and its accepted-price recovery hits only ~50% of BO items. The BO share of card sales itself is unknown. A source that reports list price inflates comps. This must be measured, not assumed.
3. **Variant collisions** (#327 Silver vs Auto-Silver; #303 Silver vs Silver Auto; "Silver Lazer"): id-keyed sources (CardHedger) reduce the risk, but only `match_confidence` plus the Review Queue make it safe.
4. **Vendor longevity**: CardHedger is a small, Bubble-built vendor and The Card API is new. Keep the adapter Protocol thin and persist raw sales so a vendor swap doesn't lose history.
5. **Licensing**: every vendor forbids bulk redistribution, and The Card API's free tier forbids storage. Slab Radar is private, so this is fine as long as it stays private. Get CardHedger's terms in writing before anything shared.
