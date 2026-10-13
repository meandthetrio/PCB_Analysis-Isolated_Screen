# WavetableController Rev 4 — Final Red-Flag Report

| | |
|---|---|
| **Date** | 2026-10-13 |
| **Inputs** | Rev-4 KiCad project (board with filled GND pour), BOM and Gerbers, sent by Trey 2026-10-13 (`rev4/`) |
| **Baselines** | Rev-3 review (`analysis/rev3/`, 65 entries) · 7 October "Rev 2 Design Review" rows · post-rev-3 chat decisions (LED values, /+9V_FLAG re-pointing, encoder RC, SD caps, inrush) |
| **Scope** | Passes 0–6 complete · 57 rev-4 ledger entries (`FINDINGS.md`) · every rev-3 finding re-scored · every Oct-7 row re-scored (`OCT7_REVIEW_STATUS.md`) |
| **Truth** | The rev-4 `.kicad_pcb` is copper truth; Trey's Gerbers agree with it on every number; nothing has been fabbed from rev 4 |
| **Verification** | 55 of 57 entries confirmed by script against the files; 1 plausible, waiting on Trey (pot taper); settled facts not re-opened |

**Decisions recorded after the passes ran (Kyle, 2026-10-13)**

- The screen is **not mounted in this build** → Oct-7 row 5 is deferred.
- The LEDs are **hand-soldered Würth 150505M173300** (part already approved) → the missing BOM line is paperwork, not an assembly gap.
- The encoder filter caps **at the encoder end are accepted** (no room near the Seed; better than none).

---

## Headline

Rev 4 is a targeted patch of rev 3, not a re-layout. Outside the changed parts the copper is identical to the millimetre: same 74.9 mm of 0.1 mm trace, same pour fragments, same SPI / SD / USB / MIDI / audio routes, same J8, same holes. Inside the patch Trey closed most of what was open after rev 3.

| Oct-7 row | Rev 3 | **Rev 4** |
|---|---|---|
| 2c — U6 fed ahead of the 3.3 Ω filters | NOT DONE | **DONE** — LED/buck node ≈ 8.1 V, independent of the display |
| 3c — LED resistors 510 Ω red / 390 Ω green-blue | NOT DONE | **DONE** — 11.6–12.1 mA, 57–69 mW in 0603 |
| 6b — L1 on the Murata DFE201610P pattern | NOT DONE | **DONE** |
| 7 — Encoder 10 k pull-ups + 10 nF caps | NOT DONE | **DONE** — caps at the encoder end, accepted |
| 9 — Delete D6; bridge to SOD-123FL | NOT DONE | **DONE** — 1N5817W, IFSM 25 A |
| SD-socket caps | NOT DONE | **DONE** — 10 µF at 5.2 mm, 100 nF at 6.9 mm from P1 VDD |
| 5 — J8 position + four M2 holes | NOT DONE | **DEFERRED** — screen not mounted in this build |
| 3d — LED part name / BOM line | DOCUMENTATION | **DOCUMENTATION** — hand-soldered Würth confirmed |
| Fab-margin rows (5) and tidy items | NOT DONE | **NOT DONE** — see Tiers 3 and 4 |

**Nothing on the Oct-7 fix list blocks ordering rev 4.** Of the 65 rev-3 findings: 4 fixed, 20 re-pass, 4 settled, 37 still open. None regressed; one got a pad worse (a ninth single-spoke GND thermal, on the new SD cap).

---

## Tier 1 — Worth fixing before ordering (judgment; nothing here is a fab rejection)

### 1. Ground returns of the bottom-side ICs run on 0.1 mm stubs; stitching the top layer is optional
*(R4-P1-08 revised 2026-10-13 after Trey's note; measured on the rev-4 board)*

- **Trey's point, confirmed:** every component is on the bottom, and the bottom ground fill is **one solid piece** (12,789 mm², 77 % of the board). The top-layer ground fragments are leftover copper that only the hand-soldered through-hole parts touch; they sit in no return path. 73 % of all signal routing (3,157 of 4,354 mm) is on the top layer, and those traces return through the solid bottom plane directly beneath them, which is exactly the right arrangement for a two-layer board. **Stitching the top fragments is therefore not a fix for anything; it is optional tidying** (marginally lower loop inductance for the 27 % of signals routed on the bottom, a little shielding). The earlier "easy fix, cheap insurance" framing overstated it.
- **What the same scan does show, and what matters for a bottom-only design:** ten IC ground pins on the bottom do not touch the plane at all, because their fine-pitch pads sit inside the zone's 0.5 mm clearance. Each reaches ground through a single track: U2.2 (USB ESD) 3.3 mm × 0.3 mm; U3.2 / U3.3 (headphone amp) 2.9 mm × 0.3 mm; **U4.4 / 7 / 9 / 11 (mic amp) 1.2–4.8 mm × 0.1 mm**; **U6.1 PGND 3.6 mm × 0.1 mm, U6.4 AGND 3.2 mm × 0.1 mm, U6.5 1.6 mm × 0.1 mm (buck)**. U6's exposed pad does sit on the plane, so the buck has a solid thermal/ground tie; its PGND pin, which carries the 2.25 MHz switching return, still gets there through a 0.1 mm stub (≈ 18 mΩ, a few nH). Nine other ground pads (C28, C9, C10, R18, U1.5, P2 A12/B1, TAC_SWITCH_1.3, U3.3) hang on one 0.5 mm thermal spoke.
- **Why it matters:** a 0.1 mm, 5 mm ground stub under the mic amp's ground pins is the kind of thing that raises the noise floor on the mic input; a 0.1 mm stub on a buck's PGND lets switching ripple ride on the local ground. Neither will break the board; both are the first places to look if the mic path hisses or the audio picks up a 2.25 MHz whine.
- **Fix (bottom layer only, ten minutes):** drop the zone clearance around U3, U4 and U6 from 0.5 to 0.25 mm (JLCPCB's minimum is 0.1), or draw 0.3–0.5 mm GND stubs from those ten pins into the pour; set the zone's thermal gap smaller or add a short GND track so the nine single-spoke pads get two. No top-layer work needed.

### 2. Inrush — no series resistor before C15; smaller than rev 3, but not limited
*(R4-P2-05 · decision 5e not applied · first raised in the rev-3 review, not on the 7 Oct list)*

- **The exact scenario:** the unit is off, so the 100 µF capacitor C15 holds no charge. The 9 V adapter is plugged in, or SW1 is flipped. For the first few microseconds an empty capacitor behaves like a short circuit, and the current that rushes in is limited only by what is in the path: the adapter's output, the barrel-jack contacts, the switch contacts, two diode drops and three ferrite beads at 0.05 Ω each. That is roughly a quarter of an ohm, so a peak of up to ≈ 30 A for ≈ 25 µs from a stiff adapter (an upper bound; a real adapter's output impedance lowers it).
- **What it does not hurt:** the diodes (the 1N5817W's 25 A rating is for an 8 ms pulse; this one is 300× shorter) and the adapter (it sags briefly).
- **Potential consequence:** the switch and jack contacts are the wear item. Each power-on puts a small spark across them as they close, and the slide switch does it several times per flip because of contact bounce. Over hundreds of cycles that pits the contacts; the symptom is a supply that drops out when the unit is bumped or the switch is wiggled. A slow failure, not a day-one one. Rev 1/2 never had this (10 µF at the input); rev 3 added 700 µF; rev 4 cut it to 310 µF, but the 100 µF directly on the unprotected path remains, and removing D6 and FB7 took 0.45 V and 50 mΩ out of the path.
- **Fix:** one part — a 1 Ω, 1 W resistor between FB5 and C15 (or an NTC). Peak drops to ≈ 8 A; cost 0.45 V and 0.2 W at full load; Daisy VIN still ≈ 7 V, inside 4–17 V. Can go in the next spin if not this one.

**If only one of these two is fixed for this build, make it the IC ground stubs under U4 and U6.**

---

## Acknowledged / deferred by decision (Kyle, 2026-10-13)

### Display mounting (Oct-7 row 5 · R4-P6-05)
- **Status:** "Acknowledged — will potentially deal with later." The screen is not mounted in this build.
- **What stands:** J8 is where it was; no M2 holes for the NHD module, no chassis holes for the board.
- **Potential consequence if the module is fitted later as-is:** it hangs on 20 solder joints behind the panel window until the holes exist; the enclosure window position stays open.

### LED bookkeeping (R4-P4-01 · R4-P2-03 · R4-P6-04)
- **Status:** Trey hand-solders Würth 150505M173300; polarity and footprint are right for it. No assembly gap.
- **What stands:** schematic Value still "CLS6B-FKW" with the Cree pin labels; no hand-solder sheet.
- **Potential consequence:** the next person reading the files reaches the wrong part and the wrong polarity conclusion, as this review did in rev 3.
- **Fix (paperwork):** Value → 150505M173300, relabel the symbol pins, add a hand-solder sheet.

### Encoder filter caps (Oct-7 row 7 · R4-P3-03 · R4-P5-04)
- **Status:** accepted as built — no room near the Seed.
- **What stands:** the four 10 nF caps sit at the encoders on the back, 6.8–10.2 mm from the encoder pins and 63–111 mm from the Daisy pins.
- **Potential consequence:** contact bounce is filtered at the source (good); the MCU input stays on an unterminated 63–111 mm line (noise pickup along the run). Keep the state-table quadrature decoder in firmware.

---

## Tier 2 — Robustness items, half done or unchanged

### 3. Decoupling: SD socket fixed, headphone amp still bare
*(R4-P2-06 · R4-P2-07 · R4-P2-08)*

- **Done:** C28 10 µF and C27 100 nF now sit 5.2 / 6.9 mm from the SD socket's VDD pin — the rev-3 "120 mm to the nearest cap" item is closed.
- **Not done:** the optional second 10 µF at Daisy pin 38 (C28 is 27.9 mm from it — acceptable); the TPA6110A2 headphone amp still has only 100 nF on its 3V3_A rail, third revision running (F-031).
- **Potential consequence:** distortion or a faint whine into long headphone leads; the mic amp shares the same under-filtered rail.
- **Fix:** 10 µF (or more) on /+3V3_A at U3.

### 4. Digital traces beside audio traces, unchanged
*(R4-P5-02 · R4-P5-03)*

- **What stands:** /USART1_RX runs 49 mm beside AUDIO_IN_L at 0.41 mm, /USART1_TX 26 mm at 0.45 mm; **/TAC_SWITCH_2 runs 27 mm beside AUDIO_OUT_R at 0.20 mm** (and 32 mm beside AUDIO_OUT_L at 0.70 mm) — the closest pairing on the board, same layer.
- **Potential consequence:** a tick on the audio input on MIDI traffic; a click on the line out when the right tactile switch is pressed.
- **Fix:** move the UART and the TAC_SWITCH_2 trace ≥ 1 mm from the audio lines, or put them on the other layer.

### 5. /RES_SPI floats until firmware drives it
*(R4-P3-05 · unchanged from rev 3)*

- **What stands:** the OLED reset line is a bare two-node net with no pull-up or RC.
- **Potential consequence:** the display's reset state is undefined from power-up until the firmware configures the pin — usually invisible, occasionally a garbage first frame or a display that needs a second init.
- **Fix:** 10 k from /RES_SPI to /+3V3_OLED.

*Everything else in this tier is as rev 3: SPI lines unterminated but electrically short (optional 22–33 Ω or GPIO slew ≤ medium), USB pair length-matched but via-heavy, audio runs long but 0.3 mm — residual judgments, no action required.*

---

## Tier 3 — Fab margins (all five Oct-7 rows still NOT DONE)

| Item | Measured | Limit | Potential consequence if left | Fix |
|---|---|---|---|---|
| MK1 annular ring (R4-P1-02) | 0.175 mm (1.0 pad / 0.65 drill) | JLCPCB 0.18 absolute, 0.25 recommended | A stricter lot rejects the order, or a thin ring breaks out and the mic pin lifts. Fabbed OK twice so far | MK1 pads 1/2 → 1.1–1.2 mm |
| USB-C NPTH-to-GND-pad (R4-P1-03) | 0.197 mm | 0.20 mm | 3 µm under: DFM rejection or a drill break-out into the GND pad possible. Fabbed OK twice | Shrink A1/A12/B1/B12 by 0.05 mm |
| U6 thermal vias (R4-P1-04) | 0.25 mm drill / 0.60 pad | Legal at JLC; project rule says 0.30 | Extra drill tool; trips the project's own DRC so real errors hide among known ones | Footprint EP vias → 0.30 / 0.70 |
| Silk outlines (R4-P6-02) | 0.12 mm stroke; refdes exactly 1.0 / 0.15 | 0.15 mm line | Outlines print faint or are dropped. Cosmetic | Footprint outline width 0.15 |
| DRC minimums (R4-P1-12) | `min_track_width 0.0`, `min_clearance 0.0` (`.kicad_pro` identical to rev 3) | — | KiCad never warns about sub-minimum copper; the next thin trace ships unnoticed | Board Setup → Constraints: 0.1 / 0.1 |
| 0.1 mm copper (R4-P1-01) | 74.9 mm, unchanged (U4 fan-out, U6 EP, USB, 5.9 mm /USART1_TX) | 0.10 mm, ±20 % | Zero margin where it remains; DRC at JLC minimums is otherwise clean | Widen the USART/USB/3V3_A bits to 0.15 where room exists |

---

## Tier 4 — Hygiene

| Item | State in rev 4 | Potential consequence if left | Fix |
|---|---|---|---|
| ERC flags (R4-P3-06 · R4-P2-11) | 14 missing no-connect flags + 4 missing PWR_FLAGs; ERC 51 items, identical to rev 3 | A real wiring error hides among 20 known false errors on the next revision | NC flags on P2 SS/SBU pins and J8 3/9/15/18; PWR_FLAG on /DSY_VIN, /+9V_FLAG, Net-(U4-VDD), GND |
| Hand-assembly sheet (R4-P4-03) | One-sheet BOM; 18 THT parts + the hand-soldered LEDs listed nowhere | A board passes assembly and fails on the bench because a through-hole cap or the LEDs were never fitted | Second BOM sheet with value, footprint, net and source for every hand-fitted part |
| Position-file flags (R4-P4-04) | "Exclude from position" only on J3–J7; 15 CPL rows with no BOM match | JLC upload shows 15 unmatched entries; harmless but noisy | Set the flag on all THT parts |
| BOM cell hygiene (R4-P4-05) | Numeric footprint cells, mojibake, one stale cell (D2–D5 say "SOD-323" for the SOD-123FL part ordered) | None at JLC (keys on LCSC #); confuses a human reader | Tidy the cells; fix the D2–D5 text |
| Refdes repurposed (R4-P4-06) | C19–C22 100 µF → 10 nF, R31/R32 3.3 Ω → 10 k between rev 3 and rev 4 | Any rev-3 note, photo or rework instruction naming them now points at a different part | One line in the change log; renumber instead next time |
| Extended parts (R4-P4-07) | U6, L1, R4, R29/R30, R35–R40, C3339 ×5, D2–D5 | Per-line handling fees; R35–R40 is avoidable (C21190 1 % is Basic) | Swap R35–R40 |
| Dangling vias (R4-P1-07) | 2, on /LED_2_R and /LED_2_B, unchanged | Two needless holes; cosmetic | Delete |
| Back-side artwork (R4-P6-01) | 3,900 polygons bury 97 of 104 bottom refdes; runs off all edges; nothing on a pad | Inspection and rework harder; assembly unaffected | Refdes halo, or move refdes to Fab |
| Headphones1 (R4-P3-07 · R4-P6-07, waiting on Trey) | Linear (B) taper as volume control; rotation sense unverified; bushing 9 mm outside the outline | Volume may run backwards or feel wrong; panel needs a cut-out | Trey to confirm; prefer A-taper |
| SD card detect (R4-P3-09) | /SWA single-pin; all 40 Daisy pins used | Card presence unreadable by firmware | Pin trade if the feature is wanted |
| SW1 contact code | Not on the JLC BOM, unverifiable | A logic-level (gold 0.4 VA) contact pits at 0.5 A and goes intermittent | Check the ordered part is 1101A4VQEA with silver 5 A contacts |

---

## What passed (verified, cited)

- Schematic ↔ PCB 112 / 112 parts, 0 net differences, 0 duplicate refdes.
- BOM ↔ schematic ↔ PCB 92 / 92 three-way; values 92 / 92; the four new LCSC numbers verified by part page; the new bridge part fits its pads.
- U6 fed from the FB6 node at ≈ 8.1 V (3–17 V window); TPS62172 loop unchanged; L1 on the Murata pattern.
- LED currents 11.6 / 12.1 mA, 57–69 mW in 0603; polarity correct for the Würth part; 3.3 V-only Daisy pins behind 1 kΩ bases.
- D6 and FB7 gone; 1N5817W bridge on matching pads; Daisy VIN 6.8–7.5 V; grounds tied; reverse polarity by the bridge; IPC-2221 ampacity on every rail.
- SD socket decoupled; encoder pull-ups and caps wired and routed; encoder clicks routed.
- J8 wiring = NHD serial pin table 20 / 20; 4-wire SPI strap; NC pins correct.
- DRC at JLCPCB minimums: 0 clearance / width / edge / drill errors; courtyards, outline, mask, hole spacing clean.

## Question for Trey

- **Headphones1:** is CW = louder as wired, and is a linear taper intended? (carried from rev 3)

## Threshold-source caveats

As rev 3: Daisy, Cree and Murata hosts blocked from this session; Daisy pin facts from the KiCad symbol and libDaisy; SSD1322 10 MHz from memory. JLCPCB capabilities and the four new part pages fetched live 2026-10-13.
