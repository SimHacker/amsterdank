#!/usr/bin/env python3
"""Turn CannaMap's Amsterdam records into claims, keyed by address.

CannaMap is evidence, not truth: its compilation is unlicensed, so nothing here
gets republished as ours and nothing here reaches OpenStreetMap. What we take is
the shape of the leads -- which addresses have a name, hours, a coordinate, and how
old the newest menu photograph is, because photo age is a decent staleness signal
for whether a shop still exists.

Usage:  python3 scripts/import_cannamaps.py [path-to-cannamaps-checkout]
Writes: data/claims-cannamaps.csv
"""

import csv
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from addr import address_key, parse_freeform, subject_id

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_REPO = "/Users/a2deh/GroundUp/git/cannamaps"
SOURCE = "cannamaps"
OBSERVED = "2026-09-15"          # the day this checkout was taken

# One claim per (subject, field). Amenity and hours blobs are stored as JSON text:
# this table is a ledger of assertions, not a normalized warehouse.
SIMPLE_FIELDS = ["name", "status", "website", "instagram", "shop_type"]


def load_roster():
    """address_key -> roster row, for the current gedooglijst."""
    path = None
    for f in sorted(os.listdir(os.path.join(HERE, "data"))):
        if f.startswith("gedooglijst-") and f.endswith(".csv"):
            path = os.path.join(HERE, "data", f)
    if not path:
        sys.exit("run scripts/fetch_gedooglijst.py first")
    roster = {}
    with open(path, encoding="utf-8") as f:
        for row in csv.DictReader(f):
            roster[address_key(row["street_raw"], row["number"])] = row
    return roster


def main():
    repo = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_REPO
    shops = json.load(open(os.path.join(repo, "public/data/shops.json"), encoding="utf-8"))["shops"]
    roster = load_roster()

    # Menu-photo recency, from the Amsterdam-only CSV, keyed the same way.
    recency = {}
    ams_csv = os.path.join(repo, "coffeeshopdata/amsterdam-coffeeshops.csv")
    if os.path.exists(ams_csv):
        with open(ams_csv, encoding="utf-8") as f:
            for row in csv.DictReader(f):
                k = address_key(row["street"].rsplit(" ", 1)[0], row["street"].rsplit(" ", 1)[-1]) \
                    if row.get("street") else None
                p = parse_freeform(row.get("address") or row.get("street") or "")
                k = address_key(p["street"], p["number"])
                recency[k] = row

    claims, matched, unmatched = [], 0, 0

    def add(subject, field, value, note=""):
        if value in (None, "", [], {}):
            return
        claims.append({
            "subject": subject, "field": field, "value": value,
            "source": SOURCE, "observed": OBSERVED, "confidence": "reported", "note": note,
        })

    for s in shops:
        if (s.get("city") or "").strip().lower() != "amsterdam":
            continue
        p = parse_freeform(s.get("address", ""))
        if not p["number"]:
            continue
        key = address_key(p["street"], p["number"])
        hit = roster.get(key)
        if hit:
            matched += 1
            sid = subject_id(hit["street_raw"], hit["number"], hit["suffix"])
        else:
            unmatched += 1
            sid = subject_id(p["street"], p["number"], p["suffix"])

        add(sid, "address_as_written", s.get("address", ""))
        if not hit:
            add(sid, "off_roster", "yes",
                "address not on the current gedooglijst: closed, moved, renumbered, or a bad address")
        for f in SIMPLE_FIELDS:
            add(sid, f, s.get(f) or "")
        if s.get("lat") and s.get("lng"):
            add(sid, "lat", f"{s['lat']:.7f}")
            add(sid, "lng", f"{s['lng']:.7f}")
        if s.get("opening_hours"):
            add(sid, "opening_hours_json", json.dumps(s["opening_hours"], separators=(",", ":")),
                f"hours_source={s.get('hours_source','')}")
        if s.get("amenities"):
            avail = sorted(k for k, v in s["amenities"].items() if v.get("available"))
            add(sid, "amenities", ";".join(avail))
        if s.get("menu_images"):
            add(sid, "menu_photo_count", str(len(s["menu_images"])),
                "his photographs, not ours -- do not copy; ride and shoot our own")
        if s.get("closed_source"):
            add(sid, "closed_reported_by", s["closed_source"])
        if s.get("note"):
            add(sid, "note_upstream", s["note"])
        r = recency.get(key)
        if r and r.get("latest_menu"):
            add(sid, "latest_menu_photo", r["latest_menu"], "staleness signal, not an opening claim")
        if r and r.get("source_page"):
            add(sid, "source_page", r["source_page"], "chains provenance past CannaMap to coffeeshopmenus.org")

    out = os.path.join(HERE, "data", "claims-cannamaps.csv")
    with open(out, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["subject", "field", "value", "source", "observed", "confidence", "note"])
        w.writeheader()
        w.writerows(claims)

    print(f"{matched} Amsterdam records matched the roster, {unmatched} did not")
    print(f"{len(claims)} claims -> {os.path.relpath(out, HERE)}")


if __name__ == "__main__":
    main()
