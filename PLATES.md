# Seed Hammer plate geometry

Source: Seed Hammer plate drawing (01.DXF, 02.DXF, 03.DXF, shared on Thingiverse, thing 6635265)
and the engraver code (`backup/backup.go`, Seed Hammer v1.2.1 and later).

## Holes

All plates are 85 mm wide, with R3 corners and Ø3.5 mm holes whose centres are 3 mm in from
the edges.

| Plate | Size (mm) | Holes | Hole centre spacing (mm) | Seed Hammer versions |
|---|---|---|---|---|
| SH01 | 85 × 55 | 4 | 79 × 49 | up to v1.2.x (incl. SeedCard) |
| SH02 | 85 × 85 | 4 | 79 × 79 | all versions; the only size since v1.3.0 |
| SH02, Seed Hammer v2 machine | 85 × 85 | **none** | — | v2 machine (same plate size, no holes, same seed-side layout) |
| SH03 | 85 × 134 | 6 | 79 across; 49 then 79 down (middle pair 52 mm from the top) | up to v1.2.x |

SH03 is an SH01 hole pattern above an SH02 pattern, sharing the middle pair.

## Seed side text (engraver code)

Same on every size and version: Seed Hammer's constant font at 4.1 mm (9 font units, 6-unit
cell width), lines `%2d WORD`, column 1 starting 10 mm from the left edge, words 17–24 at 44 mm,
text at least 3 mm from any edge.

| | SH01 | SH02 / SH03 |
|---|---|---|
| Word column, vertically | centred on the plate height | centred (SH03 shifted 24.5 mm down to clear the middle holes) |
| Fingerprint, key number, version mark | turned 90°, up the left edge | horizontal, 4 mm above the words |
| Title | turned 90°, up the right edge | horizontal, 4 mm below the words |
| SeedQR (standard Seed Hammer) | centred at x = 60 mm | centred at x = 60 mm |

## Check against real photos (SH01, 22 November 2026)

Predicted from the drawing and the code, compared with the calibration fitted on the dummy
plate photos (canonical view: holes → 1580 × 1000 px):

| | Predicted | Fitted |
|---|---|---|
| px per font unit, across | 9.11 | 9.04 |
| px per font unit, down | 9.30 | 9.33 |
| column start | ≈ 191 px | 187 px (0.2 mm) |

So each size's layout can be computed from the drawing and the code, without photo calibration.

## Reader consequences

- Hole finder: look for 79 × 49 (ratio 1.61) and 79 × 79 (square) rectangles; six holes = SH03.
- **Plates without holes** (Seed Hammer v2) and holes hidden by fingers or a holder: register on
  the **text grid** instead: the column of line numbers (1–12 or 1–24, 4.1 mm apart), the fixed
  offset of the words after them, and the fingerprint above. This needs no plate edge or hole, so
  it works for every Seed Hammer seed plate; holes, when found, are a faster and more precise first
  try. On the device, a framing box on the camera screen keeps the search small.
- SH02: the square hole pattern doesn't fix the orientation; try all four and keep the best reading.
- Testing: SH01 on real plates; SH02 on a few real blanks (the size on sale now); SH03 and holeless
  v2 SH02 on plates simulated from the engraver code; a real v2 plate when one is available.
