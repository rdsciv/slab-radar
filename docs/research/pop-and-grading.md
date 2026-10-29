# Pop & Grading Research (M0)

Research date: **2026-10-02**. All sources accessed 2026-10-02 unless a different date is shown.

How claims are tagged:
- **VERIFIED**: I fetched the primary source myself: the company's own site, docs, or API spec, either live or as a Wayback snapshot from 2026.
- **REPORTED**: the claim comes from a secondary source (news, hobby blog, or forum).
- **UNVERIFIED**: no source I could fetch backs it up, or it is my own inference.

Fetch caveats. Several primary sites block non-browser clients:
- psacard.com returns 403 on most pages.
- gemrate.com returns 403 on every page.
- beckett.com is in maintenance mode.

Where a site blocked me, I used one of these instead, and each row says which:
- an official Wayback snapshot (web.archive.org), with its date;
- GemRate's own docs host `docs.gemrate.com`;
- GemRate's staging mirror `gemrate-staging.herokuapp.com`. It serves the same FAQ and Terms, © 2026.

---

## TL;DR: most decision-relevant facts

| # | Fact | Tag |
|---|---|---|
| 1 | The PSA Public API has **more than cert lookup**. The Swagger spec lists 6 GET endpoints:<br>• cert<br>• cert + "file append"<br>• **cert images**<br>• order progress<br>• submission progress<br>• **`/pop/GetPSASpecPopulation/{specID}`**, a per-spec pop broken out by grade<br>Auth is a bearer token tied to a PSA login. | VERIFIED |
| 2 | **The PSA daily cap is not published anywhere I could fetch.** Here is what a forum thread reported:<br>• 2026-06-22: "100 calls per day".<br>• 2026-06-24: an account dropped to "one API call per day".<br>• 2026-06-25: "PSA just told me they killed the free API tier". A poster with Collectors Club Premium still had access.<br>**Treat the free 100/day cap as dead or unreliable.** | REPORTED |
| 3 | **GemRate has a real API**:<br>• Base URL `api.gemrate.com/v1`, auth via `x-api-key`.<br>• Keys are only issued by contacting GemRate.<br>• Quotas are set per plan: daily or monthly buckets, and a `429 quota_exceeded` when you run out.<br>• "Basic plans" **exclude** pop history, the change feed, images, and catalog CSVs.<br>• Graders covered: **PSA, Beckett, SGC, CGC only. No TAG.**<br>• Data updates once a day, roughly 16:00–20:00 UTC. | VERIFIED |
| 4 | **PSA 10 standard**: centering "not to exceed approximately **55/45** percent on the front, and **75/25** percent on the reverse".<br>**PSA 9**: "approximately **60/40** or better on the front and **90/10** or better on the reverse". | VERIFIED (Wayback 2026-09-15, 2026-03-20) |
| 5 | **PSA crossover**:<br>• You must give a minimum grade.<br>• PSA grades the card inside its existing holder and only re-slabs it if the grade is at or above your minimum. Otherwise it is "returned to you in the original holder".<br>• "**Full grading fee is charged even if item does not meet minimum grade.**" | VERIFIED (Wayback 2025-07-05; no 2026 snapshot) |
| 6 | **PSA tiers paused**:<br>• All four Value tiers (Value Bulk, Value, Value Plus, Value Max) since **2026-06-02 15:00 PT**. They are still paused on the 2026-09-20 page.<br>• A new **Standard** tier ($59.99, 90–100 business days) launched **2026-09-14**.<br>• Regular was renamed **Priority** ($79.99) and Walk-Through was renamed **Premier** ($599). | VERIFIED (page) / REPORTED (dates and renames) |
| 7 | **Beckett tiers paused**:<br>• Base and Standard paused **2026-08-06**, with a target reopen of 2026-09-15.<br>• A reported reopen on about 2026-09-16 did not hold. **As of 2026-10-02, beckett.com says Base and Standard are paused again and only Express is open**, via a temporary form.<br>• Beckett's digital platforms are offline. | VERIFIED (live page) / REPORTED (dates) |
| 8 | The NFL **and NFLPA** named Topps (Fanatics) their "**official exclusive** trading card licensee" (NFL.com, 2026-04-02). The first set was **2025 Topps Chrome Football**, released 2026-04-15. | VERIFIED |

---

## Part A: Population and grading data sources

### A1. GemRate

| Item | Finding | Tag | Source |
|---|---|---|---|
| Graders (web) | Universal Search and the Universal Pop Report combine PSA, Beckett, SGC, and CGC. | REPORTED (search snippet; gemrate.com 403) | https://www.gemrate.com/universal-search |
| Graders (API) | `grader` enum is `[psa, beckett, sgc, cgc]`. The spec has **no TAG**. Spec lookup is PSA-only (`enum: [psa]`). | VERIFIED | https://docs.gemrate.com/openapi.yaml |
| Categories | Overall and category data uses PSA's categories. Set, item, and player data covers Baseball, Basketball, Boxing/Wrestling/MMA, **Football**, Golf, Hockey, Misc, Multi-Sport, Soccer, and TCG. | VERIFIED (staging mirror) | https://gemrate-staging.herokuapp.com/faq |
| Update time (web) | The classic pop report updates late morning ET. The Universal Pop Report updates early afternoon ET. | VERIFIED (staging mirror) | same FAQ |
| Lag | "Generally, there is a **1–2 day lag** from when a card is graded to when it appears on the pop report and is captured by GemRate." Daily grading counts come from comparing pop snapshots, not from cert feeds. | VERIFIED (staging mirror) | same FAQ |
| Update time (API) | Pop history is "updated once per day approximately between 16:00 and 20:00 UTC". A population change is dated "typically the day after grading". Daily history starts **2022-01-01**. | VERIFIED | https://docs.gemrate.com/llms-full.txt |
| Gem definition | **Gems** are:<br>• PSA 10<br>• Beckett 9.5, 10 Pristine, and Black Label<br>• SGC 10 and 10 Pristine<br>• CGC 10 (plus legacy 9.5 Gem MT), 10 Pristine, and 10 Perfect<br>The API's `gem_total` uses the matching label keys: `psa_10`; `beckett_9_5`, `beckett_10_pristine`, `beckett_10_black`; `sgc_10`, `sgc_10_pristine`; `cgc_10`, `cgc_10_pristine`, `cgc_10_perfect`. **Beckett 9.5 counts as a gem.** Keep that in mind when you compare gem rates across graders. | VERIFIED | FAQ above; https://docs.gemrate.com/gemrate-grades |
| Autos | GemRate merges PSA's separate auto and non-auto breakouts into one report. The API exposes `population_context_auto_split` on PSA certs. | VERIFIED | FAQ; llms-full.txt |
| Set taxonomy | GemRate uses PSA's taxonomy. **BGS treats parallels as separate sets**: for example, Prizm Silver is its own set, "Panini Prizm Prizms Silver". GemRate shows these "as is" and does not normalize them across graders. | VERIFIED (staging mirror) | FAQ |
| Universal matching | Each grader gets one best match per card. Variations without a match appear as solo listings. Variations are not merged. | VERIFIED (staging mirror) | FAQ |
| `gemrate_id` | It is scoped **per grader**, so one card can have up to 4 IDs. One of them is promoted to `universal_gemrate_id`, which is stable. It is the 40-hex segment after `/card/` in the URL. Example from the docs: `https://www.gemrate.com/card/d74f909463a77b5d16a878900d60e2f93710a17f/2025-cooper-flagg-topps-chrome-refractor-251`. The slug after the ID is decorative. Older IDs keep working after a match. | VERIFIED | https://docs.gemrate.com/gemrate-id |
| Universal search URL | `https://www.gemrate.com/universal-search` | VERIFIED (linked from docs) | gemrate-id doc |
| Player page URL | `https://www.gemrate.com/player?grader=psa&category=&player=<Name>`. Note the **`grader=` parameter**. | REPORTED (URL seen in search results; page 403) | e.g. https://www.gemrate.com/player?grader=psa&category=&player=Gengar |
| **Is "Gems/Total" in a player CSV PSA-only or universal?** | **Unknown; not confirmed from a primary source.** My inference: the player page is scoped by grader (`grader=psa` in the URL). The export also has PSA-specific Card Ladder links plus a separate Universal Pop link. Together that suggests the Gems and Total columns are **PSA-only**. To check, compare one row's Total with PSA's pop for that card, or call API `GET /v1/cards/{id}/population` and compare against `by_grader.psa`. | UNVERIFIED | n/a |
| API endpoints | `GET /v1/certs/{grader}/{cert}`, `/certs/{grader}/{cert}/population`, `/certs/{grader}/{cert}/images`*, `/cards/{gemrate_id}/population`, `/cards/{id}/population/history`*, `/cards/population/changes`*, `/cards/search/structured`, `/cards/search/simple` (beta), `/specs/psa/{spec_id}`, `/specs/psa/{spec_id}/population`, `/catalogs/{catalog}`*. Endpoints marked * are "not included in basic plans". Catalog CSVs exist only for `psa` and `pokemon`, each behind an allowlist. | VERIFIED | https://docs.gemrate.com/llms.txt |
| API cert extras | Beckett certs return `subgrades` "if present". PSA certs return `spec_id`. Beckett **BCCG** certs come back with a null `gemrate_id`. | VERIFIED | llms-full.txt |
| API access and terms | "Get an API key. **Contact the GemRate team** to request one." No public prices or plan limits are published. Usage is per account, by UTC day or month. 400 and 404 responses still count against quota. 403, 429, and 5xx do not. | VERIFIED | openapi.yaml (info.description) |
| Exports (web) | The player page has "Export to CSV". The user's export columns match: Cat, Year, Set, Name, Parallel, Card #, Gems, Total, Gem Rate, CL links, Universal Pop link, Recent Cert. | REPORTED | search snippet for gemrate.com player pages |
| ToS on automated access | The Terms of Use (operator: Central Park Analytics, LLC) have **no explicit clause against scraping or bots** in the text I fetched. They do reserve the right to "terminate or suspend access … for any reason". In practice, gemrate.com returns **HTTP 403** to curl and WebFetch, so it is bot-protected. **Use the API, not scraping.** Third-party Apify "GemRate scrapers" exist, but they are not sanctioned as far as I can tell. | VERIFIED (staging mirror ToS + live 403) | https://gemrate-staging.herokuapp.com/terms |
| Other | The user's Card Ladder links point to PSA (Card Ladder is Collectors-owned). Card Ladder also has its own pop feature. | REPORTED | https://www.cardladder.com/blog/new-feature-in-depth-population-reports |

### A2. PSA Public API and pop report

| Item | Finding | Tag | Source |
|---|---|---|---|
| Base URL and auth | `https://api.psacard.com/publicapi/` over HTTPS. Header: `Authorization: bearer <token>`. The token is generated from your PSA login: "OAuth 2 with password grant". You must have a PSA account. | VERIFIED | https://www.psacard.com/publicapi/documentation ; https://www.psacard.com/publicapi |
| Endpoints | From `swagger.json`:<br>• `GET /cert/GetByCertNumber/{certNumber}`<br>• `GET /cert/GetByCertNumberForFileAppend/{certNumber}`<br>• `GET /cert/GetImagesByCertNumber/{certNumber}`<br>• `GET /order/GetProgress/{orderNumber}`<br>• `GET /order/GetSubmissionProgress/{submissionNumber}`<br>• **`GET /pop/GetPSASpecPopulation/{specID}`** | VERIFIED | https://api.psacard.com/publicapi/swagger.json |
| Pop endpoint shape | `PSASpecPopulationModel {SpecID, Description, PSAPop, PSADNAPop}`. Each pop block has `Total, Auth, Grade1…Grade10`, half grades (`Grade1_5…Grade8_5`), and qualifier counts (`Grade1Q…Grade9Q`). **Many blogs say PSA has no pop API. The spec shows that is wrong.** Whether a free or basic token can call it is unknown. | VERIFIED (spec) / UNVERIFIED (access) | swagger.json |
| Cert fields | `CertNumber, SpecID, SpecNumber, Year, Brand, Category, CardNumber, Subject, Variety, GradeDescription, CardGrade, TotalPopulation, TotalPopulationWithQualifier, PopulationHigher, …`. **`SpecID` from a cert lookup is the key for the pop endpoint and for GemRate `/specs/psa/{spec_id}`.** One secondary source says the pop fields in cert responses are "always null". | VERIFIED (schema) / REPORTED (nulls) | swagger.json; https://github.com/maccann-24/sports-card-research/blob/master/02-PSA-API.md |
| Errors | A 500 usually means invalid credentials. 204 means an empty request. A 200 with `{"IsValidRequest":true,"ServerMessage":"No data found"}` means no match. | VERIFIED | documentation page |
| **Daily cap** | **Not stated on any PSA page I could fetch.** The End User Agreement is behind login.<br>• Secondary sources (Jan–Jun 2026): "100 API calls per day" on the free tier, with HTTP 429 when exceeded.<br>• Collectors Universe forum: "Limit of 100 calls per day" (80sOPC, 2026-06-22); then "my account can only make one API call per day" (2026-06-24); then "PSA just told me their killed the free API tier" (2026-06-25). Another user with "collectors club premium" still had access.<br>A probe of `api.psacard.com/publicapi/Help` with no token returned **429** on 2026-10-02. | REPORTED | https://forums.collectors.com/discussion/1123788/psa-api ; https://cardgrader.ai/blog/psa-api ; GitHub doc above |
| Paid tiers | No public price list. One secondary source says "Contact PSA … pricing not publicly listed". The forum suggests access may be tied to Collectors Club Premium. | REPORTED | same |
| Pop report (web) | `https://www.psacard.com/pop`. Set URLs look like `https://www.psacard.com/pop/basketball-cards/1986/fleer/36766` (example from the GemRate docs). | VERIFIED (URL pattern via GemRate doc) | https://docs.gemrate.com/openapi.yaml |
| psacard.com bot posture | Most pages return 403 to curl and WebFetch (Cloudflare). | VERIFIED (observed) | n/a |

### A3. SGC, BGS, CGC, and TAG pop reports and grade distinctions

| Grader | Pop report URL | Top-grade distinctions | Per-card public? | Tag | Source |
|---|---|---|---|---|---|
| SGC | `https://www.gosgc.com/pop-report` (Angular SPA; data loads through JS). A legacy pop exists at `https://sgclegacy.com/PopulationReport.aspx`. | Filter options in the SGC bundle: "10 Pristine only", "10 Gem or 10 Pristine", "9.5 MT+", … plus an "old SGC grades" toggle (the legacy 100-point scale). | Yes, a public web pop. No documented API. | VERIFIED (bundle strings) | https://gosgc.com/ (main-*.js) |
| Beckett (BGS) | Beckett pop report on beckett.com. **The site has been offline since about 2026-09-09.** Cert data can differ from Beckett's pop report, especially for off-checklist cards. | 9.5 Gem Mint (gold label), 10 Pristine, 10 Black Label. The API key `beckett_10_black` confirms Black Label is tracked separately. | Yes when online. GemRate also mirrors it. | VERIFIED (GemRate FAQ and docs; live beckett.com maintenance notice) | https://www.beckett.com/grading ; https://docs.gemrate.com/gemrate-grades |
| CGC | `https://www.cgccards.com/population-report/` returns 200. | Pristine 10, Gem Mint 10, and **Perfect 10, which is now a "Retired grade; retains Perfect 10 status"**. CSG Perfect 10 is also retired. | Yes | VERIFIED | https://www.cgccards.com/card-grading/grading-scale/ |
| TAG | Pop, rank, and chron are viewable per card through the DIG report. A "POP REPORT" menu lists categories. | **Pristine 10 = 990–1000; Gem Mint 10 = 950–989**; Mint 9 = 900–949; 8.5 = 850–899; 8 = 800–849 … 1 = 100–149. | Yes, through the DIG report. | VERIFIED | https://taggrading.com/pages/scale |

### A4. TAG DIG reports

| Item | Finding | Tag | Source |
|---|---|---|---|
| Score | "the TAG Score on a 1000-point scale, and an industry 10-point equivalent" | VERIFIED | https://help.taggrading.com/en/articles/6747781-what-is-the-tag-dig-report |
| 8 subgrades | "front and back centering, front and back corners, front and back surface, and front and back edges" | VERIFIED | same |
| Defects | "specific metrics and **defect annotations**"; stereoscopic "Card Vision" (photometric stereo) surface view | VERIFIED | same; https://taggrading.com/pages/dig |
| Measured centering | The rubric states numeric centering tolerances per grade (see B6). The help article does not say whether the DIG shows exact measured ratios. | VERIFIED (tolerances) / UNVERIFIED (measured ratio display) | https://taggrading.com/pages/rubric |
| URL pattern | "**tagd.co/CERT#**". There is also a cert search at `https://taggrading.com/pages/cert-search`. The cert format is reported as 1 letter + 7 digits. | VERIFIED (pattern) / REPORTED (format) | https://taggrading.com/pages/dig |
| Regular vs DIG+ | The Regular service gets "a streamlined report of the cause of the card's grade" instead of the full DIG+. | VERIFIED | help article |
| API | None found. | UNVERIFIED | n/a |
| **ToS** | Prohibits using "any robot, spider, crawlers, scraper, or other automatic device … that … 'mines,' scrapes, extracts … to monitor, extract, copy or collect information or data". It also bars copying or redistributing information "obtained from or through the Services". **Do not scrape TAG.** Use it only for manual, per-cert lookups. | VERIFIED | https://taggrading.com/policies/terms-of-service |

### A5. Subgrades by grader (2026)

| Grader | Subgrades? | Tag | Source |
|---|---|---|---|
| PSA | **No subgrades.** **Grader Notes** covering corners, edges, surface, and centering, with the defects that kept the card from a 10, come at **Express and above**. Only the submitter can see them. The 2026-09-20 tier list confirms "Includes Grader Notes" on Express, Super Express, Premier, and Premium. | VERIFIED (tier page) / REPORTED (scope) | Wayback https://web.archive.org/web/20260920133357/https://www.psacard.com/services/tradingcardgrading ; https://www.cllct.com/sports-collectibles/sports-cards/inside-psa-move-to-add-grader-notes-the-right-thing-to-do |
| BGS | Subgrades are **not always included**. Base is sold as "no subgrades" ($14.95) or "with subgrades" ($17.95). The scale has four areas: centering, corners, edges, and surface. Beckett cert data includes subgrades "if present". | REPORTED (tier split) / VERIFIED (cert field) | https://heavy.com/sports/cards/beckett-grading-news/ ; https://docs.gemrate.com/llms-full.txt |
| CGC | The 2026-10-02 add-on list has Pedigree, CrossOver, Error, and Custom Label, **with no subgrade add-on**. Secondary sources conflict: one says subgrades were discontinued in 2025, another says $8. | VERIFIED (absent from fee page) / REPORTED (conflict) | https://www.cgccards.com/submit/services-fees/cgc-grading/ |
| SGC | No subgrades by default. One secondary source says they are available "on request as an add-on". Unconfirmed for 2026. | UNVERIFIED | https://hobbycardindex.com/guides/psa-vs-bgs-vs-sgc-subgrades/ |
| TAG | 8 subgrades on every DIG (front and back × 4). | VERIFIED | TAG help article |

---

## Part B: Grading standards

### B6. Centering tolerances (front / back)

| Grader | Grade | Front | Back | Tag | Source |
|---|---|---|---|---|---|
| PSA | **Gem Mint 10** | "not to exceed approximately **55/45**" | "**75/25**" | VERIFIED (Wayback 2026-09-15 and 2026-03-20) | https://web.archive.org/web/20260915055526/https://www.psacard.com/gradingstandards |
| PSA | Mint 9 | "approximately **60/40** or better" | "**90/10** or better" | VERIFIED (Wayback 2026-03-20) | https://web.archive.org/web/20260320215109/https://www.psacard.com/gradingstandards?utm_source=chatgpt.com |
| PSA | Leeway rule | "A **5% leeway** is given to the front centering minimum standards for cards which grade PSA 7 or better". For example, a 65/35 front "may be deemed" to meet the PSA 9 standard "if the eye appeal of the card is good". Centering is measured "at the most off-center part of the card". | — | VERIFIED (2026-03-20) | same |
| PSA | 10 "flex rule" on borderless 2025 Topps Chrome | PSA reportedly accepts either of two reference edges. If both top/bottom and left/right are in range by either measure, the card can still be a 10. | — | REPORTED | https://www.businessofcardgrading.com/p/a-guide-to-2025-topps-chrome-centering (2026-09-03) |
| SGC | Pristine 10 | 50/50 | not published | REPORTED (SGC scale page is a JS SPA) | https://www.cardcenteringcalculator.com/articles/card-centering-tolerance-by-grade |
| SGC | Gem Mint 10 | 55/45 | not published | REPORTED | same |
| BGS | **Pristine 10** (centering subgrade) | "**50/50 all around**" | "**60/40** or better" | VERIFIED (Wayback 2026-05-03) | https://web.archive.org/web/20260503161916/https://www.beckett.com/grading/scale |
| BGS | **Gem Mint 9.5** | "**50/50 one way, 55/45 the other**" | "60/40 or better" | VERIFIED | same |
| BGS | Mint 9 | "55/45 both ways" | "70/30 or better" | VERIFIED | same |
| BGS | Black Label | All four subgrades must be 10. Black Label is tracked separately from 10 Pristine (`beckett_10_black`). | — | REPORTED (rule) / VERIFIED (key) | https://pregradecards.com/blog/what-is-bgs-black-label ; GemRate grades doc |
| BGS | 9.5 overall | Reportedly needs ≥3 subgrades of 9.5+ and the fourth ≥9. | — | REPORTED | https://blog.cardcenteringtool.com/beckett-bgs-subgrades-centering-corners-edges-and-surface-explained/ |
| CGC | **Pristine 10** | "The centering is **50/50**" | — | VERIFIED | https://www.cgccards.com/card-grading/grading-scale/ |
| CGC | **Gem Mint 10** | "not to exceed approximately **55/45**" | "not to exceed **75/25**". A Gem Mint 10 is a 10 overall where "one of the grading criteria does not meet the requirements of a Pristine 10". | VERIFIED | same |
| CGC | Mint 9 | 60/40 | 90/10 | VERIFIED | same |
| CGC | Perfect 10 | Retired grade; existing slabs keep "Perfect 10 status" | — | VERIFIED | same |
| TAG | **Pristine 10 (990–1000)** | ~**51/49** | ~**54.5/45.5** (sports), ~52/48 (TCG) | VERIFIED | https://taggrading.com/pages/rubric |
| TAG | **Gem Mint 10 (950–989)** | ~**55/45** | ~**70/30** (sports), ~65/35 (TCG) | VERIFIED | same |
| TAG | Mint 9 (900–949) | ~60/40 | ~90/10 (sports), ~75/25 (TCG) | VERIFIED | same |
| TAG | 8.5 (850–899) | ~62.5/37.5 | ~95/5 (sports), ~85/15 (TCG) | VERIFIED | same |

### B7. Crossover services

| Grader | Mechanics | Fee | Tag | Source |
|---|---|---|---|---|
| PSA | You must enter a minimum grade; use "1" to accept any grade. PSA "will grade your item in the existing holder and will only remove it and encapsulate it in a PSA holder if your item meets or exceeds the minimum grade. If your item doesn't meet the minimum grade, it is returned to you in the original holder." | "**Full grading fee is charged even if item does not meet minimum grade**" and "Regardless of the result, the grading price will be charged." **The fee is the grading tier price**, so the 2026 tier table below applies. Whether crossover can use the new Standard tier is unknown. | VERIFIED (Wayback **2025-07-05**; no 2026 snapshot found, so wording may have changed) | https://web.archive.org/web/20250705032036/https://www.psacard.com/services/tradingcardgrading/crossover |
| CGC | Takes PSA, Beckett, or SGC holders. CGC re-slabs only if the grade would be the same or higher; otherwise the card comes back in its original holder "and the full grading fee will still apply". A "Cross at Any Grade" option exists. BCCG slabs are treated as raw. | According to tier | VERIFIED | https://www.cgccards.com/submit/services-fees/cgc-grading/ |
| TAG | Reported "no-crossover rule". | — | REPORTED | https://tcgtreasury.com/resources/tag-grading-paused-2026 |

### B8. Fees and turnaround (as of 2026-10-02)

**PSA** (US cards). Prices are VERIFIED from the PSA page snapshot dated 2026-09-20. Dates are REPORTED as noted.

| Tier | Price | Max value | Est. turnaround (business days) | Status | Effective | Tag / Source |
|---|---|---|---|---|---|---|
| Value Bulk | $24.99 (reported) | $500 | n/a | **PAUSED** since 2026-06-02 15:00 PT | — | VERIFIED (paused banner) / REPORTED (price): Wayback 2026-09-20; https://www.si.com/collectibles/major-hobby-news-psa-confirms-extended-grading-pause (2026-05-28); https://pregradecards.com/state-of-card-submission-2026 |
| Value | $32.99 (reported) | $500 | n/a | **PAUSED** | 2026-06-02 | same |
| Value Plus | $49.99 (reported) | $1,000 | n/a | **PAUSED** | 2026-06-02 | REPORTED (SI) |
| Value Max | $64.99 (reported) | $1,500 | n/a | **PAUSED** | 2026-06-02 | REPORTED (SI) |
| **Standard** (new) | **$59.99** | $1,000 | 90–100 | Open; processed after existing Value and Bulk orders | **2026-09-14** | VERIFIED (price) / REPORTED (date): https://icv2.com/articles/news/view/63434/psa-adds-grading-service-tier-opens-psa-europe-facility (2026-09-22) |
| Priority (formerly Regular) | $79.99 | $1,500 | 70–80 | Open | rename reported 2026-09 | VERIFIED / REPORTED (rename, ICv2) |
| Express | $199 | $2,500 | 20–30 | Open; includes Grader Notes | snapshot 2026-09-20 | VERIFIED |
| Super Express | $349 | $5,000 | 10–15 | Open | same | VERIFIED |
| Premier (formerly Walk-Through) | $599 | $10,000 | 7–10 | Open | same | VERIFIED |
| Premium 1 / 2 / 3 / 5 | $999 / $1,999 / $2,999 / $4,999 | $25k / $50k / $100k / $250k | 5–7 | Open | same | VERIFIED |
| Premium 10 | $9,999+ (+$399 per $10k over $350k) | >$250k | 5–7 | Open | same | VERIFIED |

PSA backlog: "nearly 10 million cards" (2026-05-28) and 9.9M (2026-09-22). The target is 5M within "5–6 months". Tag: REPORTED (SI, ICv2).

**Beckett (BGS)**

| Tier | Price | Turnaround | Status 2026-10-02 | Effective | Tag / Source |
|---|---|---|---|---|---|
| Base (no subgrades) | $14.95 | 75+ BD | **PAUSED** | Paused 2026-08-06. Briefly reported reopened about 9/16, but the live page shows paused. | VERIFIED (live page: "temporarily paused Base and Standard") / REPORTED (prices): https://www.beckett.com/grading ; https://icv2.com/articles/news/view/63045/beckett-pumps-brakes-accepting-online-grading-submissions (2026-08-06) ; https://heavy.com/sports/cards/beckett-grading-news/ (2026-08-05) ; https://pregradecards.com/blog/beckett-grading-reopens-september-2026 (2026-09-16) |
| Base (with subgrades) | $17.95 | 75+ BD | **PAUSED** | same | same |
| Standard | $34.95 | 45 BD | **PAUSED** | same | same |
| Express | $79.95 | 15 BD | **Open** (temporary form, Plano TX only; no EU) | — | VERIFIED (live) / REPORTED (price) |
| Priority | $124.95 | 5 BD | Unclear. The live FAQ says only "Express is currently available". | — | VERIFIED (FAQ wording) |

Beckett.com and the Beckett app have been offline since about 2026-09-09 (REPORTED). The maintenance redirect was observed 2026-10-02 (VERIFIED).

**SGC** (all REPORTED; gosgc.com is a JS app I could not render)

| Tier | Price | Max value | Turnaround | Effective | Source |
|---|---|---|---|---|---|
| Standard | $50 (was $15–18) | $1,500 | ">40 BD" (est. 40–50) | **2026-09-02** | https://www.si.com/collectibles/sgc-latest-company-raise-grading-prices ; https://pregradecards.com/state-of-card-submission-2026 |
| Standard | $85 | $3,500 | 40–50 BD | 2026-09-02 | pregradecards |
| Expedited | $150 / $250 / $500 / $1,000 / $2,000 | $3.5k / $7.5k / $20k / $50k / $100k | 2–3 BD | as of 2026-10-01 | pregradecards |
| Expedited $100k+ | $3,750 + $375 per $10k | unlimited | 2–3 BD | as of 2026-10-01 | pregradecards |

**CGC** (VERIFIED live, 2026-10-02; working days)

| Tier | Fee | Max value | Turnaround |
|---|---|---|---|
| Bulk (25-card min) | $17 | $500 | 150 |
| Economy | $20 | $1,000 | 90 |
| Standard | $55 | $3,000 | 10 |
| Express | $100 | $10,000 | 5 |
| WalkThrough | $300 | $100,000 | 2 |
| Unlimited Value | $300 + 1% FMV | unlimited | 2 |
| ReHolder | $10 | — | 20 |

Associate and Premium members get 10% off; Elite members get 20% off. Source: https://www.cgccards.com/submit/services-fees/cgc-grading/

**TAG**

| Tier | Price | Max value | Turnaround | Status | Tag / Source |
|---|---|---|---|---|---|
| Basic | $22 | $300 | 45+ BD | PAUSED | REPORTED: https://pregradecards.com/state-of-card-submission-2026 |
| Standard | $39 | $500 | 30 BD | PAUSED | REPORTED |
| Express | $59 | $1,000 | 15 BD | PAUSED | REPORTED |
| Priority | $149 | $2,500 | ~5 BD | Open, limited slots | REPORTED: https://tcgtreasury.com/resources/tag-grading-paused-2026 (2026-06-17) |
| Walkthrough | $299 | $5,000 | 2–3 BD | Open, limited slots | REPORTED |
| "Limited drops" | $59–79, 5–10 card minimum | — | — | Randomized queue | REPORTED |

The taggrading.com banner on 2026-10-02 reads "**LIMITED REOPENING IS HERE / TAG BACKLOG TRACKER**". Tag: VERIFIED. The pricing table loads through JS and did not render.

---

## Part C: Licensing (for `config/products.yaml`)

**Key facts**
- NFL.com (published **2026-04-02**): Fanatics Collectibles, the NFL, and the **NFLPA** "announced Topps' … return as the NFL and NFLPA's official **exclusive** trading card licensee". The rights cover logos, team names, marks, helmets, uniforms, and NFL branding, with global distribution. The first set is "2025 Topps Chrome Football, released on April 15 (pre-order April 3)". Tag: **VERIFIED**. Source: https://www.nfl.com/news/fanatics-collectibles-nfl-and-nflpa-announce-multi-year-licensing-deal
- Panini's NFL exclusive ended **2026-03-31**. Tag: REPORTED. Source: https://sports.yahoo.com/articles/topps-football-comeback-april-2026-191037286.html
- **NFLPA and Panini after 2026.**
  - Background: the NFLPA terminated Panini's deal and granted Fanatics a reported 20-year exclusive starting in 2026. In Oct 2023 an arbitrator let Panini keep selling NFLPA cards while the case was pending.
  - Given the 2026-04-02 NFLPA exclusive to Topps, Panini's post-cutoff football **does not use the NFL license or the NFLPA group license**. It reportedly relies on **individual player agreements**.
  - Several blogs say "NFLPA-only" instead. That contradicts NFL.com, so treat it as wrong.
  - Tags: REPORTED for the arbitration and individual deals; UNVERIFIED for the exact rights Panini holds now.
  - Sources: https://www.nbcsports.com/nfl/profootballtalk/rumor-mill/news/arbitrator-allows-panini-to-continue-to-sell-nflpa-licensed-trading-cards ; https://www.beckett.com/news/report-fanatics-lands-20-year-nflpa-football-card-exclusive-starting-2026/ (beckett.com down) ; https://thecardshopfinder.com/guides/card-brands/topps-vs-panini/

| Product | Maker | Release | NFL license | Player rights | Tag | Source |
|---|---|---|---|---|---|---|
| 2023 Panini Prizm FB | Panini | 2023 | Licensed | NFLPA | REPORTED (Panini was the exclusive then) | Yahoo above |
| 2024 Panini Prizm FB | Panini | 2024–25 | Licensed | NFLPA | REPORTED | same |
| 2025 Panini Prizm FB | Panini | Hobby 2026-01-09; No Huddle 2026-01-23; panini.com 2026-02-02 | **Licensed** (pre-cutoff) | NFLPA | REPORTED | https://dknetwork.draftkings.com/2026/02/02/2025-prizm-football-checklist/ ; https://www.si.com/collectibles/2025-panini-prizm-football-release-guide-rare-inserts-autographs-and-parallels |
| 2025 Panini Silhouette FB | Panini | 2026-03-27 | Licensed (reported as the last licensed Panini NFL product) | NFLPA | REPORTED | search summary citing Cardboard Connection |
| 2025 Topps Chrome FB | Topps | **2026-04-15** | **Licensed** (first of the new era) | NFLPA | VERIFIED | NFL.com |
| 2025 Topps Chrome Black / Sapphire / Cosmic FB | Topps | 2026 | Licensed | NFLPA | REPORTED | https://www.checklistinsider.com/2025-topps-chrome-black-football ; https://www.beckett.com/news/2025-topps-chrome-sapphire-football-cards/ |
| 2026 Topps Chrome Black FB | Topps | 2026-07-09 | Licensed | NFLPA | REPORTED | https://legacycomicsohio.com/blogs/news/2026-topps-chrome-black-football-release-date-checklist-product-breakdown |
| 2026 Topps Flagship FB | Topps | 2026-08-21 | Licensed | NFLPA | REPORTED | https://www.beckett.com/news/2026-topps-flagship-football-cards/ |
| 2026 Bowman FB (NFL + college combined) | Topps | 2026-09-30 | Licensed | NFLPA | REPORTED | https://heavy.com/sports/cards/2026-bowman-football-release-price/ |
| 2026 Topps Chrome FB | Topps | **not announced** as of the search | Licensed (expected) | NFLPA | REPORTED | https://thecollectornation.com/releases/2026-topps-chrome-football |
| 2026 Panini Donruss FB | Panini | **2026-10-28** | **Unlicensed** (no logos or team names) | Individual player deals (reported) | REPORTED | https://thecollectornation.com/releases/2026-donruss-football-guide ; https://evoretro.ca/blogs/news/panini-unlicensed-football-cards-2026-explained (2026-09-22) |
| 2026 Panini Prizm / Optic / Select FB | Panini | unknown | **Unlicensed** if released | Individual deals | UNVERIFIED | — |

### C10. Flagship rookie card per class

| Class | Flagship RC | Tag | Source |
|---|---|---|---|
| 2023 | Panini Prizm Silver | UNVERIFIED (I lost web search access before finding a source; this is the long-standing hobby default) | — |
| 2024 | Panini Prizm Silver | UNVERIFIED (same) | — |
| 2025 | **Both**: Prizm Silver and Topps Chrome Refractor. Cardlines (2026-04-24): Prizm has "Established flagship status … stronger long-term brand equity"; Chrome "wins on autos"; "we have licensed 2025 releases of both for the first time ever". | REPORTED | https://cardlines.com/2025-topps-chrome-football-nfl-checklist-review/ |
| 2026+ | Probably Topps Chrome Refractor, since Panini 2026 is unlicensed. This is my projection. | UNVERIFIED | — |

---

## Part D: Known product issues (for `knowledge/product_issues.yaml`; all REPORTED)

| Product | Issue | Evidence | Source |
|---|---|---|---|
| 2025 Topps Chrome FB | Roller marks and indentations, mostly on card backs in the middle and right-corner areas | PSA noted "roller marks and indentations". PSA 10 rate was 24.6% for base vs ~40% for 2024, and 21.4% for RC autos vs ~50%. | https://www.si.com/collectibles/3-key-points-psa-data-2025-topps-chrome-football-cards (2026-05-21) |
| 2025 Topps Chrome FB | Centering is ambiguous because the design has no clear border. PSA reportedly applies a "flex rule" (either reference edge). | — | https://www.businessofcardgrading.com/p/a-guide-to-2025-topps-chrome-centering (2026-09-03) |
| Panini Prizm (Silver) | Print lines ("functionally disqualifying" for a 10 if visible to the naked eye); left/right centering skew toward 55/45; silver-border chipping that caps cards at 8–9; scratches on the chrome surface; heavy print lines in 2023–24 | SEO hobby blog; treat as low confidence | https://pregradecards.com/blog/panini-prizm-card-grading-guide-2026 (2026-09-28) |
| Donruss Optic | Edge chipping on dark borders; centering on Holo; print lines | Search summary only; I could not fetch the page | https://www.cardsense.app/blog/donruss-optic-set-guide |
| Colored-border chrome (general) | Border chipping is factory-born. Micro-chips under ~0.1 mm can still be a 10. | Low confidence | pregradecards (above) |

---

## Implications for Slab Radar

1. **Primary pop source: the GemRate API**, keyed on `universal_gemrate_id`, the 40-hex ID that matches your CSV links. Ask GemRate for a key and pricing. History and change feed are not in the basic plan. Without them, build your own daily snapshot diff by polling `/cards/{id}/population` once a day after 20:00 UTC. **TAG is not covered.**
2. **PSA API** is a backup at best. The free quota is reportedly near zero, so test what a token actually gets before designing around it. Note that `GetPSASpecPopulation` exists and could replace GemRate for PSA-only pop, if quota allows.
3. **Gem-rate math**: GemRate counts **BGS 9.5 as a gem**. Store per-grader label keys (`psa_10`, `beckett_9_5`, …) and calculate "strict 10" and "gem" as separate metrics.
4. **Do not scrape** TAG (ToS forbids it), GemRate (bot-blocked), or PSA (Cloudflare 403).
5. Fee and turnaround inputs change monthly. Store fees with an `effective_date` and a `status` (open or paused).
