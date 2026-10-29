# M0 research: nflverse data and infrastructure

Researched 2026-10-02. Data checks ran against live nflverse releases. The newest asset timestamps were 2026-10-02 15:48 UTC for stats and play-by-play, and 2026-10-03 03:16 UTC for schedules.

**Tags**
- **VERIFIED**: I ran the code, or read the primary source myself (source code, the official docs page, or the GitHub API).
- **REPORTED**: A secondary or official source states it, but I did not test it.
- **UNVERIFIED**: An inference or an open question.

Load scripts are in the session scratchpad. Each of them is a 20-line `uv run --with nflreadpy` call.

---

## TL;DR: decisions

1. **The 2026 season is live in nflverse.**
   - Weeks 1–3 are complete: 16 games each in `player_stats`, `snap_counts`, `ff_opportunity`, `pbp` and NGS.
   - Week 4 holds only Thursday's game so far (1 of 16).
   - 2023, 2024 and 2025 are complete for weeks 1–22, REG+POST. (VERIFIED)
2. **Use `gsis_id` (`00-00XXXXX`) as the canonical player key.**
   - It is native to `player_stats.player_id`, `ff_opportunity.player_id`, NGS `player_gsis_id`, `injuries.gsis_id`, `rosters.gsis_id`, depth charts (2025+) `gsis_id`, and pbp `*_player_id`.
   - `snap_counts` is the exception. It has only `pfr_player_id`. Bridge it through `load_players().pfr_id`, which matched 1,814 of 1,820 offensive 2026 snap rows. (VERIFIED)
3. **No routes, TPRR or YPRR in-season.** Participation for 2026 is not available. `load_participation(2026)` raises `Season must be between 2016 and 2025`. FTN participation is released only after the postseason. (VERIFIED + REPORTED)
4. **Schedule the ETL for about 12:00–16:00 UTC, not right after the nflverse cron times.**
   - nflverse's own scheduled GitHub runs start 4–6 hours late. For example, the ffopportunity cron for Fri 05:45 UTC started at 11:20 UTC, and the NGS cron for 07:00 started at 13:16. (VERIFIED from the run history)
   - The safe weekly read for a Sunday/Monday slate is **Tuesday ~16:00 UTC**.
5. **Use Cloudflare R2 for storage, not Vercel Blob.**
   - R2 is S3-compatible, DuckDB has a native `r2://` secret, egress is $0, and 10 GB-month is free.
   - Vercel Blob's Hobby plan includes only 1 GB and has no S3 API, so DuckDB cannot attach to it directly.
6. **Next.js 16.3.8 is current.** Basic auth goes in **`proxy.ts`**, which exports `function proxy`. `middleware.ts` is deprecated as of v16.0.0. (VERIFIED)
7. **Vercel Hobby is non-commercial only.** If Slab Radar ever earns money (ads, affiliate links, paid tiers), it must move to Pro. (VERIFIED)

### Michael Wilson, 2026 (gsis `00-0038559`, WR, **ARI**; still ARI on the weekly roster for weeks 1–4)

| Week | Opp | Targets | target_share | air_yards_share | WOPR | Rec air yds | Off snaps (pct) | xFP (`total_fantasy_points_exp`) |
|---|---|---|---|---|---|---|---|---|
| 1 | @LAC | 7 | 0.189 | 0.293 | 0.489 | 83 | 64 (85%) | 11.13 |
| 2 | SEA | 7 | 0.269 | 0.459 | 0.725 | 50 | 47 (94%) | 8.92 |
| **3** | **@SF** | **17** | **0.340** | 0.509 | 0.867 | 162 | 81 (93%) | 32.95 |

- **Week 3 at SF is his highest 2026 target share so far: 17 targets, a 0.34 target share (17 of ARI's 50 targets), team ARI.** (VERIFIED, computed from `load_player_stats(2026)`)
- ARI's week 4 game is at NYG on 2026-10-04 and has not been played yet.
- NGS for week 3: avg_separation 2.27, avg_cushion 7.12, avg_yac_above_expectation −0.97.

---

## Part A: nflverse

### A1. nflreadpy: version and loaders

- **Version: `nflreadpy` 0.1.5** (released 2025-11-19, requires Python >=3.10). It is the latest on PyPI and in GitHub releases. (VERIFIED: https://pypi.org/pypi/nflreadpy/json, https://github.com/nflverse/nflreadpy/releases)
- All loaders return **polars** DataFrames. (VERIFIED: return type `polars.dataframe.frame.DataFrame`)
- Caching is configured through env vars: `NFLREADPY_CACHE` (`memory`/`filesystem`/`off`), `NFLREADPY_CACHE_DIR`, `NFLREADPY_CACHE_DURATION`, `NFLREADPY_TIMEOUT`. (VERIFIED: `nflreadpy/config.py`)
- Exported loaders: `load_pbp, load_player_stats, load_team_stats, load_snap_counts, load_nextgen_stats, load_injuries, load_depth_charts, load_schedules, load_rosters, load_rosters_weekly, load_players, load_ff_playerids, load_ff_opportunity, load_ff_rankings, load_participation, load_ftn_charting, load_pfr_advstats, load_combine, load_contracts, load_draft_picks, load_officials, load_trades, load_teams`, plus `get_current_season()` and `get_current_week()`. On 2026-10-02 these two returned season 2026, week 4. (VERIFIED)

**Signatures (VERIFIED, `inspect.signature`)**
- `load_player_stats(seasons=None, summary_level='week'|'reg'|'post'|'reg+post')`
- `load_nextgen_stats(seasons=None, stat_type='passing'|'receiving'|'rushing')`
- `load_ff_opportunity(seasons=None, stat_type='weekly'|'pbp_pass'|'pbp_rush', model_version='latest'|'v1.0.0')`
- `load_snap_counts(seasons=None)`

#### Columns relevant to Slab Radar (VERIFIED by loading 2026 data)

| Dataset (loader) | Grain / key | Relevant columns |
|---|---|---|
| `load_player_stats(s, 'week')` (150 cols) | one row per player-game: `player_id`(gsis), `season`, `week`, `season_type`, `game_id` | `targets, target_share, air_yards_share, wopr, receiving_air_yards, receptions, receiving_yards, receiving_yards_after_catch, receiving_epa, racr, carries, rushing_yards, rushing_epa, fantasy_points, fantasy_points_ppr, team, opponent_team, position, position_group` |
| `load_snap_counts(s)` (16 cols) | player-game: `pfr_player_id` + `game_id` | `offense_snaps, offense_pct` (0–1 fraction, e.g. 0.93), `defense_snaps, defense_pct, st_snaps, st_pct, player, position, team, opponent, pfr_game_id`. **No gsis_id.** |
| `load_nextgen_stats(s,'receiving')` (23) | `player_gsis_id`, `season`, `season_type`, `week`. **`week == 0` is the season-to-date aggregate row.** | `avg_separation, avg_cushion, avg_yac, avg_expected_yac, avg_yac_above_expectation, avg_intended_air_yards, percent_share_of_intended_air_yards` (0–100 scale), `targets, receptions, catch_percentage, yards, rec_touchdowns` |
| `load_nextgen_stats(s,'rushing')` (22) | same as receiving | `expected_rush_yards, rush_yards_over_expected, rush_yards_over_expected_per_att, rush_pct_over_expected, efficiency, percent_attempts_gte_eight_defenders, avg_time_to_los, rush_attempts, rush_yards` |
| `load_nextgen_stats(s,'passing')` (29) | same as receiving | `avg_time_to_throw, aggressiveness, avg_intended_air_yards, completion_percentage_above_expectation, …` |
| `load_ff_opportunity(s)` weekly (159 cols) | `season` (**str**), `week` (**float**), `game_id`, `player_id` (gsis), `posteam` | Expected points: `total_fantasy_points_exp, rec_fantasy_points_exp, rush_fantasy_points_exp, pass_fantasy_points_exp`. Actuals: `total_fantasy_points, rec_fantasy_points, …`. Differences: `*_diff`. Volume: `rec_attempt` (targets), `rec_air_yards, rush_attempt, receptions_exp, rec_yards_gained_exp, rec_touchdown_exp, rec_first_down_exp`. Team totals: every metric with `_team` suffix, e.g. `rec_attempt_team, total_fantasy_points_exp_team`. |
| `load_ff_opportunity(s,'pbp_pass')` (57) | play-level: `game_id, play_id`, `receiver_player_id` | `pass_completion_exp, yards_after_catch_exp, pass_touchdown_exp, pass_first_down_exp, air_yards, xpass, vegas_wp, implied_total` |
| `load_pbp(s)` (372 cols) | play: `game_id, play_id` | `receiver_player_id, rusher_player_id, passer_player_id` (gsis), `air_yards, yards_after_catch, xyac_*, cpoe, epa, pass_oe` |
| `load_injuries(s)` (16) | `season, week, game_type, gsis_id` | `report_status, report_primary_injury, practice_status, practice_primary_injury` |
| `load_depth_charts(s)` 2025+ (12) | snapshot: `dt`, `team`, `gsis_id`/`espn_id`, `pos_grp_id`, `pos_slot` | `pos_abb, pos_rank` (see A4) |
| `load_rosters_weekly(s)` (36) | `season, week, gsis_id` | `team, status, position, depth_chart_position`, plus the cross-IDs: `espn_id, sportradar_id, pff_id, pfr_id, sleeper_id, yahoo_id, …` |

**ffopportunity grain caveats (VERIFIED)**
- The key `(season, week, player_id)` is unique for non-null `player_id`.
- About 25 rows per week have `player_id = null`. These are team-level "unassigned target" rows: 162 `rec_attempt`, zero rush or pass attempts in 2026 weeks 1–3. Filter them out, or keep them only for team denominators.
- Cast `season` to int and `week` to int on ingest.

### A2. Season availability and metric definitions

**Availability (VERIFIED: `load_player_stats([y], 'week')` and `load_schedules([2026])`)**

| Season | player_stats rows | Weeks present | Season types |
|---|---|---|---|
| 2023 | 18,643 | 1–22 | REG, POST |
| 2024 | 18,983 | 1–22 | REG, POST |
| 2025 | 19,422 | 1–22 | REG, POST |
| 2026 | 3,407 | 1, 2, 3, 4 (wk 4 = 1 game) | REG |

- The 2026 schedule has 272 games.
- Weeks 1–3 have all 16 results. Week 4 has 1 of 16. (VERIFIED)
- `snap_counts`, `ff_opportunity`, `pbp`, NGS, `injuries` and `rosters_weekly` for 2026 all contain weeks 1–4, with week 4 partial. (VERIFIED)

**Definitions** (VERIFIED: nflfastR 6.0.0 `R/calculate_stats.R`, https://github.com/nflverse/nflfastR/blob/main/R/calculate_stats.R, lines 167–181 and 380–417)

```r
# grouped by season, week, team (or season, team for season summaries)
team_targets   = sum(stat_id == 115)
team_air_yards = sum((stat_id %in% 111:112) * yards)   # passer-side air yards
receiving_air_yards = sum((stat_id == 115) * team_play_air_yards)
target_share    = targets / first(team_targets)
air_yards_share = receiving_air_yards / first(team_air_yards)
wopr            = 1.5 * target_share + 0.7 * air_yards_share
```

Empirical checks on 2026 weeks 1–4 (VERIFIED):
- `target_share == targets / sum(team targets in game)`, max abs error 0.0.
- `wopr == 1.5*target_share + 0.7*air_yards_share`, max abs error 0.0.
- `air_yards_share` does **not** always equal player air yards divided by the sum of receivers' air yards (max deviation 0.093). The denominator is the team's *passer* air yards (stat IDs 111/112), which include passes with no credited receiver. Use nflverse's column as-is. Do not recompute it from receiver sums.
- For season summaries (`summary_level='reg'`), shares are computed over season totals, not as an average of weekly shares (VERIFIED, same source, `group_by` on `season, team`).

### A3. Update cadence: actual cron lines and observed behavior

Cron lines read via the GitHub API on 2026-10-02 (VERIFIED):

| Dataset | Repo / workflow | Cron (UTC) |
|---|---|---|
| pbp + player stats | `nflverse/nflverse-pbp/.github/workflows/update_data.yaml` | `3 9 * 1,2,9-12 *` (daily 09:03)<br>`33 5 * 1,2,9-12 5` (Fri 05:33, after TNF)<br>`3 22 * 1,2,9-12 0` (Sun 22:03, early window)<br>`7 0 * 1,2,9-12 1` (Mon 00:07, late window)<br>`33 5 * 1,2,9-12 1` and `33 5 * 1,2,9-12 2` (Mon/Tue 05:33, after SNF/MNF) |
| NGS | `nflverse/ngs-data/.github/workflows/update_ngs.yaml` | `0 7 * 1,2,9-12 *` |
| Snap counts | `nflverse/nflverse-pfr/.github/workflows/update_snap_counts.yaml` | `0 */6 * 9-12,1 *` and `0 */6 1-15 2 *` |
| Injuries | `nflverse/nflverse-rosters/.github/workflows/update_injuries.yaml` | `7 7 * 1,2,9,10,11,12 *` |
| Depth charts | `nflverse/nflverse-rosters/.github/workflows/update_depth_charts.yaml` | `7 7 * * *` (year-round) |
| Rosters | `nflverse/nflverse-rosters/.github/workflows/update_rosters.yaml` | `7 7 * * *` |
| Players | `nflverse/nflverse-players/.github/workflows/update_players.yaml` | `0 8 * * *` |
| ffopportunity | `ffverse/ffopportunity/.github/workflows/ep-update-data.yaml` (the repo is **ffverse**, not nflverse) | `45 5 * 1,2,9-12 5` (Fri)<br>`15 22 * 1,2,9-12 0` (Sun)<br>`20 0 * 1,2,9-12 1` (Mon)<br>`45 5 * 1,2,9-12 1` (Mon)<br>`45 5 * 1,2,9-12 2` (Tue) |

**pbp/stats** (VERIFIED, workflow source):
- The pbp workflow builds `pbp` and `pbp_stats`, then a dependent `stats` job. The release step runs `exec/update_data.R`.
- Each run regenerates the **whole current season** via `get_current_season()`. Stat corrections therefore flow in on the next run; the data is never append-only.
- `update_stats.yaml` is a manual-only (`workflow_dispatch`) rebuild.

**Official schedule page** (REPORTED: https://nflreadr.nflverse.com/articles/nflverse_data_schedule.html)
- pbp: "nightly basis after each game day (and additionally at specific points on game days)"
- player stats: same as pbp
- snap counts: 0/6/12/18 UTC in season
- NGS: "every night (in the range of 3 am – 5 am ET)"
- injuries: 7AM UTC in season
- depth charts: 7AM UTC year-round
- schedules: every 5 minutes in season
- participation: "after all post-season games are completed"

**Observed lag is the planning number (VERIFIED: GitHub Actions run history and release asset `updated_at`)**
- ffopportunity scheduled runs started at 11:20 (Fri 10-02, cron 05:45), 11:33 (Tue 09-29), 11:58 (Mon 09-28), 05:31 (Mon 09-28, cron 05:45 the night before) and 00:48 (Mon 09-28, cron 00:20). Each run takes about 2 minutes.
- So a cron of 05:45 effectively means 05:30–12:00 UTC.
- NGS: scheduled 07:00 started 13:16 (10-02) and 13:58 (10-01). nflverse also fires `workflow_dispatch` at exactly 06:00 and 09:00, presumably from an external trigger that works around GitHub delays. (UNVERIFIED as to motive)
- Asset timestamps on 2026-10-02 (UTC): `stats_player_week_2026` 15:48, `play_by_play_2026` 15:46, `snap_counts_2026` 11:01, `ngs_receiving` 13:25, `injuries_2026` 13:47, `depth_charts_2026` 13:49, `ep_weekly_2026` (ffopportunity) 11:22.
- **Implication:** a Tuesday ~16:00 UTC Slab Radar ETL sees the full Sun+Mon slate in every dataset. A Monday run will miss MNF.

**Download sizes for 2026 week 4, parquet (VERIFIED)**

| File | Size |
|---|---|
| `stats_player_week_2026` | 0.25 MB |
| `play_by_play_2026` | 3.55 MB |
| `snap_counts_2026` | 0.06 MB |
| `ngs_receiving` (all seasons, single file) | 1.08 MB |
| `ep_weekly_2026` | 0.26 MB |
| `depth_charts_2026` | 2.54 MB (594,789 rows of snapshots) |
| `players` | 3.23 MB |

The whole weekly pull is under 15 MB.

**Direct DuckDB access (VERIFIED)**
- DuckDB 1.5.6 can read the release URLs directly, for example: `read_parquet('https://github.com/nflverse/nflverse-data/releases/download/stats_player/stats_player_week_2026.parquet')`. This returned 3,407 rows, max week 4.

### A4. Depth charts: the 2025 source change, and injuries

**Source change** (VERIFIED, nflreadr dictionary)
- "the data source has changed after the 2024 season. From 2025 onwards, the following variables and descriptions will apply." (https://nflreadr.nflverse.com/articles/dictionary_depth_charts.html)
- The new source is **ESPN**. `exec/update-depth-charts.R` in nflverse-rosters calls `nflverse.espn::espn_depth_charts(season = szn)`, prepends the new rows to the existing season file, and maps `espn_id` to `gsis_id` via `nflverse.players`. (VERIFIED: https://github.com/nflverse/nflverse-rosters/blob/main/exec/update-depth-charts.R)

**Old schema (≤2024, VERIFIED)**
- 15 columns: `season, club_code, week, game_type, depth_team, last_name, first_name, football_name, formation, gsis_id, jersey_number, position, elias_id, depth_position, full_name`
- Weekly grain.

**New schema (2025+, VERIFIED)**
- 12 columns: `dt` (ISO8601 **string** load timestamp), `team, player_name, espn_id, gsis_id, pos_grp_id, pos_grp, pos_id, pos_name, pos_abb, pos_slot` (int), `pos_rank` (int).
- **There is no `week` and no `season` column.** It is a time-series of snapshots.
- 2026 has 212 distinct `dt` values, from 2026-03-22 to 2026-10-02 13:49Z, so several snapshots per day.
- `pos_grp` values are formation names: `"3WR 1TE"`, `"Base 4-3 D"`, `"Base 3-4 D"`, `"Special Teams"`.
- Example: M. Wilson appears with `pos_abb=WR, pos_slot=1, pos_rank=1` in "3WR 1TE", and as `PR` (pos_rank 2) in Special Teams.
- `gsis_id` is null on 26,796 of 594,789 rows (4.5%).

**ETL rule:** map each snapshot to an NFL week by taking the latest `dt` before that week's first kickoff (`schedules.gameday` and `gametime`). Join on `gsis_id`, falling back to `espn_id` through `load_players().espn_id`.

**Injuries** (VERIFIED)
- 2025: 6,068 rows, weeks 1–22.
- 2026: 1,025 rows, weeks 1–4.
- Columns: `season, season_type, game_type, team, week, gsis_id, position, full_name, …, report_status, report_primary_injury, practice_status, …`
- Michael Wilson has no 2026 injury rows.

### A5. Participation (routes): not available in-season

- `load_participation([2026])` fails with `ValueError('Season must be between 2016 and 2025')`. (VERIFIED)
- 2025 and 2024 exist now (45k rows each) and include a `route` column. They are post-season releases only. (VERIFIED)
- "Participation data from 2023 onwards is courtesy of FTN and is provided after all post-season games are completed." (REPORTED: https://nflreadr.nflverse.com/articles/nflverse_data_schedule.html, https://nflreadr.nflverse.com/reference/load_participation.html)
- **No in-season routes, TPRR or YPRR from nflverse.** The usable recorded metrics are `offense_pct` (snaps), `target_share`, `wopr`, and NGS `percent_share_of_intended_air_yards`.
- ~~The 2025 `route` column could be used offline to calibrate a snaps-to-routes model.~~ **Dropped 2026-10-06: violates the hard rule (no route estimates or proxies).**

### A6. ID mapping

| Dataset | Player ID column | Format | Joins to gsis? |
|---|---|---|---|
| player_stats | `player_id` | gsis `00-0038559` | native |
| ff_opportunity | `player_id` (null on team-unassigned rows) | gsis | native (VERIFIED: 100% of non-null values start `00-`) |
| NGS | `player_gsis_id` | gsis | native |
| pbp | `receiver_player_id`, `rusher_player_id`, … | gsis | native |
| injuries, rosters, rosters_weekly | `gsis_id` | gsis | native |
| depth_charts 2025+ | `gsis_id` + `espn_id` | gsis (4.5% null) | native, with espn fallback |
| snap_counts | `pfr_player_id` (e.g. `WilsMi02`) | PFR | via `load_players().pfr_id`: 4,571 of 4,579 rows matched; 6 of 1,820 offensive rows unmatched (VERIFIED) |

- `load_players()` (39 cols) has `gsis_id, esb_id, nfl_id, pfr_id, pff_id, otc_id, espn_id, smart_id, latest_team, status, …`.
- `load_ff_playerids()` (35 cols, from DynastyProcess) has `gsis_id, sleeper_id, espn_id, yahoo_id, pfr_id, mfl_id, fantasypros_id, ktc_id, sportradar_id, …`. Use it for external fantasy-platform joins. (VERIFIED)

**Recommendation:**
- Keep a `dim_player` table keyed on `gsis_id`, built from `load_players()` and left-joined to `load_ff_playerids()`.
- Bridge snap counts through `pfr_id`, falling back to roster `pfr_id`.
- Log unmatched rows instead of dropping them silently.

---

## Part B: infrastructure

### B7. Cloudflare R2 vs Vercel Blob

| | Cloudflare R2 (Standard) | Vercel Blob |
|---|---|---|
| Storage | $0.015 / GB-mo (IA tier $0.01) | ~$0.023 / GB-mo (the docs' pricing example; regional) |
| Writes | Class A $4.50 / M | Advanced ops $5.00 / M (put/copy/list) |
| Reads | Class B $0.36 / M | Simple ops $0.40 / M (cache MISS / head only) |
| Egress | **Free** | Blob Data Transfer ~$0.05/GB (iad1 example), plus Fast Origin Transfer on misses |
| Free tier | 10 GB-mo, 1M Class A, 10M Class B, free egress | Hobby: **1 GB**, 10k simple ops, 2k advanced ops, 10 GB transfer. If exceeded, Blob is locked for 30 days. |
| S3 API | Yes. Endpoint `https://<ACCOUNT_ID>.r2.cloudflarestorage.com`, region `auto`. Supports GetObject ranges, PutObject, multipart, ListObjectsV2. | No S3 API documented; access is SDK/REST (`@vercel/blob`) only (UNVERIFIED that none exists) |
| Private objects | Buckets are private unless public access is enabled (REPORTED) | Private stores: reads need a token, served through Functions via `get()`. The access mode is fixed at store creation. |
| DuckDB | Native `CREATE SECRET (TYPE r2, KEY_ID, SECRET, ACCOUNT_ID)` with `r2://` URLs (VERIFIED: created locally on DuckDB 1.5.6). `COPY … TO` writes via multipart. A `.duckdb` file can be `ATTACH`ed **read-only** over S3/HTTPS. | Not directly. You would need signed URLs over HTTPS for read-only access. |
| Max object | (not checked) | 5 TB; objects over 512 MB are never CDN-cached |

Sources:
- R2 pricing (VERIFIED): https://developers.cloudflare.com/r2/pricing/
- R2 S3 compatibility (VERIFIED): https://developers.cloudflare.com/r2/api/s3/api/
- R2 private by default (REPORTED): https://developers.cloudflare.com/r2/buckets/public-buckets/
- Blob pricing and limits (VERIFIED, page updated 2026-09-23): https://vercel.com/docs/vercel-blob/usage-and-pricing
- Blob private/public, OIDC and caching (VERIFIED): https://vercel.com/docs/vercel-blob
- DuckDB S3/R2 (VERIFIED): https://duckdb.org/docs/current/core_extensions/httpfs/s3api.html
- DuckDB read-only attach (VERIFIED): https://duckdb.org/docs/current/guides/network_cloud_storage/duckdb_over_https_or_s3.html

**Recommendation: R2.**
- At 1–5 GB of Parquet plus a DuckDB file, weekly writes and occasional reads, R2 costs **$0/month**: it stays inside 10 GB, with only hundreds of operations a month and free egress.
- Vercel Blob Hobby caps storage at 1 GB, so it fails the size requirement outright.
- GitHub Actions writes with DuckDB `COPY TO 'r2://…'`, or with `aws s3 cp --endpoint-url` / boto3.

**Pattern for page payloads:**
- The ETL also writes small precomputed JSON files (per player, per week) to R2.
- Next.js server components fetch them at build or ISR time with the S3 client (`@aws-sdk/client-s3` or `aws4fetch`, region `auto`), using keys stored as Vercel env vars. (REPORTED: standard S3 SDK usage)
- Avoid running DuckDB inside Vercel functions. Serving JSON is simpler.

**Caveat:** Blob's private mode and OIDC are nicer when everything lives on Vercel. That advantage does not outweigh the S3 and DuckDB gap.

### B8. Vercel: deploy hooks, plan limits, Next.js

**Deploy hooks** (VERIFIED: https://vercel.com/docs/deploy-hooks, updated 2026-09-16)
- Created under Project → Settings → Git. Each hook is tied to one branch.
- Trigger with `curl -X POST https://api.vercel.com/v1/integrations/deploy/<prj_id>/<hook_id>` (GET also works). No auth header is needed: the URL is the secret, so store it as a GitHub Actions secret.
- The response is `{"job":{"id","state":"PENDING","createdAt"}}`.
- The build cache is used by default. Append `?buildCache=false` to disable it.
- Repeated triggers for the same version cancel earlier deployments from that hook.
- Limits: **5 hooks per project** (Hobby and Pro), and **60 triggers per hour per project**.
- Hooks do not fire if `vercel.json` sets `github.enabled = false`.

**Hobby vs Pro** (VERIFIED: https://vercel.com/docs/plans/hobby, https://vercel.com/docs/cron-jobs/usage-and-pricing, https://vercel.com/docs/limits/fair-use-guidelines)

| | Hobby | Pro |
|---|---|---|
| Function max duration | 300 s | 300 s default, configurable to 800 s (1800 s beta) |
| Cron jobs | 100 per project, **at most once per day**, ±59 min precision (expressions that run more often fail at deploy) | 100, per-minute |
| Deployments per day | 100 | 6,000 |
| Hobby included usage | 1M invocations, 4 active-CPU hours, 100 GB Fast Data Transfer | n/a |
| Password protection | n/a | $20 per month per project |

- **Commercial use:** "Hobby teams are restricted to non-commercial personal use only." Commercial use is defined as a deployment "used for the purpose of financial gain of anyone involved in any part of the production". Examples include payments, ads, affiliate-primary sites, or being paid to build the site. Donations are allowed.
- **Pro pricing:** $20 per developer seat per month, with usage-based credit. (VERIFIED, Hobby page)

**Next.js** (VERIFIED: npm `next@latest` = **16.3.8**; https://nextjs.org/docs/app/api-reference/file-conventions/proxy, docs version 16.3.8)
- The App Router is the default and current router.
- **`middleware.ts` → `proxy.ts`**: "The `middleware` file convention is deprecated and has been renamed to `proxy`" (v16.0.0).
- Proxy defaults to the **Node.js runtime**, and the `runtime` option is not allowed in the file.
- Export `function proxy(request)` (or a default export) plus `config.matcher`.
- Codemod: `npx @next/codemod@canary middleware-to-proxy .`
- Basic-auth sketch: check the `authorization` header in `proxy.ts`. Return `new Response('Auth required', {status: 401, headers: {'WWW-Authenticate': 'Basic realm="slab"'}})` when it is missing or wrong. Use a matcher that excludes `_next/static|_next/image|favicon.ico`.
- Note from the docs: Proxy still runs for `_next/data` routes even if a matcher excludes them. Server Functions must check auth themselves rather than relying on Proxy.

### B9. GitHub Actions scheduling

Sources (VERIFIED):
- https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows
- https://docs.github.com/en/actions/how-tos/manage-workflow-runs/disable-and-enable-workflows
- https://docs.github.com/en/actions/how-tos/write-workflows/choose-when-workflows-run/control-workflow-concurrency
- https://docs.github.com/en/billing/concepts/product-billing/github-actions

**Delays**
- The docs say: "The `schedule` event can be delayed during periods of high loads… High load times include the start of every hour."
- The minimum interval is 5 minutes. Schedules run only on the default branch.
- The nflverse evidence in A3 shows delays of **4–6 hours** at 05:45 and 07:00 UTC. (VERIFIED)
- **Mitigations:** use an off-hour minute (e.g. `17 16 * * 2`), make the ETL idempotent, and add a `workflow_dispatch` input for manual reruns.

**60-day auto-disable**
- The docs say: "In a public repository, scheduled workflows are automatically disabled when no repository activity has occurred in 60 days."
- The docs mention the rule **only for public repositories**. They are silent on private repos. (VERIFIED as to wording; whether it applies to private repos is UNVERIFIED)
- The weekly ETL commit or any push resets activity in either case.

**Concurrency**
- A `concurrency: group` allows one running and one pending run.
- By default a newly queued run **cancels the existing pending one**. `cancel-in-progress: true` cancels the running one instead.
- There is a `queue: max` option that keeps up to 100 pending runs FIFO. It cannot be combined with `cancel-in-progress`.
- **Use `group: etl, cancel-in-progress: false`** so a scheduled run never kills a run that is mid-write to R2.

**Minutes**
- GitHub Free, private repos: **2,000 minutes per month and 500 MB artifact storage**. Linux 2-core is $0.006/min beyond that.
- Public repos on standard runners are free.
- A weekly ~5-minute ETL uses under 30 minutes a month.

### B10. Fine-grained PAT committing from a Vercel function

Sources (VERIFIED):
- https://docs.github.com/en/rest/authentication/permissions-required-for-fine-grained-personal-access-tokens
- https://docs.github.com/en/rest/repos/contents#create-or-update-file-contents

**Permissions**
- `PUT /repos/{owner}/{repo}/contents/{path}` requires **Contents: write**. The docs flag that an additional permission may apply: per the endpoint docs, the `workflow` scope is needed only for files under `.github/workflows`.
- The Git Data endpoints (`POST git/blobs`, `git/trees`, `git/commits`) also need Contents: write. `git/refs` has an extra-permission flag.

**Endpoint constraints**
- Content must be base64.
- Updating a file requires its current blob `sha`.
- Files over 100 MB are unsupported.
- Concurrent contents PUT and DELETE calls conflict, so issue them serially.

**Conclusion:** a fine-grained PAT limited to the single repo, with Contents read/write, can create commits through the contents API from a Vercel route handler. It is plain HTTPS with `Authorization: Bearer <token>`, and nothing about it is Vercel-specific.
- (REPORTED/inferred; I did not run a live commit, since that needs a token.)

**Cautions**
- Fine-grained PATs expire. Set a calendar reminder.
- Each commit triggers a Vercel Git deploy if the repo is linked. That counts toward the 100-per-day Hobby deployment cap. Use `[skip ci]`, or `ignoreCommand`, for data-only paths if needed. (UNVERIFIED: not tested here)

---

## Open items

- Test a live R2 write and read from GitHub Actions with DuckDB `r2://` (needs an account; not done, per instructions).
- Decide whether to snapshot nflverse weekly. Since nflverse overwrites the current season with stat corrections, Slab Radar should store its own `as_of` copies if historical "what we knew Tuesday" views matter.
- ~~Prototype estimating routes from the 2025 participation `route` column against `offense_pct`.~~ Dropped (hard rule).
