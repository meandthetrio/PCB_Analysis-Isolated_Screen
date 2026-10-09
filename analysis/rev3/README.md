# Rev 3 analysis index

Start with **`FINAL_REPORT.md`** (tiered red flags + questions for Trey). `FINDINGS.md` is the ledger: Part A = rev-3 findings by pass (ids R3-Pn-nn), Part B = status of every rev-2 finding, Part C = scorecard.

- `OCT7_REVIEW_STATUS.md` — every item of the 7 October "Rev 2 Design Review" doc scored against these files
- `PASS0_BASELINE.md` — what changed rev 2 → rev 3, ERC/DRC baselines, threshold sources
- `PASS1_FAB_CONSTRAINTS.md` … `PASS6_MECHANICAL.md` — per-pass evidence
- `SOURCE_OF_TRUTH_ADDENDUM.md`, `HIGH_LEVEL_PLAN.md` — method and status
- `scripts/` — the pcbnew/netlist scripts behind every measurement (`python3 -I`)
- Regenerate raw outputs with `kicad-cli`/`pcbnew` from `rev3/`; they live in the git-ignored `kicad_out/rev3/`.
