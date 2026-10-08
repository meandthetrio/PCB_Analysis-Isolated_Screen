# Power-rating sweep — every part on the Rev 2 (2026-10) board
**Date:** 2026-10-08 · **Why:** Round 2 claimed a ratings check but missed FB7 (F-076). This pass lists every designator in the netlist with its worst-case stress against the BOM rating, so nothing is implied. · **Truth:** Rev 2 netlist (`WavetableController.kicad_sch`, kicad-cli 9.0.9), BOM `ManifoldRe_BOM_NEW - Excel Format.xls` (ratings in the description text), PASS2_POWER_2026-10 §2 current budget (0.30 A typ / 0.49 A worst in the 9 V trunk; display buck input 0.19–0.26 A; Daisy branch 0.10–0.14 A), archived datasheets in `datasheets_2026-10/`.
**Input assumption:** 9 V regulated pedal supply (9.0–9.6 V). J1 is rated 12 V, so a 12 V adapter is the hard limit; the Daisy VIN limit is 17 V.
**Sources not reachable from this sandbox (figures taken from distributor/search text, flagged):** 1N5817WS SOD-323 datasheet (Pd 250 mW, RθJA 400 °C/W, Tj 125 °C, IF(AV) 1 A); MIDI CA-033 (3.3 V transmitter: 33 Ω **0.5 W**, 10 Ω 0.25 W).

## Verdict summary
| Status | Parts |
|---|---|
| **Over rating (new)** | R4 (F-077, fault case the MIDI spec requires you to survive) |
| **Marginal (new)** | D2–D5 bridge and D6 (F-078: 78 % of Pd at worst case in SOD-323, junction near 125 °C in a warm box; D6 is also redundant with the bridge) |
| Over rating (already logged) | FB3–FB6 (F-050), FB7 (F-076), R31/R32 (F-051), C25 (F-049), LED1/LED2 reverse voltage (F-052) |
| In rating, low margin (>50 %) | R29/R30 65 %, U6 75 %, U1 output 75 % |
| Unverifiable | Daisy +3V3_D / +3V3_A rail limits (no published figure, carried from Round 1); SW1 contact rating (part not on the JLCPCB BOM; sibling C&K 1101A3VQEA is 5 A silver, confirm 1101A4VQEA) |
| Everything else | in rating with ≥ 2× margin — table below |

## Resistors (all 0603, 100 mW, 75 V unless noted)
| Ref | Value | Where | Worst-case stress | % of 100 mW | Verdict |
|---|---|---|---|---|---|
| R1 | 10 Ω | UART TX → MIDI OUT tip | 8 mA loop → 0.7 mW. Fault (TS plug shorts tip? no — tip is sink; cable short): current limited by the STM32 pin, ≤ ~60 mW | <1 % / ≤60 % | OK; MIDI spec asks 0.25 W, STM32 pin is the weak link in a short (abs max 20 mA/pin) |
| **R4** | **33 Ω** | +3V3_D → MIDI OUT ring (source) | 8 mA → 2 mW normal. **TS plug or shorted cable: 3.3 V/33 Ω = 100 mA → 330 mW**, and 100 mA pulled from the Daisy 3.3 V rail for as long as the plug is in | **330 %** | **F-077** — MIDI CA-033 specifies 0.5 W for exactly this reason |
| R5 | 220 Ω | MIDI IN series | 5 mA → 5.5 mW | 6 % | OK |
| R6 | 270 Ω | H11L1 output pull-up | opto on: 12.2 mA → 40 mW | 40 % | OK |
| R2, R3 | 0 Ω | MIDI IN | 5 mA | — | OK |
| R7–R11, R33 | 47 k | SD pull-ups, buck FB | < 0.3 mW | <1 % | OK |
| R12–R15 | 22 k / 33 k | headphone amp gain | audio, < 0.5 mW | <1 % | OK |
| R16, R17 | 5.1 k | USB-C CC | 5 V → 5 mW | 5 % | OK |
| R18, R19, R20 | 100 k / 150 k / 2.2 k | MAX9814 bias | < 1 mW | <1 % | OK |
| R21, R24–R28 | 300 Ω | LED cathodes to +9V_FLAG | 0 as drawn (LEDs reverse-biased, F-052). With the doc's low-side LED fix they are replaced by 1206 parts | — | covered by item 3 |
| R22, R23 | 10 k | headphone output loads | 1.4 Vp → 0.1 mW | <1 % | OK |
| R29, R30 | 3.3 Ω | Daisy branch RC ladder | 0.14 A → 65 mW (0.10 A typ → 33 mW) | 65 % | OK, low margin; 1206 if the layout allows |
| R31, R32 | 3.3 Ω | display branch RC ladder | 0.19–0.23 A → 120–175 mW | 120–175 % | F-051 (already) |
| R34 | 15 k | buck FB | < 0.1 mW | <1 % | OK |

## Capacitors
| Ref | Value / rating | Node voltage | % of rating | Verdict |
|---|---|---|---|---|
| C14, C16 | 100 nF 25 V X7R | 9.2 V (bridge out / D6 anode) | 37 % | OK (12 V adapter: 48 %) |
| C1, C4, C5, C8, C11 | 100 nF 25 V | ≤ 3.3 V | 13 % | OK |
| C2, C3, C10 | 470 nF 25 V | ≤ 3.3 V | 13 % | OK |
| C9, C13 | 2.2 µF 10 V X5R | ≤ 3.3 V | 33 % | OK |
| C12 | 4.7 µF 10 V | ≤ 3.3 V | 33 % | OK |
| C15, C17–C22 | 100 µF 35 V electrolytic | ≤ 9.2 V | 26 % | OK |
| C6, C7 | 100 µF 35 V | ≤ 3.3 V (headphone coupling) | 9 % | OK |
| C25 | 10 µF **6.3 V** | 5.2–9 V (buck input) | 83–143 % | F-049 (already) |
| C26 | 22 µF 6.3 V X5R | 3.3 V | 52 % | OK on voltage; DC-bias derating leaves ~10 µF effective, inside the TPS62172 stable range (4.7–400 µF table) and C24 100 µF is in parallel |
| C23, C24 | 100 nF axial, 100 µF radial (hand-placed, not on the JLCPCB BOM) | 3.3 V | rating unknown, any stock part is ≥ 6.3 V | OK |

## Diodes
| Ref | Part | Stress | Verdict |
|---|---|---|---|
| D2–D5 | 1N5817WS SOD-323, IF(AV) 1 A, Pd 250 mW, RθJA 400 °C/W | Two conduct at a time, each at the full trunk current: 0.30 A → ~0.10 W (ΔT ≈ 42 °C); **0.49 A → ~0.20 W = 78 % of Pd, ΔT ≈ 78 °C**, Tj ≈ 103 °C at 25 °C ambient, ≈ 123 °C at 45 °C in a closed enclosure (limit 125 °C). Reverse 9 V vs 20 V OK | **F-078** marginal |
| D6 | same part | full trunk current, same numbers | **F-078**; also redundant — the bridge already fixes polarity, D6 only adds 0.45 V of drop and 0.2 W of heat |
| D1 | Schottky 1 A SOD-323 | MIDI IN reverse clamp, 5 mA | OK |

## Beads and inductor
| Ref | Rating | Stress | Verdict |
|---|---|---|---|
| FB3–FB6 | 200 mA, 450 mΩ | 0.30–0.49 A | F-050 |
| FB7 | 200 mA | 0.19–0.26 A | F-076 |
| FB2 | 200 mA | 3.1 mA typ / 6 mA max (MAX9814) | OK, 30× |
| FB1 | — | both ends GND | no-op (F-060) |
| L1 | DFE201610P-2R2M, 1.4 A rms / 2 A sat, 168 mΩ | 0.375 A avg, ≈ 0.53 A peak (ΔI ≈ 0.3 A at 6 V in), 24 mW | OK, 27 % |

## ICs and modules
| Ref | Limit | Stress | Verdict |
|---|---|---|---|
| U6 TPS62172 | 500 mA, VIN 3–17 V | 345–375 mA (69–75 %), VIN 5.2–9 V, ≈ 0.14 W loss in WSON-8 with thermal vias | OK, low margin |
| U3 TPA6110A2 | VDD 2.5–5.5 V, 150 mW/ch into 16 Ω | 3.3 V; full swing into 16 Ω ≈ 60 mA from +3V3_A | OK |
| U4 MAX9814 | 2.7–5.5 V, 6 mA max | 3.3 V, via FB2 | OK |
| U1 H11L1 | VCC 3–15 V, IOL 16 mA | 3.3 V, LED 5 mA, output sinks 12 mA through R6 | OK, 75 % |
| U2 USBLC6-2P6 | 5.25 V VBUS | 5 V | OK |
| A1 Daisy Seed | VIN 4–17 V (5 V min in v1.1.5); 3.3 V rails: **no published limit** | VIN 5.8 V worst (6.25 V with D6 gone). +3V3_D ≈ 130 mA normal (SD burst 100 mA + opto 15 mA + pull-ups), 230 mA with the R4 fault. +3V3_A ≈ 65 mA max (headphones full + mic amp) | VIN OK; rails unverifiable (Round 1 F-0xx carry-over) |
| U5 L7805 | on BOM, not in the design | — | PASS0 (already) |

## Connectors and electromechanical
| Ref | Rating | Stress | Verdict |
|---|---|---|---|
| J1 barrel | 12 V, 3 A | 9 V, 0.49 A | OK; 12 V adapter is the ceiling |
| SW1 slide | C&K 1101A4VQEA — not on the JLCPCB BOM, datasheet not reachable; sibling 1101A3VQEA is silver, 5 A | 9 V, 0.49 A | probably OK — **confirm** the contact code (a gold "logic level" 1101 variant is 0.4 VA and would be 10× over) |
| J8 display | 1×20 header, 2.54 mm pitch (≥ 1 A/pin) | 375 mA on pin 2 | OK |
| P2 USB-C | 3 A | data only | OK |
| TAC_×4, ENCL1/ENCR1, S1/S2 | 50 mA logic | 3.3 V logic | OK |
| Headphones1 pot, MK1, J3–J7 | signal | signal | OK |
| LED1, LED2 | V_R 5 V | 6–8.5 V reverse as drawn | F-052 (already) |

## New findings from this sweep
- **F-077 — VIOLATION:** R4 (33 Ω, 0603, 100 mW) is the MIDI OUT source resistor. The 3.3 V MIDI circuit in CA-033 calls for a **0.5 W** 33 Ω part because a TS (mono) plug in the TRS jack, or a shorted cable, puts the full 3.3 V across it: 100 mA, 330 mW, for as long as the plug is in. Fix: 33 Ω 1206 or 2512 rated ≥ 0.5 W (two 1206 0.25 W in series at 16 Ω each also works). The same fault pulls 100 mA from the Daisy's 3.3 V rail.
- **F-078 — JUDGMENT (strong):** the bridge D2–D5 and D6 are 1 A Schottkys in SOD-323 whose 1 A rating needs ~75 °C/W of copper the layout does not give; at 400 °C/W the worst case runs each conducting diode at ~0.2 W, 78 % of Pd and within ~2 °C of Tj max inside a warm enclosure. D6 is redundant: the bridge already guarantees polarity, so D6 only costs 0.45 V and 0.2 W. Fix: delete D6 (Daisy VIN worst case rises from 5.8 V to 6.25 V), and move the bridge to an SMA/SOD-123FL part (SS14 class, RθJA ≈ 75–100 °C/W) or a single series diode if the center-negative-only convention is acceptable (Electrosmith's choice).
