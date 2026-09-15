#!/usr/bin/env python3
"""Fetch the authoritative spine: Amsterdam's gedooglijst, from the primary source.

The list is published as a beleidsregel of the burgemeester on
lokaleregelgeving.overheid.nl, republished in full every time it changes, with a
"Geldend van" validity date. Version 2 is in force from 2026-03-05.

Official Dutch publications carry no copyright (Auteurswet art. 11), which is why
this is the one input that is unambiguously safe to hold, republish, and reconcile
against OpenStreetMap.

Usage:  python3 scripts/fetch_gedooglijst.py [version]
Writes: data/gedooglijst-<valid_from>.csv  and prints the row count.
"""

import csv
import html
import os
import re
import sys
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from addr import split_number

CVDR = "CVDR756282"
URL = "https://lokaleregelgeving.overheid.nl/{}/{}"
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def fetch(version):
    url = URL.format(CVDR, version)
    req = urllib.request.Request(url, headers={"User-Agent": "amsterdank-dataset/0.1 (github.com/SimHacker)"})
    with urllib.request.urlopen(req) as r:
        return url, r.read().decode("utf-8", "replace")


def strip_tags(s):
    return html.unescape(re.sub(r"<[^>]+>", "", s)).replace("\xa0", " ").strip()


def parse(page):
    valid = ""
    m = re.search(r"Geldend van\s*([0-9]{2})-([0-9]{2})-([0-9]{4})", page)
    if m:
        valid = f"{m.group(3)}-{m.group(2)}-{m.group(1)}"

    rows = []
    for tr in re.findall(r"<tr[^>]*>(.*?)</tr>", page, re.S):
        cells = [strip_tags(c) for c in re.findall(r"<t[dh][^>]*>(.*?)</t[dh]>", tr, re.S)]
        # street | number | huisletter/toevoeging | postcode digits | postcode letters
        if len(cells) != 5 or not re.match(r"^\d+", cells[1].strip()):
            continue
        street, number, suffix, pc4, pc2 = cells
        # The roster is hand-typed and not uniform: two rows carry the huisletter
        # inside the number cell ("14B", "4c") and one has a lowercase postcode.
        # A parser that demands a bare integer here silently loses Hoekenrode 14B
        # and Tt. Vasumweg 4C, which is how you end up reporting 165 or 166.
        num, tail = split_number(number)
        rows.append({
            "street_raw": street,
            "number": num,
            "suffix": (suffix.strip() or tail).upper(),
            "postcode": f"{pc4.strip()}{pc2.strip().upper()}",
        })
    return valid, rows


def main():
    version = sys.argv[1] if len(sys.argv) > 1 else "2"
    url, page = fetch(version)
    valid, rows = parse(page)
    if not rows:
        sys.exit("no address rows found -- the page layout changed, inspect it by hand")

    out = os.path.join(HERE, "data", f"gedooglijst-{valid or 'unknown'}.csv")
    with open(out, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["street_raw", "number", "suffix", "postcode", "valid_from", "source_url"])
        w.writeheader()
        for r in rows:
            r["valid_from"] = valid
            r["source_url"] = url
            w.writerow(r)

    print(f"{len(rows)} tolerated addresses, valid from {valid}")
    print(f"wrote {os.path.relpath(out, HERE)}")


if __name__ == "__main__":
    main()
