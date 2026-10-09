# Status of the 7 October "Rev 2 Design Review" items in the 9 October files
**Date:** 2026-10-09 · **Baseline:** Kyle's Claude doc "WavetableController Rev 2 Design Review" (claude.ai artifact, dated 2026-10-07/08), which reviewed an intermediate design that already had the GND pour, the TPS62172 buck, J8, the bead chain and the 3.3 Ω filters. That doc is the real "what Trey was asked to change" list; the repo's `analysis/` folder is the older August review of the LedFix fab files. Every item below was re-measured on `rev3/` (files received 2026-10-09).

**Important discrepancy:** the 7 Oct doc says the ground is "stitched with 225 vias". The 9 Oct board has 244 vias and **0 of them are on GND** (every via is on a signal or power net). Either the earlier count took all vias as stitching, or the stitching was removed between the two file sets. As the files stand there are no ground stitching vias (R3-P1-08).

## "Fix before ordering" items

| # | Asked for (7 Oct) | Rev 3 (9 Oct) status | Evidence | Fix | Potential consequence if left |
|---|---|---|---|---|---|
| 1 | C25 10 µF 6.3 V → 16/25 V, 0805 | **DONE** | BOM C15850 = 10 µF 25 V X5R 0805; footprint C_0805 | none | — |
| 2a | Beads FB3–FB7 200 mA → 2 A (decision: 600 Ω 0805 MPZ2012S601; 0603 fallback 220 Ω MPZ1608S221) | **DONE on rating, different part** | FB2–FB7 = LCSC C14709, 120 Ω @100 MHz, 2 A, 0603; current ≤25 % of rating | Optional: swap to the decided 600 Ω 0805 (MPZ2012S601AT000) or the 220 Ω 0603 (MPZ1608S221ATA00) if the 120 Ω part proves too weak on the bench | Beads no longer saturate, so the real risk is gone. 120 Ω attenuates less above ~20 MHz; the 3.3 Ω/100 µF stages still carry the audio-band filtering, so at worst a slightly higher HF floor |
| 2b | R31/R32 3.3 Ω → ½ W body | **DONE (over-delivered)** | R29–R32 all 3.3 Ω 1 W 2512 (C2960677); ≤0.30 W | none | — |
| 2c | Feed U6 from the C19 node, before R31 | **NOT DONE** | FB7 still hangs on /+9V_FLAG after R31/R32; U6's 0.2–0.4 A still flows through them | Move FB7's input from /+9V_FLAG to Net-(C19-Pad1); R31/R32 then carry only LED current | /+9V_FLAG sags to ~5.8 V at 9 V in and moves with display content; the LED rail (and LED brightness) follows what the screen is showing. Not damaging now that the resistors are 1 W |
| 3a | LED drive: add a low-side switch per colour | **DONE, different part** | Q1–Q6 MMBT3904 NPN with 1 k base R35–R40 instead of 2N7002 + 100 k pull-downs; saturation fine (R3-P2-13) | none for the switch itself | — |
| 3b | **Turn each LED around** (9 V → R → anode → cathode → switch) | **DONE — already correct for the real part** | The 7 Oct ask assumed the Cree CLS6B-FKW named on the schematic (odd pads = anodes). Trey's actual LED is a Würth WL-SFTW 150505M173300 (datasheet supplied 9 Oct): pads 1/3/5 are cathodes, 2/4/6 anodes. The board has 2/4/6 → 300 Ω → supply and 1/3/5 → collectors: correct polarity, correct colours, no reverse-voltage exposure. The earlier "180° placement" workaround is withdrawn (it would reverse-bias this part). | Set the symbol Value to 150505M173300 and relabel its pins per the datasheet (pad 1 = blue cathode, not "AR") so the files stop saying Cree | None electrically. Documentation only: the wrong part name misleads the next reviewer, as it did this one |
| 3c | 300 Ω resistors → 1206 | **NOT DONE** | R21, R24–R28 still 0603 (R3-P2-04) | Keep the 0603 bodies and change values for the 7.7 V node (after the R31/R32 block is removed): red R24, R27 → 510 Ω (10.8 mA, 59 mW); green R25, R28 and blue R21, R26 → 390 Ω (11 mA, 47 mW). One-value option: 470 Ω in all six (red 11.7 mA / 64 mW, G/B 9.1 mA / 40 mW). Trim brightness with PWM | At 9 V with today's 5.8 V rail: 43 mW, within rating, LEDs dim (red 12 mA, G/B 8 mA with Würth Vf). If the R31/R32 block is removed (LEDs at ≈7.7 V): red 18 mA at **101 mW**, at the 0603 rating; 390 Ω gives 14 mA at 78 mW |
| 3d | (new) LED part vs files | **DOCUMENTATION** | Footprint matches the Würth land pattern (pads 2.0 × 1.1 at ±2.4 vs 1.6 × 1.0 at ±2.2, same inner edge, chamfer at the cathode-mark corner). Schematic Value says Cree; symbol pin labels are the Cree names; no LED BOM line (hand-soldered) | Value → 150505M173300; pin labels per datasheet; add LED1/LED2 to the hand-solder sheet | A future reviewer or builder reads "Cree" and reaches the wrong polarity conclusion again |
| 4 | BOM: C17 off the 100 nF line; delete S1/S2 and U5 | **DONE** | 100 nF line = C1,C4,C5,C8,C11,C14,C16; no S1/S2/U5 lines; 90/90 join clean | none | — |
| 5 | Move J8 to y 86.3, add four M2 holes at (135.0/209.2, 84.3/126.8), module outline in footprint | **NOT DONE** | J8 pin 1 still at (196.26, 81.30); 0 mounting holes; projected hole sites collide with R2/R5/U1 (R3-P6-05/06) | Move J8 down 5 mm, add the four 2.4 mm holes and standoffs, move U1/R2/R5 tracks clear, put the outline and holes in the J8 footprint | Display hangs on 20 solder joints; pressing the glass through the panel window loads them and cracks joints or the module PCB over time. Enclosure window has to be cut before the hole positions are final |
| 6a | U6: drawing (R33/R34 adjustable) vs BOM (fixed 3.3 V) — make them match | **DONE** | R34 gone; FB pin → GND; R33 100 k now a PG pull-up; BOM C59873 = TPS62172DSGR | none (R33 is harmless; delete if PG is unused) | — |
| 6b | L1 on the 2016 (DFE201610P) footprint | **NOT DONE** | still `L_0805_2012Metric` (R3-P4-02) | Replace the footprint with stock `Inductor_SMD:L_Murata_DFE201610P` | Pads 0.4 mm narrower than the terminations, ~50 % overlap, 0.5 mm overhang: a weak joint on the one part carrying the switching current; intermittent display rail or tombstoning at reflow |
| 6c | Move L1 next to U6 SW (was 8.3 mm) | **DONE** | SW node 4.7 mm at 0.2 mm | none | — |
| 6d | C26 22 µF → 0805 | **DONE** | C45783 22 µF 25 V 0805 | none | — |
| 7 | Encoder A/B: 10 k pull-up + 10 nF per line | **NOT DONE** | /ENCL_A, /ENCL_B, /ENCR_A, /ENCR_B are 2-node nets (encoder + Daisy only) | Add 4 × 10 k to 3V3_D and 4 × 10 nF to GND near the Daisy on pins 12, 13, 32, 33; use a state-table decoder in firmware | Skipped or doubled detents on fast or heavy-detent turns, worse with 80–146 mm of unterminated trace on internal pull-ups; looks like a firmware bug |
| 8 | R4 33 Ω → ½ W (1206/2512) | **DONE** | C2907549 33 Ω 500 mW 1210 | none | — |
| 9 | Delete D6; bridge to SMA/SOD-123FL | **NOT DONE** | D6 present (C727114 SOD-323); D2–D5 unchanged (R3-P2-06) | Remove D6 (link its pads); change D2–D5 to an SS14-class SMA/SOD-123FL part | At 0.49 A each conducting diode runs ~0.2 W in a 250 mW SOD-323; junction near 125 °C in a warm box, shortened life or a failed bridge. D6 costs 0.45 V and 0.2 W for no protection the bridge doesn't already give |
| — | SW1 contact code | unverifiable here | not on the JLC BOM | Check the ordered part is 1101A4VQEA with silver 5 A contacts, not the gold 0.4 VA logic-level variant | A logic-level contact at 0.5 A pits and goes intermittent; power drop-outs on the switch |

**Score: 10 done, 2 done with a different part, 6 not done, 1 documentation item.** The three "will damage parts" items: C25 fixed; beads/resistors fixed on rating; LED polarity correct for the actual part (the 7 Oct item was written against the wrong part name).

## Fab margins

| Item | 7 Oct ask | Rev 3 | Fix | Potential consequence if left |
|---|---|---|---|---|
| MK1 annular ring 0.175 → 1.1 mm pad | NOT DONE | 0.175 mm (R3-P1-02) | Set MK1 pads 1/2 to 1.1 mm diameter | Below JLC's 0.18 absolute minimum: a stricter lot rejects the order, or a thin ring breaks out and the mic pin lifts |
| P2 NPTH-to-GND-pad 0.197 → shrink pads 0.05 | NOT DONE | 0.197 mm (R3-P1-03) | Shrink P2 A1/A12/B1/B12 by 0.05 mm, or nudge them away from the NPTH | 3 µm under the 0.20 limit: fabbed OK twice, but a DFM rejection or a drill break-out into the GND pad is possible |
| U6 thermal vias → 0.3 hole / 0.7 pad | NOT DONE | 0.25 hole / 0.6 pad (R3-P1-04) | Edit the U6 footprint's two EP vias to 0.3/0.7 | Extra 0.25 mm drill tool; ring 0.175 under the 0.18 minimum; trips the project's own DRC so real errors hide among known ones |
| Silk outlines 0.12 → 0.15 mm | NOT DONE | 0.12 mm (R3-P6-02) | Set footprint outline width to 0.15 | Outlines print faint or are dropped; cosmetic |
| DRC min track/clearance 0 → 0.1 | NOT DONE | still 0.0 (R3-P1-14) | Board Setup → Constraints: min track 0.1, min clearance 0.1 | KiCad never warns about sub-minimum copper; the next 0.1 mm or thinner trace ships unnoticed |

## "Worth tidying"

| Item | Rev 3 | Fix | Potential consequence if left |
|---|---|---|---|
| 100 nF + 10 µF at the SD socket P1 | NOT DONE — still only C1, 120 mm away (R3-P2-10) | Add 100 nF + 10 µF across P1 VDD/VSS; 10 µF at A1.38 | Rail dips at the card on 100 mA write bursts: CRC errors, fallback to 1-bit, the likeliest cause of the Round 1 4-bit failure. MIDI opto shares the dip |
| TPA6110A2 10 µF bulk + 5 pF across R14/R15 | NOT DONE (R3-P2-11) | 10 µF (or more) on 3V3_A at U3; 5 pF across R14 and R15 | Distortion or a faint whine with long headphone leads; mic amp on the same under-filtered rail |
| AUDIO_IN_L beside USART1_RX; AUDIO_OUT_R beside TAC_SWITCH_2 | NOT DONE — UART still 49 mm at 0.41 mm from AUDIO_IN_L; now the closest pairing on the board (R3-P5-04) | Move the UART tracks ≥0.5 mm (ideally 3× width) from AUDIO_IN_L, or put them on the other layer | A tick on the audio input on MIDI traffic; a click on a button press |
| Delete FB1 | DONE — FB1 removed | none | — |
| Firmware: SPI1 transmit-only (MISO = TAC_SHIFT_R) | firmware, unchanged (pin 10 still TAC_SHIFT_R) | Open SPI1 as TX-only in libDaisy | Right shift button dies the moment the display driver initialises; looks like a hardware fault |
| ERC: 14 NC flags + 4 PWR_FLAGs | NOT DONE (R3-P3-06) | Add NC flags on P2 SS/SBU pins and J8 3/9/15/18; PWR_FLAG on /DSY_VIN, Net-(U6-EN), Net-(U4-VDD), GND | A real wiring error hides among 20 known false errors on the next revision |
| Chassis standoffs near the jack row | NOT DONE — 0 mounting holes (R3-P6-05) | Add ≥2 standoff holes within ~15 mm of J3–J7; close-fit panel holes | Every plug insertion flexes the board about the encoder nuts; cracked jack joints over time |
| Hand-assembly BOM sheet | NOT DONE (R3-P4-03) | Second BOM sheet listing the 18 THT parts incl. C23, C24, J8, Headphones1 | A board passes assembly and fails on the bench because a through-hole cap at the display was never fitted |

## Items the 7 Oct review did not have, found in the 9 Oct files
No GND stitching vias (R3-P1-08); 8 single-spoke GND thermals (R3-P1-06); no inrush limit for the 700 µF (R3-P2-05, judgment); /RES_SPI floating (R3-P3-04); Headphones1 linear taper + bushing 9 mm outside the outline (R3-P3-07, R3-P6-07); "exclude from position" flags inconsistent (R3-P4-04); C14/C15/C17 refdes repurposed since the August files (R3-P4-06).
