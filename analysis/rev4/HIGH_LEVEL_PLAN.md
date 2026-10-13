# Rev 4 — High-Level Plan
Governed by `analysis/SOURCE_OF_TRUTH.md` + the rev-3 and rev-4 addenda. Same six-pass structure as rev 2 and rev 3; the rev-3 scripts were rerun unchanged except for two refs (D6, FB7) that no longer exist.

| Pass | Status | Deliverable | Headline |
|---|---|---|---|
| 0 Inputs, provenance, baselines | COMPLETE 2026-10-13 | `PASS0_BASELINE.md` | all four inputs new and one generation; `.kicad_pro` identical; ERC 51 (same), DRC 576 / 0 unconnected |
| 1 Fab constraints | COMPLETE | `PASS1_FAB_CONSTRAINTS.md` | copper identical to rev 3 outside the patch; MK1/P2/U6-via margins unchanged; **0 GND vias**; 9 single-spoke thermals |
| 2 Power + LED drive | COMPLETE | `PASS2_POWER.md` | U6 ahead of R29/R30 ✓; 510/390 Ω ✓; D6/FB7 gone ✓; SD caps ✓; no inrush limiter; TPA bulk still missing |
| 3 Connectivity | COMPLETE | `PASS3_CONNECTIVITY.md` | sch ↔ pcb 0 diffs; encoder RC present, caps at the encoders; ERC unchanged |
| 4 BOM | COMPLETE | `PASS4_BOM.md` | 92/92 clean; LEDs still off-BOM; no hand-solder sheet; bridge part verified |
| 5 Signals | COMPLETE | `PASS5_SIGNALS.md` | routes unchanged; UART and TAC_SWITCH_2 beside audio |
| 6 Mechanical | COMPLETE | `PASS6_MECHANICAL.md` | J8 and holes unchanged → row 5 still open |
| Final synthesis | COMPLETE | `FINDINGS.md`, `FINAL_REPORT.md`, `OCT7_REVIEW_STATUS.md` | 57 entries; rev-3: 4 fixed / 20 pass / 4 settled / 37 open; Oct-7: 2c, 3c, 6b, 9, SD caps moved to DONE; 7 done differently; 5 open |
