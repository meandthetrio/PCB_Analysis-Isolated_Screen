# Pass 6 — Mechanical & Assembly, Round 2 (2026-10 files)
**Date:** 2026-10-07 · **Truth checked:** `.kicad_pcb` geometry + `Manifold_Gerbs_2026-10/` paste/mask/silk + DRC baseline (`baseline_2026-10/`) · **References:** Newhaven NHD-2.7-12864WDW3 Rev 6 mechanical drawing (p. 4, archived), JLCPCB capabilities 2026-10-07 · **Status: COMPLETE**

## 1. Board and outline
165.3 × 101.8 mm (bbox x 89.48–254.78, y 61.00–162.80), 1.6 mm, polygon outline **byte-identical to the fabbed LedFix Edge_Cuts** — same SW1 notch at the top edge. Dimension tolerance ±0.2 mm (JLCPCB regular). No change from Round 1.

## 2. Which side is which (new in Round 2)
| Side | Parts |
|---|---|
| **F.Cu (8 parts)** | ENCL1, ENCR1 encoders; TAC_SWITCH_1/2; LED1/2; MK1 mic; **J8 OLED** |
| **B.Cu (92 parts)** | A1 Daisy, all SMD, all five 3.5 mm jacks (J3–J7), J1 barrel, P1 microSD, P2 USB-C, SW1 slide switch, TAC_SHIFT_L1/R1, Headphones1 pot, C23/C24 THT |

The user-interface parts are split: display, encoders and the two main buttons face **front**; the volume pot, power switch, shift buttons and every connector face **back** (connectors exit through the top/bottom edges). The front-panel artwork that was on F.Silkscreen in Round 1 is now on **B.Silkscreen** (3,900 filled polygons, ≈ 10,100 mm² = 60 % of the board, extent x 85.8–244.6 / y 51.4–169.6, i.e. slightly past the outline on all four sides). Either the back is the legend side now, or the artwork was mirrored to the wrong layer when the board was re-laid-out. **Q-R2-6 for Trey.** It matters for §4 and §6.

## 3. Display module fit (J8 = NHD-2.7-12864WDW3) — computed from the Newhaven drawing
Drawing (Rev 6, p. 4): module PCB **82.0 × 47.5 mm**, 2.4 mm PCB + glass to 5.5 mm; 1×20 header, 2.54 mm pitch, 48.26 mm long, starting 16.87 mm from the module's left edge and 4.5 mm below its top edge; **four Ø2.5 mm mounting holes** on a 74.2 × 42.5 mm pattern (3.9 / 2.5 mm from the corners); bezel opening 66 × 33 mm, active area 61.41 × 30.69 mm; FPC/driver bump ≈ 2 mm below the module's lower edge.

Board: J8 is a 20-pin THT row (Ø1.0 drill, 1.7 mm pads) on F.Cu at y = 81.3, pin 1 at x = 196.26, pin 20 at x = 148.0 (rot −90°). Pin 1 on the **right** when viewed from the front = the module face-up with its header on its back, matching the drawing's rear view (pin 1 left from behind) ✓.

Projected module footprint on the board (header centre x = 172.1):
| | Board coordinates |
|---|---|
| Module PCB outline | **x 131.1 – 213.1, y 76.8 – 124.3** |
| Mounting-hole centres | (135.0, 79.3), (209.2, 79.3), (135.0, 121.8), (209.2, 121.8) |
| Active-area / bezel-window centre | ≈ (172.1, 100.7); window ≈ 66 × 33 mm |
| FPC bump below module | y ≈ 124–126, x ≈ 160–185 |

Checks:
- **Nothing on F.Cu under the module** — ENCR1 (231.8, 99.8) is 18 mm clear of the right edge; TAC_SWITCH_1/2, LED1/2 and MK1 sit at y ≥ 131.8, ≥ 7.5 mm below the module's lower edge ✓. The module overhangs nothing: y 76.8 is 15.8 mm inside the top edge.
- **No mounting holes on the board for the module's four Ø2.5 holes** (NPTH inventory: only jack posts, J1, P2). An 82 × 47 mm glass module would hang from 20 soldered header pins alone — a cantilever with the glass 3–8 mm above the board and no standoffs. Round 1's `screen mounting solution.md` describes a tape-and-gasket mount for a bare COG panel and does not apply to this module. → **F-071**.
- DRC courtyard overlaps: **0** (J8's courtyard is only the header row, 146.2–198.1 × 79.5–83.1, so the DRC cannot see the module body — the projection above is the real check).

## 4. Silkscreen (F-033 revisited, F-046)
DRC: 199 `silk_overlap` = 135 footprint-outline-segment × artwork + **63 reference-field × artwork** + 1; 199 `silk_over_copper` = artwork polygons over copper (fab clips on pads, prints over mask); 49 `silk_edge_clearance` = artwork reaching/past the outline (fab clips).
- **92 of 100 reference designators are on B.Silkscreen, and 63 of them are overprinted by the artwork** (A1 ×2, P1, C18, C21, C22, R25 … per the DRC list). On an assembled back side that means the refdes an assembler or rework tech needs are inside solid artwork fills. → **F-072** (JUDGMENT; becomes a VIOLATION of basic assembly practice if the back is *not* the legend side — Q-R2-6).
- 588 footprint silk strokes at 0.12 mm vs JLCPCB's 0.15 mm legend minimum (F-046, cosmetic, confirmed in Pass 1).
- F.Silkscreen now carries only the 8 front-side refdes and outlines; zero board-level drawings.

## 5. Paste, mask, stencil (F-034 revisited)
| Check | Result |
|---|---|
| F.Paste | **12 apertures = LED1 + LED2 only** (unchanged): the top stencil exists solely for parts not on the BOM — F-034 persists |
| B.Paste | 234 apertures; the parser's "10 paste flashes without a mask opening" are exactly the paste-only sub-pads KiCad uses to split exposed-pad paste: U3 ×4, U4 ×4, U6 ×2 ✓ — so **all three exposed pads (TPA6110A2, MAX9814, TPS62172) are stencilled** (TPS6217x: "must be soldered to achieve appropriate power dissipation") ✓ |
| Mask | expansion 1:1 (JLCPCB supports since June 2025); all SMD pads have openings; 0 `solder_mask_bridge` at the 0.10 mm green minimum ✓ |
| THT pads with paste | P2's 4 anchor pads (footprint quirk, harmless) |
| Fiducials | **none** — JLCPCB SMT does not require them for single boards; add two Ø1 mm for repeatability (JUDGMENT, minor) |
| Hand-solder parts | 18 (F-026): all THT + the two THT caps at the display connector |

## 6. Mechanical, holes, clearance
- **No chassis mounting holes** — NPTH inventory unchanged: 5 × Ø1.2 under each of J3–J7 (25), 2 × Ø2.0 at J1, 2 × Ø0.65 at P2. **F-032 persists**; with the display now also unsupported (F-071) the board's only mechanical attachment is still the jack/encoder/switch panel hardware.
- Tallest back-side parts: Headphones1 pot ≈ 15 mm, A1 Daisy ≈ 11 mm (with headers), J1 and C24 ≈ 11 mm, nine 100 µF electrolytics 7.7 mm, jacks 8 mm. Front: encoders 20 mm (H20 shaft), display ≤ 5.5 mm above its header standoff. Enclosure needs ≥ 15 mm behind the board and ≥ 20 mm (plus panel) in front.
- Edge: SW1 pads 0.414 mm, +3V3_D tracks 0.451 mm (Pass 1 — inside JLCPCB's 0.2 mm). Jacks centred 4.2–5.8 mm inside the top/bottom edges with their bushings through the edge, as in Round 1 ✓.
- Single-spoke GND thermals (F-042): the nine pads are SMD reflow or THT hand-solder joints where one spoke is, if anything, easier to solder; no assembly finding. Close as *accepted / layout tidy-up*.

## 7. Findings
- **F-071 (JUDGMENT, strong):** display module has four Ø2.5 mounting holes and the board provides none — 82 × 47 mm glass module on a 20-pin solder cantilever. Add four NPTH at (135.0, 79.3), (209.2, 79.3), (135.0, 121.8), (209.2, 121.8) ±0.3 mm and standoffs matching the header height; retire `screen mounting solution.md` or re-point it at this module.
- **F-072 (JUDGMENT → VIOLATION if the back is not the legend side):** panel artwork moved to B.Silkscreen and overprints 63 of the 92 back-side reference designators.
- **F-073 (PASS):** all three exposed pads stencilled; mask bridges ≥ 0.15 mm vs 0.10 mm min; courtyards 0 overlaps; nothing under the display on the front; module projection clear of every part by ≥ 7.5 mm.
- **F-074 (VIOLATION of the F-071 fix as first written, added 2026-10-08):** the projected top-left hole (135.0, 79.3) is 1.44 mm from SW1 pad 3. Resolution: shift J8 down 5 mm → holes (135.0, 84.3), (209.2, 84.3), (135.0, 126.8), (209.2, 126.8), Ø2.4 for M2; U1/R2 move ≈ 3 mm from the top-right hole; reroute TAC_SHIFT_L, ENCR_A, USART1_RX/TX; module lower edge 0.9 mm from TAC_SWITCH_1/2; trim SW1/C23/C24 tails. Full scan in `FINDINGS.md`.
- Persisting: F-032 (no chassis holes), F-034 (top stencil = missing LEDs), F-026 (hand-solder list), F-046 (0.12 mm silk).
- Closed: F-010 (corrected in Pass 1), F-042 (accepted).

## 8. Questions for Trey
- **Q-R2-6:** which side faces the user? The artwork is on the back silk; the display/encoders are on the front; pot, switches and jacks are on the back.
- **Q-R2-7:** how is the NHD module meant to be held — socketed on the header only, or with standoffs through its four holes?
