# Pass 6 (rev 3) — Mechanical & Assembly Report
**Date:** 2026-10-09 · **Truth checked:** `rev3/WavetableController.kicad_pcb` geometry (courtyards, paste/mask/silk layers, Edge.Cuts) + `kicad_out/rev3/drc_asis.json` (project rules) and `kicad_out/rev3/drc_jlc_nc01_allsev.json` (JLC limits, all rules enabled) + `kicad_out/rev3/bom_rev3.txt` · **Thresholds:** JLCPCB capabilities page fetched 2026-10-09 (legend line ≥ 0.15 mm, text height ≥ 1.0 mm, pad-to-silk 0.15 mm, copper-to-edge 0.2 mm); Newhaven NHD-2.7-12864WDW3 datasheet mechanical drawing (fetched 2026-10-09 from newhavendisplay.com; PCB 82.0 × 47.5 mm, pin row 2.50 mm from the top edge, pin 1 at 16.87 mm from the side, pitch 2.54 → row centred, 4 × Ø2.50 mm holes on a 74.20 × 42.50 mm pattern, module thickness 5.50 mm).

Script: `analysis/rev3/scripts/pass6_mech.py` (silk decomposition, courtyards, paste↔BOM, NPTH, outline, J8/module overlay, new-part placement). Renders used for the visual check: `kicad-cli pcb render --side top|bottom` (scratchpad only).

## 1. Board
- Edge.Cuts: **exactly one closed polygon (132 vertices), no other items**; bbox 89.48–254.78 × 61.00–162.80 → **165.30 × 101.80 mm**, 1.6 mm. Four R ≈ 9 mm rounded corners; **no notches** (the rev-2 SW1 notch is gone → F-010 fixed, see Pass 1 R3-P1-05). Same envelope as rev 2.
- Side assignment: **F = control face** (ENCL1/ENCR1, TAC_SWITCH_1/2, LED1/LED2, MK1, J8 OLED header — 8 footprints, no board artwork); **B = everything else** (102 footprints: all SMD, Daisy A1, SD, USB-C, jacks, Headphones1, SW1, TAC_SHIFT_L1/R1).
- 110 footprints (rev 2: 79): removed J2 (2.42" I²C OLED header), FB1; added J8, Headphones1, U6+L1+C25/C26+FB7+R33 (buck), C18–C22 (five more 100 µF), C23/C24 (THT 100 nF / 100 µF), D6, FB5/FB6, Q1–Q6, R29–R32 (2512 3.3 Ω), R35–R40 (1 k). 63 parts moved (Daisy A1 from (195.6,160.6) to (115.5,145.5); the audio parts U3/U4 now at (190–215, 152–160)).

## 2. Silkscreen — decomposition of the 447 warnings
`drc_asis.json`: 199 `silk_overlap` + 199 `silk_over_copper` + 49 `silk_edge_clearance` (75 at JLC's 0.15 silk clearance).

| Group | Count | What it is |
|---|---|---|
| silk_over_copper | 199 | **all** = board-level B.Silkscreen artwork polygons over copper/pads. Zero involve a refdes or footprint outline |
| silk_overlap: artwork vs refdes | 59 | artwork polygons under reference text (A1 ×7, C10, C11, C24 ×13, C26 ×14, Headphones1 ×18, R38 ×16, R14 ×15 …) |
| silk_overlap: artwork vs footprint silk outlines | 138 | A1 50, P1 33, C21 12, FB7 7, Q1/Q2/C22 4 each, C26 3, L1/R27/C25/U4 2 each, 1 each for C18, R10, R8, R25, R9, U6, R26, R28, C10, R19, R20, C5, C13 |
| silk_overlap: artwork vs footprint silk polygons | 2 | Q1, Q2 SOT-23 pin-1 marks |
| silk_edge_clearance: artwork beyond the outline | 22 | artwork extents 85.8–253.7 × 51.4–169.6 mm, i.e. it runs off all four edges (fab clips it) |
| silk_edge_clearance: footprint silk beyond the outline | 24 + 1 | J3/J4/J5/J6/J7 ×4 each, J1 ×2, Headphones1 ×2 (bushings outside the board), SW1 ×1 |
| silk_edge_clearance: artwork into a hole | 2 | artwork over J1's 2.0 mm NPTH |

**What changed:** rev 2 had 88 artwork polygons on **F**.Silkscreen (control-panel graphics); rev 3 has **3,900 zero-stroke filled polygons on B.Silkscreen** — a full-board traced engraving (Flammarion woodcut; bottom render confirms) plus three mirrored texts ("Stellar Crucible | Manifold" 3.0 mm, "v4.1" 2.0 mm, "Designed by FJ Bourgeois" 1.5 mm, all 0.3 mm stroke, correctly mirrored, inside the board at x 244.8–253.7). The front face now carries no legend other than refdes.

Consequences (JUDGMENT, R3-P6-01): B is the SMD assembly side; 97 of the 102 B-side refdes bboxes intersect artwork polygons, so refdes are effectively unreadable on the assembled side. JLCPCB removes silk from pads automatically (the 199 silk_over_copper hits are benign) and ignores silk for placement (pos file), so **assembly is unaffected**; inspection, rework and debugging are harder. Fine engraving detail below 0.15 mm will simply not print. If the art stays, a 1 mm refdes halo (or moving refdes to Fab) is the cheap fix.

Refdes/text check: all 110 refdes are **1.0 mm high / 0.15 mm stroke — exactly JLC's legend minimum** (ZERO-MARGIN, R3-P6-02); none hidden, none on the wrong side; the JLC-clearance DRC run (silk clearance 0.15) reports **no refdes over any pad**. Footprint outlines use 0.12 mm strokes (632 segments; below the 0.15 legend minimum → may print thin/broken; cosmetic) — R3-P6-02.

## 3. Courtyards
- `courtyards_overlap`: **0** (DRC, all severities) and 0 in an independent polygon-collision check; missing courtyards: 0.
- Courtyards protruding past the outline: J1, J3–J7, P2, TAC_SHIFT_L1/R1 and **Headphones1 (by 9.0 mm, to y = 171.8)** — all edge/panel-mounted parts whose bushings leave the board; expected.
- Touching (0.00 mm gap, legal but no margin): C19/C20, C15/R29, C22/R32; tight: L1/R33 0.18, C18/R30 0.20, C23/C24 0.21, C6/C7 0.46, Headphones1/C3 1.14 mm. (R3-P6-03)

## 4. Paste layers vs BOM (`bom_rev3.txt`, 37 lines, 95 designators)
- **F.Paste = 12 apertures = LED1 + LED2 (6 pads each), the only top-side SMD parts; LED1/LED2 are absent from the BOM** → **F-034 / F-002 STILL OPEN** (R3-P6-04). Values: CLS6B-FKW; footprint now `Retroactive_Custom_Parts:LED_RGB_5050-6_Retroactive Pin Out`.
- B.Paste = 260 apertures; every B-side paste footprint has a BOM line (93 refs), and every BOM designator exists on the board → the rev-2 phantom S1/S2 lines are gone (F-003 resolved; note for Pass 4).
- 18 footprints without paste (TH/hand-solder, not in the SMT BOM, expected): A1, C23, C24, ENCL1, ENCR1, Headphones1, J3–J7, J8, MK1, SW1, TAC_SHIFT_L1/R1, TAC_SWITCH_1/2. **C23 (axial 100 nF) and C24 (radial 100 µF) on the new OLED rail are new hand-solder parts** — the hand-assembly list asked for in F-026 is still missing.
- Footprint attributes: J3–J7 are flagged "exclude from position files" only; nothing is excluded from BOM.

## 5. Mounting holes (F-032) and the OLED module
- **Still no chassis mounting holes.** NPTH inventory: 25 × 1.2 mm (five per 3.5 mm jack), J1 2.0 mm + 2.0×1.5 slot, P2 2 × 0.65 mm. No-net PTH: encoder posts (2.8×1.5 slots ×4), jack anchors 0.8 ×10, SW1 1.85 ×3, TAC_SHIFT 1.3 ×4. The board hangs from panel hardware (jack/encoder/pot nuts) as in rev 2 → **F-032 STILL OPEN** (R3-P6-05).
- **J8** (`Retroactive_Custom_Parts:Newhaven2.7_OLED`, F side, rot −90): a *straight* 1×20 pin-header footprint (1.0 mm drill / 1.7 mm pad, ring 0.35), pin 1 at (196.258, 81.301), pin 20 at (147.998, 81.301), pitch 2.540; courtyard 146.2–198.1 × 79.5–83.1; carries the module STEP (`Newhaven2.7_12864WDX3.STEP`). Pin usage: 1/5/6/10–14/19/20 GND, 2 /+3V3_OLED, 4 /DC_SPI, 7 /SCLK_SPI, 8 /SD_IN_SPI, 16 /RES_SPI, 17 /CS_SPI; 3/9/15/18 NC (4-wire SPI strapping).
- **Module overlay** (datasheet 82.0 × 47.5 mm, row 2.5 mm from the module edge, row centred): with pin 1 on the right as placed, the datasheet front view puts the module body toward **+y (down the board)**: **x 131.1–213.1, y 78.8–126.3**. That rectangle is inside the outline and clear of every F-side part: ENCL1 (bbox to x 117.4) 13.7 mm, ENCR1 (from x 227.4) 14.3 mm, TAC_SWITCH_1/2 (y ≥ 130.2) 3.9 mm, LED1/LED2 7.5 mm, MK1 7.4 mm. The opposite orientation (body toward −y) would overhang the top edge by 24.7 mm over the rear jacks — not viable. So **placement fits**, but only in the +y orientation, and only as a parallel stack (female header on the board, male header on the module, ≈ 8.5 mm + 5.5 mm stack) — a straight header soldered directly would stand the module perpendicular. (R3-P6-06)
- **The module's 4 × Ø2.5 mm mounting holes (74.2 × 42.5 pattern) have no counterpart on the board.** Projected on the board they land at (135.0, 81.3), (209.2, 81.3), (135.0, 123.8), (209.2, 123.8): the (209.2, 81.3) site is on top of R2 (206.3,81.5)/R5 (214.2,81.6)/U1 (211.5,87.3) on the B side, (135.0, 123.8) is 0.7 mm from C22's courtyard. Without them the 9 g module hangs on the 20 header pins. The repo's `screen mounting solution.md` describes a **different display** (Crystalfontz CFAL12864G-024W glass COG with an FPC/ZIF, tape-and-gasket mount) — it does not apply to the NHD module J8 is built for. (R3-P6-05/06)
- **Audio corridor (REV2_OLED_PLAN §7, keep display power/I²C out of x ≈ 165–200):** the header spans x 148–196 and the module covers the full 35 mm corridor width; the OLED buck (U6 at (196.9,123.0), L1 (199.3,119.5), C25/C26 (193.5,128/116.5), FB7 (198.0,128.0)) and the rail caps C23/C24 (191–199, 86–90) all sit inside the corridor, directly between the audio jacks (y ≈ 65) and MAX9814 U4 (190.7,155.3). Mechanically fine; the electrical consequence is for Pass 2/5 — flagged here because it contradicts the plan's placement rule. (R3-P6-06)

## 6. New parts — placement and legibility
| Part | Side / position | Observation |
|---|---|---|
| Headphones1 (Alps RK097 dual 10 k, horizontal) | B (224.75,146.5), rot 90; 6 PTH 1.0 drill / 1.8 pad (ring 0.40) | Shaft axis x ≈ 222.25 exits the **bottom edge**, bushing 9.0 mm outside the outline; the PHONES jack J7 (centre x 239.0) is on the same edge 16.75 mm away → both need a panel cut-out; knob ≤ ~14 mm. Refdes at (215.4–217.1, 141.4–151.6), overlapped by 18 artwork polygons |
| C15, C17, C18, C19, C20, C21, C22 (100 µF 6.3×7.7) | B, cluster x 118–155, y 89–127 (power entry/filter) | 7.7 mm tall on the Daisy side (A1 header ≈ 8.5 mm) — no height conflict; courtyards touch R29/R32/each other (0.00 mm); all in BOM line C3339 |
| C6, C7 (100 µF, headphone coupling) | B (236.75/246.7, 139.95) | 0.46 mm courtyard gap; C7 3.3 mm from the right edge |
| C23 (axial 100 nF THT), C24 (radial 100 µF THT) | B (199.25,86.25) / (191.75,90.25) | hand-solder, not in SMT BOM; courtyards 0.21 mm apart; both GND pins stitch the F.Cu pour (Pass 1) |
| U6/L1/C25/C26/FB7/R33 (buck) | B, (193–200, 116–128) | 0.5 mm-pitch WSON with 0.25 mm thermal vias (Pass 1 R3-P1-04); refdes all under artwork |
| J8 | F, see §5 | refdes "J8" rotated at the pin-1 end (197.8–199.5, 80.3–82.3), unobstructed |
| LED1/LED2, MK1, TAC_SWITCH_1/2 | F, y 130–140 | refdes unobstructed (no F artwork) |

## 7. Findings (Pass 6, rev 3)

| ID | Class | Status | Finding | Evidence | Threshold source |
|----|-------|--------|---------|----------|------------------|
| R3-P6-01 | JUDGMENT | confirmed | All 447 silk warnings are the **back-side artwork** (3,900 filled polygons, runs off all edges) over copper/refdes/footprint outlines, plus edge-mounted parts' outlines leaving the board. Nothing lands silk on a pad that the fab will not clip. Side effect: refdes on the SMD side (97/102) are buried in the art — no assembly impact (pos file), inspection/rework impact yes | §2 decomposition, bottom render | JLCPCB: silk on pads removed; legend min 0.15 mm |
| R3-P6-02 | ZERO-MARGIN | confirmed | All 110 refdes are 1.0 mm / 0.15 mm = exactly JLC's minimum legend size; footprint outline strokes 0.12 mm are below the 0.15 mm line minimum (cosmetic) | refdes size histogram | JLCPCB caps 2026-10-09 |
| R3-P6-03 | PASS | confirmed | Courtyards: 0 overlaps, 0 missing; 10 protrude past the outline (all panel-mounted parts); three courtyard pairs touch at 0.00 mm (C19/C20, C15/R29, C22/R32) | §3 | — |
| R3-P6-04 | VIOLATION | confirmed — **F-034/F-002 STILL OPEN** | Top stencil has exactly LED1+LED2's 12 apertures while LED1/LED2 are missing from `bom_rev3`; B.Paste (260) fully covered by the BOM; S1/S2 phantom lines gone | §4 | — |
| R3-P6-05 | JUDGMENT | confirmed — **F-032 STILL OPEN, widened** | No mounting holes at all, and none for the NHD module's 74.2 × 42.5 Ø2.5 pattern; projected sites collide with R2/R5/U1 and sit 0.7 mm from C22. `screen mounting solution.md` targets a different (COG/ZIF) display | §5 | NHD-2.7-12864WDW3 datasheet mech. drawing |
| R3-P6-06 | JUDGMENT | confirmed | J8 fits only with the module body toward +y (x 131.1–213.1, y 78.8–126.3) as a parallel stack on a socket; clear of all F parts (≥ 3.9 mm); the −y orientation overhangs the top edge by 24.7 mm. Header + buck + rail caps occupy the x 165–200 audio corridor the rev-2 plan reserved (electrical review → Pass 2/5) | §5 overlay | NHD datasheet; REV2_OLED_PLAN §7 |
| R3-P6-07 | JUDGMENT | confirmed | Headphones1 bushing 9.0 mm beyond the bottom edge next to J7 (16.75 mm pitch): consistent with a panel-through design; add to the panel drawing; pads 1.0/1.8 (ring 0.40) fine | §6 | — |
| R3-P6-08 | JUDGMENT | confirmed | Hand-assembly list (F-026) still missing and now longer: 18 TH parts incl. new C23, C24, J8, Headphones1 | §4 | — |
| R3-P6-09 | PASS | confirmed | Outline: one closed 132-vertex polygon, 165.30 × 101.80 mm, rounded corners, no notch, no stray Edge.Cuts items | §1 | — |
| R3-P6-10 | PASS | confirmed | Back-side texts correctly mirrored and on-board; front refdes (J8, LEDs, MK1, switches, encoders) unobstructed | §2, §6, top render | — |

## 8. Rev-2 mechanical findings — status in rev 3

| Rev-2 ID | Rev-3 status | Evidence |
|---|---|---|
| F-010 SW1 edge notch / 0.0 mm copper | **FIXED** | outline has no notch; SW1 pads 0.414 mm from edge (Pass 1) |
| F-032 no mounting holes | **STILL OPEN** (+ OLED module holes) → R3-P6-05 | NPTH/PTH inventory |
| F-033 silk warnings = panel artwork | **CHANGED** → R3-P6-01: artwork moved F→B (3,900 polys), 143 → 447 warnings, now covers the assembly side's refdes | §2 |
| F-034 top paste = missing LEDs | **STILL OPEN** → R3-P6-04 | F.Paste 12 = LED1/LED2, not in BOM |
| F-035 mechanical passes (courtyards, mask) | **PASS re-confirmed** → R3-P6-03 | DRC all-severity, own check |
| F-026 no hand-assembly list | **STILL OPEN** → R3-P6-08 | 18 TH parts |
| F-003 phantom S1/S2 in BOM | **FIXED** (noted for Pass 4) | all BOM designators exist on the board |

## 9. Reproduce
```
python3 -I analysis/rev3/scripts/pass6_mech.py [board.kicad_pcb] [drc.json] [bom.txt]
```
