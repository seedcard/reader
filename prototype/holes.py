"""Locate the plate by its four corner holes.

1. Dense hole-likeness map: for each pixel and each radius, compare the colour
   inside a disc (background showing through the hole) with a ring just outside
   it (steel). Letters such as O have steel inside, so they score low.
2. Peaks of that map are hole candidates.
3. Geometric search: four candidates forming a rectangle with the known aspect
   ratio and similar radii, checked by a corner test (outside = background,
   inside = steel).
Returns the four hole centres (full-res px) going round the rectangle, with the
first two forming a long side, plus the hole radius.
"""
import itertools
import cv2
import numpy as np

WORK = 1000
ASPECT = 1.58           # hole rectangle long/short
ASPECT_TOL = 0.22
RADII = (5, 6.5, 8, 10, 12.5, 15, 18)


def _disk(r):
    k = int(np.ceil(r))
    yy, xx = np.mgrid[-k:k + 1, -k:k + 1]
    return (np.hypot(xx, yy) <= r).astype(np.float32)


def _ring(r0, r1):
    k = int(np.ceil(r1))
    yy, xx = np.mgrid[-k:k + 1, -k:k + 1]
    d = np.hypot(xx, yy)
    return ((d >= r0) & (d <= r1)).astype(np.float32)


def hole_map(lab):
    """Return (best score, best radius) per pixel."""
    f = lab.astype(np.float32)
    f2 = f * f
    best = np.zeros(lab.shape[:2], np.float32)
    best_r = np.zeros(lab.shape[:2], np.float32)
    for r in RADII:
        dk = _disk(0.7 * r); dk /= dk.sum()
        rk = _ring(1.3 * r, 1.9 * r); rk /= rk.sum()
        inner = cv2.filter2D(f, -1, dk)
        ring = cv2.filter2D(f, -1, rk)
        ring2 = cv2.filter2D(f2, -1, rk)
        std = np.sqrt(np.maximum(ring2 - ring * ring, 0)).mean(2)
        diff = np.linalg.norm(inner - ring, axis=2)
        s = diff / (1.0 + 0.6 * std)
        m = s > best
        best[m] = s[m]
        best_r[m] = r
    return best, best_r


def peaks(score, radius, n=60):
    dil = cv2.dilate(score, np.ones((9, 9), np.uint8))
    ys, xs = np.where((score == dil) & (score > 3))
    vals = score[ys, xs]
    order = np.argsort(vals)[::-1][:n]
    return np.array([(xs[i], ys[i], radius[ys[i], xs[i]], vals[i]) for i in order],
                    dtype=np.float32).reshape(-1, 4)


def rectangle_fits(c):
    n = len(c)
    if n < 4:
        return []
    pts, rad = c[:, :2], c[:, 2]
    hs = c[:, 3] / max(float(c[:, 3].max()), 1e-6)
    fits = []
    for i, j in itertools.permutations(range(n), 2):
        a, b = pts[i], pts[j]
        v = b - a
        d = float(np.hypot(*v))
        if d < 60:
            continue
        rr = (rad[i] + rad[j]) / 2
        if not 0.008 < rr / d < 0.04:
            continue
        nrm = np.array([-v[1], v[0]]) / d
        exp_k = a + nrm * d / ASPECT
        dk = np.hypot(*(pts - exp_k).T)
        for k in np.where(dk < 0.15 * d)[0]:
            if k in (i, j):
                continue
            side = pts[k] - a
            dl = np.hypot(*(pts - (b + side)).T)
            l = int(np.argmin(dl))
            if l in (i, j, k) or dl[l] > 0.07 * d:
                continue
            ratio = d / float(np.hypot(*side))
            if abs(ratio - ASPECT) > ASPECT_TOL:
                continue
            q = [i, j, l, k]
            qr = rad[q]
            if qr.max() / qr.min() > 1.6:
                continue
            err = dl[l] / d + abs(ratio - ASPECT) * 0.3 - hs[q].min() - 0.3 * hs[q].mean()
            fits.append((err, (a, b, pts[l], pts[k], float(qr.mean()))))
    fits.sort(key=lambda t: t[0])
    return fits[:60]


def _patch(lab, p, rad):
    h, w = lab.shape[:2]
    x, y, r = int(round(p[0])), int(round(p[1])), max(1, int(rad))
    if x - r < 0 or y - r < 0 or x + r >= w or y + r >= h:
        return None
    return lab[y - r:y + r + 1, x - r:x + r + 1].reshape(-1, 3).astype(np.float32).mean(0)


def corner_score(lab, quad, r):
    """Each hole sits near a plate corner. Just inside (between hole and the
    rest of the plate) should be steel, and the two inner samples should agree;
    just outside, past the plate edge, should NOT look like steel."""
    quad = np.asarray(quad, np.float32)
    scores = []
    for idx in range(4):
        p = quad[idx]
        u1 = p - quad[(idx + 1) % 4]; u1 /= np.linalg.norm(u1)
        u2 = p - quad[(idx - 1) % 4]; u2 /= np.linalg.norm(u2)
        steel = [_patch(lab, p - u * 2.2 * r, r * 0.5) for u in (u1, u2)]
        outside = [_patch(lab, p + u * 3.4 * r, r * 0.6) for u in (u1, u2)]
        if any(x is None for x in steel + outside):
            return -1e9
        steel_c = np.mean(steel, 0)
        steel_spread = np.linalg.norm(steel[0] - steel[1])
        for o in outside:
            d = np.linalg.norm(o - steel_c)
            scores.append(min(1.0, d / 12.0) - min(1.0, steel_spread / 25.0))
    return float(np.mean(scores))


def find_holes(img, debug=None):
    h, w = img.shape[:2]
    s = WORK / max(h, w)
    small = cv2.resize(img, (int(w * s), int(h * s)), interpolation=cv2.INTER_AREA)
    lab = cv2.cvtColor(cv2.GaussianBlur(small, (3, 3), 0), cv2.COLOR_BGR2LAB)
    score, radius = hole_map(lab)
    c = peaks(score, radius)
    if debug is not None:
        debug['cands'] = c / [s, s, s, 1]
    fits = rectangle_fits(c)
    if not fits:
        return None
    # combine: corner test (plate edge just outside each hole) and geometry/hole strength
    scored = [(corner_score(lab, f[:4], f[4]), corner_score(lab, f[:4], f[4]) - 6.0 * err, f)
              for err, f in fits]
    sc, _, best = max(scored, key=lambda t: t[1])
    if debug is not None:
        debug['corner'] = sc
    if sc < 0.15:
        return None
    a, b, cc, d, rr = best
    quad = np.array([a, b, cc, d], dtype=np.float32)
    # refine each hole: strongest hole response within a small window
    for i, (x, y) in enumerate(quad):
        R = int(max(3, 1.5 * rr))
        x0, y0 = max(0, int(x) - R), max(0, int(y) - R)
        win = score[y0:int(y) + R + 1, x0:int(x) + R + 1]
        if win.size:
            yy, xx = np.unravel_index(np.argmax(win), win.shape)
            quad[i] = (x0 + xx, y0 + yy)
    quad, r_full = quad / s, rr / s
    return refine_full(img, quad, r_full), r_full


def refine_full(img, quad, r):
    """Re-centre each hole on a local full-resolution crop, rescaled so the hole
    radius is ~10 px, using the same inside-vs-ring hole score."""
    out = quad.copy()
    for i, (x, y) in enumerate(quad):
        R = int(4 * r)
        x0, y0 = int(x) - R, int(y) - R
        if x0 < 0 or y0 < 0 or x0 + 2 * R >= img.shape[1] or y0 + 2 * R >= img.shape[0]:
            continue
        crop = img[y0:y0 + 2 * R, x0:x0 + 2 * R]
        k = 10.0 / r
        small = cv2.resize(crop, None, fx=k, fy=k, interpolation=cv2.INTER_AREA)
        lab = cv2.cvtColor(cv2.GaussianBlur(small, (3, 3), 0), cv2.COLOR_BGR2LAB)
        f = lab.astype(np.float32)
        best, pos = -1, None
        for rr in (8, 9, 10, 11, 12.5):
            dk = _disk(0.75 * rr); dk /= dk.sum()
            rk = _ring(1.2 * rr, 1.7 * rr); rk /= rk.sum()
            sc = np.linalg.norm(cv2.filter2D(f, -1, dk) - cv2.filter2D(f, -1, rk), axis=2)
            c = sc.shape[0] // 2
            m = np.zeros_like(sc); cc = int(1.6 * 10)
            m[c - cc:c + cc, c - cc:c + cc] = 1   # stay near the coarse estimate
            sc = sc * m
            yy, xx = np.unravel_index(np.argmax(sc), sc.shape)
            if sc[yy, xx] > best:
                best, pos = sc[yy, xx], (xx, yy)
        out[i] = (x0 + pos[0] / k, y0 + pos[1] / k)
    return out
