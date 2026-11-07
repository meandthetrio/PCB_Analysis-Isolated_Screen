# Pass 3 — Connectivity Report
**Date:** 2026-11-07 · **Truth checked:** schematic (KiCad 9 ERC on the converted copy; author's KiCad 10 ERC), netlist three-way, board pad nets

## PB-F-017 — ERC, netlist and routing: PASS
- ERC: 0 errors / 0 warnings in the author's KiCad 10 run; 0 errors + 94 `lib_symbol_mismatch` warnings in KiCad 9 (embedded KiCad 10 symbols differ from KiCad 9's library copies; hygiene only).
- 57 nets, none with a single node, identical in the KiCad 9 export, the author's netlist and the board.
- 0 unconnected items in DRC; all 57 nets routed.
- 15 no-connect flags, all on unused positions of the off-board switch symbols: SW2 × 10 (positions 4–12 and pole b), SW1 × 4 (positions 5, 6, 11, 12), SW4 × 1 (unused throw). Nothing on an IC or a connector.
- 24 board pads carry no net: the coil footprint's C1–C12 (physical coil pins) and B1–B12 (breakout row) — see PB-F-018.

## PB-F-018 — the inductor is electrically absent until hand jumpers are fitted (JUDGMENT, Tier 1)
L1 uses the author's `RM10_corner_12P_breakout` footprint: each of the 12 coil pins (C1–C12) is
tied by a 0.4 mm copper line inside the footprint to one pad of a 12-pad breakout row (B1–B12,
2.54 mm pitch, y = 15.24), declared as 12 net-tie pairs. The circuit nets end on a *separate*
five-pad row (pad 0 = RST/common, pads 1–4 = TAP4…TAP1, y = 17.78, 2.54 mm below the breakout
row). No copper joins the two rows. The footprint's own silk says "coil pins → row 1-12; jumper
to 0-4", and the upload README says the pinout is unknown until the coil arrives. So: the fabbed
and stuffed board has an open coil until five wire links are soldered by hand, and which pads to
link is not yet defined. The fallback (wire the coil's leads to J13/J17 instead) works but then
the footprint is dead weight. Recommendation: get Don-Audio's pin drawing before fab and route
the five nets to the right C pads directly; failing that, print the jumper table on the silk once
known and add it to the parts-list build notes. KiCad 9's 12 `shorting_items` DRC errors on this
footprint are the tool objecting to copper joining no-net pads; KiCad 10 accepts the net-tie
declaration.

## PB-F-019 — off-board wiring tables reconstructed from the netlist (info, all consistent)
| Block | Pin 1 | Pin 2 | Pin 3 | Function |
|---|---|---|---|---|
| J3 | VPIN | GND | VNIN | PSU +15 / 0 / −15 |
| J1 / J2 | IN / OUTX | GND / GND | — | input / output jacks |
| J4 | GND | W1 (→ U2B +in) | IN1 (C1) | RV1 INPUT pot |
| J5 | GND | W2 (→ U3A +in) | SWO | RV2 OUTPUT pot |
| J6 | R34B (180 Ω to VP) | WIP (→ R16 → Q6 base) | R15T (3k3 to GND) | RV4 BIAS pot |
| J7 | FBA (R35 4k7 from U1A out) | U1AN | U1AN | RV5a DRIVE gang a (rheostat in U1A feedback) |
| J18 | R30X (R30 4k7 from U3A out) | U2AN | U2AN | RV5b DRIVE gang b (make-up gain) |
| J8 / J16 | X | TAP1 (188 mH) | TAP2 (94 mH) / TAP3 (47 mH), TAP4 (23.5 mH) | SW1a FREQUENCY, coil taps |
| J9 / J15 | X | CS1S (13.3 µF) | CS2S (6.8 µF) / CS3S (3.3 µF), CS4S (1.68 µF) | SW1b FREQUENCY, tuning caps |
| J10 / J14 | P | RAP1S (120 Ω) / RAP2S (56 Ω), RAP3S (30 Ω) | — | SW2 Q, drive resistor |
| J11 | SWO | OUTJ (block out, TP1) | D (drive, TP4) | SW3 BYPASS |
| J12 | Q6C | X | — | SW4 BIAS in/out |
| J13 / J17 | RST (common) | TAP4 (800 Hz) / TAP2 (200 Hz) | TAP3 (400 Hz) / TAP1 (100 Hz) | coil leads, wire alternative |

Tuning check (f = 1/2π√LC): 188 mH ‖ 13.3 µF → 100.7 Hz; 94 mH ‖ 6.8 µF → 199 Hz; 47 mH ‖ 3.3 µF → 404 Hz; 23.5 mH ‖ 1.68 µF → 801 Hz — the tap/cap pairing on SW1a/SW1b is consistent (TAP1 = pin 4 = 188 mH, TAP4 = pin 1 = 23.5 mH). SW1 must be non-shorting (taps must never be bridged) and SW2 shorting (drive never interrupted) — matches the parts list's Rev K note; not verifiable from the netlist.

Op-amp usage: U2B input buffer (pin 5 = W1, 6–7 tied), U1A inverting drive (pin 3 = GND, R21 2k4 in, RV5a + R35 feedback), U1B and U3B unity followers of U1A's output (pins 5 tied to U1AO), outputs through R22/R23/R24 (10 Ω) summing into D; U3A output buffer (pin 3 = W2), U2A inverting make-up (pin 3 = GND, R31 240 k feedback, RV5b + R30 input) → R32 100 Ω → C16 → OUTX. All six halves used; no floating inputs.

Discrete stage: Q1 (base P) / Q2 (base N = R1 from D + R10 from OUT, i.e. OUT = 2P − D) long-tailed pair, R4 27 k tail to VN, R3 10 k load → Q3 PNP (C5 150 p compensation) → D1/D2 bias → Q4/Q5 complementary emitter followers with R8/R9 10 Ω → OUT → R12 27 Ω ‖ C9 220 µ → O1 → R14 10 Ω + C10 15 n Zobel → OUTJ with R13 2 k load.
