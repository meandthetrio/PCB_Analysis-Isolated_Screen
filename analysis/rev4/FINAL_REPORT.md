# WavetableController Rev 4 — Final Red-Flag Report
**Date:** 2026-10-13 · **Inputs:** the rev-4 KiCad project, BOM and Gerbers Trey sent 2026-10-13 (`rev4/`) · **Baselines:** the rev-3 review (`analysis/rev3/`, branch `claude/charming-meitner-c0w1jh`, 65 entries) and the 7 October "Rev 2 Design Review" rows as scored there, plus the post-rev-3 chat decisions (LED values, /+9V_FLAG re-pointing, encoder RC placement, SD caps, inrush) · **Scope:** Passes 0–6 complete (`HIGH_LEVEL_PLAN.md`), 57 rev-4 ledger entries (`FINDINGS.md`), every rev-3 finding re-scored, every Oct-7 row re-scored (`OCT7_REVIEW_STATUS.md`) · **Truth:** the rev-4 `.kicad_pcb` carries the filled GND pour and is copper truth; the Gerbers Trey plotted from it agree with it on every number; nothing has been fabbed from rev 4.
**Verification state:** 55 of 57 entries confirmed by script against the files; 1 plausible, blocked on Trey (R4-P3-07, pot taper); settled facts not re-opened.

**Decisions after the passes ran (Kyle, 2026-10-13):** the screen is not mounted in this build (row 5 deferred); the LEDs are hand-soldered Würth 150505M173300 (the missing BOM line is paperwork); the encoder caps at the encoder end are accepted. The tiers below reflect those decisions.

---

## The short version

Rev 4 is a targeted patch of rev 3, not a re-layout: outside the changed parts the copper is identical to the millimetre (same 74.9 mm of 0.1 mm trace, same pour fragments, same SPI/SD/USB/MIDI/audio routes, same J8, same holes). Within that patch Trey closed most of what was open after rev 3:

**Moved from NOT DONE to DONE:** 2c (U6 now fed ahead of the 3.3 Ω filters; the LED/buck node is ≈ 8.1 V and no longer tracks the display), 3c (510 Ω red / 390 Ω green-blue, exactly decision 5a: 11.6–12.1 mA, 57–69 mW in 0603), 6b (L1 on the Murata DFE201610P pattern), 9 (D6 deleted; bridge is now 1N5817W SOD-123FL, IFSM 25 A), and the SD-socket caps (10 µF at 5.2 mm, 100 nF at 6.9 mm from P1 VDD). Row 7 (encoder RC) is done with the 10 nF caps at the encoders on the back — Trey found no room at the Seed, and that placement is accepted as better than none.

**Deferred by decision:** row 5 (J8 position and the four M2 holes), because the screen is not being mounted in this build.

**Documentation only:** the 3d item (schematic still says CLS6B-FKW, LEDs on no BOM sheet) — Trey hand-solders the approved Würth part.

**Still NOT DONE:** all five fab-margin rows and the ERC / PWR_FLAG / hand-assembly / chassis-hole / UART-beside-audio tidy items. Nothing on the Oct-7 fix list blocks ordering rev 4.

Of the 65 rev-3 entries: 4 fixed, 20 re-pass, 4 settled, 37 still open — none regressed, one got a pad worse (a ninth single-spoke GND thermal, on the new SD cap).

## Tier 1 — Worth fixing before ordering (judgment; nothing here is a fab rejection)

**1. Ground stitching — zero stitching vias; an easy fix and cheap insurance against noise.** (R4-P1-08 ✔; first raised in the rev-3 review, not on the 7 Oct list)

*What it is, plainly:* everything on the board **is** connected to ground (DRC: 0 unconnected items). The issue is how the two ground layers join each other. The board has a ground copper fill on both sides. The bottom one is a single sheet. The top one is chopped into 15 separate patches by the tracks running across it. Normally a designer drops small plated holes called stitching vias every centimetre or so, purely to tie each top patch to the bottom sheet. This board has 253 vias and not one is on ground: the only places a top patch touches the bottom sheet are where a component's through-hole pin passes through both, and three patches rely on a single pin for that. The same 10 IC/cap GND pads (U2, U3, U4, U6) reach ground by one thin track, and nine GND pads have a single thermal spoke (the new C28 joined that list).

*Why it matters:* when a signal runs on the top layer over a top ground patch, its return current wants to flow in that patch directly underneath. If the patch has only one way back to the main sheet, the return current detours, and that detour is what couples noise between circuits. On an audio board the symptom is hum or a faint digital hash in the headphones, not a dead board; the rev-1 boards worked without it.

*Fix:* a few minutes in KiCad — add GND vias (0.6/0.3, like the rest) in every top-side ground patch, especially the three single-pin ones, and next to the U2/U3/U4/U6 ground pads; set the zone's minimum spokes to 2 or add a short GND track on the nine single-spoke pads.

**2. Inrush — no series resistor before C15; smaller than rev 3, but not limited.** (R4-P2-05 ✔; decision 5e NOT DONE; first raised in the rev-3 review, not on the 7 Oct list)

*The exact scenario:* the unit is off, so the 100 µF capacitor C15 holds no charge. The 9 V adapter is plugged in, or SW1 is flipped on. For the first few microseconds an empty capacitor behaves like a short circuit, and the current that rushes in to fill it is limited only by what is in the path: the adapter's output, the barrel-jack contacts, the switch contacts, two diode drops and three ferrite beads at 0.05 Ω each — roughly a quarter of an ohm in all, so a peak of up to ≈ 30 A for ≈ 25 µs from a stiff adapter (a computed upper bound; a real adapter's output impedance lowers it).

*What it does and does not hurt:* the diodes are fine (the 1N5817W's 25 A IFSM is an 8 ms rating; this pulse is 300× shorter). The adapter is fine (it sags briefly). **The switch and jack contacts are the wear item:** each power-on puts a small spark across them as they close, and the slide switch does it several times per flip because of contact bounce. Over hundreds of cycles that pits the contacts, and the symptom is a supply that drops out when the unit is bumped or the switch wiggled — a slow failure, not a day-one one. Rev 1/2 never had this (10 µF at the input); rev 3 added 700 µF; rev 4 cut it to 310 µF, which helps, but the 100 µF directly on the unprotected path remains, and removing D6 and FB7 took 0.45 V and 50 mΩ out of the path.

*Fix:* one part — a 1 Ω, 1 W resistor between FB5 and C15 (or an NTC). It caps the peak at ≈ 8 A and costs 0.45 V and 0.2 W at full load; Daisy VIN still sits ≈ 7 V, inside 4–17 V. Cheap insurance for SW1 and the jack; can go in the next spin if not this one.

**If only one of these two is fixed for this build, make it the ground vias.**

## Acknowledged / deferred by decision (Kyle, 2026-10-13)

- **Display mounting (row 5, R4-P6-05):** "Acknowledged — will potentially deal with later." The screen is not mounted in this build. J8 is where it was and there are no M2 or chassis holes; if the module is fitted later it hangs on 20 solder joints until the holes exist. Nothing to do now.
- **LED bookkeeping (R4-P4-01, R4-P2-03, R4-P6-04):** Trey hand-solders Würth 150505M173300 (part already approved); polarity and footprint are right for it. What remains is paperwork: Value → 150505M173300, relabel the symbol pins, and a hand-solder sheet so the next builder knows. No assembly gap.
- **Encoder filter caps (row 7, R4-P3-03, R4-P5-04):** no room near the Seed, so the 10 nF caps sit at the encoders on the back (6.8–10.2 mm from the encoder pins, 63–111 mm from the Daisy pins). Accepted as better than none: it debounces the contact at the source; keep the state-table decoder in firmware.

## Tier 2 — Half done or unchanged robustness items

**3. Decoupling: the socket is fixed, the amp is not.** (R4-P2-06 ✔, R4-P2-07, R4-P2-08)
C27/C28 at P1 close the SD-rail item; the optional second 10 µF at Daisy pin 38 was not added (C28 is 27.9 mm from it, acceptable). The TPA6110A2 still has only 100 nF on /+3V3_A (F-031, third revision running).

**4. Signal proximity unchanged.** (R4-P5-02, R4-P5-03 ✔)
/USART1_RX 49 mm beside AUDIO_IN_L at 0.41 mm, /USART1_TX 26 mm at 0.45 mm; **/TAC_SWITCH_2 27 mm beside AUDIO_OUT_R at 0.20 mm** (the closest pairing on the board, same layer). /RES_SPI still floats (R4-P3-05). SPI, SD, USB, MIDI and audio otherwise as rev 3.

## Tier 3 — Fab margins (all five Oct-7 rows still NOT DONE)
MK1 annular ring 0.175 mm vs 0.18 (R4-P1-02); P2 NPTH-to-copper 0.197 vs 0.20 (R4-P1-03); U6 EP vias 0.25 mm drill vs the project's 0.30 rule (R4-P1-04); silk outlines 0.12 mm (R4-P6-02); `.kicad_pro` byte-identical to rev 3 with `min_track_width 0.0` / `min_clearance 0.0` (R4-P1-12). 74.9 mm of 0.1 mm copper remains, unchanged (R4-P1-01). DRC at JLCPCB's minimums: 0 width / clearance / edge / drill errors.

## Tier 4 — Hygiene
ERC 51 items identical to rev 3: 14 NC flags and 4 PWR_FLAGs still missing (R4-P3-06, R4-P2-11). BOM: no hand-assembly sheet, pos-file exclusion only on J3–J7, hand-edited cells (D2–D5's footprint cell says SOD-323 for the SOD-123FL part ordered — correct part, stale text), refdes repurposed again (C19–C22, R31/R32: any rev-3 note naming them is stale; R4-P4-05/06). Two dangling LED vias (R4-P1-07). Back-side artwork buries the B-side refdes (R4-P6-01). Headphones1 taper/rotation still for Trey (R4-P3-07 ⏳); its bushing exits 9 mm outside the outline (R4-P6-07).

## What passed (verified, cited)
Schematic ↔ PCB 112/112, 0 net diffs, 0 duplicate refdes · BOM ↔ sch ↔ PCB 92/92 three-way, values 92/92, 4/4 new LCSC numbers verified by part page · U6 fed from the FB6 node, ≈ 8.1 V, 3–17 V window · LED currents 11.6/12.1 mA, 57–69 mW in 0603 · D6/FB7 gone, 1N5817W bridge on matching pads · L1 on the Murata pattern, loop unchanged · SD socket decoupled · Daisy VIN 6.8–7.5 V, grounds tied, reverse polarity by bridge · IPC-2221 on every rail · encoder pull-ups and caps wired and routed · J8 = NHD table 20/20 · DRC at JLC minimums clean · courtyards, outline, mask, hole spacing clean.

## Question for Trey (⏳)
1. **Headphones1:** CW = louder as wired, and is linear taper intended? (carried from rev 3)

## Threshold-source caveats
As rev 3 (Daisy, Cree, Murata hosts blocked; Daisy pin facts from the KiCad symbol and libDaisy; SSD1322 10 MHz from memory). JLCPCB caps and the four new part pages fetched live 2026-10-13.
