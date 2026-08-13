# Pass 3 — Connectivity Report
**Date:** 2026-08-13 · **Truth checked:** both (sch/pcb intent + Gerber fab truth where they diverge)

## Headline: encoder click switches are dead on the physical boards (F-007 → CONFIRMED)
`/ENCL_CLICK` (ENCL1.S1 → Daisy pin 11) and `/ENCR_CLICK` (ENCR1.S1 → Daisy pin 29) are defined in the schematic but have **no routing in the `.kicad_pcb` AND no copper at any of the four pad locations on either layer of the fabbed Gerbers** (geometric check, 0.8mm tolerance). The encoder ground-side pins reach the GND pour, so on the physical boards the click inputs are **floating** — firmware reading them gets undefined levels. This is a fab-truth violation, not a file artifact.
- Note for the future fix: ENCR_CLICK is on Daisy pin 29, one of the datasheet's 3.3V-only pins — fine for a switch-to-GND, but it must never gain a pull-up above 3V3.

## SWA thread resolved (from Pass 0 open threads)
`/SWA` is single-pin **in the schematic too** (P1.10, the microSD card-detect switch A; ERC: "Label connected to only one pin"). Its partner SWB is tied to GND (ERC: name collision, GND wins). So card-detect is half-wired by design: harmless electrically, but **card presence can never be read by firmware**. Classification: JUDGMENT (unused feature), not a defect — unless card-detect was intended.

## Dangling tracks: all four are GND stubs (F-006 artifact)
DRC's 4 `track_dangling` warnings are all short GND stubs on B.Cu (0.11–1.85mm). In the fabbed board these terminate into the GND pour; they only dangle in the pour-less `.kicad_pcb`. No action beyond restoring the pour (F-006).

## ERC error triage — all 17 error-severity items dispositioned
| Items | Disposition |
|---|---|
| P2 TX1±/RX1±/TX2±/RX2±, SBU1/2 not connected (10) | **Intentional** — USB-C 24-pin receptacle used USB2-only (design decision). Cosmetic fix: add no-connect flags |
| A1 ADC_0 (22), ADC_6 (28), USB_ID (1) NC (3) | **Intentional** — unused GPIO. Add no-connect flags |
| A1 VIN "power pin not driven" | **False positive** — driven through D1 Schottky + FB3 (ERC can't see through passives). Add PWR_FLAG |
| U4 VDD "power pin not driven" | **False positive** — driven through FB2 from 3V3_D. Add PWR_FLAG |
| #PWR01 not driven | Missing PWR_FLAG on the 9V input net — cosmetic |
| J4.R not connected | Stereo jack ring left floating (mono use). Acceptable; tie to GND or sleeve if plug-detection/hum matters (Pass 5 audio review) |

The remaining 190 ERC warnings are library-hygiene noise (110 lib_symbol_issues + 78 footprint_link_issues = symbols/footprints not found in local libraries on this machine — expected when files travel without their project libraries; 2 handled above).

## Net-count reconciliation
Schematic 93 pin-bearing nets vs PCB 85: difference fully explained by (a) 14 intentional `unconnected-*` single-pin nets, (b) LED2 net-name skew (F-014), (c) `/SWA` single-pin net. **No unexplained net differences remain.**

## Findings
- **F-007 CONFIRMED (VIOLATION, fab truth):** encoder clicks unrouted on physical boards — floating GPIO inputs.
- **F-022 (JUDGMENT):** SD card-detect half-wired (SWA floating, SWB grounded) — feature unusable as built.
- **F-023 (info):** 4 dangling GND stubs = missing-pour artifact, ties to F-006.
- **F-024 (JUDGMENT):** ERC hygiene — 13 missing no-connect flags, 2 missing PWR_FLAGs; would take ERC errors to zero and make future regressions visible.
