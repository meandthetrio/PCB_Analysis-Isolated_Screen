# Status of the 7 October "Rev 2 Design Review" items in the rev-4 files
**Date:** 2026-10-13 · **Baseline:** `analysis/rev3/OCT7_REVIEW_STATUS.md` (rev-3 scoring, 9 October) plus the decisions made in chat after rev 3 (LED values 5a; /+9V_FLAG re-pointing 5b; encoder RC placement 5c; SD caps 5d; inrush 5e). Every row re-measured on `rev4/` with the scripts in `analysis/rev4/scripts/`.

**Rev-3 score was 10 done, 2 done with a different part, 6 not done, 1 documentation.** The six NOT DONE rows were 2c, 3c, 5, 6b, 7, 9, plus the SD-socket caps row. **In rev 4: 2c, 3c, 6b, 7 and 9 are DONE (7 with the caps at the encoder end, accepted); the SD-caps row is DONE at the socket; 5 is deferred by decision (screen not mounted in this build); the 3d documentation item is still open but, with the hand-soldered Würth LEDs confirmed, is paperwork only.** Nothing regressed. The GND-stitching discrepancy noted in the rev-3 baseline still stands: **0 of 253 vias are on GND.**

## "Fix before ordering" items

| # | Asked for (7 Oct) | Rev 3 | **Rev 4** | Evidence | Still to do / consequence if left |
|---|---|---|---|---|---|
| 1 | C25 10 µF → 16/25 V 0805 | DONE | **DONE** | C15850 10 µF 25 V 0805 (now ×2 with C28) | — |
| 2a | Beads 200 mA → 2 A | DONE, different part | **DONE, different part (unchanged)** | FB2–FB6 C14709 120 Ω / 2 A / 50 mΩ; ≤ 22 % of rating; FB7 removed | — |
| 2b | R31/R32 3.3 Ω → ½ W | DONE (over-delivered) | **DONE / MOOT** | R29/R30 remain 3.3 Ω 1 W 2512 (≤ 132 mW); R31/R32 are now 10 k encoder pull-ups — the second filter no longer exists (decision 5b) | — |
| 2c | Feed U6 from the C19 node, before R31 | NOT DONE | **DONE** | /+9V_FLAG = FB6 output; U6.2/U6.3 + C25 + the six LED resistors sit on it ahead of R29; ≈ 8.1 V, independent of display load (Pass 2 §2) | — |
| 3a | Low-side switch per LED | DONE, different part | **DONE (unchanged)** | Q1–Q6 MMBT3904 + 1 k | — |
| 3b | LED polarity | DONE (correct for the Würth part) | **DONE (unchanged)** | settled | — |
| 3c | LED resistors (decision 5a: 510 red / 390 G-B, 0603) | NOT DONE | **DONE** | R24/R27 510 Ω (C23193), R21/R25/R26/R28 390 Ω (C23151); 11.6 / 12.1 mA, 69 / 57 mW at the 8.1 V node (Pass 2 §3) | — |
| 3d | LED part vs files (documentation) | DOCUMENTATION | **DOCUMENTATION (still open, not a build blocker)** | schematic Value still "CLS6B-FKW", Cree pin labels, no LED line on any BOM sheet. **Kyle 2026-10-13: Trey hand-solders the approved Würth 150505M173300, so assembly is covered** | Value → 150505M173300, relabel pins, add a hand-solder sheet when convenient |
| 4 | BOM: C17 off the 100 nF line; delete S1/S2/U5 | DONE | **DONE (unchanged)** | 92/92 join clean | — |
| 5 | Move J8 to y 86.3; four M2 holes at (135.0/209.2, 84.3/126.8); module outline in footprint | NOT DONE | **ACKNOWLEDGED — WILL POTENTIALLY DEAL WITH LATER** (Kyle 2026-10-13: the screen is not being mounted in this build) | J8 pin 1 still (196.26, 81.30); NPTH set identical to rev 3; 0 mounting holes (Pass 6 §5) | Deferred by decision. If the module is fitted later it hangs on 20 solder joints until the holes exist; the enclosure window position stays open |
| 6a | U6 drawing vs BOM | DONE | **DONE (unchanged)** | FB → GND; R33 PG pull-up harmless | — |
| 6b | L1 on the DFE201610P footprint | NOT DONE | **DONE** | `Inductor_SMD:L_Murata_DFE201610P` in sch + PCB (pads 0.55 × 1.60 at ±0.725) | — |
| 6c | L1 next to U6 SW | DONE | **DONE** (3.79 mm) | — | — |
| 6d | C26 22 µF → 0805 | DONE | **DONE** | C45783 | — |
| 7 | Encoder A/B: 10 k pull-up + 10 nF per line (decision 5c: pull-ups anywhere; caps within ~2 mm of Daisy pins 12/13/32/33 on the FRONT face, GND via each) | NOT DONE | **DONE — caps at the encoder end, accepted** (Kyle 2026-10-13: no room near the Seed; better than none) | 4 × 10 k (R31/R32/R34/R41 → /+3V3_D) ✓; 4 × 10 nF C19–C22 ✓ but placed **at the encoders on the back**: 6.8–10.2 mm from the encoder pins, **63–111 mm from the Daisy pins** (Pass 3 §3) | Debounce at the contact works; the MCU input stays on an unterminated 63–111 mm line. Keep the state-table decoder in firmware |
| 8 | R4 33 Ω → ½ W | DONE | **DONE** | C2907549 1210 | — |
| 9 | Delete D6; bridge to SMA/SOD-123FL | NOT DONE | **DONE** | D6 gone; D2–D5 = C169541 1N5817W **SOD-123FL**, 1 A / 25 A IFSM, on `D_SOD-123F` pads (BOM footprint cell still says "SOD-323" — stale text, correct part) | fix the BOM cell text |
| — | SW1 contact code | unverifiable | **unverifiable** (not on the JLC BOM) | — | check 1101A4VQEA silver 5 A contacts |

## Fab margins

| Item | Rev 3 | **Rev 4** | Fix |
|---|---|---|---|
| MK1 annular ring 0.175 → 1.1 mm pad | NOT DONE | **NOT DONE** (0.175, R4-P1-02) | MK1 pads 1/2 → 1.1–1.2 mm |
| P2 NPTH-to-GND-pad 0.197 → shrink pads | NOT DONE | **NOT DONE** (0.1966, R4-P1-03) | shrink A1/A12/B1/B12 by 0.05 |
| U6 thermal vias → 0.3 hole / 0.7 pad | NOT DONE | **NOT DONE** (0.25 / 0.6, R4-P1-04) | edit the footprint's EP vias |
| Silk outlines 0.12 → 0.15 mm | NOT DONE | **NOT DONE** (R4-P6-02) | footprint outline width 0.15 |
| DRC min track/clearance 0 → 0.1 | NOT DONE | **NOT DONE** (`.kicad_pro` byte-identical, R4-P1-12) | Board Setup → Constraints |

## "Worth tidying"

| Item | Rev 3 | **Rev 4** | Fix |
|---|---|---|---|
| 100 nF + 10 µF at the SD socket P1 (decision 5d: + 10 µF at pin 38) | NOT DONE | **DONE at the socket**: C28 10 µF 5.2 mm, C27 100 nF 6.9 mm from P1.4; the extra 10 µF at A1.38 not added (C28 is 27.9 mm from it) | optional 10 µF at A1.38 |
| TPA6110A2 10 µF bulk (+5 pF optional) | NOT DONE | **NOT DONE** (R4-P2-08) | 10 µF on /+3V3_A at U3 |
| AUDIO_IN_L beside USART1_RX; AUDIO_OUT_R beside TAC_SWITCH_2 | NOT DONE | **NOT DONE**: UART 0.41 mm / 49 mm and 0.45 / 26 mm; **TAC_SWITCH_2 0.20 mm / 27 mm** beside AUDIO_OUT_R (R4-P5-02/03) | move apart ≥ 1 mm or change layer |
| Delete FB1 | DONE | DONE | — |
| Firmware: SPI1 TX-only (MISO = TAC_SHIFT_R) | firmware | firmware (pin 10 unchanged) | libDaisy SPI1 TX-only |
| ERC: 14 NC flags + 4 PWR_FLAGs | NOT DONE | **NOT DONE** (ERC 51 identical, R4-P3-06) | add flags |
| Chassis standoffs near the jack row | NOT DONE | **NOT DONE** (0 mounting holes) | ≥ 2 holes near J3–J7 |
| Hand-assembly BOM sheet | NOT DONE | **NOT DONE** (one sheet; 18 THT + LEDs, R4-P4-03) | second sheet |

## Items found in the 9 Oct review (rev 3), re-scored
| Item | Rev 3 | **Rev 4** |
|---|---|---|
| No GND stitching vias (R3-P1-08) | open | **Re-scoped 2026-10-13 (Trey's note):** top-layer stitching is optional — all parts are on the bottom and the bottom plane is one piece. What stands: 10 bottom IC ground pins (U4 ×4, U6 ×3, U3 ×2, U2) on single 0.1–0.3 mm stubs; fix with 0.25 mm zone clearance or 0.3–0.5 mm GND stubs |
| Single-spoke GND thermals (R3-P1-06) | 8 | **9** (+ C28.1) |
| Inrush limiter (R3-P2-05, decision 5e) | open | **NOT DONE** — no R/NTC before C15; bulk cut 700 → 310 µF and unlimited cap 200 → 100 µF, but D6 + FB7 removal stiffens the path (≈ 30 A stiff-adapter bound into C15; bridge IFSM 25 A for 8.3 ms vs a ≈ 25 µs pulse — diodes fine, SW1/jack contacts still the concern) |
| /RES_SPI floating (R3-P3-04) | open | **NOT DONE** |
| Headphones1 taper / rotation (R3-P3-07) | ⏳ | ⏳ unchanged |
| Headphones1 bushing outside the outline (R3-P6-07) | open | unchanged (panel cut-out) |
| Position-file flags (R3-P4-04) | open | **NOT DONE** |
| Refdes repurposed (R3-P4-06) | C14/C15/C17 | **repeated**: C19–C22, R31/R32 changed function again |
| Dangling LED vias (R3-P1-07) | 2 | 2, unchanged |
| LEDs not on BOM (R3-P4-01) | open | **documentation only** — hand-soldered Würth 150505M173300 confirmed by Kyle |

**Rev-4 score on the 17 "fix before ordering" rows (1–9 as tabled): 14 DONE (incl. 7 as accepted), 1 DONE with a different part (2a), 1 ACKNOWLEDGED/DEFERRED (5), 1 DOCUMENTATION (3d). Nothing on this list blocks ordering rev 4.** Fab-margin rows: 0 of 5 done. Worth-tidying rows: SD caps done; the other six unchanged.
