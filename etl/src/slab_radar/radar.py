"""Breakout Radar (plan §4). Window rates are Σnum/Σden over the player's active games (≥1 offensive snap).

All share/volume metrics are OBSERVED. z-scores, P(share rose) and the breakout score are MODEL outputs.
"""
import math
from dataclasses import dataclass

import numpy as np
import polars as pl

SHARES = {  # metric: (numerator, denominator)
    "ts": ("targets", "team_targets"),
    "ays": ("rec_air_yards", "team_pass_air_yards"),
    "snap": ("offense_snaps", "team_offense_snaps"),
    "carry": ("carries", "team_carries"),
    "rz": ("rz_opps", "team_rz_opps"),
}
PER_GAME = {"xfp": "xfp", "dropbacks": "dropbacks", "designed_rush": "designed_rushes"}
METRICS = list(SHARES) + list(PER_GAME)


@dataclass(frozen=True)
class Config:
    weights: dict          # position -> {metric: w, "last1": w}
    flags: dict            # flag -> bonus
    p_td: float
    nu: float = 4.0        # shrink player sd toward position sd
    min_snap_share: float = 0.25
    signal_p: float = 0.90
    noise_p: float = 0.70
    mc_draws: int = 20_000
    seed: int = 20261006


def pos_group(position: str) -> str:
    return "WR/TE" if position in ("WR", "TE") else position


def weekly_values(df: pl.DataFrame) -> pl.DataFrame:
    """Per-game metric values (for sds, position distributions, charts)."""
    exprs = [pl.when(pl.col(d) > 0).then(pl.col(n) / pl.col(d)).otherwise(None).alias(m) for m, (n, d) in SHARES.items()]
    exprs += [pl.col(c).cast(pl.Float64).alias(m) for m, c in PER_GAME.items()]
    return df.with_columns(exprs)


def window_rate(rows: pl.DataFrame, metric: str) -> tuple[float | None, float, float]:
    """Σnum/Σden (shares) or mean per game; returns (value, num, den)."""
    if metric in SHARES:
        n, d = SHARES[metric]
        num, den = float(rows[n].sum()), float(rows[d].sum())
        return (num / den if den > 0 else None), num, den
    c = PER_GAME[metric]
    vals = rows[c].drop_nulls()
    return (float(vals.mean()) if len(vals) else None), float(vals.sum()) if len(vals) else 0.0, float(len(vals))


def mad_z(x: float | None, pop: np.ndarray) -> float | None:
    if x is None or len(pop) < 5:
        return None
    med = float(np.median(pop))
    mad = 1.4826 * float(np.median(np.abs(pop - med)))
    return (x - med) / mad if mad > 0 else None


def beta_prior(shares: np.ndarray) -> tuple[float, float] | None:
    """Method-of-moments Beta fit to per-player season shares (prior season)."""
    if len(shares) < 10:
        return None
    m, v = float(shares.mean()), float(shares.var(ddof=1))
    if v <= 0 or v >= m * (1 - m):
        return None
    k = m * (1 - m) / v - 1
    return m * k, (1 - m) * k


def p_rose(prior, k_r, n_r, k_b, n_b, draws, rng) -> dict | None:
    """P(θ_recent > θ_base) by seeded Monte Carlo, with posterior means and 80% credible intervals."""
    if prior is None or n_r <= 0 or n_b <= 0:
        return None
    a, b = prior
    r = rng.beta(a + k_r, b + n_r - k_r, draws)
    s = rng.beta(a + k_b, b + n_b - k_b, draws)
    q = lambda x: [float(np.quantile(x, 0.1)), float(np.quantile(x, 0.9))]
    return {"p": float((r > s).mean()), "recent_mean": float(r.mean()), "recent_ci80": q(r),
            "base_mean": float(s.mean()), "base_ci80": q(s), "n_recent": n_r, "n_base": n_b}


def compute(fpw: pl.DataFrame, week: int, cfg: Config, priors: dict, injuries: pl.DataFrame | None = None) -> list[dict]:
    """Radar rows for `week` (one per player active that week)."""
    rng = np.random.default_rng(cfg.seed + week)
    df = weekly_values(fpw.filter(pl.col("week") <= week).with_columns(rz_opps=pl.col("rz_targets") + pl.col("rz_carries")))
    active = df.filter(pl.col("offense_snaps") > 0)

    # Windows per player: last1 = this week; last3 = last 3 active games; baselines = active games before each window.
    games = active.sort("week").group_by("gsis_id", maintain_order=True).agg(pl.col("week"))
    gmap = {r["gsis_id"]: r["week"] for r in games.iter_rows(named=True)}
    this = active.filter(pl.col("week") == week)

    # Position distributions for z_pos (players passing the min-snap filter in the same window) and pooled sds.
    def window_table(k):
        rows = []
        for pid, wks in gmap.items():
            if wks[-1] != week:
                continue
            w = active.filter((pl.col("gsis_id") == pid) & pl.col("week").is_in(wks[-k:]))
            snap, _, _ = window_rate(w, "snap")
            rows.append({"gsis_id": pid, "pg": pos_group(w["position"][0]), "snap": snap,
                         **{m: window_rate(w, m)[0] for m in METRICS}})
        return pl.DataFrame(rows, infer_schema_length=None)
    tables = {1: window_table(1), 3: window_table(3)}
    pos_sd = {}
    qual_games = active.filter(pl.col("snap") >= cfg.min_snap_share).with_columns(pg=pl.col("position").map_elements(pos_group, return_dtype=pl.String))
    for (pg,), g in qual_games.group_by("pg"):
        for m in METRICS:
            # pooled within-player variance: removes between-player level differences
            v = g.group_by("gsis_id").agg(pl.col(m).var().alias("v"), pl.col(m).count().alias("n")).filter(pl.col("n") >= 2)
            tot = float((v["v"].fill_null(0) * (v["n"] - 1)).sum()); dof = float((v["n"] - 1).sum())
            pos_sd[(pg, m)] = math.sqrt(tot / dof) if dof > 0 and tot > 0 else None
        fp = g.filter(pl.col("xfp").is_not_null()).with_columns(d=pl.col("fantasy_points_ppr") - pl.col("xfp"))["d"]
        pos_sd[(pg, "fp_minus_xfp")] = float(fp.std()) if len(fp) > 2 else None

    # Starting QB per team-game (most dropbacks) for qb_change.
    qb = (df.filter(pl.col("position") == "QB").sort("dropbacks", descending=True)
          .group_by("team", "week").agg(pl.col("gsis_id").first().alias("qb"), pl.col("player_display_name").first().alias("qb_name")))
    qbmap = {(r["team"], r["week"]): (r["qb"], r["qb_name"]) for r in qb.iter_rows(named=True)}
    out_status = {}
    if injuries is not None:
        inj = injuries.filter((pl.col("week") == week) & pl.col("report_status").is_in(["Out", "Doubtful"]))
        out_status = {r["gsis_id"]: r["report_status"] for r in inj.iter_rows(named=True)}

    rows = []
    for r in this.iter_rows(named=True):
        pid, wks, pg = r["gsis_id"], gmap[r["gsis_id"]], pos_group(r["position"])
        if pg not in cfg.weights:
            continue
        mine = active.filter(pl.col("gsis_id") == pid)
        metrics, z = {}, {1: {}, 3: {}}
        for k in (1, 3):
            win_wks, base_wks = wks[-k:], wks[:-k]
            win, base = mine.filter(pl.col("week").is_in(win_wks)), mine.filter(pl.col("week").is_in(base_wks))
            for m in METRICS:
                val, num, den = window_rate(win, m)
                bval = window_rate(base, m)[0] if len(base_wks) >= 2 else None
                entry = metrics.setdefault(m, {})
                entry[f"last{k}"], entry[f"last{k}_num"], entry[f"last{k}_den"] = val, num, den
                entry[f"base{k}"], entry[f"base{k}_games"] = bval, len(base_wks)
                # z_self: Δ / (sd_i · sqrt(1/k + 1/n_base)), sd_i² = (n_i s_i² + ν s_pos²)/(n_i + ν)
                zs = None
                s_pos = pos_sd.get((pg, m))
                if val is not None and bval is not None and s_pos:
                    vals = base[m].drop_nulls().to_numpy()
                    n_i = len(vals)
                    s_i2 = float(vals.var(ddof=1)) if n_i >= 2 else 0.0
                    sd = math.sqrt((n_i * s_i2 + cfg.nu * s_pos ** 2) / (n_i + cfg.nu))
                    zs = (val - bval) / (sd * math.sqrt(1 / k + 1 / max(n_i, 1))) if sd > 0 else None
                pop = tables[k].filter((pl.col("pg") == pg) & (pl.col("snap") >= cfg.min_snap_share))[m].drop_nulls().to_numpy()
                zp = mad_z(val, pop)
                entry[f"z_self{k}"], entry[f"z_pos{k}"] = zs, zp
                parts = [x for x in (zs, zp) if x is not None]
                z[k][m] = sum(parts) / len(parts) if parts else None
        for k in (1, 3):  # WOPR shown, not weighted (linear in TS and AYS)
            ts, ays = metrics["ts"][f"last{k}"], metrics["ays"][f"last{k}"]
            metrics.setdefault("wopr", {})[f"last{k}"] = 1.5 * ts + 0.7 * ays if ts is not None and ays is not None else None

        w = cfg.weights[pg]
        core = {m: wt for m, wt in w.items() if m != "last1"}
        clip = lambda v: max(-3.0, min(3.0, v))
        contrib = {m: wt * clip(z[3][m]) for m, wt in core.items() if z[3].get(m) is not None}
        l1 = sum(wt * clip(z[1][m]) for m, wt in core.items() if z[1].get(m) is not None) / sum(core.values())
        score = sum(contrib.values()) + w.get("last1", 0) * l1

        # Flags (recorded data only).
        flags = []
        fp_d = (r["fantasy_points_ppr"] - r["xfp"]) if r["xfp"] is not None else None
        sd_fp = pos_sd.get((pg, "fp_minus_xfp"))
        zx = metrics["xfp"]["z_self1"]
        td_driven = bool(fp_d is not None and sd_fp and fp_d >= max(6.0, 1.5 * sd_fp) and (zx is None or zx < 1))
        if td_driven:
            flags.append({"flag": "td_driven", "detail": f"FP − xFP = {fp_d:.1f}"})
        prev = [x for x in wks if x < week]
        if prev:
            prev_team = mine.filter(pl.col("week") == prev[-1])["team"][0]
            if prev_team != r["team"]:
                flags.append({"flag": "team_change", "detail": f"{prev_team} → {r['team']}"})
            now_qb, before_qb = qbmap.get((r["team"], week)), qbmap.get((prev_team, prev[-1]))
            if now_qb and before_qb and now_qb[0] != before_qb[0] and prev_team == r["team"]:
                flags.append({"flag": "qb_change", "detail": f"{before_qb[1]} → {now_qb[1]}"})
        share_m = "carry" if pg == "RB" else "ts"
        for t in active.filter((pl.col("team") == r["team"]) & (pl.col("gsis_id") != pid)
                               & (pl.col("week") < week)).select("gsis_id", "player_display_name", "position").unique().iter_rows(named=True):
            if pos_group(t["position"]) != pg:
                continue
            tb = active.filter((pl.col("gsis_id") == t["gsis_id"]) & (pl.col("team") == r["team"]) & (pl.col("week") < week))
            if tb.height < 2:
                continue
            share = window_rate(tb, share_m)[0] or 0
            played = active.filter((pl.col("gsis_id") == t["gsis_id"]) & (pl.col("week") == week)).height > 0
            if share >= 0.15 and not played:
                why = out_status.get(t["gsis_id"], "no offensive snaps")
                flags.append({"flag": "vacated_opportunity",
                              "detail": f"{t['player_display_name']} ({why}); baseline {share_m.upper()} {share:.0%}"})
        score += sum(cfg.flags.get(name, 0) for name in {f["flag"] for f in flags} - {"td_driven"})  # once per flag type
        score -= cfg.p_td * td_driven

        # P(true share rose): last-3 vs its baseline when ≥2 baseline games exist, else last-1 vs its baseline.
        pr = None
        if pg in ("WR/TE", "RB"):
            mm, (n, d) = metrics[share_m], SHARES[share_m]
            for k in (3, 1):
                if len(wks) - k >= 2:
                    base = mine.filter(pl.col("week").is_in(wks[:-k]))
                    pr = p_rose(priors.get((pg, share_m)), mm[f"last{k}_num"], mm[f"last{k}_den"],
                                float(base[n].sum()), float(base[d].sum()), cfg.mc_draws, rng)
                    if pr:
                        pr.update(metric=share_m, window=k)
                        break
        badge = None
        if pr:
            k = pr["window"]
            snap_delta = metrics["snap"][f"last{k}"] - metrics["snap"][f"base{k}"] if metrics["snap"][f"base{k}"] is not None else None
            rose = (mm[f"last{k}"] or 0) > (mm[f"base{k}"] or 0)
            if pr["p"] >= cfg.signal_p and (snap_delta is None or snap_delta >= 0):
                badge = "signal"
            elif rose and pr["p"] < cfg.noise_p:  # the share went up, but not convincingly
                badge = "noise"

        rows.append({
            "gsis_id": pid, "name": r["player_display_name"], "position": r["position"], "team": r["team"],
            "opponent": r["opponent_team"], "games": len(wks),
            "passes_min_snaps": (metrics["snap"]["last3"] or 0) >= cfg.min_snap_share,
            "fp_ppr": r["fantasy_points_ppr"], "metrics": metrics, "z": {"last1": z[1], "last3": z[3]},
            "contrib": contrib, "last1_term": w.get("last1", 0) * l1,
            "score": score, "flags": flags, "td_driven": td_driven, "p_share_up": pr, "badge": badge,
        })
    rows.sort(key=lambda x: -x["score"])
    return rows
