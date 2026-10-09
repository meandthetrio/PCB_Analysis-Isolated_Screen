<!-- Export of the shared Claude Doc "WavetableController Rev 2 Design Review" (https://claude.ai/code/artifact/6e30a194-1011-47d6-9039-bcceaed10b4a), tab 1, rev 65, exported 2026-10-09. The doc is the plain-language version for Trey; analysis/FINAL_REPORT_2026-10.md is the technical version. The doc's second tab (Power ratings, every part) is appended below. -->

# WavetableController Rev 2 Design Review

Oct 7, 2026 · @Kyle

The Rev 2 files are a big step up from the boards in hand: the ground plane, the duplicate part, the dead encoder buttons and the hair-thin traces are all fixed. Three things will damage parts if built as drawn, and six need a parts-list or layout edit before ordering.

## Pass by pass

Six review passes, each starting from what the new files got right. "Fix" means over a limit or will mis-build; "Tidy" means works today, cheap to improve.

| Pass | Done well | Fix | Tidy |
| --- | --- | --- | --- |
| 0 Files | The board file, Gerbers and schematic are one consistent set: re-plotting the board reproduces the Gerbers byte for byte. Ground pour on both layers, zero unconnected nets, the duplicate R21 gone. | 0 | 0 |
| 1 Fab limits | Hair-thin 0.1 mm trace length cut from 3850 mm to 73 mm; the 3V3 rail is 0.3 mm end to end. Vias, spacing, hole sizes and hole-to-track gaps all clear JLCPCB's limits. | 3 | 3 |
| 2 Power | Ground stitched with 225 vias; every chip has a capacitor within 6 mm; 9 V rails are 0.5 mm copper; electrolytics are 35 V parts; the new 3.3 V buck uses TI's reference inductor and capacitor values. | 4 | 2 |
| 3 Connectivity | Schematic and board agree on every pin. Encoder buttons now routed. The display connector matches Newhaven's 4-wire SPI table pin for pin. Every Daisy pin is on the right function. All 20 ERC errors explained. | 1 | 2 |
| 4 Parts list | All 80 parts shared between the BOM and the board match on value and part number, checked against LCSC. Every new part is listed. | 2 | 2 |
| 5 Signals | Display SPI bus clean. USB pair now matched to 0.4 mm. SD runs halved. MIDI in and out textbook. Headphone amp passes TI's gain, filter and bypass checks. Mic amp matches the Maxim evaluation kit pin for pin. | 0 | 3 |
| 6 Mechanical | Outline unchanged from the working boards. All three exposed thermal pads are stencilled. No courtyard overlaps. The area under the display is clear. | 1 | 2 |
| **Total** |  | **11** | **14** |

## Fix before ordering boards

Three things will damage parts if the board is built as drawn.

**1. C25, the buck converter U6's input capacitor, is rated 6.3 V on an 8 V wire.** Every capacitor has a maximum voltage. C25 is a 6.3 V part, but it sits on U6's input, which carries about 8 V. Run a ceramic above its rating and it loses most of its capacitance and can short. Fix: same 10 µF value in a 16 V or 25 V rating, 0805 size, which is what TI's own reference design uses.

**2. The 9 V supply path is undersized for the new display.** The Newhaven OLED on J8 draws 345 mA typical and 375 mA at full white (datasheet Rev 6). That makes the whole board about 0.3 A typical, 0.5 A worst case. A ferrite bead only filters noise while its current stays under its rating; above that it saturates, stops filtering and heats up. The four beads in series (FB3 to FB6) are rated 200 mA, so all four are over their limit and give no more filtering than one. The real noise filtering comes from the 3.3 Ω plus 100 µF stages (R29 to R32 with C17 to C22), which work fine. Fix: keep one bead (FB3) rated 1 A or more and delete FB4, FB5 and FB6. A fifth bead, FB7, feeds the display buck U6 on its own and carries 0.19 to 0.26 A, so it is over the same 200 mA rating and needs the 1 A part too (or can go; the buck's own input capacitor does that job). The other two beads are fine: FB2 feeds the mic amp at 3 mA, and FB1 does nothing (both ends on ground, see below). For reference, Electrosmith's Seed3 Pedal Dev Kit, which this circuit was copied from, uses the identical four-bead chain but with a 1 A bead, and its board draws under 0.25 A with no display, so the copy failed on the part rating and the added display current, not on the topology. Decision 2026-10-08: every bead becomes a 2 A part. Keep the 600 ohm at 100 MHz impedance class (all beads are specified at 100 MHz; the number to choose is the impedance, and 600 ohm is what both the current part and Electrosmith's use). A 600 ohm 2 A bead does not exist in 0603 from a stocked source, so the footprint moves to 0805: TDK MPZ2012S601AT000, 600 ohm at 100 MHz, 2 A, 0.1 ohm. If the 0603 footprint must stay, the 2 A option is 220 ohm (TDK MPZ1608S221ATA00, 2.2 A, 0.05 ohm), which filters less above 20 MHz but is still far more than the saturated beads do today. Separately, the two 3.3 Ω resistors feeding the display branch (R31, R32) dissipate 120 to 175 mW, and the 0603 size is rated for 100 mW. Simplest fix: keep the 3.3 Ω value but use a physically bigger resistor, 1206 or 2512, rated half a watt. Nothing electrical changes; a bigger body just sheds heat. Cleaner fix: the display is powered by U6, a step-down switching regulator (a "buck") that turns the 8 V into 3.3 V. A regulator rejects input noise on its own, so the two resistors do little for it while carrying all of its 0.2 A. Feed U6 from the point before R31 (the C19 node) instead, leaving R31 and R32 to carry only the LED current, and the Daisy keeps its own separate filter (R29, R30, C17, C18) exactly as drawn.

**3. The RGB LEDs are wired so they can never light, and can damage the Daisy.** The parts are LED1 and LED2, Cree CLS6B-FKW: three colours in one package, each with its own in and out pin, so two LEDs use six Daisy pins (24, 25, 26, 27, 30, 31). Each colour is like a bulb with a one-way valve. Today the Daisy pin is on the valve's in side and the out side goes through 300 Ω (R21, R24 to R28) to the 8 V supply, the +9V\_FLAG net. That is backwards, so no current flows and the light never comes on. The valve is also rated to hold back only 5 V the wrong way and is being asked to hold back 8 V, so over time it can give out. If it does, the 8 V reaches the Daisy pin through 300 Ω, and three of these six pins are the Daisy's 3.3 V-only pins. Nothing breaks on day one; it is a slow fuse. The wiring is unchanged from Round 1; only the net name moved.

Fix: turn each colour around and add a switch. 9 V → 300 Ω → LED in → LED out → switch → ground, with the Daisy pin driving the switch. The six Daisy traces stay on the same nets; they just end at a switch instead of at the LED pad. The LEDs stay hand-mounted and in place; the layout change is six small footprints near the LEDs and the resistors moved to the other side of each LED.

Parts, verified on LCSC on 7 Oct 2026:

| Role | Part | LCSC | Qty | Notes |
| --- | --- | --- | --- | --- |
| Switch, recommended | 2N7002 MOSFET, SOT-23 | C8545 | 6 | Works straight from a 3.3 V Daisy pin; full 20 mA per colour. AO3400A (C20917) is a drop-in alternative. |
| Switch, fewer parts | ULN2003A array, SOIC-16 | C7512 | 1 | Seven switches in one chip. Drops about 1 V, so green and blue fall to about 13 mA unless the resistors go to 220 Ω. |
| Gate pull-down | 100 kΩ, 0603 | any | 6 | One per MOSFET, gate to ground, so the LEDs stay off during power-up before the Daisy drives its pins. Not needed with the ULN2003. |
| LED resistors | 300 Ω (or 330 Ω for margin), **1206 size** | any | 6 | Keep the value, change the size. Once the LEDs light, red leaves about 6 V across its resistor at 20 mA, about 120 to 135 mW, over the 100 mW rating of the current 0603 parts. 1206 is rated 250 mW. |

Brightness: the switch is on or off, but the Daisy can flick it thousands of times a second (PWM) and the eye sees that as dimming, which is also how colours are mixed. Four of the six pins already used (24, 25, 26, 31) have hardware PWM; pins 27 and 30 would be dimmed in software, or swapped to PWM-capable pins in this revision.

Why not the simple Daisy pin → resistor → LED → ground? Green and blue in this LED need about 3.1 V just to turn on, and a Daisy pin gives 3.3 V, so they come out dim. Red would be fine. If dim green and blue are acceptable for status lights, that four-trace fix works with no new parts.

## Fix in the parts list and layout before assembly

These will stall the order or mis-build the board. None needs new engineering.

**4. Parts list: one position ordered twice, three parts with nowhere to go.** C17 is one position on the board and holds a 100 µF electrolytic. The BOM lists C17 twice: once on that electrolytic line and once on the 100 nF ceramic line, a leftover from the old BOM. The assembler is told to put two different parts in one place. Fix: remove C17 from the 100 nF line. Separately, the BOM orders two surface-mount buttons called S1 and S2 and a 7805 regulator called U5, but no position on the board has any of those names. The board's four buttons are through-hole parts soldered by hand. Fix: delete the S1/S2 line and the U5 line.

**5. The display module has no way to be mounted.** The Newhaven display on J8 is not a bare screen. It is a small circuit board, 82 by 47 mm, with the glass glued on and the 20 pins on its back. Newhaven put four screw holes in its corners so it can be bolted down on standoffs. Our board has no holes under those corners, so the only thing holding the display would be the 20 solder joints. Press the glass through a panel window and the joints take the load. Fix: move J8 down 5 mm, from y 81.3 to y 86.3, and add four 2.4 mm holes for M2 screws at (135.0, 84.3), (209.2, 84.3), (135.0, 126.8) and (209.2, 126.8) in board coordinates, plus four standoffs matched to the header height. Why the move: with J8 where it is, the top-left hole lands on pad 3 of the power switch SW1, 1.4 mm from its centre (F-074). After the move the display window centre goes from (172.1, 100.7) to (172.1, 105.7), so the enclosure window moves down 5 mm with it. Three small back-side changes come with the holes: U1 and its R2 tracks sit under the top-right screw head and move about 3 mm; the TAC\_SHIFT\_L track at the top-left hole and the ENCR\_A, USART1\_RX and USART1\_TX tracks at the bottom-right hole reroute around the holes. The module's bottom edge then sits 0.9 mm from the TAC\_SWITCH\_1 and TAC\_SWITCH\_2 bodies, so any button cap must stay within the switch body width. The pin tails of SW1, C23 and C24 come through the front under the module and must be trimmed flush. Put the holes and the module outline into the J8 footprint itself so they move with it and DRC checks them. The 20-pin wiring itself is correct.

**6. The 3.3 V regulator U6: drawing and parts list disagree, and the inductor L1 is on the wrong pads.** TI makes U6 in two flavours. The TPS62172 is fixed and always puts out 3.3 V. The TPS62170 is adjustable and needs two resistors to set the voltage. The schematic has the two resistors (R33 47 kΩ, R34 15 kΩ) drawn in, as for the adjustable part, but the BOM buys the fixed part. It works either way because the fixed chip ignores the resistors; just pick one and make the drawing match. The inductor L1 is a 2.0 by 1.6 mm Murata part, but the pads on the board are drawn for a 2.0 by 1.25 mm part, so it overhangs them by 0.35 mm on each side. It will usually solder, but weakly, on the one part carrying the switching current. Fix: use the 2016-size footprint. While there, move L1 closer to U6's SW pin (it is 8.3 mm away; TI asks for short) and change C26, the output capacitor, to an 0805 body, since a 22 µF 0603 loses about half its capacitance at 3.3 V.

**7. Encoder inputs need a filter so every detent counts exactly once.** The two encoders' A and B lines (ENCL1 on Daisy pins 33 and 32, ENCR1 on pins 12 and 13) go straight to the Daisy with no external parts, relying on the Daisy's internal pull-ups over 80 to 146 mm of trace. That is enough to work but not enough to guarantee one count per click on a heavy detented encoder. Fix: on each of the four A/B lines, a 10 kΩ pull-up to 3.3 V and a 10 nF capacitor to ground, placed near the Daisy. Four resistors and four capacitors, 0603. Pair it in firmware with a state-table quadrature decoder rather than simple debounce, and skipped or doubled steps go away. The two click switches and the four buttons (TAC\_SWITCH\_1, TAC\_SWITCH\_2, TAC\_SHIFT\_L1, TAC\_SHIFT\_R1) can stay on internal pull-ups.

## Power-rating sweep, every part (added 2026-10-08)

The earlier pass missed FB7, so this is a redo that lists every designator against its BOM rating rather than implying it was checked. Two new items came out of it, plus one part whose rating could not be confirmed.

| Group | Checked | Result |
| --- | --- | --- |
| Ferrite beads (7) | branch current vs 200 mA | FB3 to FB7 over (item 2); FB2 fine; FB1 no-op |
| Resistors (34) | worst-case power vs 100 mW | R31, R32 over (item 2); R4 over in the MIDI fault case (item 8, new); R29, R30 at 65 %; rest under 10 % |
| Capacitors (26) | node voltage vs rating | C25 over (item 1); all others at 52 % or less |
| Diodes (6) | current, heat, reverse voltage | bridge and D6 marginal on heat, D6 redundant (item 9, new); D1 fine |
| Inductor, buck, amps, opto, ESD | current and supply range | L1 27 %, U6 75 %, U1 output 75 %, U3 and U4 fine |
| Connectors and switches | current | barrel 9 V at 0.5 A fine (12 V adapter is its ceiling); display header fine; SW1 not confirmable |
| Daisy 3.3 V rails | load vs limit | about 130 mA digital, 65 mA analog; the Daisy publishes no limit, so still unverifiable |

**8. R4, the MIDI OUT 33 Ω resistor, needs a half-watt part.** The MIDI 3.3 V circuit specifies 33 Ω at 0.5 W because a mono TS plug in the TRS jack, or a shorted cable, puts the full 3.3 V across it: 100 mA and 330 mW for as long as the plug is in, in a 100 mW 0603 body. It also pulls 100 mA from the Daisy's 3.3 V rail while shorted. Fix: 33 Ω in a 1206 or 2512 body rated 0.5 W.

**9. The input diodes run hot, and D6 does nothing the bridge does not already do.** The bridge D2 to D5 and D6 are 1 A Schottkys in the tiny SOD-323 body, which only reaches 1 A with far more copper than the layout gives. At the 0.49 A worst case each conducting diode dissipates about 0.2 W, 78 % of its 250 mW limit, and the junction sits within a few degrees of its 125 °C maximum inside a warm enclosure. The bridge already fixes polarity, so D6 only adds 0.45 V of drop and another 0.2 W of heat. Fix: delete D6 (Daisy input rises from 5.8 V to 6.25 V worst case) and move the bridge to an SMA or SOD-123FL part such as the SS14 class, or to a single series diode if center-negative-only is acceptable, which is what Electrosmith does.

**Could not confirm: SW1.** The power switch is a C&K 1101A4VQEA sourced outside the JLCPCB BOM. Its sibling 1101A3VQEA has silver contacts rated 5 A, which would be fine, but the 1101 family also has a gold "logic level" variant rated 0.4 VA that would be ten times over. Please check the contact code on the part you buy.

The full part-by-part tables are in the second tab: Power ratings, every part

## Fab margins

Checked against JLCPCB's published limits (fetched 7 Oct 2026). Nothing is a hard rejection; three items sit a few thousandths of a millimetre under the absolute minimum and would be rejected by a stricter fab lot. Each is a one-line footprint edit.

| Item | Board | JLCPCB limit | Fix |
| --- | --- | --- | --- |
| Ring of copper around the microphone's two pins (MK1) | 0.175 mm | 0.18 mm minimum, 0.25 recommended | 1.1 mm pad instead of 1.0 |
| USB-C connector P2's own alignment holes to its ground pads | 0.197 mm | 0.20 mm | shrink those four pads by 0.05 mm |
| Two thermal vias under the buck regulator U6 | 0.25 mm hole, 0.175 mm ring | hole OK; ring 0.18 mm minimum | 0.3 mm hole with a 0.7 mm pad |
| Silkscreen part outlines | 0.12 mm lines | 0.15 mm minimum | cosmetic only; outlines print faint |

Also worth knowing: the project's own design rules still have the minimum track width and clearance set to zero, so KiCad will never warn about any of this. Set both to 0.1 mm. The last 73 mm of 0.1 mm trace is mostly forced by the mic amp U4's tiny pads; six short segments on the UART, analog 3V3 and USB nets could be widened.

## Worth tidying

Everything here works today. Each is cheap to fix on the next edit.

- **Digital 3.3 V rail has a single 100 nF capacitor, C1 at the MIDI opto U1.** The SD card socket P1 is 120 mm from it. Add 100 nF plus 10 µF at P1. The thin-trace half of the Round 1 noise problem is already fixed by the 0.3 mm rail. *Potential consequence:* SD card errors or fallback to 1-bit mode under load, and a rail that dips every time the card writes, which the MIDI opto also shares. This is the likeliest reason 4-bit mode failed on the Round 1 boards.
- **Headphone amp is missing two capacitors TI recommends.** A 10 µF or larger bulk capacitor near the TPA6110A2 (U3; the analog 3.3 V rail has only one 100 nF on it, C5), and a 5 pF capacitor across each feedback resistor (R14, R15). Gain, filter and bypass checks all pass. *Potential consequence:* audible distortion or a faint whine in the headphones under load, especially with long headphone leads; the mic amp shares the same under-filtered rail.
- **Two audio traces run close to digital ones.** The right audio output (AUDIO\_OUT\_R) runs 25 mm at 0.2 mm from the TAC\_SWITCH\_2 button line; the audio input (AUDIO\_IN\_L) runs 43 mm beside the MIDI UART line USART1\_RX. Both aggressors are slow, so the worst case is a click when the button is pressed. Move them 0.5 mm apart. *Potential consequence:* a click on the right output when the main button is pressed, and a faint tick on the input when MIDI traffic arrives. Minor, but it is the kind of thing a reviewer with headphones notices.
- **FB1 has both ends on ground.** It does nothing. Delete it, or use it to join the analog and digital grounds, which is probably what it was for. *Potential consequence:* none electrically. It is a wasted part and a source of confusion for anyone reading the schematic later.
- **Firmware note, not hardware.** Daisy pin 10 is SPI1's MISO line and is used as the right shift button TAC\_SHIFT\_R1 while SPI1 drives the display on J8. Open SPI1 as transmit-only or the SPI driver will take over the button pin. *Potential consequence:* the right shift button stops working the moment the display driver is initialised, and it will look like a hardware fault.
- **ERC hygiene.** Fourteen intentionally unused pins lack no-connect flags and four power nets lack PWR\_FLAG symbols. Adding them takes ERC to zero errors, so future mistakes show up. *Potential consequence:* a real wiring mistake in a future revision hides among the 20 known false errors and ships.
- **No chassis mounting holes, and the 3.5 mm jacks are unthreaded.** The board hangs from the encoder nuts alone. The five jacks (J3 to J7) are CUI SJ1-352x right-angle jacks: a plastic body with no thread or nut, held only by five solder pins and five plastic posts in holes in the board, with the panel just a clearance hole around the nose. Two things reduce plug-in strain on those joints. First, standoffs within about 15 mm of the jack row: they do not reduce the push from the plug, but they stop the board flexing about the encoder mounts under that push, and repeated flex is what cracks joints. Second, a close-fitting panel hole, about 0.2 mm larger than the jack nose: the panel then takes the sideways load from the cable instead of the solder. A threaded-bushing jack (Thonkiconn PJ398SM style) is the full fix but needs a new footprint, so it is a Rev 3 decision. *Potential consequence:* every cable insertion loads the solder joints of an unanchored board. Over years that is the usual cause of cracked joints and intermittent jacks on panel-hung boards.
- **No hand-assembly list.** Eighteen parts are soldered by hand, including two through-hole capacitors at the display connector, C23 and C24, that are easy to forget. A second BOM sheet would cover it. *Potential consequence:* a board that passes assembly and fails on the bench because a through-hole capacitor was never fitted, and nobody has a checklist to find it.

## Noise: which items matter, ranked

The original problem with the Round 1 boards was display noise. Rev 2 already fixed the structural cause: the display is off the shared 3.3 V rail and on its own regulator with its own two-stage filter, the ground plane covers both layers with 225 stitching vias, the 3.3 V rail is 0.3 mm, and the analog runs are shorter and wider. Of the items above, these are the ones that still move the noise floor, biggest first.

1. **The saturated ferrite beads (item 2).** A bead over its current rating saturates and stops filtering. At 0.3 to 0.5 A all four (FB3 to FB6) are inert, so the protection they were added for is not there. One 1 A bead in FB3's place restores it. The 3.3 Ω plus 100 µF stages (R29 to R32, C17 to C22) are doing the real filtering today and they are good: each rolls off from about 480 Hz, so two stages knock down the buck's 2.25 MHz switching and the display's content-rate current swings before they reach the Daisy.
2. **The buck converter U6 (fixes 1 and 6 in the sections above).** U6 (TPS62172) is the step-down regulator that makes the display's 3.3 V from the 9 V ladder, and it is the one deliberate noise source on the board. Three simple actions, all cheap:
   - **C25, the input capacitor: change to a 16 V part.** C25 is currently 10 µF rated 6.3 V, sitting on U6's 8 V input node. Over its rating it has lost most of its capacitance, so U6's switching ripple is pushed back into the 9 V ladder instead of being absorbed.
   - **L1, the inductor: move it next to U6's SW pin.** L1 (Murata DFE201610P, 2.2 µH) is 8.3 mm from U6 pin 7. The loop U6 → L1 → C26 → ground carries the switching current, and at that length it acts as an antenna.
   - **C26, the output capacitor: change to an 0805 body.** C26 (22 µF, 0603, 6.3 V) delivers about half its rated value at 3.3 V, so the display rail carries more ripple than the design intends. The same 22 µF in 0805 keeps most of its value.

   U3 and U4, the audio amplifiers, are 33 mm from U6 and the nearest audio trace is 60 mm from the SW node, which is adequate.
3. **The digital 3.3 V rail with one 100 nF.** SD card writes pull current in bursts and the nearest capacitor, C1, is 120 mm away. That rail also feeds the MIDI opto U1. Add 100 nF plus 10 µF at the card socket P1.
4. **Headphone amp capacitors.** The analog 3.3 V rail feeds both the headphone amp U3 and the mic amp U4 and carries only one 100 nF, C5. TI recommends the 10 µF bulk cap specifically against distortion and oscillation with long output leads. The 5 pF compensation cap across R14 and R15 is a stability item; an amp near the edge of stability shows up as hiss or a whine.
5. **The two trace neighbours.** AUDIO\_OUT\_R 0.2 mm from the TAC\_SWITCH\_2 line for 25 mm; AUDIO\_IN\_L beside USART1\_RX for 43 mm. Slow signals, so the worst case is a click on a button press or a tick on MIDI traffic. Move them 0.5 mm.
6. **FB1 with both ends on ground.** If it was meant to split analog and digital grounds through a bead, do not. One solid plane stitched with vias is the better arrangement for this board, and a split ground with audio and digital traces crossing it usually makes noise worse. Delete FB1.

No effect on noise: the C17 duplicate, the phantom parts S1, S2 and U5, the J8 display mounting holes, the fab margins, and the L1 inductor pad size (though a weak inductor joint can become intermittent). Fixing the LED wiring removes six resistors from the 9 V ladder, a small bonus.

## SD card 4-bit mode

Nothing on the Rev 2 layout prevents 4-bit mode. The most likely reason it failed on the Round 1 boards is power at the card, not the data traces, and that part is unchanged.

| Requirement for 4-bit | Rev 2 board | Round 1 board |
| --- | --- | --- |
| All four data lines on the SDMMC pins | Yes: D0 to D3, CMD and CLK land on Daisy pins 2 to 7 and the right microSD pads | Yes |
| Pull-ups on CMD and D0 to D3 | 47 kΩ on all five, per the Daisy datasheet's Fig 1.6 | Yes |
| Trace length and matching | 27 to 49 mm, all 0.3 mm; worst skew 22 mm, about 150 ps against a 20 ns bit at 50 MHz | 89 to 108 mm, mostly 0.1 mm |
| Crosstalk | No SD line runs within 0.6 mm of any other trace for more than 2 mm | not measured |
| Ground return | Card VSS on the stitched ground plane | pour on the fabbed boards |
| Power at the card | **120 mm of trace to the nearest capacitor, a single 100 nF (C1)** | same, over 0.1 mm trace |

A card in 4-bit high-speed mode draws current in bursts of 100 mA or more. With no capacitor at the socket, each burst dips the rail at the card, the card sees CRC errors, and the driver falls back or fails. Fix: 100 nF plus 10 µF across P1's VDD and VSS pads. This is the same item as the first bullet under Worth tidying.

Firmware: libDaisy's SD driver defaults to 4-bit at 50 MHz, so if the Round 1 code only worked after forcing 1-bit, the failure was on the physical board. Card detect is still half wired, but that only affects detecting insertion, not the bus.

Target: 4-bit at 50 MHz (libDaisy `FAST`), which is the SD standard's high-speed mode at 3.3 V and libDaisy's default. Do not design to the 100 MHz setting; libDaisy labels it overclocked, the standard only defines it with 1.8 V signalling, and it buys nothing a synth would notice. The capacitor pair at the socket is the only board change needed for 50 MHz to be solid.

Cards: a slow or counterfeit microSD fails at 50 MHz on any board. Bring up with a name-brand card rated A1 or better and, if one card fails, try the 25 MHz setting before blaming the board. The speed printed on the card's packaging (for example 150 or 195 MB/s) is for UHS readers and is not reachable from the Daisy; the bus here tops out around 25 MB/s and any current name-brand card exceeds that.

One experiment on an existing Round 1 board: solder a 10 µF ceramic across the card socket's VDD and VSS pads and retry 4-bit. If that fixes it, the Rev 2 layout only needs the capacitor added.

## Checked and passed

Each of these was measured on the files and compared with a fetched datasheet or JLCPCB's limits.

- **Files.** Board file reproduces the Gerbers byte for byte; schematic and board agree on every pin; zero unconnected nets; the LED2 wiring question from Round 1 is resolved.
- **Power.** Analog and digital grounds tied as the Daisy datasheet requires; the Daisy's VIN stays above its 5 V minimum even at worst-case load (about 5.8 V); all 100 µF electrolytics are 35 V parts; 9 V rails are 0.5 mm copper good for 1.4 A; the 3.3 V buck's inductor and capacitor values match TI's reference; its enable, sense and power-good pins are wired per the datasheet.
- **Connectivity.** SPI, UART, SD card and audio pins all land on the right Daisy functions; the display connector matches Newhaven's 4-wire SPI table exactly, including the four intentionally unconnected pins; the two main buttons are wired correctly for their footprint; USB-C has its 5.1 kΩ pull-downs; SD has its 47 kΩ pull-ups.
- **Signals.** Display bus 89 to 124 mm at 0.3 mm, point to point. USB pair 130.2 and 130.6 mm, 0.4 mm skew. SD runs 27 to 49 mm. MIDI in is TRS type A with the opto's own 270 Ω pull-up; MIDI out uses the 10 and 33 Ω 3.3 V practice. Headphone amp: gain 1.5, 15 Hz input corner, mid-rail bypass rule and 100 µF output coupling all pass TI's checks. Mic amp matches the MAX9814 evaluation kit on every pin. USB ESD part pinout correct.
- **Fab.** Vias 0.6/0.3 mm; copper spacing 0.15 mm against 0.10; hole-to-hole 0.50 mm; hole-to-track gaps above minimum; solder-mask bridges 0.15 mm against 0.10; all drill sizes in range; outline identical to the working boards.
- **Parts list.** All 80 shared parts match the LCSC listings on value and part number.
- **Mechanical.** All three exposed thermal pads are stencilled; no courtyard overlaps; nothing on the front under the display; connectors sit at the edges as before.

## Questions for Trey

1. **Has this Gerber set already gone to JLCPCB, or is it the candidate?** If boards exist, item 2 means the 3.3 Ω resistors and beads are running hot right now.
2. **Was the display branch meant to share the 3.3 Ω and 100 µF filter?** The buck tolerates ripple; 0603 resistors and 200 mA beads do not tolerate 0.2 to 0.5 A.
3. **TPS62170 (adjustable) or TPS62172 (fixed)?** The schematic says one, the parts list the other.
4. **Are the LEDs meant to be fitted this round?** If yes, the drive must be rewired first (item 3).
5. **What is U5?** The parts list orders a 7805 regulator with no place on the board. A plan the buck replaced, or is a 5 V rail still wanted somewhere?
6. **How is the display held?** On the header only, or on standoffs through its four corner holes (item 5)?
7. **Which encoder exactly, and which shaft length?** The footprint under ENCL1 and ENCR1 is the Alps EC11E pattern, with mounting lugs 11.2 mm apart. A Bourns PEC11R will not seat in it, because its lugs are 13.2 mm apart. The full part number also gives the bushing thread length, which sets how far the front panel can sit from the board and so which display header works (item 5).


---

<!-- Tab 2 of the shared doc -->

# Power ratings, every part

Every designator on the Rev 2 board checked against the rating on its BOM line, 2026-10-08. Worst case is a 9 V supply with the display fully lit: 0.49 A in the 9 V trunk, 0.19 to 0.26 A into the display buck, 0.10 to 0.14 A into the Daisy. J1 is rated 12 V, so a 12 V adapter is the hard ceiling. The 1N5817WS diode datasheet and the MIDI electrical spec could not be opened from the review environment, so their figures come from distributor and spec summary text.

## Summary

| Status | Parts |
| --- | --- |
| Over rating, new in this sweep | R4 (MIDI fault case, item 8) |
| Marginal, new in this sweep | D2 to D5 bridge and D6 (item 9) |
| Over rating, already in the report | FB3 to FB7 (item 2), R31 and R32 (item 2), C25 (item 1), LED1 and LED2 reverse voltage (item 3) |
| In rating, under 2x margin | R29 and R30 at 65 %, U6 at 75 %, U1 output at 75 % |
| Could not verify | Daisy 3.3 V rail limits (none published), SW1 contact rating |
| Everything else | in rating with at least 2x margin |

## Resistors (all 0603, 100 mW, 75 V)

| Ref | Value | Where | Worst-case stress | Share of 100 mW | Verdict |
| --- | --- | --- | --- | --- | --- |
| R1 | 10 ohm | UART TX to MIDI OUT tip | 8 mA, 0.7 mW. In a short the STM32 pin limits current, at most about 60 mW | under 1 %, up to 60 % in a short | OK. The MIDI spec asks 0.25 W; the Daisy pin (20 mA abs max) is the weak link in a short |
| R4 | 33 ohm | 3.3 V digital to MIDI OUT ring | 8 mA, 2 mW normally. TS plug or shorted cable: 100 mA, 330 mW, plus 100 mA off the Daisy 3.3 V rail | 330 % | Over, item 8 |
| R5 | 220 ohm | MIDI IN series | 5 mA, 5.5 mW | 6 % | OK |
| R6 | 270 ohm | opto output pull-up | 12 mA when the opto is on, 40 mW | 40 % | OK |
| R2, R3 | 0 ohm | MIDI IN | 5 mA | none | OK |
| R7 to R11, R33 | 47 k | SD pull-ups, buck feedback | under 0.3 mW | under 1 % | OK |
| R12 to R15 | 22 k, 33 k | headphone amp gain | under 0.5 mW | under 1 % | OK |
| R16, R17 | 5.1 k | USB-C CC | 5 mW | 5 % | OK |
| R18, R19, R20 | 100 k, 150 k, 2.2 k | mic amp bias | under 1 mW | under 1 % | OK |
| R21, R24 to R28 | 300 ohm | LED cathodes to the 9 V node | none as drawn (LEDs reverse-biased). Replaced by 1206 parts in the item 3 fix | none | item 3 |
| R22, R23 | 10 k | headphone output loads | 0.1 mW | under 1 % | OK |
| R29, R30 | 3.3 ohm | Daisy branch filter | 0.14 A, 65 mW (0.10 A typical, 33 mW) | 65 % | OK, low margin. 1206 if the layout allows |
| R31, R32 | 3.3 ohm | display branch filter | 0.19 to 0.23 A, 120 to 175 mW | 120 to 175 % | Over, item 2 |
| R34 | 15 k | buck feedback | under 0.1 mW | under 1 % | OK |

## Capacitors

| Ref | Value and rating | Node voltage | Share of rating | Verdict |
| --- | --- | --- | --- | --- |
| C14, C16 | 100 nF 25 V X7R | 9.2 V, bridge output and D6 anode | 37 % (48 % on a 12 V adapter) | OK |
| C1, C4, C5, C8, C11 | 100 nF 25 V | 3.3 V or less | 13 % | OK |
| C2, C3, C10 | 470 nF 25 V | 3.3 V or less | 13 % | OK |
| C9, C13 | 2.2 uF 10 V X5R | 3.3 V or less | 33 % | OK |
| C12 | 4.7 uF 10 V | 3.3 V or less | 33 % | OK |
| C15, C17 to C22 | 100 uF 35 V electrolytic | 9.2 V or less | 26 % | OK |
| C6, C7 | 100 uF 35 V | 3.3 V, headphone coupling | 9 % | OK |
| C25 | 10 uF 6.3 V | 5.2 to 9 V, buck input | 83 to 143 % | Over, item 1 |
| C26 | 22 uF 6.3 V X5R | 3.3 V | 52 % | OK on voltage. DC bias leaves about 10 uF effective, inside the buck's stable range, and C24 100 uF is in parallel |
| C23, C24 | 100 nF axial, 100 uF radial, hand placed | 3.3 V | rating unknown, any stock part is 6.3 V or more | OK |

## Diodes

| Ref | Part | Stress | Verdict |
| --- | --- | --- | --- |
| D2 to D5 | 1N5817WS SOD-323, 1 A, 250 mW, 400 C/W | two conduct at a time, each at the full trunk current. 0.30 A: about 0.10 W, 42 C rise. 0.49 A: about 0.20 W, 78 % of the limit, 78 C rise, junction near 103 C at 25 C ambient and near 123 C at 45 C inside a closed box (limit 125 C). Reverse 9 V against 20 V is fine | Marginal, item 9 |
| D6 | same part | full trunk current, same numbers. Redundant: the bridge already fixes polarity | Marginal and redundant, item 9 |
| D1 | Schottky 1 A SOD-323 | MIDI IN reverse clamp, 5 mA | OK |

## Beads and inductor

| Ref | Rating | Stress | Verdict |
| --- | --- | --- | --- |
| FB3 to FB6 | 200 mA, 450 mohm | 0.30 to 0.49 A | Over, item 2 |
| FB7 | 200 mA | 0.19 to 0.26 A | Over, item 2 |
| FB2 | 200 mA | 3 mA typical, 6 mA max (mic amp) | OK, 30x margin |
| FB1 | none | both ends on ground | no-op, see Worth tidying |
| L1 | 2.2 uH, 1.4 A rms, 2 A saturation, 168 mohm | 0.375 A average, about 0.53 A peak, 24 mW | OK, 27 % |

## ICs and modules

| Ref | Limit | Stress | Verdict |
| --- | --- | --- | --- |
| U6 TPS62172 buck | 500 mA, input 3 to 17 V | 345 to 375 mA (69 to 75 %), input 5.2 to 9 V, about 0.14 W loss | OK, low margin |
| U3 TPA6110A2 headphone amp | 2.5 to 5.5 V, 150 mW per channel into 16 ohm | 3.3 V; full swing into 16 ohm draws about 60 mA from the analog 3.3 V rail | OK |
| U4 MAX9814 mic amp | 2.7 to 5.5 V, 6 mA max | 3.3 V through FB2 | OK |
| U1 H11L1 opto | 3 to 15 V, output sinks 16 mA | 3.3 V, LED 5 mA, output sinks 12 mA through R6 | OK, 75 % |
| U2 USBLC6-2P6 ESD | 5.25 V | 5 V | OK |
| A1 Daisy Seed | VIN 4 to 17 V (5 V minimum per the v1.1.5 sheet); 3.3 V rails have no published limit | VIN 5.8 V worst (6.25 V with D6 removed). Digital 3.3 V about 130 mA normal (SD burst 100 mA, opto 15 mA, pull-ups), 230 mA during the R4 fault. Analog 3.3 V about 65 mA max | VIN OK; rails cannot be verified |
| U5 L7805 | on the BOM, not in the design | none | already reported |

## Connectors and switches

| Ref | Rating | Stress | Verdict |
| --- | --- | --- | --- |
| J1 barrel jack | 12 V, 3 A | 9 V, 0.49 A | OK. 12 V adapter is the ceiling |
| SW1 power slide switch | C&K 1101A4VQEA, bought outside the JLCPCB BOM; datasheet not reachable. Sibling 1101A3VQEA is silver, 5 A | 9 V, 0.49 A | Probably OK. Confirm the contact code: the gold logic-level 1101 variant is 0.4 VA and would be 10x over |
| J8 display | 1 by 20 header, 2.54 mm pitch, 1 A or more per pin | 375 mA on pin 2 | OK |
| P2 USB-C | 3 A | data only | OK |
| TAC switches, encoders, S1, S2 | 50 mA logic | 3.3 V logic | OK |
| Headphones pot, MK1, J3 to J7 | signal | signal | OK |
| LED1, LED2 | reverse voltage 5 V | 6 to 8.5 V reverse as drawn | Over, item 3 |
