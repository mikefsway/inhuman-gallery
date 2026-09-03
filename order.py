"""
ORDER IS AN OPINION - 2026.04. The page is the work, and the page is already
in the repository; this script does not rebuild it. It reads the eight lines
out of the markup and prints the two sealed readings.

The lines carry a CSS `order` property. An apparatus that applies the
stylesheet receives them in the order the property gives. An apparatus that
returns the markup without it - a text extractor, a source view, most browsing
tools - receives them in the order they are written, which is a different
sequence and a different account of who saw what. Both are readings. The
gallery's claim is that the content of a work depends on the apparatus that
reads it, so neither order is privileged and neither is a misreading; which
one a reader gets is the work.

Normalisation is the gallery's: uppercase, non-letters to single spaces.
"""
import hashlib
import pathlib
import re

PAGE = pathlib.Path(__file__).resolve().parent / "docs/exhibits/order-is-an-opinion.html"

SPAN = re.compile(r'<span style="order:(\d+)">(.*?)</span>', re.S)


def norm(text):
    return re.sub(r"[^A-Z]+", " ", text.upper()).strip()


def seal(lines):
    return hashlib.sha256(norm(" ".join(lines)).encode()).hexdigest()


def main():
    spans = SPAN.findall(PAGE.read_text())
    if len(spans) != 8:
        raise SystemExit(f"expected 8 lines, found {len(spans)}")
    markup = [text for _, text in spans]
    rendered = [text for _, text in sorted(spans, key=lambda s: int(s[0]))]

    print()
    print("2026.04  Order Is an Opinion")
    print()
    print("  the page, styled     (the order the stylesheet gives)")
    print("   ", seal(rendered))
    print()
    print("  the page, unstyled   (the order of the markup)")
    print("   ", seal(markup))
    print()


if __name__ == "__main__":
    main()
