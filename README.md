# PCB Analysis — WavetableController (Daisy Seed synth)

**Read this first.** This folder holds a design review of Trey's "WavetableController" board — an Electrosmith Daisy Seed–based wavetable synth controller, 2-layer, 165×102 mm, designed in KiCad 9 — in two rounds:

- **Round 1 (2026-08, complete):** review of the boards that were fabbed twice at JLCPCB (`Manifold_Gerb_LedFix/`). Output: [analysis/FINAL_REPORT.md](analysis/FINAL_REPORT.md) + findings F-001…F-035 in [analysis/FINDINGS.md](analysis/FINDINGS.md).
- **Rev 2b (2026-10-09, partial):** Trey's revised board + BOM after the Round 2 review, stored in `rev2b_2026-10-09/`, diffed in [analysis/REV2B_DIFF_2026-10-09.md](analysis/REV2B_DIFF_2026-10-09.md); schematic still outstanding. The plain-language review shared with Trey is exported at [analysis/REV2_DESIGN_REVIEW_shared_doc.md](analysis/REV2_DESIGN_REVIEW_shared_doc.md).
- **Round 2 (2026-10, complete):** review of the revised file set Trey sent on 2026-10-07 (`Manifold_Gerbs_2026-10/`, the root KiCad files, and a 2026-10-06 BOM). Output: [analysis/FINAL_REPORT_2026-10.md](analysis/FINAL_REPORT_2026-10.md) + findings F-036…F-073, backed by `PASS0…PASS6_*_2026-10.md`. Pass plan and status: [analysis/HIGH_LEVEL_PLAN.md](analysis/HIGH_LEVEL_PLAN.md) (Round 2 section at the end).

**If you are Claude opening this fresh:** Round 2 is complete; the next step is whatever the user asks after reviewing `analysis/FINAL_REPORT_2026-10.md` (likely edits to the asks, then a shareable version for Trey, then Round 3 on his revised files). Do not re-derive anything that is already in `FINDINGS.md`. Methodology and which-file-is-truth rules are in [analysis/SOURCE_OF_TRUTH.md](analysis/SOURCE_OF_TRUTH.md).

## Folder contents

| Path | What it is |
|---|---|
| `WavetableController.kicad_pro` / `.kicad_sch` / `.kicad_pcb` | **Round 2** KiCad 9 design files (received 2026-10-07). Verified to be the exact source of `Manifold_Gerbs_2026-10/` (re-plot is byte-identical). The `.kicad_pcb` is 31.7 MB because the front-panel artwork lives on B.Silkscreen as ~3,900 polygons |
| `Manifold_Gerbs_2026-10/` | **Round 2** Gerbers + drills, plotted 2026-10-07 from the files above. Whether this set has gone to fab is an open question (Q-R2-1) |
| `ManifoldRe_BOM_NEW - Excel Format.xls` | **Round 2** JLCPCB-format BOM, saved 2026-10-06 (37 lines) |
| `Manifold_Gerb_LedFix/` | **Round 1** Gerbers + drills actually sent to JLCPCB ("LedFix" round, 2nd proto, plotted 2026-07-22). **Fab truth for the boards that physically exist.** |
| `rev2b_2026-10-09/` | Trey's **2026-10-09** board (31.9 MB) + BOM (90 designators), received after the Round 2 review. No Gerbers, no schematic yet. Not the Gerber-verified set — see `analysis/REV2B_DIFF_2026-10-09.md` |
| `archive/rev1_2026-08/` | Round 1 KiCad files + BOM, kept for reference. The `.kicad_pcb` there is the stale no-pour copy described below — never plot from it |
| `analysis/` | Both rounds: FINAL_REPORT (Round 1), findings ledger, SOURCE_OF_TRUTH, PASS1–6 reports (Round 1), PASS0_BASELINE_2026-10 (Round 2), `baseline_2026-10/` ERC/DRC JSON, REV2 OLED plan, routing CSVs, board SVG, parser script. Has its own [README](analysis/README.md) index. |
| `screen mounting solution.md` | Mechanical mounting guide for the Round-1-planned Crystalfontz CFAL12864G-024W COG OLED. Note: Round 2 files use a Newhaven NHD-2.7-12864WDW3 on SPI instead (F-043) — this guide needs revisiting |

## Critical provenance warning (Round 1 files — historical)

**Resolved for Round 2:** the 2026-10 `.kicad_pcb` re-plots to byte-identical Gerbers, so the Round 2 set is a single consistent truth (F-036). The paragraph below describes the Round 1 files now in `archive/rev1_2026-08/`.

Trey sent files reluctantly and in stages: Gerbers+BOM first, then .pro/.sch, then the .kicad_pcb last. File mtimes are transfer times, not edit times. The `.kicad_pcb` in this folder matches the LedFix Gerbers ~97% **but contains NO GND pour** (only 5 keepout zones), while the fabbed B.Cu Gerber has a 164×100 mm filled pour covering 44/63 GND pads. It is a stale/wrong version — **never regenerate Gerbers from this copy.** Standing ask: get Trey's real working .kicad_pcb (the one that shows a filled B.Cu pour when opened). Where sch and pcb disagree (e.g. LED2 wiring), the pcb matches the fabbed boards, so the schematic is the outlier.

## Round 2 (2026-10) status after Pass 0

What the new files show versus the fabbed board (details in `analysis/PASS0_BASELINE_2026-10.md`): GND pour present on both layers; duplicate R21 gone; encoder clicks routed; 0.1 mm trace length cut from 3850 mm to 73 mm; display moved from I2C to a Newhaven NHD-2.7-12864WDW3 on SPI with its own TPS62172 buck; power entry reworked. New project-rule DRC errors to size against JLCPCB in Pass 1: two 0.25 mm drills under U6, three +3V3_D tracks 0.451 mm from the board edge, nine single-spoke GND thermals. BOM adds a U5 that does not exist in the design.

## Round 1 headline findings (fabbed LedFix boards; details + evidence in analysis/)

- **Encoder push-buttons dead** — ENCL_CLICK / ENCR_CLICK have zero copper in the Gerbers (floating inputs; ENCR lands on a 3.3V-only Daisy pin). Fab-confirmed.
- **RGB LEDs triple-broken** — LED1/LED2 (CLS6B-FKW) are unplaced (missing from BOM, though the paste stencil expects them), reverse-biased via 300Ω to +9V_FILT (never light either polarity), and three LED pins sit on Daisy's 3.3V-only pins 24/25/30.
- **I2C has zero pull-ups in-design** — the ~203 mm bus relies entirely on the OLED module's onboard pull-ups (open question F-027 for Trey).
- **Duplicate refdes R21** — a layout-only 300Ω footprint at (170.1, 84.8) bridges /OLED_HOT–/+3V3_D in parallel with FB4 (Trey's noise-debug hack, on physical boards, not in schematic). Pick-and-place would put 300Ω where the 10Ω OLED damper belongs; breaks BOM/CPL matching.
- **0.1 mm traces board-wide** — exactly AT JLCPCB's 2-layer 1oz minimum (not below it), zero margin; carries the +3V3_D rail, I2C, SD, MIDI, USB. Recommend 0.2–0.25 mm. DRC min_track_width is 0.0 in the .kicad_pro, so KiCad won't flag them.
- **BOM refdes mismatch** — BOM's S1/S2 don't exist in the schematic (real refs are TAC_SWITCH_1/2, TAC_SHIFT_L1/R1 — note: underscore refs escape `[A-Z]+[0-9]+` regexes).
- 3 marginal fab violations (MK1 annular ring, P2 NPTH clearance, SW1 edge copper — the last is a deliberate notch, accepted). Power design: USB-C is data-only by design; 9V barrel → Schottky bridge → +9V_FILT (~8.3V).

**Open questions blocked on Trey:** F-014 (LED2 sch-vs-pcb, which is intended), F-027 (OLED module pull-up value), and the real .kicad_pcb with the GND pour.

## Rev-2 screen work (planning only, no design files changed)

[analysis/REV2_OLED_PLAN.md](analysis/REV2_OLED_PLAN.md): replace the two HiLetgo SSD1309 modules (boost-coil whine) with bare COG panels on 0.5 mm ZIF, independent I2C addresses 0x3C/0x3D. Two candidate panels:

- **Mono:** Crystalfontz CFAL12864G-024W (2.4", SSD1309) — needs 12.5–13.5V VCC, so a 15V adapter + ~13V LDO. Mounting solved in `screen mounting solution.md`.
- **Greyscale (user's preference):** no 2.42" greyscale panel exists anywhere. Best match is Raystar REX012864U / Winstar WEO012864U — 2.7" SSD1357, 16-level grey, VCC 8–10.5V (12V adapter + 10V LDO). **Unresolved geometry flag:** two 73 mm glasses = 146 mm side-by-side and conflict with the x≈165–200 audio-corridor keep-out. Fallback: stay mono, or 1.54" SSD1327.

Board changes either way: add 2.2k I2C pull-ups, remove J2/FB4/C14/C17/both R21s, use Daisy spare pads 22 & 28 for RES# and VCC_EN sequencing.

## Tooling notes

- **KiCad 9.0.9 (Linux / Claude Code on the web):** `kicad-cli` and the `pcbnew` Python module are on PATH. `.claude/hooks/session-start.sh` (a SessionStart hook) runs `tools/kicad_env_setup.sh` automatically in web sessions; run it by hand with `sudo tools/kicad_env_setup.sh` elsewhere. It installs the stock symbol/footprint libs and seed the user library tables (otherwise ERC/DRC add ~190 "library not found" warnings). `tools/kicad_check.sh` runs ERC, DRC, netlist, Gerber, SVG and PDF exports into `kicad_out/` (git-ignored) as a smoke test.
- **Freerouting 2.4.1 autorouter** is installed by the same setup script (needs Java 25, installed alongside the system Java 21; `freerouting` wrapper on PATH runs it headless with analytics off). `tools/autoroute.py IN.kicad_pcb OUT.kicad_pcb [--passes N]` does DSN export → route → SES import. It temporarily renames the duplicate R21, because the Specctra exporter refuses boards with duplicate refdes (an independent confirmation of that finding). On the stale checked-in board, 2 passes took 53 unrouted connections to 5. Remaining lib warnings name Trey's private libs (`Retroactive_Custom_Parts`, `Jack_3.5mm_CUI_RetroactiveCustom`, `SOP-6_...(RetroactiveCustom)`), which only exist on his machine; footprints are embedded in the `.kicad_pcb`, so they are harmless. Note `pcbnew.LoadBoard(...).Zones()` returns 0 here because the 6 keepout zones live inside footprints, not at board level.
- On Trey's Mac, KiCad 10.0.5 lives at `/Applications/KiCad.app` (kicad-cli at `Contents/MacOS/kicad-cli`; brew cask fails without sudo).
- `analysis/gerber_analyze.py DIR` is the Gerber parser that produced the routing CSVs (`DIR` defaults to `Manifold_Gerb_LedFix/`; pass `Manifold_Gerbs_2026-10` for Round 2). Other scratch scripts (pcb_parse.py, pcb_audit.py, DRC/ERC reports) lived in a session scratchpad and may be gone — regenerate from gerber_analyze.py patterns if needed.
- Net names in the routing CSVs are geometrically inferred (anchored at Daisy pins, 6/6 validated on LED nets), not authoritative; `island_*` = unidentified copper.
