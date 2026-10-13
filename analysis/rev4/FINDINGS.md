# Rev 4 Findings Ledger — WavetableController
**Date:** 2026-10-13 · Rules: `analysis/SOURCE_OF_TRUTH.md` + the rev-3 and rev-4 addenda. Never delete a finding. Full evidence in the per-pass reports; this file is the index. Settled facts (9 V only; Würth LED, polarity correct; 3.3 V-only pins 24/25/28/29/30; Pedal-kit power entry) are not re-opened.

## Part A — Rev-4 findings by pass (ids R4-Pn-nn; one line each, evidence in the pass report)

### Pass 1 — Fab constraints (`PASS1_FAB_CONSTRAINTS.md`)
| ID | Class | Status | Finding |
|---|---|---|---|
| R4-P1-01 | ZERO-MARGIN | confirmed | 74.9 mm / 68 segs of 0.10 mm copper, identical to rev 3 |
| R4-P1-02 | VIOLATION (marginal) | confirmed | MK1 ring 0.175 mm (F-016 carry) |
| R4-P1-03 | VIOLATION (marginal) | confirmed | P2 NPTH-to-GND-pad 0.1966 mm (F-008 carry) |
| R4-P1-04 | JUDGMENT | confirmed | U6 EP vias 0.25 hole / 0.60 pad; project DRC errors |
| R4-P1-05 | JUDGMENT | confirmed | SW1 0.414 / /+3V3_D 0.451 mm to edge: project 0.5 rule only |
| R4-P1-06 | JUDGMENT | confirmed | 9 single-spoke GND pads (rev 3's 8 + C28.1) |
| R4-P1-07 | JUDGMENT | confirmed | 2 dangling vias /LED_2_R, /LED_2_B |
| R4-P1-08 | JUDGMENT | confirmed — **revised 2026-10-13** (Trey: all parts on the bottom; bottom plane is one piece) | 0 GND stitching vias / 15 top fragments = optional tidying. What remains: 10 bottom IC ground pins (U2, U3, U4 ×4, U6 ×3) reach the plane only through single 0.1–0.3 mm stubs of 1.2–4.8 mm; 9 single-spoke GND pads |
| R4-P1-09 | PASS | confirmed | No copper islands |
| R4-P1-10 | PASS | confirmed | Hole spacing, hole-to-copper, mask, tenting all pass |
| R4-P1-11 | PASS | confirmed | DRC at JLC minimums: 0 clearance / width errors |
| R4-P1-12 | JUDGMENT | confirmed | `.kicad_pro` DRC minimums still zero (F-005 carry) |

### Pass 2 — Power + LED drive (`PASS2_POWER.md`)
| ID | Class | Status | Finding |
|---|---|---|---|
| R4-P2-01 | PASS | confirmed | U6 fed ahead of R29/R30; /+9V_FLAG ≈ 8.1 V, load-independent (row 2c) |
| R4-P2-02 | PASS | confirmed | LED resistors 510/390 Ω → 11.6/12.1 mA, 69/57 mW (row 3c, decision 5a) |
| R4-P2-03 | JUDGMENT (doc) | confirmed — documentation only (hand-soldered Würth confirmed 2026-10-13) | Schematic still names CLS6B-FKW; LEDs on no BOM sheet |
| R4-P2-04 | PASS | confirmed | D6 and FB7 removed; bridge now 1N5817W SOD-123FL (row 9) |
| R4-P2-05 | JUDGMENT | confirmed | No inrush limiter (decision 5e); bulk 700 → 310 µF, unlimited cap 200 → 100 µF, path stiffer (≈ 30 A bound); diodes fine (25 µs pulse vs 25 A / 8.3 ms), contacts not |
| R4-P2-06 | PASS | confirmed | SD socket decoupled: C28 10 µF 5.2 mm, C27 100 nF 6.9 mm from P1.4 (decision 5d) |
| R4-P2-07 | JUDGMENT | confirmed | Extra 10 µF at A1.38 not added; C28 at 27.9 mm serves it |
| R4-P2-08 | JUDGMENT | confirmed | TPA6110A2 still without ≥ 10 µF; 4.8 mm of 0.1 mm on /+3V3_A (F-031 carry) |
| R4-P2-09 | PASS | confirmed | TPS62172 loop unchanged; L1 on the Murata pattern (row 6b) |
| R4-P2-10 | PASS | confirmed | Daisy VIN 6.8–7.5 V; grounds tied; reverse polarity by bridge; 3.3 V-only pins behind 1 k bases |
| R4-P2-11 | JUDGMENT | confirmed | 4 PWR_FLAGs still missing |
| R4-P2-12 | JUDGMENT (doc) | confirmed | Refdes repurposed again (C19–C22, R31/R32) |

### Pass 3 — Connectivity (`PASS3_CONNECTIVITY.md`)
| ID | Class | Status | Finding |
|---|---|---|---|
| R4-P3-01 | PASS | confirmed | sch ↔ pcb 112 ↔ 112, 0 dups, 0 real pad-net diffs |
| R4-P3-02 | PASS | confirmed | 4 × 10 k encoder pull-ups present and routed (row 7) |
| R4-P3-03 | JUDGMENT | confirmed — **accepted as built** (no room near the Seed, Kyle 2026-10-13) | 4 × 10 nF at the encoders on the back, 63–111 mm from the Daisy pins |
| R4-P3-04 | PASS | confirmed | Encoder clicks routed (unchanged) |
| R4-P3-05 | JUDGMENT | confirmed | /RES_SPI still floating (no 10 k) |
| R4-P3-06 | JUDGMENT | confirmed | 14 NC + 4 PWR_FLAG ERC items unchanged |
| R4-P3-07 | JUDGMENT | plausible ⏳ | Headphones1 taper / rotation sense (Trey) |
| R4-P3-08 | PASS | confirmed | J8 = NHD table 20/20 |
| R4-P3-09 | JUDGMENT | confirmed | /SWA card detect unusable; no spare pin |
| R4-P3-10 | PASS | confirmed | SD caps wired at P1.4 |

### Pass 4 — BOM (`PASS4_BOM.md`)
| ID | Class | Status | Finding |
|---|---|---|---|
| R4-P4-01 | JUDGMENT (doc; was VIOLATION) | confirmed — downgraded 2026-10-13: Trey hand-solders Würth 150505M173300 | LED1/LED2 on no BOM line; F.Paste = their 12 apertures; needs a hand-solder sheet, not an SMT line |
| R4-P4-02 | PASS | confirmed | L1 footprint fixed in sch + PCB |
| R4-P4-03 | JUDGMENT | confirmed | No hand-assembly sheet (18 THT + LEDs) |
| R4-P4-04 | JUDGMENT | confirmed | Position-file exclusion only on J3–J7 |
| R4-P4-05 | JUDGMENT | confirmed | File hygiene unchanged; D2–D5 Footprint cell says SOD-323 for a SOD-123FL part |
| R4-P4-06 | JUDGMENT (doc) | confirmed | Refdes repurposed between rev 3 and rev 4 |
| R4-P4-07 | JUDGMENT (cost) | confirmed | Extended parts incl. new D2–D5 C169541; R35–R40 avoidable |
| R4-P4-08 | PASS | confirmed | 92/92 values; 4/4 new LCSC numbers verified; bridge fits its pads |

### Pass 5 — Signals (`PASS5_SIGNALS.md`)
| ID | Class | Status | Finding |
|---|---|---|---|
| R4-P5-01 | JUDGMENT | confirmed | SPI OLED unterminated (optional series R / slew) |
| R4-P5-02 | JUDGMENT | confirmed | MIDI UART beside AUDIO_IN_L 0.41/0.45 mm for 49/26 mm |
| R4-P5-03 | JUDGMENT | confirmed | /TAC_SWITCH_2 beside AUDIO_OUT_R 0.20 mm for 27 mm (and OUT_L 0.70 / 32 mm) |
| R4-P5-04 | JUDGMENT | confirmed — accepted as built | Encoder RC caps at the encoder end: no termination at the MCU input; keep the state-table decoder |
| R4-P5-05 | PASS | confirmed | SD, USB, MIDI, audio, LED-driver nets unchanged from rev 3 |

### Pass 6 — Mechanical (`PASS6_MECHANICAL.md`)
| ID | Class | Status | Finding |
|---|---|---|---|
| R4-P6-01 | JUDGMENT | confirmed | Back-side artwork: 447 silk warnings, refdes buried, nothing on a pad |
| R4-P6-02 | ZERO-MARGIN | confirmed | Refdes 1.0 / 0.15 mm; outlines 0.12 mm |
| R4-P6-03 | PASS | confirmed | Courtyards clean |
| R4-P6-04 | JUDGMENT (doc; was VIOLATION) | confirmed — hand-solder confirmed | Top stencil = LEDs; LEDs off-BOM (F-034 carry); stencil apertures are harmless for a hand-fitted part |
| R4-P6-05 | JUDGMENT | confirmed — **ACKNOWLEDGED, deferred** (screen not mounted in this build, Kyle 2026-10-13) | No mounting holes for board or module; J8 not moved (row 5) |
| R4-P6-06 | JUDGMENT | confirmed | Module fits only toward +y; buck in the audio corridor |
| R4-P6-07 | JUDGMENT | confirmed | Headphones1 bushing 9 mm outside the outline |
| R4-P6-08 | JUDGMENT | confirmed | Hand-assembly list missing |
| R4-P6-09 | PASS | confirmed | Outline unchanged |
| R4-P6-10 | PASS | confirmed | Texts mirrored; front refdes clear |

## Part B — Status of every rev-3 finding in rev 4

| Rev-3 ID | Short | **Rev-4 status** | Rev-4 ref |
|---|---|---|---|
| R3-P1-01 | 74.9 mm of 0.1 mm copper | STILL OPEN (identical) | R4-P1-01 |
| R3-P1-02 | MK1 ring 0.175 | STILL OPEN | R4-P1-02 |
| R3-P1-03 | P2 NPTH 0.197 | STILL OPEN | R4-P1-03 |
| R3-P1-04 | U6 0.25 vias | STILL OPEN | R4-P1-04 |
| R3-P1-05 | edge 0.414/0.451 vs project 0.5 | STILL OPEN (judgment) | R4-P1-05 |
| R3-P1-06 | 8 single-spoke thermals | STILL OPEN, **+1** | R4-P1-06 |
| R3-P1-07 | 2 dangling vias | STILL OPEN | R4-P1-07 |
| R3-P1-08 | 0 GND stitching vias | STILL OPEN, **re-scoped** to the bottom IC ground stubs (top stitching optional) | R4-P1-08 |
| R3-P1-09…13 | islands / spacing / clearance / mask passes | PASS re-verified | R4-P1-09/10/11 |
| R3-P1-14 | DRC minimums zero | STILL OPEN | R4-P1-12 |
| R3-P2-01, -02 | LED polarity / footprint | REFUTED (settled) | — |
| R3-P2-03 | LED symbol labels / value | STILL OPEN (doc) | R4-P2-03 |
| R3-P2-04 | LED resistor values | **FIXED** | R4-P2-02 |
| R3-P2-05 | inrush | STILL OPEN (improved by subtraction) | R4-P2-05 |
| R3-P2-06 | D6 redundant, 4 beads, 2 π-filters | **FIXED** (D6 + 2nd filter gone; 4 beads remain) | R4-P2-04 |
| R3-P2-07 | Daisy VIN etc. | PASS re-verified | R4-P2-10 |
| R3-P2-08 | TPS62172 loop / vias | STILL OPEN (unchanged) | R4-P2-09, R4-P1-04 |
| R3-P2-09 | U6 sizing | PASS re-verified | R4-P2-09 |
| R3-P2-10 | 3V3_D one cap, SD 120 mm | **FIXED** at the socket | R4-P2-06 |
| R3-P2-11 | TPA 10 µF | STILL OPEN | R4-P2-08 |
| R3-P2-12, -13 | ampacity, 3.3 V-only pins | PASS re-verified | R4-P2-10 |
| R3-P2-14 | PWR_FLAGs | STILL OPEN | R4-P2-11 |
| R3-P3-01, -02, -03, -08 | consistency, annotation, clicks, J8 | PASS re-verified | R4-P3-01/04/08 |
| R3-P3-04 | /RES_SPI floats | STILL OPEN | R4-P3-05 |
| R3-P3-05 | OLED rail domain | STILL OPEN (judgment, unchanged) | — |
| R3-P3-06 | ERC flags | STILL OPEN | R4-P3-06 |
| R3-P3-07 | Headphones1 taper | STILL OPEN ⏳ | R4-P3-07 |
| R3-P3-09 | LED polarity (cross-ref) | N/A (refuted) | — |
| R3-P3-10 | /SWA | STILL OPEN | R4-P3-09 |
| R3-P3-11 | via stubs | STILL OPEN (cosmetic) | R4-P1-07 |
| R3-P4-01 | LEDs off BOM | STILL OPEN | R4-P4-01 |
| R3-P4-02 | L1 land pattern | **FIXED** | R4-P4-02 |
| R3-P4-03 | hand-assembly sheet | STILL OPEN | R4-P4-03 |
| R3-P4-04 | pos-file flags | STILL OPEN | R4-P4-04 |
| R3-P4-05 | BOM hygiene | STILL OPEN | R4-P4-05 |
| R3-P4-06 | refdes repurposed | STILL OPEN, repeated | R4-P4-06 |
| R3-P4-07 | Extended parts | STILL OPEN | R4-P4-07 |
| R3-P4-08 | BOM passes | PASS re-verified | R4-P4-08 |
| R3-P5-01 | SPI termination | STILL OPEN (judgment) | R4-P5-01 |
| R3-P5-02 | SD | PASS | R4-P5-05 |
| R3-P5-03 | USB vias | STILL OPEN (judgment) | R4-P5-05 |
| R3-P5-04 | UART beside audio | STILL OPEN | R4-P5-02 |
| R3-P5-05 | MIDI | PASS | R4-P5-05 |
| R3-P5-06 | audio runs | STILL OPEN (judgment) | R4-P5-05 |
| R3-P5-07 | I2C | N/A | — |
| R3-P5-08 | LED signal lines | PASS | R4-P5-05 |
| R3-P6-01 | back artwork | STILL OPEN | R4-P6-01 |
| R3-P6-02 | refdes at minimum / outlines 0.12 | STILL OPEN | R4-P6-02 |
| R3-P6-03 | courtyards | PASS | R4-P6-03 |
| R3-P6-04 | paste vs BOM (LEDs) | STILL OPEN | R4-P6-04 |
| R3-P6-05 | no mounting holes | STILL OPEN | R4-P6-05 |
| R3-P6-06 | module orientation / corridor | STILL OPEN | R4-P6-06 |
| R3-P6-07 | Headphones1 bushing | STILL OPEN | R4-P6-07 |
| R3-P6-08 | hand-assembly list | STILL OPEN | R4-P6-08 |
| R3-P6-09, -10 | outline, texts | PASS | R4-P6-09/10 |

## Part C — Rev-3 scorecard (65 entries)

| Outcome | Count | IDs |
|---|---|---|
| FIXED | 4 | R3-P2-04, R3-P2-06, R3-P2-10, R3-P4-02 |
| PASS re-verified | 20 | R3-P1-09…13, R3-P2-07/09/12/13, R3-P3-01/02/03/08, R3-P4-08, R3-P5-02/05/08, R3-P6-03/09/10 |
| N/A / refuted (settled) | 4 | R3-P2-01, R3-P2-02, R3-P3-09, R3-P5-07 |
| STILL OPEN | 37 | everything else in Part B; of these, R3-P2-05 improved (bulk reduced) and R3-P1-06 worsened by one pad |

## Part D — Rev-2 findings (F-001…F-035)
Statuses as in `analysis/rev3/FINDINGS.md` Part B, with these changes in rev 4: **F-019** (3V3_D decoupling) → FIXED at the SD socket (the trunk and the socket cap are both done); everything else unchanged (F-002/F-034 LEDs off-BOM, F-005, F-008, F-016, F-022, F-024, F-026, F-031, F-032, F-033 still open; F-004 at 74.9 mm).

**Not-a-finding / decision register:** USB-C data-only by design; 9 V barrel power; LED polarity (Würth); the Cree names printed by `sch_pcb_diff.py` are a script artefact; **display not mounted in this build (row 5 deferred); LEDs hand-soldered Würth 150505M173300; encoder caps at the encoder end accepted** (all Kyle, 2026-10-13).
