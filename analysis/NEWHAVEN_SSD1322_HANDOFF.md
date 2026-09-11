# Handoff: BAKER firmware — HiLetgo SSD1309 (I2C) → Newhaven NHD-2.7-12864WDW3 (SSD1322, SPI)

Self-contained brief for whoever does the port (human or Claude session). Facts
verified against the NHD-2.7-12864WDW3 datasheet rev.6, Newhaven's official example
code (github.com/NewhavenDisplay/NHD-2.7-12864WD_Example), libDaisy `daisy_pod.cpp`,
and BAKER branch `CUZ_AUG_WRAPUP`. Hardware: Daisy Pod + breadboard.

## The port is three changes plus a reset pulse

All UI screens draw through one class — `OledPager` (`src/ui/oled_pager.{h,cpp}`,
a `OneBitGraphicsDisplayImpl` with 1bpp page-layout buffers) — so **no screen code
changes**. Rework that one class:

1. **Bus: I2C → 4-wire SPI.** The SSD1322 has no I2C mode. Old in-band prefix bytes
   (`0x00` cmd / `0x40` data) become a **D/C GPIO level** (low = command, high = data).
   SPI mode 0, MSB first, TX-only, **max ~3.3 MHz** (spec) — full frame ≈ 20 ms,
   same as the old I2C path, so no timing budget changes.
2. **Init: new sequence** (below). Also delete the vestigial
   `OledDisplay<SSD130xI2c128x64Driver>` from `main.cpp:39,103-117` — with no I2C
   device it just times out at boot; `OledPager` owns init now.
3. **Frame format: 1 bit/pixel → 1 byte/pixel.** Keep the existing 1bpp buffers;
   expand during transfer: each bit → `0xFF` or `0x00` (the byte's two nibbles are the
   panel's two horizontally-doubled controller pixels). Frame grows 1,024 → 8,192 B.
   Per frame send the window once — `0x15 0x1C 0x5B`, `0x75 0x00 0x3F`, `0x5C` —
   then stream all 8,192 bytes linearly. **Column origin is 0x1C, not 0.**

**Reset pulse** (the HiLetgo did this onboard; now firmware must): drive /RES low
**≥ 200 µs**, high, wait **≥ 200 µs**, then init. `0xAE`/`0xAF` display off/on are the
same opcodes as the SSD1309, so `SetDisplayOn` logic ports unchanged.

Init sequence (datasheet p.15, verbatim — cmd, then data bytes):
`AE · B3 91 · CA 3F · A2 00 · AB 01 · A0 16 11 · C7 0F · C1 9F · B1 F2 · BB 1F ·
B4 A0 FD · BE 04 · A6 · AF`
(To rotate 180°: `A0 04 11`. Contrast lives at `C1`, not `0x81`.)

## Pins (Daisy Pod + BAKER breadboard rig)

SPI1 is fixed at SCK = D8, MOSI = D10; BAKER currently has controls on those pins.
Three wires + three code lines move:

| Daisy pin | Today | Change |
|---|---|---|
| D7 | Ext encoder A (`controls.cpp:47`) | → **D11**; D7 becomes OLED **/CS** |
| D8 | Ext encoder B (`controls.cpp:48`) | → **D12**; D8 becomes OLED **SCLK** |
| D9 | Right-shift button (`controls.cpp:52`) | stays (MISO unused — display is write-only) |
| D10 | Pod encoder click (`main.cpp:381`) | → **D0**; D10 becomes OLED **SDIN** |
| D11/D12 | old I2C (`oled_pager.cpp:17-18`, `main.cpp:114-115`) | freed |
| D29 / D30 | free | OLED **D/C** / **/RES** |

(Pod itself claims D13, D15, D17–D21, D23–D28 + SD + audio — don't touch those.)

## 20-pin header wiring

| Pin | → | Pin | → |
|---|---|---|---|
| 1, 5, 6, 10–14 (VSS) | GND | 15 VCC | open (default) / **15.0 V** (Option #2) |
| 2 VDD | 3.3 V (see power note) | 16 /RES | D30 |
| 3 BC_VDD | open | 17 /CS | D7 |
| 4 D/C | D29 | 18 /SHDN | open |
| 7 SCLK | D8 | 19 BS1 | **GND** |
| 8 SDIN | D10 | 20 BS0 | **GND** (BS1=BS0=0 → 4-wire SPI) |

Decoupling at the header: 100 nF + ≥10 µF on VDD (Option #2: also 100 nF + ≥100 µF on
VCC). Common ground everywhere.

**Power note:** as shipped (jumper R4), the module runs from single 3.3 V but pulls
**up to 375 mA** through its onboard boost — fine for first light, but power it from an
external ≥500 mA 3.3 V supply, **never the Seed's 3V3 pin**. The end-state is Jumper
Option #2 (move the 0 Ω from R4 to R7, datasheet p.5): boost bypassed, pin 15 = 15.0 V
external (spec 14.5–15.5 V, ~70 mA), VDD then only ~µA (Pod 3V3 is fine). Sequence
3.3 V up before 15 V, reverse at power-down.

## Bench-debug shortcuts (where the time actually goes)

- First smoke test: after init send **`0xA5`** (all pixels on, no RAM writes). Dark
  panel here = power / reset / BS straps / SPI mode — not your frame code.
- Then a checkerboard: smeared or double-wide squares = column window or nibble order
  (remap `0xA0` bit A[2] = nibble swap).
- Start SPI ~1.6 MHz, raise to ~3.1 MHz once clean.
- Keep the async structure: BAKER's pager sends one chunk per main-loop tick via DMA
  (`dma_in_flight_` gate pattern in `oled_pager.cpp`). Natural chunk = 8 rows = 1 KB,
  8 chunks/frame; window commands at frame start, then D/C stays high all frame.
  DMA buffer must live in `DMA_BUFFER_MEM_SECTION` (like the existing `s_dma_buf_`).
- Don't carry over the old SSD1309 `0xD5`/`0xD9` init tweaks — obsolete lore.

Later, free upgrades the SSD1309 never offered: windowed partial updates
(dirty-rect refresh) and 16-level grayscale (byte-per-pixel already supports it).
