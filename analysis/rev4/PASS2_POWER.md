# Pass 2 (rev 4) — Power Distribution + LED Drive Report
**Design case:** 9 V barrel adapter only (settled). · **Date:** 2026-10-13 · **Truth checked:** `rev4/WavetableController.kicad_sch` → `kicad_out/rev4/netlist.net` for topology; `rev4/WavetableController.kicad_pcb` (filled pour) for distances/widths. · **Thresholds:** as rev 3 (TPS62172 SLVSAT8E, NHD-2.7-12864WDW3 IDD 345/375 mA, Würth 150505M173300 Vf 2.0/3.2 V and IF 30 mA, onsemi MMBT3904, IPC-2221 computed, Daisy VIN 4–17 V). Bead ratings from the rev-4 BOM (FB2–FB6 C14709, 120 Ω / 2 A / 50 mΩ, unchanged); bridge D2–D5 now **C169541 1N5817W SOD-123FL, 1 A, 20 V, IFSM 25 A, Vf 0.45 V at 1 A** (JLCPCB part page, fetched 2026-10-13).
**Scripts:** `analysis/rev4/scripts/pass2/` — `netlist_parse.py`, `board_dump.py`, `power_geom.py` (patched to skip D6/FB7), `power_budget.py` (rewritten for the rev-4 topology), `sch_pcb_diff.py`. Raw: `kicad_out/rev4/power_budget.txt`, `power_geom.txt`, `sch_pcb_diff_p2.txt`.

## 1. Rail topology (rev 4, every node verified in the netlist)
```
J1 barrel ─┬─ pin1 ── Net-(D2-A) ── D2.A ┐            D5.K ┘ (D5.A = GND)
           └─ pin2 ── SW1 ── Net-(D3-A) ── D3.A ┤ bridge   D4.K ┘ (D4.A = GND)       D2–D5 now SOD-123F
                                                └─► Net-(D2-K) [C14 100n] → FB3 → FB4 → FB5
   → Net-(C15-Pad1) [C15 100µ, C16 100n]  → FB6                                       (D6 deleted)
   → /+9V_FLAG [C25 10µ]  ── U6.2 VIN + U6.3 EN (TPS62172, no FB7 any more)
                           ── R21/R24–R28 (390/510 Ω) → LED anodes (Würth pads 2/4/6)
                           ── R29 3.3 Ω → Net-(C17-Pad1) [C17 100µ] → R30 3.3 Ω → /DSY_VIN [C18 100µ] → A1.39
   (R31/R32/C20–C22 second π-filter removed; those refdes are now encoder parts)
U6 SW → L1 2.2 µH (now on L_Murata_DFE201610P) → /+3V3_OLED [C26 22µ, C24 100µ THT, C23 100n THT, R33 100k PG pull-up] → J8.2 only
A1.38 → /+3V3_D: C1 100n (MIDI opto), **C27 100n + C28 10µ (new, at the SD socket)**, P1.4, 5×47k SD pull-ups, R31/R32/R34/R41 10k encoder pull-ups, U1.6, R4, R6
A1.21 → /+3V3_A: C5 100n, U3.6, U4.10, FB2 → Net-(U4-VDD) [C13 2.2µ]
```
Changes vs rev 3, in Oct-7 terms: **row 2c done** (U6 fed from the FB6 output, ahead of R29/R30; /+9V_FLAG re-pointed, not orphaned — decision 5b), **row 9 done** (D6 gone; bridge now SOD-123F, part pending BOM), **row 3c done** (510/390 Ω, decision 5a), **SD caps done at the socket** (see §5).

## 2. Rail budget (`power_budget.py`; Daisy VIN current 0.10–0.20 A estimated; OLED 345/375 mA; buck η 0.88)

| I_daisy | OLED | Bridge out | /+9V_FLAG (LED + U6 VIN) | C17 node | /DSY_VIN (Daisy 4–17 V) | I through FB3–FB6 (2 A beads) | I_U6 |
|---|---|---|---|---|---|---|---|
| 0.10 A | typ | 8.20 V | **8.13 V** | 7.80 V | **7.47 V** | 331 mA | 159 mA |
| 0.10 A | max | 8.20 V | 8.13 V | 7.80 V | 7.47 V | 345 mA | 173 mA |
| 0.20 A | typ | 8.20 V | 8.11 V | 7.45 V | **6.79 V** | 431 mA | 159 mA |
| 0.20 A | max | 8.20 V | 8.11 V | 7.45 V | 6.79 V | 445 mA | 173 mA |

- The LED/U6 node is now ≈ 8.1 V (rev 3: 5.7–5.9 V behind R31/R32 and D6). LED brightness no longer tracks the display load. Daisy VIN 6.8–7.5 V (rev 3: 6.4–7.1). All within limits. U6 VIN 8.1 V in 3–17 V.
- R29/R30 dissipate ≤ 132 mW of 1 W. Beads ≤ 22 % of 2 A.

## 3. LED drive (Würth 150505M173300; pads 1/3/5 cathodes on Q collectors, 2/4/6 anodes via R to /+9V_FLAG — correct, settled)
At 8.1 V: **red (510 Ω) 11.6 mA / 69 mW; green and blue (390 Ω) 12.1 mA / 57 mW** per 0603 (100 mW). Ic/Ib 4.7–5.0 → saturated (Ib 2.45 mA through 1 kΩ). That is exactly decision 5a's outcome ("510 red / 390 G-B, keep 0603"). The 3.3 V-only pins 24/25/30 still see only a base through 1 kΩ (R3-P2-13 holds). **Schematic Value is still "CLS6B-FKW"** with the Cree pin labels (row 3d documentation NOT DONE); `sch_pcb_diff.py` still prints the Cree names — ignore, settled.

## 4. TPS62172 (U6) — unchanged layout
Cin+ 4.85 mm / Cin− 6.60 / Cout+ 5.90 / Cout− 9.04 / L1→SW 3.79 mm (L1 pads moved to the Murata pattern, 0.55 × 1.60 at ±0.725); SW net 4.9 mm @ 0.2 mm; EP 2 × 0.25 mm vias; R33 PG pull-up still feeds nothing. VIN now comes straight from /+9V_FLAG (FB7 removed) with C25 10 µF 4.85 mm from the pin: Cin unchanged, so the removal of FB7 only drops the bead's 50 mΩ and its HF isolation between the buck and the LED resistors. Sizing (R3-P2-09) unchanged: 345/375 mA vs 500 mA. **L1 land pattern fixed** (R3-P4-02 → FIXED, row 6b).

## 5. Decoupling audit (`power_geom.py §B`, pad centre → nearest same-net cap)

| Power pin | Net | Rev 3 | **Rev 4** | Verdict |
|---|---|---|---|---|
| P1.4 SD VDD | /+3V3_D | C1 at 120.2 mm, no local cap | **C28 10 µF at 5.2 mm, C27 100 nF at 6.9 mm** (copper path 6.4 / 9.9 mm) | **FIXED** (decision 5d first half) |
| A1.38 Daisy 3V3_D | /+3V3_D | C1 at 110.9 mm | **C28 at 27.9 mm** (46.6 mm copper), C27 30.9, C1 110.9 | improved; the separate 10 µF "at pin 38" (decision 5d) was not added — C28 serves both at 28 mm |
| A1.21 / U3.6 3V3_A | /+3V3_A | C5 100 nF only | **unchanged** — no ≥10 µF at the TPA6110A2 | F-031 / R3-P2-11 STILL OPEN |
| A1.39 VIN | /DSY_VIN | C18 at 45.4 mm | unchanged | OK |
| U6.2 / U6.6 / J8.2 | — | 4.85 / 5.9 / 5.3 mm | unchanged | OK |

/+3V3_D copper is now **327.5 mm** (rev 3: 249.4) because the right-hand encoder pull-ups R34/R41 sit at x = 246.75, 245 mm of copper from A1.38; 0.54 Ω end to end at 0.3 mm. Harmless for 10 k pull-ups; noted because the rail now visits every corner of the board.

## 6. IPC-2221 ampacity (1 oz, ΔT 10 °C: 0.2 mm → 0.74 A, 0.3 → 1.00, 0.5 → 1.45)
/+9V_FLAG: 117.7 mm (107.6 @ 0.5 + **10.0 @ 0.2**), 0.13 Ω; carries U6 input + LEDs ≈ 0.25 A (34 % of the 0.2 mm limit) — PASS. Net-(C15-Pad1) 15.8 mm (10.0 @ 0.5 + 5.7 @ 0.2) carries the whole board 0.33–0.45 A (61 % of 0.74 A) — PASS but the narrowest loaded copper on the board. Net-(C17-Pad1) 23.3 @ 0.5, /DSY_VIN 77.2 @ 0.5 — PASS. /+3V3_A still 4.8 mm @ 0.1 (0.45 A, load < 0.1 A) — zero-margin width (R4-P1-01).

## 7. Inrush (decision 5e) — NOT DONE
No series resistor or NTC was added before C15 (Net-(C15-Pad1) = C15, C16, FB5.2, FB6.1 only). What changed: the bulk on the ~8 V side fell from 7 × 100 µF to **3 × 100 µF + 10 µF** (C19–C22 100 µF are gone), and the cap on the unlimited path fell from 200 µF (C15 + C19) to **100 µF (C15)**; stored energy 23.5 → 10.4 mJ. But the path got stiffer: D6 and one bead are gone, so with the rev-3 beads (50 mΩ) the peak into C15 from a stiff adapter is ≈ (9 − 0.8)/(3 × 0.05 + 0.1 ESR) ≈ **33 A** (rev 3: ≈ 26 A), through a bridge rated IFSM 25 A (8.3 ms half-sine). The pulse into 100 µF behind 0.25 Ω lasts ≈ 25 µs (τ = RC), so the energy is a tiny fraction of the 8.3 ms rating pulse and the diodes will survive; the number is a stiff-adapter upper bound — a real 9 V adapter's output impedance and current limit set the actual peak. The 7 Oct consequence (stress on SW1 and the jack contacts, bounce into the caps) remains. C17/C18 remain limited by R29 (2.5 A) and R29 + R30 (1.2 A). **Half-fixed by subtraction; the 1–2.2 Ω / NTC before C15 is still the ask.** Plain-language scenario (what wears, what doesn't) in `FINAL_REPORT.md` Tier 1 item 2.

## 8. ERC power items — unchanged
`power_pin_not_driven` ×4 (A1.39 VIN, U4.5 VDD, U6.2 VIN, #PWR01 GND): still no PWR_FLAGs (R3-P2-14 / F-024 STILL OPEN).

## 9. Findings (Pass 2, rev 4)

| ID | Class | Status | Finding | Evidence | Threshold |
|---|---|---|---|---|---|
| R4-P2-01 | PASS | confirmed | **U6 fed ahead of the 3.3 Ω filters** (row 2c FIXED); /+9V_FLAG ≈ 8.1 V and independent of display load; R29/R30 ≤ 132 mW; beads ≤ 22 %. | §1–2 | computed |
| R4-P2-02 | PASS | confirmed | **LED resistors 510 Ω red / 390 Ω green-blue** → 11.6 / 12.1 mA, 69 / 57 mW in 0603 (row 3c FIXED per decision 5a). | §3 | Würth Vf/IF |
| R4-P2-03 | JUDGMENT (doc) | confirmed (R3-P2-03 unchanged) | Schematic still names CLS6B-FKW with Cree pin labels; LEDs still have no hand-solder line (BOM pending). | sch Value | — |
| R4-P2-04 | PASS | confirmed | **D6 removed**, FB7 removed; bridge D2–D5 now SOD-123F (row 9 FIXED on the schematic; part rating pending BOM). Series chain is now bridge → 4 beads → R29/R30 only. | §1 | — |
| R4-P2-05 | JUDGMENT | confirmed (R3-P2-05 **STILL OPEN**, changed) | No inrush limiter before C15 (decision 5e not applied). Bulk reduced 700 → 310 µF and unlimited cap 200 → 100 µF, but the path lost D6 + 1 bead → peak ≈ 33 A at 9 V with 50 mΩ beads. Bridge is 1N5817W (IFSM 25 A, 8.3 ms): survives the ≈25 µs pulse; SW1/jack contact stress and cap bounce remain the reason for the 1–2.2 Ω. | §7 | computed |
| R4-P2-06 | PASS | confirmed | **SD socket decoupled**: C28 10 µF 5.2 mm + C27 100 nF 6.9 mm from P1.4 (R3-P2-10 half → FIXED at the socket). | §5 | — |
| R4-P2-07 | JUDGMENT | confirmed | The second 10 µF at A1.38 (decision 5d) was not added; nearest cap to the Daisy 3V3_D pin is C28 at 27.9 mm (46.6 mm copper). Acceptable (the Daisy has its own LDO output caps); add if SD bursts still dip the rail. | §5 | — |
| R4-P2-08 | JUDGMENT | confirmed (F-031 / R3-P2-11 unchanged) | TPA6110A2: still no ≥10 µF on /+3V3_A; 4.8 mm of 0.1 mm trace. | §5 | SLOS314B |
| R4-P2-09 | PASS | confirmed | TPS62172 sizing and loop unchanged; **L1 now on the Murata land pattern** (row 6b FIXED). EP vias 0.25 (Pass 1). R33 PG pull-up unused. | §4 | SLVSAT8E |
| R4-P2-10 | PASS | confirmed | Daisy VIN 6.8–7.5 V (4–17 V); AGND/DGND tied; reverse polarity by the bridge; 3.3 V-only pins behind 1 kΩ bases. | §2–3 | Daisy datasheet (rev-2 record) |
| R4-P2-11 | JUDGMENT | confirmed (R3-P2-14 unchanged) | 4 PWR_FLAGs still missing. | ERC | — |
| R4-P2-12 | JUDGMENT (doc) | confirmed | **Refdes repurposed again**: C19–C22 were 100 µF electrolytics in rev 3 and are 10 nF encoder caps in rev 4; R31/R32 were 3.3 Ω 1 W and are 10 k pull-ups. Any rev-3 note naming them is stale (R3-P4-06 pattern repeats). | netlist diff | — |

## 10. Rev-3 Pass-2 findings — status in rev 4
R3-P2-01/02 REFUTED (settled) · R3-P2-03 STILL OPEN (doc) · R3-P2-04 **FIXED** (510/390) · R3-P2-05 STILL OPEN (bulk reduced, no limiter) · R3-P2-06 **FIXED** (D6 gone, π-filter #2 gone; 4 beads remain) · R3-P2-07 PASS · R3-P2-08 unchanged (vias 0.25, loop distances) · R3-P2-09 PASS, L1 pattern fixed · R3-P2-10 **FIXED at the socket** · R3-P2-11 STILL OPEN · R3-P2-12 PASS · R3-P2-13 PASS · R3-P2-14 STILL OPEN.
