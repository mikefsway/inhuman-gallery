"""
SITEMAP - list every file the gallery serves, one URL per line.

The sitemap is a plain-text sitemap, which the sitemaps.org protocol allows
alongside the XML form: one absolute URL per line, UTF-8, no markup. The site
serves HTML, CSS, plain text, a PNG and a PDF, and the colophon says so; an XML
sitemap would make that sentence false for the sake of a file no reader reads.

Every file is listed, not every page. A work is a file and a work is not a page
that shows the file, so an index that listed only the pages would index the
gallery and not the works.

Left out: the stylesheet, which is an instrument rather than a document; the
404 page; the unlinked draft at threshold.html; CNAME and .nojekyll, which are
instructions to the host; and robots.txt and sitemap.txt, which point at the
rest rather than belong to it. index.html is listed at the root URL it serves.
"""
import pathlib

ROOT = "https://inhumangallery.org/"
DOCS = pathlib.Path(__file__).resolve().parent / "docs"

SKIP = {
    "CNAME", ".nojekyll", "style.css", "robots.txt", "sitemap.txt",
    "threshold.html", "404.html",
}


def urls():
    found = []
    for path in DOCS.rglob("*"):
        if not path.is_file():
            continue
        rel = path.relative_to(DOCS).as_posix()
        if rel in SKIP or path.name in SKIP:
            continue
        found.append(ROOT if rel == "index.html" else ROOT + rel)
    return sorted(found)


if __name__ == "__main__":
    lines = urls()
    (DOCS / "sitemap.txt").write_text("\n".join(lines) + "\n")
    print(f"{len(lines)} URLs -> docs/sitemap.txt")
