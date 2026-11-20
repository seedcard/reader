# SeedCard plate reader

Reads the 12 seed words off an engraved SeedCard plate with a camera, so a SeedSigner can load
a seed from the steel plate itself, with no SeedQR card.

The plates come from the [SeedCard engraver](https://github.com/seedcard/engraver): Seed Hammer
SH01 credit-card plates with 12 words in one column, the master fingerprint, and no SeedQR
(engraved SeedQRs are often hard to scan off steel).

> **Status: laptop prototype.** It reads the test photos correctly. It has not yet run on a
> Pi camera or a Pi Zero, and it is **not** for real seeds yet.

## What's here

| Folder | What it is |
|---|---|
| [`prototype/`](prototype/) | The reader in Python (OpenCV): finds the plate by its corner holes, straightens it, reads each letter against Seed Hammer's own font, picks the BIP39 words and checks the checksum |
| [`plate-capture/`](plate-capture/) | Camera test kit for a Pi Zero with the SeedSigner camera: takes full-resolution photos onto the SD card |
| [`testdata/`](testdata/) | Photos of a **dummy** plate (never funded) and the words they should read as |

## How it reads a plate

1. **Find the plate** by its four corner holes: inside each hole is background, around it steel.
2. **Straighten** it to a fixed view, both ways up.
3. **Stroke map:** engraving shows bright or dark depending on the light; this makes both bright.
4. **Align** the text grid on the line numbers 1–12, which are the same on every plate.
5. **Read** each letter cell against Seed Hammer's font; pick the best BIP39 word per line
   (empty cells after a short word count too).
6. **Checksum:** if it fails, show the closest alternatives. A suggested fix is only a
   suggestion: the user confirms every word against the plate.

## Where it's going

1. Pi camera photos with `plate-capture` → test and tune (focus, light).
2. Fast enough for a Pi Zero.
3. A **minimal SeedSigner fork**: official SeedSigner plus one added option, "Read SeedCard
   plate", under Load a seed. It tracks official releases, has a reproducible build with published
   hashes, and shrinks to a plate template if SeedSigner releases its own handwritten-word reader.
   Contributing plate support upstream would be better still.

The plan for the whole SeedCard system is in the engraver's
[TODO.md](https://github.com/seedcard/engraver/blob/seedcard/TODO.md).

## Safety

- Photograph **dummy plates only.** A photo of a real plate is a copy of the seed.
- The reader never decides for you: every word is shown for confirmation before use.
