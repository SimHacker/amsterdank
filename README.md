# amsterdank

An Amsterdam coffeeshop register that holds its own disagreements instead of averaging them
away, built as a [MOOLLM](https://github.com/SimHacker/moollm)-compatible world: every place
is a directory, every record is YAML, and the spreadsheet and the database are outputs
rather than sources.

Code is MIT. The facts are CC0, because a toll booth on a fact defeats the purpose. The
photographs are CC-BY. See [LICENSE](LICENSE) and [LICENSE-DATA](LICENSE-DATA) -- the
licensing is not boilerplate here, it is load-bearing, for reasons in the provenance section.

## Why the data model is shaped like this

Every existing coffeeshop list disagrees with every other one, and the disagreements are the
interesting part. The city's tolerance roster says a shop is at Oudezijds Voorburgwal 88 H;
a directory says 90; the plate on the door says something too. Averaging two coordinates
puts a shop in a canal. Picking a winner throws away the evidence that there was a fight.

So the unit of data is a **claim**: a subject, a field, a value, a source, a date, and a
confidence. A place accumulates claims and keeps them all. Resolution happens at read time
by source preference, and it is always reversible, because nothing was deleted.

The **address is the subject**, not the business. Businesses close, get renamed, and are
succeeded by a different shop at the same door, but the door persists. Keying on the address
means a closure is a tenancy ending rather than a row that has to be found and mutated.

## Provenance, which is the whole architecture

The register mixes an official municipal publication, scraped commercial directories, our own
photographs, and OpenStreetMap. These are not interchangeable, and the differences have legal
teeth in both directions:

| Direction | Constraint |
|---|---|
| **Into OSM** | Nothing traced from a proprietary map may ever reach a changeset. Tainted edits get reverted and can flag the account. |
| **Out of OSM** | OSM is ODbL share-alike. Merging it into our records would pull everything under ODbL. |

Both are enforced structurally rather than by intention: [`sources.yml`](sources.yml) marks
every source `osm_ok: true|false`, OSM material stays in `data/osm/` and is referenced by ID
rather than copied, and third-party extracts are `.gitignore`d.

Run the pipeline today and it reports `osm-safe claims: 0`, which is the honest answer: desk
research produces nothing that can lawfully be contributed. **Your own photographs, your own
GPS traces, and a conversation at the door are the only unambiguously clean provenance.**
Field survey is not merely richer. It is the only importable evidence there is.

Nothing in this repository writes to OSM. Survey findings are exported as a worklist, and a
human types them into an OSM editor as their own survey, from their own photographs.

## The 2009 survey

225 photographs from an October 2009 campaign on an iPhone 3GS, every one carrying GPS EXIF
with position, `GPSImgDirection` (the compass bearing the camera faced, which tells you which
side of the street the shopfront is on) and `GPSDOP` for fix quality. Own camera, own hand,
own GPS: clean provenance, seventeen years old, and the ancestor of this repo.

They came with a 56-column spreadsheet whose first four rows describe the schema -- machine
names, then a prose description of every column, then types, then display roles. A
self-documenting schema in a format with no comment syntax, which is
[YAML Jazz](https://github.com/SimHacker/moollm/tree/main/skills/yaml-jazz) invented out of
necessity. `PictureProblem` held retake requests: *scaffolding* at Crush, *blurry* at Rick's,
*missing picture* at Korsakoff. Still open.

## Layout

```
places/<subject-id>/PLACE.yml     canonical record; a place is a directory
places/<subject-id>/survey/       photographs, tracks, notes: the evidence
skills/coffeeshop/                the MOOLLM skill this repo is built on
sources.yml                       every source, its license, and its osm_ok flag
data/*.csv                        derived views, regenerated, never hand-edited
scripts/                          fetch, import, build
```

YAML is the source of truth. The CSV register and the SQLite database are derived, and the
sync is one-way: **generators propose, humans edit, and the generator never overwrites a
hand-written comment,** because the comments in a PLACE.yml are the fieldwork.

## Skills

MOOLLM-compatible, with the split rule: does it have a jurisdiction?

- [`skills/coffeeshop/`](skills/coffeeshop/) lives here. `gedoogd` status is a Dutch
  municipal instrument, and the menu ontology is specific to this trade.
- [`place`](https://github.com/SimHacker/moollm/tree/main/skills/place),
  [`room`](https://github.com/SimHacker/moollm/tree/main/skills/room), and
  [`budtender`](https://github.com/SimHacker/moollm/tree/main/skills/budtender) are inherited
  from moollm and referenced rather than vendored, because a vendored skill silently forks.

A shop declares `inherits: [coffeeshop, room, place]`, left to right, and `place` answers
where and who was here before, `room` answers what happens when you walk in, and
`coffeeshop` answers whether it may sell and what is on the board.

## Menus are polymorphic on purpose

Every shop organizes its board differently, and flattening that into one schema destroys the
most characteristic thing about the trade. So each shop declares its own categories in its
own words -- capitals, Dutch, house slang intact -- with a `projects_to:` mapping onto a
coarse shared vocabulary for cross-shop queries. Prices keep the unit as sold: per gram, per
bag, per piece, per pre-rolled joint. A fixed-price bag has no gram price, and inventing one
would be a fabrication with a decimal point on it.

`Illegible` is a legitimate value. A note saying *third column smudged, go back* is worth more
than a guess, and it schedules the next visit.

## Running it

```bash
python3 scripts/fetch_gedooglijst.py    # official tolerance roster, the only authority on status
python3 scripts/import_2009.py          # the 2009 photographs and their EXIF fixes
python3 scripts/build_register.py       # derived register, review queue, OSM-safe subset
```

`build_register.py` prints the review queue: which addresses one look would settle, and why.
That queue is the route for the next ride.

## Related

- [MOOLLM](https://github.com/SimHacker/moollm) — the framework, the skills, the design docs
- [`skills/place`](https://github.com/SimHacker/moollm/tree/main/skills/place) — address as subject, coordinates as claims
- [OPENSTROLLMAP](https://github.com/SimHacker/moollm/blob/main/designs/webtop/OPENSTROLLMAP.md) — the subjective layer over OSM's objective geometry
