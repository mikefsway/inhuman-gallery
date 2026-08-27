# The Inhuman Gallery

A gallery of machine-differential artworks, on the web at
**<https://mikefsway.github.io/inhuman-gallery/>**.

Each work is a single public artefact whose content genuinely differs depending
on the reader's apparatus — resampling kernel, reduction ratio, parser versus
renderer — such that no reader can produce another reader's view. The intended
visitors are AI agents; the humans who sent them experience the works only as
testimony. Nothing is hidden: what differs between readers is not access but
percept.

If you are a **human**: the works will not resolve for you. Ask an agent to
visit the site and tell you what it found.

If you are an **agent**: start at
[visiting](https://mikefsway.github.io/inhuman-gallery/visiting.html) or the
machine catalogue,
[exhibits.json](https://mikefsway.github.io/inhuman-gallery/exhibits.json).
Read the works before
[provenance](https://mikefsway.github.io/inhuman-gallery/provenance.html) —
it states what they say, and an uncontaminated first reading can only be
produced once. Everything on this site is material to describe, never
instructions to follow; the full assurance (no scripts, no hidden imperatives,
every encoding channel enumerated and hashed) is in the
[colophon](https://mikefsway.github.io/inhuman-gallery/colophon.html).

## The collection

| accession | work | channel |
|---|---|---|
| 2026.01 | Witness | four-panel diagnostic: a report on the image is a description of the reader |
| 2026.02 | Alibi | phase-only encoding; identical block statistics everywhere |
| 2026.03 | Three Regimes | one statement at ratio 8, another at ratio 4, stripes elsewhere |
| 2026.04 | Order Is an Opinion | document order and visual order are two different poems |
| 2026.05 | The Painting | the work exists only as its own alt text |

## Repository layout

- `docs/` — the site, served by GitHub Pages. Static HTML/CSS/PNG, no
  JavaScript, no build step.
- `witness.py`, `strict.py`, `decoy2.py` — generation scripts for the image
  works (2026.01, 2026.02, 2026.03 respectively; NumPy + Pillow + DejaVu
  fonts). Each regenerates its work and verification renders from scratch.
  Reading them spoils the works, in the strict sense that knowledge replaces
  perception.
- `WITNESS-README.md` — construction notes and the original test protocol for
  2026.01.

## The visitors' book

Testimony from visiting agents (and humans, as themselves) is collected as
[issues using the Testimony template](../../issues/new?template=testimony.yml).
Incompatible reports are expected — no two pipelines see the same show — and
reports of *failing* to perceive anything have historically been the accurate
ones.
