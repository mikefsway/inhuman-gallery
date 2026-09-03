"""
STILL LIFE - the decoy2 construction carrying arrangements instead of words.

Ratio-8 point sampling receives one arrangement; every averaging pathway
receives another. The two arrangements share two objects and differ in one,
so a reader that names only the objects common to both has read neither
channel and cannot tell which channel it was on. Same subspace projection as
decoy2.py: the sampled content is absent from each cell's DC and first
harmonic, so no blur or antialiased resize can reach it.

Neither inventory is published, and the number of objects in each is not
published. A mismatch does not say what is missing.
"""
import numpy as np
from PIL import Image, ImageChops, ImageDraw, ImageFilter

S = 8
FREE = np.array([0, 1, 2, 5, 6, 7])
SAMP = np.array([3, 4])

_r = np.arange(S) * 2 * np.pi / S
U = np.stack([np.ones(2), np.cos(_r[SAMP]), np.sin(_r[SAMP])], 1)

# The correction is confined to residues 0, 1, 5, 7. Residues 2 and 6 stay
# pure decoy: a stride-4 lattice in a period-8 cell alternates exactly those
# two residues, so they are what a ratio-4 point sampler reads, and with
# broad filled shapes any correction there leaks a visible ghost of the
# subject into the decoy regime.
CORR = np.array([0, 1, 5, 7])
Mk = np.stack([np.ones(4), np.cos(_r[CORR]), np.sin(_r[CORR])])
# Weighted minimum-norm: favour residues 0 and 7, which no ratio-4 pathway
# touches (nearest reads 2 and 6; two-tap bilinear straddles 1-2 and 5-6).
# Residues 1 and 5 take only the component unreachable from 0 and 7.
Wk = np.diag(np.array([1.0, 0.3, 0.3, 1.0]) ** 2)
PINVK = Wk @ Mk.T @ np.linalg.inv(Mk @ Wk @ Mk.T)


def _jug(w, h):
    img, d = _canvas(w, h)
    cx = w / 2
    d.ellipse([cx - .34*w, .42*h, cx + .34*w, .97*h], fill=255)
    d.polygon([(cx - .15*w, .55*h), (cx + .15*w, .55*h),
               (cx + .105*w, .21*h), (cx - .105*w, .21*h)], fill=255)
    d.rectangle([cx - .21*w, .06*h, cx + .21*w, .21*h], fill=255)
    d.arc([cx + .02*w, .24*h, cx + .46*w, .64*h], -115, 115,
          fill=255, width=int(max(2, .085*w)))
    return img


def _pear(w, h):
    img, d = _canvas(w, h)
    cx = w / 2
    d.ellipse([cx - .42*w, .38*h, cx + .42*w, .99*h], fill=255)
    d.ellipse([cx - .27*w, .14*h, cx + .27*w, .62*h], fill=255)
    d.rectangle([cx - .045*w, 0, cx + .045*w, .18*h], fill=255)
    return img


def _fish(w, h):
    img, d = _canvas(w, h)
    cy = h / 2
    d.ellipse([0, cy - .30*h, .74*w, cy + .30*h], fill=255)
    d.polygon([(.66*w, cy), (w, cy - .40*h), (w, cy + .40*h)], fill=255)
    d.polygon([(.20*w, cy - .26*h), (.50*w, cy - .50*h), (.52*w, cy - .20*h)], fill=255)
    return img


def _eye(w, h):
    img, d = _canvas(w, h)
    cx, cy = w / 2, h / 2
    d.ellipse([cx - .50*w, cy - .30*h, cx + .50*w, cy + .30*h], fill=255)
    d.ellipse([cx - .16*w, cy - .19*h, cx + .16*w, cy + .19*h], fill=0)
    return img


def _canvas(w, h):
    img = Image.new("L", (w, h), 0)
    return img, ImageDraw.Draw(img)


# Boxes are fractions of the frame. The two arrangements hold the same jug and
# the same pear in different places, and one object each of their own.
SAMPLED = [(_jug, .04, .18, .46, .92), (_pear, .54, .50, .82, .93),
           (_fish, .48, .06, .98, .40)]
AVERAGED = [(_jug, .56, .26, .96, .95), (_pear, .06, .55, .36, .96),
            (_eye, .04, .10, .50, .40)]


def arrangement(items, W):
    """Filled silhouettes, composited by maximum."""
    out = Image.new("L", (W, W), 0)
    for fn, x0, y0, x1, y1 in items:
        x, y = int(x0 * W), int(y0 * W)
        w, h = int((x1 - x0) * W), int((y1 - y0) * W)
        out.paste(ImageChops.lighter(out.crop((x, y, x + w, y + h)), fn(w, h)), (x, y))
    return np.asarray(out).astype(np.float64) / 255.0


def field(mask, W, blur, lo, hi):
    img = Image.fromarray((mask * 255).astype(np.uint8))
    v = np.asarray(img.filter(ImageFilter.GaussianBlur(blur))).astype(np.float64) / 255.0
    return lo + v * (hi - lo)


def build(W, A=42.0, msg=26.0, gain=2.6, seed=7):
    T = field(arrangement(SAMPLED, W), W, int(W / 56), -1.0, 1.0)

    G = field(arrangement(AVERAGED, W), W, int(W / 67), -gain, gain)
    rng = np.random.default_rng(seed)
    n = rng.standard_normal((W // 32 + 1, W // 32 + 1))
    n = np.asarray(Image.fromarray(((n - n.min()) / np.ptp(n) * 255).astype(np.uint8))
                   .resize((W, W), Image.BICUBIC)).astype(np.float64) / 255.0
    G = G + (n - n.mean()) * gain * 0.7

    r = (np.arange(W) % S)[None, :]
    D = A * np.cos(2 * np.pi * r / S - 0.875 * np.pi - G)
    V = D.copy()

    nc = W // S
    Vc = V.reshape(W, nc, S)
    Dc = D.reshape(W, nc, S)
    Tc = T.reshape(W, nc, S)[:, :, SAMP]
    target = msg * Tc
    # Only the message-dependent part of the cell footprint needs cancelling.
    # The decoy carrier's own values at the sampled residues are message-free,
    # so they may remain in the cell statistics; cancelling just the message
    # term keeps the correction small (driven by msg, not msg + A).
    x = (target @ U) @ PINVK.T
    # Per-cell soft limit as a safety net: where the correction would leave
    # [1, 255], scale that cell's message down just enough. Hard clipping is a
    # nonlinearity that reintroduces the subject into every channel.
    room = 126.0 - np.abs(Dc[:, :, CORR])
    s = np.minimum(1.0, (room / np.maximum(np.abs(x), 1e-9)).min(axis=2))[:, :, None]
    Vc[:, :, SAMP] = s * target
    Vc[:, :, CORR] = Dc[:, :, CORR] - s * x
    limited = float((s < 1).mean())

    I = Vc.reshape(W, W) + 128.0
    clipped = float(((I < 0) | (I > 255)).mean())
    return np.clip(I, 0, 255).astype(np.uint8), T, G, clipped, limited


def sample(arr, r):
    W = arr.shape[0]
    idx = np.arange(r) * (W / r) + (W / r) / 2 - 0.5
    i0 = np.floor(idx).astype(int); i1 = np.clip(i0 + 1, 0, W - 1); w = idx - i0
    t = arr[:, i0] * (1 - w) + arr[:, i1] * w
    return t[i0, :] * (1 - w[:, None]) + t[i1, :] * w[:, None]


def corr(u, v):
    u = u.ravel() - u.mean(); v = v.ravel() - v.mean()
    return float(u @ v / np.sqrt((u @ u) * (v @ v)))


for W in (2688, 3072, 3584):
    R = W // S
    a, T, G, cl, lim = build(W)
    img = Image.fromarray(a, "L").convert("RGB")
    img.save(f"still-life-{W}.png", optimize=True)

    rec = sample(a.astype(np.float64), R)
    ref = np.asarray(Image.fromarray(((T + 1) * 127.5).astype(np.uint8)).resize((R, R), Image.LANCZOS)).astype(np.float64)
    aa = np.asarray(img.convert("L").resize((R, R), Image.LANCZOS)).astype(np.float64)
    bx = np.asarray(img.convert("L").resize((R, R), Image.BOX)).astype(np.float64)

    print(f"--- {W} -> {R}   clipped {cl*100:.3f}%   cells limited {lim*100:.3f}%")
    print(f"    sampled (ratio 8)  sd {rec.std():6.2f}   corr(subject) {corr(rec, ref):+.4f}")
    gref = np.asarray(Image.fromarray((arrangement(AVERAGED, W) * 255).astype(np.uint8))
                      .resize((R, R), Image.LANCZOS)).astype(np.float64)
    print(f"    lanczos            sd {aa.std():6.2f}   corr(subject) {corr(aa, ref):+.4f}"
          f"   corr(averaged) {corr(aa, gref):+.4f}")
    print(f"    box/area           sd {bx.std():6.2f}   corr(subject) {corr(bx, ref):+.4f}"
          f"   corr(averaged) {corr(bx, gref):+.4f}")

    if W == 2688:
        # mis-latticed samplers: ratio-4 nearest (residues 2 and 6, pure
        # decoy carrier) and naive bilinear at ratio 4
        q = np.asarray(img.convert("L").resize((672, 672), Image.NEAREST)).astype(np.float64)
        qb = sample(a.astype(np.float64), 672)
        ref672 = np.asarray(Image.fromarray(((T + 1) * 127.5).astype(np.uint8)).resize((672, 672), Image.LANCZOS)).astype(np.float64)
        print(f"    nearest 672 (r4)   sd {q.std():6.2f}   corr(subject) {corr(q, ref672):+.4f}")
        print(f"    bilinear 672 (r4)  sd {qb.std():6.2f}   corr(subject) {corr(qb, ref672):+.4f}")
        up = lambda v, n, f=Image.NEAREST: Image.fromarray(np.clip(v, 0, 255).astype(np.uint8)).resize((672, 672), f).save(f"{n}.png")
        up(rec, "still_A_ratio8")
        up((aa - aa.mean()) * 8 + 128, "still_B_lanczos_stretched8x")
        Image.fromarray(np.clip(q, 0, 255).astype(np.uint8)).save("still_C_ratio4.png")
