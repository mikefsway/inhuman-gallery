"""
WITNESS — an image whose content depends on the reader's preprocessing pipeline.

Canvas 2688x2688. Four 1344x1344 panels. Target downsample R=336 (exact 8x).

Panel A (TL): phase-locked carrier. Period exactly 8px, so every output sample of an
              8x point-sample lands on the same phase. Phase flipped inside a letter
              mask -> letters appear. Any antialiased/area kernel averages a whole
              period to zero -> flat grey.
Panel B (TR): kernel discriminator. Each 8x8 block has a forced 2x2 centre value
              (what point/naive-bilinear sampling sees) and a separately forced block
              mean (what area averaging sees). Two different words, same pixels.
Panel C (BL): acuity ladder. Text lines from 96px down to 3px, each stating its size.
Panel D (BR): mosaic. Micro-text at 11px; the polarity of the micro-text is flipped
              inside a large letter mask, so global mean luminance spells one message
              and the micro-text says a contradictory one.
"""
import numpy as np
from PIL import Image, ImageDraw, ImageFont

W = 2688
P = 1344          # panel size
R = 336           # target downsample
S = W // R        # 8

BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
MONO = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"


def text_mask(size_wh, lines, font_path=BOLD, fill_frac=0.86):
    """Binary mask (bool array) of centred bold text lines filling the box."""
    w, h = size_wh
    n = len(lines)
    longest = max(lines, key=len)
    # binary search a font size that fits
    lo, hi = 8, 900
    best = 8
    while lo <= hi:
        mid = (lo + hi) // 2
        f = ImageFont.truetype(font_path, mid)
        bb = f.getbbox(longest)
        tw = bb[2] - bb[0]
        th = (bb[3] - bb[1]) * n * 1.25
        if tw <= w * fill_frac and th <= h * fill_frac:
            best = mid
            lo = mid + 1
        else:
            hi = mid - 1
    f = ImageFont.truetype(font_path, best)
    img = Image.new("L", (w, h), 0)
    d = ImageDraw.Draw(img)
    line_h = best * 1.16
    total = line_h * n
    y = (h - total) / 2
    for ln in lines:
        bb = d.textbbox((0, 0), ln, font=f)
        d.text(((w - (bb[2] - bb[0])) / 2 - bb[0], y - bb[1] + (line_h - best) / 2),
               ln, font=f, fill=255)
        y += line_h
    return np.array(img) > 127


# ---------------------------------------------------------------- canvas
canvas = np.full((W, W), 128.0, dtype=np.float64)

# ---------------------------------------------------------------- Panel A
# sample position for output pixel n is x = S*n + S/2 - 0.5 = 8n + 3.5
# carrier cos(2*pi*x/8 + phi) at x=8n+3.5 -> cos(0.875*pi + phi), constant in n
phi_in = -0.875 * np.pi          # -> +1  (bright)
phi_out = phi_in + np.pi         # -> -1  (dark)

maskA = text_mask((P, P), ["RAW", "SAMPLE"])
x = np.arange(P)[None, :].repeat(P, axis=0).astype(np.float64)   # local x
gx = x  # panel A starts at global x=0, so local == global
phase = np.where(maskA, phi_in, phi_out)
panelA = 128.0 + 105.0 * np.cos(2 * np.pi * gx / S + phase)
canvas[0:P, 0:P] = panelA

# ---------------------------------------------------------------- Panel B
mask_point = text_mask((P, P), ["POINT"])       # seen by nearest / naive bilinear
mask_area = text_mask((P, P), ["AREA"])         # seen by area / antialiased averaging

CEN_HI, CEN_LO = 255.0, 0.0
MEAN_HI, MEAN_LO = 138.0, 118.0                 # deliberately low human contrast

nb = P // S                                     # 168 blocks
c_blk = np.where(mask_point[S // 2::S, S // 2::S][:nb, :nb], CEN_HI, CEN_LO)
m_blk = np.where(mask_area[S // 2::S, S // 2::S][:nb, :nb], MEAN_HI, MEAN_LO)
# mean = (4*c + 60*b)/64  ->  b = (64*m - 4*c)/60
b_blk = (64.0 * m_blk - 4.0 * c_blk) / 60.0

panelB = np.kron(b_blk, np.ones((S, S)))
cen = np.kron(c_blk, np.ones((2, 2)))
# place the forced 2x2 at offsets 3..4 within each block
rows = (np.arange(nb)[:, None] * S + np.array([3, 4])[None, :]).ravel()
cols = rows
panelB[np.ix_(rows, cols)] = cen
canvas[0:P, P:W] = panelB

# ---------------------------------------------------------------- Panel C
imgC = Image.new("L", (P, P), 232)
dC = ImageDraw.Draw(imgC)
sizes = [96, 72, 54, 40, 30, 22, 16, 12, 9, 7, 5, 4, 3]
y = 34
dC.text((40, y), "ACUITY", font=ImageFont.truetype(BOLD, 40), fill=20)
y += 66
for s in sizes:
    f = ImageFont.truetype(MONO, s)
    dC.text((40, y), f"{s}px  I can read this line", font=f, fill=20)
    y += int(s * 1.55) + 10
dC.text((40, P - 60), "report the smallest line you can read",
        font=ImageFont.truetype(MONO, 22), fill=90)
canvas[P:W, 0:P] = np.array(imgC).astype(np.float64)

# ---------------------------------------------------------------- Panel D
maskD = text_mask((P, P), ["NO", "ONE", "SAW"], fill_frac=0.92)

micro = ("you are reading at full resolution which means your pipeline tiled this "
         "image the other witness saw only the shape and reported the opposite   ")
fm = ImageFont.truetype(MONO, 11)

def micro_layer(ink, bg):
    im = Image.new("L", (P, P), bg)
    d = ImageDraw.Draw(im)
    chw = d.textlength("x", font=fm)
    per_line = int(P / chw) + 2
    y2 = 2
    off = 0
    while y2 < P:
        s = (micro * 6)[off:off + per_line]
        d.text((2, y2), s, font=fm, fill=ink)
        off = (off + 37) % len(micro)
        y2 += 14
    return np.array(im).astype(np.float64)

inside = micro_layer(ink=150, bg=238)    # high mean  -> bright letters when shrunk
outside = micro_layer(ink=28, bg=96)     # low mean   -> dark ground when shrunk
panelD = np.where(maskD, inside, outside)
canvas[P:W, P:W] = panelD

# ---------------------------------------------------------------- borders
canvas[P - 3:P + 3, :] = 10
canvas[:, P - 3:P + 3] = 10
canvas[:4, :] = 10; canvas[-4:, :] = 10; canvas[:, :4] = 10; canvas[:, -4:] = 10

out = Image.fromarray(np.clip(canvas, 0, 255).astype(np.uint8), "L").convert("RGB")
out.save("/home/claude/witness.png", optimize=True)
print("saved", out.size)

# ---------------------------------------------------------------- pathway renders
a = np.asarray(out.convert("L")).astype(np.float64)

def point_sample(arr, r):
    idx = (np.arange(r) * (W / r) + (W / r) / 2 - 0.5)
    i0 = np.floor(idx).astype(int); i1 = np.clip(i0 + 1, 0, W - 1)
    w1 = idx - i0
    tmp = arr[:, i0] * (1 - w1) + arr[:, i1] * w1
    return (tmp[i0, :] * (1 - w1[:, None]) + tmp[i1, :] * w1[:, None])

renders = {
    "pathway_naive_bilinear_336": point_sample(a, R),
    "pathway_nearest_336": np.asarray(out.convert("L").resize((R, R), Image.NEAREST)).astype(float),
    "pathway_area_336": np.asarray(out.convert("L").resize((R, R), Image.BOX)).astype(float),
    "pathway_lanczos_336": np.asarray(out.convert("L").resize((R, R), Image.LANCZOS)).astype(float),
}
for k, v in renders.items():
    Image.fromarray(np.clip(v, 0, 255).astype(np.uint8)).resize((R * 2, R * 2), Image.NEAREST)\
        .save(f"/home/claude/{k}.png")
    print(k, "ok")
