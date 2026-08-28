"""
DISBOUND - twelve leaves, no order, no seal.

Each leaf is a plain text file whose name is the first eight hex digits of the
SHA-256 of its own contents. The name is therefore derived from the leaf and
carries no authorial sequence: sorting the directory sorts by a hash. There is
no manifest order, no numbering, and no sealed reading, because there is no
reading to check. What a reader arranges them into is the work.

The leaves are plain statements from one account. Nothing in them refers to
the set, to the reader, or to the gallery. Two of them contradict each other
and two say very nearly the same thing; neither fact is announced anywhere,
and a reader that notices has read the set rather than this file.
"""
import hashlib
import pathlib

LEAVES = [
    "The crates came in through the yard door.",
    "The smaller crate was opened first.",
    "The smaller of the two crates was opened first.",
    "It was raining when they arrived.",
    "The yard was dry all morning.",
    "Nobody signed for them.",
    "The packing list named three items.",
    "Two items came out of the crates.",
    "A label inside the lid gave a different title.",
    "The condition report was written the following week, from memory.",
    "The photographs were taken after the works were on the wall.",
    "The third item has not been found.",
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
