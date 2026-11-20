import cv2, numpy as np

def stroke_map(warped):
    """Polarity-free engraving map: how far each pixel departs from the local
    steel background, normalised by local contrast. Bright or dark letters
    both come out bright."""
    g = cv2.cvtColor(warped, cv2.COLOR_BGR2GRAY).astype(np.float32)
    bg = cv2.medianBlur(g.astype(np.uint8), 41).astype(np.float32)
    d = np.abs(g - bg)
    d = cv2.GaussianBlur(d, (3, 3), 0)
    # local normalisation so faint and strong areas compare
    scale = cv2.GaussianBlur(d, (0, 0), 60) + 2.0
    return np.clip(d / scale / 4.0, 0, 1)
