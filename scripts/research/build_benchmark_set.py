"""Build fixtures/comps/benchmark_cards.csv: the 20-card comp-source benchmark set (PROMPT §3).

Cards 2-20 are looked up in fixtures/gemrate/tyler_shough.csv by (set, parallel, card_no); the
script fails if any lookup misses or is not unique. Card 1 (2023 Prizm Michael Wilson Silver #303)
is not in the export; its card number is REPORTED (COMC catalog), gemrate_id unknown until a
Wilson export or the GemRate API supplies it.
"""
import csv, re, pathlib

ROOT = pathlib.Path(__file__).resolve().parents[2]
rows = list(csv.reader(open(ROOT / "fixtures/gemrate/tyler_shough.csv", encoding="utf-8-sig")))[2:]

def ids(x):
    cl = re.search(r"gemRateId=([0-9a-f]{40})", x[10])
    gr = re.search(r"gemrate_id=([0-9a-f]{40})", x[13])
    return (gr.group(1) if gr else ""), (cl.group(1) if cl else "")

# (set, parallel, card_no, why it is in the set)
PICKS = [
    ("Panini Prizm", "Silver Prizm", "327", "spec: flagship RC"),
    ("Panini Prizm", "Silver Prizm", "429", "spec: Rookie Variation; collides with #327 when no card no."),
    ("Topps Chrome", "Refractor", "398", "spec: 2025 co-flagship RC"),
    ("Panini Donruss Optic", "Holo", "223", "spec: Optic Holo; 'Silver Holo' title hazard"),
    ("Topps Chrome", "Football Leather Refractor", "398", "spec: numbered parallel (/150 REPORTED)"),
    ("Panini Prizm", "Autograph-Silver Prizm", "327", "spec: auto; collides with Silver #327"),
    ("Panini Prizm", "Base", "327", "Card Ladder id != GemRate id (plan F2)"),
    ("Panini Prizm", "Lazer Prizm", "327", "'Silver Lazer' title hazard"),
    ("Panini Donruss Optic", "Base", "223", "Card Ladder id != GemRate id (plan F2)"),
    ("Topps Chrome", "Base", "398", "Topps base RC; Base vs Refractor split"),
    ("Panini Donruss Downtown", "Base", "19", "highest-pop card (1,655); case-hit insert"),
    ("Panini Donruss", "Base", "304", "Rated Rookie base; cheap, high volume"),
    ("Panini Donruss", "Optic Preview-Pink", "304", "'Optic Preview' is Donruss, not Optic"),
    ("Panini Mosaic", "Base", "273", "Mosaic #273 vs #312 split"),
    ("Panini Mosaic", "Reactive Purple", "312", "Mosaic second RC number"),
    ("Panini Select", "Silver Prizm", "41", "Select tiered numbering (#41/#141/#341/#441)"),
    ("Panini Donruss", "Autograph-Orange", "304", "second auto, different product"),
    ("Panini Prizm", "Blue Wave", "327", "low-pop parallel (78): recall stress"),
    ("Panini Prizm Draft Picks", "Gold Ice", "49", "pre-NFL product; 'Prizm' name collision"),
]

out = [dict(bench_no=1, year="2023", player="Michael Wilson", set="Panini Prizm", parallel="Silver Prizm",
            card_no="303", gemrate_id="", cardladder_gemrate_id="", psa_gems="", psa_total="",
            card_no_label="REPORTED (COMC catalog)", why="spec: 2023 Prizm Silver RC")]
for i, (s, p, n, why) in enumerate(PICKS, start=2):
    hit = [x for x in rows if x[2] == "2025" and x[3] == s and x[5] == p and x[6] == n]
    assert len(hit) == 1, (s, p, n, len(hit))
    x = hit[0]
    gr, cl = ids(x)
    out.append(dict(bench_no=i, year="2025", player=x[4], set=s, parallel=p, card_no=n, gemrate_id=gr,
                    cardladder_gemrate_id=cl, psa_gems=x[7].replace(",", ""), psa_total=x[8].replace(",", ""),
                    card_no_label="VERIFIED (GemRate export)", why=why))

dst = ROOT / "fixtures/comps/benchmark_cards.csv"
dst.parent.mkdir(parents=True, exist_ok=True)
with open(dst, "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(out[0]))
    w.writeheader()
    w.writerows(out)
print(f"wrote {len(out)} cards -> {dst.relative_to(ROOT)}")
