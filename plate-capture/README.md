# plate-capture: Pi camera test for Seed Hammer plates

Takes full-resolution photos of an engraved plate with the SeedSigner camera, so we can see
whether the Pi camera (fixed focus, OV5647) and your lighting are good enough to read the words.

**Dummy seeds only.** Photos are saved unencrypted to the card.

## What you need

- A spare microSD card (not your SeedSigner card)
- The Pi Zero + camera from your SeedSigner (the LCD hat can stay on, it just won't be used)
- A mini-HDMI monitor cable, a micro-USB OTG adapter and a USB keyboard, for interactive mode
- A laptop with Raspberry Pi Imager

## 1. Flash the card

1. In Raspberry Pi Imager choose **Raspberry Pi Zero** as the device and
   **Raspberry Pi OS Lite (32-bit)** as the OS.
2. Open **Edit settings** and set a username and password. Wi-Fi isn't needed: the Pi Zero v1.3 has none.
3. Write the card.

## 2. Copy the kit

1. Re-insert the card in your laptop. A small partition called `bootfs` appears.
2. Copy the whole `plate-capture` folder onto it, so you have `bootfs/plate-capture/capture.sh`.
3. Eject the card.

## 3. Take photos

Put the card in the Pi, connect the monitor and keyboard, power on, wait for the first boot to
finish (it may reboot once), and log in.

**Interactive mode** shows a live preview on the monitor; press Enter to take each photo:

    bash /boot/firmware/plate-capture/capture.sh

**Burst mode** needs no monitor once started: it takes a photo every 4 seconds, 30 photos:

    bash /boot/firmware/plate-capture/capture.sh burst

## What to shoot (10–20 photos is plenty)

- **Distance:** plate filling about 60 %, 80 % and 100 % of the frame (this finds the focus limit)
- **Light:** window light, a desk lamp from the side, a desk lamp from above, a lamp behind a sheet of paper
- **Angle:** flat on, and tilted about 15°
- **Background:** dark surface and light surface

Then run `sudo poweroff`, put the card in your laptop and send the photos from
`bootfs/plate-captures/<date-time>/`.

## If the photos are blurry up close

The OV5647 has a fixed-focus lens set for roughly arm's length. On most modules the lens
can be turned a little anticlockwise (with tweezers or a lens tool) to focus closer. That also
changes QR scanning distance, so only try this after we've seen the photos.
