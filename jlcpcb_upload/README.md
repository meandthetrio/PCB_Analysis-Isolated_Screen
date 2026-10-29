# JLCPCB upload package — WavetableController, "LedFix" revision

Everything needed to quote (and order) another run of the board revision that
was fabbed and assembled twice at JLCPCB. Nothing here changes the design; the
Gerbers are byte-identical copies of `../Manifold_Gerb_LedFix/`.

| Upload step | File | Status |
|---|---|---|
| PCB quote: "Add Gerber file" | `WavetableController_LedFix_Gerbers.zip` | Ready. Flat zip of the 12 fab files (2 copper, 2 mask, 2 paste, 2 silk, Edge.Cuts, PTH + NPTH Excellon drills, .gbrjob). SHA-256 verified against the source folder. |
| SMT assembly: "Add BOM file" | `../ManifoldRe_BOM_NEW - Excel Format.xls` | Ready (JLCPCB template columns `Comment / Designator / Footprint / JLCPCB Part #`, 31 lines, 62 designators, every LCSC number well-formed). See caveats. |
| SMT assembly: "Add CPL file" | `WavetableController_LedFix_CPL.csv` | **Newly generated** — the repo had no pick-and-place file. 61 bottom-side SMD parts. See how it was verified. |

## Quote settings that the files imply

- 2 layers, 165.3 × 101.8 mm, 1.6 mm FR-4, 1 oz outer copper (from the .gbrjob).
- Min trace/space on the board is 0.10 mm, exactly JLCPCB's 2-layer 1 oz limit (F-004). Do **not** pick 2 oz copper: its 0.16 mm minimum would make the board unmanufacturable.
- Vias 0.6 mm pad / 0.3 mm drill → the standard "0.3 mm" via option is fine.
- Outline has a deliberate notch for SW1 and one 1.5 mm routed slot (NPTH) — both fabbed fine twice.
- Assembly side: **Bottom** only. Every BOM part sits on the bottom copper; the only top-side SMD parts are LED1/LED2, which are not in the BOM (see below).
- Surface finish is not in the files; the .gbrjob says "None" (choose HASL/ENIG at order time).

## How the CPL was produced and verified

Source: `kicad-cli pcb export pos --format csv --units mm --smd-only` on
`../WavetableController.kicad_pcb`, converted to JLCPCB's
`Designator, Mid X, Mid Y, Layer, Rotation` columns (mm, KiCad's native rotation,
same coordinate frame as the Gerbers: absolute origin, Y negated).

The checked-in `.kicad_pcb` is known to be a stale copy (no GND pour, F-006), so
the positions were checked against the fabbed Gerbers rather than trusted:

- Every paste-bearing SMD pad in the `.kicad_pcb` (12 top, 188 bottom) has a paste
  aperture in `F_Paste`/`B_Paste` at the same coordinate (tolerance 0.02 mm):
  **200 / 200 matched**. All 63 SMD footprints are where the fabbed boards have them.
- Every footprint's placement point coincides with its pad-group centre except P2
  (USB-C), where the KiCad library footprint's origin is the connector body centre
  (1.3 mm from the pad centroid) — this is what JLCPCB expects for Mid X/Y.
- The Gerbers contain two extra SMD footprints that are **not** in the `.kicad_pcb`:
  a 6.3×7.7 mm electrolytic land pattern at (167.95, −94.0) and an 0603 at
  (217.75, −74.5). Both have unconnected pads (no track reaches them, matcher nets
  `island_*`) and no BOM line, so they are abandoned placeholders; the CPL omits them.

Two deliberate edits relative to the raw export:

1. **The 10 Ω OLED damper is listed as `R29`, not `R21`.** The board has two R21s
   (F-013). Left as-is, JLCPCB maps both to the single 300 Ω R21 BOM line and places
   300 Ω in the OLED supply (F-025). With the rename, JLCPCB will warn that R29 has no
   BOM line and leave it unpopulated (the OLED still gets power through FB4). To have
   it placed, add `R29` to the BOM's existing 10 Ω line (`R1`, LCSC C22859).
2. **LED1/LED2 are excluded.** They are not in the BOM, and placing them as wired is
   harmful (reverse-biased to +9 V, 3.3 V-only Daisy pins — FINAL_REPORT Tier 1 #2).

## Caveats you will see during upload (all known findings, none block a quote)

- BOM lines `S1, S2` (SMD tactile switch C2835239) have no CPL position — the board's
  tactile switches are through-hole (F-003). JLCPCB will flag "no placement data"
  and skip them. Delete the line before ordering, or it is paid for and not placed.
- `R29` not in BOM (see above).
- Rotation: the CPL carries KiCad library orientations. JLCPCB's part 0° can differ
  by 90°/180° for some packages, so check the polarised/keyed parts in their placement
  preview before confirming: D1–D5 (SOD-323), C6, C7, C15 (electrolytics), U1 (SOP-6),
  U2 (SOT-666), U3 (MSOP-8), U4 (DFN-14), P1, P2, J1. If Trey still has the CPL he
  uploaded for the previous two runs, prefer it — it is fab truth for rotations.
- BOM "Comment" cells contain mojibake (`Œ©` for Ω, `‚ÑÉ` for ℃) and some
  "Footprint" cells read `603` — cosmetic; JLCPCB matches on the LCSC number.
- 18 through-hole parts (Daisy Seed, encoders, jacks, SW1, MK1, C14 470 µF, the four
  tactile switches) are intentionally absent from the SMT BOM and must be hand-soldered
  (F-026). JLCPCB can quote THT assembly separately if you add them to the BOM/CPL.

## Reminder

This package re-orders the board **as it exists today**, including the Tier 1 defects
in `../analysis/FINAL_REPORT.md` (dead encoder clicks, broken LED circuit, no I2C
pull-ups). It is the right thing to quote a reprint of the known-working boards; it
is not rev-2.

## Format references (JLCPCB help centre, fetched 2026-10-29)

- CPL: required fields Designator, Mid X/Mid Y (mm), Layer (Top/Bottom), Rotation
  (degrees, counter-clockwise positive); .csv/.xls/.xlsx —
  https://jlcpcb.com/help/article/46-pick-place-file-for-pcb-assembly
- BOM: Comment, Designator, Footprint, LCSC/JLCPCB Part #; .csv/.xls/.xlsx —
  https://jlcpcb.com/help/article/how-to-generate-the-bom-and-centroid-file-from-kicad
- Gerbers: all copper/mask/paste/silk layers + Edge.Cuts + Excellon drills
  (absolute origin, mm, decimal), zipped —
  https://jlcpcb.com/help/article/how-to-generate-gerber-and-drill-files-in-kicad-8
