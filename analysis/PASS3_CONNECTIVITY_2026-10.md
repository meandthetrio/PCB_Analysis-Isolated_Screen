# Pass 3 — Connectivity, Round 2 (2026-10 files)
**Date:** 2026-10-07 · **Truth checked:** `.kicad_sch` netlist (kicadxml export) vs `.kicad_pcb` pad nets; single truth per F-036 · **References:** Daisy Seed datasheet v1.2.0, Newhaven NHD-2.7-12864WDW3 Rev 6 (both in `datasheets_2026-10/`), libDaisy `src/hid/switch.cpp` / `encoder.cpp` (fetched 2026-10-07) · **Status: COMPLETE**

## 1. Schematic ↔ board netlist diff — clean

| | Count |
|---|---|
| Schematic nets (netlist export) | 110 (17 single-node) |
| Board nets (pads with a net) | 102 |
| Shared nets with **any** membership difference | **0** |
| Nets only in the board | 0 |
| Nets only in the schematic | 8 — P2's TX1±/TX2±/RX1±/RX2± SuperSpeed pins: the GCT USB4105 **16-pin** footprint has no pads for them (symbol is the 24-pin receptacle) |

So 110 − 8 = 102 ✓, every shared net has identical (ref, pin) membership, DRC reports 0 unconnected items and 0 schematic-parity issues. Round 1's F-013 (dup R21), F-014 (LED2 skew) and F-015 (reroutes) have no Round 2 counterpart.

**F-014 resolution:** LED2 is now wired the way the Round 1 *schematic* had it (pin 2 → R26, pin 6 → R28); the board was changed to match. With the Cree pinout (pin 2 = blue cathode, 6 = green cathode) the choice is immaterial — all six cathodes go to identical 300 Ω / `/+9V_FLAG` resistors — and the drive problem is F-052 regardless.

## 2. Encoder clicks (F-039 → confirmed fixed)
`/ENCL_CLICK` ENCL1.S1 → A1.22 (ADC_0 / D15), `/ENCR_CLICK` ENCR1.S1 → A1.29 (A7 / D22, **3.3 V-only**); S2 of both encoders to GND; routed 170.6 / 190.6 mm, 0.3 mm. No external pull-up: the inputs depend on the STM32 internal pull-up, which is what libDaisy uses by default (`Switch::Init(... GPIO::Pull::PULLUP)`, `Encoder::Init` sets A/B to `INPUT, PULLUP`). The internal pull-up is to 3V3, so pin 29's 3.3 V-only restriction is respected. Round 1's F-007 (dead clicks) is **closed** for Round 2.

## 3. Every input, checked against the Daisy pinout (datasheet v1.2.0 table)

| Signal | Daisy pin (primary / alt) | Wiring | Verdict |
|---|---|---|---|
| ENCL A/B | 33 / 32 (SAI2_SD_A/B, GPIO) | encoder → GPIO, common C → GND | OK, internal pull-up |
| ENCR A/B | 12 / 13 (I2C1 SCL/SDA, GPIO) | same | OK — datasheet: Rev4/Rev7 do not use the I2C pins |
| ENCL/ENCR click | 22 / 29 | S1 → GPIO, S2 → GND | OK (§2) |
| TAC_SHIFT_L / R | 23 (ADC_1) / **10 (SPI1_MISO)** | pin 2 → GPIO, pin 1 → GND | OK electrically; see F-061 |
| TAC_SWITCH_1 / 2 | 34 / 35 (SAI2_FS / SCK, GPIO) | pins 1+4 → GPIO, pins 2+3 → GND | OK — footprint pads 1–4 and 2–3 are the 6.5 mm (internally common) pairs of a 6 × 6 tactile; pressing joins the 4.5 mm pairs → signal to GND. (Symbol is `SW_MEC_5E`, whose A/K pin *names* suggest an LED; the part is a plain switch.) Same wiring as the working Round 1 boards |
| SPI display | 8 (SPI1_NSS) = /CS, 9 (SPI1_SCK), 11 (SPI1_MOSI) = SDIN, 28 (GPIO) = D/C, 1 (D0) = /RES | → J8 17 / 7 / 8 / 4 / 16 | OK — matches Newhaven's 4-wire SPI row exactly; BS1/BS0 (J8 19/20) to GND = 4-wire; J8 3, 9, 15 N/C per datasheet, 18 /SHDN internally pulled high |
| MIDI | 14 (USART1_TX) → R1 10 Ω → J3 tip; R4 33 Ω 3V3 → J3 ring; J6 tip → R3 0 Ω → D1/U1 LED, ring → R2 0 Ω → R5 220 Ω; U1.4 → 15 (USART1_RX) | — | OK (R1 F-029 topology unchanged); U1 pin 3 = H11L1 NC, no-connect flagged |
| SD card | 2–7 (SD_DATA3…SD_CLK) → P1; R7–R11 47 k pull-ups on D0–D3 and CMD to 3V3_D; DET_B → GND, **DET_A → `/SWA` single-pin** | — | OK except F-022 (card-detect still half-wired) |
| USB | 36 / 37 (USB_D±) ← U2 ESD ← P2 A6/A7 + B6/B7; CC1/CC2 → R16/R17 5.1 k → GND (UFP sink); VBUS → U2 only | — | OK; data-only by design |
| Audio | 16 ← J4 tip (AUDIO_IN_L); 17 ← C12 ← U4 mic amp; 18/19 → J5 tip/ring and → Headphones1 pot → C2/C3 → R12/R13 → U3 | — | OK; **J4 ring now tied to GND** (Round 1 open note resolved; mono input, a stereo plug's R channel is shorted — acceptable); detail in Pass 5 |
| LEDs | 24, 25, 26, 27, 30, 31 → LED anodes | — | F-052 (Pass 2) |
| 3.3 V-only pins 24/25/28/29/30 | LED_2_R, LED_1_B, DC_SPI, ENCR_CLICK, LED_2_B | — | 28/29 carry 3.3 V logic ✓; 24/25/30 are the LED pins — F-052 |

## 4. ERC — all 20 error-severity items dispositioned (F-059)

| Items | Disposition |
|---|---|
| P2 TX1±/RX1±/TX2±/RX2±, SBU1/2 `pin_not_connected` (10) | **Intentional** — USB2-only on a 24-pin symbol; the 16-pin footprint has no such pads. Add no-connect flags (F-024 carry-over) |
| J8 pins 3, 9, 15, 18 `pin_not_connected` (4) | **Intentional, datasheet-verified** — BC_VDD, NC, VCC (jumper options, N/C by default), /SHDN (internally pulled high). Add no-connect flags |
| U6 PG `pin_not_connected` (1) | **Intentional, datasheet-verified** — "if not used, the PG pin should be connected to GND but may be left floating" |
| A1 VIN, U4 VDD, U6 VIN `power_pin_not_driven` (3) | **False positives** — driven through R30, FB2, FB7 respectively; add PWR_FLAGs |
| #PWR01 `power_pin_not_driven` (1) | Missing PWR_FLAG on the 9 V input — cosmetic |
| `SWA` `label_dangling` (1) + `multiple_net_names` SWB/GND warning | **F-022 persists** — card-detect DET_A floats, DET_B grounded; card presence unreadable |

Warnings: 19 `footprint_link_issues` + 6 `lib_symbol_mismatch` = private-library hygiene (Trey's `Retroactive_*` libs), as in Round 1. Net total: zero real connectivity errors; F-024's hygiene recommendation (NC flags + PWR_FLAGs) is unchanged and would take ERC to zero.

## 5. Other observations
- **FB1 has both pins on GND** (F-060): a no-op ferrite in the BOM's 7-bead line, present in Round 1 too. Either delete it or use it as the AGND/DGND bridge it was presumably meant to be (today AGND and DGND are the same net).
- **Daisy pin 10 is SPI1_MISO** and is used as the TAC_SHIFT_R GPIO while SPI1 drives the display (F-061). Hardware is fine; firmware must open SPI1 as TX-only (libDaisy `SpiHandle` direction `TWO_LINES_TX_ONLY`) or the MISO alternate function will claim the button pin.
- No external pull-ups or RC debounce anywhere on the eight switch/encoder inputs (F-058) — 40 kΩ internal pull-ups over 90–190 mm of trace. Works on the Round 1 boards; if the encoders ever glitch, 10 k + 10 nF per line is the fix.
- Single-node nets: `/SWA` (F-022) and 16 `unconnected-*` nets, all flagged no-connect except the 14 above that ERC still reports.

## 6. Findings
F-056 netlist parity clean (closes F-013/F-014/F-015 for Round 2) · F-057 encoder clicks confirmed (closes F-007) · F-058 no external pull-ups/debounce (JUDGMENT) · F-059 ERC disposition (F-024 carry-over) · F-060 FB1 no-op · F-061 MISO pin as GPIO (firmware note) · F-062 pin-function passes · F-022 persists.
