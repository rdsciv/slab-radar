# Slab Radar — project rules for agents

Private tool for Ryan: weekly NFL usage (nflverse) × sports-card market data → per-player card strategy.
Spec: `PROMPT.md`. Plan: `docs/plan.md`. DDL: `docs/schema.sql`. Sources: `docs/data-sources.md`. Lessons: `docs/lessons.md` (read it first; append when corrected or when a test disproves an assumption).

## Hard rules
- **NFL metrics = recorded only.** Allowed: nflverse-data, nflreadpy, nflfastR pbp, PFR snaps via nflverse, NGS via nflverse, ffopportunity (labeled MODEL). Never routes run / TPRR / YPRR / any estimate or proxy.
- Check `~/Developer/warpy/groknflanalytics/nflanalytic` (wiki/code, wiki/concepts, SCHEMA.md) before defining an NFL metric and reuse its formula; if it lacks one, use the nflverse source definition and cite it.
- Use nflverse's `air_yards_share` denominator (team **passer** air yards), not Σ receiver air yards.
- **Every card-side number carries a label (OBSERVED | MODEL | MARKET_IMPLIED), n, and an interval.** Never show a model output as an observation.
- Rounding: prices whole dollars ($5 steps above $500); rates whole percent; n next to every rate.
- Ambiguous sale titles (no card no. and >1 card for player×product×parallel) → Review Queue. Never assign or average.
- `is_rc` comes from a source, never inferred from year. 1/1s excluded from gem-rate priors.
- Strategy decisions are deterministic code. Claude writes rationale text only; every number in the text must appear in the payload.
- GemRate: `card_key = gemrate_id` if present else `sr_<sha1(natural_key)>`; keep `cardladder_gemrate_id` separately (they differ on some rows).

## Ask Ryan before
Any paid signup or trial · enabling any scraper adapter · changing any cron schedule · pushing to remote / deploying · anything irreversible. No direct eBay HTML scraping in scheduled jobs. Never commit secrets.

## Stack and commands
- ETL: Python 3.12, uv, polars, duckdb, nflreadpy — `cd etl && uv run pytest`, `uv run slab-radar run --season S --week W --stage all --offline`
- Web: Next.js 16 App Router + TS; auth in `proxy.ts` — `cd web && npm run build && npm test`
- Store: Parquet on Cloudflare R2 (source of truth) → DuckDB rebuilt per run.
- Jobs: GitHub Actions; workflow_dispatch + concurrency + idempotent (season, week, stage).

## Milestone discipline
Stop for review after each milestone (M0–M6). At each: what runs, what's tested (with output), open issues, next step; run an independent code-review subagent first.
