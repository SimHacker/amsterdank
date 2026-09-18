# SURVEY — one rider, 245 doors, and the worklist that already existed

The register has 246 addresses and one of them is finished. The other 245 each carry at least one
question that a person standing at the door could settle by looking, and those questions were not
invented for this document — `build_places.py` wrote them into `review.reasons` while projecting the
claims, months before anyone thought about riding out to answer them.

`scripts/build_worklist.py` reads those reasons and emits `data/worklist.yml`: 29 rounds, ordered so
that consecutive stops are neighbours, with the question and the frame to take at each door.

## Being the customer first

This is a one-person survey with no crowd, no credit system and nobody to thank, and that is the
point rather than a limitation. A worklist that only works with a hundred volunteers is not a tool,
it is a business plan. If it cannot make a single Saturday afternoon more productive for the person
who wrote it, the crowd version was never going to work either — it would just have failed more
slowly and with other people's time.

So the order is: ride it, find out which questions are wrong, find out which prompts are useless at
a door in the rain, fix those, and only then hand it to anyone else. What other people eventually get
is a route sheet that has been ridden.

The same argument sits under `apps/ebike-safari/design/mechanical-turk-ebike.md` in the WWSFF repo,
which describes the multi-rider version. This is its v0, and it is deliberately the boring one.

## What is outstanding

| Question | Doors | What settles it |
|---|---|---|
| `stale-everything` | 222 | Still trading, still that name |
| `off-roster-unexplained` | 78 | It left the roster and nobody knows why. What is there now? |
| `huisletter-unverified` | 53 | The roster claims a house letter; the door is the authority |
| `no-coordinate` | 23 | No fix on record at all. Standing there with a GPS *is* the deliverable |
| `no-evidence-since-2011` | 20 | Anything |
| `no-name` / `never-photographed` | 18 each | The sign; the front |
| One-offs | ~12 | A cat, a junk collection, a seat, a dolphin, some horse doors |

The 78 off-roster doors are the interesting half of the job. A shop that vanished from the
gedooglijst is a hole in the record, and the repo's rule is that **absence means unknown, never
false** — so "off the roster" is a question, not a closure. Turning one into a closure requires a
date, a cause and a document, which is what `places/vijzelgracht-33/` looks like when it is done
properly, and that is one record out of 246.

Twelve of the one-offs exist only because somebody hand-wrote them, and they are the reason to go:
whether the very old cat in the Jordaan junk shop has a successor, which seat in the 420 Café was
John Sinclair's, which doors on Marnixstraat belonged to Amsterdam's first horse butchery. No
generator would ever ask those.

## The protocol

**Ride a round, not a list.** Each round is 18 stops in Hilbert order, which is a compact blob of
city rather than a stripe across it. One round is an afternoon. Take them in either direction.

**One frame, two answers.** Where the number plate and the name board fit in a single photograph,
that photograph closes both `huisletter-unverified` and `stale-everything`. The worklist marks these
with `one_frame`. Framing for two questions instead of one halves the survey.

**Say it, do not type it.** Speak the answer; the phone is in a mount and your hands are on the bars.
The class word first, then whatever a reader needs to understand it — the door says 36 not 36H, the
old lettering still shows under the paint, the neighbour is numbered 34 so the renumbering theory
holds. The sentence is the payload, not the checkbox.

**Exterior from public space. Interior only if invited.** Dutch coffeeshops generally do not welcome
cameras inside, and the menu board is the sharpest case: it is what the business sells, photographed
in a private room. Ask, and if the answer is no it stays no and nothing is recorded from inside. If
the answer is yes, record who said yes and when, because a granted permission that nobody wrote down
is indistinguishable from no permission at all.

**A hand-written question always wins.** Three records carry `review.one_look_settles`, a sentence
written by a person about that specific door. The generator uses it verbatim and marks the stop
`ask_is_hand_written: true`. Same rule as everywhere else in this repo: the generator proposes and
never argues with a human.

**Nothing is answered "no".** A door you could not read, a shop that was shut at the time, a number
hidden behind scaffolding — all of those are `illegible` and schedule a revisit. A guess is not an
answer, and *closed* is a conclusion that needs a document.

## Where the answers go

**Not into the worklist.** `data/worklist.yml` is derived, holds no findings, and can be deleted at
any time. Answers go into `places/<id>/PLACE.yml`:

```yaml
survey:
  - visited: 2026-09-20          # append; never edit the 2009 entry
    by: don
    key_photo: survey-2026/IMG_1234.JPG
    open_at_visit: true
    coordinate: { lat: 52.3671, lng: 4.8956, heading: 152.9, extractor: PIL-exif }
    note: "Door plate reads 36, no huisletter. Neighbour is 34. Name board still Bushdocter 1."
```

Then regenerate the worklist and that question is gone from it. Claims accumulate and are never
replaced, so a 2026 observation sits beside the 2009 one and any disagreement between them is
preserved — which is the interesting part, since a disagreement across seventeen years is a history
of the street rather than a data error.

## Why doing it yourself unblocks the OSM side

The register is boxed in by licensing. The gedooglijst is `osm_ok: true` and authoritative about
which addresses may sell, and it says nothing about names, hours, or whether a door is open today.
Everything that does say those things — the compilations in `sources.yml` — is `osm_ok: false`, so
the facts may be *known* here and still unusable upstream.

A first-party doorstep observation has no such problem. Your own photograph, your own GPS fix, your
own reading of a sign is the cleanest source this project can have, and it is `osm_ok: true` by
construction. Riding the worklist is therefore not only a data-quality exercise: it is the only path
that converts what the repo suspects into something it may contribute.

That is also why the survey must not consult the unlicensed compilations at the door. A name recalled
from a directory and then "observed" on site is laundering with extra steps. Read the sign, or record
that you could not.

↑ [`SKILL.md`](SKILL.md) · [`GHOSTS.md`](GHOSTS.md) · [`BUDTENDERS.md`](BUDTENDERS.md) · [`../../sources.yml`](../../sources.yml) · `scripts/build_worklist.py`
