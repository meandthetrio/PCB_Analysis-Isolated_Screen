# Rev 4 — Pass 0: Inputs, provenance, baselines and the rev-3→rev-4 delta
**Date:** 2026-10-13 · **Inputs:** `rev4/WavetableController.kicad_sch` + `.kicad_pro` (Google Drive, shared 2026-10-13 by fernand.bourgeois.iii@gmail.com), `rev4/WavetableController.kicad_pcb` (31,869,998 B, via a GitHub upload of `WavetableController.kicad_pcb 2.zip` — the Drive connector caps downloads at 10 MB), `rev4/ManifoldRe_BOM_NEW - Excel Format (rev4).xls` (chat upload 2026-10-13), `rev4/Gerbers/` (ManifoldGerbs.zip, plotted 2026-10-13 11:41 CDT by Pcbnew 9.0.4 from this board) · **Tools:** kicad-cli 9.0.9, pcbnew Python, xlrd 2.0.2.

## 1. Provenance and file identity — all four design inputs are complete and differ from rev 3

| File | Rev 3 (`rev3/` on branch `claude/charming-meitner-c0w1jh`) | Rev 4 (`rev4/`) | Differs? |
|---|---|---|---|
| `.kicad_sch` | 423,788 B, md5 c544fb05… | 429,986 B, md5 24ad93dd…, `version 20250114`, eeschema 9.0, one root sheet | **yes** — 3,032 changed lines; §2 |
| `.kicad_pro` | 15,087 B | 15,087 B, md5 0d5a2f3c… | **byte-identical** → DRC rules unchanged (`min_track_width 0.0`, `min_clearance 0.0`, edge 0.5, hole 0.3; F-005 / R3-P1-14 still open) |
| `.kicad_pcb` | 31,856,096 B · 110 footprints · 114 nets · 1,032 segs · 244 vias · 1 GND zone filled F+B | **31,869,998 B · 112 footprints · 110 nets · 1,077 segs · 253 vias · 1 GND zone filled (15 + 5 fill polys) · 0 duplicate refs**, `version 20241229` | **yes** (md5 227a2bbf… vs ed92c959…); same outline 165.30 × 101.80 |
| BOM `.xls` | 36 lines / 90 designators | **38 lines / 92 designators**, one sheet | **yes** (md5 differs; `bom_diff.txt`) |
| Gerbers | none | 12 files, same job GUID; agree with the board file on every Pass-1 number | new |

Schematic, board and BOM are one design generation: the netlist delta (§2), the footprint set (Pass 3: 112 ↔ 112, 0 pad-level diffs) and the BOM delta (Pass 4) name the same parts. The Gerbers are a plot of this board, not an independent fab snapshot — nothing has been fabbed from rev 4. The silk still reads "v4.1".

## 2. What changed rev 3 → rev 4 (`scripts/netlist_diff.py` over `kicad-cli` XML netlists; `scripts/netlist_diff_rev3_rev4.txt`)

**Components 110 → 112.** Removed: **D6** (series Schottky), **FB7** (bead into U6 VIN). Added: **C27** 100 nF 0603 + **C28** 10 µF 0805 on /+3V3_D at the SD socket; **R34, R41** 10 k (encoder pull-ups). Changed:

| Ref | Rev 3 | Rev 4 | Oct-7 row / decision |
|---|---|---|---|
| R21, R25, R26, R28 | 300 Ω | **390 Ω** (C23151) | 3c / 5a (green, blue) |
| R24, R27 | 300 Ω | **510 Ω** (C23193) | 3c / 5a (red) |
| R31, R32 | 3.3 Ω 2512 1 W | **10 k 0603** on /ENCL_A, /ENCL_B | 7 / 5c; second π-filter removed (5b) |
| C19, C20, C21, C22 | 100 µF 6.3×7.7 | **10 nF 0603** (C57112) to GND on /ENCL_A/B, /ENCR_A/B | 7 / 5c |
| D2–D5 | 1N5817WS SOD-323 (C727114) | **1N5817W SOD-123FL (C169541), IFSM 25 A** | 9 |
| L1 | `L_0805_2012Metric` | **`L_Murata_DFE201610P`** | 6b / R3-P4-02 |

**Nets 121 → 117.** Removed Net-(C19-Pad1), Net-(C20-Pad1), Net-(D6-A), Net-(D6-K), Net-(U6-EN); added Net-(C15-Pad1) = {C15.1, C16.1, FB5.2, FB6.1}. `/+9V_FLAG` is now the FB6 output node and carries C25, U6 VIN + EN, the six LED resistors and R29 — **U6 is fed ahead of R29/R30 (row 2c)** and the net was re-pointed, not orphaned (decision 5b). Each encoder A/B net gains a 10 k to /+3V3_D and a 10 nF to GND. `/+3V3_D` gains C27, C28, R31, R32, R34, R41.

**Power-entry chain, rev 4:** J1 → D2–D5 bridge → [C14] → FB3 → FB4 → FB5 → [C15 100 µ, C16] → FB6 → /+9V_FLAG [C25; U6; LEDs] → R29 → [C17] → R30 → /DSY_VIN [C18] → A1.39. Bulk on the ~8 V side 3 × 100 µF + 10 µF (rev 3: 7 × 100 µF).

**Board delta (layout):** the copper outside the changed parts is untouched — identical 0.1 mm segment set (68 / 74.9 mm), identical F.Cu fragment areas, identical SPI/SD/USB/MIDI/audio net lengths, J8 and all NPTH unchanged; +9 vias (encoder RC and SD-cap routing), D2–D5 pads swapped in place, L1 pads re-patterned.

**Unchanged from rev 3:** J8 and its nets, U6/L1/C25/C26 buck, Q1–Q6 + R35–R40, SD, USB, MIDI, audio, Headphones1, FB2–FB6 part, schematic LED value "CLS6B-FKW" (row 3d not done), /RES_SPI 2-node, /SWA single-pin, no PWR_FLAG / NC flags, 0 GND stitching vias, no mounting holes.

## 3. ERC / DRC baselines (`kicad_out/rev4/`)
- **ERC 51 — identical to rev 3** in type and count: 19 footprint_link_issues + 12 lib_symbol_mismatch (library noise), 14 pin_not_connected (10 × P2 SS/SBU, 4 × J8 3/9/15/18), 4 power_pin_not_driven (A1 VIN, U4 VDD, U6 VIN, #PWR01), 1 label_dangling (SWA), 1 multiple_net_names (GND/SWB).
- **DRC as-is 576** (rev 3: 569): 199 silk_overlap, 199 silk_over_copper, 49 silk_edge_clearance, 75 + 19 library warnings, **17 clearance** (U3/U4 0.15 mm pad gaps vs 0.2 netclass — F-009 noise), **9 starved_thermal** (rev 3: 8; new = C28.1), **5 copper_edge_clearance** (project 0.5 rule), **2 drill_out_of_range** (U6 0.25 vias), 2 via_dangling. **0 unconnected items.**
- **DRC with JLCPCB minimums + netclass 0.1 (scratch copy) 578:** zero clearance / track-width / edge / drill errors; 9 starved_thermal, 2 via_dangling, 75 silk_edge_clearance + silk/library warnings.

## 4. Threshold sources
JLCPCB capabilities page re-fetched 2026-10-13 (values as the rev-3 fetch). JLCPCB part pages fetched 2026-10-13 for C169541, C23151, C23193, C57112. Daisy, NHD, TPS62172, Würth, MMBT3904 figures carried from the rev-3 pass reports (same parts, settled facts).
