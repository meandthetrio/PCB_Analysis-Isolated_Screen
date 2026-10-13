# Rev 4 — High-Level Plan
Governed by `analysis/SOURCE_OF_TRUTH.md` + the rev-3 and rev-4 addenda. Same six-pass structure as rev 2 and rev 3.

| Pass | Status | Deliverable | Headline |
|---|---|---|---|
| 0 Inputs, provenance, baselines | **PARTIAL 2026-10-13** — schematic/project/Gerbers done; `.kicad_pcb` + BOM pending | `PASS0_BASELINE.md` | sch differs from rev 3 (D6/FB7 gone, encoder RC, SD caps, 390/510 Ω, L1 footprint); `.kicad_pro` identical to rev 3; ERC 51 (same set) |
| 1 Fab constraints | pending board file (Gerber-only pass in `rev4/REV4_PASS1_GERBERS.md`) | `PASS1_FAB_CONSTRAINTS.md` | |
| 2 Power + LED drive | schematic side done (`scripts/pass2/power_budget.py`); geometry pending | `PASS2_POWER.md` | |
| 3 Connectivity | ERC done; sch↔pcb diff pending | `PASS3_CONNECTIVITY.md` | |
| 4 BOM | pending rev-4 BOM | `PASS4_BOM.md` | |
| 5 Signals | pending board file | `PASS5_SIGNALS.md` | |
| 6 Mechanical | pending board file | `PASS6_MECHANICAL.md` | |
| Final synthesis | pending | `FINDINGS.md`, `FINAL_REPORT.md`, `OCT7_REVIEW_STATUS.md` | |
