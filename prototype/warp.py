import cv2, numpy as np
L, S = 1580, 1000          # canonical hole-rectangle size in px
PAD = 60                   # include a margin beyond the holes

def warp(img, quad, flip=False):
    q = np.asarray(quad, np.float32)
    if flip:
        q = q[[2, 3, 0, 1]]
    dst = np.float32([[PAD, PAD], [PAD + L, PAD], [PAD + L, PAD + S], [PAD, PAD + S]])
    M = cv2.getPerspectiveTransform(q, dst)
    return cv2.warpPerspective(img, M, (L + 2 * PAD, S + 2 * PAD), flags=cv2.INTER_AREA)
