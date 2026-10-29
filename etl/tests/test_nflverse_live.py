"""Live nflverse checks (network). Formula equality vs nflverse columns + the PROMPT acceptance week."""
import polars as pl
import pytest

from slab_radar import radar
from slab_radar.cli import load_cfg, priors_for
from slab_radar.nfl import build_player_week, complete_weeks

WILSON = "00-0038559"


@pytest.fixture(scope="module")
def fpw():
    f, _ = build_player_week(2026)
    return f


def test_target_share_and_ays_match_nflverse(fpw):
    x = fpw.filter(pl.col("targets") > 0)
    assert (x["targets"] / x["team_targets"] - x["nflverse_target_share"]).abs().max() < 1e-9
    y = x.filter(pl.col("team_pass_air_yards") != 0)
    assert (y["rec_air_yards"] / y["team_pass_air_yards"] - y["nflverse_air_yards_share"]).abs().max() < 1e-9
    w = y.filter(pl.col("nflverse_wopr").is_not_null())
    wopr = 1.5 * w["targets"] / w["team_targets"] + 0.7 * w["rec_air_yards"] / w["team_pass_air_yards"]
    assert (wopr - w["nflverse_wopr"]).abs().max() < 1e-9


def test_wilson_spike_week_is_week3_and_on_radar(fpw):
    assert 3 in complete_weeks(2026, fpw)
    cfg, _ = load_cfg()
    rows = [r for r in radar.compute(fpw.filter(pl.col("week") <= 3), 3, cfg, priors_for(2026)) if r["passes_min_snaps"]]
    me = next(r for r in rows if r["gsis_id"] == WILSON)
    m = me["metrics"]["ts"]
    assert (m["last1_num"], m["last1_den"]) == (17, 50)
    assert m["last1"] - m["base1"] == pytest.approx(17 / 50 - 14 / 63)
    assert rows.index(me) < 10   # top 10 of qualifying players that week
