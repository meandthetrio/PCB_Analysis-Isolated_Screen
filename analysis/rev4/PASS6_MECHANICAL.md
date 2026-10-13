# Pass 6 (rev 4) — Mechanical & Assembly Report
**Date:** 2026-10-13 · **Truth checked:** `rev4/WavetableController.kicad_pcb` + `kicad_out/rev4/drc_asis.json` / `drc_jlc_nc01_allsev.json` · **Thresholds:** JLCPCB (legend ≥ 0.15 mm, text ≥ 1.0 mm, pad-to-silk 0.15, edge 0.2); NHD-2.7-12864WDW3 mechanical drawing as recorded in rev-3 Pass 6 (82.0 × 47.5 mm, 4 × Ø2.5 holes on 74.2 × 42.5). Script `analysis/rev4/scripts/pass6_mech.py` (patched to tolerate removed refs), raw `kicad_out/rev4/pass6_mech.txt`; renders `kicad-cli pcb render` top/bottom (scratchpad).

## 1. Board — unchanged
Edge.Cuts one closed 132-vertex polygon, 165.30 × 101.80 mm, R≈9 corners, no notches. F = control face (ENCL1/ENCR1, TAC_SWITCH_1/2, LED1/LED2, MK1, J8 — 8 footprints); B = everything else (104 footprints).

## 2. Silkscreen — unchanged
447 silk DRC items (199 `silk_over_copper`, 199 `silk_overlap`, 49 `silk_edge_clearance`; 75 at JLC's 0.15 silk clearance), all from the 3,900-polygon back-side artwork + the three mirrored texts ("Stellar Crucible | Manifold", "v4.1", "Designed by FJ Bourgeois"). `silk_over_copper pad targets: []` — no refdes on a pad; JLC clips artwork from pads. All 112 refdes 1.0 mm / 0.15 mm (exactly the minimum, R3-P6-02); footprint outlines 0.12 mm. The silk still runs off all four edges (85.8–253.7 × 51.4–169.6). The new parts' refdes (C19–C22, C27, C28, R31/R32/R34/R41) are buried in the art like the rest of the B side. R3-P6-01/02 unchanged.

## 3. Courtyards
0 overlaps, 0 missing. 10 protrude past the outline (panel parts: J1, J3–J7, P2, TAC_SHIFT_L1/R1, Headphones1 by 9.0 mm). Tight pairs: C15/R29 0.00, C18/R30 0.20, C17/FB6 0.70, C19/R31 0.19, C20/R32 0.19, C21/R34 0.16, C22/C21 0.19, C23/C24 0.21, L1/R33 0.68 (L1's courtyard shrank with the Murata pattern), C6/C7 0.46.

## 4. Paste vs BOM
F.Paste = 12 = LED1 + LED2; B.Paste = 264 (rev 3: 260; +2 × 0603 pads … net of the removed D6/FB7 and the added C27/C28/R34/R41/C19–C22 size changes). BOM (Pass 4): every B-side paste footprint has a BOM line; LED1/LED2 have none (R4-P4-01). 18 no-paste THT parts unchanged; exclude-from-pos only on J3–J7.

## 5. Mounting holes and the OLED module — NOT DONE (7 Oct row 5, R3-P6-05/06)
- NPTH inventory identical to rev 3: P2 0.65 ×2, jacks 1.2 ×25, J1 2.0 + 2.0×1.5. **No chassis holes, no module holes.**
- J8 unchanged: F side, rot −90, pin 1 (196.258, 81.301), pin 20 (147.998, 81.301), 2.54 pitch, courtyard 146.2–198.1 × 79.5–83.1. The ask was "move to y 86.3, add four Ø2.4 holes at (135.0/209.2, 84.3/126.8)". Nothing moved.
- Module overlay unchanged: fits only toward +y (x 131.1–213.1, y 78.8–126.3), clear of all F parts; −y would overhang the top edge by 24.7 mm. The module's hole sites still land on R2/R5/U1 and 0.7 mm from C22's old spot (C22 is now a 10 nF at the right encoder, so that specific collision is gone; the R2/R5/U1 one is not).

## 6. New-part placement (rev 4)
| Part | Side / position | Observation |
|---|---|---|
| C19, C20, R31, R32 (ENCL RC) | B, (101.25, 95.5–100.75) in a column beside ENCL1 | 10.2 mm from the left edge; courtyards 0.19 mm apart; on the B.Cu pour (GND pads direct) |
| C21, C22, R34, R41 (ENCR RC) | B, (246.75, 96.3–101.5) beside ENCR1 | **6.5 mm from the right edge**, under the "Stellar Crucible" text column; courtyards 0.16–0.19 mm |
| C27, C28 (SD caps) | B, (93.5, 145.0) / (97.0, 144.75) next to P1 | 4.0 mm from the left edge; C28.1 single-spoke thermal |
| D2–D5 | B, (139.8–144.0, 78.8–84.8) | SOD-123F pads replaced SOD-323 in place; no courtyard conflicts |
| L1 | B, (199.25, 119.5) | Murata pattern; 0.68 mm to R33 |

## 7. Headphones1 — unchanged (R3-P6-07): bushing 9.0 mm outside the bottom edge, 16.75 mm from J7.

## Findings (rev 4, Pass 6)
| ID | Class | Status | Finding | Evidence |
|---|---|---|---|---|
| R4-P6-01 | JUDGMENT | confirmed (R3-P6-01 unchanged) | Back-side artwork: 447 silk warnings, refdes buried, art off all edges and into J1's NPTH; nothing on a pad. | §2 |
| R4-P6-02 | ZERO-MARGIN | confirmed (R3-P6-02 unchanged) | Refdes 1.0 / 0.15 mm at the minimum; outlines 0.12 mm. "Silk outlines 0.15" NOT DONE. | §2 |
| R4-P6-03 | PASS | confirmed | Courtyards clean; tight pairs listed. | §3 |
| R4-P6-04 | VIOLATION | confirmed (R3-P6-04 / F-034 STILL OPEN) | F.Paste = LED1/LED2's 12 apertures; LEDs on no BOM line. | §4, Pass 4 |
| R4-P6-05 | JUDGMENT | confirmed (R3-P6-05 unchanged) | **No mounting holes for board or module; J8 not moved** (row 5 NOT DONE). | §5 |
| R4-P6-06 | JUDGMENT | confirmed (R3-P6-06 unchanged) | Module fits only toward +y; buck and rail caps still in the x 165–200 corridor. | §5 |
| R4-P6-07 | JUDGMENT | confirmed (R3-P6-07 unchanged) | Headphones1 bushing outside the outline. | §7 |
| R4-P6-08 | JUDGMENT | confirmed (R3-P6-08 STILL OPEN) | Hand-assembly list still missing (one-sheet BOM); 18 THT parts + the hand-soldered LEDs. | §4, Pass 4 |
| R4-P6-09 | PASS | confirmed | Outline unchanged, one polygon. | §1 |
| R4-P6-10 | PASS | confirmed | Back texts mirrored; front refdes unobstructed. | §2 |
