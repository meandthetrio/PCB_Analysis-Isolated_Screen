# Analysis folder index

Start here: **`FINAL_REPORT.md`** — the tiered red-flag summary, including the three open questions for Trey. Everything else is supporting material; no findings live only in this README.

## Reports
- `PASS0_BASELINE_2026-10.md` — **Round 2** (2026-10 files) Pass 0: provenance proof, parser validation, ERC/DRC baselines, old↔new delta
- `PASS1_FAB_CONSTRAINTS_2026-10.md` — Round 2 Pass 1: 13-row limit table vs JLCPCB, F-037/040/041/046/047/048
- `PASS2_POWER_2026-10.md` — Round 2 Pass 2: new 9 V ladder + TPS62172 buck + OLED budget, F-049…F-055
- `datasheets_2026-10/` — archived PDFs + text: TPS6217x, Daisy Seed v1.2.0, Cree CLS6B-FKW, NHD-2.7-12864WDW3 (fetched 2026-10-07)
- `baseline_2026-10/` — Round 2 ERC/DRC JSON and parser output (stock rules + JLCPCB-minimum copy)
- `FINAL_REPORT.md` — final summary, Tiers 1–4, questions for Trey
- `FINDINGS.md` — full ledger: F-001…F-035 (Round 1), F-036… (Round 2)
- `HIGH_LEVEL_PLAN.md` — the pass plan; Round 1 complete, Round 2 status at the end
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
