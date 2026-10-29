"""Constructed edge-case titles for parser unit tests. ALL records are synthetic=true.
These are NOT observed titles and must never be counted toward gold-set precision."""
import json, pathlib
ROOT = pathlib.Path(__file__).resolve().parents[2]
TS, MW = "Tyler Shough", "Michael Wilson"
def C(title, case, **exp):
    base = dict(player=None, year=None, product=None, subset=None, card_no=None, parallel=None, print_run=None, serial_no=None,
                is_auto=False, grader=None, grade=None, grade_label=None, qualifier=None, subgrades=None, auto_grade=None,
                tag_score=None, exclusion_reason=None, ambiguous=False)
    base.update(exp)
    return dict(raw_title=title, case=case, expected=base, synthetic=True)
P = dict(product="Prizm")
S = [
 # ---- ambiguity rule ----
 C("2025 Panini Prizm Tyler Shough Silver Prizm RC PSA 10", "shough_silver_no_card_no", player=TS, year="2025", **P, parallel="Silver Prizm", grader="PSA", grade=10.0, ambiguous=True),
 C("2025 Prizm Tyler Shough Silver Rookie Variation PSA 10", "variation_word_resolves_429", player=TS, year="2025", **P, subset="Rookie Variation", card_no="429", parallel="Silver Prizm", grader="PSA", grade=10.0),
 C("2025 Prizm Tyler Shough RV Silver PSA 9", "RV_abbrev_resolves_429", player=TS, year="2025", **P, subset="Rookie Variation", card_no="429", parallel="Silver Prizm", grader="PSA", grade=9.0),
 C("2025 Prizm Tyler Shough #327 Silver PSA 10 GEM MT", "explicit_327", player=TS, year="2025", **P, subset="Base", card_no="327", parallel="Silver Prizm", grader="PSA", grade=10.0, grade_label="GEM MINT"),
 C("2025 Prizm Tyler Shough No. 327 Silver RC", "card_no_No.", player=TS, year="2025", **P, card_no="327", parallel="Silver Prizm"),
 C("2025 Prizm Tyler Shough RC 327 Silver Prizm", "card_no_after_RC_bare", player=TS, year="2025", **P, card_no="327", parallel="Silver Prizm"),
 C("2025 Prizm Tyler Shough Silver PSA 10 #429/#327", "two_card_nos", player=TS, year="2025", **P, parallel="Silver Prizm", grader="PSA", grade=10.0, ambiguous=True),
 # ---- near-miss parallels (must NOT become Silver Prizm) ----
 C("2025 Prizm Tyler Shough #327 Silver Wave", "near_miss_silver_wave", player=TS, year="2025", **P, card_no="327", parallel="Silver Wave"),
 C("2025 Prizm Tyler Shough #327 Hyper Prizm /200", "near_miss_hyper", player=TS, year="2025", **P, card_no="327", parallel="Hyper Prizm", print_run=200),
 C("2025 Prizm Tyler Shough #327 White Disco Silver", "near_miss_disco_with_silver_word", player=TS, year="2025", **P, card_no="327", parallel="White Disco"),
 C("2025 Prizm Tyler Shough #327 Red White Blue Prizm", "near_miss_rwb", player=TS, year="2025", **P, card_no="327", parallel="Red White & Blue Prizm"),
 C("2025 Prizm Tyler Shough #327 RWB Silver Prizm", "near_miss_rwb_abbrev", player=TS, year="2025", **P, card_no="327", parallel="Red White & Blue Prizm"),
 C("2025 Prizm Tyler Shough #327 Silver Lazer PSA 10", "near_miss_lazer", player=TS, year="2025", **P, card_no="327", parallel="Lazer Prizm", grader="PSA", grade=10.0),
 C("2025 Prizm Tyler Shough #327 Silver Sparkle", "near_miss_sparkle", player=TS, year="2025", **P, card_no="327", parallel=None, ambiguous=True),
 C("2025 Prizm Tyler Shough #327 Prizm RC", "bare_prizm_token", player=TS, year="2025", **P, card_no="327", parallel=None, ambiguous=True),
 C("2025 Prizm Tyler Shough #327 Base RC NOT SILVER", "negation_phrase", player=TS, year="2025", **P, card_no="327", parallel="Base"),
 C("2023 Prizm Michael Wilson #303 Silver Prizm Wave", "near_miss_trailing_wave", player=MW, year="2023", **P, card_no="303", parallel=None, ambiguous=True),
 # ---- Optic ----
 C("2025 Optic Tyler Shough Rated Rookie Holo PSA 10", "optic_holo", player=TS, year="2025", product="Donruss Optic", subset="Rated Rookie", card_no="223", parallel="Holo", grader="PSA", grade=10.0),
 C("2025 Optic Tyler Shough RR Silver #223", "optic_silver_means_holo", player=TS, year="2025", product="Donruss Optic", subset="Rated Rookie", card_no="223", parallel="Holo"),
 C("2025 Optic Tyler Shough #223 Blue Hyper Holo", "optic_holo_word_inside_other_parallel", player=TS, year="2025", product="Donruss Optic", card_no="223", parallel="Blue Hyper"),
 C("2025 Donruss Tyler Shough Optic Preview Holo #304", "donruss_optic_preview_not_optic", player=TS, year="2025", product="Donruss", subset="Optic Preview", card_no="304", parallel="Holo"),
 # ---- Topps Chrome ----
 C("2025 TC Tyler Shough Refractor RC #398 PSA 10", "TC_abbrev", player=TS, year="2025", product="Topps Chrome", card_no="398", parallel="Refractor", grader="PSA", grade=10.0),
 C("2025 Topps Chrome Tyler Shough X-Fractor #398", "near_miss_xfractor", player=TS, year="2025", product="Topps Chrome", card_no="398", parallel="X-Fractor"),
 C("2025 Topps Chrome Tyler Shough Prism Refractor #398", "near_miss_prism", player=TS, year="2025", product="Topps Chrome", card_no="398", parallel="Prism Refractor"),
 C("2025 Topps Chrome Tyler Shough Sepia Refractor #398", "near_miss_sepia_not_in_gemrate", player=TS, year="2025", product="Topps Chrome", card_no="398", parallel="Sepia Refractor"),
 C("2025 Topps Chrome Tyler Shough Gold Refractor #12/50 #398", "colored_refractor_serial", player=TS, year="2025", product="Topps Chrome", card_no="398", parallel="Gold Refractor", print_run=50, serial_no="12/50"),
 C("2025 Topps Chrome Sapphire Tyler Shough #398", "sapphire_is_distinct_product", player=TS, year="2025", product="Topps Chrome Sapphire Edition", card_no="398", parallel="Base"),
 C("2025 Bowman Chrome Tyler Shough Refractor", "bowman_chrome_not_topps_chrome", player=TS, year="2025", product="Bowman Chrome", exclusion_reason=None, ambiguous=True),
 # ---- year formats ----
 C("23 Prizm Michael Wilson Silver #303 PSA 10", "two_digit_year", player=MW, year="2023", **P, card_no="303", parallel="Silver Prizm", grader="PSA", grade=10.0),
 C("2023-24 Prizm Michael Wilson Silver #303", "season_year_on_football", player=MW, year="2023", **P, card_no="303", parallel="Silver Prizm", ambiguous=True),
 # ---- serial / print run ----
 C("2025 Prizm Tyler Shough #327 Purple Ice 23/225", "serial_no_hash", player=TS, year="2025", **P, card_no="327", parallel="Purple Ice", print_run=225, serial_no="23/225"),
 C("2025 Prizm Tyler Shough #327 Pandora #/400", "hash_slash_print_run", player=TS, year="2025", **P, card_no="327", parallel="Pandora", print_run=400),
 C("2025 Prizm Tyler Shough #327 Gold 1/10 Jersey #1", "jersey_number_match_token", player=TS, year="2025", **P, card_no="327", parallel="Gold Prizm", print_run=10, serial_no="1/10"),
 # ---- autos ----
 C("2025 Prizm Tyler Shough RPA /99 Silver", "rpa_prizm", player=TS, year="2025", **P, subset="Rookie Patch Autographs", parallel="Silver Prizm", print_run=99, is_auto=True),
 C("2025 Prizm Tyler Shough Rookie Patch Auto Silver /99 BGS 9.5/10", "auto_grade_slash", player=TS, year="2025", **P, subset="Rookie Patch Autographs", parallel="Silver Prizm", print_run=99, is_auto=True, grader="BGS", grade=9.5, auto_grade=10.0),
 C("2025 Prizm Tyler Shough #327 Silver Auto PSA 10 Auto 10", "psa_dual_grade", player=TS, year="2025", **P, card_no="327", parallel="Silver Prizm", is_auto=True, grader="PSA", grade=10.0, auto_grade=10.0),
 C("2025 Prizm Tyler Shough #327 Silver Facsimile Signature", "facsimile_not_auto", player=TS, year="2025", **P, card_no="327", parallel="Silver Prizm", is_auto=False),
 # ---- graders ----
 C("2023 Prizm Michael Wilson #303 Silver PSA 9 MINT", "psa9", player=MW, year="2023", **P, card_no="303", parallel="Silver Prizm", grader="PSA", grade=9.0, grade_label="MINT"),
 C("2023 Prizm Michael Wilson #303 Silver PSA 8 (OC)", "psa_qualifier_OC", player=MW, year="2023", **P, card_no="303", parallel="Silver Prizm", grader="PSA", grade=8.0, qualifier="OC"),
 C("2023 Prizm Michael Wilson #303 Silver PSA 7 ST", "psa_qualifier_ST", player=MW, year="2023", **P, card_no="303", parallel="Silver Prizm", grader="PSA", grade=7.0, qualifier="ST"),
 C("2023 Prizm Michael Wilson #303 Silver PSA 6 MK", "psa_qualifier_MK", player=MW, year="2023", **P, card_no="303", parallel="Silver Prizm", grader="PSA", grade=6.0, qualifier="MK"),
 C("2023 Prizm Michael Wilson #303 Silver PSA 8 PD", "psa_qualifier_PD", player=MW, year="2023", **P, card_no="303", parallel="Silver Prizm", grader="PSA", grade=8.0, qualifier="PD"),
 C("2023 Prizm Michael Wilson #303 Silver PSA 7 MC OF", "psa_two_qualifiers", player=MW, year="2023", **P, card_no="303", parallel="Silver Prizm", grader="PSA", grade=7.0, qualifier="MC,OF"),
 C("2023 Prizm Michael Wilson #303 Silver PSA 10 OC", "psa10_with_qualifier_invalid", player=MW, year="2023", **P, card_no="303", parallel="Silver Prizm", grader="PSA", ambiguous=True),
 C("2023 Prizm Michael Wilson #303 Silver BGS 9.5 10/9.5/9.5/9.5", "bgs_slash_subgrades", player=MW, year="2023", **P, card_no="303", parallel="Silver Prizm", grader="BGS", grade=9.5, subgrades={"centering": 10, "corners": 9.5, "edges": 9.5, "surface": 9.5}),
 C("2023 Prizm Michael Wilson #303 Silver BGS 9.5 C10 Co9.5 E9.5 S9.5", "bgs_labeled_subgrades", player=MW, year="2023", **P, card_no="303", parallel="Silver Prizm", grader="BGS", grade=9.5, subgrades={"centering": 10, "corners": 9.5, "edges": 9.5, "surface": 9.5}),
 C("2023 Prizm Michael Wilson #303 Silver BGS 10 Black Label", "bgs_black_label", player=MW, year="2023", **P, card_no="303", parallel="Silver Prizm", grader="BGS", grade=10.0, grade_label="Black Label"),
 C("2023 Prizm Michael Wilson #303 Silver Beckett Pristine 10", "bgs_pristine_alias", player=MW, year="2023", **P, card_no="303", parallel="Silver Prizm", grader="BGS", grade=10.0, grade_label="Pristine"),
 C("2023 Prizm Michael Wilson #303 Silver SGC 10 PRI", "sgc_pristine_abbrev", player=MW, year="2023", **P, card_no="303", parallel="Silver Prizm", grader="SGC", grade=10.0, grade_label="Pristine"),
 C("2023 Prizm Michael Wilson #303 Silver SGC 10 GEM MINT", "sgc_gem", player=MW, year="2023", **P, card_no="303", parallel="Silver Prizm", grader="SGC", grade=10.0, grade_label="GEM MINT"),
 C("2023 Prizm Michael Wilson #303 Silver SGC 9.5", "sgc_95", player=MW, year="2023", **P, card_no="303", parallel="Silver Prizm", grader="SGC", grade=9.5),
 C("2023 Prizm Michael Wilson #303 Silver CGC Perfect 10", "cgc_perfect", player=MW, year="2023", **P, card_no="303", parallel="Silver Prizm", grader="CGC", grade=10.0, grade_label="Perfect"),
 C("2023 Prizm Michael Wilson #303 Silver CGC Pristine 10", "cgc_pristine", player=MW, year="2023", **P, card_no="303", parallel="Silver Prizm", grader="CGC", grade=10.0, grade_label="Pristine"),
 C("2023 Prizm Michael Wilson #303 Silver TAG 9 (895)", "tag_score", player=MW, year="2023", **P, card_no="303", parallel="Silver Prizm", grader="TAG", grade=9.0, tag_score=895),
 C("2023 Prizm Michael Wilson #303 Silver TAG Pristine 10", "tag_pristine", player=MW, year="2023", **P, card_no="303", parallel="Silver Prizm", grader="TAG", grade=10.0, grade_label="Pristine"),
 C("2023 Prizm Michael Wilson #303 Silver TAG 10", "tag_10_label_unknown", player=MW, year="2023", **P, card_no="303", parallel="Silver Prizm", grader="TAG", grade=10.0),
 C("2023 Prizm Michael Wilson #303 Silver PSA/DNA Authentic", "psa_auth_only", player=MW, year="2023", **P, card_no="303", parallel="Silver Prizm", grader="PSA", grade_label="Authentic"),
 C("2023 Prizm Michael Wilson #303 Silver Gem Mint 10", "grade_without_grader", player=MW, year="2023", **P, card_no="303", parallel="Silver Prizm", ambiguous=True),
 C("2023 Prizm Michael Wilson #303 Silver PSA 10 + SGC 10", "two_graders_two_cards", player=MW, year="2023", **P, card_no="303", parallel="Silver Prizm", exclusion_reason="multi_card_lot"),
 C("2023 Prizm Michael Wilson #303 Silver PSA 9 Crossover to BGS 9.5?", "crossover_speculation", player=MW, year="2023", **P, card_no="303", parallel="Silver Prizm", grader="PSA", grade=9.0),
 # ---- exclusions ----
 C("2023 Prizm Michael Wilson Silver RC lot x2", "lot_x2", player=MW, year="2023", **P, parallel="Silver Prizm", exclusion_reason="multi_card_lot"),
 C("2023 Prizm Michael Wilson Silver #303 PSA READY", "psa_ready", player=MW, year="2023", **P, card_no="303", parallel="Silver Prizm", exclusion_reason="hype_raw"),
 C("2023 Prizm Michael Wilson Silver #303 GEM? Potential 10", "gem_question", player=MW, year="2023", **P, card_no="303", parallel="Silver Prizm", exclusion_reason="hype_raw"),
 C("2023 Prizm Michael Wilson Silver #303 Reprint", "reprint", player=MW, exclusion_reason="reprint"),
 C("2023 Prizm Michael Wilson Silver #303 Custom ACEO Art Card", "custom", player=MW, exclusion_reason="custom"),
 C("Michael Wilson 2023 Prizm Silver Digital Card Topps Bunt NFT", "digital", player=MW, exclusion_reason="digital"),
 C("2023 Prizm Football Silver You Pick Michael Wilson Bijan Robinson", "you_pick_multi_name", exclusion_reason="you_pick"),
 C("2023 Prizm Michael Wilson Silver #303 PSA 10 Empty Slab / Case Only", "empty_slab", player=MW, exclusion_reason="not_a_card"),
 C("2022 Prizm Michael Wilson Silver PSA 10", "wrong_year_no_rc", player=MW, year="2022", **P, parallel="Silver Prizm", grader="PSA", grade=10.0, ambiguous=True),
 # ---- multi-player ----
 C("2023 Prizm Rookie Duals Michael Wilson / Marvin Harrison Jr. Silver PSA 10", "multi_player_card", player=[MW, "Marvin Harrison Jr."], year="2023", **P, subset=None, parallel="Silver Prizm", grader="PSA", grade=10.0, ambiguous=True),
 C("2023 Prizm Michael Wilson & Kyler Murray Lot PSA 10", "two_players_lot", exclusion_reason="multi_card_lot"),
]
out = ROOT / "fixtures/titles/synthetic_cases.jsonl"
with open(out, "w") as f:
    for i, r in enumerate(S, 1):
        f.write(json.dumps({"id": f"syn-{i:03d}", **r}, ensure_ascii=False) + "\n")
print(len(S), "->", out)
