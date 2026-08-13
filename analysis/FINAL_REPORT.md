# WavetableController — Final Red-Flag Report
**Date:** 2026-08-13 · **Scope:** Passes 0–6 complete (see `HIGH_LEVEL_PLAN.md`), 35 ledger entries (`FINDINGS.md`), all verified per `SOURCE_OF_TRUTH.md` — every measurement scripted, every threshold fetched and cited.
**Verification state:** 33 of 35 findings confirmed; 2 blocked on information only Trey has (marked ⏳ below). Nothing remains unverified-and-unflagged.

---

## Tier 1 — Defects in the working boards (physical, today)

**1. Encoder click switches are dead.** (F-007, fab-truth confirmed)
No copper exists at any of the four click-switch pad sites on either layer of the fabbed Gerbers. Both encoder push-inputs float. If firmware reads them, behavior is undefined. *Fix: route ENCL1.S1→pin 11, ENCR1.S1→pin 29 (pin 29 is 3.3V-only — never pull above 3V3).*

**2. The RGB LEDs are broken three ways.** (F-001/F-018/F-002/F-034)
(a) Not placed: the only SMD parts missing from the BOM — while the top-side paste stencil contains exactly their 12 apertures. (b) Wired to never light: permanently reverse-biased (anodes on GPIOs, cathodes toward +9V via 300Ω). (c) Hazardous if placed: 5.7–9V reverse across dice rated ~5V, and three of the six GPIOs (Daisy pins 24/25/30) are on the datasheet's 3.3V-only list — an avalanche event injects current into non-tolerant pins. *Fix: rewire GPIO→resistor→LED→GND per the Daisy reference (Fig 1.8), resize resistors for 3.3V, add LEDs to BOM.*

**3. The I2C/OLED subsystem stands on two hidden crutches.** (F-019 confirmed + F-027 ⏳)
The 203mm I2C bus has **zero pull-up resistors in the design** — it works only because of undocumented pull-ups presumed on the OLED module. And the +3V3_D rail feeding SD+OLED+MIDI has a single 100nF cap, with the SD card 109.5mm (~0.5Ω of 0.1mm trace) from it. Together these are the causal chain behind the OLED/I2C noise that was historically patched with a ferrite + 470µF + hand-added 10Ω. *Fix: explicit 2.2–4.7k pull-ups; 100nF+10µF at the SD connector; wider 3V3_D trunk. ⏳ Ask Trey what pull-ups the OLED module carries.*

## Tier 2 — Landmines that fire on the NEXT build (files as they stand)

**4. The `.kicad_pcb` in hand has no ground plane.** (F-006)
Provably not the file that made the working Gerbers (which contain a 164×100mm B.Cu pour this file cannot produce). Re-plot from it and you ship a board with 51 floating GND connections. *Fix: get Trey's real working file, or re-create the GND zone before any re-plot.*

**5. Duplicate refdes R21 → automated mis-build.** (F-013/F-025)
Two R21s on the PCB (300Ω LED resistor + 10Ω OLED damper); the BOM's only R21 line is 300Ω. Pick-and-place from this board puts **300Ω in the OLED's power feed** (30× intended). *Fix: rename the damper (e.g., R29), give it its own BOM line.*

**6. Board-level fixes were never back-annotated.** (F-020/F-014 ⏳)
The 10Ω OLED damper exists only in the PCB; the schematic doesn't know about it. LED2's pin-wiring differs between schematic and PCB (PCB matches the fabbed Gerbers; the schematic is the outlier). Any respin driven from the schematic silently reverts both. *⏳ Reconcile against Trey's current working files.*

**7. BOM S1/S2 can't be built.** (F-003)
An SMD 6×6mm tactile switch (C2835239) with no matching board position — the board's tactile switches are all through-hole. Stale line or diverged part choice; an assembler will flag or skip it.

## Tier 3 — Fab-margin risks (absorbed by tolerance so far)

**8. 3.85 meters of trace at exactly the 0.10mm minimum** (F-004/F-012) — zero margin against JLCPCB's ±20% width tolerance, including the 3V3_D power rail. Not a violation; the defining latent risk of the layout. *Widen to ≥0.2mm on respin; note 2oz copper would make 0.1mm illegal (min 0.16).* 
**9. Three marginal spec violations, fabbed OK twice** — MK1 annular ring 0.175mm vs 0.18 absolute min (F-016); USB-C footprint NPTH-to-copper 0.194 vs 0.20mm (F-008); SW1 edge copper in its deliberate notch, 0.0 vs 0.2mm — accepted (F-010). *Footprint edits when convenient; a stricter fab lot could reject any of them.*

## Tier 4 — Robustness & hygiene (JUDGMENT)

- **Headphone amp missing its datasheet-recommended ≥10µF bulk cap** on 3V3_A (F-031, TI SLOS314B cited; mid-rail bypass check passes).
- **No chassis mounting holes** — board hangs from panel hardware; confirm the enclosure plan (F-032).
- Long thin analog runs (up to 285mm @ 0.1mm) — fine as built, shorten on respin (F-030). USB pair asymmetry — benign at Full-Speed (F-028). SD card-detect half-wired, unusable by firmware (F-022). ERC hygiene: 13 missing no-connect flags + 2 PWR_FLAGs would take ERC to zero (F-024). Hand-assembly parts (incl. the 470µF noise-fix cap) exist on no list (F-026). Silk warnings = panel artwork, cosmetic (F-033). DRC minimums zeroed in the project file — set to JLC values so KiCad guards the margins (F-005).

## What passed (verified, cited)
Power-entry topology (9V within VIN 4–17V; D2–D5 bridge); AGND↔DGND tie; SD interface incl. reference-design 47K pullups; MIDI in/out exactly per 3.3V MIDI practice; all rails within IPC-2221 ampacity; via geometry (0.6/0.3mm, wide margin); all drill sizes; hole-to-hole spacing; copper spacing; courtyards (zero overlaps); mask consistency; BOM values (58/58 designators consistent).

## The three questions for Trey
1. Send the **current working `.kicad_pcb`** — the one that shows a filled bottom ground pour when opened (this copy has none).
2. **What pull-ups are on the OLED module?** (determines whether I2C stands on anything at all)
3. Is the **schematic or the PCB** right about LED2's wiring — and does your schematic have the 10Ω OLED damper the PCB carries as a second "R21"?
