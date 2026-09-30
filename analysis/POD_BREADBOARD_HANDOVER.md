# Handover: Newhaven OLED breadboard test on a Daisy Pod

*Written 2026-09-30 for a new, separate firmware repo. Source of the decisions below:
`analysis/REV2_OLED_PLAN.md` §11 in the PCB_Analysis-Isolated_Screen repo.*

Copy this file, the Newhaven datasheet PDF (`NHD-2.7-12864WDW3-3.pdf`), and Trey's pin
list (`OLED_Pin_Connects_to_Newhaven.txt`) into the new repo's `docs/` folder.

---

## 1. What we are doing and why

**Project:** WavetableController, a Daisy Seed based synth controller (Trey's board).
Rev 1 uses a HiLetgo 2.42" SSD1309 OLED module over I2C. Its on-board boost converter
causes audible coil whine and couples noise into the audio path. Rev 2 replaces it.

**New screen:** Newhaven **NHD-2.7-12864WDW3** — 2.7" 128×64 white OLED module,
**SSD1322** controller (16-level grayscale), **4-wire SPI**, 1×20 pin 2.54 mm header.
It is a module on its own PCB, not bare glass.

**This phase:** prove the screen works with the Daisy platform before any PCB changes.
Concretely:

1. Wire the module to a **Daisy Pod** on a breadboard.
2. Write a small libDaisy program that initialises the SSD1322 over SPI and draws
   something recognisable (text / rectangle / test pattern).
3. Confirm the SPI pin assignment that the rev-2 board will use, unchanged.

The existing firmware's SSD1309 driver does **not** carry over. SSD1322 is a different
command set and a 4-bit-per-pixel framebuffer. libDaisy has no SSD1322 driver; its
`src/dev/oled_ssd1327.h` (also 4-bit grayscale) is the closest reference.

**Deliberate constraint:** the screen's five signal pins are **identical on the Pod and on
the rev-2 PCB**. The screen is the new/complex element, so it keeps fixed pins and the
simple things (encoders, buttons) move around it on the board. Do not "just use any free
pin" on the Pod — use the table in §3.

---

## 2. Power for this test (decided)

**Default jumpers, everything from 3.3 V.** Module as shipped: R4 closed, R5 open,
R7 open. Pin 2 (VDD) gets 3.3 V; the module's on-board boost makes the panel voltage.
Pins 3 and 15 stay open. Pin 18 (/SHDN) stays open (internally pulled high → boost on).

Datasheet (p.6, Default Jumper Setting): VDD 3.0–3.5 V, **IDD 345 mA typ / 375 mA max
at 100 % pixels on**.

We could not find a published current limit for the Seed's 3V3 output (its datasheet
doesn't state one). To keep the test safe regardless:

- Power the Pod from a **USB wall adapter ≥ 1 A**, not a laptop USB port (500 mA budget
  is already exceeded by Seed + Pod + screen).
- **Do not run the all-pixels-on test (0xA5).** That is the 375 mA case. Normal UI
  content (10–30 % pixels) draws roughly proportionally less.
- **Start with master contrast reduced**: command `0xC7` with data `0x03` (¼ output)
  instead of the datasheet's `0x0F`. Raise later once current is known.
- Draw text / outlines, not filled screens.
- Feel the Seed's regulator after a minute. Warm is fine; too hot to hold is stop.
- Decouple pins 2→1 at the header: 100 nF + 10–100 µF. The boost pulls current in bursts
  and breadboard rails are poor.

Later (not this test): jumper option #2 feeds the panel from an external 14.5–15.5 V on
pin 15 and disables the boost. That is the rev-2 noise fix; it is a separate experiment.

---

## 3. Wiring: Newhaven module → Daisy Pod (20 pins)

From the datasheet serial-interface pin table (p.4) and interface-select table (p.5).
Seed pin = the 40-pin physical numbering on the Seed / Pod headers.

| Module pin | Symbol | Connect to | Notes |
|---|---|---|---|
| 1 | VSS | GND | |
| 2 | VDD | **3.3 V** (Seed pin 38, 3V3_D) | + decoupling caps, see §2 |
| 3 | NC (BC_VDD) | open | |
| 4 | D/C | **D11** = Seed pin 12 (PB8) | 0 = command, 1 = data |
| 5 | VSS | GND | |
| 6 | VSS | GND | |
| 7 | SCLK | **D8** = Seed pin 9 (PG11, SPI1_SCK) | |
| 8 | SDIN | **D10** = Seed pin 11 (PB5, SPI1_MOSI) | |
| 9 | NC | open | |
| 10 | VSS | GND | |
| 11 | VSS | GND | |
| 12 | VSS | GND | |
| 13 | VSS | GND | |
| 14 | VSS | GND | |
| 15 | NC (VCC) | open | (15 V input, only with jumper option #2) |
| 16 | /RES | **D12** = Seed pin 13 (PB9) | active low; optional 10 k pull-down to GND |
| 17 | /CS | **D7** = Seed pin 8 (PG10, SPI1_NSS) | active low |
| 18 | /SHDN | open | internally pulled high |
| 19 | BS1 | GND | BS1 = 0, BS0 = 0 → 4-wire SPI |
| 20 | BS0 | GND | |

No pull-up resistors are needed (SPI is push-pull). Nothing above 3.3 V anywhere.

**These five pins are the rev-2 board assignment too:** D7 /CS, D8 SCLK, D10 SDIN,
D11 D/C, D12 /RES. On the board, /ENCR_A, /ENCR_B and /ENCL_CLICK move off D7/D8/D10
to make room.

---

## 4. Daisy Pod pin usage (Pod Rev 3/4 on Seed Rev 3/4)

From libDaisy `src/daisy_pod.cpp`, `src/daisy_seed.h`, `src/per/uart.cpp`.
Seed digital pin numbering: D0–D14 = physical pins 1–15; D15–D30 = physical pins 22–37.

### Used by the Pod

| libDaisy | STM32 | Seed pin | Pod function |
|---|---|---|---|
| D13 | PB6 | 14 | Encoder click (also USART1_TX, unused: no MIDI out) |
| D14 | PB7 | 15 | MIDI in (USART1_RX) |
| D15 | PC0 | 22 | Knob 2 (ADC) |
| D17 | PB1 | 24 | LED 2 red |
| D18 | PA7 | 25 | LED 1 blue |
| D19 | PA6 | 26 | LED 1 green |
| D20 | PC1 | 27 | LED 1 red |
| D21 | PC4 | 28 | Knob 1 (ADC) |
| D23 | PA4 | 30 | LED 2 blue |
| D24 | PA1 | 31 | LED 2 green |
| D25 | PA0 | 32 | Encoder B |
| D26 | PD11 | 33 | Encoder A |
| D27 | PG9 | 34 | Button 1 |
| D28 | PA2 | 35 | Button 2 |
| — | — | 16–19 | Audio in/out L/R (codec) |
| D29 / D30 | PB14 / PB15 | 36 / 37 | USB D− / D+ |

Fixed: pins 20 and 40 GND, 21 3V3_A, 38 3V3_D, 39 VIN.

### Free on the Pod

| libDaisy | STM32 | Seed pin | Note |
|---|---|---|---|
| D0 | PB12 | 1 | USB_ID, usable GPIO |
| D1–D6 | PC11, PC10, PC9, PC8, PD2, PC12 | 2–7 | SDMMC pins (no SD slot on Pod) |
| **D7** | **PG10** | 8 | **SPI1_NSS → screen /CS** |
| **D8** | **PG11** | 9 | **SPI1_SCK → screen SCLK** |
| D9 | PB4 | 10 | SPI1_MISO (unused; screen is write-only) |
| **D10** | **PB5** | 11 | **SPI1_MOSI → screen SDIN** |
| **D11** | **PB8** | 12 | **→ screen D/C** |
| **D12** | **PB9** | 13 | **→ screen /RES** |
| D16 | PA3 | 23 | free (ADC-capable) |
| D22 | PA5 | 29 | free (3.3 V-only pin) |

The Pod's knobs, buttons, encoder, LEDs and MIDI are all untouched by the screen wiring.

---

## 5. SSD1322 / firmware facts needed to write the program

### libDaisy transport already fits

`libDaisy/src/dev/oled_ssd130x.h` contains `SSD130x4WireSpiTransport`. Its **defaults are
exactly our pins**: SPI1, SCLK PG11 (D8), MOSI PB5 (D10), NSS PG10 (D7), hardware NSS,
TX-only, 8-bit, mode 0. Only `pin_config.dc` and `pin_config.reset` need overriding to
PB8 (D11) and PB9 (D12). Its `SendCommand()` / `SendData()` handle the D/C line. Reuse it;
write only the SSD1322 init and framebuffer code. Set `baud_prescaler` to `PS_32` or
slower to start (few MHz); SSD1322 SPI limit is ~10 MHz.

### Reset timing (datasheet p.15)

/RES low ≥ 200 µs → high → wait ≥ 200 µs → send commands. (The libDaisy transport's
`Init()` does 10 ms each side, which is fine.)

### Init sequence (datasheet p.15, Newhaven's own routine, verbatim)

```
0xAE              display OFF
0xB3 0x91         clock divide / oscillator
0xCA 0x3F         MUX ratio 64
0xA2 0x00         display offset
0xAB 0x01         function select: internal VDD regulator
0xA0 0x16 0x11    re-map (nibble remap + dual COM mode)
0xC7 0x0F         master contrast   ← use 0x03 for the first test (see §2)
0xC1 0x9F         contrast current
0xB1 0xF2         phase length
0xBB 0x1F         pre-charge voltage
0xB4 0xA0 0xFD    VSL / display enhancement
0xBE 0x04         VCOMH
0xA6              normal display
0xAF              display ON
```

Then to write pixels:

```
0x15 0x1C 0x5B    column address window 28..91
0x75 0x00 0x3F    row address window 0..63
0x5C              write RAM, then stream data bytes
```

### Framebuffer format (derived from the datasheet mechanical drawing, Detail A; verify
against Newhaven's example code at github.com/newhavendisplay before trusting it)

- The SSD1322 has 480 segments × 128 rows of RAM; this panel uses 256 segments × 64 rows,
  mapped at segments 112–367 → column addresses 28–91 (`0x1C`–`0x5B`). Each column address
  is 4 segments = 2 bytes.
- The panel wires **2 segments per visible pixel** (drawing: "Segment 112,113 = Column
  128", "Segment 366,367 = Column 1"). So one **byte = one pixel**, both nibbles the same
  4-bit grey value. `0xFF` = full white, `0x00` = off.
- Frame = 64 rows × 128 bytes = **8192 bytes**. Send it as data after `0x5C`.
- Note the segment order is reversed relative to column number in the drawing (segment
  112 = column 128). The `0xA0 0x16` remap in the init handles orientation; if the image
  comes out mirrored, that's the byte to change (bit A[1] column remap, A[4] COM scan).

### Other commands worth knowing (p.8–10)

- `0xA4` all off / `0xA5` all on (avoid, see §2) / `0xA6` normal / `0xA7` inverse.
- `0xFD 0x12` unlock (default is unlocked; `0xFD 0x16` locks).
- Full SSD1322 datasheet: http://www.newhavendisplay.com/app_notes/SSD1322.pdf

---

## 6. Suggested test program steps

1. Init transport (pins above), run reset + init with master contrast `0x03`.
2. Clear RAM: set window, `0x5C`, send 8192 × `0x00`.
3. Draw a 1-pixel border rectangle and a diagonal line. Confirms orientation, window
   bounds, and byte→pixel mapping in one image.
4. Draw text (port the 6×8 font from libDaisy's `oled_ssd130x` / `hid/disp` or Newhaven's
   example).
5. Only after the above: brief grayscale ramp (16 bars) at low master contrast.
6. Use Pod Button 1 to toggle display ON/OFF (`0xAF`/`0xAE`) and Knob 1 for contrast
   (`0xC1 n`) — cheap way to explore current draw with a meter on the 3.3 V line.

Suggested repo layout (standard Daisy):

```
<repo>/
  libDaisy/            git submodule: https://github.com/electro-smith/libDaisy
  PodOledTest/
    PodOledTest.cpp
    Makefile           TARGET=PodOledTest, CPP_SOURCES=PodOledTest.cpp,
                       LIBDAISY_DIR=../libDaisy, include $(LIBDAISY_DIR)/core/Makefile
  docs/                this file + datasheet + Trey's pin list
  .vscode/             copy from electro-smith/DaisyExamples
```

Toolchain: Electro-Smith's Daisy Toolchain installer (arm-none-eabi-gcc, make,
dfu-util, openocd) + VS Code C/C++ and Cortex-Debug extensions. Flash with
`make program-dfu` (Seed in DFU: hold BOOT, press RESET, release BOOT).

---

## 7. What this test is NOT

- Not a noise test. The boost converter is running in this configuration; noise
  evaluation needs jumper option #2 (external 15 V) and is a later experiment.
- Not the final driver. Once pixels are proven, the driver gets written properly
  (DMA, framebuffer class, libDaisy `OledDisplay` template) in the main firmware.

## 8. Open items carried from the plan

- 15 V supply scheme for the rev-2 board (adapter → bridge gives ~14.3 V, below the
  module's 14.5 V minimum).
- Whether the LED-drive redesign frees Seed pins (would give back two ADCs).
- /CS on D7: hardware NSS vs software-driven GPIO. Same pin either way; firmware choice.
- Seed 3V3 output current limit: unverified. If a datasheet copy is available, check it.
