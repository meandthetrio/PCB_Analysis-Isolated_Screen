# ProtoBuild1 (Rev K iron block) - auto-routed PCB, complete file set, 7 Nov 2026

Everything for the auto-routed board in one place. Board: 170 x 130 mm, two layers, through-hole, all 57 nets routed
(0.4 mm tracks, 0.2 mm clearance, 0.8/0.4 mm vias), ground also poured on the bottom. ERC 0, DRC 0, nothing unconnected.

| Folder / file | What it is |
|---|---|
| `kicad-project/ProtoBuild1.kicad_pro` | open this in KiCad (9 or 10) |
| `kicad-project/ProtoBuild1.kicad_sch` | schematic, net-label style, one A1 sheet |
| `kicad-project/ProtoBuild1.kicad_pcb` | the routed board, KiCad 8 file format (press B after opening to fill the ground zone) |
| `kicad-project/ProtoBuild1-zones-filled-kicad10-format.kicad_pcb` | same board with the zone fill stored, saved by KiCad 10 (KiCad 9 may refuse it); the Gerbers came from this one |
| `kicad-project/ProtoBuild1.kicad_sym`, `ProtoBuild1.pretty/` | custom coil symbol; footprints `RM10_corner_12P_breakout` (used) and `RM10_coilformer_2x6` (DIL alternative) |
| `kicad-project/sym-lib-table`, `fp-lib-table` | project library tables for the custom parts |
| `gerbers/` | F/B copper, F/B silk, F/B mask, edge cuts, Excellon drill file + drill map PDF, job file: upload the whole folder (or the zip) to JLCPCB, 2 layers, 1.6 mm |
| `ProtoBuild1-board-top.pdf`, `-bottom.pdf` | copper + silk views (bottom mirrored) |
| `ProtoBuild1-schematic-kicad.pdf` | the schematic as PDF |
| `ProtoBuild1-parts-list.xlsx` | parts list with manufacturer numbers, stock and the fill-in column for Trey |
| `reports/ERC-report.txt`, `DRC-report.txt` | the rule-check reports (0 violations each) |
| `reports/ProtoBuild1-netlist.net` | the KiCad net list, checked pin for pin against the circuit data |

Coil: the footprint is the corner-group RM10 former. Every coil pin is wired inside the footprint to breakout pad 1-12;
circuit pads 0 (common) and 1-4 (taps) sit in the row below. Jumper the used breakout pads to 0-4 once the coil's pinout
is known. The terminal blocks J13/J17 take the coil on wires instead if preferred. Coil pads are drilled 0.75 mm for
the 0.6 mm pins.

References renamed for KiCad: R1 = R1a, R50 = Rdc, R51 = Rs, C31/C32 = Cs1a/b, C33 = Cs2, C34 = Cs3, C35/C36 = Cs4a/b,
J14-J18 = second halves of J10, J9, J8, J13, J7. Panel parts (pots, switches) are on the schematic only and wire to the
terminal blocks J4-J18.

The unrouted version of the same board (for hand routing) is in `deliverables/ProtoBuild1-kicad/`.
