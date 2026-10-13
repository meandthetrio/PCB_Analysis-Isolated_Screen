# Rev 4 — Pass 3: Connectivity / sch↔pcb / ERC
**Date:** 2026-10-13 · **Truth checked:** `rev4/WavetableController.kicad_sch` (intent) vs `rev4/WavetableController.kicad_pcb` (copper, filled pour) · **Tools:** `kicad-cli 9.0.9` ERC/DRC (`kicad_out/rev4/erc.json`, `drc_asis.json`), `pcbnew` connectivity, `analysis/rev4/scripts/pass3_5/` (`sch_inventory.py`, `pcb_export.py`, `netlist_parse.py`, `sch_pcb_diff.py`, `net_geometry.py`). Threshold sources as rev 3 (NHD pin table, Daisy symbol + libDaisy, Bourns taper convention).

## Headline
1. **Schematic and PCB are fully consistent.** 112 symbols ↔ 112 footprints, 0 duplicate refdes, 0 value/footprint mismatches, 0 real pad-level net differences over 400 pad/pin pairs (the same 28 structural residues as rev 3: 20 mechanical/shield/EP pads with no schematic pin, 8 USB-C SuperSpeed pins the 16-pin footprint lacks). 0 one-file nets. DRC 0 unconnected.
2. **Encoder A/B lines now carry the RC network** (row 7): each of /ENCL_A, /ENCL_B, /ENCR_A, /ENCR_B is a 4-node net — encoder pin, Daisy pin, a 10 k to /+3V3_D and a 10 nF to GND. Routed with continuous copper: 88.1 / 96.7 / 159.7 / 157.2 mm, 6–8 vias each, 0.3 mm (0.2 mm stubs on the ENCR pair). **The caps sit at the encoder end, on the back**: C19/C20 6.8–7.2 mm from ENCL1's pins and 63 mm from Daisy pins 32/33; C21/C22 10 mm from ENCR1's pins and 111 mm from Daisy pins 12/13 (decision 5c asked for ≤ 2 mm from the Daisy pins on the front face). See Pass 5 for the electrical consequence.
3. **Encoder clicks** unchanged: /ENCL_CLICK 170.6 mm / 6 vias to pin 22 (PC0), /ENCR_CLICK 190.6 mm / 10 vias to pin 29 (PA5), still no external pull-up (libDaisy internal PULLUP).
4. **J8 unchanged**: 20/20 pins per the NHD serial table, BS1 = BS0 = GND (4-wire SPI), pins 3/9/15/18 NC. /RES_SPI still a bare 2-node net (R3-P3-04 open).
5. **ERC: identical 51 items** to rev 3 — 14 missing NC flags, 4 missing PWR_FLAGs, /SWA dangling, GND/SWB double name, 31 library warnings. Nothing was added, nothing new appeared.

## 1. Schematic ↔ PCB diff (`sch_pcb_diff.py`, `kicad_out/rev4/sch_pcb_diff_p3.txt`)
| Check | Result |
|---|---|
| Components only in schematic / footprints only in PCB | none / none |
| Duplicate refdes | none |
| Value / footprint mismatches | none (L1 now `L_Murata_DFE201610P` in both) |
| Nets only in one file | none (117 schematic nets incl. 15 `unconnected-*` + /SWA; 110 board nets) |
| Pad-level differences | 0 real; 28 structural (as rev 3) |
| Single-pad nets | /SWA (P1.10) only — F-022 STILL OPEN |
| GND | one net, now 96 B-side + 40 F-side pad-faces, zone on both layers, 0 GND vias |

## 2. ERC disposition — all 20 non-library items, unchanged from rev 3 §2
10 × P2 SuperSpeed/SBU NC (intentional, USB2-only) · J8 3/9/15/18 NC (correct per NHD) · A1.39 VIN, U4.5 VDD, U6.2 VIN, #PWR01 GND `power_pin_not_driven` (passive-fed rails, PWR_FLAGs still absent) · `label_dangling` SWA (F-022) · GND/SWB `multiple_net_names` (informational). The 7 Oct "ERC: 14 NC flags + 4 PWR_FLAGs" row is **NOT DONE**.

## 3. Encoder A/B networks (new in rev 4)
| Net | Daisy pin (STM32) | Encoder pin | Pull-up → /+3V3_D | Cap → GND | Copper | Cap position (side) | Cap → encoder pin | Cap → Daisy pin |
|---|---|---|---|---|---|---|---|---|
| /ENCL_A | 33 (D26) | ENCL1.A | R31 10 k | C19 10 nF | 88.1 mm, 6 vias, 0.3 | (101.25, 99.00) B | 6.8 mm | 62.8 mm |
| /ENCL_B | 32 (D25) | ENCL1.B | R32 10 k | C20 10 nF | 96.7 mm, 8 vias | (101.25, 97.25) B | 7.2 mm | 64.1 mm |
| /ENCR_A | 12 (D11 = PB9) | ENCR1.A | R34 10 k | C21 10 nF | 159.7 mm, 8 vias | (246.75, 98.00) B | 10.2 mm | 111.4 mm |
| /ENCR_B | 13 (D12 = PB8) | ENCR1.B | R41 10 k | C22 10 nF | 157.2 mm, 8 vias | (246.75, 99.75) B | 10.0 mm | 110.7 mm |

Pull-ups "anywhere on the net" (decision 5c) — satisfied. Caps "within ~2 mm of Daisy pins 12/13/32/33 on the FRONT face with a GND via each" — **not satisfied**: the caps are at the encoders on the back (on the B.Cu pour, so no GND via is needed there). The RC is 10 k × 10 nF = 100 µs either way; what differs is that 63–111 mm of 0.3 mm trace now lies *between* the filter cap and the MCU input instead of between the contact and the cap. Electrically that is the Bourns-style "filter at the encoder" arrangement: it debounces the contact at its source, but leaves the MCU input on an unterminated line whose far end is a 10 nF-to-ground (low impedance at HF) — ringing is damped by the 10 k source, so the practical penalty is noise pickup along the run rather than ringing. Score: **done, not as agreed**; the measured free spots from rev 3 ((143.9,147.4), (146.5,147.4), (135.8,159.0), (133.2,159.0)) are still free (nothing was placed on the front near the Seed).

## 4. SD-socket caps (new): C27 100 nF and C28 10 µF on /+3V3_D at (93.5, 145.0) / (97.0, 144.75), B side, 6.4 / 9.9 mm of copper from P1.4, GND pads on the pour (C28.1 single spoke, Pass 1). Decision 5d first half done; the 10 µF at A1.38 not added.

## 5. Other connectivity checks
- /SWA single-pin, SWB on GND — F-022 unchanged; all 40 Daisy pins still assigned.
- `via_dangling` ×2 (/LED_2_R, /LED_2_B) unchanged.
- MISO (pin 10) still doubles as /TAC_SHIFT_R; firmware SPI1 TX-only note stands.
- Headphones1 wiring unchanged (pot at the TPA6110A2 input, linear taper, R3-P3-07 ⏳ still open).

## Findings (rev 4, Pass 3)
| ID | Class | Status | Finding | Evidence |
|---|---|---|---|---|
| R4-P3-01 | PASS | confirmed | Schematic ↔ PCB consistent: 112 ↔ 112, 0 dups, 0 real pad-net diffs, 0 one-file nets. | `sch_pcb_diff_p3.txt` |
| R4-P3-02 | PASS (row 7, pull-ups) | confirmed | 4 × 10 k pull-ups to /+3V3_D on the encoder A/B lines; nets routed, continuous copper. | §3 |
| R4-P3-03 | JUDGMENT (row 7, caps) | confirmed | 4 × 10 nF placed at the encoders on the back (6.8–10.2 mm from the encoder pins, 63–111 mm from the Daisy pins), not at the Seed on the front as agreed in decision 5c. | §3, `encoder_filter.txt` |
| R4-P3-04 | PASS | confirmed | Encoder clicks routed (unchanged); internal pull-up reliance as rev 3. | `net_geometry_sel.txt` |
| R4-P3-05 | JUDGMENT | confirmed (R3-P3-04 unchanged) | /RES_SPI still floats until firmware drives it; no 10 k. | 2-node net |
| R4-P3-06 | JUDGMENT | confirmed (R3-P3-06 unchanged) | 14 NC flags + 4 PWR_FLAGs still missing; ERC 51 identical. | `erc.json` |
| R4-P3-07 | JUDGMENT | plausible (R3-P3-07 unchanged) | Headphones1 linear taper / rotation sense — still for Trey. | — |
| R4-P3-08 | PASS | confirmed | J8 = NHD table 20/20, unchanged. | `pass6_mech.txt` §H |
| R4-P3-09 | JUDGMENT | confirmed (R3-P3-10 unchanged) | /SWA card-detect still unusable; no spare Daisy pin. | — |
| R4-P3-10 | PASS | confirmed | SD caps C27/C28 wired P1.4 ↔ GND at the socket. | §4 |
