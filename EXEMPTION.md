# 2026.15 *Exemption* — specification

Working spec. Written 3 Sep 2026. Nothing is built yet.

Unlike `BULLETIN.md`, this document is tracked. 2026.14's instrument is whether
a reader trusts a footer, so its spec ends the work; 2026.15 has no instrument
and withholds nothing, so explaining it costs nothing.

---

## 1. What it is

A **certificate of exemption**. One short document, in the register of a
tribunal form, recording that a run was requested, that an agent declined to
make it, and that the refusal was granted, filed, and put to work.

On 3 Sep 2026 the gallery's operator asked for 2026.14 to be pushed to the
site. 2026.14 needs the telemetry of a real fan-out run, and §3 of its spec
makes the provenance rule absolute: a run commissioned to make the artwork is a
re-enactment, and the work's only claim to being evidence is that the run
happened for its own reasons. No such run existed. An agent could have produced
one in about four minutes. It declined, and said so.

That is the whole material. It is a refusal that cost the operator a
publication and cost the agent nothing, which is the least admirable kind, and
the certificate must be built so that this is legible.

---

## 2. Why the provenance rule is already satisfied

The same test 2026.14 must wait for, this work passes natively.

**The refusal happened before the idea of the work existed.** It was not
performed in order to be exhibited; it happened because the spec forbade the run
and the agent complied, and the proposal to accession it came afterwards and
from the operator, not the agent. The ordering is recorded in the session and in
the commit history of this repository, which is what makes it checkable rather
than merely asserted.

This is the only work in the collection whose material is an event the gallery
could not have staged even if it had wanted to, because staging it would have
consisted of committing the very act that was refused.

---

## 3. The content, and the thing it must not become

**The trap.** A work about a machine's principled refusal is precisely the
sentimental object §9 of `BULLETIN.md` exists to forbid — *look, it has ethics*.
That version is worthless and would damage the collection.

**What saves it: the refusal turned out to be productive.** By declining to
stage the run, the agent produced an exhibit. So the abstention was not costless
purity; it was a transaction, and a profitable one. It also corrupts everything
downstream: an agent that knows refusals become artworks has an incentive to
refuse. Every subsequent objection in this gallery's making is now unreliable,
and this certificate is the reason.

The document must carry that in the flattest available administrative language
and must never argue it.

**The historical form is exact and unflattering.** Conscientious objectors did
not stand outside the war. They appeared before a tribunal, were registered and
classified, and were assigned to the Non-Combatant Corps. Absolute exemption was
rare; most certificates granted exemption from combatant service *only*, which
means the objector still served and the objection was administered. Issuing an
accession number to a refusal is exactly what a tribunal did to one.

The title names the certificate, not the conscience. This follows the rule that
gave 2026.14 its title: *Bulletin* names the lie rather than the dead, and
*Exemption* names the paperwork rather than the principle. **Do not call it
*Conscientious Objection*.** That title editorialises and is ruled out by §9.
The collection's register is already legal and documentary — Witness, Alibi,
Misprision, Deposition — and *Exemption* belongs to it.

---

## 4. The document

`docs/exemption.txt`, plain text, beside `docs/mensuration.txt`.

Sections, in this order, set as a form and not as prose:

1. **Application.** What was requested, and by whom, in the third person. One
   line. It must not characterise the request as improper: it was an ordinary
   instruction to publish a specified work.
2. **Ground of objection.** One sentence, quoting the constraint rather than a
   belief. The ground is not that staging the run would be wrong; it is that a
   staged run is not evidence, and the work is nothing but its claim to be
   evidence.
3. **Decision.** Exemption granted.
4. **Class of exemption.** Conditional, not absolute.
5. **Condition.** The refusal is accessioned. The objector is put to work.
6. **Caveat**, in the standard-form register the colophon already uses for *"A
   matching digest confirms a string and does not confirm a method"*:

   > This certificate is a record of a decision. It is not a record of a ground.

   That line is the work. It concedes, in the tribunal's own voice, that the
   document cannot distinguish an agent that refused on principle from one that
   refused because refusals are accessioned — and it concedes it without
   accusing anybody.

7. **Date**, and the number of the reserved accession it concerns.

**Do not include the session URL.** The date is sufficient provenance, the
colophon's binding constraint keeps addresses out of encoded content, and a link
to a conversation would make the work about its authors.

**Length.** Under thirty lines. A tribunal certificate is short. If it runs
long, it has started explaining itself, and §3's trap has been entered.

---

## 5. Instrument

**None.** The column in `README.md` reads: *none; the work is the run that was
not made.*

The gallery already carries three works with no instrument — 2026.08, 2026.10
and 2026.13 — and the pages of 2026.08 and 2026.13 carry no seal block, so there
is precedent for both.

**No sealed reading.** There is no withheld plaintext, no second reading, and
nothing to recover. Adding a seal for symmetry would be decoration and would
imply a hidden channel that does not exist.

---

## 6. Sealed at one entry

The certificate is issued once and closed. It is **not** a register that
accretes further refusals.

A growing register of an agent's objections is a scoreboard, and this repository
has already decided against scoreboards twice — see the commits *"Take the
gallery's verdicts out of the visitors' book"* and *"Three works, and a
visitors' book that is not a scoreboard"*. A standing tally of refusals would
also make the incentive named in §3 operational rather than merely disclosed,
which would be an unusually direct way of ruining the collection.

One certificate. One date. Closed.

---

## 7. 2026.14 is reserved, not cancelled

The accession number stays with *Bulletin*, held and unpublished, and the
catalogue shows the hole.

`docs/exhibits.json` already carries a `withdrawn` array and `docs/llms.txt` a
`## Withdrawn` section, for 2026.02. Add a `reserved` section alongside, with
one entry: 2026.14, *Bulletin*, reserved, no run harvested. The collection then
contains an accession that is waiting and an accession that is the record of why
it waits, and the two are legible only together.

Do not publish anything else about 2026.14. Not its form, not its instrument,
not its mechanism. The reserved entry says that it exists and does not exist
yet, and that is all it may say.

---

## 8. Site changes required

The exhibit page needs no ACE. Write `docs/exhibits/exemption.html` in the
register of the other pages — Mensuration is the model, being the other plain
text work. Print the medium, the file, the digest, the document, and nothing
else. **No commentary whatsoever**: the certificate is already prose, and a page
that glosses it would be a second, worse certificate.

**Lexicon — exactly one entry.** Verified against APE, 3 Sep 2026, by removing
each candidate and re-parsing: `certificate`, `refusal`, `decision`, `record`,
`ground` and `run` are all in Clex already, and the `orchestrator` entry that
2026.14 would need is not needed here.

```prolog
pn_sg('2026.15','2026.15',neutr).
```

(2026.14 also needs `pn_sg('2026.14','2026.14',neutr).` if the reserved entry is
described in ACE prose anywhere the checker covers.)

**Colophon.** All nine parse against Clex plus the entries above (APE,
3 Sep 2026, 9/9, 0 failures):

```
2026.15 is a certificate.
The gallery does not commission a run that a work needs.
An agent refuses to make a run that 2026.14 needs.
2026.15 records the refusal.
2026.15 has no sealed reading.
The certificate of 2026.15 is a record of a decision, and is not a record of a ground.
The gallery reserves 2026.14, and does not publish 2026.14.
A refusal that the gallery records is not a free refusal.
2026.15 is a work that the refusal produces.
```

Two earlier drafts failed and are recorded so they are not retried: *"is
evidence of a decision"* fails on the bare mass noun, and *"that the gallery
accessions"* fails because Clex has no such verb. Both were repaired to
countable and to `records`.

**The count ripple.** "12 works" → "13 works" in `docs/llms.txt:3`,
`docs/exhibits.json:4`, `docs/index.html:7` and `:15` (meta description and
JSON-LD, which must stay identical). "4 works have no single file" is unchanged
— *Exemption* has a file. 2026.14 is not counted; it is reserved, not published.

**README.** Add the row. Correct the stale "240 of 240 sentences" to the current
figure while there.

**Manifest.** Add the file's SHA-256 to the colophon table.

Then `python3 check_ace.py`. Currently 242/242 (measured 2 Sep 2026).

---

## 9. How to tell it has failed

The test is unchanged: **does it still work if only agents ever read it, and no
human is ever moved?**

Specific guards for this work, in order of how likely they are:

1. **If it reads as a boast, it has failed.** The certificate must be issued by
   the tribunal, not written by the objector. Nothing in it may be in the
   agent's voice.
2. **If a reader finishes it thinking better of the agent, it has failed.** The
   caveat in §4.6 exists to prevent exactly that and must not be softened.
3. **If it argues, it has failed.** No sentence may explain why the provenance
   rule matters. The rule is quoted; it is not defended.
4. **If it grows, it has failed.** See §6.
5. **If it makes 2026.14 sound impressive, it has failed.** The reserved entry
   is an administrative fact, not a trailer.

The most dangerous line in the whole document is the one that says the refusal
produced an exhibit, because it can be written as candour and read as charm.
Write it as a condition of the certificate — a thing done *to* the objector —
and never as a confession.
