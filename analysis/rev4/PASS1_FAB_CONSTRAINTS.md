# Pass 1 (rev 4) — Fab Constraints Report
**Date:** 2026-10-13 · **Truth checked:** `rev4/WavetableController.kicad_pcb` (filled board-level GND zone, F.Cu + B.Cu; copper truth) + `rev4/WavetableController.kicad_pro` rules (byte-identical to rev 3). The rev-4 Gerbers Trey plotted from this file (`rev4/Gerbers/`) were checked first in `rev4/REV4_PASS1_GERBERS.md` and agree with the board file on every number below. · **Thresholds:** JLCPCB capabilities page, fetched 2026-10-13 (same values as the rev-3 fetch, table in `analysis/rev3/PASS1_FAB_CONSTRAINTS.md` §1): 0.10/0.10 mm trace/space ±20 %, PTH ring 0.18 absolute / 0.25 recommended, via 0.15 hole / 0.25 dia, via-via 0.20 / pad-pad 0.45, NPTH-to-track 0.20, copper-to-edge 0.20, legend ≥ 0.15.

Method as rev 3: `analysis/rev4/scripts/pass1_copper.py`, `pass1_connectivity.py`, `pass1_islands.py` (raw output `kicad_out/rev4/pass1_*.txt`), cross-checked against `kicad-cli pcb drc` as-is (`drc_asis.json`, 576 items) and with JLCPCB minimums + netclass clearance 0.1 on a scratchpad copy (`drc_jlc_nc01_allsev.json`, 578 items).

## 1. Measured vs limit (whole board) — rev 3 → rev 4

| # | Parameter | Rev 3 | **Rev 4** | JLCPCB limit | Class |
|---|---|---|---|---|---|
| 1 | Trace width | 0.10: 68 segs / 74.9 mm | **0.10: 68 segs / 74.9 mm** (identical); 0.20: 261 / 857; 0.30: 633 / 3,808; 0.50: 115 / 413 | ≥ 0.10 | ZERO-MARGIN unchanged (R4-P1-01) |
| 2 | Copper clearance | 0.15 (17 U3/U4 pad pairs), 0.20 next | **0.15 (17), 0.20 (120)** | ≥ 0.10 / 0.15 pad-pad | PASS |
| 3 | Vias | 244 × 0.6/0.3 | **253 × 0.6/0.3**, 0 on GND | hole ≥ 0.15 | PASS |
| 4 | PTH annular ring | 0.175 ×4 | **0.175 ×4** (MK1.1/.2 1.0 pad / 0.65 drill; U6.9 ×2 0.6 pad / 0.25 drill); 0.20 ×8 (ENC posts, P2 shield); 0.25 ×4 | abs 0.18 / rec 0.25 | VIOLATION marginal (R4-P1-02) |
| 5 | Drill sizes | 0.25 ×2 … | unchanged: 0.25 ×2, 0.65 ×2, 0.8 ×4, 1.0 ×40, 1.1 ×48, 1.3 ×4, 1.85 ×5, slots as rev 3 | 0.15–6.3 | PASS (0.25: R4-P1-04) |
| 6 | NPTH | 0.65 ×2, 1.2 ×25, 2.0 + 2.0×1.5 | **unchanged** | ≥ 0.5 | PASS |
| 7 | NPTH-to-copper | 0.197 | **0.1966** (P2 A1/A12/B1/B12); next 0.2505 | ≥ 0.20 | VIOLATION marginal (R4-P1-03) |
| 8 | Hole-to-hole | via-via 0.50, pad-pad 0.75 | **unchanged** | 0.20 / 0.45 | PASS |
| 9 | Copper-to-edge | SW1 0.414, /+3V3_D 0.451 | **unchanged** (SW1 pads 0.4143; /+3V3_D F.Cu 0.451; pour 0.5005) | ≥ 0.20 | PASS vs JLC; 5 DRC errors from the project's own 0.5 rule |
| 10 | Board | 165.30 × 101.80, one outline | **unchanged** | — | PASS |

**DRC at JLCPCB minimums (scratch copy, netclass 0.1):** 0 clearance, 0 track-width, 0 edge, 0 drill errors — only 9 `starved_thermal`, 2 `via_dangling`, 75 `silk_edge_clearance` and the library/silk warnings. F-012 re-confirmed.

### 1a. Where the 0.10 mm copper is — unchanged from rev 3
GND 16 segs / 14.4 mm (U4 DFN escapes + U6 EP stitching), Net-(U4-VDD) 9 / 11.9, U4 MICBIAS/CT/TH/CG/MICIN/MICOUT/BIAS 32 / 33.6, /USART1_TX 3 / 5.9 (under LED2), /+3V3_A 3 / 4.8, /USB_IN_N + /USB_IN_MCU_N 5 / 4.2. Trey did not touch any of them.

### 1b. GND zone and stitching — unchanged
- B.Cu fill **12,789 mm² in one piece** (77 % of the board) + 3 slivers (4.4, 1.1, 1.5 mm²); touches 86 of 96 B.Cu GND pad-faces. The same 10 pads as rev 3 reach GND only through one thin track: U2.2, U3.2, U3.3, U4.4/7/9/11, U6.1/4/5.
- F.Cu fill **7,956 mm² in 15 fragments** (4,445 / 952 / 809 / 550 / 437 / 272 / 260 / 88 / 50 / 44 / 33 / 12 / 1.5 / 1.0 / 0.9 mm²) — the same fragment set as rev 3 to the square millimetre. No islands (every fragment touches a GND PTH pad). Single-pad fragments still: #7 (TAC_SWITCH_1.3), #8 (MK1.1), #12 (ENCR1.C), #3/#4/#6 (A1.20).
- **GND vias: 0 of 253.** R3-P1-08 (zero stitching vias) is STILL OPEN; the 9 new vias are on signal nets (encoder RC and SD-cap routing).

### 1c. Starved thermals: 8 → 9
The rev-3 eight (TAC_SWITCH_1.3, U1.5, P2.A12, P2.B1, R18.1, C9.1, U3.3, C10.1) plus **C28.1** — the GND pad of the new 10 µF SD-socket cap, on one 0.5 mm spoke. All electrically connected (DRC 0 unconnected; `pass1_connectivity.py` confirms fill contact), robustness only.

### 1d. Dangling vias: 2, unchanged
/LED_2_R (167.75, 145.9) and /LED_2_B (168.534, 145.743), no F.Cu connection, nets routed elsewhere. R3-P1-07 STILL OPEN.

### 1e. U6 thermal vias — unchanged
Two 0.25 mm holes / 0.60 pads under the WSON EP: legal at JLC (dia ≥ 0.45 → no surcharge), 2 `drill_out_of_range` errors against the project's 0.30 rule, extra drill tool. R3-P1-04 STILL OPEN.

### 1f. Project rules — unchanged
`.kicad_pro` md5 identical to rev 3: `min_track_width 0.0`, `min_clearance 0.0`, edge 0.5, hole 0.3. F-005 / R3-P1-14 STILL OPEN.

## 2. Findings (Pass 1, rev 4)

| ID | Class | Status | Finding | Evidence | Threshold |
|---|---|---|---|---|---|
| R4-P1-01 | ZERO-MARGIN | confirmed (R3-P1-01 unchanged) | 74.9 mm / 68 segments of 0.10 mm copper, same segments as rev 3 (U4 fan-out, U6 EP stitching, USB fan-out, 5.9 mm /USART1_TX under LED2). | `pass1_copper.txt` | JLCPCB 0.10 ±20 % |
| R4-P1-02 | VIOLATION (marginal) | confirmed (F-016 / R3-P1-02 unchanged) | MK1 pads 0.175 mm ring (1.0 / 0.65). 7 Oct fab-margin row "1.1 mm pad" NOT DONE. | annular histogram | JLC abs 0.18 |
| R4-P1-03 | VIOLATION (marginal) | confirmed (F-008 / R3-P1-03 unchanged) | P2 GND pads 0.1966 mm from P2's own 0.65 NPTH. "Shrink pads 0.05" NOT DONE. | hole-to-copper scan | JLC 0.20 |
| R4-P1-04 | JUDGMENT | confirmed (R3-P1-04 unchanged) | U6 EP vias 0.25 hole / 0.60 pad; project DRC errors ×2; extra drill. "0.3 hole / 0.7 pad" NOT DONE. | DRC asis | JLC via rule; .kicad_pro |
| R4-P1-05 | JUDGMENT | confirmed (R3-P1-05 unchanged) | SW1 pads 0.414 / /+3V3_D track 0.451 from the edge: 5 DRC errors against the project's 0.5 rule only. | copper-to-edge scan | JLC 0.20 |
| R4-P1-06 | JUDGMENT | confirmed (R3-P1-06 **+1**) | 9 single-spoke GND pads: the rev-3 eight plus **C28.1** (new SD cap). | DRC + connectivity | — |
| R4-P1-07 | JUDGMENT | confirmed (R3-P1-07 unchanged) | 2 leftover vias on /LED_2_R, /LED_2_B. | DRC via_dangling | — |
| R4-P1-08 | JUDGMENT | confirmed, **re-scoped 2026-10-13** | Zero GND stitching vias and 15 top-side fragments: optional, since every part is on the bottom, the bottom plane is one piece and 73 % of signal routing is on top returning through it. The substantive part: 10 bottom IC GND pins (U2.2 3.3 mm × 0.3; U3.2/.3 2.9 × 0.3; U4.4/7/9/11 1.2–4.8 × 0.1; U6.1/4/5 1.6–3.6 × 0.1 mm) reach the plane only through single stubs inside the zone's 0.5 mm clearance. Fix on the bottom: zone clearance 0.25 near U3/U4/U6 or 0.3–0.5 mm GND stubs. Explanation in `FINAL_REPORT.md` Tier 1 item 1. | `pass1_islands.txt` | layout practice |
| R4-P1-09 | PASS | confirmed | No copper islands; island removal = always; DRC isolated_copper 0. | `pass1_islands.txt` | — |
| R4-P1-10 | PASS | confirmed | Hole-to-hole, via-hole-to-copper, PTH-hole-to-track, mask, tenting: all as rev 3, all pass. | `pass1_copper.txt` | JLC |
| R4-P1-11 | PASS | confirmed | Copper clearance min 0.15 (U3/U4 pad gaps), 0.20 elsewhere; DRC at 0.1/0.1 → 0 clearance / width errors (F-012). | `drc_jlc_nc01_allsev.json` | JLC |
| R4-P1-12 | JUDGMENT | confirmed (F-005 / R3-P1-14 unchanged) | `.kicad_pro` unchanged; DRC minimums still zero. | md5 identical | — |

## 3. Rev-3 Pass-1 findings — status in rev 4
R3-P1-01 ZERO-MARGIN unchanged · R3-P1-02 STILL OPEN · R3-P1-03 STILL OPEN · R3-P1-04 STILL OPEN · R3-P1-05 unchanged (judgment) · R3-P1-06 STILL OPEN, +1 pad · R3-P1-07 STILL OPEN · R3-P1-08 STILL OPEN · R3-P1-09…13 PASS re-confirmed · R3-P1-14 STILL OPEN.

## 4. Reproduce
```
cd kicad_out/rev4 && python3 -I ../../analysis/rev4/scripts/pass1_copper.py ../../rev4/WavetableController.kicad_pcb
python3 -I analysis/rev4/scripts/pass1_connectivity.py rev4/WavetableController.kicad_pcb
python3 -I analysis/rev4/scripts/pass1_islands.py rev4/WavetableController.kicad_pcb
```
