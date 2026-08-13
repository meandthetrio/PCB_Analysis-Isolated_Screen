# Source of Truth — PCB Analysis Methodology
**Project:** WavetableController (Electrosmith Daisy Seed wavetable synth controller, 2-layer 165×102mm, KiCad 9)
**Established:** 2026-08-12
**Status:** Governing document. Every analysis pass must follow these rules. Re-read before starting each pass.

---

## 1. Ground truth hierarchy

| Rank | Source | Role |
|------|--------|------|
| 1 | `WavetableController.kicad_pcb` | Authoritative layout (s-expression, fully parseable) |
| 1 | `WavetableController.kicad_sch` | Authoritative connectivity intent |
| 2 | `Manifold_Gerb_LedFix/*.gbr, *.drl` | What was actually sent to fab — cross-check against #1 |
| 3 | `ManifoldRe_BOM_NEW - Excel Format.xls` | Procurement — third independent source |

**Discrepancies between sources are themselves red flags** (e.g., BOM designators that don't exist in the schematic).

**Dual-truth rule (established 2026-08-12, see FINDINGS F-006/F-013/F-014/F-015):** the sources are ~97% aligned but NOT identical. Gerbers (plotted 2026-07-22) describe the physical boards that exist and work; the .kicad_sch/.kicad_pcb (saved 2026-08-12) are the current working intent, which diverges at: GND pour (Gerber-only), LED2 wiring (sch vs pcb disagree), duplicate R21 (pcb), reroutes near TAC_SWITCH_1/2 and the power entry. Every pass must state which truth it checks against: fab-related passes (1, 6) → Gerbers; intent-related passes (2, 3, 4, 5) → KiCad files, with Gerber cross-check where they diverge.

## 2. Core rules — how every finding is produced

1. **Every red flag = measured fact + cited threshold.** The measurement comes from a script; the threshold comes from a fetched authoritative source, never from model memory.
2. **Extract numbers with scripts, never by "reading and noticing."** Write parsers that emit complete tables (all trace widths, all clearances below X, full footprint↔BOM mapping). Judgment operates only on those tables. A script over the whole file can't fatigue halfway through.
3. **Don't hand-roll what a real tool does better.** Use `kicad-cli` ERC/DRC as the completeness anchor. Custom scripts fill only the gaps DRC doesn't cover (BOM cross-checks, current capacity, fab-specific rules).
4. **Never modify the design files.** DRC runs that need adjusted settings (e.g., the zeroed min_track_width) use a *copy* of the project in the scratchpad.
5. **Validate parsers before trusting them.** Every custom extraction gets a known-answer check (e.g., prior session validated Gerber-to-net matching 6/6 on LED nets before use).

## 3. Threshold sources (fetch live, per claim class)

| Claim class | Authoritative source |
|---|---|
| Fab rules (min trace/space/via/annular ring) | JLCPCB capabilities page — fetched 2026-08-12: 2-layer 1oz min 0.10mm/4mil, ±20% width tolerance; 2oz raises min to 0.16mm |
| Trace current capacity | IPC-2221 external-trace formula, computed per trace |
| Part behavior (pinouts, Vf, ratings) | The actual datasheet (Daisy Seed, CLS6B-FKW LED, etc.) |
| Interface rules | The relevant spec (USB 2.0 FS pair, I2C bus capacitance) |

## 4. Finding classification

Every finding is labeled exactly one of:

- **VIOLATION** — measured fact breaks a cited rule
- **ZERO-MARGIN** — at a limit but not past it (e.g., 0.1mm traces exactly at JLCPCB's minimum)
- **JUDGMENT** — recommendation; explicitly opinion, no rule citation claimed

And carries a status: `plausible` → `confirmed` / `refuted`. Nothing is reported as real until independently verified. Findings live in `analysis/FINDINGS.md` and never silently evaporate between passes.

## 5. Lessons already paid for (do not repeat)

1. **The 0.1mm trace error:** first flagged as *below* JLCPCB minimum from memory; fetching the actual capabilities page showed it's exactly *at* the 0.10mm minimum — a zero-margin finding, not a violation. → Rule 1 exists because of this.
2. **The "all DRC minimums are zero" overstatement:** a closer read showed only `min_track_width` and one clearance are zeroed; via/hole minimums are set. → Partial reads produce overstatements; run complete extractions.

## 6. Process

- One pass per domain (see `HIGH_LEVEL_PLAN.md`), reviewed between passes.
- After each pass: update FINDINGS.md, mark the pass complete in HIGH_LEVEL_PLAN.md, re-read this document before the next pass.
- Verification of `plausible` findings is a distinct step, done with independent method/source from the original detection.

## 7. Known project context (from prior sessions, 2026-08-12)

- Board is on its 2nd JLCPCB proto round; **boards physically work**.
- USB-C is data-only by design (9V barrel via Schottky bridge) — a deliberate choice after OLED/SSD1309 I2C noise debugging. Don't flag as an oversight.
- Known prior findings to re-verify against the now-available `.kicad_pcb`: LED 9V-drive bug (LED1/LED2 resistors to +9V_FILT vs 3.3V GPIOs), LEDs missing from BOM, phantom BOM designators S1/S2, 0.1mm traces on +3V3_D (~254mm run), SD, I2C, USB, MIDI, pot/encoder, LED nets.
