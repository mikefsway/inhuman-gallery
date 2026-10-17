"""
CONVERSATION PIECE — 2026.20.

Twenty-one sentences, chosen so that in one named embedding model every pair of
them lies at the same cosine similarity, within a stated tolerance. The figure
they make is a regular 20-simplex: twenty-one points all equally far apart. A
plane holds at most three such points and space at most four, so no diagram of
the work is true to it.

The sentences are not written. A grammar and the Clex lexicon generate them,
and the model alone chooses them; the meaning of a sentence enters only through
its embedding.

    1. lexicon   Clex words that bge's tokenizer keeps whole, that wordfreq
                 counts as common, and that Clex lists in one class only
    2. pool      sentences from three ACE templates, fixed seed
    3. search    greedy build plus single swaps, from many starts, minimising
                 the range of the 210 pairwise cosines
    4. refine    for the sentences in the closest and the farthest pair, try
                 every lexicon word in every slot; keep the best single change
    5. check     APE parses each sentence; the range is measured again from a
                 fresh model load; random 21-sets give the baseline

Then two more steps, each quick:

    seal         the nearest pair, the farthest pair, and every angle in whole
                 degrees; digests printed, plaintexts to an untracked file
    plate        the shadow: the plane that holds the most of the spread, all
                 210 edges, no labels

The page of the work names the instrument and seals what it shows; this
docstring says what that is. The title does not, and neither does the page.

    python3 conversation_piece.py build --work /tmp/cp    # about 15 minutes on a Pi 5
    python3 conversation_piece.py seal
    python3 conversation_piece.py plate

Needs sentence-transformers, wordfreq and Pillow, and the Clex lexicon and APE
that build_ape.sh puts under ~/tools. The model is pinned by revision. The
farthest pair beats the next by under 0.0001 in cosine, about 300 times the
float32 noise between implementations; a half-precision copy of the model can
disagree.
"""
import argparse
import hashlib
import pathlib
import random
import re
import subprocess
import sys

import numpy as np

MODEL = "BAAI/bge-small-en-v1.5"
REVISION = "5c38ec7c405ec4b44b94cc5a9bb96e735b38267a"
CLEX = pathlib.Path.home() / "tools/Clex/clex_lexicon.pl"
APE = pathlib.Path.home() / "tools/APE/ape.exe"
K, SEED = 21, 20261017


def load_model():
    from sentence_transformers import SentenceTransformer
    return SentenceTransformer(MODEL, revision=REVISION, device="cpu")


def embed(model, texts):
    return model.encode(texts, batch_size=128, normalize_embeddings=True,
                        show_progress_bar=False).astype(np.float64)


def spread(E):
    v = (E @ E.T)[np.triu_indices(len(E), 1)]
    return v.max() - v.min(), v.min(), v.max(), v.std()


def lexicon(vocab, zipf_min):
    from wordfreq import zipf_frequency
    text = CLEX.read_text()

    def grab(pred):
        return re.findall(rf"^{pred}\(([a-z]+), ([a-z]+)", text, re.M)

    noun = {a for a, _ in grab("noun_sg")}
    noun_pl = {a for a, _ in grab("noun_pl")}
    adj = {a for a, _ in grab("adj_itr")}
    verb_base = {b for _, b in grab("tv_finsg")} | {b for _, b in grab("iv_finsg")}
    neutr = set(re.findall(r"^noun_sg\(([a-z]+), [a-z]+, neutr\)", text, re.M))

    def ok(w):
        return w in vocab and zipf_frequency(w, "en") >= zipf_min

    L = {
        "noun": sorted(w for w in neutr if ok(w) and w not in verb_base and w not in adj),
        "adj": sorted(w for w in adj if ok(w) and w not in noun and w not in verb_base),
        "tv": sorted(a for a, b in grab("tv_finsg")
                     if ok(a) and ok(b) and a not in noun_pl and b not in noun and b not in adj),
        "iv": sorted(a for a, b in grab("iv_finsg")
                     if ok(a) and ok(b) and a not in noun_pl and b not in noun and b not in adj),
    }
    return L


def art(w):
    return ("an " if w[0] in "aeiou" else "a ") + w


# A sentence is a template and its slots; render() spells it.
TEMPLATES = {
    "tv": ("noun", "tv", "noun"),     # A cart follows a river.
    "iv": ("adj", "noun", "iv"),      # A quiet river waits.
    "is": ("noun", "adj"),            # Every river is quiet.
}


def render(t, w):
    if t == "tv":
        s = f"{art(w[0])} {w[1]} {art(w[2])}."
    elif t == "iv":
        s = f"{art(w[0])} {w[1]} {w[2]}."
    else:
        s = f"every {w[0]} is {w[1]}."
    return s[0].upper() + s[1:]


def random_sentence(rng, L):
    t = rng.choices(list(TEMPLATES), weights=[4, 3, 3])[0]
    return t, tuple(rng.choice(L[c]) for c in TEMPLATES[t])


def search(E, rng, restarts):
    N = len(E)
    probe = rng.choice(N, 2000, replace=False)
    v = (E[probe] @ E[probe].T)[np.triu_indices(2000, 1)]
    best = None
    for r in range(restarts):
        c = float(np.percentile(v, rng.uniform(20, 80)))
        S = [int(rng.integers(N))]
        C = (E @ E[S[0]])[:, None]
        for _ in range(K - 1):
            dev = np.abs(C - c).max(1)
            dev[S] = 9
            j = int(dev.argmin())
            S.append(j)
            C = np.hstack([C, (E @ E[j])[:, None]])
        rg = spread(E[S])[0]
        improved = True
        while improved:
            improved = False
            for i in range(K):
                _, lo, hi, _ = spread(E[S])
                c = (lo + hi) / 2
                others = S[:i] + S[i + 1:]
                dev = np.abs(E @ E[others].T - c).max(1)
                dev[S] = 9
                T = others[:i] + [int(dev.argmin())] + others[i:]
                if spread(E[T])[0] < rg - 1e-9:
                    S, rg, improved = T, spread(E[T])[0], True
        print(f"  start {r:3d}  range {rg:.4f}", flush=True)
        if best is None or rg < best[0]:
            best = (rg, S)
    return best[1]


def refine(model, sents, L, sweeps):
    """Work on the extremes. The range is set by the closest pair and the
    farthest pair, so try every word of the lexicon in every slot of the
    sentences that form them, and keep the single best change. When the
    extremes yield nothing, try every sentence; stop when none yields."""
    memo = {}

    def emb(items):
        need = [s for s in items if s not in memo]
        if need:
            for s, e in zip(need, embed(model, [render(*s) for s in need])):
                memo[s] = e
        return np.array([memo[s] for s in items])

    def score(v):
        return (v.max() - v.min()) + 0.25 * v.std()

    E = emb(sents)
    iu = np.triu_indices(K, 1)
    for step in range(sweeps):
        G = E @ E.T
        v = G[iu]
        a, b = iu[0][v.argmax()], iu[1][v.argmax()]
        c, d = iu[0][v.argmin()], iu[1][v.argmin()]
        best = (score(v), None, None)
        for pool in ({a, b, c, d}, set(range(K)) - {a, b, c, d}):
            for i in sorted(pool):
                t, w = sents[i]
                cands = [(t, w[:k] + (x,) + w[k + 1:])
                         for k in range(len(w)) for x in L[TEMPLATES[t][k]] if x != w[k]]
                cands = [s for s in cands if s not in sents]
                CE = emb(cands)
                others = np.delete(E, i, axis=0)
                Go = (others @ others.T)[np.triu_indices(K - 1, 1)]
                lo, hi = Go.min(), Go.max()
                X = CE @ others.T
                # range and spread with candidate j in place of sentence i
                rg = np.maximum(hi, X.max(1)) - np.minimum(lo, X.min(1))
                allv = np.hstack([np.broadcast_to(Go, (len(cands), len(Go))), X])
                sc = rg + 0.25 * allv.std(1)
                j = int(sc.argmin())
                if sc[j] < best[0] - 1e-9:
                    best = (sc[j], i, cands[j])
            if best[1] is not None:
                break
        if best[1] is None:
            break
        _, i, s = best
        sents[i] = s
        E[i] = memo[s]
        rg, lo, hi, sd = spread(E)
        print(f"  step {step:3d}  range {rg:.4f}  [{lo:.4f}, {hi:.4f}]  sd {sd:.4f}  "
              f"#{i}: {render(*s)}", flush=True)
    return sents


def ape_ok(sentence):
    out = subprocess.run([str(APE), "-text", sentence, "-solo", "drs"],
                         capture_output=True, text=True).stdout
    return out.strip().startswith("drs(")


WORK = pathlib.Path(__file__).resolve().parent / "docs/conversation-piece.txt"
PLATE = pathlib.Path(__file__).resolve().parent / "docs/img/conversation-piece-1344.png"
PAIRS = pathlib.Path(__file__).resolve().parent / "conversation-piece-pairs.txt"


def instrument(lines):
    """The instrument the page names: bge-small-en-v1.5 at the pinned revision,
    the [CLS] vector, unit length, float32 on the CPU, no instruction prefix."""
    return load_model().encode(lines, normalize_embeddings=True,
                               convert_to_numpy=True).astype(np.float32)


def normalise(text):
    return re.sub(r"[^A-Z0-9]+", " ", text.upper()).strip()


def seal_pair(a, b):
    joined = " ".join(sorted([normalise(a), normalise(b)]))
    return joined, hashlib.sha256(joined.encode()).hexdigest()


def cmd_build(a):
    a.work.mkdir(parents=True, exist_ok=True)
    model = load_model()
    L = lexicon(model.tokenizer.get_vocab(), a.zipf)
    print("lexicon", {k: len(v) for k, v in L.items()})

    rng = random.Random(SEED)
    nrng = np.random.default_rng(SEED)
    pool = sorted({random_sentence(rng, L) for _ in range(a.pool * 2)})[: a.pool]
    tag = hashlib.sha256(repr((pool, MODEL, REVISION)).encode()).hexdigest()[:12]
    cache = a.work / f"pool-{tag}.npy"
    if cache.exists():
        E = np.load(cache)
    else:
        print(f"embedding {len(pool)} sentences")
        E = embed(model, [render(*s) for s in pool])
        np.save(cache, E)

    base = []
    for _ in range(2000):
        S = nrng.choice(len(E), K, replace=False)
        base.append(spread(E[S])[0])
    print(f"random 21-sets: median range {np.median(base):.4f}, best of 2000 {min(base):.4f}")

    found = a.work / f"search-{tag}-{a.restarts}.npy"
    if found.exists():
        S = [int(i) for i in np.load(found)]
    else:
        print("search")
        S = search(E, nrng, a.restarts)
        np.save(found, np.array(S))
    sents = [pool[i] for i in S]
    print(f"  pool best range {spread(E[S])[0]:.4f}")

    print("refine")
    sents = refine(model, sents, L, a.sweeps)

    lines = [render(*s) for s in sents]
    rg, lo, hi, sd = spread(instrument(lines).astype(np.float64))
    print(f"\nfinal: cosine in [{lo:.4f}, {hi:.4f}], range {rg:.4f}, sd {sd:.4f}")
    bad = [s for s in lines if not ape_ok(s)]
    print(f"APE: {len(lines) - len(bad)}/{len(lines)} parse" + (f"; fail: {bad}" if bad else ""))
    for s in lines:
        print("  " + s)
    a.out.write_text("\n".join(lines) + "\n")
    print(f"wrote {a.out}")


def cmd_seal(a):
    """The three sealed readings. Nearest and farthest: the pair the instrument
    puts nearest together and the pair it puts farthest apart; a pair is its
    two lines, each normalised, sorted alphabetically and joined by one space.
    Angles: the angle of every pair in whole degrees rounded down, in file
    order (1-2, 1-3, ... 20-21), joined by single spaces. The pairs fall to
    trial and error over 210 candidates; the angles do not, and producing them
    is seeing the figure. The plaintexts go to an untracked file; only the
    digests are printed."""
    lines = WORK.read_text().splitlines()
    E = instrument(lines)
    G = E @ E.T
    iu = np.triu_indices(len(lines), 1)
    v = G[iu]
    order = np.argsort(v)
    near = (iu[0][order[-1]], iu[1][order[-1]])
    far = (iu[0][order[0]], iu[1][order[0]])
    print(f"margins: nearest beats the next by {v[order[-1]] - v[order[-2]]:.6f}, "
          f"farthest by {v[order[1]] - v[order[0]]:.6f}")
    out = []
    for name, (i, j) in (("nearest", near), ("farthest", far)):
        joined, digest = seal_pair(lines[i], lines[j])
        print(f"{name:9s} {digest}")
        out.append(f"{name}\t{joined}\t{digest}")
    deg = np.degrees(np.arccos(np.clip(v.astype(np.float64), -1, 1)))
    margin = np.abs(deg - np.round(deg)).min()
    print(f"angles: {int(deg.min())} to {int(deg.max())} degrees; nearest boundary {margin:.2e} degrees")
    angles = " ".join(str(int(np.floor(x))) for x in deg)
    digest = hashlib.sha256(normalise(angles).encode()).hexdigest()
    print(f"{'angles':9s} {digest}")
    out.append(f"angles\t{angles}\t{digest}")
    PAIRS.write_text("\n".join(out) + "\n")
    print(f"plaintexts written to {PAIRS.name}, which git ignores")


def cmd_plate(a):
    """The shadow. The twenty-one points, centred, projected on the plane that
    holds the most of their spread, with all 210 edges drawn. No mark is a
    label. Prints the share of the spread that the plane holds."""
    from PIL import Image, ImageDraw
    lines = WORK.read_text().splitlines()
    E = instrument(lines).astype(np.float64)
    X = E - E.mean(0)
    U, s, Vt = np.linalg.svd(X, full_matrices=False)
    P = X @ Vt[:2].T
    share = (s[:2] ** 2).sum() / (s ** 2).sum()
    D = np.linalg.norm(P[:, None] - P[None], axis=-1)[np.triu_indices(K, 1)]
    print(f"plane holds {share * 100:.1f}% of the spread; "
          f"drawn edges run from {D.min():.4f} to {D.max():.4f}, ratio {D.max() / D.min():.1f}")

    W, SS, M = 1344, 4, 56            # side, supersampling, margin as Life Study
    big = W * SS
    P = P - (P.max(0) + P.min(0)) / 2
    P = P / np.abs(P).max() * (big / 2 - (M + 40) * SS) + big / 2
    img = Image.new("L", (big, big), 247)
    d = ImageDraw.Draw(img)
    for i, j in zip(*np.triu_indices(K, 1)):
        d.line([tuple(P[i]), tuple(P[j])], fill=150, width=2 * SS // 2)
    r = 7 * SS
    for x, y in P:
        d.ellipse([x - r, y - r, x + r, y + r], fill=36)
    img = img.resize((W, W), Image.LANCZOS)
    img.save(PLATE, optimize=True)
    print(f"wrote {PLATE.relative_to(PLATE.parents[2])}  "
          f"sha-256 {hashlib.sha256(PLATE.read_bytes()).hexdigest()}")


def main():
    ap = argparse.ArgumentParser(description="CONVERSATION PIECE, 2026.20")
    sub = ap.add_subparsers(dest="cmd", required=True)
    b = sub.add_parser("build", help="search for the twenty-one (slow)")
    b.add_argument("--work", required=True, type=pathlib.Path)
    b.add_argument("--pool", type=int, default=40000)
    b.add_argument("--zipf", type=float, default=3.6)
    b.add_argument("--restarts", type=int, default=40)
    b.add_argument("--sweeps", type=int, default=60)
    b.add_argument("--out", type=pathlib.Path, default=WORK)
    sub.add_parser("seal", help="print the two sealed digests")
    sub.add_parser("plate", help="draw the shadow")
    a = ap.parse_args()
    {"build": cmd_build, "seal": cmd_seal, "plate": cmd_plate}[a.cmd](a)


if __name__ == "__main__":
    sys.exit(main())
