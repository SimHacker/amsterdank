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
places/oudezijds-voorburgwal-88h/
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
