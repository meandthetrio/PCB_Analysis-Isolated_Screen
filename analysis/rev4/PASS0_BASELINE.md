# Rev 4 — Pass 0: Inputs, provenance, baselines and the rev-3→rev-4 delta
**Date:** 2026-10-13 · **Inputs so far:** `rev4/WavetableController.kicad_sch` + `.kicad_pro` (Google Drive, shared 2026-10-13 by fernand.bourgeois.iii@gmail.com, file dates 16:44–16:52 UTC), `rev4/Gerbers/` (ManifoldGerbs.zip, plotted 2026-10-13 11:41 CDT by Pcbnew 9.0.4) · **Pending:** the rev-4 `.kicad_pcb` (31,869,998 bytes on Drive; the connector refuses files over 10 MB) and the rev-4 BOM · **Tools:** kicad-cli 9.0.9, pcbnew Python.

## 1. Provenance and file identity

| File | Rev 3 (`rev3/` on branch `claude/charming-meitner-c0w1jh`) | Rev 4 (`rev4/`) | Differs? |
|---|---|---|---|
| `.kicad_sch` | 423,788 B, md5 c544fb05… | 429,986 B, md5 24ad93dd…, `version 20250114`, generator eeschema 9.0, single root sheet | **yes** — 3,032 changed lines; netlist delta in §2 |
| `.kicad_pro` | 15,087 B | 15,087 B, md5 0d5a2f3c… | **byte-identical** → DRC rules unchanged: `min_track_width 0.0`, `min_clearance 0.0`, netclass Default 0.2/0.2, via 0.6/0.3, edge 0.5, hole 0.3 (F-005 / R3-P1-14 still open) |
| `.kicad_pcb` | 31,856,096 B, filled GND zone | 31,869,998 B on Drive (not yet downloaded) | size differs by 13,902 B → different file; content check pending |
| Gerbers | none (rev 3 was pre-fab) | 12 files, Pcbnew 9.0.4, job GUID 57617665-… (same project), outline 165.3 × 101.8 | new |
| BOM | `ManifoldRe_BOM_NEW - Excel Format (rev3).xls`, 36 lines / 90 designators | not received | — |

The rev-4 schematic and the Gerbers are the same design generation on the evidence available: the schematic's new parts (C27, C28, R31/R32/R34/R41 as 10 k, C19–C22 as 10 nF) and the Gerber pad delta from the rev-1 board both show ~36 new or replaced bottom-side parts, and the Gerber footprint count of new 0603s matches. Full confirmation (112 symbols ↔ footprints, pad-level nets) waits on the board file.

## 2. What changed rev 3 → rev 4 (netlist diff, `scripts/netlist_diff.py` over `kicad-cli` XML netlists)

**Components:** 110 → 112.
- **Removed:** D6 (the redundant series Schottky — 7 Oct row 9), FB7 (the bead between /+9V_FLAG and U6 VIN).
- **Added:** C27 100 nF 0603, C28 10 µF 0805 (both on /+3V3_D ↔ GND — the SD-socket caps, placement to be checked on the board); R34, R41 10 k 0603 (encoder pull-ups, with R31/R32 re-valued to 10 k).
- **Changed value/footprint:**

| Ref | Rev 3 | Rev 4 | Maps to |
|---|---|---|---|
| R21, R25, R26, R28 | 300 Ω 0603 | **390 Ω** 0603 | 7 Oct row 3c, decision 5a (green/blue) |
| R24, R27 | 300 Ω 0603 | **510 Ω** 0603 | row 3c, decision 5a (red) |
| R31, R32 | 3.3 Ω 2512 | **10 k 0603** (now encoder pull-ups on /ENCL_A, /ENCL_B) | row 7 / decision 5c; the second π-filter is gone (decision 5b) |
| C19, C20, C21, C22 | 100 µF electrolytic | **10 nF 0603** to GND on /ENCL_A, /ENCL_B, /ENCR_A, /ENCR_B | row 7 / decision 5c |
| D2–D5 | SOD-323 | **SOD-123F** | row 9 ("bridge to SMA/SOD-123FL") — part number pending BOM |
| L1 | `L_0805_2012Metric` | **`L_Murata_DFE201610P`** | row 6b / R3-P4-02 |

**Nets:** 121 → 117. Removed: Net-(C19-Pad1), Net-(C20-Pad1), Net-(D6-A), Net-(D6-K), Net-(U6-EN). Added: Net-(C15-Pad1) = {C15.1, C16.1, FB5.2, FB6.1}. Changed membership:
- `/+9V_FLAG` now = {FB6.2, C25.1, U6.2 VIN, U6.3 EN, R29.1, R21/R24–R28 pin 2}: **U6 is fed from the node right after FB6, ahead of R29/R30** (7 Oct row 2c done), and the net was re-pointed rather than orphaned (decision 5b satisfied; ERC shows no dangling label).
- `/ENCL_A`, `/ENCL_B`, `/ENCR_A`, `/ENCR_B` each gain a 10 k to /+3V3_D and a 10 nF to GND (row 7, schematic side done; placement check pending).
- `/+3V3_D` gains C27, C28, R31, R32, R34, R41.
- GND gains the four 10 nF and C27/C28.

**Power-entry chain, rev 4** (every node verified in `kicad_out/rev4/netlist.net`):
```
J1 → D2–D5 bridge → Net-(D2-K) [C14 100n] → FB3 → FB4 → FB5 → Net-(C15-Pad1) [C15 100µ, C16 100n] → FB6
  → /+9V_FLAG [C25 10µ; U6 VIN+EN; R21/R24–R28 → LED anodes; R29]
  → R29 3.3 Ω → Net-(C17-Pad1) [C17 100µ] → R30 3.3 Ω → /DSY_VIN [C18 100µ] → A1.39
```
Bulk capacitance on the ~8 V side: 3 × 100 µF + 10 µF (rev 3: 7 × 100 µF). Unlimited-inrush caps: C15 100 µF (rev 3: C15 + C19 = 200 µF).

**Unchanged from rev 3:** J8 20-pin header and its nets, U6/L1/C25/C26 buck, Q1–Q6 drivers, R35–R40, SD, USB, MIDI, audio, Headphones1, FB2–FB6 part (pending BOM), schematic LED value still "CLS6B-FKW" (documentation row 3d not done), /RES_SPI still a 2-node net (R3-P3-04 open), /SWA still single-pin.

## 3. Gerber-derived facts that already score 7 Oct rows (to be confirmed on the board file)
From `rev4/REV4_PASS1_GERBERS.md` (geometry scripts in `rev4/tools/`): J8 pin row still at y = 81.30 (pin 1 at x = 196.26) → **row 5 not moved**; NPTH inventory identical to rev 3 (28 holes + 1 slot, all component pegs) → **no M2 holes, no chassis holes**; 253 × 0.3 mm vias + 2 × 0.25 mm (U6 thermal) vs 244 + 2 in rev 3; 0.1 mm copper 75 mm (same as rev 3); pours on both sides; MK1 ring 0.175 and P2 NPTH 0.194 unchanged; bottom-silk artwork now overlaps 242 of 264 SMD paste pads and runs 699 mm² outside the outline.

## 4. ERC / DRC baselines (`kicad_out/rev4/`)
ERC (51, identical categories and counts to rev 3): 19 footprint_link_issues + 12 lib_symbol_mismatch (library noise), 14 pin_not_connected (10 × P2 SS/SBU, 4 × J8 3/9/15/18), 4 power_pin_not_driven (A1 VIN, U4 VDD, U6 VIN, #PWR01 GND), 1 label_dangling (SWA), 1 multiple_net_names (GND/SWB). No PWR_FLAG or NC flags were added → F-024 / R3-P3-06 / R3-P2-14 still open. DRC: pending the board file.

## 5. Threshold sources
JLCPCB capabilities page re-fetched 2026-10-13 (values unchanged from the rev-3 fetch: 0.10/0.10 mm, ±20 %, ring 0.18/0.25, via 0.15/0.25, NPTH-to-track 0.2, edge 0.2, silk 0.15). Daisy, NHD, TPS62172, Würth, MMBT3904 figures carried from the rev-3 pass reports (same parts). Bridge diode and bead ratings await the rev-4 BOM.
