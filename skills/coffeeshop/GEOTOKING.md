# Geotoking: inventory, the ride, and where you actually were

*A plugin of [`coffeeshop`](CARD.yml). The robot at the counter
([`BUDTENDERS.md`](BUDTENDERS.md)) sells you something that goes in a bag you carry around
the city. This is what is in the bag, where it gets used, and what that leaves behind.*

## The loop

    read the board  →  buy (virtually)  →  carry it  →  use it somewhere  →  say what happened
         menu/            inventory/         the ride        a spot            an assessment

Every arrow is a MOOLLM object and every step is optional. You can play the whole thing
without buying anything real, and you can mirror a real purchase item for item. The point of
the virtual layer is not pretend shopping. It is that **a purchase is the moment a place, a
price, a date, and an intention all coincide**, which makes it the best available hook to
hang a memory on.

## An item in your inventory

```yaml
# inventory/2026-09-20-white-widow.yml
inherits: [item, purchase]
label: "White Widow"              # exactly as the board wrote it. Not "white-widow".
from:
  shop: places/oudezijds-voorburgwal-88h
  board: menu/2026-09-20.yml      # the reading it came off, so the price is checkable
  category: WIET                  # the shop's own category, not a normalized one
paid:
  amount: 12.00
  unit: bag                       # as sold. A fixed-price bag has no gram price.
  currency: EUR
real: true                        # this one mirrors an actual purchase
state: partial                    # unopened | partial | finished
acquired: 2026-09-20T15:40+02:00
```

`real: false` is the default and the whole thing works fine that way -- the virtual economy
runs on the real board without anybody having to buy anything. `real: true` turns the same
structure into a strain-and-price diary of a kind no shop will ever hand you, because
[they are not allowed to publish one](SKILL.md).

## A spot, which is a place with no address

This is where the data model has to stretch, and it is worth being honest that it does. A
bench by the Vondelpark pond has no street, no number, and no postcode, so the rule that
[the address is the subject](https://github.com/SimHacker/moollm/tree/main/skills/place)
cannot key it. A spot is identified by what it actually is:

```yaml
# spots/vondelpark-pond-bench-east.yml
inherits: [spot, place]
identity:
  osm: { type: node, id: 1234567890 }      # preferred: the commons already named it
  coordinate: { lat: 52.3579, lng: 4.8686, source: field-survey }
  name: "the bench on the east side of the big pond"   # what you and your friends call it
what: bench
context: [pond, willow, ducks, sun_until_1900]
sit: 3                            # how many fit, honestly
```

Which is exactly why the micro-mapping matters, and why Vondelpark is the ideal place to
start: **the game is only as good as the furniture.** Benches, drinking fountains, bins,
trees worth sitting under, the things in the middle of roundabouts, ponds, bridges, the
grassy bit that gets sun until seven. Every one of those consistently tagged in OSM is
another spot the game can put on the board, and unlike a coffeeshop, none of it is legally
fraught to map. It is also the kind of survey that
[StreetComplete](https://streetcomplete.app/) exists to make pleasant, one question at a
time, from a bike.

## An episode: the part that is actually yours

```yaml
# episodes/2026-09-20-vondelpark.yml
inherits: [episode, assessment]
when: 2026-09-20T16:25+02:00
where: spots/vondelpark-pond-bench-east.yml
used: inventory/2026-09-20-white-widow.yml
with: [marieke, the_dog]          # people, by consent; see BUDTENDERS.md
weather: "low sun, 19C, wind off the pond"
by: don                           # signed. Never averaged into a rating.
thought: |
  Two hours between buying it and smoking it, and the walk over was the better half.
  The bench faces west so the sun goes down the length of the pond, and the ducks
  come over if you rustle anything. Would ride back for this specifically.
```

Signed, dated, attributed, and never collapsed into stars, per
[SIGNED-ASSESSMENTS](https://github.com/SimHacker/moollm/blob/main/designs/webtop/SIGNED-ASSESSMENTS.md).
The useful question is not *how good is this bench* but *whose afternoon was this and do I
want the same one*.

An episode is also the cleanest possible survey artifact: it carries a coordinate, a
timestamp, a photograph if you took one, and a reason to have been there. The subjective log
and the objective survey turn out to be the same act recorded twice.

## Your log is sensitive data about you

Nothing in this repository is more legally interesting than a timestamped, coordinate-tagged
record of a person's cannabis consumption -- and it is about **you**, not about the shops. So
the defaults are structural rather than promised:

- **Local-first.** Episodes live on the device. No sync by default, no account required.
- **Shared as a stripped assessment.** What leaves is the spot and the opinion. Not the dose,
  not the timestamp, not the sequence of your afternoon.
- **Exportable and deletable in one action**, because a diary you cannot get out of an app is
  a hostage.
- Worth knowing rather than worrying about: a synced consumption log is a record that can be
  read by anyone who gets the device, at a border or otherwise.

Publishing the coffeeshop register is a contribution to the commons. Publishing your episodes
is nobody's business but yours.

## Bongo Bingo, which already existed

The 2009 TurboGears backend had a `bingo_card` table, a shared `gameSeed` so a whole season
plays the same deck, a per-card `cardSeed` so no two cards match, a 5×5 grid headed **BONGO**
with a free centre square, a 3×3 `usa` variant, and an 11×11 variant headed **GODVERDOMME**.
Squares were coffeeshops. Marks came from Foursquare check-ins.

Foursquare check-ins are gone, and the replacement is better: a mark is **your own
photograph with GPS EXIF within N metres of the square**. Same game, no platform, and the
marks are survey evidence -- so playing bingo populates the register. The seeds mean a card
is reproducible from two integers, which is how a card can be shared as a link and verified
later.

`GODVERDOMME` is eleven letters, so the big card is 121 squares against a roster of 167
tolerated addresses. It remains, as it was in 2009, a poor life decision and an excellent
data collection strategy.

## Related

- [`BUDTENDERS.md`](BUDTENDERS.md) — who is behind the counter, and what they agreed to
- [`SKILL.md`](SKILL.md) — the board, the ontology, the price traps
- [`place`](https://github.com/SimHacker/moollm/tree/main/skills/place) — address as subject, and why a spot needs a different key
- [EBIKE-PATH-GRAMMAR](https://github.com/SimHacker/moollm/blob/main/designs/webtop/EBIKE-PATH-GRAMMAR.md) — dwell, velocity, and how media attaches to a ride
- [TOURS-AND-PLAYLISTS](https://github.com/SimHacker/moollm/blob/main/designs/webtop/TOURS-AND-PLAYLISTS.md) — couching a route, dramaturgically rather than shortest-first
