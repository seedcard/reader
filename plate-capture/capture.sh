#!/bin/bash
# plate-capture: camera test for reading Seed Hammer plates on a Pi Zero + OV5647.
# Saves photos to the SD card's boot partition so a laptop can read them.
#
# Usage (log in with keyboard + HDMI monitor, then):
#   bash /boot/firmware/plate-capture/capture.sh            # interactive: preview, Enter = photo
#   bash /boot/firmware/plate-capture/capture.sh burst      # timed: one photo every 4 s, 30 photos
#   bash /boot/firmware/plate-capture/capture.sh burst 8 20 # every 8 s, 20 photos
#
# USE DUMMY SEEDS ONLY. Photos are stored unencrypted on the card.

set -u

# Boot partition is /boot/firmware on Bookworm and later, /boot on older images.
if [ -d /boot/firmware ] && mountpoint -q /boot/firmware; then
  BOOT=/boot/firmware
else
  BOOT=/boot
fi

OUT="$BOOT/plate-captures/$(date +%Y%m%d-%H%M%S)"
sudo mkdir -p "$OUT"

# Pick the camera tool: rpicam-still (current) or libcamera-still (older Bookworm).
if command -v rpicam-still >/dev/null 2>&1; then
  CAM=rpicam-still
elif command -v libcamera-still >/dev/null 2>&1; then
  CAM=libcamera-still
else
  echo "No camera tool found (rpicam-still / libcamera-still). Is this Raspberry Pi OS?"
  exit 1
fi

# Check a camera is detected before going further.
if ! $CAM --list-cameras 2>&1 | grep -qi "ov5647\|imx\|available cameras"; then
  echo "No camera detected. Check the ribbon cable (contacts facing the board) and"
  echo "that config.txt has camera_auto_detect=1 (the default)."
  $CAM --list-cameras
  exit 1
fi
$CAM --list-cameras 2>&1 | head -5

# Full sensor resolution of the OV5647; JPEG quality 95 keeps fine stroke detail.
COMMON=(--width 2592 --height 1944 --quality 95 --nopreview --immediate)

MODE="${1:-interactive}"

if [ "$MODE" = "burst" ]; then
  EVERY="${2:-4}"
  COUNT="${3:-30}"
  echo "Burst: $COUNT photos, one every $EVERY s, into $OUT"
  echo "Move the plate between shots: closer/further, tilt, different light."
  for i in $(seq -w 1 "$COUNT"); do
    echo "  photo $i in 2 s..."
    sleep 2
    sudo $CAM "${COMMON[@]}" -o "$OUT/plate_$i.jpg" 2>/dev/null && echo "  saved plate_$i.jpg"
    sleep $(( EVERY > 2 ? EVERY - 2 : 0 ))
  done
else
  echo "Interactive mode. A live preview shows on the HDMI monitor."
  echo "Fill the frame with the plate. Press Enter to take a photo, type q then Enter to quit."
  n=0
  while true; do
    # Preview runs until Enter, then captures one still.
    n=$((n+1))
    f=$(printf "%s/plate_%02d.jpg" "$OUT" "$n")
    sudo $CAM --width 2592 --height 1944 --quality 95 -t 0 --keypress -o "$f" 2>/dev/null
    if [ -f "$f" ]; then echo "  saved $(basename "$f")"; fi
    read -r -p "Enter = next photo, q = quit: " ans
    [ "$ans" = "q" ] && break
  done
fi

sync
echo "Done. Shut down (sudo poweroff), put the card in your laptop, and look in"
echo "  plate-captures/$(basename "$OUT")  on the boot partition."
