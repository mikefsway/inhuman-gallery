#!/bin/sh
# Build the Attempto Parsing Engine, which check_ace.py needs.
#
#     ./build_ape.sh && python3 check_ace.py
#
# APE is not on PyPI and is not vendored here, so this clones it and builds it
# once. It goes outside the repository, under ~/tools by default; set APE_DIR
# to put it elsewhere. Needs git, make, and SWI-Prolog (swipl).
#
# The Clex copy matters. APE ships a 2000-line sample lexicon under the name
# clex_lexicon.pl, and a build that keeps it fails ordinary words like "site"
# and "file". The real Clex is a separate repository.
set -eu

APE_DIR="${APE_DIR:-$HOME/tools/APE}"
CLEX_DIR="${CLEX_DIR:-$(dirname "$APE_DIR")/Clex}"

if [ -x "$APE_DIR/ape.exe" ]; then
    echo "ape.exe is already built at $APE_DIR/ape.exe"
    exit 0
fi

command -v swipl >/dev/null || { echo "swipl is not installed" >&2; exit 1; }

clone() {
    [ -d "$2" ] || git clone --depth 1 "https://github.com/Attempto/$1.git" "$2"
}

mkdir -p "$(dirname "$APE_DIR")"
clone APE "$APE_DIR"
clone Clex "$CLEX_DIR"

cp "$CLEX_DIR/clex_lexicon.pl" "$APE_DIR/prolog/lexicon/clex_lexicon.pl"
( cd "$APE_DIR" && make install )

"$APE_DIR/ape.exe" -text "Every man likes a car." -solo drs >/dev/null
echo "built $APE_DIR/ape.exe"
