#!/usr/bin/env python3
"""Import the 2009 survey out of the old Coffeeshops trunk.

Two sources live in that checkout and they must NOT be conflated:

  photos-2009      225 iPhone 3GS photographs. Own camera, own GPS, own hand.
                   EXIF carries position, bearing and fix quality. OSM-eligible.

  placesdata-2011  PlacesData.csv, 228 places, 56 columns. Mixed provenance:
                   every row has a GooglePlacePage and a lat/lng that was almost
                   certainly geocoded from it. NOT OSM-eligible, per-cell
                   untangling being impossible after this long.

So the photograph supplies the coordinate and the spreadsheet supplies the
identity, and only the first of those can ever reach a changeset.

The spreadsheet has a four-row preamble before the data: machine names (the
real CSV header), descriptions, types, display roles, human labels.
"""

import csv
import os
import sys
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from addr import parse_freeform, subject_id, dutch_title

TRUNK = os.path.expanduser("~/GroundUp/Code/Coffeeshops/trunk/Coffeeshops")
SHEET = os.path.join(TRUNK, "Spreadsheets/PlacesData.csv")
PHOTOS = os.path.join(TRUNK, "PicturesOriginal")
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data")

PREAMBLE = 4  # rows after the header that describe the schema rather than a place


def dms(v, ref):
    """EXIF rational DMS to signed decimal. iPhones write degrees + decimal minutes."""
    d, m, s = (float(x) for x in v)
    dec = d + m / 60.0 + s / 3600.0
    return -dec if ref in ("S", "W") else dec


def read_exif(path):
    from PIL import ExifTags, Image

    try:
        raw = Image.open(path)._getexif() or {}
    except Exception as e:
        return {"error": str(e)}
    tags = {ExifTags.TAGS.get(k, k): v for k, v in raw.items()}
    g = {ExifTags.GPSTAGS.get(k, k): v for k, v in (tags.get("GPSInfo") or {}).items()}
    out = {}
    when = tags.get("DateTimeOriginal") or tags.get("DateTime")
    if when:
        try:
            out["observed"] = datetime.strptime(when, "%Y:%m:%d %H:%M:%S").date().isoformat()
        except ValueError:
            pass
    out["camera"] = " ".join(x for x in (tags.get("Make"), tags.get("Model")) if x).strip()
    if "GPSLatitude" in g and "GPSLongitude" in g:
        out["lat"] = round(dms(g["GPSLatitude"], g.get("GPSLatitudeRef", "N")), 7)
        out["lng"] = round(dms(g["GPSLongitude"], g.get("GPSLongitudeRef", "E")), 7)
    if "GPSImgDirection" in g:
        out["heading"] = round(float(g["GPSImgDirection"]), 1)
    if "GPSDOP" in g:
        # Dilution of precision, unitless. Under 5 is a usable urban fix; the
        # iPhone 3GS in a canal street routinely did worse.
        out["dop"] = round(float(g["GPSDOP"]), 1)
    if "GPSAltitude" in g:
        out["alt"] = round(float(g["GPSAltitude"]), 1)
    return out


def load_sheet():
    with open(SHEET, encoding="utf-8", errors="replace") as f:
        rows = list(csv.reader(f))
    hdr = rows[0]
    idx = {h: n for n, h in enumerate(hdr)}
    places = []
    for r in rows[1 + PREAMBLE:]:
        # Ragged by design: the exporter drops trailing empty cells, and most rows
        # are short because most of the 56 columns were aspirational. Pad, never skip.
        r = r + [""] * (len(hdr) - len(r))
        if not r[idx["Name"]].strip():
            continue
        get = lambda k: r[idx[k]].strip() if k in idx else ""
        places.append({k: get(k) for k in hdr})
    return places


def photo_index():
    """Case-insensitive basename to path. The sheet says img_0201, the disk says IMG_0201.JPG."""
    out = {}
    for f in sorted(os.listdir(PHOTOS)):
        if f.startswith("."):
            continue
        base, ext = os.path.splitext(f)
        if ext.lower() in (".jpg", ".jpeg", ".heic", ".png"):
            out[base.lower()] = f
    return out


def main():
    places = load_sheet()
    photos = photo_index()
    claims = []
    matched = unmatched = nogps = 0

    def claim(subj, field, value, source, observed, confidence, note=""):
        claims.append({
            "subject": subj, "field": field, "value": value, "source": source,
            "observed": observed, "confidence": confidence, "note": note,
        })

    for p in places:
        a = parse_freeform(p["Address"])
        if not a["street"]:
            continue
        subj = subject_id(a["street"], a["number"], a["suffix"])
        seen = "2011-07-18"  # the spreadsheet's own mtime; nothing finer survives

        # Identity, from the spreadsheet. Tainted for OSM, fine for us.
        claim(subj, "name", p["Name"], "placesdata-2011", seen, 0.7)
        if p.get("SortName") and p["SortName"] != p["Name"]:
            claim(subj, "sort_name", p["SortName"], "placesdata-2011", seen, 0.7)
        if p.get("AlsoKnownAs"):
            claim(subj, "also_known_as", p["AlsoKnownAs"], "placesdata-2011", seen, 0.6)
        if p.get("ClassName"):
            claim(subj, "kind", p["ClassName"].lower(), "placesdata-2011", seen, 0.8)
        if p.get("PhoneNumber"):
            claim(subj, "phone", p["PhoneNumber"], "placesdata-2011", seen, 0.5,
                  "seventeen years stale, verify before use")
        if p.get("WebSite"):
            claim(subj, "website", p["WebSite"], "placesdata-2011", seen, 0.4)
        if p.get("FoursquareVenue"):
            claim(subj, "foursquare", p["FoursquareVenue"], "placesdata-2011", seen, 0.5)

        # The spreadsheet's own coordinate. Quarantined: same row as a Google Place page.
        if p.get("Latitude") and p.get("Longitude"):
            try:
                claim(subj, "coordinate", "%s,%s" % (float(p["Latitude"]), float(p["Longitude"])),
                      "placesdata-2011", seen, 0.4,
                      "geocoded alongside a GooglePlacePage; never eligible for OSM")
            except ValueError:
                pass

        # It was trading in 2009 with a photograph to prove it.
        pic = p.get("Picture", "").lower()
        fn = photos.get(pic) or photos.get(os.path.splitext(pic)[0])
        if not fn:
            unmatched += 1
            if p.get("PictureProblem"):
                claim(subj, "photo_wanted", p["PictureProblem"], "placesdata-2011", seen, 0.9,
                      "retake request from the 2009 survey, still open")
            continue

        matched += 1
        ex = read_exif(os.path.join(PHOTOS, fn))
        obs = ex.get("observed", "2009-10-01")
        claim(subj, "key_photo", "PicturesOriginal/" + fn, "photos-2009", obs, 1.0, ex.get("camera", ""))
        claim(subj, "trading", "true", "photos-2009", obs, 1.0,
              "photographed open; presence attested, not a claim about today")
        if "lat" in ex:
            note = "own GPS"
            if "dop" in ex:
                note += ", DOP %s" % ex["dop"]
            if "heading" in ex:
                note += ", camera bearing %s deg true" % ex["heading"]
            conf = 0.9 if ex.get("dop", 9) <= 5 else 0.6
            claim(subj, "coordinate", "%s,%s" % (ex["lat"], ex["lng"]), "photos-2009", obs, conf, note)
            if "heading" in ex:
                claim(subj, "photo_heading", str(ex["heading"]), "photos-2009", obs, 1.0,
                      "the shopfront lies along this bearing from the fix")
        else:
            nogps += 1

    os.makedirs(OUT, exist_ok=True)
    path = os.path.join(OUT, "claims-2009.csv")
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["subject", "field", "value", "source",
                                          "observed", "confidence", "note"])
        w.writeheader()
        w.writerows(claims)

    subjects = len({c["subject"] for c in claims})
    own = [c for c in claims if c["source"] == "photos-2009" and c["field"] == "coordinate"]
    print("%d places read, %d photos matched, %d unmatched, %d matched without GPS"
          % (len(places), matched, unmatched, nogps))
    print("%d claims over %d subjects -> %s" % (len(claims), subjects, os.path.relpath(path)))
    print("%d OSM-eligible coordinates from your own camera" % len(own))


if __name__ == "__main__":
    main()
