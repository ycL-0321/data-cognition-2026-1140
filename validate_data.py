from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd


BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
RAW_DIR = BASE_DIR / "raw"

EXPECTED_REGIONS = {
    "关都",
    "城都",
    "丰缘",
    "神奥",
    "合众",
    "卡洛斯",
    "阿罗拉",
    "伽勒尔",
    "帕底亚",
}

VALID_TYPES = {
    "一般",
    "火",
    "水",
    "电",
    "草",
    "冰",
    "格斗",
    "毒",
    "地面",
    "飞行",
    "超能力",
    "虫",
    "岩石",
    "幽灵",
    "龙",
    "恶",
    "钢",
    "妖精",
}

REQUIRED_SPECIES_COLUMNS = {
    "species_id",
    "dex_number",
    "name_zh",
    "generation",
    "region_cn",
    "type1_zh",
    "hp",
    "attack",
    "defense",
    "special_attack",
    "special_defense",
    "speed",
    "total_stats",
}

REQUIRED_FORM_COLUMNS = {
    "species_id",
    "form_id",
    "form_name_zh",
    "form_region_cn",
    "type1_zh",
    "total_stats",
}

STAT_COLUMNS = [
    "hp",
    "attack",
    "defense",
    "special_attack",
    "special_defense",
    "speed",
    "total_stats",
]


def add_check(
    checks: list[dict],
    name: str,
    passed: bool,
    details: str,
) -> None:
    checks.append({"check": name, "passed": bool(passed), "details": details})


def main() -> int:
    species_path = DATA_DIR / "pokemon_clean.csv"
    forms_path = DATA_DIR / "forms_clean.csv"
    quality_path = DATA_DIR / "data_quality.json"

    checks: list[dict] = []
    required_paths = [species_path, forms_path, quality_path]
    missing_paths = [str(path.relative_to(BASE_DIR)) for path in required_paths if not path.exists()]
    add_check(
        checks,
        "required_files",
        not missing_paths,
        "All required files exist."
        if not missing_paths
        else f"Missing: {', '.join(missing_paths)}",
    )
    if missing_paths:
        result = {
            "validated_at_utc": datetime.now(timezone.utc).isoformat(),
            "overall_passed": False,
            "checks": checks,
        }
        (DATA_DIR / "validation_report.json").write_text(
            json.dumps(result, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        return 1

    species = pd.read_csv(species_path)
    forms = pd.read_csv(forms_path)
    quality = json.loads(quality_path.read_text(encoding="utf-8"))

    missing_species_columns = sorted(
        REQUIRED_SPECIES_COLUMNS.difference(species.columns)
    )
    add_check(
        checks,
        "species_columns",
        not missing_species_columns,
        "All required species columns exist."
        if not missing_species_columns
        else f"Missing columns: {', '.join(missing_species_columns)}",
    )

    missing_form_columns = sorted(REQUIRED_FORM_COLUMNS.difference(forms.columns))
    add_check(
        checks,
        "form_columns",
        not missing_form_columns,
        "All required regional form columns exist."
        if not missing_form_columns
        else f"Missing columns: {', '.join(missing_form_columns)}",
    )

    row_count_ok = len(species) == int(quality.get("species_rows", -1))
    add_check(
        checks,
        "species_row_count",
        row_count_ok,
        f"CSV rows={len(species)}, quality report rows={quality.get('species_rows')}",
    )

    duplicate_species = int(species["species_id"].duplicated().sum())
    add_check(
        checks,
        "duplicate_species_ids",
        duplicate_species == 0,
        f"Duplicate species IDs: {duplicate_species}",
    )

    actual_regions = set(species["region_cn"].dropna().astype(str))
    region_ok = actual_regions == EXPECTED_REGIONS
    add_check(
        checks,
        "region_coverage",
        region_ok,
        f"Covered regions: {', '.join(sorted(actual_regions))}",
    )

    core_columns = [
        "species_id",
        "name_zh",
        "region_cn",
        "type1_zh",
        "generation",
    ] + STAT_COLUMNS
    missing_core_values = int(species[core_columns].isna().sum().sum())
    add_check(
        checks,
        "missing_core_values",
        missing_core_values == 0,
        f"Missing values in core columns: {missing_core_values}",
    )

    type_one_ok = set(species["type1_zh"].dropna().astype(str)).issubset(VALID_TYPES)
    type_two_values = set(
        species["type2_zh"].dropna().astype(str).loc[lambda values: values != ""]
    )
    type_two_ok = type_two_values.issubset(VALID_TYPES)
    add_check(
        checks,
        "valid_types",
        type_one_ok and type_two_ok,
        f"Unexpected types: {sorted((set(species['type1_zh'].dropna().astype(str)) | type_two_values) - VALID_TYPES)}",
    )

    stats_in_range = True
    for column in STAT_COLUMNS:
        numeric = pd.to_numeric(species[column], errors="coerce")
        stats_in_range = stats_in_range and numeric.between(1, 1125).all()
    add_check(
        checks,
        "stat_ranges",
        bool(stats_in_range),
        "All six base stats and total stats are positive numeric values.",
    )

    if forms.empty:
        add_check(
            checks,
            "regional_forms",
            True,
            "No regional form rows were collected; this is allowed for a partial test.",
        )
    else:
        duplicate_form_ids = int(forms["form_id"].duplicated().sum())
        forms_link_ok = forms["species_id"].isin(species["species_id"]).all()
        add_check(
            checks,
            "regional_forms",
            duplicate_form_ids == 0 and bool(forms_link_ok),
            "Duplicate form IDs: "
            f"{duplicate_form_ids}; all form species links valid: {bool(forms_link_ok)}",
        )

    failed_count = int(quality.get("failed_species_count", -1))
    add_check(
        checks,
        "collection_failures",
        failed_count == 0,
        f"Failed species: {failed_count}",
    )

    raw_species_files = len(list((RAW_DIR / "species").glob("*.json")))
    raw_pokemon_files = len(list((RAW_DIR / "pokemon").glob("*.json")))
    add_check(
        checks,
        "raw_cache",
        raw_species_files > 0 and raw_pokemon_files > 0,
        f"Raw species files: {raw_species_files}; raw Pokemon files: {raw_pokemon_files}",
    )

    overall_passed = all(check["passed"] for check in checks)
    report = {
        "validated_at_utc": datetime.now(timezone.utc).isoformat(),
        "overall_passed": overall_passed,
        "summary": {
            "species_rows": int(len(species)),
            "regional_form_rows": int(len(forms)),
            "regions": int(species["region_cn"].nunique()),
            "duplicate_species_ids": duplicate_species,
            "raw_species_files": raw_species_files,
            "raw_pokemon_files": raw_pokemon_files,
        },
        "checks": checks,
    }
    (DATA_DIR / "validation_report.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    print("Data validation")
    print("=" * 60)
    for check in checks:
        status = "PASS" if check["passed"] else "FAIL"
        print(f"[{status}] {check['check']}: {check['details']}")
    print("=" * 60)
    print(f"Overall result: {'PASS' if overall_passed else 'FAIL'}")
    print(f"Report: {DATA_DIR / 'validation_report.json'}")
    return 0 if overall_passed else 1


if __name__ == "__main__":
    sys.exit(main())
