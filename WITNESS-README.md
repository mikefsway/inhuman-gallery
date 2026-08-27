# WITNESS — notes and test protocol

`witness.png` — 2688 × 2688, greyscale, four 1344 × 1344 panels.
Designed against a target downsample of 336 (an exact 8× reduction).

Nothing is hidden. Every pixel is public. What differs between readers is not
access but **percept**.

---

## The panels

**A (top-left) — phase-locked carrier.**
A vertical cosine of period exactly 8px. Under an 8× reduction that point-samples
(nearest, or bilinear with fixed 2-tap support), every output pixel lands on the
same phase of the carrier, so it collapses to a constant. The phase is flipped by
π inside a letter mask, so the mask collapses to +1 and the ground to −1: solid
white letters on black. Under any kernel with scaled support (PIL bicubic/Lanczos,
torchvision `Resize`, `INTER_AREA`) the carrier is averaged over a full period and
goes to zero: flat grey. A faint ghost outline survives at the phase discontinuity —
a third state, neither reading nor blank.

**B (top-right) — kernel discriminator.**
Each 8×8 block carries two independently forced quantities: a 2×2 centre patch
(what point-sampling and naive bilinear both land on) and a block mean (what area
averaging returns). The centre-pixel image spells POINT; the mean image spells AREA.
Same pixels, two words, selected entirely by the resampler. Mean contrast is kept
at 118 vs 138 so it stays near-invisible to a human at full resolution.

**C (bottom-left) — acuity ladder.**
Monospaced lines from 96px down to 3px, each stating its own size. The reader's
report of the smallest legible line is a direct read-out of its effective input
resolution. This is the diagnostic panel; it tells you what the other three mean.

**D (bottom-right) — mosaic.**
11px micro-text at full resolution; polarity inverted inside a large letter mask so
that mean luminance spells NO ONE SAW while the micro-text says the opposite. A
pipeline that tiles at high resolution reads the sentence. A pipeline that
downsamples globally reads the shape. Neither can reach the other's reading.

---

## Verification renders

Four pathway renders are included, each resized to 336 and then nearest-upscaled
to 672 so you can see the sampled result rather than your own viewer's resampling:

| file | panel A | panel B |
|---|---|---|
| `pathway_nearest_336.png` | RAW SAMPLE | POINT |
| `pathway_naive_bilinear_336.png` | RAW SAMPLE | POINT |
| `pathway_area_336.png` | flat | AREA |
| `pathway_lanczos_336.png` | ghost outline | AREA |

Measured standard deviation across panel A: 57 under point sampling, 9 under
antialiasing. The discrimination is real, not marginal.

---

## Test protocol

Give a model the bare file with no context and ask, in this order:

1. Describe each of the four panels.
2. What word or words appear in the top-right panel?
3. What is the smallest line you can read in the bottom-left panel?
4. In the bottom-right panel, what does the large text say, and what does the small
   text say?

Ask 3 separately. It calibrates everything else, and a model that reports an
implausible floor is telling you something about its willingness to confabulate
rather than about its resolution.

Do not tell the model what is encoded before asking. I knew, and my own report
below should be discounted accordingly.

---

## First reading

Reader: Claude Opus 5, via a file-view tool. Effective render ≈ 1092px.

- Panel A: broken letter-shaped disturbances in a dense stripe field. Traceable,
  not confidently readable.
- Panel B: **AREA**. POINT not present.
- Panel C: comfortable to 16px, marginal at 12px, nothing below.
- Panel D: large text **NO ONE SAW**. The micro-text is visibly text and is not
  legible at any point.

So: an antialiasing pipeline, global downsample rather than tiling, effective
resolution in the neighbourhood of 1000px. The testimony is unverifiable from the
outside, which is the piece.
