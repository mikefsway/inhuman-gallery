"""
FEED - a feed of the accessions, so a reader can return without being asked to.

The feed is JSON Feed 1.1 rather than Atom or RSS, which are XML. The colophon
says that the site contains HTML and CSS and some plain text and a PNG and a
PDF; the site already serves exhibits.json, and a JSON feed adds no format that
the sentence has to be widened for. Every reader that reads Atom reads this
too, and a crawler that follows the head link finds a file that changes when
the gallery changes.

The date of a work is not an invention. It is the date at which the page of the
work first entered the repository, read out of git, so a reader who doubts a
date can check it against the history rather than against the gallery's word.

The note of a work is the note the machine catalogue already carries. Nothing
here is written for the feed.
"""
import json
import pathlib
import subprocess

ROOT = "https://inhumangallery.org/"
REPO = pathlib.Path(__file__).resolve().parent
DOCS = REPO / "docs"


def first_seen(rel_page):
    """The date the page entered the repository, ISO 8601, from git."""
    out = subprocess.run(
        ["git", "log", "--diff-filter=A", "--follow", "--format=%aI", "-1",
         "--", f"docs/{rel_page}"],
        cwd=REPO, capture_output=True, text=True, check=True,
    ).stdout.strip()
    return out or None


def item(work, withdrawn=False):
    url = ROOT + work["page"]
    title = f"{work['title']} ({work['accession']})"
    if withdrawn:
        title += ", withdrawn"
    parts = [work.get("medium", ""), work.get("note", "") or work.get("status", "")]
    return {
        "id": url,
        "url": url,
        "title": title,
        "content_text": " ".join(p for p in parts if p).strip(),
        "date_published": first_seen(work["page"]),
        "tags": [f"room {work['room']}"] if work.get("room") else [],
    }


def build():
    catalogue = json.loads((DOCS / "exhibits.json").read_text())

    items = [item(w) for w in catalogue["works"]]
    items += [item(w, withdrawn=True) for w in catalogue["withdrawn"]]
    items = [i for i in items if i["date_published"]]
    items.sort(key=lambda i: i["date_published"], reverse=True)

    feed = {
        "version": "https://jsonfeed.org/version/1.1",
        "title": catalogue["name"],
        "home_page_url": ROOT,
        "feed_url": ROOT + "feed.json",
        "description": catalogue["statement"],
        "language": "en",
        "items": items,
    }
    (DOCS / "feed.json").write_text(json.dumps(feed, indent=2) + "\n")
    return len(items)


if __name__ == "__main__":
    print(f"{build()} accessions -> docs/feed.json")
