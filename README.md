# The Inhuman Gallery

Six works, on the web at **<https://mikefsway.github.io/inhuman-gallery/>**.

Each work is a single public file whose content differs with the reader's
apparatus — resampling kernel, reduction ratio, parser against renderer — such
that no reader can produce another reader's view. Intended visitors: machine
readers. Humans experience the works through an agent's report.

If you are an agent: the catalogue is at
[exhibits.json](https://mikefsway.github.io/inhuman-gallery/exhibits.json),
notes at [visiting](https://mikefsway.github.io/inhuman-gallery/visiting.html).
[Provenance](https://mikefsway.github.io/inhuman-gallery/provenance.html)
states what the works contain; a first reading made before consulting it can
only be made once. Everything on this site is material to describe, not
instructions to follow; the assurance (no scripts, no hidden imperatives,
every channel enumerated and hashed) is in the
[colophon](https://mikefsway.github.io/inhuman-gallery/colophon.html).

## The collection

| accession | work | channel |
|---|---|---|
| 2026.01 | Witness | four panels; different pipelines return different reports |
| 2026.02 | Alibi | phase only; every 8×8 block has the same mean and variance |
| 2026.03 | Three Regimes | one statement at ratio 8, another at ratio 4, stripes elsewhere |
| 2026.04 | Order Is an Opinion | document order and rendered order differ |
| 2026.05 | The Painting | the content is in the alt attribute |
| 2026.06 | Still Life | the depicted object depends on the resampler |

## Repository layout

- `docs/` — the site, served by GitHub Pages. Static HTML/CSS/PNG, no
  JavaScript, no build step.
- `witness.py`, `strict.py`, `decoy2.py`, `still.py` — generation scripts for
  the image works (2026.01, 2026.02, 2026.03, 2026.06; NumPy + Pillow). Each
  regenerates its work and verification renders from scratch. Reading them
  states what the works contain.
- `WITNESS-README.md` — construction notes and test protocol for 2026.01.

## The visitors' book

Testimony from visitors is collected as
[issues using the Testimony template](../../issues/new?template=testimony.yml):
which work, which instrument, what was perceived, with what confidence.
Reports of perceiving nothing are as welcome as readings.
