# Rev4 — Pass 1: Gerber-only fab and delta review
**Date:** 2026-10-13 · **Input:** `rev4/Gerbers/` (ManifoldGerbs.zip from Trey; plotted 2026-10-13 11:41 CDT by KiCad/Pcbnew 9.0.4, job GUID identical to rev 1). **No KiCad project, BOM or change note received yet**, so this pass covers only what Gerbers can prove: fab rules, geometry, and the physical delta against the rev-1 LedFix set. Net-level checks (I2C pull-ups, LED drive, power tree, refdes/BOM) wait on the `.kicad_sch`/`.kicad_pcb`/BOM.

Method per `analysis/SOURCE_OF_TRUTH.md`: every number below comes from a script (`rev4/tools/checks.py`, `delta.py`, `render.py`; raw output in `checks_rev4.txt`, `gaps_rev4.txt`, `delta_rev4.txt`), thresholds from the JLCPCB capabilities page fetched 2026-10-13 (2-layer 1 oz: 0.10/0.10 mm trace/space, ±20 % width tolerance; PTH annular ring 0.18 absolute / 0.25 recommended; via 0.15 hole / 0.25 dia min; via hole-to-hole 0.2, pad hole-to-hole 0.45; NPTH-to-track 0.2; copper-to-routed-edge 0.2; silk line ≥ 0.15; pad-to-silk 0.15).

The board silk identifies itself as "Stellar Crucible | Manifold", "V4.1", "Designed by PJ Bourgeois".

---

## A. What changed since rev 1 (measured)

| Item | Rev 1 (LedFix) | Rev4 | Note |
|---|---|---|---|
| Outline | 165.3 × 101.8 mm | identical (byte-identical Edge_Cuts) | |
| Track width | 0.10 mm: 3.85 m; 0.20 mm: 0.9 m | 0.30 mm: 3.81 m; 0.50 mm: 0.41 m; 0.20 mm: 0.86 m; **0.10 mm: 75 mm** | F-004 addressed; residual 0.1 mm only in fine-pitch fan-outs (see B-7) |
| Copper pours | B.Cu only (in Gerber; none in the .kicad_pcb we had) | **B.Cu 12 820 mm² (77 % of board) + F.Cu 15 regions, 7 956 mm² (48 %)** | F-006 moot for Rev4 once we get the real file |
| Vias | 93 × 0.3/0.6 | **253 × 0.3/0.6 + 2 × 0.25/0.6** (thermal vias in a DFN pad) | |
| PTH component holes | 77 | 105 (+22 × 1.0 mm, +4 × 0.8 mm) | Daisy header rows re-placed; new headers |
| NPTH | 28 + 1 slot | identical count | |
| SMD pads, bottom (paste) | 192 | **264** | ~36 new/replaced parts on the component side |
| SMD pads, top (paste) | 12 (LED1/LED2 only) | 12 (LED1 unmoved, LED2 shifted 0.3 mm) | LEDs still the only top-side SMD |
| Front silk | artwork (98 regions) + refdes | refdes only, 50 mm² | |
| Bottom silk | refdes | **full-board artwork: 3 911 polygons, 9 776 mm² on-board (59 %), 699 mm² off-board** | see B-1 |

**Footprint delta** (`delta.py`, matching rev-1 pad coordinates within 0.15 mm): only 11 rev-1 footprints are at their old coordinates (C6, C7, ENCL1, ENCR1, J2, LED1, R6, R22, R23, R24, U1). Everything else moved or was replaced. Identifiable from pad geometry alone:
- **Daisy Seed moved** from the right edge (rev-1 centre x≈196, y≈−161) to the lower-left: two 20-pin rows at y = −145.5 and −160.8, x = 115.5 … 163.7.
- **New 16-pin 2.54 mm header "J8"** at y = −81.3, x = 148 … 196 (two groups of 8), top-side silk label J8. The old 4-pin OLED header J2 is still there, unmoved. No 0.5 mm-pitch 31-pad ZIF pattern exists on the board, so the rev-2 "bare COG panel on ZIF" plan was **not** what got built; this looks like a module header. *Confirm with Trey.*
- **New 2×3 2.54 mm header** at (219.8 … 224.8, −144/−146.5).
- **New DFN-8 2×2 mm (0.5 mm pitch) with exposed pad and two 0.25 mm thermal vias** at (196.9, −123.0). Probably the new regulator or load switch; see B-2.
- **New 0.5 mm-pitch 14-lead IC** (pads 0.25 × 0.7) at (191.0, −154.8) with six 0603s, and a **new 8-lead 0.5 mm-pitch IC** at (211.6, −158.6). Identity unknown without the schematic.
- **USB-C replaced**: 22-pad rev-1 footprint gone; new 12-signal-pad + 4-anchor (16-pin, USB 2.0-only) footprint at (123.8, −67.7) with its two 0.65 mm pegs at (120.86/126.64, −66.68).
- **Micro-SD socket replaced**: new 1.1 mm-pitch 9+1 pad pattern at (97.7, −140.7).
- Four 3.0 × 2.0 mm pads at (144.4/155.4, −65.7/−71.7) bracketing the old barrel-jack position: likely an SMD DC jack.
- Six new 3-pad SOT-23-class footprints (0.3 × 1.175 pads) scattered around the switch/LED area, plus many new 0603/0805 passives.
- Rev-1 problem parts: both R21 positions, R25–R28 (LED resistors), FB4, C14 (470 µF), C17 are not at their rev-1 coordinates; whether they were removed or just moved needs the PCB file.

## B. Findings (Rev4)

Classification per SOURCE_OF_TRUTH §4. IDs continue the ledger as R4-xx so they don't collide with F-001…F-035.

**R4-1 · VIOLATION · Bottom silkscreen artwork sits on the component side and over the pads.** The full-board engraving + title block is on B.Silkscreen, which is the side carrying all 264 SMD pads (B.Paste). Measured: silk overlaps **393 of 418** bottom mask openings and **242 of 264** SMD paste pads, and 699 mm² of it lies outside the board outline (y down to −171.7 vs edge −162.7). JLCPCB's rule is 0.15 mm pad-to-silk; their CAM normally clips silk from mask openings, but (a) ink remains between the 0.5 mm-pitch DFN/SOIC leads and around every pad, a solderability/inspection risk for an assembled board, and (b) in rev 1 the artwork was on the *front* (panel) side, where the encoders, switches, LEDs and mic are. **Question for Trey:** was the art meant to be on the back? If it was meant for the panel face, it's on the wrong layer; either way, crop it to the outline and keep it off the SMD footprints (KiCad: put the bitmap on a user layer or add a silk keep-out, and run "clip silkscreen to mask" on plot).

**R4-2 · VIOLATION · GND pour at zero clearance to three pins of the new DFN-8.** On B.Cu the main pour keeps its 0.50 mm clearance from five of the eight 0.25 × 0.5 mm DFN pads but comes to **0.0005, 0.016 and 0.037 mm** from the pads at (196.14, −123.91), (197.64, −123.91) and (196.14, −122.01) with no overlap and no thermal spoke (`gaps_rev4.txt`, `renders/crop_dfn_b.png`). Below JLCPCB's 0.10 mm spacing minimum; after etch tolerance these three pins will be randomly bridged to or isolated from the pour. If those pins are GND (plausible for a regulator), the connection is unreliable; if they aren't, it's a short. Looks like a pad-level clearance override of 0 in the footprint, which KiCad's DRC would then *not* flag. **Needs the .kicad_pcb to settle which it is; fix either way** (solid/thermal connection to the pour, or restore the 0.5 mm clearance).

**R4-3 · VIOLATION (marginal, carried from F-016) · MK1 annular ring 0.175 mm.** The mic pads at (170.96/172.86, −136.0) are still 1.0 mm pad / 0.65 mm drill → 0.175 mm vs 0.18 absolute minimum. Fabbed fine twice; still 5 µm under spec. Enlarge the pad to ≥1.15 mm.

**R4-4 · VIOLATION (marginal, carried from F-008) · USB-C NPTH-to-copper 0.194 mm.** The new 16-pin USB-C footprint keeps the same peg geometry: both 0.65 mm pegs are 0.194 mm from B.Cu copper (limit 0.20). Same tolerance-absorbed risk as before.

**R4-5 · JUDGMENT · Silk line widths below the 0.15 mm minimum.** B.Silkscreen: 1 532 mm of 0.12 mm lines and 15 mm of 0.10 mm; F.Silkscreen: 289 mm of 0.12 mm. JLCPCB says text narrower than 0.15 mm is unidentifiable. These are the refdes strokes; set the silk text thickness to 0.15 mm.

**R4-6 · INFO · 0.25 mm thermal-via drills.** Two 0.25 mm holes with 0.6 mm pads in the DFN exposed pad (ring 0.175). Legal under JLCPCB's via rule (0.15 hole / 0.25 dia), but a non-standard size that may add a drill-tool charge; 0.3 mm would be free.

**R4-7 · ZERO-MARGIN · 75 mm of 0.1 mm track remains.** F.Cu 9 mm, B.Cu 66 mm, all in the fan-outs of the new 0.5 mm-pitch parts around (185–198, −151…−159) and the DFN at (195–199, −122…−124). At the JLCPCB minimum, not below it; acceptable for escape routing, but 0.15 mm would fit between 0.5 mm-pitch pads.

**R4-8 · INFO (not a defect) · 47 same-net copper notches < 0.1 mm.** The copper-to-copper scan found 17 (F) + 30 (B) gaps under 0.10 mm. All but R4-2 are same-net routing notches: 45° corner stubs leaving a 0.054 mm wedge (0.5/√2 − 0.3), track end-caps 0.005–0.05 mm from a pad or via they also touch through another segment (e.g. LED2 pad at (198.4, −138.4), SD pad at (101.85, −141.24)). Harmless; listed so nobody re-flags them.

## C. Rev-1 findings re-checked against Rev4 Gerbers

| Rev-1 finding | Rev4 status | Evidence |
|---|---|---|
| F-007 encoder click switches unrouted | **FIXED** | ENCL1 pin 1 (108.0, −85.25) has an F.Cu track; ENCR1 pin 1 (231.75, −85.25) a B.Cu track; both pin 2s sit in the GND pour on both layers |
| F-004/F-012 0.1 mm traces board-wide | **FIXED** | 3.85 m → 75 mm of 0.1 mm; trunk is 0.3/0.5 mm |
| F-006 no GND pour in the .kicad_pcb | **MOOT for the Gerbers** (pours on both sides); still need the matching .kicad_pcb | section A |
| F-010 SW1 copper at the edge notch | **FIXED / moved** | zero copper features within 0.2 mm of the outline on either layer |
| F-016 MK1 annular ring | **OPEN** → R4-3 | |
| F-008 USB-C NPTH clearance | **OPEN** → R4-4 (new footprint, same pegs) | |
| F-002/F-034 LEDs top-side paste vs BOM | **UNKNOWN** — paste still has exactly the 12 LED apertures; need the Rev4 BOM | |
| F-001/F-018 LED drive to +9V, F-013/F-025 duplicate R21, F-020 10 Ω damper, F-019/F-027 3V3_D caps & I2C pull-ups, F-014 LED2 wiring, F-003 BOM S1/S2, F-022 card detect, F-031 amp bulk cap | **NEED SCHEMATIC/PCB/BOM** — the LED resistors, both R21s, FB4, C14 and C17 are no longer at their rev-1 coordinates, so something changed, but Gerbers can't say what | delta.py |
| F-017 via count | 93 → 255 | |
| F-032 no chassis mounting holes | **OPEN** — NPTH set is unchanged (28 + 1 slot, all component pegs) | |
| F-033 silk warnings cosmetic | superseded by R4-1 (now a real overlap on the component side) | |

## D. What is needed to finish Rev4

1. **Rev4 KiCad project** — `.kicad_pro`, `.kicad_sch` (all sheets), and the `.kicad_pcb` that produced these Gerbers (it must show both pours filled). Settles R4-2 (which DFN pins), identifies every new part, and unlocks ERC/DRC, netlist, power and I2C checks.
2. **Rev4 BOM / CPL** — settles the LED, R21 and S1/S2 ledger items.
3. **Trey's intent on two points:** is the artwork meant to be on the back (R4-1)? And what display/connector did Rev4 settle on (J8 16-pin header vs the planned ZIF)?

## E. Reproduce
```
python3 rev4/tools/checks.py rev4/Gerbers            # fab geometry (needs shapely: pip install shapely)
python3 rev4/tools/delta.py Manifold_Gerb_LedFix rev4/Gerbers   # needs pcbnew + rev-1 .kicad_pcb
python3 rev4/tools/render.py rev4/Gerbers OUT "" B_Cu,F_Cu,Edge_Cuts 8   # SVG+PNG via headless Chromium
```
