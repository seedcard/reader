"""Per-photo fine alignment using content that is identical on every plate:
the line numbers ' 1'..'12' (Seed Hammer wordColumn format). The seed words are
NOT used here, so this works on unknown plates."""
import json
import os
import cv2
import numpy as np
from scipy.optimize import minimize
from calibrate import render_lines

LAYOUT = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "layout.json")))


def number_lines(n):
    return [f"{i + 1:2d}" for i in range(n)]


def align(smap, layout=LAYOUT):
    lines = number_lines(layout["lines"])
    p0 = np.array([layout["x0"], layout["y0"], layout["ux"], layout["uy"]])

    def score(p):
        r = render_lines(smap.shape, lines, *p)
        return float((r * smap).sum() / (np.sqrt((r * r).sum()) + 1e-6))
    best = (-1, p0)
    for dx in range(-48, 49, 6):
        for dy in range(-36, 37, 6):
            p = p0 + [dx, dy, 0, 0]
            s = score(p)
            if s > best[0]:
                best = (s, p)
    res = minimize(lambda p: -score(p), best[1], method="Nelder-Mead",
                   options={"xatol": 0.05, "fatol": 1e-4, "maxiter": 400})
    p = res.x
    # keep scale near calibration (numbers alone constrain it weakly horizontally)
    p[2] = 0.5 * p[2] + 0.5 * p0[2]
    return p, -res.fun
