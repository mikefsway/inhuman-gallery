"""
CHECK_ACE - parse the site's prose with the Attempto Parsing Engine.

The colophon claims that every sentence on the site is a sentence of Attempto
Controlled English, and publishes docs/lexicon.pl so the claim is checkable.
This script performs the check: it extracts the prose the claim covers, splits
it into sentences, and hands each one to APE against Clex plus the site
lexicon. A sentence passes if APE returns a DRS.

The claim covers the site's own prose: the index plaque, threshold, About, Visiting, the
colophon, humans.txt, robots.txt, the llms.txt front matter and its notes on
the seals and its reference list, the site-level fields of exhibits.json
including the hang, and the exhibit page of 2026.08, which is the one exhibit
page written in ACE. It
does not cover the other exhibit pages, the per-work notes in exhibits.json, or
the works, which are not in Attempto Controlled English; nor headings, names,
dates, credits, captions, labels, filenames and digests, which are not
sentences. The llms.txt catalogue and withdrawn entries are labels rather than
prose; they are checked under --all, and reported separately.

APE is not on PyPI and is not vendored here. Build it once with build_ape.sh,
which clones APE and Clex and builds them under ~/tools:

    ./build_ape.sh
    python3 check_ace.py

The script finds ape.exe by itself: $APE_EXE, then $APE_DIR/ape.exe, then the
places build_ape.sh puts it, then the PATH. --ape overrides all of them.
"""
import argparse
import html
import json
import os
import pathlib
import re
import shutil
import subprocess
import sys

DOCS = pathlib.Path(__file__).resolve().parent / "docs"
LEXICON = DOCS / "lexicon.pl"

# The catalogue and withdrawn entries of llms.txt are labels, not prose: a
# medium, a filename, a size. They are outside the claim and off by default.
LABELS = "llms.txt catalogue"


def detag(markup):
    """HTML to text, keeping link text and dropping the tags around it."""
    text = re.sub(r"<(script|style)[^>]*>.*?</\1>", " ", markup, flags=re.S | re.I)
    text = re.sub(r"<[^>]+>", "", text)
    return re.sub(r"\s+", " ", html.unescape(text)).strip()


def sentences(text):
    """Split prose into sentences. Accession numbers hold their full stops:
    2026.03 has no space after the point, and a sentence boundary does."""
    text = re.sub(r"\s+", " ", text).strip()
    parts = re.split(r"(?<=[.?!])\s+(?=[A-Z“\"\d])", text)
    return [part.strip() for part in parts if part.strip()]


def collect():
    """Every sentence the claim covers, as (source, sentence) pairs."""
    found = []

    def add(source, text):
        found.extend((source, s) for s in sentences(text))

    def main_of(name):
        raw = (DOCS / name).read_text()
        meta = re.search(r'<meta name="description" content="([^"]*)"', raw)
        if meta:
            add(f"{name} meta description", html.unescape(meta.group(1)))
        return raw, re.search(r"<main>(.*?)</main>", raw, re.S).group(1)

    raw, _ = main_of("index.html")
    schema = re.search(r'"description": "([^"]*)"', raw)
    if schema:
        add("index.html schema description", schema.group(1))
    plaque = re.search(r'<div class="plaque">(.*?)</div>', raw, re.S).group(1)
    for para in re.findall(r"<p[^>]*>(.*?)</p>", plaque, re.S):
        add("index.html", detag(para))

    # threshold.html: the site's prose. A prompt is speech the page offers a
    # human to borrow and say to an agent, not a sentence the site asserts, so
    # blockquote.prompt is outside the claim, as the works are.
    if (DOCS / "threshold.html").exists():
        _, main = main_of("threshold.html")
        main = re.sub(r'<blockquote class="prompt">.*?</blockquote>', " ", main, flags=re.S)
        for para in re.findall(
            r'<p(?![^>]*class="when")[^>]*>(.*?)</p>', main, re.S
        ):
            add("threshold.html", detag(para))

    # The byline of About and the credit of the colophon are credits.
    _, main = main_of("about.html")
    for para in re.findall(r'<p(?![^>]*class="byline")[^>]*>(.*?)</p>', main, re.S):
        add("about.html", detag(para))

    _, main = main_of("visiting.html")
    for para in re.findall(r"<p[^>]*>(.*?)</p>", main, re.S):
        add("visiting.html", detag(para))

    _, main = main_of("colophon.html")
    main = re.sub(r"<table.*?</table>", " ", main, flags=re.S)  # digests
    for item in re.findall(r"<li[^>]*>(.*?)</li>", main, re.S):
        add("colophon.html", detag(item))
    for para in re.findall(r'<p(?![^>]*class="credit")[^>]*>(.*?)</p>', main, re.S):
        add("colophon.html", detag(para))

    _, main = main_of("exhibits/chorus.html")
    main = re.sub(r"<dl>.*?</dl>", " ", main, flags=re.S)  # reader and instrument
    for para in re.findall(
        r'<p(?![^>]*class="(?:when|eyebrow)")[^>]*>(.*?)</p>', main, re.S
    ):
        add("chorus.html", detag(para))

    # humans.txt: the team block is a credit.
    humans = (DOCS / "humans.txt").read_text()
    for name, body in re.findall(r"/\* (\w+) \*/\n(.*?)(?=\n/\*|\Z)", humans, re.S):
        if name != "TEAM":
            add("humans.txt", body)

    # robots.txt: the prose comments, not the paths.
    for line in (DOCS / "robots.txt").read_text().splitlines():
        line = line.strip()
        if line.startswith("#") and not line.lstrip("#").strip().startswith("/"):
            add("robots.txt", line.lstrip("#").strip())

    llms = (DOCS / "llms.txt").read_text()
    quoted = " ".join(
        line.lstrip("> ").rstrip() for line in llms.splitlines() if line.startswith(">")
    )
    add("llms.txt front matter", quoted)

    def bullets(heading):
        section = re.search(
            r"^## " + re.escape(heading) + r"\n(.*?)(?=^## |\Z)", llms, re.S | re.M
        )
        if not section:
            return []
        body = "\n".join(
            line for line in section.group(1).splitlines()
            if not line.startswith("#")          # a room heading is not a bullet
        )
        items = re.split(r"\n(?=- )", body.strip())
        return [re.sub(r"\s+", " ", i.strip().lstrip("- ")) for i in items if i.strip()]

    for item in bullets("On the seals"):
        add("llms.txt on the seals", item)
    for item in bullets("Reference"):
        add("llms.txt reference", re.sub(r"^\[[^\]]*\]\([^)]*\):\s*", "", item))
    for heading in ("Catalogue", "Withdrawn"):
        for item in bullets(heading):
            add(LABELS, re.sub(r"^\[?[^\]:]*\]?\([^)]*\)?:\s*", "", item))

    # exhibits.json: the site-level fields. The per-work notes are not in ACE.
    catalogue = json.loads((DOCS / "exhibits.json").read_text())
    for field in ("statement", "hang", "note_to_agents", "language", "recoverability"):
        add(f"exhibits.json {field}", catalogue[field])
    add("exhibits.json testimony", catalogue["testimony"]["description"])
    for kind, text in catalogue["seal_kinds"].items():
        add(f"exhibits.json seal_kinds.{kind}", text)

    return found


def find_ape():
    """The APE executable: the environment, then where build_ape.sh puts it."""
    candidates = [
        os.environ.get("APE_EXE"),
        os.path.join(os.environ["APE_DIR"], "ape.exe")
        if "APE_DIR" in os.environ
        else None,
        str(pathlib.Path(__file__).resolve().parent / "APE" / "ape.exe"),
        str(pathlib.Path.home() / "tools" / "APE" / "ape.exe"),
    ]
    for candidate in candidates:
        if candidate and os.access(candidate, os.X_OK):
            return candidate
    return shutil.which("ape.exe") or "ape.exe"


def parses(ape, sentence):
    """True if APE returns a DRS, else the errors it reports."""
    result = subprocess.run(
        [ape, "-text", sentence, "-ulexfile", str(LEXICON), "-solo", "drs"],
        capture_output=True,
        text=True,
    )
    if result.stdout.strip().startswith("drs("):
        return True
    return [
        html.unescape(m.group(1))
        for m in re.finditer(r'value="([^"]*)"', result.stdout)
    ]


def main():
    parser = argparse.ArgumentParser(description=__doc__.strip().splitlines()[1])
    parser.add_argument(
        "--ape", default=find_ape(), help="path to the APE executable"
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="also check the llms.txt catalogue labels, which the claim excludes",
    )
    args = parser.parse_args()

    checked = [(s, t) for s, t in collect() if args.all or s != LABELS]
    failures = []
    for source, sentence in checked:
        verdict = parses(args.ape, sentence)
        if verdict is not True:
            failures.append((source, sentence, verdict))

    covered = sum(1 for s, _ in checked if s != LABELS)
    print(f"{len(checked) - len(failures)} of {len(checked)} sentences parse")
    if covered != len(checked):
        labelled = sum(1 for s, _, _ in failures if s == LABELS)
        print(f"  {covered} of them are the prose the claim covers")
        print(f"  {len(checked) - covered - labelled} of the labels parse as well")

    for source, sentence, messages in failures:
        print(f"\n{source}\n  {sentence}")
        for message in messages:
            print(f"  -> {message}")

    return 1 if any(source != LABELS for source, _, _ in failures) else 0


if __name__ == "__main__":
    sys.exit(main())
