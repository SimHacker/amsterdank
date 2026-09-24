# Bongo Bingo

Amsterdank Coffeeshop Bongo Bingo was a bingo game played across Amsterdam. The squares on your
card were coffeeshops, and the only way to mark a square was to go there and check in on
Foursquare. Don built it on the Amsterdank server and published it at
[amsterdank.nl](https://amsterdank.nl) for the Amsterdam Cannabis Cup in November 2011. There was
no money to promote or advertise it.

The challenge is the trip. You mark a square by moving your position in the city itself, not by
clicking on a map of it, and the only way to move it is to carry yourself there. That makes it a
small, complete example of the argument in
[An interface to agency](https://github.com/SimHacker/moollm/blob/main/designs/INTERFACE-TO-AGENCY.md),
where it appears in the
[Ebike Safari part](https://github.com/SimHacker/moollm/blob/main/designs/interface-to-agency/ebike-safari.md).

## How it worked in 2011

The server was TurboGears, with Genshi templates and a `bingo_card` table.

**Signing in.** You logged in with Foursquare, and the page greeted you with your Foursquare name
and photo.

**Marking squares.** The server called the Foursquare API for your venue history and matched each
venue you had been to against the coffeeshops in the Amsterdank database, by Foursquare venue ID.
Every coffeeshop you had ever checked into marked its square, so a card you started today could
already have marks from last year. The server also took Foursquare's push notifications, so a new
check-in was recorded as it happened. A check-in at a venue that was not a coffeeshop was ignored.

**Dealing a card.** Two numbers dealt every card:

- The **game seed** was shared by everyone that season. It drew 15 coffeeshops for each of the five
  columns from all the coffeeshops in the database, the way a bingo column holds 15 numbers.
- The **card seed** was yours. It dealt five coffeeshops from each column's 15, so no two cards
  matched, but every card was drawn from the same deck.

The centre square was free. Because a card is reproducible from its two seeds, it could be shared
and checked later.

**Winning.** Five in a row, in a column or on either diagonal, and you pressed the button. The page
counted your bingos on that card, or told you "You do not have a bingo, silly!" You could hold up
to five cards at once.

**Variants.**

| Card | Header | Grid | Coffeeshops per column |
| --- | --- | --- | --- |
| Standard | BONGO | 5×5 | 15 |
| American | USA | 3×3 | 15 |
| Dutch | GODVERDOMME | 11×11 | 18 |

GODVERDOMME has eleven letters, so the Dutch card has 121 squares. There was also a hidden deck in
which every square was Betty Too.

## What changes now

Foursquare moved check-ins into its Swarm app in 2014, and the API the game called is gone. The
replacement is better: a mark is **your own photograph, with GPS in its EXIF data, taken within N
metres of the square**
([GEOTOKING.md](GEOTOKING.md#bongo-bingo-which-already-existed)). The game no longer depends on a
platform, and every mark is also survey evidence, so playing bingo fills in the coffeeshop register.

## How it fits Ebike Safari

[Ebike Safari](https://github.com/SimHacker/WillWrightShowForFood/tree/main/apps/ebike-safari)
records a ride: where you went, where you stopped, how long you stayed, and the photographs you
took. Bongo Bingo does not need its own tracking. A stop at a coffeeshop with a photograph is a
mark, and the card reads it from the same log as everything else.

That is what makes Ebike Safari a platform for games like this rather than a single game. A game is
a **rubric**: a file that names a selection over the log, some metrics, a goal and a display
([VERBS-AND-RUBRICS.md](https://github.com/SimHacker/moollm/blob/main/designs/webtop/VERBS-AND-RUBRICS.md)).
A rubric cannot change the history; it can only read it. Bongo Bingo is one rubric. Others read the
same ride:

- **Bench Compass**: sit on benches facing every direction.
- **Nose Map**: cover the city in smell reports.
- **Bridge Toll**: count the distinct bridges you crossed.

One ride can mark a bingo square, add a bench bearing and pay a bridge toll at once, because every
game reads the same log and the same register of places. Rubrics are files, so a patron can write a
new game over your own history without asking anyone to build a feature.

Bingo is also a family of cards, with Blogo, Gonzo and Gonzo Bongo Bingo proposed alongside the one
that shipped ([SUMMARY-GENRES.md](https://github.com/SimHacker/moollm/blob/main/designs/webtop/SUMMARY-GENRES.md)).

## Rules carried forward

- **Scores stay local and opt-in.** A public ranking of who smoked in the most coffeeshops is a bad
  thing to publish about real people, including yourself. There is no leaderboard by default.
- **Your log is yours.** Where you were and when is sensitive data, and it stays on your device
  ([GEOTOKING.md](GEOTOKING.md#your-log-is-sensitive-data-about-you)).
- **Other people's Foursquare data stays out.** The 2011 import brought in other users' tips, photos
  and mayorships. Those are quarantined and never published ([sources.yml](../../sources.yml)).

## Source

The 2011 TurboGears server is in Don's Subversion checkout of the Coffeeshops project, not in this
repository. It contains API credentials, so it stays out.

## Related

- [GEOTOKING.md](GEOTOKING.md): inventory, spots, episodes, and the short history of this game
- [SKILL.md](SKILL.md): the board, the ontology, the price traps
- [EBIKE-PATH-GRAMMAR](https://github.com/SimHacker/moollm/blob/main/designs/webtop/EBIKE-PATH-GRAMMAR.md): dwell, velocity, and how media attaches to a ride
- [DISPENSERS-AND-SOUVENIRS](https://github.com/SimHacker/moollm/blob/main/designs/webtop/DISPENSERS-AND-SOUVENIRS.md): a claimed square as a stamped souvenir
