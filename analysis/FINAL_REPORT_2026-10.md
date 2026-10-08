# WavetableController Round 2 — Final Red-Flag Report (technical version)

> **Shared version for Trey:** the plain-language report, reviewed with the user on 2026-10-07, is the Claude Doc "WavetableController Rev 2 Design Review" (https://claude.ai/code/artifact/6e30a194-1011-47d6-9039-bcceaed10b4a). It drops the back-silk artwork item (ruled irrelevant), treats the display, encoders and LEDs as hand-assembled, and omits finding IDs. This file remains the traceable technical version.
**Date:** 2026-10-07 · **Files reviewed:** the 2026-10-07 KiCad set (`WavetableController.kicad_sch/.kicad_pcb/.kicad_pro`), `Manifold_Gerbs_2026-10/` (proven byte-identical to a re-plot of that board, F-036) and the 2026-10-06 BOM · **Scope:** Round 2 Passes 0–6 complete (`HIGH_LEVEL_PLAN.md`), ledger entries F-036…F-073 (`FINDINGS.md`), every measurement scripted, every threshold fetched and archived (`datasheets_2026-10/`, `baseline_2026-10/`) per `SOURCE_OF_TRUTH.md`.
**Verification state:** 37 of 38 Round 2 findings confirmed; 1 plausible (F-065, Murata land pattern not fetched). Seven questions need Trey (⏳).
**Status of this set:** treated as the **pre-fab candidate** (⏳ Q1). Nothing below is "fabbed OK twice" — that only applies to the Round 1 boards.

---

## What Round 2 fixed (credit where due)
The new files close most of Round 1's Tier 1–2: the ground pour is in the board file and on both layers (F-006); the duplicate R21 is gone (F-013/F-020/F-025); the encoder clicks are routed (F-007); 0.1 mm trace length fell from 3850 mm to 73 mm and the 3V3 rail is 0.3 mm end to end (F-004); the USB pair is now matched to 0.4 mm (F-028); the I2C bus and its missing pull-ups no longer exist (F-027); analog runs are 25–70 % shorter and 3× wider (F-030); schematic and board agree pin for pin (F-014/F-015). Schematic ↔ board ↔ Gerbers are one consistent snapshot.

## Tier 1 — Will not work, or will damage parts, as designed (fix before ordering)

**1. The buck converter's input capacitor is rated 6.3 V on a 5–8.5 V node.** (F-049, confirmed)
C25 (10 µF 6.3 V, LCSC C1691) sits on the TPS62172's VIN, fed from the 9 V ladder. TI's reference design uses 10 µF **25 V** 0805. *Fix: 10 µF ≥ 16 V, 0805.*

**2. The 9 V supply path is undersized for the new display.** (F-050 + F-051, confirmed)
The Newhaven OLED draws 345 mA typical / 375 mA max at 3.3 V (datasheet Rev 6). Through the buck that is ≈ 0.2 A at the ladder input, and the whole board ≈ 0.3 A typical, ≈ 0.5 A worst case. That current passes in series through **four 0603 ferrite beads rated 200 mA** (FB3–FB6: 150–245 % of rating, ≈ 0.9 V of DCR drop) and then through **R31/R32, 3.3 Ω 0603 100 mW parts dissipating 120–175 mW** (400 mW if the LEDs ever work). The Daisy-branch resistors R29/R30 sit at 65 % of rating. *Fix: one ≥ 1 A bead (or none — the RC ladder already filters); ≥ 0.5 W resistors in the display branch, or take the buck off the ladder entirely (⏳ Q2). Voltage budget still clears the Daisy's 5 V minimum (≈ 5.8 V worst case) and the buck's 3 V minimum.*

**3. The RGB LEDs are still wired to never light, and still not on the BOM.** (F-052, F-002/F-034, confirmed; unchanged from Round 1)
Anodes on Daisy GPIO 24/25/26/27/30/31, cathodes through 300 Ω to the ≈ 6–8.5 V `/+9V_FLAG` net — permanently reverse-biased past the Cree part's 5 V limit, on three 3.3 V-only pins; now verified against the Cree pin drawing. The top-side stencil still contains exactly their 12 apertures while the BOM omits them. *Fix (if LEDs are wanted, ⏳ Q4): keep the 9 V supply and the 300 Ω (≈ 20 mA per colour, 330 Ω for margin) and add a low-side switch per colour — 9 V → 300 Ω → LED → N-MOSFET (2N7002-class) or ULN2003 channel → GND, GPIO on the gate/base. The Daisy-reference GPIO → R → LED → GND topology is wrong for this part: green/blue V_F is 3.1 V typ (3.8 max), so a 3.3 V pin leaves no headroom and they run dim. Parts (LCSC, verified 2026-10-07): 6 × 2N7002 C8545 (or AO3400A C20917) + 6 × 100 k gate pull-downs, or 1 × ULN2003A C7512 (≈1 V drop → 13 mA on G/B unless R → 220 Ω). **The six 300 Ω resistors must go to 1206:** once conducting, red dissipates ≈ 6 V × 20 mA ≈ 120–135 mW in a 100 mW 0603. PWM dimming: pins 24/25/26/31 have hardware timers (TIM1/TIM3/TIM2/TIM5), 27 and 30 do not. LEDs are hand-mounted, so no BOM change beyond the switches and resistors. If not wanted: delete LED1/LED2 and the six resistors.*

## Tier 2 — Will stall the order or mis-build the board (BOM and mechanical)

**4. BOM: one designator on two lines, three designators with no part.** (F-063, F-064, confirmed)
C17 is on both the 100 nF 0603 line and the 100 µF electrolytic line; the design's C17 is the electrolytic (stale Round 1 entry). U5 is an **ST L7805 DPAK** that exists nowhere in the schematic or board (⏳ Q5); S1/S2 are the Round 1 SMD tactile phantoms. JLCPCB will reject or question all of these. *Fix: delete C17 from line 8; delete lines 27 (S1/S2) and 32 (U5).*

**5. The display module has no way to be mounted.** (F-071, confirmed)
The NHD-2.7-12864WDW3 is an 82 × 47 mm glass-on-PCB module with four Ø2.5 mm mounting holes. Projected from the header (J8), those holes land at **(135.0, 79.3), (209.2, 79.3), (135.0, 121.8), (209.2, 121.8)** on the board — and there are no holes there. The module would hang from 20 soldered header pins. The area under it is clear on the front. *Fix: four Ø2.7 NPTH at those coordinates (±0.3 mm) and standoffs matched to the header height (⏳ Q7). The old `screen mounting solution.md` is for a different panel.*

**6. The front-panel artwork is now on the back silkscreen, over the parts.** (F-072, confirmed; class depends on ⏳ Q6)
3,900 filled polygons covering 60 % of the board moved from F.Silkscreen to B.Silkscreen and overprint **63 of the 92 back-side reference designators** — the side with every SMD part. Display, encoders and main buttons face front; pot, switches and all connectors face back. If the back is meant to be the user-facing legend, this is a hygiene item; if the artwork landed on the wrong layer, it is a build error.

**7. Two part/footprint mismatches on the new regulator.** (F-053, F-065)
The BOM's TPS62172 is the **fixed** 3.3 V part, but the schematic carries the **adjustable** TPS62170's 47 k/15 k feedback divider (TI: "connect FB to AGND on fixed output voltage versions"). Harmless today, but pick one (⏳ Q3). The inductor L1 is a Murata 2.0 × 1.6 mm part on an 0805 (2.0 × 1.25) land pattern — terminals overhang the pads by 0.35 mm (plausible; Murata drawing not fetched). *Fix: 0806/2016 land.* Also: SW → L1 is 8.3 mm (TI: keep the inductor close to SW); the 22 µF 0603 6.3 V output cap loses much of its capacitance at 3.3 V bias (TI uses 0805).

**7a. Encoder inputs need an RC filter (F-058, promoted to a fix on 2026-10-08).** ENCL/ENCR A and B go straight to Daisy pins on internal pull-ups over 80–146 mm; the user requires exactly one count per detent on heavy encoders. *Fix: 10 k pull-up to 3V3 + 10 nF to GND on each of the four A/B lines, placed near the Daisy; state-table quadrature decoder in firmware.*

## Tier 3 — Fab margins (JLCPCB capabilities fetched 2026-10-07)

**8. Three marginal annular-ring / clearance items, 3–5 µm under the absolute minimum** (F-016, F-008, F-040) — MK1 pads 0.175 mm ring vs 0.18; USB-C NPTH-to-copper 0.197 vs 0.20; the TPS62172 footprint's two 0.25 mm thermal vias with a 0.175 mm ring (and below the project's own 0.30 mm hole rule). All one-line footprint edits. The first two fabbed OK twice.
**9. Project-rule items that are inside JLCPCB's limits:** three +3V3_D tracks 0.451 mm from the edge and the SW1 pads at 0.414 mm (both ≥ 0.2 mm, F-041/F-047 — Round 1's "0.0 mm" was a measurement artefact); 588 silk strokes at 0.12 mm vs the 0.15 mm legend minimum (cosmetic, F-046); the last 73 mm of 0.1 mm trace, 46 mm of it forced by the mic amp's pads (F-037). DRC `min_track_width`/`min_clearance` are still 0.0 in the project file (F-005) — set them to 0.1 so KiCad guards the margins.

## Tier 4 — Robustness and hygiene (JUDGMENT)
- **+3V3_D still has a single 100 nF**; the SD card is 120 mm from it (F-054). Add 100 nF + 10 µF at P1. The resistive half of Round 1's F-019 is fixed by the 0.3 mm trunk.
- **Headphone amp:** TI's recommended ≥ 10 µF bulk cap near the TPA6110A2 is still absent (F-031); no 5 pF compensation cap across R14/R15 (F-069). Gain, HPF, mid-rail rule and output coupling all pass.
- **Crosstalk:** AUDIO_OUT_R runs 25 mm at 0.20 mm from the TAC_SWITCH_2 line; AUDIO_IN_L runs 43 mm beside the MIDI UART (F-070). Slow aggressors; move 0.5 mm.
- **FB1 has both pins on GND** — a no-op part (F-060). Delete, or use it as the AGND/DGND bridge.
- **Firmware note:** Daisy pin 10 is SPI1_MISO and is used as the TAC_SHIFT_R button while SPI1 drives the display — open SPI1 TX-only (F-061).
- SD card-detect half-wired (F-022) — **not needed**, card is never hot-swapped; ERC hygiene — 14 no-connect flags + 4 PWR_FLAGs would take ERC to zero (F-059); no chassis mounting holes (F-032); no fiducials; no hand-assembly list for 18 THT parts incl. the two THT caps at the display connector (F-026); nine single-spoke GND pads (F-042, accepted).

## Noise — which items matter, ranked
Round 1's original complaint was display noise. Rev 2 fixed the structural cause (display off the shared 3V3 rail onto its own buck + two-stage RC ladder; GND plane on both layers with 225 stitching vias; 0.3 mm 3V3_D; shorter, wider analog runs). Of the findings above, these still move the noise floor, biggest first:

1. **F-050 saturated beads.** FB3–FB6 (200 mA) at 0.3–0.5 A are inert — the protection they were added for is absent. One ≥ 1 A bead restores it. The 3.3 Ω / 100 µF stages (f_c ≈ 480 Hz each, two in series per branch) are the real filter and are good.
2. **F-049 / F-053 buck (Tier 1 item 1 and Tier 2 item 7).** Three simple actions: 16 V input cap; L1 moved next to the SW pin (now 8.3 mm, a loop antenna); 0805 output cap (22 µF 0603 ≈ half value at 3.3 V). Audio parts 33 mm and nearest audio trace 60 mm from the SW node — adequate.
3. **F-054 3V3_D single 100 nF.** SD bursts, 120 mm to the nearest cap; rail also feeds the MIDI opto. 100 nF + 10 µF at P1.
4. **F-031 / F-069 headphone amp.** +3V3_A (headphone + mic amps) carries one 100 nF; TI's ≥ 10 µF bulk cap is against THD/oscillation with long leads; the 5 pF compensation cap is a stability item (hiss/whine if marginal).
5. **F-070 trace neighbours.** AUDIO_OUT_R 0.20 mm from TAC_SWITCH_2 for 25 mm; AUDIO_IN_L beside USART1_RX for 43 mm. Slow aggressors → click on button press / tick on MIDI traffic. Move 0.5 mm.
6. **F-060 FB1.** If it was meant as an AGND/DGND split, don't: one stitched plane is better for this board; delete it.

No noise effect: F-063/F-064 BOM, F-071 mounting, Tier 3 margins, F-065 pads (weak joint → intermittent at most). Fixing F-052 removes six resistors from the 9 V ladder.

## SD card 4-bit mode (asked 2026-10-07)
Nothing on the Rev 2 layout prevents SDMMC 4-bit; the Round 1 failure most likely came from power at the card, which is unchanged.

| Requirement | Rev 2 | Round 1 |
|---|---|---|
| D0–D3, CMD, CLK on SDMMC1 pins (Daisy 2–7) and the right microSD pads | ✓ | ✓ |
| 47 k pull-ups on CMD, D0–D3 (Daisy Fig 1.6) | ✓ R7–R11 | ✓ |
| Length / skew | 27–49 mm @ 0.3 mm, skew 22 mm ≈ 150 ps vs 20 ns bit at 50 MHz | 89–108 mm, mostly 0.1 mm |
| Crosstalk | no SD line within 0.6 mm of another trace for > 2 mm | — |
| **Power at P1 VDD** | **120 mm to the only cap (C1 100 nF)** — F-054 | same, over 0.1 mm |

4-bit HS bursts ≥ 100 mA with no local cap → rail dips at the card → CRC errors → fallback/failure. Fix: 100 nF + 10 µF at P1. libDaisy `SdmmcHandler::Config::Defaults()` = `BITS_4`, `FAST` (50 MHz), so a Round 1 build that only worked at 1-bit points at the board. Bench test on a Round 1 board: 10 µF across P1 VDD/VSS, retry 4-bit.

**Target: 4-bit at 50 MHz** (`Speed::FAST` = SD high-speed mode at 3.3 V, libDaisy default). Not `VERY_FAST` (100 MHz): libDaisy calls it overclocked; SDR50/SDR104 require 1.8 V signalling the Daisy does not provide. Card choice: name-brand, A1 or better; packaging speeds (150–195 MB/s) are UHS-reader figures, unreachable here — the bus tops out ≈ 25 MB/s. If a card fails at 50 MHz, try `STANDARD` (25 MHz) before blaming the board.

## What passed (verified, cited)
Provenance: board file ↔ Gerbers byte-identical; sch ↔ pcb 0 differences; DRC 0 unconnected. Power: AGND/DGND tied; VIN in range; 35 V electrolytics on 9 V nodes; rail copper 0.5 mm (1.45 A) / 0.3 mm (1.0 A); GND zone on both layers with 225 stitching vias; local caps at every IC within 6 mm; buck LC per TI reference; EN/VOS/PG per datasheet. Connectivity: every Daisy pin on the right function; display connector matches Newhaven's 4-wire SPI table exactly (BS1/BS0, D/C, SCLK, SDIN, /RES, /CS, N/C pins); tactile switches wired correctly for the footprint; USB CC 5.1 k; SD 47 k pull-ups; MIDI in = TRS type A with the opto's own 270 Ω test-condition pull-up, out = 10/33 Ω 3.3 V practice; mic amp = MAX9814 EV-kit configuration pin for pin; USB ESD pinout correct. Fab: vias 0.6/0.3; copper spacing 0.15 vs 0.10; hole-to-hole 0.50; PTH/via/NPTH-to-track all above minimum; mask bridges 0.15 vs 0.10; drills in range. BOM: 80/80 shared designators match the LCSC listings. Mechanical: 0 courtyard overlaps; all three exposed pads stencilled; outline identical to the fabbed board; nothing under the display on the front.

## The seven questions for Trey
1. **Has this 2026-10 Gerber set been sent to JLCPCB**, or is it the candidate? (Decides whether Tier 1 is "fix now" or "we have boards that will cook their 3.3 Ω resistors".)
2. **Was the display branch meant to share the 3.3 Ω / 100 µF ladder?** A buck tolerates ripple; 0603 resistors and 200 mA beads do not tolerate 0.2–0.5 A.
3. **TPS62170 (adjustable) or TPS62172 (fixed)?** The schematic says one, the BOM the other.
4. **Are the LEDs meant to be populated this round?** If yes, the drive must be rewired first.
5. **What is BOM U5 (L7805)?** A plan the buck replaced, or is a 5 V rail still intended somewhere?
6. **Which side faces the user?** The artwork is on the back silk; the display is on the front.
7. **How is the Newhaven module held** — header only, or standoffs through its four holes?

---
*Supporting detail: `PASS0_BASELINE_2026-10.md` … `PASS6_MECHANICAL_2026-10.md`; ledger `FINDINGS.md` (F-036…F-073); thresholds in `datasheets_2026-10/` and `baseline_2026-10/`.*
