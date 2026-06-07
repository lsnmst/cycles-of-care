#!/usr/bin/env python3
"""
recipe_names.py
────────────────────────────────────────
Generate poetic titles + enriched accession numbers
for Cycles of Care recipes.

Accessions include:
COUNTRY-DISEASE-COUNT+PART-SCIENTIFIC_SLUG
"""

import json
from pathlib import Path
from collections import Counter

import pandas as pd

# ─────────────────────────────────────────────
# Paths
# ─────────────────────────────────────────────

ROOT = Path(__file__).parents[2]

CSV_PATH = ROOT / "public" / "data" / "recipes.csv"
OUT_PATH = ROOT / "public" / "data" / "recipes_named.json"


# ─────────────────────────────────────────────
# Mappings
# ─────────────────────────────────────────────

COUNTRY_CODES = {
    "Albania": "AL", "Andorra": "AD", "Austria": "AT", "Belarus": "BY",
    "Belgium": "BE", "Bosnia and Herzegovina": "BA", "Bulgaria": "BG",
    "Croatia": "HR", "Cyprus": "CY", "Czechia": "CZ", "Denmark": "DK",
    "Estonia": "EE", "Finland": "FI", "France": "FR", "Germany": "DE",
    "Greece": "GR", "Hungary": "HU", "Iceland": "IS", "Ireland": "IE",
    "Italy": "IT", "Latvia": "LV", "Liechtenstein": "LI", "Lithuania": "LT",
    "Luxembourg": "LU", "Malta": "MT", "Monaco": "MC", "Montenegro": "ME",
    "Netherlands": "NL", "North Macedonia": "MK", "Norway": "NO",
    "Poland": "PL", "Portugal": "PT", "Romania": "RO",
    "Russian Federation": "RU", "San Marino": "SM", "Serbia": "RS",
    "Slovakia": "SK", "Slovenia": "SI", "Spain": "ES", "Sweden": "SE",
    "Switzerland": "CH", "Turkey": "TR", "Ukraine": "UA",
    "United Kingdom": "GB", "Vatican City": "VA",
}

DISEASE_CODES = {
    "amenorrhea": "AM",
    "amenorrea": "AM",
    "dysmenorrhea": "DY",
    "dismenorrea": "DY",
    "menorrhagia": "ME",
    "menorragia": "ME",
    "stop menstrual flux": "SF",
    "to regulate menstrual cycle": "RC",
    "metrorrhagia": "MT",
}

PART_CODES = {
    "flower": "F", "flowers": "F", "flowering tops": "F",
    "leaf": "L", "leaves": "L",
    "root": "R", "roots": "R", "radice": "R",
    "seed": "S", "seeds": "S",
    "fruit": "FR", "fruits": "FR",
    "bark": "B",
    "plant": "P",
}

NUMBER_WORDS = {
    1: "One", 2: "Two", 3: "Three", 4: "Four", 5: "Five",
    6: "Six", 7: "Seven", 8: "Eight", 9: "Nine", 10: "Ten",
    11: "Eleven", 12: "Twelve",
}


# ─────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────

def normalize(text: str) -> str:
    if pd.isna(text):
        return ""
    return str(text).strip().lower()


def dominant_part(parts):
    clean = []
    for p in parts:
        p = normalize(p)
        if ";" in p:
            p = p.split(";")[0]
        if p:
            clean.append(p)

    return Counter(clean).most_common(1)[0][0] if clean else "plant"


def dominant_scientific_name(group):
    names = group.get("scientific_name", pd.Series([])).dropna().tolist()
    names = [normalize(n) for n in names if n]

    return Counter(names).most_common(1)[0][0] if names else "unknown"


def slugify_scientific(name: str) -> str:
    """
    Convert scientific name into compact stable slug.
    Examples:
        matricaria chamomilla → matchamo
        symphytum officinale → symoffic
    """
    parts = normalize(name).split()

    if not parts:
        return "unk"

    if len(parts) == 1:
        return parts[0][:6]

    genus = parts[0][:3]
    species = parts[1][:5]

    return f"{genus}{species}"


def accession_code(country, disease, count, part, sci_name):
    country_code = COUNTRY_CODES.get(str(country).strip(), "XX")
    disease_code = DISEASE_CODES.get(normalize(disease), "ND")
    part_code = PART_CODES.get(normalize(part), "P")
    plant_code = slugify_scientific(sci_name)

    return f"{disease_code}-{count:02d}{part_code}-{plant_code}-{country_code}"


def generate_title(count, part):
    number = NUMBER_WORDS.get(count, str(count))
    part = normalize(part)

    if part in ["flower", "flowers", "flowering tops"]:
        label = "Flowers"
    elif part in ["leaf", "leaves"]:
        label = "Leaves"
    elif part in ["root", "roots", "radice"]:
        label = "Roots"
    elif part in ["seed", "seeds"]:
        label = "Seeds"
    elif part in ["fruit", "fruits"]:
        label = "Fruits"
    else:
        label = "Plants"

    return f"Assembly of {number} {label}"


# ─────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────

def main():
    df = pd.read_csv(CSV_PATH)
    df.columns = df.columns.str.strip()

    recipes = []
    grouped = df.groupby("name")

    for recipe_id, group in grouped:

        ingredient_count = len(group)

        country = (
            group["country"].dropna().iloc[0]
            if "country" in group.columns and not group["country"].dropna().empty
            else "Unknown"
        )

        disease = group["disease"].dropna().iloc[0]

        dom_part = dominant_part(group["parts"])
        dom_sci = dominant_scientific_name(group)

        title = generate_title(ingredient_count, dom_part)

        accession = accession_code(
            country,
            disease,
            ingredient_count,
            dom_part,
            dom_sci
        )

        recipes.append({
            "id": str(recipe_id),
            "title": title,
            "accession": accession,
            "country": country,
            "disease": disease,
            "ingredient_count": ingredient_count,
            "dominant_part": dom_part,
            "dominant_scientific": dom_sci,
        })

    with open(OUT_PATH, "w", encoding="utf-8") as f:
        json.dump(recipes, f, ensure_ascii=False, indent=2)

    print(f"✓ wrote {len(recipes)} recipes → {OUT_PATH}")


if __name__ == "__main__":
    main()