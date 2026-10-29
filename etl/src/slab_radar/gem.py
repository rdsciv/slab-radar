"""GemRate CSV importer + hierarchical beta-binomial gem-rate shrinkage (plan §3.1, §7; lessons 2026-10-02/06).

Importer rules:
- Two header rows. Universal Pop link carries `gemrate_id=<40 hex>` or the literal `None` (→ NULL).
- card_key = universal id → else PSA-scoped id from Card Ladder links (flag psa_scoped_id_only)
  → else 'sr_' + sha1(natural_key) (flag no_gemrate_id). [fallback pending Ryan's approval, plan F1]
- Counts may contain thousands separators ("1,655").
- Gem rate is recomputed from counts; GemRate's string is never used.
- 1/1s are kept in the catalog but excluded from priors. is_rc is never inferred (the export has no RC column).

Shrinkage levels (most specific first): (year, set, parallel) → (year, set) → (year) → global.
A level is used only with ≥3 cards and Σn ≥ 100; otherwise its parent's (μ, κ). Each level is fit by
maximizing the beta-binomial marginal likelihood with a N(0, 1) penalty on logit μ − logit μ_parent.
"""
import csv
import hashlib
import math
import re
from pathlib import Path

import numpy as np
import yaml
from scipy import optimize, special, stats

HEX = re.compile(r"[0-9a-f]{40}")
MIN_CARDS, MIN_N = 3, 100


def natural_key(year, set_, name, parallel, card_no) -> str:
    return "|".join(" ".join(str(x).lower().split()) for x in (year, set_, name, parallel, card_no))


def _int(s: str) -> int:
    return int(s.replace(",", "") or 0)


def product_facts(set_: str, year: int, products: dict) -> dict:
    best = max((p for p in products["prefixes"] if set_.startswith(p)), key=len, default=None)
    pre_nfl = products["prefixes"][best]["pre_nfl"] if best else None
    lic = next((l for l in products.get("license", []) if set_.startswith(l["prefix"]) and year in l["years"]), None)
    return {"pre_nfl": pre_nfl, "license": lic}


def load_gemrate_csv(path: Path, products: dict) -> list[dict]:
    rows = list(csv.reader(open(path, encoding="utf-8-sig")))[2:]
    cards, seen = [], {}
    for x in rows:
        cat, year, set_, name, parallel, card_no = x[1], x[2], x[3], x[4], x[5], x[6]
        uni = re.search(r"gemrate_id=([0-9a-f]{40})", x[13])
        cl = re.search(r"gemRateId=([0-9a-f]{40})", x[10])
        uni, cl = (uni.group(1) if uni else None), (cl.group(1) if cl else None)
        nk = natural_key(year, set_, name, parallel, card_no)
        flags = []
        if uni:
            key = uni
            if cl and cl != uni:
                flags.append("gemrate_id_mismatch")
        elif cl:
            key = cl
            flags.append("psa_scoped_id_only")
        else:
            key = "sr_" + hashlib.sha1(nk.encode()).hexdigest()
            flags.append("no_gemrate_id")
        if not card_no.strip():
            flags.append("no_card_no")
        if "/" in name:
            flags.append("multi_player")
        if key in seen:  # never silently merge two rows onto one key
            raise ValueError(f"card_key collision {key}: {seen[key]} vs {nk}")
        seen[key] = nk
        gems, total = _int(x[7]), _int(x[8])
        cards.append({
            "card_key": key, "gemrate_id": uni, "cardladder_gemrate_id": cl, "natural_key": nk,
            "category": cat, "year": int(year), "set": set_, "name": name, "parallel": parallel, "card_no": card_no,
            "gems": gems, "total": total, "one_of_one": "1/1" in parallel or "1/1" in set_,
            "flags": flags, **product_facts(set_, int(year), products),
        })
    return cards


def _negll(params, g, n, mu_parent):
    lm, lk = params
    mu, kappa = special.expit(lm), math.exp(lk)
    a, b = mu * kappa, (1 - mu) * kappa
    ll = np.sum(special.betaln(g + a, n - g + b) - special.betaln(a, b))
    pen = 0.0 if mu_parent is None else 0.5 * (lm - special.logit(mu_parent)) ** 2
    return -ll + pen


def fit_level(g: np.ndarray, n: np.ndarray, mu_parent: float | None) -> tuple[float, float]:
    """(μ, κ) maximizing the penalized beta-binomial marginal likelihood."""
    pooled = (g.sum() + 0.5) / (n.sum() + 1.0)
    x0 = [special.logit(pooled if mu_parent is None else mu_parent), math.log(10.0)]
    res = optimize.minimize(_negll, x0, args=(g, n, mu_parent), method="Nelder-Mead",
                            options={"xatol": 1e-6, "fatol": 1e-8, "maxiter": 4000})
    lm, lk = res.x
    return float(special.expit(lm)), float(min(math.exp(lk), 1e4))


def shrink(cards: list[dict]) -> list[dict]:
    """Attach posterior gem rate (MODEL) to every card with total > 0."""
    eligible = [c for c in cards if c["total"] > 0 and not c["one_of_one"]]
    keyfns = [("year_set_parallel", lambda c: (c["year"], c["set"], c["parallel"])),
              ("year_set", lambda c: (c["year"], c["set"])),
              ("year", lambda c: (c["year"],)),
              ("global", lambda c: ())]
    arr = lambda cs, f: np.array([c[f] for c in cs], dtype=float)
    glob = fit_level(arr(eligible, "gems"), arr(eligible, "total"), None)
    fits = {("global", ()): ("global", glob)}

    def level_fit(depth: int, c) -> tuple[str, tuple[float, float]]:
        name, fn = keyfns[depth]
        k = (name, fn(c))
        if k in fits:
            return fits[k]
        parent = level_fit(depth + 1, c)
        members = [e for e in eligible if fn(e) == fn(c)]
        if len(members) >= MIN_CARDS and sum(e["total"] for e in members) >= MIN_N:
            fits[k] = (name, fit_level(arr(members, "gems"), arr(members, "total"), parent[1][0]))
        else:
            fits[k] = parent  # too thin: inherit parent's (μ, κ) and its level name
        return fits[k]

    for c in cards:
        if c["total"] <= 0:
            c["gem"] = None
            continue
        level, (mu, kappa) = level_fit(0, c)
        a, b = mu * kappa + c["gems"], (1 - mu) * kappa + c["total"] - c["gems"]
        c["gem"] = {
            "raw_rate": c["gems"] / c["total"], "n": c["total"],
            "post_mean": a / (a + b), "ci95": [float(stats.beta.ppf(0.025, a, b)), float(stats.beta.ppf(0.975, a, b))],
            "prior_level": level, "prior_mu": mu, "prior_kappa": kappa,
            "provenance": "MODEL", "raw_provenance": "OBSERVED",
            "scope": "GemRate export, grader scope unconfirmed",
        }
    return cards


def load_products(path: Path) -> dict:
    return yaml.safe_load(open(path))
