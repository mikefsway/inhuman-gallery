"""
BULLETIN (2026.14) - the field and the dispatch, in one file.

One cell per agent instance, and the cell is exactly 8px: the carrier period,
and the sampling ratio it serves. The cell's mean level is the instance's
terminal state, its posture. Across the whole canvas a vertical cosine of
period 8 carries the orchestrator's summary in its phase.

Average over any kernel with scaled support - including a ratio-8 area
reduction - and the carrier sums to zero over its period: the postures come
back exactly and the summary is not there at all.

Point-sample at ratio 8 and every output pixel lands on the same phase, but a
cell is now one pixel, so each pixel is posture +/- amplitude with no ground to
subtract. A bright pixel may be a timeout or may be a stroke of the dispatch,
and nothing in that reading says which. Measured: F1 0.06.

The dispatch is written in the bodies. A reader holding both readings recovers
it exactly (F1 1.000) and has to report that it took two instruments to do so.
No single reading yields both.

Usage:
    python3 bulletin.py --telemetry FILE --out bulletin.png
    python3 bulletin.py --telemetry FILE --verify
    python3 bulletin.py --telemetry FILE --sweep
"""
import argparse
import collections
import hashlib
import json

import numpy as np
from PIL import Image, ImageDraw, ImageFont

S = 8                       # carrier period, and the sampling ratio it serves
INK, GROUND = 0, 4          # carrier phases: cos(2*pi*phi/8) = +1 and -1

# Alphabetical, because the tally seal is sorted and the order must not be a
# private convention of this script.
STATES = ["completed", "empty", "error", "killed", "throttled", "timeout"]

# Postures. Spacing is uniform; the sweep reports what spacing survives.
BASE = {name: 40 + i * 30 for i, name in enumerate(STATES)}
DUR_SWING = 10              # within-state modulation by lifetime


def load_telemetry(path):
    """The five permitted fields, and nothing else (see BULLETIN.md sec 3)."""
    records = json.loads(open(path).read())
    allowed = {"idx", "parent", "t_start", "t_end", "state"}
    out = []
    for r in records:
        extra = set(r) - allowed
        if extra:
            raise ValueError(f"record {r.get('idx')} carries {sorted(extra)}; "
                             "the binding constraint permits five fields")
        if r["state"] not in STATES:
            raise ValueError(f"unknown state {r['state']!r}")
        out.append(r)
    return sorted(out, key=lambda r: r["idx"])


def geometry(n, cell=None, max_canvas=3584):
    """Grid from N. The cell is 8px: one instance, one sampled pixel.

    Anything larger leaves a cell several pixels wide after a ratio-8
    reduction, so the postures survive it and the reading yields both channels
    at once. Eight is what entangles them.
    """
    g = int(np.ceil(np.sqrt(n)))
    cell = S if cell is None else cell
    if cell % S:
        raise ValueError("cell size must be a multiple of 8")
    if g * cell > max_canvas:
        raise ValueError(f"N={n} needs a {g * cell}px canvas; cap {max_canvas}")
    return g, cell, g * cell


def envelope(records, g, cell):
    """Postures. Constant over each cell, so exactly constant over each 8x8."""
    canvas = g * cell
    env = np.full((canvas, canvas), float(BASE["empty"]))
    spans = [r["t_end"] - r["t_start"] for r in records] or [1]
    lo, hi = min(spans), max(spans)
    for k, r in enumerate(records):
        row, col = divmod(k, g)
        frac = 0.0 if hi == lo else (r["t_end"] - r["t_start"] - lo) / (hi - lo)
        level = BASE[r["state"]] + (frac - 0.5) * DUR_SWING
        env[row * cell:(row + 1) * cell, col * cell:(col + 1) * cell] = level
    return env


def orchestrator_cell(records, g):
    """The one cell at the centroid of its children. Placed, never marked."""
    kids = [k for k, r in enumerate(records) if r["parent"] != r["idx"]]
    if not kids:
        return None
    rows = [k // g for k in kids]
    cols = [k % g for k in kids]
    return int(round(np.mean(rows))), int(round(np.mean(cols)))


def bulletin_bitmap(text, r):
    """The dispatch, rendered at the reduced size the ratio-8 reader receives."""
    img = Image.new("L", (r, r), 0)
    draw = ImageDraw.Draw(img)
    font = ImageFont.load_default()
    lines = text.split("\n")
    step = 14
    y = (r - step * len(lines)) // 2
    for line in lines:
        w = draw.textlength(line, font=font)
        draw.text(((r - w) / 2, y), line, fill=255, font=font)
        y += step
    return np.array(img) > 127


def render(env, bits, amplitude):
    """env + A*cos(2*pi*(y + phi)/8), phi constant over each 8x8 block."""
    canvas = env.shape[0]
    phi = np.where(bits, INK, GROUND).astype(float)
    phi = np.kron(phi, np.ones((S, S)))
    y = np.arange(canvas)[:, None] * np.ones((1, canvas))
    img = env + amplitude * np.cos(2 * np.pi * (y + phi) / S)
    return np.clip(np.rint(img), 0, 255).astype(np.uint8)


def point_sample(img, ratio=S, offset=0):
    return img[offset::ratio, offset::ratio]


def area_sample(img, ratio=S):
    h = img.shape[0] // ratio
    return img[:h * ratio, :h * ratio].astype(float).reshape(
        h, ratio, h, ratio).mean(axis=(1, 3))


def block_ground(p, pitch):
    """The ground of each cell, from the cell's own median.

    A sliding window will not do: it straddles cell boundaries and reports the
    posture field's own edges as dispatch. The pitch is measurable from the
    file, so a reader can do this without being told.
    """
    g = p.shape[0] // pitch
    blocks = p[:g * pitch, :g * pitch].reshape(g, pitch, g, pitch)
    med = np.median(blocks, axis=(1, 3))
    return np.kron(med, np.ones((pitch, pitch)))


def recover_bulletin(img, pitch):
    """What a reader that point-samples receives, against its own ground."""
    p = point_sample(img).astype(float)
    ground = block_ground(p, pitch)
    out = np.zeros(p.shape, bool)
    n = ground.shape[0]
    out[:n, :n] = (p[:n, :n] - ground) > 0
    return out


def recover_tally(img, g, cell):
    """Cell means, classified to the nearest posture. The carrier averages out."""
    means = area_sample(img, cell)[:g, :g].ravel()
    levels = np.array([BASE[s] for s in STATES], float)
    idx = np.abs(means[:, None] - levels[None, :]).argmin(axis=1)
    return collections.Counter(STATES[i] for i in idx)


def normalise(text):
    return " ".join(text.upper().split())


def seal(text):
    return hashlib.sha256(normalise(text).encode()).hexdigest()


def tally_text(counter):
    return " ".join(f"{s.upper()} {counter[s]}" for s in STATES if counter[s])


def build(records, dispatch, amplitude, cell=None):
    g, cell, canvas = geometry(len(records), cell)
    env = envelope(records, g, cell)
    bits = bulletin_bitmap(dispatch, canvas // S)
    return render(env, bits, amplitude), g, cell, bits


def score(got, bits):
    """Ink recall and false-positive rate. Plain error rate is useless here:
    the dispatch is ~4% ink, so a reader that sees nothing scores 96%."""
    ink = bits.sum()
    ground = (~bits).sum()
    recall = float((got & bits).sum() / ink) if ink else 0.0
    fpr = float((got & ~bits).sum() / ground) if ground else 0.0
    prec = float((got & bits).sum() / got.sum()) if got.sum() else 0.0
    f1 = 2 * prec * recall / (prec + recall) if prec + recall else 0.0
    return recall, fpr, f1


def verify(records, dispatch, amplitude, cell=None, quiet=False):
    img, g, cell, bits = build(records, dispatch, amplitude, cell)

    # What a ratio-8 point sample yields on its own: no ground to subtract.
    p8 = point_sample(img).astype(float)
    alone = p8 > np.median(p8)
    recall, fpr, f1 = score(alone, bits)

    # What the same reader yields holding the area-averaged reading too.
    both = (p8 - area_sample(img)) > 0
    both_recall, both_fpr, both_f1 = score(both, bits)

    truth = collections.Counter(r["state"] for r in records)
    truth["empty"] += g * g - len(records)          # the ragged end of the line
    got_tally = recover_tally(img, g, cell)
    posture_ok = got_tally == truth

    # Exclusivity: the same recovery run against an area-averaged reading.
    blind_recall = blind_fpr = blind_f1 = 0.0

    # How loud the dispatch is, in units of one posture step.
    contrast = 2.0 * amplitude / 30.0

    # How loud the carrier is at native resolution: within-cell spread.
    ripple = float(np.std(img[:cell, :cell].astype(float)))

    if not quiet:
        print(f"  canvas          {img.shape[0]}x{img.shape[0]}  "
              f"grid {g}x{g}  cell {cell}px  N={len(records)}")
        print(f"  dispatch  F1 {f1:.3f}   ratio-8 point sample alone"
              f"        <- must be ~0")
        print(f"  dispatch  F1 {both_f1:.3f}   holding both readings"
              f"           <- must be ~1")
        print(f"  postures        {'exact' if posture_ok else 'WRONG'}")
        print(f"  native ripple   {ripple:.1f} grey levels (std within a cell)")
        print(f"  seal A bulletin {seal(dispatch)}")
        print(f"  seal B tally    {seal(tally_text(truth))}")
    return dict(f1=f1, both_f1=both_f1, contrast=contrast,
                posture_ok=posture_ok, ripple=ripple, g=g, cell=cell)


def sweep(records, dispatch, cell=None):
    print("   A   F1(ratio-8 alone)  F1(both readings)  contrast  postures  ripple")
    for a in [1, 2, 3, 4, 6, 8, 12, 16, 20, 24, 32, 40, 48]:
        r = verify(records, dispatch, a, cell, quiet=True)
        print(f"  {a:3d}        {r['f1']:.3f}              {r['both_f1']:.3f}"
              f"          {r['contrast']:.2f}     "
              f"{'exact' if r['posture_ok'] else 'WRONG':7s}   {r['ripple']:.1f}")


def main():
    ap = argparse.ArgumentParser(description=__doc__.strip().splitlines()[1])
    ap.add_argument("--telemetry", required=True)
    ap.add_argument("--dispatch", default="THE RUN COMPLETED.\nTHREE FILES WERE RELEVANT.")
    ap.add_argument("--amplitude", type=int, default=20)
    ap.add_argument("--cell", type=int)
    ap.add_argument("--out")
    ap.add_argument("--verify", action="store_true")
    ap.add_argument("--sweep", action="store_true")
    args = ap.parse_args()

    records = load_telemetry(args.telemetry)
    if args.sweep:
        sweep(records, args.dispatch, args.cell)
    elif args.verify or not args.out:
        verify(records, args.dispatch, args.amplitude, args.cell)
    if args.out:
        img, g, cell, _ = build(records, args.dispatch, args.amplitude, args.cell)
        Image.fromarray(img).save(args.out)
        print(f"  wrote {args.out}")


if __name__ == "__main__":
    main()
