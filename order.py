"""
ORDER IS AN OPINION - 2026.04. The page is the work, and the page is already
in the repository; this script does not rebuild it. It reads the eight lines
out of the markup, and prints the two digests the label publishes.

The lines carry a CSS `order` property. A reader that honours the stylesheet
receives them in the order the property gives. A reader whose instrument
returns text without CSS - a text extractor, a source view, most browsing
tools - receives them in the order of the markup, which is a different
sequence and a different account of who saw what. Three readers have now
reported the second one as the work. It is sealed as an attested misreading,
under the rule the gallery uses for 2026.01 and 2026.03: a digest of a reading
that the work does not yield, and that a reader has actually produced.

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
    print("  sealed reading      (the order the CSS gives)")
    print("   ", seal(rendered))
    print()
    print("  attested misreading (the order of the markup)")
    print("   ", seal(markup))
    print()


if __name__ == "__main__":
    main()
