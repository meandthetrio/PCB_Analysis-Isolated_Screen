# Rev 4 — JLCPCB order package
Generated 2026-10-13 from the rev-4 KiCad files (`rev4/WavetableController.kicad_sch` / `.kicad_pcb`) and the LCSC numbers in Trey's rev-4 BOM, with live stock from the JLCPCB parts API. Scripts: `analysis/rev4/scripts/make_order_bom.py`, `make_order_xlsx.py`.

| File | What it is | Use |
|---|---|---|
| `BOM_JLCPCB_SMT.csv` | The SMT BOM in JLCPCB's upload format (Comment, Designator, Footprint, JLCPCB Part #), 38 lines / 92 designators, every designator validated against schematic **and** board (`BOM_check.txt`: 92 SMT + 20 hand-fitted = 112 of 112 footprints, no inconsistencies) | **Upload this as the BOM.** Designators have no spaces or line breaks; footprint cells are text (no Excel "603.0"); the D2–D5 cell now says SOD-123FL to match the part actually ordered |
| `HAND_SOLDER.csv` | The 20 parts JLCPCB does not fit: 18 through-hole parts plus LED1/LED2 (Würth 150505M173300, hand-soldered, with the pin-1 and polarity notes) | Trey's bench list; keep with the boards |
| `STOCK_CHECK.csv` | Every SMT line with JLCPCB assembly stock, Basic/Extended, unit price, status for a 10-board run, and a verified alternative where one matters | Read before uploading; see below |
| `Rev4_JLCPCB_Order.xlsx` | The three sheets above in one workbook. `Stock_Check!B1` is the board quantity (default 10); Needed and Status recalculate from it | Change B1 to the real run size |
| `BOM_check.txt` | Coverage and consistency summary from the generator | — |

## Stock, as of 2026-10-13 (JLCPCB assembly stock, not LCSC retail stock)

**One line is short: U3, TPA6110A2DGNR (C130212) — 5 in stock, minimum buy 7.** JLCPCB will not let the order through with that line as-is. The only in-stock sibling, TPA6111A2DR (C497472, 887 pcs), is SOIC-8 and does not fit the HVSSOP-8-EP pads; the HVSSOP TPA6111A2DGN variants show 0 stock. Options, in order of least disruption:
1. Buy TPA6110A2DGNR from Mouser/Digi-Key and either **hand-solder U3** (move it to the hand-solder list and delete the line from the BOM before upload) or use JLCPCB's consigned-parts service.
2. Ask JLCPCB for a global-sourcing pre-order of C130212 (adds lead time).
3. Next spin: change U3's footprint to SOIC-8 and use TPA6111A2DR.

Everything else covers a 10-board run with ≥ 5× margin. Lines under 2,000 pcs, fine for a small run but worth a glance before a bigger one: D1 NSR1020MW2T3G 501 (Basic drop-in 1N5819WS C191023 listed as the alternative), J1 DC-050-T20 1,407, U2 USBLC6-2P6 1,850, U6 TPS62172DSGR 1,993.

## Optional Basic-library swaps (each removes one Extended-part handling fee)
Verified in-stock Basic equivalents are listed in the Alternative column for: C1590 → C14663 (100 nF 50 V), C1226 → C22962 (220 Ω 1 %), C25600 → C25819 (47 k 1 %), C23344 → C31850 (22 k 1 %), C1607 → C23630 (2.2 µF 16 V), C1705 → C19666 (4.7 µF 16 V), C14675 → C25803 (100 k 1 %), C22369937 → C25804 (10 k 1 %), C14676 → C21190 (1 k 1 %). None changes the circuit (same value, same package, equal or better voltage/tolerance). Not applied to the BOM; swap the LCSC number on the line if wanted.

## Not included, by request
The pick-and-place (CPL) file with rotation corrections for JLCPCB's assembly preview. Trey generates and checks that himself.

## Assumptions
Run size 10 boards for the Status column (edit `Stock_Check!B1`). Stock figures are a snapshot; JLCPCB re-checks at upload. Part identities (MPN, package, Basic/Extended) come from the JLCPCB parts API on 2026-10-13.
