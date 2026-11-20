"""Read the 12 BIP39 words from a photo of a Seed Hammer plate.

Pipeline: corner holes -> straighten (both 180 deg orientations) -> stroke map
-> fine alignment on the line numbers -> per-cell letter scores against the
Seed Hammer font -> best BIP39 word per line -> checksum.

Usage: python3 reader.py photo.jpg [more.jpg ...]
"""
import json
import sys
import time

import cv2
import numpy as np
from mnemonic import Mnemonic

from align import LAYOUT, align
from font import glyph_image
from holes import find_holes
from strokes import stroke_map
from warp import warp

M = Mnemonic("english")
WORDLIST = [w.upper() for w in M.wordlist]
LETTERS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
MAXLEN = max(len(w) for w in WORDLIST)   # 8


def templates(ux, uy):
    t = {}
    for ch in LETTERS:
        g = glyph_image(ch, ux, uy, thick=5, blur=2.5)
        t[ch] = g
    return t


def cell_scores(smap, p, n_lines, word_col=3, cells=MAXLEN):
    """Return S[line, pos, letter] (normalised correlation) and E[line, pos]
    (stroke energy) for every character cell of every word."""
    x0, y0, ux, uy = p
    tmpl = templates(ux, uy)
    th, tw = next(iter(tmpl.values())).shape
    m = int(round(1.2 * ux))  # search slack in px around the expected cell
    S = np.full((n_lines, MAXLEN, 26), -1.0, np.float32)
    E = np.zeros((n_lines, MAXLEN), np.float32)
    for i in range(n_lines):
        for k in range(cells):
            cx = int(round(x0 + (word_col + k) * 6 * ux))
            cy = int(round(y0 + i * 9 * uy))
            win = smap[max(0, cy - m):cy + th + m, max(0, cx - m):cx + tw + m]
            if win.shape[0] < th or win.shape[1] < tw:
                continue
            core = smap[cy + int(2 * uy):cy + int(8 * uy), cx + int(1 * ux):cx + int(5 * ux)]
            E[i, k] = float(core.mean()) if core.size else 0.0
            for j, ch in enumerate(LETTERS):
                r = cv2.matchTemplate(win, tmpl[ch], cv2.TM_CCOEFF_NORMED)
                S[i, k, j] = float(r.max())
    return S, E


def decode_line(S, E, e_ref, top=3):
    """Score every BIP39 word against one line of cells."""
    # a cell is "empty" when no letter fits it well and it carries little ink
    best = S.max(1)
    blank = np.clip(0.85 - best - 0.6 * np.maximum(E / e_ref - 0.5, 0), -0.6, 0.7)
    scores = []
    for w in WORDLIST:
        s = sum(S[k, ord(c) - 65] for k, c in enumerate(w))
        s += blank[len(w):].sum()
        scores.append(s / MAXLEN)
    scores = np.array(scores)
    order = np.argsort(scores)[::-1][:top]
    return [(WORDLIST[i], float(scores[i])) for i in order]


def read_plate(img, verbose=True):
    t0 = time.time()
    found = find_holes(img)
    if found is None:
        return {"ok": False, "error": "plate not found (holes)"}
    quad, _ = found
    n = LAYOUT["lines"]
    best = None
    for flip in (False, True):
        w = warp(img, quad, flip)
        smap = stroke_map(w)
        p, sc = align(smap)
        # orientation test: the first 3 cells of every word always hold a letter;
        # the right way up, they match the font far better
        S3, _ = cell_scores(smap, p, n, cells=3)
        q = float(S3.max(2).mean())
        if best is None or q > best[0]:
            best = (q, flip, smap, p, sc)
    q, flip, smap, p, sc = best
    S, E = cell_scores(smap, p, n)
    e_ref = float(np.median(E[:, :3]))   # first 3 cells always hold letters
    lines = [decode_line(S[i], E[i], e_ref) for i in range(n)]
    words = [l[0][0] for l in lines]
    margins = [l[0][1] - l[1][1] for l in lines]
    valid = M.check(" ".join(words).lower())
    out = {"ok": True, "words": words, "checksum_valid": valid,
           "margins": [round(m, 3) for m in margins],
           "alternatives": [[(w, round(s, 3)) for w, s in l] for l in lines],
           "flipped": flip, "align_score": round(sc, 1),
           "seconds": round(time.time() - t0, 1)}
    if not valid:
        out["suggestion"] = repair(lines)
    return out


def repair(lines, max_changes=2):
    """If the checksum fails, look for the smallest score loss that yields a
    valid checksum by swapping low-margin words for their alternatives.
    Only a SUGGESTION: the user must confirm against the plate."""
    import itertools
    base = [l[0][0] for l in lines]
    weak = sorted(range(len(lines)), key=lambda i: lines[i][0][1] - lines[i][1][1])[:4]
    best = None
    for nchg in range(1, max_changes + 1):
        for idxs in itertools.combinations(weak, nchg):
            for alts in itertools.product(*[range(1, len(lines[i])) for i in idxs]):
                ws = list(base)
                loss = 0.0
                for i, a in zip(idxs, alts):
                    ws[i] = lines[i][a][0]
                    loss += lines[i][0][1] - lines[i][a][1]
                if M.check(" ".join(ws).lower()) and (best is None or loss < best[0]):
                    best = (loss, ws, idxs)
        if best:
            break
    if best is None:
        return None
    return {"words": best[1], "changed_lines": [i + 1 for i in best[2]], "score_loss": round(best[0], 3)}


if __name__ == "__main__":
    for path in sys.argv[1:]:
        res = read_plate(cv2.imread(path))
        print(path)
        if not res["ok"]:
            print("  FAILED:", res["error"]); continue
        for i, (w, m) in enumerate(zip(res["words"], res["margins"])):
            flag = "" if m > 0.05 else "   <- low confidence, check"
            alts = ", ".join(f"{a}" for a, _ in res["alternatives"][i][1:])
            print(f"  {i + 1:2d} {w:<9} margin {m:.3f}  (next: {alts}){flag}")
        print("  checksum:", "VALID" if res["checksum_valid"] else "INVALID",
              f"| {res['seconds']} s | flipped={res['flipped']}")
        if res.get("suggestion"):
            print("  suggestion:", res["suggestion"])
