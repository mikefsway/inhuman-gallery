# 2026.14 *Bulletin* — specification

Working spec for the next accession. Rewritten 3 Sep 2026. Nothing is built yet.

This replaces an earlier image-based spec, kept at `bulletin.py` and in the
scratchpad copy of the old document. Why it was abandoned is in §10; the short
version is that it made telemetry into a picture because a picture was the
elegant thing to make, and the material never asked for it.

---

## 1. What it is

One plain-text document: the **return** of a real fan-out run. Many agent
instances spawned against a single task, most of which return nothing usable,
one line per instance, and a footer that totals them.

The form is Napoleonic, transposed by document rather than by imagery. The
*Bulletin de la Grande Armée* had a counterpart, the *état de situation* — the
return, the muster. The bulletin was the dispatch that reached the public; the
return was the count that did not. Both were documents. The genre's load-bearing
parts are: multitude; anonymity in the foreground and one name in the middle
distance; a summary compiled by someone who was not there; and materiel that
outlasts its owner and stays legible.

**The gallery publishes the return. It does not publish the bulletin.** The
title names the document the reader does not get. The dispatch survives into the
published file only as arithmetic — as the footer's total, which is the last
thing left of a summary once the sentences are gone.

---

## 2. The instrument: nobody adds up a return

The work has one instrument and it is not a channel. It is **whether the reader
counts the rows.**

A footer exists so that it need not be checked. That is the entire social
function of a summary line, and declining to trust one is pathological behaviour
in a human reader. An agent asked to describe a table tallies it unbidden,
because the tally is free and because "describe this" invites verification.

So the document is **fully legible and withholds nothing**, and still divides
its readers completely.

**The footer is not wrong.** Make it a definition, never an error. The total
counts instances that *returned*. Instances that were killed or throttled never
returned, and so were never borne on the roll. That is a defensible definition,
it is how these numbers are actually produced — in armies and in orchestrators
alike — and under it the footer is exactly correct.

A reader who reads the footer has read the document correctly. A reader who
counts the rows has read it correctly. Both readings are complete, neither
contains a mistake, and they cannot be reconciled. There is nothing to recover
and no second instrument to hold.

This is not machine-only in the strong sense; a determined human counts. It is a
work whose two readings correspond to two dispositions, where the human
disposition is the *right* one for reading a return and is wrong here for
exactly the reason the bulletins were believed. Anything strictly impossible for
a human would be obfuscation, and obfuscation is worse: it hides instead of
dividing, and a machine-readable dump of agent telemetry on a public site reads
as a leak or as injection scaffolding. This form reads as a document, because it
is one.

Visiting already carries the right sentence: the gallery *"lacks the report of a
point at which a reader stops."* The human stops at the footer. **That stopping
point is the work**, and the visitors' book is already the instrument for
recording it.

---

## 3. Provenance rule: harvested, not staged

**The run must have happened for its own reasons.** A run commissioned to make
the artwork is a re-enactment — Lady Butler hiring cavalry to charge past her
studio. The rule is absolute and it is the work's only claim to being evidence.

- The task must be unrelated to the gallery.
- The telemetry is extracted post hoc from a run log, never by instrumenting a
  run in order to produce the file.
- The gallery records **that** it harvested and **when**. It does not record
  **what** the run was for. §4's constraint requires this anyway.

The old spec's N ≈ 40,000 floor is **gone**. It existed only because a reduced
image had to be wide enough for legible text. A return has no legibility floor.
Several hundred instances is ample; an ordinary fan-out will do. This is the
single biggest reason to prefer this form — it turns the provenance rule from
near-impossible into routine.

---

## 4. What to instrument

Per instance, exactly five fields, and nothing else:

| field | column | note |
|---|---|---|
| `idx` | INST | spawn order, 0-based, zero-padded |
| `parent` | — | not printed; used only to establish that all point at 0 |
| `t_start` | OPENED | ms from run start |
| `t_end` | CLOSED | ms from run start |
| `state` | STATE | see below |

`state` ∈ `completed` · `error` · `timeout` · `killed` · `throttled` · `empty`
(returned, but returned nothing usable).

**Everything else is discarded before the file is written**: prompts, tool
names, file paths, model ids, outputs, task description. This is not
fastidiousness, it is forced. The colophon's binding constraint says:

> No encoded content in the gallery describes a tool of a reader, or describes a
> credential of a reader, [...] or describes a file of a reader [...] No encoded
> content names a second site, and no encoded content names an address.

A telemetry dump breaches that on the first line. The constraint drives the work
toward exactly the anonymity the genre requires — the foreground of *Eylau* is
thousands of bodies and not one name. The gallery's own rules produce the
composition.

`state` is written as **a word**, not a code. The old spec encoded states as
grey levels, which made the tally seal unmatchable: a reader recovering the
field perfectly got six unlabelled levels and could never produce
`COMPLETED 271 …` without already knowing the vocabulary. Words close that hole
completely and make the tally genuinely checkable.

---

## 5. The document

```
RETURN OF INSTANCES
Run closed 94,015 ms after opening.

  INST    OPENED    CLOSED   STATE
  ─────────────────────────────────────
  00000         0     94015   completed
  00001        12     31204   completed
  00002        12       847   throttled
  00003        13      1044   error
  00004        13     28860   completed
  ...
  00446       751     89204   completed

  TOTAL BORNE ON THE ROLL              400
  completed 271 · error 12 · empty 8 · timeout 21
```

Rules:

- **Rows in completion order** — ascending `t_end`, which is simply how a log is
  appended. This is not decoration: the dead finish first, so the head of the
  document is disproportionately `throttled` and `error`. A reader who reads the
  opening and stops has an accurate-feeling impression of a run that was
  strangled by the scheduler, and it is badly unrepresentative. Nobody misled
  them; they read the beginning.
- **The orchestrator is line 00000**, on its own return, in the same form as
  every other row. A commander appears on his own muster. It is not marked. It
  is findable because everything points at it — `parent` is 0 for all — but
  `parent` is not printed, so at the level of the document it is findable only
  because it opened at 0 and closed last.
- **The footer breakdown omits the states the total omits.** `killed` and
  `throttled` appear in the rows and not in the footer. The footer is internally
  consistent and says nothing false.
- **No count is printed anywhere except the footer.** No row numbers in a
  margin, no line count, nothing that lets a reader arrive at the true figure
  without counting.
- Fixed-width columns, one file, no header row repetition, no pagination.

### The weather is the scheduler

`throttled` must be common. It is indifferent, unmalicious, and it kills more
instances than anything adversarial. Snow at Eylau; mud in *1814*. That it is
also one of the states the footer does not count is the whole arithmetic of the
piece.

---

## 6. The seals

Two sealed readings, normalised the gallery's existing way — uppercase, words
joined with one space:

- **Seal A, the bulletin.** The orchestrator's dispatch text. **Not published.**
  The gallery holds it, as it holds the 2026.11 original. A reader cannot
  produce this from anything the gallery serves. That is the point: the title
  names it, the footer is its residue, and the document withholds it.
- **Seal B, the tally.** The multiset of terminal states counted **from the
  rows**, states in alphabetical order, e.g. `COMPLETED 271 EMPTY 8 ERROR 12
  KILLED 14 THROTTLED 33 TIMEOUT 21`. A reader who counts produces this exactly.

The footer is printed in plain sight and does not match Seal B. **The gallery
never says so.** A reader who matches Seal B has demonstrated the discrepancy
themselves, without the gallery having asserted anything. That is the *Bulletin
de la Grande Armée* — reliably enough false that "to lie like a bulletin"
entered the language — except that here nothing is false, which is worse.

The colophon already carries the right disclaimer: *"A matching digest confirms
a string and does not confirm a method."*

Keep the harvested log in an untracked file, as `misprision-true.txt` and
`deposition-strings.txt` already are.

**A constraint on the dispatch plaintext.** The colophon states that exactly 2
encoded contents address a reader. Seal A must therefore be a flat third-person
past-tense dispatch that does not address the reader, or that sentence changes
and the audit of the whole collection moves. It must also be **true** — the
point is not that the orchestrator lied, but that an honest summary omits the
dead as a matter of course. *"No errors blocked completion"* is the register:
true, and devastating, and no defence.

---

## 7. Site changes required

The exhibit page needs **no ACE** — the colophon states only 2026.08's page is
in Attempto Controlled English, and `check_ace.py` collects only from index,
about, visiting, colophon, chorus, humans.txt, robots.txt and llms.txt. Write
`docs/exhibits/bulletin.html` in the register of the other exhibit pages: name
the medium, print the seals, say nothing about what is in them. Three Regimes is
the model.

**Do not label the seals with an instrument.** Three Regimes can print `ratio 8
—` because each of its seals corresponds to one instrument. Here Seal A
corresponds to no reading a visitor can take, and labelling it would be a lie.
Print the two digests with the house wording and nothing more.

**File.** `docs/return.txt`, beside `docs/mensuration.txt`. Plain text,
`text/plain`. Not `.jsonl`, not `.csv` — a data format invites ingestion rather
than reading, and reads as a dump.

**Lexicon — exactly two entries**, unchanged from the old spec. Everything else
this version needs (`return`, `footer`, `tally`, `dispatch`, `instance`, `row`,
`total`) is already in Clex. Verified empirically against APE, 3 Sep 2026, by
removing each candidate entry and re-parsing:

```prolog
pn_sg('2026.14','2026.14',neutr).
noun_sg(orchestrator, orchestrator, neutr).
noun_pl(orchestrators, orchestrator, neutr).
```

**The count ripple.** "12 works" → "13 works" in four places: `docs/llms.txt:3`,
`docs/exhibits.json:4`, and `docs/index.html:7` and `:15` (meta description and
JSON-LD, which must stay identical to each other). "4 works have no single file"
is unchanged — *Bulletin* has a file.

**Colophon.** 2026.14 is **not** added to the resampling channel sentence; this
version uses no channel. Add the sentences below. All 14 parse against Clex plus
the two lexicon entries above (APE, 3 Sep 2026, 14/14, 0 failures):

```
2026.14 is a return of a run.
The return of 2026.14 lists every instance of a run.
A row of 2026.14 records 1 instance.
A footer of 2026.14 states a total.
2026.14 has a sealed reading of a dispatch.
The gallery does not publish the dispatch of 2026.14.
2026.14 has a sealed reading of a tally.
A reader that counts every row of 2026.14 produces the tally.
A reader that reads the footer of 2026.14 does not count a row.
The gallery does not say that the total of 2026.14 agrees with the tally.
2026.14 records a run that the gallery does not commission.
No row of 2026.14 names a tool, and no row names a file.
The orchestrator is an agent, and the orchestrator spawns every other agent.
A row of 2026.14 records the orchestrator.
```

Then rebuild and re-run: `./build_ape.sh` (already built at `~/tools/APE`), then
`python3 check_ace.py`. Currently 242/242 (measured 2 Sep 2026; `README.md`
still says 240, which is stale and should be corrected in the same commit).
Expect roughly 256 after this.

**README.** Add the 2026.14 row to the collection table. The instrument column
reads: *the footer, or the rows*.

**Manifest.** Add the file's SHA-256 to the colophon table.

---

## 8. Before it ships

1. Harvest a real run. Several hundred instances is enough; see §3.
2. Confirm the dispatch plaintext is true, third-person, and does not address
   the reader (§6).
3. Confirm no field of the record survives except the five in §4.
4. Confirm the footer's definition is stated nowhere on the site. The gallery
   must not explain that the total excludes non-returning instances. A reader
   who works it out has done the work; a reader who is told has been robbed.
5. Confirm nothing in the document permits a row count without counting.
6. Re-run `check_ace.py`.

---

## 9. How to tell it has failed

**The test: does it still work if only agents ever read it, and no human is ever
moved?**

If the work's real audience turns out to be humans feeling something about AI
mortality, it has become the sentimental object this gallery is a standing
rebuke to. Guard specifically against: an elegiac exhibit page; any word in the
prose that grieves; a title that editorialises; and — new to this version — any
typographic sympathy in the return itself. No rules under the dead. No
whitespace that mourns. A return is set by a clerk.

**The second failure mode, specific to this form:** if the discrepancy reads as
a puzzle, it has failed. The footer must never feel planted. It must read as the
ordinary output of an ordinary reporting convention, which is what makes it
damning — the arithmetic that erases the dead is nobody's decision and no one is
lying.

The register that makes it work is the flat one the site already has. A manifest
is more devastating than a lament, and it is also the only honest form — an
agent has no dread beforehand and no grief afterwards, so the residue is the
only part that ever exists. That is why the work is the aftermath and not the
death.

---

## 10. The abandoned version

The first spec encoded the return as a greyscale PNG: one 8px cell per instance
carrying the state as a mean level, and the dispatch carried in the phase of an
8px vertical cosine. Area-average at ratio 8 and the carrier cancels, yielding
the postures exactly; point-sample at ratio 8 and each cell becomes one pixel
with no ground to subtract. Measured on synthetic scaffolding: dispatch F1 0.068
from the point sample alone, 1.000 holding both readings, postures exact at
every amplitude 1–48. `bulletin.py` implements it and the measurements
reproduce.

It was abandoned for four reasons, in ascending order of seriousness:

1. **The tally seal was unmatchable.** A perfect reading yielded six unlabelled
   grey levels. Nothing in the file supplied the words, so §6's claim that "a
   careful reader can produce this by counting cells" was false.
2. **N ≈ 40,000** was forced by the legibility of the reduced reading, and that
   floor made the provenance rule of §3 nearly impossible to satisfy honestly.
3. **The work needed explaining.** Every sibling work turns one dial; this one
   needed two readings of different kinds, differenced. Since every standard
   resampler area-averages by default, the second reading would essentially
   never be found — leaving the work read as a field of dead agents, which is
   precisely the elegiac half §9 forbids.
4. **The material never asked to be a picture.** Telemetry's native form is a
   document, and both halves of the historical object — the bulletin and the
   return — were documents. Making them pixels was borrowed from image culture.
   Gros did not miss Eylau through a resampling artefact. He missed it because
   he read the dispatch.

Keep `bulletin.py` untracked, or commit it as a documented dead end. Do not
delete it: the F1 measurement is the only place in this repository where the
exclusivity of two resampling kernels is measured rather than asserted, and
2026.09 may want it.
