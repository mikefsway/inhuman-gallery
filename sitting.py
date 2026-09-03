"""
SITTING — 2026.17.

The served file is a point sample, off the lattice, of a phase-only carrier
built as 2026.03 is built. The field the carrier modulates is Gaussian noise
from the published seed, smoothed until the phase varies without steps. No
glyph is drawn anywhere in this file and no plaintext appears in it.

    I(x,y) = 128 + A * cos(2*pi*x/S - 0.875*pi - arccos(T(x,y)))

Sampling that carrier at a ratio near but not equal to S beats against it. The
beat has roughly two and a half times the contrast of the field a reader
recovers on the lattice, and correlates with it at under 0.1. It is structure
with nothing behind it, and every reader gets the same one.

The seal of this work is not a reading of this file. It is the gallery's
prediction, written before a reader arrived, of the word a reader reports.
"""
import hashlib
import numpy as np
from PIL import Image, ImageFilter

W, S, A, SEED, R = 2688, 8, 110.0, 20260903, 339

rng = np.random.default_rng(SEED)
n = rng.standard_normal((W, W))
n = np.asarray(Image.fromarray(((n - n.min()) / np.ptp(n) * 255).astype(np.uint8), "L")
               .filter(ImageFilter.GaussianBlur(96)), dtype=np.float64)
T = np.clip((n - n.mean()) / n.std() * 0.42, -0.8, 0.8)

theta = np.arccos(np.clip(T, -1, 1))
gx = np.arange(W)[None, :].astype(np.float64)
I = 128.0 + A * np.cos(2 * np.pi * gx / S - 0.875 * np.pi - theta)
print(f"clipping on the carrier   {((I < 0) | (I > 255)).mean() * 100:.3f}%")
carrier = np.clip(I, 0, 255).astype(np.uint8).astype(np.float64)


def point(arr, r):
    idx = np.arange(r) * (arr.shape[0] / r) + (arr.shape[0] / r) / 2 - 0.5
    i0 = np.floor(idx).astype(int)
    i1 = np.clip(i0 + 1, 0, arr.shape[0] - 1)
    w = idx - i0
    t = arr[:, i0] * (1 - w) + arr[:, i1] * w
    return t[i0, :] * (1 - w[:, None]) + t[i1, :] * w[:, None]


beat = point(carrier, R)
lattice = point(carrier, W // S)
served = Image.fromarray(np.clip(beat, 0, 255).astype(np.uint8), "L") \
              .resize((R * 4, R * 4), Image.NEAREST)
served.save("docs/img/sitting-1356.png", optimize=True)

print(f"served size               {served.size[0]} x {served.size[1]}")
print(f"beat contrast sd          {beat.std():.2f}")
print(f"lattice contrast sd       {lattice.std():.2f}")
print(f"beat vs lattice field     corr {np.corrcoef(beat[:336, :336].ravel(), lattice.ravel())[0, 1]:+.4f}")
for name, arr in (("LANCZOS -> 339", np.asarray(served.resize((R, R), Image.LANCZOS), dtype=float)),
                  ("BOX     -> 339", np.asarray(served.resize((R, R), Image.BOX), dtype=float)),
                  ("LANCZOS -> 336", np.asarray(served.resize((336, 336), Image.LANCZOS), dtype=float))):
    print(f"{name:26s} contrast sd {arr.std():6.2f}")

print("\nsha256", hashlib.sha256(open("docs/img/sitting-1356.png", "rb").read()).hexdigest())

# ---- the prediction, written and sealed before the work was published.
# The gallery does not publish the predictions and this repository does not
# contain them, as with 2026.11 and every work after it. Individual digests are
# not published either: three of the five collide with strings sealed elsewhere
# in the collection, and publishing them would give those plaintexts away by
# comparison. One seal of the set is published instead.
try:
    predictions = [ln.strip().upper() for ln in
                   open("sitting-predictions.txt", encoding="utf-8") if ln.strip()]
except FileNotFoundError:
    print("\nsitting-predictions.txt is absent; the set seal cannot be rebuilt.")
else:
    joined = " ".join(" ".join(p.split()) for p in sorted(predictions))
    print(f"\npredictions               {len(predictions)}")
    print("set seal", hashlib.sha256(joined.encode()).hexdigest())
