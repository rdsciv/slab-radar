"""nflverse → fact_player_week: one row per (season, week, gsis_id), additive numerators + team denominators.

Recorded data only (CLAUDE.md). Definitions:
- target share   = targets / team targets                      (nflverse player_stats.target_share)
- air-yards share = receiving air yards / team PASSER air yards (nflverse air_yards_share denominator)
- snap share     = offense snaps / team offense snaps           (PFR via nflverse)
- carry share    = carries / team carries
- RZ opp share   = (rz targets + rz carries) / team (rz targets + rz carries), yardline_100 <= 20
- dropbacks      = qb_dropback plays by passer_id (incl. sacks, scrambles)
- designed rushes = QB play_type 'run' with qb_scramble == 0 (kneels are play_type 'qb_kneel', excluded)
- xFP            = ffopportunity total_fantasy_points_exp — an nflverse MODEL output, labeled as such
pbp play filter (reference repo "Filter Offensive Plays"): play_type in {pass, run}, epa and posteam
non-null; two-point tries excluded explicitly (they carry epa).
"""
import nflreadpy as nfl
import polars as pl

POSITIONS = ("QB", "RB", "WR", "TE")
KEY = ["season", "week", "gsis_id"]


def offensive_plays(pbp: pl.DataFrame) -> pl.DataFrame:
    return pbp.filter(
        pl.col("play_type").is_in(["pass", "run"])
        & pl.col("epa").is_not_null()
        & pl.col("posteam").is_not_null()
        & (pl.col("two_point_attempt").fill_null(0) == 0)
        & (pl.col("season_type") == "REG")
    )


def pbp_player_week(pbp: pl.DataFrame) -> tuple[pl.DataFrame, pl.DataFrame]:
    """Per-player red-zone opportunities, dropbacks, designed rushes; per-team RZ totals."""
    p = offensive_plays(pbp)
    rz = p.filter(pl.col("yardline_100") <= 20)
    rz_tgt = (rz.filter((pl.col("play_type") == "pass") & pl.col("receiver_id").is_not_null())
              .group_by("season", "week", pl.col("receiver_id").alias("gsis_id")).agg(pl.len().alias("rz_targets")))
    rz_car = (rz.filter((pl.col("play_type") == "run") & pl.col("rusher_id").is_not_null())
              .group_by("season", "week", pl.col("rusher_id").alias("gsis_id")).agg(pl.len().alias("rz_carries")))
    team_rz = (rz.filter(((pl.col("play_type") == "pass") & pl.col("receiver_id").is_not_null())
                         | ((pl.col("play_type") == "run") & pl.col("rusher_id").is_not_null()))
               .group_by("season", "week", pl.col("posteam").alias("team")).agg(pl.len().alias("team_rz_opps")))
    # Dropbacks are counted on all REG non-2pt plays (not the EPA filter), so spikes and no-EPA plays still count.
    allp = pbp.filter((pl.col("season_type") == "REG") & (pl.col("two_point_attempt").fill_null(0) == 0))
    drop = (allp.filter((pl.col("qb_dropback") == 1) & pl.col("passer_id").is_not_null())
            .group_by("season", "week", pl.col("passer_id").alias("gsis_id")).agg(pl.len().alias("dropbacks")))
    designed = (p.filter((pl.col("play_type") == "run") & (pl.col("qb_scramble").fill_null(0) == 0)
                         & pl.col("rusher_id").is_not_null())
                .group_by("season", "week", pl.col("rusher_id").alias("gsis_id")).agg(pl.len().alias("rushes_non_scramble")))
    players = rz_tgt.join(rz_car, on=KEY, how="full", coalesce=True)
    for d in (drop, designed):
        players = players.join(d, on=KEY, how="full", coalesce=True)
    return players.fill_null(0), team_rz


def build_player_week(season: int, pbp: pl.DataFrame | None = None) -> tuple[pl.DataFrame, list[dict]]:
    """Returns (fact_player_week, data-quality warnings)."""
    warnings: list[dict] = []
    ps = nfl.load_player_stats([season]).filter(pl.col("season_type") == "REG")
    team = ps.group_by("season", "week", "team").agg(
        pl.col("targets").sum().alias("team_targets"),
        pl.col("passing_air_yards").sum().alias("team_pass_air_yards"),
        pl.col("carries").sum().alias("team_carries"),
    )
    base = (ps.filter(pl.col("position").is_in(POSITIONS))
            .select(pl.col("player_id").alias("gsis_id"), "player_display_name", "position", "season", "week",
                    "game_id", "team", "opponent_team", "targets", pl.col("receiving_air_yards").alias("rec_air_yards"),
                    "carries", "receptions", "receiving_yards", "rushing_yards", "receiving_tds", "rushing_tds",
                    "passing_yards", "passing_tds", "attempts", "fantasy_points_ppr",
                    pl.col("target_share").alias("nflverse_target_share"),
                    pl.col("air_yards_share").alias("nflverse_air_yards_share"),
                    pl.col("wopr").alias("nflverse_wopr"))
            .join(team, on=["season", "week", "team"], how="left"))

    # Snaps: PFR ids bridged to gsis via load_players().pfr_id; unmatched rows are warned, not dropped silently.
    sc = nfl.load_snap_counts([season]).filter(pl.col("game_type") == "REG")
    # Team snaps recovered from PFR's own ratio (offense_pct = snaps / team snaps); max(snaps) fails when no one plays every snap.
    team_snaps = (sc.filter(pl.col("offense_pct") > 0)
                  .group_by("season", "week", "team")
                  .agg((pl.col("offense_snaps") / pl.col("offense_pct")).median().round(0).alias("team_offense_snaps")))
    ids = nfl.load_players().select("gsis_id", pl.col("pfr_id").alias("pfr_player_id")).drop_nulls()
    sc = sc.join(ids, on="pfr_player_id", how="left")
    unmatched = sc.filter(pl.col("gsis_id").is_null() & (pl.col("offense_snaps") > 0)
                          & pl.col("position").is_in(POSITIONS))
    for r in unmatched.select("week", "player", "team", "offense_snaps").iter_rows(named=True):
        warnings.append({"kind": "snap_id_unmatched", **r})
    snaps = (sc.filter(pl.col("gsis_id").is_not_null())
             .group_by("season", "week", "gsis_id").agg(pl.col("offense_snaps").sum()))
    base = (base.join(snaps, on=KEY, how="left")
            .join(team_snaps, on=["season", "week", "team"], how="left"))

    ff = (nfl.load_ff_opportunity(seasons=[season])
          .filter(pl.col("player_id").is_not_null())
          .select(pl.col("season").cast(pl.Int32), pl.col("week").cast(pl.Int32),
                  pl.col("player_id").alias("gsis_id"), pl.col("total_fantasy_points_exp").alias("xfp")))
    base = base.join(ff, on=KEY, how="left")

    if pbp is None:
        pbp = nfl.load_pbp([season])
    pp, team_rz = pbp_player_week(pbp)
    pp = pp.with_columns(pl.col("season").cast(pl.Int32), pl.col("week").cast(pl.Int32))
    team_rz = team_rz.with_columns(pl.col("season").cast(pl.Int32), pl.col("week").cast(pl.Int32))
    base = (base.join(pp, on=KEY, how="left").join(team_rz, on=["season", "week", "team"], how="left")
            .with_columns(pl.col("rz_targets", "rz_carries", "dropbacks", "rushes_non_scramble", "team_rz_opps").fill_null(0))
            # Unmatched snap rows stay NULL (snap share unknown), never 0: the player still counts as active below.
            .with_columns(active=(pl.col("offense_snaps").fill_null(0) > 0) | (pl.col("targets") > 0)
                          | (pl.col("carries") > 0) | (pl.col("attempts") > 0))
            # ffopportunity has no row for an active game with no opportunity: that game's xFP is 0, not missing.
            .with_columns(xfp=pl.when(pl.col("xfp").is_null() & (pl.col("targets") == 0) & (pl.col("carries") == 0)
                                      & (pl.col("attempts") == 0)).then(0.0).otherwise(pl.col("xfp")))
            .with_columns(designed_rushes=pl.when(pl.col("position") == "QB")
                          .then(pl.col("rushes_non_scramble")).otherwise(0))
            .drop("rushes_non_scramble"))
    return base.sort("season", "week", "team", "gsis_id"), warnings


def complete_weeks(season: int, fpw: pl.DataFrame) -> list[int]:
    """Freshness gate: a week counts only when every scheduled REG game has a score AND player_stats rows."""
    sch = nfl.load_schedules([season]).filter(pl.col("game_type") == "REG")
    have = set(fpw.select("game_id").unique().to_series().to_list())
    out = []
    for wk, games in sch.group_by("week"):
        ids = games["game_id"].to_list()
        if games["result"].null_count() == 0 and all(g in have for g in ids):
            out.append(int(wk[0]))
    return sorted(out)


def season_shares(season: int) -> pl.DataFrame:
    """Per-player season target/carry share (prior-season Beta priors). Players traded mid-season count per team stint."""
    ps = nfl.load_player_stats([season]).filter(pl.col("season_type") == "REG")
    team = ps.group_by("week", "team").agg(pl.col("targets").sum().alias("tt"), pl.col("carries").sum().alias("tc"))
    return (ps.filter(pl.col("position").is_in(POSITIONS)).join(team, on=["week", "team"])
            .group_by("player_id", "position", "team")
            .agg(pl.len().alias("games"), pl.col("targets").sum(), pl.col("tt").sum(),
                 pl.col("carries").sum(), pl.col("tc").sum()))
