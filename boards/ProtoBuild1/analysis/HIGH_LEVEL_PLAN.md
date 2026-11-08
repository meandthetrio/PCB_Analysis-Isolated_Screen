# High-Level Plan — ProtoBuild1 PCB Analysis
Governed by `SOURCE_OF_TRUTH.md`. Same six-pass checklist as the Manifold review. Update the
status line of each pass when it completes; do not delete completed passes.

**Status legend:** `NOT STARTED` · `IN PROGRESS` · `COMPLETE` · `BLOCKED`

---

## Pass 0 — Environment & baselines
**Status: COMPLETE** (2026-11-07)
- [x] Upload unpacked into an isolated scratch dir; 32 files inventoried; provenance read from file headers, Gerber job file, drill header, netlist source path (not from the README)
- [x] KiCad 9.0.9 load failure diagnosed by bisect → PB-F-001; `tools/kicad10_to_9.py` written, verified byte-identical to the review copies
- [x] ERC baseline (KiCad 9): 0 errors, 94 lib_symbol_mismatch warnings → `data/erc.json`
- [x] DRC baseline with the project's own rules: 12 `shorting_items` on L1 only (net-tie copper, KiCad-9 artifact), 0 unconnected → `data/drc_board_rules.json`
- [x] Gerber ↔ board cross-check: F.Cu 521/521, B.Cu 247/247 segments exact; 43 Gerber-only draws = the coil footprint's internal ties; 86 via drills = 86 vias
- [x] Netlist three-way: KiCad 9 export = author's KiCad 10 netlist = board pad nets (57 nets, identical membership); 96 footprints = 92 symbols + H1–H4
- **Deliverable:** ✅ `PASS0_BASELINES.md`; PB-F-001…PB-F-005
- **Headline:** one consistent design state, but only KiCad 10 can open it, and the project carries no DRC constraints

## Pass 1 — Fab constraints
**Status: COMPLETE** (2026-11-07)
- [x] JLCPCB capabilities fetched 2026-11-07 (`THRESHOLDS.md`)
- [x] Full extraction: 768 segments all 0.40 mm; 86 vias 0.8/0.4; 239 PTH / 6 NPTH pads with rings; drill inventory (331 holes); hole-to-hole; NPTH-to-copper; copper-to-edge; pour-to-edge/NPTH from the Gerbers; mask openings; silk sizes
- [x] DRC re-run with JLCPCB minimums on a scratch copy (`data/drc_jlcpcb_rules.json`)
- [x] Island check: KiCad 9 refill reproduces the Gerber's 5 regions exactly (no floating copper)
- **Deliverable:** ✅ `PASS1_FAB_CONSTRAINTS.md` — 15-row limit table
- **Result:** 1 violation (PB-F-006 TO-92 annular 0.15 < 0.18), via ring at 0.20 (above abs min, below recommended), silk text below JLCPCB legibility minimums; everything else ≥ 2× margin

## Pass 2 — Power distribution
**Status: COMPLETE** (2026-11-07)
- [x] Rail topology from the netlist; series-diode drop; Traco TEN 5 datasheet checked (load regulation range, cap-load limit, no minimum-load clause in this revision)
- [x] Decoupling distances for every IC/transistor rail pin; rail copper length/width/vias; IPC-2221 ampacity and resistance
- [x] Polarity audit of every polarised part and diode against the netlist; transistor pin order against four datasheets
- [x] Q6 bias current-source arithmetic (0–80 mA; dissipation vs heatsink)
- **Deliverable:** ✅ `PASS2_POWER.md`
- **Result:** PB-F-011 (polarity PASS), PB-F-012 (diode drop/bleed note), PB-F-013 (output stage undecoupled), PB-F-014 (ampacity PASS), PB-F-015 (Q6 up to ~0.85 W), PB-F-016 (mounting holes vs pour)

## Pass 3 — Connectivity
**Status: COMPLETE** (2026-11-07)
- [x] ERC 0 errors in both KiCad 10 (author) and KiCad 9 (here); 15 no-connect flags dispositioned (SW2 ×10, SW1 ×4, SW4 ×1 — all unused switch positions)
- [x] 57 nets, no single-node nets, 0 unrouted; 24 no-net pads = coil pins + breakout row (PB-F-018)
- [x] Off-board wiring tables (pots, switches, coil) reconstructed from the netlist and checked against the circuit description; tuning arithmetic checked
- **Deliverable:** ✅ `PASS3_CONNECTIVITY.md`
- **Result:** PB-F-017 (PASS), PB-F-018 (coil requires hand jumpers — the top landmine), PB-F-019 (wiring tables consistent)

## Pass 4 — Three-way BOM cross-check
**Status: COMPLETE** (2026-11-07)
- [x] 57 parts-list lines expanded (ranges, aliases Rs/Rdc/Cs1a…/J13B…) ↔ 92 schematic refs ↔ 96 board footprints; every row dispositioned
- [x] Values and footprints: 100 % consistent for all 70 on-board electrical refs
- **Deliverable:** ✅ `PASS4_BOM.md`
- **Result:** PB-F-020 (two terminal blocks missing), PB-F-021 (PASS), PB-F-022 (alias refdes vs silkscreen), PB-F-023 (heatsink clearance vs BOM's own 10 mm rule)

## Pass 5 — Signal-specific
**Status: COMPLETE** (2026-11-07)
- [x] Analog net lengths and routing; op-amp paralleling; supply vs NE5532 limits; compensation/output network; input/output coupling
- **Deliverable:** ✅ `PASS5_SIGNALS.md`
- **Result:** PB-F-024 (long autorouted analog nets — judgment), PB-F-025 (supply PASS), PB-F-026 (I/O notes)

## Pass 6 — Mechanical & assembly
**Status: COMPLETE** (2026-11-07)
- [x] Mounting holes, terminal-block edge orientation (18/18 outward), body overlaps (none), courtyards (all present), silk, mask/tenting
- [x] Coil footprint vs Ferroxcube RM10/I 12-pin former drawing; pin-hole and clip-hole sizes
- **Deliverable:** ✅ `PASS6_MECHANICAL.md`
- **Result:** PB-F-027 (PASS), PB-F-028 (coil footprint commits to one former type), PB-F-029 (vias tented, fine), PB-F-030 (TO-92 pitch vs formed-lead parts)

## Final — Synthesis
**Status: COMPLETE** (2026-11-07)
- [x] Verification sweep: every finding re-checked by an independent method where one exists; nothing left `plausible` except items that need Trey's input (coil pinout, heatsink orientation, chassis-ground intent)
- [x] Ranked report: Tier 1 (blocks a working first build) → Tier 4 (next-rev robustness) + verified passes + questions for Trey
- **Deliverable:** ✅ `FINAL_REPORT.md`

**ALL PASSES COMPLETE.**

## Decisions log
- 2026-11-08 — inductor to a plug-in daughterboard with a keyed 1 × 5 header on the main board (PB-F-031); PB-F-018 and PB-F-028 superseded.
