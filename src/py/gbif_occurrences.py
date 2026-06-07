#!/usr/bin/env python3
"""
gbif_occurrences.py
────────────────────
Downloads occurrence GeoJSON from GBIF for each species in ingredients.csv
and saves them to public/data/geo/<GBIF_id>.geojson

These files can be loaded by MapView.svelte for offline/cached distribution layers.
(Currently MapView uses live GBIF map tiles; this script is for future use or
if you want to run your own hexbin analysis.)

Usage:
    python src/py/gbif_occurrences.py [--limit 500]

Requires:
    pip install requests pandas

Notes:
  - GBIF occurrence download API requires registration for bulk downloads.
    This script uses the lighter /occurrence/search endpoint instead,
    which returns paginated JSON (max 300 per page).
  - For real biogeographic analysis consider the GBIF Download API
    (https://www.gbif.org/developer/occurrence#download).
"""

import os
import json
import time
import argparse
import requests
import pandas as pd
from pathlib import Path

# ─── Config ───────────────────────────────────────────────
CSV_PATH   = Path(__file__).parents[2] / "public" / "data" / "ingredients.csv"
OUTPUT_DIR = Path(__file__).parents[2] / "public" / "data" / "geo"
SLEEP_SEC  = 0.4
GBIF_OCC_URL = "https://api.gbif.org/v1/occurrence/search"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def fetch_occurrences(taxon_key: str, limit: int = 300) -> list[dict]:
    """
    Fetches up to `limit` occurrence records for a taxon from GBIF.
    Returns list of {lat, lng} dicts.
    """
    params = {
        "taxonKey": taxon_key,
        "hasCoordinate": "true",
        "hasGeospatialIssue": "false",
        "limit": min(limit, 300),
        "offset": 0,
    }
    points = []
    try:
        resp = requests.get(GBIF_OCC_URL, params=params, timeout=15)
        resp.raise_for_status()
        data = resp.json()
        for rec in data.get("results", []):
            lat = rec.get("decimalLatitude")
            lng = rec.get("decimalLongitude")
            if lat is not None and lng is not None:
                points.append({"lat": lat, "lng": lng})
    except Exception as e:
        print(f"  [!] occurrence fetch error for taxon {taxon_key}: {e}")
    return points


def points_to_geojson(points: list[dict], species_name: str) -> dict:
    return {
        "type": "FeatureCollection",
        "name": species_name,
        "features": [
            {
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [p["lng"], p["lat"]],
                },
                "properties": {},
            }
            for p in points
        ],
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=300, help="Max occurrences per species")
    args = parser.parse_args()

    df = pd.read_csv(CSV_PATH)
    df.columns = df.columns.str.strip()

    if "GBIF_id" not in df.columns:
        print("[!] No GBIF_id column found in ingredients.csv")
        return

    rows = df[["scientific_name", "GBIF_id"]].drop_duplicates()
    rows = rows[rows["GBIF_id"].notna() & (rows["GBIF_id"].astype(str).str.strip() != "")]

    print(f"Processing {len(rows)} species (limit={args.limit} occurrences each)…\n")

    for _, row in rows.iterrows():
        name      = row["scientific_name"].strip()
        taxon_key = str(int(float(row["GBIF_id"]))).strip()
        dest      = OUTPUT_DIR / f"{taxon_key}.geojson"

        if dest.exists():
            print(f"  ✓ {name} — already fetched")
            continue

        print(f"  ↓ {name} (taxonKey={taxon_key})")
        points = fetch_occurrences(taxon_key, limit=args.limit)

        if not points:
            print(f"    no occurrences found")
        else:
            gj = points_to_geojson(points, name)
            with open(dest, "w") as f:
                json.dump(gj, f)
            print(f"    {len(points)} points → {dest.name}")

        time.sleep(SLEEP_SEC)

    print("\nDone. GeoJSON files written to:", OUTPUT_DIR)


if __name__ == "__main__":
    main()
