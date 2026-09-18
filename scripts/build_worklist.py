#!/usr/bin/env python3
"""Turn places/*/PLACE.yml into a rideable survey worklist: data/worklist.yml (+ .geojson).

THE TASK TAXONOMY ALREADY EXISTS. build_places.py wrote review.reasons on every record —
huisletter-unverified, off-roster-unexplained, no-coordinate, stale-everything — and each of
those is already a question answerable at a door by looking. This script does not invent
questions; it reads the ones the data is already asking and puts them in an order you can
ride.

WHAT GOES IN:
  places/<id>/PLACE.yml    canonical, hand-editable, the only truth here
  review.reasons           the questions
  coordinates.claims       our own fixes only (photos-2009), for ordering
  address.postcode         fallback grouping for the 23 records with no fix at all

WHAT COMES OUT:
  data/worklist.yml        derived. NEVER hand-edit; change PLACE.yml and regenerate.
  data/worklist.geojson    same rounds as points, for the viewer / phone map

ORDERING: stops are sorted along a Hilbert curve so consecutive stops are near each other,
then cut into rounds of ROUND_SIZE. A Hilbert chunk is a compact blob of city rather than the
stripe you get from sorting by latitude, which is the whole reason not to sort by latitude.

WHAT STAYS OUT: anything from an osm_ok:false source. This worklist exists to produce
first-party observations, which are the cleanest source the project can have; seeding it with
someone else's compilation would defeat that. Names appear only where PLACE.yml already
carries them, and they are shown as "expected", never as answers.

Usage: python3 scripts/build_worklist.py [--round-size 18]
"""

import argparse
import os
import sys
from collections import defaultdict

import yaml

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PLACES = os.path.join(REPO, "places")
OUT_YML = os.path.join(REPO, "data", "worklist.yml")
OUT_GEOJSON = os.path.join(REPO, "data", "worklist.geojson")

ROUND_SIZE = 18

# review.reason -> (question you can answer by looking, what to capture)
# Order matters: the first matching reason names the task, the rest ride along as also_asks.
TASKS = {
    "no-coordinate": (
        "Stand at the door. Take the fix and the camera bearing.",
        "One frame square-on to the door, GPS held still.",
    ),
    "never-photographed": (
        "Nobody has ever photographed this door. Do that.",
        "Door number AND name board in one frame if they fit.",
    ),
    "no-name": (
        "What is it called? Read the sign, not a directory.",
        "The name board, legible.",
    ),
    "off-roster-unexplained": (
        "Not on the current roster and nobody knows why. What is at this address now?",
        "Whatever is actually there — successor business, vacancy, or building.",
    ),
    "probable-renumbering": (
        "The number may have moved. Which door is it, and what are the neighbours numbered?",
        "This door plus the doors either side, numbers legible.",
    ),
    "huisletter-unverified": (
        "The roster says a huisletter the door may disagree with. What does the door say?",
        "The number plate itself, close and sharp.",
    ),
    "no-evidence-since-2011": (
        "Nothing since 2011. Anything at all is an improvement.",
        "Anything.",
    ),
    "stale-everything": (
        "Still trading? Still that name?",
        "Front, with the name and the number.",
    ),
    "never-surveyed": (
        "Never been looked at. Everything is open.",
        "Number, sign, and the front as it stands.",
    ),
    "coord-conflict": (
        "Two fixes disagree by more than the street is wide. Settle it at the door.",
        "One frame square-on with the GPS held still, plus the neighbours' numbers.",
    ),
    "number-unverified": (
        "What number is actually on this door?",
        "The number plate.",
    ),
    "name-unverified": (
        "Read the name off the building, not off a directory.",
        "The name board.",
    ),
    "rename-undated": (
        "It has been renamed and nobody knows when. What is on the sign now?",
        "The sign, and any old lettering still showing through.",
    ),
    "same-business-or-new": (
        "New name — a repaint, or a different operator? Ask inside if it feels welcome.",
        "The sign; the interior only with permission.",
    ),
}

# Answered from a chair, not a saddle. Kept in the worklist, flagged, never routed.
DESK = {"no-osm-link"}

# Not door checks at all. Out of the riding rounds.
NOT_A_SURVEY = {"closed-confirmed", "ceremony-unvisited"}

# One-offs from hand-authored records. No general form, so they are named and carried through
# rather than folded into a generic prompt. Losing these would be losing the reason to go.
FREEFORM = {
    "cat-status-unknown": "Is there a cat, and what is its name? Do not carry the old cat forward.",
    "junk-status-unknown": "Is the junk still there? The collection was the room.",
    "seat-unlocated": "Which seat was his. Don knows; the file does not.",
    "horse-doors-unlocated": "Which doors belonged to the horse butchery. The history is the door's, not the tenant's.",
    "mascot-ungranted": "The house has a mascot and no grant. Ask whether they want one; take no for an answer.",
    "sibling-shop-unresolved": "How this door relates to its sibling shop.",
}


def hilbert_d(x, y, order=16):
    """Hilbert curve index for integer x,y in [0, 2**order). Standard xy2d."""
    rx = ry = 0
    d = 0
    s = 1 << (order - 1)
    while s > 0:
        rx = 1 if (x & s) > 0 else 0
        ry = 1 if (y & s) > 0 else 0
        d += s * s * ((3 * rx) ^ ry)
        # rotate
        if ry == 0:
            if rx == 1:
                x = s - 1 - x
                y = s - 1 - y
            x, y = y, x
        s >>= 1
    return d


def load_places():
    for entry in sorted(os.listdir(PLACES)):
        path = os.path.join(PLACES, entry, "PLACE.yml")
        if not os.path.isfile(path):
            continue
        try:
            with open(path) as f:
                doc = yaml.safe_load(f) or {}
        except yaml.YAMLError as e:
            print(f"  skip {entry}: unparseable ({e.__class__.__name__})", file=sys.stderr)
            continue
        doc["_id"] = entry
        yield doc


def own_fix(doc):
    """First coordinate claim. build_places only ever publishes our own, so any claim is ours."""
    for claim in (doc.get("coordinates") or {}).get("claims") or []:
        if "lat" in claim and "lng" in claim:
            return float(claim["lat"]), float(claim["lng"])
    return None


def make_stop(doc):
    reasons = list((doc.get("review") or {}).get("reasons") or [])
    survey_reasons = [r for r in reasons if r not in NOT_A_SURVEY]
    if not survey_reasons:
        return None

    named = [r for r in survey_reasons if r in TASKS]
    if not named:
        ask, capture = "Open question with no standard form — read the record before you go.", "Use judgement."
    else:
        ask, capture = TASKS[named[0]]

    # A hand-written one_look_settles beats any generated question, so it wins outright.
    # Same rule as build_places.py: the generator fills gaps and never argues with a human.
    hand = (doc.get("review") or {}).get("one_look_settles")
    if hand:
        ask = hand
        capture = "Whatever answers that, in as few frames as it takes."

    addr = doc.get("address") or {}
    number = f"{addr.get('number', '?')}{addr.get('suffix', '') or ''}"
    names = doc.get("names") or {}
    expected = names.get("current") or names.get("final")

    stop = {
        "id": doc["_id"],
        "at": f"{addr.get('street', '?')} {number}",
        "postcode": addr.get("postcode"),
        "ask": ask,
        "capture": capture,
        "because": survey_reasons,
    }
    if hand:
        stop["ask_is_hand_written"] = True

    # Anything the primary question does not cover is surfaced, never swallowed.
    also = [FREEFORM[r] for r in survey_reasons if r in FREEFORM]
    also += [
        f"{r} — no standard question for this one; read the record"
        for r in survey_reasons
        if r not in TASKS and r not in FREEFORM and r not in DESK
    ]
    if also:
        stop["also_ask"] = also

    desk = [r for r in survey_reasons if r in DESK]
    if desk:
        stop["at_the_desk"] = desk

    if expected:
        stop["expected_name"] = f"{expected} — expected, not confirmed"
    if (doc.get("gedoog") or {}).get("tolerated") is False:
        stop["off_roster"] = True

    # The efficiency case: one frame settles two questions at once.
    if "huisletter-unverified" in survey_reasons and (
        "never-photographed" in survey_reasons or "stale-everything" in survey_reasons
    ):
        stop["one_frame"] = "Number plate and name board together closes both."

    fix = own_fix(doc)
    if fix:
        stop["lat"], stop["lng"] = fix
    else:
        stop["find_the_door"] = True
    return stop


def rounds_from(stops, round_size):
    """Hilbert-order the located stops; group the unlocated ones by postcode district."""
    located = [s for s in stops if "lat" in s]
    unlocated = [s for s in stops if "lat" not in s]

    if located:
        lats = [s["lat"] for s in located]
        lngs = [s["lng"] for s in located]
        lat0, lat1 = min(lats), max(lats)
        lng0, lng1 = min(lngs), max(lngs)
        span_lat = (lat1 - lat0) or 1e-9
        span_lng = (lng1 - lng0) or 1e-9
        n = 1 << 16
        for s in located:
            x = int((s["lng"] - lng0) / span_lng * (n - 1))
            y = int((s["lat"] - lat0) / span_lat * (n - 1))
            s["_h"] = hilbert_d(x, y)
        located.sort(key=lambda s: s["_h"])
        for s in located:
            del s["_h"]

    out = []
    for i in range(0, len(located), round_size):
        chunk = located[i : i + round_size]
        out.append(
            {
                "round": len(out) + 1,
                "kind": "ride",
                "stops": len(chunk),
                "note": "Hilbert-ordered, so consecutive stops are neighbours. Ride it in either direction.",
                "list": chunk,
            }
        )

    by_district = defaultdict(list)
    for s in unlocated:
        pc = (s.get("postcode") or "unknown")
        by_district[pc[:4] if pc != "unknown" else "unknown"].append(s)
    for district, chunk in sorted(by_district.items()):
        out.append(
            {
                "round": len(out) + 1,
                "kind": "find_the_door",
                "district": district,
                "stops": len(chunk),
                "note": "No coordinate on record. Find the door, then the fix is the deliverable.",
                "list": chunk,
            }
        )
    return out


HEADER = """\
# GENERATED by scripts/build_worklist.py — DERIVED FILE, DO NOT HAND-EDIT.
# The questions come from review.reasons in places/*/PLACE.yml. To change a question, change
# the record (or the TASKS table in the script) and regenerate.
#
# Answers do NOT come back here. They go into the place's own PLACE.yml as a new survey entry
# and new claims, because claims accumulate and are never replaced. This file is a route sheet;
# it holds no findings and is safe to delete at any time.
#
# Protocol, permissions and what counts as an answer: skills/coffeeshop/SURVEY.md
"""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--round-size", type=int, default=ROUND_SIZE)
    args = ap.parse_args()

    stops, skipped, resolved = [], 0, 0
    for doc in load_places():
        stop = make_stop(doc)
        if stop is None:
            resolved += 1
            continue
        stops.append(stop)

    rounds = rounds_from(stops, args.round_size)

    reason_counts = defaultdict(int)
    for s in stops:
        for r in s["because"]:
            reason_counts[r] += 1

    doc = {
        "worklist": {
            "generated_from": "places/*/PLACE.yml",
            "open_stops": len(stops),
            "resolved_or_not_a_door_check": resolved,
            "rounds": len(rounds),
            "questions_outstanding": dict(sorted(reason_counts.items(), key=lambda kv: -kv[1])),
        },
        "rounds": rounds,
    }

    os.makedirs(os.path.dirname(OUT_YML), exist_ok=True)
    with open(OUT_YML, "w") as f:
        f.write(HEADER)
        yaml.safe_dump(doc, f, sort_keys=False, allow_unicode=True, width=100)

    features = []
    for rnd in rounds:
        for i, s in enumerate(rnd["list"], 1):
            if "lat" not in s:
                continue
            features.append(
                {
                    "type": "Feature",
                    "geometry": {"type": "Point", "coordinates": [s["lng"], s["lat"]]},
                    "properties": {
                        "id": s["id"],
                        "at": s["at"],
                        "round": rnd["round"],
                        "order": i,
                        "ask": s["ask"],
                        "because": ", ".join(s["because"]),
                    },
                }
            )
    import json

    with open(OUT_GEOJSON, "w") as f:
        json.dump({"type": "FeatureCollection", "features": features}, f, indent=1)

    print(f"{len(stops)} open stops, {resolved} resolved, {len(rounds)} rounds")
    print(f"  {OUT_YML}")
    print(f"  {OUT_GEOJSON} ({len(features)} located)")


if __name__ == "__main__":
    main()
