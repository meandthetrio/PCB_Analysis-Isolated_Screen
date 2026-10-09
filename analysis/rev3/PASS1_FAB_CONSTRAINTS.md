# Pass 1 (rev 3) — Fab Constraints Report
**Date:** 2026-10-09 · **Truth checked:** `rev3/WavetableController.kicad_pcb` (contains the filled board-level GND zone → copper truth; no rev-3 Gerbers exist) + `rev3/WavetableController.kicad_pro` rules · **Thresholds:** JLCPCB capabilities page (https://jlcpcb.com/capabilities/pcb-capabilities), fetched 2026-10-09, 2-layer 1 oz; exact numbers quoted in §1.

Method: every number below comes from a script over the whole board (`analysis/rev3/scripts/pass1_copper.py`, `pass1_connectivity.py`, `pass1_islands.py`; raw output in `kicad_out/rev3/pass1_copper.json`), cross-checked against three `kicad-cli pcb drc` runs: `drc_asis.json` (project rules), `drc_jlc.json` (JLC board minimums, project netclass clearance 0.2 left in place) and `drc_jlc_nc01_allsev.json` (JLC minimums **and** netclass clearance 0.1, all rules at least warning — the scratchpad copy is `kicad_out/rev3/WavetableController_jlcrules.kicad_pro`-style, design files untouched). Classification per `analysis/SOURCE_OF_TRUTH.md` §4.

## 1. Thresholds used (JLCPCB page, 2026-10-09)

| Parameter | JLCPCB 2-layer 1 oz | Note |
|---|---|---|
| Min track / spacing | 0.10 / 0.10 mm, width tolerance ±20% | 2 oz would be 0.16/0.16 |
| Pad-to-track clearance | 0.10 mm | SMD pad-to-pad (different nets) 0.15 mm |
| Via hole / diameter | 0.15 / 0.25 mm; dia ≥ hole + 0.10 (0.15 preferred); preferred min hole 0.20 | Note ③: 0.2/0.25 mm holes with via dia **< 0.45 mm** cost extra |
| PTH annular ring | recommended ≥ 0.25 mm; absolute min 0.18 mm | hole tolerance +0.13/−0.08 mm |
| NPTH pad annular ring | recommended ≥ 0.45 mm | min NPTH 0.50 mm |
| Drill range | 0.15 – 6.3 mm | PTH ≥ 0.5 mm recommended against mask/tin in hole |
| Via hole-to-hole / pad hole-to-hole | 0.20 / 0.45 mm | |
| Via hole-to-track / PTH-to-track / NPTH-to-track | 0.20 / 0.28 (0.35 rec.) / 0.20 mm | |
| Copper to routed edge | ≥ 0.20 mm | ±0.2 mm routing tolerance |
| Solder-mask bridge | 0.10 mm (green) | mask opening 1:1 allowed |
| Legend | line ≥ 0.15 mm, text height ≥ 1.0 mm, pad-to-silk 0.15 mm | (used in Pass 6) |

## 2. Measured vs limit (whole board)

| # | Parameter | Rev 3 (measured) | JLCPCB limit | Margin | Class |
|---|-----------|------------------|--------------|--------|-------|
| 1 | Trace width | **0.100 mm: 68 segs, 74.9 mm** · 0.200: 261 segs, 864 mm · 0.300: 580 segs, 3,665 mm · 0.500: 123 segs, 425 mm | ≥ 0.10 | **0.000** on 74.9 mm (was 3,850 mm in rev 2) | **ZERO-MARGIN**, 98% reduced (R3-P1-01) |
| 2 | Copper clearance (different nets, same layer) | **0.150 mm** (17 pairs, all U3 HVSSOP/U4 DFN pad-to-pad gaps); next 0.200 mm (120 pairs: P2, U2 pads, USB tracks/vias) | ≥ 0.10 track; ≥ 0.15 SMD pad-pad | 0.05 / 0.00 | PASS (R3-P1-12) |
| 3 | Vias | 244 vias, all 0.60 dia / 0.30 hole (ring 0.15), all tented both sides | hole ≥ 0.15, dia ≥ hole + 0.10 | 0.15 / 0.20 | PASS |
| 4 | PTH annular ring | **0.175 mm ×4: MK1.1, MK1.2 (1.0 pad / 0.65 drill) and U6.9 thermal vias ×2 (0.6 pad / 0.25 drill)**; 0.200 ×8 (ENCL1/ENCR1 MP posts 3.2×2.0 / 2.8×1.5 slot; P2 shield S1 ×4); 0.25 ×4 (encoder S1/S2); rest ≥ 0.30 | abs min 0.18, rec. ≥ 0.25 | **−0.005** (MK1); U6.9 judged as vias (OK) | **VIOLATION (marginal)** (R3-P1-02 = F-016 still open) |
| 5 | Drill sizes (PTH) | 0.25 ×2 (U6.9), 0.65 ×2 (MK1), 0.8 ×4, 1.0 ×40, 1.1 ×48, 1.3 ×4, 1.85 ×5; slots 0.4×1.4 ×15 (P1), 0.6×1.4/1.7 ×4 (P2 shield), 0.8×1.5 ×10 (jacks), 2.8×1.5 ×4 (encoders) | 0.15 – 6.3 | ample | PASS; 0.25 hole: see R3-P1-04 |
| 6 | NPTH sizes | 0.65 ×2 (P2), 1.2 ×25 (jacks), 2.0 and 2.0×1.5 slot (J1) | ≥ 0.50 | 0.15 | PASS |
| 7 | NPTH-to-copper | **0.197 mm** (P2 GND pads A1/A12/B1/B12 to P2's own 0.65 NPTH); next 0.251 (P2 NPTH to /+5V_USB track), 0.2505 (jack/J1 NPTH posts to GND pour) | ≥ 0.20 | **−0.003** | **VIOLATION (marginal)** (R3-P1-03 = F-008 still open) |
| 8 | Hole-to-hole (edge gap) | via-via **0.50** (12 pairs, e.g. (124.466,74.392)/(123.750,74.750)); pad-pad 0.75 (U6.9 pair); via-pad ≥ 1.0 | via-via ≥ 0.20; pad-pad ≥ 0.45 | 0.30 / 0.30 | PASS (R3-P1-10) |
| 9 | Via hole-to-other-net copper | 0.35 mm (USB vias at (122.0,75.25), (123.75,74.75); SPI vias at (131.25,135.5)) | ≥ 0.20 | 0.15 | PASS (R3-P1-11) |
| 10 | PTH hole-to-other-net track | ≥ 0.45 mm (none below) | ≥ 0.28 | ≥ 0.17 | PASS |
| 11 | Copper-to-edge | **SW1 4 anchor pads 0.414 mm**; **/+3V3_D F.Cu 0.3 mm track 0.451 mm** (3 segs, (91.75,151.1)→(120.54,160.75) along the bottom edge); GND pour 0.5005; next 0.669 | ≥ 0.20 | 0.21 / 0.25 | PASS vs JLC; the 5 DRC errors are against the project's own 0.5 rule (R3-P1-05) |
| 12 | Solder mask | expansion 0 (1:1), min pad gap 0.15 (U3/U4) | bridge ≥ 0.10 | 0.05 | PASS (R3-P1-13) |
| 13 | Board | 165.30 × 101.80 mm, 1.6 mm, one closed outline | — | — | PASS |

### 2a. Where the remaining 0.1 mm copper is (all 68 segments)

| Net | segs | mm | Location |
|---|---|---|---|
| GND | 16 | 14.4 | U4 (MAX9814 DFN-14, 0.4 mm pitch) pad escapes at (189–192, 155–157) and U6 (TPS62172 WSON) thermal-pad stitching at (194.5–198.9, 122–124) |
| Net-(U4-VDD) | 9 | 11.9 | U4 escapes (192.2–197.8, 153.8–156.0), one F.Cu seg |
| Net-(U4-MICBIAS) / -TH / -CT / -CG / -MICIN / -MICOUT / -BIAS | 32 | 33.6 | all U4 escapes, inside (185–198, 149–158) |
| /USART1_TX | 3 | 5.9 | F.Cu (197.0,139.0)→(202.5,138.75), under LED2 |
| /+3V3_A | 3 | 4.8 | B.Cu (187.75,155.75)→(187.75,159.07), U4 supply |
| /USB_IN_N, /USB_IN_MCU_N | 5 | 4.2 | P2/U2 fan-out at (122–123.75, 67.8–76.2) |

Everything else is ≥ 0.2 mm. The three long power/signal trunks flagged in rev 2 (+3V3_D 254 mm, I2C, SD, MIDI) are now 0.3 mm; +3V3_D has 8 vias, USART 13/11 vias.

### 2b. Via inventory
244 vias (rev 2: 94), one size (0.6/0.3). Busiest nets: /USART1_TX 13, /USART1_RX 11, /USB_IN_MCU_N 11, /ENCR_CLICK 10, /USB_IN_MCU_P 9, AUDIO_IN_L 8, /+3V3_D 8, /ENCR_A/B 8 each. **GND: 0 vias** (see R3-P1-08). The drill file exported from this board (`kicad_out/rev3/gerbers/WavetableController.drl`) has 244 × 0.30 + 2 × 0.25 hits = exactly the board's vias + U6 thermal pads; 411 holes total, 15 tools.

### 2c. GND zone sanity
- One zone, net GND, F.Cu + B.Cu, filled; min thickness 0.25, clearance 0.5, thermal gap 0.5, spoke 0.5, island removal = always.
- **B.Cu fill: 12,852 mm² in one piece** (≈ 77% of the ≈ 16,760 mm² board) + 3 slivers (4.4, 1.1, 1.5 mm²); touches 84 of the 94 B.Cu GND pad-faces; 20 GND track segments (26 mm) feed the remaining 10 (U2.2, U3.2, U3.3, U4.4/7/9/11, U6.1/4/5 — each reaches GND via one 0.1–0.3 mm track).
- **F.Cu fill: 7,990 mm² in 15 fragments** (4,466 / 965 / 809 / 550 / 437 / 272 / 260 / 88 / 50 / 44 / 33 / 12 / 1.5 / 1.0 / 0.9 mm²); every fragment touches ≥ 1 GND PTH pad → **no islands**; 40/40 F.Cu GND pad-faces touch the fill. Fragments are cross-stitched to B.Cu only through component PTH pads (J8 GND pins ×10, A1.20/A1.40, TAC_SWITCH_1/2, TAC_SHIFT_L1/R1, ENCL1/ENCR1 C+S2, MK1.1, Headphones1.3/6, P2 shield ×4, C23.1, C24.2, U6.9 ×2). Single-pad fragments: #7 (12 mm², TAC_SWITCH_1.3 — the one-spoke pad), #8 (44 mm², MK1.1), #12 (88 mm², ENCR1.C), #3/#4/#6 (A1.20).
- DRC: 0 unconnected items; 0 `isolated_copper` in the all-severity run.

### 2d. The 8 `starved_thermal` errors (zone min spokes 2, actual 1)
Independent connectivity check (`pass1_connectivity.py`, `GetConnectedTracks`/fill collision):

| Pad | Net | Layer | Touches fill? | Other path | Verdict |
|---|---|---|---|---|---|
| TAC_SWITCH_1.3 (134.0,136.25) | GND | F.Cu | yes, 1 spoke (also B.Cu) | none | connected |
| U1.5 (207.88,87.23) | GND | B.Cu | yes, 1 spoke | none | connected |
| P2.A12 / P2.B1 (126.95,67.755) | GND | B.Cu | yes, 1 spoke | pad-to-pad with each other | connected |
| R18.1 (185.31,149.78) | GND | B.Cu | yes, 1 spoke | none | connected |
| C9.1 (196.0,157.03) | GND | B.Cu | yes, 1 spoke | none | connected |
| U3.3 (211.79,159.1) | GND | B.Cu | **no** | 1 track, 0.30 mm | connected |
| C10.1 (185.31,154.89) | GND | B.Cu | yes, 1 spoke | none | connected |

No connectivity gap (DRC reports 0 unconnected). A single 0.5 mm × 1 oz spoke carries ≈ 1 A (IPC-2221 external) — adequate for every pad above (bypass caps, opto GND, USB GND). It is a robustness/thermal-relief count issue, not a fab or electrical one → JUDGMENT R3-P1-06.

### 2e. The 2 `via_dangling` warnings
`/LED_2_R` via at (167.750,145.900) and `/LED_2_B` via at (168.534,145.743): both sit mid-track on B.Cu (3 B.Cu segments each), have **no F.Cu connection** (nothing within 2.5 mm on F.Cu), and the nets are fully routed around them (R39.1→A1.24 and R40.1→A1.30 via other vias at (167.8,149.0)/(168.6,149.0)). They are leftover vias: harmless electrically; each adds a hole and an isolated F.Cu annulus, and they sit 0.50 mm hole-edge from their neighbours (JLC min 0.20). Delete → JUDGMENT R3-P1-07. (The neighbouring `/LED_2_G` via at (167.0,146.449) is a real layer change.)

### 2f. U6 (TPS62172 WSON-8) thermal-pad vias
Two PTH pads "9" in the footprint at (196.387,122.959) and (197.387,122.959): 0.25 mm hole, 0.60 mm pad, ring 0.175, hole-to-hole 0.75. Against JLCPCB via rules: hole 0.25 ≥ 0.15 ✓, dia 0.60 ≥ 0.25 + 0.10 ✓, and because the via diameter is ≥ 0.45 mm JLC's note ③ surcharge for 0.2/0.25 mm holes **does not apply**. They fail only the project's own `min_through_hole_diameter 0.3` (2 `drill_out_of_range` errors) and add a 2nd drill tool. Judged as vias: PASS; as a tidy-up, make them 0.30 like the other 244 → JUDGMENT R3-P1-04.

### 2g. Project DRC rules (`rev3/WavetableController.kicad_pro`, F-005)
`min_track_width 0.0`, `min_clearance 0.0` (netclass Default 0.2 is what actually polices spacing), `min_copper_edge_clearance 0.5`, `min_hole_clearance 0.25`, `min_hole_to_hole 0.25`, `min_via_diameter 0.5`, `min_via_annular_width 0.1`, `min_through_hole_diameter 0.3`, `min_resolved_spokes 2`, `min_silk_clearance 0.0`, `min_text_height 0.8`. Unchanged from rev 2 → F-005 STILL OPEN. The 0.5 edge rule and 0.3 hole rule are stricter than JLC and produce 7 of the 32 rev-3 DRC errors; the 17 `clearance` errors are the netclass-0.2 vs 0.15-pitch footprint noise already dispositioned as F-009.

## 3. Findings (Pass 1, rev 3)

| ID | Class | Status | Finding | Evidence | Threshold source |
|----|-------|--------|---------|----------|------------------|
| R3-P1-01 | ZERO-MARGIN | confirmed | 0.10 mm copper reduced from 3,850 mm (rev 2) to **74.9 mm / 68 segments**, confined to the U4 MAX9814 DFN fan-out (54 segs), U6 thermal stitching, P2/U2 USB fan-out (5 segs) and a 5.9 mm /USART1_TX run under LED2. Still exactly at JLC's 0.10 minimum with ±20% tolerance; all long trunks now 0.3 mm. Recommend 0.15 mm for the USART/USB/3V3_A bits (room exists); the U4 escapes can stay | `pass1_copper.py` width histogram, §2a | JLCPCB caps 2026-10-09 (0.10/0.10, ±20%) |
| R3-P1-02 | VIOLATION (marginal) | confirmed — **F-016 STILL OPEN** | MK1.1/MK1.2 (170.963/172.863,136.0): 1.0 mm pad, 0.65 mm drill → 0.175 mm ring, 5 µm under JLC's 0.18 absolute minimum (0.25 recommended); with JLC's +0.13 mm hole tolerance the finished ring can be ≈ 0.11 mm. Footprint unchanged from rev 2 (`Sensor_Audio:POM-2244P-C3310-2-R`); fabbed OK twice. Fix: 1.2 mm pad | pad/drill geometry, annular histogram | JLCPCB caps 2026-10-09 |
| R3-P1-03 | VIOLATION (marginal) | confirmed — **F-008 STILL OPEN** | P2 (USB-C, moved to (123.75,64.08)) GND pads A1/A12/B1/B12 are 0.197 mm from the footprint's own 0.65 mm NPTH holes (JLC NPTH-to-copper ≥ 0.20). Same stock footprint as rev 2; latent | NPTH-to-copper scan (`hole_to_copper_under_0p45`) | JLCPCB caps 2026-10-09 |
| R3-P1-04 | JUDGMENT | confirmed | U6 thermal vias 0.25 hole / 0.60 pad: legal at JLC (hole ≥ 0.15, dia ≥ hole+0.1, no surcharge since dia ≥ 0.45) but trip the project's 0.3 min-hole rule (2 DRC errors) and add a drill tool. Change to 0.30 hole or relax the rule | §2f, drill file tool list | JLCPCB caps 2026-10-09 (via note ③) |
| R3-P1-05 | JUDGMENT | confirmed | Copper-to-edge: SW1 anchor pads 0.414 mm and the /+3V3_D 0.3 mm F.Cu track 0.451 mm from the bottom edge — both above JLC's 0.20 (margins 0.21/0.25) and only fail the project's self-imposed 0.5 rule (5 DRC errors). Either move the +3V3_D track 0.05 mm inboard or set the rule to 0.3; rev-2 F-010 (0.0 mm at the SW1 notch) is **FIXED** — the notch is gone | copper-to-edge scan §2 row 11; DRC asis vs jlc | JLCPCB caps 2026-10-09 (≥ 0.2 routed edge) |
| R3-P1-06 | JUDGMENT | confirmed | 8 starved-thermal GND pads each hang on one 0.5 mm spoke (U3.3 on one 0.3 mm track): electrically connected, no fab issue, but single-neck GND returns for the USB connector (P2 A12/B1) and the audio parts (U3, C9, C10, R18). Reduce zone thermal gap to 0.3 mm or add a short GND track per pad | §2d | — (IPC-2221 for the 1 A spoke estimate) |
| R3-P1-07 | JUDGMENT | confirmed | 2 leftover vias on /LED_2_R (167.75,145.9) and /LED_2_B (168.534,145.743) with no F.Cu connection — delete | §2e | — |
| R3-P1-08 | JUDGMENT (strong) | confirmed | **Zero GND stitching vias.** The F.Cu pour is 15 fragments tied to the B.Cu plane only through component through-holes; three fragments depend on a single pad, and 10 B.Cu GND pads (U2, U3, U4, U6) reach ground only by one thin track. The B.Cu plane itself is solid (one 12,852 mm² piece). Add GND vias at every F.Cu fragment, at U3/U4/U6 GND pads and along the audio section before fab | §2c, `pass1_islands.py` | — (layout practice; cross-ref Pass 2/5 for the noise argument) |
| R3-P1-09 | PASS | confirmed | No copper islands: all 19 fill fragments touch a GND pad; island removal set to "always"; DRC isolated_copper 0 | §2c | — |
| R3-P1-10 | PASS | confirmed | Hole-to-hole: via-via 0.50, pad-pad 0.75, via-pad ≥ 1.0; NPTH-to-track 0.251, NPTH-to-pour 0.2505 | §2 rows 7–8 | JLCPCB caps 2026-10-09 |
| R3-P1-11 | PASS | confirmed | Via-hole-to-other-net copper 0.35; PTH-hole-to-other-net track ≥ 0.45 | §2 rows 9–10 | JLCPCB caps 2026-10-09 |
| R3-P1-12 | PASS | confirmed | Min copper clearance 0.15 (U3/U4 footprint pad gaps), 0.20 everywhere else; DRC with 0.1/0.1 and netclass 0.1 → 0 clearance, 0 track-width errors (F-012 re-confirmed). The 17 DRC `clearance` errors are F-009 config noise | `pass1_copper.py` clearance histogram; `drc_jlc_nc01_allsev.json` | JLCPCB caps 2026-10-09 |
| R3-P1-13 | PASS | confirmed | Mask 1:1 (expansion 0), narrowest mask sliver 0.15 ≥ 0.10; all 244 vias tented both sides | board settings, via tenting flags | JLCPCB caps 2026-10-09 |
| R3-P1-14 | JUDGMENT | confirmed — **F-005 STILL OPEN** | `.kicad_pro` still has `min_track_width 0.0` and `min_clearance 0.0`; set 0.1/0.1 (JLC) so KiCad can catch width regressions; the 0.5 edge and 0.3 hole rules are stricter than JLC and generate the only "errors" the fab would not care about | §2g | — |

## 4. Rev-2 fab findings — status in rev 3

| Rev-2 ID | Rev-3 status | Evidence |
|---|---|---|
| F-004 0.1 mm traces (3,850 mm) | **STILL OPEN, 98% reduced** → R3-P1-01 | 74.9 mm / 68 segs at 0.10; trunks now 0.3 mm |
| F-005 DRC minimums zeroed | **STILL OPEN** → R3-P1-14 | rev3 `.kicad_pro` rules unchanged |
| F-006 no GND pour in `.kicad_pcb` | **FIXED** | one GND zone F.Cu+B.Cu, filled, 12,852 mm² B / 7,990 mm² F; no Gerber/pcb split anymore |
| F-008 P2 NPTH-to-copper 0.194 | **STILL OPEN** → R3-P1-03 | 0.197 mm, same footprint |
| F-010 SW1 pads at 0.0 mm edge | **FIXED** (notch removed) → R3-P1-05 | SW1 pads 0.414 mm, outline is a plain rounded rectangle |
| F-012 DRC at JLC minimums clean | **PASS re-confirmed** → R3-P1-12 | 0 clearance / width errors with 0.1/0.1 + netclass 0.1 |
| F-016 MK1 annular 0.175 | **STILL OPEN** → R3-P1-02 | unchanged footprint; ENC MP / P2 shield still 0.20 |
| F-017 Gerber vs pcb via count delta | **N/A** (no fab Gerbers for rev 3); board ↔ exported drill consistent (244 + 2) | drill file tool hits |
| F-023 4 dangling GND stubs | **FIXED** (0 `track_dangling`); new: 2 dangling LED vias → R3-P1-07 | DRC asis |
| F-009 U3/U4 clearance config noise | still present, still noise | 17 errors, 0.15 pad gaps |

## 5. Reproduce
```
python3 -I analysis/rev3/scripts/pass1_copper.py        # tables, writes pass1_copper.json in cwd
python3 -I analysis/rev3/scripts/pass1_connectivity.py  # starved thermals, dangling vias, fill fragments
python3 -I analysis/rev3/scripts/pass1_islands.py       # per-fragment GND pad/track contact
kicad-cli pcb drc --severity-all --format json -o drc.json <scratch copy with JLC rules + netclass clearance 0.1>
```
Run from any directory; the scripts take the board path as the first argument (default `rev3/WavetableController.kicad_pcb`) and never write to the design files.
