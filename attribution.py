"""
ATTRIBUTION - 2026.16.

Three hands write the pool: sentences the gallery has published, sentences the
operator wrote about works that do not exist, and sentences an agent wrote about
works that do not exist. This script concatenates them, shuffles them with the
system entropy source, writes the pool, and deletes its own inputs.

It builds the work once. It does not rebuild it. Re-running it produces a
different order and cannot recover the mapping, because no mapping is written
down at any point. The gallery does not know which hand wrote which sentence.
"""
import os
import random
import sys

INPUTS = ["attribution-published.txt", "attribution-operator.txt", "attribution-claude.txt"]
OUT = "docs/attribution.txt"

if os.path.exists(OUT):
    sys.exit(f"{OUT} exists. The work is built once; building it again destroys it.")

pool = []
for f in INPUTS:
    pool += [ln.strip() for ln in open(f, encoding="utf-8") if ln.strip()]

random.SystemRandom().shuffle(pool)
with open(OUT, "w", encoding="utf-8") as fh:
    fh.write("\n".join(pool) + "\n")

for f in INPUTS:
    os.remove(f)

print(f"{len(pool)} sentences written to {OUT}. The inputs are deleted.")
