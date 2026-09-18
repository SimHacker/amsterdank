# Budtenders: the room is furnished, and some of the furniture is people

*A plugin of [`coffeeshop`](CARD.yml). The shop is a
[`room`](https://github.com/SimHacker/moollm/tree/main/skills/room) at a
[`place`](https://github.com/SimHacker/moollm/tree/main/skills/place), and a room with
nobody in it is a floor plan. This is how the people get in without anyone being
conscripted.*

## A shop is a directory, not a file

One YAML file cannot hold a shop, because a shop accumulates kinds of content that want
different neighbours: photographs, a board read three times over four years, the objects on
the shelves, and the people behind the counter.

```
places/oudezijds-voorburgwal-88/          # street and number; the huisletter is a field
  PLACE.yml            the address: coordinates, tenancies, site history, OSM identity
  ROOM.yml             the interior: what you see walking in, layout, contents, exits
  COFFEESHOP.yml       the trade: gedoog status, amenities, vibe, hours
  menu/
    2026-09-20.yml     one board reading, dated, in the shop's own ontology
    2009-10-04.yml     an older one; menus are a time series, never overwritten
    board.jpg          the photograph the reading came from
  survey/
    2026-09-20-key.heic
    2026-09-20-number.heic
  characters/
    consent.yml        who agreed to what, and what to do absent agreement
    robot.yml          the machine that staffs the counter when nobody consented
    marieke.yml        exists only with consent, and can be deleted on request
  objects/
    grinder.yml        furniture, props, the cat, the board itself as an object
```

Directory listing as advertisement index: the filenames tell you what has been done and what
has not. No `menu/` means nobody has read the board. No `characters/` means nobody has been
asked yet, which is a task, not a gap in the schema.

## The one rule about real people

**Ask them. Represent only what they agreed to. Delete on request, for real.**

Everything below is an elaboration of that, and none of it is optional, because a budtender
is a worker at their job being asked by a stranger to appear in software. The power gradient
runs the wrong way for assumptions.

What is forbidden outright, without asking anyone:

- **Building a character from scraped material.** Reviews, Instagram, TripAdvisor comments
  about "the friendly guy with the dreads" -- that is a facsimile assembled behind someone's
  back from other people's opinions of them. It is the single most tempting shortcut here
  and it is out of bounds. It is also personal data processed without a lawful basis, and a
  photograph of an identifiable worker is theirs, not the photographer's, to publish.
- **Inferring anything protected.** Ethnicity, nationality, immigration status, religion,
  sexuality, health, drug use. Not from a photograph, not from a name, not ever.
- **Putting words in their mouth.** A generated recommendation attributed to a named real
  person is a fabricated quotation, and in a trade that is legally forbidden to advertise it
  can cause them an actual problem. See the `afficheren` section of [`SKILL.md`](SKILL.md).

## Consent tiers

Ask once, record the answer, and honour exactly that level. Anything not granted is refused
by default, and the default is the robot.

| Tier | What exists | What it takes |
|---|---|---|
| **0 declined** | nothing; the robot staffs the counter | a shrug, or silence, or a bad moment |
| **1 role** | "a budtender", anonymous, no name, no description | "yeah, fine, don't use my name" |
| **2 named** | first name and a description **in their words** | "sure, say I'm Marieke and I know the hash" |
| **3 character** | voice, recommendations, stories, photograph, with review rights before publication | a real conversation and an explicit yes |
| **4 self-authored** | they write or edit their own YAML | the best outcome, and worth asking for |

Tier 4 is the goal, not tier 3. A budtender who edits their own file has stopped being
represented and started participating, which is the whole difference between a dataset about
people and a place people live in. Hand them the phone.

A shop can reach tier 4 too, by authoring a character that is nobody's likeness at all: see
[the house mascot](#the-house-mascot-a-shops-own-tier-4).

## The ask, out loud

Short, plain, no pitch. Deliver it after buying something, never instead.

> I'm making a guide to Amsterdam coffeeshops -- own photos, no advertising, and it's free.
> Would you want to be in it, and how? I can leave you out completely, use just a first
> name, or you can write your own bit however you like. Whatever you say goes, and you can
> change your mind whenever.

Then write down what they said, including a no. A recorded refusal is valuable: it stops the
next person asking again, and it stops a future you assuming nobody was ever asked.

## consent.yml, and being able to keep the promise

Revocation has to actually work, and git makes that harder than people assume: a committed
file lives in the history even after deletion. So real-person records are **referenced, never
inlined**, kept in their own file, excluded from derived exports unless consent is current,
and -- the part that matters -- **not committed until consent is recorded**.

```yaml
# characters/consent.yml — the gate. No entry here, no character rendered. Ever.
asked:
  - who: marieke                    # the file characters/marieke.yml, only if tier >= 2
    when: 2026-09-20
    asked_by: don
    tier: 2                         # named, description in her words
    words: |
      "Say I'm Marieke and I know more about hash than anyone here.
       Don't put my picture in."
    photo: false                    # asked separately, and refused. Honour it.
    review_before_publish: true
    revoke: "any message to don@..., and the file goes, including from the history"
    expires: 2028-09-20             # consent goes stale; ask again rather than assume

  - who: null                       # the guy on Tuesdays
    when: 2026-09-20
    tier: 0                         # declined, politely, twice
    note: "Do not ask again. Recorded so nobody does."

absent_consent: robot               # the only permitted fallback
```

A consent record that has expired is not consent. Two years is generous for a job with the
turnover of retail; when it lapses, the character stops rendering and the shop is staffed by
the robot again until someone asks.

## The robot budtender

When nobody has consented, the counter is staffed by a machine that says so.

```yaml
# characters/robot.yml
inherits: [robot-budtender, character]
name: "the machine behind the counter"
is_a_person: false                  # stated in the object, not just implied by the name
voice: "flat, helpful, cites the board and nothing else"

knows:
  - "this shop's menu as photographed, in this shop's own categories"
  - "the date the board was read, and that boards change"

never:
  - "impersonating the staff, or borrowing their manner"
  - "speaking for the shop — a recommendation is the robot's, attributed to the robot"
  - "inventing an item, a price, a percentage, or a strain that was not on the board"
  - "answering a legal or medical question as though it had standing"

when_it_does_not_know: "says the board was illegible or the visit is stale, and offers to add it to the survey queue"
```

The robot is a deliberate use of the
[masking effect](https://github.com/SimHacker/moollm/blob/main/designs/GLOSSARY.md): make it
iconic and obviously artificial, put it in front of a photographically detailed real shop,
and it reads as a helper rather than as a fake employee. An abstract robot in a real doorway
is honest. A realistic person in a real doorway is a lie about who works there.

It can be charming. It cannot be authoritative, and it cannot be mistaken for staff -- the
[I-Beam constitution](https://github.com/SimHacker/moollm/blob/main/skills/cursor-mirror/characters/i-beam/CONSTITUTION.md)
already refuses "letting a useful fiction become a claim of authority", and this is that
refusal wearing an apron.

## The house mascot: a shop's own tier 4

The Dolphin's on Kerkstraat 39 has dolphins. Nobody had to consent to a dolphin. The shop
invented it, the shop owns it, and it is not a facsimile of any worker who has to stand next
to it all day -- which makes a mascot the one character a shop can hand us outright.

A mascot is the robot in a house costume. It inherits the robot's honesty floor unchanged
(`is_a_person: false`, no inventing stock, no pretending to be staff) and adds only what the
shop wrote. The gain is not decoration: a mascot **speaks the shop's own words**, so what it
says arrives as a self-published claim with the shop as its source, which outranks anything
we could infer from the doorway. A shop that wants control of how it appears here now has a
lever that does not require trusting our judgement about its vibe.

```yaml
# characters/mascot.yml — no consent record needed, because nobody's likeness is involved
inherits: [mascot, robot-budtender, character]
name: "the dolphin"
is_a_person: false
authored_by: shop                   # the house wrote the voice; we did not invent it for them
grant:
  who: "the shop, in writing"       # a person who can speak for the business
  when: 2026-09-20
  scope: "use the dolphin in this guide; the shop keeps everything else"
  revocable: true                   # it goes when they say so, same as a budtender's
speaks_for_the_shop: from_what_the_shop_wrote   # and no further
```

### A licensed celebrity is three rights, and the shop holds one

2e Cheech and Chong's on De Clercqstraat 30 is still open (a menu dated 19 April 2026), and
the register carries that name as a plain fact about a business. What the register does not
do is grow a Cheech-voiced budtender out of it, because a name is not a persona and a shop's
brand deal is not a grant to us:

1. **the performers' own rights** in their name, likeness and voice -- in the Netherlands
   *portretrecht*, Auteurswet art. 21, and publicity rights elsewhere;
2. **the trademark licence** the shop may hold, which licenses *the shop's* use in *its*
   trade, and is silent about a third party rendering the character in software;
3. **our use, here**, which neither of the above conveys.

So "we're licensed, go ahead" is not sufficient, however sincerely offered. It takes a
written warranty naming the licensor and the scope, and the character does not exist here
until that exists. The tell is usually easy to read from the doorway: two visitors report
that 2e Cheech and Chong's has no Cheech and Chong theme in it at all. The name is a name.

If a rights holder genuinely wants a character here -- Snoop, or anyone whose name a shop is
already trading under -- the clean version is the one we offer a budtender, and it is the same
rule: they write it themselves. Tier 4 does not care whether you are famous. Hand them the
phone.

### The eponymous animal, where all three rights land on one owner

The Bulldog can have a bulldog. When the creature in the name is one the house made up for
itself, the three layers collapse into a single owner: they hold the name, they hold the
character, and there is no performer to clear. The mascot is free the moment they grant it,
and one grant rides along the whole chain -- six Bulldogs in the 2011 sheet, three of those
addresses still tolerated in 2026.

If there is also an actual bulldog asleep by the door, it is a pet *and* a mascot at once,
which is fine as long as the two stay in their own files: observed facts in the pet, authored
words in the mascot. The real dog's snoring is evidence. The mascot's opinions are the house's.

### The regime belongs to the tenancy, not the address

Marnixstraat 333 has carried one permit and six signboards: Aggie, Baywatch, Softland 2, Funky
Munkey from around 2010 to 2024, SWED a Snoop Dogg Store in 2024, and Tha Dogg House from
2025. Don photographed it in 2009 during the changeover, and his sheet records it as Softland 2
with Funky Munkey as an also-known-as.

So the same door went from a monkey the house made up -- free, nobody to clear -- to a licensed
celebrity brand, without moving an inch. **A `mascot:` block is therefore dated and belongs to
the tenancy**, and the register has to be able to say *free then, restricted now*. It runs the
other way too: when Tha Dogg House is eventually replaced by somebody's invented gecko, the
freedom comes back with the gecko. And a retired mascot does not become unrenderable by
retiring -- the funky monkey stays available, dated to its era, the same way a room description
from 2010 stays true about 2010.

It is tempting to read this as *Snoop has lawyers and the monkey does not*, and that gets the
rule backwards even though it gets the risk right. The requirement is identical for Snoop and
for the guy behind the counter on a Tuesday: a real person's likeness needs that person's own
grant. What differs is enforcement, and it runs opposite to care -- Snoop can send a letter,
while a budtender has no lawyer, no leverage, and nothing but our restraint between them and a
fabricated quotation in a trade that is forbidden to advertise. If lawyer-count set the
treatment we would have it exactly inverted. The power gradient runs the wrong way, which is
the same reason this file opens by saying so.

## Pets: the easy case, and its two traps

Nobody has to ask a cat. An animal has no likeness rights and no privacy interest, so
photograph it, name it, record its habits and put it in the room. The register already runs
on this: a cat at the 420 Café with an etiquette rule attached (act disgusted when it touches
you and your service suffers), no cats at De Kroon II stated by a visitor as a virtue, and a
very old cat at 2e Laurierdwarsstraat 44 that kept the place free of rats. Dogs, parrots,
snakes, a tank of fish -- same deal.

Three things in a shop look alike and are not: a **pet** is a real animal, observed, and
lives in `characters/` because it is animate; a **mascot** is a fiction the house wrote; a
**prop** is the aquarium or the shelf of stuffed animals, and lives in `objects/`. The drift
to watch is a real cat quietly becoming a mascot, at which point we have started inventing an
animal that has to go on existing without us.

**A talking animal is us talking.** The cat at the 420 Café is a narrative buffer for a
memorial, and a buffer is not a loophole: what it may say about a real person is exactly what
we may say directly, no more, which is why it refuses to speak *as* John Sinclair. The parrot
makes the point sharper, because a parrot repeats, and what there is to repeat in a coffeeshop
is customers talking. **A parrot's repertoire may contain only what the house wrote.** Never
anything overheard. That clause binds every species; the parrot just makes it obvious.

**The house rule outranks the joke.** On the bar at the 420 Café: *"Please Do Not Give Drugs
To Our Cat"*. Record rules like that verbatim, and never render an animal consuming anything
as a gag -- cannabis is genuinely toxic to cats and dogs, and the shop has already asked.

```yaml
# characters/the-cat.yml — animate, so characters/, though nothing here is gated by consent
inherits: [pet, character]
species: cat
name: unknown                     # ask. Staff enjoy this question more than any other.
is_a_person: false
present_at: [2010, 2013]          # observed. Pets die and pets move; absence is not death,
                                  # any more than a dark window is a closure.
job: "rat control"                # some of them are working animals
house_rule: "Please Do Not Give Drugs To Our Cat"      # verbatim, from the sign
speaks: fiction                   # if it talks, we wrote it, and the buffer rule applies
never:
  - "consuming anything, as a joke or otherwise"
  - "repeating what it heard in the room"              # the parrot clause. Every species.
```

## What the robot sells you

Virtual goods, from the real board, into your inventory, which is where the ride begins:
see [`GEOTOKING.md`](GEOTOKING.md).

## This is an application of representation-ethics, not a new regime

The base law lives upstream in
[`representation-ethics`](https://github.com/SimHacker/moollm/tree/main/skills/representation-ethics),
and the tiers above are its **consent hierarchy** (self → explicit → public → private →
deceased) applied to a retail counter. Read that skill before extending anything here:

- `consent-hierarchy.yml` — the general ladder these five tiers instantiate
- `self-authored-persona.yml` — tier 4, and the reason tier 4 is the goal
- `emoji-disclosure.yml` — the **🤖 Robot Rule**, which is exactly what `is_a_person: false` above is
- `framing-spectrum.yml` — activate traditions, do not impersonate
- `worth-of-representation.yml` — whether a person belongs in the collection at all

What this file adds is only what the counter adds: **expiry**, because retail turnover means
old consent is not consent; **recorded refusals**, so the same person is not asked twice; and
**referenced never inlined**, because git history makes deletion a lie unless the record was
never committed in the first place. If those three generalize to another room full of real
people, they belong upstream rather than here.

The sibling regime for guests is
[`schemas/portrayal-standards.md`](https://github.com/SimHacker/WillWrightShowForFood/blob/main/schemas/portrayal-standards.md)
in WillWrightShowForFood: a portrayal is *about* a person and is never them, the subject may
correct, reduce, replace or delete their own directory at any time, and silence is an answer
that gets honoured. A budtender gets the same deal as a guest on the show.
