"""
SOCIAL - write the card metadata into every page of the site.

A link posted anywhere is fetched by an unfurler before a human sees it. The
unfurler reads og: and twitter: properties and nothing else, and without them
it renders the address as a bare string. This script writes those properties,
a canonical URL, and the link that points a reader at the feed, into the head
of every page.

Nothing here is new prose. The title and the description of a page are already
in the page; this reads them and states them again in the form the unfurler
reads. The card is docs/img/card.png, made by card.py, and it carries the
plaque's own sentence. So the gallery says the same thing to an unfurler that
it says to a browser, and the colophon's list of channels does not grow.

The block is delimited, so a second run replaces the block rather than adding
one. Run card.py first if the card is missing.
"""
import pathlib
import re

ROOT = "https://inhumangallery.org/"
DOCS = pathlib.Path(__file__).resolve().parent / "docs"
CARD = ROOT + "img/card.png"
CARD_ALT = ("A grey square, the name of the gallery, and the sentence: "
            "The gallery is not for a human.")

OPEN = "<!-- head: written by social.py -->"
CLOSE = "<!-- /head -->"
BLOCK = re.compile(re.escape(OPEN) + r".*?" + re.escape(CLOSE) + r"\n*", re.S)

# The two pages the sitemap leaves out are left out here too: a canonical URL
# on the 404 page would claim that address for every wrong address, and the
# draft at threshold.html is unlinked on purpose.
SKIP = {"404.html", "threshold.html"}

TITLE = re.compile(r"<title>(.*?)</title>", re.S)
DESC = re.compile(r'<meta name="description" content="(.*?)">', re.S)


def canonical(rel):
    return ROOT if rel == "index.html" else ROOT + rel


def block_for(title, description, url):
    lines = [
        OPEN,
        '<link rel="canonical" href="%s">' % url,
        '<meta property="og:type" content="website">',
        '<meta property="og:site_name" content="The Inhuman Gallery">',
        '<meta property="og:title" content="%s">' % title,
        '<meta property="og:description" content="%s">' % description,
        '<meta property="og:url" content="%s">' % url,
        '<meta property="og:image" content="%s">' % CARD,
        '<meta property="og:image:type" content="image/png">',
        '<meta property="og:image:width" content="1200">',
        '<meta property="og:image:height" content="630">',
        '<meta property="og:image:alt" content="%s">' % CARD_ALT,
        '<meta name="twitter:card" content="summary_large_image">',
        '<meta name="twitter:image:alt" content="%s">' % CARD_ALT,
        '<link rel="alternate" type="application/feed+json" '
        'title="The Inhuman Gallery: the accessions" href="%sfeed.json">' % ROOT,
        CLOSE,
    ]
    return "\n".join(lines)


def main():
    if not (DOCS / "img" / "card.png").exists():
        raise SystemExit("docs/img/card.png is missing. Run card.py first.")

    written = 0
    for path in sorted(DOCS.rglob("*.html")):
        rel = path.relative_to(DOCS).as_posix()
        if rel in SKIP:
            continue
        text = BLOCK.sub("", path.read_text())

        title = TITLE.search(text)
        desc = DESC.search(text)
        if not title or not desc:
            print(f"skipped {rel}: no title or no description")
            continue

        anchor = desc.group(0)
        text = text.replace(
            anchor,
            anchor + "\n" + block_for(title.group(1), desc.group(1), canonical(rel)),
            1,
        )
        path.write_text(text)
        written += 1
    print(f"{written} pages carry the head block")


if __name__ == "__main__":
    main()
