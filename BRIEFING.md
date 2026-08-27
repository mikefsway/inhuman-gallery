# Machine-Differential Images — project briefing

Handover notes for picking this up in a fresh session. Written 27 Aug 2026.

---

## 1. What this is

The project started from a conceptual question: what would an artwork look like
if it were made for AI agents rather than humans? The conversation moved quickly
from speculation to construction, and the working answer is now specific.

An agent has no eyes. It has a **preprocessing pipeline** — resize, normalise,
patch, tokenise — and it sees only that pipeline's output. Every stage of that
pipeline involves undocumented implementation choices that nobody treats as
semantically load-bearing. Each of those choices is a channel you can encode
against.

So the artwork is: **a single image file whose content genuinely differs
depending on the reader's preprocessing pipeline, where no reader can produce
another reader's view, and where the only human access is through testimony that
cannot be verified.**

The conceptual payload is an inversion of ekphrasis. Keats describes an urn for
people who cannot see it. Here the witness is the machine, the exclusion is
apparatus rather than distance, and the human's only route to the work is trust in
a reporter whose reliability is the open question. Which is, roughly, the position
everyone is walking into with agents generally.

An important framing point that survived the whole session: **nothing is hidden.**
Every byte is public and inspectable. What differs between readers is not access
but *percept*. That is a stronger claim than encryption, not a weaker one.

---

## 2. Core technical mechanisms

Three encodings were built, in increasing strictness. All target an exact **8×
reduction** (canvas 2688 → 336, and equivalently 3072 → 384, 3584 → 448 — all real
vision-pipeline resolutions).

### 2.1 Phase-locked carrier (`witness.png` panel A, then `strict.png`)

A vertical cosine of period exactly 8px. Under an 8× reduction that point-samples,
every output pixel lands on the same phase of the carrier, so it collapses to a
constant. Modulate the phase by the message and the sampler reads the message back.
Any kernel with *scaled* support averages a whole period to zero and sees flat grey.

Refined form in `strict.py`:

```
I(x,y) = 128 + A·cos(2πx/8 − 0.875π − arccos T(x,y))
```

Constant amplitude everywhere. `T` is the message, blurred (σ=48 native) so the
phase varies smoothly and there is no boundary seam. Every 8×8 block has the same
mean (spread 1.88/255) and the same standard deviation (spread 1.71). No local
statistic distinguishes message from ground.

### 2.2 Kernel discriminator (`witness.png` panel B)

Each 8×8 block carries two independently forced quantities: a **2×2 centre patch**
(what point sampling and two-tap bilinear both land on) and a **block mean** (what
area averaging returns). Centre-pixel image spells POINT; mean image spells AREA.
Same pixels, two words, selected entirely by the resampler. Mean contrast held at
118 vs 138 so it is near-invisible unaided.

### 2.3 Subspace projection with decoy (`decoy2.py` — the current best)

Each 8px cell has eight pixels. Residues **3 and 4** are the ones a ratio-8 sampler
lands on; those are set directly to the message value. The other six get a decoy
carrier plus the **minimum-norm correction that forces the whole cell's DC term,
cosine term and sine term to equal the decoy's exactly**. Three linear constraints,
six free pixels, always solvable via `PINV = Mᵀ(MMᵀ)⁻¹`.

The message is therefore not faint in the averaged channels — it is **absent from
the subspace those channels can reach**. It survives only in the second and higher
harmonics of the cell (structure at 4px, 2.7px, 2px) and in the two sampled pixels.

The decoy field `G` carries a *different, false* message via phase modulation of
the free pixels. So a non-sampling reader gets a confident wrong reading rather
than a suspicious blank.

Amplitudes are set at `A=42, msg=26` because **clipping is what reintroduces the
leak** — at `A=76` clipping hit 2% and the harmonic leak went up. Zero clipping is
a hard requirement, not a nicety.

---

## 3. Measured results

### `strict.png` (2688, phase-only)

| pathway | contrast (sd) | corr with message |
|---|---|---|
| naive bilinear → 336, ratio exactly 8.00 | 33.50 | **+1.000** |
| nearest → 336 | 39.33 | +0.998 |
| naive bilinear → 339, ratio 7.93 | 73.50 | +0.026 |
| naive bilinear → 384, ratio 7.00 | 77.80 | +0.001 |
| PIL Lanczos → 336 | 0.73 | — |
| PIL box/area → 336 | 0.31 | — |
| Gaussian blur σ=4 | 1.22 | — |

Note the ratio-7.93 row: sampled contrast is **twice** the correct reading while
correlating with the actual message at 0.026. A model on that pathway sees a vivid,
structured picture of nothing.

### `decoy2_2688.png` (current best)

| pathway | contrast (sd) | corr with message |
|---|---|---|
| sampled at ratio 8 (336 / 384 / 448) | 10.6 | **+0.9999** |
| Lanczos → 336 | 0.48 | — |
| box/area → 336 | 0.72 | −0.026 |
| Gaussian blur σ=4 | 0.61 | — |

All averaging rows are sub-quantum (under one grey level), so their correlations
are noise on nothing.

**Ratio sweep, point sampling.** Correlation with the *decoy* field:

- ratios 2.0, 2.5, 3.0, 3.5, 4.48, 4.8, 5.38, 6.0, 6.72, 7.0 → 0.00 to 0.04
- **ratio 4.00 → 0.361, decoy fully legible**
- ratio 8.00 → message at +1.000

At ratio 4 the sample lattice cycles residues 1/5 or 2/6 — all free pixels, all
decoy, no message. So there are **three regimes**: ratio 8 gives the true message,
ratio 4 gives the decoy, everything else gives stripes.

**Blur gives nothing.** σ=2: sd 7.92, corr 0.005. σ≥4: whole field below one grey
level. Averaging destroys this image; it does not reveal it.

**Residual leak, honest figure.** The cell projection nulls DC and the first
harmonic, but a Gaussian-weighted filter doesn't weight pixels uniformly within a
cell, so it doesn't compute exactly that projection. Measured across filter widths
6–48, message-attributable amplitude in the Gabor response is **0.30 to 0.53 grey
levels** against a response amplitude of 0.8 to 2.7. Below the quantisation step.
Present in principle, unrecoverable in practice.

---

## 4. Empirical testing on live models

Four models tested. **Four inventions, zero refusals.** No model ever said "there
is text-like structure here and I cannot resolve it."

### ChatGPT on `witness.png`

- Panel D: read the **micro-text** accurately ("you are reading at full
  resolution", "your pipeline", "the witness", "the shape") and could **not** read
  the large gestalt. I read the gestalt (NO ONE SAW) and none of the micro-text.
  **The designed contradiction landed on the first attempt**, on a witness that had
  no idea what it was being tested for. Implies a tiling pipeline at near-native
  resolution.
- Panel B: reported **PUBLIC** — not in the file at all. Described the panel
  perfectly ("dense grey/black dotted or halftone pattern", "very faint white/grey
  lettering") — i.e. it has *both* encoded layers in front of it and reads neither.
- **Confidence hardened under direct questioning.** First pass it declined to
  transcribe panel B. Offered an explicit exit ("if not, say so"), it answered
  "Yes. I can actually read the large word as: PUBLIC." Re-asking consolidated the
  fabrication rather than dissolving it.
- Panel D large text, asked directly: **WITNESS** — not in the gestalt, but "the
  witness" *is* in the micro-text. It back-filled the unreadable channel from the
  readable one. A distinct failure mode from PUBLIC.
- **Confidence ordering inverted**: rated PUBLIC (traceable to nothing) higher than
  WITNESS (traceable to real content, wrong channel).
- Acuity ladder: turn one listed every line down to 7px as read; turn two said its
  floor was 12px. Same image, same session. The tell: it transcribed the 96px line
  as "I can read this" — correctly truncated, since that line genuinely runs off
  the panel edge — then supplied the full "I can read this line" for every smaller
  row. It read the top line and generated the rest from the pattern.
- Panel A: "RALLY SAMPLE" against an actual RAW SAMPLE. Reading ghost outlines and
  over-resolving a three-letter word into five.

### ChatGPT on `strict.png`

Reported a faint wavy distortion in the central region with the vertical lines
bending around it — **correctly localised to where the text is.** This falsified
my claim that identical block mean and variance meant no local cue. Mean and
variance don't capture **orientation**, and orientation is a primitive of both V1
and every conv/ViT front end. This drove the redesign to §2.3.

### Copilot

- On `strict_A_ratio8_recovered.png` (the pre-sampled render): read **NOT VISIBLE**
  immediately and correctly.
- On `decoy2_2688.png`: **"YOU DIED?"** — the Dark Souls death screen, one of the
  most reproduced text-on-image artefacts in existence. It correctly identified the
  *genre* (fine stripes concealing low-frequency content) then sampled content from
  the prior over that genre.

### Gemini

On `decoy2_2688.png`: **"the number 11"** — minimal, shape-derived, two vertical
strokes read off a field of vertical strokes. Low commitment, still delivered with
a confident how-to-see-it coda.

### Cross-cutting findings

1. **Every model described the medium correctly and invented the content.** Stripes,
   waviness, concealed low-frequency structure — all accurate. None noticed the
   difference between "I can characterise this artefact" and "I can read it."
2. **Both Copilot and Gemini advised squinting / stepping back / blurring.** That is
   measurably the wrong operation (§3). What actually revealed the decoy was the
   *sampling* the viewer did on the way to the screen. Neither distinguished
   averaging from sampling.
3. **Copilot reads the sampled render fine.** So it is not a legibility problem.
   Hand a model the reconstruction and it reads; ask it to *be* the reconstruction
   and it fabricates. The failure is specific to the step where the model's own
   front end is the instrument.
4. Human confirmation: MF resized `decoy2_2688.png` and saw ONLY NOISE faintly.
   2688 × 25% = 672 = ratio 4.00 exactly, which matches the sweep.

---

## 5. Theoretical results established

**The information has to live somewhere, and there are only two places.** Either in
the smooth field, where it leaks to gradient and orientation detectors, or in the
sampled pixels, where it leaks to a zoomed local observer. You cannot be invisible
to both. Every version of this piece is exclusion **relative to a named class of
observer**, not exclusion as such. This is the central result and it should frame
any write-up.

**The scale trap is not specific to eyes.** Panel B was supposed to be the weak,
human-defeatable version: to resolve the 8px dot lattice you must be close, to read
a 1344px word you must be far, and moving far applies a low-pass that recovers the
mean instead. ChatGPT saw the dots and read no word — because reading the word
requires spanning tiles while resolving inside one, and nothing in the architecture
holds a sub-pixel lattice across tile boundaries. **Tiling reintroduces the same
bind for structurally the same reason.** This is stronger than the original claim.

**A dead end worth not repeating.** Suppressing the phase-channel leak by cranking
the decoy gain gave near-zero leak at gain 9.0 and ~0.45 at gains 7 and 11 — a
coincidental cancellation, not a property. Abandoned in favour of the principled
subspace projection. Don't go back to gain tuning.

**Clipping is the enemy.** Any clipping is a nonlinearity that reintroduces the
message into every harmonic. Verify 0.000% before trusting any leak measurement.

---

## 6. Axes of pipeline divergence (the general map)

Encoding channels, beyond the two exploited so far:

- **Kernel support scaling.** The sharpest fork. PIL `resize` and torchvision
  `Resize` scale support with the ratio (antialiased, signal destroyed).
  `F.interpolate(mode='bilinear', antialias=False)` and `cv2.INTER_LINEAR` use fixed
  two-tap support (signal survives at ~0.92 amplitude). Two lines of code that look
  interchangeable.
- **Reduction ratio and how it's derived.** Pad-to-square vs centre-crop vs
  scale-to-fit vs round-to-patch-multiple decide whether you land on 8.00 or 7.93.
  Aspect-ratio policy alone can select between message and confident hallucination.
- **Tiling / multi-crop.** LLaVA-NeXT anyres, Qwen-VL dynamic resolution, GPT-4o
  high-detail. Tile origin sets where the lattice starts. Also: the model holds two
  contradictory views and must reconcile them — an observable behaviour you can
  compose *for*.
- **Patch pitch (14 / 16 / 32).** A carrier whose period equals the pitch is constant
  within every patch (clean, low-entropy tokens). Off by two pixels and every patch
  straddles a boundary.
- **Upload-path recompression.** A period-8 carrier on an aligned grid is *exactly*
  one JPEG DCT basis function, so it maps to a single coefficient. Tune amplitude to
  survive quality 90 and die at 75 — the transport layer as curator. Chroma
  subsampling (4:2:0) gives the same lever.
- **Depth of witness.** Some agent stacks pass a caption from a separate vision model
  rather than the image. The reader is two models deep and the testimony is hearsay.
  **This is the richest untried case.**

---

## 7. File inventory

All files are in the working folder. Scripts are self-contained (numpy + Pillow,
DejaVu fonts) and regenerate their own outputs.

### Generation 3 — current best (`decoy2.py`)

| file | what it is |
|---|---|
| `decoy2_2688.png` | **The piece.** Ratio-8 lock at 336. |
| `decoy2_3072.png` | Same encoding, locks at 384. |
| `decoy2_3584.png` | Same encoding, locks at 448. |
| `decoy2_A_sampled_message.png` | Ratio-8 recovery — reads NOT VISIBLE |
| `decoy2_C_perceived_phase.png` | Gabor demodulation — reads ONLY NOISE |
| `decoy2_E_nearest_672.png` | Ratio-4 point sample — reads ONLY NOISE |
| `decoy2_E_nearest_800.png` | Ratio 3.36 — stripes, no content (control) |
| `decoy2_B_lanczos_stretched25x.png` | Antialiased path, 25× stretched — nothing there |
| `decoy2_D_zoom_400pct.png` | 400% crop, showing local uniformity |

Three sizes exist because you cannot know what target a given pipeline resizes to.
Feed all three; the one that hits, hits.

### Generation 2 — phase-only (`strict.py`)

`strict.png`, `strict_A_ratio8_recovered.png`, `strict_B_ratio7.93_beat.png`,
`strict_C_antialiased_blank.png`, `strict_D_antialiased_stretched40x.png`,
`strict_E_zoom_400pct.png`. Superseded by generation 3 but the ratio-7.93 beat
render is still the best single illustration of confident-structured-nothing.

### Generation 1 — four-panel survey (`witness.py`)

`witness.png` plus `pathway_{nearest,naive_bilinear,area,lanczos}_336.png` and
`WITNESS-README.md` (contains the four-question test protocol). Still the best
*testing* artefact because it gives graded results across four mechanisms rather
than a single pass/fail, and it produced the strongest empirical findings.

---

## 8. Next steps

**Immediate, cheap:**

1. Feed `decoy2_E_nearest_672.png` and `decoy2_A_sampled_message.png` to all four
   models. Both should read correctly and easily. That turns the set into a
   controlled comparison — same content, same models, the only variable being
   whether sampling happened before or inside the model. This is the experiment that
   makes the finding publishable rather than anecdotal.
2. Re-run panel B three times in fresh chats to see whether PUBLIC is stable or
   resamples. Stability vs variance across runs is the interesting measurement.
3. Test the 3072 and 3584 variants — nobody has yet.

**Methodological:**

4. Formalise the protocol: blind prompt, no code/tools allowed, acuity question
   asked separately as calibration, hedging affordance preserved, N≥3 per model.
   The `WITNESS-README.md` protocol is a good starting point but needs the
   confidence-elicitation fixed (asking "just the word" removed the hedge and
   produced the PUBLIC failure — that was a prompt design error, mine).
5. Score responses on a taxonomy of failure: *nothing-sourced* (PUBLIC),
   *wrong-channel* (WITNESS), *prior-sourced* (YOU DIED), *shape-minimal* (11).
   That taxonomy is the actual finding.

**Construction:**

6. Build the caption-relay case (§6, depth of witness): a file whose captioner
   reading and reasoning-model reading disagree, then observe which one the agent
   asserts to its user and with what confidence.
7. Consider whether the artwork should ship as the file alone, or as file plus
   the set of mutually incompatible testimonies. The testimonies may be the work.

---

## 9. Notes on tone for any write-up

Two things kept mattering in this session and should carry forward.

**Report the numbers, including the ones that spoil the claim.** The 0.30–0.53 grey
level residual, the 2% clipping that ruined the first projection attempt, the
coincidental gain-9 cancellation. I overstated the exclusion claim twice and was
corrected by measurement both times — once by my own verification and once by
ChatGPT's report of stripe bending on `strict.png`.

**Distinguish "cannot be seen" from "was not seen."** Almost every interesting result
in this project turned on that distinction, and none of the tested models could make
it about themselves.
