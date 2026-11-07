# Pass 2 — Power Distribution Report
**Date:** 2026-11-07 · **Truth checked:** schematic netlist for topology, converted board for copper/distances · **Thresholds:** Traco TEN 5 datasheet, TI NE5532, onsemi BD139/BD140, IPC-2221 computed (THRESHOLDS.md)

## Rail topology (from the netlist)
```
J3.1 +15 in ─ VPIN ─ D3 (1N4002, A→K) ─ VP ─┬─ C11 100µ/50V, C12 100n   (power entry, left edge)
                                            ├─ U1.8, U2.8, U3.8 (NE5532 VCC+) with C17/C19/C21 100n
                                            ├─ Q2.C, Q4.C (BD139 collector), R3, R5 (Q stage loads)
                                            └─ R34 → RV4 → R15 divider; R17 39Ω → Q6 emitter; C15 100µ base filter
J3.2 0 V  ─ GND (26 pads, B.Cu pour + 500 mm of 0.4 mm track, 16 vias)
J3.3 −15 in ─ VNIN ─ D4 (1N4002, K at VNIN) ─ VN ─┬─ C13 100µ/50V (+ to GND), C14 100n, R18 1k5 bleed
                                                  ├─ U1.4, U2.4, U3.4 (VCC−) with C18/C20/C22 100n
                                                  └─ Q5.C (BD140 collector), R4 27k LTP tail, R7
```
Supply is an off-board Traco TEN 5-1223 (±15 V, ±200 mA) fed from a 12 V adapter, per the parts list.

## Verified against datasheets (cited)
| Check | Board | Source | Verdict |
|---|---|---|---|
| Op-amp supply | ±15 V minus one 1N4002 drop ≈ ±14.3 V | NE5532 recommended ±5 … ±15 V, abs max ±18 V | OK |
| DC-DC cap load | 100 µF + 6 × 100 n per rail | TEN 5 dual: 1000 µF max per output | OK |
| DC-DC load range | VP quiescent ≈ 3 × 6–16 mA (NE5532) + ~1 mA Q stage + 3 mA divider + 0–80 mA Q6 bias; VN ≈ same op-amp share + 9.5 mA bleed | regulation specified for 20–100 % load (40–200 mA); datasheet gives a no-load input current and **no minimum-load clause** | OK — at zero bias the rails sit near/below the 20 % regulation band; ripple/regulation simply fall outside the spec'd window, nothing fails |
| Transistor pin order | KiCad `Q_NPN_ECB`/`Q_PNP_ECB` (1 = E, 2 = C, 3 = B) on `TO-92_Inline` and `TO-126-3_Vertical` pads 1-2-3 | KSC1845 / KSA992 "1. Emitter 2. Collector 3. Base"; BD139/BD140 "1 Emitter 2 Collector 3 Base" | OK (PB-F-011) |
| Q6 dissipation | up to 0.82 W at ±14.3 V (0.91 W at ±15) — see below | BD140 PC 12.5 W (case), 1.25 W free air; RθJC 10 °C/W (BD139 sheet; same package); heatsink 26 °C/W | OK thermally (ΔTj ≈ 0.85 × 36 ≈ 31 °C) but **above the parts list's "0.6 W at 50 mA"** (PB-F-015) |

## PB-F-011 — polarity / orientation audit: all PASS
Netlist pin 1 of every KiCad `C_Polarized` is the positive terminal: C6.1 = OUT (parts list "+ toward OUT") ✓; C9.1 = O1, the amplifier side ✓; C11.1 = VP ✓; C13.1 = GND, C13.2 = VN (positive to ground on the negative rail) ✓; C15.1 = VP ✓. Diodes (`Device:D` pin 1 = cathode): D3 anode VPIN → cathode VP ✓; D4 cathode VNIN, anode VN (conducts from VN toward the more-negative input) ✓; bias string D1/D2 anode-to-cathode from node A (Q4 base) to node C (Q5 base) ✓.

## PB-F-012 — series reverse-protection diodes (JUDGMENT, informational)
D3/D4 in series cost ≈ 0.7–0.9 V per rail (1N4002 at tens of mA). ±14.3 V is inside every part's range and the op-amps lose ~0.7 V of headroom — acceptable; a Schottky (SB1xx) would halve the drop if headroom ever matters. R18 (1k5, ½ W) bleeds 9.5 mA / 0.14 W on VN only; the datasheet revision in hand states no minimum load, so it is belt-and-braces rather than required. Not a defect.

## PB-F-013 — output stage and input pair have no local decoupling (JUDGMENT)
Nearest same-rail capacitor to each rail pin (straight-line, `scripts/pb1_power_extract.py`):
| Pin | Rail | Nearest cap | Distance |
|---|---|---|---|
| Q2.2 (LTP) | VP | C21.1 | 24.9 mm |
| Q4.2 (BD139 C) | VP | C21.1 | 29.9 mm |
| Q5.2 (BD140 C) | VN | C18.1 | 50.0 mm |
| U1.8 / U1.4 | VP / VN | C21 / C18 | 14.1 / 6.3 mm |
| U2.8 / U2.4 | VP / VN | C17 / C20 | 14.7 / 9.3 mm |
| U3.8 / U3.4 | VP / VN | C19 / C22 | 4.9 / 5.1 mm |
The bulk caps C11/C13 are at the power entry, ~110 mm from Q4/Q5. The discrete stage drives a 2 kΩ load (R13) and the output network, so rail currents are < 10 mA and the risk is low; add a 100 n pair at Q4/Q5 on the next revision. The op-amp caps are present and on the right rails (C17/C19/C21 = VP, C18/C20/C22 = VN) but the autorouter did not pair each cap with "its" op-amp (U1's nearest VP cap is C21, nominally U3's) — harmless.

## PB-F-014 — copper capacity and resistance: PASS
All tracks 0.40 mm / 1 oz → 1.23 A at ΔT 10 °C (IPC-2221), 0.123 Ω per 100 mm. Rail copper: VP 336 mm (8 vias), VN 270 mm (9 vias) → ≤ 0.42 Ω end to end, i.e. < 15 mV at 35 mA. Worst currents on the board: Q6 bias ≤ 80 mA (0.4 mm trace → 3× margin at ΔT 10 °C), coil drive from three paralleled NE5532 halves ≤ ~100 mA peak (IOS 38 mA each). GND: 26 pads on a pour plus 500 mm of track and 16 vias.

## PB-F-015 — Q6 bias current source: 0 … ~80 mA, ~0.85 W (JUDGMENT)
Divider R34 180 Ω – RV4 1 k – R15 3k3 across VP→GND puts the wiper between 0.737·VP and 0.96·VP; emitter follows at +0.65 V; I = (VP − Ve)/R17 (39 Ω).
| VP | wiper at top | wiper at bottom |
|---|---|---|
| 15.0 V | 0 mA | 84.6 mA, P(R17) 0.28 W, P(Q6) ≈ 0.91 W |
| 14.3 V (after D3) | 0 mA | 79.9 mA, P(R17) 0.25 W, P(Q6) ≈ 0.82 W |
The 180 Ω top resistor does make the pot start at 0 mA as intended. The parts list's "up to 0.6 W at 50 mA" understates the end-stop by ~35 %; with the 26 °C/W slip-on heatsink plus RθJC 10 °C/W, Tj rises ≈ 30 °C above ambient — fine — but R17 is at half its ½ W rating and the full 80 mA DC also flows through SW1a, the coil tap, the coil's DCR (BOM asks ≤ 10 Ω → ≤ 0.06 W) and the 1 Ω sense resistor (TP3 reads 80 mV). Either document 80 mA as the design maximum or raise R17 to 68 Ω for a 50 mA stop.

## PB-F-016 — mounting holes: isolated from GND but 0.25 mm from the pour (JUDGMENT)
H1–H4 are plain 3.2 mm NPTH; the bottom pour stops 0.25 mm from the hole edge (Gerber measurement) and is only solder-mask-covered beyond that. An M3 screw head or washer (Ø 5.5–7 mm) will sit on masked GND copper; a scratched mask makes an unintended, intermittent chassis bond. Decide: either bond deliberately (one hole with a copper ring tied to GND, others with a 4 mm radius copper keep-out) or keep-out all four.
