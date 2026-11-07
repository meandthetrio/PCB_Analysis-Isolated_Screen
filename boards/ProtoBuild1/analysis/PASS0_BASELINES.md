# Pass 0 — Environment, provenance and baselines
**Date:** 2026-11-07 · **Inputs:** `ProtoBuild1-autorouted.zip` (883 kB, 32 files, all stamped 2026-11-07 16:10 = transfer time) · **Tools:** KiCad 9.0.9 `kicad-cli` + `pcbnew` (this session), the author's KiCad 10.0.8 outputs

## Provenance (from file contents, not the README)
| Artifact | Evidence |
|---|---|
| Design authored in KiCad 10.0.8 | netlist header `(tool "Eeschema 10.0.8")`, source path `…/Quad Eight/work/kicad/ProtoBuild1.kicad_sch`; Gerber/drill `GenerationSoftware KiCad Pcbnew 10.0.8`, job file `Revision "K"`, 2 layers, 1.6 mm |
| Timeline (single morning, −06:00) | ERC + netlist 09:38:20 → DRC + Gerbers + drill 09:42:06 (same second: plotted and checked in one run) |
| Board files | `ProtoBuild1.kicad_pcb`: header `version 20240108 / generator_version "8.0"`, 96 footprints, 768 segments, 86 vias, 1 zone with **no stored fill**; `…-zones-filled-kicad10-format.kicad_pcb`: `version 20260206 / 10.0`, fill stored (5 polygons), KiCad-10 pad tenting/covering tokens |
| Schematic | `version 20231120 / 8.0`, one A1 sheet, 109 symbol instances (16 library symbols embedded), 252 wires (all pin stubs), 252 local labels, 15 no-connects, 0 junctions — a **net-label-style, machine-generated** schematic |
| Status | not fabricated; parts list says "Nothing has been ordered"; JLCPCB named as fab |

## PB-F-001 — the shipped files are KiCad-10-only (VIOLATION of the upload's own "KiCad 9 or 10" claim)
`kicad-cli` 9.0.9 reports "Failed to load board/schematic"; `pcbnew.LoadBoard` returns `None`; the
plugin API throws `PARSE_ERROR`. Bisect (add known-good pieces to a known-good header, one
subprocess per trial) isolated the cause to KiCad-10-only grammar inside the embedded library
content: `.kicad_pcb` → `(duplicate_pad_numbers_are_jumpers …)` in 95 footprints and six
`(point …)` fab-layer markers; `.kicad_sch` → `(in_pos_files …)` and
`(duplicate_pin_numbers_are_jumpers …)` in 15 library symbols plus the embedded
`power:PWR_FLAG` definition (`(power global)` form). The custom coil symbol/footprint, written by
the author's own generator, parse fine in KiCad 9. With those four tokens stripped and the stock
PWR_FLAG substituted, KiCad 9 loads both files; `tools/kicad10_to_9.py` reproduces the review
copies byte-for-byte. Consequence: anyone on KiCad 8/9 (and the Manifold toolchain) cannot open
the project; recommend re-saving from KiCad 10 as native 10 files and stating the requirement.

## PB-F-002 — no DRC constraints in the project (JUDGMENT)
`ProtoBuild1.kicad_pro` is a 7-line stub (`"rules": {}`). KiCad therefore checks only the default
netclass (clearance 0.2, track 0.2, via 0.6/0.3) and leaves min track width, min clearance,
annular ring etc. at 0. The author's "DRC 0" is true but cannot catch fab-rule problems; the same
board with JLCPCB minimums in the constraints reports the TO-92 annular-ring violation (Pass 1).

## PB-F-003 — one consistent design state (PASS)
- **Gerber ↔ board copper:** F.Cu 521/521 and B.Cu 247/247 segments match exactly (endpoints, widths); the 43 extra F.Cu draws in the Gerber are the coil footprint's 43 internal 0.4 mm tie lines; 86 `T1 0.40` drill hits = 86 vias; 325 copper flashes per layer = 239 PTH + 86 vias.
- **Netlist three-way:** KiCad 9 export of the converted schematic, the author's KiCad 10 netlist and the board's pad nets agree on all 57 nets with identical membership. 96 board footprints = 92 schematic components + H1–H4 (3.2 mm NPTH, board-only).
- **Zone fill:** a KiCad 9 refill of the unfilled file reproduces the Gerber's five fill polygons (89 / 114 / 14 / 24 / 18 522 mm²) exactly — same fill rules, no floating islands.

## PB-F-004 — net-label schematic (JUDGMENT)
Every component sits in a grid with a stub wire and a label per pin; there is no drawn circuit.
ERC is clean, but a human cannot read the topology from the sheet — the five section titles and
the netlist are the only readable descriptions. Fine as a build artefact; for a Rev L drawn by
hand or for anyone else reviewing it, a conventional wired schematic would pay for itself.

## PB-F-005 — the supplied ERC/DRC reports ignore some checks (info)
Author's KiCad 10 ERC ignores "label only appears once", "four connection points", footprint-filter
checks; DRC ignores missing courtyards, track-not-centred-on-via, footprint type/pad mismatch.
None hides a real defect here: KiCad 9 ERC (severity-all) = 0 errors + 94 `lib_symbol_mismatch`
warnings (the embedded KiCad 10 symbols differ from KiCad 9's library copies — hygiene only);
KiCad 9 DRC = 12 `shorting_items`, all on L1 where the footprint's copper lines join its
net-tie pad pairs (C*n*–B*n*, both without a net) — a KiCad-9 interpretation of the net-tie
groups, clean in KiCad 10. 0 unconnected items.

## Baseline numbers (converted copy, `scripts/pb1_stats.py`)
96 footprints · 768 tracks (all 0.40 mm; F.Cu 521 / 4 724 mm, B.Cu 247 / 1 140 mm) · 86 vias 0.8/0.4 · 1 GND zone on B.Cu (outline 1 mm inside the edge, clearance 0.5, min width 0.25, thermal gap/spoke 0.5/0.5) · 58 net codes (57 + unassigned) · board 170.0 × 130.0 mm · no duplicate references.
