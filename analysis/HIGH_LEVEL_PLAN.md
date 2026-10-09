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

---

# Round 2 — 2026-10 file set
Trey supplied a new, mutually consistent set on 2026-10-07: `Manifold_Gerbs_2026-10/`, root `.kicad_pcb/.kicad_sch/.kicad_pro`, and a 2026-10-06 BOM (Round 1 design files archived in `archive/rev1_2026-08/`). Same pass structure; same rules. One pass per session, reviewed between passes.

## R2 Pass 0 — Environment & baselines
**Status: COMPLETE** (2026-10-07)
- [x] Inventory: Gerber set complete (9 layers + 2 drills + job); KiCad files + BOM received on request
- [x] **Provenance proven**: re-plot from the new `.kicad_pcb` is byte-identical to the supplied Gerbers (copper/mask/paste/edge/drills) → single truth, F-036
- [x] Parser `gerber_analyze.py` re-validated on the new set (hole/aperture/region counts vs raw file); now takes a directory argument
- [x] ERC baseline 46 (20 errors) → `analysis/baseline_2026-10/erc_2026-10.json`
- [x] DRC baseline 558 + **0 unconnected** (stock) and identical with JLCPCB minimums on a scratchpad copy → `drc_stock_2026-10.json`, `drc_jlcpcb_min_2026-10.json`
- [x] Old↔new delta table (footprints, nets, widths, vias, pour, silkscreen, BOM)
- **Deliverable:** ✅ `PASS0_BASELINE_2026-10.md`; findings F-036…F-045
- **Headlines:** GND pour present and consistent; dup R21 gone; encoder clicks routed; 0.1 mm trace length 3850 → 73 mm; display moved from I2C to SPI with a new TPS62172 buck; new project-rule DRC errors (0.25 mm drills at U6, 3V3_D tracks 0.451 mm from edge, 9 one-spoke thermals); BOM adds a U5 that is not in the design
- **Open question:** Q-R2-1 — has this set been fabbed?

## R2 Pass 1 — Fab constraints
**Status: COMPLETE** (2026-10-07) — thresholds re-fetched live from jlcpcb.com the same day after the domain was allowed (archived in `baseline_2026-10/`); four extra rows added (PTH/via/NPTH-to-track, mask bridge), all pass; F-046 silk upgraded to cosmetic VIOLATION
- [x] Full extraction from the Round 2 `.kicad_pcb` (pcbnew): widths, 225 vias, 138 PTH pads with rings, 29 NPTH, hole-to-hole, NPTH-to-copper, copper-to-edge (outline-only distance), hole-to-edge, slots, mask, silk — cross-checked against the Gerber parser (histograms match)
- [x] 13-row limit table → `PASS1_FAB_CONSTRAINTS_2026-10.md`
- [x] F-037 confirmed (0.1 mm residual 73 mm, ≈46 mm forced by U4); F-040 confirmed marginal (U6 thermal vias ring 0.175, hole 0.25 legal); F-041 downgraded to project-rule JUDGMENT; F-010 corrected (SW1 pads 0.414 mm, OK) → F-047; F-046 silk 0.12 mm plausible; F-048 passes list
- **Result:** no hard fab violations; three marginal 0.175/0.197 mm items (MK1, U6, P2) all one-line footprint edits
- **Carried to Pass 6:** 10 B-paste flashes without mask openings; silk artwork regions

## R2 Pass 2 — Power distribution
**Status: COMPLETE** (2026-10-07) — datasheets fetched the same day after the hosts were allowed and archived in `analysis/datasheets_2026-10/` (TPS6217x Rev E, Daisy v1.2.0, Cree Rev 5, NHD Rev 6); F-050/F-051 upgraded to confirmed, Cree pinout verified for F-052
- [x] Rail topology mapped from the netlist: bridge → FB3–FB6 → D6 → two 3.3 Ω/100 µF RC ladders (Daisy branch, display+LED branch) → TPS62172 buck → OLED
- [x] Current/voltage budget: display 345/375 mA at 3.3 V dominates; main path ≈ 0.30–0.49 A; Daisy VIN ≈ 5.8 V worst case (in range)
- [x] Decoupling audit (nearest same-net cap per IC power pin) and rail copper/IPC-2221 table
- [x] LED drive re-derived: unchanged, still reverse-biased to ~9 V on 3.3 V-only pins (F-052)
- **Deliverable:** ✅ `PASS2_POWER_2026-10.md`; findings F-049…F-055
- **Headlines:** F-049 input cap 6.3 V on an 8 V node (confirmed); F-050 four 200 mA beads carrying 0.3–0.5 A; F-051 0603 3.3 Ω resistors over their 100 mW rating in the display branch; F-053 fixed-voltage buck wired with an adjustable divider; F-054 3V3_D still has one 100 nF
- **Questions:** Q-R2-2, Q-R2-3, Q-R2-4

## R2 Pass 3 — Connectivity
**Status: COMPLETE** (2026-10-07)
- [x] Full sch↔pcb netlist diff: 0 membership differences across 102 shared nets; 8 sch-only = USB-C SS pins absent from the 16-pin footprint (F-056)
- [x] Encoder clicks confirmed routed + internal pull-up model verified in libDaisy source (F-057, closes F-007)
- [x] Every input checked against the Daisy v1.2.0 pinout and the Newhaven 4-wire SPI table; TAC_SWITCH wiring verified against footprint pad geometry (F-062)
- [x] All 20 ERC errors dispositioned (F-059); F-022 SWA persists; F-024 hygiene carries over
- **Deliverable:** ✅ `PASS3_CONNECTIVITY_2026-10.md`; findings F-056…F-062
- **Headlines:** connectivity is clean; only judgments remain — FB1 is a no-op (both pins GND), SPI1_MISO pin reused as a button (firmware TX-only), no external pull-ups/debounce

## R2 Pass 4 — Three-way BOM cross-check
**Status: COMPLETE** (2026-10-07)
- [x] Full join: 37 BOM lines / 84 designators ↔ 100 sch ↔ 100 pcb; every row dispositioned; LCSC listing titles fetched for all 37 part numbers (archived)
- [x] Values audit: 80/80 shared designators consistent (F-066)
- [x] NEW F-063: C17 on two BOM lines (100 nF and 100 µF) — stale entry; F-064: U5 = L7805 DPAK + S1/S2 with no positions; F-065: L1 footprint is 0805 for a 2.0 × 1.6 mm inductor
- [x] F-002/F-034 (LEDs), F-003, F-026 persist; F-025 closed
- **Deliverable:** ✅ `PASS4_BOM_2026-10.md`; findings F-063…F-066
- **Question:** Q-R2-5 (U5 intent)

## R2 Pass 5 — Signal-specific
**Status: COMPLETE** (2026-10-07) — TPA6110A2, MAX9814, H11L1 and USBLC6-2 datasheets all archived; every Pass 5 verdict is datasheet-cited
- [x] SPI display bus: 89–124 mm, 0.3 mm, point-to-point — PASS (F-067)
- [x] USB pair re-measured: 130.2/130.6 mm, 0.4 mm skew, 0.3 mm — F-028 fixed; SD 27–49 mm; MIDI unchanged — all PASS (F-068)
- [x] Headphone amp vs SLOS314B: gain, HPF, Eq. 6, coupling cap all PASS; **F-031 (no ≥ 10 µF bulk) persists**; F-069 no 5 pF compensation cap
- [x] Mic amp = MAX9814 EV-kit configuration (F-068)
- [x] Analog/digital proximity scan: F-070 (AUDIO_OUT_R 0.20 mm from TAC_SWITCH_2 for 25 mm; AUDIO_IN_L beside the UART for 43 mm); analog runs 25–70 % shorter and 3× wider than Round 1 (F-030 improved)
- **Deliverable:** ✅ `PASS5_SIGNALS_2026-10.md`; findings F-067…F-070

## R2 Pass 6 — Mechanical & assembly
**Status: COMPLETE** (2026-10-07)
- [x] Side assignment mapped: 8 parts front (display, encoders, main buttons, LEDs, mic), 92 back (everything else incl. all connectors and the artwork)
- [x] NHD module projected from the Newhaven drawing: x 131–213 / y 77–124, clear of every front part; **no holes for its four Ø2.5 mounts → F-071**
- [x] 2026-10-08 follow-up: projected top-left hole sits on SW1 pad 3 → **F-074**; fix = J8 down 5 mm, holes at (135.0, 84.3) (209.2, 84.3) (135.0, 126.8) (209.2, 126.8), U1/R2 move, four tracks reroute
- [x] Silk decomposed: artwork on B.Silk overprints 63 back-side refdes → F-072; F-046 0.12 mm strokes
- [x] Paste/mask: all three exposed pads stencilled (the 10 "paste-without-mask" flashes are KiCad EP sub-pads), top stencil = LEDs only (F-034 persists), 0 courtyard overlaps, no fiducials (F-073)
- [x] F-032 persists (no chassis holes); F-042 closed as accepted
- **Deliverable:** ✅ `PASS6_MECHANICAL_2026-10.md`; findings F-071…F-073
- **Questions:** Q-R2-6 (which side faces the user), Q-R2-7 (module mounting)

## R2b — Trey's 2026-10-09 revision (diff check, 2026-10-09)
- [x] BOM diffed line by line; every new LCSC number resolved (`REV2B_DIFF_2026-10-09.md` §1)
- [x] Board diffed with pcbnew (footprints, positions, nets, holes); DRC with Round 2 rules → `baseline_2026-10/drc_rev2b_2026-10-09.json`
- [x] Closed: F-049, F-050, F-051, F-053, F-060, F-063, F-064, doc item 8 · Partial: L1 move · Open: R21/R24–R28 size, F-071/F-074 holes, F-075, D6
- [x] New: **F-076** (CLS6B-FKW cannot fit the 5050 footprint — pre-existing miss), **F-077** (rev2b switches sink the anodes; still reverse-biased)
- [ ] ERC + netlist parity — waiting on `.kicad_sch` / `.kicad_pro` (iCloud placeholders received instead)
- [ ] Q-R2-9 (physical LED part + pinout) to Trey
- Files: `rev2b_2026-10-09/` (board + BOM). Root files stay the Round 2 / Gerber-verified set.

## R2 Final — Synthesis
**Status: COMPLETE** (2026-10-07) — asks reviewed with the user; plain-language version published for Trey as a Claude Doc (link in `FINAL_REPORT_2026-10.md`); F-072 (back-silk artwork) dropped from the shared version as irrelevant
- [x] Verification sweep: 37/38 confirmed, F-065 plausible; Round 1 closures and persistences listed in `FINDINGS.md`
- [x] Ranked report: Tier 1 (3 items: C25 rating, 9 V ladder vs display current, LED drive) → Tier 2 (BOM, display mounting, back-side artwork, regulator part/footprint) → Tier 3 (fab margins) → Tier 4 (robustness) + passes + 7 questions
- **Deliverable:** ✅ `FINAL_REPORT_2026-10.md` (draft)
