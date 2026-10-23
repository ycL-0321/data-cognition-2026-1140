from __future__ import annotations

import argparse
import json
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd
import requests
from requests.adapters import HTTPAdapter
from tqdm import tqdm
from urllib3.util.retry import Retry


API_ROOT = "https://pokeapi.co/api/v2"

GENERATION_META = {
    "generation-i": (1, "第一世代", "kanto", "关都"),
    "generation-ii": (2, "第二世代", "johto", "城都"),
    "generation-iii": (3, "第三世代", "hoenn", "丰缘"),
    "generation-iv": (4, "第四世代", "sinnoh", "神奥"),
    "generation-v": (5, "第五世代", "unova", "合众"),
    "generation-vi": (6, "第六世代", "kalos", "卡洛斯"),
    "generation-vii": (7, "第七世代", "alola", "阿罗拉"),
    "generation-viii": (8, "第八世代", "galar", "伽勒尔"),
    "generation-ix": (9, "第九世代", "paldea", "帕底亚"),
}

TYPE_ZH = {
    "normal": "一般",
    "fire": "火",
    "water": "水",
    "electric": "电",
    "grass": "草",
    "ice": "冰",
    "fighting": "格斗",
    "poison": "毒",
    "ground": "地面",
    "flying": "飞行",
    "psychic": "超能力",
    "bug": "虫",
    "rock": "岩石",
    "ghost": "幽灵",
    "dragon": "龙",
    "dark": "恶",
    "steel": "钢",
    "fairy": "妖精",
}

STAT_KEYS = {
    "hp": "hp",
    "attack": "attack",
    "defense": "defense",
    "special-attack": "special_attack",
    "special-defense": "special_defense",
    "speed": "speed",
}

REGIONAL_FORM_MARKERS = {
    "alola": ("阿罗拉", 7),
    "galar": ("伽勒尔", 8),
    "hisui": ("洗翠", 0),
    "paldea": ("帕底亚", 9),
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Collect Pokemon species, regional forms, and type/stat data."
    )
    parser.add_argument(
        "--max-species",
        type=int,
        default=None,
        help="Only collect the first N species. Useful for a quick connectivity test.",
    )
    parser.add_argument(
        "--species-limit",
        type=int,
        default=2000,
        help="Maximum number of species returned by the index endpoint.",
    )
    parser.add_argument(
        "--delay",
        type=float,
        default=0.1,
        help="Delay in seconds between uncached API requests.",
    )
    parser.add_argument(
        "--refresh",
        action="store_true",
        help="Ignore cached JSON and request every resource again.",
    )
    parser.add_argument(
        "--max-consecutive-failures",
        type=int,
        default=5,
        help="Stop after this many species fail without a successful request.",
    )
    return parser.parse_args()


class PokeClient:
    def __init__(self, delay: float, refresh: bool) -> None:
        self.delay = max(delay, 0.0)
        self.refresh = refresh
        self.request_count = 0
        self.session = requests.Session()
        self.session.headers.update(
            {
                "User-Agent": "pokemon-course-project/1.0",
                "Accept": "application/json",
            }
        )
        retry = Retry(
            total=5,
            connect=5,
            read=5,
            backoff_factor=0.6,
            status_forcelist=(429, 500, 502, 503, 504),
            allowed_methods=frozenset({"GET"}),
        )
        adapter = HTTPAdapter(max_retries=retry)
        self.session.mount("https://", adapter)

    def get(self, url: str, cache_path: Path) -> dict[str, Any]:
        if cache_path.exists() and not self.refresh:
            try:
                with cache_path.open("r", encoding="utf-8") as file:
                    return json.load(file)
            except (json.JSONDecodeError, OSError):
                cache_path.unlink(missing_ok=True)

        response = self.session.get(url, timeout=(10, 60))
        response.raise_for_status()
        data = response.json()

        cache_path.parent.mkdir(parents=True, exist_ok=True)
        temporary_path = cache_path.with_name(f"{cache_path.name}.tmp")
        with temporary_path.open("w", encoding="utf-8") as file:
            json.dump(data, file, ensure_ascii=False, indent=2)
        temporary_path.replace(cache_path)

        self.request_count += 1
        if self.delay:
            time.sleep(self.delay)
        return data


def resource_id(url: str) -> int:
    return int(url.rstrip("/").rsplit("/", 1)[-1])


def localized_name(
    names: list[dict[str, Any]], fallback: str, language_preferences: tuple[str, ...]
) -> str:
    by_language = {
        item["language"]["name"].lower(): item["name"]
        for item in names
        if item.get("language") and item.get("name")
    }
    for language in language_preferences:
        if language.lower() in by_language:
            return by_language[language.lower()]
    return fallback


def pokemon_types(pokemon: dict[str, Any]) -> tuple[str, str, str, str]:
    ordered = sorted(pokemon["types"], key=lambda item: item["slot"])
    type_names = [item["type"]["name"] for item in ordered]
    while len(type_names) < 2:
        type_names.append("")
    type_one_en, type_two_en = type_names[:2]
    return (
        type_one_en,
        TYPE_ZH.get(type_one_en, type_one_en),
        type_two_en,
        TYPE_ZH.get(type_two_en, ""),
    )


def pokemon_stats(pokemon: dict[str, Any]) -> dict[str, int]:
    stats = {key: 0 for key in STAT_KEYS.values()}
    for item in pokemon["stats"]:
        name = item["stat"]["name"]
        if name in STAT_KEYS:
            stats[STAT_KEYS[name]] = int(item["base_stat"])
    stats["total_stats"] = sum(
        stats[key]
        for key in ("hp", "attack", "defense", "special_attack", "special_defense", "speed")
    )
    return stats


def ability_names(pokemon: dict[str, Any]) -> tuple[str, str]:
    regular: list[str] = []
    hidden: list[str] = []
    ordered = sorted(pokemon.get("abilities", []), key=lambda item: item["slot"])
    for item in ordered:
        name = item["ability"]["name"].replace("-", " ")
        if item.get("is_hidden"):
            hidden.append(name)
        else:
            regular.append(name)
    return "; ".join(regular), "; ".join(hidden)


def common_pokemon_fields(pokemon: dict[str, Any]) -> dict[str, Any]:
    type_one_en, type_one_zh, type_two_en, type_two_zh = pokemon_types(pokemon)
    stats = pokemon_stats(pokemon)
    abilities, hidden_ability = ability_names(pokemon)
    return {
        "pokemon_id": int(pokemon["id"]),
        "type1_en": type_one_en,
        "type1_zh": type_one_zh,
        "type2_en": type_two_en,
        "type2_zh": type_two_zh,
        **stats,
        "height_m": round(pokemon["height"] / 10, 1),
        "weight_kg": round(pokemon["weight"] / 10, 1),
        "base_experience": pokemon.get("base_experience"),
        "abilities": abilities,
        "hidden_ability": hidden_ability,
    }


def collect_species(
    species_id: int,
    species: dict[str, Any],
    default_pokemon: dict[str, Any],
    client: PokeClient,
    raw_dir: Path,
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    generation_name = species["generation"]["name"]
    generation_order, generation_cn, region_en, region_cn = GENERATION_META.get(
        generation_name,
        (0, generation_name, generation_name, generation_name),
    )
    species_name_en = species["name"]
    species_name_zh = localized_name(
        species.get("names", []),
        fallback=species_name_en,
        language_preferences=("zh-Hans", "zh-Hant", "en"),
    )
    base_fields = common_pokemon_fields(default_pokemon)

    record = {
        "species_id": species_id,
        "dex_number": species.get("id"),
        "name_en": species_name_en,
        "name_zh": species_name_zh,
        "generation": generation_name,
        "generation_cn": generation_cn,
        "generation_order": generation_order,
        "region_en": region_en,
        "region_cn": region_cn,
        "color": (species.get("color") or {}).get("name", ""),
        "habitat": (species.get("habitat") or {}).get("name", ""),
        "growth_rate": (species.get("growth_rate") or {}).get("name", ""),
        "capture_rate": species.get("capture_rate"),
        "base_happiness": species.get("base_happiness"),
        "is_legendary": bool(species.get("is_legendary")),
        "is_mythical": bool(species.get("is_mythical")),
        **base_fields,
    }

    form_records: list[dict[str, Any]] = []
    for variety in species.get("varieties", []):
        form_name_en = variety["pokemon"]["name"]
        if "-cap" in form_name_en or "-totem" in form_name_en:
            continue
        matched_marker = None
        for marker, meta in REGIONAL_FORM_MARKERS.items():
            if f"-{marker}" in form_name_en:
                matched_marker = (marker, meta)
                break
        if matched_marker is None:
            continue

        form_region_cn, form_region_order = matched_marker[1]
        form_cache = raw_dir / "pokemon" / f"{form_name_en}.json"
        form_pokemon = client.get(variety["pokemon"]["url"], form_cache)
        form_fields = common_pokemon_fields(form_pokemon)
        form_records.append(
            {
                "species_id": species_id,
                "dex_number": species.get("id"),
                "species_name_en": species_name_en,
                "species_name_zh": species_name_zh,
                "form_id": form_fields["pokemon_id"],
                "form_name_en": form_name_en,
                "form_name_zh": f"{species_name_zh}（{form_region_cn}形态）",
                "form_region_en": matched_marker[0],
                "form_region_cn": form_region_cn,
                "form_region_order": form_region_order,
                "is_regional_form": True,
                **form_fields,
            }
        )

    return record, form_records


def build_outputs(
    species_records: list[dict[str, Any]],
    form_records: list[dict[str, Any]],
    failed_species: list[dict[str, str]],
    client: PokeClient,
    data_dir: Path,
    delay: float,
) -> None:
    data_dir.mkdir(parents=True, exist_ok=True)

    species_columns = [
        "species_id",
        "dex_number",
        "name_en",
        "name_zh",
        "generation",
        "generation_cn",
        "generation_order",
        "region_en",
        "region_cn",
        "type1_en",
        "type1_zh",
        "type2_en",
        "type2_zh",
        "hp",
        "attack",
        "defense",
        "special_attack",
        "special_defense",
        "speed",
        "total_stats",
        "is_legendary",
        "is_mythical",
        "height_m",
        "weight_kg",
        "base_experience",
        "abilities",
        "hidden_ability",
        "color",
        "habitat",
        "growth_rate",
        "capture_rate",
        "base_happiness",
        "pokemon_id",
    ]
    species_df = pd.DataFrame(species_records)
    if species_df.empty:
        raise RuntimeError("No species records were collected.")
    species_df = species_df[species_columns].sort_values(
        ["generation_order", "species_id"]
    )
    species_df.to_csv(
        data_dir / "pokemon_clean.csv", index=False, encoding="utf-8-sig"
    )

    forms_df = pd.DataFrame(form_records)
    if not forms_df.empty:
        form_columns = [
            "species_id",
            "dex_number",
            "species_name_en",
            "species_name_zh",
            "form_id",
            "form_name_en",
            "form_name_zh",
            "form_region_en",
            "form_region_cn",
            "form_region_order",
            "is_regional_form",
            "type1_en",
            "type1_zh",
            "type2_en",
            "type2_zh",
            "hp",
            "attack",
            "defense",
            "special_attack",
            "special_defense",
            "speed",
            "total_stats",
            "height_m",
            "weight_kg",
            "base_experience",
            "abilities",
            "hidden_ability",
            "pokemon_id",
        ]
        forms_df = forms_df[form_columns].sort_values(
            ["form_region_order", "species_id", "form_id"]
        )
        forms_df.to_csv(
            data_dir / "forms_clean.csv", index=False, encoding="utf-8-sig"
        )
    else:
        pd.DataFrame().to_csv(
            data_dir / "forms_clean.csv", index=False, encoding="utf-8-sig"
        )

    region_summary = (
        species_df.groupby(
            ["generation_order", "generation_cn", "region_en", "region_cn"],
            as_index=False,
        )
        .agg(
            species_count=("species_id", "count"),
            legendary_count=("is_legendary", "sum"),
            mythical_count=("is_mythical", "sum"),
            avg_hp=("hp", "mean"),
            avg_attack=("attack", "mean"),
            avg_defense=("defense", "mean"),
            avg_special_attack=("special_attack", "mean"),
            avg_special_defense=("special_defense", "mean"),
            avg_speed=("speed", "mean"),
            avg_total_stats=("total_stats", "mean"),
        )
        .sort_values("generation_order")
    )
    numeric_columns = [
        "avg_hp",
        "avg_attack",
        "avg_defense",
        "avg_special_attack",
        "avg_special_defense",
        "avg_speed",
        "avg_total_stats",
    ]
    region_summary[numeric_columns] = region_summary[numeric_columns].round(2)
    region_summary.to_csv(
        data_dir / "region_summary.csv", index=False, encoding="utf-8-sig"
    )

    type_rows: list[dict[str, Any]] = []
    for row in species_df.to_dict("records"):
        for slot, column in ((1, "type1_zh"), (2, "type2_zh")):
            type_name = row[column]
            if type_name:
                type_rows.append(
                    {
                        "generation_order": row["generation_order"],
                        "region_cn": row["region_cn"],
                        "type_slot": slot,
                        "type_cn": type_name,
                    }
                )
    type_long = pd.DataFrame(type_rows)
    type_long.to_csv(
        data_dir / "type_region_long.csv", index=False, encoding="utf-8-sig"
    )
    type_matrix = (
        type_long.groupby(["region_cn", "type_cn"])
        .size()
        .unstack(fill_value=0)
        .reindex(
            species_df.drop_duplicates("region_cn")
            .sort_values("generation_order")["region_cn"]
        )
    )
    type_matrix.to_csv(data_dir / "type_region_matrix.csv", encoding="utf-8-sig")

    missing_counts = {
        column: int(species_df[column].isna().sum()) for column in species_columns
    }
    quality = {
        "collected_at_utc": datetime.now(timezone.utc).isoformat(),
        "api_root": API_ROOT,
        "delay_seconds": delay,
        "net_api_requests_this_run": client.request_count,
        "species_rows": int(len(species_df)),
        "regional_form_rows": int(len(forms_df)),
        "regions": {
            str(key): int(value)
            for key, value in species_df["region_cn"].value_counts().items()
        },
        "duplicate_species_ids": int(species_df["species_id"].duplicated().sum()),
        "missing_counts": missing_counts,
        "failed_species_count": len(failed_species),
        "failed_species": failed_species,
    }
    with (data_dir / "data_quality.json").open("w", encoding="utf-8") as file:
        json.dump(quality, file, ensure_ascii=False, indent=2)

    print("\nData collection complete.")
    print(f"Species rows: {len(species_df)}")
    print(f"Regional form rows: {len(forms_df)}")
    print(f"Failed species: {len(failed_species)}")
    print(f"Output directory: {data_dir}")


def main() -> None:
    args = parse_args()
    project_dir = Path(__file__).resolve().parent
    raw_dir = project_dir / "raw"
    data_dir = project_dir / "data"
    client = PokeClient(delay=args.delay, refresh=args.refresh)

    index_url = (
        f"{API_ROOT}/pokemon-species?limit={args.species_limit}&offset=0"
    )
    index_data = client.get(
        index_url, raw_dir / "index" / f"species_list_{args.species_limit}.json"
    )
    species_items = index_data["results"]
    if args.max_species is not None:
        species_items = species_items[: max(args.max_species, 0)]

    species_records: list[dict[str, Any]] = []
    form_records: list[dict[str, Any]] = []
    failed_species: list[dict[str, str]] = []
    consecutive_failures = 0

    for item in tqdm(species_items, desc="Collecting Pokemon", unit="species"):
        species_id = resource_id(item["url"])
        cache_path = raw_dir / "species" / f"{species_id}.json"
        try:
            species = client.get(item["url"], cache_path)
            default_variety = next(
                (
                    variety
                    for variety in species.get("varieties", [])
                    if variety.get("is_default")
                ),
                None,
            )
            if default_variety is None:
                raise ValueError("No default Pokemon variety found.")

            pokemon_name = default_variety["pokemon"]["name"]
            pokemon_cache = raw_dir / "pokemon" / f"{pokemon_name}.json"
            default_pokemon = client.get(
                default_variety["pokemon"]["url"], pokemon_cache
            )
            species_record, species_forms = collect_species(
                species_id,
                species,
                default_pokemon,
                client,
                raw_dir,
            )
            species_records.append(species_record)
            form_records.extend(species_forms)
            consecutive_failures = 0
        except Exception as exc:  # Keep a resumable record of failed resources.
            failed_species.append(
                {
                    "species": item["name"],
                    "url": item["url"],
                    "error": repr(exc),
                }
            )
            consecutive_failures += 1
            tqdm.write(f"Failed: {item['name']} ({exc!r})")
            if consecutive_failures >= args.max_consecutive_failures:
                tqdm.write(
                    "Stopped after repeated failures. Reconnect the network and "
                    "run the same command again; cached resources will be reused."
                )
                break

    build_outputs(
        species_records=species_records,
        form_records=form_records,
        failed_species=failed_species,
        client=client,
        data_dir=data_dir,
        delay=args.delay,
    )


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(
            "\nStopped by user. Cached API responses are preserved; "
            "run the same command again to resume."
        )
