# Pass 4 (rev 4) — Three-Way BOM Cross-Check
**Date:** 2026-10-13 · **Sources:** `rev4/ManifoldRe_BOM_NEW - Excel Format (rev4).xls` (received 2026-10-13; 38 lines, 92 designators, one sheet, JLCPCB format) ↔ `rev4/WavetableController.kicad_sch` (112 non-power symbols, `sch_symbols.py`, validated against the `kicad-cli` netlist) ↔ `rev4/WavetableController.kicad_pcb` (112 footprints, `pcb_footprints.py`). Supporting: `kicad_out/rev4/pos.csv` (107 rows), paste Gerbers plotted from the board, JLCPCB part pages fetched 2026-10-13 for the four new LCSC numbers. **Scripts:** `analysis/rev4/scripts/pass4/` (rev-3 scripts unchanged) with the raw outputs `join.csv`, `bom_lines.csv`, `summary.txt`, `bom_diff.txt` checked in alongside.

## Verdict summary
- **The join is clean again:** 92 BOM designators ↔ 92 schematic symbols ↔ 92 PCB footprints; 0 BOM-only, 0 schematic-only, 0 PCB-only, 0 duplicate refs, 0 designators on two lines, 0 LCSC numbers on two lines.
- **Values 92/92 consistent.** New LCSC numbers verified by part page: C169541 = **1N5817W, SOD-123FL, 1 A / 20 V / IFSM 25 A / Vf 0.45 V** (Extended); C23151 = 390 Ω 1 % 0603 UNI-ROYAL; C23193 = 510 Ω 1 % 0603 UNI-ROYAL; C57112 = 10 nF 50 V X7R 0603 Fenghua (Basic). The 10 k line (C22369937) now also covers R31/R32/R34/R41; the 10 µF line (C15850) covers C25 + C28; the 100 nF line covers C27.
- **Footprints 87/92 consistent + 3 generic.** Two mismatches, both **cosmetic cells, correct parts**: D2–D5's Footprint cell still says "SOD-323" while the ordered 1N5817W is SOD-123FL and the board has `D_SOD-123F` (the part fits the pads; the cell is stale text); L1's cell says "0806" while the board now uses `L_Murata_DFE201610P` (the correct pattern for that 0806 part — R3-P4-02 **FIXED**, the checker just doesn't know the Murata name).
- **LED1/LED2 are still absent from the BOM** while F.Paste contains exactly their 12 apertures (F-002 / F-034 / R3-P4-01 **STILL OPEN**). As settled, they are hand-soldered Würth 150505M173300s — they need a hand-solder line, which still does not exist.
- **Still no hand-assembly sheet** (one sheet in the file): 18 THT parts off-BOM (R3-P4-03 STILL OPEN). "Exclude from position files" still only on J3–J7; `pos.csv` has 107 rows incl. the LEDs and 13 THT parts (R3-P4-04 STILL OPEN).
- File hygiene unchanged (R3-P4-05): footprint cells numeric on 26/38 rows, mojibake on 19/38 comments, spacing oddities on 7 rows, a newline in the 100 µF footprint cell. Harmless to JLCPCB.

## What changed since rev 3 (`bom_diff.py`)
rev 3: 36 lines / 90 designators → rev 4: 38 lines / 92.
- **Removed:** D6, FB7.
- **Added:** C27 (→ C1590 100 nF), C28 (→ C15850 10 µF), R34, R41 (→ C22369937 10 k).
- **Changed part:** C19–C22 C3339 100 µF electrolytic → **C57112 10 nF 0603**; D2–D5 C727114 1N5817WS SOD-323 → **C169541 1N5817W SOD-123FL**; R21/R25/R26/R28 C23025 300 Ω → **C23151 390 Ω**; R24/R27 → **C23193 510 Ω**; R31/R32 C2960677 3.3 Ω 2512 → **C22369937 10 k 0603**. Line counts: C3339 ×9 → ×5, C2960677 ×4 → ×2, C14709 ×6 → ×5, C727114 line gone.
- The 7 Oct row 4 state holds (100 nF line = C1,C4,C5,C8,C11,C14,C16 + C27; no S1/S2/U5).

## Findings (rev 4, Pass 4)
| ID | Class | Status | Finding | Evidence |
|---|---|---|---|---|
| R4-P4-01 | VIOLATION | confirmed (R3-P4-01 / F-002 / F-034 STILL OPEN) | LED1/LED2 (hand-soldered Würth) have no BOM line of any kind; F.Paste = their 12 apertures; both in `pos.csv`. Nobody is told to fit them. | `summary.txt`, `paste_gerber.py` |
| R4-P4-02 | PASS | confirmed (R3-P4-02 FIXED) | L1 on `L_Murata_DFE201610P` in sch + PCB; BOM part C237554 unchanged. | `join.csv` |
| R4-P4-03 | JUDGMENT | confirmed (R3-P4-03 STILL OPEN) | No hand-assembly sheet; 18 THT parts incl. C23/C24/J8/Headphones1 off-BOM. | one sheet |
| R4-P4-04 | JUDGMENT | confirmed (R3-P4-04 STILL OPEN) | Position-file exclusion only on J3–J7; 15 CPL rows with no BOM match. | `pcb_footprints.csv` |
| R4-P4-05 | JUDGMENT | confirmed (R3-P4-05 STILL OPEN) | Hand-edited file hygiene unchanged; new: D2–D5 Footprint cell "SOD-323" is wrong for the SOD-123FL part ordered (cosmetic, JLC keys on LCSC). | `bom_lines.csv` |
| R4-P4-06 | JUDGMENT (doc) | confirmed (R3-P4-06 repeats) | Refdes repurposed again: C19–C22 100 µF → 10 nF, R31/R32 3.3 Ω → 10 k. Rev-3 notes naming them are stale. | `bom_diff.txt` |
| R4-P4-07 | JUDGMENT (cost) | confirmed | Extended parts now: U6, L1, R4, R29/R30, R35–R40 (C14676; C21190 1 % is Basic), C3339 ×5, **D2–D5 C169541**. New 390/510 Ω and 10 nF lines are Basic-class. | part pages |
| R4-P4-08 | PASS | confirmed | 92/92 values; 4/4 new LCSC numbers match MPN/package/value; bridge part fits the new SOD-123F pads; FB2–FB6 still C14709 (2 A, 50 mΩ) as assumed in Pass 2. | part pages |

## Hand-solder list (sch + PCB, not in BOM) — unchanged from rev 3 (18 THT) + LED1/LED2
A1, C23 (100 nF axial, /+3V3_OLED), C24 (100 µF radial, /+3V3_OLED), ENCL1, ENCR1, Headphones1, J3–J7, J8, MK1, SW1, TAC_SHIFT_L1/R1, TAC_SWITCH_1/2; **LED1, LED2 (Würth 150505M173300, top, SMD hand-solder)**.

## Full join
`analysis/rev4/scripts/pass4/join.csv` (112 rows). 92 ALL THREE · 2 SCH+PCB SMD not BOM (LED1, LED2) · 18 SCH+PCB THT not BOM.
