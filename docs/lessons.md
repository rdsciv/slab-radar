# Lessons

Append-only. Each entry: date · trigger (correction or disproven assumption) · rule.

## 2026-10-02 · M0 fixture profiling
- **Not every GemRate row has a `gemrate_id`.** `tyler_shough.csv`: 441/1,877 rows have all link columns empty (all Total ≤ 28). Rule: fall back to `sr_<sha1(natural_key)>`, flag `no_gemrate_id`; never assume the id exists.
- **Card Ladder's `gemRateId` can differ from GemRate's `gemrate_id` for the same row** (13 rows, incl. 2025 Prizm Base #327). Rule: store both; pull comps with the Card Ladder id, pop with the GemRate id.
- **GemRate's "Gem Rate" string uses round-half-up; Python `round` is half-to-even** (15/24 → "63%" vs 62). Rule: recompute from counts; display with explicit half-up rounding.
- **Pre-NFL can't be inferred from manufacturer** (Panini … Collegiate, Leaf, Wild Card, Bowman University, Onit … Nil). Rule: explicit set-prefix list in `config/products.yaml`; unknown → Review Queue.

## 2026-10-02 · M0 nflverse research
- **`air_yards_share` uses team passer air yards as denominator.** Recomputing from receiver sums is off by up to 0.09. Rule: store passer-side team air yards; test equality with nflverse's column.
- **Your reference repo has no target share / WOPR / snap share / xFP definitions.** Rule: use nflverse source definitions with citation; don't claim they came from the reference repo.
- **nflverse cron jobs start 4–6 h late in practice.** Rule: freshness gate before every ETL; never assume data landed at the cron time.
- **Next.js 16 uses `proxy.ts`, not `middleware.ts`.**

## 2026-10-06 · benchmark-set build disproved plan F1's framing
- **"Has a gemrate_id" hid three states.** Universal Pop link is `gemrate_id=None` (literal string) on 1,114/1,877 rows incl. flagship Prizm Silver #327; only the PSA-scoped id in Card Ladder links exists there. Rule: parse the literal `None` as NULL; key = universal → PSA-scoped → `sr_` (pending Ryan's OK); count id states separately in every profile.
- **GemRate CSV counts can carry thousands separators** (`"1,655"`). Rule: strip `,` before integer cast; importer test includes that row.

## 2026-10-29 · M0 refresh
- **"Peak week" moved after week 4** (Wilson TS 0.371 in wk 4 > 0.340 in wk 3), while the largest self-delta stayed wk 3. Rule: acceptance tests pin a *definition* (largest last-1 self-delta vs season-to-date baseline), never "max of a live, growing series".
- **Grading-tier status goes stale within weeks and sources conflict** (Beckett "reopened 9/15" in news vs paused on its own page 10/2; TAG Value back ~10/20). Rule: `fees.yaml` entries carry `status ∈ {open, paused, unverified}` + `checked_date`; news-only changes enter as `unverified`.
