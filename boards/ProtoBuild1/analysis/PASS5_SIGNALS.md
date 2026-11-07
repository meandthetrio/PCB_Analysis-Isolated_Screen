# Pass 5 — Signal-Specific Report
**Date:** 2026-11-07 · **Truth checked:** converted board geometry + netlist · **Thresholds:** NE5532 (TI), transistor datasheets (THRESHOLDS.md)

Audio below 1 kHz on a 2-layer board with a full bottom ground pour: trace length, impedance and
skew are electrically irrelevant; what matters is hum/crosstalk loop area, decoupling (Pass 2)
and the high-current coil path.

## PB-F-024 — autorouted analog nets are long (JUDGMENT)
Net copper lengths (`scripts/pb1_power_extract.py`), all 0.4 mm:
| Net | Role | Length | Vias |
|---|---|---|---|
| N | Q2 base — the OUT = 2P − D summing node (10 k ‖ 10 k source) | 164 mm | 2 |
| P | Q1 base / coil-side node | 190 mm | 3 |
| X | coil top (SW1 commons, SW4, TP2) | 159 mm | 3 |
| TAP1–TAP4 | coil taps to SW1a and J13/J17 | 180–216 mm | 0–4 |
| D | drive bus (3 × 10 Ω, Rap1–3, SW3, TP4) | 253 mm | 6 |
| OUTJ / OUTX | block output / output jack | 207 / 147 mm | 3 / 0 |
| IN / IN1 | input jack → C1 → RV1 | 57 / 75 mm | 0 |
| Q6C | bias current to SW4 | 106 mm | 1 |
The sensitive node N runs 164 mm through the middle of the board at 5 kΩ source impedance; P and
X each cross the board to reach the terminal blocks on the top edge. Nothing here will stop the
prototype working, and the pour keeps loop areas small; for a hand-routed Rev L keep Q1/Q2/R1/R10
and N inside ~20 mm of each other, and keep the D → Rap → P → cap → X → tap → coil → Rs loop
compact. The loop necessarily leaves the board three times (SW2, SW1b, SW1a) — the parts list
already says to twist those leads.

## PB-F-025 — op-amp operating points: PASS
±14.3 V supply inside the NE5532 recommended ±5…±15 V; three halves paralleled into D through 10 Ω each — offset mismatches of a few mV circulate < 1 mA, well under IOS 38 mA; U1A closed-loop gain (R35 4k7 + RV5a) / R21 2k4 = ×2 … ×23; U2A make-up ×(240 k / (4k7 + RV5b)) — with the dual pot both gangs move together, which is the stated "DRIVE holds level" intent. Slew (5 V/µs) and bandwidth are irrelevant at 800 Hz.

## PB-F-026 — I/O and output network: notes, no defects
- Input: unbalanced jack → C1 10 µF film → RV1 (10 k log) → U2B buffer. No RF/ESD network — acceptable for a studio-rack prototype.
- Output: U2A → R32 100 Ω build-out → C16 10 µF film → OUTX, R33 100 k bleed to GND ✓.
- Discrete stage: C5 150 pF across Q3 b–c (parts list carries a 220 pF fallback) ✓; emitter resistors R8/R9 10 Ω ✓; R12 27 Ω ‖ C9 220 µF plus R14 10 Ω / C10 15 n Zobel ✓; R13 2 k block load ✓.
- Bias injection: Q6 DC enters X and returns through the coil and Rs 1 Ω, so TP3 reads the sum of bias and signal current (1 mV/mA) — intended per the parts list.
- Test points TP1 (OUTJ), TP2 (X), TP3 (RST), TP4 (D), TP5/TP6 (GND) placed near their nets ✓.
