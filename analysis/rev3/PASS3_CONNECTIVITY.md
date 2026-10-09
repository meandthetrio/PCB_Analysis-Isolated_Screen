# Rev 3 — Pass 3: Connectivity / sch↔pcb / ERC
**Date:** 2026-10-09 · **Truth checked:** `rev3/WavetableController.kicad_sch` (intent) vs `rev3/WavetableController.kicad_pcb` (copper truth for rev 3 — it carries the filled GND zone; no rev-3 Gerbers exist yet, pre-fab review) · **Tools:** `kicad-cli 9.0.9` ERC/DRC (`kicad_out/rev3/erc.json`, `drc_asis.json`), `pcbnew` Python connectivity, scripts in `analysis/rev3/scripts/pass3_5/` (`sch_inventory.py`, `pcb_export.py`, `netlist_parse.py`, `sch_pcb_diff.py`, `net_geometry.py`).
**Threshold sources:** NHD-2.7-12864WDW3 datasheet (scratchpad `datasheets/NHD.txt`, pin tables lines 143–185, interface-select table 190–203); Daisy Seed pin functions from the stock KiCad symbol `MCU_Module:Electrosmith_Daisy_Seed_Rev4` embedded in the rev-3 schematic + libDaisy `src/daisy_seed.h` (raw.githubusercontent.com, fetched 2026-10-09) — **secondary sources**, the Daisy datasheet hosts are blocked from this session; 3.3V-only pin list (24, 25, 28, 29, 30) carried from rev-2 Pass 2 (Electrosmith forum); libDaisy `src/hid/encoder.cpp` + `src/hid/switch.h` (fetched 2026-10-09) for the click-pin pull-up.

## Headline
1. **Schematic and PCB are fully consistent.** 110 symbols ↔ 110 footprints, no duplicate refdes, zero pad-level net differences (396 pad/pin pairs compared; the only residue is 28 "pins" that exist in just one file — 20 mechanical/shield pads with no schematic pin, and the 8 USB-C SuperSpeed pins that the 16-pin receptacle footprint physically lacks). Rev-2 F-013 (dup R21) and F-014 (LED2 sch≠pcb) are **FIXED**.
2. **The "unannotated symbols" are not symbols.** The `U`×5 / `L` / `RV` / `Q` references are the generic prefixes of the eight `lib_symbols` *library definitions* (MAX9814, TPA6110A2DGN, H11L1, USBLC6-2P6, TPS62172DSG, L_Iron, R_Potentiometer_Dual, MMBT3904). Every one of the 155 placed instances (110 parts + 45 power symbols) is annotated; the dual pot is placed as **`Headphones1`** in both files. ERC's `unannotated` check (severity error in the `.kicad_pro`) correctly reports none. Rev 2's "`U`×4" was the same artefact (TPS62172 is the fifth definition).
3. **Encoder clicks are routed (F-007 → FIXED on paper).** `/ENCL_CLICK` ENCL1.S1 → A1.22: 170.6 mm, 6 vias, 0.3 mm; `/ENCR_CLICK` ENCR1.S1 → A1.29: 190.6 mm, 10 vias, 0.3 mm. Continuous copper verified independently of DRC (graph walk over segments/vias/pads, `net_geometry.py`), and `pcbnew` connectivity reports 0 unconnected items board-wide.
4. **J8 matches the NHD serial-interface pin table line for line** (20/20 pins, 4-wire SPI strapping BS1=BS0=GND). Two judgment items: `/RES` has no pull-up/RC, and the OLED's logic rail (`/+3V3_OLED`, from the new U6 buck) is a different 3.3 V domain from the Daisy GPIOs (`/+3V3_D`).
5. **LED drive polarity still reads reversed in the netlist** — LED anodes on the NPN collectors, cathodes through 300 Ω to `/+9V_FLAG` (connectivity fact; electrical disposition belongs to Pass 2, cross-referenced as R3-P3-09).

## 1. Schematic ↔ PCB netlist diff (`sch_pcb_diff.py`)
| Check | Result |
|---|---|
| Components only in schematic | none |
| Footprints only in PCB | none |
| Duplicate refdes in PCB | none (rev 2 had R21×2) |
| Value / footprint-id mismatches | none |
| Nets only in one file | none (121 sch nets = 105 multi-node + 15 `unconnected-*` + `/SWA`; PCB 113 = 105 + 7 `unconnected-*` surviving on real pads + `/SWA`) |
| Pad-level net differences | **0** real. 28 structural: ENCL1/ENCR1 `MP`, J1.3, J3–J7 `RN`/`TN`, SW1 `""`/`3`, TAC_SHIFT_*/U3/U4/U6 `""` = mounting/shield/EP pads with no schematic pin; P2 A2/A3/A10/A11/B2/B3/B10/B11 = SuperSpeed pins absent from the 16-pin `USB_C_Receptacle_GCT_USB4105` footprint |
| Single-pad nets in PCB | `/SWA` only (P1.10, card-detect A; no copper) |
| Nets with pads but no copper | `/SWA` only |
| GND / AGND tie | single `GND` net, 90 nodes: A1.20 AGND + A1.40 DGND, U6 PGND/AGND/PAD, P1 VSS+SHIELD+DET_B, one GND zone on F.Cu+B.Cu filled (20,849 mm² total copper) |

**Parser validation:** the independent copper-walk flagged one false split (`/SD_D1` branch to R7.2 ends inside the annulus of via (93.795, 142.25), 0.064 mm off-centre — KiCad connectivity accepts this, `pcbnew` reports 0 unconnected on the net). All other 54 audited nets resolve to one island per net. Treat `drc_asis.json` `unconnected_items = 0` as the completeness anchor.

## 2. ERC disposition — all 20 non-library items
| # | ERC item (severity) | Rev-3 net / path | Disposition |
|---|---|---|---|
| 1–10 | P2 TX1±/RX1±/TX2±/RX2±/SBU1/SBU2 `pin_not_connected` (error) | no net; pads do not exist on the 16-pin footprint | **Intentional** (USB2-only, design decision). Add no-connect flags → carried F-024 |
| 11 | J8.3 NC | NHD pin 3 = NC / BC_VDD (jumper R5 open by default, NHD.txt l.168–169, 207–219) | **Intentional, correct** |
| 12 | J8.9 NC | NHD serial pin 9 = NC (D2) (l.175) | **Intentional, correct** |
| 13 | J8.15 NC | NHD pin 15 = NC / VCC (jumper R7 open by default, l.177–178, 222–226) | **Intentional, correct** |
| 14 | J8.18 NC | NHD pin 18 = /SHDN "internally pulled HIGH" (l.181) | **Intentional, acceptable.** Could drive the boost-converter shutdown from a GPIO for a hard display-off, but all 40 Daisy pins are now assigned (§5) |
| 15 | A1.39 VIN `power_pin_not_driven` | `/DSY_VIN` ← R30 3.3Ω ← R29 3.3Ω ← FB6 ← D6 ← FB5 ← FB4 ← FB3 ← D2/D3 bridge ← J1 | **False positive** — only passives between the input and VIN; no `power_out` pin on the chain. Add PWR_FLAG |
| 16 | U4.5 VDD not driven | `Net-(U4-VDD)` ← FB2 ← `/+3V3_A` (A1.21 is `power_out`) | **False positive** through FB2 (unchanged from rev 2). Add PWR_FLAG |
| 17 | #PWR01 not driven | `#PWR01` is a **`power:GND` symbol** (sch l.16040); the whole GND net has only `power_in` pins (A1.20/40, P1.6, U1.5, U3.2, U4.7, U6.1/4/9) and no PWR_FLAG | **Cosmetic** — one PWR_FLAG on GND clears it. (Rev-2 note called this "the 9V input net"; in rev 3 it is GND.) |
| 18 | U6.2 VIN not driven | `Net-(U6-EN)` ← FB7 ← `/+9V_FLAG` (VIN and EN tied, C25 10 µF local) | **False positive** through FB7. Add PWR_FLAG |
| 19 | `label_dangling` 'SWA' | P1.10 DET_A single-pin, no copper | **F-022 STILL OPEN** — card detect unreadable; harmless |
| 20 | `multiple_net_names` GND/SWB (warning) | P1.9 DET_B labelled SWB and tied to GND | **Informational**, consequence of 19 |

Library warnings: 19 `footprint_link_issues` + 12 `lib_symbol_mismatch` naming Trey's private libraries — expected noise per CLAUDE.md. The three rev-2 NC errors on Daisy ADC_0 / ADC_6 / USB_ID are gone because those pins are now used (`/ENCL_CLICK`, `/DC_SPI`, `/RES_SPI`).

## 3. Encoder click switches (F-007)
| Net | Switch pad | Daisy pin | STM32 pin (libDaisy D-index = pin−7 for pins 22–37) | Copper | Pull-up |
|---|---|---|---|---|---|
| `/ENCL_CLICK` | ENCL1.S1 (S2 → GND) | 22 "ADC_0" | D15 = **PC0** (GPIO + ADC) | 170.6 mm, 6 vias, 0.3 mm, one island | none external (2-node net) |
| `/ENCR_CLICK` | ENCR1.S1 (S2 → GND) | 29 "DAC_OUT2" | D22 = **PA5** (3.3V-only list) | 190.6 mm, 10 vias, 0.3 mm, one island | none external (2-node net) |

- Both are switch-to-GND with **no external pull-up anywhere in the schematic**; the design relies on the STM32 internal pull-up. libDaisy `Encoder::Init` calls `sw_.Init(click)` and `Switch::Init`'s pull argument defaults to `GPIO::Pull::PULLUP` (switch.h, fetched); so the stock driver provides it. A 10 k external pull-up to `/+3V3_D` would make the input robust against firmware that configures the pin differently — JUDGMENT, optional. Pin 29 is on the 3.3V-only list — fine for a switch-to-GND with a 3.3 V pull-up; never pull above 3V3.
- Pin 22 is a usable GPIO/ADC (PC0: ADC1/2/3_INP10 on STM32H750); the previous assignment (pin 11) is now SPI1 MOSI, so the move was required.
- Rev-2 moved: `/ENCL_CLICK` pin 11 → 22; `/ENCR_CLICK` stays on 29.

## 4. SPI OLED header J8 vs NHD-2.7-12864WDW3 serial-interface pin table
Footprint `Newhaven2.7_OLED`: 20 PTH pads, 2.54 mm pitch, in a row on F.Cu at y = 81.3 (pin 1 at x = 196.26, pin 20 at 148.0) — matches "Recommended Pin Header: 1x20pin 2.54mm pitch" (NHD.txt l.140).

| J8 pin | Net (sch = pcb) | NHD serial-mode function (l.163–185) | Verdict |
|---|---|---|---|
| 1 | GND | VSS | ✓ |
| 2 | `/+3V3_OLED` | VDD 3.0–3.5 V, IDD up to 375 mA (l.244–245) | ✓ rail supplied by U6 TPS62172 (Pass 2 checks current) |
| 3 | NC | NC (BC_VDD jumper) | ✓ |
| 4 | `/DC_SPI` ← A1.28 | D/C (4-wire) | ✓ |
| 5, 6 | GND | VSS ("Tie LOW" R/W, E) | ✓ |
| 7 | `/SCLK_SPI` ← A1.9 | SCLK | ✓ |
| 8 | `/SD_IN_SPI` ← A1.11 | SDIN | ✓ |
| 9 | NC | NC (D2) | ✓ |
| 10–14 | GND | VSS (D3–D7 "Tie LOW") | ✓ |
| 15 | NC | NC (VCC jumper) | ✓ |
| 16 | `/RES_SPI` ← A1.1 | /RES | ✓ wiring; no pull-up/RC (R3-P3-04) |
| 17 | `/CS_SPI` ← A1.8 | /CS | ✓ |
| 18 | NC | /SHDN, internally pulled HIGH | ✓ |
| 19 | GND | BS1 = 0 | ✓ |
| 20 | GND | BS0 = 0 | ✓ → **4-wire serial** (l.192–195) |

Daisy side (symbol pin names + libDaisy `daisy_seed.h`, D-index = pin−1 for pins 1–15):
| Signal | Daisy pin | Symbol function | STM32 pin (libDaisy) | Role |
|---|---|---|---|---|
| `/CS_SPI` | 8 | SPI1_CS | D7 = PG10 (SPI1_NSS AF5) | hardware NSS or GPIO — both fine |
| `/SCLK_SPI` | 9 | SPI1_SCK | D8 = PG11 (SPI1_SCK) | ✓ |
| (MISO) | 10 | SPI1_POCI | D9 = PB4 | used as `/TAC_SHIFT_R` GPIO — fine; firmware must init SPI1 without MISO |
| `/SD_IN_SPI` | 11 | SPI1_PICO | D10 = PB5 (SPI1_MOSI) | ✓ |
| `/DC_SPI` | 28 | ADC_6 | D21 = PC4 (3.3V-only list) | plain GPIO output — fine |
| `/RES_SPI` | 1 | USB_ID | D0 = PB12 (OTG_HS_ID) | plain GPIO — fine; the Daisy's external USB (pins 36/37) is device-mode and does not need ID |

Mapping rule validated on two independent pins: pin 36 = D29 = PB14 = USB_D− and pin 29 = D22 = PA5 = DAC1_OUT2, both as the KiCad symbol names them.

Other SPI-header facts: no series resistors, no pull-ups, no RC on any of the five lines (all 2-node nets). Decoupling at J8.2: C23 100 nF (axial THT) at 10.5 mm copper path, C24 100 µF at 14.5 mm; U6 output cap C26 22 µF at 38 mm. `/+3V3_OLED` is 0.5 mm wide (50.4 of 54.6 mm).

## 5. Dual-gang pot `Headphones1` (B10k, Bourns PTD902-2015K-B103)
| Pin | Net | Role |
|---|---|---|
| 1 | AUDIO_OUT_L (A1.18 + J5.T) | gang-1 end — Daisy line-out L |
| 2 | Net-(C2-Pad1) → C2 470 nF → R12 22 k → U3.8 IN1− | gang-1 wiper → headphone-amp input |
| 3 | GND | gang-1 end |
| 4 | AUDIO_OUT_R (A1.19 + J5.R) | gang-2 end |
| 5 | Net-(C3-Pad1) → C3 470 nF → R13 22 k → U3.4 IN2− | gang-2 wiper |
| 6 | GND | gang-2 end |

- Topology: **volume control at the TPA6110A2 input** (potential divider across the Daisy codec output), not between the amp and J7. Line-out J5 is fed directly, unattenuated, in parallel with the pot's 10 k. Gain after the pot = R14/R12 = 33 k/22 k = 1.5× (inverting), unchanged from rev 2 (Pass-5 Eq.-6 check still holds with Ri = 22 k, Ci = 470 nF).
- Gang mapping is consistent (L: 1-2-3, R: 4-5-6; footprint pads 2.5 mm pitch rows at y = 146.5 / 144.0).
- **Taper:** "B" in Bourns' code is **linear**; a volume control normally uses audio/log ("A") taper — JUDGMENT R3-P3-07.
- **Rotation sense:** signal on pin 1, GND on pin 3. Whether pin 1 is the CCW or CW terminal of the PTD902 is not derivable from the files (datasheet host blocked); if pin 1 = CCW the volume *decreases* clockwise — verify before fab, R3-P3-07.

## 6. LED driver wiring (connectivity view; electrical disposition → Pass 2)
Each of the six channels: Daisy GPIO → 1 k (R35–R40) → Qn base (MMBT3904 pin 1), emitter (pin 2) → GND, collector (pin 3) → LED **anode** pin (AR/AG/AB). The LED **cathode** pins (KR/KB, symbol pin names) go through 300 Ω (R21, R24–R28) to `/+9V_FLAG`. All GPIO→base nets and base nets are clean 2-node nets (nothing else on them); lengths 33–51 mm (GPIO→R) and 4–43 mm (R→base), 0.2 mm wide. The 3.3V-only concern of F-018 is gone (GPIO sees only a base-emitter junction via 1 k). **But the LED is still oriented anode-to-collector / cathode-to-+9V, i.e. reverse-biased when the transistor conducts** — identical polarity to rev 2's F-018, now with a transistor in the anode leg. Either the custom LED symbol's A/K pin names are wrong for the CLS6B-FKW, or the LEDs still cannot light. Flagged R3-P3-09 for Pass 2 to confirm against the LED datasheet. Note LED1 has two pins named "KR" (pin 2 and pin 4) in the custom symbol — one is presumably KG.

## 7. Other connectivity-level checks
- `/SWA` single-pin (P1.10), `SWB` on GND — unchanged F-022.
- `via_dangling` ×2 (DRC): vias on `/LED_2_R` (167.75, 145.9) and `/LED_2_B` (168.53, 145.74) connected on one layer only — zero-length via stubs at the end of a trace; harmless, cosmetic (rev-2 F-023's GND track stubs are gone with the pour).
- Daisy pin budget: **all 40 pins are assigned** (every A1 pin has a net). No spare GPIO for /SHDN, card detect, or a RES/VCC sequencing line.
- MISO (pin 10) doubles as `/TAC_SHIFT_R` — acceptable; the OLED is write-only.
- Widths: new signal routing is 0.3 mm; the only 0.1 mm remnants are 5.9 mm on `/USART1_TX`, 1.1 mm on `/USB_IN_MCU_N`, 3.1 mm on `/USB_IN_N` (Pass 1 territory).

## Findings (rev 3, Pass 3)
| ID | Class | Status | Finding | Evidence | Source |
|---|---|---|---|---|---|
| R3-P3-01 | PASS | confirmed | Schematic ↔ PCB fully consistent: 110↔110 parts, 0 dup refs, 0 real pad-net diffs, 0 one-file nets; F-013/F-014 fixed | `sch_pcb_diff.py` | — |
| R3-P3-02 | PASS | confirmed | "Unannotated U/L/RV/Q" are lib_symbols definitions, not instances; 0 unannotated placed symbols; `Headphones1` is the dual pot in both files | `sch_inventory.py` | — |
| R3-P3-03 | PASS | confirmed | Encoder clicks routed with continuous copper (170.6 / 190.6 mm, 0.3 mm); pin 22 = PC0 GPIO/ADC; relies on STM32 internal pull-up (libDaisy default PULLUP) | `net_geometry.py`, libDaisy encoder.cpp/switch.h | libDaisy (secondary) |
| R3-P3-04 | JUDGMENT | confirmed | `/RES_SPI` is a bare 2-node net: no pull-up/pull-down/RC. Floats (STM32 high-Z) from power-up until firmware drives it; NHD marks /SHDN "internally pulled HIGH" but says nothing of the kind for /RES. Add 10 k to `/+3V3_OLED` (or 10 k down + firmware release) for a defined reset state | §4 | NHD.txt l.180–181 |
| R3-P3-05 | JUDGMENT | confirmed | OLED logic rail `/+3V3_OLED` (U6 buck from 9 V) ≠ Daisy GPIO rail `/+3V3_D`. Levels are compatible (VIH 0.8·VDD = 2.64 V ≤ STM32 VOH), but the SSD1322 inputs can be driven while its own VDD is down if U6 is slower than the Daisy's LDO + boot; Daisy GPIOs are high-Z through boot, so low practical risk — Pass 2 to compare U6 soft-start vs Daisy 3V3 rise | §4 | NHD.txt l.258–259 |
| R3-P3-06 | JUDGMENT | confirmed | ERC hygiene: 14 missing NC flags (10 USB-C SS/SBU + J8 3/9/15/18), 4 missing PWR_FLAGs (`/DSY_VIN`, `Net-(U4-VDD)`, `Net-(U6-EN)`, GND). All verified false-positive/intentional. Carries F-024 | §2 | — |
| R3-P3-07 | JUDGMENT | plausible | `Headphones1` is a **linear** (B) taper 10 k used as a volume control; and signal is on pin 1 / GND on pin 3 — rotation sense depends on the PTD902 terminal order (datasheet unreachable). Prefer A-taper; verify CW = louder | §5, BOM line `PTD902-2015K-B103` | Bourns taper code (industry convention; datasheet not fetched) |
| R3-P3-08 | PASS | confirmed | J8 wiring = NHD serial pin table 20/20; BS1=BS0=0 → 4-wire SPI; D3–D7, R/W, E tied low; NC pins correct; Daisy pins 8/9/11 are SPI1 NSS/SCK/MOSI; DC/RES on plain GPIO | §4 | NHD.txt l.163–203; KiCad symbol + libDaisy |
| R3-P3-09 | VIOLATION (cross-domain) | plausible — Pass 2 to confirm | LED polarity in netlist: anode→NPN collector, cathode→300 Ω→+9 V ⇒ reverse-biased when driven (same orientation as F-018). Signal side (GPIO→1 k→base, clean 2-node nets) is PASS | §6 | needs CLS6B-FKW pinout vs custom symbol pin names |
| R3-P3-10 | JUDGMENT | confirmed | F-022 unchanged: `/SWA` single-pin, SWB grounded — card detect unusable; all 40 Daisy pins now consumed so wiring it needs a pin trade | §2, §7 | — |
| R3-P3-11 | info | confirmed | 2 single-layer via stubs (`/LED_2_R`, `/LED_2_B`); cosmetic | DRC `via_dangling` | — |

## Rev-2 finding status (Pass-3 domain)
| Rev-2 ID | Rev-3 status | Evidence |
|---|---|---|
| F-007 encoder clicks unrouted | **FIXED** (pre-fab, on paper) | continuous copper both nets; `drc_asis` 0 unconnected |
| F-011 ERC triage | N/A (superseded by F-024) | — |
| F-013 duplicate R21 | **FIXED** | 0 duplicate refs; 110 = 110 |
| F-014 LED2 sch≠pcb wiring | **FIXED** | 0 pad-level diffs (LED1/LED2 pins 1–6 identical in both files) |
| F-020 PCB-only 10 Ω damper | **FIXED / N/A** | OLED_HOT subsystem removed; no PCB-only parts |
| F-022 SD card-detect half-wired | **STILL OPEN** | `label_dangling` SWA, `/SWA` single pad |
| F-023 dangling GND stubs | **FIXED** (pour present); 2 new cosmetic via stubs | DRC `via_dangling` ×2, `track_dangling` 0 |
| F-024 ERC hygiene (NC flags, PWR_FLAGs) | **STILL OPEN** (14 NC + 4 PWR_FLAG; rev 2: 13 + 2) | `erc.json` |
