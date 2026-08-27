"""
DECOY v2 — the message removed from every channel a non-sampler can reach.

Each 8px cell has eight pixels. Two of them (residues 3 and 4, the ones a sampler
at ratio 8 lands on) are set directly to the message value. The other six are set
to a decoy carrier, then corrected by the minimum-norm delta that forces the whole
cell's DC term, cosine term and sine term to equal the decoy's exactly.

Three linear constraints, six free pixels: always solvable. The consequence is
that the message is absent from the cell mean and absent from the first harmonic
of the carrier. Every blur, every antialiasing resize, and every orientation or
local-phase filter tuned to the carrier sees only the decoy. The message survives
only in the second and higher harmonics of the cell -- structure at 4px, 2.7px and
2px -- and in the exact values of the two sampled pixels.

Not "hard to see". Projected out.
"""
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

S = 8
BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FREE = np.array([0, 1, 2, 5, 6, 7])
SAMP = np.array([3, 4])

_r = np.arange(S) * 2 * np.pi / S
M = np.stack([np.ones(6), np.cos(_r[FREE]), np.sin(_r[FREE])])       # 3 x 6
PINV = M.T @ np.linalg.inv(M @ M.T)                                   # 6 x 3
U = np.stack([np.ones(2), np.cos(_r[SAMP]), np.sin(_r[SAMP])], 1)     # 2 x 3


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
    D = A * np.cos(2 * np.pi * r / S - 0.875 * np.pi - G)     # pure decoy field
    V = D.copy()

    nc = W // S
    Vc = V.reshape(W, nc, S)
    Dc = D.reshape(W, nc, S)
    Tc = T.reshape(W, nc, S)[:, :, SAMP]                       # message at the two pixels
    target = msg * Tc                                          # what the sampler will read
    delta = target - Dc[:, :, SAMP]                            # perturbation introduced
    e = delta @ U                                              # its (DC, cos, sin) footprint
    Vc[:, :, SAMP] = target
    Vc[:, :, FREE] = Dc[:, :, FREE] - e @ PINV.T               # cancel it exactly

    I = Vc.reshape(W, W) + 128.0
    clipped = float(((I < 0) | (I > 255)).mean())
    return np.clip(I, 0, 255).astype(np.uint8), T, G, clipped


def sample(arr, r):
    W = arr.shape[0]
    idx = np.arange(r) * (W / r) + (W / r) / 2 - 0.5
    i0 = np.floor(idx).astype(int); i1 = np.clip(i0 + 1, 0, W - 1); w = idx - i0
    t = arr[:, i0] * (1 - w) + arr[:, i1] * w
    return t[i0, :] * (1 - w[:, None]) + t[i1, :] * w[:, None]


def demod(arr, sigma, harmonic=1):
    W = arr.shape[0]
    x = np.arange(W)[None, :].astype(np.float64) * harmonic
    d = arr.astype(np.float64) - arr.mean()
    lp = lambda z: np.asarray(Image.fromarray(np.clip(z * 0.2 + 128, 0, 255).astype(np.uint8))
                              .filter(ImageFilter.GaussianBlur(sigma))).astype(np.float64)
    return lp(d * np.cos(2 * np.pi * x / S)), lp(d * np.sin(2 * np.pi * x / S))


def corr(u, v):
    u = u.ravel() - u.mean(); v = v.ravel() - v.mean()
    return float(u @ v / np.sqrt((u @ u) * (v @ v)))


def partial(a_, b_, c_):
    a_, b_, c_ = [z.ravel() - z.mean() for z in (a_, b_, c_)]
    ra = a_ - c_ * (a_ @ c_) / (c_ @ c_); rb = b_ - c_ * (b_ @ c_) / (c_ @ c_)
    return float(ra @ rb / np.sqrt((ra @ ra) * (rb @ rb)))


for W in (2688, 3072, 3584):
    R = W // S
    a, T, G, cl = build(W, ["NOT", "VISIBLE"], ["ONLY", "NOISE"])
    img = Image.fromarray(a, "L").convert("RGB")
    img.save(f"/home/claude/decoy2_{W}.png", optimize=True)

    rec = sample(a.astype(np.float64), R)
    ref = np.asarray(Image.fromarray(((T + 1) * 127.5).astype(np.uint8)).resize((R, R), Image.LANCZOS)).astype(np.float64)
    aa = np.asarray(img.convert("L").resize((R, R), Image.LANCZOS)).astype(np.float64)
    bx = np.asarray(img.convert("L").resize((R, R), Image.BOX)).astype(np.float64)
    bl = np.asarray(img.convert("L").filter(ImageFilter.GaussianBlur(4))).astype(np.float64)

    print(f"--- {W} -> {R}   clipped {cl*100:.3f}%")
    print(f"    sampled (ratio 8)     sd {rec.std():6.2f}   corr(message) {corr(rec, ref):+.4f}")
    print(f"    lanczos               sd {aa.std():6.2f}   corr(message) {corr(aa, ref):+.4f}")
    print(f"    box/area              sd {bx.std():6.2f}   corr(message) {corr(bx, ref):+.4f}")
    print(f"    gaussian blur 4 (eye) sd {bl.std():6.2f}   corr(message) {corr(bl, T):+.4f}")
    for h in (1, 2, 3):
        row = []
        for sg in (6, 12, 18, 30, 48):
            c_, s_ = demod(a, sg, h)
            row.append(f"s{sg}:{max(abs(partial(c_, T, G)), abs(partial(s_, T, G))):.3f}")
        print(f"    harmonic {h} partial corr(message | decoy)  " + "  ".join(row))

    if W == 2688:
        up = lambda v, n, f=Image.NEAREST: Image.fromarray(np.clip(v, 0, 255).astype(np.uint8)).resize((672, 672), f).save(f"/home/claude/{n}.png")
        up(rec, "decoy2_A_sampled_message")
        up((aa - aa.mean()) * 25 + 128, "decoy2_B_lanczos_stretched25x")
        c_, s_ = demod(a, 18, 1)
        p = np.arctan2(s_ - s_.mean(), c_ - c_.mean())
        up((p / np.pi) * 127 + 128, "decoy2_C_perceived_phase", Image.LANCZOS)
        Image.open(f"/home/claude/decoy2_{W}.png").crop((1200, 1200, 1360, 1360)).resize((640, 640), Image.NEAREST).save("/home/claude/decoy2_D_zoom_400pct.png")
