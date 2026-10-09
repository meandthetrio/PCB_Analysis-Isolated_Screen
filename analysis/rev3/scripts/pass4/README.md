# Pass 4 (rev 3) scripts — three-way BOM cross-check

Run from the repo root with `python3 -I`; nothing here writes into `rev3/`.

| Script | What it does |
|---|---|
| `sch_symbols.py SCH.kicad_sch > sch_symbols.csv` | Placed symbol instances (ref/unit/lib_id/value/footprint/in_bom/dnp). Validated 110/110 refs+values+footprints against `kicad-cli sch export netlist` (`kicad_out/rev3/netlist.xml`). |
| `pcb_footprints.py BOARD.kicad_pcb > pcb_footprints.csv` | Every footprint via `pcbnew`: side, SMD/THT attribute, exclude-from-BOM/POS/DNP flags, pad counts, pads with F/B paste, pad sizes, position. |
| `bom_join.py BOM.xls sch_symbols.csv pcb_footprints.csv OUT/` | The join. Emits `join.csv`, `join.md`, `bom_lines.csv`, `summary.txt`. Contains known-answer self-tests for the value checker (asserts). |
| `paste_gerber.py BOARD.kicad_pcb F_Paste.gtp B_Paste.gbp` | Counts D03 flashes/G36 regions in the exported paste Gerbers and maps each to the nearest pcbnew paste pad (0.25 mm). Independent check of the pcbnew paste-pad data. |
| `bom_diff.py REV2.xls REV3.xls` | Designator-level diff of two JLCPCB-format BOMs. |
| `fp_compare.py` | Pad geometry of `L_Murata_DFE201610P` vs `L_0805_2012Metric` vs the 0805 hand-solder cap pattern, from the stock KiCad libraries. |
| `pad_nets.py BOARD.kicad_pcb [REF ...]` | Pad-to-net listing (all THT parts if no refs given). |

Outputs checked in alongside: `join.csv`, `bom_lines.csv`, `summary.txt` (2026-10-09 run).
