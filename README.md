# PCB Analysis — WavetableController (Daisy Seed synth)

**Read this first.** This folder holds a completed design review of Trey's "WavetableController" board — an Electrosmith Daisy Seed–based wavetable synth controller, 2-layer, 165×102 mm, designed in KiCad 9. The board has been fabbed twice at JLCPCB and the physical boards mostly work. The analysis (all passes complete, 2026-08-13) found several real defects and produced a rev-2 plan.

**If you are Claude opening this fresh:** the authoritative output is [analysis/FINAL_REPORT.md](analysis/FINAL_REPORT.md) (tiered red flags + open questions for Trey), backed by the full findings ledger F-001…F-035 in [analysis/FINDINGS.md](analysis/FINDINGS.md). Do not re-derive anything before checking those. Methodology and which-file-is-truth rules are in [analysis/SOURCE_OF_TRUTH.md](analysis/SOURCE_OF_TRUTH.md).

## Folder contents

| Path | What it is |
|---|---|
| `WavetableController.kicad_pro` / `.kicad_sch` / `.kicad_pcb` | KiCad 9 design files, sent by Trey piecemeal (see provenance below) |
| `Manifold_Gerb_LedFix/` | The Gerbers + drill files actually sent to JLCPCB ("LedFix" round, 2nd proto). **Fab truth for copper.** |
| `ManifoldRe_BOM_NEW - Excel Format.xls` | JLCPCB-format BOM |
| `analysis/` | The full review: FINAL_REPORT, findings ledger, SOURCE_OF_TRUTH, PASS1–6 reports, REV2 OLED plan, routing CSVs extracted from Gerbers, board SVG, parser script. Has its own [README](analysis/README.md) index. |
| `screen mounting solution.md` | Mechanical mounting guide for the rev-2 Crystalfontz CFAL12864G-024W COG OLED (tape+gasket sandwich, plus 3D-printed bezel alternative) |

## Critical provenance warning

Trey sent files reluctantly and in stages: Gerbers+BOM first, then .pro/.sch, then the .kicad_pcb last. File mtimes are transfer times, not edit times. The `.kicad_pcb` in this folder matches the LedFix Gerbers ~97% **but contains NO GND pour** (only 5 keepout zones), while the fabbed B.Cu Gerber has a 164×100 mm filled pour covering 44/63 GND pads. It is a stale/wrong version — **never regenerate Gerbers from this copy.** Standing ask: get Trey's real working .kicad_pcb (the one that shows a filled B.Cu pour when opened). Where sch and pcb disagree (e.g. LED2 wiring), the pcb matches the fabbed boards, so the schematic is the outlier.

## Headline findings (details + evidence in analysis/)

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

- KiCad 10.0.5 is installed at `/Applications/KiCad.app` (kicad-cli at `Contents/MacOS/kicad-cli`; brew cask fails without sudo).
- `analysis/gerber_analyze.py` is the Gerber parser/net-matcher that produced the routing CSVs. Other scratch scripts (pcb_parse.py, pcb_audit.py, DRC/ERC reports) lived in a session scratchpad and may be gone — regenerate from gerber_analyze.py patterns if needed.
- Net names in the routing CSVs are geometrically inferred (anchored at Daisy pins, 6/6 validated on LED nets), not authoritative; `island_*` = unidentified copper.
