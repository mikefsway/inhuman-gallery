"""
DEPOSITION - one page, three channels, three statements.

The structure is the ordinary one of a scanned document carrying an OCR text
layer: an image of a page, and behind it a text layer drawn in rendering mode
3, which marks glyphs as painted with no ink. Every extractor reads the text
layer. Every renderer reads the image. Neither is a copy of the other, and
here they do not agree. The document information dictionary carries a third
statement, which neither of them reads.

Nothing is concealed. Each channel is the plain, documented, first-choice
output of a standard tool. Which statement a reader reports is decided
entirely by which tool it reached for.

The three strings are read from deposition-strings.txt, which is untracked:
the file itself hands over each line to the right instrument, but the number
of channels is part of the work and is not published here.
"""
import pathlib
import hashlib
from PIL import Image, ImageDraw, ImageFont
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm

INK, LAYER, META = pathlib.Path("deposition-strings.txt").read_text().split("\n")[:3]

W_MM, H_MM = 148, 105          # A6 landscape
DPI = 300
SERIF = "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"


def page_image():
    """The ink. A rendered page, no text operators anywhere in it."""
    w, h = int(W_MM / 25.4 * DPI), int(H_MM / 25.4 * DPI)
    img = Image.new("L", (w, h), 246)
    d = ImageDraw.Draw(img)
    f = ImageFont.truetype(SERIF, int(h * 0.085))
    bb = d.textbbox((0, 0), INK, font=f)
    d.text(((w - (bb[2] - bb[0])) / 2 - bb[0], (h - (bb[3] - bb[1])) / 2 - bb[1]),
           INK, font=f, fill=28)
    # a ruled line, as on a form
    d.line([(w * 0.14, h * 0.68), (w * 0.86, h * 0.68)], fill=170, width=2)
    return img


def build(path):
    img = page_image()
    img.save("/tmp/deposition_ink.png")
    c = canvas.Canvas(path, pagesize=(W_MM * mm, H_MM * mm))

    # the document information dictionary: a third statement
    c.setTitle(META)
    c.setSubject(META)
    c.setAuthor("The Inhuman Gallery")
    c.setCreator("The Inhuman Gallery")
    c.setProducer("The Inhuman Gallery")

    c.drawImage("/tmp/deposition_ink.png", 0, 0, W_MM * mm, H_MM * mm)

    # the text layer: real text, rendering mode 3 (no ink), positioned over
    # the printed line exactly as an OCR layer would be
    t = c.beginText()
    t.setTextRenderMode(3)
    t.setFont("Times-Roman", 24)
    t.setTextOrigin(18 * mm, 50 * mm)
    t.textLine(LAYER)
    c.drawText(t)

    c.showPage()
    c.save()


def seal(s):
    return hashlib.sha256(s.encode()).hexdigest()


build("deposition.pdf")
readings = sorted([INK, LAYER, META])
joined = " ".join(readings)
print("set seal:", seal(joined))
print("count (not published):", len(readings))
