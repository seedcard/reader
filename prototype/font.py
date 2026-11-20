"""Seed Hammer 'constant' engraving font (public domain, from seedhammer/font/constant).

Each glyph is a polyline in a 6 x 9 unit cell (advance 6, line height 9,
baseline at y=8). Glyphs sit side by side in the SVG, so glyph k is offset
by 6*k units; we subtract that to get cell-local coordinates.
"""
import os
import re
import cv2
import numpy as np

NAMES = {"one": "1", "two": "2", "three": "3", "four": "4", "five": "5", "six": "6",
         "seven": "7", "eight": "8", "nine": "9", "zero": "0", "slash": "/"}


def load(path=os.path.join(os.path.dirname(__file__), "constant.svg")):
    svg = open(path).read()
    glyphs = {}
    for m in re.finditer(r'<(polyline|line)\s+id="([^"]+)"[^>]*?(?:points="([^"]+)"|x1="([^"]+)" y1="([^"]+)" x2="([^"]+)" y2="([^"]+)")', svg):
        kind, gid = m.group(1), m.group(2)
        if kind == "polyline":
            nums = [float(v) for v in re.split(r"[ ,]+", m.group(3).strip())]
            pts = np.array(nums, np.float32).reshape(-1, 2)
        else:
            pts = np.array([[float(m.group(4)), float(m.group(5))],
                            [float(m.group(6)), float(m.group(7))]], np.float32)
        ch = gid if len(gid) == 1 else NAMES.get(gid)
        if ch is None:
            continue
        off = 6 * np.floor(pts[:, 0].min() / 6)
        pts[:, 0] -= off
        glyphs[ch] = pts
    return glyphs


GLYPHS = load()


def draw_text(canvas, text, x, y, ux, uy, thick, value=1.0):
    """Draw text into canvas with the cell top-left of char 0 at (x, y);
    ux, uy = pixels per font unit horizontally / vertically."""
    for i, ch in enumerate(text):
        g = GLYPHS.get(ch)
        if g is None:
            continue
        p = np.stack([x + (i * 6 + g[:, 0]) * ux, y + g[:, 1] * uy], 1)
        cv2.polylines(canvas, [np.round(p * 4).astype(np.int32)], False, value,
                      thick, cv2.LINE_AA, shift=2)
    return canvas


def glyph_image(ch, ux, uy, thick, blur):
    """A single glyph cell rendered at the given scale, for template matching."""
    w, h = int(round(6 * ux)), int(round(9 * uy))
    img = np.zeros((h, w), np.float32)
    draw_text(img, ch, 0, 0, ux, uy, thick)
    if blur:
        img = cv2.GaussianBlur(img, (0, 0), blur)
    return img
