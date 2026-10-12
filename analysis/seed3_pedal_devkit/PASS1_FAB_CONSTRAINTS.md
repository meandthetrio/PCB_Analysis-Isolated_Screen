# Pass 1 (Seed 3 Pedal Dev Kit Rev3) — Fab Constraints Report
**Date:** 2026-10-12 · **Board:** Electrosmith Seed3 Pedal Dev Kit Rev3 (`github.com/daisyaudio/ES-Seed3-DevKit-Pedal` @ f79f932, 2026-10-06), a 197 × 100 mm effects-pedal main board · **Truth checked:** `reference/electrosmith/seed3_pedal_devkit/Rev3/ES-Seed3-DevKit-Pedal-Rev3.kicad_pcb` (KiCad 9 format 20241229, loaded in KiCad 10.0.7 — native, no conversion) with its filled GND zones, **cross-checked against the production Gerber/drill set** `Rev3/production/ES-Seed3-DevKit-Pedal-Rev3-2025-12-10/` (KiCad 9.0.2, 2025-12-10T12:59, ENIG, 1.6 mm), which §2l shows is the same copper to 0.1 µm. Nothing under `reference/` was written.

**Thresholds:** JLCPCB capabilities page (https://jlcpcb.com/capabilities/pcb-capabilities), fetched 2026-10-12, 2-layer 1 oz (§1), **and** the project's own `.kicad_pro` rules (§1a — byte-identical to the Eurorack kit's). Classification per `analysis/SOURCE_OF_TRUTH.md` §4.

Method: identical to the Eurorack pass — `analysis/seed3_pedal_devkit/scripts/kit_pass1_copper.py`, `kit_pass1_fill.py`, `kit_drc_jlc.sh`, `kit_gerber_compare.py`, `kit_gerber_diff_map.py` pointed at this board. Outputs in `kicad_out/pedal3/` (`drc_asis_allsev_10.0.7.json`, `drc_jlc_nc0.1.json`, `pass1_copper.json/.txt`, `pass1_fill.txt`, `gerber_compare.txt`). Note on the baseline: `kicad_out/pedal3/drc.json` was produced by **KiCad 9.0.9** and reports 0 `hole_clearance`; re-running the same project with 10.0.7 adds the **2 `hole_clearance` errors** the Eurorack baseline already showed (same J7 footprint) — a checker difference, not a board difference (§2h).

## 1. Thresholds used (JLCPCB page, 2026-10-12)

| Parameter | JLCPCB 2-layer 1 oz | Note |
|---|---|---|
| Min track / spacing | 0.10 / 0.10 mm | |
| Via hole / diameter | 0.15 / 0.25 | hole position tolerance ±0.075 |
| PTH annular ring | recommended ≥ 0.25; absolute min 0.18 | |
| NPTH min | 0.50 | |
| Via hole-to-hole / pad hole-to-hole | 0.20 / 0.45 | |
| Via hole-to-track / PTH-to-track / NPTH-to-track | 0.20 / 0.28 (0.35 rec.) / 0.20 | |
| Copper to routed edge | ≥ 0.20 | |
| Solder-mask | 1:1 allowed; ≥ 0.09 opening-to-trace; bridge = pad spacing 0.10 (green), 0.13 black/white | |
| Legend | line ≥ 0.15, text ≥ 1.0, pad-to-silk 0.15 | Pass 6 |

### 1a. The project's own rules (`ES-Seed3-DevKit-Pedal-Rev3.kicad_pro`)
Identical to the Eurorack kit: `min_clearance 0.1524`, `min_track_width 0`, `min_copper_edge_clearance 0.025`, `min_hole_clearance 0.2`, `min_hole_to_hole 0.2`, via 0.5 / 0.3 / ring 0.1, `min_resolved_spokes 2`, mask/paste expansion 0, text 0.8 / 0.08, silk classes ignored; netclasses Default (0.2 track, 0.6/0.3 via), CODEC (0.2032, 0.7056/0.35 — CODEC_IN_L/R), SDMMC (0.2, 0.6/0.3 — SDMMC_*), all with 0.1524 clearance; zones F.Cu GND prio 4 / B.Cu GND prio 6, min thickness 0.1016, thermal 0.2532 / 0.2532. No rule areas at all on this board (the Eurorack's jack keep-outs come from a footprint this board does not use).

## 2. Measured vs limit (whole board)

| # | Parameter | Pedal Rev3 (measured) | JLCPCB limit | Own rule | Class |
|---|---|---|---|---|---|
| 1 | Trace width | **min 0.200 mm** (8 segs, 40.0 mm: TOG_SW2 5 segs 20.9 mm, EXPRESSION_IN_EXT 3 segs 19.1 mm) · **0.2032 (8 mil): 17 segs, 76.3 mm, all SDMMC_DETECT** · 0.254: 631 segs, 3,099 mm · 0.406: 179 segs, 959 mm (+3V3 289, +3V3_A 184, +5V_A 170, +9V_A 165, +5V 19, +5V_USB 17, …) · 0.61: 31 segs, 184 mm (power entry) · **0 segs at 0.10** | ≥ 0.10 | netclass 0.2 / 0.2032 | PASS, margin 0.10 (PD-P1-01) |
| 2 | Copper clearance (different nets, same layer) | **0.1524** = the netclass: 1,385 items at 0.1529 from the GND fill, track–via 0.1524 (SDMMC_D2 track vs SDMMC_D3 via), pad–track 0.1524 (+5V_USB track vs U14.4); track–track min **0.171** (TOG_SW1_A vs TOG_SW1_B at x 70.6–71.0, y 125–145); pad–pad 0.20 (J7); pad–via 0.275 | ≥ 0.10 | ≥ 0.1524 | PASS vs JLC (+0.052); **ZERO-MARGIN vs own rule** (PD-P1-02) |
| 3 | Vias | **62 × 0.6/0.3 + 4 × 0.7056/0.35** (CODEC class: CODEC_IN_L/R), ring 0.15 / 0.178, all **tented** (0 of 66 on F/B.Mask; production F_Mask 460 flashes = pads only); via–via hole gap min **0.95**; **4 on GND** (a cluster at (153.0, 87.0), (156.25, 87.0), (161.0, 87.25), (164.25, 87.25) between C24 and C23 under the audio-jack row); busiest nets +9V_A 9, AREF_AUDIO_IN_BIAS 8, +3V3 4, GND 4, +3V3_A 3, SDMMC_DETECT 3 | hole ≥ 0.15, dia ≥ 0.25, hole-hole ≥ 0.2 | 0.5 / 0.3 / ring 0.1 | PASS (PD-P1-03) |
| 4 | PTH annular ring | **SW1 (ON-OFF-ON toggle) 0.161 ×3** (2.845 × 1.422 pad on 1.1 drill); SW2/SW3 (`TOGGLE_ON_ON_2`) 0.339 ×6; FSW_1/FSW_2 footswitch pins **0.254 ×4** (3.048 × 1.524 pad on 1.016); pots 0.275 ×18; Seed A1 0.30 ×40; DIN J1/J10/J11 pins 0.3375 ×21 (2.025/1.35) and shells 0.508 ×6 (3.406/2.39); Neutrik jacks 0.80 ×30 (3.0/1.4); J8 barrel slots 0.5 ×3 (4.0 × 1.8 pad on 3.0 × 0.8 slot, 4.4 × 1.8 on 3.4 × 0.8); SW4/SW5 0.432; LEDs 0.45; U11 0.4; H1–H4 1.75 (7.0/3.5); U7 NPTH 1.0 ring 0 | abs min 0.18, rec. ≥ 0.25 | 0.1 | **VIOLATION (marginal, −0.019)** ×3 (PD-P1-04); FSW at 0.254 = ZERO-MARGIN vs the 0.25 recommendation |
| 5 | Drills (PTH) | 0.8 ×6 (U11), 0.9 ×6 (LEDs), 1.016 ×12 (SW4/5, FSW), 1.1 ×67 (pots, toggles, Seed), 1.35 ×21 (DIN pins), 1.4 ×30 (Neutrik), 2.1 ×12 (pot chassis), 2.39 ×6 (DIN shells), **3.0 × 0.8 ×2 + 3.4 × 0.8 ×1 plated slots** (J8), 3.5 ×4 (H1–H4); vias 0.3 ×62 + 0.35 ×4 → **237 hits, 13 tools, 3 slots**; production drill identical (§2l) | 0.15 – 6.3; ≥ 0.5 rec. PTH; slot width ≥ 0.65 (JLC's slot row was not in the captured page text — **unverified**) | ≥ 0.3 | PASS (PD-P1-05) |
| 6 | NPTH | 0.65 ×2 (J7), 1.0 ×2 (U7) | ≥ 0.50 | — | PASS |
| 7 | Hole-to-hole | via–via 0.95; no pad–pad or via–pad pair under 1.0 | 0.20 / 0.45 | 0.2 | PASS |
| 8 | Copper-to-edge | **0.0231 mm — both GND pours, both layers** (fill 0.0255 from the Edge.Cuts centre-line; the production F_Cu/B_Cu regions are inset 0.0255 on all four sides); next: C36.2 / C41.2 (GND pads of the two 100 µF cans at the left edge) **0.85**, DIN shell pads J1/J10/J11 GND1/GND2 0.9924 | ≥ 0.20 | ≥ 0.025 | **VIOLATION vs JLC** (−0.177); PASS vs own rule — by design (PD-P1-06) |
| 9 | Solder-mask bridge | 11 `solder_mask_bridge` = **J7 USB-C**: 0.200 pad gaps, 0.102 local mask margin → openings overlap by 0.004 (one window over the row); next tightest U7 0.3445 → 0.14 opening gap, U2 SOT-23-5 0.35, U14 0.35, LED2 0.363 | pad spacing ≥ 0.10 for a dam; 1:1 allowed | 0 board, 0.102 local | JUDGMENT (PD-P1-08) |
| 10 | Hole-to-copper | **J7 NPTH 0.65 pegs → J7 GND pads A1/B12 (57.075, 79.69) and B1/A12 (57.075, 86.09): 0.1751** (the 2 `hole_clearance` errors in the 10.0.7 run; absent from the 9.0.9 baseline) · pegs → +5V_USB pads 0.2099 · J7 / U7 NPTH → GND fill **0.2005** · via hole → other-net track 0.3024 (SDMMC_D3 via vs SDMMC_D2 track) · via hole → fill 0.3029 | NPTH-track ≥ 0.20; via-track ≥ 0.20 | 0.2 | **VIOLATION (marginal, −0.025)** ×2 (PD-P1-07); fill at +0.0005 = ZERO-MARGIN |
| 11 | Zones | 2 board zones, each one fragment: F.Cu 16,650.1 mm² (**85 %** of 19,694.6), B.Cu 17,444.9 mm² (89 %); 0 holes-in-fill, 0 islands, 0 rule areas | — | island removal = always | PASS (PD-P1-11) |
| 12 | Board | 197.05 × 100.05 mm rounded rectangle (r 2.5), 56 vertices, no cutouts, 1.6 mm, area 19,694.6 mm² (Pass 6 §1) | — | — | PASS |

### 2a. Where the thinnest copper is
Nothing at JLC's limit. 0.254 mm carries everything (631 segs, 3.10 m); 0.406 the rails (+3V3, +3V3_A, +5V_A, +9V_A ≈ 165–290 mm each); 0.61 the 9 V entry (31 segs, 184 mm: J8 → D5/FB9/FB10 → +9V/+9V_A, the U2 LP2985 ON/OFF node). The 0.2 mm copper is 40 mm on two slow nets: TOG_SW2 (20.9 mm) and EXPRESSION_IN_EXT (19.1 mm, the TRS expression jack J6's ring); **SDMMC_DETECT is 76.3 mm at 0.2032** — the 8 mil value is the CODEC class's width, which suggests the net was routed while assigned to that class (the pattern `SDMMC_*` puts it in SDMMC at 0.2; a KiCad "track width from netclass" would have drawn 0.2). Harmless (2× JLC), but inconsistent with its class. **vs WavetableController rev 3:** 68 segs / 74.9 mm at exactly 0.10. **vs Pod:** 0.2032 min, 674 mm. **vs Eurorack kit:** 0.2 × 7.5 mm, no 0.2032.

### 2b. Via inventory
66 vias: 62 × 0.6/0.3 (ring 0.15) and the 4 CODEC-class 0.7056/0.35 (ring 0.178) on CODEC_IN_L / CODEC_IN_R near (100.7, 98.4–99.7). All tented in the project and in the production mask layers. **4 GND vias**, all in one 11 mm-wide cluster at y ≈ 87 between the 100 µF cans C23/C24 under the ¼" jacks — a local tie for the audio-input ground, not stitching (0.02 per cm²). **vs rev 3:** 244 × 0.6/0.3, 0 on GND. **vs Pod:** 115, 24 on GND (0.53/cm²). **vs Eurorack kit:** 96, 0 on GND.

### 2c. GND: 4 vias, both pours whole (PD-P1-10)
- F.Cu GND one piece (85 %), B.Cu one piece (89 %); all 97 F-side and 32 B-side GND pad-faces touch the fill; 95 of 97 GND pads are fill-only (no track).
- 65 of the 97 GND pads are **SMD on F** (every part is on the front). F↔B GND links: **32 PTH GND pads** (the Seed's 2, J1/J11 DIN shells 3 each, J2–J6 Neutrik sleeves, J8 barrel, FSW_1/2, SW1–SW5's 7, LED cathodes, U11, 6 pot pin-1s) **plus the 4 vias**.
- Distance from each SMD GND pad to the nearest link: 4 pads < 5 mm, 3 at 5–10, 7 at 10–15, 13 at 15–20, **21 at 20–25, 15 at 25–30, 2 at 30–35**. Farthest: **C39.2 31.1** (100 µF at the left), R18.1 30.6, C46.1 28.6, C25.2 28.6, U3.4 28.2 (OPA1652 V−), R71.2 28.0, U1.4 27.4 (MCP6002), R60.2 27.4, C33.2 27.2, C8.2, C30.2, C55.2 ≈ 27. The analogue core (U1/U3/U9/U10 and their RC networks around (85–145, 95–135)) returns to the back plane through the ¼" jack sleeves 20–30 mm away or the 4-via cluster; the digital corner (Seed, SD, USB-C) through the Seed's two GND pins. A whole F pour makes this work; the plane pair is still only point-tied. **vs rev 3:** 0 vias and a 15-fragment F pour. **vs Pod:** 24 vias. **vs Eurorack kit:** 0 vias, farthest 34.6 mm.
- Islands 0, isolated copper 0, unconnected 0.

### 2d. The 2 `starved_thermal` errors (PD-P1-09)
J7.A1/B12 (57.075, 79.69) and J7.B1/A12 (57.075, 86.09) — the USB-C GND pins, 0.6 × 1.15, fill-only, one 0.2532 mm spoke each (≈ 0.6 A, IPC-2221). Same footprint, same geometry, same finding as the Eurorack kit (EU-P1-09). **vs rev 3:** 8. **vs Pod:** 1 (U7.2).

### 2e. The 3 toggle rings at 0.161 (PD-P1-04)
Only SW1 (`parts-for-kicad:TOGGLE_ON_OFF_ON`, C&K ON-OFF-ON) uses the 2.845 × 1.422 oblong on a 1.1 drill (0.161 short-axis ring, below JLC's 0.18 absolute); SW2/SW3 use `TOGGLE_ON_ON_2`, whose pads give 0.339 — the fix already exists on the same board. Nets TOG_SW1_A, GND, TOG_SW1_B. The footswitch pads (FSW_1/2, 3.048 × 1.524 on 1.016) give 0.254, 4 µm over JLC's 0.25 recommendation. **vs rev 3:** MK1 0.175. **vs Pod:** P5 pegs 0.0576 (no net). **vs Eurorack kit:** SW3/SW4 0.161 ×6.

### 2f. Copper to the routed edge: 0.0255 mm (PD-P1-06)
Identical mechanism to the Eurorack kit: `min_copper_edge_clearance 0.025`, pours at ≈ 0 clearance, fill at 0.0255 from the centre-line of the 0.05 mm Edge.Cuts stroke on all four sides, confirmed in the production copper (region bbox inset 0.0255/0.0255/0.0255/0.0255). JLC asks ≥ 0.2 from a routed edge; Electrosmith's fab built it. Note that on this board two 100 µF GND pads (C36.2, C41.2) sit 0.85 mm from the left edge and the DIN shell pads 0.99 from the right edge — all fine against 0.2, so the pours are the only edge issue. **vs rev 3:** 0.414. **vs Pod:** 0.475.

### 2g. The 11 `solder_mask_bridge` errors — J7 (PD-P1-08)
Same vendor footprint `USB4110GFA:GCT_USB4110GFA` as the Eurorack kit, at (56.0, 82.89): 13 pads on 0.5/0.8 pitch, 0.200 gaps, 0.102 local mask margin → adjacent openings overlap by 0.004 → one mask window over the row (the 11 adjacent different-net pairs: GND–VBUS ×2, VBUS–SBU ×2, CC–SBU ×2, CC–D∓ ×2, D+–D− ×2, SBU–D+ ×1). Copper spacing 0.2 ≥ JLC's 0.10 → no fab rule broken; the dam is given up by the footprint. Margin 0 → 0.2 dam. **vs rev 3:** 1:1, min sliver 0.15. **vs Pod:** 0.09 slivers at U4/P1/P5.

### 2h. The 2 `hole_clearance` errors — J7 pegs (PD-P1-07), and the 9.0.9 vs 10.0.7 difference
J7's 0.65 NPTH board-locks at (56.0, 80.0) and (56.0, 85.78) are 0.1751 from the corners of the GND pads A1/B12 and B1/A12 — identical geometry to the Eurorack kit (EU-P1-07): below the project's 0.2 and JLC's NPTH-to-track 0.2 by 0.025, worst case 0.10 with ±0.075 drill placement; pegs → fill 0.2005. The checked-in baseline `kicad_out/pedal3/drc.json` (KiCad 9.0.9) does not report these two; the 10.0.7 run of the same unmodified project does (and 9.0.9 vs 10.0.7 agree on everything else). KiCad 10's hole-clearance test evaluates NPTH pads against SMD pads of the same footprint where 9.0.9 did not; the measured 0.1751 is real either way (the copper script finds it independently). **vs rev 3:** P2 NPTH → pad 0.197 (R3-P1-03). **vs Pod:** 0.2505.

### 2i. DRC with JLC rules (scratch copies)
`drc_asis_allsev_10.0.7.json`: errors 11 mask bridge + 5 courtyards + 2 thermals + 2 hole clearance; warnings 37 silk_over_copper, 23 silk_edge_clearance, 1 silk_overlap, 17 missing_courtyard (Pass 6), 97 + 1 lib noise. `drc_jlc_nc0.1.json` (JLC minimums, netclass 0.1): **0 clearance, 0 track_width, 0 annular (KiCad's 0.05 via rule), 0 hole_to_hole, 0 isolated copper, 0 unconnected**; +2 `copper_edge_clearance` (the pours, 0.0255); warnings +62 text_thickness, +12 text_height, +7 silk_overlap, +3 silk_edge (Pass 6). No clearance noise — the 0.1524 netclass matches the routing. **vs rev 3:** 17 noise errors.

### 2j. Mask / paste consistency
- Mask 1:1 at board level; local margins **0.1016 on 78 pads** (FSW_1/2, J1/J10/J11 DIN, SW1–SW5, VR1–VR6 — Electrosmith's THT footprints), **0.102 on 29** (J7, U7), **0.5 on 3** (FD1–FD3); the KiCad-library parts (Neutrik jacks, barrel jack, Seed, LEDs, passives, ICs, H1–H4) have none. Opening gaps: J7 −0.004 (§2g), U7 0.14 (0.3445 − 0.204), then U2 / U14 0.35 and LED2 0.363 (no local margin, so opening gap = pad gap), everything else ≥ 0.4. Production F_Mask 460 / B_Mask 171 flashes = the pad faces, vias absent → consistent.
- Paste 1:1. **F.Paste 286 apertures on 115 footprints, B.Paste none.** Every SMD pad but the 3 fiducials; no regions. Production F_Paste 286, identical. (Pass 6 §4 has the BOM side.)
- Vias: no openings anywhere. Consistent.

### 2k. Rule areas
None. The Neutrik `Jack_6.35mm_Neutrik_NMJ6HCD2_Horizontal` and DIN `57PC5F` footprints have no keep-outs; the fill runs between their pins (clearance 0.1524 from each). Nothing to flag.

### 2l. Project ↔ production Gerber consistency (PD-P1-12)
Plotted from the project (10.0.7, page origin, 4.6) vs the committed set (9.0.2, aux origin (50,155), 4.5), after origin normalisation and scaling to nm:

| Layer | apertures | flashes | draws | regions | difference |
|---|---|---|---|---|---|
| F_Cu | 60 / 60 | 522 / 522 | 704 / 704 | 1 / 1 | flash sets **identical**; 13 draws differ by 0.0001 mm |
| B_Cu | 26 / 26 | 233 / 233 | 162 / 162 | 1 / 1 | **identical** |
| F_Mask / B_Mask / F_Paste / B_Paste / Edge_Cuts / B_Fab | | 460 / 171 / 286 / 0 | | | **identical** |
| F_Silkscreen | 17 / 72 | 0 / 460 | 8,626 / 8,626 | 563 / 563 | production silk plotted with pad-shaped clear flashes (plot option); draw sets equal |
| Drill | 13 tools, 237 hits + 3 slots in both | | | | 1 via differs by **0.001 mm** |

The committed 2025-12-10 Gerbers are this exact project state (the only deltas are KiCad 9.0.2 → 10.0.7 coordinate rounding and silk plot options); the repo commit (2026-10-06) changed no copper. **vs rev 2:** Gerbers ≠ KiCad (F-006/F-013). **vs rev 3 / Pod:** no Gerbers.

## 3. Findings (Pass 1, Seed 3 Pedal Dev Kit Rev3)

| ID | Class | Status | Finding | Evidence | Threshold source | vs WavetableController rev 3 / vs Pod |
|----|-------|--------|---------|----------|------------------|------------------------------|
| PD-P1-01 | PASS (margin) | confirmed | Narrowest copper 0.200 (8 segs, 40 mm: TOG_SW2, EXPRESSION_IN_EXT) and 0.2032 (17 segs, 76 mm, SDMMC_DETECT — the CODEC class width on an SDMMC-pattern net); fabric 0.254 (3.10 m), rails 0.406, 9 V entry 0.61; nothing at 0.10 | §2 row 1, §2a (`kit_pass1_copper.py`) | JLCPCB caps 2026-10-12; .kicad_pro netclasses | Rev 3: 74.9 mm at 0.10 · Pod: 0.2032 min · Eurorack kit: 0.2 × 7.5 mm |
| PD-P1-02 | PASS vs JLC / ZERO-MARGIN vs own rule | confirmed | Min clearance 0.1524 = the 6 mil netclass (1,385 fill gaps at 0.1529, track–via / pad–track 0.1524); track–track 0.171 (TOG_SW1_A/B), pad–pad 0.20 (J7). 0 clearance errors at 0.1/0.1 and as-is | §2 row 2, §2i | JLCPCB caps; .kicad_pro | Rev 3: 0.15 / 0.20, 17 noise · Pod: 0.127 |
| PD-P1-03 | PASS | confirmed | 66 vias (62 × 0.6/0.3, 4 × 0.7056/0.35 CODEC), all tented in project and production; via–via ≥ 0.95; 4 on GND in one cluster (→ PD-P1-10) | §2 row 3, §2b | JLCPCB caps | Rev 3: 244, 0 GND · Pod: 115, 24 GND |
| PD-P1-04 | VIOLATION (marginal, electrical) | confirmed | SW1 toggle pins 0.161 ring ×3 (2.845 × 1.422 on 1.1) under JLC's 0.18 absolute (−0.019); SW2/SW3 already use `TOGGLE_ON_ON_2` with 0.339 — use that pad on SW1. FSW_1/2 at 0.254 sit on the 0.25 recommendation | §2 row 4, §2e | JLCPCB caps (0.18 abs / 0.25 rec) | Rev 3: MK1 0.175 · Pod: P5 0.0576 (no net) · Eurorack kit: ×6 |
| PD-P1-05 | PASS | confirmed | 13 tools, 237 hits + 3 plated slots (J8 barrel: 0.8 wide × 3.0/3.4 long, 0.5 ring); min PTH 0.8, NPTH 0.65, vias 0.3/0.35; DIN 0.3375 / 0.508, Neutrik 0.80, H1–H4 1.75 rings. JLC's slot-width minimum was not captured from the page (unverified; 0.8 is above the commonly stated 0.65) | §2 rows 4–6 | JLCPCB caps | Rev 3: 15 tools / 411 · Pod: 9 / 152 |
| PD-P1-06 | VIOLATION vs JLC (by design) | confirmed | Both GND pours at 0.0255 mm from the routed edge on all sides (project rule 0.025); confirmed in the production copper. JLC ≥ 0.2 → router cuts copper on every edge. Electrosmith's fab built it; for JLC set zone/edge clearance ≥ 0.25. Other copper ≥ 0.85 (C36/C41 GND pads) | §2 row 8, §2f, §2l | JLCPCB caps (0.2); .kicad_pro 0.025 | Rev 3: 0.414 · Pod: 0.475 |
| PD-P1-07 | VIOLATION (marginal) | confirmed | J7 USB-C 0.65 NPTH pegs 0.1751 from the J7 GND pads (2 `hole_clearance` errors in 10.0.7; the 9.0.9 baseline missed them); project 0.2, JLC NPTH-to-track 0.2 (−0.025, worst case 0.10 with ±0.075 drill placement); pegs → fill 0.2005 | §2 row 10, §2h | JLCPCB caps; .kicad_pro | Rev 3: P2 0.197 (R3-P1-03) · Pod: 0.2505 |
| PD-P1-08 | JUDGMENT | confirmed | 11 `solder_mask_bridge` = J7: 0.2 gaps with a 0.102 local margin → one mask window over the 13-pin row, no dam between D+/D−/CC/VBUS/GND; copper spacing 0.2 ≥ JLC 0.10, no fab rule broken; margin 0 restores a 0.2 dam | §2 row 9, §2g, §2j | JLCPCB caps (bridge 0.10; 1:1) | Rev 3: 1:1, 0.15 · Pod: 0.09 slivers (DP-P1-13) |
| PD-P1-09 | JUDGMENT | confirmed | J7's GND pins A1/B12 and B1/A12 on a single 0.2532 mm spoke each, no track (the 2 `starved_thermal`); add a GND stub/via beside each | §2d | — (IPC-2221) | Rev 3: 8 · Pod: 1 |
| PD-P1-10 | JUDGMENT | confirmed | Only 4 GND vias, all in one cluster under the jack row; pours whole (F 85 %, B 89 %), all 129 GND pad-faces on fill, 95/97 fill-only; 65 F-side SMD GND pads reach B through 32 PTH GND pads + the cluster, 38 of them 20–35 mm from the nearest link (analogue core U1/U3/U9/U10 and the left-edge 100 µF cans) | §2c (`kit_pass1_fill.py`) | — | Rev 3: 0 vias, 15 F fragments · Pod: 24 vias · Eurorack kit: 0 vias |
| PD-P1-11 | PASS | confirmed | Islands 0, isolated copper 0, unconnected 0; one fragment per layer; no rule areas needed | §2 row 11, §2c, §2k | — | Rev 3: 15 fragments · Pod: 1 (+1) |
| PD-P1-12 | PASS | confirmed | Project ↔ production Gerbers identical: flash sets equal on every pad layer, drill table 237 + 3 slots equal, 13 copper draws and 1 via within 0.001 mm (9.0.2 → 10.0.7 rounding), silk differs only by plot options. The 2025-12-10 set is this project state | §2l | — | Rev 2: Gerbers ≠ KiCad · Rev 3 / Pod: no Gerbers |
| PD-P1-13 | PASS | confirmed | Mask/paste sane: 1:1 board; local 0.1016 (ES THT), 0.102 (J7/U7), 0.5 (fiducials); F.Paste 286 = all SMD pads but fiducials, no B paste; vias tented; production flashes identical | §2j | JLCPCB caps (1:1) | Rev 3: 1:1 · Pod: 0.0762 frame |
| PD-P1-14 | JUDGMENT | confirmed | Rule set shared with the Eurorack kit: `min_track_width 0`, edge 0.025, silk ignored; JLC minimums add only the 2 edge errors; KiCad's annular test cannot see PD-P1-04; and the kit's checked-in 9.0.9 DRC baseline hides PD-P1-07 (10.0.7 finds it) | §1a, §2h, §2i | — | Rev 3: `min_track_width 0`, `min_clearance 0` · Pod: converted defaults |
| PD-P1-15 | PASS | confirmed | Via hole → other-net track 0.3024, via → fill 0.3029 (JLC 0.20); no pad hole pair under 1.0 (JLC 0.45); via–via 0.95 | §2 rows 7/10 | JLCPCB caps | Rev 3: 0.35 · Pod: 0.3302 |

## 4. Summary against the rev-3 / Pod / Eurorack fab findings

| Check | Pedal Rev3 | Eurorack Rev3 | WavetableController rev 3 | Pod Rev5 |
|---|---|---|---|---|
| Narrowest copper | 0.20 (40 mm) + 0.2032 (76 mm) | 0.20 (7.5 mm) | 0.10, 74.9 mm | 0.2032 |
| Min clearance | 0.1524 (netclass) | 0.1524 | 0.15 / 0.20 | 0.127 |
| Vias / on GND | 66 / 4 (one cluster) | 96 / 0 | 244 / 0 | 115 / 24 |
| F pour | 1 piece, 85 % | 1 piece, 87 % | 15 fragments | 1 (+1) |
| PTH ring minimum | 0.161 (SW1) | 0.161 (SW3/SW4) | 0.175 | 0.0576 |
| NPTH-to-copper | 0.1751 (J7) | 0.1751 (J7) | 0.197 | 0.2505 |
| Copper-to-edge | 0.0255 (pours) | 0.0255 (pours) | 0.414 | 0.475 |
| Mask | J7 openings merge | same | 1:1 → 0.15 | 0.09 |
| Starved thermals | 2 (J7) | 2 (J7) | 8 | 1 |
| Gerbers vs project | identical | identical | n/a | n/a |

## 5. Reproduce
```
cd kicad_out/pedal3 && python3 ../../analysis/seed3_pedal_devkit/scripts/kit_pass1_copper.py ../../reference/electrosmith/seed3_pedal_devkit/Rev3/ES-Seed3-DevKit-Pedal-Rev3.kicad_pcb
python3 analysis/seed3_pedal_devkit/scripts/kit_pass1_fill.py reference/electrosmith/seed3_pedal_devkit/Rev3/ES-Seed3-DevKit-Pedal-Rev3.kicad_pcb
sh analysis/seed3_pedal_devkit/scripts/kit_drc_jlc.sh reference/electrosmith/seed3_pedal_devkit/Rev3/ES-Seed3-DevKit-Pedal-Rev3.kicad_pcb <scratch_dir> 0.1
python3 -I analysis/seed3_pedal_devkit/scripts/kit_gerber_compare.py kicad_out/pedal3/gerbers reference/electrosmith/seed3_pedal_devkit/Rev3/production/ES-Seed3-DevKit-Pedal-Rev3-2025-12-10/gerbers
python3 analysis/seed3_pedal_devkit/scripts/kit_gerber_diff_map.py <board> kicad_out/pedal3/gerbers <production gerbers> 50 155
```
All scripts take the board path as an argument and never write to `reference/`.
