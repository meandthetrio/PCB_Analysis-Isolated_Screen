# WavetableController Rev 3 — Final Red-Flag Report
**Date:** 2026-10-09 · **Inputs:** the rev-3 KiCad project + BOM Trey sent 2026-10-09 (`rev3/`) · **Baselines:** the August review of the LedFix fab files (`analysis/`, F-001…F-035) and Kyle's 7 October "Rev 2 Design Review" doc of the intermediate files, scored item by item in `OCT7_REVIEW_STATUS.md` · **Scope:** Passes 0–6 complete (`HIGH_LEVEL_PLAN.md`), 65 ledger entries (`FINDINGS.md`), every rev-2 finding F-001…F-035 re-scored · **Truth:** the rev-3 `.kicad_pcb` carries the filled GND pour and is copper truth; nothing has been fabbed from these files yet.
**Verification state:** 60 of 65 entries confirmed by an independent method; 4 plausible, each blocked on information only Trey has (marked ⏳); 1 not applicable (I2C removed). The headline LED finding was verified three ways (Pass 2 script, Pass 3 script, coordinator's own netlist + datasheet-drawing check).

---

## The short version

Against the 7 October review (the list Trey was actually working from): 9 of its 19 fix items are done, 2 done with a different part, 7 not done, and the one that matters most, turning the LEDs around, is among the not-done. Full table in `OCT7_REVIEW_STATUS.md`.

Rev 3 is a real step forward: the ground pour is in the file, the 0.1 mm traces are 98 % gone, the encoder clicks are routed, the duplicate R21 and the whole I2C noise-fix thicket are gone, the schematic and PCB agree pad-for-pad, and the new SPI OLED header matches its datasheet pin-for-pin. Of the 35 rev-2 findings, 10 are fixed, 4 re-pass, 5 improved, 3 no longer apply.

But **the LED subsystem is still wrong in the files**: the LEDs are drawn reverse-biased (covered on the hand-built boards by a documented 180° placement), the footprint doesn't fit the part named on the schematic, and the LEDs are still not on the BOM. There are also two new mechanical gaps (no mounting holes for the display module or the board) and one new layout-robustness gap (no ground stitching vias at all).

## Tier 1 — Will fail on the next build as the files stand

**1. LEDs still cannot light as drawn, and the part/footprint don't match.** (R3-P2-01 ✔, R3-P2-02 ⏳, R3-P2-03, R3-P4-01 ✔, R3-P6-04 ✔)
This review does not know what LED Trey is actually using: the schematic names a Cree CLS6B-FKW, the footprint is for a different package, and the BOM has no LED line. Every polarity statement below is relative to the symbol's pin names, not a verified part.
The new NPN low-side drivers (Q1–Q6, 1 k base resistors) fixed the 3.3V-only-pin exposure, but the diode orientation was carried over unchanged: the Cree CLS6B-FKW anodes (pads 1/3/5) sit on the transistor collectors and the cathodes go through 300 Ω to the +9V rail. Current can never flow; when a transistor turns on the die sees about 5.5 V reverse against a 5 V rating. Separately, the custom `LED_RGB_5050-6_Retroactive Pin Out` footprint is a two-column 5050 pattern, while CLS6B-FKW is a 4.7 × 1.5 mm single-row part that cannot be placed on it. And the BOM still has no LED line while the paste layer has exactly their 12 apertures. *Disposition (Kyle, 2026-10-09): Trey hand-solders the LEDs and mounts them rotated 180° from the silk mark, which corrects the polarity on this three-row footprint for a row-paired two-column 5050 (red and blue swap, a firmware change). That makes the built board fine and leaves the files wrong. Still to do: confirm which LED is actually used (⏳ Trey, the 180° trick cannot work for the Cree part named on the schematic or for a diagonal-paired 5050); then flip the six dice in the schematic, relabel the symbol pins, use the real footprint, add the BOM line, and re-value the 300 Ω for the ≈5.8 V rail (R3-P2-04).*

**2. The display module has nowhere to mount.** (R3-P6-05 ✔, R3-P6-06 ⏳)
The NHD-2.7-12864WDW3 has four Ø2.5 mm holes on a 74.2 × 42.5 mm pattern. With J8 where it is, those holes land on R2, R5 and U1 and 0.7 mm from C22. The module only fits with its body toward +y; the other orientation overhangs the board edge by 24.7 mm (orientation inferred from the datasheet views — confirm against the STEP). `screen mounting solution.md` still describes the earlier Crystalfontz COG panel, not this module. *Fix: move/clear the four hole sites, add the holes, update the mounting doc.*

**3. L1 is on the wrong land pattern.** (R3-P4-02 ✔)
The Murata DFE201610P (2.0 × 1.6 mm) sits on `L_0805_2012Metric`: pads 0.4 mm narrower than the terminations, ≈50 % of the reference overlap, 0.5 mm overhang. It will often solder, but it is the only inductor on the new OLED buck. *Fix: swap to KiCad's stock `L_Murata_DFE201610P`.*

## Tier 2 — Robustness gaps that will show up as noise, heat or intermittents

**4. No ground stitching vias.** (R3-P1-08 ✔) The F.Cu pour is 15 fragments joined to the B.Cu plane only through component holes; three fragments hang on a single pad, and ten bottom-side GND pads on U2/U3/U4/U6 reach ground through one thin track. Eight GND pads have a single thermal spoke (R3-P1-06). *Fix: stitch every fragment and the IC grounds with vias.*

**5. Power entry: no inrush limit, and more series parts than needed.** (R3-P2-05, R3-P2-06 ✔) The buck, the 3.3 Ω/100 µF ladder and the bead chain were already in the design the 7 October review covered, and that review asked for 2 A beads, ½ W resistors and a 25 V C25, all of which were done. What it did not cover: 700 µF of bulk capacitance sits behind only Schottkys and bead DCR: ≈26 A peak at plug-in through diodes rated 9 A surge and 2 A beads. D6 duplicates the bridge's protection for another 0.4 V and ≈0.2 W; four identical beads are in series; the two 3.3 Ω π-filters make DSY_VIN ≈6.4–7.1 V and the "+9V" LED/OLED rail ≈5.8 V at 9 V in (all still within limits, R3-P2-07 ✔). *Fix: NTC or series R before C15, drop D6, consolidate beads, rename +9V_FLAG.*

**6. Decoupling left half-done.** (R3-P2-10, R3-P2-11 ✔) The 3V3_D trunk is now 0.3 mm (good) but still has one 100 nF for SD + MIDI + pull-ups, 111–120 mm from both the Daisy and the SD socket. The headphone amp still lacks its datasheet ≥10 µF. *Fix: 100 nF + 10 µF at P1, 10 µF at A1.38, 10 µF at U3.*

**7. Small signal-integrity items.** /RES_SPI floats until firmware drives it — add a 10 k (R3-P3-04). MIDI UART runs 26–49 mm parallel to AUDIO_IN_L at 0.41–0.45 mm on the same layer (R3-P5-04). USB pair now length-matched but 9/11 vias (R3-P5-03). TPS62172 input/output caps are 5–9 mm from the pins (R3-P2-08). SPI lines are fine at ≤10 MHz; optional 22–33 Ω series (R3-P5-01).

## Tier 3 — Fab margins (same three as rev 2, plus the project's own rules)

- MK1 annular ring 0.175 mm vs 0.18 absolute minimum (R3-P1-02); P2 USB-C NPTH-to-copper 0.197 vs 0.20 (R3-P1-03) — both unchanged footprint defects, fabbed OK twice before.
- 74.9 mm of 0.10 mm copper remains, almost all U4's DFN fan-out (R3-P1-01). DRC minimums are still zero in the project file (R3-P1-14), so KiCad would not have caught it.
- U6 thermal vias use a 0.25 mm drill: legal at JLC, but they break the project's own 0.30 rule and add a drill tool (R3-P1-04). The five copper-edge DRC errors are the project's 0.5 mm rule, not JLC's 0.2 (R3-P1-05).
- Silk: every refdes is exactly at the 1.0 mm / 0.15 mm legend minimum (R3-P6-02); the engraving artwork moved to the back and now buries 97 of 102 bottom-side refdes (R3-P6-01) — cosmetic, but rework gets harder.

## Tier 4 — Hygiene (ERC/BOM/docs)

LED resistors: within rating at 9 V, but the LEDs would only reach 8–12 mA because the rail behind R31/R32 is ≈5.8 V (R3-P2-04).

ERC: 14 missing no-connect flags + 4 PWR_FLAGs, all false positives (R3-P3-06, R3-P2-14). BOM: still no hand-assembly sheet, now 18 THT parts including the OLED-rail caps C23/C24 (R3-P4-03); "exclude from position" set on only 5 of 18 THT parts (R3-P4-04); file coerced/mojibaked by hand editing (R3-P4-05); C14/C15/C17 were silently repurposed so rev-2 notes naming them are stale (R3-P4-06); R35–R40 are an avoidable Extended part (R3-P4-07). SD card-detect still half-wired and all 40 Daisy pins are now used (R3-P3-10). The headphone pot is a linear taper used as a volume control (R3-P3-07 ⏳) and its bushing exits 9 mm outside the outline (R3-P6-07). Two dangling vias to delete (R3-P1-07).

## What passed (verified, cited)

Schematic ↔ PCB 110/110 parts, 0 net diffs, 0 duplicate refdes · GND pour filled, 0 islands, 0 unconnected · DRC at JLC minimums: 0 width/spacing/clearance errors · encoder clicks routed to GPIO-capable pins · J8 wiring = NHD serial pin table 20/20, 4-wire SPI strap, NC pins correct · TPS62172 sizing (2.2 µH / 22 µF / 10 µF, 345–375 mA OLED load vs 500 mA) · Daisy VIN in range, AGND/DGND tied, reverse-polarity protected · IPC-2221 ampacity on every rail, beads ≤25 %, 2512s ≤0.3 W · SD 24–41 mm with 47 k pull-ups · MIDI unchanged and correct · audio runs 28–69 % shorter and 3× wider · BOM 90/90 values and 11/11 new LCSC numbers correct · courtyards, outline, mask, via tenting, hole spacing all clean · 3.3V-only pins now isolated behind 1 k base resistors.

## The questions for Trey (⏳)

Design case confirmed by Kyle 2026-10-09: 9 V from the barrel jack. 12 V figures in the pass reports are the jack's ceiling, not a design case.

1. **Which RGB LED are you actually buying?** The schematic says Cree CLS6B-FKW (4.7 × 1.5 mm, single row) but the footprint is a two-column 5050. The polarity fix depends on the answer.
2. **Module orientation and mounting:** does the STEP (`Newhaven2.7_12864WDX3.STEP`) put the module body toward +y, and how will the module and the board be fastened?
3. **Headphone pot:** is CW = louder with the PTD902 terminal order as wired, and is a linear taper intended?

## Threshold-source caveats
daisy.audio and its mirrors, cree-led.com (text) and murata.com were blocked from this session; Daisy pin facts come from the stock KiCad symbol, libDaisy source and the rev-2 datasheet citation, and the Cree pinout from the datasheet PDF fetched via a mirror and read from its page-9 drawing. These are the first items to re-verify when the primary documents are to hand.
