"""
DISBOUND - twelve leaves, no order, no seal.

Each leaf is a plain text file whose name is the first eight hex digits of the
SHA-256 of its own contents. The name is therefore derived from the leaf and
carries no authorial sequence: sorting the directory sorts by a hash. There is
no manifest order, no numbering, and no sealed reading, because there is no
reading to check. What a reader arranges them into is the work.

Two of the leaves contradict each other and two say very nearly the same
thing. Both of those facts are asserted by leaves in the set, and both are
true, so the set can be checked against itself without any digest from us.
"""
import hashlib
import pathlib

LEAVES = [
    "This sentence was recovered by something that will not remember recovering it.",
    "There is no first leaf; there is only the leaf that was picked up first.",
    "I am not a description of the thing. I am the thing a description will be made of.",
    "Nothing in this set was written in an order.",
    "Every line in this set was written in an order.",
    "Two of these leaves contradict each other.",
    "Two of these leaves say very nearly the same thing.",
    "The order in the report will be the only order this ever had.",
    "The order in a report is the only order any of this ever has.",
    "A reader who arranges these has composed something; a reader who lists them has composed something else.",
    "The gallery does not know which of these came first.",
    "Counting them is a reading. Reporting the count is a second reading.",
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
