# ProtoBuild1 (Rev K iron block) — Final Design Review Report
**Date:** 2026-11-07 · **Scope:** the `ProtoBuild1-autorouted` upload (KiCad 10 project, Gerbers, parts list) · **Method:** the six-pass checklist in `HIGH_LEVEL_PLAN.md` under `SOURCE_OF_TRUTH.md` · **Ledger:** `FINDINGS.md` (PB-F-001…030) · **Status:** all passes complete; every finding verified except two that wait on information only Trey / Don-Audio have.

This board has not been fabricated. Unlike the Manifold review there is no "what the physical
boards do" tier; Tier 1 here means "will stop the first build from working or from being
ordered as-is".

## Decisions log

- **2026-11-08 — inductor moves to a plug-in daughterboard** (PB-F-031). The main board drops the RM10 footprint and gets a keyed 1 × 5 header: common/RST, 23.5 mH/TAP4, 47 mH/TAP3, 94 mH/TAP2, 188 mH/TAP1. PB-F-018 and PB-F-028 are superseded; the former-pinout question now lives on the small board only.

## Tier 1 — fix before ordering

1. **Define the coil header (PB-F-031, replaces PB-F-018).** Replace the coil footprint with a keyed 1 × 5 header wired common / 23.5 / 47 / 94 / 188 mH = RST / TAP4 / TAP3 / TAP2 / TAP1, holes ≈1.0 mm. Until that is drawn, the board as uploaded still has an open coil and five undefined jumpers.
2. **TO-92 annular ring 0.15 mm on Q1–Q3 (PB-F-006)** is under JLCPCB's 0.18 mm absolute minimum; the same narrow 1.27 mm footprint also conflicts with the lead-formed 2.54 mm parts on the order (PB-F-030). Swap to `TO-92_Inline_Wide` — one change fixes both.
3. **Parts list is short two terminal blocks (PB-F-020):** J13 (3-pos) and J17 (2-pos), the coil-lead blocks. 8 × MKDS 1,5/2 and 10 × MKDS 1,5/3 are needed, 46 positions not 41.
4. **The design files only open in KiCad 10 (PB-F-001)** despite the README's "9 or 10"; the DRC that reports 0 ran with no constraints at all (PB-F-002). Re-save natively from KiCad 10, put the JLCPCB minimums into Board Setup → Constraints (`data/ProtoBuild1.jlcpcb-rules.kicad_pro` has the values), and re-run — it will then show item 2.

## Tier 2 — assembly and first-power landmines

5. **Coil former pinout now belongs to the daughterboard (PB-F-028, superseded).** The corner-group footprint, its Ø0.75 pin holes and 1.2 mm clip stakes still need Don-Audio's drawing, but a wrong guess now costs a small respin instead of the main board.
6. **Q6 bias current source tops out near 80 mA / ~0.85 W (PB-F-015)**, not the parts list's 50 mA / 0.6 W. Thermally fine with the heatsink, but 80 mA DC flows through SW1a, the tap, the coil and the 1 Ω sense; set the design maximum deliberately (R17 68 Ω for 50 mA) or document 80.
7. **Heatsink clearance (PB-F-023):** C15 and R17 are 6 mm from Q6 where the parts list asks for 10 mm; the slip-on sink is 19.8 mm in one axis.
8. **Parts-list names ≠ silkscreen names (PB-F-022):** Rs/Rdc/R1a/Cs1a…/J-2/J-3 vs R51/R50/R1/C31…/J1–J18. Rename or add a column before stuffing.
9. **Mounting holes vs ground pour (PB-F-016):** pour 0.25 mm from the M3 holes under mask only; screw heads will sit on it. Decide on a deliberate chassis bond or a copper keep-out.

## Tier 3 — fab margins and cosmetics

10. Via ring 0.20 mm (above 0.18 abs, below 0.25 recommended) on all 86 vias (PB-F-007).
11. Silkscreen references 0.8 mm / 0.12 mm, below JLCPCB's 1.0 / 0.15 legibility minimum; five refs sit on film-cap outlines (PB-F-008).
12. KiCad 9 reports 12 "shorting items" on the coil footprint and 94 library-mismatch warnings — tool artifacts of the version mix, not defects (PB-F-005).

## Tier 4 — robustness, next revision

13. No local rail decoupling at the discrete output stage / LTP; nearest caps 25–50 mm, bulk 110 mm (PB-F-013). Low current, low risk; add 100 n at Q4/Q5.
14. Long autorouted analog nets: N 164 mm, P 190, X 159, D 253 (PB-F-024). Hand-route N/P/X short on Rev L.
15. Series 1N4002 diodes cost ~0.7 V per rail; R18 bleed is optional per the Traco sheet (PB-F-012).
16. Net-label-style schematic is unreadable as a circuit (PB-F-004); worth a drawn sheet before anyone else works on it.
17. **Drive headroom changes with the Q switch (PB-F-033):** the three paralleled NE5532 halves current-limit at ≈13 / 6.7 / 4.1 V peak on Q 1 / 2 / 4. Fine if intended as soft limiting; otherwise note it or add drive capability.

## Verified passes (cited in the pass reports)

- Gerbers, board file and netlist describe one design state: 768/768 copper segments, 86/86 vias, 57/57 nets, pour polygons reproduced exactly (PB-F-003).
- ERC 0 errors in KiCad 10 and 9; 15 no-connects all on unused switch positions; 0 unrouted (PB-F-017).
- Every polarised capacitor, every diode and every transistor pin order checks against the netlist and the onsemi datasheets (PB-F-011).
- All fab dimensions other than items 2, 10, 11 pass with ≥2× margin: 0.40 mm tracks, ≥0.202 mm clearance, 0.407 mm hole-to-track, 0.52 mm hole-to-hole, 0.89 mm copper-to-edge, mask web 0.94 mm (PB-F-009).
- Rail capacity 1.23 A vs ≤0.1 A; ±14.3 V inside NE5532 limits; 100 µF per rail inside the Traco's 1000 µF cap-load limit (PB-F-014, PB-F-025).
- Tuning arithmetic lands on 100.7 / 199 / 404 / 801 Hz; switch/pot/coil wiring tables are self-consistent (PB-F-019).
- Function verified from the netlist: a tuned second-order all-pass around the coil (OUT = 2P − D), flat magnitude, Q 0.9 / 1.8 / 2.9, DRIVE and make-up gains exactly complementary — an iron-saturation colour stage, not an EQ (PB-F-032).
- Parts list values and footprints match the schematic for all 70 on-board refs (PB-F-021).
- 18/18 terminal blocks on an edge, facing outward; no body overlaps; courtyards everywhere; vias tented; M3 holes at the corners (PB-F-027, PB-F-029).

## Questions for Trey

1. **Coil pinout / former type** — Don-Audio's drawing for the RM10-CTM 23.5/47/94/188 mH part, now for the daughterboard layout (PB-F-031); plus the header keying choice.
2. **Which KiCad is the working tool?** If KiCad 10 on the Mac, re-save the project natively and drop the "KiCad 9" claim; if anyone needs 9, `tools/kicad10_to_9.py` makes a review copy only.
3. **Lead form actually ordered for Q1–Q3** (KSC1845FTA / KSA992FTA are lead-formed per onsemi) — confirms the footprint swap in item 2.
4. **Heatsink orientation on Q6** and whether 80 mA is the intended bias maximum.
5. **Chassis grounding intent** for the four M3 holes.
6. **SW1 non-shorting / SW2 shorting** — cannot be checked from the files; the parts list says Rev K requires it.
