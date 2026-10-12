# Daisy Seed 3 Pedal Dev Kit Rev3 — Reference Design Review
**Date:** 2026-10-12 · **Inputs:** Electrosmith's published Rev3 KiCad project and production Gerbers (2025-12-10) from `github.com/daisyaudio/ES-Seed3-DevKit-Pedal`, the Rev4 BOM from the Daisy CDN (`reference/electrosmith/seed3_pedal_devkit/`) · **Scope:** Passes 1–6, 78 ledger entries (`FINDINGS.md`): 4 violations, 5 zero-margin, 43 passes, the rest judgment · **Tooling:** KiCad 10.0.7; Pass 1 showed the committed production Gerbers are this exact project state.

---

## The short version

This is the board Trey's power entry was copied from, and the copy is exact. The Pedal kit's chain is the Seed 3 datasheet's Figure 1.1: three beads, a single series Schottky, one more bead, a 100 µF split node, then two 3.3 Ω / 100 µF / 3.3 Ω / 100 µF π-filters, one to Seed VIN and one to the analog 9 V rail. Trey's FB3/FB4/FB5 → D6 → FB6 → C19 → R29/R30 and R31/R32 chains are the same components in the same order. The differences are what Trey added and what he loads it with.

## The bead-chain answer (7 October items 2 and 9)

| | Pedal kit Rev3 | WavetableController rev 3 |
|---|---|---|
| Bead part | Chilisin PBY160808T-601Y-N, 600 Ω @100 MHz, **1 A**, 200 mΩ (PD-P2-01) | Murata C14709, 120 Ω, 2 A, 50 mΩ |
| Reverse-polarity scheme | the single series Schottky D5 is the whole scheme | 4-diode bridge D2–D5 **plus** the series diode D6 |
| Series diode current | 40–130 mW, ≤65 % of rating at 0.3 A | ≈0.2 W, near rating (R3-P2-06) |
| Second π branch load | 17 mA (op-amps + LDO) | 0.22–0.30 A (OLED buck + LEDs) |
| Bulk behind the beads | 200 µF, no inrush limit (PD-P2-03) | 200 µF, no inrush limit (R3-P2-05) |
| π resistors | 3.3 Ω 1206, 0.75 W | 3.3 Ω 2512, 1 W |

So: the 7 October review's "1 A bead" claim is confirmed; D6 is the copy and the bridge is the addition; the inrush exposure is inherited from the reference (the kit's 200 mΩ beads actually limit it four times better than Trey's 50 mΩ ones); and the reason Trey's "+9V" rail sags to 5.8 V while the kit's analog rail sits at 8.2–8.5 V is the 15× heavier load on that branch, not the circuit. The recommendation to feed the OLED buck from the C19 node, or delete the second π stage, stands.

## Tier 1 — Fab-rule violations in the reference (marginal; built this way)

- **Ground pours 0.025 mm from the routed edge** (PD-P1-06), same as the Eurorack kit, vs JLCPCB 0.2.
- **Toggle SW1 pads 0.161 mm ring** on three pads (PD-P1-04); footswitch pads at 0.254 on the 0.25 recommendation.
- **USB-C pegs 0.175 mm from GND pads** (PD-P1-07). KiCad 9.0.9 misses these two `hole_clearance` errors; 10.0.7 reports them.
- **Silk:** 62 strokes and 12 heights under JLC minimums, 39 of them user-facing legends (PD-P6-02).

## Tier 2 — Zero-margin and reference habits

- **Expression input on 3.3 V-only pin 28** fed from a 5 V MCP6002 follower through a 10k/20k divider: 3.33 V nominal, 3.36–3.38 V worst case, the datasheet's own Figure 4.5 (PD-P3-07, PD-P2-11).
- **+3V3_A has no capacitor at all** (PD-P2-06); +3V3 has one 100 nF at the opto, 209 mm routed from the Seed; SD socket 239 mm from any cap (PD-P2-05). Same family of omission as the Pod, the Eurorack kit and rev 3.
- **MIDI IN has no anti-parallel diode** across the opto LED (PD-P3-09); the Pod, the Eurorack kit and rev 3 all have one. THRU makes the H11L1 sink 21 mA (PD-P2-16).
- **Nine unfiltered switch inputs**, footswitch runs 116–148 mm on internal pull-ups (PD-P5-07).
- **4 GND vias only**, 38 of 65 SMD GND pads 20–35 mm from any layer link (PD-P1-10).
- **Documentation drift:** README switch refdes are the Rev1 names, sheet files are still named Rev1, the README links a Rev4 BOM that adds a D6 the Rev3 board doesn't have, and the Rev3 repo's only BOM has no MPN/DNP/assembly columns (PD-P4-02, PD-P6-06, PD-P2-18). The production BOM merges two footprints on one 10 µF line (PD-P4-01).

## Tier 3 — Things the kit does better than rev 3

- **Card detect is wired** to pin 12 with libDaisy support, the only board in the set that can see a card (PD-P3-05).
- **Audio is buffered** both ways (OPA1652 on +9V_A, 1 MΩ AC-coupled inputs, 100 Ω outputs) and no digital trace runs within 1 mm of any analog trace (PD-P5-05), the cleanest of the three references; MIDI lines stay 180 mm from the audio.
- **Every part is on a BOM with an Assembly column**, THT included.
- **Four 3.5 mm mounting holes** at 5 mm from every edge (PD-P6-07).

## What passed (verified, cited)
Schematic ↔ board 150/150, 0 pad diffs; 0 unconnected; min copper 0.20 mm; 0 clearance errors at JLC minimums; production Gerbers = project; paste ↔ BOM 286/286; 39/40 Seed pins on nets, firmware map 30/30; SD guideline met; USB pair 33 ps skew, 0 vias; power per datasheet Figure 1.1 with DSY_VIN 6.4–7.9 V; LP2985 and OPA1652 decoupled per datasheet; pots direct to ADC0–5.

## Caveats
Enclosure drawing not published, so hole positions are reported, not checked. Microchip, Kingbright, H11L1 and Chilisin datasheets unreachable; the bead rating comes from JLCPCB's part page and the Rev4 CDN BOM. STM32 absolute maximum ratings from memory, flagged.
