# Status of the 7 October "Rev 2 Design Review" items in the 9 October files
**Date:** 2026-10-09 · **Baseline:** Kyle's Claude doc "WavetableController Rev 2 Design Review" (claude.ai artifact, dated 2026-10-07/08), which reviewed an intermediate design that already had the GND pour, the TPS62172 buck, J8, the bead chain and the 3.3 Ω filters. That doc is the real "what Trey was asked to change" list; the repo's `analysis/` folder is the older August review of the LedFix fab files. Every item below was re-measured on `rev3/` (files received 2026-10-09).

**Important discrepancy:** the 7 Oct doc says the ground is "stitched with 225 vias". The 9 Oct board has 244 vias and **0 of them are on GND** (every via is on a signal or power net). Either the earlier count took all vias as stitching, or the stitching was removed between the two file sets. As the files stand there are no ground stitching vias (R3-P1-08).

## "Fix before ordering" items

| # | Asked for (7 Oct) | Rev 3 (9 Oct) status | Evidence |
|---|---|---|---|
| 1 | C25 10 µF 6.3 V → 16/25 V, 0805 | **DONE** | BOM C15850 = 10 µF 25 V X5R 0805; footprint C_0805 |
| 2a | Beads FB3–FB7 200 mA → 2 A (decision: 600 Ω 0805 MPZ2012S601; 0603 fallback 220 Ω MPZ1608S221) | **DONE on rating, different part** | FB2–FB7 = LCSC C14709, 120 Ω @100 MHz, 2 A, 0603. Current ≤25 % of rating. Impedance class is 120 Ω, not the 600 Ω decided; filters less above ~20 MHz |
| 2b | R31/R32 3.3 Ω → ½ W body | **DONE (over-delivered)** | R29–R32 all 3.3 Ω 1 W 2512 (C2960677); ≤0.30 W |
| 2c | Feed U6 from the C19 node, before R31 | **NOT DONE** | FB7 still hangs on /+9V_FLAG after R31/R32; U6's 0.2–0.4 A still flows through them |
| 3a | LED drive: add a low-side switch per colour | **DONE, different part** | Q1–Q6 MMBT3904 NPN with 1 k base R35–R40 instead of 2N7002 + 100 k pull-downs; saturation fine (R3-P2-13) |
| 3b | **Turn each LED around** (9 V → R → anode → cathode → switch) | **NOT DONE** | anodes (Cree pads 1/3/5) on the collectors, cathodes via 300 Ω to +9V_FLAG — still reverse-biased, still 5.5–8.7 V reverse vs 5 V (R3-P2-01) |
| 3c | 300 Ω resistors → 1206 | **NOT DONE** | R21, R24–R28 still 0603 (R3-P2-04) |
| 3d | (new) LED footprint | **NEW PROBLEM** | custom 2-column 5050 footprint does not fit CLS6B-FKW 4.7 × 1.5 mm (R3-P2-02); LEDs still not on BOM (R3-P4-01) |
| 4 | BOM: C17 off the 100 nF line; delete S1/S2 and U5 | **DONE** | 100 nF line = C1,C4,C5,C8,C11,C14,C16; no S1/S2/U5 lines; 90/90 join clean |
| 5 | Move J8 to y 86.3, add four M2 holes at (135.0/209.2, 84.3/126.8), module outline in footprint | **NOT DONE** | J8 pin 1 still at (196.26, 81.30); 0 mounting holes; projected hole sites collide with R2/R5/U1 (R3-P6-05/06) |
| 6a | U6: drawing (R33/R34 adjustable) vs BOM (fixed 3.3 V) — make them match | **DONE** | R34 gone; FB pin → GND; R33 100 k now a PG pull-up; BOM C59873 = TPS62172DSGR |
| 6b | L1 on the 2016 (DFE201610P) footprint | **NOT DONE** | still `L_0805_2012Metric` (R3-P4-02) |
| 6c | Move L1 next to U6 SW (was 8.3 mm) | **DONE** | SW node 4.7 mm at 0.2 mm |
| 6d | C26 22 µF → 0805 | **DONE** | C45783 22 µF 25 V 0805 |
| 7 | Encoder A/B: 10 k pull-up + 10 nF per line | **NOT DONE** | /ENCL_A, /ENCL_B, /ENCR_A, /ENCR_B are 2-node nets (encoder + Daisy only) |
| 8 | R4 33 Ω → ½ W (1206/2512) | **DONE** | C2907549 33 Ω 500 mW 1210 |
| 9 | Delete D6; bridge to SMA/SOD-123FL | **NOT DONE** | D6 present (C727114 SOD-323); D2–D5 unchanged (R3-P2-06) |
| — | SW1 contact code | unverifiable here | not on the JLC BOM |

**Score: 9 done, 2 done with a different part, 7 not done, 1 new problem.** The three "will damage parts" items: C25 fixed; beads/resistors fixed on rating; **LED polarity still wrong.**

## Fab margins

| Item | 7 Oct ask | Rev 3 |
|---|---|---|
| MK1 annular ring 0.175 → 1.1 mm pad | NOT DONE | 0.175 mm (R3-P1-02) |
| P2 NPTH-to-GND-pad 0.197 → shrink pads 0.05 | NOT DONE | 0.197 mm (R3-P1-03) |
| U6 thermal vias → 0.3 hole / 0.7 pad | NOT DONE | 0.25 hole / 0.6 pad (R3-P1-04) |
| Silk outlines 0.12 → 0.15 mm | NOT DONE | 0.12 mm (R3-P6-02) |
| DRC min track/clearance 0 → 0.1 | NOT DONE | still 0.0 (R3-P1-14) |

## "Worth tidying"

| Item | Rev 3 |
|---|---|
| 100 nF + 10 µF at the SD socket P1 | NOT DONE — still only C1, 120 mm away (R3-P2-10) |
| TPA6110A2 10 µF bulk + 5 pF across R14/R15 | NOT DONE (R3-P2-11) |
| AUDIO_IN_L beside USART1_RX; AUDIO_OUT_R beside TAC_SWITCH_2 | NOT DONE — UART still 49 mm at 0.41 mm from AUDIO_IN_L; it is now the closest pairing on the board (R3-P5-04) |
| Delete FB1 | DONE — FB1 removed |
| Firmware: SPI1 transmit-only (MISO = TAC_SHIFT_R) | firmware, unchanged (pin 10 still TAC_SHIFT_R) |
| ERC: 14 NC flags + 4 PWR_FLAGs | NOT DONE (R3-P3-06) |
| Chassis standoffs near the jack row | NOT DONE — 0 mounting holes (R3-P6-05) |
| Hand-assembly BOM sheet | NOT DONE (R3-P4-03) |

## Items the 7 Oct review did not have, found in the 9 Oct files
No GND stitching vias (R3-P1-08); 8 single-spoke GND thermals (R3-P1-06); no inrush limit for the 700 µF (R3-P2-05, judgment); /RES_SPI floating (R3-P3-04); Headphones1 linear taper + bushing 9 mm outside the outline (R3-P3-07, R3-P6-07); "exclude from position" flags inconsistent (R3-P4-04); C14/C15/C17 refdes repurposed since the August files (R3-P4-06).
