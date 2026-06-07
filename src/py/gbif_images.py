#!/usr/bin/env python3
"""
gbif_images.py (herbarium-aware)
─────────────────────────────────
Priority pipeline:
1. PRESERVED_SPECIMEN (herbarium sheets)
2. StillImage illustrations (flora plates)
3. Any remaining media

Saves best botanical image per species.
"""

import time
import requests
import pandas as pd
from pathlib import Path

# ─── Config ───────────────────────────────────────────────
CSV_PATH   = Path(__file__).parents[2] / "public" / "data" / "ingredients.csv"
OUTPUT_DIR = Path(__file__).parents[2] / "public" / "img" / "botanica"

SLEEP_SEC = 0.5
MAX_SIZE  = (800, 1200)

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# ─── GBIF API ──────────────────────────────────────────────
GBIF_MEDIA_URL = "https://api.gbif.org/v1/species/{taxon_key}/media"
GBIF_OCC_URL   = "https://api.gbif.org/v1/occurrence/search"


# ─────────────────────────────────────────────
# 1. HERBARIUM-FIRST OCCURRENCE IMAGE
# ─────────────────────────────────────────────
def fetch_herbarium_image(taxon_key: str):
    params = {
        "taxonKey": taxon_key,
        "mediaType": "StillImage",
        "basisOfRecord": "PRESERVED_SPECIMEN",
        "limit": 10
    }

    try:
        r = requests.get(GBIF_OCC_URL, params=params, timeout=15)
        r.raise_for_status()
        data = r.json()
    except Exception as e:
        print(f"[!] herbarium fetch error {taxon_key}: {e}")
        return None

    results = data.get("results", [])

    for rec in results:
        media = rec.get("media", [])
        if not media:
            continue

        m = media[0]
        url = m.get("identifier")
        if url:
            return url, "herbarium"

    return None


# ─────────────────────────────────────────────
# 2. ILLUSTRATIONS / PLATES
# ─────────────────────────────────────────────
def fetch_illustration_image(taxon_key: str):
    try:
        r = requests.get(
            GBIF_MEDIA_URL.format(taxon_key=taxon_key),
            params={"limit": 20},
            timeout=15,
        )
        r.raise_for_status()
        data = r.json()
    except Exception as e:
        print(f"[!] media API error {taxon_key}: {e}")
        return None

    results = data.get("results", [])
    if not results:
        return None

    def score(item):
        t = (item.get("title") or "").lower()
        u = (item.get("identifier") or "").lower()

        is_illustration = any(k in t + u for k in [
            "illustr", "plate", "flora", "drawing", "botanical"
        ])

        is_image = item.get("type") == "StillImage"

        return (2 if is_image else 0) + (3 if is_illustration else 0)

    best = max(results, key=score)
    return best.get("identifier"), "illustration"


# ─────────────────────────────────────────────
# 3. FALLBACK ANY IMAGE
# ─────────────────────────────────────────────
def fetch_any_image(taxon_key: str):
    try:
        r = requests.get(
            GBIF_MEDIA_URL.format(taxon_key=taxon_key),
            params={"limit": 10},
            timeout=15,
        )
        r.raise_for_status()
        data = r.json()
    except Exception as e:
        return None

    results = data.get("results", [])
    if not results:
        return None

    for item in results:
        if item.get("identifier"):
            return item["identifier"], "other"

    return None


# ─────────────────────────────────────────────
# PIPELINE (IMPORTANT PART)
# ─────────────────────────────────────────────
def fetch_best_image_url(taxon_key: str):
    """
    Priority:
    1. herbarium
    2. illustration
    3. fallback
    """

    herb = fetch_herbarium_image(taxon_key)
    if herb:
        return herb

    illu = fetch_illustration_image(taxon_key)
    if illu:
        return illu

    return fetch_any_image(taxon_key)


# ─────────────────────────────────────────────
def download_image(url: str, dest: Path) -> bool:
    try:
        r = requests.get(url, stream=True, timeout=20)
        r.raise_for_status()

        with open(dest, "wb") as f:
            for chunk in r.iter_content(8192):
                f.write(chunk)

        return True

    except Exception as e:
        print(f"[!] download failed {url}: {e}")
        return False


# ─────────────────────────────────────────────
def resize_image(path: Path):
    try:
        from PIL import Image
        img = Image.open(path)
        img.thumbnail(MAX_SIZE, Image.LANCZOS)
        img.save(path, quality=85, optimize=True)
    except Exception:
        pass


# ─────────────────────────────────────────────
def main():
    df = pd.read_csv(CSV_PATH)
    df.columns = df.columns.str.strip()

    rows = df[["scientific_name", "GBIF_id"]].drop_duplicates()
    rows = rows[rows["GBIF_id"].notna()]

    print(f"Processing {len(rows)} species...\n")

    for _, row in rows.iterrows():
        name = row["scientific_name"].strip()
        taxon = str(int(float(row["GBIF_id"])))

        dest = OUTPUT_DIR / f"{taxon}.jpg"

        if dest.exists():
            print(f"✓ {name} already exists")
            continue

        print(f"↓ {name} ({taxon})")

        result = fetch_best_image_url(taxon)

        if not result:
            print("  no image found")
            time.sleep(SLEEP_SEC)
            continue

        url, source = result
        print(f"  → {source}")

        if download_image(url, dest):
            resize_image(dest)
            print(f"  saved {dest.name}")

        time.sleep(SLEEP_SEC)


if __name__ == "__main__":
    main()