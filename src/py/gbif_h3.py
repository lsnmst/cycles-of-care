#!/usr/bin/env python3
"""
gbif_h3.py
──────────
Converts GBIF occurrence points into H3 spatial indexes
with optional buffering for ecological presence modeling.

Output:
    public/data/h3/<GBIF_id>.json

Each file contains:
{
  "taxon_key": "8370958",
  "resolution": 6,
  "buffer_k": 1,
  "cells": ["862a100ffffffff", ...]
}

Usage:
    python src/py/gbif_h3.py --limit 300 --resolution 6 --buffer 1

Requires:
    pip install requests pandas h3
"""

import json
import time
import argparse
import requests
import pandas as pd
import h3
from pathlib import Path

# ─────────────────────────────────────────────
CSV_PATH = Path(__file__).parents[2] / "public" / "data" / "ingredients.csv"
OUTPUT_DIR = Path(__file__).parents[2] / "public" / "data" / "h3"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

GBIF_OCC_URL = "https://api.gbif.org/v1/occurrence/search"

SLEEP_SEC = 0.4

EUROPE_POLYGON = (
    "POLYGON(("
    "-25 34,"
    "45 34,"
    "45 72,"
    "-25 72,"
    "-25 34"
    "))"
)

# ─────────────────────────────────────────────
def fetch_occurrences(taxon_key: str, limit: int = 300, max_total: int = 6000):
    """
    Fetch paginated GBIF occurrences.
    max_total controls how many points you want overall.
    """

    all_points = []
    offset = 0

    while offset < max_total:
        params = {
            "taxonKey": taxon_key,
            "hasCoordinate": "true",
            "hasGeospatialIssue": "false",
            "limit": limit,
            "offset": offset,
            "geometry": EUROPE_POLYGON,
        }

        try:
            resp = requests.get(GBIF_OCC_URL, params=params, timeout=20)
            resp.raise_for_status()
            data = resp.json()

            results = data.get("results", [])
            if not results:
                break

            for rec in results:
                lat = rec.get("decimalLatitude")
                lng = rec.get("decimalLongitude")

                if lat is not None and lng is not None:
                    all_points.append((lat, lng))

            offset += limit

            # stop if last page
            if len(results) < limit:
                break

        except Exception as e:
            print(f"[!] GBIF error {taxon_key}: {e}")
            break

    return all_points


# ─────────────────────────────────────────────
def points_to_h3(points, resolution: int):
    """
    Convert lat/lng points → H3 cells.
    """
    cells = set()

    for lat, lng in points:
        try:
            cell = h3.latlng_to_cell(lat, lng, resolution)
            cells.add(cell)
        except Exception:
            continue

    return cells


# ─────────────────────────────────────────────
def buffer_h3(cells, k: int):
    """
    Expands H3 cells by k-ring neighborhood.
    Ecological "uncertainty / dispersal buffer".
    """
    if k <= 0:
        return cells

    expanded = set()

    for c in cells:
        expanded.add(c)
        try:
            neighbors = h3.grid_disk(c, k)
            for n in neighbors:
                expanded.add(n)
        except Exception:
            continue

    return expanded


# ─────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser()

    parser.add_argument("--limit", type=int, default=300)
    parser.add_argument("--resolution", type=int, default=6)
    parser.add_argument("--buffer", type=int, default=1)

    args = parser.parse_args()

    df = pd.read_csv(CSV_PATH)
    df.columns = df.columns.str.strip()

    if "GBIF_id" not in df.columns:
        print("[!] Missing GBIF_id column")
        return

    rows = df[["scientific_name", "GBIF_id"]].drop_duplicates()
    rows = rows[
        rows["GBIF_id"].notna()
        & (rows["GBIF_id"].astype(str).str.strip() != "")
    ]

    print(f"\nProcessing {len(rows)} species\n")

    for _, row in rows.iterrows():

        name = row["scientific_name"].strip()
        taxon_key = str(int(float(row["GBIF_id"]))).strip()

        out_file = OUTPUT_DIR / f"{taxon_key}.json"

        if out_file.exists():
            print(f"✓ {name} — already processed")
            continue

        print(f"↓ {name} ({taxon_key})")

        # 1. fetch points
        points = fetch_occurrences(taxon_key, limit=args.limit)

        if not points:
            print("  no occurrences found")
            time.sleep(SLEEP_SEC)
            continue

        # 2. points → H3
        cells = points_to_h3(points, args.resolution)

        # 3. buffer
        buffered = buffer_h3(cells, args.buffer)

        # 4. save
        output = {
            "taxon_key": taxon_key,
            "scientific_name": name,
            "resolution": args.resolution,
            "buffer_k": args.buffer,
            "cells": list(buffered),
        }

        with open(out_file, "w") as f:
            json.dump(output, f)

        print(f"  → {len(buffered)} cells saved")

        time.sleep(SLEEP_SEC)

    print("\nDone → H3 files written to:", OUTPUT_DIR)


if __name__ == "__main__":
    main()