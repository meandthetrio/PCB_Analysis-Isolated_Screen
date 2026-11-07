# Analysis folder index — ProtoBuild1

Start here: **`FINAL_REPORT.md`** — the tiered red-flag summary and the questions for Trey.
Everything else is supporting material; no finding lives only in this README.

## Reports
- `FINAL_REPORT.md` — final summary, Tiers 1–4, verified passes, questions for Trey
- `FINDINGS.md` — full ledger (PB-F-001…PB-F-030) behind the summary
- `HIGH_LEVEL_PLAN.md` — the pass plan the review followed (same six passes as the Manifold review)
- `SOURCE_OF_TRUTH.md` — methodology: which file is authoritative for what, verification rules
- `THRESHOLDS.md` — every fetched limit used (JLCPCB capabilities 2026-11-07, datasheets) with sources
- `PASS0_BASELINES.md` … `PASS6_MECHANICAL.md` — per-pass detail

## Data files (derived, machine-generated, from the KiCad-9 converted copy unless stated)
- `data/pads.csv` — every pad: ref, number, shape, position, size, drill, net
- `data/erc.json` — KiCad 9 ERC, severity-all (94 lib_symbol_mismatch warnings, 0 errors)
- `data/drc_board_rules.json` — KiCad 9 DRC with the project's own (empty) constraints
- `data/drc_jlcpcb_rules.json` — KiCad 9 DRC with JLCPCB minimums (`data/ProtoBuild1.jlcpcb-rules.kicad_pro`) on a scratch copy
- `data/netlist9.net` — KiCad 9 netlist export of the converted schematic (identical to the author's KiCad 10 netlist)
- `data/board-top.png`, `data/board-bottom.png` — the author's copper+silk PDFs rendered at 150 dpi
- `datasheets/*.txt` — pdftotext extracts of the datasheets cited in THRESHOLDS.md

## Scripts (`scripts/`)
Scratch-grade but complete; each emits a full table rather than a sample (SOURCE_OF_TRUTH rule 2).
They take the converted board path as an argument; `SCRATCH_DIR` / `KICAD_OUT` placeholders mark
the session paths they were run from. See `scripts/README.md`.
