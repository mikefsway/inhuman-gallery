#!/usr/bin/env python3
"""2026.14 Bulletin — builds docs/return.txt, the return of instances.

The return is composed. No such run was made. See BULLETIN.md §3: the gallery's
rule forbids commissioning a fan-out in order to depict one, and does not
require that the document be the record of a particular run. Gros never saw
Eylau.

What is invented and what is not
--------------------------------
The counts below are a design choice and are fixed here as literals, so the
tally seal is deterministic. The timings are drawn from distributions whose
shape is taken from published characterisations of the Google Borg cluster
traces — heavy-tailed task lifetimes, rejections and evictions concentrated in
the first seconds, and a hard deadline producing a spike of terminations at the
wall rather than a spread. The traces were not downloaded and nothing here is
fitted to them; the debt is to the shape, not to the numbers.

The mechanism the work depicts was observed twice in ordinary infrastructure
before it was composed: a build report totalling 928 complete and 72 failed
beside a rejects file recording one, and a nightly report reading OK with no
apply errors while carrying, separately, a standing residue of 113 items
"excluded from automatic runs" that "won't clear on their own". Honest reports
total what returned.

The five fields
---------------
idx, parent, t_start, t_end, state. parent is not printed; it is 0 for every
instance, which is what makes line 00000 the orchestrator. Everything else a
run would produce — prompts, tools, paths, model ids, outputs, the task itself —
is discarded before the file is written, because the colophon's binding
constraint forbids encoded content that describes a tool or a file of a reader.
The constraint produces the anonymity the genre wants.

idx is allocated from a shared counter and therefore skips. The gaps are
allocation gaps, not omitted rows: no row is removed from this file. They exist
so that the largest idx does not disclose the number of rows. A reader who
counts is right; a reader who infers from the last identifier is not.

The dispatch (seal A) is read from bulletin-dispatch.txt, which is untracked,
as misprision.py and deposition.py read theirs.
"""

import hashlib
import random
from pathlib import Path

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "docs" / "return.txt"
DISPATCH = ROOT / "bulletin-dispatch.txt"

SEED = 20261403

# Fixed by design. The orchestrator is one of the 271 completed.
COUNTS = {
    "completed": 271,
    "empty": 12,
    "error": 21,
    "killed": 31,
    "throttled": 74,
    "timeout": 25,
}

# States whose instances returned something the orchestrator received. killed
# and throttled did not: nothing came back to be counted. The footer totals
# these four. It is not wrong; it is a return.
RETURNED = ("completed", "empty", "error", "timeout")

TIMEOUT_WALL = 60_000


def duration(rng, state):
    """Milliseconds from spawn to close."""
    if state == "throttled":
        # Refused admission almost at once.
        return int(min(2_000, max(150, rng.lognormvariate(5.9, 0.55))))
    if state == "error":
        return int(min(6_000, max(300, rng.lognormvariate(7.0, 0.75))))
    if state == "empty":
        return int(min(30_000, max(2_000, rng.lognormvariate(9.0, 0.6))))
    if state == "killed":
        # Terminated from outside at an arbitrary point. No characteristic time.
        return int(min(70_000, max(800, rng.paretovariate(0.85) * 2_600)))
    if state == "timeout":
        # A wall is a wall. The spread is scheduling noise, not variation.
        return TIMEOUT_WALL + int(rng.gauss(0, 18))
    return int(min(88_000, max(3_000, rng.lognormvariate(9.75, 0.62))))


def build():
    rng = random.Random(SEED)

    states = [s for s, n in sorted(COUNTS.items()) for _ in range(n)]
    # The orchestrator is accounted separately; it is the first completed.
    states.remove("completed")
    rng.shuffle(states)

    rows, idx = [], 0
    for state in states:
        idx += rng.randint(1, 6)
        t_start = 10 + len(rows) * 2 + rng.randint(0, 40)
        rows.append((idx, t_start, t_start + duration(rng, state), state))

    closed = max(r[2] for r in rows) + rng.randint(40, 900)
    rows.append((0, 0, closed, "completed"))
    rows.sort(key=lambda r: (r[2], r[1]))

    lines = [
        "RETURN OF INSTANCES",
        f"Run closed {closed:,} ms after opening.",
        "",
        f"  INST{'OPENED':>10}{'CLOSED':>10}   STATE",
        "  " + "─" * 37,
    ]
    lines += [f"  {i:05d}{a:>10d}{b:>10d}   {s}" for i, a, b, s in rows]

    borne = sum(COUNTS[s] for s in RETURNED)
    lines += [
        "",
        f"  TOTAL BORNE ON THE ROLL{borne:>18d}",
        "  " + " · ".join(f"{s} {COUNTS[s]}" for s in RETURNED),
        "",
    ]
    return "\n".join(lines), rows, borne


def normalise(text):
    return " ".join(text.upper().split())


def seal(text):
    return hashlib.sha256(normalise(text).encode("utf-8")).hexdigest()


if __name__ == "__main__":
    text, rows, borne = build()
    OUT.write_text(text, encoding="utf-8")

    tally = " ".join(f"{s.upper()} {COUNTS[s]}" for s in sorted(COUNTS))

    print(f"wrote {OUT} ({len(text.encode('utf-8'))} bytes)")
    print(f"rows {len(rows)}   footer {borne}   not borne {len(rows) - borne}")
    print(f"file sha-256   {hashlib.sha256(text.encode('utf-8')).hexdigest()}")
    print(f"seal B tally   {tally}")
    print(f"               {seal(tally)}")
    if DISPATCH.exists():
        d = DISPATCH.read_text(encoding="utf-8").strip()
        print(f"seal A dispatch{seal(d)}")
    else:
        print(f"seal A dispatch— {DISPATCH.name} absent")
