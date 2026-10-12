# Daisy Pod Rev5 — Pass 5: Signal-Specific Report
**Date:** 2026-10-12 · **Truth checked:** `ES_Daisy_Pod_Rev5.brd` copper (Eagle source of record) via the KiCad 9.0.9 conversion `daisy_pod/kicad/ES_Daisy_Pod_Rev5.kicad_pcb` (pcbnew export; per-net wire totals cross-checked to 0.1 mm against an independent parse of the `.brd` `<signal>` wires — Pass 3 §1) + the Eagle schematic networks. Board 90.2 × 52.3 mm, 2-layer; Eagle layer 1 = Top, 16 = Bottom.
**Tools** (`analysis/daisy_pod/scripts/`): `pcb_export.py` (rev-3 script, unchanged, run on the Pod conversion), `net_geometry.py` (pad-to-pad copper path, widths, vias, islands, stubs; rev-3 script with an `ALL` option), `proximity.py` (same-layer edge gap, parallel run at ≤ GAP, opposite-layer crossings; rev-3 script unchanged), `eagle_brd_netlist.py`.
**Thresholds / sources:** trace delay **5.64 ps/mm** (rev-3 Pass 5 derivation, Hammerstad microstrip ε_eff 2.86 for 0.3 mm on 1.5 mm FR-4; for the Pod's 0.2–0.25 mm traces ε_eff changes < 2 %, so the same figure is used); SDMMC 25/50 MHz class periods 40/20 ns; USB 2.0 FS 12 Mb/s (83 ns bit); MIDI 31.25 kbaud; TPA6110A2 datasheet **SLOS314B fetched 2026-10-12 from ti.com** (`scratchpad/pod_p3_5/dl/ti/tpa.txt`: SHUTDOWN pin description l.100, decoupling l.1012–1030, Eq. 6/7/8 and Table 1 l.1040–1090); libDaisy `led.cpp` (software PWM); STM32H750 timer alternate functions **from memory, not fetched**; rev-3 numbers from `analysis/rev3/PASS5_SIGNALS.md` / `PASS3_CONNECTIVITY.md`.

## Headline
- **The Pod is a compact, clean reference.** Longest digital line is the USB ID (79 mm); SD lines are 11–20 mm; the USB D+/D− pair runs **coupled for 47.8 mm at a 0.127 mm edge gap with 0 vias and 1.4 mm length mismatch**; audio lines are 44–56 mm; **no digital trace runs parallel to any audio signal within 1.0 mm on the same layer**. Trey's rev-3 equivalents are 2–6× longer because his board is 3.6× the area (165×102 vs 90×52 mm) with the jacks on the far edge.
- **Topologies Trey inherited verbatim:** SD with 47 k pull-ups on DAT0–3/CMD and none on CLK; USB through a USBLC6-2 with VBUS only as the clamp reference; MIDI IN 220 Ω + H11L1 + antiparallel diode + 270 Ω pull-up; headphone chain Seed → dual pot → 470 nF → 22 k → TPA6110A2 (33 k feedback, gain 1.5) → 100 µF → jack; volume pot at the amp input; knobs on `+3V3_A`; no RC on switches/encoder/knobs. The Pod **also lacks the TPA6110A2's recommended ≥ 10 µF electrolytic** (only C60 100 nF on `+3V3_A`) — Trey's F-031 is inherited, not introduced.
- **Two Pod-only items:** no local decoupling at the SD socket (nearest cap 70 mm away; Pass 2) and the ENC_CLICK/USART1_TX firmware conflict (Pass 3 DP-P3-08).

## 1. SD interface (P1 Hirose DM3AT ↔ Seed pins 2–7)
| Net | Seed pin → P1 pad | Pad-to-pad | Vias | Width (mm) | Pull-up (47 k → `+3V3_D`) | Pull-up stub from P1 |
|---|---|---|---|---|---|---|
| `SD_D0` | 5 → 7 (DAT0) | 12.4 mm | 1 | 0.203 | R2 | 4.8 mm |
| `SD_D1` | 4 → 8 (DAT1) | 20.3 mm | 3 | 0.203 (+2.6 mm 0.254) | R16 | 3.9 mm |
| `SD_D2` | 3 → 1 (DAT2) | 10.6 mm | 1 | 0.254 / 0.203 | R3 | 5.7 mm |
| `SD_D3` | 2 → 2 (CD/DAT3) | 16.9 mm | 1 | 0.254 | R4 | 4.3 mm |
| `SD_CMD` | 6 → 3 (CMD) | 11.9 mm | 1 | 0.203 / 0.2 / 0.254 | R1 | 3.7 mm |
| `SD_CK` | 7 → 5 (CLK) | 11.3 mm | 1 | 0.203 | none (correct) | — |
- Data-to-clock skew ≤ 9.0 mm (`SD_D1`) = **51 ps**; data-to-data ≤ 9.7 mm = 55 ps — 0.1–0.3 % of a 20–40 ns SDMMC period. `SD_CK` runs 0.4 mm from `SD_CMD` for 0.4 mm and 0.7 mm from `SD_D0` for 0.5 mm (`proximity.py`) — nothing parallel. Widths 8–10 mil (0.203/0.254 mm). Every net is one copper island, no stubs beyond the pull-up branches.
- **Decoupling at P1.VDD (pad 4):** the only capacitor on `+3V3_D` is C11 100 nF at the opto U15, **70.3 mm** of copper from P1.VDD; the Seed's pin 38 (source) is 37.7 mm away. No local cap at the SD socket. → noted for Pass 2 (JUDGMENT DP-P5-01b). Trey's rev 3 should be checked for the same (rev-3 Pass 2).
- Card detect: `SWA` open, `SWB` GND (Pass 3 DP-P3-04).
- **PASS** on the interface itself; identical pull-up scheme to Trey's (rev-2 F-021 cited the Daisy reference — this *is* that reference).

## 2. USB Full-Speed pair (P5 micro-AB → U7 USBLC6-2SC6 → Seed pins 36/37)
| Net | Path | Length | Vias | Width |
|---|---|---|---|---|
| `USB_OTG_FS_D_IN_−` | P5.2 → U7.1 | 3.8 mm | 0 | 0.203 |
| `USB_OTG_FS_D_IN_+` | P5.3 → U7.3 | 4.2 mm | 0 | 0.203 |
| `USB_OTG_FS_D−` | U7.6 → U1.36 | 57.9 mm | 0 | 0.203 |
| `USB_OTG_FS_D+` | U7.4 → U1.37 | 59.3 mm | 0 | 0.203 |
| `USB_OTG_FS_ID` | P5.4 → U1.1 | 79.4 mm | 4 | 0.203 (57.3) + 0.254 (22.1) |
| `USB_VBUS` | P5.1 → U7.5 | 7.4 mm | 0 | 0.203 |
- Pair mismatch **1.4 mm = 8 ps** (0.01 % of an 83 ns bit); **0 vias on the Seed side**, all on the top layer; D+/D− run **parallel for 47.8 mm at a 0.127 mm (5 mil) minimum edge gap** — a deliberately coupled pair. No impedance control (2-layer, 0.2 mm/0.127 mm on 1.6 mm FR-4 is nowhere near 90 Ω differential), which is normal for FS; the Seed itself does the same. U7 sits 7.9 mm from the connector (P5 at (65.5, 1.5), U7 at (65.4, 9.2)), stubs 3.8/4.2 mm — correct TVS placement. Pass-through pin pairs 1→6 and 3→4 (USBLC6 pinout from memory; consistent with the schematic's I/O_1/I/O1 naming).
- **PASS.** Rev 3: 130.2/130.6 mm, 9/11 vias, 0.4 mm skew — functionally equivalent, 2.2× longer, far more layer changes.

## 3. MIDI
**IN (J1, TRS):** `J1.RING → R79 0 Ω (34.1 mm) → MIDI_IN_A → R63 220 Ω (11.9 mm) → N$77 (6.2 mm) → U15.A` with D5 NSR1020 cathode on N$77; `J1.TIP → R83 0 Ω (25.5 mm) → MIDI_IN_B (10.3 mm) → U15.C` with D5 anode — D5 is antiparallel across the opto LED (reverse protection). R78/R84 (DNI) are the crossed alternates (Type B). Output: `U15.OUT → R64 270 Ω (8.1 mm) → +3V3_D` pull-up and `→ U1.15` USART1_RX (17.0 mm, 1 via); U15.V decoupled by C11 100 nF at 2.7 mm. All 0.203 mm wide, bottom layer mostly. Topology = the standard 5 mA current-loop receiver; identical, part for part, to Trey's rev-3 MIDI IN (R2/R3 0 Ω, R5 220 Ω, U1 H11L1, D1, R6 270 Ω — rev-2 F-029). **PASS.** BOM lists all four 0 Ω jumpers (Pass 3 DP-P3-12).
**OUT:** **none on the Pod.** The only USART1_TX-capable pin (14) carries `ENC_CLICK`. Trey added MIDI OUT (J3, 10 Ω/33 Ω) on pin 14 — the one place rev 3 is a superset of the Pod, and it removes the Pod's firmware conflict (Pass 3 §5).

## 4. Audio
**Jacks (CUI SJ2-35863B1, 3.5 mm TRS, pads 1 sleeve / 2 tip / 3 ring / 4,10 switch contacts):** J2 IN: tip = `AUDIO_IN_L` (Seed 16), ring = `AUDIO_IN_R` (17), sleeve GND, switch contacts open. J3 OUT: tip = `AUDIO_OUT_L` (18), ring = `AUDIO_OUT_R` (19). J4 HEADPHONE: tip ← C62−, ring ← C63−. All sleeves on the single GND.

| Net | Path | Length | Vias | Width |
|---|---|---|---|---|
| `AUDIO_IN_L` | J2.tip → U1.16 | 56.3 mm | 2 | 0.254 |
| `AUDIO_IN_R` | J2.ring → U1.17 | 46.0 mm | 0 | 0.254 |
| `AUDIO_OUT_L` | U1.18 → J3.tip | 44.3 mm (pot end P8.P$5 tapped at 30.6 mm) | 3 | 0.254 |
| `AUDIO_OUT_R` | U1.19 → J3.ring | 51.8 mm (pot end P8.P$4 at 22.3 mm) | 6 | 0.254 |
| `HEADPHONE_WIPER_L` | P8.P$2 → C53 | 20.0 mm | 2 | 0.254 |
| `HEADPHONE_WIPER_R` | P8.P$3 → C54 | 13.5 mm | 2 | 0.254 |
| `N$34` / `N$12` | C53/C54 → R23/R24 22 k | 1.5 / 1.5 mm | 0 | 0.254 |
| `N$19` / `N$20` | R23/R24 → U4.IN1/IN2 (R27/R33 33 k feedback 2.4/1.5 mm) | 5.8 / 5.8 mm | 0 | 0.254 |
| `N$40` / `N$41` | U4.OUT1/OUT2 → C62+/C63+ | 23.8 / 21.4 mm | 3 / 1 | 0.254 |
| `HEADPHONE_OUT_L/R` | C62−/C63− → J4 tip/ring | 20.6 / 28.6 mm | 0 | 0.305 |
| `N$39` | U4.BPASS → C56 100 nF | 2.9 mm | 0 | 0.254 |

- **Headphone chain** = Seed line out → dual pot P8 (10 k, ends on `AUDIO_OUT_L/R`, other ends GND, volume at the amp *input*) → 470 nF (C53/C54) → 22 k (R23/R24) → TPA6110A2 inverting input, 33 k feedback → **gain 1.5 V/V** (schematic note "Gain = 33K/22K = 1.5 V/V") → 100 µF (C62/C63) → J4. Exactly Trey's rev-3 chain (rev-3 Pass 3 §5: C2/C3 470 nF, R12/R13 22 k, R14 33 k, C6/C7 100 µF).
- **SHUTDOWN (U4.3) tied to GND** = normal operation: SLOS314B l.100 "Puts the device in a low quiescent current mode when held high"; IDD spec'd at SHUTDOWN = 0 V. ✓
- **Datasheet checks (SLOS314B):** Eq. 6 start-up/pop rule 1/(C_B·230 k) ≤ 1/(C_i·R_i): 1/23 ms ≤ 1/10.3 ms ✓ (C_B = C56 100 nF, within the recommended 0.1–1 µF, l.1063); Eq. 8 adds ≤ 1/(R_L·C_C) = 1/3.2 ms (32 Ω, 100 µF) ✓. Output corner Eq. 7: f_c = 1/(2π·R_L·C_C) = **50 Hz at 32 Ω, 99 Hz at 16 Ω** — better than TI's own Table-1 example (68 µF/32 Ω = 73 Hz, "headphone response is adequate"). Line-level loads (10 k) → 0.16 Hz. PASS; thin bass into 16 Ω earbuds is inherent to the single-supply SE topology, not a Pod defect.
- **Supply decoupling:** U4.VCC has C60 100 nF at **3.4 mm** ✓ ("typically 0.1 µF, as close as possible", l.1026) but **no ≥ 10 µF aluminium electrolytic "near the power amplifier"** (l.1029) anywhere on `+3V3_A` (the rail's only capacitor is C60; the Seed's own `+3V3_A` output caps are the nearest bulk, ≥ 47 mm away). This is the same gap rev-2 F-031 found on Trey's board — **inherited from the Pod** (JUDGMENT DP-P5-05).
- Line inputs `AUDIO_IN_L/R` go straight from the jack tip/ring to the Seed codec pins with no series R, no TVS, no cap (the Seed carries 3.6 k + 4.7 µF on-module, Seed Rev7 sheet R24/C33). Same on Trey's board.

## 5. Proximity of audio to digital (`proximity.py`)
Aggressors: all SD, USB, encoder, button, LED (GPIO and cathode) nets, `USART1_RX`, MIDI nets, SPI/I2C header lines, `+3V3_D`. Victims: `AUDIO_IN/OUT_L/R`, both wipers, all TPA6110 input/output nets, `HEADPHONE_OUT_L/R`, `POT_1/2`, `A1`, `A7`, `+3V3_A`.
| Pair | Same-layer min edge gap | Parallel run at ≤ 0.5 mm | at ≤ 1.0 mm | Opposite-layer crossings |
|---|---|---|---|---|
| any digital net vs any **audio signal** net | ≥ 1.03 mm | **0** | **0** | `LED_2_R`×`AUDIO_IN_L` 1, `ENC_A/B`×`AUDIO_IN_L` 1 each (1.23–1.34 mm), `ENC_A/B`×`AUDIO_IN_R` 1 each |
| `ENC_A` vs `+3V3_A` (rail) | 0.261 mm | 9.4 mm | 9.4 mm | 1 |
| `USB_OTG_FS_ID` vs `+3V3_A` | 0.383 mm | 0.7 mm | 0.7 mm | 1 |
| `MIDI_IN_B` vs `+3V3_A` | 0.548 mm | 0 | 2.5 mm | 0 |
| `N$3` (LED1 green cathode) vs `POT_1` | 0.711 mm | 0 | 5.4 mm | 1 |
| `LED_1_G` vs `POT_1` | 0.691 mm | 0 | 1.5 mm | 0 |
| `USART1_RX` vs anything analogue | > 1 mm | 0 | 0 | 0 |
- **No same-layer parallel run between a digital line and an audio signal within 1.0 mm.** The closest pairings are rail-adjacent (`ENC_A` along the 0.41 mm `+3V3_A` rail for 9.4 mm — the rail is low-impedance, and the encoder line toggles at hand speed) and the knob wiper `POT_1` beside the LED1 green line (0.7 mm, 5.4 mm; 120 Hz software PWM edges at 0.3 mA through 1 k — negligible into a 10 k wiper with 32× ADC oversampling). **PASS**, versus rev 3's `/USART1_RX` 49 mm at 0.41 mm beside `AUDIO_IN_L` (R3-P5-04): the Pod places the opto U15 and the MIDI jack J1 at the top-right, away from J2/J3, so the UART never meets the audio lines.

## 6. LED lines (common anode on `+3V3_D`, GPIO sinks through 1 k)
| Channel | Seed pin (STM32) | GPIO → R | R → LED cathode (net) | Timer channel on this pin (from memory, DS12556 AF table — unverified) |
|---|---|---|---|---|
| LED1 R | 27 (PC1) | 3.6 mm / 1 via (R6) | 49.4 mm / 3 vias (`N$2`) | none |
| LED1 G | 26 (PA6) | 4.5 / 1 (R7) | 42.5 / 3 (`N$3`) | TIM3_CH1, TIM13_CH1 |
| LED1 B | 25 (PA7) | 7.5 / 1 (R8) | 46.9 / 3 (`N$4`) | TIM3_CH2, TIM14_CH1, TIM1_CH1N |
| LED2 R | 24 (PB1) | 42.8 / 3 (R9) | 6.2 / 1 (`N$5`) | TIM3_CH4, TIM1_CH3N |
| LED2 G | 31 (PA1) | 10.2 / 1 (R10) | 18.4 / 1 (`N$6`) | TIM2_CH2, TIM5_CH2, TIM15_CH1N |
| LED2 B | 30 (PA4) | 7.1 / 1 (R11) | 21.1 / 1 (`N$7`) | none (DAC1_OUT1) |
- All twelve nets are clean 2-node nets, 0.203/0.254 mm. `+3V3_D` reaches LED1.A in 26.3 mm and LED2.A in 45.6 mm from the Seed (0.41 mm rail). The 1 k resistors sit at the Seed end for LED1 and at the LED end for LED2 — inconsequential.
- **PWM:** libDaisy `Led::Update()` is **software PWM** (`pwm_ += 120.f / samplerate_`, i.e. a 120 Hz ramp compared against a cubed brightness, driven from the audio callback); hardware timer capability is not used, so the two pins without a timer channel (PC1, PA4) do not matter. The STM32 timer-AF assignments above are from memory and only informational.
- Drive level: (3.3 V − V_f)/1 k ≈ 1.3 mA (red, V_f ≈ 2.0 V) / ≈ 0.3 mA (green/blue, V_f ≈ 3.0 V) — low; electrical disposition and the CLVBA-FKA V_f belong to Pass 2 (JUDGMENT note only). No 3.3V-only-pin concern: the GPIO never sees more than `+3V3_D`.
- **PASS** (signal side). Trey's rev 3 instead drives +9 V through NPN low-side stages; the GPIO→1 k→base nets are 33–51 mm there vs 4–43 mm here.

## 7. Encoder and buttons
| Net | Part pad → Seed pin | Length | Vias | Width | Filtering / pull-up |
|---|---|---|---|---|---|
| `ENC_A` | ENC_1.A → 33 (PD11) | 62.3 mm | 4 | 0.203 (51.8) + 0.254 (10.4) | none; libDaisy internal PULLUP |
| `ENC_B` | ENC_1.B → 32 (PA0) | 62.8 mm | 4 | 0.203 (54.1) + 0.254 (8.8) | none; internal PULLUP |
| `ENC_CLICK` | ENC_1.E (sym pin 2) → 14 (PB6) | 38.6 mm | 2 | 0.254 | none; internal PULLUP (Switch default) — **and USART1_TX AF after `InitMidi()`, Pass 3 DP-P3-08** |
| `TAC_SWITCH_1` | S3.1/S3.2 → 34 (PG9) | 42.9 / 38.0 mm | 2 | 0.203/0.254 | none; internal PULLUP |
| `TAC_SWITCH_2` | S2.1/S2.2 → 35 (PA2) | 43.1 / 38.3 mm | 2 | 0.254/0.203 | none; internal PULLUP |
- Encoder common `C` and pad `D` (click return) on GND; switch pads 3/4 on GND; both switch pads 1/2 are paralleled on the net (4.8 mm link). A/B matched to 0.5 mm. No RC debounce anywhere — libDaisy debounces in software (`Encoder::Debounce` 1 kHz shift register, `Switch::Debounce`). **PASS**, same scheme as Trey's rev 3 (ENCL on the same pins 32/33 as the Pod's encoder; rev-3 clicks 170.6/190.6 mm vs 38.6 mm here).

## 8. Knobs
| Net | VR wiper → Seed pin | Length | Vias | Width | RC |
|---|---|---|---|---|---|
| `POT_1` | VR_1.2 → 28 (PC4, ADC6) | 32.3 mm | 1 | 0.203 | none |
| `POT_2` | VR_2.2 → 22 (PC0, ADC0) | 32.2 mm | 1 | 0.203 | none |
- Pot ends: pin 1 GND, pin 3 `+3V3_A` (the analogue rail — the ADC reference domain on the Seed), 10 k linear (BOM "P-10K-B-R", B = linear — correct for a parameter knob). No wiper cap, no series R; libDaisy samples with 32× oversampling (`seed.adc.Init` comment). `+3V3_A` path Seed → VR_1.3 is 59.6 mm, → VR_2.3 46.6 mm at 0.41 mm. **PASS.** Trey's rev 3 moved pin 28 to `/DC_SPI` and pin 22 to `/ENCL_CLICK`; his knob set is on other ADC pins (not re-derived here).

## 9. Comparison — Pod Rev5 reference vs WavetableController rev 3
| Item | Daisy Pod Rev5 (this pass) | WavetableController rev 3 (`analysis/rev3/PASS5_SIGNALS.md`, `PASS3_CONNECTIVITY.md`) | Reading |
|---|---|---|---|
| Board | 90 × 52 mm, 2-layer | 165 × 102 mm, 2-layer | rev 3 is 3.6× the area; every run below scales with it |
| SD D0–D3/CMD/CK | 10.6–20.3 mm, 1–3 vias, 0.203/0.254 mm; skew ≤ 9.7 mm (55 ps); 47 k on DAT/CMD, none on CLK; no local cap at P1 (70 mm) | 24–41 mm, 2–4 vias, 0.3 mm; skew 16.8 mm (95 ps); same 47 k scheme | both PASS; rev 3 2× longer, still negligible at SDMMC |
| USB FS pair | 57.9/59.3 mm, **0 vias**, 1.4 mm skew, coupled 47.8 mm at 0.127 mm gap, 0.203 mm; TVS 7.9 mm from the connector | 130.2/130.6 mm, **9/11 vias**, 0.4 mm skew, 0.3 mm | both PASS; rev 3 tidier in skew, far worse in vias (R3-P5-03) |
| MIDI IN | 220 Ω + H11L1 + NSR1020 antiparallel + 270 Ω pull-up; 0 Ω polarity jumpers (Type A fitted) | identical chain (R5 220 Ω, U1 H11L1, D1, R6 270 Ω; R2/R3 0 Ω) | inherited verbatim |
| MIDI OUT | **none** (pin 14 = encoder click) | J3 with 10 Ω / 33 Ω from pin 14 USART1_TX | rev 3 adds the function and thereby avoids DP-P3-08 |
| Audio line runs IN L / OUT L / OUT R | 56.3 / 44.3 / 51.8 mm, 0.254 mm, 0–6 vias | 140.9 / 205.6 / 227.6 mm, 0.3 mm, 3–8 vias | rev 3 2.5–4.6× longer (R3-P5-06, judgment only) |
| Headphone chain | pot → 470 nF → 22 k → TPA6110A2 (33 k, ×1.5) → 100 µF → jack; 100 nF at 3.4 mm; **no ≥ 10 µF** | same values; 0.1 µF at 5.5 mm; **no ≥ 10 µF** (F-031) | F-031 is inherited from the Pod |
| Digital beside audio | **no** same-layer parallel run ≤ 1.0 mm; closest crossing 1.03 mm | `/USART1_RX` 49 mm at 0.41 mm and `/USART1_TX` 26 mm at 0.45 mm beside `AUDIO_IN_L` (R3-P5-04) | Pod keeps MIDI top-right, away from the audio jacks — the layout cue rev 3 should copy |
| Encoder wiring | one encoder: A/B on pins 33/32 (PD11/PA0), click on pin 14 (PB6 = USART1_TX, conflict with libDaisy MIDI TX), 62 mm A/B, no RC, internal pull-ups | two encoders: ENCL A/B on 33/32 (same as Pod), click on 22 (PC0); ENCR A/B on 12/13 (Pod I2C header pins), click on 29 (PA5); 170/190 mm clicks, no RC | rev 3 keeps the Pod's A/B pins and moves the click off the UART pin |
| SPI1 (pins 8/9/10/11) | all four only to the DNI header P2 | 8 CS, 9 SCLK, 11 MOSI → OLED J8; 10 = `/TAC_SHIFT_R` GPIO; DC on 28, RES on 1 | rev 3 uses the Pod's expansion pins exactly as intended |
| I2C1 (pins 12/13) | DNI header P2 | `/ENCR_A`, `/ENCR_B` | rev 3 re-purposed the I2C pins as GPIO once the I2C OLED was dropped |
| USB power | data-only (VBUS → TVS only); board powered via the Seed's own USB; VIN only on P2 | data-only (USB-C), powered from a 9 V barrel into `/DSY_VIN` | Trey's data-only USB mirrors the Pod |
| Card detect | SWA open / SWB GND | identical (F-022) | inherited |
| LEDs | common anode on `+3V3_D`, GPIO sinks via 1 k, software PWM | NPN low-side from +9 V via 300 Ω, GPIO → 1 k → base (polarity flagged R3-P3-09) | rev 3 diverges here, and that is where its LED problems live |

## Findings (Daisy Pod, Pass 5)
| ID | Class | Status | Finding | Evidence | Source |
|---|---|---|---|---|---|
| DP-P5-01 | PASS | confirmed | SD interface 10.6–20.3 mm, 0.2/0.25 mm, 1–3 vias, data-clock skew ≤ 51 ps; 47 k pull-ups on DAT0–3/CMD at 3.7–5.7 mm from P1, none on CLK | §1 | SDMMC period vs 5.64 ps/mm |
| DP-P5-01b | JUDGMENT | confirmed | No decoupling capacitor at the SD socket: P1.VDD is 70.3 mm from the only `+3V3_D` cap (C11) and 37.7 mm from the Seed pin → Pass 2 | §1 | — |
| DP-P5-02 | PASS | confirmed | USB FS pair 57.9/59.3 mm (1.4 mm = 8 ps skew), 0 vias, coupled 47.8 mm at 0.127 mm, through U7 USBLC6-2 (1→6, 3→4) 7.9 mm from P5; no impedance control (normal for FS, 2-layer) | §2 | USB FS bit 83 ns |
| DP-P5-03 | PASS | confirmed | MIDI IN = standard 220 Ω / H11L1 / antiparallel diode / 270 Ω pull-up receiver, Type A with the fitted 0 Ω pair; 0.203 mm traces; no MIDI OUT exists on the Pod | §3 | RP-054 mapping from memory (midi.org unreachable); schematic |
| DP-P5-04 | PASS | confirmed | Audio: TRS jack wiring tip = L / ring = R; line runs 44–56 mm, 0.254 mm; headphone chain Seed → P8 → 470 nF → 22 k → TPA6110A2 (gain 1.5) → 100 µF → J4; SHUTDOWN = GND = normal operation; Eq. 6/8 satisfied; output corner 50 Hz @ 32 Ω (better than TI's 73 Hz example) | §4 | SLOS314B l.100, 1040–1090 (fetched) |
| DP-P5-05 | JUDGMENT (datasheet-cited) | confirmed | TPA6110A2 `+3V3_A` has the 100 nF at 3.4 mm but no ≥ 10 µF electrolytic near the amplifier (SLOS314B l.1026–1030) — **the Pod is the origin of Trey's F-031** | §4 | SLOS314B (fetched) |
| DP-P5-06 | PASS | confirmed | No digital trace runs parallel to any audio signal within 1.0 mm on the same layer; 3 opposite-layer crossings ≥ 1.03 mm; only rail-adjacent pairings (`ENC_A` 9.4 mm at 0.26 mm beside `+3V3_A`) and `POT_1` 5.4 mm at 0.71 mm beside the LED1-G cathode line | §5 | `proximity.py`, 3W rule-of-thumb |
| DP-P5-07 | PASS | confirmed | LED lines: common-anode sink topology, GPIO→1 k 3.6–42.8 mm, R→LED 6–49 mm, all 2-node; software PWM at 120 Hz in libDaisy so timer pins are irrelevant; ~1.3/0.3 mA drive (V_f assumed) → Pass 2 | §6 | libDaisy `led.cpp`; STM32 AF table from memory |
| DP-P5-08 | PASS | confirmed | Encoder A/B 62.3/62.8 mm (0.5 mm matched), click 38.6 mm; buttons 43 mm; no RC, no external pull-ups (libDaisy internal PULLUP + software debounce). Click-pin conflict carried as Pass 3 DP-P3-08 | §7 | libDaisy `encoder.cpp`, `switch.h` |
| DP-P5-09 | PASS | confirmed | Knob wipers 32.3/32.2 mm, 0.203 mm, 1 via, no RC; pots across GND/`+3V3_A` (analogue rail), linear taper appropriate | §8 | BOM "P-10K-B-R" |
| DP-P5-10 | PASS (comparison) | confirmed | Rev 3 inherits every Pod signal topology (SD, USB, MIDI IN, headphone chain, encoder A/B pins, no-RC switches, data-only USB, card-detect quirk, missing 10 µF) and differs only where it adds (MIDI OUT, SPI OLED, second encoder) or diverges (9 V LED drivers); its longer runs and the UART-beside-audio finding are consequences of board size and jack placement, not of the reference | §9 | rev-3 reports |
