# Thresholds used in the ProtoBuild1 review (all fetched 2026-11-07)

Rule 1 of SOURCE_OF_TRUTH: no limit comes from memory. Text extracts of the datasheets are in
`datasheets/`; the JLCPCB page was read live.

## JLCPCB — 2-layer, 1 oz FR-4 (jlcpcb.com/capabilities/pcb-capabilities)
| Parameter | Limit |
|---|---|
| Min trace width / spacing | 0.10 / 0.10 mm; finished width tolerance ±20 % |
| Pad-to-track clearance | 0.10 mm ("stay well above if possible") |
| Same-net track spacing | 0.25 mm |
| Via hole-to-track | 0.20 mm |
| PTH-to-track | 0.28 mm (0.35 recommended) |
| NPTH-to-track | 0.20 mm |
| Via hole / diameter | ≥0.15 / ≥0.25 mm; diameter ≥ hole + 0.10 (0.15 preferred) |
| Via annular ring | recommended 0.25 mm, absolute min 0.18 mm |
| Component PTH annular ring | ≥0.20 general; recommended 0.25, absolute min 0.18 mm |
| NPTH min drill | 0.50 mm |
| Via hole-to-hole | 0.20 mm; pad hole-to-hole 0.45 mm |
| Copper-to-routed edge | ≥0.20 mm (V-cut 0.40) |
| Solder-mask bridge | 0.10 mm (green); mask-to-trace clearance ≥0.09 mm |
| Silkscreen | line width ≥0.15 mm, text height ≥1.0 mm, pad-to-silk 0.15 mm |
| Board size | 3 × 3 mm … 670 × 600 mm |

## IPC-2221 (external trace, computed)
I = 0.048 · ΔT^0.44 · A^0.725 (A in mil²). 0.40 mm × 35 µm → **1.23 A** at ΔT 10 °C; 0.25 mm → 0.88 A; 0.10 mm → 0.45 A. Resistance of 0.40 mm × 35 µm copper: **123 mΩ per 100 mm** (ρ = 1.72e-8 Ω·m).

## Datasheets
| Part | Values used | Source (extract) |
|---|---|---|
| KSC1845 (Q1, Q2) | TO-92 pin 1 Emitter, 2 Collector, 3 Base; VCEO 120 V; IC 50 mA; NF 7 dB typ | onsemi `ksc1845.txt` |
| KSA992 (Q3) | pin 1 Emitter, 2 Collector, 3 Base; VCEO −120 V; IC −50 mA | onsemi `ksa992.txt` |
| BD139 (Q4) | TO-126 pins 1 Emitter, 2 Collector, 3 Base (figure); VCEO 80 V; IC 1.5 A; 12.5 W; RθJC 10 °C/W; RθJA 100 °C/W | onsemi `bd135_137_139.txt` |
| BD140 (Q5, Q6) | TO-126 "1 2 3 = 1 Emitter, 2 Collector, 3 Base"; VCEO −80 V; IC −1.5 A; PC 12.5 W (case), 1.25 W (free air, TA 25 °C) | onsemi `bd136_138_140.txt` |
| NE5532 (U1–U3) | abs max VCC+ +18 V / VCC− −18 V; recommended ±5 … ±15 V; ICC 6 typ / 16 max mA (per dual); IOS 38 mA; SR 5 V/µs | TI `ne5532.txt` |
| Traco TEN 5-1223 | ±15 VDC ±200 mA, 84 %, input 9–18 VDC; load regulation spec'd for 20–100 % load (dual: 2 % balanced / 5 % unbalanced); ripple 50 mVpp max; 300 kHz PFM; cap load 1000 µF max per output; I/O isolation 1500 VDC; **no minimum-load clause in this datasheet revision** (gives a no-load input current instead) | `traco_ten5.txt` |
| Ferroxcube RM10/I coil former | CSV-RM10-1S-12P: 1 section, 12 pins, all positions used; pin ∅0.6; drawing labels 2.54 / 10.16 / 15.24 / 20.32; clip CLI/P-RM10/I; core 24.7 × 21.2 ∅ × 18.6 | Philips 2000-04-20 `ferroxcube_rm10i.txt` |
| Heatsink 577500B00000G (HS1) | 8.13 × 19.81 × 13.21 mm, slip-on for TO-126, 26 °C/W natural convection — **distributor data (RS, Future, DigiKey), no manufacturer sheet found** | web search |
| Panasonic ECQ-E1106KF (C1, C16, Cs1a) | 26 × 11.5 × 21 mm body, lead spacing 22.5 mm — **distributor data** | web search |
