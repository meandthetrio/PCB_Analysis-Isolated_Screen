# High-Level Plan — WavetableController PCB Analysis
Governed by `SOURCE_OF_TRUTH.md`. Update the status line of each pass when it completes; do not delete completed passes.

**Status legend:** `NOT STARTED` · `IN PROGRESS` · `COMPLETE` · `BLOCKED`

---

## Pass 0 — Environment & baselines
**Status: COMPLETE** (2026-08-12)
- [x] KiCad **10.0.5** installed to `/Applications/KiCad.app` (brew cask needed sudo → installed from cached DMG instead; `kicad-cli` at `/Applications/KiCad.app/Contents/MacOS/kicad-cli`)
- [x] Framework files created (SOURCE_OF_TRUTH, this plan, FINDINGS ledger)
- [x] Project copied to scratchpad `drc_copy/`; DRC minimums set to JLCPCB values (track 0.1, clearance 0.1) in the copy only
- [x] ERC baseline: 207 violations (17 error-severity) → `drc_copy/erc_report.json`
- [x] DRC baseline: 249 violations + 53 unconnected (51 = GND) → `drc_copy/drc_report.json`
- [x] Parser validated: 0.1mm segment counts match prior Gerber-derived counts (275/282 vs ~270 per layer)
- **Deliverable:** ✅ baselines produced; findings F-006…F-012 logged
- **Headline:** F-006 — the `.kicad_pcb` has no GND pour but the Gerbers do → file-version mismatch; Gerbers are the fab truth for copper

## Pass 1 — Fab constraints
**Status: COMPLETE** (2026-08-13)
- [x] Full extraction: trace widths (0.1/0.2mm only), 93/94 vias all 0.6/0.3mm, complete drill inventory (170 PTH + 28 NPTH), PTH annular rings, hole-to-hole gaps
- [x] JLCPCB capabilities fetched fresh 2026-08-13 (incl. disambiguating via vs component-PTH annular rules)
- [x] PCB↔Gerber cross-check done during alignment audit (97% match; F-015/F-017)
- **Deliverable:** ✅ `PASS1_FAB_CONSTRAINTS.md` — 10-row limit table
- **Result:** 3 marginal violations (F-008 NPTH-to-copper 0.194, F-016 MK1 annular 0.175, F-010 SW1 edge copper 0.0) + the defining zero-margin item (F-004: 3.85m of trace at exactly 0.10mm)

## Pass 2 — Power distribution
**Status: COMPLETE** (2026-08-13)
- [x] Rail topology mapped (9V→Daisy VIN; Daisy 3v3D/3v3A source all peripherals; USB 5V → ESD only)
- [x] IPC-2221 capacity + resistance per rail — ampacity all OK; impedance is the issue
- [x] Decoupling audit — every IC power pin's distance to nearest same-net cap measured
- [x] LED bug re-verified & refined with Daisy datasheet citations (F-018: reverse-biased + 3.3V-only pins 24/25/30)
- [x] Daisy datasheet v1.0.5 fetched & archived; VIN range / AGND tie / SD pullups verified OK
- **Deliverable:** ✅ `PASS2_POWER.md`
- **Result:** F-018 (LED, worse than known), F-019 (3V3_D impedance = OLED/I2C noise root cause), F-020 (PCB-only 10Ω fix not in schematic), F-021 (passing checks)
- **Carried to Pass 5:** TPA6110A2 supply decoupling vs its datasheet

## Pass 3 — Connectivity
**Status: COMPLETE** (2026-08-13)
- [x] Full sch↔pcb netlist diff (done in alignment audit; net-count 93 vs 85 fully reconciled — zero unexplained)
- [x] Encoder clicks verified against fab truth: NO copper at any pad site in Gerbers → F-007 confirmed
- [x] Single-pin (/SWA = half-wired card-detect), dangling (4 GND stubs = pour artifact), unconnected-* (14, intentional) all dispositioned
- [x] All 17 ERC error-severity items dispositioned (10 intentional NC, 3 unused GPIO, 2 PWR_FLAG false positives, 1 jack ring, 1 power flag)
- **Deliverable:** ✅ `PASS3_CONNECTIVITY.md`
- **Result:** F-007 confirmed on fab truth (encoder clicks float); F-022 card-detect unusable; F-023, F-024 hygiene

## Pass 4 — Three-way BOM cross-check
**Status: COMPLETE** (2026-08-13)
- [x] Full three-way join (31 BOM lines ↔ 78 sch refs ↔ 79 pcb footprints), every row dispositioned
- [x] Values audit: all 58 shared designators consistent — zero wrong-part findings
- [x] F-002 sharpened (LEDs = only missing SMD), F-003 refined (S1/S2 = SMD switch vs THT footprints)
- [x] NEW F-025: dup-R21 → 300Ω would be auto-placed at the 10Ω OLED damper position
- **Deliverable:** ✅ `PASS4_BOM.md`

## Pass 5 — Signal-specific
**Status: COMPLETE** (2026-08-13)
- [x] USB FS pair measured (7.2mm/2-via asymmetry — fine at FS; F-028)
- [x] I2C: 203/205mm bus and **ZERO pull-ups in the design** (F-027 — depends on OLED module's onboard pull-ups; pairs with F-019 as the noise causal chain)
- [x] SD: 89–108mm, skew trivial, 47K pullups per reference — PASS
- [x] MIDI: verified against 3.3V MIDI practice — PASS (F-029; D1's true role corrected)
- [x] Audio: TPA6110A2 checked vs SLOS314B — missing recommended ≥10µF bulk (F-031); mid-rail Eq.6 PASS; run-length notes (F-030)
- **Deliverable:** ✅ `PASS5_SIGNALS.md`
- **Carried out:** ask Trey / check OLED module for onboard I2C pull-up value (F-027 confirmation)

## Pass 6 — Mechanical & assembly
**Status: COMPLETE** (2026-08-13)
- [x] SW1 edge copper resolved: deliberate outline notch for slide switch (F-010 → accepted deviation)
- [x] Mounting-hole audit: NO chassis holes; board hangs from panel hardware (F-032)
- [x] Silk warnings decomposed: 143 = panel artwork + minor overlaps, cosmetic (F-033)
- [x] Paste/mask vs Gerbers: top paste = exactly the 12 missing-LED pads (F-034, corroborates F-002); courtyards zero-overlap
- **Deliverable:** ✅ `PASS6_MECHANICAL.md`

## Final — Synthesis
**Status: COMPLETE** (2026-08-13)
- [x] Verification sweep: 33/35 findings confirmed; 2 blocked on Trey (F-014 which-file-is-right, F-027 OLED pull-ups) — explicitly marked, nothing silently open
- [x] Stale statuses closed (F-001 re-verified via Pass 2; F-011 superseded by F-024)
- [x] Ranked report: 4 tiers (working-board defects → next-build landmines → fab margins → robustness) + verified-passes list + 3 questions for Trey
- **Deliverable:** ✅ `FINAL_REPORT.md`

**ALL PASSES COMPLETE.**
