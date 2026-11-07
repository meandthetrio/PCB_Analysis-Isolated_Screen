# Pass 1 — Fab Constraints Report
**Date:** 2026-11-07 · **Truth checked:** Gerbers (candidate fab set) + converted board for pad geometry · **Thresholds:** JLCPCB capabilities page, fetched 2026-11-07 (2-layer, 1 oz) — `THRESHOLDS.md`

Every dimension in use vs. JLCPCB's published limit (`scripts/pb1_fab_extract.py`, `pb1_gerber_pour.py`, exact-shape clearance script in PASS0/1 session log; DRC re-run with the same limits as KiCad constraints → `data/drc_jlcpcb_rules.json`).

| # | Parameter | Board (measured) | JLCPCB limit | Margin | Class |
|---|-----------|------------------|--------------|--------|-------|
| 1 | Trace width | 0.40 mm, all 768 segments (5 864 mm) | ≥0.10 mm | +0.30 (4×) | OK |
| 2 | Copper spacing | pad-to-track 0.202 mm (Q1.1/Q3.x vs VP, exact shapes); track-to-track 0.234 mm (RAP1S/X); DRC clean at the 0.20 mm netclass | ≥0.10 mm (pad-to-track 0.10) | +0.10 | OK |
| 3 | Via diameter / hole | 0.80 / 0.40 mm, all 86 | ≥0.25 / ≥0.15; dia ≥ hole + 0.10 | +0.55 / +0.25 | OK |
| 4 | Via annular ring | 0.20 mm | abs min 0.18, recommended 0.25 | +0.02 / −0.05 | OK, below recommended (PB-F-007) |
| 5 | Component PTH annular ring | **0.15 mm — Q1, Q2, Q3 (9 pads, `TO-92_Inline` 1.05 × 1.5 oval / Ø0.75)**; next 0.355 (TO-126), then 0.375 … 0.65 | abs min 0.18, recommended 0.25 | **−0.03** | **VIOLATION (PB-F-006)** |
| 6 | PTH drill sizes | 0.75 (56), 0.80 (104), 1.00 (15), 1.10 (4), 1.20 (14), 1.30 (46) | 0.15 – 6.3 mm | ample | OK |
| 7 | NPTH sizes | 1.20 (×2, coil clip stakes), 3.20 (×4, M3) | ≥0.50 mm | +0.70 | OK |
| 8 | NPTH-to-copper | pour edge 0.25 mm from every NPTH hole edge (Gerber); nearest track 0.32 mm (H2 vs TAP3) | ≥0.20 mm | +0.05 | OK (tight; see PB-F-016) |
| 9 | PTH hole-to-track | 0.407 mm (Q3.1 hole vs VP track) | ≥0.28 (0.35 rec.) | +0.13 | OK |
| 10 | Via hole-to-track | 0.498 mm | ≥0.20 | +0.30 | OK |
| 11 | Hole-to-hole | 0.52 mm (TO-92 pads, 1.27 mm pitch, Ø0.75) | pad-pad ≥0.45; via-via ≥0.20 | +0.07 | OK (tight) |
| 12 | Copper-to-edge | tracks 0.89 (TAP2), vias 1.64, pads 5.2, pour 1.00 mm | ≥0.20 mm (routed) | +0.69 | OK |
| 13 | Solder mask | openings = 239 PTH + 6 NPTH per side; vias tented; narrowest mask web 0.94 mm | bridge ≥0.10 | ample | OK (PB-F-029) |
| 14 | Silkscreen | 92/96 reference designators 0.8 mm high / 0.12 mm stroke; 5 ref/outline overlaps (C31–C35) | ≥1.0 mm height, ≥0.15 mm width, 0.15 mm to pads | **−0.2 / −0.03** | JUDGMENT, legibility (PB-F-008) |
| 15 | Board | 170 × 130 × 1.6 mm, 2 layers, HASL | 3 × 3 … 670 × 600 | — | OK |

## PB-F-006 — TO-92 annular ring 0.15 mm (VIOLATION)
KiCad's `TO-92_Inline` (narrow, 1.27 mm pitch) uses 1.05 × 1.5 mm oval pads on Ø0.75 drills so
the pads fit the pitch; the short-axis ring is (1.05 − 0.75)/2 = 0.15 mm, 0.03 mm under JLCPCB's
absolute minimum for component holes and 0.10 under the recommended 0.25. All nine pads of
Q1, Q2, Q3. DRC with the JLCPCB constraints reports exactly these nine `annular_width` errors.
Fix: `TO-92_Inline_Wide` (2.54 mm pitch, Ø1.5 round pads on Ø0.8 → 0.35 mm ring), which also
matches the parts list's "formed leads 2.54 mm" (PB-F-030); or keep the narrow footprint with a
Ø0.65 drill (ring 0.20) — the TO-92 lead is ≤ 0.55 mm.

## PB-F-007 — via ring at 0.20 mm (JUDGMENT)
Above the 0.18 mm absolute minimum but below the 0.25 recommended; 86 vias. 0.9/0.4 or 0.8/0.3 gives 0.25 at no routing cost on this board (netclass via is 0.6/0.3; the autorouter used 0.8/0.4).

## PB-F-008 — silkscreen below JLCPCB's legibility minimums (JUDGMENT)
Library-default 0.8 mm / 0.12 mm references on 92 footprints; JLCPCB says 0.15 mm lines, 1.0 mm text. Set 1.0/0.15 board-wide (Edit Text & Graphics Properties) and nudge the five film-cap references off their outlines.

## PB-F-009 — all other fab dimensions pass with ≥2× margin (PASS)
Rows 1–3, 6–13, 15 above. Noteworthy only because of how uniform the board is: one track width, one via, no SMD, no fine pitch.

## PB-F-010 — Gerber set completeness (info)
7 layers (F/B Cu, F/B mask, F/B silk, Edge.Cuts) + one Excellon file with PTH and NPTH merged (`FileFunction MixedPlating`, tool attributes present) + drill map + `.gbrjob`. No paste layers (through-hole only) and no fab/assembly drawing. JLCPCB's upload path accepts KiCad's merged drill file with X2 attributes; the "-filled-" file-name prefix is cosmetic.

## DRC with JLCPCB constraints (KiCad 9, scratch copy, severity-all): 244 items
109 `text_thickness` + 109 `text_height` (PB-F-008) · 9 `annular_width` (PB-F-006) · 5 `silk_overlap` (PB-F-008) · 12 `shorting_items` (L1 net-tie copper, tool artifact — PB-F-005). 0 clearance, 0 track-width, 0 hole-clearance, 0 edge-clearance, 0 courtyard, 0 unconnected.

## Island check
A KiCad 9 refill of the GND zone with island removal on reproduces the Gerber's five fill polygons exactly (89, 114, 14, 24 and 18 522 mm²; 85 % of the board); with island removal off it produces 22 — so the four small polygons near U1/U2 are connected pour fragments, not floating copper.
