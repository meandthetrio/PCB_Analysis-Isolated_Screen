# Pass 2 — Power Distribution Report
**Date:** 2026-08-13 · **Truth checked:** `.kicad_sch` netlist for topology, `.kicad_pcb` for copper/distances (GND copper deferred to Gerber truth per dual-truth rule) · **Thresholds:** Daisy Seed datasheet v1.0.5 (fetched 2026-08-13, saved in scratchpad), IPC-2221 computed, JLCPCB caps (Pass 1)

## Rail topology (from schematic netlist)
```
9V barrel (J1) → D2–D5 Schottky bridge → FB3 → /+9V_FILT ── A1.39 Daisy VIN  [+ C15 10µF bulk, 67mm away]
   (corrected per Pass 5 F-029: D1 is the MIDI-input protection diode, not the power diode)
                                          └── R21/R24–R28 (300Ω ×6) → LED1/LED2 cathodes  ← THE LED BUG (F-001/F-018)
Daisy A1.38 (3v3 digital out) → /+3V3_D ── SD card P1, MIDI opto U1, 5×47K SD pullups,
                                           FB2 → MAX9814 mic amp, FB4 → /OLED_HOT → J2 OLED
Daisy A1.21 (3v3 analog out)  → /+3V3_A ── U3 TPA6110A2 headphone amp
USB VBUS → /+5V_USB → U2 ESD protector only (data-only USB — by design, not-a-finding)
```

## Verified against datasheet (cited)
| Check | Board | Datasheet | Verdict |
|---|---|---|---|
| VIN range | 9V in | VIN abs max +4…+17V (Table 1) | OK |
| AGND↔DGND tie | A1.20 and A1.40 both on GND | "AGND must be connected to DGND" (Fig 1.1) | OK |
| SD pullups | 5×47K to 3V3_D | "47K pullup resistors necessary, except Pin 7" (Fig 1.6) | OK — matches reference design |
| LED drive | 300Ω to **9V** | Reference: GPIO → 1K → LED → **GND** (Fig 1.8) | **VIOLATION — see F-018** |
| 3v3 rail load capacity | est. ~150mA peak external | **datasheet publishes no 3v3 current limit** | UNVERIFIABLE — load estimate only |

## F-018 — LED drive: worse than previously logged (refines F-001)
LED anodes sit on Daisy GPIOs; cathodes pull to +9V through 300Ω. Consequences, now datasheet-cited:
1. **LEDs can never light** — permanently reverse-biased (GPIO 0–3.3V vs 9V cathode side).
2. **LED dice see 5.7–9V reverse voltage** — typical LED reverse max is ~5V (CLS6B-FKW datasheet to confirm in Pass 4).
3. **Three of the six GPIO pins are the 3.3V-only pins** — LED_2_R=pin 24, LED_1_B=pin 25, LED_2_B=pin 30, exactly on the datasheet's "3.3V tolerant I/O only" list (Table 1 notes). If any reverse-stressed LED die avalanches, it injects current into pins with **no 5V tolerance**. Latent MCU-damage path, not just a dead-LED bug.

## F-019 — +3V3_D distribution architecture (the OLED/I2C noise root cause)
Measured: the entire rail has **one** decoupling cap (C1 100nF, located at the MIDI opto). The SD card's power pin is **109.5mm** from it over 0.1mm trace (≈0.49Ω/100mm ⇒ ~0.5Ω path R), with **no local capacitor**. The rail totals 254mm of 0.1mm trace shared by SD, OLED feed, MIDI opto, and I2C pullups.
- Ampacity is fine (IPC-2221: 0.1mm/1oz = 450mA @ ΔT10°C vs ~150mA est. peak) — **the problem is impedance, not heating**: SD card burst currents (up to ~100mA) create dips/noise on the shared rail.
- The board itself testifies: the OLED branch got a ferrite (FB4) + **470µF** (C14) + 100nF (C17) + a hand-added 10Ω damper (the PCB-only duplicate R21) — symptom treatment added during Trey's noise debugging.
- Recommendation (JUDGMENT): 100nF+10µF at the SD connector, 0.25mm+ rail trunk, and the 470µF band-aid likely becomes unnecessary.

## F-020 — Board-level fix never back-annotated
The 10Ω R21 on /OLED_HOT↔/+3V3_D exists only in the PCB (duplicate refdes, F-013); the schematic's OLED feed is FB4 only. Whoever respins from the schematic loses the noise fix silently.

## Rail copper summary (.kicad_pcb)
| Rail | Copper | IPC-2221 capacity @ΔT10 | Est. load | Path R note |
|---|---|---|---|---|
| /+9V_FILT | 143mm @ 0.2mm | 745mA | Daisy VIN (est. ~100mA) | OK |
| /+3V3_D | 254mm @ 0.1mm + 18mm @ 0.2 | 450mA | ~150mA peak (est.) | ~0.5Ω to SD — F-019 |
| /+3V3_A | 84mm @ 0.2mm | 745mA | headphone amp | supply-cap review → Pass 5 |
| /+5V_USB | 11mm @ 0.2mm | 745mA | ESD chip only | OK |
| GND | 73mm @ 0.1mm (pcb) / **pour (Gerber truth)** | — | — | fine as fabbed; F-006 for the file |

Open item for Pass 5: TPA6110A2 supply decoupling (100nF only) vs its datasheet recommendation — not yet fetched, unverified.
