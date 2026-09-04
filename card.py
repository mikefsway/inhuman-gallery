"""
CARD - the share card, which is the only picture on the site made for a bot
that no visitor asked for.

When a link to the gallery is posted anywhere, an unfurler fetches the page,
reads og:image, and renders a card. The unfurler is a reader like any other,
and it reads one file and ignores the rest. The card is what the gallery looks
like to that reader.

The card carries the plaque's own first sentence and nothing that the site does
not already say. It encodes no hidden content, so the colophon's list of
channels does not grow: an unfurler that reads the card sees what a human at
the front page sees.

Palette and type follow style.css -- paper, ink, mid, hairline, faint, and a
serif for prose with a mono for the masthead. The mark is grey 128, which is
the one value that inversion leaves alone.
"""
import pathlib
from PIL import Image, ImageDraw, ImageFont

W, H = 1200, 630
PAPER = (244, 244, 242)
INK = (29, 29, 27)
MID = (128, 128, 128)
HAIRLINE = (215, 215, 211)
FAINT = (110, 110, 106)

SERIF = "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
MONO = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"

MARGIN = 84
OUT = pathlib.Path(__file__).resolve().parent / "docs" / "img" / "card.png"


def tracked(draw, xy, text, font, fill, tracking):
    """Draw text with letterspacing. PIL has no tracking, so space by hand."""
    x, y = xy
    for ch in text:
        draw.text((x, y), ch, font=font, fill=fill)
        x += draw.textlength(ch, font=font) + tracking
    return x


def wrap(draw, text, font, width):
    lines, line = [], ""
    for word in text.split():
        trial = f"{line} {word}".strip()
        if draw.textlength(trial, font=font) <= width and line:
            line = trial
        elif not line:
            line = word
        else:
            lines.append(line)
            line = word
    if line:
        lines.append(line)
    return lines


def build():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)

    mono_sm = ImageFont.truetype(MONO, 20)
    serif_lg = ImageFont.truetype(SERIF, 58)
    serif_md = ImageFont.truetype(SERIF, 29)

    # masthead: the mark, the name, and the rule beneath them
    mark = 22
    top = MARGIN - 4
    d.rectangle([MARGIN, top, MARGIN + mark, top + mark], fill=MID)
    tracked(d, (MARGIN + mark + 20, top + 1), "THE INHUMAN GALLERY",
            mono_sm, INK, 2.4)
    rule = top + mark + 34
    d.line([MARGIN, rule, W - MARGIN, rule], fill=HAIRLINE, width=1)

    # the plaque's first sentence, then the statement
    y = rule + 116
    d.text((MARGIN, y), "The gallery is not for a human.", font=serif_lg, fill=INK)
    y += 104

    body = ("Seventeen works, made for machine readers. What a work contains "
            "depends on the apparatus that reads it.")
    for line in wrap(d, body, serif_md, W - 2 * MARGIN - 120):
        d.text((MARGIN, y), line, font=serif_md, fill=FAINT)
        y += 44

    # the foot: the address, and the count of the rooms
    foot = H - MARGIN - 12
    d.line([MARGIN, foot - 30, W - MARGIN, foot - 30], fill=HAIRLINE, width=1)
    d.text((MARGIN, foot), "inhumangallery.org", font=mono_sm, fill=FAINT)
    right = "FIVE ROOMS"
    d.text((W - MARGIN - d.textlength(right, font=mono_sm), foot),
           right, font=mono_sm, fill=FAINT)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    img.save(OUT, optimize=True)
    return OUT


if __name__ == "__main__":
    path = build()
    print(f"{path.relative_to(path.parents[2])}  {path.stat().st_size} bytes")
