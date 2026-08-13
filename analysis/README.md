# Analysis folder index

Start here: **`FINAL_REPORT.md`** — the tiered red-flag summary, including the three open questions for Trey. Everything else is supporting material; no findings live only in this README.

## Reports
- `FINAL_REPORT.md` — final summary, Tiers 1–4, questions for Trey
- `FINDINGS.md` — full ledger (F-001…F-035) behind the summary
- `HIGH_LEVEL_PLAN.md` — the pass plan the review followed
- `SOURCE_OF_TRUTH.md` — methodology: which file is authoritative for what, verification rules
- `PASS1_FAB_CONSTRAINTS.md` … `PASS6_MECHANICAL.md` — per-pass detail (fab limits, power, connectivity, BOM, signals, mechanical)
- `REV2_OLED_PLAN.md` — OLED/I2C rev-2 planning

## Data files (derived, machine-generated)
Extracted from the fabbed Gerbers, with net names assigned by geometrically cross-referencing copper connectivity against the schematic netlist (anchored at Daisy Seed pins). Net attribution is inferred, not authoritative — `island_*` entries are copper the matcher could not identify.
- `routing_tracks.csv` — every track segment: layer, endpoints, width, length, net
- `routing_pads.csv` — pads: layer, position, shape, size, net
- `routing_vias.csv` — vias: position, drill, pad, net
- `wavetable_board.svg` — rendered board view from the Gerbers
- `gerber_analyze.py` — the parser/matcher script that produced the above
