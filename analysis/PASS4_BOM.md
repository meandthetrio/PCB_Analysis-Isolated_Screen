# Pass 4 — Three-Way BOM Cross-Check
**Date:** 2026-08-13 · **Sources:** `ManifoldRe_BOM_NEW - Excel Format.xls` (31 lines, JLCPCB format: Comment/Designator/Footprint/LCSC#) ↔ schematic (78 refs) ↔ `.kicad_pcb` (79 footprints incl. dup R21)

## Verdict summary
- **Values: 100% consistent.** Every shared designator's BOM description matches the schematic value (all 58 checked: resistor values, cap values/dielectrics, ICs, connectors). No wrong-part findings.
- **The only SMD parts missing from the BOM are LED1/LED2** (F-002 sharpened — see below).
- **Every through-hole part is absent from the BOM** — consistent with a JLCPCB *SMT assembly* BOM where TH parts are hand-soldered. Intentional, but see F-026.
- **Two assembly landmines found:** S1/S2 (F-003 refined) and the duplicate-R21 placement trap (F-025, new).

## F-002 (sharpened): LED1/LED2 are the ONLY missing SMD parts
CLS6B-FKW RGB 5050 LEDs, top side. Boards return from assembly without LEDs. Combined with F-018 (they're wired to never light), the LED subsystem is doubly broken: not placed, and unable to work if placed.

## F-003 (refined): S1/S2 are a footprint-technology mismatch, not just phantoms
BOM S1/S2 = **SMD**-4P 6×6mm tactile switch (LCSC C2835239). The board's four tactile switches (TAC_SWITCH_1/2, TAC_SHIFT_L1/R1) are all **through-hole** footprints. So S1/S2 most plausibly *intend* TAC_SWITCH_1/2 — but as an SMD part that cannot mount on the THT footprints. Either a stale line from another revision or a part-selection/footprint divergence. Assembly house behavior: two BOM lines with no matching placement positions → flagged or silently skipped.

## F-025 (NEW — VIOLATION): the duplicate R21 is an auto-assembly trap
The BOM's only R21 line is **300Ω** (grouped with R24–R28, the LED resistors). The PCB contains **two** R21 positions: the 300Ω LED resistor *and* the 10Ω OLED damper (F-013/F-020). Any pick-and-place file exported from this PCB has two "R21" placements resolving to the single 300Ω BOM line → **a 300Ω resistor gets placed at the OLED damper position**, starving the OLED feed (30× the intended resistance in series with the display supply). This converts the refdes duplication from a bookkeeping bug into a physical mis-build on the next assembly run.

## F-026 (JUDGMENT): hand-assembly parts have no list
18 parts are TH/hand-soldered and appear on no BOM: A1 Daisy Seed, ENCL1/ENCR1 encoders, J1–J7 (OLED, MIDI ×2, audio ×3, phones... J1 barrel *is* in the SMT BOM), SW1, MK1 mic, C14 **470µF** (the OLED noise-fix bulk cap), TAC_×4. Risk: the noise-fix cap and other hand parts rely on memory. Recommend a second "hand assembly" BOM sheet.

## Housekeeping
- BOM D1 (C385198) differs from D2–D5 (C727114) — both Schottky, D1 is the power-entry diode: legitimate, not a mismatch.
- BOM encoding artifacts (`¬±`, `‚ÑÉ`, `Œ©` = mojibake for ±, ℃, Ω) — cosmetic only; LCSC part numbers are the authoritative column and are intact.
- BOM filename says "ManifoldRe", sheet says "WaveControllerBOM_NEW" — same project, naming drift only.
