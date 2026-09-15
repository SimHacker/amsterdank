#!/usr/bin/env python3
"""Fold every claim into one wide row per address, and compute the review queue.

data/claims-*.csv is the truth. data/register.csv is a VIEW, regenerated from the
claims and never hand-edited -- if a cell is wrong, the claim behind it is wrong.
That is what lets the same address hold three different coordinates from three
sources with the disagreement visible instead of averaged away.

Also writes data/osm-safe.csv, which contains only claims whose source says
osm_ok: true in sources.yml. That file, and only that file, may become a changeset.

Usage:  python3 scripts/build_register.py
"""

import csv
import glob
import json
import math
import os
import re
import sys
from collections import defaultdict

import yaml

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from addr import address_key, dutch_title, fold, parse_freeform, street_key, subject_id

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Who wins when two sources claim the same field. Your own eyes first, the
# municipality for anything legal, the commons before the compilations, memory last.
PREFERENCE = ["field-survey", "gedooglijst", "osm", "pdok", "historical-sheet", "cannamaps", "user-lead"]

COORD_CONFLICT_M = 40       # two coordinates farther apart than this disagree about the building
STALE_MENU_YEARS = 5

COLUMNS = [
    "subject_id", "tolerated", "roster_valid_from",
    "sort_name", "name", "html_name", "also_known_as",
    "street", "number", "suffix", "postcode", "address_as_written",
    "status", "lat", "lng", "coord_source", "coord_spread_m",
    "osm_type", "osm_id", "foursquare_id", "website", "instagram",
    "opening_hours_json", "amenities", "menu_photo_count", "latest_menu_photo",
    "closure_date", "closure_cause", "relocated_from", "relocated_to",
    "site_history", "field_survey_date",
    "review_priority", "review_reasons", "probable_pair", "sources_seen",
]

ARTICLES = ("the ", "de ", "het ", "la ", "le ", "'t ", "t ")


def haversine(a, b):
    (la1, lo1), (la2, lo2) = a, b
    r = 6371000.0
    p1, p2 = math.radians(la1), math.radians(la2)
    dp, dl = p2 - p1, math.radians(lo2 - lo1)
    h = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * r * math.asin(math.sqrt(h))


def sort_name(name):
    low = name.lower()
    for a in ARTICLES:
        if low.startswith(a):
            return name[len(a):].strip() + ", " + name[: len(a)].strip()
    return name


def html_name(name):
    return (name.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))


def load_sources():
    with open(os.path.join(HERE, "sources.yml"), encoding="utf-8") as f:
        return yaml.safe_load(f)["sources"]


def load_roster():
    path = sorted(glob.glob(os.path.join(HERE, "data", "gedooglijst-*.csv")))[-1]
    rows = {}
    with open(path, encoding="utf-8") as f:
        for r in csv.DictReader(f):
            rows[subject_id(r["street_raw"], r["number"], r["suffix"])] = r
    return rows


def load_claims():
    claims = defaultdict(lambda: defaultdict(list))     # subject -> field -> [claim]
    for path in sorted(glob.glob(os.path.join(HERE, "data", "claims-*.csv"))):
        with open(path, encoding="utf-8") as f:
            for c in csv.DictReader(f):
                claims[c["subject"]][c["field"]].append(c)
    return claims


def pick(claims_for_field):
    """Best claim for one field, by source preference; ties keep the first seen."""
    if not claims_for_field:
        return None
    def rank(c):
        try:
            return PREFERENCE.index(c["source"])
        except ValueError:
            return len(PREFERENCE)
    return sorted(claims_for_field, key=rank)[0]


def main():
    sources = load_sources()
    roster = load_roster()
    claims = load_claims()

    subjects = sorted(set(roster) | set(claims))
    rows, safe_rows = [], []

    for sid in subjects:
        c = claims.get(sid, {})
        r = roster.get(sid)
        row = {k: "" for k in COLUMNS}
        row["subject_id"] = sid
        row["tolerated"] = "yes" if r else "no"
        if r:
            row.update(street=dutch_title(r["street_raw"]), number=r["number"], suffix=r["suffix"],
                       postcode=r["postcode"], roster_valid_from=r["valid_from"])

        for field in ("name", "status", "website", "instagram", "opening_hours_json", "amenities",
                      "menu_photo_count", "latest_menu_photo", "address_as_written", "foursquare_id",
                      "osm_type", "osm_id", "closure_date", "closure_cause", "relocated_from",
                      "relocated_to", "site_history", "field_survey_date"):
            best = pick(c.get(field, []))
            if best:
                row[field] = best["value"]

        if not r and row["address_as_written"]:
            p = parse_freeform(row["address_as_written"])
            row.update(street=dutch_title(p["street"]), number=p["number"],
                       suffix=p["suffix"], postcode=p["postcode"])

        if row["name"]:
            row["sort_name"] = sort_name(row["name"])
            row["html_name"] = html_name(row["name"])

        # Every distinct name anybody has claimed, current one excluded, semicolon
        # separated because no shop name contains a semicolon and plenty contain commas.
        names, seen = [], {fold(row["name"])}
        for cl in c.get("name", []) + c.get("former_name", []):
            if fold(cl["value"]) not in seen:
                seen.add(fold(cl["value"]))
                names.append(cl["value"])
        row["also_known_as"] = ";".join(names)

        # Coordinates: keep the disagreement as a number instead of averaging it away.
        pts = []
        lat_claims, lng_claims = c.get("lat", []), c.get("lng", [])
        by_source = {}
        for a in lat_claims:
            for b in lng_claims:
                if a["source"] == b["source"]:
                    by_source[a["source"]] = (float(a["value"]), float(b["value"]))
        if by_source:
            best_src = pick([{"source": s} for s in by_source])["source"]
            row["lat"], row["lng"] = (f"{v:.7f}" for v in by_source[best_src])
            row["coord_source"] = best_src
            pts = list(by_source.values())
            if len(pts) > 1:
                row["coord_spread_m"] = str(int(max(haversine(p, q) for p in pts for q in pts)))

        reasons = []
        if r and not row["name"]:
            reasons.append("no-name: on the roster and nobody names it")
        if r and not c:
            reasons.append("roster-only: tolerated address invisible to every directory")
        if not r and (row["status"] or "").lower() == "open":
            reasons.append("off-roster-but-open: a source says open at an address the burgemeester does not tolerate")
        if len({fold(x["value"]) for x in c.get("name", [])}) > 1:
            reasons.append("name-conflict: sources disagree on the current name")
        if row["coord_spread_m"] and int(row["coord_spread_m"]) > COORD_CONFLICT_M:
            reasons.append(f"coord-conflict: {row['coord_spread_m']} m between sources")
        if not any(sources.get(x["source"], {}).get("osm_ok") for x in lat_claims):
            reasons.append("no-usable-coord: no coordinate from a source we may publish")
        if not row["osm_id"]:
            reasons.append("no-osm-link: not yet reconciled with OpenStreetMap")
        m = re.search(r"(19|20)\d{2}", row["latest_menu_photo"] or "")
        if m and 2026 - int(m.group(0)) > STALE_MENU_YEARS:
            reasons.append(f"stale-menu: newest menu photo is from {m.group(0)}")
        if any(x["source"] == "user-lead" for f in c.values() for x in f):
            reasons.append("unverified-lead: a remembered claim needs a citation or a visit")

        # Suffix disagreement is expected often enough that it is a note, not an alarm:
        # the join deliberately ignores huisletters, so this is where they get reported.
        if r and r["suffix"] and row["address_as_written"]:
            written = re.search(r"\d+\s*([A-Za-z]{1,2})\b", row["address_as_written"])
            if written and written.group(1).upper() != r["suffix"].upper():
                reasons.append(f"suffix-mismatch: roster says {r['number']}{r['suffix']}, "
                               f"a source writes {written.group(0).strip()}")

        row["review_reasons"] = " | ".join(reasons)
        row["sources_seen"] = ";".join(sorted({x["source"] for f in c.values() for x in f}))
        rows.append(row)

        for field, cl in c.items():
            for x in cl:
                if sources.get(x["source"], {}).get("osm_ok"):
                    safe_rows.append({**x, "license": sources[x["source"]]["license"]})

    # Cross-row pass. An unnamed tolerated address a few doors from a NAMED off-roster
    # address on the same street is almost always one shop wearing two house numbers --
    # the roster and the shopfront disagree, as with Bulldog at Oudezijds Voorburgwal
    # 88 versus 90. Pairing them turns a queue of alarms into a queue of questions, and
    # one look at the door settles each pair.
    by_street = defaultdict(list)
    for row in rows:
        if row["street"] and row["number"].isdigit():
            by_street[street_key(row["street"])].append(row)

    for group in by_street.values():
        for a in group:
            if a["tolerated"] != "yes" or a["name"]:
                continue
            near = [b for b in group
                    if b["tolerated"] == "no" and b["name"]
                    and abs(int(b["number"]) - int(a["number"])) <= 4]
            if near:
                b = min(near, key=lambda x: abs(int(x["number"]) - int(a["number"])))
                a["probable_pair"] = b["subject_id"]
                b["probable_pair"] = a["subject_id"]
                hint = (f"probable-renumbering: likely the same shop as {b['name']} at "
                        f"{b['street']} {b['number']}; check the number on the door")
                for row in (a, b):
                    row["review_reasons"] = (row["review_reasons"] + " | " + hint).strip(" |")

    # Priority is assigned last, so the pairing pass can demote what it explains.
    HIGH = ("no-name", "roster-only", "off-roster-but-open", "name-conflict", "coord-conflict")
    for row in rows:
        reasons = [x.strip() for x in row["review_reasons"].split("|") if x.strip()]
        alarming = [x for x in reasons if x.startswith(HIGH)]
        if alarming and row["probable_pair"]:
            row["review_priority"] = "paired"        # explained, needs one look rather than a hunt
        elif alarming:
            row["review_priority"] = "high"
        elif reasons:
            row["review_priority"] = "medium"
        else:
            row["review_priority"] = "low"

    with open(os.path.join(HERE, "data", "register.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=COLUMNS)
        w.writeheader()
        w.writerows(rows)

    with open(os.path.join(HERE, "data", "osm-safe.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["subject", "field", "value", "source", "observed", "confidence", "note", "license"])
        w.writeheader()
        w.writerows(safe_rows)

    prio = defaultdict(int)
    for row in rows:
        prio[row["review_priority"]] += 1
    print(f"{len(rows)} subjects: {sum(1 for x in rows if x['tolerated']=='yes')} tolerated, "
          f"{sum(1 for x in rows if x['tolerated']=='no')} off-roster")
    print(f"named: {sum(1 for x in rows if x['name'])} | "
          f"review high {prio['high']}, medium {prio['medium']}, low {prio['low']}")
    print(f"osm-safe claims: {len(safe_rows)}")


if __name__ == "__main__":
    main()
