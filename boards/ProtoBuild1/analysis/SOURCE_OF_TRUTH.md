# Source of Truth — ProtoBuild1 Analysis Methodology
**Project:** ProtoBuild1 "Rev K iron block" (Quad Eight project; tapped-inductor resonant EQ section, ±15 V, through-hole, 2-layer 170 × 130 mm, KiCad 10)
**Established:** 2026-11-07 · **Status:** governing document for this board; same rules as the Manifold review, re-stated here so this folder stands alone.

---

## 1. Ground truth hierarchy

| Rank | Source | Role |
|------|--------|------|
| 1 | `source/kicad-project/ProtoBuild1-zones-filled-kicad10-format.kicad_pcb` | Authoritative layout: the native KiCad 10.0.8 save that the Gerbers were plotted from (zone fill stored) |
| 1 | `source/kicad-project/ProtoBuild1.kicad_sch` | Authoritative connectivity intent (net-label style, one A1 sheet) |
| 2 | `source/gerbers/*.gbr, *.drl, *.gbrjob` | Candidate fab set, plotted 2026-11-07T09:42:06-06:00 by KiCad 10.0.8. **Not yet sent to a fab**, so there is no "fabbed truth" yet — the Gerbers are checked *against* rank 1, not the other way round |
| 2 | `source/kicad-project/ProtoBuild1.kicad_pcb` | Same board in a KiCad 8 file header without the zone fill (the pre-fill working file). Copper verified identical to rank 1 |
| 3 | `source/reports/` | The author's KiCad 10 ERC (0), DRC (0), netlist — corroboration only, re-run independently here |
| 4 | `source/ProtoBuild1-parts-list.xlsx` | Procurement — the independent third source for the BOM cross-check |

**Single-version situation (unlike Manifold):** every file in the upload was produced on the
same morning from the same design state; Pass 0 proved the schematic netlist, the board pad
nets and the Gerber copper agree 100 %. Where the KiCad 8-header and KiCad 10 board files
differ it is only the stored zone fill plus KiCad 10 pad-tenting/version tokens.

**Converted copies:** KiCad 9.0.9 cannot parse the shipped `.kicad_sch`/`.kicad_pcb` (PB-F-001).
All KiCad-9 work used copies made by `tools/kicad10_to_9.py` (strips four KiCad-10-only tokens
and swaps the embedded PWR_FLAG symbol for the stock one). The copies live in `kicad_out/` and
are **analysis-only**; the review verified they carry the same 57 nets and the same copper.

## 2. Core rules — how every finding is produced

1. **Every red flag = measured fact + cited threshold.** The measurement comes from a script; the threshold comes from a fetched source (`THRESHOLDS.md`), never from model memory.
2. **Extract numbers with scripts, never by "reading and noticing."** Complete tables (all pads, all rings, all nets), judgment only on the tables. Scripts are in `scripts/`.
3. **Don't hand-roll what a real tool does better.** `kicad-cli` ERC/DRC are the completeness anchor; custom scripts fill the gaps (fab rules, BOM join, Gerber cross-check, clearances KiCad's own rule set is not configured for).
4. **Never modify the design files.** DRC with JLCPCB minimums ran on a scratch copy with an edited `.kicad_pro` (`data/ProtoBuild1.jlcpcb-rules.kicad_pro`).
5. **Validate parsers before trusting them.** Gerber parser validated by exact match against the board file (768/768 segments); netlist parser validated by exact match between the KiCad 9 export, the author's KiCad 10 netlist and the board pads; BOM alias map validated against the schematic's bracketed names.

## 3. Threshold sources (fetched this review — see THRESHOLDS.md for the numbers)

| Claim class | Source |
|---|---|
| Fab rules | JLCPCB PCB capabilities page, fetched 2026-11-07 (2-layer, 1 oz) |
| Trace current / resistance | IPC-2221 external-trace formula, computed per width |
| Transistor pinout / ratings / thermal | onsemi KSC1845, KSA992, BD135/137/139, BD136/138/140 datasheets (pdftotext extracts in `datasheets/`) |
| Op-amp supply / current | TI NE5532 datasheet |
| DC-DC supply | Traco TEN 5 series datasheet (model TEN 5-1223) |
| Coil former geometry | Philips/Ferroxcube RM10/I data sheet (2000-04-20) |
| Heatsink, film-cap dimensions | distributor listings only (no manufacturer sheet found) — marked as such wherever used |

## 4. Finding classification

Exactly one of **VIOLATION** (measured fact breaks a cited rule), **ZERO-MARGIN** (at a limit),
**JUDGMENT** (recommendation; no rule claimed), plus a status `plausible → confirmed / refuted`.
IDs are `PB-F-nnn` so they never collide with the Manifold ledger's `F-nnn`.

## 5. Lessons already paid for (this board)

1. **Trust the file header, lose a morning.** "version 20240108 / generator_version 8.0" did not mean KiCad 8 content. Bisect by *adding* known-good pieces to a known-good header, not by regex-deleting sections — the first attempt left unbalanced fragments and every variant "failed" for the wrong reason.
2. **pcbnew's `LoadBoard` returns `None` silently** on a parse error and the plugin API aborts the interpreter; isolate each trial load in a subprocess.
3. **Point-in-polygon tests on KiCad zone fills lie about islands**: thermal-relief pads sit inside cut-ins that the test counts as "outside". Refill in KiCad with island removal on/off and compare outline counts instead (PASS1).
4. **The author's "DRC 0" was true and uninformative** — the project file carries no constraints; always re-run DRC with the fab's minimums in the constraints.

## 6. Process

One pass per domain (HIGH_LEVEL_PLAN.md). After each pass: update FINDINGS.md, mark the pass in
the plan, re-read this file. Verification of `plausible` findings uses an independent method
from the one that found them.
