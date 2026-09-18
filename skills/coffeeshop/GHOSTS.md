# Ghosts: what an address was before, and what it was before that

*A plugin of [`coffeeshop`](CARD.yml). The register keys on the door, and doors outlive
businesses by centuries. This is how the past of a place gets recorded without being invented.*

## Three kinds of past at one address

The register holds 167 tolerated addresses and 79 that are not tolerated, which means a third of
it is already historical. Sort the past into three kinds, because they take different evidence:

| | example | what it takes |
|---|---|---|
| **an earlier tenancy** | Softland 2, then Funky Munkey, then a Snoop-branded shop, one permit at Marnixstraat 333 | a licence history, or our own sheet catching the changeover |
| **a dead shop** | Mellow Yellow, closed 1 January 2017 | a date, a cause, and a document |
| **an earlier trade entirely** | Amsterdam's first horse butchery, 1852, now a coffeeshop called *First Aid* | archives, and something still standing in the street |

## Off-roster is a question. Closed is an answer.

The generator marks every unlisted address `off-roster-unexplained`, which is honest and useless:
it might be shut, renumbered, or wrong in our old data. A closure is a different object — it has
a date, a cause and a source, and it retires the question:

```yaml
closed:
  date: 2017-01-01              # last trading day was 31 December 2016
  cause: afstandscriterium      # the 250-metre school rule
  detail: "a hairdressing academy 230 metres away. Twenty-one more metres and it would have stayed."
  cohort: "one of 8 closed that weekend; 11 earlier under the same rule"
  source: press-and-reference
```

Record the **policy** behind a closure, not just the fact, because policy closes shops in cohorts
and one paragraph explains dozens of empty addresses. Amsterdam's distance rule was a trade made
in 2012: the city escaped the *ingezetenencriterium* — the residents-only wietpas — and accepted
a 250-metre school exclusion instead. Eight shops died on one weekend for that bargain, and the
count went from 350 in 1995 to the 167 our roster still lists.

A dead shop keeps its whole record. Its menu readings stay, its room description stays, dated to
the era it described. Nothing is deleted for being over.

## Deep history belongs to the address

Marnixstraat 194 sells weed today under the name 1e Hulp. From 1852 it was Het Zwarte Paard,
Amsterdam's first horse butchery, where a tanner's son invented the wheeled hoist that pulled
drowning horses out of the canals about fifty times a year — and where a horse hurt past saving
was bought on the spot and sold over the counter the same day. The full story, with the
photograph, is at [`spots/leliegracht-horse-hoist/STORY.md`](../../spots/leliegracht-horse-hoist/STORY.md).

Two rules make this work rather than sprawl:

**It attaches to the door, not the business.** 1e Hulp did not do any of that. The address did.
So `site_history:` is a list of what stood here, each entry dated and sourced, and the current
tenant is simply the newest one.

**It has to survive into the street to earn a stop.** The big horse doors into the warehouse next
door are still there, which turns a footnote into a place you can ride to and photograph. Deep
history with nothing left standing is a paragraph; deep history with a surviving door is a
destination. Log what survives under `still_standing:`, with a survey task if it is unlocated.

## Every image gets a sidecar, every story gets a wrapper

A photograph in a repository with no sidecar is an orphan: nobody can tell whether they may
republish it, and nobody knows what they are looking at.

```
spots/leliegracht-horse-hoist/
  1929-07-leliegracht-toestel-van-sinck.jpg    the artifact
  1929-07-leliegracht-toestel-van-sinck.yml    same basename — rights, archive id, maker, view
  STORY.md                                     embeds the image and tells it, for humans
  SPOT.yml                                     the place itself
```

The sidecar carries what the pixels cannot: which archive, which id, who made it, what rights
apply, and how large the original is. **Rights decide whether a file may live here at all.** The
1929 press photo is marked *auteursrechtvrij* by the Stadsarchief, so it can be committed with
credit; a menu board photographed by somebody else is linked and never copied.

The wrapper exists because YAML is for machines and a story is for a person. It is allowed to be
good. Write the narrative once, properly, and let the YAML stay boring.

## Then and now, from one viewpoint

A rephotograph from the same angle is the cheapest time machine available, and it costs a bike
ride. Pair the archive frame with a modern one: same viewpoint, geotagged, timestamped, and
attached to a track — which gives the historical photograph something it never had, a position
fix that this project is actually allowed to use.

## Ceremony, and why this is not Pokémon Go

A closed shop can still be visited. Standing outside a dark window late at night, when there is
nobody around to be bothered, and smoking one for the buds and the budtenders and the regulars,
is a reasonable thing to do with an evening, and the register can hold that: a `ceremony:` block
saying it is open to visitors and what suits.

```yaml
ceremony:
  open_to: visitors
  suggested: "late, when the street is empty, for the buds and the budtenders and the regulars"
```

Rules, mostly about restraint:

- **The dead do not speak.** A ghost record is *about* a shop, never in its voice, and the same
  goes for its people — see [`BUDTENDERS.md`](BUDTENDERS.md), which is where the memorial rules
  live.
- **No points, no leaderboard, no check-in.** The reward for coming is knowing what happened
  there, which is not something a scoring system can hand out.
- **A closed shop's people are still alive.** The business can no longer consent to anything,
  but the person who worked the counter for fifteen years can still object to being narrated.
  Consent does not become available by the shop dying; it becomes *unobtainable*, so the room
  gets described and the people do not, unless they are asked directly.

The difference from a monster-collecting game is not the technology, it is what the place is for.
Pokémon Go treats a location as a coordinate: interchangeable, valuable because something was
dropped on it. Here the coordinate is the least interesting part, and what is dropped on it
already happened — a horse came out of that canal on that spot in front of that crowd. You cannot
move that to a different bridge.

Which yields the itinerary Don rode before any of it was written down: buy at the yard where they
recycled the horses, and smoke it a few blocks away where they lifted one out of the water.

## Related

- [`spots/leliegracht-horse-hoist/`](../../spots/leliegracht-horse-hoist/) — the worked example
- [`places/marnixstraat-194/`](../../places/marnixstraat-194/) — the yard, still trading
- [`places/vijzelgracht-33/`](../../places/vijzelgracht-33/) — Mellow Yellow, the flagship ghost
- [`GEOTOKING.md`](GEOTOKING.md) — spots, episodes, and what you carry between them
- [`VERBS-AND-RUBRICS`](https://github.com/SimHacker/moollm/blob/main/designs/webtop/VERBS-AND-RUBRICS.md)
  — how a ceremony becomes a verb an object advertises
- [`place`](https://github.com/SimHacker/moollm/tree/main/skills/place) — why the address is the
  subject, which is the whole reason deep history has somewhere to attach
