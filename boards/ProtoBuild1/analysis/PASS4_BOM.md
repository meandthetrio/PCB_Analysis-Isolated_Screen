# Pass 4 — Three-Way BOM Cross-Check
**Date:** 2026-11-07 · **Sources:** `ProtoBuild1-parts-list.xlsx` (57 lines in 9 sections, DigiKey prices/stock of 7 Nov 2026) ↔ schematic/netlist (92 refs) ↔ board (96 footprints) · `scripts/pb1_bom_xcheck.py`

## Join mechanics
The parts list uses circuit names (R1a, Rdc, Rs, Cs1a/b, Cs2, Cs3, Cs4a/b, J7B…J13B) that the
schematic carries only as bracketed aliases in the Value field ("10k [R1a]"). The join maps the
14 aliases, expands ranges (C17-C22) and multi-ref cells, then compares value and footprint text.

## Verdict summary
- **Values: 100 % consistent** for all 70 on-board electrical references (resistor/capacitor values incl. 1k5 ↔ 1.5 kΩ spellings, ratings, dielectrics, transistor and op-amp types).
- **Footprints: 100 % consistent** — every parts-list "footprint / where it mounts" text names the schematic's footprint (TO-92 inline, TO-126 vertical, DIP-8 socket, DO-35/DO-41 axial, 10.16/12.7 mm axial resistors, rect film 5/10/15/22.5 mm pitch, radial 2.5/3.5 mm). Film-cap body sizes quoted (26 × 11.5 × 22, 18.5 × 8.5, 26 × 9, 18.5 × 6) match the KiCad footprints chosen (L26.5/W11.5, L18/W9, L26.5/W8.5, L18/W6, L11.5/W5).
- Off-board items reconcile: RV1/RV2/RV4/RV5, SW1–SW4 (schematic-only, no footprint) ✓; "L" = L1 ✓; "TP1-TP4" + "TP GND ×2" = TP1–TP6 ✓; "Sockets ×3" = U1–U3 DIP-8_Socket ✓; HS1 on Q6 ✓; "M3 standoffs ×4" = H1–H4 (3.2 mm) ✓; "PCB: 2-layer 1.6 mm HASL, JLCPCB" = Gerber job (2 layers, 1.6 mm) ✓.
- "C5 (+ spare)" and the five-value "Retune kit" are intentional extras with no board position — fine.

## PB-F-020 — two terminal blocks missing from the parts list (VIOLATION)
| | 2-position (MKDS 1,5/2) | 3-position (MKDS 1,5/3) | positions |
|---|---|---|---|
| Parts list | 7 — "IN, OUT, SW4, SW1a (2 of 5), SW1b (2 of 5), SW2 (2 + 2)" | 9 — "PWR, RV1, RV2, RV4, SW3, RV5 (×2), SW1a (3 of 5), SW1b (3 of 5)" | 41 |
| Schematic / board | 8 — J1, J2, J10, J12, J14, J15, J16, **J17** | 10 — J3, J4, J5, J6, J7, J8, J9, J11, J18, **J13** | 46 |
The coil-lead blocks J13 (common / 800 / 400) and J17 (200 / 100) — the documented wire
alternative to the footprint — are on the board but not on the order. The "Off-board wiring
plan: 41 terminal positions" line inherits the error.

## PB-F-021 — everything else reconciles (PASS)
Full join table in the script output; no wrong-part, no phantom, no footprint-technology mismatch.

## PB-F-022 — alias references will not be on the silkscreen (JUDGMENT)
The board silk prints R51, R50, R1, C31–C36, J14–J18; the parts list bags are labelled Rs, Rdc,
R1a, Cs1a…Cs4b, J-2/J-3. The mapping exists only in the upload README and the schematic Value
fields. Either rename the KiCad references to the circuit names (KiCad accepts "Rs", "Cs1a") or
add a "board ref" column to the parts list before anyone stuffs the board.

## PB-F-023 — heatsink clearance contradicts the parts list's own rule (JUDGMENT)
HS1 row: "No PCB holes; leave 10 mm clear around Q6". Measured (body outlines, `scripts/pb1_mech_extract.py`): C15 at 5.95 mm and R17 at 5.96 mm from Q6's body; U3 9.65 mm, R10 9.70 mm. The 577500B00000G slip-on is 8.13 × 19.81 × 13.21 mm (distributor data): if the 19.8 mm dimension lies across the TO-126's 8 mm width it overhangs ~6 mm per side and will touch C15/R17. Confirm orientation or move those two parts.
