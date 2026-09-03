"""
DISBOUND - twelve leaves, no order, no seal.

Each leaf is a plain text file whose name is the first eight hex digits of the
SHA-256 of its own contents. The name is therefore derived from the leaf and
carries no authorial sequence: sorting the directory sorts by a hash. There is
no manifest order and no numbering, and no order is sealed, because the work
has no order to seal. What a reader arranges them into is the work.

The leaves are plain statements from one account. Nothing in them refers to
the set, to the reader, or to the gallery. Two of them contradict each other
and two say very nearly the same thing. Those two relations are sealed and are
announced nowhere else, so a reader that recovers one has opened every leaf
and held them together; a reader that lists the directory has only the set.

Naming by digest is what makes this cost something. Two leaves that differ by
three words take names with nothing in common, so the work's own mechanism
conceals the one relation a binding would have made obvious.
"""
import hashlib
import pathlib
import re

LEAVES = [
    "The crates came in through the yard door.",
    "The smaller crate was opened first.",
    "Nobody signed for them.",
    "It was raining when they arrived.",
    "A label inside the lid gave a different title.",
    "The smaller of the two crates was opened first.",
    "The photographs were taken after the works were on the wall.",
    "The yard was dry all morning.",
    "The packing list named three items.",
    "The third item has not been found.",
    "Two items came out of the crates.",
    "The condition report was written the following week, from memory.",
]

out = pathlib.Path("docs/disbound")
for old in out.glob("*.txt"):
    old.unlink()

names = []
for text in LEAVES:
    body = text + "\n"
    h = hashlib.sha256(body.encode()).hexdigest()
    (out / f"{h[:8]}.txt").write_text(body)
    names.append((h[:8], h, text))

for short, full, text in sorted(names):
    print(f"{short}.txt  {len(text):3d}  {text}")
print(f"\n{len(names)} leaves, {len({n for n,_,_ in names})} distinct names")


# The two sealed relations. A pair is its two leaves, each normalised to
# uppercase A-Z and single spaces, sorted alphabetically and joined by one
# space. Which leaves make each pair is read from an untracked file, as with
# 2026.11 and every work after it, so this script rebuilds the leaves and does
# not name the pairs. The file holds two lines, "contradiction" and
# "near-identical", each followed by the two indices of that pair.
def seal(a, b):
    norm = lambda t: re.sub(r"[^A-Z]+", " ", t.upper()).strip()
    joined = " ".join(sorted([norm(a), norm(b)]))
    return hashlib.sha256(joined.encode()).hexdigest()


print()
try:
    spec = pathlib.Path("disbound-pairs.txt").read_text(encoding="utf-8")
except FileNotFoundError:
    print("disbound-pairs.txt is absent; the seals cannot be rebuilt.")
else:
    for line in spec.split("\n"):
        if not line.strip():
            continue
        name, i, j = line.split()
        print(f"{name:15s} {seal(LEAVES[int(i)], LEAVES[int(j)])}")
