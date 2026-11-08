# Pass 6 — Mechanical & Assembly Report
**Date:** 2026-11-07 · **Truth checked:** converted board geometry, Gerber mask/silk layers, Ferroxcube RM10/I data sheet, distributor dimensions for the heatsink

## PB-F-027 — board-level mechanics: PASS
- Outline: plain 170.0 × 130.0 mm rectangle on Edge.Cuts; 4 × Ø3.2 mm NPTH (H1–H4) at 5 mm from each corner edge, matching the parts list's "M3 standoffs ×4".
- All 18 screw-terminal blocks sit on an edge with the body 0.78 mm from the outline and the wire-entry face outward (left: J1, J3, J4; top: J6, J8, J9, J10, J12, J14, J15, J16; right: J2, J5, J7, J11, J13, J17, J18). Checked for every block by body-centre offset vs pad centroid (`scripts/pb1_mech_extract.py`).
- No footprint body outlines overlap; no footprint leaves the board; every footprint, the custom coil one included, has a courtyard.
- TO-126 pair Q4/Q5 side by side (10.5 mm centres), DIP sockets, large film caps all have free space.

## PB-F-028 — the coil footprint commits to one former type (JUDGMENT, needs Trey/Don-Audio)
`RM10_corner_12P_breakout` places the 12 coil pins as two diagonal 6-pin corner clusters on a
2.54 mm grid, 20.32 mm across, Ø0.75 mm holes, plus two Ø1.2 mm clip-stake holes at (±10.16,
∓10.16). The Philips/Ferroxcube RM10/I sheet's Fig. 3 former (CSV-RM10-1S-12P, 12 pins, Ø0.6)
carries exactly the 2.54 / 10.16 / 15.24 / 20.32 dimension labels, so the footprint is a
plausible transcription of that drawing — but the same sheet also lists a DIL former
(CPV-RM10-1S-12PD, Fig. 2, two rows) that would not fit it. Don-Audio's product page does not say
which former they wind on, and the parts list itself says "pitch unknown until the coil or
Don-Audio's drawing arrives". Two detail points to verify against the real part: (a) Ø0.75 holes
for Ø0.6 pins leave 0.075 mm radial slack before JLCPCB's drill tolerance — 0.8–0.9 mm is the
usual choice; (b) the sheet shows a "1.3 +0.15/0" feature at the clip location while the footprint
drills 1.2 mm for the clip stakes. Alternative already provided: wire the coil to J13/J17.

**Decision 2026-11-08 (PB-F-031):** superseded for the main board — the footprint moves to a daughterboard, where these checks still apply.

## PB-F-029 — solder mask / tenting: fine
245 mask openings per side = 239 PTH pads + 6 NPTH; the 86 vias have no openings (tented, matching the KiCad 10 setup). Mask expansion 0; narrowest pad-to-pad mask web is on the 2.54 mm rows (0.94 mm) — far above JLCPCB's 0.10 mm bridge minimum. HASL finish per the parts list.

## PB-F-030 — TO-92 footprint pitch vs the ordered lead form (JUDGMENT; see PB-F-006 for the ring)
Q1–Q3 use KiCad's `TO-92_Inline` — 1.27 mm pitch, 1.05 × 1.5 mm oval pads, Ø0.75 drill — while the parts list orders KSC1845FTA / KSA992FTA and states "Formed leads: 2.54 mm inline". If the parts arrive with 2.54 mm formed leads they will not drop into a 1.27 mm footprint without re-forming; the wide variant (`TO-92_Inline_Wide`, 2.54 mm pitch) matches the order *and* has room for a compliant annular ring. Confirm the lead form from the onsemi ordering table before fab.

## Silkscreen (see PB-F-008)
92 of 96 reference designators are 0.8 mm high / 0.12 mm stroke (the KiCad library defaults); JLCPCB's stated legibility minimums are 1.0 mm / 0.15 mm. Five reference labels overlap their own film-cap outlines (C31–C35). The board title text is 1.5 mm / 0.2 mm. Cosmetic, but on a hand-stuffed prototype the refs are what the builder reads.
