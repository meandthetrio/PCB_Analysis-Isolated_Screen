# Pass 4 (Rev 3) — Three-Way BOM Cross-Check
**Date:** 2026-10-09 · **Truth checked:** intent (rev-3 `.kicad_sch` / `.kicad_pcb`) — no rev-3 Gerbers exist yet; paste check uses the F/B paste layers plotted from the rev-3 board (`kicad_out/rev3/gerbers/`).
**Sources:** `rev3/ManifoldRe_BOM_NEW - Excel Format (rev3).xls` (36 BOM lines, 90 designators, 1 sheet, JLCPCB format Comment/Designator/Footprint/JLCPCB Part #) ↔ `rev3/WavetableController.kicad_sch` (110 non-power symbols, parser validated 110/110 against `kicad-cli` netlist) ↔ `rev3/WavetableController.kicad_pcb` (110 footprints, 110 unique refs). Supporting: `kicad_out/rev3/pos.csv` (105 rows), `kicad_out/rev3/netlist.xml`, JLCPCB part pages fetched 2026-10-09, stock KiCad 9.0.9 footprint libraries.
**Scripts:** `analysis/rev3/scripts/pass4/` (`sch_symbols.py`, `pcb_footprints.py`, `bom_join.py`, `paste_gerber.py`, `bom_diff.py`, `fp_compare.py`, `pad_nets.py`) plus the raw outputs `join.csv`, `bom_lines.csv`, `summary.txt`. Updates the rev-2 review in `analysis/PASS4_BOM.md`.

## Verdict summary
- **The join is clean.** 90 BOM designators ↔ 90 schematic symbols ↔ 90 PCB footprints, all three-way. **Zero** BOM-only (phantom) designators, **zero** PCB-only or schematic-only parts, **zero** duplicate refdes in the PCB, **zero** designators on two BOM lines. Rev 2's S1/S2 phantom line and the duplicate R21 are gone (F-003, F-013, F-025 → FIXED).
- **Values: 90/90 consistent** (scripted token match of schematic Value vs BOM Comment, with known-answer self-tests). **MPNs of all 11 new/changed LCSC numbers confirmed** against JLCPCB part pages (U6 = TPS62172DSGR, L1 = DFE201610P-2R2M=P2, Q1–Q6 = MMBT3904, FB = BLM18PG121SN1D 120 Ω/2 A, …).
- **Footprints: 89/90 consistent.** The one mismatch is real: **L1** is a 2.0×1.6 mm (0806/2016) inductor placed on a generic **0805 (2012) inductor land pattern** in both schematic and PCB (R3-P4-02).
- **LED1/LED2 are still the only SMD parts missing from the BOM**, and the top paste layer still contains exactly their 12 openings (F-002 / F-034 → STILL OPEN; R3-P4-01).
- **No hand-assembly sheet** — 18 through-hole parts remain off-BOM, now including the OLED rail's bulk/decoupling caps C24/C23 (F-026 → STILL OPEN; R3-P4-03).
- **Three refdes were silently repurposed between rev 2 and rev 3** (C14 470 µF THT → 100 nF 0603; C17 100 nF → 100 µF electrolytic; C15 10 µF/100 V → 100 µF/35 V), which invalidates rev-2 notes that cite them by refdes (R3-P4-06).
- Correction to the pass brief: the schematic has **no unannotated symbols**. The `U`, `L`, `RV`, `Q`, `J`… references the brief mentions are the default `Reference` properties inside the file's `lib_symbols` cache, not placed instances; the dual pot is `Headphones1` in schematic, netlist and PCB alike.

## What changed since rev 2 (scripted `bom_diff.py`)
rev 2: 31 lines / 62 designators → rev 3: 36 lines / 90 designators.
- **Removed:** FB1, S1, S2.
- **Added (31):** C14, C18–C22, C25, C26, D6, FB5–FB7, L1, Q1–Q6, R29–R33, R35–R40, U6.
- **Changed part:** FB2–FB4 C1002 (600 Ω/200 mA, Basic) → C14709 (120 Ω/2 A, Basic); R4 C23140 0603 33 Ω (Basic) → C2907549 1210 33 Ω 500 mW (Extended); C15 C72482 (10 µF 100 V) → C3339 (100 µF 35 V); C17 C1590 (100 nF 0603) → C3339 (100 µF 6.3×7.7 electrolytic).

## Findings

| ID | Class | Status | Finding | Evidence |
|---|---|---|---|---|
| R3-P4-01 | VIOLATION | confirmed | **LED1/LED2 (CLS6B-FKW, top-side 5050 RGB) are still absent from the BOM** while the board expects them: both have 6 F.Paste pads each, the plotted F_Paste Gerber contains exactly 12 flashes which map 12/12 (0 unmatched) onto LED1/LED2 pads, and both appear in `pos.csv`. They remain the only SMD parts in the "sch+pcb but not BOM" bucket. Boards will again return from JLCPCB SMT assembly without LEDs. Carries F-002/F-034 forward unchanged. | `summary.txt` ("Paste pads but no BOM line: LED1(F,top), LED2(F,top)"); `paste_gerber.py` F_Paste 12 flashes → LED1:6 LED2:6; `pos.csv` rows LED1/LED2 |
| R3-P4-02 | JUDGMENT (strong) | confirmed | **L1 land pattern does not fit the part.** BOM: C237554 = Murata DFE201610P-2R2M=P2, package "0806" (2.0×1.6×1.0 mm). Schematic *and* PCB footprint: `Inductor_SMD:L_0805_2012Metric` — the IPC nominal pattern for a 2.0×**1.25** mm body: pads 0.875×1.20 mm at ±1.062 (inner edges ±0.625, outer ±1.50). KiCad's stock `L_Murata_DFE201610P` (derived from the Murata drawing; murata.com is blocked from this session) is pads **0.55×1.60 at ±0.725** (inner ±0.45, outer ±1.00), courtyard 2.59×2.19. Consequences: pads are 0.4 mm narrower than the 1.6 mm terminations, start 0.175 mm further out than the terminal inner edge, and overhang the body end by 0.5 mm; the pad/terminal overlap is ≈0.375×1.2 = 0.45 mm² per end vs 0.88 mm² on the reference pattern (≈50 %). It will usually solder, but it is a non-recommended pattern on the only inductor of the new OLED buck (hot loop + 1.4 A rated part). The BOM's own Footprint cell ("0806") already disagrees with the design ("0805"), which the join flags automatically. **Fix:** swap L1 to `Inductor_SMD:L_Murata_DFE201610P` (stock library) in the schematic and update the PCB. | `fp_compare.py` output; `join.csv` L1 fp_check=MISMATCH "bom 0806 vs pcb 0805"; JLCPCB C237554 page (MPN, package 0806) |
| R3-P4-03 | JUDGMENT | confirmed | **Still no hand-assembly list** (F-026). The .xls has one sheet. 18 THT parts are off-BOM (table below). The pattern rev 2 warned about — a noise-critical bulk cap living only in hand-solder — recurs: the new dedicated OLED rail `/+3V3_OLED` (U6 buck output) is bulked by **C24 100 µF radial THT + C23 100 nF axial THT**, neither on any BOM. Recommend a second sheet (or a KiCad BOM export with `in_bom` filtering) listing value, footprint, source and net for every THT part. | `summary.txt` THT bucket (18); `pad_nets.py` C23/C24 on /+3V3_OLED; `xlrd` sheet_names = 1 |
| R3-P4-04 | JUDGMENT | confirmed | **"Exclude from position files" is applied inconsistently**: only J3–J7 carry the flag; 13 other THT parts (A1, C23, C24, ENCL1, ENCR1, Headphones1, J8, MK1, SW1, TAC_SHIFT_L1/R1, TAC_SWITCH_1/2) plus the off-BOM LEDs are in the pick-and-place export (105 rows = 110 − 5). JLCPCB's uploader will list 15 CPL entries with no BOM match; harmless, but it buries the two entries that matter (LED1/LED2). Set the flag on all THT parts, or filter the CPL export to SMD-only. | `pcb_footprints.py` excl_pos column; `pos.csv` row count |
| R3-P4-05 | JUDGMENT | confirmed | **BOM file hygiene (harmless to JLCPCB matching, which keys on the LCSC column — but every item is a sign the sheet is hand-edited):** (a) Footprint column stored as *numbers* on 24/36 rows (Excel coerced "0603" → `603.0`, "0806" → `806.0`, "1210" → `1210.0` …); (b) row 15 (100 µF line) Footprint cell starts with a newline (`"\nSMD,D6.3xL7.7mm"`); (c) designator spacing inconsistent on 9 rows (`C1, C4, C5, C8, C11,C14,C16`, `R21, R24,R25…`, `C6, C7,C15,…`) — rows 8, 12, 13, 14, 15, 18, 21, 27, 30; (d) Comment mojibake on 20/36 rows in **two** corruption styles (UTF-8-read-as-cp1252: `Œ©`=Ω, `‚ÑÉ`=℃, `¬±`=±; and dropped characters: `-55_~+150_`, `±100ppm/_`); (e) row 2 (D1) Comment lost its temperature prefix (`"1 Independent 1A 20V…"`). No designator appears on two lines; no LCSC number appears on two lines. | `bom_lines.csv` (fp_note, spacing_oddity, mojibake columns) |
| R3-P4-06 | JUDGMENT | confirmed | **Refdes repurposed across revisions — documentation hazard.** C14 was the 470 µF THT OLED-noise-fix cap in rev 2 (F-019/F-026 cite it); in rev 3 **C14 is a 100 nF 0603** at (145.25, 88.0). C17 went from 100 nF 0603 to a 100 µF electrolytic; C15 from 10 µF/100 V to 100 µF/35 V. Any rev-2 note, rework instruction or photo that names C14/C15/C17 now points at a different part. Not a build error (all three are consistent in rev 3), but worth a line in the rev-3 change log, and the rev-2 ledger entries should be annotated. | `bom_diff.py` changed/added lists; `join.csv` rows C14/C15/C17 |
| R3-P4-07 | JUDGMENT (cost) | confirmed | **Extended-part count.** New/changed lines that are JLCPCB *Extended* (per-line handling fee): U6 C59873, L1 C237554, R4 C2907549 (its rev-2 predecessor C23140 0603 33 Ω is Basic), R29–R32 C2960677, **R35–R40 C14676 1 kΩ 5 %** (C21190 1 kΩ 1 % 0603 is Basic — a free swap), C3339 ×9, D2–D6 C727114. *Basic:* Q1–Q6 C20526, FB2–FB7 C14709, C25 C15850, C26 C45783. Only R35–R40 looks like an avoidable Extended line; R4's 1210/500 mW choice should be justified by whoever changed it (33 Ω MIDI series resistor in rev 2 — Pass 5 to confirm its rev-3 role). | JLCPCB part pages (Basic/Extended badge), fetched 2026-10-09 |
| R3-P4-08 | PASS | confirmed | **Everything else passes:** 90/90 values; R4 is 1210 in BOM/sch/PCB (pads 1.30×2.65); C25/C26 are 0805 in all three (pads 1.175×1.45 hand-solder variant); R29–R32 are 2512 in all three (pads 1.40×3.35); all nine 100 µF (C6, C7, C15, C17–C22) are `CP_Elec_6.3x7.7` in sch+PCB and "SMD,D6.3xL7.7mm" in BOM, matching C3339 (RVT1V101M0607, 6.3×7.7); U6 is `WSON-8-1EP_2x2mm_P0.5mm_EP0.9x1.6mm_ThermalVias` in sch+PCB vs BOM "WSON-8-EP(2x2)" and TI DSG; U6's stock symbol pin map (2=VIN 3=EN 7=SW 6=VOS 5=FB 8=PG 1=PGND 4=AGND 9=PAD) lands on sensible nets (VIN+EN tied with C25 10 µF, SW→L1→/+3V3_OLED, VOS→/+3V3_OLED, FB→GND for the fixed-3V3 variant, PG pulled up by R33 100 k); FB2–FB7 use `Diode_SMD:D_0603_1608Metric` (pads 0.88×0.95 — a 0603 chip land under a different library name; fine, but `Inductor_SMD:L_0603_1608Metric` would be the tidy choice); D1 (C385198) vs D2–D6 (C727114) both Schottky, as in rev 2; every BOM line has paste pads on the board (no "BOM line but no paste" entries); no DNP / exclude-from-BOM flags set in the PCB. | `summary.txt`, `join.csv` |

## LCSC part sanity (JLCPCB part pages, fetched 2026-10-09; lcsc.com pages also loaded but carry no Basic/Extended badge)

| LCSC | BOM line | Fetched MPN / maker | Key specs on page | Matches sch Value / footprint? | JLC class |
|---|---|---|---|---|---|
| C59873 | U6 | **TPS62172DSGR**, TI | 500 mA fixed 3.3 V buck, 3–17 V in, 2.25 MHz, WSON-8-EP 2×2 | sch `TPS62172DSG` ✓; PCB WSON-8-1EP 2x2 P0.5 EP0.9x1.6 ✓ | Extended |
| C237554 | L1 | **DFE201610P-2R2M=P2**, Murata | 2.2 µH ±20 %, 1.4 A rated / 2 A Isat, 168 mΩ, package "0806" | sch `2.2UH DFE201610P-2R2M=P2` ✓; **footprint ✗ (R3-P4-02)** | Extended |
| C20526 | Q1–Q6 | **MMBT3904** (range 100–300), JSCJ | NPN 40 V 200 mA SOT-23 | sch `MMBT3904` / SOT-23 ✓ | Basic |
| C14709 | FB2–FB7 | **BLM18PG121SN1D**, Murata | 120 Ω @100 MHz, 2 A, 50 mΩ, 0603 | sch generic `FerriteBead` / 0603-class land ✓ | Basic |
| C2907549 | R4 | **FRC1210J330 TS**, FOJAN | 33 Ω 5 % 500 mW 1210 | sch `33R` / R_1210 ✓ | Extended |
| C2960677 | R29–R32 | **FRC2512J3R3 TS**, FOJAN | 3.3 Ω 5 % 1 W 2512 (page lists tempco inconsistently, ±200 vs ±400 ppm) | sch `3.3R` / R_2512 ✓ | Extended |
| C15850 | C25 | **CL21A106KAYNNNE**, Samsung | 10 µF 25 V X5R 0805 | sch `10UF` / C_0805 ✓ | Basic |
| C45783 | C26 | **CL21A226MAQNNNE**, Samsung | 22 µF 25 V X5R 0805 | sch `22UF` / C_0805 ✓ | Basic |
| C14676 | R35–R40 | **RC0603JR-071KL**, Yageo | 1 kΩ 5 % 0603 | sch `1K` / R_0603 ✓ | Extended (C21190 1 k 1 % is Basic) |
| C727114 | D2–D6 | **1N5817WS**, TWGMC | 20 V 1 A Schottky SOD-323 | sch `D_Schottky` / D_SOD-323 ✓ | Extended |
| C3339 | C6,C7,C15,C17–C22 | **RVT1V101M0607**, Honor | 100 µF 35 V, 6.3×7.7 mm | sch `100UF` / CP_Elec_6.3x7.7 ✓ | Extended |
| (ref) C23140 | rev-2 R4 | 0603WAF330JT5E, UNI-ROYAL | 33 Ω 0603 | — | Basic |
| (ref) C1002 | rev-2 FB | GZ1608D601TF, Sunlord | 600 Ω 200 mA | — | Basic |

## Hand-solder list (sch+PCB, not in BOM) — the sheet R3-P4-03 asks for

| Ref | Value (sch) | Footprint | Side | Nets (from PCB) |
|---|---|---|---|---|
| A1 | Electrosmith Daisy Seed Rev4 | Retroactive_Custom_Parts:Electrosmith_Daisy_Seed_Cuz (40 PTH) | bottom | all MCU nets |
| C23 | 100 nF | Capacitor_THT:C_Axial_L3.8mm_D2.6mm_P7.50mm_Horizontal | bottom | /+3V3_OLED ↔ GND |
| C24 | 100 µF | Capacitor_THT:CP_Radial_D6.3mm_P2.50mm | bottom | /+3V3_OLED ↔ GND |
| ENCL1 | RotaryEncoder_Switch | Retroactive_Custom_Parts:RotaryEncoder_Alps_Vertical_H20mm | top | /ENCL_A /ENCL_B /ENCL_CLICK GND |
| ENCR1 | RotaryEncoder_Switch | same | top | /ENCR_A /ENCR_B /ENCR_CLICK GND |
| Headphones1 | B10k Dual (PTD902-2015K-B103) | Retroactive_Custom_Parts:DualGang_Headphone_PTD902-2015K-B103 | bottom | AUDIO_OUT_L/R, Net-(C2-Pad1), Net-(C3-Pad1), GND |
| J3 | MIDI OUTPUT 3.5 mm | Connector_Audio:Jack_3.5mm_CUI_RetroactiveCustom | bottom | Net-(J3-PadR), Net-(J3-PadT), GND |
| J4 | AUDIO INPUT 3.5 mm | same | bottom | AUDIO_IN_L, GND |
| J5 | AUDIO OUTPUT 3.5 mm | same | bottom | AUDIO_OUT_L/R, GND |
| J6 | MIDI INPUT 3.5 mm | same | bottom | /MIDI_IN_TIP, /MIDI_IN_RING, GND |
| J7 | PHONES 3.5 mm | same | bottom | HEADPHONE_OUT_L/R, GND |
| J8 | NHD-2.7-12864WDW3 OLED, 20-pin | Retroactive_Custom_Parts:Newhaven2.7_OLED | top | /+3V3_OLED, SPI (/SCLK_SPI /SD_IN_SPI /CS_SPI /DC_SPI /RES_SPI), GND; pins 3/9/15/18 unconnected |
| MK1 | Microphone_Condenser | Sensor_Audio:POM-2244P-C3310-2-R | top | /MIC_HOT, GND |
| SW1 | Power ON/OFF slide (DigiKey 1101A4VQEA) | Retroactive_Custom_Parts:DigiKey_1101A4VQEA_SPDT_Vertical_SlideSwitch | bottom | Net-(SW1-A), Net-(D3-A) |
| TAC_SHIFT_L1 | SW_Push (90°) | Retroactive_Custom_Parts:Retroactive_90DegSW_Tactile | bottom | /TAC_SHIFT_L, GND |
| TAC_SHIFT_R1 | SW_Push (90°) | same | bottom | /TAC_SHIFT_R, GND |
| TAC_SWITCH_1 | SW_MEC_5E 6 mm H9.5 | Retroactive_Custom_Parts:Retroactive_THT_TACTSW_6mm_H9.5mm | top | /TAC_SWITCH_1, GND |
| TAC_SWITCH_2 | SW_MEC_5E 6 mm H9.5 | same | top | /TAC_SWITCH_2, GND |
| *(SMD, assembly gap)* LED1, LED2 | CLS6B-FKW | Retroactive_Custom_Parts:LED_RGB_5050-6_Retroactive Pin Out | top | /LED_x_R/G/B, R21/R24–R28 nets |

## Rev-2 finding status

| Rev-2 ID | Rev-2 finding | Rev-3 status | Evidence |
|---|---|---|---|
| F-002 | LED1/LED2 missing from BOM | **STILL OPEN** | 90-way join: LED1/LED2 are the only SMD sch+pcb parts with no BOM line; both in `pos.csv` |
| F-034 | Top paste = 12 LED apertures with no BOM line | **STILL OPEN** | `paste_gerber.py`: F_Paste 12 flashes → LED1:6, LED2:6, 0 unmatched |
| F-003 | S1/S2 phantom SMD tactile line | **FIXED** | `bom_diff.py` removed [FB1, S1, S2]; join has 0 BOM-only designators |
| F-013 | Duplicate refdes R21 in PCB | **FIXED** | `pcb_footprints.py`: 110 footprints, 110 unique refs, duplicate list empty; single R21 = 300R at (153.25, 130.5) |
| F-025 | Dup-R21 pick-and-place trap (300 Ω at OLED damper) | **FIXED** (by removal) | One R21 ↔ one BOM line; the 10 Ω OLED damper no longer exists anywhere — the OLED now has its own buck rail `/+3V3_OLED` (U6/L1/C26/C24/C23). Pass 2 should confirm F-020 is closed by that design change rather than dropped by accident |
| F-026 | No hand-assembly list | **STILL OPEN** | One-sheet .xls; 18 THT parts off-BOM incl. the new OLED-rail bulk caps C24/C23 |
| (rev-2 housekeeping) | Mojibake, "ManifoldRe" filename vs "WaveControllerBOM_NEW" sheet | unchanged | 20/36 rows mojibake; same sheet name |

## Full three-way join (110 refs)
Disposition key: ALL THREE = BOM ∩ sch ∩ pcb. Paste: F/B = footprint has pads on F.Paste/B.Paste. Value/Fp chk only computed for ALL-THREE rows.

| Ref | Disposition | BOM line (row:LCSC) | BOM fp | Sch value | Sch footprint | PCB footprint | Side/Tech | Paste | Value chk | Fp chk |
|---|---|---|---|---|---|---|---|---|---|---|
| A1 | SCH+PCB not BOM: THT -> hand-solder |  |  | Electrosmith_Daisy_Seed_Rev4 | Electrosmith_Daisy_Seed_Cuz | Electrosmith_Daisy_Seed_Cuz | bottom/THT | - | - | - |
| C1 | ALL THREE | row8:C1590 | 0603 | 100NF | C_0603_1608Metric | C_0603_1608Metric | bottom/SMD | B | OK | OK |
| C2 | ALL THREE | row13:C1623 | 0603 | 470NF | C_0603_1608Metric | C_0603_1608Metric | bottom/SMD | B | OK | OK |
| C3 | ALL THREE | row13:C1623 | 0603 | 470NF | C_0603_1608Metric | C_0603_1608Metric | bottom/SMD | B | OK | OK |
| C4 | ALL THREE | row8:C1590 | 0603 | 100NF | C_0603_1608Metric | C_0603_1608Metric | bottom/SMD | B | OK | OK |
| C5 | ALL THREE | row8:C1590 | 0603 | 100NF | C_0603_1608Metric | C_0603_1608Metric | bottom/SMD | B | OK | OK |
| C6 | ALL THREE | row15:C3339 | SMD,D6.3xL7.7mm | 100UF | CP_Elec_6.3x7.7 | CP_Elec_6.3x7.7 | bottom/SMD | B | OK | OK |
| C7 | ALL THREE | row15:C3339 | SMD,D6.3xL7.7mm | 100UF | CP_Elec_6.3x7.7 | CP_Elec_6.3x7.7 | bottom/SMD | B | OK | OK |
| C8 | ALL THREE | row8:C1590 | 0603 | 100NF | C_0603_1608Metric | C_0603_1608Metric | bottom/SMD | B | OK | OK |
| C9 | ALL THREE | row21:C1607 | 0603 | 2.2UF | C_0603_1608Metric | C_0603_1608Metric | bottom/SMD | B | OK | OK |
| C10 | ALL THREE | row13:C1623 | 0603 | 470NF | C_0603_1608Metric | C_0603_1608Metric | bottom/SMD | B | OK | OK |
| C11 | ALL THREE | row8:C1590 | 0603 | 100NF | C_0603_1608Metric | C_0603_1608Metric | bottom/SMD | B | OK | OK |
| C12 | ALL THREE | row25:C1705 | 0603 | 4.7UF | C_0603_1608Metric | C_0603_1608Metric | bottom/SMD | B | OK | OK |
| C13 | ALL THREE | row21:C1607 | 0603 | 2.2UF | C_0603_1608Metric | C_0603_1608Metric | bottom/SMD | B | OK | OK |
| C14 | ALL THREE | row8:C1590 | 0603 | 100NF | C_0603_1608Metric | C_0603_1608Metric | bottom/SMD | B | OK | OK |
| C15 | ALL THREE | row15:C3339 | SMD,D6.3xL7.7mm | 100UF | CP_Elec_6.3x7.7 | CP_Elec_6.3x7.7 | bottom/SMD | B | OK | OK |
| C16 | ALL THREE | row8:C1590 | 0603 | 100NF | C_0603_1608Metric | C_0603_1608Metric | bottom/SMD | B | OK | OK |
| C17 | ALL THREE | row15:C3339 | SMD,D6.3xL7.7mm | 100UF | CP_Elec_6.3x7.7 | CP_Elec_6.3x7.7 | bottom/SMD | B | OK | OK |
| C18 | ALL THREE | row15:C3339 | SMD,D6.3xL7.7mm | 100UF | CP_Elec_6.3x7.7 | CP_Elec_6.3x7.7 | bottom/SMD | B | OK | OK |
| C19 | ALL THREE | row15:C3339 | SMD,D6.3xL7.7mm | 100UF | CP_Elec_6.3x7.7 | CP_Elec_6.3x7.7 | bottom/SMD | B | OK | OK |
| C20 | ALL THREE | row15:C3339 | SMD,D6.3xL7.7mm | 100UF | CP_Elec_6.3x7.7 | CP_Elec_6.3x7.7 | bottom/SMD | B | OK | OK |
| C21 | ALL THREE | row15:C3339 | SMD,D6.3xL7.7mm | 100UF | CP_Elec_6.3x7.7 | CP_Elec_6.3x7.7 | bottom/SMD | B | OK | OK |
| C22 | ALL THREE | row15:C3339 | SMD,D6.3xL7.7mm | 100UF | CP_Elec_6.3x7.7 | CP_Elec_6.3x7.7 | bottom/SMD | B | OK | OK |
| C23 | SCH+PCB not BOM: THT -> hand-solder |  |  | 100NF | C_Axial_L3.8mm_D2.6mm_P7.50mm_Horizontal | C_Axial_L3.8mm_D2.6mm_P7.50mm_Horizontal | bottom/THT | - | - | - |
| C24 | SCH+PCB not BOM: THT -> hand-solder |  |  | 100UF | CP_Radial_D6.3mm_P2.50mm | CP_Radial_D6.3mm_P2.50mm | bottom/THT | - | - | - |
| C25 | ALL THREE | row34:C15850 | 0805 | 10UF | C_0805_2012Metric_Pad1.18x1.45mm_HandSolder | C_0805_2012Metric_Pad1.18x1.45mm_HandSolder | bottom/SMD | B | OK | OK |
| C26 | ALL THREE | row35:C45783 | 0805 | 22UF | C_0805_2012Metric_Pad1.18x1.45mm_HandSolder | C_0805_2012Metric_Pad1.18x1.45mm_HandSolder | bottom/SMD | B | OK | OK |
| D1 | ALL THREE | row2:C385198 | SOD-323 | D_Schottky | D_SOD-323 | D_SOD-323 | bottom/SMD | B | OK | OK |
| D2 | ALL THREE | row3:C727114 | SOD-323 | D_Schottky | D_SOD-323 | D_SOD-323 | bottom/SMD | B | OK | OK |
| D3 | ALL THREE | row3:C727114 | SOD-323 | D_Schottky | D_SOD-323 | D_SOD-323 | bottom/SMD | B | OK | OK |
| D4 | ALL THREE | row3:C727114 | SOD-323 | D_Schottky | D_SOD-323 | D_SOD-323 | bottom/SMD | B | OK | OK |
| D5 | ALL THREE | row3:C727114 | SOD-323 | D_Schottky | D_SOD-323 | D_SOD-323 | bottom/SMD | B | OK | OK |
| D6 | ALL THREE | row3:C727114 | SOD-323 | D_Schottky | D_SOD-323 | D_SOD-323 | bottom/SMD | B | OK | OK |
| ENCL1 | SCH+PCB not BOM: THT -> hand-solder |  |  | RotaryEncoder_Switch | RotaryEncoder_Alps_Vertical_H20mm | RotaryEncoder_Alps_Vertical_H20mm | top/THT | - | - | - |
| ENCR1 | SCH+PCB not BOM: THT -> hand-solder |  |  | RotaryEncoder_Switch | RotaryEncoder_Alps_Vertical_H20mm | RotaryEncoder_Alps_Vertical_H20mm | top/THT | - | - | - |
| FB2 | ALL THREE | row20:C14709 | 0603 | FerriteBead | D_0603_1608Metric | D_0603_1608Metric | bottom/SMD | B | OK | OK |
| FB3 | ALL THREE | row20:C14709 | 0603 | FerriteBead | D_0603_1608Metric | D_0603_1608Metric | bottom/SMD | B | OK | OK |
| FB4 | ALL THREE | row20:C14709 | 0603 | FerriteBead | D_0603_1608Metric | D_0603_1608Metric | bottom/SMD | B | OK | OK |
| FB5 | ALL THREE | row20:C14709 | 0603 | FerriteBead | D_0603_1608Metric | D_0603_1608Metric | bottom/SMD | B | OK | OK |
| FB6 | ALL THREE | row20:C14709 | 0603 | FerriteBead | D_0603_1608Metric | D_0603_1608Metric | bottom/SMD | B | OK | OK |
| FB7 | ALL THREE | row20:C14709 | 0603 | FerriteBead | D_0603_1608Metric | D_0603_1608Metric | bottom/SMD | B | OK | OK |
| Headphones1 | SCH+PCB not BOM: THT -> hand-solder |  |  | B10k Dual | DualGang_Headphone_PTD902-2015K-B103 | DualGang_Headphone_PTD902-2015K-B103 | bottom/THT | - | - | - |
| J1 | ALL THREE | row26:C114916 | SMD | Barrel_Jack | Retroactive_SMDBarrelJack_CLIFF | Retroactive_SMDBarrelJack_CLIFF | bottom/SMD | B | OK | OK(generic) |
| J3 | SCH+PCB not BOM: THT -> hand-solder |  |  | MIDI OUTPUT | Jack_3.5mm_CUI_RetroactiveCustom | Jack_3.5mm_CUI_RetroactiveCustom | bottom/THT | - | - | - |
| J4 | SCH+PCB not BOM: THT -> hand-solder |  |  | AUDIO INPUT | Jack_3.5mm_CUI_RetroactiveCustom | Jack_3.5mm_CUI_RetroactiveCustom | bottom/THT | - | - | - |
| J5 | SCH+PCB not BOM: THT -> hand-solder |  |  | AUDIO OUTPUT | Jack_3.5mm_CUI_RetroactiveCustom | Jack_3.5mm_CUI_RetroactiveCustom | bottom/THT | - | - | - |
| J6 | SCH+PCB not BOM: THT -> hand-solder |  |  | MIDI INPUT | Jack_3.5mm_CUI_RetroactiveCustom | Jack_3.5mm_CUI_RetroactiveCustom | bottom/THT | - | - | - |
| J7 | SCH+PCB not BOM: THT -> hand-solder |  |  | PHONES | Jack_3.5mm_CUI_RetroactiveCustom | Jack_3.5mm_CUI_RetroactiveCustom | bottom/THT | - | - | - |
| J8 | SCH+PCB not BOM: THT -> hand-solder |  |  | NHD-2.7-12864WDW3 | Newhaven2.7_OLED | Newhaven2.7_OLED | top/THT | - | - | - |
| L1 | ALL THREE | row33:C237554 | 0806 | 2.2UH DFE201610P-2R2M=P2 | L_0805_2012Metric | L_0805_2012Metric | bottom/SMD | B | OK | MISMATCH (bom 0806 vs pcb 0805) |
| LED1 | SCH+PCB not BOM: SMD -> assembly gap |  |  | CLS6B-FKW | LED_RGB_5050-6_Retroactive Pin Out | LED_RGB_5050-6_Retroactive Pin Out | top/SMD | F | - | - |
| LED2 | SCH+PCB not BOM: SMD -> assembly gap |  |  | CLS6B-FKW | LED_RGB_5050-6_Retroactive Pin Out | LED_RGB_5050-6_Retroactive Pin Out | top/SMD | F | - | - |
| MK1 | SCH+PCB not BOM: THT -> hand-solder |  |  | Microphone_Condenser | POM-2244P-C3310-2-R | POM-2244P-C3310-2-R | top/THT | - | - | - |
| P1 | ALL THREE | row9:C114218 | SMD | Micro_SD_Card_Det2 | microSD_HC_Hirose_DM3AT-SF-PEJM5 | microSD_HC_Hirose_DM3AT-SF-PEJM5 | bottom/SMD | B | OK | OK(generic) |
| P2 | ALL THREE | row17:C393939 | SMD | USB_C31-S-RA-CS2-SMT-BK-T/R | USB_C_Receptacle_GCT_USB4105-xx-A_16P_TopMnt_Horizontal | USB_C_Receptacle_GCT_USB4105-xx-A_16P_TopMnt_Horizontal | bottom/SMD | B | OK | OK(generic) |
| Q1 | ALL THREE | row37:C20526 | SOT-23 | MMBT3904 | SOT-23 | SOT-23 | bottom/SMD | B | OK | OK |
| Q2 | ALL THREE | row37:C20526 | SOT-23 | MMBT3904 | SOT-23 | SOT-23 | bottom/SMD | B | OK | OK |
| Q3 | ALL THREE | row37:C20526 | SOT-23 | MMBT3904 | SOT-23 | SOT-23 | bottom/SMD | B | OK | OK |
| Q4 | ALL THREE | row37:C20526 | SOT-23 | MMBT3904 | SOT-23 | SOT-23 | bottom/SMD | B | OK | OK |
| Q5 | ALL THREE | row37:C20526 | SOT-23 | MMBT3904 | SOT-23 | SOT-23 | bottom/SMD | B | OK | OK |
| Q6 | ALL THREE | row37:C20526 | SOT-23 | MMBT3904 | SOT-23 | SOT-23 | bottom/SMD | B | OK | OK |
| R1 | ALL THREE | row28:C22859 | 0603 | 10R | R_0603_1608Metric | R_0603_1608Metric | bottom/SMD | B | OK | OK |
| R2 | ALL THREE | row4:C21189 | 0603 | 0R | R_0603_1608Metric | R_0603_1608Metric | bottom/SMD | B | OK | OK |
| R3 | ALL THREE | row4:C21189 | 0603 | 0R | R_0603_1608Metric | R_0603_1608Metric | bottom/SMD | B | OK | OK |
| R4 | ALL THREE | row29:C2907549 | 1210 | 33R | R_1210_3225Metric_Pad1.30x2.65mm_HandSolder | R_1210_3225Metric_Pad1.30x2.65mm_HandSolder | bottom/SMD | B | OK | OK |
| R5 | ALL THREE | row5:C1226 | 0603 | 220R | R_0603_1608Metric | R_0603_1608Metric | bottom/SMD | B | OK | OK |
| R6 | ALL THREE | row7:C22966 | 0603 | 270R | R_0603_1608Metric | R_0603_1608Metric | bottom/SMD | B | OK | OK |
| R7 | ALL THREE | row10:C25600 | 0603 | 47K | R_0603_1608Metric | R_0603_1608Metric | bottom/SMD | B | OK | OK |
| R8 | ALL THREE | row10:C25600 | 0603 | 47K | R_0603_1608Metric | R_0603_1608Metric | bottom/SMD | B | OK | OK |
| R9 | ALL THREE | row10:C25600 | 0603 | 47K | R_0603_1608Metric | R_0603_1608Metric | bottom/SMD | B | OK | OK |
| R10 | ALL THREE | row10:C25600 | 0603 | 47K | R_0603_1608Metric | R_0603_1608Metric | bottom/SMD | B | OK | OK |
| R11 | ALL THREE | row10:C25600 | 0603 | 47K | R_0603_1608Metric | R_0603_1608Metric | bottom/SMD | B | OK | OK |
| R12 | ALL THREE | row12:C23344 | 0603 | 22K | R_0603_1608Metric | R_0603_1608Metric | bottom/SMD | B | OK | OK |
| R13 | ALL THREE | row12:C23344 | 0603 | 22K | R_0603_1608Metric | R_0603_1608Metric | bottom/SMD | B | OK | OK |
| R14 | ALL THREE | row14:C4216 | 0603 | 33K | R_0603_1608Metric | R_0603_1608Metric | bottom/SMD | B | OK | OK |
| R15 | ALL THREE | row14:C4216 | 0603 | 33K | R_0603_1608Metric | R_0603_1608Metric | bottom/SMD | B | OK | OK |
| R16 | ALL THREE | row18:C23186 | 0603 | 5K1 | R_0603_1608Metric | R_0603_1608Metric | bottom/SMD | B | OK | OK |
| R17 | ALL THREE | row18:C23186 | 0603 | 5K1 | R_0603_1608Metric | R_0603_1608Metric | bottom/SMD | B | OK | OK |
| R18 | ALL THREE | row22:C14675 | 0603 | 100K | R_0603_1608Metric | R_0603_1608Metric | bottom/SMD | B | OK | OK |
| R19 | ALL THREE | row23:C22807 | 0603 | 150K | R_0603_1608Metric | R_0603_1608Metric | bottom/SMD | B | OK | OK |
| R20 | ALL THREE | row24:C4190 | 0603 | 2K2 | R_0603_1608Metric | R_0603_1608Metric | bottom/SMD | B | OK | OK |
| R21 | ALL THREE | row30:C23025 | 0603 | 300R | R_0603_1608Metric | R_0603_1608Metric | bottom/SMD | B | OK | OK |
| R22 | ALL THREE | row27:C22369937 | 0603 | 10k | R_0603_1608Metric | R_0603_1608Metric | bottom/SMD | B | OK | OK |
| R23 | ALL THREE | row27:C22369937 | 0603 | 10k | R_0603_1608Metric | R_0603_1608Metric | bottom/SMD | B | OK | OK |
| R24 | ALL THREE | row30:C23025 | 0603 | 300R | R_0603_1608Metric | R_0603_1608Metric | bottom/SMD | B | OK | OK |
| R25 | ALL THREE | row30:C23025 | 0603 | 300R | R_0603_1608Metric | R_0603_1608Metric | bottom/SMD | B | OK | OK |
| R26 | ALL THREE | row30:C23025 | 0603 | 300R | R_0603_1608Metric | R_0603_1608Metric | bottom/SMD | B | OK | OK |
| R27 | ALL THREE | row30:C23025 | 0603 | 300R | R_0603_1608Metric | R_0603_1608Metric | bottom/SMD | B | OK | OK |
| R28 | ALL THREE | row30:C23025 | 0603 | 300R | R_0603_1608Metric | R_0603_1608Metric | bottom/SMD | B | OK | OK |
| R29 | ALL THREE | row31:C2960677 | 2512 | 3.3R | R_2512_6332Metric_Pad1.40x3.35mm_HandSolder | R_2512_6332Metric_Pad1.40x3.35mm_HandSolder | bottom/SMD | B | OK | OK |
| R30 | ALL THREE | row31:C2960677 | 2512 | 3.3R | R_2512_6332Metric_Pad1.40x3.35mm_HandSolder | R_2512_6332Metric_Pad1.40x3.35mm_HandSolder | bottom/SMD | B | OK | OK |
| R31 | ALL THREE | row31:C2960677 | 2512 | 3.3R | R_2512_6332Metric_Pad1.40x3.35mm_HandSolder | R_2512_6332Metric_Pad1.40x3.35mm_HandSolder | bottom/SMD | B | OK | OK |
| R32 | ALL THREE | row31:C2960677 | 2512 | 3.3R | R_2512_6332Metric_Pad1.40x3.35mm_HandSolder | R_2512_6332Metric_Pad1.40x3.35mm_HandSolder | bottom/SMD | B | OK | OK |
| R33 | ALL THREE | row22:C14675 | 0603 | 100K | R_0603_1608Metric | R_0603_1608Metric | bottom/SMD | B | OK | OK |
| R35 | ALL THREE | row36:C14676 | 0603 | 1K | R_0603_1608Metric | R_0603_1608Metric | bottom/SMD | B | OK | OK |
| R36 | ALL THREE | row36:C14676 | 0603 | 1K | R_0603_1608Metric | R_0603_1608Metric | bottom/SMD | B | OK | OK |
| R37 | ALL THREE | row36:C14676 | 0603 | 1K | R_0603_1608Metric | R_0603_1608Metric | bottom/SMD | B | OK | OK |
| R38 | ALL THREE | row36:C14676 | 0603 | 1K | R_0603_1608Metric | R_0603_1608Metric | bottom/SMD | B | OK | OK |
| R39 | ALL THREE | row36:C14676 | 0603 | 1K | R_0603_1608Metric | R_0603_1608Metric | bottom/SMD | B | OK | OK |
| R40 | ALL THREE | row36:C14676 | 0603 | 1K | R_0603_1608Metric | R_0603_1608Metric | bottom/SMD | B | OK | OK |
| SW1 | SCH+PCB not BOM: THT -> hand-solder |  |  | Power ON/OFF | DigiKey_1101A4VQEA_SPDT_Vertical_SlideSwitch | DigiKey_1101A4VQEA_SPDT_Vertical_SlideSwitch | bottom/THT | - | - | - |
| TAC_SHIFT_L1 | SCH+PCB not BOM: THT -> hand-solder |  |  | SW_Push | Retroactive_90DegSW_Tactile | Retroactive_90DegSW_Tactile | bottom/THT | - | - | - |
| TAC_SHIFT_R1 | SCH+PCB not BOM: THT -> hand-solder |  |  | SW_Push | Retroactive_90DegSW_Tactile | Retroactive_90DegSW_Tactile | bottom/THT | - | - | - |
| TAC_SWITCH_1 | SCH+PCB not BOM: THT -> hand-solder |  |  | SW_MEC_5E | Retroactive_THT_TACTSW_6mm_H9.5mm | Retroactive_THT_TACTSW_6mm_H9.5mm | top/THT | - | - | - |
| TAC_SWITCH_2 | SCH+PCB not BOM: THT -> hand-solder |  |  | SW_MEC_5E | Retroactive_THT_TACTSW_6mm_H9.5mm | Retroactive_THT_TACTSW_6mm_H9.5mm | top/THT | - | - | - |
| U1 | ALL THREE | row6:C20082 | SOP-6-2.54mm | H11L1 | SOP-6_3.8x4.1mm_P2.54mm(RetroactiveCustom) | SOP-6_3.8x4.1mm_P2.54mm(RetroactiveCustom) | bottom/SMD | B | OK | OK |
| U2 | ALL THREE | row16:C53059594 | SOT-666 | USBLC6-2P6 | SOT-666 | SOT-666 | bottom/SMD | B | OK | OK |
| U3 | ALL THREE | row11:C130212 | MSOP-8-EP | TPA6110A2DGN | HVSSOP-8-1EP_3x3mm_P0.65mm_EP1.57x1.89mm | HVSSOP-8-1EP_3x3mm_P0.65mm_EP1.57x1.89mm | bottom/SMD | B | OK | OK |
| U4 | ALL THREE | row19:C41714 | TDFN-14-EP(3x3) | MAX9814 | DFN-14-1EP_3x3mm_P0.4mm_EP1.78x2.35mm | DFN-14-1EP_3x3mm_P0.4mm_EP1.78x2.35mm | bottom/SMD | B | OK | OK |
| U6 | ALL THREE | row32:C59873 | WSON-8-EP(2x2) | TPS62172DSG | WSON-8-1EP_2x2mm_P0.5mm_EP0.9x1.6mm_ThermalVias | WSON-8-1EP_2x2mm_P0.5mm_EP0.9x1.6mm_ThermalVias | bottom/SMD | B | OK | OK |

## Method notes
- Schematic parser = s-expression walk of top-level `(symbol …)` instances (the `lib_symbols` cache is skipped, which is why the brief's "unannotated U/L/RV/Q" do not appear — they are library default references). Validated: identical ref set, values and footprints to `kicad-cli sch export netlist` (110/110).
- PCB side = `pcbnew` footprint iteration (attributes, pads, paste layers); paste Gerbers parsed independently and matched to pcbnew pad centres within 0.25 mm: F 12/12, B 260/260, 0 unmatched — so the "SMD with paste but no BOM line" list is the same from either source.
- Value checker = normalised token (e.g. `5K1`→`5.1kΩ`, `100NF`→`100nF`, `3.3R`→`3.3Ω`) searched in the BOM Comment with digit guards on both sides; ICs/diodes/beads/connectors checked by package or family keyword, and all new ones additionally by MPN from the fetched part page. 15 known-answer asserts in `bom_join.py` (e.g. `33R` vs "330Ω" → MISMATCH).
- Footprint checker maps the BOM Footprint cell (after undoing Excel's numeric coercion) onto the KiCad footprint name class (`1608Metric`→0603, `2012Metric`→0805, `3225Metric`→1210, `6332Metric`→2512, package keywords for ICs, `SMD` accepted as generic for connectors). Only L1 fails.
- Basic/Extended read from the badge in the JLCPCB part page HTML (`>Basic<` / `>Extended<` span next to the part number), downloaded 2026-10-09; the murata.com product page is blocked from this session, so the DFE201610P reference land pattern is KiCad 9.0.9's `L_Murata_DFE201610P` (its description links the Murata drawing).
