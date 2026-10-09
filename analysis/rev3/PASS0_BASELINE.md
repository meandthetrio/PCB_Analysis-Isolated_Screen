# Rev 3 — Pass 0: Inputs, provenance, baselines and the rev-2→rev-3 delta
**Date:** 2026-10-09 · **Inputs:** `rev3/WavetableController.kicad_{pro,sch,pcb}` + `rev3/ManifoldRe_BOM_NEW - Excel Format (rev3).xls` (received from Trey 2026-10-09) · **Tools:** kicad-cli 9.0.9, pcbnew Python, xlrd

## 1. Provenance and file identity

All four uploads differ from the rev-2 files at the repo root (md5 differs on all four). Content, not just checksum:

| File | Rev 2 (repo root) | Rev 3 (`rev3/`) |
|---|---|---|
| `.kicad_pcb` | 1.56 MB · 79 footprints · 86 nets · 816 segments · 94 vias · **no GND zone** (F-006) · 2× R21 | 31.9 MB · 110 footprints · 114 nets · 1032 segments · 244 vias · **one board-level GND zone, filled, F.Cu+B.Cu (15 + 4 fill polygons)** · 1× R21 |
| `.kicad_sch` | 24 lib symbols · 278 wires · 91 labels | 28 lib symbols · 379 wires · 98 labels (~9,200 changed lines) |
| `.kicad_pro` | — | trivial diff only: default pad size 2.0→1.5, plot dir `NewGerberLedFix/`→`ManifoldGerbs/`, STEP name `…wPowerSW`→`…_w_Volume`; **DRC rules block unchanged** (min_track_width still 0.0, min_clearance still 0.0) |
| BOM `.xls` | 32 rows | 37 rows |

Both KiCad files are `version 20241229`, generator `pcbnew` 9.0. The schematic and PCB are the same design generation: every new part (J8, U6, Q1–Q6, R29–R33, R35–R40, L1, C18–C26, D6, FB5–FB7, Headphones1/RV) appears in both, and the removed parts (J2, FB1, 10R R21, THT C14) are absent from both.

**Truth hierarchy for rev 3:** unlike rev 2, the `.kicad_pcb` carries the filled pour, so it is copper truth. No rev-3 Gerbers exist (pre-fab review), so there is no fab snapshot to cross-check against; the Gerbers in `kicad_out/rev3/gerbers/` are plotted from this file and are derived, not independent.

## 2. What changed (netlist + footprint diff)

**Removed:** J2 (HiLetgo SSD1306 I2C OLED), FB1, R21 (10Ω OLED damper, the duplicate refdes), C14 (470µF THT), C17 (100nF), nets `/I2C_SCL`, `/I2C_SDA`, `/OLED_HOT`, `/+9V_FILT`; LED1/LED2 stock `LED_RGB_5050-6` footprint.

**Added:**
- SPI OLED header **J8** (20-pin, `Retroactive_Custom_Parts:Newhaven2.7_OLED`, value NHD-2.7-12864WDW3) on nets `/RES_SPI` (A1.1), `/CS_SPI` (A1.8), `/SCLK_SPI` (A1.9), `/SD_IN_SPI` (A1.11), `/DC_SPI` (A1.28) and a new rail `/+3V3_OLED`.
- Buck regulator **U6** TPS62172DSG + **L1** 2.2µH + **C25** 10µF + **C26** 22µF + **R33** 100k; nets `/DSY_VIN`, `/+9V_FLAG`, `Net-(U6-EN)`, `Net-(U6-PG)`, `Net-(U6-SW)`.
- **D6** Schottky; ferrites **FB5–FB7**; electrolytics **C15, C17–C22** (100µF SMD) + **C24** (100µF THT) + **C23** (100nF axial THT); **R29–R32** 3.3Ω 1W 2512.
- LED drivers **Q1–Q6** MMBT3904 + **R35–R40** 1k; LED1/LED2 moved to custom footprint `LED_RGB_5050-6_Retroactive Pin Out`; six new `Net-(LEDx-Ay)` anode nets and `Net-(Qx-B)` base nets.
- Dual-gang pot **Headphones1** (B10k, `DualGang_Headphone_PTD902-2015K-B103`); schematic symbol is unannotated (`RV`).
- Encoder click nets `/ENCL_CLICK` → A1.22 and `/ENCR_CLICK` → A1.29 are now routed (22 and 24 segments respectively).
- Previously-unconnected A1 pins 1 (USB_ID), 22 (ADC_0), 28 (ADC_6) are now used (RES_SPI, ENCL_CLICK, DC_SPI).

**Changed:** R4 33Ω 0603 → 1210; FB2–FB7 part changed from 600Ω/200mA (C1002) to 120Ω/2A (C14709); C14 is now a 100nF 0603.

## 3. Copper baseline

| Metric | Rev 2 | Rev 3 |
|---|---|---|
| Track at 0.10 mm | 557 segs, **3.85 m** | 68 segs, **0.07 m** |
| Track at 0.20 mm | 259 segs, 0.89 m | 261 segs, 0.86 m |
| Track at 0.30 mm | — | 580 segs, 3.66 m |
| Track at 0.50 mm | — | 123 segs, 0.43 m |
| Vias | 94 × 0.6/0.3 | 244 × 0.6/0.3 |
| Board outline | 165 × 102 mm | 165.3 × 101.8 mm |
| Unconnected items (DRC) | 53 | **0** |

## 4. ERC / DRC baselines (`kicad_out/rev3/`)

ERC (51): 19 footprint_link_issues + 12 lib_symbol_mismatch (library noise, expected), **14 pin_not_connected** (10 × P2 USB-C SS/SBU pins, 4 × J8 pins 3/9/15/18), **4 power_pin_not_driven** (A1 VIN, U4 VDD, #PWR01, U6 VIN), **1 label_dangling** (`SWA`), 1 multiple_net_names (GND/SWB). Note: ERC reported **no `unannotated` errors** even though the schematic contains symbols with references `U` ×5, `L`, `RV`, `Q` — dispositioned in Pass 3.

DRC as-is (569): 199 silk_overlap, 199 silk_over_copper, 49 silk_edge_clearance, 69+19 lib footprint warnings, **17 clearance errors** (U3/U4 fine-pitch pad-to-pad 0.15 mm vs 0.2 netclass — same as rev-2 F-009), **8 starved_thermal**, **5 copper_edge_clearance** (3 × `/+3V3_D` track at 0.451 mm, 2 × SW1 pads at 0.41 mm, vs the project's 0.5 mm rule), **2 drill_out_of_range** (U6 thermal vias 0.25 mm vs project min 0.3), 2 via_dangling (`/LED_2_R`, `/LED_2_B`).

DRC with JLCPCB minimums on a scratchpad copy (590): identical error set except copper_edge_clearance disappears (JLC limit 0.2 mm) and silk_edge_clearance rises to 75. **Zero track-width and zero trace-spacing violations at 0.10/0.10 mm.**

## 5. Threshold sources used in this review

| Source | Status 2026-10-09 |
|---|---|
| JLCPCB capabilities page | fetched live (values in PASS1) |
| Newhaven NHD-2.7-12864WDW3 datasheet | fetched (PDF → text, scratchpad `datasheets/NHD.txt`): SSD1322, VDD 3.0–3.5 V, default jumper powers panel boost from VDD, **IDD 345 mA typ / 375 mA max at 3.3 V 100% on**, 4-wire SPI = BS1 0 / BS0 0, pin 18 /SHDN internally pulled high |
| TI TPS62172 datasheet SLVSAT8 | fetched (PDF → text) |
| Daisy Seed datasheet v1.0.5 | **host blocked by the session proxy** (daisy.audio, electrokit mirror, GitHub API). Pin functions taken from the stock KiCad symbol `MCU_Module:Electrosmith_Daisy_Seed_Rev4` embedded in the schematic and libDaisy `daisy_seed.cpp`; 3.3V-only pin list (24, 25, 28, 29, 30) carried over from the rev-2 citation of Table 1 |
| Cree CLS6B-FKW datasheet | **host blocked**; LED Vf treated as assumed where used |
