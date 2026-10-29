from pathlib import Path

import numpy as np
import pytest
from scipy import stats

from slab_radar import gem

ROOT = Path(__file__).resolve().parents[2]
FIX = ROOT / "fixtures/gemrate/tyler_shough.csv"
PRODUCTS = gem.load_products(ROOT / "config/products.yaml")


@pytest.fixture(scope="module")
def cards():
    if not FIX.exists():
        pytest.skip("GemRate export is local-only (not published)")
    return gem.load_gemrate_csv(FIX, PRODUCTS)


def test_id_states_and_counts(cards):
    flags = lambda f: sum(f in c["flags"] for c in cards)
    assert len(cards) == 1877
    assert flags("psa_scoped_id_only") == 1114 and flags("no_gemrate_id") == 441
    assert flags("gemrate_id_mismatch") == 13 and flags("multi_player") == 32 and flags("no_card_no") == 5
    assert len({c["card_key"] for c in cards}) == 1877


def test_thousands_separator(cards):
    downtown = next(c for c in cards if c["set"] == "Panini Donruss Downtown" and c["card_no"] == "19")
    assert (downtown["gems"], downtown["total"]) == (1163, 1655)


def test_silver_327_and_429_are_distinct_cards(cards):
    s = {c["card_no"]: c for c in cards if c["set"] == "Panini Prizm" and c["parallel"] == "Silver Prizm" and c["year"] == 2025}
    assert (s["327"]["gems"], s["327"]["total"]) == (27, 152)
    assert (s["429"]["gems"], s["429"]["total"]) == (53, 193)
    assert s["327"]["card_key"] != s["429"]["card_key"]
    assert "psa_scoped_id_only" in s["327"]["flags"]   # flagship has no universal id (plan F1)


def test_pre_nfl_is_explicit(cards):
    by_set = {c["set"]: c["pre_nfl"] for c in cards}
    assert by_set["Bowman University Chrome Prospects"] is True
    assert by_set["Panini Prizm Draft Picks"] is True
    assert by_set["Panini Prizm"] is False
    assert by_set["Leaf Trinity Autographs"] is None   # unknown stays unknown


def test_is_rc_never_inferred(cards):
    assert all("is_rc" not in c for c in cards)


def _card(i, set_, parallel, g, n, year=2025):
    return {"year": year, "set": set_, "parallel": parallel, "gems": g, "total": n, "one_of_one": False}


def test_posterior_is_conjugate_beta():
    cs = [_card(i, "S", f"P{i}", g, n) for i, (g, n) in enumerate([(30, 100), (50, 100), (20, 80), (45, 90)])]
    out = gem.shrink(cs)
    for c in out:
        g = c["gem"]
        a = g["prior_mu"] * g["prior_kappa"] + c["gems"]
        b = (1 - g["prior_mu"]) * g["prior_kappa"] + c["total"] - c["gems"]
        assert g["post_mean"] == pytest.approx(a / (a + b))
        assert g["ci95"][0] == pytest.approx(stats.beta.ppf(0.025, a, b))


def test_thin_pool_inherits_parent():
    cs = [_card(0, "Thin", "X", 3, 4)] + [_card(i, "Thick", f"P{i}", 40, 100) for i in range(1, 5)]
    out = gem.shrink(cs)
    thin = out[0]["gem"]
    assert thin["prior_level"] in ("year", "global")   # 1 card, n=4 < thresholds → never its own level
    assert thin["post_mean"] < thin["raw_rate"]           # 3/4 pulled toward ~0.4


def test_one_of_ones_excluded_from_priors():
    base = [_card(i, "S", f"P{i}", 40, 100) for i in range(4)]
    one = dict(_card(9, "S", "Superfractor 1/1", 1, 1), one_of_one=True)
    a = gem.shrink([dict(c) for c in base])
    b = gem.shrink([dict(c) for c in base] + [one])
    assert a[0]["gem"]["prior_mu"] == pytest.approx(b[0]["gem"]["prior_mu"])
