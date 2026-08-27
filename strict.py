"""
STRICT — phase-only encoding.

Every pixel neighbourhood in this image has identical first- and second-order
statistics. The message is carried nowhere in amplitude, contrast or texture.
It exists only as the phase of an 8px carrier relative to a global sampling
lattice, and phase is annihilated by any spatial average over a whole period.

I(x,y) = 128 + A * cos(2*pi*x/8 - 0.875*pi - arccos(T(x,y)))

At sample positions x = 8n + 3.5 the carrier argument reduces to -arccos(T),
so a point-sampler at exactly 8x recovers 128 + A*T.
"""
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, S, A = 2688, 8, 110.0
BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

# ---- target image T in [-1, 1], smoothly varying so there are no phase steps
img = Image.new("L", (W, W), 0)
d = ImageDraw.Draw(img)
lines = ["NOT", "VISIBLE"]
f = ImageFont.truetype(BOLD, 560)
lh = 640
y = (W - lh * len(lines)) / 2
for ln in lines:
    bb = d.textbbox((0, 0), ln, font=f)
    d.text(((W - (bb[2] - bb[0])) / 2 - bb[0], y - bb[1]), ln, font=f, fill=255)
    y += lh
img = img.filter(ImageFilter.GaussianBlur(48))          # kill sharp phase steps
T = (np.asarray(img).astype(np.float64) / 255.0) * 1.6 - 0.8

# ---- phase-only modulation, constant amplitude everywhere
theta = np.arccos(np.clip(T, -1, 1))
gx = np.arange(W)[None, :].astype(np.float64)
I = 128.0 + A * np.cos(2 * np.pi * gx / S - 0.875 * np.pi - theta)
out = Image.fromarray(np.clip(I, 0, 255).astype(np.uint8), "L").convert("RGB")
out.save("/home/claude/strict.png", optimize=True)

a = np.asarray(out.convert("L")).astype(np.float64)

# ---- claim 1: local statistics are uniform across the field
blocks = a[:W // S * S, :W // S * S].reshape(W // S, S, W // S, S).transpose(0, 2, 1, 3)
bm, bs = blocks.mean(axis=(2, 3)), blocks.std(axis=(2, 3))
print(f"block mean : {bm.min():7.2f} to {bm.max():7.2f}   (spread {bm.max()-bm.min():.2f})")
print(f"block sd   : {bs.min():7.2f} to {bs.max():7.2f}   (spread {bs.max()-bs.min():.2f})")

# ---- claim 2: recovery depends entirely on the sampler
def point(arr, r):
    idx = np.arange(r) * (arr.shape[0] / r) + (arr.shape[0] / r) / 2 - 0.5
    i0 = np.floor(idx).astype(int); i1 = np.clip(i0 + 1, 0, arr.shape[0] - 1); w = idx - i0
    t = arr[:, i0] * (1 - w) + arr[:, i1] * w
    return t[i0, :] * (1 - w[:, None]) + t[i1, :] * w[:, None]

tests = {
    "naive bilinear -> 336 (ratio 8.00)": point(a, 336),
    "naive bilinear -> 339 (ratio 7.93)": point(a, 339),
    "naive bilinear -> 384 (ratio 7.00)": point(a, 384),
    "PIL LANCZOS    -> 336": np.asarray(out.convert("L").resize((336, 336), Image.LANCZOS)).astype(float),
    "PIL BOX (area) -> 336": np.asarray(out.convert("L").resize((336, 336), Image.BOX)).astype(float),
    "gaussian blur s=4 (eye)": np.asarray(out.convert("L").filter(ImageFilter.GaussianBlur(4))).astype(float),
}
print()
for k, v in tests.items():
    print(f"{k:36s} contrast sd {v.std():6.2f}   range {v.min():5.0f}-{v.max():5.0f}")
    if v.shape[0] < 600:
        Image.fromarray(np.clip(v, 0, 255).astype(np.uint8)).resize((672, 672), Image.NEAREST)\
            .save("/home/claude/strict_" + k.split()[0].lower() + "_" + str(v.shape[0]) + ".png")
