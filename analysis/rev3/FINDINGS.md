# Rev 3 Findings Ledger — WavetableController
**Date:** 2026-10-09 · Rules: `analysis/SOURCE_OF_TRUTH.md` + `SOURCE_OF_TRUTH_ADDENDUM.md`. Never delete a finding. Full evidence lives in the per-pass reports (`PASS0_BASELINE.md`, `PASS1_FAB_CONSTRAINTS.md`, `PASS2_POWER.md`, `PASS3_CONNECTIVITY.md`, `PASS4_BOM.md`, `PASS5_SIGNALS.md`, `PASS6_MECHANICAL.md`); this file is the index.

## Part A — New / carried findings in rev 3

Class: VIOLATION (measured fact breaks a cited rule) · ZERO-MARGIN · JUDGMENT · PASS (verified OK, recorded so it is not re-derived). Status: confirmed = independently verified; plausible = single method, or blocked on information only Trey has.

### Pass 2 — Power distribution & LED drive (`PASS2_POWER.md`)

| ID | Class | Status | Finding | Threshold source |
|----|-------|--------|---------|------------------|
| R3-P2-01 | **VIOLATION** | **confirmed** (netlist chain + Cree p.9 pin drawing, verified twice: Pass 2 script and coordinator's independent netlist/drawing check) | **LEDs still reverse-biased.** Cree CLS6B-FKW pads 1/3/5 are anodes; the netlist puts exactly those pads on the Q1–Q6 collectors and pads 2/4/6 (cathodes) through 300 Ω to /+9V_FLAG. A low-side NPN switch needs supply→R→anode→cathode→collector. As drawn the LEDs can never light and see 5.5 V reverse vs VR max 5 V. The rev-2 F-001/F-018 polarity bug was carried through the new transistor stage unchanged. | Cree CLD-CT1475 rev 5 |
| R3-P2-02 | **VIOLATION** | plausible — needs Trey (which LED is actually bought) | **LED footprint ≠ named package.** CLS6B-FKW is a 4.7 × 1.5 mm single-row 6-lead part (pads at x = ±2.02/±1.21/±0.53); the custom `LED_RGB_5050-6_Retroactive Pin Out` is a two-column 5050 pattern (1.1 × 2.0 pads at x = ±2.40, y = 0/±1.70). The named part cannot be placed on it. With no LED BOM line (R3-P4-01) the physical part is unknown; if it is a generic 5050, R3-P2-01/03 must be re-checked against that part's pinout. | Cree datasheet mechanical; stock KiCad `LED_Cree-PLCC6_4.7x1.5mm` |
| R3-P2-03 | JUDGMENT | confirmed | Custom LED symbol pin labels are wrong for the named part (pad 1 "AR" is blue anode, pad 3 "AG" is red anode, pad 5 "AB" is green anode; pad 4 labelled "KR" twice). Nets were wired so colours come out right (/LED_x_R → pad 3 = red …): two errors cancel. Fix the labels so a future edit doesn't "correct" one of them. | Cree p.9 |
| R3-P2-04 | JUDGMENT | confirmed | 300 Ω 0603 LED resistors are within rating at the 9 V design case (43/24/22 mW of 100 mW) but the LEDs only get 11–12 / 8–9 mA because /+9V_FLAG is really ≈5.8 V (R31/R32 π-filter) and shared with the OLED buck input: dim LEDs. Re-value for the real rail, or feed the LEDs from the C19 node. (The 7 Oct ask for 1206 bodies only matters if a 12 V adapter, the jack's ceiling, were ever used.) | Cree Vf/IF; BOM 0603 rating |
| R3-P2-05 | JUDGMENT | confirmed | **No inrush limit:** 200 µF (C15 + C19) behind ≈0.2 Ω of bead DCR + Schottkys → ≈26 A peak from a stiff adapter through diodes rated 9 A surge and 2 A beads; 700 µF total, 23–44 mJ per plug-in or SW1 flip. NTC/series R before C15, or fewer bulk caps. | computed; BOM C727114 |
| R3-P2-06 | JUDGMENT | confirmed | Series-element audit: D6 is redundant (bridge already protects both polarities; third ≈0.4 V drop, ≈0.2 W SOD-323 at 0.5 A); four identical beads FB3/4/5/6 in series; the two 3.3 Ω π-filters make both rails load-dependent (DSY_VIN 6.4–7.1 V, /+9V_FLAG 5.7–5.9 V at 9 V). All within limits — simplify. | — |
| R3-P2-07 | PASS | confirmed | Daisy VIN 6.4–7.1 V at the 9 V design case, within 4–17 V; AGND/DGND tied; reverse polarity by D2–D5; 5 × 47k SD pull-ups unchanged. F-021 re-verified. | Daisy datasheet v1.0.5 as recorded in rev-2 PASS2 (host blocked) |
| R3-P2-08 | JUDGMENT | confirmed | TPS62172 layout loose: Cin+ 4.85 mm / Cin− 6.6 mm / Cout− 9.0 mm from the IC, VIN feed 0.2 mm; SW node 4.7 mm @0.2 (good); VOS at Cout, FB→AGND (good). Thermal vias Ø0.25 mm violate the project's own 0.30 mm min-hole rule (2 DRC errors) though inside JLCPCB's limit; R33 PG pull-up feeds nothing. | SLVSAT8E §11.1 |
| R3-P2-09 | PASS | confirmed | U6 sizing: OLED 345/375 mA vs 500 mA (69/75 %); 2.2 µH + 22 µF is the datasheet standard combo; Cin 10 µF; IL(peak) 0.53 A vs L1 1.4 A; U6 VIN 5.7–9 V in 3–17 V; J8 at default jumper, 4-wire SPI; 100 nF + 100 µF within 9.2 mm of J8.2. | SLVSAT8E; NHD datasheet l.244–250 |
| R3-P2-10 | JUDGMENT (F-019 carry) | confirmed | /+3V3_D trunk widened 0.1 → 0.3 mm (249 mm, 0.41 Ω) **but still a single 100 nF (C1 at the MIDI opto)**; A1.38 → C1 110.9 mm, SD P1.4 → C1 120.2 mm, no cap at the SD socket. Half of F-019 done. | IPC-2221 computed |
| R3-P2-11 | JUDGMENT (F-031 carry) | confirmed | TPA6110A2: C5 100 nF at 5.6 mm ✓; the datasheet's ≥10 µF near the amp is still absent; /+3V3_A has no bulk and keeps 4.8 mm of 0.1 mm trace. | SLOS314B (rev-2 archive) |
| R3-P2-12 | PASS | confirmed | IPC-2221 (1 oz, ΔT 10 °C): every power net OK; narrowest loaded 0.2 mm stubs ≤68 % of 0.74 A; beads ≤25 % of 2 A; 3.3 Ω 2512 ≤0.30 W of 1 W. | IPC-2221 computed |
| R3-P2-13 | PASS | confirmed | 3.3 V-only pins 24/25/30 now see only 1 kΩ → base (≤0.85 V); no path to the +9 V side; Ib 2.45 mA, Ic/Ib ≤9 → saturated. F-018 item 3 closed. | onsemi MMBT3904; rev-2 pin list |
| R3-P2-14 | JUDGMENT | confirmed | ERC `power_pin_not_driven` on A1 VIN, U6 VIN, U4 VDD, #PWR01 — diode/bead/resistor-fed rails lacking PWR_FLAGs (F-024 carry). | — |

### Pass 3 — Connectivity (`PASS3_CONNECTIVITY.md`)

| ID | Class | Status | Finding | Threshold source |
|----|-------|--------|---------|------------------|
| R3-P3-01 | PASS | confirmed | Schematic ↔ PCB fully consistent: 110 ↔ 110 parts, 0 duplicate refs, 0 pad-level net diffs over 396 pad/pin pairs, no one-file nets. | — |
| R3-P3-02 | PASS | confirmed | The apparent "unannotated U/L/RV/Q" symbols are `lib_symbols` definitions, not placed instances; 0 unannotated placed symbols; `Headphones1` is the dual pot in both files. (Withdraws the coordinator's pass-0 caveat.) | — |
| R3-P3-03 | PASS | confirmed | Encoder clicks routed with continuous copper: /ENCL_CLICK 170.6 mm / 6 vias to pin 22 (PC0), /ENCR_CLICK 190.6 mm / 10 vias to pin 29 (PA5), 0.3 mm; no external pull-up (libDaisy Switch default is internal PULLUP). | libDaisy (secondary) |
| R3-P3-04 | JUDGMENT | confirmed | /RES_SPI is a bare 2-node net: no pull-up/down or RC; floats until firmware drives it (NHD says only /SHDN is internally pulled high). Add 10 k to /+3V3_OLED. | NHD datasheet |
| R3-P3-05 | JUDGMENT | confirmed | OLED logic rail /+3V3_OLED (U6, from the 9 V side) is a different 3.3 V domain from Daisy /+3V3_D; levels OK (VIH 2.64 V); SSD1322 inputs can be driven before its VDD is up if U6 is slower than Daisy boot; low practical risk because Daisy GPIOs are high-Z through boot. | NHD datasheet |
| R3-P3-06 | JUDGMENT | confirmed | ERC hygiene: 14 missing NC flags (10 USB-C SS/SBU + J8 pins 3/9/15/18, all correct per NHD table) and 4 missing PWR_FLAGs. All false positives. F-024 carry. | — |
| R3-P3-07 | JUDGMENT | plausible | Headphones1 is a **linear (B) taper** 10 k used as a volume control; signal on pin 1, GND on pin 3, so rotation sense depends on the PTD902 terminal order (datasheet unreachable). Prefer A-taper; verify CW = louder. | Bourns taper convention |
| R3-P3-08 | PASS | confirmed | J8 wiring matches the NHD serial pin table 20/20; BS1 = BS0 = GND → 4-wire SPI; D3–D7, R/W, E tied low; NC pins correct; /SHDN NC OK; Daisy pins 8/9/11 are SPI1 NSS/SCK/MOSI; DC/RES on plain GPIO. | NHD datasheet; KiCad symbol + libDaisy |
| R3-P3-09 | VIOLATION (cross-domain) | confirmed via R3-P2-01 | LED polarity reversed in netlist (anode → collector, cathode → 300 Ω → +9 V). Signal side (GPIO → 1 k → base) is clean. | → R3-P2-01 |
| R3-P3-10 | JUDGMENT | confirmed | F-022 unchanged: /SWA single-pin, SWB grounded — card detect unusable; all 40 Daisy pins now consumed, so wiring it needs a pin trade. | — |
| R3-P3-11 | info | confirmed | 2 single-layer via stubs on /LED_2_R, /LED_2_B (DRC via_dangling) — cosmetic. | — |

### Pass 4 — BOM three-way cross-check (`PASS4_BOM.md`)

| ID | Class | Status | Finding | Threshold source |
|----|-------|--------|---------|------------------|
| R3-P4-01 | **VIOLATION** | confirmed | **LED1/LED2 still absent from the BOM** while the board expects them: F_Paste has exactly 12 flashes mapping 12/12 to LED1/LED2 pads, both are in pos.csv. The only SMD parts in the "sch+pcb but not BOM" bucket. Boards will again return from assembly without LEDs (F-002/F-034 unchanged). | — |
| R3-P4-02 | JUDGMENT (strong) | confirmed | **L1 land pattern doesn't fit the part.** BOM C237554 = Murata DFE201610P-2R2M (2.0 × 1.6 mm); sch + PCB use `Inductor_SMD:L_0805_2012Metric` (pads 0.875 × 1.20 at ±1.062) instead of the stock `L_Murata_DFE201610P` (0.55 × 1.60 at ±0.725): pads 0.4 mm narrower than the terminations, ≈50 % of reference overlap, 0.5 mm overhang. Swap to the Murata footprint. | KiCad stock footprint (murata.com blocked) |
| R3-P4-03 | JUDGMENT | confirmed | Still no hand-assembly list (F-026): 18 THT parts off-BOM, now including the OLED-rail bulk caps C24 100 µF / C23 100 nF on /+3V3_OLED. | — |
| R3-P4-04 | JUDGMENT | confirmed | "Exclude from position files" set only on J3–J7; 13 other THT parts + the LEDs appear in the CPL (105 rows), which buries the two LED no-match entries at JLCPCB upload. | — |
| R3-P4-05 | JUDGMENT | confirmed | BOM file hygiene: footprint column numerically coerced on 24/36 rows ("0603" → 603.0), a leading newline in one cell, inconsistent designator spacing on 9 rows, mojibake on 20/36 comment rows. Harmless to JLCPCB (keys on LCSC #). | — |
| R3-P4-06 | JUDGMENT | confirmed | Refdes repurposed across revisions: C14 (rev-2 470 µF THT noise-fix cap) is now a 100 nF 0603; C17 100 nF → 100 µF; C15 10 µF/100 V → 100 µF/35 V. Rev-2 notes citing those refdes are stale. | — |
| R3-P4-07 | JUDGMENT (cost) | confirmed | Extended parts: U6, L1, R4 (C2907549; rev-2 C23140 was Basic), R29–R32, R35–R40 (C14676 1 k 5 % Extended; C21190 1 k 1 % is Basic — free swap), C3339 ×9, C727114 ×5. | JLCPCB part pages, fetched 2026-10-09 |
| R3-P4-08 | PASS | confirmed | 90/90 values consistent; R4 1210, C25/C26 0805, R29–R32 2512, nine 100 µF CP_Elec_6.3x7.7, U6 WSON-8 2x2 consistent in all three; 11/11 new LCSC numbers confirmed by MPN; U6 pin map lands on sensible nets. | JLCPCB part pages |

### Pass 5 — Signals (`PASS5_SIGNALS.md`)

| ID | Class | Status | Finding | Threshold source |
|----|-------|--------|---------|------------------|
| R3-P5-01 | JUDGMENT | confirmed | SPI OLED lines 88–124 mm, 1–7 vias, 0.3 mm, no stubs, no series termination; electrically short at 10 MHz (0.5–0.7 ns ≪ 100 ns). Optional 22–33 Ω on SCLK/SDIN or medium GPIO slew; keep SCLK ≤ 10 MHz (SSD1322 figure from memory, flagged). | t_pd computed |
| R3-P5-02 | PASS | confirmed | SD interface 24–41 mm (rev 2: 89–108), 0.3 mm, 47 k pull-ups, skew 95 ps. | Daisy ref design (rev-2 F-021) |
| R3-P5-03 | JUDGMENT | confirmed | USB FS pair matched to 0.4 mm (rev 2: 7.2 mm) but 9/11 vias (rev 2: 3/5); functionally fine at 12 Mb/s. | — |
| R3-P5-04 | JUDGMENT (new) | confirmed | /USART1_RX runs 49.1 mm parallel to AUDIO_IN_L at 0.41 mm, /USART1_TX 26.1 mm at 0.45 mm, same layer — the closest digital/analogue pairing on the board. Separate on respin. | 3W rule of thumb |
| R3-P5-05 | PASS | confirmed | MIDI OUT (10 Ω/33 Ω) and IN (0 Ω/220 Ω/H11L1/D1/270 Ω) unchanged; R4 0603 → 1210 explained by 0.33 W output-short dissipation (inferred). | — |
| R3-P5-06 | JUDGMENT | confirmed | Audio runs shortened 28–69 % and widened to 0.3 mm (OUT_L 206, OUT_R 228, IN_L 141, mic 53 mm); pot at the TPA6110A2 input; J5 line-out fed directly; J4 ring now grounded. | — |
| R3-P5-07 | N/A | — | I2C pull-ups (F-027): bus removed. | — |
| R3-P5-08 | PASS | confirmed | LED GPIO → 1 k → base nets clean 2-node, 2.6 mA base drive. | — |

### Pass 1 — Fab constraints and Pass 6 — Mechanical
#### Pass 1 — Fab constraints (`PASS1_FAB_CONSTRAINTS.md`)

| ID | Class | Status | Finding | Threshold source |
|----|-------|--------|---------|------------------|
| R3-P1-01 | ZERO-MARGIN (F-004 carry) | confirmed | 0.10 mm copper down from 3,850 mm to **74.9 mm / 68 segments**: U4 MAX9814 DFN fan-out (54 segs), U6 thermal stitching, USB fan-out (5), one 5.9 mm /USART1_TX run under LED2. All trunks are now 0.3 mm. Still exactly at JLCPCB's minimum where it remains. | JLCPCB caps 2026-10-09 (0.10/0.10, ±20 %) |
| R3-P1-02 | VIOLATION (marginal, F-016 carry) | confirmed | MK1 pads 1/2 annular ring 0.175 mm (1.0 pad / 0.65 drill) vs JLC absolute minimum 0.18; ENC posts and P2 shield at 0.20 (below the 0.25 recommended). Reproduced within 3 µm of rev 2 by an independent polygon method. | JLCPCB caps |
| R3-P1-03 | VIOLATION (marginal, F-008 carry) | confirmed | P2 USB-C GND pads 0.197 mm from the footprint's own 0.65 mm NPTH vs 0.20 minimum. Footprint-level defect, unchanged. | JLCPCB caps |
| R3-P1-04 | JUDGMENT | confirmed | U6 thermal vias 0.25 mm hole / 0.60 pad: legal at JLC (dia ≥ hole + 0.1, no surcharge at ≥ 0.45 dia) but trip the project's 0.30 min-hole rule (2 DRC errors) and add a drill tool. Make them 0.30. | JLCPCB caps; .kicad_pro |
| R3-P1-05 | JUDGMENT | confirmed | Copper-to-edge: SW1 pads 0.414 mm, /+3V3_D track 0.451 mm — both above JLC 0.2; the 5 DRC errors come only from the project's 0.5 rule. The SW1 outline notch is gone (F-010 FIXED). | JLCPCB caps |
| R3-P1-06 | JUDGMENT | confirmed | The 8 starved-thermal GND pads (TAC_SWITCH_1.3, U1.5, P2 A12/B1, R18.1, C9.1, U3.3, C10.1) are all connected — one 0.5 mm spoke each, U3.3 via one 0.3 mm track; 0 unconnected. Robustness only: reduce thermal gap or add GND tracks. | DRC |
| R3-P1-07 | JUDGMENT | confirmed | 2 dangling vias /LED_2_R (167.75, 145.9) and /LED_2_B (168.53, 145.74): leftovers with no F.Cu connection; nets fully routed elsewhere. Delete. | DRC |
| R3-P1-08 | JUDGMENT (strong) | confirmed | **Zero GND stitching vias.** F.Cu pour is 15 fragments (7,990 mm²) tied to the one-piece 12,852 mm² B.Cu plane only through component through-holes; 3 fragments hang on a single pad (TAC_SWITCH_1.3, MK1.1, ENCR1.C); 10 B-side GND pads (U2, U3, U4, U6) reach GND only by one thin track. Add stitching vias (every ~10–15 mm and at every F.Cu fragment). | — |
| R3-P1-09 | PASS | confirmed | No copper islands: all 19 fill fragments touch a GND pad (island removal = always). | — |
| R3-P1-10 | PASS | confirmed | Hole-to-hole via–via 0.50, pad–pad 0.75; NPTH-to-track 0.251, NPTH-to-pour 0.2505 (P2 aside, R3-P1-03). | JLCPCB caps |
| R3-P1-11 | PASS | confirmed | Via-hole-to-other-net copper 0.35; PTH-hole-to-other-net track ≥ 0.45. | JLCPCB caps |
| R3-P1-12 | PASS (F-012 re-confirmed) | confirmed | Min copper clearance 0.15 (U3/U4 pad gaps), else 0.20; DRC at 0.1/0.1 with netclass 0.1 → 0 errors. The 17 as-is clearance errors are F-009 netclass noise. | JLCPCB caps |
| R3-P1-13 | PASS | confirmed | Mask 1:1, min sliver 0.15 ≥ 0.10; all 244 vias one size (0.6/0.3), tented both sides; drill file = 244 × 0.3 + 2 × 0.25. | JLCPCB caps |
| R3-P1-14 | JUDGMENT (F-005 carry) | confirmed | .kicad_pro still has min_track_width 0.0 and min_clearance 0.0 — KiCad will not guard the 0.10 mm margin. Set to JLC values. | .kicad_pro |

#### Pass 6 — Mechanical & assembly (`PASS6_MECHANICAL.md`)

| ID | Class | Status | Finding | Threshold source |
|----|-------|--------|---------|------------------|
| R3-P6-01 | JUDGMENT (F-033 carry, changed) | confirmed | All 447 silk warnings are the **back-side artwork** (3,900 zero-stroke polygons running off all four edges; rev 2 had 88 polygons on F.Silk): over copper 199, over refdes 59, over outlines 138, edge-mounted outlines beyond the edge 25, art into J1's NPTH 2. No refdes lands on a pad. 97/102 B-side refdes are buried in the art — assembly unaffected, inspection/rework harder. | DRC at 0.15 silk clearance |
| R3-P6-02 | ZERO-MARGIN | confirmed | All 110 refdes are 1.0 mm / 0.15 mm — exactly JLC's legend minimum; footprint outlines are 0.12 mm stroke (below 0.15). | JLCPCB caps |
| R3-P6-03 | PASS | confirmed | 0 courtyard overlaps, 0 missing; 10 protrude past the outline (all panel-mounted parts; Headphones1 by 9.0 mm); C19/C20, C15/R29, C22/R32 courtyards touch at 0.00 mm. | — |
| R3-P6-04 | VIOLATION (F-034/F-002 carry) | confirmed | F.Paste = exactly LED1 + LED2's 12 apertures; LEDs absent from the BOM; B.Paste 260 apertures all covered. | — |
| R3-P6-05 | JUDGMENT (F-032 carry, widened) | confirmed | **No mounting holes at all, and none for the NHD module's 74.2 × 42.5 mm Ø2.5 pattern.** Projected hole sites (135.0, 81.3) / (209.2, 81.3) / (135.0, 123.8) / (209.2, 123.8) collide with R2/R5/U1 and sit 0.7 mm from C22. `screen mounting solution.md` describes a different display (Crystalfontz COG/ZIF). | NHD datasheet mechanical |
| R3-P6-06 | JUDGMENT | plausible (orientation inferred from datasheet views; confirm against Trey's STEP) | J8 (straight 1×20, pin 1 at (196.26, 81.30), pin 20 at (148.0, 81.30), F side) fits only with the module body toward +y: footprint x 131.1–213.1, y 78.8–126.3, clear of all F parts (≥ 3.9 mm to TAC_SWITCH_1/2, ≥ 13.7 mm to encoders); the −y orientation overhangs the top edge by 24.7 mm. Header, buck (U6/L1/C25/C26/FB7) and rail caps C23/C24 sit inside the x 165–200 audio corridor the rev-2 plan reserved. | NHD datasheet; REV2_OLED_PLAN |
| R3-P6-07 | JUDGMENT | confirmed | Headphones1 (Alps RK097-style dual, B side at (224.75, 146.5)) bushing exits the bottom edge 9 mm outside the outline, 16.75 mm from the PHONES jack J7 — panel cut-out needed. Pads 1.0/1.8 fine. | — |
| R3-P6-08 | JUDGMENT (F-026 carry) | confirmed | Hand-assembly list still missing; 18 THT parts incl. new C23, C24, J8, Headphones1. | — |
| R3-P6-09 | PASS | confirmed | Edge.Cuts = one closed 132-vertex polygon, 165.30 × 101.80 mm, R≈9 corners, no notches, no stray items. | — |
| R3-P6-10 | PASS | confirmed | Back texts correctly mirrored; front refdes unobstructed. | — |

## Part B — Status of every rev-2 finding in rev 3

| Rev-2 ID | Rev-2 finding (short) | Rev-3 status | Evidence / rev-3 ref |
|---|---|---|---|
| F-001 | LED drive broken (300 Ω to +9V, GPIO anodes) | **STILL OPEN** | polarity unchanged through Q1–Q6 → R3-P2-01 |
| F-002 | LEDs missing from BOM | **STILL OPEN** | R3-P4-01 |
| F-003 | BOM S1/S2 phantom switches | **FIXED** | line removed, 0 BOM-only designators |
| F-004 | 3.85 m of 0.10 mm trace | **IMPROVED 98 %** (74.9 mm remains, still zero-margin) | R3-P1-01 |
| F-005 | DRC minimums zeroed in .kicad_pro | **STILL OPEN** | R3-P1-14 |
| F-006 | .kicad_pcb has no GND pour | **FIXED** | board-level GND zone filled on F.Cu + B.Cu; DRC 0 unconnected |
| F-007 | Encoder clicks unrouted | **FIXED** (on paper, pre-fab) | R3-P3-03 |
| F-008 | USB-C NPTH-to-copper 0.194 mm | **STILL OPEN** (0.197) | R3-P1-03 |
| F-009 | U3/U4 fine-pitch clearance DRC noise | **STILL OPEN** (config noise) | 17 identical clearance errors in drc_asis.json |
| F-010 | SW1 edge copper in notch | **FIXED** (notch removed; 0.414 mm) | R3-P1-05 |
| F-011 | ERC triage list | N/A (superseded by F-024) | |
| F-012 | DRC at JLC minimums: 0 width/spacing violations | **PASS again** | drc_jlc.json |
| F-013 | Duplicate refdes R21 | **FIXED** | 110 unique refs; R3-P3-01 |
| F-014 | LED2 wiring sch ≠ pcb | **FIXED** | 0 pad-level diffs |
| F-015 | Version/provenance timeline | **RESOLVED** | rev 3 sch and pcb are one generation (PASS0 §1) |
| F-016 | MK1 annular ring 0.175 mm | **STILL OPEN** | R3-P1-02 |
| F-017 | Gerber 93 vs pcb 94 vias | N/A | no rev-3 Gerbers |
| F-018 | LEDs reverse-biased, 3.3V-only pins exposed | **OPEN (items 1–2)** / item 3 **FIXED** | R3-P2-01 / R3-P2-13 |
| F-019 | 3V3_D impedance / single 100 nF | **PARTIAL** | trunk 0.3 mm; still one cap → R3-P2-10 |
| F-020 | PCB-only 10 Ω damper not in sch | **RESOLVED by redesign** | OLED_HOT branch removed |
| F-021 | Power checks that pass | **PASS re-verified** | R3-P2-07/12 |
| F-022 | SD card-detect half-wired | **STILL OPEN** | R3-P3-10 |
| F-023 | Dangling GND stubs | **FIXED** | pour present; 2 cosmetic via stubs → R3-P3-11 |
| F-024 | ERC hygiene (NC flags, PWR_FLAGs) | **STILL OPEN** (14 NC + 4 PWR_FLAG) | R3-P3-06 / R3-P2-14 |
| F-025 | Dup-R21 pick-and-place trap | **FIXED** | one R21 ↔ one BOM line |
| F-026 | No hand-assembly list | **STILL OPEN** | R3-P4-03 |
| F-027 | I2C no pull-ups | **N/A** | bus removed → R3-P5-07 |
| F-028 | USB pair asymmetry | **FIXED (length) / REGRESSED (vias)** | R3-P5-03 |
| F-029 | MIDI passes | **PASS unchanged** | R3-P5-05 |
| F-030 | Long thin audio runs | **IMPROVED** (judgment residual) | R3-P5-06 |
| F-031 | TPA6110A2 ≥10 µF bulk missing | **STILL OPEN** | R3-P2-11 |
| F-032 | No chassis mounting holes | **STILL OPEN, widened** (no module holes either) | R3-P6-05 |
| F-033 | Silk warnings cosmetic | **CHANGED** (art moved F→B, 143 → 447, still cosmetic) | R3-P6-01 |
| F-034 | Paste expects LEDs the BOM lacks | **STILL OPEN** | R3-P4-01 |
| F-035 | Mechanical passes | **PASS re-verified** | R3-P6-03/09/10 |

**Not-a-finding register (carry from rev 2):** USB-C is data-only by design; 9 V barrel power.

## Part C — Rev-2 scorecard (35 findings)

| Outcome | Count | IDs |
|---|---|---|
| FIXED / RESOLVED | 10 | F-003, F-006, F-007, F-010, F-013, F-014, F-015, F-020, F-023, F-025 |
| PASS re-verified | 4 | F-012, F-021, F-029, F-035 |
| IMPROVED / PARTIAL | 5 | F-004, F-018 (1 of 3), F-019, F-028, F-030 |
| STILL OPEN | 13 | F-001, F-002, F-005, F-008, F-009, F-016, F-022, F-024, F-026, F-031, F-032, F-033, F-034 |
| N/A in rev 3 | 3 | F-011, F-017, F-027 |
