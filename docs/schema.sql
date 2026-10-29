-- Slab Radar — canonical store DDL (DuckDB 1.x dialect).
-- Proposed at M0; final once approved. Parquet files mirror each table 1:1
-- under r2://slab-radar/warehouse/<table>/season=<s>/... (fact tables) or
-- r2://slab-radar/warehouse/<table>.parquet (dims). The DuckDB file is a
-- convenience build of the same data; Parquet is the source of truth.
--
-- Conventions
--   * Additive facts only in fact_player_week: every window rate is
--     recomputed as sum(numerator)/sum(denominator), never averaged.
--   * Every derived number published to the site carries a provenance label
--     (OBSERVED | MODEL | MARKET_IMPLIED) plus n and an interval; see the
--     mart_* tables at the bottom.
--   * Money is stored as DECIMAL(12,2) USD; rounding for display is a UI
--     concern (whole dollars; $5 steps above $500).
--   * *_ts columns are UTC TIMESTAMPTZ; *_date columns are calendar dates.

CREATE TYPE provenance AS ENUM ('OBSERVED', 'MODEL', 'MARKET_IMPLIED');
CREATE TYPE grader     AS ENUM ('RAW', 'PSA', 'BGS', 'SGC', 'CGC', 'TAG', 'OTHER');
CREATE TYPE sale_type  AS ENUM ('AUCTION', 'BIN', 'BEST_OFFER', 'UNKNOWN');
CREATE TYPE match_status AS ENUM ('MATCHED', 'AMBIGUOUS', 'LOW_CONFIDENCE', 'EXCLUDED', 'UNMATCHED');

-- ───────────────────────────── NFL side ─────────────────────────────

CREATE TABLE dim_player (
    gsis_id            VARCHAR PRIMARY KEY,          -- nflverse canonical id (00-00xxxxx)
    display_name       VARCHAR NOT NULL,
    position           VARCHAR NOT NULL,             -- QB/RB/WR/TE (others ignored)
    team               VARCHAR,                      -- latest team abbr
    rookie_season      SMALLINT,
    draft_round        SMALLINT,                     -- NULL = undrafted
    draft_pick         SMALLINT,                     -- overall pick
    birth_date         DATE,                         -- age computed at query time
    pfr_id             VARCHAR,                      -- join key for snap counts
    card_aliases       VARCHAR[] NOT NULL DEFAULT [],-- e.g. ['Mike Wilson','Michael Wilson']
    updated_ts         TIMESTAMPTZ NOT NULL
);

CREATE TABLE fact_player_week (
    season             SMALLINT NOT NULL,
    week               SMALLINT NOT NULL,
    season_type        VARCHAR  NOT NULL,            -- REG / POST
    gsis_id            VARCHAR  NOT NULL REFERENCES dim_player (gsis_id),
    team               VARCHAR  NOT NULL,
    opponent           VARCHAR,
    game_id            VARCHAR  NOT NULL,
    -- snaps (PFR via nflverse snap_counts)
    offense_snaps      SMALLINT,
    team_offense_snaps SMALLINT,
    -- receiving (pbp-derived, nflverse player_stats definitions)
    targets            SMALLINT NOT NULL DEFAULT 0,
    team_targets       SMALLINT NOT NULL DEFAULT 0,
    receptions         SMALLINT NOT NULL DEFAULT 0,
    receiving_yards    SMALLINT NOT NULL DEFAULT 0,
    receiving_tds      SMALLINT NOT NULL DEFAULT 0,
    receiving_air_yards INTEGER NOT NULL DEFAULT 0,  -- may be negative per play
    team_air_yards     INTEGER NOT NULL DEFAULT 0,  -- team PASSER air yards (nflverse air_yards_share denominator)
    -- rushing
    carries            SMALLINT NOT NULL DEFAULT 0,
    team_carries       SMALLINT NOT NULL DEFAULT 0,
    rushing_yards      SMALLINT NOT NULL DEFAULT 0,
    rushing_tds        SMALLINT NOT NULL DEFAULT 0,
    -- QB volume (pbp)
    dropbacks          SMALLINT NOT NULL DEFAULT 0,
    designed_rushes    SMALLINT NOT NULL DEFAULT 0,  -- QB rushes excluding scrambles
    passing_yards      SMALLINT NOT NULL DEFAULT 0,
    passing_tds        SMALLINT NOT NULL DEFAULT 0,
    -- red zone (pbp; yardline_100 <= 20 / <= 10, same cut as reference repo)
    rz20_targets       SMALLINT NOT NULL DEFAULT 0,
    team_rz20_targets  SMALLINT NOT NULL DEFAULT 0,
    rz10_targets       SMALLINT NOT NULL DEFAULT 0,
    team_rz10_targets  SMALLINT NOT NULL DEFAULT 0,
    rz20_carries       SMALLINT NOT NULL DEFAULT 0,
    team_rz20_carries  SMALLINT NOT NULL DEFAULT 0,
    rz10_carries       SMALLINT NOT NULL DEFAULT 0,
    team_rz10_carries  SMALLINT NOT NULL DEFAULT 0,
    -- fantasy (recorded) and expected (ffopportunity model, labeled MODEL)
    fantasy_points_ppr DECIMAL(6,2),
    xfp_total          DECIMAL(6,2),                 -- ffopportunity total_fantasy_points_exp
    xfp_rec            DECIMAL(6,2),
    xfp_rush           DECIMAL(6,2),
    xfp_pass           DECIMAL(6,2),
    -- Next Gen Stats (weekly, published only above NGS volume minimums → nullable)
    ngs_avg_separation DECIMAL(5,2),
    ngs_avg_cushion    DECIMAL(5,2),
    ngs_avg_yac_above_expectation DECIMAL(5,2),
    ngs_rush_yards_over_expected  DECIMAL(7,2),
    ngs_rush_attempts  SMALLINT,                     -- denominator for RYOE/att
    -- lineage
    source_versions    JSON NOT NULL,                -- {"pbp":"2026-09-30T..","snap_counts":...}
    loaded_ts          TIMESTAMPTZ NOT NULL,
    PRIMARY KEY (season, week, season_type, gsis_id)
);

CREATE TABLE fact_team_context_week (
    season             SMALLINT NOT NULL,
    week               SMALLINT NOT NULL,
    season_type        VARCHAR  NOT NULL,
    team               VARCHAR  NOT NULL,
    starting_qb_gsis_id VARCHAR,
    qb_changed         BOOLEAN  NOT NULL,            -- vs previous game
    dropbacks          SMALLINT,
    plays              SMALLINT,
    pass_rate          DECIMAL(5,4),                 -- dropbacks / (dropbacks + designed runs)
    neutral_pass_rate  DECIMAL(5,4),                 -- wp 20–80%, excl. last 2 min of halves
    injuries           JSON,                         -- [{gsis_id, report_status, practice_status}]
    depth_chart        JSON,                         -- [{gsis_id, pos, depth}] as published
    depth_changes      JSON,                         -- [{gsis_id, from, to}] vs prior week
    transactions       JSON,                         -- trades / IR moves when available
    loaded_ts          TIMESTAMPTZ NOT NULL,
    PRIMARY KEY (season, week, season_type, team)
);

CREATE TABLE fact_breakout_week (
    season SMALLINT NOT NULL, week SMALLINT NOT NULL, gsis_id VARCHAR NOT NULL,
    position VARCHAR NOT NULL,
    passes_min_snaps   BOOLEAN NOT NULL,
    metrics            JSON NOT NULL,   -- {metric: {last1, last3, baseline, z_self, z_pos, n}}
    p_share_up         DECIMAL(5,4),    -- MODEL: P(true target/carry share rose) (beta-binomial)
    share_posterior    JSON,            -- MODEL: {metric: {recent_mean, recent_lo80, recent_hi80, base_mean, base_lo80, base_hi80, n_recent, n_base}}
    td_driven_flag     BOOLEAN NOT NULL,
    context_flags      VARCHAR[] NOT NULL DEFAULT [],
    breakout_score     DECIMAL(6,3) NOT NULL,
    weights_version    VARCHAR NOT NULL,
    PRIMARY KEY (season, week, gsis_id)
);

-- ───────────────────────────── Card side ─────────────────────────────

CREATE TABLE dim_card (
    card_key           VARCHAR PRIMARY KEY,          -- = gemrate_id, else cardladder_gemrate_id, else 'sr_' || sha1(natural key)  [PENDING approval, plan F1]
    gemrate_id         VARCHAR,                      -- 40-hex universal id from GemRate universal-search link (literal 'None' on 1,114/1,877 fixture rows → NULL)
    cardladder_gemrate_id VARCHAR,                   -- 40-hex PSA-scoped GemRate id in Card Ladder links (≠ gemrate_id on 13 of the 322 rows that have both)
    natural_key        VARCHAR NOT NULL UNIQUE,      -- normalized year|set|name|parallel|card_no
    category           VARCHAR NOT NULL,             -- Football / Multi Sport
    year               SMALLINT NOT NULL,
    manufacturer       VARCHAR NOT NULL,             -- Panini / Topps / Bowman / Leaf / Sage / Onit / Wild Card …
    product            VARCHAR NOT NULL,             -- 'Prizm', 'Donruss Optic', 'Topps Chrome'
    subset             VARCHAR,                      -- insert/subset name when GemRate 'Set' extends the product
    card_no            VARCHAR,                      -- required for matching; NULL only when source has none (flagged)
    parallel           VARCHAR NOT NULL,             -- 'Base' when none
    print_run          INTEGER,                      -- /99 → 99; 1 for 1/1
    variation          VARCHAR,
    is_auto            BOOLEAN NOT NULL DEFAULT FALSE,
    is_relic           BOOLEAN NOT NULL DEFAULT FALSE,
    is_rc              BOOLEAN,                      -- from source only; NULL = unknown (never inferred from year)
    pre_nfl            BOOLEAN NOT NULL,             -- college / NIL product
    multi_player       BOOLEAN NOT NULL,
    license_status     VARCHAR,                      -- from config/products.yaml
    coverage_tier      VARCHAR NOT NULL DEFAULT 'C', -- A / B / C
    pinned             BOOLEAN NOT NULL DEFAULT FALSE,
    source             VARCHAR NOT NULL,             -- 'gemrate_csv', 'comp_adapter', …
    flags              VARCHAR[] NOT NULL DEFAULT [],-- e.g. 'no_gemrate_id', 'psa_scoped_id_only', 'gemrate_id_mismatch', 'no_card_no'
    first_seen_ts      TIMESTAMPTZ NOT NULL,
    updated_ts         TIMESTAMPTZ NOT NULL
);

CREATE TABLE bridge_card_player (
    card_key  VARCHAR NOT NULL REFERENCES dim_card (card_key),
    gsis_id   VARCHAR,                               -- NULL for non-NFL co-subjects (e.g. a college teammate)
    name_on_card VARCHAR NOT NULL,
    multi_player BOOLEAN NOT NULL,
    PRIMARY KEY (card_key, name_on_card)
);

CREATE TABLE fact_sale (
    source             VARCHAR NOT NULL,             -- adapter name
    sale_id            VARCHAR NOT NULL,             -- source-native id
    sale_date          DATE NOT NULL,
    price              DECIMAL(12,2),                -- realized/accepted price; NULL when unknown (never the list price)
    price_is_accepted  BOOLEAN NOT NULL,             -- FALSE: best offer with only list price known → price NULL, counted as n_bo_unknown
    list_price         DECIMAL(12,2),
    sale_type          sale_type NOT NULL,
    marketplace        VARCHAR,                      -- eBay / Goldin / Fanatics Collect / Heritage …
    title              VARCHAR NOT NULL,
    grader             grader NOT NULL,
    grade              DECIMAL(4,1),                 -- NULL for RAW in facts; marts use 0 sentinel
    grade_label        VARCHAR NOT NULL DEFAULT '',  -- '' | 'Pristine' | 'Black Label' | 'Perfect' (never a qualifier)
    qualifier          VARCHAR NOT NULL DEFAULT '',  -- '' | PSA OC/ST/PD/MC/MK/OF
    subgrades          JSON,                         -- {"centering":10,"corners":9.5,...}
    tag_score          SMALLINT,                     -- 0–1000
    cert_no            VARCHAR,
    serial_no          SMALLINT,                     -- 23 in 23/99
    serial_of          SMALLINT,                     -- 99 in 23/99
    image_url          VARCHAR,
    listing_url        VARCHAR,
    card_key           VARCHAR REFERENCES dim_card (card_key),  -- NULL unless MATCHED
    match_status       match_status NOT NULL,
    match_confidence   DECIMAL(4,3) NOT NULL,
    parser_version     VARCHAR NOT NULL,
    outlier_flag       VARCHAR,                      -- NULL | 'mad' | 'shill_suspect' | 'relist_npb'
    ingested_ts        TIMESTAMPTZ NOT NULL,
    PRIMARY KEY (source, sale_id),
    CHECK (price_is_accepted = (price IS NOT NULL)),
    CHECK (price_is_accepted OR sale_type IN ('BEST_OFFER', 'UNKNOWN'))
);

CREATE TABLE fact_listing (
    source             VARCHAR NOT NULL,
    listing_id         VARCHAR NOT NULL,
    snapshot_date      DATE NOT NULL,
    card_key           VARCHAR REFERENCES dim_card (card_key),
    grader             grader NOT NULL,
    grade              DECIMAL(4,1),
    grade_label        VARCHAR NOT NULL DEFAULT '',
    qualifier          VARCHAR NOT NULL DEFAULT '',
    ask_price          DECIMAL(12,2) NOT NULL,
    format             VARCHAR,                      -- BIN / AUCTION / BIN+BO
    title              VARCHAR NOT NULL,
    listing_url        VARCHAR,
    match_status       match_status NOT NULL,
    match_confidence   DECIMAL(4,3) NOT NULL,
    PRIMARY KEY (source, listing_id, snapshot_date)
);

CREATE TABLE fact_pop_snapshot (
    card_key           VARCHAR NOT NULL REFERENCES dim_card (card_key),
    grader             grader NOT NULL,
    grade              DECIMAL(4,1) NOT NULL,
    grade_label        VARCHAR NOT NULL DEFAULT '',  -- '' | 'Pristine' | 'Black Label' | 'Perfect' (never a qualifier)
    qualifier          VARCHAR NOT NULL DEFAULT '',  -- '' | PSA OC/ST/PD/MC/MK/OF (qualified pop, e.g. 9Q)
    pop_count          INTEGER NOT NULL,
    snapshot_date      DATE NOT NULL,
    source             VARCHAR NOT NULL,             -- 'gemrate_csv' / 'gemrate_api' / 'psa_pop' …
    source_lag_days    SMALLINT,                     -- documented source lag (GemRate ≈1–2d)
    PRIMARY KEY (card_key, grader, grade, grade_label, qualifier, snapshot_date, source)
);

CREATE TABLE fact_grade_detail (
    grader             grader NOT NULL,
    cert_no            VARCHAR NOT NULL,
    card_key           VARCHAR REFERENCES dim_card (card_key),
    grade              DECIMAL(4,1),
    grade_label        VARCHAR NOT NULL DEFAULT '',
    qualifier          VARCHAR NOT NULL DEFAULT '',
    sub_centering      DECIMAL(3,1),
    sub_corners        DECIMAL(3,1),
    sub_edges          DECIMAL(3,1),
    sub_surface        DECIMAL(3,1),
    tag_score          SMALLINT,
    tag_subgrades      JSON,                         -- 8: {front|back}×{centering,corners,edges,surface}
    centering_front_lr DECIMAL(4,1),                 -- % on the larger side, e.g. 55.0 means 55/45
    centering_front_tb DECIMAL(4,1),
    centering_back_lr  DECIMAL(4,1),
    centering_back_tb  DECIMAL(4,1),
    defects            JSON,                         -- [{side, category, note}]
    source             VARCHAR NOT NULL,             -- 'psa_api' / 'gemrate_api' / 'manual_tag_dig' / 'manual' / 'title' (TAG: manual per-cert entry only; ToS bars automation)
    fetched_ts         TIMESTAMPTZ NOT NULL,
    PRIMARY KEY (grader, cert_no)
);

CREATE TABLE fact_crossover_obs (
    obs_id             VARCHAR PRIMARY KEY,
    card_key           VARCHAR NOT NULL REFERENCES dim_card (card_key),
    before_grader      grader NOT NULL,
    before_grade       DECIMAL(4,1) NOT NULL,
    before_label       VARCHAR,
    before_subgrades   JSON,
    before_tag_score   SMALLINT,
    after_grader       grader NOT NULL,              -- normally PSA
    after_grade        DECIMAL(4,1),                 -- NULL = crossover declined (min not met)
    min_grade_requested DECIMAL(4,1),
    evidence_type      VARCHAR NOT NULL,             -- serial_match / image_hash / my_log / import
    evidence           JSON NOT NULL,                -- serial, cert numbers, sale ids, hash distance
    confirmed          BOOLEAN NOT NULL DEFAULT FALSE,
    observed_date      DATE,
    created_ts         TIMESTAMPTZ NOT NULL
);

CREATE TABLE review_queue (
    item_id            VARCHAR PRIMARY KEY,
    kind               VARCHAR NOT NULL,             -- sale_match / crossover_candidate / hypothesis
    payload            JSON NOT NULL,
    reason             VARCHAR NOT NULL,             -- 'ambiguous_card_no', 'low_confidence', …
    decision           VARCHAR,                      -- NULL | approved | rejected
    decided_ts         TIMESTAMPTZ,
    created_ts         TIMESTAMPTZ NOT NULL
);

-- ───────────────────────────── Ops ─────────────────────────────

CREATE TABLE run_manifest (
    run_id      VARCHAR NOT NULL,
    season      SMALLINT NOT NULL,
    week        SMALLINT NOT NULL,
    stage       VARCHAR NOT NULL,
    status      VARCHAR NOT NULL,                    -- ok / failed / skipped / blocked_by_gate
    row_counts  JSON NOT NULL,
    inputs_hash VARCHAR NOT NULL,                    -- idempotency: same inputs → skip
    started_ts  TIMESTAMPTZ NOT NULL,
    finished_ts TIMESTAMPTZ,
    message     VARCHAR,
    PRIMARY KEY (season, week, stage, run_id)
);

CREATE TABLE llm_cache (
    payload_hash VARCHAR PRIMARY KEY,                -- sha256 of canonical JSON payload + prompt version + model id
    model_id     VARCHAR NOT NULL,
    text         VARCHAR NOT NULL,
    validated    BOOLEAN NOT NULL,                   -- every number in text ⊂ payload numbers
    fallback     BOOLEAN NOT NULL,                   -- TRUE = template text used
    created_ts   TIMESTAMPTZ NOT NULL
);

-- ───────────────────────────── Marts (published) ─────────────────────────────
-- One row per published number family. Every value carries provenance, n and an interval.

CREATE TABLE mart_card_grade_market (
    card_key VARCHAR NOT NULL, grader grader NOT NULL,
    grade DECIMAL(4,1) NOT NULL,                                   -- 0 = sentinel for RAW (PK columns cannot be NULL)
    grade_label VARCHAR NOT NULL DEFAULT '',
    as_of_date DATE NOT NULL,
    last_sale DECIMAL(12,2), last_sale_date DATE,
    median_7d DECIMAL(12,2), n_7d INTEGER NOT NULL, median_7d_lo DECIMAL(12,2), median_7d_hi DECIMAL(12,2),
    median_30d DECIMAL(12,2), n_30d INTEGER NOT NULL, median_30d_lo DECIMAL(12,2), median_30d_hi DECIMAL(12,2),
    median_90d DECIMAL(12,2), n_90d INTEGER NOT NULL, median_90d_lo DECIMAL(12,2), median_90d_hi DECIMAL(12,2),
    trend_slope_30d DECIMAL(8,5), trend_slope_30d_lo DECIMAL(8,5), trend_slope_30d_hi DECIMAL(8,5),  -- Theil–Sen Δlog(price)/day, bootstrap 80%
    trend_slope_90d DECIMAL(8,5), trend_slope_90d_lo DECIMAL(8,5), trend_slope_90d_hi DECIMAL(8,5),
    volatility_90d DECIMAL(8,5), volatility_90d_lo DECIMAL(8,5), volatility_90d_hi DECIMAL(8,5),    -- 1.4826·MAD of log residuals, bootstrap 80%
    active_listings INTEGER, lowest_ask DECIMAL(12,2),
    ask_last_spread DECIMAL(8,4),                                  -- OBSERVED point (census of current asks, n = active_listings); no sampling interval
    n_excluded_outliers INTEGER NOT NULL,
    n_bo_unknown INTEGER NOT NULL DEFAULT 0,                       -- best-offer sales with unknown accepted price (counted, not priced)
    provenance provenance NOT NULL DEFAULT 'OBSERVED',
    PRIMARY KEY (card_key, grader, grade, grade_label, as_of_date)
);

CREATE TABLE mart_card_multiple (
    card_key VARCHAR NOT NULL, as_of_date DATE NOT NULL,
    numerator VARCHAR NOT NULL, denominator VARCHAR NOT NULL,      -- e.g. 'PSA 10' / 'PSA 9', 'PSA 10' / 'RAW'
    ratio DECIMAL(8,3), ratio_lo DECIMAL(8,3), ratio_hi DECIMAL(8,3), -- 30-day medians; bootstrap 80%
    n_num INTEGER NOT NULL, n_den INTEGER NOT NULL,
    provenance provenance NOT NULL DEFAULT 'OBSERVED',
    PRIMARY KEY (card_key, as_of_date, numerator, denominator)
);

CREATE TABLE mart_gem_rate (
    card_key VARCHAR NOT NULL, as_of_date DATE NOT NULL, scope VARCHAR NOT NULL,  -- 'PSA10' | 'ALL_GRADER_GEM'
    gems INTEGER NOT NULL, total INTEGER NOT NULL,
    raw_rate DECIMAL(5,4),
    prior_level VARCHAR NOT NULL,          -- product_parallel_year | product_year | global
    prior_alpha DOUBLE NOT NULL, prior_beta DOUBLE NOT NULL,
    post_mean DECIMAL(5,4) NOT NULL, ci_lo DECIMAL(5,4) NOT NULL, ci_hi DECIMAL(5,4) NOT NULL,
    provenance provenance NOT NULL DEFAULT 'MODEL',
    PRIMARY KEY (card_key, as_of_date, scope)
);

CREATE TABLE mart_crossgrade (
    card_key VARCHAR NOT NULL, as_of_date DATE NOT NULL,
    source_grader grader NOT NULL, source_grade_band VARCHAR NOT NULL,  -- 'SGC 9.5', 'BGS 9.5 [C10/9.5x3]', 'TAG 950–979'
    method VARCHAR NOT NULL,               -- observed | subgrade_model | equipercentile | combined | market_implied
    p_psa10 DECIMAL(5,4), p_psa9 DECIMAL(5,4), p_le8 DECIMAL(5,4),
    ci_lo DECIMAL(5,4), ci_hi DECIMAL(5,4), n INTEGER NOT NULL,
    confidence VARCHAR NOT NULL,           -- high / medium / low
    crossover_ev DECIMAL(12,2), breakeven_p DECIMAL(5,4),
    provenance provenance NOT NULL,
    PRIMARY KEY (card_key, as_of_date, source_grader, source_grade_band, method)
);

CREATE TABLE mart_strategy (
    season SMALLINT NOT NULL, week SMALLINT NOT NULL, gsis_id VARCHAR NOT NULL,
    primary_playbook VARCHAR NOT NULL, secondary_playbook VARCHAR,
    payload JSON NOT NULL,                 -- cards, max entry, exit target/window, triggers, EV, size, liquidity, confidence
    payload_hash VARCHAR NOT NULL,
    rationale VARCHAR,                     -- Claude text (validated) or template
    rules_version VARCHAR NOT NULL,
    PRIMARY KEY (season, week, gsis_id)
);
