"""Build fixtures/titles/seed_gold.jsonl from titles observed during M0 research (2026-10-02).

Every raw_title below was observed verbatim on a public page or a search-engine result
title. Nothing here is synthetic. gemrate_id is looked up from fixtures/gemrate/tyler_shough.csv
when the labeled (set, parallel, card_no) is present there; otherwise null.
"""
import csv, json, re, pathlib

ROOT = pathlib.Path(__file__).resolve().parents[2]
rows = list(csv.reader(open(ROOT / "fixtures/gemrate/tyler_shough.csv", encoding="utf-8-sig")))[2:]
GR = {}
for x in rows:
    m = re.search(r"gemRateId=([0-9a-f]{40})", x[10])
    if m:
        GR[(x[2], x[3], x[5], x[6])] = m.group(1)

E = "ebay_item_serp"        # eBay /itm/ listing title seen as a search-engine result title (not fetched; sold status unknown)
EC = "ebay_catalog_serp"    # eBay /p/ catalog or catalog-derived title seen in search results
FL = "fanatics_lot_fetched" # Fanatics Collect lot page fetched; sold price/date confirmed on page
FS = "fanatics_serp"        # Fanatics Collect title seen in search results (not fetched)
GS = "goldin_serp"          # Goldin item title seen in search results (Goldin pages are a JS shell)
DS = "dealer_serp"          # small dealer / retailer product title seen in search results

def L(player, year, mfr, product, subset="Base", card_no=None, parallel="Base", print_run=None, serial_no=None,
      is_rc=True, is_auto=False, grader=None, grade=None, grade_label=None, qualifier=None, subgrades=None,
      auto_grade=None, tag_score=None, exclusion_reason=None):
    return dict(player=player if isinstance(player, list) else [player], year=year, manufacturer=mfr, product=product,
                subset=subset, card_no=card_no, parallel=parallel, print_run=print_run, serial_no=serial_no,
                is_rc=is_rc, is_auto=is_auto, grader=grader, grade=grade, grade_label=grade_label, qualifier=qualifier,
                subgrades=subgrades, auto_grade=auto_grade, tag_score=tag_score, exclusion_reason=exclusion_reason)

TS, MW = "Tyler Shough", "Michael Wilson"
R = []
def add(src, url, title, labels, gr_key=None, ambiguous=False, why=None, hazards=(), sold=None, price=None, date=None):
    R.append(dict(source_type=src, source_url=url, raw_title=title, sold_confirmed=sold, sale_price_usd=price,
                  sale_date=date, labels=labels, gemrate_key=gr_key, ambiguous=ambiguous, ambiguity_reason=why,
                  hazards=list(hazards), synthetic=False))

# ---------------- 2025 Prizm Tyler Shough ----------------
add(E, "https://www.ebay.com/itm/406972731826", "2025 Panini Prizm - Rookie Variation Tyler Shough #429 Silver Prizm (RC)",
    L(TS, "2025", "Panini", "Prizm", "Rookie Variation", "429", "Silver Prizm"), ("2025", "Panini Prizm", "Silver Prizm", "429"),
    hazards=["catalog_style_title"])
add(E, "https://www.ebay.com/itm/117036627491", "2025 Panini Prizm Tyler Shough Silver Image Variation Prizm (RC) #429",
    L(TS, "2025", "Panini", "Prizm", "Rookie Variation", "429", "Silver Prizm"), ("2025", "Panini Prizm", "Silver Prizm", "429"),
    hazards=["variation_alias:image_variation"])
add(E, "https://www.ebay.com/itm/376936660750", "Tyler Shough Rookie 2025 Panini Prizm Football #327 Silver Lazer RC Saints",
    L(TS, "2025", "Panini", "Prizm", "Base", "327", "Lazer Prizm"), ("2025", "Panini Prizm", "Lazer Prizm", "327"),
    hazards=["near_miss:silver_lazer_is_lazer_not_silver"])
add(E, "https://www.ebay.com/itm/157946663524", "Tyler Shough: Louisville (Prizm Silver, Wild Card /299, Pumpkins).",
    L(TS, None, None, None, None, None, None, is_rc=None, exclusion_reason="multi_card_lot"),
    hazards=["multiple_cards_in_one_title", "college_team_name"])
add(E, "https://www.ebay.com/itm/198023529744", "2025 Panini Prizm - Tyler Shough - Silver Lazer Rookie RC Saints",
    L(TS, "2025", "Panini", "Prizm", "Base", "327", "Lazer Prizm"), ("2025", "Panini Prizm", "Lazer Prizm", "327"),
    why=None, hazards=["near_miss:silver_lazer_is_lazer_not_silver", "no_card_no_resolved_by_catalog:lazer_only_at_327"])
add(E, "https://www.ebay.com/itm/137395622924", "2025 Panini Prizm #16 Tyler Shough Prizmatic",
    L(TS, "2025", "Panini", "Prizm", "Prizmatic", "16", "Base"), ("2025", "Panini Prizm Prizmatic", "Base", "16"),
    hazards=["insert_subset_low_number"])
add(E, "https://www.ebay.com/itm/336701510018", "Panini 2025 Prizm Tyler Shough Saints Silver Prizm RC #327 PSA 10 LOW POP",
    L(TS, "2025", "Panini", "Prizm", "Base", "327", "Silver Prizm", grader="PSA", grade=10.0),
    ("2025", "Panini Prizm", "Silver Prizm", "327"), hazards=["manufacturer_before_year", "hype_suffix:LOW POP"])
add(E, "https://www.ebay.com/itm/398142996979", "2025 Panini Prizm - Rookies Tyler Shough #327 Silver Prizm (RC)",
    L(TS, "2025", "Panini", "Prizm", "Base", "327", "Silver Prizm"), ("2025", "Panini Prizm", "Silver Prizm", "327"),
    hazards=["catalog_style_title"])
add(E, "https://www.ebay.com/itm/377246295797", "2025 Panini Prizm Tyler Shough Silver Lazer RC Rookie #327 Saints",
    L(TS, "2025", "Panini", "Prizm", "Base", "327", "Lazer Prizm"), ("2025", "Panini Prizm", "Lazer Prizm", "327"),
    hazards=["near_miss:silver_lazer_is_lazer_not_silver"])
add(E, "https://www.ebay.com/itm/127990870487", "2025 Panini Prizm- Silver Prizm Auto- Tyler Shough #327 (RC)",
    L(TS, "2025", "Panini", "Prizm", "Rookie Autographs", "327", "Silver Prizm", is_auto=True),
    ("2025", "Panini Prizm", "Autograph-Silver Prizm", "327"), hazards=["auto_shares_base_card_no"])
add(E, "https://www.ebay.com/itm/366370329907", "Panini 2025 Prizm Tyler Shough #327 Rookie irl auto Prizm New Orleans Saints",
    L(TS, "2025", "Panini", "Prizm", "Base", "327", None, is_auto=False, exclusion_reason="aftermarket_auto"),
    ambiguous=True, why="'irl auto' = signed in person (not a pack-certified auto); parallel unstated ('Prizm' could mean Silver or base)",
    hazards=["aftermarket_auto", "bare_prizm_token"])
add(E, "https://www.ebay.com/itm/147198246354", "2025 Panini Prizm - Rookies Tyler Shough #327 (RC)",
    L(TS, "2025", "Panini", "Prizm", "Base", "327", "Base"), ("2025", "Panini Prizm", "Base", "327"))
add(E, "https://www.ebay.com/itm/178521798539", "TYLER SHOUGH PSA 9 2025 PANINI PRIZM #327 ROOKIE AUTO SILVER RC SAINTS 2017",
    L(TS, "2025", "Panini", "Prizm", "Rookie Autographs", "327", "Silver Prizm", is_auto=True, grader="PSA", grade=9.0),
    ("2025", "Panini Prizm", "Autograph-Silver Prizm", "327"), hazards=["stray_year_token:2017", "grade_before_year"])
add(E, "https://www.ebay.com/itm/298096921494", "2025 Panini Prizm Silver Tyler Shough RC Rookie Auto Saints",
    L(TS, "2025", "Panini", "Prizm", "Rookie Autographs", "327", "Silver Prizm", is_auto=True),
    ("2025", "Panini Prizm", "Autograph-Silver Prizm", "327"),
    hazards=["no_card_no_resolved_by_catalog:silver_auto_only_at_327"])
add(DS, "https://monmouthcards.com/products/2025-panini-prizm-tyler-shough-327-rookie-new-orleans-saints-cgc-9",
    "2025 Panini Prizm Tyler Shough #327 Rookie New Orleans Saints CGC 9",
    L(TS, "2025", "Panini", "Prizm", "Base", "327", "Base", grader="CGC", grade=9.0), ("2025", "Panini Prizm", "Base", "327"))
add(E, "https://www.ebay.com/itm/117377530645", "TYLER SHOUGH 2025 PANINI PRIZM SILVER LAZER PRIZM ROOKIE RC #327 CGC 10 GEM MINT",
    L(TS, "2025", "Panini", "Prizm", "Base", "327", "Lazer Prizm", grader="CGC", grade=10.0, grade_label="GEM MINT"),
    ("2025", "Panini Prizm", "Lazer Prizm", "327"), hazards=["near_miss:silver_lazer_is_lazer_not_silver", "cgc_gem_mint_vs_pristine"])
add(E, "https://www.ebay.com/itm/168296263388", "2025 Panini Prizm Tyler Shough Blue Wave /230 PSA 10",
    L(TS, "2025", "Panini", "Prizm", "Base", "327", "Blue Wave", print_run=230, grader="PSA", grade=10.0),
    ("2025", "Panini Prizm", "Blue Wave", "327"), hazards=["no_card_no_resolved_by_catalog:blue_wave_only_at_327"])
add(E, "https://www.ebay.com/itm/168370857189", "2025 Panini Prizm Tyler Shough Saints Blue Wave Rookie RC /230 PSA 10 GEM MINT",
    L(TS, "2025", "Panini", "Prizm", "Base", "327", "Blue Wave", print_run=230, grader="PSA", grade=10.0, grade_label="GEM MINT"),
    ("2025", "Panini Prizm", "Blue Wave", "327"), hazards=["no_card_no_resolved_by_catalog:blue_wave_only_at_327"])
add(E, "https://www.ebay.com/itm/147160885138", "2025 Prizm Football \"Rookie Varient Silver Prizm\"🔥HOT🔥",
    L(None, "2025", "Panini", "Prizm", "Rookie Variation", None, "Silver Prizm", exclusion_reason="player_unspecified"),
    hazards=["typo:varient", "no_player_name", "emoji"])
add(E, "https://www.ebay.com/itm/168238350073", "2025 PANINI PRIZM MANGA VERTICAL TYLER SHOUGH #11 ROOKIE RC SAINTS PSA 9 MINT",
    L(TS, "2025", "Panini", "Prizm", "Manga Vertical", "11", "Base", grader="PSA", grade=9.0, grade_label="MINT"),
    ("2025", "Panini Prizm Manga Vertical", "Base", "11"))
add(E, "https://www.ebay.com/itm/158289318644", "2025 TYLER SHOUGH Prizm Football MANGA VERTICAL Saints Rookie PSA 10🔥RC No. 11",
    L(TS, "2025", "Panini", "Prizm", "Manga Vertical", "11", "Base", grader="PSA", grade=10.0),
    ("2025", "Panini Prizm Manga Vertical", "Base", "11"), hazards=["card_no_format:No.", "emoji_glued_to_grade"])
add(E, "https://www.ebay.com/itm/306848152635", "Tyler Shough Manga Vertical 2025 Panini Prizm - #11 (RC) BGS9!!!!",
    L(TS, "2025", "Panini", "Prizm", "Manga Vertical", "11", "Base", grader="BGS", grade=9.0),
    ("2025", "Panini Prizm Manga Vertical", "Base", "11"), hazards=["grader_grade_no_space:BGS9"])
add(E, "https://www.ebay.com/itm/137625164329", "Lot of 5 2025 NFL Prizm Sparkle Packs Football Cam Ward Jaxson Dart Tyler Shough",
    L(["Cam Ward", "Jaxson Dart", TS], "2025", "Panini", "Prizm", None, None, None, is_rc=None, exclusion_reason="sealed_product_lot"),
    hazards=["lot", "sealed_packs", "multiple_player_names"])

# ---------------- 2025 Topps Chrome Tyler Shough ----------------
add(E, "https://www.ebay.com/itm/277903527269", "TYLER SHOUGH 2025 Topps Chrome #398 Football Leather Refractor Blue /150 RC",
    L(TS, "2025", "Topps", "Topps Chrome", "Base", "398", "Blue Football Leather", print_run=150),
    ("2025", "Topps Chrome", "Blue Football Leather", "398"), hazards=["color_after_parallel_name"])
add(E, "https://www.ebay.com/itm/127812261732", "2025 TOPPS CHROME FOOTBALL TYLER SHOUGH #398 PULSAR REFRACTOR RC",
    L(TS, "2025", "Topps", "Topps Chrome", "Base", "398", "Pulsar"), ("2025", "Topps Chrome", "Pulsar", "398"),
    hazards=["near_miss:pulsar_refractor_is_not_refractor"])
add(E, "https://www.ebay.com/itm/147262176171", "2025 Topps Chrome Football NFL Tyler Shough Refractor (RC) #398 Saints 🔥🔥🐸🐸",
    L(TS, "2025", "Topps", "Topps Chrome", "Base", "398", "Refractor"), ("2025", "Topps Chrome", "Refractor", "398"),
    hazards=["emoji"])
add(EC, "https://www.ebay.com/p/24093807191", "2025 Topps Chrome - Rookies Tyler Shough #398 RayWave Refractor (RC) for sale online",
    L(TS, "2025", "Topps", "Topps Chrome", "Base", "398", "Raywave"), ("2025", "Topps Chrome", "Raywave", "398"),
    hazards=["site_suffix:for sale online", "near_miss:raywave_refractor_is_not_refractor"])
add(E, "https://www.ebay.com/itm/389894402125", "2025 Topps Chrome Tyler Shough Rookie Refractor #398 RC",
    L(TS, "2025", "Topps", "Topps Chrome", "Base", "398", "Refractor"), ("2025", "Topps Chrome", "Refractor", "398"))
add(DS, "https://burbankcards.com/products/handle176511", "2025 Topps Chrome Rookie Pulsar Refractor #398 Tyler Shough RC",
    L(TS, "2025", "Topps", "Topps Chrome", "Base", "398", "Pulsar"), ("2025", "Topps Chrome", "Pulsar", "398"),
    hazards=["near_miss:pulsar_refractor_is_not_refractor"])
add(E, "https://www.ebay.com/itm/257753528046", "2025 Topps Chrome Tyler Shough RC Refractor Saints Rookie #398 PSA 9 Mint",
    L(TS, "2025", "Topps", "Topps Chrome", "Base", "398", "Refractor", grader="PSA", grade=9.0, grade_label="MINT"),
    ("2025", "Topps Chrome", "Refractor", "398"))
add(E, "https://www.ebay.com/itm/298639595371", "2025 TOPPS CHROME RED WHITE & BLUE REFRACTOR #398 TYLER SHOUGH ROOKIE RC PSA 9",
    L(TS, "2025", "Topps", "Topps Chrome", "Base", "398", "Red White and Blue Refractor", grader="PSA", grade=9.0),
    ("2025", "Topps Chrome", "Red White and Blue Refractor", "398"), hazards=["near_miss:rwb_refractor_is_not_refractor", "ampersand_vs_and"])

# ---------------- 2025 Optic / Donruss / other Shough ----------------
add(E, "https://www.ebay.com/itm/397654586992", "TYLER SHOUGH 2025 DONRUSS OPTIC RATED ROOKIE SILVER HOLO PRIZM RC #223 SAINTS",
    L(TS, "2025", "Panini", "Donruss Optic", "Rated Rookie", "223", "Holo"), ("2025", "Panini Donruss Optic", "Holo", "223"),
    hazards=["silver_means_holo_in_optic"])
add(E, "https://www.ebay.com/itm/177934930414", "2025 Panini Donruss Optic Tyler Shough (Rated Rookie) #223 SILVER HOLO MINT",
    L(TS, "2025", "Panini", "Donruss Optic", "Rated Rookie", "223", "Holo"), ("2025", "Panini Donruss Optic", "Holo", "223"),
    hazards=["silver_means_holo_in_optic", "raw_condition_word:MINT_without_grader"])
add(E, "https://www.ebay.com/itm/178026388711", "2025 Panini Donruss Optic Football - Tyler Shough #223 Rated Rookie (RC, Base)",
    L(TS, "2025", "Panini", "Donruss Optic", "Rated Rookie", "223", "Base"), ("2025", "Panini Donruss Optic", "Base", "223"))
add(E, "https://www.ebay.com/itm/317904653750", "2025 Panini Donruss Optic - Rated Rookie Tyler Shough #223 (RC)",
    L(TS, "2025", "Panini", "Donruss Optic", "Rated Rookie", "223", "Base"), ("2025", "Panini Donruss Optic", "Base", "223"))
add(E, "https://www.ebay.com/itm/127874359424", "2025 Panini Donruss Optic Tyler Shough #223 Rated Rookie Saints",
    L(TS, "2025", "Panini", "Donruss Optic", "Rated Rookie", "223", "Base"), ("2025", "Panini Donruss Optic", "Base", "223"))
add(E, "https://www.ebay.com/itm/177960203491", "2025 Donruss Tyler Shough Rated Rookie Optic RC Saints #223",
    L(TS, "2025", "Panini", "Donruss Optic", "Rated Rookie", "223", "Base"), ("2025", "Panini Donruss Optic", "Base", "223"),
    hazards=["product_tokens_split:Donruss...Optic", "card_no_disambiguates_optic_223_vs_donruss_304"])
add(E, "https://www.ebay.com/itm/117125881411", "Tyler Shough Rookie 2025 Panini Donruss Optic Rated Rookie #223 Saints",
    L(TS, "2025", "Panini", "Donruss Optic", "Rated Rookie", "223", "Base"), ("2025", "Panini Donruss Optic", "Base", "223"))
add(DS, "https://monmouthcards.com/products/2025-donruss-optic-holo-prizm-tyler-shough-223-psa-9",
    "2025 Donruss Optic Holo Prizm Tyler Shough #223 PSA 9",
    L(TS, "2025", "Panini", "Donruss Optic", "Rated Rookie", "223", "Holo", grader="PSA", grade=9.0),
    ("2025", "Panini Donruss Optic", "Holo", "223"))
add(FL, "https://www.fanaticscollect.com/weekly/7a622240-d9f9-11f0-8139-06a8e6f96a47/2025-donruss-optic-preview-red-green-prizm-tyler-shough-rookie-304-cgc-8-nm-mt",
    "2025 Donruss Optic Preview Red & Green Prizm Tyler Shough ROOKIE #304 CGC 8 NM-MT",
    L(TS, "2025", "Panini", "Donruss", "Optic Preview", "304", "Red & Green", grader="CGC", grade=8.0, grade_label="NM-MT"),
    ("2025", "Panini Donruss", "Optic Preview-Red & Green", "304"),
    hazards=["optic_preview_is_donruss_product_not_optic"], sold=True, price=12, date="2025-12-22")
add(E, "https://www.ebay.com/itm/267788369054", "2025 Panini Mosaic Tyler Shough RC Variation Blue Reactive Prizm Saints SGC 10",
    L(TS, "2025", "Panini", "Mosaic", "Rookie Variation", None, "Reactive Blue", grader="SGC", grade=10.0),
    ambiguous=True, why="Mosaic Reactive Blue exists at #273 and #312 in GemRate; title has no card number",
    hazards=["missing_card_no_multi_candidate", "word_order:Blue Reactive vs Reactive Blue"])
add(E, "https://www.ebay.com/itm/377520623358", "2025 Panini Mosaic Reactive Purple Prizm #273 Tyler Shough RC Rookie BGS 7.5",
    L(TS, "2025", "Panini", "Mosaic", "Base", "273", "Reactive Purple", grader="BGS", grade=7.5),
    ("2025", "Panini Mosaic", "Reactive Purple", "273"))
add(E, "https://www.ebay.com/itm/318876157613", "2025 Panini Mosaic Tyler Shough Rookie Prizm Autograph #312 - Saints PSA 9",
    L(TS, "2025", "Panini", "Mosaic", "Rookie Autographs", "312", "Base", is_auto=True, grader="PSA", grade=9.0),
    ("2025", "Panini Mosaic", "Autograph", "312"), hazards=["bare_prizm_token_in_mosaic"])
add(E, "https://www.ebay.com/itm/227314197387", "2025 Panini Mosaic - Light It Up Mosaic Tyler Shough #9 Silver Prizm (RC) PSA 10",
    L(TS, "2025", "Panini", "Mosaic", "Light It Up", "9", "Silver", grader="PSA", grade=10.0),
    ("2025", "Panini Mosaic Light It Up", "Silver", "9"), hazards=["silver_in_non_prizm_product", "mosaic_as_product_and_parallel"])
add(FS, "https://www.fanaticscollect.com/buy-now/8fb9f0cc-24fe-416a-8951-55d8df7cee8c", "2025 panini select #141 tyler shough zebra shock psa 10",
    L(TS, "2025", "Panini", "Select", "Base", "141", "Zebra Shock", grader="PSA", grade=10.0),
    ("2025", "Panini Select", "Zebra Shock", "141"), hazards=["all_lowercase", "select_tier_numbers:41/141/341/441"])
add(FS, "https://www.fanaticscollect.com/weekly/5f5cac3e-ccae-11f0-9652-0a58a9feac02/2025-donruss-downtown-tyler-shough-rookie-19-cgc-10-gem-mint",
    "2025 Donruss Downtown Tyler Shough ROOKIE #19 CGC 10 GEM MINT on Fanatics Collect",
    L(TS, "2025", "Panini", "Donruss", "Downtown", "19", "Base", grader="CGC", grade=10.0, grade_label="GEM MINT"),
    ("2025", "Panini Donruss Downtown", "Base", "19"), hazards=["site_suffix:on Fanatics Collect", "donruss_vs_optic_downtown"])
add(FS, "https://www.fanaticscollect.com/weekly/ad71fc9a-9b20-11f0-8a8d-0a58a9feac02/2025-panini-the-national-color-blast-tyler-shough-rookie-125-ts-cgc-auth",
    "2025 Panini The National Color Blast Tyler Shough ROOKIE 1/25 #TS CGC AUTH on Fanatics Collect",
    L(TS, "2025", "Panini", "National Sports Collectors Convention", "Color Blast", "TS", "Base", serial_no="1/25", print_run=25,
      grader="CGC", grade=None, grade_label="Authentic"),
    ambiguous=True, why="'1/25' could be serial 1 of 25 or a 1-of-25 print run; GemRate set name for this release unclear",
    hazards=["serial_without_hash", "cgc_auth_no_numeric_grade"])
add(FS, "https://www.fanaticscollect.com/buy-now/55170c42-b4d5-4b97-9751-bba7c29abedc/2025-immaculate-collection-premium-emerald-tyler-shough-rookie-patch-auto-25-cgc-auth",
    "2025 Immaculate Collection Premium Emerald Tyler Shough ROOKIE PATCH AUTO /25 CGC AUTH on Fanatics Collect",
    L(TS, "2025", "Panini", "Immaculate Collection", "Premium Patch Rookie Autographs", None, "Emerald", print_run=25, is_auto=True,
      grader="CGC", grade_label="Authentic"), ambiguous=True, why="no card number; Immaculate has several Shough patch-auto subsets",
    hazards=["cgc_auth_no_numeric_grade", "missing_card_no_multi_candidate"])
add(FS, "https://www.fanaticscollect.com/weekly/44842aa6-db8e-11f0-9519-060c140c1bf5/2025-donruss-gridiron-kings-tyler-shough-rookie-rgk-tsh-cgc-auth",
    "2025 Donruss Gridiron Kings Tyler Shough ROOKIE #RGK-TSH CGC AUTH on Fanatics Collect",
    L(TS, "2025", "Panini", "Donruss", "Rookie Gridiron Kings", "RGK-TSH", "Base", grader="CGC", grade_label="Authentic"),
    hazards=["alnum_card_no", "cgc_auth_no_numeric_grade"])
add(FS, "https://www.fanaticscollect.com/weekly/df4b5890-e6db-11f0-b20a-021a2a98ad37/2025-panini-mosaic-stained-glass-oversized-tyler-shough-rookie-18-cgc-auth",
    "2025 Panini Mosaic Stained Glass Oversized Tyler Shough ROOKIE #18 CGC AUTH on Fanatics Collect",
    L(TS, "2025", "Panini", "Mosaic", "Stained Glass Oversized", "18", "Base", grader="CGC", grade_label="Authentic"),
    hazards=["oversized_is_distinct_card_from_standard_#18"])
add(FS, "https://www.fanaticscollect.com/weekly/2de38c08-d619-11f0-a124-0a58a9feac02/2025-donruss-oversized-downtown-tyler-shough-rookie-19-cgc-auth",
    "2025 Donruss Oversized Downtown Tyler Shough ROOKIE #19 CGC AUTH on Fanatics Collect",
    L(TS, "2025", "Panini", "Donruss", "Downtown", "19", "Oversize", grader="CGC", grade_label="Authentic"),
    ("2025", "Panini Donruss Downtown", "Oversize", "19"), hazards=["oversized_is_distinct_card_from_standard_#19"])
add(FS, "https://www.fanaticscollect.com/buy-now/824c37de-3493-4103-bb91-ed371239db35/2025-panini-origins-tyler-shough-rookie-117-cgc-auth",
    "2025 Panini Origins Tyler Shough ROOKIE #117 CGC AUTH on Fanatics Collect",
    L(TS, "2025", "Panini", "Origins", "Base", "117", "Base", grader="CGC", grade_label="Authentic"),
    ("2025", "Panini Origins", "Base", "117"))
add(FS, "https://www.fanaticscollect.com/buy-now/25881155-68c6-412a-90aa-95bd1d250d13/2025-absolute-rookie-wave-19-tyler-shough",
    "2025 Absolute Rookie Wave #19 Tyler Shough on Fanatics Collect",
    L(TS, "2025", "Panini", "Absolute", "Rookie Wave", "19", "Base"), ambiguous=True,
    why="GemRate numbers this card RW-TSH; title uses #19 -> card_no conflicts with catalog",
    hazards=["card_no_conflicts_with_catalog"])
add(E, "https://www.ebay.com/itm/306987269625", "2025 Topps Signature Class Tyler Shough Rookie Auto #126/275 #104 Saints RC",
    L(TS, "2025", "Topps", "Signature Class", "Rookie Autographs", "104", "Base", print_run=275, serial_no="126/275", is_auto=True),
    hazards=["serial_with_hash_looks_like_card_no", "two_hash_tokens"])
add(E, "https://www.ebay.com/itm/397721575714", "2025 Panini Phoenix Tyler Shough Rookie Silver Seismic Prizm Auto /99 Saints",
    L(TS, "2025", "Panini", "Phoenix", "Rookie Autographs", None, "Silver Seismic", print_run=99, is_auto=True), ambiguous=True,
    why="GemRate lists Phoenix 'Autograph-Seismic' #169 but no 'Autograph-Silver Seismic'; card/subset unresolved",
    hazards=["near_miss:silver_seismic_is_not_silver_prizm", "missing_card_no"])
add(E, "https://www.ebay.com/itm/147181309159", "2025 National Treasures Tyler Shough Rookie Patch Auto RC /99 Saints CRPA-TSH",
    L(TS, "2025", "Panini", "National Treasures", "Crossover Rookie Patch Autographs", "CRPA-TSH", "Base", print_run=99, is_auto=True),
    hazards=["card_no_without_hash"])
add(E, "https://www.ebay.com/itm/358301982765", "2025 Panini Immaculate Tyler Shough Rookie Auto RPA /99 Signature Patches Saints",
    L(TS, "2025", "Panini", "Immaculate Collection", "Immaculate Signature Patches Rookie", None, "Base", print_run=99, is_auto=True),
    hazards=["missing_card_no"])
add(E, "https://www.ebay.com/itm/177990093338", "2025 National Treasures Tyler Shough Rookie Patch Auto /49 • RC Saints",
    L(TS, "2025", "Panini", "National Treasures", None, None, None, print_run=49, is_auto=True), ambiguous=True,
    why="NT has several RPA subsets and /49 parallels; no card number or subset name", hazards=["missing_card_no_multi_candidate", "bullet_char"])
add(E, "https://www.ebay.com/itm/227535677848", "2025 TOPPS RESURGENCE TYLER SHOUGH RADIAL ROOKIE AUTO BLUE RPA PATCH /125",
    L(TS, "2025", "Topps", "Resurgence", "Radial Rookie Autographs", None, "Blue", print_run=125, is_auto=True),
    hazards=["missing_card_no"])
add(E, "https://www.ebay.com/itm/168659644913", "2025 Topps Resurgence Tyler Shough Patch Auto /125 RC Saints",
    L(TS, "2025", "Topps", "Resurgence", None, None, None, print_run=125, is_auto=True), ambiguous=True,
    why="color/subset not stated (likely Blue Radial per sibling listing, but do not infer)", hazards=["missing_parallel"])
add(E, "https://www.ebay.com/itm/168679119631", "2025 Panini Phoenix - Tyler Shough Rookie Patch Auto RPA Bronze Pandora /199",
    L(TS, "2025", "Panini", "Phoenix", "RPS Rookie Patch Autographs", None, "Bronze Pandora", print_run=199, is_auto=True),
    hazards=["missing_card_no"])
add(E, "https://www.ebay.com/itm/157667277363", "2025 Panini Immaculate - Tyler Shough / Rookie Patch Auto /99 - No. 105 TRUE RPA",
    L(TS, "2025", "Panini", "Immaculate Collection", "Rookie Patch Autographs", "105", "Base", print_run=99, is_auto=True),
    hazards=["card_no_format:No.", "slash_separator_not_print_run"])
add(E, "https://www.ebay.com/itm/277645698176", "2025 Phoenix Football Tyler Shough Auto Jumbo Patch RPA /199 Chrome Saints MINT",
    L(TS, "2025", "Panini", "Phoenix", None, None, None, print_run=199, is_auto=True), ambiguous=True,
    why="'Chrome' is descriptive, not a Topps product; subset/parallel unclear", hazards=["chrome_word_in_panini_title", "raw_condition_word:MINT_without_grader"])
add(E, "https://www.ebay.com/itm/327043105355", "2025 Panini Flawless True RPA 2/25 Tyler Shough Saints Rookie Patch Auto 📈💎",
    L(TS, "2025", "Panini", "Flawless", "Rookie Patch Autographs", None, None, print_run=25, serial_no="2/25", is_auto=True),
    hazards=["serial_without_hash", "emoji"])

# ---------------- 2023 Prizm Michael Wilson (#303) ----------------
add(E, "https://www.ebay.com/itm/167960424805", "Michael Wilson 2023 Panini Prizm Rookie RC Silver Prizm AUTO Autographed #303",
    L(MW, "2023", "Panini", "Prizm", "Rookie Autographs", "303", "Silver Prizm", is_auto=True), hazards=["auto_shares_base_card_no"])
add(E, "https://www.ebay.com/itm/147141847543", "Michael Wilson 2023 Panini Prizm NFL Silver Prizm Auto Autograph Rookie RC NRMT+",
    L(MW, "2023", "Panini", "Prizm", "Rookie Autographs", "303", "Silver Prizm", is_auto=True),
    hazards=["raw_condition_word:NRMT+_without_grader", "no_card_no_resolved_by_catalog"])
add(E, "https://ebay.com/itm/395791723639", "2023 Panini Prizm - Rookies Michael Wilson #303 Silver Prizm Autographs (AU, RC) for sale online",
    L(MW, "2023", "Panini", "Prizm", "Rookie Autographs", "303", "Silver Prizm", is_auto=True), hazards=["site_suffix:for sale online", "AU_token"])
add(E, "https://www.ebay.com/itm/137320160379", "2023 Panini Prizm - Rookies Michael Wilson #303 Neon Green Pulsar Prizm (RC)",
    L(MW, "2023", "Panini", "Prizm", "Base", "303", "Neon Green Pulsar Prizm"))
add(E, "https://www.ebay.com/itm/405720466265", "Michael Wilson 2023 Panini Prizm Base Rookie RC #303 Arizona Cardinals NFL",
    L(MW, "2023", "Panini", "Prizm", "Base", "303", "Base"))
add(E, "https://www.ebay.com/itm/128028978908", "Michael Wilson Rookie RC 2023 Prizm Football Card #303 Arizona Cardinals",
    L(MW, "2023", "Panini", "Prizm", "Base", "303", "Base"), hazards=["no_parallel_token_defaults_base"])
add(E, "https://www.ebay.com/itm/404779147717", "2023 Wildcard Mania Michael Wilson RC AUTO 4/4 Cardinals",
    L(MW, "2023", "Wild Card", "Wild Card Mania", None, None, None, print_run=4, serial_no="4/4", is_auto=True, is_rc=None),
    hazards=["unlicensed_pre_nfl_product", "RC_claim_on_unlicensed", "serial_without_hash"])
add(E, "https://www.ebay.com/itm/286104866550", "2023 Panini Prizm #303 Michael Wilson Purple Prizm /125 Cardinals RC PSA 10",
    L(MW, "2023", "Panini", "Prizm", "Base", "303", "Purple Prizm", print_run=125, grader="PSA", grade=10.0))
add(E, "https://www.ebay.com/itm/336484739573", "Panini 2023 Prizm Michael Wilson #303 Gold No Huddle Auto /10 Rookie PSA 10",
    L(MW, "2023", "Panini", "Prizm", "Rookie Autographs", "303", "No Huddle Gold", print_run=10, is_auto=True, grader="PSA", grade=10.0),
    hazards=["word_order:Gold No Huddle vs No Huddle Gold", "auto_grade_unstated"])
add(E, "https://www.ebay.com/itm/136924464311", "2023 Panini Prizm - Rookies Michael Wilson #303 Snake Skin Prizm (RC) for sale online",
    L(MW, "2023", "Panini", "Prizm", "Base", "303", "Snakeskin Prizm"), hazards=["site_suffix:for sale online", "spacing:Snake Skin vs Snakeskin"])
add(E, "https://www.ebay.com/itm/235385461937", "2023 Panini Prizm Football Michael Wilson #303 Green Pulsar Prizm Rookie RC...",
    L(MW, "2023", "Panini", "Prizm", "Base", "303", None), ambiguous=True,
    why="'Green Pulsar' vs 'Neon Green Pulsar' (both names in use); title truncated by search engine",
    hazards=["truncated_title", "color_prefix_dropped"])
add(E, "https://www.ebay.com/itm/277784159664", "2023 Panini Prizm Michael Wilson Gold Auto /10 Rookie RC Cardinals PSA 9 Mint",
    L(MW, "2023", "Panini", "Prizm", None, None, None, print_run=10, is_auto=True, grader="PSA", grade=9.0, grade_label="MINT"),
    ambiguous=True, why="'Gold Auto /10' could be Rookie Autographs Gold Prizm or No Huddle Gold (both /10); no card number",
    hazards=["missing_card_no_multi_candidate"])
add(E, "https://www.ebay.com/itm/405400088044", "2023 Panini Prizm Draft Picks Michael Wilson Rookie Stanford Cardinal #147",
    L(MW, "2023", "Panini", "Prizm Draft Picks", "Base", "147", "Base", is_rc=False),
    hazards=["draft_picks_is_separate_college_product", "Cardinal(Stanford)_vs_Cardinals", "rookie_word_on_non_RC"])
add(E, "https://www.ebay.com/itm/145342456376", "Michael Wilson rookie auto 2023 Panini Prizm Draft Picks Stanford AZ Cardinals",
    L(MW, "2023", "Panini", "Prizm Draft Picks", "Draft Picks Autographs", "DPA-MWI", "Base", is_auto=True, is_rc=False),
    hazards=["draft_picks_is_separate_college_product", "no_card_no_resolved_by_catalog"])
add(E, "https://www.ebay.com/itm/167626558212", "🔥2023 Panini Prizm Draft Picks Michael Wilson #DPA-MWI Rookie Auto Cardinals🔥",
    L(MW, "2023", "Panini", "Prizm Draft Picks", "Draft Picks Autographs", "DPA-MWI", "Base", is_auto=True, is_rc=False),
    hazards=["emoji_glued_to_year", "alnum_card_no"])
add(E, "https://www.ebay.com/itm/335404625952", "2023 Prizm Draft Picks Michael Wilson football Rookie card #147 Stanford",
    L(MW, "2023", "Panini", "Prizm Draft Picks", "Base", "147", "Base", is_rc=False))
add(E, "https://www.ebay.com/itm/317632431512", "2023 Panini Prizm Draft Picks - Draft Picks Autographs Michael Wilson #DPA-MWI (AU, RC) for sale online",
    L(MW, "2023", "Panini", "Prizm Draft Picks", "Draft Picks Autographs", "DPA-MWI", "Base", is_auto=True, is_rc=False),
    hazards=["site_suffix:for sale online", "catalog_RC_flag_on_college_card"])
add(DS, "https://www.amazon.com/Panini-Michael-Cardinals-Football-Trading/dp/B0CVG5LXLL",
    "2023 Panini Prizm Prizm Green #303 Michael Wilson RC Rookie Cardinals NFL Football Trading Card : Everything Else",
    L(MW, "2023", "Panini", "Prizm", "Base", "303", "Green Prizm"), hazards=["doubled_token:Prizm Prizm", "site_suffix:Everything Else"])

# ---------------- Other players: grade/grader/qualifier/parallel patterns ----------------
add(E, "https://www.ebay.com/itm/297365732109", "2023 PANINI PRIZM SILVER PRIZM #343 ANTHONY RICHARDSON PSA 8",
    L("Anthony Richardson", "2023", "Panini", "Prizm", "Base", "343", "Silver Prizm", grader="PSA", grade=8.0))
add(E, "https://www.ebay.com/itm/267699586312", "2023 Panini Prizm Will Levis #397 Silver Rookie PSA 9",
    L("Will Levis", "2023", "Panini", "Prizm", "Base", "397", "Silver Prizm", grader="PSA", grade=9.0))
add(DS, "https://www.greatamericansportscards.com/products/2023-prizm-cj-stroud-silver-rookie-variation-psa-9-oc",
    "2023 Prizm CJ Stroud Silver Rookie Variation PSA 9 (OC)",
    L("C.J. Stroud", "2023", "Panini", "Prizm", "Rookie Variation", None, "Silver Prizm", grader="PSA", grade=9.0, qualifier="OC"),
    hazards=["psa_qualifier_parenthesized", "variation_card_no_missing_but_unique"])
add(E, "https://www.ebay.com/itm/136437050751", "2024 Panini Prizm - Michael Penix Jr. #378 Silver Prizm ROOKIE PSA 8",
    L("Michael Penix Jr.", "2024", "Panini", "Prizm", "Base", "378", "Silver Prizm", grader="PSA", grade=8.0), hazards=["name_suffix:Jr."])
add(FS, "https://www.fanaticscollect.com/weekly/33eea994-6b1a-11f0-a039-0abfa49f70c7/2024-panini-prizm-silver-michael-penix-jr-rookie-378-psa-9-mint",
    "2024 Panini Prizm Silver Michael Penix Jr. ROOKIE #378 PSA 9 MINT on Fanatics Collect",
    L("Michael Penix Jr.", "2024", "Panini", "Prizm", "Base", "378", "Silver Prizm", grader="PSA", grade=9.0, grade_label="MINT"),
    hazards=["site_suffix:on Fanatics Collect", "player_first_name_collision:Michael"])
add(FS, "https://www.fanaticscollect.com/buy-now/c3c3db0a-118c-4ea8-8496-6abf3a8dd6dc/2023-prizm-jahmyr-gibbs-rookie-silver-331-psa-9-112",
    "2023 Prizm Jahmyr Gibbs Rookie Silver #331 PSA 9 112",
    L("Jahmyr Gibbs", "2023", "Panini", "Prizm", "Base", "331", "Silver Prizm", grader="PSA", grade=9.0),
    hazards=["trailing_number_after_grade:112"])
add(E, "https://www.ebay.com/itm/176637825373", "2020 Joe Burrow Prizm Silver PSA 10 GEM #307 Panini RC NFL Rookie",
    L("Joe Burrow", "2020", "Panini", "Prizm", "Base", "307", "Silver Prizm", grader="PSA", grade=10.0, grade_label="GEM MINT"),
    hazards=["grade_label_abbrev:GEM", "card_no_after_grade"])
add(E, "https://www.ebay.com/itm/177182907628", "2024 Prizm - JAYDEN DANIELS - Fireworks Silver Prizm - PSA 10",
    L("Jayden Daniels", "2024", "Panini", "Prizm", "Fireworks", None, "Silver Prizm", grader="PSA", grade=10.0),
    hazards=["near_miss:insert_silver_vs_base_silver", "missing_card_no"])
add(FL, "https://www.fanaticscollect.com/weekly/70a4be4a-19fe-11f0-aae2-0a58a9feac02/2024-panini-prizm-no-huddle-jayden-daniels-rookie-17-bgs-10-pristine",
    "2024 Panini Prizm No Huddle Jayden Daniels ROOKIE #17 BGS 10 PRISTINE",
    L("Jayden Daniels", "2024", "Panini", "Prizm No Huddle", "Base", "17", "Base", grader="BGS", grade=10.0, grade_label="Pristine"),
    ambiguous=True, why="'No Huddle' is both a Prizm parallel name and a standalone product; #17 (not base #347) implies the standalone product",
    hazards=["no_huddle_product_vs_parallel", "bgs_pristine_vs_black_label"], sold=True, price=564, date="2025-04-28")
add(FL, "https://www.fanaticscollect.com/weekly/faa6f1b0-3aa8-11f0-8cad-02c1a2a55fd5/2024-panini-prizm-lazer-jj-mccarthy-rookie-400-cgc-auth",
    "2024 Panini Prizm Lazer Marvin Harrison Jr. ROOKIE #375 SGC 10 GEM MINT",
    L("Marvin Harrison Jr.", "2024", "Panini", "Prizm", "Base", "375", "Lazer Prizm", grader="SGC", grade=10.0, grade_label="GEM MINT"),
    hazards=["url_slug_disagrees_with_title(slug=JJ McCarthy CGC AUTH)", "sgc_gem_mint_vs_pristine"], sold=True, price=31.20, date="2025-06-23")
add(FL, "https://www.fanaticscollect.com/premier/8b5b2d0a-f94b-11f0-b27c-02723737d1b7/2023-panini-prizm-silver-victor-wembanyama-rookie-136-bgs-10-pristine-black-label",
    "2023 Panini Prizm Silver Victor Wembanyama ROOKIE #136 BGS 10 PRISTINE, BLACK LABEL",
    L("Victor Wembanyama", "2023-24", "Panini", "Prizm", "Base", "136", "Silver Prizm", grader="BGS", grade=10.0, grade_label="Black Label",
      subgrades={"centering": 10, "corners": 10, "edges": 10, "surface": 10}),
    hazards=["black_label_vs_pristine", "basketball_single_year_for_season_set"], sold=True, price=19800, date="2026-02-20")
add(FL, "https://www.fanaticscollect.com/fixed/515fe6f0-0fef-11ef-8e47-0a58a9feac02",
    "2023 Panini Prizm Draft Picks Tyrique Stevenson ROOKIE #195 CGC 10 PRISTINE",
    L("Tyrique Stevenson", "2023", "Panini", "Prizm Draft Picks", "Base", "195", "Base", is_rc=False, grader="CGC", grade=10.0, grade_label="Pristine"),
    hazards=["cgc_pristine_vs_gem_mint", "rookie_word_on_non_RC"], sold=True, price=34, date="2024-08-08")
add(FS, "https://www.fanaticscollect.com/fixed/4f18d84e-eafe-11ef-8751-0ae9a1b6d63f/2020-panini-prizm-silver-cole-anthony-rookie-292-sgc-10-gem-mint",
    "2020 Panini Prizm Silver Cole Anthony ROOKIE #292 SGC 10 GEM MINT on Fanatics Collect",
    L("Cole Anthony", "2020-21", "Panini", "Prizm", "Base", "292", "Silver Prizm", grader="SGC", grade=10.0, grade_label="GEM MINT"),
    hazards=["basketball_single_year_for_season_set"])
add(FS, "https://www.fanaticscollect.com/buy-now/eaab08bd-7591-44ab-b0ce-f0b4d9ad0259/2015-panini-prizm-silver-stefon-diggs-rookie-285-cgc-10-gem-mint",
    "2015 Panini Prizm Silver Stefon Diggs ROOKIE #285 CGC 10 GEM MINT on Fanatics Collect",
    L("Stefon Diggs", "2015", "Panini", "Prizm", "Base", "285", "Silver Prizm", grader="CGC", grade=10.0, grade_label="GEM MINT"))
add(FS, "https://www.fanaticscollect.com/fixed/dc390bae-a25b-11ef-9ba4-0a58a9feac02",
    "2020 Panini Prizm Silver LaMelo Ball ROOKIE #278 SGC 9.5 MINT+ on Fanatics Collect",
    L("LaMelo Ball", "2020-21", "Panini", "Prizm", "Base", "278", "Silver Prizm", grader="SGC", grade=9.5, grade_label="MINT+"))
add(FS, "https://www.fanaticscollect.com/fixed/1be77f4a-3809-11f0-93e0-06c888132649/2024-panini-prizm-silver-jj-mccarthy-rookie-400-psa-10-gem-mint",
    "2024 Panini Prizm Silver J.J. McCarthy ROOKIE #400 SGC 9.5 MINT+ on Fanatics Collect",
    L("J.J. McCarthy", "2024", "Panini", "Prizm", "Base", "400", "Silver Prizm", grader="SGC", grade=9.5, grade_label="MINT+"),
    ambiguous=True, why="search title says SGC 9.5; URL slug says PSA 10 GEM MINT; page no longer renders -> grade unverifiable",
    hazards=["url_slug_disagrees_with_title", "listing_page_recycled"])
add(FS, "https://www.fanaticscollect.com/fixed/122a1912-14b5-11f0-9fd5-0a58a9feac02/2024-panini-instant-jayden-daniels-rookie-170-sgc-10-gem-mint",
    "2024 Panini Prizm Green Wave Jayden Daniels ROOKIE #347 PSA 10 GEM MINT on Fanatics Collect",
    L("Jayden Daniels", "2024", "Panini", "Prizm", "Base", "347", "Green Wave", grader="PSA", grade=10.0, grade_label="GEM MINT"),
    ambiguous=True, why="URL slug describes a different card (2024 Instant #170 SGC 10); title/slug mismatch",
    hazards=["url_slug_disagrees_with_title", "listing_page_recycled"])
add(FS, "https://www.fanaticscollect.com/premier/40ed8d06-56f5-11f0-84c9-022ff6a22105/2024-panini-prizm-gold-jayden-daniels-rookie-10-347-psa-9-mint",
    "2024 Panini Prizm Gold Jayden Daniels ROOKIE /10 #347 PSA 9 MINT on Fanatics Collect",
    L("Jayden Daniels", "2024", "Panini", "Prizm", "Base", "347", "Gold Prizm", print_run=10, grader="PSA", grade=9.0, grade_label="MINT"),
    hazards=["print_run_before_card_no"])
add(FS, "https://www.fanaticscollect.com/premier/a84dfb0e-6fcb-11f0-8c7b-0a58a9feac02/2024-panini-prizm-gold-bo-nix-rookie-10-309-psa-8-nm-mt",
    "2024 Panini Prizm Gold Bo Nix ROOKIE /10 #309 PSA 8 NM-MT on Fanatics Collect",
    L("Bo Nix", "2024", "Panini", "Prizm", "Base", "309", "Gold Prizm", print_run=10, grader="PSA", grade=8.0, grade_label="NM-MT"),
    hazards=["print_run_before_card_no"])
add(FS, "https://www.fanaticscollect.com/premier/f101826a-cb31-11ef-92a9-0a58a9feac02/2017-panini-prizm-patrick-mahomes-ii-rookie-auto-ra-pm-sgc-10-gem-mint",
    "2017 Panini Prizm Patrick Mahomes II ROOKIE AUTO #RA-PM SGC 10 GEM MINT on Fanatics Collect",
    L("Patrick Mahomes II", "2017", "Panini", "Prizm", "Rookie Autographs", "RA-PM", "Base", is_auto=True, grader="SGC", grade=10.0, grade_label="GEM MINT"),
    hazards=["name_suffix:II"])
add(FS, "https://www.fanaticscollect.com/fixed/01754a00-68a4-11ef-be03-02a18dc87d5b/2022-panini-prizm-draft-picks-silver-ej-liddell-rookie-74-cgc-10-gem-mint",
    "2022 Panini Prizm Draft Picks Silver E.J. Liddell ROOKIE #74 CGC 10 GEM MINT on Fanatics Collect",
    L("E.J. Liddell", "2022-23", "Panini", "Prizm Draft Picks", "Base", "74", "Silver Prizm", is_rc=False, grader="CGC", grade=10.0, grade_label="GEM MINT"))
add(FS, "https://www.fanaticscollect.com/weekly/f922ec9a-95ee-11ef-b718-0a58a9feac02/2020-select-certified-prizm-justin-jefferson-rookie-scr-9-psa-10-gem-mint",
    "2020 Select Certified Prizm Justin Jefferson ROOKIE #SCR-9 PSA 10 GEM MINT on Fanatics Collect",
    L("Justin Jefferson", "2020", "Panini", "Select", "Select Certified Rookies", "SCR-9", "Base", grader="PSA", grade=10.0, grade_label="GEM MINT"),
    ambiguous=True, why="bare 'Prizm' after an insert name in Select: base insert vs Silver Prizm parallel unclear",
    hazards=["bare_prizm_token", "prizm_word_in_non_prizm_product"])
add(FS, "https://www.fanaticscollect.com/weekly/aa2043cc-c4c8-11f0-8dac-0a58a9feac02/2019-panini-prizm-tyler-herro-rookie-259-psa-10-gem-mint",
    "2019 Panini Prizm Tyler Herro ROOKIE #259 PSA 10 GEM MINT on Fanatics Collect",
    L("Tyler Herro", "2019-20", "Panini", "Prizm", "Base", "259", "Base", grader="PSA", grade=10.0, grade_label="GEM MINT"),
    hazards=["player_first_name_collision:Tyler"])
add(FS, "https://www.fanaticscollect.com/buy-now/5262fb75-2716-48ef-b0c5-10793785432f/2019-panini-prizm-choice-tiger-stripe-prizms-tyler-herro-rookie-259-psa-9-mint",
    "2019 Panini Prizm Choice Tiger Stripe Prizms Tyler Herro ROOKIE #259 PSA 9 MINT on Fanatics Collect",
    L("Tyler Herro", "2019-20", "Panini", "Prizm", "Base", "259", "Choice Tiger Stripe Prizm", grader="PSA", grade=9.0, grade_label="MINT"),
    hazards=["plural_parallel:Prizms"])
add(FS, "https://www.fanaticscollect.com/buy-now/abe04835-c119-4925-828b-a68d0ac55194", "2016 Panini Prizm Mosaic LeBron James #64 PSA 9 MINT",
    L("LeBron James", "2016-17", "Panini", "Prizm", "Base", "64", "Mosaic Prizm", is_rc=False, grader="PSA", grade=9.0, grade_label="MINT"),
    hazards=["mosaic_as_product_and_parallel"])
add(E, "https://www.ebay.com/itm/165525767473", "2017-18 Panini Prizm Jayson Tatum Rookie Card BGS 9.5 GEM MINT 🔥🔥🔥",
    L("Jayson Tatum", "2017-18", "Panini", "Prizm", "Base", "16", "Base", grader="BGS", grade=9.5, grade_label="GEM MINT"),
    hazards=["season_year_format", "no_card_no_resolved_by_catalog", "subgrades_absent"])
add(E, "https://www.ebay.com/itm/265114885671", "2012-13 Panini Prizm Andre Drummond BGS 9.5 True Gem+ Rookie RC",
    L("Andre Drummond", "2012-13", "Panini", "Prizm", "Base", None, "Base", grader="BGS", grade=9.5, grade_label="GEM MINT"),
    hazards=["seller_lingo:True Gem+ (subgrades all >=9.5, not a grader label)", "missing_card_no"])
add(DS, "https://www.walmart.com/ip/Ben-Simmons-Rookie-Card-2016-17-Panini-Prizm-1-BGS-9-5-9-5-9-5-9-5-9/5318211872",
    "Ben Simmons Rookie Card 2016-17 Panini Prizm #1 BGS 9.5 (9.5 9.5 9.5 9) - Walmart.com",
    L("Ben Simmons", "2016-17", "Panini", "Prizm", "Base", "1", "Base", grader="BGS", grade=9.5, subgrades={"unordered": [9.5, 9.5, 9.5, 9.0]}),
    hazards=["subgrades_space_separated_unlabeled", "site_suffix:Walmart.com"])
add(DS, "https://www.walmart.com/ip/Doug-Martin-SILVER-PRIZM-ROOKIE-CARD-BGS-9-5-Gem-Mint-RC-2012-Panini-Prizm-BUCS/13671308459",
    "Doug Martin SILVER PRIZM ROOKIE CARD BGS 9.5 Gem Mint RC 2012 Panini Prizm BUCS - Walmart.com",
    L("Doug Martin", "2012", "Panini", "Prizm", "Base", None, "Silver Prizm", grader="BGS", grade=9.5, grade_label="GEM MINT"),
    hazards=["year_after_grade", "missing_card_no"])
add(DS, "https://cardboardpicasso.com/2019-panini-prizm-ja-morant-rookie-rc-249-bgs-9-5-gem-mint-w-10-sub/",
    "2019 PANINI PRIZM JA MORANT ROOKIE RC #249 BGS 9.5 GEM MINT w/10 sub - Cardboard Picasso",
    L("Ja Morant", "2019-20", "Panini", "Prizm", "Base", "249", "Base", grader="BGS", grade=9.5, grade_label="GEM MINT", subgrades={"partial": "one 10"}),
    hazards=["partial_subgrade_phrase:w/10 sub"])
add(E, "https://www.ebay.com/itm/115120743721", "Giannis antetokounmpo Prizm Rookie SGC 10 🔥",
    L("Giannis Antetokounmpo", None, "Panini", "Prizm", "Base", None, "Base", grader="SGC", grade=10.0), ambiguous=True,
    why="no year; no parallel", hazards=["missing_year", "missing_card_no"])
add(E, "https://www.ebay.com/itm/256979012966", "2023 Select Anniversary Silver Prizm Rookie C.J. Stroud SGC 9.5 GS1",
    L("C.J. Stroud", "2023", "Panini", "Select", "Anniversary", None, "Silver Prizm", grader="SGC", grade=9.5),
    hazards=["unknown_trailing_token:GS1", "missing_card_no"])
add(E, "https://www.ebay.com/itm/364844071117", "O-Max Prosper 2023-24 Prizm #RSI-OMP Rookie Signatures Silver Prizm RC SGC 10/10",
    L("O-Max Prosper", "2023-24", "Panini", "Prizm", "Rookie Signatures", "RSI-OMP", "Silver Prizm", is_auto=True, grader="SGC", grade=10.0, auto_grade=10.0),
    hazards=["card_and_auto_grade:10/10_looks_like_serial"])
add(E, "https://www.ebay.com/itm/126657182265", "2023 Panini Prizm Football You Pick Rookies Shimmers Silver Prizms",
    L(None, "2023", "Panini", "Prizm", None, None, "Silver Prizm", exclusion_reason="you_pick"), hazards=["you_pick"])
add(E, "https://www.ebay.com/itm/126648108358", "2023 Panini Prizm Football SILVER PRIZM Complete Your Set You Pick Card #1-300",
    L(None, "2023", "Panini", "Prizm", None, None, "Silver Prizm", exclusion_reason="you_pick"), hazards=["you_pick", "card_no_range"])
add(E, "https://www.ebay.com/itm/267784365195", "2024 Panini Donruss Rated Rookie Malik Nabers #383 Optic Preview Holo - PSA 10",
    L("Malik Nabers", "2024", "Panini", "Donruss", "Optic Preview", "383", "Holo", grader="PSA", grade=10.0),
    hazards=["optic_preview_is_donruss_product_not_optic"])
add(E, "https://www.ebay.com/itm/396705711184", "2024 Panini Donruss - Rated Rookie Bo Nix Optic Preview Red Wave Prizm PSA 10.",
    L("Bo Nix", "2024", "Panini", "Donruss", "Optic Preview", None, "Red Wave", grader="PSA", grade=10.0),
    hazards=["optic_preview_is_donruss_product_not_optic", "trailing_period_on_grade", "missing_card_no"])
add(E, "https://www.ebay.com/itm/326431484324", "2024 Panini Donruss #394 Brock Bowers Rated Rookie PSA 10 RC Las Vegas Raiders",
    L("Brock Bowers", "2024", "Panini", "Donruss", "Rated Rookie", "394", "Base", grader="PSA", grade=10.0),
    hazards=["donruss_rated_rookie_vs_optic_rated_rookie"])
add(E, "https://www.ebay.com/itm/388664671145", "2024 Donruss Optic Rated Rookie Brock Bowers RC Las Vegas Raiders #215",
    L("Brock Bowers", "2024", "Panini", "Donruss Optic", "Rated Rookie", "215", "Base"))
add(E, "https://www.ebay.com/itm/225869942653", "Bryan Bresee Silver Prizm Rookie 2023 Panini Prizm Draft Picks Football",
    L("Bryan Bresee", "2023", "Panini", "Prizm Draft Picks", "Base", None, "Silver Prizm", is_rc=False), hazards=["missing_card_no"])
add(E, "https://www.ebay.com/itm/125097458599", "Zion Williamson Panini Prizm ROOKIE CARD ~RC~ PSA 7",
    L("Zion Williamson", None, "Panini", "Prizm", "Base", None, "Base", grader="PSA", grade=7.0), ambiguous=True,
    why="no year; Prizm vs Prizm Draft Picks unclear", hazards=["missing_year", "tilde_decoration"])
add(E, "https://www.ebay.com/itm/284296860619", "ZION WILLIAMSON PRIZM DP ROOKIE CARD PSA 8",
    L("Zion Williamson", "2019-20", "Panini", "Prizm Draft Picks", "Base", None, "Base", is_rc=False, grader="PSA", grade=8.0), ambiguous=True,
    why="no year or card number; 'DP' abbreviation", hazards=["abbrev:DP=Draft Picks", "missing_year"])
add(GS, "https://goldin.co/item/17-2019-20-panini-prizm-248-zion-williamson-rookie-card-bgs-pristine-1m9tz6",
    "(17) 2019-20 Panini Prizm #248 Zion Williamson Rookie Card - BGS PRISTINE 10",
    L("Zion Williamson", "2019-20", "Panini", "Prizm", "Base", "248", "Base", grader="BGS", grade=10.0, grade_label="Pristine",
      exclusion_reason="multi_card_lot"), hazards=["goldin_lot_quantity_prefix:(17)", "grade_label_before_number"])
add(GS, "https://goldin.co/item/2020-21-panini-prizm-rookie-signatures-black-prizm-aew-anthony-edwardsyh7ti",
    "2020/21 Panini Prizm Rookie Signatures Black Prizm #AEW Anthony Edwards Signed Rookie Card (#1/1)",
    L("Anthony Edwards", "2020-21", "Panini", "Prizm", "Rookie Signatures", "AEW", "Black Prizm", print_run=1, serial_no="1/1", is_auto=True),
    hazards=["season_year_slash:2020/21", "serial_in_parens_with_hash"])
add(GS, "https://goldin.co/item/2022-panini-select-draft-picks-purple-lazer-prizm-4-garrett-wilson-roo1b1hx",
    "2022 Panini Select Draft Picks Purple Lazer Prizm #4 Garrett Wilson Rookie Card - PSA GEM MT 10",
    L("Garrett Wilson", "2022", "Panini", "Select Draft Picks", "Base", "4", "Purple Lazer Prizm", is_rc=False, grader="PSA", grade=10.0, grade_label="GEM MINT"),
    hazards=["grade_label_before_number:PSA GEM MT 10", "surname_collision:Wilson"])
add(GS, "https://goldin.co/item/2023-panini-origins-wnba-jumbo-jersey-blue-jjajw-a-ja-wilson-relic-15ui46r",
    "2023 Panini Origins WNBA Jumbo Jersey-Blue #JJAJW A Ja Wilson Relic (15/25) - PSA NM-MT 8",
    L("A'ja Wilson", "2023", "Panini", "Origins WNBA", "Jumbo Jersey", "JJAJW", "Blue", print_run=25, serial_no="15/25", is_rc=False,
      grader="PSA", grade=8.0, grade_label="NM-MT"),
    hazards=["surname_collision:Wilson", "apostrophe_dropped_in_name", "serial_in_parens", "grade_label_before_number"])
add(DS, "https://www.steelcitycollectibles.com/i/drake-maye-2024-topps-now-football-rookie-card-rc--10-bgs-10-black-label",
    "Drake Maye 2024 Topps Now Football Rookie Card RC #10 BGS 10 Black Label",
    L("Drake Maye", "2024", "Topps", "Topps Now", "Base", "10", "Base", grader="BGS", grade=10.0, grade_label="Black Label"),
    hazards=["card_no_equals_grade:#10_BGS_10"])
add(EC, "https://www.ebay.com/p/10090548239", "2025 Panini Donruss Optic - Rated Rookie Tyler Shough #223 Purple Shock Prizm (RC) for sale online",
    L(TS, "2025", "Panini", "Donruss Optic", "Rated Rookie", "223", "Purple Shock"), ("2025", "Panini Donruss Optic", "Purple Shock", "223"),
    hazards=["site_suffix:for sale online"])
add(EC, "https://www.ebay.com/p/4090575521", "2025 Panini Donruss Optic - Rookie Kings Tyler Shough #14 (RC) for sale online",
    L(TS, "2025", "Panini", "Donruss Optic", "Rookie Kings", "14", "Base"), hazards=["site_suffix:for sale online"])

out = ROOT / "fixtures/titles/seed_gold.jsonl"
with open(out, "w") as f:
    for i, r in enumerate(R, 1):
        k = r.pop("gemrate_key")
        r = {"id": f"seed-{i:03d}", **r, "gemrate_id": GR.get(k) if k else None}
        if k and r["gemrate_id"] is None:
            raise SystemExit(f"gemrate key not found: {k}")
        f.write(json.dumps(r, ensure_ascii=False) + "\n")
print(len(R), "records ->", out)
