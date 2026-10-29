import numpy as np
import polars as pl
import pytest
import yaml
from pathlib import Path

from slab_radar import radar

ROOT = Path(__file__).resolve().parents[2]


def test_window_rate_is_ratio_of_sums_not_mean_of_ratios():
    rows = pl.DataFrame({"targets": [1, 9], "team_targets": [10, 30]})
    val, num, den = radar.window_rate(rows, "ts")
    assert val == pytest.approx(10 / 40) and (num, den) == (10, 40)
    assert val != pytest.approx((0.1 + 0.3) / 2)


def test_beta_prior_moments():
    rng = np.random.default_rng(1)
    a, b = radar.beta_prior(rng.beta(2, 10, 5000))
    assert a / (a + b) == pytest.approx(2 / 12, abs=0.01)


def test_p_rose_deterministic_and_symmetric():
    rng = lambda: np.random.default_rng(7)
    p1 = radar.p_rose((2, 10), 10, 50, 10, 50, 20000, rng())
    p2 = radar.p_rose((2, 10), 10, 50, 10, 50, 20000, rng())
    assert p1 == p2 and p1["p"] == pytest.approx(0.5, abs=0.02)
    assert radar.p_rose((2, 10), 17, 50, 14, 63, 20000, rng())["p"] > 0.8


def test_mad_z():
    assert radar.mad_z(3.0, np.array([1, 2, 3, 4, 5.0])) == pytest.approx((3 - 3) / (1.4826 * 1))
    assert radar.mad_z(1.0, np.array([1, 1, 1, 1, 1.0])) is None


def test_hard_rule_no_route_metrics():
    banned = ("route", "tprr", "yprr")
    names = radar.METRICS + list(yaml.safe_load(open(ROOT / "config/breakout_weights.yaml"))["weights"]["WR/TE"])
    assert not [n for n in names if any(b in n.lower() for b in banned)]


def test_weights_sum_to_one():
    w = yaml.safe_load(open(ROOT / "config/breakout_weights.yaml"))["weights"]
    for pg, ws in w.items():
        assert sum(ws.values()) == pytest.approx(1.0), pg
