# Reference: Electrosmith Seed3 Pedal Dev Kit — 9 V power input chain
**Date:** 2026-10-08 · **Source:** https://github.com/daisyaudio/Seed3-DevKit-Pedal (CERN-OHL-P-2.0), Rev3 netlist exported with kicad-cli 9.0.9 (Rev4 files are KiCad 10 format; BOM and sheet symbol list confirmed identical power section) · **Cross-check:** Daisy Seed3 datasheet, Power section, Figure 1.1 "+9V Power Supply Input" (same circuit, same refdes).

Context: Trey copied this circuit into the WavetableController Rev 2 schematic (FB3–FB6, R29–R32, C17–C22; Rev 2 files live on this branch, rev 1 under `archive/rev1_2026-08/`). The Rev 2 Design Review doc, item 2, flags the four series beads as over-current. This note records what Electrosmith actually built so the comparison is not re-derived.

## Electrosmith's chain (Rev2/Rev3/Rev4, unchanged since Rev2)
```
J8 barrel (centre-neg) → C20 100n → FB10 → FB4 → FB5 → [C21 100µ + C22 100n] → D5 NSR1020 Schottky → FB9 → +9V [C13 100µ]
  +9V → R30 3R3 → [C41 100µ] → R6 3R3 → DSY_VIN [C36 100µ]          (Daisy branch)
  +9V → R48 3R3 → [C14 100µ] → R55 3R3 → +9V_A [2×100µ, 3×100n]      (op-amp branch)
  +9V_A → R57 3R3 → [100µ, 10µ, 100n] → U2 LP2985-5.0 → +5V → FB1 → +5V_A
```
- Bead part: **FH CBW160808U601T**, 600 Ω @ 100 MHz, **1 A rated, 300 mΩ DCR** (LCSC C139183) — all nine positions in the Rev1 BOM, five in Rev2+.
- Rev1 also had a 3-bead chain in the *ground return* (FB3→FB7→FB8) and a 1 mH inductor (L2) in the Daisy branch; both were deleted in Rev2 ("Lots of little changes, and removed relays, etc."). The 3R3 resistors replaced the inductor, matching the datasheet's advice that 3.3 Ω "is not as strong of a filter as the inductor... however the resistor will cause some voltage drop".
- Electrosmith's own schematic note next to FB1: *"idk if we need this extra FB pi filter with everything else going on.."* — the beads are belt-and-braces, not load-bearing.
- Dev kit 9 V load: Seed3 + three OPA1652 + MCP6002 + LEDs, no display. Roughly 150–250 mA, so every bead runs at ≤ 25 % of its 1 A rating.

## Why the same topology misbehaves on WavetableController Rev 2
| | Electrosmith kit | WavetableController Rev 2 |
|---|---|---|
| Beads in the main 9 V path | 4 (FB10, FB4, FB5, FB9) | 4 (FB3–FB6) |
| Bead rating | 1 A, 300 mΩ | 200 mA, 450 mΩ (Sunlord GZ1608D601TF, LCSC C1002 — same part as rev-1 FB1–FB4) |
| 9 V load | ~0.15–0.25 A, no display | ~0.3 A typ / 0.5 A worst (Newhaven OLED 345–375 mA) |
| Bead margin | ≥ 4× under rating | 1.5–2.5× **over** rating |
| Drop across 4 beads @ 0.5 A | 0.6 V, 75 mW each | 0.9 V, 112 mW each (0603 ≈ 100 mW limit) |

The topology is sound and is Electrosmith's published reference. The defect in Rev 2 is the bead part number, not the schematic: the copy kept the drawing but not the 1 A part, and the OLED added ~0.35 A that the reference never had to carry.

## Options for Rev 2 (either closes item 2 of the review)
1. **BOM-only fix:** keep FB3–FB6 exactly as drawn, change the part to CBW160808U601T (or any 600 Ω / ≥1 A / ≤0.3 Ω 0603 bead, e.g. Murata BLM18KG601SN1D 1.3 A). Zero layout change. Beads stay within rating at 0.5 A, drop falls from 0.9 V to 0.6 V.
2. **Simplify:** one ≥1 A bead at the FB3 position, delete FB4–FB6 (the review's current recommendation). Loses ~10 dB of >30 MHz attenuation that the extra two input beads provided, which the 3R3/100 µF stages (fc ≈ 480 Hz) do not cover but which has no identified victim on this board.

Both keep the 3R3 + 100 µF RC stages, which are the filter that actually matters here and are identical to Electrosmith's.

## Every bead on WavetableController Rev 2 (netlist 2026-10-08; all seven are the same 200 mA / 450 mΩ C1002 part)
| Bead | Between | Branch current | Within 200 mA? |
|---|---|---|---|
| FB1 | GND ↔ GND | none | no-op (F-060) |
| FB2 | /+3V3_A → U4 MAX9814 VDD | 3.1 mA typ, 6 mA max (datasheet) | yes, 30× margin |
| FB3, FB4, FB5 | bridge → D6 anode (trunk) | 0.30 A typ / 0.49 A worst | **no** (F-050) |
| FB6 | D6 cathode → C19 node (trunk) | 0.30 A typ / 0.49 A worst | **no** (F-050) |
| FB7 | /+9V_FLAG → U6 TPS62172 VIN | 0.19–0.26 A | **no / marginal** (F-076, new) |

## Decision 2026-10-08 — all beads go to 2 A
Beads are always specified at 100 MHz; the parameter to pick is the impedance. Keep 600 Ω @ 100 MHz (the class the current part and Electrosmith's part are in: ≈ 50–100 Ω at 10 MHz, ≈ 200 Ω at 30 MHz, useful 10–300 MHz; below ~5 MHz every bead is a few ohms and the 3R3/100 µF stages do the work). A stocked 600 Ω / 2 A bead does not exist in 0603, so FB3–FB7 move to **0805: TDK MPZ2012S601AT000** (600 Ω, 2 A, 0.1 Ω max). 0603 alternative at 2 A is 220 Ω (TDK MPZ1608S221ATA00, 2.2 A, 0.05 Ω). Voltage drop at 0.49 A through four 0.1 Ω beads: 0.2 V (was 0.9 V). The one 0603 600 Ω/2 A part found (Eaton MFBA2V1608P-601-R) showed zero stock and a 19-week lead time.
