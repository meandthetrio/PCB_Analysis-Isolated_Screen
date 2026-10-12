# Daisy Seed 3 Eurorack Dev Kit Rev3 — Reference Design Review
**Date:** 2026-10-12 · **Inputs:** Electrosmith's published Rev3 KiCad 10 project, BOMs, production Gerbers (2026-06-18) from `github.com/daisyaudio/ES-Seed3-DevKit-Eurorack` and the Daisy CDN (`reference/electrosmith/seed3_eurorack_devkit/`) · **Scope:** Passes 1–6, 79 ledger entries (`FINDINGS.md`): 4 violations, 3 zero-margin, 44 passes, the rest judgment · **Tooling:** KiCad 10.0.7 native; Pass 1 showed the committed production Gerbers are this exact project state.

---

## The short version

A 28HP Eurorack module, 141.9 × 128.6 mm, that is the Seed 3 datasheet's reference circuits assembled verbatim: Figure 1.2 power entry (per-rail 1 A bead, series Schottky, 100 µF/10 µF/100 nF, 3.3 Ω-100 µF-3.3 Ω-100 µF to VIN), Figure 4.2 pots through a CD4051, Figure 4.3 CV inputs, Figure 2.4 gate inputs, Figure 6.1 CV outputs, TL072 audio buffering at ±12 V. Schematic and board agree pad for pad, the firmware pin map matches 32/32, the SD interface meets all three Seed 3 routing guidelines with the module's own traces included, and nothing digital runs beside the audio. All 31 Seed GPIO are consumed, so there is no spare pin for anything, including a display on SPI1.

## Tier 1 — Fab-rule violations in the reference (marginal; built this way)

- **Ground pours 0.025 mm from the routed edge on every side** (EU-P1-06). The project rule allows 0.025; JLCPCB asks for 0.2. Confirmed in the production copper. Any fab that enforces edge clearance will clip or reject it.
- **Toggle-switch pads SW3/SW4: 0.161 mm annular ring** on a 1.1 mm drill, six pads, under JLCPCB's 0.18 absolute minimum and invisible to the project's own 0.1 rule (EU-P1-04).
- **USB-C alignment pegs 0.175 mm from the connector's GND pads** vs 0.2 required; these are the two `hole_clearance` DRC errors (EU-P1-07). The same GCT USB4110 footprint issue appears on the Pedal kit; Trey's rev 3 has the same class of problem on its USB4105 (0.197).
- **Silk under JLC minimums** on 31 strokes and 9 heights (EU-P6-02), cosmetic.

## Tier 2 — Habits shared with Trey's board (and the Pod)

| Habit | Eurorack kit | Rev 3 |
|---|---|---|
| No capacitor at the SD socket | 124.7 mm to the only 3V3 cap (EU-P2-04) | 120 mm |
| One 100 nF on +3V3 at the opto, no bulk | yes | yes |
| No encoder/button/toggle filtering | yes (EU-P2-10) | yes |
| No GND stitching vias; F-side GND reaches the B plane only through component holes | 0 vias, 46 F-side SMD GND pads via 39 PTH pads (EU-P1-10) | 0 vias, 15 fragments |
| No PWR_FLAGs → 5 ERC "power pin not driven" false positives | yes (EU-P2-17) | yes (4) |
| Card detect not wired | yes (EU-P3-05) | half-wired |
| Unlimited inrush into the bulk caps | 110 µF per rail, 30 mJ (EU-P2-03) | 200 µF, 26 A |
| USB-C data-only, 5.1 k CC, USBLC6 | yes | yes |

Two findings worth carrying to rev 3: the Seed 3 datasheet's SD guideline (≤10 mm spread, equal DATA/CMD via counts including the module's own) is what the kit was designed to, and rev 3's 24–41 mm runs would fail it if the board ever moves to a Seed 3 (EU-P5-01c); and TL072 op-amps bypassed only rail-to-rail with no cap to ground within 54–130 mm (EU-P2-06) is a reference habit, not something to copy.

## Tier 3 — Reference details that answer earlier questions

- **MIDI OUT/THRU series resistors are 10 Ω/10 Ω** per the Seed 3 datasheet (EU-P3-10), not the 10/33 Ω MIDI-association values rev 3 uses; both work. MIDI THRU makes the H11L1 sink 21 mA when low (EU-P2-14), at the opto's rating.
- **LEDs are sourced from GPIO through 2 kΩ**: red 0.7 mA, green/blue 0.17 mA, with green/blue Vf at the 3.3 V rail (EU-P2-08/09, zero-margin). Dimmer than the Pod; opposite polarity to both the Pod and rev 3.
- **Gate input threshold is ≈0.75 V**, where the README says 0.4 V (EU-P3-11).
- **BOM:** the CDN sheet substitutes generic parts for the ones the schematic names (Shikues B5817WS for NSR1020, HXY for ST USBLC6, HOAUC for GCT USB-C) on "Sub OK = NO" lines (EU-P4-02); the production export splits one 100 k line because of a `100k`/`100K` case difference (EU-P4-01); the project folder carries the Pedal kit's Rev1 parts list and libraries (EU-P4-05). Every pasted part is on the BOM; all 32 THT parts are listed with an Assembly column, which is the hand-solder sheet rev 3 lacks.

## What passed (verified, cited)
Schematic ↔ board 139/139, 0 pad diffs; 0 unconnected; min copper 0.20 mm; 0 clearance errors at JLC minimums; vias 0.6/0.3 tented; production Gerbers = project; paste ↔ BOM 272/272; Seed 3 pin table 40/40 with the five 3.3 V-only pins bounded; firmware map 32/32; SD guideline met; USB pair 15 ps skew; MIDI Type A on all three jacks; CV/gate/DAC scaling per datasheet; four Eurorack rail slots on 122.5 × 126.9 mm.

## Caveats
Eurorack panel-spec comparison is from memory (Doepfer page unreachable). Seed 3 datasheet publishes no VIN/3V3 current figure, so Seed current is bracketed. Microchip, Kingbright, H11L1 and Chilisin datasheets were unreachable; values flagged where used.
