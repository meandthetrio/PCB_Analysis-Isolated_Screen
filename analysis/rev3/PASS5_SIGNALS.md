# Rev 3 — Pass 5: Signal-Specific Report
**Date:** 2026-10-09 · **Truth checked:** `rev3/WavetableController.kicad_pcb` geometry (copper truth for rev 3, GND zone present; pre-fab) + rev-3 schematic networks · **Tools:** `pcbnew` export (`pcb_export.py`), `net_geometry.py` (lengths, widths, vias, pad-to-pad copper path), `proximity.py` (aggressor/victim gap + parallel run + crossings), all in `analysis/rev3/scripts/pass3_5/`.
**Thresholds:** NHD-2.7-12864WDW3 datasheet (scratchpad `datasheets/NHD.txt`); SSD1322 serial-clock minimum cycle **100 ns (10 MHz) — from model memory of the SSD1322 datasheet Table "Serial Interface Timing", NOT fetched (Newhaven/Solomon hosts blocked) — flagged, verify before relying on it**; trace delay derived from first principles (Hammerstad microstrip ε_eff with ε_r = 4.3, w = 0.3 mm, h = 1.5 mm → ε_eff 2.86 → **5.64 ps/mm**); JLCPCB caps as fetched 2026-08-12/13 (Pass 1); rev-2 BOM/BOM-rev3 package power ratings (`kicad_out/rev3/bom_rev3.txt`); MIDI 3.3 V electrical practice (rev-2 F-029); TPA6110A2 SLOS314B (rev-2 F-031, not re-derived).

## Headline
- **SPI OLED bus is electrically short and clean.** Longest line `/DC_SPI` 123.8 mm → 0.70 ns one-way; at the SSD1322's 10 MHz maximum (100 ns period) that is 0.7 % of a bit. Lines only become "long" for driver edges faster than 1.0–1.4 ns, i.e. only at the STM32's *very-high* GPIO speed setting. **No series termination, no pull-ups, 1–7 vias per line, all 0.3 mm** — one judgment item (optional 22–33 Ω at the Daisy end or keep GPIO speed ≤ medium).
- **MIDI UART runs parallel to the line input:** `/USART1_RX` sits 0.41 mm from `AUDIO_IN_L` for 49 mm and `/USART1_TX` 0.45 mm for 26 mm (same layer). Only proximity finding of the pass (R3-P5-04).
- **USB pair now length-matched to 0.4 mm but via-heavy** (11/9 vias vs 3/5 in rev 2). **Audio runs shortened 28–69 %** and widened 0.1 → 0.3 mm. **I2C pull-up finding F-027 is N/A** (bus removed).

## 1. SPI OLED bus (A1 → J8)
| Net | Daisy pin → J8 pin | Length (pad-to-pad copper) | Vias | Width | F.Cu / B.Cu | Other parts on net |
|---|---|---|---|---|---|---|
| `/CS_SPI` | 8 → 17 | 88.5 mm | 2 | 0.3 | 86.9 / 1.6 | none |
| `/SCLK_SPI` | 9 → 7 | 112.3 mm | 4 | 0.3 | 105.1 / 7.2 | none |
| `/SD_IN_SPI` | 11 → 8 | 106.5 mm | 6 | 0.3 (95.6) + 0.2 (11.0) | 98.2 / 8.4 | none |
| `/DC_SPI` | 28 → 4 | 123.8 mm | 7 | 0.3 | 86.4 / 37.4 | none |
| `/RES_SPI` | 1 → 16 | 104.9 mm | 1 | 0.3 | 93.8 / 11.1 | none |

- No stubs (every net is a single pad-to-pad path, `stubs=[]`), no series resistors, no pull-ups/downs on any line (2-node nets).
- **Timing budget (computed):** t_pd = 5.64 ps/mm → delays 0.50 / 0.63 / 0.60 / 0.70 / 0.59 ns. SCLK↔SDIN skew 5.8 mm = 33 ps; SCLK↔CS 24 mm = 134 ps. Against a 100 ns clock period (10 MHz) and the SSD1322's setup/hold figures (tens of ns class, from memory, unverified) these are negligible: **length does not matter at this interface.** Even at 4× the datasheet clock it would not.
- **Reflections/ringing:** a line is electrically long when L > t_r/(2·t_pd). For `/DC_SPI` that threshold is t_r = 1.40 ns, for `/SCLK_SPI` 1.27 ns. STM32H7 GPIO edges at low/medium OSPEEDR are several ns (datasheet class figures, not fetched) → lines are short; at "very high" speed (sub-2 ns) they are borderline and 4–7 vias plus an unterminated 2.54 mm header would ring. **JUDGMENT (R3-P5-01):** either add 22–33 Ω series at the Daisy end of SCLK/SDIN (DC/CS/RES are quasi-static) or pin the GPIO speed at ≤ medium in firmware; SPI1 clock prescaler must keep SCLK ≤ 10 MHz (with libDaisy's 100 MHz-class SPI kernel clock that is ≥ /16).
- **Crosstalk to audio:** `proximity.py` at a 1.0 mm gap threshold finds **no same-layer parallel run** between any SPI line and any audio net; `/DC_SPI` crosses `AUDIO_OUT_L`, `AUDIO_MIC_IN_R`, `AUDIO_OUT_R`, `AUDIO_IN_L` once each on the opposite layer (min gap 0.45–0.95 mm at the crossing) — D/C toggles only per transaction; acceptable.
- **Return path:** both layers carry the single GND zone (20,849 mm² filled); SPI lines are 78–98 % on F.Cu with 1–7 layer changes; no return-via placement next to signal vias (normal for this class of board, noted only).
- **Rail / level:** OLED VDD = `/+3V3_OLED` (U6), driver rail = `/+3V3_D`; VIH = 0.8·VDD = 2.64 V (NHD.txt l.258) is met by a 3.3 V CMOS high. See Pass-3 R3-P3-05 for sequencing.

## 2. SD card (P1 ↔ A1 pins 2–7)
| Net | Length A1↔P1 | Vias | Width | Pull-up |
|---|---|---|---|---|
| `/SD_D0` | 41.0 mm | 4 | 0.3 (+6.1 mm 0.2) | R8 47 k → `/+3V3_D` |
| `/SD_D1` | 38.3 mm | 4 | 0.3 (+5.9 mm 0.2) | R7 47 k |
| `/SD_D2` | 26.7 mm | 2 | 0.3 | R11 47 k |
| `/SD_D3` | 24.2 mm | 2 | 0.3 | R10 47 k |
| `/SD_CMD` | 39.5 mm | 2 | 0.3 | R9 47 k |
| `/SD_CK` | 37.3 mm | 2 | 0.3 | none (correct) |
- Rev 2 was 89–108 mm, 0.1/0.2 mm; rev 3 is **24–41 mm, 0.3 mm** (P1 moved next to the Daisy at (98.7, 133.0)). Max skew 16.8 mm = 95 ps — irrelevant at SDMMC 25–50 MHz (20–40 ns period). 47 k pull-ups on DAT0–3/CMD unchanged, per the Daisy reference (rev-2 F-021). **PASS, improved.**

## 3. USB Full-Speed pair (F-028)
| Net | Length | Vias | Width |
|---|---|---|---|
| `/USB_IN_MCU_P` U2.4 → A1.37 | 130.2 mm | 9 | 0.3 |
| `/USB_IN_MCU_N` U2.6 → A1.36 | 130.6 mm | 11 | 0.3 (+1.1 mm 0.1) |
| `/USB_IN_P` P2 → U2.3 | 14.1 mm | 4 | 0.3/0.2 |
| `/USB_IN_N` P2 → U2.1 | 14.2 mm | 2 | 0.3/0.2/0.1 (3.1 mm) |
- Length mismatch 0.4 mm (2 ps) — rev 2 was 7.2 mm. Via count rose from 3/5 to 9/11 (each via ≈ 0.5–1 nH + ~0.3 pF; 20 vias on a 12 Mb/s pair is harmless but untidy). Still no impedance control (2-layer). Routes through U2 USBLC6-2P6 correctly. **F-028: matched-length part FIXED, via-count part REGRESSED; functionally PASS** (JUDGMENT).

## 4. MIDI (F-029)
- OUT (J3): A1.14 USART1_TX → R1 10 Ω → J3.T (131.4 mm to R1, 13 vias, 0.3 mm with a 5.9 mm 0.1 mm remnant; R1→tip 3.8 mm); `/+3V3_D` → R4 33 Ω → J3.R (43.6 mm). Topology unchanged = MIDI 3.3 V practice (10 Ω / 33 Ω). **PASS.**
- IN (J6): J6.R/T → R2/R3 0 Ω (11.3 / 5.8 mm) → R5 220 Ω → U1 H11L1 with D1 reverse-protection; U1.4 → R6 270 Ω pull-up / A1.15 (112.6 mm, 11 vias). Unchanged. **PASS.**
- **R4 0603 → 1210 (why):** BOM rev 3 line 30: "33Ω **500mW** 1210" (C2907549) vs the 0603 family "100mW" (e.g. line 37). A MIDI-out ring shorted to sleeve (half-inserted TRS plug, mis-wired cable) dissipates 3.3²/33 = **0.33 W** in R4 continuously — above a 0.1 W 0603, inside a 0.5 W 1210. Inferred rationale: survive an indefinite output short. Consistent with the 1 W 2512 choice for R29–R32 in the power entry. **Reasonable, PASS** (inference, not documented in the files).
- **R3-P5-04 (JUDGMENT, new):** `/USART1_RX` runs 49.1 mm parallel to `AUDIO_IN_L` at 0.41 mm edge gap and `/USART1_TX` 26.1 mm at 0.45 mm, same layer (`proximity.py`). MIDI is 31.25 kbaud with CMOS edges; AUDIO_IN_L is the unbuffered line input to the codec. Coupling is capacitive-edge only and the MIDI link is idle most of the time, so audibility is unlikely but the run is the closest digital/analogue pairing on the board. Move the UART or the audio-in trace apart (≥ 3 W ≈ 1 mm) on the next pass.

## 5. Audio paths (F-030)
| Net | Rev 2 | Rev 3 | Vias | Width |
|---|---|---|---|---|
| AUDIO_OUT_L A1.18 → J5.T | 285 mm | 205.6 mm (pot tap at 69.8 mm) | 3 | 0.3 |
| AUDIO_OUT_R A1.19 → J5.R | 277 mm | 227.6 mm (pot tap at 76.6 mm) | 3 | 0.3 |
| AUDIO_IN_L J4.T → A1.16 | 213 mm | 140.9 mm | 8 | 0.3 |
| AUDIO_MIC_IN_R C12.2 → A1.17 | 171 mm | 53.0 mm | 1 | 0.2 |
| Pot wiper → C2 / C3 | — | 14.6 / 42.8 mm | 0 / 4 | 0.3 |
| HEADPHONE_OUT_L/R C6/C7 → J7 | — | 12.1 / 12.1 mm | 0 | 0.3 |
- Everything is shorter (−28 % to −69 %) and 0.1 → 0.3 mm. The line outputs still traverse the board (Daisy bottom-centre → J5 top-centre) because the jacks are on the rear edge; both run 94 % on F.Cu over the B.Cu pour. **F-030: improved, residual JUDGMENT** (keep as "tidy", not a defect).
- The volume pot is at the amp *input* (Pass 3 §5); the R-channel wiper lead to C3 is 42.8 mm with 4 vias vs 14.6 mm/0 vias for L — asymmetric but a 10 k source into a 22 k input; negligible.
- J4 ring is now tied to GND (rev-2 "floating ring" item from F-024 resolved).
- TPA6110A2 decoupling/bulk cap (F-031) → Pass 2.

## 6. I2C (F-027) → N/A
J2, `/I2C_SCL`, `/I2C_SDA`, `/OLED_HOT`, FB4-OLED, C14/C17 (old), R21 (10 Ω) are gone; Daisy pins 12/13 are now the right encoder A/B. No I2C bus exists in rev 3. F-027 is **N/A**.

## 7. LED driver signal lines
| GPIO net | Daisy pin | → R (1 k) | GPIO→R | R→base | Extra nodes |
|---|---|---|---|---|---|
| `/LED_1_R` | 27 | R36 → Q2 | 48.9 mm/5 vias | 36.3 mm | none |
| `/LED_1_G` | 26 | R35 → Q3 | 47.8/5 | 4.1 | none |
| `/LED_1_B` | 25 | R37 → Q1 | 44.6/5 | 42.7 | none |
| `/LED_2_R` | 24 | R39 → Q5 | 33.0/2 | 9.1 | none |
| `/LED_2_G` | 31 | R38 → Q6 | 50.5/2 | 4.2 | none |
| `/LED_2_B` | 30 | R40 → Q4 | 48.1/4 | 23.8 | none |
All twelve nets are clean 2-node nets, 0.2 mm wide. Base current 3.3 V − 0.7 V / 1 k ≈ 2.6 mA per channel (within any GPIO rating); the 3.3V-only pins 24/25/30 now see only a base-emitter junction. **Signal side PASS.** LED orientation (anode on collector, cathode via 300 Ω to +9 V) is flagged in Pass 3 R3-P3-09 for Pass 2.

## Findings (rev 3, Pass 5)
| ID | Class | Status | Finding | Evidence | Source |
|---|---|---|---|---|---|
| R3-P5-01 | JUDGMENT | confirmed | SPI OLED lines (88–124 mm, 1–7 vias, 0.3 mm) are electrically short at 10 MHz (0.5–0.7 ns ≪ 100 ns); no series termination — add 22–33 Ω on SCLK/SDIN at A1 or keep GPIO slew ≤ medium; keep SCLK ≤ 10 MHz | §1 | t_pd computed (ε_eff 2.86); SSD1322 10 MHz from memory, unverified |
| R3-P5-02 | PASS | confirmed | SD interface 24–41 mm, 0.3 mm, 47 k pull-ups retained, skew 95 ps | §2 | Daisy ref (rev-2 F-021) |
| R3-P5-03 | JUDGMENT | confirmed | USB FS pair matched to 0.4 mm but 9/11 vias (rev 2: 3/5); no impedance control; functionally fine at 12 Mb/s | §3 | — |
| R3-P5-04 | JUDGMENT | confirmed | MIDI UART RX/TX parallel to AUDIO_IN_L at 0.41/0.45 mm for 49/26 mm on the same layer — closest digital/analogue pairing on the board; separate on respin | `proximity.py` | 3W rule-of-thumb (judgment) |
| R3-P5-05 | PASS | confirmed | MIDI OUT/IN topology unchanged and correct; R4 1210/0.5 W absorbs a 0.33 W output-short dissipation (inferred rationale) | §4 | BOM rev 3 lines 30/37 |
| R3-P5-06 | JUDGMENT | confirmed | Audio runs shortened 28–69 % and widened to 0.3 mm; line-outs still 206/228 mm across the board; residual tidy-up only | §5 | — |
| R3-P5-07 | N/A | — | I2C pull-ups (F-027): bus removed | §6 | — |
| R3-P5-08 | PASS | confirmed | LED GPIO → 1 k → base nets clean (2-node), 2.6 mA base drive, no other loads | §7 | — |

## Rev-2 finding status (Pass-5 domain + wiring consistency)
| Rev-2 ID | Rev-3 status | Evidence |
|---|---|---|
| F-027 I2C no pull-ups | **N/A** | no I2C nets in rev 3 |
| F-028 USB pair asymmetry | **FIXED (length) / REGRESSED (vias 3→9, 5→11)**; still PASS functionally | §3 |
| F-029 MIDI | **PASS, unchanged**; R4 package change explained | §4 |
| F-030 audio runs long/thin | **IMPROVED, still open as judgment** (−28…−69 %, 0.3 mm) | §5 |
| F-031 TPA6110A2 bulk cap | → Pass 2 (not re-derived here) | — |
| F-014 wiring consistency (LED2 sch≠pcb) | **FIXED** (0 pad-level diffs, Pass 3 §1) | `sch_pcb_diff.py` |
| F-007 encoder clicks | **FIXED** (Pass 3 §3) | `net_geometry.py` |
| F-022 card detect | **STILL OPEN** | Pass 3 §2 |
| F-023 GND stubs | **FIXED** (pour); 2 cosmetic via stubs remain | DRC |
| F-024 ERC hygiene | **STILL OPEN** (14 NC + 4 PWR_FLAG) | `erc.json` |
| F-011 | N/A (superseded) | — |
