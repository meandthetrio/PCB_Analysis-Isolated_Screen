# Rev 4 analysis index

Start with **`FINAL_REPORT.md`** (tiered red flags + questions for Trey). `FINDINGS.md` is the ledger: Part A = rev-4 findings by pass (ids R4-Pn-nn), Part B = status of every rev-3 finding, Part C = scorecard.

- `OCT7_REVIEW_STATUS.md` — every row of the 7 October "Rev 2 Design Review" doc re-scored against the rev-4 files (baseline: the rev-3 scoring on branch `claude/charming-meitner-c0w1jh`)
- `PASS0_BASELINE.md` — what changed rev 3 → rev 4, ERC/DRC baselines, threshold sources
- `PASS1_FAB_CONSTRAINTS.md` … `PASS6_MECHANICAL.md` — per-pass evidence
- `SOURCE_OF_TRUTH_ADDENDUM.md`, `HIGH_LEVEL_PLAN.md` — method and status
- `scripts/` — the rev-3 scripts (copied, paths re-pointed to `rev4/` and `kicad_out/rev4/`) plus `netlist_diff.py`; run with `python3 -I`
- Raw outputs regenerate with `kicad-cli`/`pcbnew` from `rev4/` into the git-ignored `kicad_out/rev4/`.

Inputs live in `rev4/`: `WavetableController.kicad_{pro,sch,pcb}` (pcb has the filled GND pour), `ManifoldRe_BOM_NEW - Excel Format (rev4).xls`, and `Gerbers/` (ManifoldGerbs.zip, Trey's plot of this board, 2026-10-13). `REV4_PASS1_GERBERS.md` in `rev4/` is the Gerber-only first look done before the KiCad files arrived.
