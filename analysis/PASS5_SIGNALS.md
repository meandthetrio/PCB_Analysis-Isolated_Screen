# Pass 5 — Signal-Specific Report
**Date:** 2026-08-13 · **Truth checked:** `.kicad_pcb` geometry + schematic networks · **Thresholds:** TPA6110A2 datasheet SLOS314B (fetched, archived in scratchpad), MIDI 1.0 3.3V electrical practice, Daisy datasheet v1.0.5

## F-027 (NEW — the big one): the I2C bus has NO pull-up resistors in this design
`/I2C_SCL` = A1.12 ↔ J2.3 and `/I2C_SDA` = A1.13 ↔ J2.4 — **two-node nets, no resistors, in both schematic and BOM**. I2C is open-drain and cannot work without pull-ups, so the working boards must be relying on pull-ups **on the OLED module itself** (J2 carries a Retroactive 2.42" SSD1306/1309 module; such breakouts usually include ~4.7–10k) or STM32 internal pull-ups (~40k, far too weak for this bus). The bus is **203/205mm long with 3–4 vias per line** — combine an undocumented/uncontrolled pull-up with a 200mm bus sharing the noisy 3V3_D rail (F-019) and you have a complete causal chain for the historical I2C/OLED instability. Action: confirm the module's onboard pull-up value; add explicit 2.2–4.7k pull-ups at the board level on a respin.

## USB (F-028 — JUDGMENT, minor)
MCU-side pair: P = 127.6mm/3 vias, N = 134.8mm/5 vias → 7.2mm and 2-via asymmetry; widths mix 0.1/0.2mm; no impedance control (inherent to 2-layer/1.6mm). At Full-Speed (12Mbps, ~7mm ≈ 45ps vs multi-ns edges) this is functionally fine — and field-proven. Tidy on respin, not a defect. USB routes through U2 (USBLC6-2P6 ESD) correctly.

## MIDI (F-029 — PASS, cited)
- **MIDI OUT (J3):** USART1_TX → R1 10Ω → Tip; +3V3_D → R4 33Ω → Ring — exactly the MIDI 3.3V electrical recommendation (10Ω data / 33Ω source).
- **MIDI IN (J6):** Ring/Tip → R2/R3 (0Ω) → H11L1 opto (the classic MIDI opto) with 220Ω current limit (R5) and reverse-protection diode — textbook.
- **Refdes clarification recorded:** D1 is the MIDI-input protection diode, NOT the power diode; the barrel input's "Schottky bridge" is D2–D5. (Corrects the Pass 2 topology sketch's "D1 Schottky" label.)

## SD interface (PASS)
Runs 89–108mm, max skew ~19mm (~130ps — irrelevant at SDIO 25–50MHz). 47K pull-ups per Daisy reference design (verified Pass 2). Width mix 0.1/0.2mm noted; harmless.

## Audio path
- **F-031 (JUDGMENT, datasheet-cited): headphone amp bulk cap missing.** TPA6110A2 SLOS314B: 0.1µF close to VDD ✓ (C5 at 5.5mm) **plus** "aluminum electrolytic capacitor of 10µF or greater placed near the power amplifier is recommended" — absent; 3V3_A has only the 100nF, fed over 84mm from the Daisy. THD/oscillation risk per datasheet, especially with long output leads.
- **Mid-rail bypass check (PASS, computed per datasheet Eq. 6):** C(B)·230k = 100nF·230k = 23ms ≥ Ci·Ri = 470nF·22k = 10.3ms ✓.
- Output coupling 100µF (C6/C7) + 10k bleed resistors (R22/R23) to GND — good practice ✓.
- **F-030 (JUDGMENT):** line-level audio runs are long and thin: AUDIO_OUT_L/R 285/277mm, AUDIO_IN_L 213mm, mic return 171mm — all 0.1mm, crossing the board over the (Gerber-truth) ground pour. Works as built; on a respin keep analog shorter/edge-routed and away from SD/USB corridors.
- J4 (audio in) ring floating — mono-source assumption, acceptable (carried from F-024).

## Findings ledger updates
F-027 (I2C pull-ups — VIOLATION-plausible pending module check), F-028 (USB tidy-up), F-029 (MIDI PASS + D1 role corrected), F-030 (audio run lengths), F-031 (TPA6110 bulk cap, datasheet-cited).
