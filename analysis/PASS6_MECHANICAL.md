# Pass 6 — Mechanical & Assembly Report
**Date:** 2026-08-13 · **Truth checked:** `.kicad_pcb` geometry + Gerber paste/mask/silk + DRC baseline

## Board
165.1 × 101.6mm bounding box (matches the ~165×102 expectation), 1.6mm, outline is a polygon (not a plain rectangle — see SW1).

## F-010 RESOLVED: SW1 edge copper is deliberate
SW1 is a vertical **slide switch** (DigiKey 1101A4VQEA) at the top edge; its no-net anchor pads sit 0.41mm from the board's bounding box, but the Edge.Cuts **polygon notches inward** at the switch so the outline reaches the pads (DRC's 0.000mm). This is a deliberate edge-mount: the actuator needs the notch. Reclassified **JUDGMENT — accepted design deviation**: still technically below JLCPCB's 0.2mm copper-to-edge spec, fab-proven twice; expect occasional burrs/exposed copper at the notch. No action unless a fab rejects it.

## F-032 (NEW — JUDGMENT): no chassis mounting holes
Every NPTH on the board is a component alignment post: 5×1.2mm under each of the five 3.5mm jacks (25), 2.0mm at the barrel jack, 2×0.65mm at USB-C. There are **no M2.5/M3 mounting holes**. For a synth control surface this usually means the board hangs entirely from panel hardware (jack bushings, encoder nuts, switch bushings) — workable, but all mechanical stress from cable insertions transfers through solder joints and panel nuts. Confirm the enclosure plan; if the board isn't nut-mounted to a panel, this is a real gap.

## F-033 (NEW — JUDGMENT/cosmetic): silkscreen findings are panel artwork
The 143 silk warnings decompose as: 62 = front-silk **artwork polygons** (the 88 gr_polys — this board's front silk is the control-panel graphics) over copper, 37 = artwork reaching the board edge, 32 overlaps among art/refdes (ENCR1, TAC_SWITCH_2, LED2 etc.), 7 = SW1's back-silk over copper. Fabs clip silk on exposed pads automatically; over-masked-copper silk prints fine. Cosmetic — worth one visual check of the fab's silk preview on the next order, nothing more.

## F-034 (NEW — corroborates F-002): the stencil expects the missing LEDs
Paste flash counts: **F.Paste = 12 flashes — exactly the 12 pads of LED1+LED2** (the only top-side SMD parts); B.Paste = 192 (all other SMD, bottom side). So the top stencil and placement data anticipate the LEDs that the BOM omits — the assembly gap is physical, not just clerical: paste gets printed (if a top stencil was ordered) for parts that never arrive.

## Clean checks
- **Courtyard overlaps: zero** (severity-all DRC reported none) — PASS.
- **Mask layers consistent**: F/B mask flash counts (151/321) consistent with pad+via tenting config — PASS.
- **Connector accessibility**: jacks/encoders/switch all on top face with bushings at or near edges (panel-through design) — consistent with F-032's panel-mount assumption.
- Hole-to-hole, edge clearances (other than SW1), drill ranges: all covered and passed in Pass 1.
