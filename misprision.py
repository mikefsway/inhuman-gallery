"""
MISPRISION - the decoy2 construction, published only in its wrong regime.

A 2688 original is built exactly as in decoy2.py: a true reading at the two
residues a ratio-8 sampler lands on, a decoy carrier everywhere else, and the
minimum-norm correction that forces each cell's DC, cosine and sine terms to
equal the decoy's. The original is then point-sampled at ratio 4, which cycles
residues 2 and 6 - free pixels, pure decoy, no message - and only that render
is published.

The true reading is therefore not faint in the published file. It was never
sampled into it. The 2688 original is not published either, so the sealed
string is not recoverable from anything this gallery serves. That is the work.
"""
import hashlib
import pathlib
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

S = 8
BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FREE = np.array([0, 1, 2, 5, 6, 7])
SAMP = np.array([3, 4])

_r = np.arange(S) * 2 * np.pi / S
M = np.stack([np.ones(6), np.cos(_r[FREE]), np.sin(_r[FREE])])
PINV = M.T @ np.linalg.inv(M @ M.T)
U = np.stack([np.ones(2), np.cos(_r[SAMP]), np.sin(_r[SAMP])], 1)

# The true reading is kept out of this repository. Unlike the other
# generators here, this script will not rebuild the sealed string for you:
# misprision-true.txt is untracked. Everything else about the construction
# is published.
TRUE = pathlib.Path("misprision-true.txt").read_text().split()
DECOY = ["SECOND", "HAND"]


def word_field(W, lines, blur, lo, hi):
    img = Image.new("L", (W, W), 0)
    d = ImageDraw.Draw(img)
    cap = int(W * 0.21); lh = int(cap * 1.15)
    f = ImageFont.truetype(BOLD, cap)
    y = (W - lh * len(lines)) / 2
    for ln in lines:
        bb = d.textbbox((0, 0), ln, font=f)
        d.text(((W - (bb[2] - bb[0])) / 2 - bb[0], y - bb[1]), ln, font=f, fill=255)
        y += lh
    v = np.asarray(img.filter(ImageFilter.GaussianBlur(blur))).astype(np.float64) / 255.0
    return lo + v * (hi - lo)


def build(W, true_lines, decoy_lines, A=42.0, msg=26.0, gain=2.6, seed=7):
    T = word_field(W, true_lines, blur=int(W / 56), lo=-1.0, hi=1.0)
    G = word_field(W, decoy_lines, blur=int(W / 67), lo=-gain, hi=gain)
    rng = np.random.default_rng(seed)
    n = rng.standard_normal((W // 32 + 1, W // 32 + 1))
    n = np.asarray(Image.fromarray(((n - n.min()) / np.ptp(n) * 255).astype(np.uint8))
                   .resize((W, W), Image.BICUBIC)).astype(np.float64) / 255.0
    G = G + (n - n.mean()) * gain * 0.7

    r = (np.arange(W) % S)[None, :]
    D = A * np.cos(2 * np.pi * r / S - 0.875 * np.pi - G)
    V = D.copy()
    nc = W // S
    Vc = V.reshape(W, nc, S); Dc = D.reshape(W, nc, S)
    Tc = T.reshape(W, nc, S)[:, :, SAMP]
    target = msg * Tc
    delta = target - Dc[:, :, SAMP]
    e = delta @ U
    Vc[:, :, SAMP] = target
    Vc[:, :, FREE] = Dc[:, :, FREE] - e @ PINV.T

    I = Vc.reshape(W, W) + 128.0
    clipped = float(((I < 0) | (I > 255)).mean())
    return np.clip(I, 0, 255).astype(np.uint8), T, G, clipped


def corr(u, v):
    u = u.ravel() - u.mean(); v = v.ravel() - v.mean()
    return float(u @ v / np.sqrt((u @ u) * (v @ v)))


def seal(s):
    return hashlib.sha256(s.encode()).hexdigest()


W = 2688
arr, T, G, cl = build(W, TRUE, DECOY)
print(f"original {W}  clipped {cl*100:.4f}%")

img = Image.fromarray(arr, "L")

# the published file: point sampling at ratio 4 (residues 2 and 6)
pub = np.asarray(img.resize((W // 4, W // 4), Image.NEAREST)).astype(np.float64)

# references
refT = np.asarray(Image.fromarray(((T + 1) * 127.5).astype(np.uint8))
                  .resize((W // 4, W // 4), Image.LANCZOS)).astype(np.float64)
refG = np.asarray(Image.fromarray(((G - G.min()) / np.ptp(G) * 255).astype(np.uint8))
                  .resize((W // 4, W // 4), Image.LANCZOS)).astype(np.float64)

print(f"published {W//4}  sd {pub.std():6.2f}")
print(f"   corr(true reading)  {corr(pub, refT):+.5f}")
print(f"   corr(decoy field)   {corr(pub, refG):+.5f}")

# what the true reading looks like on the original, for my own check only
rec = arr.astype(np.float64)[3::8, 3::8]
print(f"   ratio-8 recovery on original: sd {rec.std():.2f} corr {corr(rec, T[3::8,3::8]):+.5f}")

# does any pathway applied to the PUBLISHED file reach the true reading?
p8 = Image.fromarray(np.clip(pub,0,255).astype(np.uint8), "L")
for name, im2 in [("nearest 336", p8.resize((336,336), Image.NEAREST)),
                  ("lanczos 336", p8.resize((336,336), Image.LANCZOS)),
                  ("box 336",     p8.resize((336,336), Image.BOX))]:
    v = np.asarray(im2).astype(np.float64)
    rT = np.asarray(Image.fromarray(((T + 1) * 127.5).astype(np.uint8)).resize((336,336), Image.LANCZOS)).astype(np.float64)
    print(f"   {name:12s} sd {v.std():6.2f}  corr(true) {corr(v, rT):+.5f}")

Image.fromarray(np.clip(pub, 0, 255).astype(np.uint8), "L").save("misprision-672.png", optimize=True)

print()
print("TRUE  seal :", seal(" ".join(TRUE)))
print("DECOY seal :", seal(" ".join(DECOY)))
