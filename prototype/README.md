# Plate reader: laptop prototype

Reads the 12 BIP39 words from a photo of a SeedCard plate (Seed Hammer SH01, engraved by
[seedcard/engraver](https://github.com/seedcard/engraver): four corner holes, words in one column,
no SeedQR). Runs on a laptop with Python 3:

    pip install -r requirements.txt
    python3 reader.py photo1.jpg photo2.jpg
    python3 run_tests.py          # every photo in ../testdata against expected.json

**Dummy seeds only.** Nothing here is hardened for real keys yet.

## How it works

1. **holes.py**: finds the four corner holes. For every pixel and hole size it compares the colour
   inside a disc (the background showing through) with a ring just outside (steel), then
   picks the four peaks that form the plate's hole rectangle. A corner test checks that the
   area just past the plate edge isn't steel.
2. **warp.py**: straightens the plate into a fixed 1580 × 1000 px view. Both 180° orientations
   are tried.
3. **strokes.py**: builds a stroke map: how far each pixel departs from the local steel
   colour. Engraving that looks bright or dark both come out bright, so the lighting angle
   doesn't matter.
4. **align.py**: fine-tunes the text grid on the line numbers 1–12. These are the same on
   every plate, so no seed words are needed for this step.
5. **reader.py**: scores every character cell against Seed Hammer's own font
   (`constant.svg`, public domain), picks the best BIP39 word per line (empty cells after a
   short word count too), checks the checksum, and lists the next-best words per line.
   If the checksum fails it suggests the smallest change that passes. That is a **suggestion**
   only: the 4-bit checksum means about 1 in 16 random wrong combinations also pass.
6. **calibrate.py**: one-time fit of the text grid from a plate with known words. The result
   is in `layout.json`, and any plate from the same fork version uses it unchanged.

## Results on the test photos

`python3 run_tests.py`, 20 November 2026:

| Photo | Words | Checksum | Result |
|---|---|---|---|
| dummy-01 window light | 12/12 | valid | pass |
| dummy-02 direct sun | 12/12 | valid | pass |
| dummy-03 angled, on cloth | 12/12 | valid | pass |
| dummy-04 rotated, slight blur | 11/12 (FAN read as PEN) | invalid | pass: caught, suggestion correct |
| dummy-05 too far | not read | invalid | pass: fails safely |

About 9 s per photo on a laptop CPU.

## Known limits / next steps

- **Speed:** about 8.5 s on a laptop CPU. A Pi Zero will be much slower until it's optimised:
  work at half resolution, align the number column with a single template match instead of
  repeated rendering, and narrow the hole search using the on-screen framing guide.
- **Pi camera photos:** not tested yet. Take them with `../plate-capture` and add them to `../testdata`.
- **Letter templates:** drawn from the font geometry. Training them on real crops (the
  engraving often shows as two groove edges) should widen the confidence margins.
- **12-word layout only.** 24-word plates need their own calibration.
