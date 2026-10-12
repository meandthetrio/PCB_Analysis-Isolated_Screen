# Daisy Pod Rev5 — Reference Design Review
**Date:** 2026-10-12 · **Inputs:** Electrosmith's published Pod Rev5 set (`reference/electrosmith/daisy_pod/`: Eagle schematic + board, BOM, schematic PDF, databrief) · **Why:** the WavetableController is derived from this design; every pass carries a side-by-side against Trey's rev 3 · **Scope:** Passes 1–6, 74 ledger entries (`FINDINGS.md`): 7 violations, 4 conversion artefacts, 43 passes, the rest judgment.
**Truth:** the Eagle files are the source of record. They were converted to KiCad for DRC and geometry after stripping 115 custom Eagle layers the headless importer cannot map; everything that conversion changed is tagged CONVERSION-ARTEFACT in the ledger and is not a finding against Electrosmith.

---

## The short version

The Pod is a clean, small, well-grounded board: one-piece ground planes on both layers with 24 stitching vias, 0.2 mm minimum copper, every chip's capacitor within 3 mm, signal runs of 10–60 mm, nothing routed beside the audio. It also carries, in the reference itself, several of the habits the rev-2 and rev-3 reviews flagged on Trey's board: no capacitor at the SD socket, one 100 nF per rail and no bulk, no ≥10 µF at the headphone amp, no encoder or button filtering, card detect half-wired, LEDs that run at a milliamp. Trey inherited all of those. Where his board is worse than the reference it is a consequence of being three times the size and carrying a 9 V input and a display, not of changing the circuits.

Two things in the Pod files are genuinely wrong, both in the BOM, and one firmware-hardware conflict in the reference as shipped.

## Tier 1 — Errors in Electrosmith's own files

**1. The BOM orders the two DNI MIDI jumpers.** (DP-P4-01 ✔, DP-P3-12 ✔) R78 and R84 are "DNI 0R" in the schematic and board (they select TRS Type B), but the BOM's 0 Ω line lists all four jumpers. Fitting them shorts MIDI tip to ring and kills MIDI in. The BOM has no DNI column.

**2. One Seed socket where two are needed.** (DP-P4-02 ✔) The Samtec SSM-120 line is quantity 1; the Seed footprint is two 20-pin rows 15.24 mm apart.

**3. Encoder click shares a pin with the MIDI UART's TX.** (DP-P3-08, verified in libDaisy master) The click is on Seed pin 14 = PB6. libDaisy's MIDI transport defaults to USART1 with TX on PB6 in transmit-and-receive mode, and `DaisyPod::Init()` calls the MIDI init after the encoder init, so PB6 becomes a push-pull output idling high. Pressing the encoder shorts that output to ground. One-line firmware fix (TX pin unset or RX-only mode). Trey's rev 3 is immune: its clicks are on pins 22 and 29 and pin 14 is MIDI OUT.

## Tier 2 — Margins in the reference (fabbed fine; worth knowing because Trey copied them)

- **Micro-USB shell-peg pads** have a 0.058 mm ring on their short axis, under JLCPCB's 0.18 minimum and Eagle's own rule; no-net pads, cosmetic break-out risk (DP-P1-04).
- **Solder-mask slivers of 0.09–0.098 mm** between fine-pitch pads because Eagle plots a 0.0762 mm mask frame; JLC will gang those openings (DP-P1-13).
- **Minimum clearance 0.127 mm** on the USB lines, exactly Eagle's 5 mil rule, above JLC's 0.10 (DP-P1-02).
- **Silk:** 61 of 78 legend texts are under JLC's 1.0 mm / 0.15 mm minimum (DP-P6-01, DP-P6-02); cosmetic.
- **USBLC6 ground on a single thermal spoke** (DP-P1-11).

## Tier 3 — Reference habits Trey inherited (same finding on both boards)

| Habit | Pod | Rev 3 |
|---|---|---|
| No capacitor at the SD socket | VDD 70 mm (routed) from the only 3V3_D cap | 120 mm (R3-P2-10) |
| One 100 nF per rail, no bulk | yes | yes, plus 700 µF on the 9 V side |
| TPA6110A2 without the ≥10 µF the datasheet recommends | yes (DP-P5-05) | yes (R3-P2-11) |
| Encoder/buttons on internal pull-ups, no RC | yes (DP-P2-08) | yes |
| SD card detect half-wired | yes (DP-P3-04) | yes (F-022) |
| USB data-only, VBUS to the TVS only | yes (DP-P3-05) | yes |
| MIDI in: 220 Ω / H11L1 / NSR1020 / 270 Ω, TRS A by jumpers | yes | yes, plus MIDI OUT |
| LEDs on Seed pins 24/25/26/27/30/31, three of them 3.3 V-only | yes, harmless at 1 mA | yes, behind 1 k into transistor bases |

**One correction to the rev-3 list that fell out of this review:** TI's SLOS314B asks for the 5 pF feedback capacitors only when the feedback resistor exceeds 50 kΩ. Both boards use 33 kΩ, so that half of the headphone-amp tidy item on Trey's list is optional; the 10 µF bulk half stands (DP-P2-11).

## Where rev 3 is worse than the reference, and why

- **Ground.** Pod: one-piece planes both sides, 24 stitching vias, 0 islands. Rev 3: 0 GND vias, front pour in 15 fragments (R3-P1-08). This is the single biggest divergence from the reference and the easiest to fix.
- **Rail length.** Pod 3V3_D trunk 110 mm at 0.41 mm (69 mΩ); rev 3 249 mm at 0.3 mm (0.41 Ω). Board size.
- **Signal runs.** SD 11–20 mm vs 24–41; audio 44–56 mm vs 141–228; USB pair 0 vias vs 9/11; nothing beside audio vs UART at 0.41 mm for 49 mm (R3-P5-04). Board size and jack placement.
- **Minimum copper.** Pod 0.20 mm; rev 3 still has 75 mm at 0.10.
- **BOM completeness.** Pod BOM is SMD-complete (47/47 join, all paste matched); rev 3 has the LEDs off-BOM and 18 THT parts on no list.

## Where rev 3 improves on the reference

- **LED brightness.** Pod drives the LEDs straight from 3.3 V GPIO through 1 k: red 1.2 mA, green and blue 0.2–0.5 mA, zero at the LED's maximum Vf (DP-P2-05/06). Rev 3's transistor stage from the 9 V side gives 10–20× the current, which is why that circuit exists.
- **MIDI OUT** (the Pod has none), **bleed resistors** on the headphone outputs, **click moved off the UART pin**, **two encoders**, **USB-C**.
- **Mounting holes:** the Pod has four M3; rev 3 has none (R3-P6-05). The reference is right here.

## Conversion artefacts (not findings against the design)

Stripping Eagle's unmappable layers removed the two milled slots for the micro-USB board-lock legs (DP-P1-07) and the fiducials' copper-restrict diamonds (DP-P1-09, the 6 mask-bridge DRC errors), and KiCad's same-net zone overlap rule flags the thermal-free pad under the headphone amp (DP-P1-10). The converted project carries KiCad default rules, not Eagle's (DP-P1-15); Eagle has no courtyards (DP-P6-04). Anyone building from the conversion rather than the Eagle source must put the USB slots back.

## Sources

JLCPCB capabilities (fetched 2026-10-12), the board's own Eagle rule set `ES_DRC_MaskedVias`, TI SLOS314B (fetched from ti.com), Bourns PEC11J datasheet (fetched), JLCPCB parts API for every MPN, libDaisy master (`daisy_pod.cpp`, `hid/midi.cpp`). Not reachable: Cree CLVBA-FKA datasheet (Vf taken from the same-family CLS6B sheet), STM32H7 GPIO absolute maximum (from memory, flagged), Alps and Song Huei pot sheets.
