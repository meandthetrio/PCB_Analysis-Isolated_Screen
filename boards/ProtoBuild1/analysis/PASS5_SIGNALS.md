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

## Function check (added 2026-11-08) — PB-F-032, PB-F-033
Derived from the netlist, not from the labels. The LTP feedback forces N = P with N the midpoint of
R1 (10 k from D) and R10 (10 k from OUT), so OUT = 2P − D. With Z = j(ωL − 1/ωC) + r the coil leg
(r = Rs 1 Ω + coil DCR, ≈11 Ω assumed) and P = D·Z/(Rap + Z):

  OUT/D = (Z − Rap)/(Z + Rap)  — a second-order all-pass. |H| = 0 dB away from f0, phase 0 → −360°
  through f0, and a dip of (Rap − r)/(Rap + r) at f0 that exists only because of r.

| Setting | f0 | ω0·L | Rap 120 Ω ("Q 1") | Rap 56 Ω ("Q 2") | Rap 30 Ω ("Q 4") |
|---|---|---|---|---|---|
| 188 mH / 13.3 µF | 100.7 Hz | 119 Ω | Q 0.91, dip −1.6 dB | Q 1.77, dip −3.5 dB | Q 2.90, dip −6.7 dB |
| 94 mH / 6.8 µF | 199.1 Hz | 118 Ω | same | same | same |
| 47 mH / 3.3 µF | 404.1 Hz | 119 Ω | same | same | same |
| 23.5 mH / 1.68 µF | 801.0 Hz | 118 Ω | same | same | same |

ω0·L is 118 Ω on every setting by construction (L halves as f doubles), so each Rap gives the same
series Q at all four frequencies, and the parts list's "Exact 118 Ω" note for Rap1 is Q = 1 exactly.
DRIVE: U1A gain (4k7 + RV5a)/2k4 = ×1.96…×22.8, make-up U2A 240 k/(4k7 + RV5b) = ×51…×4.4; the
product is 240 k/2k4 = ×100 (40 dB) at every pot position, so DRIVE changes coil current, not
output level. Purpose: push AC current (and the optional 0–80 mA DC bias from Q6) through the iron
core in a selectable band so the core's nonlinearity colours the signal while the response stays
flat — a saturation/"iron" stage, not an EQ. The "Quad Eight amplifier" Q1–Q5 is a discrete op-amp
used as the 2P − D summing stage; no published Quad Eight circuit for this block was found, so the
lineage is the author's claim, the function is verified.

**PB-F-033 (JUDGMENT):** the available drive depends on the Q switch. At resonance D sees Rap + r:
131 / 67 / 41 Ω. Three NE5532 halves (IOS 38 mA each) through 10 Ω share resistors can source
roughly 100 mA peak, so the drive stage current-limits at ≈ 13 / 6.7 / 4.1 V peak on the three Q
settings before the ±14 V rails clip — about 10 dB less headroom at "Q 4" than at "Q 1". May be
intended (soft limiting), but it means the Q switch also changes the maximum drive level and the
coil current (≈ 7.6 / 15 / 24 mA per volt at D).

## PB-F-026 — I/O and output network: notes, no defects
- Input: unbalanced jack → C1 10 µF film → RV1 (10 k log) → U2B buffer. No RF/ESD network — acceptable for a studio-rack prototype.
- Output: U2A → R32 100 Ω build-out → C16 10 µF film → OUTX, R33 100 k bleed to GND ✓.
- Discrete stage: C5 150 pF across Q3 b–c (parts list carries a 220 pF fallback) ✓; emitter resistors R8/R9 10 Ω ✓; R12 27 Ω ‖ C9 220 µF plus R14 10 Ω / C10 15 n Zobel ✓; R13 2 k block load ✓.
- Bias injection: Q6 DC enters X and returns through the coil and Rs 1 Ω, so TP3 reads the sum of bias and signal current (1 mV/mA) — intended per the parts list.
- Test points TP1 (OUTJ), TP2 (X), TP3 (RST), TP4 (D), TP5/TP6 (GND) placed near their nets ✓.
