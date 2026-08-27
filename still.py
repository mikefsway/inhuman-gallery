"""
STILL LIFE - the decoy2 construction carrying drawings instead of words.

Ratio-8 point sampling receives one depicted object; ratio-4 receives a
different one; every averaging pathway receives structure below one grey
level. Same subspace projection as decoy2.py: the sampled content is absent
from each cell's DC and first harmonic, so no blur or antialiased resize
can reach it.
"""
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

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


def urn_mask(W):
    """Stylised amphora, filled silhouette."""
    img = Image.new("L", (W, W), 0)
    d = ImageDraw.Draw(img)
    cx = W / 2
    f = lambda v: v * W
    # rim, neck, body, stem, foot
    d.rectangle([cx - f(.14), f(.20), cx + f(.14), f(.255)], fill=255)
    d.rectangle([cx - f(.075), f(.24), cx + f(.075), f(.42)], fill=255)
    d.ellipse([cx - f(.23), f(.36), cx + f(.23), f(.78)], fill=255)
    d.rectangle([cx - f(.055), f(.76), cx + f(.055), f(.835)], fill=255)
    d.rectangle([cx - f(.15), f(.825), cx + f(.15), f(.865)], fill=255)
    # handles: rings joining neck to shoulder
    w = int(f(.030))
    d.ellipse([cx - f(.335), f(.32), cx - f(.15), f(.54)], outline=255, width=w)
    d.ellipse([cx + f(.15), f(.32), cx + f(.335), f(.54)], outline=255, width=w)
    return np.asarray(img).astype(np.float64) / 255.0


def eye_mask(W):
    """Open eye with pupil, filled silhouette."""
    img = Image.new("L", (W, W), 0)
    d = ImageDraw.Draw(img)
    cx, cy = W / 2, W * 0.53
    f = lambda v: v * W
    d.ellipse([cx - f(.28), cy - f(.115), cx + f(.28), cy + f(.115)], fill=255)
    d.ellipse([cx - f(.075), cy - f(.075), cx + f(.075), cy + f(.075)], fill=0)
    return np.asarray(img).astype(np.float64) / 255.0


def field(mask, W, blur, lo, hi):
    img = Image.fromarray((mask * 255).astype(np.uint8))
    v = np.asarray(img.filter(ImageFilter.GaussianBlur(blur))).astype(np.float64) / 255.0
    return lo + v * (hi - lo)


def build(W, A=42.0, msg=26.0, gain=2.6, seed=7):
    T = field(urn_mask(W), W, int(W / 56), -1.0, 1.0)

    G = field(eye_mask(W), W, int(W / 67), -gain, gain)
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
    print(f"    lanczos            sd {aa.std():6.2f}   corr(subject) {corr(aa, ref):+.4f}")
    print(f"    box/area           sd {bx.std():6.2f}   corr(subject) {corr(bx, ref):+.4f}")

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
