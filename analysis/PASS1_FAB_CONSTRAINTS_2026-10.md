# Pass 1 — Fab Constraints, Round 2 (2026-10 files)
**Date:** 2026-10-07 · **Truth checked:** `Manifold_Gerbs_2026-10/` + root `.kicad_pcb` (proven identical in Pass 0, F-036) · **Status: COMPLETE**, with one threshold caveat (§3).

Every dimension in use on the Round 2 board vs. JLCPCB's published 2-layer / 1 oz limits. Classification per SOURCE_OF_TRUTH §4. Round 1 values in the last column for the fabbed LedFix board.

## 1. Limit table

| # | Parameter | Round 2 board (measured) | JLCPCB limit | Margin | Class | Round 1 |
|---|-----------|--------------------------|--------------|--------|-------|---------|
| 1 | Trace width | 0.100 mm × 66 segs / **73 mm** (GND 12.8, U4 fan-out ≈46, USART1_TX 5.9, +3V3_A 4.8, USB_IN_N 3.1, USB_IN_MCU_N 1.1); 0.2 × 176; 0.3 × 572; 0.5 × 115 | ≥ 0.10 mm (1 oz) | 0.000 mm on 1.5 % of routing | **ZERO-MARGIN, residual** (F-037) | 0.1 mm × 557 segs / 3850 mm |
| 2 | Copper spacing | 0.150 mm min (U3 MSOP-8 / U4 TDFN-14 pad gaps); everything else ≥ 0.20 (netclass, 0 other DRC hits) | ≥ 0.10 mm | 0.050 mm | OK (F-009 unchanged) | same |
| 3 | Via diameter / hole | 0.60 / 0.30 mm, **225 vias, all identical**; ring 0.150 | dia ≥ 0.25; dia ≥ hole + 0.10 | 0.35 / 0.20 mm | OK | 93 vias |
| 4 | Component PTH annular ring | **0.175 mm** (MK1.1, MK1.2 — 1.0 pad / 0.65 drill; **and U6 pad 9 ×2 — 0.6 pad / 0.25 drill**); 0.200 (ENCL1/ENCR1 MP slots, P2 shield); rest ≥ 0.25 | abs min 0.18; recommended ≥ 0.25 | **−0.005 mm** | **VIOLATION (marginal)** (F-016 persists; F-040 adds U6) | MK1 only |
| 5 | PTH drill sizes | **0.25 (×2, U6)**, 0.30 (×225), 0.65, 0.80, 1.00, 1.10, 1.30, 1.85 mm — 330 holes; slots 0.4×1.4, 0.6×1.4, 0.6×1.7, 0.8×1.5, 2.8×1.5 | 0.15–6.3 mm | 0.10 mm at the 0.25 holes | OK vs JLCPCB; **breaks the project's own 0.30 min** (F-040) | 170 holes, min 0.30 |
| 6 | NPTH sizes | 0.65 (×2, P2), 1.20 (×25, jacks), 2.00 (×1), 2.0×1.5 slot (×1) | ≥ 0.50 mm | 0.15 mm | OK | same |
| 7 | NPTH-to-copper | **0.197 mm** (P2 GND pads A1/A12/B1/B12 to P2's own 0.65 NPTH, B.Cu); next 0.251 (/+5V_USB tracks) | ≥ 0.20 mm | **−0.003 mm** | **VIOLATION (marginal)** (F-008 persists — footprint unchanged) | 0.194 |
| 8 | Hole-to-hole gap | 0.500 mm min (via–via, 12 pairs); no pad–pad pair under 0.6 | via–via ≥ 0.2; pad–pad ≥ 0.45 | 0.30 mm | OK | 0.50 |
| 9 | Copper-to-edge | **0.414 mm** (SW1 two no-net anchor pads, both rounds — see §2); **0.451 mm** (3 × /+3V3_D tracks, F.Cu, bottom edge x ≈ 102–121); GND pour 0.50 | ≥ 0.20 mm (fetched 2026-08-13); community reports the page now says ≥ 0.30 | +0.21 / +0.15 (vs 0.2); +0.11 / +0.15 (vs 0.3) | OK vs JLCPCB; **breaks the project's own 0.50 rule** (F-041); F-010 re-classified OK | reported 0.0 for SW1 (§2) |
| 10 | Hole-edge to board-edge | 0.735 mm (SW1 1.85 drills); NPTH 1.05 (jacks) | ≥ 0.25 (NPTH), ≥ 0.4 (drill to outline) per JLCPCB support | 0.34 / 0.65 mm | OK | — |
| 11 | Solder mask | expansion 0.0 (openings = pads); narrowest mask web 0.15 mm between U3/U4 pads; `min mask web` 0.0 in project | not in fetched table (see §3) | — | unverified | same |
| 12 | Silkscreen | lines 0.12 mm (588 footprint strokes, KiCad lib default) + 1 × 0.10; artwork = 3,905 filled regions (0 stroke); text min 1.0 mm / 0.15 mm thick (105 of 108 refdes) | not in fetched table; community rule 0.15 mm thickness / 1.0 mm height | 0.12 vs 0.15 → −0.03 | **plausible, threshold unverified** (F-046) | same lib defaults |
| 13 | Board thickness / copper | 1.6 mm, 2 layers, 1 oz (gbrjob stackup 0.035 mm Cu) | standard | — | OK | same |

Gerber cross-check: parser (`gerber_analyze.py Manifold_Gerbs_2026-10`) gives the same track-width histogram per layer (F 0.1×5 / B 0.1×61 = 66 ✓; 0.2: 115+61 ✓; 0.3: 271+301 ✓; 0.5: 29+86 ✓), 330/330 PTH↔pad matches on both layers, min via ring 0.150, drill tools T1C0.250 ×2 hits.

## 2. Notes

- **Row 1** — the defining Round 1 risk is substantially retired: 0.1 mm length fell 3850 → 73 mm and the +3V3_D rail is 0.3 mm end to end. What remains is mostly the U4 (TPA6110A2 mic amp) fan-out, which is forced by its 0.25 mm pads and 0.15 mm gaps — the only place 0.1 mm is justified. The six 0.1 mm segments on USART1_TX / +3V3_A / USB_IN_N / USB_IN_MCU_N are not forced and should be widened on the next edit (JUDGMENT).
- **Row 4 / F-040** — the two 0.25 mm holes are the thermal vias baked into the stock KiCad `WSON-8-1EP_2x2mm_P0.5mm_EP0.9x1.6mm_ThermalVias` footprint for the TPS62172. They are legal at JLCPCB (≥ 0.15) but the ring (0.6 − 0.25)/2 = 0.175 sits 5 µm under the 0.18 absolute minimum, exactly like MK1. Two options, either is a one-line footprint edit: drill 0.30 / pad 0.65 (ring 0.175 → same), or drill 0.25 / pad 0.70 (ring 0.225). Also raise the project `min_through_hole_diameter` to match or DRC will keep flagging it. Note: the small-hole surcharge JLCPCB applies to sub-0.3 mm drills could not be verified (§3).
- **Row 7 / F-008** — the P2 USB-C footprint is unchanged, so the 0.197 mm NPTH-to-copper stays 3 µm under spec. It fabbed twice. Latent, not blocking.
- **Row 9 / F-010 correction** — Round 1 reported SW1 anchor pads at 0.000 mm from the edge. Re-measuring both rounds' boards with the same method (pad polygon vertices to the Edge.Cuts outline, outline-only distance) gives **0.414 mm for both**; KiCad DRC agrees (0.4105). The Round 1 figure was a measurement artefact, not a copper change (SW1 moved +8.9 mm in x between rounds; Edge_Cuts is byte-identical). SW1 is **OK** against JLCPCB and only trips the project's own 0.5 mm rule. F-010 is re-classified OK; the notch remains a deliberate outline feature.
- **Row 9 / F-041** — the three +3V3_D tracks at 0.451 mm are inside JLCPCB's limit (0.2 or 0.3) with margin. The project rule (0.5) is the designer's own, stricter target. JUDGMENT: nudge the trunk 50 µm inboard to clear the designer's rule, or accept and set an exclusion.
- **Row 12 / F-046** — the 0.12 mm silk strokes are KiCad's library default and are widely fabbed at JLCPCB, but the published silk minimum could not be fetched (§3). Leave as plausible.
- Unused drill-tool definitions (0.4, 0.6, 0.8, 1.5 at 0 hits) are plot artefacts, as in Round 1.

## 3. Threshold provenance caveat

`jlcpcb.com` is blocked by this session's network egress policy (also `schemalyzer.com`), so the capabilities page could **not** be re-fetched today as SOURCE_OF_TRUTH §3 requires. Thresholds used:

1. **Primary:** the JLCPCB capabilities values fetched on 2026-08-12/13 and recorded in `SOURCE_OF_TRUTH.md` §3 and `PASS1_FAB_CONSTRAINTS.md` (trace/space 0.10, via ≥ 0.25 dia / hole + 0.1, PTH ring 0.18 abs / 0.25 rec, drill 0.15–6.3, NPTH ≥ 0.5, NPTH-to-copper 0.20, via–via 0.2 / pad–pad 0.45, copper-to-edge 0.20).
2. **Corroboration (2026-10-07 web search, search-engine summaries of jlcpcb.com):** same trace/space, ring, via, hole-to-hole and NPTH figures; copper-to-routed-edge quoted as ≥ 0.2 by the page summary and as "≥ 0.3 (updated for router tolerance)" by a 2023 comment on the darkxst KiCad-rules gist. Both values are shown in row 9. Silk and mask minimums were not in any fetched source.

**Action:** re-fetch `https://jlcpcb.com/capabilities/pcb-capabilities` from a session where the domain is allowed (environment → Network access → add `jlcpcb.com`) and update rows 9, 11, 12 if the live page differs. Nothing in the table changes class under either edge value.

## 4. Results

- **No hard fab violations.** Two marginal ones persist from Round 1 (F-016 MK1 ring 0.175, F-008 P2 NPTH 0.197) and the TPS62172 footprint adds a third of the same 0.175-ring kind (F-040).
- **Zero-margin trace width is now residual** (73 mm, F-037), mostly justified by U4.
- **F-041 and the SW1 pads are project-rule items, not fab items**; F-010 corrected to OK.
- **New plausible:** silk stroke 0.12 mm vs an unverified 0.15 mm minimum (F-046).
- Carried to Pass 6: 10 B-paste flashes without matching mask openings (parser), silk artwork regions over pads.
