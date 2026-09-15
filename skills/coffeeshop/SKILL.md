---
name: coffeeshop
description: "Model an Amsterdam coffeeshop: a tolerated address whose menu is its own ontology. Use when authoring a shop record, reading a menu board from a photograph, comparing prices across shops, or reasoning about gedoogd legal status."
allowed-tools: [read_file, write, run_terminal_cmd, grep]
permissions: [read, write, files]
related: [place, room, budtender, character, korz]
consumes: [place, room]
composes_with: [budtender, room, adventure, tour]
respects: [yaml-jazz, postel, no-ai-slop]
moollm_compatible: true
license: MIT
tags: [amsterdam, place, menu, ontology, survey, osm]
credits:
  - "Don Hopkins — the 2009 survey, the 2011 PlacesData schema, and the ride"
moollm:
  ecosystem: false
  home_repo: "https://github.com/SimHacker/amsterdank"
  self_contained_guidance: "SKILL.md is usable alone. CARD.yml adds the schema; GLANCE.yml is the sniff. Its parent `place` lives in the moollm repo."
---

# coffeeshop — a tolerated address with a menu that is its own ontology

Part of MOOLLM · [This skill's directory](https://github.com/SimHacker/amsterdank/tree/main/skills/coffeeshop) · parent skill [`place`](https://github.com/SimHacker/moollm/tree/main/skills/place) lives in [moollm](https://github.com/SimHacker/moollm)

*Read [`GLANCE.yml`](GLANCE.yml) then [`CARD.yml`](CARD.yml) first. This is the protocol
for authoring a shop, reading a board, and projecting a menu without flattening it.*

```yaml
inherits: [coffeeshop, room, place]
```

Three parents, three questions. `place`: where is it, which building, who was here before.
`room`: what happens when you walk in. `coffeeshop`: may it sell, under what conditions,
and what is on the board today. This is the ordinary case for multiple inheritance, not a
clever use of it -- and the ordering is the answer to "what is this thing mostly."

## The legal shape, because it dictates the schema

Nothing is legalized. Sales are **tolerated**, and in Amsterdam the burgemeester keeps a
[gedooglijst](https://lokaleregelgeving.overheid.nl/CVDR756282/2) -- 167 addresses in the
version valid from 2026-03-05 -- published as a beleidsregel with a validity date and
republished in full on every change.

The permission attaches to the **address**. That single fact settles a dozen schema
arguments: identity, coordinates and history belong to `place`, and this skill holds only
the permission, the board, and the people. A shop that moves is one tenancy ending and
another beginning at a different `place`, which is why relocations stop being a special
case.

The conditions are AHOJG-I, and the first letter matters more than people expect.

## Afficheren: the constraint that explains the data drought

**A is for no advertising.** That prohibition is why menu data barely exists in
machine-readable form, why the archives are *photographs of boards*, and why the price of
a gram is easier to learn by walking in than by searching.

Which puts a design question in front of anyone building a directory: a polished
price-comparison feed with push notifications is doing, at scale, the thing the shop is
forbidden to do for itself. Collecting is fine. Recording what you saw is fine. Consider
carefully before building the part that shouts. This is not legal advice and the skill
takes no position beyond: notice that you are near a line the shops themselves cannot
cross.

## Every shop's menu is its own ontology

This is the part worth getting right, because it is the most interesting data in the set
and the easiest to destroy.

One board reads `WIET / HASJ / VOORGEDRAAID`. The next reads `Indica / Sativa / Hybrid`.
The next sorts by tier, or Nederhasj against import, or bio against the rest. **How a shop
cuts the world is a fact about the shop** -- its clientele, its era, its self-image. A
house schema deletes exactly that.

So: the shop's taxonomy is primary and verbatim, and a projection makes it queryable.

```yaml
menu:
  photographed: 2026-09-20        # the board this was read from, so staleness is visible
  board_order: [wiet, hasj, voorgedraaid]     # top of the board first, always
  axes: [form, lineage]            # what THIS shop thinks distinguishes its products
  categories:

    wiet:
      label: "WIET"                # VERBATIM. Capitals, Dutch, spelling errors and all.
      projects_to: flower          # into the shared vocabulary, for querying only
      items:
        - { name: "Amnesia Haze", unit: gram, price: 15.00, lineage: sativa }
        - name: "White Widow"
          unit: bag                # the classic Amsterdam form
          price: 12.00
          weight_g: null           # the shop does not say, so neither do we
          # Regulars call this the twelve-euro bag. Weight drifts with the harvest.

    voorgedraaid:
      label: "VOORGEDRAAID"
      projects_to: preroll
      items:
        - { name: "joint puur", unit: joint, price: 6.00 }   # puur = no tobacco
```

**The shared vocabulary is closed, coarse, and unauthorable:** `flower, hash, preroll,
edible, drink, vape, seed, accessory, other`. It exists so you can ask who sells hash
across 167 shops. Nothing is ever written into it directly, and a new term gets added only
when a real shop cannot project into any existing one. That is the same discipline as
[SIGNED-ASSESSMENTS.md](https://github.com/SimHacker/moollm/blob/main/designs/webtop/SIGNED-ASSESSMENTS.md): a closed vocabulary
compiled from open ones, where the local words survive and the shared words are a
projection you can throw away and rebuild.

### The trap in prices

A fixed-price bag is not a price per gram. Divide `12.00` by a weight the shop never
quoted and you have manufactured a number, lost the thing the shop actually said, and
made two shops look comparable when they are not. Units are **as sold**: `gram`, `bag`,
`piece`, `joint`. `weight_g` stays null unless the board states it.

### Reading a board is a MOOLLM job, and stays honest by refusing

`READ-BOARD` turns a photograph into this shop's taxonomy. It may propose projections,
never rename a category, never translate the Dutch, and never tidy `SUPER SKUNK !!!` into
`Super Skunk`. If the board is ambiguous, the ambiguity is recorded -- a YAML Jazz comment
is the right place for *"third column is smudged, looks like hasj prices, go back."*

### Korz: the same menu, different readers

Menu rendering is dispatch on the viewer, not a property of the menu
([designs/korz/](https://github.com/SimHacker/moollm/blob/main/designs/korz/README.md)). A tourist sees form and strength; a local
sees price per bag and what changed since last week; a surveyor sees which fields are
stale; **OpenStreetMap sees none of it, because a menu is not verifiable geography and
does not belong in the commons.** One object, four projections, no duplication.

## Status is three different questions

```yaml
status:
  trading: closed
  closed_because: order        # clock | order | business | unknown
  closure_date: 2016-12-31
  closure_cause: school-distance
```

A directory that renders "Closed" because it is three in the morning is saying nothing
about whether the business exists. Keep the clock away from the business, always.

And name the cause precisely, because the causes get blurred and then history is wrong:
the **250 m school-distance criterion** is what closed Mellow Yellow at the end of 2016;
**Project 1012** is what *moved* shops out of the red-light district. Different policies,
different mechanisms, different years. A single `closed: true` erases both stories.

## Absence never implies closure

A shop missing from the roster is a question, not a finding. It could be closed, moved,
renumbered, or simply written down differently -- see the orphan-pair rule in
[`place/SKILL.md`](https://github.com/SimHacker/moollm/blob/main/skills/place/SKILL.md#article-2-matching-addresses-is-the-whole-game-and-dutch-fights-back).
`GEDOOG-CHECK` returns `tolerated`, `off-roster`, or `probable-renumbering`, and never
promotes any of them to a closure. Only a look at the door does that.

## The staff are characters

A budtender is not a field on the shop, it is a
[`budtender`](https://github.com/SimHacker/moollm/tree/main/skills/budtender) -- a role that already exists as a skill, inheriting from
`bartender`, with `RECOMMEND-STRAIN` and `EXPLAIN-TERPENES`. `ASK-BUDTENDER` delegates
with *this* shop's board in hand, which is the difference between a recommendation and a
generic strain lookup. When you meet someone and they tell you their name, they become a
character in the shop's directory, with the date you met them.

## Amenities are sparse, and absence means unknown

Wi-Fi, outlets, terrace, cards, step-free entry in a canal house. A missing key means
nobody has checked -- never false. `wifi: claimed` and `wifi: verified` are different
facts, and only one of them survives an afternoon of trying to work there.

## Vibe is signed and never averaged

`touristiness` and `gezellig` are assessments with an author, evidence, and a date. They
do not collapse into a star rating, because the useful question is not *how good is this
shop* but *whose judgment is this and do I ride with them*.

## Related

This skill lives in [amsterdank](https://github.com/SimHacker/amsterdank) and inherits from
skills in [moollm](https://github.com/SimHacker/moollm). The split is deliberate: a tolerated
address under a Dutch municipal beleidsregel is jurisdiction-bound, while the things it
inherits from are not.

- [`place`](https://github.com/SimHacker/moollm/tree/main/skills/place) — where it is, who was here before, what may be uploaded
- [`room`](https://github.com/SimHacker/moollm/tree/main/skills/room) — the interior, its contents, and what it advertises
- [`budtender`](https://github.com/SimHacker/moollm/tree/main/skills/budtender) — the person behind the counter
- [`designs/korz/`](https://github.com/SimHacker/moollm/blob/main/designs/korz/README.md) — subjective dispatch, which is how one menu becomes four views

## Part of MOOLLM

**This skill's directory (browse and fetch everything):** [skills/coffeeshop/](https://github.com/SimHacker/amsterdank/tree/main/skills/coffeeshop)

- **MOOLLM:** [repo](https://github.com/SimHacker/moollm) · **Skill index and docs:** [skills/README](https://github.com/SimHacker/moollm/blob/main/skills/README.md)
- **This skill is not part of the official MOOLLM skill set.** It is a MOOLLM-compatible
  skill in an application repo, which is the normal case for anything with a jurisdiction.
