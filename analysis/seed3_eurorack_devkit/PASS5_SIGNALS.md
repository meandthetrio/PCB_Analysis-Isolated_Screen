# Seed3 Eurorack Dev Kit Rev3 — Pass 5: Signal-Specific Report
**Date:** 2026-10-12 · **Truth checked:** `reference/electrosmith/seed3_eurorack_devkit/Rev3/Seed3-DevKit-Eurorack-Rev3.kicad_pcb` (KiCad 10 board, filled GND pours) read with `pcbnew` 10.0.7 (`pcb_export.py` → `euro/pcb.json`), plus the schematic netlist for topology and values. Board 141.9 × 128.5 mm (28 HP), 2-layer, 1.6 mm; Seed A1 at (52.8, 116.5) bottom-left, jacks along the top/right edge.
**Tools** (`analysis/seed3_eurorack_devkit/scripts/`): `net_geometry.py` (pad-to-pad copper path, widths, vias, islands; `ALL` option), `proximity.py` (same-layer edge gap, parallel run ≤ GAP, opposite-layer crossings), `prox_lists.py` (aggressor/victim net classification by name), `chain_walk.py`, `sd_budget.py` (SD length/via budget incl. the Seed 3's on-module figures).
**Thresholds / sources:** Seed 3 datasheet `Daisy_Seed3_datasheet.txt` SDMMC guidelines l.1795–1798 ("Maximum difference in trace length should be kept below 10mm", "maximum trace length must be below 120 mm", "number of vias between layers should be the same for each of the DATA and CMD lines") and the Seed 3 on-module SD table l.1803–1811 (CK 4.853 mm/0 via, CMD 9.767/1, D0 13.94/2, D1 14.942/2, D2 14.224/1, D3 17.586/1); 47 k pull-ups l.1812; MIDI l.1930–1962; USB Fig 1.3 l.446; trace delay **5.64 ps/mm** (rev-3 Pass 5 derivation, 0.3 mm microstrip on 1.5 mm FR-4; the kit's 0.254 mm traces change ε_eff < 2 %); USB 2.0 FS bit 83 ns; libDaisy `led.cpp` (120 Hz software PWM), `ctrl.cpp`, `gatein.cpp`, `switch3.h`; rev-3 figures from `analysis/rev3/PASS5_SIGNALS.md`; Pod figures from `analysis/daisy_pod/PASS5_SIGNALS.md`. STM32 figures quoted from memory are marked.

## Headline
- **The SD routing is budgeted against the Seed 3's own on-module table and meets all three datasheet guidelines with margin:** kit + module totals 28.0–36.0 mm (max 36.0 < 120), spread **8.0 mm < 10 mm**, and **every DATA and CMD line totals exactly 2 vias** (kit vias 0/0/1/1/1 chosen to complement the module's 2/2/1/1/1). This is the first reference in the set where the via rule is demonstrably applied. The same SD + USB + Seed block is reused unchanged on the Pedal kit (identical numbers to 0.1 mm).
- **USB FS pair:** 29.3 / 32.0 mm, skew 2.7 mm = 15 ps, coupled 24.6 mm at 0.196 mm edge gap, TVS 8.0 mm from the receptacle; 2 vias on D+ vs 0 on D− (cosmetic asymmetry).
- **Proximity is nearly clean:** one same-layer pairing inside 0.5 mm — `MIDI_RX` beside the filtered `CV_3_ADC` node for **7.3 mm at 0.381 mm** (F.Cu, next to U2/C16) — versus rev 3's 49 mm at 0.41 mm beside an unfiltered audio input (R3-P5-04). The `+3V3` rail runs 21.5 mm at 0.46 mm beside `DAC_CV_1` on B.Cu (rail, low impedance). **No digital trace comes within 1.0 mm of any `CODEC_*` audio line.**
- **No local decoupling at the SD socket** (only `+3V3` capacitor C1 100 nF sits at the opto, 124 mm of copper from U7.VDD; Seed pin 38 is 30.7 mm away) — the Pod's DP-P5-01b again, so it is Electrosmith house style, not an omission peculiar to one board.
- Audio/CV/gate signal conditioning is all op-amp-buffered at ±12 V with 100 Ω series into/out of the Seed; the Seed never sees a jack directly. Line runs to the Seed are 83–106 mm (audio), 20–30 mm (CV ADC), 40 mm (DAC).

## 1. SD interface (U7 TF-01A ↔ Seed pins 2–7) — `sd_budget.py`
| Net | Seed pin → U7 pad | Kit path | Kit vias | Seed 3 on-module (datasheet l.1803–1811) | **Total** | **Total vias** | Pull-up (47 k → `+3V3`) | Pull-up stub from the Seed pad |
|---|---|---|---|---|---|---|---|---|
| `SDMMC_CK` | 7 → 5 | 26.7 mm | 0 | 4.853 mm / 0 | **31.6 mm** | 0 | none (correct, l.1812) | — |
| `SDMMC_CMD` | 6 → 3 | 18.2 mm | 1 | 9.767 / 1 | **28.0** | 2 | R52 | 2.6 mm |
| `SDMMC_D0` | 5 → 7 | 15.5 mm | 0 | 13.94 / 2 | **29.4** | 2 | R53 | 2.7 mm |
| `SDMMC_D1` | 4 → 8 | 14.6 mm | 0 | 14.942 / 2 | **29.5** | 2 | R54 | 2.7 mm |
| `SDMMC_D2` | 3 → 1 | 18.3 mm | 1 | 14.224 / 1 | **32.5** | 2 | R50 | 2.7 mm |
| `SDMMC_D3` | 2 → 2 | 18.4 mm | 1 | 17.586 / 1 | **36.0** | 2 | R51 | 2.7 mm |
- Max total 36.0 mm (< 120 mm ✓); max difference 36.0 − 28.0 = **8.0 mm** (< 10 mm ✓) = 45 ps; DATA + CMD vias **2/2/2/2/2 (equal ✓)**. On the kit copper alone the clock is the longest line (26.7 vs 14.6–18.4 mm) — it compensates the module's short 4.85 mm clock stub; the kit's via placement (0 on D0/D1, 1 on D2/D3/CMD) exactly complements the module's. All 0.254 mm (10 mil). Same-layer gaps: `SDMMC_CK`–`SDMMC_D0` 0.239 mm but **0 mm parallel** (a crossing-style approach), CK–CMD 0.814 mm; every net a single island, `stubs=[]`.
- Pull-ups sit **at the Seed end** (2.6–2.7 mm stubs from A1), not at the socket — electrically irrelevant at 36 mm.
- **Decoupling at U7.VDD (pad 4):** the only capacitor on `+3V3` is C1 100 nF at the MIDI block (96.5, 65.9), 10 mm from U11, **124.0 mm** of 0.406 mm copper from U7.4; A1.38 → U7.4 is 30.7 mm. No capacitor at the socket (JUDGMENT EU-P5-01b → Pass 2; identical to the Pod and the Pedal).
- Card detect not wired (Pass 3 EU-P3-05).
- **PASS** on the interface. **Rev 3 cross-check:** Trey's on-board lengths are 24.2–41.0 mm with 2–4 vias (R3-P5-02). Adding a Seed's on-module lengths — if the Seed Rev 7 is similar to the Seed 3 table — gives D3 ≈ 41.8 mm vs D0 ≈ 54.9 mm, a 13 mm spread against the 10 mm guideline, and 2–4 kit vias + 1–2 module vias are unequal. The guideline is published for the Seed 3 only; re-check when rev 3 is re-targeted to a Seed 3 (EU-P5-01c, JUDGMENT).

## 2. USB Full-Speed pair (J7 USB4110GFA → U14 USBLC6-2SC6 → Seed pins 36/37)
| Net | Path | Length | Vias | Width |
|---|---|---|---|---|
| `/Daisy/USB_IN_P` | J7.A6 → U14.1 (B6 tied, 3.8 mm) | 5.9 mm | 0 | 0.254 |
| `/Daisy/USB_IN_N` | J7.A7 → U14.3 (B7 tied through 2 vias, 7.8 mm) | 6.2 mm | 2 (on the A7/B7 tie) | 0.254 |
| `/Daisy/USB_OTG_HS_N` | U14.4 → A1.36 | 29.3 mm | 0 | 0.254 |
| `/Daisy/USB_OTG_HS_P` | U14.6 → A1.37 | 32.0 mm | 2 | 0.254 |
| `/Daisy/+5V_USB` | J7 VBUS → U14.5 | 17.9 / 13.2 mm | 2 | 0.406 |
| `Net-(J7-CC1/CC2)` | J7.A5/B5 → R1/R2 5k1 | 5.1 / 5.2 mm | 0 | 0.254 |
- Pair mismatch on the Seed side **2.7 mm = 15 ps** (0.02 % of an 83 ns FS bit); D+/D− run **parallel for 24.6 mm at a 0.196 mm (7.7 mil) edge gap** — a deliberately coupled pair; D+ carries 2 vias where D− has none (JUDGMENT, cosmetic at 12 Mb/s). No impedance control (2-layer, 0.254 mm traces), normal for FS. U14 at (64.0, 76.7) is **8.0 mm** from J7 at (56.0, 76.3), stubs 5.9/6.2 mm — correct TVS placement. VBUS serves only as the clamp reference (Pass 3 EU-P3-04).
- **PASS.** Rev 3: 130.2/130.6 mm, 9/11 vias, 0.4 mm skew; Pod: 57.9/59.3 mm, 0 vias, 1.4 mm skew.

## 3. MIDI (TRS, three jacks on the right edge x = 110.5, y = 41–84)
| Segment | Length | Vias | Width |
|---|---|---|---|
| IN ring → R4 220 R (`MIDI_IN_4`) | 15.7 mm | 0 | 0.254 |
| R4 → U11.1 ‖ D3 (`Net-(D3-K)`) | 2.9 / 2.2 mm | 0 | 0.254 |
| IN tip → U11.2 (`MIDI_IN_5`), D3 tapped at 20.5 mm | 25.9 mm | 0 | 0.254 |
| IN sleeve → C47 100 nF | 2.9 mm | 0 | 0.254 |
| U11.4 → R3 270 R / → A1.15 / → R29 (thru) (`MIDI_RX`, 74.6 mm total) | 2.4 / 58.7 / 15.7 mm | 0 | 0.254 |
| A1.14 → R59 10 R (`MIDI_TX`) → OUT tip | 60.9 mm + 4.3 mm | 3 | 0.254 |
| `+3V3` → R10 10 R → OUT ring | 17.0 mm | 0 | 0.254 |
| R29 → THRU tip / R6 → THRU ring | 9.5 / 9.9 mm | 0 | 0.254 |
- Receiver = the standard 5 mA current-loop H11L1 stage with antiparallel NSR1020 (D3) across the opto LED and a 270 R pull-up on the Schmitt output; **part for part the Pod's and rev 3's MIDI IN**. OUT/THRU are 10 R/10 R (Pass 3 EU-P3-10). C1 100 nF decouples U11.6.
- `MIDI_RX` runs 0 vias from U11 to the Seed and passes the CV op-amp U2 on the way (§5). **PASS.**

## 4. Audio, CV and gate paths
**Audio (TL072 U1 in, U15 out, ±12 V):**
| Net | Path | Length | Vias | Width |
|---|---|---|---|---|
| `Net-(J_AUDIO_IN_L1-PadTIP)` | jack tip → R61 100 k (R-jack NORM tapped at 36.3 mm) | 36.6 mm | 0 | 0.254 |
| `Net-(J_AUDIO_IN_R1-PadTIP)` | jack tip → R64 100 k | 41.3 mm | 0 | 0.254 |
| U1 stages | R61/R64 → U1B/U1A inverting, R62/R65 10 k ‖ C4/C17 330 pF (f_c 48 kHz), gain −0.1 | 5.3 mm nets | 0 | 0.254 |
| `/Daisy/CODEC_IN_L` / `_R` | R63/R66 100 R → A1.16 / A1.17 | 82.7 / 90.1 mm | 2 / 2 | 0.254 |
| `/Daisy/CODEC_OUT_L` / `_R` | A1.18 / A1.19 → R67/R68 10 k | 106.2 / 90.0 mm | 2 / 2 | 0.254 |
| U15 stages | inverting, R73/R78 100 k ‖ C21/C22 33 pF (f_c 48 kHz), gain −10 | 5.5–6.1 mm nets | 0 | 0.254 |
| `Net-(J_AUDIO_OUT_L1/R1-PadTIP)` | R79/R80 100 R → jack tips | 54.1 / 24.9 mm | 0 | 0.254 |
- Levels: 10 Vpp Eurorack in → 1.0 Vpp at the Seed (max 3.6 Vpp, datasheet l.126); Seed 0 dBFS 1 Vrms (2.83 Vpp) × 10 → clips at the TL072 rails ≈ ±10.5 V ⇒ ≈ 20 Vpp, matching the README "10Vpp nominal … headroom up to about 20Vpp". Two inversions ⇒ in-phase pass-through. 100 kΩ in / 100 Ω out as published. The Seed's codec pins see only the op-amp outputs through 100 R (in) and drive 10 k (out) — the 83–106 mm runs are low-impedance-driven and 1 nF-free, so trace length is irrelevant at audio.
**CV in (U2 MCP6004 on `+3V3_A`):** jack tip → R33/R37/R41/R46 100 k runs of **60.1 / 69.9 / 74.5 / 103.9 mm** (1–2 vias; high-impedance source side, filtered later); the summing nodes `Net-(U2x--)` are 7.2–7.4 mm; the ADC nets `/Daisy/CV_1…4_ADC` are **26.7 / 19.7 / 24.6 / 30.3 mm, 0 vias**, each carrying the 1 nF (C14–C18) at the op-amp (1.5 mm) and 33 k feedback. f_c = 1/(2π·33 k·1 nF) = **4.8 kHz** anti-alias/anti-noise at the Seed pin. Transfer −0.33·V + 1.65 V (Pass 3 §7). `-10V_REF` (LM4040) net 56.4 mm, 2 vias, C13 100 nF 11.7 mm from U3.
**CV out (U13 TL072):** `/Daisy/DAC_CV_1/2` A1.30/29 → U13.3/5 **40.0 / 39.4 mm, 1 via** (short 0.2 mm necks of 5.4/1.8 mm at the Seed); feedback nets 3.9–4.3 mm; R55/R60 100 R → jack tips 25.5 / 35.6 mm, 1 via. Gain 1.517 → 0–5 V.
**Gate in:** jack tip → R17/R24 100 k 12.8 / 11.0 mm; base/collector nets 3.6–3.8 mm; `GPIO_GATEIN_1/2` R23/R31 100 R → A1.11 / A1.28 **47.9 / 69.7 mm, 2 vias** — a 10 k-pulled logic line, no issue.
- **PASS.** Rev 3 for comparison takes the jacks straight to the Seed (AUDIO_IN 140.9 mm, OUT 205.6/227.6 mm) with no buffer stage; the kit's longer buffered runs are a different (and more robust) architecture rather than a like-for-like number.

## 5. Proximity of digital to analogue (`proximity.py`, lists from `prox_lists.py`)
Aggressors (44 nets): all `SDMMC_*`, USB, `MIDI_*` + jack-side MIDI nets, `LED_*` + LED anode nets, `TAC_*`, `TOG_*`, `MUX_CTRL_*`, `GPIO_GATEIN_*` + Q1/Q2 nets, CC nets, `+3V3`. Victims (45 nets): `CODEC_*`, `CV_n_ADC`, `POT_1–8`, `POT_MUX`, `DAC_CV_n`, all jack-tip nets, every op-amp summing/output net, `+3V3_A`, `-10V_REF`.
| Pair | Layer | Same-layer min edge gap | Parallel ≤ 0.5 mm | ≤ 1.0 mm | Crossings |
|---|---|---|---|---|---|
| `MIDI_RX` vs `/Daisy/CV_3_ADC` | F.Cu, x ≈ 94.6 vs 94.0, y 86–94 (beside U2 / C16) | **0.381 mm** | **7.3 mm** | 8.7 mm | 0 |
| `+3V3` (0.406 mm rail) vs `/Daisy/DAC_CV_1` | B.Cu, y ≈ 105 | 0.464 mm | 21.5 mm | 21.5 mm | 1 |
| `+3V3` vs `+3V3_A` | — | 0.864 mm | 0 | 16.5 mm | 2 |
| `Net-(J_MIDI_OUT1-NORM)` (3V3 via 10 R, static) vs `Net-(J_CV_IN_1-PadTIP)` | — | 0.952 mm | 0 | 0.9 mm | 0 |
| any digital net vs any `CODEC_*`, `POT_*`, `POT_MUX`, audio-jack or op-amp net | — | > 1.0 mm | 0 | 0 | single crossings only (`+3V3`×`POT_1–8`, `MIDI_TX`×`POT_5–8`, `MUX_CTRL_*`×`CV_3/4_ADC`, `-10V_REF`) |
- The `MIDI_RX`/`CV_3_ADC` run is the filtered ADC node (33 k ‖ 1 nF, 4.8 kHz) of a CV input beside a 31.25 kbaud line with 270 R-pull-up CMOS edges, 7.3 mm long: coupling into a 1 nF node is negligible (JUDGMENT EU-P5-05, low). It is the only same-layer digital/analogue pairing inside 0.5 mm on the board — against rev 3's `/USART1_RX` 49 mm at 0.41 mm beside the unfiltered `AUDIO_IN_L` (R3-P5-04). **PASS** overall; the kit keeps the MIDI block (U11 at (97.8, 56.0)) above the CV op-amp (U2 at (86.4, 85.6)) and away from the audio stages (U1/U15 at x ≈ 160–172, y 142).

## 6. LED lines (common cathode, GPIO sources through 2 k; libDaisy `invert = false`)
| Channel | Seed pin (STM32) | GPIO → R | R → LED anode | Timer on this pin (datasheet Table 2) |
|---|---|---|---|---|
| LED1 R | 10 (PB4) | 14.8 mm / 1 via (R40) | 5.9 mm (`Net-(LED1-RA)`) | none listed |
| LED1 G | 35 (PA2) | 33.4 mm / 2 vias (R25) | 15.2 mm | TIM2_CH3 / TIM5_CH3 |
| LED1 B | 9 (PG11) | 15.0 mm / 1 via (R44) | 11.6 mm | LPTIM1_IN2 |
| LED2 (mono) | 12 (PB8) | 29.0 mm / 2 vias (R43) | 7.5 mm | TIM16_CH1 / TIM4_CH3 |
- All eight nets are clean 2-node nets at 0.254 mm. libDaisy `Led::Update()` is **software PWM at 120 Hz** (`led.cpp`), so timer capability is unused. Drive ≈ (3.3 − V_f)/2 k ≈ 0.65 mA (red, V_f ≈ 2.0 V) / ≈ 0.15 mA (G/B, V_f ≈ 3.0 V; V_f values from memory) — dim by design, electrical disposition → Pass 2. No 3.3 V-only-pin concern (GPIO sources ≤ 3.3 V). **PASS** (signal side). Pod: common anode sink via 1 k; rev 3: NPN low-side from 9 V.

## 7. Switches and toggles
| Net | Part pad → Seed pin | Length | Vias | Width | Pull-up / RC |
|---|---|---|---|---|---|
| `TAC_SW1` | SW1.1/.2 → 1 (PB12) | 59.8 / 66.3 mm | 1 | 0.254 | none; libDaisy `Switch` default `PULLUP`, `POLARITY_INVERTED` |
| `TAC_SW2` | SW2.1/.2 → 27 (PC1) | 61.4 / 67.9 mm | 2 | 0.254 | same |
| `TOG_SW3_A` | SW3.1 → 34 (PG9) | 93.4 mm | 2 | 0.254 | `Switch3` `PULLUP` on both pins |
| `TOG_SW3_B` | SW3.3 → 8 (PG10) | 86.9 mm | 2 | 0.254 | same |
| `TOG_SW4` | SW4.1 → 13 (PB9) | 95.0 mm | 0 | 0.254 | `Switch` `PULLUP` |
- Switch commons (SW1/SW2 pads 3/4, SW3 pin 2, SW4 pin 2) on GND; both tactile contacts paralleled on the net (6.5 mm link). No RC, no external pull-ups anywhere — the STM32 internal pull-up (≈ 40 kΩ typical, **from memory**) and libDaisy's software debounce carry it. **PASS**, same scheme as the Pod and rev 3 (rev-3 clicks 170/190 mm).

## 8. Potentiometers (CD4051 mux) and rails
| Net | Path | Length | Vias | Width |
|---|---|---|---|---|
| `POT_1 … POT_8` | VRn wiper → U12 X-input | 63.2 / 82.7 / 100.4 / 116.3 / 55.3 / 63.2 / 90.2 / 99.9 mm | 1 / 1 / 1 / 3 / 2 / 2 / 2 / 2 | 0.254 |
| `/Daisy/POT_MUX` | U12.3 COM → A1.22 | 15.3 mm | 0 | 0.254 |
| `/Daisy/MUX_CTRL_A/B/C` | A1.31/32/33 → U12.11/10/9 | 37.9 / 41.7 / 45.3 mm | 2 each | 0.254 |
| `+3V3_A` | A1.21 → C6 (U12 VDD) 16.5 mm; → VR5 60.8, VR7 96.4, VR3 164.4, VR1 199.3 mm (daisy-chained along the pot row) | 249.6 mm total | 4 | 0.406 |
| `+3V3` | A1.38 → R50 (pull-ups) 12.6 mm, → U7.4 30.7 mm, → R10 93.7 mm, → C1 97.6 mm | 200.6 mm total | 6 | 0.406 / 0.254 |
- No wiper caps or series resistors (10 k linear pots on the analogue rail, libDaisy `SPEED_810CYCLES_5` conversion with 1 kHz control-rate smoothing). The three mux select lines toggle at the ADC scan rate and run 38–45 mm from the Seed to U12 with 2 vias each; they cross `CV_3/4_ADC` and `-10V_REF` once each on opposite layers (§5) — no parallel runs. **PASS.**

## 9. Comparison — Seed3 Eurorack Dev Kit vs WavetableController rev 3 vs Daisy Pod
| Item | Seed3 Eurorack Dev Kit Rev3 (this pass) | WavetableController rev 3 | Daisy Pod Rev5 | Reading |
|---|---|---|---|---|
| Board | 141.9 × 128.5 mm (28 HP), 2-layer | 165 × 102 mm, 2-layer | 90 × 52 mm, 2-layer | kit area ≈ 1.1× rev 3, 3.9× Pod |
| SD D0–D3/CMD/CK (board copper) | 14.6–26.7 mm, 0–1 via, 0.254 mm; **+ module = 28.0–36.0 mm, spread 8.0 mm, DATA/CMD vias 2/2/2/2/2** | 24.2–41.0 mm, 2–4 vias, 0.3 mm; spread 16.8 mm on-board | 10.6–20.3 mm, 1–3 vias, 0.2/0.25 mm; spread 9.7 mm | kit is the only one proven against the datasheet's 10 mm / equal-via rule; rev 3 would need re-checking with module lengths (EU-P5-01c) |
| SD pull-ups / CLK / local cap | 47 k at the Seed end on DAT/CMD, none on CLK; **no cap at U7** (124 mm to C1) | 47 k, none on CLK | 47 k, none on CLK; no cap at P1 (70 mm) | house style across all three |
| USB FS pair | 29.3/32.0 mm, 0/2 vias, 2.7 mm skew, coupled 24.6 mm @ 0.196 mm, TVS 8.0 mm from J7; CC 5k1 device, VBUS → TVS only | 130.2/130.6 mm, 9/11 vias, 0.4 mm skew | 57.9/59.3 mm, 0 vias, 1.4 mm skew, 47.8 mm @ 0.127 mm | all PASS; rev 3 via-heavy (R3-P5-03) |
| MIDI IN | TRS A; 220 R + H11L1 + NSR1020 + 270 R; sleeve via 100 nF; 0–26 mm | identical parts; DIN/TRS | identical parts, 0 R polarity jumpers | inherited everywhere |
| MIDI OUT / THRU | TRS A, **10 R / 10 R**, from pin 14; THRU from the opto output, 9.5/9.9 mm; `MIDI_TX` 60.9 mm 3 vias | 10 R / 33 R from pin 14; no THRU | none | rev 3 follows MMA CA-033, kit follows the Seed 3 datasheet |
| Audio runs to the Seed | buffered: CODEC_IN 82.7/90.1 mm, CODEC_OUT 106.2/90.0 mm (2 vias each), TL072 ×−0.1 / ×−10 | unbuffered: IN_L 140.9, OUT_L/R 205.6/227.6 mm | unbuffered: 44–56 mm | different architecture (kit is Eurorack-level) |
| CV / gate | 4 × CV via MCP6004 on `+3V3_A` (4.8 kHz LPF, 20–30 mm to ADC), 2 × gate via BJT, 2 × DAC out via TL072 ×1.517 | none | none | kit-only |
| Digital beside analogue (same layer ≤ 0.5 mm) | **`MIDI_RX` ∥ filtered `CV_3_ADC` 7.3 mm @ 0.381 mm**; `+3V3` rail ∥ `DAC_CV_1` 21.5 mm @ 0.464 mm; nothing ≤ 1.0 mm beside `CODEC_*` | `/USART1_RX` 49 mm @ 0.41 mm and `/USART1_TX` 26 mm @ 0.45 mm beside `AUDIO_IN_L` (R3-P5-04) | none ≤ 1.0 mm | kit and Pod keep MIDI away from audio; rev 3 does not |
| Pots | 8 × 10 k B on `+3V3_A` through CD4051 (55–116 mm to the mux, 15 mm mux → Seed), no RC | pots on ADC pins (not re-derived) | 2 × 10 k B direct, 32 mm, no RC | mux costs 3 GPIO, saves 7 ADC pins |
| Encoder | none | ENCL A/B 33/32, click 22; ENCR A/B 12/13, click 29; no RC | A/B 33/32, click 14 (= USART1_TX, DP-P3-08) | kit uses pins 12/13 for the mono LED and TOG_SW4, 22 for the pot mux, 29 for DAC 2 |
| SPI1 pins 8/9/10/11 | TOG_SW3_B, LED_B, LED_R, GATEIN_1 (plain GPIO) | CS, SCLK, `/TAC_SHIFT_R`, MOSI → OLED | DNI header | kit leaves no SPI; rev 3's OLED plan cannot be dropped onto the kit pinout |
| Pins 1 / 28 | TAC_SW1 / GATEIN_2 | `/RES_SPI` / `/DC_SPI` | USB ID / POT_1 | — |
| 3.3 V-only pins 24/25/28/29/30 | CV_2/CV_1 ADC (op-amp on 3V3_A), GATEIN_2 (10 k to 3V3), DAC 2/1 | LED lines / `/DC_SPI` / `/ENCR_CLICK` / LED | LED_2_R / LED_1_B / POT_1 / A7 hdr / LED_2_B | all bounded on all three |
| LEDs | common cathode, GPIO source via 2 k, 120 Hz software PWM | NPN low-side from 9 V via 300 R (R3-P3-09) | common anode, sink via 1 k | three different topologies |
| Power / USB power | ±12 V header, 3R3/100 µF π-filter to VIN (datasheet Fig 1.2); USB data-only | 9 V barrel, USB-C data-only | Seed's own USB; Pod USB data-only | data-only USB is universal in the family |
| Card detect | not wired (no free pin) | SWA open / SWB GND (F-022) | SWA open / SWB GND | only the Pedal kit wires it |

## Findings (Seed3 Eurorack Dev Kit Rev3, Pass 5)
| ID | Class | Status | Finding | Evidence | Source |
|---|---|---|---|---|---|
| EU-P5-01 | PASS | confirmed | SD interface meets the Seed 3 datasheet guidelines with the module included: totals 28.0–36.0 mm (< 120), spread 8.0 mm (< 10), DATA/CMD vias 2 each (equal); 47 k on DAT/CMD only; 0.254 mm; CK deliberately the longest kit line (26.7 mm) to offset the module's 4.85 mm stub | §1 | datasheet l.1795–1812; `sd_budget.py` |
| EU-P5-01b | JUDGMENT | confirmed | No decoupling capacitor at the SD socket: U7.VDD is 124 mm from the only `+3V3` cap (C1, at the opto) and 30.7 mm from Seed pin 38 → Pass 2; identical to the Pod (DP-P5-01b) and the Pedal (PD-P5-01b) | §1 | `net_geometry.py` |
| EU-P5-01c | JUDGMENT | plausible | Applied to rev 3, the same budget (board 24–41 mm + a Seed-class module table) would exceed the 10 mm spread and the equal-via rule; the rule is published for the Seed 3 only — re-run `sd_budget.py` with the Seed Rev 7 figures if rev 3 moves to a Seed 3 | §1 | rev-3 R3-P5-02 lengths |
| EU-P5-02 | PASS | confirmed | USB FS pair 29.3/32.0 mm, 2.7 mm = 15 ps skew, coupled 24.6 mm at 0.196 mm, TVS 8.0 mm from the receptacle; 2 vias on D+ vs 0 on D− (cosmetic); no impedance control (normal for FS) | §2 | USB FS 83 ns bit |
| EU-P5-03 | PASS | confirmed | MIDI IN receiver = Pod/rev-3 topology, 0–26 mm runs; `MIDI_RX` 74.6 mm 0 vias, `MIDI_TX` 60.9 mm 3 vias; THRU 9.5/9.9 mm from the opto output; OUT/THRU 10 R/10 R (EU-P3-10) | §3 | datasheet l.1930–1962 |
| EU-P5-04 | PASS | confirmed | Audio is op-amp buffered both ways (TL072 ±12 V, ×−0.1 in, ×−10 out, 48 kHz corners, 100 R series); Seed-side runs 82.7–106.2 mm, 2 vias; levels match the README (10 Vpp nominal, ≈ 20 Vpp clip); CV ADC nets 20–30 mm with 1 nF at the op-amp (4.8 kHz); DAC runs 40 mm; gate lines 48/70 mm behind 10 k pull-ups | §4 | netlist values; datasheet l.126 |
| EU-P5-05 | JUDGMENT | confirmed | One same-layer digital/analogue pairing ≤ 0.5 mm: `MIDI_RX` beside the filtered `CV_3_ADC` node 7.3 mm at 0.381 mm (F.Cu by U2/C16); `+3V3` rail beside `DAC_CV_1` 21.5 mm at 0.464 mm (B.Cu); nothing ≤ 1.0 mm beside any `CODEC_*`/pot/audio net. Far cleaner than rev 3's 49 mm at 0.41 mm beside `AUDIO_IN_L` | §5 | `proximity.py`, 3W rule-of-thumb |
| EU-P5-06 | PASS | confirmed | LED lines: common-cathode source topology, GPIO→2 k 14.8–33.4 mm, R→LED 5.9–15.2 mm, all 2-node; 120 Hz software PWM; ≈ 0.65/0.15 mA drive (V_f from memory) → Pass 2 | §6 | libDaisy `led.cpp` |
| EU-P5-07 | PASS | confirmed | Switches: tactile 60–68 mm, toggles 87–95 mm, 0–2 vias, no RC, no external pull-ups (internal PULLUP + software debounce) | §7 | libDaisy `switch.h`, `switch3.h` |
| EU-P5-08 | PASS | confirmed | Pots: 8 wipers 55–116 mm into the CD4051, mux→Seed 15.3 mm, selects 38–45 mm; pots across GND/`+3V3_A`; `+3V3_A` daisy-chained 199 mm to VR1 at 0.406 mm; no RC | §8 | BOM value `P-10K-B-R` |
| EU-P5-09 | PASS (comparison) | confirmed | The kit shares rev 3's SD pull-up scheme, USB TVS/data-only topology and MIDI IN receiver; it differs by buffering every jack, muxing the pots, using 10/10 Ω MIDI drive and keeping MIDI away from audio. Its pin plan consumes all 31 GPIO, so rev 3's OLED-on-SPI1 cannot coexist with the kit's assignments | §9 | rev-3 / Pod reports |
