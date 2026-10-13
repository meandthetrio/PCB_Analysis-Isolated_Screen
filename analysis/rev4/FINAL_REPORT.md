# WavetableController Rev 4 — Final Red-Flag Report
**Date:** 2026-10-13 · **Inputs:** the rev-4 KiCad project, BOM and Gerbers Trey sent 2026-10-13 (`rev4/`) · **Baselines:** the rev-3 review (`analysis/rev3/`, branch `claude/charming-meitner-c0w1jh`, 65 entries) and the 7 October "Rev 2 Design Review" rows as scored there, plus the post-rev-3 chat decisions (LED values, /+9V_FLAG re-pointing, encoder RC placement, SD caps, inrush) · **Scope:** Passes 0–6 complete (`HIGH_LEVEL_PLAN.md`), 57 rev-4 ledger entries (`FINDINGS.md`), every rev-3 finding re-scored, every Oct-7 row re-scored (`OCT7_REVIEW_STATUS.md`) · **Truth:** the rev-4 `.kicad_pcb` carries the filled GND pour and is copper truth; the Gerbers Trey plotted from it agree with it on every number; nothing has been fabbed from rev 4.
**Verification state:** 55 of 57 entries confirmed by script against the files; 1 plausible, blocked on Trey (R4-P3-07, pot taper); settled facts not re-opened.

---

## The short version

Rev 4 is a targeted patch of rev 3, not a re-layout: outside the changed parts the copper is identical to the millimetre (same 74.9 mm of 0.1 mm trace, same pour fragments, same SPI/SD/USB/MIDI/audio routes, same J8, same holes). Within that patch Trey closed most of what was open after rev 3:

**Moved from NOT DONE to DONE:** 2c (U6 now fed ahead of the 3.3 Ω filters; the LED/buck node is ≈ 8.1 V and no longer tracks the display), 3c (510 Ω red / 390 Ω green-blue, exactly decision 5a: 11.6–12.1 mA, 57–69 mW in 0603), 6b (L1 on the Murata DFE201610P pattern), 9 (D6 deleted; bridge is now 1N5817W SOD-123FL, IFSM 25 A), and the SD-socket caps (10 µF at 5.2 mm, 100 nF at 6.9 mm from P1 VDD). Row 7 (encoder RC) is done but with the 10 nF caps at the encoders on the back instead of at the Daisy pins on the front as agreed. **Still NOT DONE:** row 5 (J8 position and the four M2 holes), the 3d documentation item (schematic still says CLS6B-FKW, LEDs on no BOM sheet), all five fab-margin rows, and the ERC / PWR_FLAG / hand-assembly / mounting-hole / UART-beside-audio tidy items. Of the 65 rev-3 entries: 4 fixed, 20 re-pass, 4 settled, 37 still open — none regressed, one got a pad worse (a ninth single-spoke GND thermal, on the new SD cap).

## Tier 1 — Will bite on the next build as the files stand

**1. The display still has nowhere to mount.** (R4-P6-05 ✔, row 5 NOT DONE)
J8 is exactly where it was (pin 1 at (196.26, 81.30)); the NPTH set is byte-for-byte rev 3's; there are no M2 holes for the NHD module and no chassis holes for the board. The 9 g module hangs on 20 solder joints behind a panel window. *Fix: move J8 to y 86.3, add the four Ø2.4 holes at (135.0/209.2, 84.3/126.8) and clear R2/R5/U1 from under them, put the outline and holes in the J8 footprint.*

**2. The LEDs still do not exist for the assembler.** (R4-P4-01 ✔, R4-P2-03)
F.Paste is exactly LED1 + LED2's 12 apertures; the BOM has 38 lines and none is an LED; there is no hand-solder sheet; the schematic still names the Cree part with the Cree pin labels. Polarity and footprint are right for the Würth 150505M173300 (settled), so this is bookkeeping — but bookkeeping that returned rev 2's boards without LEDs. *Fix: Value → 150505M173300, relabel pins, add a hand-solder sheet listing LED1/LED2 plus the 18 THT parts.*

**3. Zero ground stitching vias, still.** (R4-P1-08 ✔)
0 of 253 vias are on GND. The F.Cu pour is 15 fragments joined to the one-piece B.Cu plane only through component holes; three fragments hang on one pad; the same 10 IC/cap GND pads (U2, U3, U4, U6) reach ground by one thin track; nine GND pads have a single thermal spoke (the new C28 joined that list). *Fix: stitch every fragment and the IC grounds; min spokes or short GND tracks on the nine pads.*

## Tier 2 — Done differently, or half done

**4. Encoder filter caps are at the wrong end of the line.** (R4-P3-03, R4-P5-04 ✔; row 7)
The four 10 k pull-ups and four 10 nF caps are present and wired, but all eight parts cluster at the encoders on the back: C19/C20 6.8–7.2 mm from ENCL1's pins and 63 mm from Daisy pins 32/33; C21/C22 10 mm from ENCR1's pins and 111 mm from pins 12/13. Decision 5c put the caps within ~2 mm of the Daisy pins on the front face. As built the RC debounces the contact at its source (the Bourns-style arrangement) but leaves each MCU input on an unterminated 63–111 mm trace. Workable with the state-table decoder; the rev-3 free spots (143.9,147.4), (146.5,147.4), (135.8,159.0), (133.2,159.0) are still free if Trey wants the agreed placement.

**5. Inrush: smaller, not limited.** (R4-P2-05 ✔; decision 5e NOT DONE)
No series resistor or NTC was added before C15. Bulk on the ~8 V side fell from 700 to 310 µF and the unlimited-path capacitance from 200 to 100 µF, but removing D6 and FB7 also removed 0.45 V and 50 mΩ from the path: the stiff-adapter bound into C15 is now ≈ 30 A. The 1N5817W bridge survives that (25 A IFSM is an 8.3 ms rating; this pulse is ≈ 25 µs); SW1's and the jack's contacts, and the cap bounce on power-up, are the remaining reason for the 1–2.2 Ω.

**6. Decoupling: the socket is fixed, the amp is not.** (R4-P2-06 ✔, R4-P2-07, R4-P2-08)
C27/C28 at P1 close the SD-rail item; the optional second 10 µF at Daisy pin 38 was not added (C28 is 27.9 mm from it, acceptable). The TPA6110A2 still has only 100 nF on /+3V3_A (F-031, third revision running).

**7. Signal proximity unchanged.** (R4-P5-02, R4-P5-03 ✔)
/USART1_RX 49 mm beside AUDIO_IN_L at 0.41 mm, /USART1_TX 26 mm at 0.45 mm; **/TAC_SWITCH_2 27 mm beside AUDIO_OUT_R at 0.20 mm** (the closest pairing on the board, same layer). /RES_SPI still floats (R4-P3-05). SPI, SD, USB, MIDI and audio otherwise as rev 3.

## Tier 3 — Fab margins (all five Oct-7 rows still NOT DONE)
MK1 annular ring 0.175 mm vs 0.18 (R4-P1-02); P2 NPTH-to-copper 0.197 vs 0.20 (R4-P1-03); U6 EP vias 0.25 mm drill vs the project's 0.30 rule (R4-P1-04); silk outlines 0.12 mm (R4-P6-02); `.kicad_pro` byte-identical to rev 3 with `min_track_width 0.0` / `min_clearance 0.0` (R4-P1-12). 74.9 mm of 0.1 mm copper remains, unchanged (R4-P1-01). DRC at JLCPCB's minimums: 0 width / clearance / edge / drill errors.

## Tier 4 — Hygiene
ERC 51 items identical to rev 3: 14 NC flags and 4 PWR_FLAGs still missing (R4-P3-06, R4-P2-11). BOM: no hand-assembly sheet, pos-file exclusion only on J3–J7, hand-edited cells (D2–D5's footprint cell says SOD-323 for the SOD-123FL part ordered — correct part, stale text), refdes repurposed again (C19–C22, R31/R32: any rev-3 note naming them is stale; R4-P4-05/06). Two dangling LED vias (R4-P1-07). Back-side artwork buries the B-side refdes (R4-P6-01). Headphones1 taper/rotation still for Trey (R4-P3-07 ⏳); its bushing exits 9 mm outside the outline (R4-P6-07).

## What passed (verified, cited)
Schematic ↔ PCB 112/112, 0 net diffs, 0 duplicate refdes · BOM ↔ sch ↔ PCB 92/92 three-way, values 92/92, 4/4 new LCSC numbers verified by part page · U6 fed from the FB6 node, ≈ 8.1 V, 3–17 V window · LED currents 11.6/12.1 mA, 57–69 mW in 0603 · D6/FB7 gone, 1N5817W bridge on matching pads · L1 on the Murata pattern, loop unchanged · SD socket decoupled · Daisy VIN 6.8–7.5 V, grounds tied, reverse polarity by bridge · IPC-2221 on every rail · encoder pull-ups and caps wired and routed · J8 = NHD table 20/20 · DRC at JLC minimums clean · courtyards, outline, mask, hole spacing clean.

## Questions for Trey (⏳)
1. **Encoder caps:** was placing C19–C22 at the encoders deliberate (source-side debounce), or should they move to the Daisy-pin spots as agreed?
2. **Headphones1:** CW = louder as wired, and is linear taper intended? (carried from rev 3)
3. **Display mounting:** when will row 5 (J8 move + M2 holes) be done — it gates the enclosure window.

## Threshold-source caveats
As rev 3 (Daisy, Cree, Murata hosts blocked; Daisy pin facts from the KiCad symbol and libDaisy; SSD1322 10 MHz from memory). JLCPCB caps and the four new part pages fetched live 2026-10-13.
