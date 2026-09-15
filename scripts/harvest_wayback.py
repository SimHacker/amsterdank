#!/usr/bin/env python3
"""Recover amsterdank.nl from the Internet Archive, 2013 snapshot.

The old site was driven by the TurboGears backend, whose place_table had a
comment_table joined to it. PlacesData.csv is dated 2011-07-18; the crawl is
2013-07-28. Two years of edits happened in the live database in between, and the
CSV never saw them -- so these pages are the only surviving copy of whatever was
written after the export, including user comments.

URL shape: http://amsterdank.nl/index/Coffeeshop_<N>, where N is the Identifier
column in PlacesData.csv. Betty Too is Coffeeshop_26, verified against the
archived URL in Don's own email. 420 Cafe is Coffeeshop_2.

PROVENANCE. This is Don's own site being recovered, so the content is his, with
two exceptions worth keeping straight:

  - user comments were written by other people and are theirs, not ours
  - coordinates on those pages came from the 2011 geocoding, which sat next to a
    GooglePlacePage, so they stay quarantined exactly as in claims-2009.csv

The Archive is flaky and rate-limits hard. This is deliberately slow, resumable,
and does nothing clever: cached files are never refetched, so re-running after a
429 storm picks up where it stopped.
"""

import json
import os
import random
import re
import sys
import time
import urllib.error
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
CACHE = os.path.join(HERE, "..", "data", "third-party", "wayback")  # gitignored
OUT = os.path.join(HERE, "..", "data")
SNAPSHOT = "20130728"
BASE = "http://web.archive.org/web/%sid_/http://amsterdank.nl/index/Coffeeshop_%d"
UA = "amsterdank-recovery/1.0 (own-site recovery; simhacker@gmail.com)"

PAUSE = 3.0          # seconds between requests; the Archive is a charity, not a CDN
MAX_TRIES = 4
BACKOFF = 20.0       # first retry wait on 429/503, doubling


def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    wait = BACKOFF
    for attempt in range(1, MAX_TRIES + 1):
        try:
            with urllib.request.urlopen(req, timeout=45) as r:
                return r.read().decode("utf-8", "replace")
        except urllib.error.HTTPError as e:
            if e.code in (429, 503, 502, 504):
                # Rate limited or the Archive is having a day. Wait and mean it.
                print("    %d, waiting %.0fs (try %d/%d)" % (e.code, wait, attempt, MAX_TRIES))
                time.sleep(wait + random.uniform(0, 5))
                wait *= 2
                continue
            if e.code == 404:
                return None
            raise
        except Exception as e:
            print("    %s (try %d/%d)" % (e, attempt, MAX_TRIES))
            time.sleep(wait)
            wait *= 2
    return None


def strip_tags(html):
    html = re.sub(r"(?is)<(script|style).*?</\1>", " ", html)
    html = re.sub(r"(?is)<br\s*/?>|</p>|</div>|</tr>", "\n", html)
    html = re.sub(r"(?s)<[^>]+>", " ", html)
    html = (html.replace("&nbsp;", " ").replace("&amp;", "&")
                .replace("&lt;", "<").replace("&gt;", ">").replace("&#39;", "'")
                .replace("&quot;", '"').replace("&shy;", ""))
    html = re.sub(r"[ \t]+", " ", html)
    return "\n".join(ln.strip() for ln in html.split("\n") if ln.strip())


def parse(html):
    """Pull what the page shows. Deliberately shallow: keep the text, note the
    structure, and leave interpretation to a human reading the cache."""
    out = {}
    m = re.search(r"(?is)<title>(.*?)</title>", html)
    if m:
        out["title"] = strip_tags(m.group(1))
    # The Wayback toolbar injects its own markup; drop everything above the
    # archived document so it does not end up in the text.
    body = re.split(r"(?i)<!--\s*END WAYBACK TOOLBAR INSERT\s*-->", html)[-1]
    out["text"] = strip_tags(body)
    out["links"] = sorted({
        u for u in re.findall(r'(?i)href="(http[^"]+)"', body)
        if "web.archive.org" not in u and "amsterdank.nl" not in u
    })
    out["images"] = sorted(set(re.findall(r'(?i)src="([^"]+\.(?:jpg|jpeg|png|gif))"', body)))
    return out


def main():
    lo, hi = 1, int(sys.argv[1]) if len(sys.argv) > 1 else 240
    os.makedirs(CACHE, exist_ok=True)
    records, fetched, cached, missing = [], 0, 0, []

    for n in range(lo, hi + 1):
        path = os.path.join(CACHE, "Coffeeshop_%d.html" % n)
        if os.path.exists(path):
            html = open(path, encoding="utf-8", errors="replace").read()
            cached += 1
        else:
            print("Coffeeshop_%d ..." % n)
            html = fetch(BASE % (SNAPSHOT, n))
            if not html:
                missing.append(n)
                time.sleep(PAUSE)
                continue
            with open(path, "w", encoding="utf-8") as f:
                f.write(html)
            fetched += 1
            time.sleep(PAUSE)

        rec = parse(html)
        rec["identifier"] = "Coffeeshop_%d" % n
        rec["archived"] = SNAPSHOT
        records.append(rec)

    with open(os.path.join(OUT, "wayback-2013.json"), "w", encoding="utf-8") as f:
        json.dump(records, f, indent=1, ensure_ascii=False)

    print("\n%d fetched, %d from cache, %d missing" % (fetched, cached, len(missing)))
    if missing:
        print("missing: %s" % ", ".join(str(n) for n in missing[:30]))
    print("%d records -> data/wayback-2013.json" % len(records))
    print("raw HTML cached in data/third-party/wayback/ (gitignored)")
    print("\nNext: read a few pages by hand before writing an importer. The point is to")
    print("find what the 2011 CSV export MISSED -- descriptions and comments written")
    print("into the live site during 2011-2013. Do not import coordinates from these")
    print("pages; they are the quarantined 2011 geocoding.")


if __name__ == "__main__":
    main()
