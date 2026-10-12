# Pass 6 (Daisy Pod Rev5) — Mechanical & Assembly Report
**Date:** 2026-10-12 · **Board:** Electrosmith Daisy Pod Rev5 (reference design for Trey's WavetableController) · **Truth checked:** `reference/electrosmith/daisy_pod/kicad/ES_Daisy_Pod_Rev5.kicad_pcb` geometry (courtyards, paste/mask/silk, Edge.Cuts, pads) cross-checked against the Eagle source `ES_Daisy_Pod_Rev5.brd` (package definitions, text sizes/ratios, element values, Dimension/Milling layers) + `kicad_out/pod/drc_asis.json` (converted project's defaults) and `kicad_out/pod/drc_jlc_nc01.json` (JLC limits, all rules enabled) + `kicad_out/pod/bom.txt` (Electrosmith BOM, 24 lines / 47 designators) + `kicad_out/pod/pos.csv` (62 rows) + `kicad_out/pod/gerbers/`. Nothing under `reference/` was modified. · **Thresholds:** JLCPCB capabilities page fetched 2026-10-12 (legend line ≥ 0.15 mm, text height ≥ 1.0 mm, pad-to-silk 0.15, copper-to-edge 0.2, NPTH ≥ 0.5); Eagle text defaults (size as drawn, ratio 8 % unless set). The Pod databrief (`Pod_databrief-3-13.pdf`, 5 pages, rendered and text-extracted) contains **no dimensioned drawing** — only a photo, feature list, pinout diagram and licence — so board size and hole positions can only be checked against the `.brd` itself (its two Eagle dimension annotations read 90 and 50).

Scripts: `analysis/daisy_pod/scripts/pod_pass6_mech.py` (DRC silk/text decomposition for both runs, text inventory, courtyards, paste↔BOM, holes, outline, edge parts), `pod_pass1_fill.py` (mask margins, paste regions, fiducials, mounting-hole proximity), `pod_eagle_brd.py` (`python3 -I`; Eagle text sizes/ratios, DNI values, stripped-layer objects).

## 1. Board
- **Outline:** four Eagle Dimension wires 0,0 → 90,50 → a **90.000 × 50.000 mm rectangle**, no corner radii, plus three package-level Dimension/Edge items that the importer merged in: the **micro-USB tab** from `47589-0001_CUT2` (9.77 × 2.185 mm, x 60.615–70.385, y −2.135…0.05 — note the 0.05 mm overlap with the main edge, which leaves an 8-vertex outer loop with a 0.05 step: cosmetic, Eagle merges overlapping 0.127 lines), and **three internal cutouts**: P8 (Alps RK10J dual pot) anchor slots 2.2 × 1.0 at x 60.15–62.35, y 40.3–41.3 and 48.7–49.7; ENC_1 (PEC11) D-slot 1.55 × 2.2 at (64.725–66.275, 24.67–26.87). Bbox incl. line width 90.15 × 52.28; outline area 4,499.5 mm²; 1.6 mm. Edge_Cuts Gerber: 83 lines.
- **Missing from the conversion:** the two 0.702 × 1.375 milled slots for P5's board-lock legs (Eagle Milling layer, stripped) — Pass 1 DP-P1-07. Any mechanical drawing or 3-D check made from the KiCad copy is short those two slots.
- Side assignment: **F = control / connector face** (26 footprints: J1–J4, P5, P2, U1 Seed sockets, ENC_1, VR_1/VR_2, S2/S3, LED1/LED2, U7, C62/C63, FD1–3, H1–H4, logos U$4/U$7); **B = passives + SD + headphone pot** (36: P1 micro-SD, P8, U4, U15, D5, all R/C, FD4–6, logos U$2/U$3).

## 2. Silkscreen and text — decomposition of the warnings
`drc_asis.json` (project defaults: text ≥ 0.8 / 0.08): 75 `silk_over_copper` + 42 `silk_edge_clearance` + 36 `text_height` + 26 `text_thickness` + 2 `silk_overlap`. `drc_jlc_nc01.json` (JLC 1.0 / 0.15, silk clearance 0.15): 75 + 44 + **57 + 62** + 12 (+ 21 `missing_courtyard`).

### 2a. Text sizes (Eagle source → what plots)
| Text group | Eagle size / ratio | Plots as (KiCad height / stroke) | n | vs JLC 1.0 / 0.15 |
|---|---|---|---|---|
| B-side refdes (R/C/D5/U4/U15/P1/P8) | 0.8128 mm (32 mil) / 8 % default | 0.652–0.753 / 0.060–0.117 | 31 | below both |
| F-side refdes S2/S3/C62/C63 | 0.8128 / 8 % | 0.753 / 0.060 | 4 | below both |
| LED1/LED2, VR_1/VR_2, U7 refdes | 1.016–1.067 / 8 % | 0.937–0.957 / 0.059–0.079; U7 0.699/0.114 | 5 | below both |
| J1–J4, ENC_1, P2, U1 refdes | 1.27–1.676 / 8–10 % | 1.156–1.546 / 0.093–0.131 | 7 | height OK, stroke below |
| Seed-header pinout labels SS/SCK/MI/MO/SCL/SDA/A7/A1/3V3/A/D/VIN/GND | 1.016 / **15 %** | 0.864 / 0.152 | 14 | stroke OK, height below |
| Panel legends SW 1/SW 2/POT 1/POT 2/ENC/PHONES/MIDI IN/LINE IN/LINE OUT | 1.778 / 8 % | 1.636 / 0.142 | 9 (+ U1's "1") | height OK, stroke 8 µm under |
| "Clicked Encoder", U1 "USB", "H11L1 SR2M" (B) | 1.016 / 8 % | 0.935 / 0.081 | 3 | below both |
| "(C) Electrosmith 2022", "Rev5", "Headphone Volume" (B, mirrored) | 1.27 / 8 % | 1.168 / 0.102 | 3 | stroke below |
| "Plant your Daisy Seed Here!" | 2.54 / 8 % | 2.337 / 0.203 | 1 | **the only text meeting both** |

Totals over the **78 visible silk texts**: 57 under 1.0 mm height, 62 under 0.15 mm stroke, 1 passes both. The as-is 36/26 are the subset under KiCad's 0.8/0.08. Hidden refdes (15): FD1–6, H1–4, U$2/3/4/7, P5 (its Eagle package has no `>NAME`). All refdes sit on the correct side's silk; none is mirrored wrongly.

Classification: refdes legibility is cosmetic — Electrosmith's fab printed these boards and the product ships with them — but it is a measured miss of JLC's stated legend capability on 61 of 78 texts, so **DP-P6-01 VIOLATION (cosmetic)**; the panel legends and pinout labels are each one parameter short by ≤ 0.14 mm → **DP-P6-02 ZERO-MARGIN**. **vs rev 3:** all 110 refdes exactly 1.0 / 0.15 (R3-P6-02 ZERO-MARGIN).

### 2b. `silk_over_copper` (75) — every one is "Silkscreen clipped by solder mask"
Mapped to the nearest mask opening: 71 are footprint outlines over **their own pads** (U4 6, D5 5, VR_1/VR_2 pot circles 3 each, U7 2, P5 2, 0603/0402/caps 2 each, jacks 1 each, LEDs, P8, C60); 4 cross **another part's** opening: the U1 Seed-socket outline over H1's 5.99 mm mounting-pad window (×2) and over P1's pads (×1), P5's outline over H3's window (×1); and 1 is the "Plant your Daisy Seed Here!" text over a U1 socket pad. All fab-clipped, no assembly impact. PASS (DP-P6-03).

### 2c. `silk_edge_clearance` (42 / 44) — parts that intentionally leave the board
P1 micro-SD (10; the card slot protrudes **5.0 mm past the left edge**, B side), J1–J4 jacks (7–8 each; bodies 2.28 mm beyond the right edge, J1 also 0.3 beyond the top), P5 (2; outline on the USB tab), P8 (1; bushing 2.08 beyond the bottom edge); the JLC run adds U1's refdes and one board text at 0.08/0.096 from the edge. Expected for edge connectors. PASS (DP-P6-03).

### 2d. `silk_overlap` (2 → 12 at 0.15) and stroke widths
LED1's pin-1 marker over the U1 outline (2); at JLC's 0.15 clearance also R83↔D5↔U15 outlines (0.04–0.13 apart), C53/C54/R27 refdes touching their own outlines (0.00–0.05), U1's "1" over its outline. Footprint silk strokes: 8,638 zero-width items (Eagle filled polygons: ES wordmark, Tonne, CE, DAISY_POD_BRANDING_2, pot pointer pips), 0.05 ×112 (P5 outline), 0.102 ×20, 0.127 ×111, 0.152 ×39, 0.203 ×36, ≥ 0.3 ×9. Lines at 0.05–0.127 are under JLC's 0.15 legend line → print thin/broken (cosmetic, DP-P6-03). **vs rev 3:** 447 warnings, all from the 3,900-polygon back-side artwork over the SMD side's refdes.

## 3. Courtyards (DP-P6-04)
Eagle has no courtyard layer. The importer turned tKeepout/bKeepout (layers 39/40) into F/B.CrtYd for **41 footprints** (all R/C, S2/S3, J1–J4, VR_1/2, ENC_1, H1–4, P1, U4); **21 have none**: C62, C63, D5, FD1–6, LED1, LED2, P2, P5, P8, U1, U15, U7, U$2/3/4/7. Among the 41: `courtyards_overlap` 0 (DRC all-severity and own polygon collision). The 21 `missing_courtyard` warnings appear only in the all-severity run. Format artefact, not a design finding. **vs rev 3:** 0 missing, 0 overlaps, three pairs touching at 0.00.

## 4. Paste vs BOM (DP-P6-05, DP-P6-06)
- **F.Paste: 104 apertures + 14 drawn regions on 14 footprints; B.Paste: 89 + 1 region on 31 footprints.** Regions: P5 shell paste polygons ×4 (Eagle tCream), **VR_1/VR_2 pin-in-paste polygons ×5 each** (package `9MM_SNAP-IN_POT_SILK_PIP` — the THT pots are reflowed), U4.9 PowerPAD 1.57 × 1.89 (Eagle `cream="no"` + explicit rectangle). The plotted `F_Paste.gtp` (104 flashes, 14 regions) and `B_Paste.gbp` (89, 1) agree.
- **Every footprint carrying paste is on the BOM**, including the three the task asked about: **LED1/LED2** (`P-LCC-4-3`, 4 pads 0.75 × 1.8 each; BOM line "RGB LED SMT PLCC4, Cree CLVBA-FKA-CAEDH8BBB7a363"), **U1** (`ES_DAISY_SEED_SMT`, 40 SMD pads 3.175 × 1.016 on 2.54 pitch, rows 15.24 apart; BOM line "1X20 FEMALE SMT 2.54MM VERTICAL, Samtec SSM-120-L-SV" — the Seed is socketed on SMT headers, so U1's paste is the sockets'), and **P2** (`1X12_NO_SILK_ALL_CIRCLE`, 12 PTH 1.016/1.88, value `M12_ALL_CIRCLE_DNI`: no paste, **not** on the BOM — DNI by value, consistent).
- BOM lines without paste: VR_1/VR_2 — they have PIP paste regions instead of pad paste (counted above). Not on the BOM and no paste, as expected: FD1–6, H1–4, U$2/3/4/7 (logos), P2 (DNI). 47 BOM designators ↔ 62 − 6 − 4 − 4 − 1 = 47 footprints: fully reconciled; pos file 62 rows = all footprints (no exclude flags set).
- **Value/BOM conflicts for Pass 4:** R78 and R84 carry the Eagle value **"DNI 0R"**, yet the BOM's "0R R0603 / AC0603FR-070RL" line lists **R79 R83 R78 R84 (qty 4)** — either two DNI parts get placed or the BOM over-orders by two. LED1/LED2's Eagle `MPN` attribute is **CLVBA-FKA-CC1F1L1BB7R3R3** while the BOM says **CLVBA-FKA-CAEDH8BBB7a363** (same Cree family, different bin code). **vs rev 3:** F.Paste = LED1+LED2 while both are missing from the BOM (F-034 open); phantom S1/S2 fixed.

## 5. Mounting holes H1–H4 (DP-P6-07)
Eagle `32-PAD_NO_SILK` = **3.2 mm PTH with a 5.842 mm copper pad (ring 1.32 mm), no net, 5.994 mm mask window** (M3 clearance), at **(4.5, 16.929), (4.5, 45.5), (73.0, 6.155), (73.0, 45.0)**. Pattern: left pair 28.571 mm apart, right pair 38.845 apart, columns 68.5 apart — not a rectangle (H1/H3 are offset to clear the Seed sockets and the USB/jack area). Edge distances: 4.5 mm to the left edge (H1/H2), 4.5 / 5.0 to the bottom (H2/H4), 6.155 to the top (H3), 17.0 to the right (H3/H4); nearest hole edge to board edge 2.9 mm, nearest pad edge 1.58 mm. Eagle keepout circles r 3.683 (kept as courtyards) and the via-restrict r 3.556 (stripped): nearest via 3.94 / 10.37 / 4.77 / 5.05 mm, nearest track end 3.94 / 5.32 / 3.60 / 4.86 — nothing inside the via restrict; H3's 3.60 is a track end 0.08 inside the part keepout (Eagle does not police tracks there). The databrief gives no dimensions to compare against (see header). PASS. **vs rev 3:** no mounting holes at all (F-032 / R3-P6-05); the NHD module's 4 × Ø2.5 pattern also unprovided.

## 6. Connectors at the edges, controls, Seed socket (DP-P6-08, DP-P6-09)
| Part | Side / position | Geometry | Note |
|---|---|---|---|
| J1–J4 CUI SJ2-35863B 3.5 mm jacks | F, x = 84.0, y 6.0 / 18.583 / 31.167 / 43.75, rot 180 | **12.583 mm pitch**, 5 SMD pads 2.2 × 3.2, 2 × 1.2 NPTH posts each, bodies 2.28 beyond the right edge, pads 0.5 from the edge | right-edge panel row (MIDI IN, LINE IN, LINE OUT, PHONES) |
| P5 Molex 47589-0001 micro-B | F, (65.5, 1.5) rot −90 | sits on the 9.77 × 2.185 tab; 5 signal pads 1.35 × 0.4 on 0.65 pitch, 2 top shell pads 1.9 × 2.0, 2 PTH pegs 0.85, 2 bottom leg pads 1.93 × 1.07 (no paste) over the stripped slots | DP-P1-04 / DP-P1-07 |
| P1 Hirose DM3AT micro-SD | **B**, (8.8, 33.2) rot 90 | 14 pads 0.7 × 1.2 (1.1 pitch) + shell pads; slot mouth 5.0 beyond the left edge; GND shell pads 0.475 from the edge | left-edge card slot; the Eagle package's 5 tRestrict rectangles were stripped (no copper-fill effect: pads are the only copper there) |
| P8 Alps RK10J12R0A0B dual pot | **B**, (61.25, 45.0) | 7 SMD pads 1.2 × 1.4; two 2.2 × 1.0 outline slots for its anchors; bushing 2.08 beyond the bottom edge | headphone volume, bottom edge |
| VR_1 / VR_2 9 mm snap-in pots (Song Huei) | F, (34.5, 34.671) / (49.73, 34.671), **15.23 pitch** | 3 × PTH 1.1/1.54 + 2 × 2.1/2.94 chassis; pin-in-paste regions | |
| ENC_1 Bourns PEC11 | F, (65.5, 21.27) | 2.05 NPTH centre, 1.55 × 2.2 D-slot cutout, 11 SMD pads (A/B/C/D + bracket) | |
| S2 / S3 TL3301 | F, (21.39, 38.033) / (7.929, 38.033), 13.46 pitch | 4 pads 1.397 × 2.794 | |
| LED1 / LED2 PLCC4 | F, (8.0, 31.5) / (21.5, 31.5), 13.5 pitch | 4 pads 0.75 × 1.8 | aligned with the switches |
| U1 Seed sockets (Samtec SSM-120) | F, (27.96, 16.905) rot 90 | pins 1–20 and 21–40 on 2.54 pitch from x 3.83 to 52.09; rows at y 26.398 / 11.158 (**15.24 apart**); alternating SMT tails (pads 3.175 × 1.016) | Seed outline silk crosses H1's window |
| P2 1×12 breakout header | F, (24.13, 3.905) | 12 PTH 1.016/1.88 along the top edge (SPI/I²C/ADC/3V3/VIN/GND, labelled 0.864 mm) | DNI |
| C62 / C63 100 µF Panasonic D (8 mm) | F, (64.0, 36.5) / (64.0, 45.0) | pads 3.0 × 1.4 | tallest F-side parts besides the controls |
| FD1–FD6 1 mm fiducials | 3 per side, near corners | diamond mask windows (Pass 1 DP-P1-09) | |

Nothing on the F side collides: courtyards present do not overlap, and the controls keep ≥ 12.6 mm pitch on the panel row. All edge-mounted parts leave the board by design (SD slot, jacks, USB, headphone pot) → consistent with a panel/enclosure that frames the PCB edges. **vs rev 3:** jacks J3–J7 and Headphones1 protrude similarly (R3-P6-07); the WavetableController has no fiducials and no mounting holes.

## 7. Mixed-process / assembly notes (DP-P6-10)
Two-sided SMT (F 26 / B 36 footprints). Non-standard steps a contract assembler must be told about: pin-in-paste reflow of VR_1/VR_2 (THT pots through the SMT line), P5's shell legs hand-soldered through the (milled) slots, P2 DNI, R78/R84 "DNI 0R" (§4 conflict), U4 PowerPAD paste region, 8 mm electrolytics C62/C63 on the control face. All 115 vias tented (no exposed via copper under the pots/switches). **vs rev 3:** 18 hand-solder THT parts with no assembly list (R3-P6-08).

## 8. Findings (Pass 6, Daisy Pod Rev5)

| ID | Class | Status | Finding | Evidence | Threshold source | vs WavetableController rev 3 |
|----|-------|--------|---------|----------|------------------|------------------------------|
| DP-P6-01 | VIOLATION (cosmetic) | confirmed | 61 of 78 visible silk texts miss JLC's legend minimum: 40 refdes drawn at Eagle 0.8128–1.07 mm / 8 % plot 0.65–0.96 mm tall with 0.06–0.12 mm strokes (31 on the B side), and the 7 larger refdes keep 0.09–0.13 strokes. The as-is DRC's 36 `text_height` / 26 `text_thickness` are the subset under KiCad's 0.8/0.08; at JLC's 1.0/0.15 they become 57/62. Legibility only; the product ships this way | §2a, `pod_pass6_mech.py` B | JLCPCB caps 2026-10-12 (text ≥ 1.0, line ≥ 0.15) | Rev 3: all 110 refdes exactly 1.0 / 0.15 (R3-P6-02 ZERO-MARGIN) |
| DP-P6-02 | ZERO-MARGIN | confirmed | User-facing legends (SW 1/2, POT 1/2, ENC, PHONES, MIDI IN, LINE IN/OUT: 1.636 mm, stroke 0.142) and the 14 pinout labels (0.864 mm, stroke 0.152) each miss one JLC parameter by 8 µm / 0.136 mm; back texts 1.168 / 0.102. Raise the Eagle ratio to 10–12 % | §2a | JLCPCB caps 2026-10-12 | Rev 3: front face carries only refdes |
| DP-P6-03 | PASS | confirmed | 75 `silk_over_copper` = footprint outlines clipped by their own pad windows (71) or the H1/H3/P1 windows (4) + 1 text; 42 `silk_edge_clearance` = P1/J1–J4/P5/P8 outlines of parts that leave the board; 2–12 `silk_overlap` = LED1 pin-1 mark, R83/D5/U15 outlines 0.04–0.13 apart; 243 outline strokes at 0.05–0.127 print thin | §2b–2d | JLCPCB: silk on pads removed; line ≥ 0.15 | Rev 3: 447 warnings from back-side artwork (R3-P6-01) |
| DP-P6-04 | CONVERSION-ARTEFACT | confirmed | Courtyards exist only where Eagle had tKeepout/bKeepout (41 footprints; 0 overlaps); 21 footprints have none (C62/C63, D5, FD1–6, LED1/2, P2, P5, P8, U1, U15, U7, logos) → 21 `missing_courtyard` in the all-severity run | §3 | — | Rev 3: 0 missing, 0 overlaps (R3-P6-03) |
| DP-P6-05 | PASS | confirmed | Paste ↔ BOM fully reconciled: F 104 + 14 regions / B 89 + 1 region; every pasted footprint on the BOM (LED1/LED2 Cree line; U1 = Samtec SSM-120 SMT sockets; P8, P1, J1–J4, ENC_1); VR_1/VR_2 pin-in-paste; P2 DNI with no paste; FD/H/logos unpasted and unlisted; 47 ↔ 47 | §4 | — | Rev 3: top stencil = LED1/LED2 absent from BOM (R3-P6-04 / F-034) |
| DP-P6-06 | JUDGMENT (for Pass 4) | plausible | R78/R84 valued "DNI 0R" in the `.brd` but counted in the BOM's 4-piece 0R line; LED1/LED2 Eagle MPN CLVBA-FKA-CC1F1L1BB7R3R3 vs BOM CLVBA-FKA-CAEDH8BBB7a363 | §4, `pod_eagle_brd.py` DNI list | — | Rev 3: phantom S1/S2 fixed (F-003) |
| DP-P6-07 | PASS | confirmed | Four M3 mounting holes (3.2 PTH, 5.842 pad, 5.994 mask window, no net) at (4.5,16.929)/(4.5,45.5)/(73,6.155)/(73,45); edge margins 4.5–6.2 mm; via/track keepouts respected; the databrief has no dimensional drawing to check positions against | §5 | — (Eagle package + JLC NPTH/PTH rules) | Rev 3: no mounting holes (F-032 / R3-P6-05) |
| DP-P6-08 | PASS | confirmed | Outline 90 × 50 rectangle + 9.77 × 2.185 USB tab + three package cutouts (2 pot anchor slots 2.2 × 1.0, encoder D-slot 1.55 × 2.2); 0.05 mm step where the tab meets the edge (cosmetic); two USB leg slots missing in the conversion (DP-P1-07) | §1 | — | Rev 3: 165.3 × 101.8 rounded rectangle, no cutouts (R3-P6-09) |
| DP-P6-09 | PASS | confirmed | Edge/panel parts: jacks on a 12.583 pitch at the right edge (2.28 overhang), micro-SD slot 5.0 past the left edge, micro-USB on its tab at the top, headphone pot 2.08 past the bottom; pots 15.23 pitch, switches 13.46, LEDs 13.5; Seed sockets 40 × 3.175 × 1.016 on 2.54 pitch, rows 15.24 apart; no F-side collisions | §6 | — | Rev 3: Headphones1 9.0 mm overhang next to J7 (R3-P6-07) |
| DP-P6-10 | JUDGMENT | confirmed | Assembly-process notes to carry with the design: PIP reflow of VR_1/VR_2, hand-soldered P5 legs through milled slots, U4 PowerPAD paste region, DNI P2 (+ R78/R84 question), 8 mm cans C62/C63 on the control face | §7 | — | Rev 3: 18 THT parts, no hand-assembly list (R3-P6-08) |
| DP-P6-11 | PASS | confirmed | Mask/paste/tenting consistent with the Eagle rules: 0.0762 frame on all 230 plated pads (NPTH posts 1:1), fiducial windows by polygon, 115 vias tented, paste 1:1 (slivers themselves are Pass 1 DP-P1-13) | Pass 1 §2j | — | Rev 3: 1:1 mask, tented vias (R3-P1-13) |

## 9. Reproduce
```
python3 analysis/daisy_pod/scripts/pod_pass6_mech.py [board.kicad_pcb] [drc_asis.json] [drc_jlc_nc01.json] [bom.txt]
python3 analysis/daisy_pod/scripts/pod_pass1_fill.py             # mask margins, paste regions, fiducials, H1-H4 proximity
python3 -I analysis/daisy_pod/scripts/pod_eagle_brd.py           # Eagle text sizes/ratios, DNI values, stripped layers
```
Defaults point at `reference/electrosmith/daisy_pod/...` and `kicad_out/pod/...`; the scripts only read.
