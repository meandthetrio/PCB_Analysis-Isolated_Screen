# Seed3 Pedal Dev Kit Rev3 — Pass 5: Signal-Specific Report
**Date:** 2026-10-12 · **Truth checked:** `reference/electrosmith/seed3_pedal_devkit/Rev3/ES-Seed3-DevKit-Pedal-Rev3.kicad_pcb` (filled GND pours) via `pcbnew` 10.0.7 (`pcb_export.py` → `pedal/pcb.json`) + the schematic netlist. Board 197.0 × 100.0 mm (README "197mm × 100mm" ✓), 2-layer; Seed A1 at (52.8, 125.3) bottom-left, SD socket U7 at (58.3, 136.7), USB J7 at (56.0, 82.9), ¼" jacks along the top edge (y = 72.3), DIN MIDI jacks on the far right (x = 235), barrel jack top-centre (166.5, 69.1).
**Tools** (`analysis/seed3_pedal_devkit/scripts/`): `net_geometry.py` (`ALL`), `proximity.py`, `prox_lists.py`, `chain_walk.py`, `sd_budget.py`.
**Thresholds / sources:** Seed 3 datasheet SDMMC guidelines l.1795–1798 and module table l.1803–1811; 47 k l.1812; MIDI l.1930–1962; expression Fig 4.5 l.1762; trace delay 5.64 ps/mm (rev-3 derivation); USB FS bit 83 ns; libDaisy `led.cpp`, `switch.h`, `pedal_devkit.cpp`; rev-3 and Pod figures from their Pass 5 reports. Figures from memory are marked.

## Headline
- **The Seed + SD + USB block is the Eurorack kit's block, placed identically:** every SD and USB-receptacle-side number matches the Eurorack kit to 0.1 mm — so the SD routing meets the Seed 3 datasheet budget the same way (totals 28.0–36.0 mm, spread 8.0 mm, DATA/CMD vias 2 each) and the same missing socket decoupling applies (C1 100 nF now **240 mm** away at the far-right opto).
- **USB FS pair 37.5 / 43.4 mm, 0 vias on both lines, 5.9 mm = 33 ps skew, coupled 33.1 mm at 0.196 mm.**
- **Proximity is the cleanest of the three references: no digital trace runs within 1.0 mm of any analogue net on the same layer**, despite `MIDI_TX`/`MIDI_RX` being 200 / 210 mm long (DIN jacks on the opposite edge from the Seed). Only the `+3V3` rail runs beside `+3V3_A` (0.51 mm, 102 mm) and crosses nine analogue nets once each.
- Audio is fully op-amp conditioned (OPA1652 single-supply on +9 V_A with a buffered half-rail bias): inputs AC-coupled 1 MΩ → buffer → ×0.59 → inverter → 100 R + 33 nF into the Seed; outputs 10 µF → ×−2.2 → 100 R → 10 µF → jack. Seed-side runs 12–69 mm.
- Long control lines: footswitches 116 / 148 mm, mono LED 144 mm, expression tip 146 mm, pots 79–138 mm — all behind pull-ups, resistors or 10 nF filters; no RC on pots/switches (house style).

## 1. SD interface (U7 TF-01A ↔ Seed pins 2–7) — `sd_budget.py`
| Net | Kit path (A1 → U7) | Kit vias | Seed 3 module (l.1803–1811) | Total | Total vias | Pull-up |
|---|---|---|---|---|---|---|
| `SDMMC_CK` | 26.7 mm | 0 | 4.853 / 0 | **31.6 mm** | 0 | none ✓ |
| `SDMMC_CMD` | 18.2 mm | 1 | 9.767 / 1 | 28.0 | 2 | R52 47 k (2.6 mm from A1) |
| `SDMMC_D0` | 15.5 mm | 0 | 13.94 / 2 | 29.4 | 2 | R53 |
| `SDMMC_D1` | 14.6 mm | 0 | 14.942 / 2 | 29.5 | 2 | R54 |
| `SDMMC_D2` | 18.3 mm | 1 | 14.224 / 1 | 32.5 | 2 | R50 |
| `SDMMC_D3` | 18.4 mm | 1 | 17.586 / 1 | 36.0 | 2 | R51 |
| `SDMMC_DETECT` | A1.12 → U7.CD1 76.3 mm | 3 | — | — | — | none (internal) |
- Max 36.0 mm < 120, spread 8.0 mm < 10 (= 45 ps), DATA/CMD vias 2/2/2/2/2 equal — **all three datasheet guidelines met** (identical to EU-P5-01). All 0.254 mm except `SDMMC_DETECT` at **0.202 mm** (the board's only 0.2 mm trace; a static switch line, irrelevant electrically).
- **Decoupling at U7.VDD:** `+3V3` is a 288.7 mm, 0.406 mm rail with 4 vias whose only capacitor C1 100 nF sits at U11 (240.2, 138.9) — **240.4 mm** from U7.4; A1.38 → U7.4 = 30.7 mm. No cap at the socket (JUDGMENT PD-P5-01b → Pass 2; same as Pod DP-P5-01b and EU-P5-01b).
- **PASS.** Card detect wired (Pass 3 PD-P3-05).

## 2. USB Full-Speed pair (J7 → U14 USBLC6-2SC6 → Seed 36/37)
| Net | Path | Length | Vias | Width |
|---|---|---|---|---|
| `/Daisy/USB_IN_P` / `_N` | J7.A6/A7 → U14.1/3 (B6/B7 tied, 3.8 / 7.8 mm) | 5.9 / 6.2 mm | 0 / 2 (B7 tie) | 0.254 |
| `/Daisy/USB_OTG_HS_N` | U14.4 → A1.36 | 37.5 mm | **0** | 0.254 |
| `/Daisy/USB_OTG_HS_P` | U14.6 → A1.37 | 43.4 mm | **0** | 0.254 |
| `/Daisy/+5V_USB` | J7 VBUS → U14.5 | 17.9 / 13.2 mm | 2 | 0.406 |
| CC1 / CC2 | J7.A5/B5 → R1/R2 5k1 | 5.1 / 5.2 mm | 0 | 0.254 |
- Skew **5.9 mm = 33 ps** (0.04 % of an 83 ns bit); pair coupled **33.1 mm at 0.196 mm**; 0 vias on either line; U14 8.0 mm from J7 (same block as the Eurorack kit, receptacle side identical to 0.1 mm; the Seed-side runs differ because A1 sits 8.8 mm lower). **PASS.** Rev 3: 130.2/130.6 mm, 9/11 vias, 0.4 mm; Pod: 57.9/59.3 mm, 0 vias, 1.4 mm.

## 3. MIDI (DIN, far-right edge)
| Segment | Length | Vias | Width |
|---|---|---|---|
| J10.4 → R4 220 R (`MIDI_IN_4`) → U11.1 | 18.6 mm + 3.0 mm | 0 | 0.254 |
| J10.5 → U11.2 (`MIDI_IN_5`) | 13.5 mm | 0 | 0.254 |
| J10.2 → C34 100 nF; shell GND1/2 → C47 | 9.2 mm (1 via) / 12.3–17.3 mm | — | 0.254 / 0.406 |
| U11.4 → R3 270 R / → A1.15 / → R29 (thru) (`MIDI_RX` 210.5 mm total) | 2.6 / **168.7** / 62.4 mm | 2 | 0.254 |
| A1.14 → R59 10 R (`MIDI_TX`) → J11.5 | **199.5 mm** + 6.0 mm | **0** | 0.254 / 0.406 |
| `+3V3` → R61 10 R → J11.4 (OUT) | 12.9 mm | 0 | 0.406 |
| R29 → J1.5 / `+3V3` → R28 → J1.4 (THRU) | 3.8 / 3.9 mm | 0 | 0.254 |
- The Seed ↔ opto/driver runs are ~170–200 mm because the DIN jacks sit at x = 235 against the Seed at x = 53; `MIDI_TX` crosses the whole board with no via at all. At 31.25 kbaud (32 µs bit) 200 mm is 1.1 ns — electrically short by three orders of magnitude; `proximity.py` finds **no analogue net within 1.0 mm on the same layer** anywhere along either line (§5). No antiparallel diode on the opto LED (Pass 3 PD-P3-09); OUT/THRU 10 R / 10 R. **PASS** on the signal side.

## 4. Audio and expression paths (OPA1652 U3/U9/U10 single-supply on `+9V_A`, bias from U1A)
**Inputs (L shown; R identical with C7/R15/R16/U3A/U3B/R26/R27/C12):**
| Net | Path | Length | Vias | Width |
|---|---|---|---|---|
| `AUDIO_IN_LEFT` | J2 tip → C29 10 µF | 28.4 mm | 0 | 0.254 |
| `Net-(C29-Pad1)` | C29 → R7 1 M (to bias) / R8 100 R | 2.7 / 4.3 mm | 0 | 0.254 |
| `Net-(U9A-+)` | R8 → U9.3 (+), C28 100 pF to GND (f_c 16 MHz RF stop) | 3.9 mm | 0 | 0.254 |
| U9A follower → R58 3k3 → `Net-(C30-Pad1)` (R71 4k7 to GND, C30 1 nF) → C35 10 µF → R69 10 k → U9B inverting (R70 10 k, C32 270 pF) | ×0.59 then ×−1 (R69/R70), f_c 59 kHz | 1.6–6.1 mm nets | 0 | 0.254 |
| `CODEC_IN_L` | U9.7 → R72 100 R → A1.16, C37 33 nF at the Seed pin (f_c with 100 R = 48 kHz) | **69.0 mm** | 2 | 0.254 |
| `CODEC_IN_R` | R27 → A1.17, C12 33 nF | 38.8 mm | 2 | 0.254 |
| `/Audio IO/AREF_AUDIO_IN_BIAS` | U1.1 → R7, R15, U3.5, U9.5, U10.3/5, R5 (9 pins) | 118.8 mm total | 8 | 0.254 |
| `Net-(J2-PadTN)` / `Net-(J4-PadTN)` | tip-normal → R64/R65 10 k → GND | 3.9 / 4.0 mm | 0 | 0.406 / 0.254 |
**Outputs:**
| Net | Path | Length | Vias | Width |
|---|---|---|---|---|
| `CODEC_OUT_L` / `_R` | A1.18/19 → C48/C3 10 µF | 12.1 / 13.6 mm | 0 | 0.254 |
| `Net-(C48-Pad1)` / `Net-(C3-Pad1)` | → R74/R11 15 k | 8.4 / 7.7 mm | 0 | 0.254 |
| U10A/U10B inverting, R75/R12 33 k ‖ C38/C5 100 pF (gain −2.2, f_c 48 kHz) → R76/R13 100 R → C42/C6 10 µF | 2.7–6.3 mm nets | 0 | 0.254 |
| `AUDIO_OUT_LEFT` / `_RIGHT` | C42/C6 → J3/J5 tip, R77/R14 10 k bleed to GND | **86.7 / 120.1 mm** | 2 / 2 | 0.254 |
- Levels: instrument-level input → ×0.59 → ×−1 (two coupling caps, 100 pF/1 nF RF stops, 33 nF at the Seed) — a 1 Vrms instrument signal arrives at ≈ 0.59 Vrms (1.7 Vpp < 3.6 Vpp, datasheet l.126); Seed 0 dBFS 1 Vrms → 2.2 Vrms out, 100 Ω source. 1 MΩ in / 100 Ω out ✓ README. The ≈ 4.5 V `AREF` bias net is 119 mm with 8 vias and feeds nine pins — a DC node decoupled by C33/C39/C55 at U1 (3.5/1.8 mm), fine.
**Expression (J6 → U1B follower on `+5V_A` → 10 k/20 k/10 nF → pin 28):**
| Net | Path | Length | Vias | Width |
|---|---|---|---|---|
| `EXPRESSION_IN_EXT` | J6 tip → U1.5 (+), R18 1 M to GND at 2.0 mm | **145.8 mm** | 1 | 0.254 (126.5) + 0.2 (19.1) |
| `Net-(J6-PadR)` | J6 ring ← R46 100 R ← `+5V_A` | 26.1 mm | 0 | 0.254 |
| `/Audio IO/ADC_EXPRESSION_PRE` | U1.7 → R17 10 k | 4.4 mm | 0 | 0.254 |
| `ADC_EXPRESSION` | R17 → A1.28, R60 20 k + C46 10 nF (f_c = 1/(2π·6.67 k·10 nF) = 2.4 kHz) | 12.0 mm | 0 | 0.254 |
- The 146 mm unbuffered tip line is a high-impedance (1 M) node, but it is a DC control signal filtered at 2.4 kHz after the follower — pickup is averaged out; the 3.33 V full-scale on a 3.3 V-only pin is Pass 3 PD-P3-07. **PASS** (signal side).

## 5. Proximity of digital to analogue (`proximity.py`, lists from `prox_lists.py`)
Aggressors (40 nets): `SDMMC_*` + `SDMMC_DETECT`, USB, `MIDI_*`, DIN-side MIDI nets, `LED_*` + anode nets, `TAC_*`, `TOG_*`, `GPIO_FSW_*`, CC, `+3V3`. Victims (45): `AUDIO_*`, `CODEC_*`, `POT_1–6`, `ADC_EXPRESSION*`, `EXPRESSION_IN_EXT`, `AREF_AUDIO_IN_BIAS`, every op-amp node, jack-normal nets, `+3V3_A`.
| Pair | Same-layer min edge gap | Parallel ≤ 0.5 mm | ≤ 1.0 mm | Crossings |
|---|---|---|---|---|
| `+3V3` (rail) vs `+3V3_A` (rail) | 0.513 mm | 0 | 101.7 mm | 2 |
| `+3V3` vs `POT_1` / `POT_2` / `POT_3` | 1.37 / 1.73 / 1.73 mm | 0 | 0 | 1 each |
| `+3V3` vs `AREF`, `CODEC_IN_R/L`, `ADC_EXPRESSION`, `AUDIO_OUT_L/R` | 5.7–22 mm | 0 | 0 | 1 each |
| **any signal-carrying digital net (SD, USB, MIDI, LED, switch, footswitch) vs any analogue net** | **> 1.0 mm** | **0** | **0** | **0** |
- No digital signal trace shares a layer within 1 mm of any analogue trace, and none crosses one. The only rail-to-rail adjacency is `+3V3` beside `+3V3_A` for 102 mm at 0.51 mm (both 0.406 mm rails running along the pot row) — two DC rails, no signal content, though `+3V3` carries the Seed's digital supply return ripple (Pass 2 topic). **PASS** — versus rev 3's `/USART1_RX` 49 mm at 0.41 mm beside `AUDIO_IN_L` (R3-P5-04) and the Eurorack kit's 7.3 mm `MIDI_RX`/`CV_3_ADC` pairing.

## 6. LED lines (common cathode, GPIO sources; `invert = false`)
| Channel | Seed pin (STM32) | GPIO → R | R → LED anode |
|---|---|---|---|
| LED1 mono red | 31 (PA1) | **143.8 mm / 0 vias** (R43 1 k, LED1 at (206, 146)) | 5.3 mm |
| LED2 R | 32 (PA0) | 26.0 mm / 0 (R40 2 k) | 4.9 mm |
| LED2 G | 34 (PG9) | 25.4 mm / 0 (R25 2 k) | 11.2 mm |
| LED2 B | 33 (PD11) | 25.7 mm / 0 (R44 2 k) | 7.8 mm |
- 120 Hz software PWM (`led.cpp`); 0.254 mm 2-node nets; drive ≈ 1.3 mA (red/1 k) and ≈ 0.65/0.15 mA (RGB, V_f from memory) → Pass 2. The 144 mm mono-LED line at 120 Hz with ≈ 1 mA edges is the longest switched line on the board; `proximity.py` finds nothing analogue within 1 mm of it. **PASS.**

## 7. Switches, toggles, footswitches
| Net | Part → Seed pin | Length | Vias | Width | Pull-up / RC |
|---|---|---|---|---|---|
| `TOG_SW1_A` / `_B` | SW1.1 → 9 (PG11) / SW1.3 → 8 (PG10) | 24.8 / 33.4 mm | 0 / 0 | 0.254 | `Switch3` PULLUP ×2 |
| `TOG_SW2` | SW2.1 → 10 (PB4) | 37.9 mm (20.9 mm at 0.2 mm) | 1 | 0.2 / 0.254 | `Switch` PULLUP |
| `TOG_SW3` | SW3.1 → 29 (PA5) | 62.9 mm | 1 | 0.254 | PULLUP |
| `TAC_SW4` | SW4.1/.2 → 1 (PB12) | 98.6 / 105.1 mm | 1 | 0.254 | PULLUP |
| `TAC_SW5` | SW5.1/.2 → 35 (PA2) | 110.4 / 116.9 mm | 1 | 0.254 | PULLUP |
| `GPIO_FSW_1` | FSW_1.2 → 11 (PB5) | **116.5 mm** | 1 | 0.254 | PULLUP |
| `GPIO_FSW_2` | FSW_2.2 → 30 (PA4) | **148.2 mm** | 1 | 0.254 | PULLUP |
| `SDMMC_DETECT` | U7.CD1 → 12 (PB8) | 76.3 mm | 3 | 0.202 | PULLUP (`sd_detect`) |
- All returns to GND; no RC, no external pull-ups — the STM32 internal pull-up (≈ 40 kΩ typ., **from memory**) and libDaisy's 1 kHz software debounce. 116–148 mm footswitch lines on a 40 k pull-up are the kit's most ESD/noise-exposed inputs (JUDGMENT PD-P5-07, same scheme as the Pod and rev 3's 170/190 mm clicks). **PASS.**

## 8. Potentiometers and rails
| Net | Path | Length | Vias | Width |
|---|---|---|---|---|
| `POT_1 … POT_6` | VRn wiper → A1.22–27 | 78.6 / 100.0 / 121.6 / 97.8 / 118.1 / 138.2 mm | 1 each | 0.254 |
| `+3V3_A` | A1.21 → VR3 113.4 mm, chained VR1/VR5 ± 43–46 mm, VR4 60 mm | 184.3 mm total | 3 | 0.406 |
| `+3V3` | A1.38 → 47 k pull-ups 12.6 mm, → U7.4 30.7 mm, → R61/R28 (MIDI source) ≈ 201–214 mm, → C1 209.7 mm | 288.7 mm total | 4 | 0.406 |
- No wiper caps/series R on any pot (house style; libDaisy 810.5-cycle conversion + 1 kHz smoothing). Pots 79–138 mm unfiltered into 16-bit ADC inputs on 3.3 V-only pins 24/25 (bounded by the pot's own rail). **PASS.**

## 9. Comparison — Seed3 Pedal Dev Kit vs WavetableController rev 3 vs Daisy Pod
| Item | Seed3 Pedal Dev Kit Rev3 (this pass) | WavetableController rev 3 | Daisy Pod Rev5 | Reading |
|---|---|---|---|---|
| Board | 197 × 100 mm, 2-layer | 165 × 102 mm, 2-layer | 90 × 52 mm | kit 1.2× rev 3 area |
| SD (board + module) | 14.6–26.7 mm kit, 0–1 via; totals 28.0–36.0 mm, spread 8.0 mm, DATA/CMD vias 2 each; **card detect on D11** (76 mm, 0.2 mm); no cap at U7 (240 mm) | 24.2–41.0 mm, 2–4 vias, spread 16.8 mm; SWA open (F-022) | 10.6–20.3 mm, spread 9.7 mm; SWA open | kit block = Eurorack kit block; only board with CD |
| USB FS pair | 37.5/43.4 mm, **0/0 vias**, 5.9 mm skew, coupled 33.1 mm @ 0.196 mm; CC 5k1, VBUS → TVS only | 130.2/130.6 mm, 9/11 vias, 0.4 mm | 57.9/59.3 mm, 0 vias, 1.4 mm | all PASS |
| MIDI IN | DIN; 220 R + H11L1 + 270 R, **no antiparallel diode**; sleeve/shell via 100 nF | 220 R + H11L1 + D1 + 270 R | same + D5 | kit follows datasheet Fig 7.1 |
| MIDI OUT / THRU | DIN, 10 R/10 R, `MIDI_TX` 199.5 mm 0 vias, `MIDI_RX` 168.7 mm to the Seed | 10 R/33 R, no THRU | none | long but isolated runs |
| Audio runs to the Seed | buffered: CODEC_IN 69.0/38.8 mm, CODEC_OUT 12.1/13.6 mm; jack sides 28 mm in / 87–120 mm out; 1 MΩ in, 100 Ω out | unbuffered 140.9 / 205.6 / 227.6 mm | unbuffered 44–56 mm | kit's Seed-side runs are the shortest of the three |
| Digital beside analogue | **none ≤ 1.0 mm, 0 crossings** (rails only: `+3V3` ∥ `+3V3_A` 102 mm @ 0.51 mm) | `/USART1_RX` 49 mm @ 0.41 mm beside `AUDIO_IN_L` | none ≤ 1.0 mm | kit is the cleanest |
| Pots | 6 direct, 79–138 mm, no RC, on `+3V3_A` | pots on ADC pins | 2 direct, 32 mm | — |
| Encoder / clicks | none; footswitches 116/148 mm, tactile 99–117 mm, toggles 25–63 mm, no RC, internal pull-ups | ENCL/ENCR A/B 33/32 & 12/13, clicks 22/29 (170/190 mm) | encoder 62 mm, click on pin 14 (DP-P3-08) | kit's pins 12/13 = SD detect / free |
| SPI1 pins 8/9/10/11 | TOG_SW1_B/A, TOG_SW2, FSW_1 (plain GPIO) | CS, SCLK, `/TAC_SHIFT_R`, MOSI → OLED | DNI header | rev 3's OLED pin set is not available on the kit |
| Pins 1 / 28 | TAC_SW4 / expression ADC (3.33 V full scale, PD-P3-07) | `/RES_SPI` / `/DC_SPI` | USB ID / POT_1 | — |
| 3.3 V-only pins 24/25/28/29/30 | POT_3, POT_4, expression, TOG_SW3, FSW_2 | LED / DC / ENCR_CLICK / LED | LED / LED / POT_1 / A7 / LED | pin 28 zero-margin on the kit |
| LEDs | common cathode, 1 k / 2 k source, 120 Hz software PWM | NPN low-side from 9 V | common anode sink 1 k | — |
| Power | 9 V barrel → 3 beads + NSR1020 + 3R3/100 µF π → VIN (datasheet Fig 1.1); 5 V LDO for expression | 9 V barrel, Schottky bridge | Seed USB | same input voltage and reverse protection as rev 3 |

## Findings (Seed3 Pedal Dev Kit Rev3, Pass 5)
| ID | Class | Status | Finding | Evidence | Source |
|---|---|---|---|---|---|
| PD-P5-01 | PASS | confirmed | SD interface = the Eurorack kit block: totals 28.0–36.0 mm, spread 8.0 mm, DATA/CMD vias 2 each — all three Seed 3 datasheet guidelines met; 47 k on DAT/CMD only; `SDMMC_DETECT` 76 mm / 3 vias / 0.202 mm (static) | §1 | datasheet l.1795–1812; `sd_budget.py` |
| PD-P5-01b | JUDGMENT | confirmed | No decoupling capacitor at the SD socket: U7.VDD is 240 mm from the only `+3V3` cap (C1 at the far-right opto), 30.7 mm from Seed pin 38 → Pass 2 (same as Pod DP-P5-01b, EU-P5-01b) | §1 | `net_geometry.py` |
| PD-P5-02 | PASS | confirmed | USB FS pair 37.5/43.4 mm, 0 vias, 5.9 mm = 33 ps skew, coupled 33.1 mm at 0.196 mm, TVS 8.0 mm from the receptacle | §2 | USB FS 83 ns bit |
| PD-P5-03 | PASS | confirmed | MIDI: `MIDI_TX` 199.5 mm 0 vias, `MIDI_RX` 168.7 mm 2 vias to the Seed (1.1 ns vs a 32 µs bit), DIN-side nets 4–19 mm, THRU 3.8/3.9 mm from the driver resistors; no analogue net within 1 mm of either line. Diode omission carried as PD-P3-09 | §3 | datasheet l.1930–1962 |
| PD-P5-04 | PASS | confirmed | Audio: 1 MΩ AC-coupled inputs → buffer → ×0.59 → inverter (59 kHz) → 100 R + 33 nF (48 kHz) → Seed, 39–69 mm; outputs 10 µF → ×−2.2 (48 kHz) → 100 R → 10 µF → jack, Seed side 12–14 mm; bias net 119 mm / 8 vias (DC); expression 146 mm high-Z tip into a follower then 10 k/20 k/10 nF (2.4 kHz) → pin 28, 12 mm | §4 | netlist values; datasheet l.126, Fig 4.5 |
| PD-P5-05 | PASS | confirmed | **No digital trace within 1.0 mm of any analogue trace on the same layer and no opposite-layer crossing of a signal line**; only the `+3V3` rail beside `+3V3_A` for 102 mm at 0.51 mm and single rail crossings. Cleanest of the three references (rev 3: 49 mm at 0.41 mm, R3-P5-04) | §5 | `proximity.py` |
| PD-P5-06 | PASS | confirmed | LED lines 25–26 mm (RGB, 2 k) and 144 mm (mono, 1 k), 0 vias, clean 2-node nets, 120 Hz software PWM; ≈ 1.3/0.65/0.15 mA drive (V_f from memory) → Pass 2 | §6 | libDaisy `led.cpp` |
| PD-P5-07 | JUDGMENT | confirmed | Footswitch lines 116.5 / 148.2 mm and tactile lines 99–117 mm with only the STM32 internal pull-up (≈ 40 kΩ, from memory) and software debounce — functional (same scheme as Pod/rev 3) but the kit's most noise/ESD-exposed inputs; toggles 25–63 mm; `TOG_SW2` has 20.9 mm at 0.2 mm width | §7 | libDaisy `switch.h` |
| PD-P5-08 | PASS | confirmed | Pots 79–138 mm, 1 via, no RC, across GND/`+3V3_A` (that rail's only load, 184 mm chain); 3.3 V-only pins 24/25 bounded by the pot rail | §8 | BOM value `P-10K-B-R` |
| PD-P5-09 | PASS (comparison) | confirmed | The Pedal kit shares rev 3's SD pull-ups, USB TVS/data-only block, 9 V barrel input and MIDI-on-pins-14/15; it adds card detect, buffers all audio, drops the MIDI-IN diode, and keeps MIDI 180 mm from the audio stages. Its pin plan leaves only pin 13 free, so rev 3's OLED-on-SPI1 cannot coexist with it | §9 | rev-3 / Pod reports |
