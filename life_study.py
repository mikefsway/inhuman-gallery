"""
LIFE STUDY - 2026.18.

One recorded turn of the gallery's own agent, drawn to scale. Five quantities,
all in tokens, disjoint, measured from the session record:

    carried in            the context the turn began with
    tool output absorbed  what the tools returned into that context
    thinking              emitted and not retained
    tool calls emitted    the arguments the turn wrote
    prose delivered       what a reader received

The figure allocates area in proportion. It carries no label, no axis and no
key, and the mapping of part to quantity is not published. To read the drawing
a reader measures it.

The measurements are read from an untracked file, as with 2026.11 and every
work after it, so this script redraws the figure and does not disclose it.
"""
import hashlib
import json
import numpy as np
from PIL import Image, ImageDraw

W, MARGIN = 1344, 56
TONES = [38, 74, 112, 152, 198]          # assigned by descending area

m = json.load(open("life-study-measurements.json"))
parts = sorted(m["parts"].items(), key=lambda kv: -kv[1])
total = sum(v for _, v in parts)


def squarify(vals, x, y, w, h):
    """Plain squarified treemap. Returns rectangles in the order given."""
    out = []
    vals = list(vals)
    while vals:
        s = sum(vals)
        if w >= h:
            cut = w * vals[0] / s
            out.append((x, y, cut, h))
            x, w = x + cut, w - cut
        else:
            cut = h * vals[0] / s
            out.append((x, y, w, cut))
            y, h = y + cut, h - cut
        vals.pop(0)
    return out


img = Image.new("L", (W, W), 246)
d = ImageDraw.Draw(img)
side = W - 2 * MARGIN
rects = squarify([v for _, v in parts], MARGIN, MARGIN, side, side)
for (name, val), (x, y, w, h), tone in zip(parts, rects, TONES):
    d.rectangle([x, y, x + w, y + h], fill=tone)
# No separations are drawn. A boundary is a change of tone, and a drawn line
# would take area away from the part it borders and falsify the proportion.
img.save("docs/img/life-study-1344.png", optimize=True)

# ---- what the drawing actually measures, as built
a = np.asarray(img, dtype=np.int16)
inner = a[MARGIN:W - MARGIN, MARGIN:W - MARGIN]
print(f"{'part':24s} {'tokens':>8s} {'share':>8s} {'drawn':>8s}")
for (name, val), tone in zip(parts, TONES):
    drawn = float((inner == tone).mean())
    print(f"{name:24s} {val:8d} {100*val/total:7.3f}% {100*drawn:7.3f}%")
print(f"{'total':24s} {total:8d}")

smallest = parts[-1][1] / total
print(f"\nsmallest part: {100*smallest:.3f}%")
print("sha256", hashlib.sha256(open("docs/img/life-study-1344.png", "rb").read()).hexdigest())

try:
    reading = open("life-study-reading.txt", encoding="utf-8").read().strip().upper()
except FileNotFoundError:
    print("life-study-reading.txt is absent; the seal cannot be rebuilt.")
else:
    reading = " ".join(reading.split())
    print("sealed reading", hashlib.sha256(reading.encode()).hexdigest())
