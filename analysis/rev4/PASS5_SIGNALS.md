# Rev 4 — Pass 5: Signal-Specific Report
**Date:** 2026-10-13 · **Truth checked:** `rev4/WavetableController.kicad_pcb` geometry + rev-4 netlist · **Tools:** `analysis/rev4/scripts/pass3_5/` `net_geometry.py` (`kicad_out/rev4/net_geometry_sel.txt`), `proximity.py` (`proximity.txt`, aggressor/victim gap ≤ 1.0 mm). Thresholds as rev 3 (SSD1322 10 MHz from memory, flagged; t_pd 5.64 ps/mm computed; 3W rule of thumb).

## Headline
- **Nothing in the SPI, SD, USB, MIDI or audio routing changed** between rev 3 and rev 4 (lengths, via counts and widths below are identical to the rev-3 tables). The only new signal content is the encoder RC network.
- **The two proximity items the 7 Oct review listed are still there:** /USART1_RX 49.1 mm parallel to AUDIO_IN_L at 0.41 mm and /USART1_TX 26.1 mm at 0.45 mm (R3-P5-04); **/TAC_SWITCH_2 27.2 mm parallel to AUDIO_OUT_R at 0.20 mm** and 31.9 mm to AUDIO_OUT_L at 0.70 mm — the closest pairing on the board, same layer.
- **Encoder lines:** the 10 nF caps are at the encoder end, so 63–111 mm of trace separates each cap from its Daisy input.

## 1. SPI OLED bus — unchanged
/CS_SPI 88.5 mm / 2 vias · /SCLK_SPI 112.3 / 4 · /SD_IN_SPI 106.5 / 6 · /DC_SPI 123.8 / 7 · /RES_SPI 104.9 / 1; all 0.3 mm, no stubs, no termination, no pull-ups. R3-P5-01 judgment stands (22–33 Ω series or GPIO slew ≤ medium; SCLK ≤ 10 MHz).

## 2. SD card — unchanged copper, better decoupling
A1↔P1 24–41 mm, 0.3 mm, 47 k pull-ups; now with C27/C28 at the socket (Pass 2). PASS.

## 3. USB — unchanged
/USB_IN_MCU_P 130.2 mm / 9 vias, /USB_IN_MCU_N 130.6 / 11 (1.1 mm at 0.1); P2→U2 14.1 / 14.2 mm. F-028 as rev 3: length matched, via-heavy, functionally fine.

## 4. MIDI — unchanged
OUT: A1.14 → R1 10 Ω → J3.T 131.4 mm / 13 vias (5.9 mm at 0.1 under LED2); R4 33 Ω 1210. IN: R2/R3 0 Ω, R5 220 Ω, U1 H11L1, D1, R6 270 Ω; /USART1_RX 112.6 mm / 11 vias. PASS. Proximity to AUDIO_IN_L unchanged → R4-P5-02.

## 5. Audio — unchanged
AUDIO_OUT_L 205.5 mm / 3 vias, AUDIO_OUT_R 227.5 / 3, AUDIO_IN_L 140.7 / 8, AUDIO_MIC_IN_R 53.0 / 1 (0.2 mm), HEADPHONE_OUT_L/R 12.1 / 0; pot taps as rev 3. Residual judgment (F-030) unchanged.

## 6. Proximity scan (same-layer parallel runs ≤ 1.0 mm, `proximity.py`)
| Aggressor | Victim | Min gap | Parallel length | Note |
|---|---|---|---|---|
| **/TAC_SWITCH_2** | **AUDIO_OUT_R** | **0.201 mm** | **27.2 mm** | 7 Oct "worth tidying" row, NOT DONE; button press = CMOS edge with internal pull-up, so a click into the line out is plausible |
| /TAC_SWITCH_2 | AUDIO_OUT_L | 0.701 | 31.9 | same run |
| /USART1_RX | AUDIO_IN_L | 0.407 | 49.1 | R3-P5-04, NOT DONE |
| /USART1_TX | AUDIO_IN_L | 0.45 | 26.1 | R3-P5-04, NOT DONE |
| /TAC_SHIFT_L | AUDIO_IN_L | 0.45 | 12.2 | new in the scan at this threshold (rev 3 listed UART only) — minor |
| /LED_1_G | AUDIO_IN_L | 0.50 | 7.2 | PWM LED line — minor |
| /LED_1_B | AUDIO_MIC_IN_R | 0.55 | 9.2 | PWM LED line beside the mic path — minor |
| /DC_SPI, /ENCR_A/B, /TAC_SHIFT_R | audio nets | 0.35–0.95 | 0 (crossings only) | acceptable |

No SPI line runs parallel to audio; Net-(U6-SW) is 4.9 mm long and 29–38 mm from U3/U4/MK1 (as rev 3).

## 7. Encoder A/B lines (new)
| Net | Length | Vias | Width | Cap → Daisy pin | Cap → encoder pin |
|---|---|---|---|---|---|
| /ENCL_A | 88.1 mm | 6 | 0.3 | 62.8 mm | 6.8 mm |
| /ENCL_B | 96.7 | 8 | 0.3 | 64.1 | 7.2 |
| /ENCR_A | 159.7 | 8 | 0.3 (18.7 mm at 0.2) | 111.4 | 10.2 |
| /ENCR_B | 157.2 | 8 | 0.3 (17.9 at 0.2) | 110.7 | 10.0 |
With R = 10 k at the Daisy end of the pull-up (R31/R32 are at the encoder too — all eight RC parts cluster at the encoders) and C = 10 nF, τ = 100 µs: contact bounce is filtered at the source, which is what the Bourns PEC11 "suggested filter" does. The agreed placement (cap at the MCU pin) would additionally terminate the 63–111 mm line at the input. Judgment: works for debouncing; the state-table decoder in firmware remains the real guard against missed detents (decision 5c).

## 8. LED driver lines — unchanged
GPIO → 1 k → base nets 33–51 mm, 0.2 mm, 2-node; collector-side nets to the Würth pads unchanged.

## Findings (rev 4, Pass 5)
| ID | Class | Status | Finding | Evidence |
|---|---|---|---|---|
| R4-P5-01 | JUDGMENT | confirmed (R3-P5-01 unchanged) | SPI OLED lines electrically short, unterminated; optional 22–33 Ω / slew limit. | §1 |
| R4-P5-02 | JUDGMENT | confirmed (R3-P5-04 unchanged) | MIDI UART RX/TX parallel to AUDIO_IN_L at 0.41/0.45 mm for 49/26 mm. NOT DONE. | §6 |
| R4-P5-03 | JUDGMENT | confirmed (7 Oct row, now measured) | /TAC_SWITCH_2 parallel to AUDIO_OUT_R at **0.20 mm for 27.2 mm** (and 0.70 mm / 31.9 mm to AUDIO_OUT_L), same layer. Move the switch trace or the line-outs ≥ 1 mm apart or to the other layer. | §6 |
| R4-P5-04 | JUDGMENT | confirmed (new) | Encoder RC caps at the encoder end: debounce OK, no termination at the MCU input over 63–111 mm; keep the state-table decoder. | §7 |
| R4-P5-05 | PASS | confirmed | SD, USB, MIDI, audio, LED-driver nets unchanged from rev 3 (all PASS / residual judgments carried). | §2–5, §8 |
