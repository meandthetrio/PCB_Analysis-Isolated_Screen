# Pass 5 — Signal-Specific, Round 2 (2026-10 files)
**Date:** 2026-10-07 · **Truth checked:** `.kicad_pcb` geometry (pcbnew extraction) + schematic networks · **Thresholds:** TPA6110A2 SLOS314B (fetched 2026-10-07, `datasheets_2026-10/`), Newhaven NHD-2.7-12864WDW3 Rev 6, Daisy Seed v1.2.0, MIDI 3.3 V practice; MAX9814 pin functions from third-party datasheet copies (analog.com blocked — see §7) · **Status: COMPLETE**

## 1. SPI display bus (new — replaces the I2C bus of Round 1)

| Net | Daisy → J8 | Length | Vias | Width | Layers |
|---|---|---|---|---|---|
| /SCLK_SPI | 9 → 7 | 112.3 mm | 4 | 0.3 | F 105 / B 7 |
| /SD_IN_SPI | 11 → 8 | 106.5 mm | 6 | 0.2 (11 mm) + 0.3 | F 98 / B 8 |
| /CS_SPI | 8 → 17 | 88.5 mm | 2 | 0.3 | F 87 / B 2 |
| /DC_SPI | 28 → 4 | 123.8 mm | 7 | 0.3 | F 86 / B 37 |
| /RES_SPI | 1 → 16 | 104.9 mm | 1 | 0.3 | F 94 / B 11 |

Point-to-point, no pull-ups needed (push-pull, unlike I2C — F-027 is moot). Electrical length ≈ 0.6–0.8 ns per line vs a ≥ 100 ns bit at the SSD1322's 10 MHz class serial clock: no termination or matching concern. SCLK/SDIN skew 5.8 mm ≈ 40 ps, irrelevant. Newhaven's example code holds /RES low ≥ 200 µs — a GPIO (pin 1 / D0) does that. All five lines run over the GND pour on both layers. **PASS** (F-067). JUDGMENT: DC_SPI's 7 vias and 37 mm on B.Cu are the untidiest of the five; cosmetic.

## 2. USB Full-Speed pair (F-028 revisited → PASS)
Connector side P2 → U2 ESD: 16.0 / 14.2 mm (4 / 2 vias). MCU side U2 → A1: **130.2 / 130.6 mm, 9 / 11 vias, 0.3 mm** — skew 0.4 mm (≈ 3 ps). Round 1's 7.2 mm / 2-via asymmetry and 0.1/0.2 width mix are gone; one 1.1 mm 0.1 mm stub remains on USB_IN_MCU_N (F-037). Still no impedance control (2-layer, 1.6 mm — inherent) and the pair goes 84 mm as the crow flies for 130 mm of trace; fine at 12 Mb/s, field-proven. U2 USBLC6-2P6 in the data path, VBUS to U2 pin 5 ✓, CC1/CC2 5.1 k pull-downs ✓ (Pass 3).

## 3. SD card (PASS)
Runs now 27–49 mm (Round 1: 89–108) — the Daisy and P1 moved together. Max skew 22 mm (≈ 150 ps) at SDIO ≤ 50 MHz: irrelevant. 47 k pull-ups on CMD, D0–D3 per the Daisy reference (Pass 3). All 0.3 mm with short 0.2 mm necks. Card-detect remains half-wired (F-022).

## 4. MIDI (F-029 → PASS, unchanged topology)
- **OUT (J3):** USART1_TX → R1 10 Ω → tip; +3V3_D → R4 33 Ω → ring. 3.3 V MIDI practice ✓. USART1_TX is 130.5 mm / 13 vias (5.9 mm at 0.1 mm — F-037).
- **IN (J6):** tip → R3 0 Ω → D1 (NSR1020 Schottky, reverse protection across the opto LED) / U1 H11L1 pin 2; ring → R2 0 Ω → R5 220 Ω → U1 pin 1. U1.4 → USART1_RX (112.6 mm / 11 vias), R6 270 Ω pull-up to 3V3_D on the opto output ✓ (H11L1 is open-collector). Textbook.
- 31.25 kbaud on 130 mm: no concern.

## 5. Audio

### 5.1 Headphone / line path (TPA6110A2, U3)
Topology: Daisy AUDIO_OUT_L/R (pins 18/19) → J5 line out (tip/ring) **and** Headphones1 dual 10 k pot (ends 1/4, GND 3/6) → wipers 2/5 → C2/C3 470 nF → R12/R13 22 k → U3 IN1−/IN2−; R14/R15 33 k feedback; VO1/VO2 → C6/C7 100 µF → J7 tip/ring with R22/R23 10 k bleed to GND; SHDN → GND (always on); BYPASS → C4 100 nF; VDD → +3V3_A with C5 100 nF at 5.6 mm.

Checked against SLOS314B:
| Item | Design | Datasheet | Verdict |
|---|---|---|---|
| Gain | −Rf/Ri = −33 k / 22 k = **−1.5 V/V** | Eq. 1 | OK (pot provides the volume) |
| Input HPF | 1/(2π · 22 k · 470 n) = **15.4 Hz** | Eq. 4 | OK |
| Mid-rail bypass rule | C(B)·230 k = 100 n · 230 k = 23 ms ≥ Ci·Ri = 470 n · 22 k = 10.3 ms | Eq. 6: 1/(C(B)·230 k) ≤ 1/(Ci·Ri) | **PASS** (same as Round 1) |
| C(B) value | 100 nF ceramic | "0.1 µF to 1 µF ceramic or tantalum low-ESR" | OK |
| Output coupling, 32 Ω load | 100 µF → f_c = 1/(2π · 32 · 100 µ) = **50 Hz** | Table 1: 68 µF → 73 Hz for 32 Ω | OK (better than the table example) |
| Compensation cap across Rf | **none** | "a small compensation capacitor of approximately 5 pF should be placed in parallel with Rf" (Eq. 3) | **JUDGMENT, F-069** — omitted; MOS input capacitance peaking risk, usually benign at gain 1.5 |
| Supply decoupling | C5 100 nF at 5.6 mm ✓; **no bulk cap on +3V3_A** (only C5 on the whole rail) | "low-ESR ceramic, typically 0.1 µF, as close as possible to VDD … For filtering lower-frequency noise signals, a larger aluminum electrolytic capacitor of 10 µF or greater placed near the power amplifier is recommended" (p. 14) | **F-031 persists** — recommended ≥ 10 µF still absent; rail now 0.5 mm / 51 mm from the Daisy (was 0.2 mm / 84 mm), which helps the resistive part only |
| Load on the codec output | 10 k pot across AUDIO_OUT_L/R, in parallel with J5 line out | Daisy line out drives ≥ 10 k loads (datasheet typ. app.) | OK |

The pot sits at the codec output (passive volume into the amp): J5's line-out level is **not** affected by the pot, which matches the "PHONES" vs "AUDIO OUTPUT" labelling. Output nets VO1/VO2 run 57/65 mm to the 100 µF caps, then 12 mm to J7 — short.

### 5.2 Mic path (MAX9814, U4) — pin functions from datasheet copies (§7)
MK1 (electret) → /MIC_HOT ← R20 2.2 k ← MICBIAS (bias resistor, matches the reference 2.21 k); /MIC_HOT → C11 100 nF → MICIN; MICOUT → C12 4.7 µF → Daisy AUDIO_IN_2 (pin 17); GAIN → +3V3_A = **40 dB** (lowest setting); A/R → GND = **1:500**; CT → C8 100 nF (attack ≈ 240 µs by the EV-kit scaling); TH ← R18 100 k / R19 150 k divider from MICBIAS (same values as the MAX9814 EV kit); CG → C9 2.2 µF; BIAS → C10 470 nF; SHDN tied to VDD (always on); VDD ← FB2 ← +3V3_A with C13 2.2 µF at 5.7 mm. Configuration is the EV-kit configuration. **PASS** on topology (F-068); the only Round 2 change is that the fan-out is the board's last 0.1 mm copper (≈ 46 mm, forced by 0.25 mm pads — F-037).

### 5.3 Run lengths and crosstalk (F-030 revisited)
Analog runs are shorter and wider than Round 1: AUDIO_OUT_L/R 205 / 228 mm (was 285 / 277, 0.1 mm → now **0.3 mm**), AUDIO_IN_L 141 mm (was 213), mic return 53 mm (was 171). All over the pour on both layers.

Same-layer proximity scan (analog vs digital, gap < 1 mm, with parallel-run length):

| Analog | Digital | Layer | Min gap | Parallel run |
|---|---|---|---|---|
| AUDIO_OUT_R | /TAC_SWITCH_2 | F.Cu | **0.20 mm** | **24.9 mm** |
| AUDIO_OUT_L | /TAC_SWITCH_2 | F.Cu | 0.70 mm | 31.9 mm |
| AUDIO_IN_L | /USART1_RX | F.Cu | 0.41 mm | **42.7 mm** |
| AUDIO_IN_L | /USART1_TX | F.Cu | 0.45 mm | 24.8 mm |
| AUDIO_IN_L | /TAC_SHIFT_L | F.Cu | 0.45 mm | 12.2 mm |
| (12 more pairs) | | | ≥ 0.35 | ≤ 6 mm |

No broadside (opposite-layer) overlaps at all. The aggressors are slow (buttons: static; MIDI UART: 31 kbaud, 0.3–3 V edges), so the coupled energy is tiny — but the AUDIO_OUT_R / TAC_SWITCH_2 pair at 0.2 mm for 25 mm is the one place where a button press could put a click on the line/headphone output (F-070, JUDGMENT). None of the SPI, USB, SD or buck-SW nets come within 1 mm of an analog trace for more than 3 mm. Buck SW node (U6 → L1, 6.8 mm) is 60 mm from the nearest analog trace.

### 5.4 Other
- J4 ring → GND (mono input; stereo plug R channel shorted) — accepted, noted in Pass 3.
- Daisy audio inputs are AC-coupled 1 Vrms line level (datasheet); the MAX9814 output is AC-coupled by C12 ✓; J4 feeds pin 16 directly (the Daisy's own coupling) ✓.

## 6. Findings
- **F-067 PASS:** SPI display bus geometry and wiring.
- **F-068 PASS:** MAX9814 configured per EV-kit (40 dB, 1:500, 2.2 k bias, 100 k/150 k TH); MIDI, SD and USB pass (USB asymmetry F-028 fixed: 0.4 mm skew, 0.3 mm throughout).
- **F-031 persists (JUDGMENT, datasheet-cited):** no ≥ 10 µF bulk capacitor near the TPA6110A2; +3V3_A carries only C5 100 nF.
- **F-069 (JUDGMENT, datasheet-cited):** no ≈5 pF compensation capacitor across R14/R15.
- **F-070 (JUDGMENT):** AUDIO_OUT_R runs 25 mm at 0.20 mm from /TAC_SWITCH_2 on F.Cu; AUDIO_IN_L runs 43 mm at 0.41 mm from USART1_RX. Slow aggressors; move 0.5 mm on the next edit.
- **F-030 improved:** analog runs 25–70 % shorter and 3× wider than Round 1.

## 7. Threshold provenance
TPA6110A2 SLOS314B fetched from ti.com and archived. NHD Rev 6 and Daisy v1.2.0 archived (Pass 2). `analog.com` (MAX9814), `onsemi.com` (H11L1) and `st.com` (USBLC6) are **not** on the allow list: MAX9814 pin functions (GAIN/A/R settings, 2.21 k bias, 100 k/150 k TH, 2.2 µF CG) were taken from search extracts of third-party datasheet copies and the MAX9814 EV-kit document; H11L1 and USBLC6 topologies are unchanged from Round 1 and were not re-verified. Add those three hosts to re-fetch.
