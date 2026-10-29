"""slab-radar run --season S [--week W] --stage {nfl,cards,all} --out DIR

nfl   : nflverse → radar JSON for every complete week (freshness-gated) + player JSON + meta.json
cards : GemRate CSV export(s) → per-player card catalog JSON (run locally; the raw export is not published)
"""
import argparse
import json
import math
import time
from datetime import datetime, timezone
from pathlib import Path

import nflreadpy as nfl
import numpy as np
import polars as pl
import yaml

from . import gem, radar
from .nfl import build_player_week, complete_weeks, season_shares

ROOT = Path(__file__).resolve().parents[3]


def _clean(o):
    """Round floats for publishing (4 dp keeps percent rounding exact) and make JSON-safe."""
    if isinstance(o, float):
        return None if math.isnan(o) or math.isinf(o) else round(o, 4)
    if isinstance(o, (np.floating, np.integer)):
        return _clean(o.item())
    if isinstance(o, dict):
        return {k: _clean(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)):
        return [_clean(v) for v in o]
    return o


def write(path: Path, obj) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(_clean(obj), separators=(",", ":")))


def load_cfg() -> tuple[radar.Config, dict]:
    raw = yaml.safe_load(open(ROOT / "config/breakout_weights.yaml"))
    cfg = radar.Config(weights=raw["weights"], flags=raw["flags"], p_td=raw["p_td"], nu=raw["nu"],
                       min_snap_share=raw["min_snap_share"], signal_p=raw["signal_p"], noise_p=raw["noise_p"])
    return cfg, raw


def priors_for(season: int) -> dict:
    """Beta priors by method of moments on prior-season per-player shares (≥8 games)."""
    s = season_shares(season - 1).filter(pl.col("games") >= 8)
    pg = pl.col("position").map_elements(radar.pos_group, return_dtype=pl.String)
    s = s.with_columns(pg=pg)
    out = {}
    for g, metric, num, den in [("WR/TE", "ts", "targets", "tt"), ("RB", "ts", "targets", "tt"), ("RB", "carry", "carries", "tc")]:
        x = s.filter((pl.col("pg") == g) & (pl.col(den) > 0))
        shares = (x[num] / x[den]).to_numpy()
        out[(g, metric)] = radar.beta_prior(shares)
    return out


def stage_nfl(season: int, out: Path) -> None:
    t0 = time.time()
    cfg, raw_cfg = load_cfg()
    fpw, warnings = build_player_week(season)
    weeks = complete_weeks(season, fpw)
    fpw = fpw.filter(pl.col("week").is_in(weeks))
    priors = priors_for(season)
    injuries = nfl.load_injuries([season])
    history: dict[str, list] = {}
    for wk in weeks:
        rows = radar.compute(fpw, wk, cfg, priors, injuries)
        write(out / f"radar/{season}-{wk:02d}.json", {"season": season, "week": wk, "rows": rows})
        qualified = [r["gsis_id"] for r in rows if r["passes_min_snaps"]]  # same ranking as the radar table
        for r in rows:
            rank = qualified.index(r["gsis_id"]) + 1 if r["passes_min_snaps"] else None
            history.setdefault(r["gsis_id"], []).append(
                {"week": wk, "score": r["score"], "rank": rank, "badge": r["badge"], "flags": [f["flag"] for f in r["flags"]],
                 "p_share_up": r["p_share_up"]["p"] if r["p_share_up"] else None,
                 "p_metric": r["p_share_up"]["metric"] if r["p_share_up"] else None,
                 "p_n": r["p_share_up"]["n_recent"] if r["p_share_up"] else None})
    vals = radar.weekly_values(fpw.with_columns(rz_opps=pl.col("rz_targets") + pl.col("rz_carries")))
    cols = ["week", "team", "opponent_team", "targets", "team_targets", "rec_air_yards", "team_pass_air_yards",
            "carries", "team_carries", "offense_snaps", "team_offense_snaps", "rz_opps", "team_rz_opps",
            "dropbacks", "designed_rushes", "receptions", "receiving_yards", "rushing_yards", "passing_yards",
            "receiving_tds", "rushing_tds", "passing_tds", "fantasy_points_ppr"] + radar.METRICS
    cols = list(dict.fromkeys(cols))  # METRICS repeats xfp / dropbacks
    for (pid,), g in vals.group_by("gsis_id"):
        g = g.sort("week")
        write(out / f"players/{pid}.json", {
            "gsis_id": pid, "name": g["player_display_name"][-1], "position": g["position"][-1], "team": g["team"][-1],
            "season": season, "games": g.select(cols).to_dicts(), "radar": history.get(pid, []),
        })
    write(out / "meta.json", {
        "generated_ts": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "season": season, "weeks": weeks, "latest_week": weeks[-1] if weeks else None,
        "weights": raw_cfg, "priors": {f"{k[0]}:{k[1]}": v for k, v in priors.items()},
        "warnings": warnings, "nflreadpy": "0.1.5", "build_seconds": round(time.time() - t0),
    })
    print(f"nfl: weeks {weeks}, {fpw.height} player-weeks, {len(warnings)} warnings, {time.time() - t0:.0f}s")


def stage_cards(out: Path) -> None:
    """Every fixtures/gemrate/*.csv → data/cards/<gsis_id>.json. Links, certs and the raw file are not published."""
    products = gem.load_products(ROOT / "config/products.yaml")
    players = nfl.load_players().select("gsis_id", "display_name", "position")
    index = []
    for f in sorted((ROOT / "fixtures/gemrate").glob("*.csv")):
        cards = gem.shrink(gem.load_gemrate_csv(f, products))
        main = max(set(c["name"] for c in cards if "/" not in c["name"]), key=lambda n: sum(c["name"] == n for c in cards))
        hit = players.filter(pl.col("display_name") == main)
        if hit.height != 1:
            raise ValueError(f"{f.name}: cannot map '{main}' to exactly one gsis_id ({hit.height} matches)")
        pid = hit["gsis_id"][0]
        keep = ["card_key", "year", "set", "name", "parallel", "card_no", "gems", "total", "one_of_one",
                "flags", "pre_nfl", "license", "gem"]
        write(out / f"cards/{pid}.json", {"gsis_id": pid, "player": main, "source": "GemRate CSV export",
                                          "exported": f.stem, "cards": [{k: c[k] for k in keep} for c in cards]})
        index.append({"gsis_id": pid, "player": main, "n_cards": len(cards), "n_slabs": sum(c["total"] for c in cards)})
        print(f"cards: {main} ({pid}) {len(cards)} cards")
    write(out / "cards/index.json", index)


def main() -> None:
    ap = argparse.ArgumentParser(prog="slab-radar")
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("run")
    r.add_argument("--season", type=int, required=True)
    r.add_argument("--stage", choices=["nfl", "cards", "all"], default="all")
    r.add_argument("--out", type=Path, default=ROOT / "web/public/data")
    a = ap.parse_args()
    if a.stage in ("nfl", "all"):
        stage_nfl(a.season, a.out)
    if a.stage in ("cards", "all"):
        stage_cards(a.out)
