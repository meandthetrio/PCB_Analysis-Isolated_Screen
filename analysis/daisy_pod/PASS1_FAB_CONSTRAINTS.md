# Pass 1 (Daisy Pod Rev5) — Fab Constraints Report
**Date:** 2026-10-12 · **Board:** Electrosmith Daisy Pod Rev5, the reference design Trey's WavetableController was derived from · **Truth checked:** `reference/electrosmith/daisy_pod/ES_Daisy_Pod_Rev5.brd` (Eagle 9.6.2, source of record — design rules, wires, vias, pads, polygons parsed straight from the XML) **and** `reference/electrosmith/daisy_pod/kicad/ES_Daisy_Pod_Rev5.kicad_pcb` (KiCad 9 conversion, GND zones filled in KiCad — used for pcbnew geometry and `kicad-cli` DRC). Both files were read, never written. Eagle's own fill is not stored in the `.brd`, so every zone statement below is about KiCad's recomputed fill; the 115 unmappable Eagle layers (and 15 non-copper objects) stripped before import are called out wherever they bite (§2g, §2h). No Pod Gerbers exist — the `.brd` is the layout truth.

**Thresholds:** JLCPCB capabilities page (https://jlcpcb.com/capabilities/pcb-capabilities), fetched 2026-10-12, 2-layer 1 oz (§1), **and** the board's own Eagle design-rule set `ES_DRC_MaskedVias *` (§1a). Both are reported for every check, as asked. Classification per `analysis/SOURCE_OF_TRUTH.md` §4 plus **CONVERSION-ARTEFACT** for things that exist only in the KiCad copy.

Method: `analysis/daisy_pod/scripts/pod_pass1_copper.py` (the rev-3 copper script pointed at the Pod; width histogram, vias, drills, annular, hole-to-hole, copper-to-edge, hole-to-copper, clearance), `pod_pass1_fill.py` (zones, fragments, fill-only pads, stitching vias, tenting, mask margins, pad gaps → mask slivers, fiducials, mounting-hole proximity), `pod_eagle_brd.py` (`python3 -I`, Eagle XML: rules, widths, vias with Eagle-derived diameters, polygons, packages, stripped-layer objects, airwires), `pod_drc_jlc.sh` (DRC on a scratch copy with JLC minimums). DRC runs: `kicad_out/pod/drc_asis.json` (converted project's default rules), `kicad_out/pod/drc_jlc.json` (JLC minimums, netclass clearance 0.2 left) and `kicad_out/pod/drc_jlc_nc01.json` (JLC minimums **and** netclass clearance 0.1, all rules at least warning). A drill file exported from the conversion lives in the scratchpad only.

## 1. Thresholds used (JLCPCB page, 2026-10-12)

| Parameter | JLCPCB 2-layer 1 oz | Note |
|---|---|---|
| Min track / spacing | 0.10 / 0.10 mm (4/4 mil) | |
| Via hole / diameter | 0.15 / 0.25; dia ≥ hole + 0.10 (0.15 preferred); preferred min hole 0.20 | 0.2/0.25 holes with via dia < 0.45 cost extra; 0.1/0.15 holes cost extra |
| PTH annular ring | recommended ≥ 0.25; absolute min 0.18 | hole tolerance +0.13 / −0.08 |
| NPTH min / NPTH pad ring | 0.50 / ≥ 0.45 | |
| Via hole-to-hole / pad hole-to-hole | 0.20 / 0.45 | |
| Via hole-to-track / PTH-to-track / NPTH-to-track | 0.20 / 0.28 (0.35 rec.) / 0.20 | |
| Copper to routed edge | ≥ 0.20 (±0.2 routing tolerance) | 0.4 for V-cut |
| Solder-mask bridge | 0.10 (green); 0.13 black/white; expansion 1:1 allowed, ≥ 0.09 opening-to-trace | |
| Legend | line ≥ 0.15, text height ≥ 1.0, pad-to-silk 0.15 | used in Pass 6 |

### 1a. The board's own rules (Eagle `ES_DRC_MaskedVias *`, from `<designrules>`; `pod_eagle_brd.py`)

| Eagle param | Value | Meaning |
|---|---|---|
| mdWireWire / mdWirePad / mdPadPad / mdSmdPad / mdSmdSmd | 5 mil = **0.127 mm** | copper clearance |
| mdWireVia / mdPadVia / mdViaVia / mdSmdVia | 6 mil = 0.1524 | clearance to vias |
| msWidth | 6 mil = **0.1524** | min trace width |
| msDrill | 13 mil = **0.3302** | min drill |
| rvViaOuter 0.25, rlMinViaOuter 7 mil = **0.1778**, rlMaxViaOuter 20 mil | | via ring = clamp(0.25 × drill, 0.1778, 0.508) |
| rvPadTop 0.20, rlMinPadTop 5 mil = **0.127**, rlMaxPadTop 20 mil | | PTH ring = clamp(0.2 × drill, 0.127, 0.508) |
| mdCopperDimension | 15 mil = **0.381** | copper to board edge |
| mlMinStopFrame = mlMaxStopFrame | 3 mil = **0.0762** | solder-mask expansion per side |
| mlViaStopLimit | 16 mil = 0.4064 | vias with drill ≤ 0.4064 get **no** mask opening (tented) |
| mlMin/MaxCreamFrame | 0 | paste 1:1 |
| slThermalIsolate | 10 mil = 0.254 | polygon thermal gap |
| mtCopper | 0.0356 mm (1 oz) | |
| net classes | DEFAULT / POWER width 0.1016, drill 0.2, clearance 0.1016 | class minima, not what was routed |

Everything Electrosmith set is tighter than JLC except the mask frame (JLC prefers 1:1). The converted `.kicad_pro` does **not** carry these rules: it has KiCad defaults (`min_track_width 0`, `min_clearance 0`, netclass clearance 0.2, `min_copper_edge_clearance 0.5`, `min_via_annular_width 0.1`, `min_hole_to_hole 0.25`, `min_through_hole_diameter 0.3`) — the source of the clearance / edge noise in `drc_asis.json` (§2i).

## 2. Measured vs limit (whole board)

| # | Parameter | Pod Rev5 (measured) | JLCPCB limit | Eagle own rule | Class |
|---|---|---|---|---|---|
| 1 | Trace width | **min 0.200 mm** (3 segs, 3.8 mm, SD_CMD) · 0.2032 (8 mil): 198 segs, 674 mm, 27 nets · 0.254: 325 segs, 795 mm, 46 nets · 0.3048: 14 segs, 56 mm · 0.4064: 75 segs, 258 mm (+3V3_D 108, +3V3_A 102, VIN 48) · **0 segs at 0.10** | ≥ 0.10 | ≥ 0.1524 | PASS, margin 0.10 / 0.05 (DP-P1-01) |
| 2 | Copper clearance (different nets, same layer) | **0.127 mm, 10 pairs** = exactly Eagle's 5 mil: USB_OTG_FS_ID ↔ D− ↔ D+ tracks on F.Cu (x 47–58, y 9–15) and the A7 track vs U1.27 (LED_1_R); next 0.1458 (D+ track vs U1.34), 0.1524 ×2 (track-via, SD and AUDIO_OUT_R/HEADPHONE_WIPER_R), 0.165 ×2, 0.186 ×2, 0.197 ×3 (D+/D−); 873 pairs at 0.25 (= zone isolate 0.254) | ≥ 0.10 track; ≥ 0.15 SMD pad-pad | ≥ 0.127 | PASS vs JLC (0.027); **ZERO-MARGIN vs own rule** (DP-P1-02) |
| 3 | Vias | 115: **77 × 0.6858/0.3302 + 38 × 0.7056/0.35**, ring **0.1778** on both (= Eagle rlMinViaOuter; the `.brd` stores no diameter, Eagle derives it), all 115 **tented both sides**; via-via hole gap min 0.666 | hole ≥ 0.15 (0.2 pref), dia ≥ hole + 0.10, ≥ 0.45 avoids surcharge, hole-hole ≥ 0.2 | drill ≥ 0.3302, ring ≥ 0.1778 | PASS vs JLC (ring 0.18 vs 0.05 min); at Eagle's own minimum drill and ring (DP-P1-03) |
| 4 | PTH annular ring | **P5 CASING3/CASING4 0.0576 mm** (micro-USB shell pegs, (67.725, 4.5)/(63.275, 4.5): Eagle `long` pad 0.9652 × 2:1 → 1.93 × 0.965, drill 0.85) · VR_1/VR_2 pins 0.22 ×6 (1.1 drill, 1.54 pad) · pot chassis 0.42 ×4 · P2 header 0.432 ×12 · H1–H4 1.321 ×4 | abs min 0.18, rec. ≥ 0.25 | ≥ 0.127 | **VIOLATION (marginal, mechanical)** ×2 — the 2 `annular_width` DRC errors (DP-P1-04); pots 0.22 below the 0.25 recommendation (DP-P1-05) |
| 5 | Drills (PTH) | 0.85 ×2 (P5 pegs), 1.016 ×12 (P2), 1.1 ×6 (pots), 2.1 ×4 (pot chassis), 3.2 ×4 (H1–H4); vias 0.3302 ×77, 0.35 ×38; **152 holes, 9 tools**; conversion drill export = 152 hits, 0 slots | 0.15 – 6.3; ≥ 0.5 rec. for PTH | ≥ 0.3302 | PASS (DP-P1-06) |
| 6 | NPTH | 1.2 ×8 (jack posts J1–J4), 2.05 ×1 (ENC_1 centre) | ≥ 0.50 | — | PASS |
| 7 | **Missing slots** | Eagle Milling layer 46 in `47589-0001_CUT2`: **2 slots 0.702 × 1.375 mm** at (61.393, 1.5) and (69.607, 1.5), under P5's bottom pads P$1/P$2 — stripped at import; absent from `.kicad_pcb`, Gerbers and drill | — | — | **CONVERSION-ARTEFACT** (DP-P1-07) |
| 8 | Copper-to-edge | **0.475** (P1 micro-SD GND pads P2/P3 at x = 0), 0.4848 (P5 P$1/P$2 to the USB tab edge), 0.498 (both GND pours, Eagle 0.5 inset), 0.500 (jack/encoder/P5 casing pads), 0.587 (HEADPHONE_WIPER_R via), 0.643 (AUDIO_IN_L track) | ≥ 0.20 | ≥ 0.381 | PASS (0.275 / 0.094); the 4 DRC `copper_edge_clearance` errors are the converted project's 0.5 default → config noise (DP-P1-08) |
| 9 | Solder-mask bridge | 6 `solder_mask_bridge` = **fiducials FD1–FD6** (§2g) · computed slivers with Eagle's 0.0762 frame: **U4 MSOP-8 0.0976, P1 micro-SD 0.0976, P5 signal pad ↔ CASING3/4 0.090**; next U7 SOT-23-6 0.198, 0402s 0.248 | ≥ 0.10 (green) | frame 0.0762/side | fiducials: **CONVERSION-ARTEFACT** (DP-P1-09); slivers: **VIOLATION (marginal)** −0.0024 / −0.010 (DP-P1-13) |
| 10 | Hole-to-copper | NPTH (jack posts, encoder) to GND fill **0.2505**; PTH CASING3/4 hole to P5.1 (USB_VBUS) / P5.5 (GND) pads **0.300**; via hole to other-net track 0.3302 ×2 | NPTH-track ≥ 0.20; PTH-track ≥ 0.28 (0.35 rec.); via-track ≥ 0.20 | 0.127 / 0.1524 | PASS (0.05 / 0.02 / 0.13) (DP-P1-14) |
| 11 | Hole-to-hole | via-via **0.666** ((7.386,25.365)/(6.370,25.339)), 0.759, 0.805; no pad-pad or via-pad pair under 1.0 | via-via ≥ 0.20, pad-pad ≥ 0.45 | 0.1524 | PASS |
| 12 | Zones | 3 GND zones: F.Cu full-board 4-vertex (Eagle polygon w 0.2032, isolate 0.254), B.Cu full-board, **B.Cu 15-vertex patch (71.4–77.4, 30.4–34.2) with thermals=no** under U4's power pad — same priority → 1 `zones_intersect` | — | Eagle merges same-net polygons | **CONVERSION-ARTEFACT** (DP-P1-10) |
| 13 | Board | 90.000 × 50.000 mm + 9.77 × 2.185 USB tab, 3 internal cutouts, 1.6 mm, area 4,499.5 mm² (Pass 6 §1) | — | — | PASS |

### 2a. Where the 0.2032 mm (8 mil) copper is — the narrowest routed width

| Net | segs | mm | Net | segs | mm |
|---|---|---|---|---|---|
| USB_OTG_FS_D+ | 11 | 59.3 | TAC_SWITCH_1 | 7 | 22.1 |
| USB_OTG_FS_D− | 11 | 57.9 | SD_D1 | 11 | 21.6 |
| USB_OTG_FS_ID | 9 | 57.3 | MIDI_IN_B | 10 | 18.4 |
| ENC_B | 13 | 54.1 | SD_D0 | 9 | 17.2 |
| ENC_A | 9 | 51.8 | MIDI_IN_A | 12 | 14.1 |
| N$4 / N$2 / N$3 (LED1 R/G/B legs) | 13 / 11 / 7 | 46.9 / 39.1 / 37.1 | SD_CK | 7 | 11.3 |
| MIDI_IN_RING | 12 | 36.3 | SD_CMD (+3 segs at 0.200) | 5 | 9.0 |
| POT_2 / POT_1 | 5 / 2 | 32.3 / 31.0 | USB_VBUS | 7 | 7.4 |
| MIDI_IN_TIP | 10 | 26.3 | SD_D2, TAC_SWITCH_2, USB_D_IN_±, N$77, LED_1_R, A7 | 1–4 each | ≤ 5.7 |

Audio (AUDIO_IN/OUT L/R, HEADPHONE_WIPER) and the SPI/I²C breakouts are 0.254; HEADPHONE_OUT_L/R 0.3048; the three rails 0.4064. 8 mil is **twice** JLC's minimum and 0.05 above Eagle's own `msWidth` — a comfortable margin class, not a finding. **vs WavetableController rev 3:** 68 segs / 74.9 mm at exactly 0.10 (zero margin), trunks 0.3.

### 2b. Via inventory
115 vias, two drills (0.3302 = Eagle `msDrill` exactly; 0.35), one ring (0.1778 = `rlMinViaOuter` exactly — i.e. the design sits on its own via minimum, with 0.10+ to spare against JLC's 0.05 min / 0.075 preferred ring and no surcharge because dia ≥ 0.45). Busiest nets: **GND 24**, +3V3_D 7, AUDIO_OUT_R 6, +3V3_A 5, ENC_A/ENC_B/USB_OTG_FS_ID 4 each. Tenting: the rule set's name (`MaskedVias`) and `mlViaStopLimit` 0.4064 > every via drill mean no via gets a mask opening; the conversion agrees (0 of 115 on F.Mask/B.Mask). **vs rev 3:** 244 × 0.6/0.3 (ring 0.15), tented, 0 on GND.

### 2c. GND pours (KiCad recomputation of Eagle's two full-board polygons + the U4 patch)
- **B.Cu: 3,246.8 mm² in one piece (72 % of the board)** + the 14.3 mm² U4 patch; touches all 17 B-side GND pad-faces and 24 GND vias.
- **F.Cu: 2,645.9 mm² in one piece (59 %)** + one 9.6 mm² fragment at (13.6–16.2, 23.4–32.2) that touches no pad but is fed by the GND via at (15.39, 29.28) → not an island; touches all 17 F-side GND pad-faces and 23 vias.
- Island removal = always; DRC `isolated_copper` 0 in the all-severity run; 0 unconnected items.
- **24 GND stitching vias (0.53 per cm²)**, four of them in a column at x = 85.1 behind the jacks (y 1.9 / 14.6 / 27.3 / 39.4), the rest spread across the Seed and control areas. 31 GND pads have **no track at all** (fill-only: U7.2, J1–J4.1, P5.5, VR_1/2.1, ENC_1.C/D, U1.20/40, S2/S3.3/4, P2.12, P1 ×6, C11.2, C56.1, C60.1, U4.2/3/9, P8.P$1, U15.5). The `.brd` stores these as **54 GND airwires on layer 19** (Eagle keeps polygon-satisfied connections as ratsnest until the polygon is calculated) — anyone CAM-ing from the `.brd` must run the polygon fill first; the KiCad fill resolves all 54. **vs rev 3:** 0 GND vias, F.Cu pour in 15 fragments tied to B.Cu only through component holes.

### 2d. The 1 `starved_thermal` error (zone min spokes 2, actual 1)
U7.2 — USBLC6-2SC6 GND pad, F.Cu, (65.405, 8.057), 0.6 × 1.2 pad between D_IN− and D_IN+ pads on 0.95 mm pitch. No track (fill-only), one 0.2532 mm spoke in KiCad's fill (Eagle: polygon width 0.2032 / thermal isolate 0.254). Electrically connected (0 unconnected). A single 0.25 mm × 1 oz spoke is ≈ 0.6 A (IPC-2221 external) — fine for a TVS clamp current-wise, but it is the ESD return path. JUDGMENT DP-P1-11. **vs rev 3:** 8 starved thermals on 0.5 mm spokes.

### 2e. The 2 `annular_width` errors — P5 CASING3/CASING4 (DP-P1-04)
Eagle package `47589-0001_CUT2` (Molex 47589-0001 micro-B): `<pad name="CASING3" drill="0.85" diameter="0.9652" shape="long"/>` with `psElongationLong 100` → a 1.93 × 0.965 oblong around an 0.85 hole: 0.54 ring on the long axis, **0.0576 on the short axis**. KiCad reports exactly that (actual 0.0576 vs its 0.1 rule). Against JLC this is below the 0.18 absolute minimum (and with +0.13 drill tolerance the short-axis ring can disappear); against Eagle's own `rlMinPadTop` 0.127 it also fails — Electrosmith must have approved the Eagle DRC error. They are no-net shell-peg pads: a plating breakout here is cosmetic/mechanical, not electrical, which is why the product ships. For a JLC order: 1.3 mm round pads (0.225 ring; the neighbouring signal pads are 0.242 away, which then becomes ≈ 0.06 — so better: keep 0.85 drill, make the pad 1.21 round = 0.18 ring and move nothing). **vs rev 3:** MK1.1/MK1.2 0.175 ring (−0.005), ENC posts/P2 shield 0.20.

### 2f. The 4 `copper_edge_clearance` errors (DP-P1-08)
P1.P2 / P1.P3 (micro-SD GND shell pads, 0.475 from the left edge x = 0) and P5.P$1 / P$2 (0.4848 from the USB tab edge at x = 60.615/70.385). All four exceed JLC's 0.20 by ≥ 0.275 and Eagle's 0.381 by ≥ 0.094; they fail only the converted project's KiCad-default 0.5. Config noise. **vs rev 3:** SW1 pads 0.414, +3V3_D track 0.451 (5 errors vs its own 0.5 rule).

### 2g. The 6 `solder_mask_bridge` errors — fiducials (DP-P1-09)
Eagle package `FIDUCIAL_1MM`: a 1.0 mm round SMD (`stop="no" cream="no"`), a **diamond polygon on tStop (layer 29)** with vertices at ±1 mm (mask opening 2.13 mm corner-to-corner in KiCad) **and the same diamond on tRestrict (layer 41)**. Layer 41 is one of the stripped layers, so KiCad's fill runs up to 0.2545 from the pad (r = 0.7545): inside the diamond's corners (corner radius 1.065, inscribed radius 0.753) four wedges of GND copper are exposed → "aperture bridges items with different nets" ×6 (FD1–FD3 F, FD4–FD6 B). In Eagle, the restrict diamond keeps copper out of the whole opening: **no exposed copper on the real board**. If anyone fabs from the conversion, add a copper keepout per fiducial. **vs rev 3:** no fiducials; mask 1:1.

### 2h. The 1 `zones_intersect` error (DP-P1-10)
Three GND zones, all priority 6: the two full-board polygons (F, B; Eagle `width 0.2032 isolate 0.254`) and a **15-vertex B.Cu polygon with `thermals="no"`, width 0.1524**, covering U4 (TPA6110 MSOP-8 PowerPAD) at (71.4–77.4, 30.4–34.2); it touches only U4.9 (the thermal pad) and is the designer's way of giving the PowerPAD a solid connection while the rest of the plane uses thermals. Eagle simply merges same-net polygons; KiCad demands distinct priorities. The intent is real and good; the error is the converter's. (In KiCad: give the patch priority 7.)

### 2i. DRC with JLC rules (scratch copies, design files untouched)
`drc_jlc.json` (JLC minimums, netclass 0.2): 21 `clearance` errors remain (all netclass-0.2 noise). `drc_jlc_nc01.json` (netclass 0.1, all rules ≥ warning): **0 clearance, 0 track-width, 0 hole-to-hole, 0 isolated copper, 0 unconnected**; the only errors left are the 6 fiducial mask bridges, 2 P5 peg rings, 1 U7 thermal and 1 zone intersect discussed above; warnings: 75 silk_over_copper, 62 text_thickness, 57 text_height, 44 silk_edge_clearance, 21 missing_courtyard, 12 silk_overlap (Pass 6). The 22 as-is `clearance` errors (0.127–0.197 actual) are therefore the converted project's 0.2 netclass vs Electrosmith's 5 mil rule — config noise, exactly the rev-2 F-009 pattern. **vs rev 3:** 17 clearance noise errors from U3/U4 footprint gaps; 0 with 0.1/0.1.

### 2j. Mask / paste consistency
- Mask: Eagle `mlMinStopFrame` 0.0762 survived the import as a **per-pad local margin on 230 of 239 pads** (the 9 without are the NPTH jack/encoder posts, opened 1:1) and is in the plotted Gerbers (`F_Mask.gts` apertures are `RoundRect,0.0762…`). Computed slivers: §2 row 9 — U4 and P1 at 0.0976, P5 signal-to-peg 0.090, everything else ≥ 0.198. JLC's 0.10 (green) is missed by 2.4 µm / 10 µm: in practice JLC gangs the openings (one window over the 0.65 mm pitch row), which is normal for MSOP/micro-USB but removes the mask dam between pads → DP-P1-13 VIOLATION (marginal). A 1:1 mask would give 0.25.
- Paste: `mlMinCreamFrame` 0 → 1:1. F.Paste 104 apertures + 14 drawn regions (P5 shell paste ×4, VR_1/VR_2 pin-in-paste ×5 each), B.Paste 89 + 1 region (U4.9 PowerPAD 1.57 × 1.89 — Eagle `cream="no"` plus an explicit tCream rectangle). No paste on: fiducials, P5 P$1/P$2 (shell legs, soldered through the missing slots), U4.9 pad itself (replaced by the region). Consistent (Pass 6 §4 has the BOM side).
- Vias: 0 mask openings (tented) ↔ Eagle `MaskedVias`. Consistent.

### 2k. Mounting-hole keepouts (stripped layers)
`32-PAD_NO_SILK` (H1–H4) has a **vRestrict circle r = 3.556 (layer 43, stripped)** and tKeepout/bKeepout circles r = 3.683 (kept as courtyards). Nearest via to each hole centre: H1 3.94, H3 4.77, H4 5.05, H2 10.37 mm — all outside the stripped via-restrict radius, so nothing was lost. Nearest track end: H3 3.60 (inside the 3.683 part keepout by 0.08 mm; Eagle keepouts police parts, not tracks). PASS.

## 3. Findings (Pass 1, Daisy Pod Rev5)

| ID | Class | Status | Finding | Evidence | Threshold source | vs WavetableController rev 3 |
|----|-------|--------|---------|----------|------------------|------------------------------|
| DP-P1-01 | PASS (margin) | confirmed | Narrowest routed copper is 0.2032 mm (8 mil) on 27 nets / 674 mm (USB D+/D−/ID, encoder, LED legs, MIDI, pots, SD) plus 3 segs at 0.200 (SD_CMD); nothing at 0.10. 2× JLC's minimum, 0.05 over Eagle's own `msWidth` 0.1524; audio 0.254, rails 0.4064 | §2 row 1, §2a (`pod_pass1_copper.py`) | JLCPCB caps 2026-10-12 (0.10); Eagle msWidth | Rev 3: 68 segs / 74.9 mm at exactly 0.10 (R3-P1-01 ZERO-MARGIN) |
| DP-P1-02 | PASS vs JLC / ZERO-MARGIN vs own rule | confirmed | Min copper clearance 0.127 mm (10 pairs: USB ID/D−/D+ tracks x 47–58, y 9–15; A7 track vs U1.27) = Eagle's 5 mil rule to the micron; 0.027 above JLC. DRC with 0.1/0.1 + netclass 0.1: 0 clearance errors; the 22 as-is errors are the converted project's 0.2 netclass | §2 row 2, §2i | JLCPCB caps 2026-10-12; Eagle mdWireWire | Rev 3: 0.15 (U3/U4 pad gaps), 0.20 elsewhere; 17 noise errors (F-009) |
| DP-P1-03 | PASS | confirmed | 115 vias, 0.6858/0.3302 ×77 and 0.7056/0.35 ×38, ring 0.1778 = Eagle's rlMinViaOuter and drill 0.3302 = Eagle's msDrill (design at its own via minima, 0.10+ over JLC's ring min, ≥ 0.45 dia so no surcharge); all tented (MaskedVias); via-via hole gap ≥ 0.666; the 2 `annular_width` errors are **not** vias (→ DP-P1-04) | §2 rows 3/11, §2b | JLCPCB caps 2026-10-12; Eagle via rules | Rev 3: 244 × 0.6/0.3 (ring 0.15), gap 0.50, 0 GND vias |
| DP-P1-04 | VIOLATION (marginal, mechanical) | confirmed | P5 micro-USB shell-peg pads CASING3/4: 1.93 × 0.965 `long` pad on 0.85 drill → 0.0576 ring on the short axis (DRC actual 0.0576); below JLC's 0.18 absolute PTH minimum and Eagle's own 0.127; no-net, so a breakout is cosmetic. Fix: 1.21 mm round pad (0.18 ring) | §2e | JLCPCB caps 2026-10-12; Eagle rlMinPadTop | Rev 3: MK1 0.175 ring (R3-P1-02, −0.005) |
| DP-P1-05 | JUDGMENT | confirmed | VR_1/VR_2 pin pads 1.54 on 1.1 drill → 0.22 ring (Eagle 20 % ratio): above JLC's 0.18 minimum, under the 0.25 recommendation; chassis 0.42, P2 0.432, H1–H4 1.32 | §2 row 4 | JLCPCB caps 2026-10-12 | Rev 3: ENC posts / P2 shield 0.20, encoder S1/S2 0.25 |
| DP-P1-06 | PASS | confirmed | Drill table: 9 tools, 152 holes (115 vias + 37 pads), min PTH 0.85, min NPTH 1.2 (JLC ≥ 0.5); conversion drill export matches the board (152 hits) but has 0 slots (→ DP-P1-07) | §2 rows 5–6 | JLCPCB caps 2026-10-12 | Rev 3: 15 tools, 411 holes, 0.25 thermal vias tripping the 0.3 rule |
| DP-P1-07 | CONVERSION-ARTEFACT (significant) | confirmed | Two 0.702 × 1.375 mm **milled slots** for the Molex 47589-0001 board-lock legs (Eagle layer 46 Milling, at (61.393, 1.5) and (69.607, 1.5), under the B.Cu pads P$1/P$2) were stripped at import. The KiCad board, its Gerbers and drill have no slots; a board built from the conversion cannot seat the USB connector's legs. The `.brd` (and Electrosmith's CAM) has them | §2 row 7, `pod_eagle_brd.py` STRIPPED column | — | Rev 3: n/a (USB-C P2 uses 0.65 NPTH, present) |
| DP-P1-08 | PASS | confirmed | Copper-to-edge min 0.475 (P1 SD GND pads), 0.4848 (P5 bottom pads to the tab edge), pours 0.498; 0.275 over JLC, 0.094 over Eagle's 0.381; the 4 DRC errors are the KiCad-default 0.5 rule | §2f | JLCPCB caps 2026-10-12; Eagle mdCopperDimension | Rev 3: SW1 0.414, +3V3_D 0.451 (R3-P1-05, own 0.5 rule) |
| DP-P1-09 | CONVERSION-ARTEFACT | confirmed | 6 `solder_mask_bridge` = FD1–FD6: the fiducial's tRestrict diamond (layer 41) was stripped, so KiCad's fill enters the 2.13 mm diamond mask opening's corners (fill at r 0.7545 vs inscribed 0.753 / corner 1.065). Eagle's fill respects the restrict → no exposed copper on the real board | §2g | JLCPCB mask bridge 0.10 (not actually at issue) | Rev 3: no fiducials; 1:1 mask, min sliver 0.15 |
| DP-P1-10 | CONVERSION-ARTEFACT (DRC config) | confirmed | `zones_intersect`: the 15-vertex thermals=no B.Cu patch under U4's PowerPAD overlaps the full-board GND polygon at equal priority; Eagle merges same-net polygons. Design intent (solid PowerPAD, thermals elsewhere) is sound | §2h | — | Rev 3: single zone, F+B |
| DP-P1-11 | JUDGMENT | confirmed | U7.2 (USBLC6 GND) hangs on one 0.25 mm spoke, no track (the single `starved_thermal`); connected, ~0.6 A, but it is the ESD clamp's return — add a GND via beside it | §2d | — (IPC-2221 spoke estimate) | Rev 3: 8 starved thermals, 0.5 mm spokes (R3-P1-06) |
| DP-P1-12 | PASS | confirmed | GND: B.Cu plane one piece 3,247 mm² (72 %), F.Cu one piece 2,646 mm² (59 %) + one via-fed 9.6 mm² fragment; 24 stitching vias (0.53/cm²); all 34 GND pad-faces on fill; no islands; 31 fill-only GND pads; the `.brd`'s 54 GND airwires are all satisfied by the fill | §2c, `pod_pass1_fill.py` | — | Rev 3: **0 GND vias**, F.Cu 15 fragments, 10 pads on single thin tracks (R3-P1-08) |
| DP-P1-13 | VIOLATION (marginal) | confirmed | Mask slivers with Eagle's 0.0762 frame (carried into the conversion and its Gerbers): U4 MSOP-8 and P1 micro-SD 0.0976, P5 signal pad to CASING peg 0.090 vs JLC 0.10 (green). Fab will gang those openings; no dam between 0.65 mm-pitch pads. Set the frame to 0 (1:1) → 0.25 | §2j | JLCPCB caps 2026-10-12 (mask bridge 0.10, 1:1 allowed) | Rev 3: 1:1, narrowest 0.15 (R3-P1-13 PASS) |
| DP-P1-14 | PASS | confirmed | Hole-to-copper: NPTH posts → GND fill 0.2505 (JLC 0.20); P5 peg holes → P5.1/P5.5 pads 0.30 (JLC PTH-to-track 0.28 min / 0.35 rec — 0.02 margin); via hole → other-net track 0.3302 | §2 row 10 | JLCPCB caps 2026-10-12 | Rev 3: P2 NPTH-to-pad 0.197 (R3-P1-03 violation); via 0.35 |
| DP-P1-15 | JUDGMENT | confirmed | The converted `.kicad_pro` carries KiCad defaults, not Eagle's rule set; it both hides Electrosmith's tighter intent (5 mil / 6 mil / 7 mil ring / 15 mil edge) and produces 26 noise errors. For any KiCad reuse: clearance 0.127, track 0.1524, edge 0.381, via ring 0.1778, hole 0.33, mask expansion 0.0762 (or 0) | §1a, §2i | — | Rev 3: `min_track_width 0`, `min_clearance 0` still (R3-P1-14 / F-005) |

## 4. Summary against the rev-3 fab findings (side by side)

| Check | Pod Rev5 | WavetableController rev 3 |
|---|---|---|
| Narrowest copper | 0.2032 mm, 674 mm (2× JLC) | 0.10 mm, 74.9 mm (at JLC) |
| Min clearance | 0.127 (own 5 mil rule) | 0.15 / 0.20 |
| Vias | 115, 0.686/0.330 + 0.706/0.35, ring 0.178, tented | 244, 0.6/0.3, ring 0.15, tented |
| GND stitching vias | 24 | 0 |
| F.Cu pour | 1 piece (+1 via-fed) | 15 fragments, pad-tied |
| PTH ring minimum | 0.0576 (USB pegs, no net) | 0.175 (MK1, signal) |
| NPTH-to-copper | 0.2505 | 0.197 |
| Copper-to-edge | 0.475 | 0.414 |
| Mask | 0.0762 frame → 0.09–0.098 slivers | 1:1 → 0.15 |
| Starved thermals | 1 (U7.2) | 8 |
| Conversion-only issues | missing USB slots, fiducial mask bridges, zone priority | n/a (native KiCad) |

## 5. Reproduce
```
python3 analysis/daisy_pod/scripts/pod_pass1_copper.py            # copper tables; writes pass1_copper.json in cwd
python3 analysis/daisy_pod/scripts/pod_pass1_fill.py              # zones, fragments, stitching, mask slivers, fiducials, H1-H4
python3 -I analysis/daisy_pod/scripts/pod_eagle_brd.py            # Eagle rules / widths / vias / packages / stripped layers
sh analysis/daisy_pod/scripts/pod_drc_jlc.sh <scratch_dir> 0.1    # DRC with JLC minimums + netclass 0.1 on a scratch copy
kicad-cli pcb export drill --format excellon --excellon-units mm -o <scratch_dir>/ reference/electrosmith/daisy_pod/kicad/ES_Daisy_Pod_Rev5.kicad_pcb
```
All scripts take the board path as the first argument and never write to `reference/`.
