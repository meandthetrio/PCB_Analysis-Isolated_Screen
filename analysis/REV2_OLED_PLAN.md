# Rev 2: OLED Display Redesign — Plan & Discussion Notes

*Compiled 2026-08-12 from design discussion. Companion to the rev-1 analysis reports in this folder.*
*Status: DISCUSSION ONLY — no PCB files have been modified.*

---

## 1. What we're doing and why

**Current state:** One HiLetgo 2.42" SSD1309 OLED module plugs into the 4-pin header J2.
The module is a mini-PCB with the screen glass glued on, plus a boost converter that
generates the panel's ~13V internally from 3.3V.

**Problem:** The boost converter is the noise villain, two ways:

1. **Audible buzz (coil whine):** the booster chops current through a tiny coil tens of
   thousands of times per second. The coil vibrates like a tiny speaker; pitch changes
   with screen content; the steel enclosure acts as a soundboard.
2. **Audio-path noise:** the booster draws power in sharp gulps that travel backward
   into the board's power system, where the audio circuits can pick them up. This is
   not hypothetical — rev 1 carries the scar tissue (a layout-only 10Ω resistor hack
   at the OLED power feed, plus a 470µF capacitor) from debugging exactly this.

**Rev-2 approach ("option B"):** Replace the module with a **bare glass panel** —
Crystalfontz **CFAL12864G-024W** (2.42" 128x64 white, same SSD1309 controller, 31-pin
flex ribbon tail). No boost converter anywhere. The panel's high voltage comes from the
power input, stepped down by a **linear regulator** — a valve, not a chopper. Nothing
switches, so nothing can buzz, and nothing gulps, so nothing couples into the audio.

- Datasheet: https://www.crystalfontz.com/products/document/3707/CFAL12864G024Wv1.1.pdf
- Demo code: https://github.com/crystalfontz/CFAL12864G_and_CFAL12864K

**Does the linear regulator make noise?** Practically none. It never switches — it
throttles ~14V down to 13V continuously and turns the difference into a trivial amount
of heat (no heatsink needed at ~20–50mA). Its intrinsic electrical noise is millionths
of a volt on a wire that only feeds the screen. Linear regulators are what audio
designers use *when they want quiet*. The 15V wall adapter is itself a switcher, but it
lives outside the box, switches steadily (not content-dependent), and its output is
cleaned twice (entry caps, then the regulator) before touching anything.

---

## 2. The power problem (IMPORTANT — the plan's premise needed correcting)

The original option-B brief said "feed the panel from the existing +12V rail; 12.0V is
at the low edge of spec." **Both halves are wrong:**

- **This board has no 12V rail.** Power nets are +9V_FILT, +5V_USB, +3V3_A, +3V3_D.
  The 9V barrel input goes through the Schottky bridge (D2–D5, ~0.7V drop) → ~8.3V.
- **The datasheet specs panel VCC at 12.5V min / 13.0V typ / 13.5V max** (p.7).
  12.0V is *below minimum*, not "the low edge."

**The fix:** change the wall adapter **9V → 15V**, add a **~13.0V linear regulator**
for the screen branch:

```
15V barrel → bridge (−0.7V) → ~14.3V → linear reg → 13.0V → ferrite bead + caps → screen VCC
```

Checked against the board:
- Daisy Seed VIN max is 17V, so 14.3V at the rail is fine (verify against current
  Daisy datasheet rev before committing).
- Dropout budget is only ~1.3V, so it must be a true LDO (AZ1117-ADJ class is fine),
  NOT an LM317 (needs ~2V of headroom).
- Screen draws 15–22mA at 50% pixels (datasheet); budget ~50mA worst case; size the
  regulator ≥150mA and forget about it.
- Don't go to an 18V adapter — bridge output ~17.3V would exceed Daisy's VIN max.
- The bridge makes the jack polarity-agnostic; the adapter swap is a label change +
  the new regulator. Update enclosure power labeling.

**One-way isolation still matters:** even without the booster, the screen's row-scan
current flutters with content at frame-rate harmonics (in the audio band). The ferrite
bead + 100µF at the connector fences that off from the rest of the board.

---

## 3. How the bare panel physically connects

The ribbon on the glass is a thin flex strip with 31 exposed metal fingers — not a
plug. It mates with a surface-mount **ZIF connector** ("zero insertion force") soldered
on the PCB: flip open the latch, slide the ribbon in, close the latch. Screen is
replaceable by unclipping. All support circuitry that used to live on the HiLetgo
mini-board moves onto our PCB, clustered around the ZIF connector.

**Candidate connectors** (31-pos, 0.5mm pitch):
- Hirose FH41-31S-0.5SH (bottom contact)
- TE 3-1734839-1 (top contact)

**⚠ The two genuinely risky steps (neither is circuit design):**

1. **Contact orientation.** The ribbon's contacts must face the connector's contacts.
   The datasheet drawing (p.4) shows the stiffener on the rear face / contacts on the
   viewer face at the tip, but the right connector flavor depends on how the tail folds
   in the enclosure stack. **Buy the panel and BOTH connector variants first, mock the
   fold with real parts against the enclosure, then finalize the footprint.**
2. **Reach.** Usable tail length ≈ 18mm after bend allowances (22.3mm total, keep
   ≥2mm flat off the glass, bend radius ≥1.5mm). The ZIF must sit almost directly
   behind the screen window. **Measure the face-to-board stack height before placing
   anything — this is the go/no-go input for the whole layout.**

Panel mechanicals: glass 60.5 × 37.0 × 2.15mm; active area 55.01 × 27.49mm; viewing
area 57.01 × 28.91mm. Panel mounts to the enclosure face with a bezel/adhesive frame.
Keep the exposed driver ledge on the glass shaded (it's light-sensitive, datasheet
p.11) — a windowed steel face does this naturally.

---

## 4. Complete pin-by-pin wiring table (I2C mode, single screen, address 0x3C)

From the CFAL12864G-024W datasheet pin function table (p.5–6) + application circuit
(p.6), cross-checked against the board's nets. **GND** = plain wire to ground.
**3.3V** = existing +3V3_D rail. **13V** = new regulated screen supply.

| Pin | Goes to | Notes |
|-----|---------|-------|
| 1 | GND | |
| 2 | GND | Main screen ground (VSS) |
| 3–10 | nothing | Leave unconnected (8 pins) |
| 11 | 3.3V | Logic power (VDD). Local caps: 100nF + 2.2µF to GND |
| 12 | 3.3V | Strap BS1=1 … |
| 13 | GND | … strap BS2=0. Together = "speak I2C" |
| 14 | nothing | Leave unconnected |
| 15 | GND | CS# — always enabled |
| 16 | Daisy spare pad (22 or 28) | RES# reset wire + 10k resistor to GND (holds screen in reset until firmware releases it) |
| 17 | GND | D/C# acts as address select → 0x3C, **same address the HiLetgo uses** — firmware address unchanged |
| 18 | GND | R/W# — required low in I2C mode |
| 19 | GND | E/RD# — required low in I2C mode |
| 20 | Daisy pad 12 (I2C_SCL) | Clock — same Daisy pin the HiLetgo SCL uses today |
| 21 | tie to pin 22 | D1+D2 joined… |
| 22 | …and to Daisy pad 13 (I2C_SDA) | …together they are the data line — same Daisy pin as today |
| 23–27 | GND | Unused data pins D3–D7, datasheet says tie low |
| 28 | 1MΩ 1% resistor to GND | IREF brightness-current set. Formula (VCC−3V)/10µA at 13V → 1MΩ |
| 29 | 1µF capacitor to GND | VCOMH reservoir (datasheet lists "C4"=1.0µF — its C3/C4 labeling has a typo; cross-check against Crystalfontz's own breakout for this panel) |
| 30 | 13V | Panel power (VCC). Local caps: 100nF ceramic + ≥100µF bulk to GND |
| 31 | GND | |

**Two parts not on any pin:** 2.2k pull-up resistors from SCL→3.3V and SDA→3.3V.
**Rev 1 has ZERO I2C pull-ups in-design (finding F-027)** — the HiLetgo module was
silently providing them. A bare panel provides nothing. **Without these two resistors,
rev 2 is dead on arrival.**

**Sanity totals:** 3 signal wires to the Daisy (pads 12 + 13 unchanged, + 1 spare pad
for reset) · 13 pins straight to ground · 2 pins to 3.3V · 2 pins with a single part ·
2 power pins with local caps · 9 pins empty.

**Optional but recommended — VCC power switch:** a high-side P-FET on the 13V branch
(gate pulled up = default off) driven by the *other* spare Daisy pad. Reason: the 13V
comes up before the Daisy's 3.3V, which is backwards from the SSD1309's preferred
VDD-then-VCC sequencing, and the datasheet warns about cutting power with VCC live
(p.10). Lets firmware sequence power correctly and hard-power-cycle the screen.
Note: pads 22 + 28 are the board's LAST spare pins (also the last spare ADCs) —
using both forecloses future pots/CV inputs; sign off deliberately.

---

## 5. What gets REMOVED from rev 1

- **J2** (4-pin OLED header) and its Retroactive_2.42_OLED_I2C footprint
- The entire OLED_HOT power subsystem: **FB4, C14 (470µF radial), C17 (100nF),
  R21 (10Ω)** — and the duplicate layout-only 300Ω "R21" hack at (170.1, 84.8).
  Side effect: resolves rev-1 findings F-013 / F-020 / F-025 (duplicate refdes,
  PCB-only damper, BOM/CPL collision).
- The schematic's "OLED RC FILT" block

## 6. BOM additions

2× ZIF connector candidates (buy both flavors as samples, use one) · LDO + set
resistors + its caps · P-FET + 2 resistors (optional VCC switch) · 1MΩ 1% · 1µF ·
2× 2.2µF · 2× 100nF · 100µF · ferrite bead(s) · 2× 2.2k pull-ups · 10k pull-down ·
optional 0.5A polyfuse on the screen branch (datasheet-recommended, p.10) ·
**15V wall adapter** (replaces 9V).

## 7. Layout guidance

- Board outline: x 89.6–254.7, y 61.1–166.0 (165 × 105mm). All rear-panel I/O along
  top edge.
- **Keep display power + I2C out of the center audio corridor (x≈165–200)** — audio
  jacks top-center, MAX9814 mic preamp dead center, Daisy + headphone amp bottom
  center. Rev 1 put the OLED feed *in* this corridor; rev-1 finding F-019 fingered it
  as the debugged noise path. Open real estate: x≈115–155 and x≈180–230 at y≈85–110.
- Put the 13V regulator near the existing bridge/filter area (x≈147–156, y≈78–90),
  run the filtered feed to the ZIF with the bead + bulk *at the connector*.
- New traces: ≥0.25mm signals, ≥0.5mm power. Do NOT inherit rev 1's 0.1mm
  at-JLC-minimum widths for new work.
- ZIF placement rule: connector within ~√(18² − h²) mm of the panel's bottom-edge
  projection, where h = face-to-board standoff in mm. At h=10mm → ~15mm reach. If the
  board sits >~15mm behind the face, the tail won't reach → extender FPC or rethink.

## 8. Firmware impact

- Same driver (SSD1309), same I2C address (0x3C), same Daisy pins → existing code
  carries over.
- New: drive RES# high after boot (release reset) before init; sequence VCC_EN after
  init if the P-FET is used.
- Keep the existing 0xD5 clock / 0xD9 precharge init tweaks (harmless, no longer
  load-bearing). No contrast compensation needed at 13.0V.
- Datasheet recommends periodic re-init/refresh as catastrophic-noise recovery (p.11)
  — cheap insurance in a synth EMI environment.

## 9. Open questions / to-do before schematic capture

1. **Enclosure CAD:** screen window center coordinates + face-to-board stack height
   (go/no-go for tail reach).
2. **Connector orientation:** settle with physical panel + both connector samples.
3. **Supply logistics:** 9V→15V adapter change acceptable? Update labeling.
4. **Verify** Daisy VIN 17V max against current Electrosmith datasheet rev.
5. Bundle the standing rev-1 fixes into this spin: encoder click routing (F-007),
   LED drive redesign (F-018), GND pour file provenance (F-006), 0.1mm trace widths.

## 10. Corrections to the original brief (for the record)

- The brief said the board hosts **two** displays sharing a bus at 0x3C/0x3D.
  The board has exactly **one** display header (J2) and rev 2 is **one screen** —
  confirmed in discussion. All dual-address strapping in the brief is moot; pin 17
  simply ties to GND.
- The brief's "+12V rail / 12.0V acceptable" premise was wrong on both counts
  (see §2).

---

## 11. Screen change: Newhaven NHD-2.7-12864WDW3 (supersedes §1–§4 where they conflict)

*Added 2026-09-29. The Crystalfontz bare-glass panel in §1–§4 has been replaced by the
Newhaven NHD-2.7-12864WDW3 module (datasheet rev 6, 07/31/2024). Status: DISCUSSION
ONLY — no design files modified.*

### 11.1 What is different

| | Crystalfontz plan (§1–§4) | Newhaven NHD-2.7-12864WDW3 |
|---|---|---|
| Controller | SSD1309, 1-bit | **SSD1322**, 16-level grayscale, different command set |
| Interface | I2C @ 0x3C | **SPI (3/4-wire) or 8-bit parallel — no I2C** |
| Connection | bare glass, 31-pin FPC into ZIF | **module PCB, 1×20 pin 2.54mm header** |
| Panel power | 13.0V from our LDO | on-board boost from 3.3V (default), or **14.5–15.5V into pin 15** (jumper option #2, R4 open / R7 closed) |
| Logic power | 3.3V | 3.0–3.5V. Default jumpers: up to 375mA @ 100% on. Option #2: ~0.3mA + 60–70mA @ 15V on VCC |

Consequences for the plan:

1. **Firmware:** the SSD1309 driver does not carry over. libDaisy has no SSD1322 driver;
   its `oled_ssd1327` (also 4-bit grayscale) is the closest starting point. Newhaven's
   init sequence is on datasheet p.15. Visible 128 columns sit at an offset inside the
   controller's 256-column RAM (mechanical drawing, Detail A) — copy the column/row window
   from Newhaven's example code.
2. **Pin count:** 4-wire SPI needs 5 Daisy pins (SCK, MOSI, CS, D/C, RES) vs 3 for I2C.
   See §11.2.
3. **Power:** the default (on-board boost) reintroduces exactly the switcher the rev-2
   brief set out to remove. Bypassing it (option #2) needs **14.5V minimum** on pin 15,
   but the §2 scheme (15V adapter → bridge → ~14.3V → LDO) can't reach that. Open — see §11.4.
4. **Mechanical:** §3 (ZIF orientation, tail reach) and `screen mounting solution.md` no
   longer apply. The module has its own PCB and header; mount per the datasheet
   mechanical drawing (bezel redesign rev 3, 2021).
5. **§5 removals and §6 BOM** still apply in spirit (J2, OLED_HOT filter block go away),
   but the ZIF, IREF/VCOMH parts and the I2C pull-ups are all dropped.

### 11.2 Daisy pin budget (from the rev-1 schematic netlist)

Physical Seed pin numbers; `D#` is the libDaisy name.

- **Free in rev 1:** pin 1 (D0, USB_ID — usable GPIO), pin 22 (D15/ADC0), pin 28 (D21/ADC6).
- **Freed by removing J2:** pin 12 (D11, /I2C_SCL), pin 13 (D12, /I2C_SDA).
- Total: 5 → enough for bit-banged SPI with no moves, but bit-banging a 4KB grayscale
  frame on the audio core with no DMA is a poor trade. Use hardware SPI1.

**Hardware SPI1 pins are all occupied in rev 1:**

| Pin | libDaisy | SPI1 role | rev-1 net |
|---|---|---|---|
| 8 | D7 | NSS | /ENCR_A |
| 9 | D8 | SCK | /ENCR_B |
| 10 | D9 | MISO | /TAC_SHIFT_R |
| 11 | D10 | MOSI | /ENCL_CLICK |

The screen is write-only, so only SCK and MOSI need the peripheral. CS is software-driven
on any GPIO (libDaisy software-NSS mode leaves D7 untouched); MISO is unused.

**Nets that move (2):**

| Net | From | To | Note |
|---|---|---|---|
| /ENCR_B | pin 9 (D8) | **pin 13 (D12)** | ex-I2C_SDA |
| /ENCL_CLICK | pin 11 (D10) | **pin 12 (D11)** | ex-I2C_SCL. Free move: this net is unrouted in rev 1 (F-007) and must be re-routed anyway |

/ENCR_A (pin 8) and /TAC_SHIFT_R (pin 10) stay.

**Proposed screen assignment:**

| Module pin | Signal | Daisy pin | Notes |
|---|---|---|---|
| 1 | VSS | GND | |
| 2 | VDD | +3V3_D | local 100nF + ≥4.7µF |
| 3 | NC (BC_VDD) | — | leave open |
| 4 | D/C | **pin 22 (D15)** | |
| 5, 6 | VSS | GND | |
| 7 | SCLK | **pin 9 (D8)** | SPI1 SCK |
| 8 | SDIN | **pin 11 (D10)** | SPI1 MOSI |
| 9 | NC | — | leave open |
| 10–14 | VSS | GND | |
| 15 | VCC | 15V branch | only with jumper option #2; ferrite + 100nF + ≥100µF at the header |
| 16 | /RES | **pin 1 (D0)** | 10k pull-down so the panel stays in reset until firmware releases it |
| 17 | /CS | **pin 28 (D21)** — or tie to GND, see below | |
| 18 | /SHDN | — | leave open (internally pulled high); unused with option #2 |
| 19 | BS1 | GND | BS1=0, BS0=0 → 4-wire SPI |
| 20 | BS0 | GND | |

**Option to keep one spare ADC:** the screen is the only SPI device, so /CS can be tied
permanently to GND (common on SSD1322 modules). Then only D/C and /RES need GPIOs and
**pin 28 (ADC6) stays spare**. Downside: no way to deselect the panel if SPI1 is ever
shared. Decide at schematic capture.

Otherwise this consumes every spare pin including both remaining ADCs (the §4 warning
still stands). If the LED-drive redesign (F-018) moves the six LEDs to a driver chip, pins
24–27/30/31 free up and the squeeze goes away — decide the two together.

SPI clock: keep ≤ 4MHz on the breadboard; SSD1322 limit is ~10MHz. Signal traces ≥0.25mm
per §7, kept out of the centre audio corridor.

STM32 port names (Trey's list, 2026-09-29): D7 = PG10 SPI1_NSS, D8 = PG11 SPI1_SCK,
D10 = PB5 SPI1_MOSI. Matches the mapping above; corroborated by two sources.

**Option 2 (Trey's assignment):** same SCLK/SDIN/BS/GND wiring, but **/CS on D7 (pin 8,
hardware SPI1_NSS)**, D/C and /RES on any free GPIO, VDD from the Seed's 3V3 pin, default
jumpers (on-board boost), pin 15 open. Differences from Option 1:

| | Option 1 (above) | Option 2 (Trey) |
|---|---|---|
| /CS | software CS on pin 28, or tied to GND | hardware NSS on D7 = pin 8 → **/ENCR_A must also move** (3 nets relocated instead of 2) |
| VDD source | +3V3_D rail | Seed 3V3 pin — same rail; fine on option #2 jumpers (~0.3mA), but with the default boost active the module can draw up to 375mA from a regulator with no published limit (F-021) |
| Jumpers | default for bring-up, then option #2 | default (boost stays) — leaves §11.4 Q6 unanswered |
| /RES pull-down | 10k to GND | not specified — keep it either way |

Option 2 is the correct Pod breadboard configuration and a fine first target. For the board,
the /CS choice and the boost-vs-external-VCC question are the two items to settle.

### 11.3 Breadboard bring-up with a Daisy Pod

**Pod pin usage** (libDaisy `daisy_pod.cpp` Rev 3/4 table, `daisy_seed.h` port map,
`uart.cpp` USART1 pins). Physical = Seed 40-pin numbering (D0–D14 = pins 1–15,
D15–D30 = pins 22–37).

| libDaisy | STM32 | Seed pin | Pod function |
|---|---|---|---|
| D13 | PB6 | 14 | Encoder click (also USART1_TX — unused, no MIDI out) |
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
| — | — | 16–19 | Audio in/out L/R |
| D29/D30 | PB14/PB15 | 36–37 | USB D−/D+ |

Fixed: 20/40 GND, 21 3V3_A, 38 3V3_D, 39 VIN.

**Free on the Pod:**

| libDaisy | STM32 | Seed pin | Note |
|---|---|---|---|
| D0 | PB12 | 1 | USB_ID, usable GPIO |
| D1–D6 | PC11, PC10, PC9, PC8, PD2, PC12 | 2–7 | SDMMC pins, no SD slot on the Pod |
| **D7** | **PG10** | 8 | **SPI1_NSS** |
| **D8** | **PG11** | 9 | **SPI1_SCK** |
| D9 | PB4 | 10 | SPI1_MISO (unused by screen) |
| **D10** | **PB5** | 11 | **SPI1_MOSI** |
| D11 | PB8 | 12 | I2C1_SCL |
| D12 | PB9 | 13 | I2C1_SDA |
| D16 | PA3 | 23 | ADC-capable |
| D22 | PA5 | 29 | 3.3V-only pin |

The whole SPI1 block D7–D10 plus D11/D12 is uncommitted on the Pod, so both Option 1 and
Option 2 wiring work there without touching any Pod control. **Pod ≠ board for the three
GPIO lines:** the board's spares (pins 1, 22, 28) are the Pod's knobs at 22/28, so on the
breadboard put D/C, /RES and (if not tied low) /CS on D0, D11, D12 or D16 instead. SCLK and
SDIN (D8/D10) are identical on both; that is the only part of the firmware pin config
that must not change between breadboard and board.

1. **Default jumpers first** (on-board boost, 3.3V only). Power VDD from a separate 3.3V
   supply able to source ≥400mA — not the Seed's 3V3 pin. Common all grounds.
2. Wire per the table above, with the Pod-side substitutions: D/C → D9, /RES → D11,
   /CS → D7 (all free on the Pod). Optionally /SHDN → D12 so firmware can kill the boost
   while audio plays and the difference can be heard through the Pod's output.
3. Firmware: /RES low ≥200µs, release, wait ≥200µs, send the p.15 init. Test with 0xA5
   (all pixels on) before real graphics.
4. **Then** move the 0Ω jumper R4 → R7 (option #2), feed 15.0V into pin 15 from a bench
   supply (3.3V up first, 15V second) and confirm the panel is quiet enough without the
   boost before committing the board to that scheme.

### 11.4 Open questions (add to §9)

6. **15V VCC source.** Option #2 needs 14.5–15.5V at pin 15. 15V adapter → bridge gives
   ~14.3V: too low. Candidates: (a) 18V adapter → bridge ~17.3V → LDO to 15.0V — but
   17.3V exceeds Daisy VIN max 17V unless the Daisy gets its own pre-regulator; (b) keep the
   9V/15V adapter and add a *quiet* boost (fixed-frequency, well filtered, placed away from
   audio) for the screen only — partly defeats the purpose; (c) accept the module's boost
   with /SHDN control + the §2 ferrite/bulk isolation, and evaluate noise on the breadboard
   first (§11.3 step 4 vs step 1 is exactly this A/B test). Decide from measurement.
7. /CS tied low vs on pin 28 (§11.2).
8. SSD1322 driver: port `oled_ssd1327` or write fresh; who owns it.
