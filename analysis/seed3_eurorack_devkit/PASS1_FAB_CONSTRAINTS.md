# Pass 1 (Seed 3 Eurorack Dev Kit Rev3) — Fab Constraints Report
**Date:** 2026-10-12 · **Board:** Electrosmith Seed3 Eurorack Dev Kit Rev3 (`github.com/daisyaudio/ES-Seed3-DevKit-Eurorack` @ 651216a, 2026-10-06), a 3U / 28HP module whose PCB is the front panel · **Truth checked:** `reference/electrosmith/seed3_eurorack_devkit/Rev3/Seed3-DevKit-Eurorack-Rev3.kicad_pcb` (KiCad 10 format 20260206, loaded natively in KiCad 10.0.7 — no conversion) with the filled GND zones it carries, **cross-checked against the production Gerber/drill set** `Rev3/production/Seed3-DevKit-Eurorack-Rev3-2026-06-18/` (KiCad 10.0.1, 2026-06-18T11:39, ENIG, 1.6 mm) which is what was fabbed (§2l proves the two are the same copper to 0.1 µm, so the dual-truth problem of rev 2 does not arise here). Nothing under `reference/` was written.

**Thresholds:** JLCPCB capabilities page (https://jlcpcb.com/capabilities/pcb-capabilities), fetched 2026-10-12 (200, 137 kB; the quoted rows are in `kicad_out/../web` scratch and were re-read by regex — §1), 2-layer 1 oz, **and** the project's own `.kicad_pro` rule set (§1a). Both are reported for every check. Classification per `analysis/SOURCE_OF_TRUTH.md` §4.

Method: `analysis/seed3_eurorack_devkit/scripts/kit_pass1_copper.py` (the rev-3/Pod copper script with the KiCad-10 `GetBoardPolygonOutlines(outline, False)` signature; width histogram, vias, drills, annular, hole-to-hole, copper-to-edge, hole-to-copper, clearance; writes `pass1_copper.json`), `kit_pass1_fill.py` (zones, fragments, fill-only GND pads, GND vias and how F-side GND reaches B, tenting, mask margins, pad gaps → mask slivers, J7 geometry), `kit_drc_jlc.sh` (two DRC runs on a scratch copy: project rules with every ignored class raised to warning, and JLC minimums + netclass clearance 0.1), `kit_gerber_compare.py` + `kit_gerber_diff_map.py` (plotted vs production Gerbers/drill: apertures, flash/draw/region counts, exact position sets after origin normalisation). Outputs are in `kicad_out/euro3/` (`drc_asis_allsev.json`, `drc_jlc_nc0.1.json`, `pass1_copper.json/.txt`, `pass1_fill.txt`, `gerber_compare.txt`); the baseline `kicad_out/euro3/drc.json` (10.0.7, project rules) was the starting point.

## 1. Thresholds used (JLCPCB page, 2026-10-12)

| Parameter | JLCPCB 2-layer 1 oz | Note |
|---|---|---|
| Min track / spacing | 0.10 / 0.10 mm | |
| Via hole / diameter | 0.15 / 0.25 (2-layer row: "0.15mm hole size / 0.25mm via diameter") | hole position tolerance ±0.075 |
| PTH annular ring | recommended ≥ 0.25; absolute min 0.18 | |
| NPTH min | 0.50 | |
| Via hole-to-hole / pad hole-to-hole | 0.20 / 0.45 | page rows "Via Hole-to-Hole Spacing 0.2mm / Pad Hole-to-Hole Spacing 0.45mm" |
| Via hole-to-track / PTH-to-track / NPTH-to-track | 0.20 / 0.28 (0.35 rec.) / 0.20 | page rows quoted verbatim |
| Copper to routed edge | ≥ 0.20 | "Copper clearance from routed board edges: ≥0.2 mm" |
| Solder-mask | expansion 1:1 allowed (LDI since 2025-06); ≥ 0.09 opening-to-trace; mask bridge = min pad spacing 0.10 (green…), 0.13 black/white | |
| Legend | line ≥ 0.15, text height ≥ 1.0, pad-to-silk 0.15 | Pass 6 |

### 1a. The project's own rules (`Seed3-DevKit-Eurorack-Rev3.kicad_pro` → `board.design_settings.rules`; identical in the Pedal kit)

| Rule | Value | Note |
|---|---|---|
| min_clearance | **0.1524** (6 mil) | netclasses Default / CODEC / SDMMC all 0.1524 |
| min_track_width | **0** | widths come from the netclass: Default 0.2, CODEC 0.2032, SDMMC 0.2 |
| min_copper_edge_clearance | **0.025** | deliberately tiny — the pours run to the edge (§2 row 8) |
| min_hole_clearance / min_hole_to_hole | 0.2 / 0.2 | |
| min_via_annular_width / min_via_diameter / min_through_hole_diameter | 0.1 / 0.5 / 0.3 | netclass via 0.6/0.3; CODEC 0.7056/0.35 |
| min_resolved_spokes | 2 | source of the 2 `starved_thermal` errors |
| solder_mask_to_copper_clearance / board mask expansion / paste | 0 / 0 / 0 | 1:1, with **per-pad local margins** on 141 pads (§2j) |
| min_silk_clearance / min_text_height / min_text_thickness | 0 / 0.8 / 0.08 | silk classes set to *ignore* (Pass 6) |
| zones | F.Cu GND priority 4, B.Cu GND priority 6, min thickness 0.1016, clearance ≈ 0 (uses netclass), thermal gap/spoke 0.2532 | 15 footprint-level rule areas (one per jack) keep fill, vias and tracks out of the jack bushing |

Everything Electrosmith set is tighter than JLC except the 0.025 edge clearance (JLC 0.2) and the unset track-width floor.

## 2. Measured vs limit (whole board)

| # | Parameter | Eurorack Rev3 (measured) | JLCPCB limit | Own rule | Class |
|---|---|---|---|---|---|
| 1 | Trace width | **min 0.200 mm** (9 segs, 7.5 mm: DAC_CV_1 5.4, DAC_CV_2 1.8, TOG_SW3_A 0.2, Net-(D3-K) 0.2) · 0.254: 805 segs, 3,190 mm · 0.406: 188 segs, 879 mm (+3V3_A 250, +12V 205, −12V 198, +3V3 190, +5V_USB 17) · 0.813: 21 segs, 74 mm (+12V 45, DSY_VIN 13, C46 8.6, GND 7.2) · **0 segs at 0.10** | ≥ 0.10 | netclass 0.2 | PASS, margin 0.10 (EU-P1-01) |
| 2 | Copper clearance (different nets, same layer) | **0.1524 mm** = the netclass to the micron: 1,559 items (pads/vias/tracks) sit at 0.1529 from the GND fill, track–via 0.1524 (SDMMC_D2 track vs SDMMC_D3 via), pad–track 0.1524 (+5V_USB track vs U14.4); track–track min 0.196 (USB_OTG_HS_P/N at (60–65, 97–101)); pad–pad 0.20 (J7 USB-C pins); via–via 0.181 | ≥ 0.10 track; ≥ 0.10 pad spacing | ≥ 0.1524 | PASS vs JLC (+0.052); **ZERO-MARGIN vs own rule** (EU-P1-02) |
| 3 | Vias | **96 × 0.6/0.3** (ring 0.15), all **tented** both sides (0 of 96 on F/B.Mask; the production F_Mask has 444 flashes = pads only, so the fabbed boards are tented too); via–via hole gap min **0.481** ((98.4,70.9)/(99.0,71.4), a POT_4/POT_1 staircase), then 0.549, 0.622; **0 vias on GND** (busiest nets −12V 9, +12V 8, +3V3 6, +3V3_A 4) | hole ≥ 0.15, dia ≥ 0.25, hole-hole ≥ 0.2 | 0.5 / 0.3 / ring 0.1 | PASS (EU-P1-03) |
| 4 | PTH annular ring | **SW3 / SW4 toggle pins 0.161 ×6** (2.845 × 1.422 oblong pad on a 1.1 drill: 0.87 long-axis, 0.161 short-axis) · jacks and pots 0.275 ×69 (1.65 pad / 1.1 drill) · Seed A1 0.30 ×40 (1.7/1.1) · LEDs 0.45 ×6 · P1 / SW1 / SW2 0.432 ×18 (1.88/1.016) · U11 0.40 ×6 · pot chassis 0.508 ×16 (3.116/2.1) · H1–H4 plated slots 0.30 (7.0 × 3.8 pad on 6.4 × 3.2 slot) · U7 1.0 NPTH ring 0 (no copper) | abs min 0.18, rec. ≥ 0.25 | 0.1 | **VIOLATION (marginal, −0.019)** ×6 (EU-P1-04); jacks/pots 0.275 ≥ 0.25 PASS |
| 5 | Drills (PTH) | 0.8 ×6 (U11), 0.9 ×6 (LEDs), 1.016 ×18 (P1, SW1, SW2), 1.1 ×115 (jacks, pots, toggles, Seed), 2.1 ×16 (pot chassis), **6.4 × 3.2 plated slots ×4** (H1–H4); vias 0.3 ×96 → **265 hits, 9 tools, 4 slots**; production drill file identical (§2l) | 0.15 – 6.3 round; ≥ 0.5 rec. PTH | ≥ 0.3 | PASS (EU-P1-05) |
| 6 | NPTH | 0.65 ×2 (J7 USB-C pegs), 1.0 ×2 (U7 micro-SD pegs) | ≥ 0.50 | — | PASS |
| 7 | Hole-to-hole | via–via 0.481; **no pad–pad or via–pad pair under 1.0 mm** | via–via ≥ 0.20, pad–pad ≥ 0.45 | 0.2 | PASS |
| 8 | Copper-to-edge | **0.0231 mm — both GND pours, both layers** (fill outline 0.0255 from the Edge.Cuts centre-line, 0.0005 from the 0.05 mm line's half-width); nothing else under 1.0 mm. Confirmed in the production Gerbers: the F_Cu / B_Cu region bounding box is inset 0.0255 (L/R/B) / 0.0276 (T) from the Edge_Cuts box (§2l) | ≥ 0.20 | ≥ 0.025 | **VIOLATION vs JLC** (−0.177); PASS vs own rule — by design (EU-P1-06) |
| 9 | Solder-mask bridge | 11 `solder_mask_bridge` = **J7 USB-C** (§2g): 13 signal/GND pads on 0.5 mm pitch with gap **0.200** and a per-pad local mask margin **0.102** → opening-to-opening = 0.2 − 0.204 = **−0.004** (the openings merge into one window); next tightest: U7 TF-01A 0.3445 − 0.204 = 0.14, U14 0.35, LED1 0.363 | pad spacing ≥ 0.10 (green) for a dam; 1:1 allowed | expansion 0 board, 0.102 local | JUDGMENT (no fab rule broken: copper gap 0.20; the dam is given up by the footprint) (EU-P1-08) |
| 10 | Hole-to-copper | **J7 NPTH 0.65 pegs → J7 GND pads A1/B12 and B1/A12: 0.1751** (the 2 `hole_clearance` errors) · J7 pegs → +5V_USB pads 0.2099 · J7 / U7 NPTH → GND fill **0.2005** · via hole → other-net track 0.3024 ×2 (SDMMC_D3 via vs SDMMC_D2 track; USB_OTG_HS_P via vs _N track) · via hole → GND fill 0.3029 | NPTH-track ≥ 0.20; via-track ≥ 0.20; PTH-track ≥ 0.28 | 0.2 | **VIOLATION (marginal, −0.025)** ×2 (EU-P1-07); fill at +0.0005 = ZERO-MARGIN |
| 11 | Zones | 2 board zones (F.Cu GND prio 4, B.Cu GND prio 6), each filling as **one fragment**: F.Cu 15,693.8 mm² (**87 %** of the 18,111 mm² board), B.Cu 15,977.1 mm² (88 %); 0 holes-in-fill, 0 islands; 15 jack rule areas | — | island removal = always | PASS (EU-P1-11) |
| 12 | Board | 141.95 × 128.55 mm rounded rectangle (r 2.5), 1 outline / 60 vertices, no cutouts, 1.6 mm, area 18,111.2 mm² (Pass 6 §1) | — | — | PASS |

### 2a. Where the thinnest copper is
There is nothing at JLC's limit. The whole signal fabric is **0.254 mm (10 mil)** — 805 segments, 3.19 m — with 0.406 for the four rails and 0.813 for the power entry (+12V from P1 through D1/FB2, DSY_VIN, the C46 node, a short GND stub). The only 0.2 mm copper is 7.5 mm of necks: DAC_CV_1/DAC_CV_2 out of the Seed (5.4 + 1.8 mm), one 0.2 mm stub on TOG_SW3_A and two on Net-(D3-K). 2× JLC's minimum, and the project itself has no track-width floor (`min_track_width 0`) — the floor is the netclass. **vs WavetableController rev 3:** 68 segs / 74.9 mm at exactly 0.10 (R3-P1-01 ZERO-MARGIN). **vs Pod:** 0.2032 min, 674 mm.

### 2b. Via inventory
96 vias, one size (0.6/0.3 = netclass Default; the CODEC class's 0.7056/0.35 is unused here — CODEC_IN_L/R are routed without vias). Ring 0.15 (3× JLC's 0.05 minimum, no surcharge at 0.6 dia). Busiest nets −12V 9, +12V 8, +3V3 6, +3V3_A 4, POT_4 3, MIDI_TX 3. **None on GND.** Tenting: KiCad's via mask state is "no opening" on both sides and the production F_Mask/B_Mask carry only pad flashes (444/169 = the pad counts) → tented in what was fabbed. **vs rev 3:** 244 × 0.6/0.3, tented, 0 on GND. **vs Pod:** 115 (77 × 0.686/0.330 + 38 × 0.706/0.35), ring 0.178, 24 on GND.

### 2c. GND: no stitching vias at all — how the two planes connect (EU-P1-10)
- Both pours fill as **one piece** (F 87 %, B 88 %). All 85 F-side GND pad-faces and all 39 B-side GND pad-faces touch the fill; 83 of 85 GND pads have no track at all (fill-only).
- 46 of the 85 GND pads are **SMD on F.Cu** (every part is on the front) — they only see the F pour. The two planes are joined solely by the **39 PTH GND pads**: 15 jack sleeves, 8 pot pin-1s, the Seed's 2 GND pins, P1's 6 GND pins, 2 LED cathodes, SW1–SW4's 6 GND pins, U11.
- Distance from each SMD GND pad to the nearest F↔B link (any GND PTH pad; there are no GND vias): 5 pads < 5 mm, 7 at 5–10, 16 at 10–15, 8 at 15–20, 6 at 20–25, 3 at 25–30, 1 at 30–35. Farthest: **U7.MP3 34.6 mm, U7.MP4 27.4, U7.6 26.6** (micro-SD shell/GND), **U2.3 25.5** (MCP6004 V−), C19.2 24.2, U2.5 23.0, U7.MP1 22.1, U2.12/11/10 21–22, **J7.S4/S2 19.7–19.9** (USB-C shell). The SD card socket and the USB-C shell return to the back plane through the jacks ~20–35 mm away; the codec/op-amp decoupling returns through the F pour alone, which is contiguous, so functionally this works (the kit ships) — but the 2-layer plane pair has no low-inductance tie near the two highest-edge-rate connectors.
- Islands: 0 (`isolated_copper` 0 in the all-severity run); unconnected items 0.
**vs rev 3:** also 0 GND vias, but there the F pour is in 15 fragments — here both pours are whole, so the comparison is "same omission, far better pour". **vs Pod:** 24 GND vias (0.53/cm²).

### 2d. The 2 `starved_thermal` errors (zone min spokes 2, actual 1) — EU-P1-09
J7.A1/B12 (57.075, 73.14) and J7.B1/A12 (57.075, 79.54): the USB-C GND pins, 0.6 × 1.15 pads at the two ends of the 0.5 mm-pitch row, no track (fill-only), one 0.2532 mm spoke each in KiCad's fill (the neighbouring +5V_USB pads and the 0.65 NPTH peg take the other spoke positions). A single 0.25 mm × 1 oz spoke is ≈ 0.6 A (IPC-2221 external) — fine for the USB GND return current-wise, but it is the only GND path of the connector's signal pins (the four shell pads S1–S4 are on the fill through full thermals). The micro-SD (U7) has the same 0.102 mask margin but its GND pads are wider and resolve 2 spokes. **vs rev 3:** 8 starved thermals on 0.5 mm spokes (R3-P1-06). **vs Pod:** 1 (U7.2 USBLC6, 0.25 spoke).

### 2e. The 6 toggle-switch rings at 0.161 (EU-P1-04)
`parts-for-kicad:TOGGLE_ON_OFF_ON_SILK` (SW3, C&K 2MS3T1B1M2QE) and `TOGGLE_ON-ON_SILK` (SW4, 2MS1T1B1M2QE): three 2.845 × 1.422 mm oblong pads on 2.54 pitch, 1.1 mm drill → 0.161 ring across the short axis, 0.87 along it. Below JLC's 0.18 absolute PTH ring (and JLC's +0.13/−0.08 hole tolerance eats the short-axis ring entirely at worst case); above the project's 0.1 rule (KiCad's `annular_width` test passes). These carry TOG_SW3_A/B, GND and TOG_SW4 — signals, not shell pegs, so a breakout is electrical. Fix for a JLC order: pad 2.845 × 1.46 (0.18) or 2.845 × 1.6 (0.25); the 2.54 pitch leaves 0.94 between pads at 1.6. **vs rev 3:** MK1.1/MK1.2 0.175 (R3-P1-02). **vs Pod:** P5 USB pegs 0.0576 (no net), pots 0.22.

### 2f. Copper to the routed edge: 0.0255 mm on both faces (EU-P1-06)
The project sets `min_copper_edge_clearance 0.025` and the pours' own clearance to ≈ 0, so KiCad fills to 0.0255 from the Edge.Cuts centre-line on all four sides; the production Gerbers show exactly that (region bbox 0.0255/0.0255/0.0255/0.0276 inside the edge box; the 0.0276 at the top is the rounded corner's chord). Against JLC's "copper clearance from routed edges ≥ 0.2 mm" this is a violation by 0.177 mm: the router will cut through copper on every edge (exposed copper, burrs, the ±0.2 routing tolerance means the actual pull-back varies 0 … 0.2). Against the project's own rule it passes by 0.0005 — i.e. it is intentional, and Electrosmith's fab (ENIG, 2026-06-18) built it. For a JLC order: zone clearance 0.3 or `min_copper_edge_clearance 0.25`. **vs rev 3:** SW1 pads 0.414, +3V3_D track 0.451. **vs Pod:** 0.475 (Eagle 0.381 rule).

### 2g. The 11 `solder_mask_bridge` errors — all J7 (GCT USB4110-GF-A) (EU-P1-08)
Footprint `USB4110GFA:GCT_USB4110GFA` (vendor import, `libs/GCT_USB4110GFA.kicad_mod`): 13 signal pads in one row at x = 57.075 (y 73.14 … 79.54), widths 0.6 (GND, VBUS) and 0.3 (CC, D±, SBU) on 0.5 / 0.8 pitch, **gap 0.200 between every neighbour**, every pad with `solder_mask_margin 0.102`. 0.2 − 2 × 0.102 = −0.004: adjacent openings overlap, so DRC reports each adjacent-different-net pair (A1/B12–A4/B9, A4/B9–B8, A5–B7, A5–B8, A6–A7, A6–B7, A7–B6, A8–B5, A8–B6, B1/A12–B4/A9, B4/A9–B5 = 11). The copper spacing 0.2 is twice JLC's 0.10 pad-spacing minimum, so JLC could print a dam if the openings allowed it; with the footprint as drawn the fab receives one 6.8 mm window over the row (the production F_Mask flashes the 13 overlapping RoundRects). This is how GCT's own recommended land pattern is usually drawn, and the kit ships — but it removes the dam between D+/D− and CC/VBUS neighbours at 0.2 mm. Setting the local margin to 0 (board is 1:1 anyway) gives a 0.2 dam; 0.05 gives 0.10. Same footprint, same 11 errors on the Pedal kit. **vs rev 3:** 1:1 mask, narrowest sliver 0.15 (R3-P1-13). **vs Pod:** Eagle 0.0762 frame → 0.09–0.098 slivers at U4/P1/P5.

### 2h. The 2 `hole_clearance` errors — J7 NPTH pegs (EU-P1-07)
J7's two 0.65 mm NPTH board-lock holes at (56.0, 73.45) and (56.0, 79.23) sit 0.1751 mm from the edge of the GND pads A1/B12 (57.075, 73.14) and B1/A12 (57.075, 79.54) — the pads' 0.6 width puts their left edge at x = 56.775, the hole's right edge at 56.325, and the vertical offset of 0.31 makes the corner distance 0.1751. Below the project's 0.2 (`min_hole_clearance`) and below JLC's NPTH-to-track 0.2 by 0.025; with JLC's ±0.075 hole-position tolerance the worst case is 0.10 from a 0.65 drill to a copper pad (drill smear into the pad edge). The pegs → +5V_USB pads are 0.2099 and pegs → GND fill 0.2005 — the fill is at zero margin. It is the vendor footprint's geometry, and both kits share it. **vs rev 3:** P2 USB-C NPTH → pad 0.197 (R3-P1-03), the same class of problem on a different USB-C footprint. **vs Pod:** 0.2505.

### 2i. DRC with JLC rules (scratch copies, design files untouched)
`drc_asis_allsev.json` (project rules, ignored classes raised to warning): errors = the baseline's 11 mask bridges + 5 courtyards + 2 thermals + 2 hole clearances; warnings 115 silk_over_copper, 33 missing_courtyard, 2 silk_edge_clearance (Pass 6), 93 + 21 lib mismatch/issue noise. `drc_jlc_nc0.1.json` (JLC minimums, netclass 0.1, all severities): **0 clearance, 0 track_width, 0 annular_width (KiCad's test uses its 0.05 via rule, not JLC's PTH 0.18), 0 hole_to_hole, 0 isolated_copper, 0 unconnected**; errors added: **2 `copper_edge_clearance` (actual 0.0255, F and B pours)**; the rest unchanged; warnings added for Pass 6: 31 text_thickness, 9 text_height, 13 silk_overlap, +3 silk_edge_clearance. Unlike rev 2 (F-009) and the Pod conversion there is no clearance-rule noise at all — the project's 0.1524 netclass matches what was routed. **vs rev 3:** 17 noise errors from U3/U4 footprint gaps.

### 2j. Mask / paste consistency
- Mask: board expansion 0 (1:1), `solder_mask_min_width` 0. Local per-pad margins: **0.1016 on 109 pads** (all 15 jacks, P1, SW1–SW4, VR1–VR8 — Electrosmith's own THT footprints), **0.102 on 29 pads** (J7, U7 — vendor imports), **0.5 on 3** (FD1–FD3 `Fiducial_1mm_Mask2mm`), none on the other 303. Resulting opening-to-opening gaps: J7 −0.004 (§2g), U7 0.14, every other footprint ≥ 0.15 (U14 SOT-23-6 0.35, LED1 0.363, 0603s ≥ 0.4). Production F_Mask 444 / B_Mask 169 flashes = exactly the pad faces (NPTH pegs included, 1:1), vias absent → consistent.
- Paste: margin 0 / ratio 0 → 1:1. **F.Paste 272 apertures on 98 footprints, B.Paste none** (single-sided SMT). Every SMD pad except the 3 fiducials carries paste; no drawn paste regions. Production F_Paste 272 flashes, identical. (Pass 6 §4 reconciles this against both BOMs.)
- Vias: no mask openings in project or production. Consistent.

### 2k. Rule areas
15 footprint-level keep-outs (`S_JACK` ×12, `STEREO_JACK_3.5MM` ×3), F.Cu only, ≈ 2.5 × 2.5 mm under each jack's bushing: no fill, no vias, no tracks. They do their job (nothing inside them; the F pour is still one piece around them). No board-level rule areas.

### 2l. Project ↔ production Gerber consistency (EU-P1-12)
`kicad-cli pcb export gerbers` from the project (10.0.7, page origin, 4.6 format) vs the committed set (10.0.1, aux origin (50,155), 4.5 format). After origin normalisation and scaling to nm:

| Layer | apertures | flashes | draws | regions | flash-set / draw-set difference |
|---|---|---|---|---|---|
| F_Cu | 46 / 46 | 536 / 536 | 757 / 757 | 1 / 1 | 20 flashes and 52 draws differ by **0.0001 mm** (nearest-neighbour), none by more |
| B_Cu | 18 / 18 | 261 / 261 | 266 / 266 | 1 / 1 | 17 / 23 at 0.0001 mm |
| F_Mask / B_Mask | 43 / 16 | 444 / 169 | 0 | 0 | 15 at 0.0001 / identical |
| F_Paste / B_Paste | 26 / 0 | 272 / 0 | 0 | 0 | 3 at 0.0001 / identical |
| Edge_Cuts | 1 | 0 | 12 / 12 | 0 | identical |
| F_Silkscreen | 16 / 59 | 0 / 444 | 8,533 / 8,533 | 594 / 594 | the production silk was plotted with pad-shaped clear flashes (43 extra apertures = the pad shapes); draw sets equal to 0.0001 |
| Drill | 9 tools, 265 hits + 4 slots in both | | | | 19 hits differ by **0.001 mm** |

The committed Gerbers are therefore this exact project state — every difference is the last decimal of KiCad's coordinate rounding between 10.0.1 and 10.0.7 (and silk/fab plot options). The repo commit (2026-10-06) is 3½ months after the Gerber date and the copper has not changed. Every number in this report therefore describes the fabbed boards. **vs rev 2:** Gerbers and KiCad files diverged (F-006/F-013…); **vs rev 3:** no Gerbers exist.

## 3. Findings (Pass 1, Seed 3 Eurorack Dev Kit Rev3)

| ID | Class | Status | Finding | Evidence | Threshold source | vs WavetableController rev 3 / vs Pod |
|----|-------|--------|---------|----------|------------------|------------------------------|
| EU-P1-01 | PASS (margin) | confirmed | Narrowest routed copper 0.200 mm (9 segs, 7.5 mm of necks on DAC_CV_1/2, TOG_SW3_A, D3-K); signal fabric 0.254 (3.19 m), rails 0.406, power entry 0.813; nothing at 0.10. 2× JLC; the project has no track-width floor, the netclass (0.2) is the floor | §2 row 1, §2a (`kit_pass1_copper.py`) | JLCPCB caps 2026-10-12 (0.10); .kicad_pro | Rev 3: 68 segs / 74.9 mm at 0.10 (ZERO-MARGIN) · Pod: 0.2032 min |
| EU-P1-02 | PASS vs JLC / ZERO-MARGIN vs own rule | confirmed | Min copper clearance 0.1524 = the 6 mil netclass exactly (1,559 fill gaps at 0.1529, track–via and pad–track 0.1524); track–track 0.196 (USB HS pair), pad–pad 0.20 (J7). DRC at 0.1/0.1 + netclass 0.1: 0 clearance errors; as-is DRC: 0 — no rule noise | §2 row 2, §2i | JLCPCB caps; .kicad_pro | Rev 3: 0.15 / 0.20, 17 noise errors · Pod: 0.127 (5 mil) |
| EU-P1-03 | PASS | confirmed | 96 vias, all 0.6/0.3 (ring 0.15, 3× JLC's min), all tented in project and production; via–via hole gap ≥ 0.481; 0 on GND (→ EU-P1-10) | §2 rows 3/7, §2b | JLCPCB caps | Rev 3: 244 × 0.6/0.3, 0 on GND · Pod: 115, 24 on GND |
| EU-P1-04 | VIOLATION (marginal, electrical) | confirmed | SW3/SW4 toggle pins: 2.845 × 1.422 pad on 1.1 drill → 0.161 short-axis ring ×6, under JLC's 0.18 absolute PTH minimum (−0.019; hole tolerance can consume it); carries TOG_SW3_A/B, TOG_SW4, GND. Passes the project's 0.1. Fix: pad 1.46–1.6 wide | §2 row 4, §2e | JLCPCB caps (PTH ring 0.18 abs / 0.25 rec) | Rev 3: MK1 0.175 (R3-P1-02) · Pod: P5 pegs 0.0576 (no net), pots 0.22 |
| EU-P1-05 | PASS | confirmed | Drill table 9 tools, 265 hits + 4 plated slots 6.4 × 3.2 (H1–H4); min PTH 0.8, min NPTH 0.65 (JLC ≥ 0.5), vias 0.3; jacks/pots 0.275 ring, Seed 0.30, P1/SW 0.432, LEDs 0.45 (all ≥ 0.25 rec.) | §2 rows 4–6 | JLCPCB caps | Rev 3: 15 tools / 411 holes · Pod: 9 tools / 152 |
| EU-P1-06 | VIOLATION vs JLC (by design) | confirmed | Both GND pours run to 0.0255 mm from the routed edge on all four sides (project rule 0.025, pour clearance ≈ 0); confirmed in the production copper Gerbers. JLC requires ≥ 0.2 from a routed edge → the router cuts copper everywhere (exposed edge copper, burrs, pull-back 0–0.2 by tolerance). Electrosmith's fab accepted it; for JLC set the zone/edge clearance ≥ 0.25 | §2 row 8, §2f, §2l | JLCPCB caps (0.2 routed edge); .kicad_pro 0.025 | Rev 3: 0.414 (SW1) · Pod: 0.475 |
| EU-P1-07 | VIOLATION (marginal) | confirmed | J7 USB-C 0.65 NPTH pegs 0.1751 from the J7 GND pads A1/B12 and B1/A12 (the 2 `hole_clearance` errors; project rule 0.2, JLC NPTH-to-track 0.2 → −0.025; worst case 0.10 with ±0.075 drill placement); pegs → GND fill 0.2005 (zero margin). Vendor footprint; identical on the Pedal kit | §2 row 10, §2h | JLCPCB caps (NPTH-to-track 0.2, hole position ±0.075); .kicad_pro | Rev 3: P2 NPTH → pad 0.197 (R3-P1-03) · Pod: 0.2505 |
| EU-P1-08 | JUDGMENT | confirmed | The 11 `solder_mask_bridge` errors are all J7: 0.2 mm pad gaps with a 0.102 local mask margin → the 13 openings overlap by 0.004 and the fab gets one window over the USB-C row (no dam between D+/D−/CC/VBUS/GND). No JLC rule is broken (pad spacing 0.2 ≥ 0.10) and the kit ships; margin 0 would give a 0.2 dam | §2 row 9, §2g, §2j | JLCPCB caps (mask bridge 0.10; 1:1 allowed) | Rev 3: 1:1 mask, min sliver 0.15 · Pod: 0.09–0.098 slivers (DP-P1-13) |
| EU-P1-09 | JUDGMENT | confirmed | J7's two GND pins (A1/B12, B1/A12) hang on a single 0.2532 mm fill spoke each, no track (the 2 `starved_thermal` errors); ≈ 0.6 A capable but the only GND path of the USB signal pins. Add a short GND track or a GND via beside each | §2d | — (IPC-2221 spoke estimate) | Rev 3: 8 starved thermals · Pod: 1 (U7.2) |
| EU-P1-10 | JUDGMENT | confirmed | **0 GND stitching vias.** Both pours are whole (F 87 %, B 88 %), all 124 GND pad-faces on fill, 83/85 GND pads fill-only. The 46 F-side SMD GND pads reach the B plane only through the 39 PTH GND pads (jacks, pots, Seed, P1, LEDs, switches, U11); farthest links: U7 micro-SD shell 27–35 mm, U2 op-amp 21–26 mm, J7 USB-C shell 20 mm. Works (single contiguous F pour), but no low-inductance plane tie near SD/USB | §2c (`kit_pass1_fill.py`) | — | Rev 3: 0 GND vias **and** F pour in 15 fragments (R3-P1-08) · Pod: 24 GND vias |
| EU-P1-11 | PASS | confirmed | Islands 0, isolated copper 0, unconnected 0; F.Cu and B.Cu GND each a single fragment; 15 jack keep-outs respected | §2 row 11, §2c, §2k | — | Rev 3: 15 F fragments · Pod: 1 (+1 via-fed) |
| EU-P1-12 | PASS | confirmed | Project ↔ production Gerbers: identical apertures, flash/draw/region counts on every layer, identical drill table (265 + 4 slots); every positional difference is 0.0001 mm (copper) / 0.001 mm (drill) = KiCad 10.0.1 vs 10.0.7 rounding. The committed 2026-06-18 set is this exact project state; the silk differs only in plot options | §2l (`kit_gerber_compare.py`, `kit_gerber_diff_map.py`) | — | Rev 2: Gerbers ≠ KiCad (F-006/F-013) · Rev 3: no Gerbers · Pod: no Gerbers |
| EU-P1-13 | PASS | confirmed | Mask/paste sane: board 1:1, local margins 0.1016 (ES THT footprints), 0.102 (J7, U7), 0.5 (fiducials); F.Paste 272 = all SMD pads but the fiducials, no B paste; vias tented; production mask/paste flashes identical | §2j | JLCPCB caps (1:1 allowed) | Rev 3: 1:1, tented · Pod: 0.0762 frame |
| EU-P1-14 | JUDGMENT | confirmed | The project rule set (shared with the Pedal kit) is tight where it matters (clearance 0.1524, hole clearance 0.2, spokes 2) but has `min_track_width 0` and `min_copper_edge_clearance 0.025`; silk/courtyard classes are *ignored*. At JLC's minimums it adds only the 2 edge errors (EU-P1-06); KiCad's annular test does not model JLC's 0.18 PTH ring (EU-P1-04 is invisible to DRC) | §1a, §2i | — | Rev 3: `min_track_width 0`, `min_clearance 0` (R3-P1-14) · Pod: converted defaults (DP-P1-15) |
| EU-P1-15 | PASS | confirmed | Via hole → other-net track 0.3024 (JLC 0.20), via hole → fill 0.3029; no pad–pad hole pair under 1.0 (JLC 0.45); via–via 0.481 (JLC 0.2) | §2 rows 7/10 | JLCPCB caps | Rev 3: via 0.35 · Pod: 0.3302 |

## 4. Summary against the rev-3 / Pod fab findings

| Check | Eurorack Rev3 | WavetableController rev 3 | Pod Rev5 |
|---|---|---|---|
| Narrowest copper | 0.20 (7.5 mm), fabric 0.254 | 0.10, 74.9 mm | 0.2032, 674 mm |
| Min clearance | 0.1524 (own netclass) | 0.15 / 0.20 | 0.127 |
| Vias | 96 × 0.6/0.3, tented | 244 × 0.6/0.3 | 115, ring 0.178 |
| GND stitching vias | **0** (pours whole, 39 PTH links) | 0 (F pour in 15 pieces) | 24 |
| PTH ring minimum | 0.161 (toggles, signal) | 0.175 (MK1) | 0.0576 (USB pegs) |
| NPTH-to-copper | 0.1751 (USB-C pegs) | 0.197 | 0.2505 |
| Copper-to-edge | **0.0255 (pours, by design)** | 0.414 | 0.475 |
| Mask | 1:1 + 0.102 local → J7 openings merge | 1:1 → 0.15 | 0.0762 frame → 0.09 |
| Starved thermals | 2 (J7 GND) | 8 | 1 |
| Gerbers vs project | identical (0.1 µm) | n/a | n/a |

## 5. Reproduce
```
cd kicad_out/euro3 && python3 ../../analysis/seed3_eurorack_devkit/scripts/kit_pass1_copper.py ../../reference/electrosmith/seed3_eurorack_devkit/Rev3/Seed3-DevKit-Eurorack-Rev3.kicad_pcb
python3 analysis/seed3_eurorack_devkit/scripts/kit_pass1_fill.py reference/electrosmith/seed3_eurorack_devkit/Rev3/Seed3-DevKit-Eurorack-Rev3.kicad_pcb
sh analysis/seed3_eurorack_devkit/scripts/kit_drc_jlc.sh reference/electrosmith/seed3_eurorack_devkit/Rev3/Seed3-DevKit-Eurorack-Rev3.kicad_pcb <scratch_dir> 0.1
python3 -I analysis/seed3_eurorack_devkit/scripts/kit_gerber_compare.py kicad_out/euro3/gerbers reference/electrosmith/seed3_eurorack_devkit/Rev3/production/Seed3-DevKit-Eurorack-Rev3-2026-06-18/gerbers
python3 analysis/seed3_eurorack_devkit/scripts/kit_gerber_diff_map.py <board> kicad_out/euro3/gerbers <production gerbers> 50 155
```
All scripts take the board path as an argument and never write to `reference/`.
