"""One-time layout calibration from a plate whose words are known (dummy seed).

Fits the text grid in the canonical (hole-aligned) view: x0, y0 = top-left of
the first line's character cell 0; ux, uy = pixels per font unit. Each line is
"%2d WORD" (Seed Hammer's wordColumn format), lines one font-height apart.
Writes layout.json, which the reader then uses for every plate of this design.
"""
import json
import os
import sys
import cv2
import numpy as np
from scipy.optimize import minimize

from font import draw_text
from holes import find_holes
from strokes import stroke_map
from warp import warp


def render_lines(shape, lines, x0, y0, ux, uy, thick=5, blur=3):
    canvas = np.zeros(shape, np.float32)
    for i, text in enumerate(lines):
        draw_text(canvas, text, x0, y0 + i * 9 * uy, ux, uy, thick)
    return cv2.GaussianBlur(canvas, (0, 0), blur) if blur else canvas


def fit(smap, lines, p0):
    def neg(p):
        r = render_lines(smap.shape, lines, *p)
        return -float((r * smap).sum() / (np.sqrt((r * r).sum()) + 1e-6))
    # coarse search over offsets first, then refine everything
    best = None
    for dx in range(-40, 41, 8):
        for dy in range(-40, 41, 8):
            p = (p0[0] + dx, p0[1] + dy, p0[2], p0[3])
            v = neg(p)
            if best is None or v < best[0]:
                best = (v, p)
    res = minimize(neg, best[1], method="Nelder-Mead",
                   options={"xatol": 0.05, "fatol": 1e-4, "maxiter": 600,
                            "initial_simplex": None})
    return res.x, -res.fun


def main(words, photos, flips):
    lines = [f"{i + 1:2d} {w.upper()}" for i, w in enumerate(words)]
    results = []
    for path, flip in zip(photos, flips):
        img = cv2.imread(path)
        quad, _ = find_holes(img)
        smap = stroke_map(warp(img, quad, flip))
        p, score = fit(smap, lines, (170, 32, 9.0, 9.3))
        print(path, np.round(p, 2), round(score, 1))
        results.append(p)
    p = np.median(np.array(results), 0)
    layout = {"x0": float(p[0]), "y0": float(p[1]), "ux": float(p[2]), "uy": float(p[3]),
              "lines": len(words), "word_col": 3, "max_letters": 8,
              "note": "canonical view from warp.py (holes -> 1580x1000 + 60 px pad)"}
    json.dump(layout, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "layout.json"), "w"), indent=2)
    print("layout", layout)


if __name__ == "__main__":
    # Calibration plate: the DUMMY wallet in ../testdata (never funded).
    here = os.path.dirname(os.path.abspath(__file__))
    td = os.path.join(here, "..", "testdata")
    words = "inject old member artwork pottery sunset weasel whip plug live you fan".split()
    photos = [os.path.join(td, f) for f in ("dummy-01-window-light.jpg", "dummy-02-direct-sun.jpg",
                                            "dummy-03-angled-cloth.jpg", "dummy-04-rotated.jpg")]
    main(words, photos, [False, False, False, True])
