# Pass 2 (Rev 3) — Power Distribution + LED Drive Report
**Design case:** 9 V barrel adapter (confirmed by Kyle 2026-10-09); every 12 V row below is the jack's rated ceiling kept for reference, not a design case. · **Date:** 2026-10-09 · **Truth checked:** `rev3/WavetableController.kicad_sch` → `kicad_out/rev3/netlist.net` for topology; `rev3/WavetableController.kicad_pcb` (has the filled GND zone → copper truth for rev 3) for distances/widths · **Thresholds:** TI TPS62172 SLVSAT8E (scratchpad `datasheets/TPS62172.txt`), Newhaven NHD-2.7-12864WDW3 (`datasheets/NHD.txt`), Cree CLS6B-FKW CLD-CT1475 rev 5 (fetched 2026-10-09 from downloads.cree-led.com, saved `scratchpad/dl/cree/HB-CLS6B-FKW.pdf`; pin table is a drawing on p. 9, read visually), onsemi MMBT3904LT1 datasheet (fetched 2026-10-09), IPC-2221 external-trace formula (computed), JLCPCB caps as fetched in rev-2 Pass 1. Daisy Seed datasheet could not be fetched (all hosts blocked by proxy): Daisy facts below are cited to the rev-2 PASS2 record of datasheet v1.0.5 (VIN 4–17 V; 3.3 V-only pins 24/25/28/29/30; no published 3v3 current limit) and to the stock KiCad `MCU_Module:Electrosmith_Daisy_Seed_Rev4` symbol embedded in the rev-3 schematic (pin functions).

**Scripts** (all in `analysis/rev3/scripts/pass2/`, run with `python3 -I`): `netlist_parse.py` (netlist → JSON/tables), `board_dump.py` (pcbnew → JSON), `power_geom.py` (rail copper, pin→cap distances, U6 loop, LED pads, series-chain placement), `power_budget.py` (rail voltages / LED currents / dissipation / inrush, assumptions listed in-file), `sch_pcb_diff.py` (sch↔pcb net diff, duplicate refdes, LED chain resolution against the Cree pin table).

---

## 1. Rail topology (from the rev-3 netlist, every node verified)

```
J1 barrel ─┬─ pin1 ──────────────── Net-(D2-A) ── D2.A ┐            D5.K ┘ (D5.A=GND)
           └─ pin2 ── SW1 (A→B) ─── Net-(D3-A) ── D3.A ┤ bridge     D4.K ┘ (D4.A=GND)
                                                       └─► Net-(D2-K) = D2.K + D3.K  [C14 100nF]
   → FB3 → FB4 → FB5 (three 120Ω@100MHz / 50mΩ beads in series)
   → Net-(D6-A)  [C15 100µF, C16 100nF]
   → D6 (Schottky, series — a 3rd diode drop; bridge already handles both polarities)
   → FB6
   → Net-(C19-Pad1)  [C19 100µF]  ── the split node
        ├─ R29 3.3Ω ─ Net-(C17-Pad1) [C17 100µF] ─ R30 3.3Ω ─► /DSY_VIN  [C18 100µF] ─► A1.39 Daisy VIN
        └─ R31 3.3Ω ─ Net-(C20-Pad1) [C20 100µF] ─ R32 3.3Ω ─► /+9V_FLAG [C21, C22 100µF]
                                                                  ├─ R21/R24–R28 (6×300Ω) → LED1/LED2 pads 2/4/6 (cathodes, see §4)
                                                                  └─ FB7 ─► Net-(U6-EN) = U6.2 VIN + U6.3 EN  [C25 10µF]
U6 TPS62172DSG (fixed 3.3 V): SW(7) → L1 2.2µH → /+3V3_OLED [C26 22µF, C24 100µF THT, C23 100nF THT, R33 100k PG pull-up]
                               VOS(6) ← /+3V3_OLED ; FB(5) → GND ; PG(8) → R33 → /+3V3_OLED (otherwise unused)
   /+3V3_OLED feeds ONLY J8.2 (NHD OLED VDD). Nothing else.
Daisy A1.38 3V3_D ─► /+3V3_D: C1 100nF, P1.4 SD VDD, R7–R11 (5×47k SD pull-ups), U1.6 H11L1, R4 33Ω (MIDI out), R6 270Ω
Daisy A1.21 3V3_A ─► /+3V3_A: C5 100nF, U3.6 TPA6110A2 VDD, U4.10 MAX9814 GAIN, FB2 → Net-(U4-VDD) [C13 2.2µF] → U4.5 VDD (+U4.2 SHDN)
USB P2 VBUS ─► /+5V_USB → U2.5 (ESD only; data-only USB by design — not a finding)
```

Answers to the scoping questions:
- **What feeds U6 VIN:** `/+9V_FLAG` through FB7 — i.e. the bridge output after FB3/4/5, D6, FB6, R31, R32. U6 VIN is *not* 9 V: computed 5.7–5.9 V at a 9 V adapter (§7).
- **What U6 VOUT supplies:** `/+3V3_OLED` → J8.2 only. The Daisy 3v3 rails no longer touch the display.
- **D6** sits between the FB3-5 bead chain and FB6, in series with everything (Daisy + OLED + LEDs).
- **The four 3.3 Ω 2512 resistors** form two RC π-filters: R29/R30 (+C17, C18) into Daisy VIN; R31/R32 (+C20, C21, C22) into the LED/U6 branch. Both branches hang off the same node (C19).
- **100 µF caps (7 SMD + 1 THT):** C15 (pre-D6), C19 (split node), C17/C18 (Daisy branch), C20/C21/C22 (LED/U6 branch) — all on the ~8 V side; C24 (THT radial) on `/+3V3_OLED` at the OLED header. C23 100 nF axial THT also at J8.
- **Beads:** FB3/FB4/FB5/FB6 all in the main input path (same current); FB7 isolates U6's input from `/+9V_FLAG`; FB2 isolates MAX9814 VDD from `/+3V3_A`. FB1 is gone; nothing isolates `/+3V3_D` branches any more.
- **Reverse polarity:** D2–D5 is a true bridge (D4/D5 anodes on GND), so either barrel polarity works ("Polarity Protection Pos or Neg" on the sheet). Two bridge diodes conduct in series for either polarity.

Sch↔PCB consistency (`sch_pcb_diff.py`): 110 footprints = 110 symbols, **0 duplicate refdes**, 378 pads compared, **0 net mismatches** (the 7 reported are `unconnected-…` vs blank naming of the same no-connects).

## 2. TPS62172 (U6) vs SLVSAT8E

| Check | Board | Datasheet | Verdict |
|---|---|---|---|
| VIN range | 5.7–5.9 V (9 V adapter), 8.9 V (12 V) — §7 | 3–17 V (§6.3); UVLO falling 2.6–2.82 V | PASS |
| EN | tied to VIN (same net) | "High = enabled"; abs max VIN+0.3 | PASS |
| FB (fixed-voltage part) | → GND | "recommended to connect FB to AGND on fixed output versions" (pin table) | PASS |
| VOS | → `/+3V3_OLED` at C26 (5.9 mm from C26.1) | "connect in the shortest way to VOUT at the output capacitor" (§11.1) | PASS |
| PG | R33 100k to `/+3V3_OLED`, no consumer | open-drain, needs pull-up "to any voltage below 7 V"; if unused "connect to GND but may be left floating" | PASS (R33 is a no-op) |
| L1 | 2.2 µH DFE201610P-2R2M (BOM: 1.4 A / 2 A, 168 mΩ) | 2.2 µH standard; Table 3 parts 1.0–1.9 A; IL(max) = Iout + ΔIL/2 = 0.375 + 0.16 = 0.53 A | PASS |
| Cin | C25 10 µF 25 V 0805 | "10 µF is sufficient and is recommended" (§9.2.2.4.2) | PASS |
| Cout | C26 22 µF 25 V 0805 (+C24 100 µF, C23 100 nF at the load) | 22 µF recommended; Table 2: 2.2 µH/22 µF = "standard value" ✓, 2.2 µH/100 µF also ✓ | PASS |
| Load | NHD IDD = **345 mA typ / 375 mA max** (VDD 3.3 V, 100 % on, default jumper — NHD.txt l.245) | 500 mA continuous | PASS, 69/75 % of rating |
| Thermal pad | EP soldered (B.Cu), 2 thermal vias in footprint, **0.25 mm drill** | "must be soldered"; TI recommends vias to ground plane | PASS electrically; see R3-P2-08 for the drill |

**Measured loop geometry** (pad centre → pad centre, `power_geom.py §C`; U6, L1, C25, C26 all on B.Cu):

| Path | mm | Trace | Datasheet §11.1 wording |
|---|---|---|---|
| C25.1 (Cin+) → U6.2 VIN | 4.85 | 0.2 mm, 7.25 mm net total | "as close as possible… wide and short" |
| C25.2 (Cin−) → U6.1 PGND | 6.60 | via GND zone | "as close as possible to the VIN and PGND pin" |
| C26.1 (Cout+) → U6.6 VOS | 5.90 | 0.2/0.5 mm | OK |
| C26.1 → L1.2 | 4.72 | 0.5 mm | "inductor… connect directly to the output capacitor" |
| C26.2 (Cout−) → U6.1 PGND | 9.04 | via GND zone | "ground as close as possible to the IC's PGND" |
| L1.1 → U6.7 SW | 4.05 | SW net 4.73 mm @ 0.2 mm, B.Cu only, 0 vias | "inductor close to the SW pin" — OK |
| U6.6 VOS → J8.2 (load) | 40.8 | `/+3V3_OLED` 54.6 mm: 46.4 mm @ 0.5 + 4.2 mm @ 0.2 (B.Cu) + 4.0 @ 0.5 (F.Cu), 0 vias | OK |
| Thermal vias | 2 × Ø0.25 mm drill, 0.6 mm pad, under the 0.9×1.6 mm EP | project DRC min hole 0.30 → 2 `drill_out_of_range` errors; JLCPCB PTH drill 0.15–6.3 mm (rev-2 PASS1 row 5) → fab OK |
| U6 → U3 / U4 / MK1 (2.25 MHz switcher vs audio) | 38.0 / 32.9 / 29.0 | — | note only |

## 3. Inrush / stored energy (JUDGMENT — no cited rule; see R3-P2-05)
- Caps on the ~8 V side: **700 µF** (C15, C17–C22). Stored energy 23.5 mJ at 9 V, 43.9 mJ at 12 V.
- Caps with no resistive limit: C15 + C19 = **200 µF**, behind only 2–3 Schottky drops and 4 beads (4 × 50 mΩ = 0.2 Ω DCR). Peak ≈ (V − 3·0.4)/(0.2 Ω + ESR + adapter Zout) → **~26 A at 9 V from a stiff source**, set by the adapter, not by the board. C17/C20 are limited to 2.4 A by R29/R31 (2512, 1 W — fine for a single pulse).
- Bridge diodes D2–D5 and D6 = LCSC C727114 (BOM line: 1 A average, 9 A surge). Beads are rated 2 A (thermal) and will saturate for the pulse (harmless to them, but they provide no limiting).
- No NTC, no soft-start, SW1 is a slide switch (contact bounce into 200 µF). The protection relies on the wall adapter's current limit / hiccup behaviour.

## 4. LED drive (6 channels)

**Chain per channel** (`sch_pcb_diff.py`; pad numbers resolved against Cree CLD-CT1475 rev 5 p. 9: ① blue anode ② blue cathode ③ red anode ④ red cathode ⑤ green anode ⑥ green cathode):

| GPIO net | Daisy pin | Base R | Q | Q.C → LED pad (symbol label → Cree die) | LED pad → R → supply |
|---|---|---|---|---|---|
| /LED_1_B | 25 (3.3 V-only) | R37 1k | Q1 | LED1.1 ("AR" → **blue anode**) | LED1.2 ("KR" → blue cathode) → R21 300R → /+9V_FLAG |
| /LED_1_R | 27 | R36 1k | Q2 | LED1.3 ("AG" → **red anode**) | LED1.4 ("KR" → red cathode) → R24 300R → /+9V_FLAG |
| /LED_1_G | 26 | R35 1k | Q3 | LED1.5 ("AB" → **green anode**) | LED1.6 ("KB" → green cathode) → R25 300R → /+9V_FLAG |
| /LED_2_B | 30 (3.3 V-only) | R40 1k | Q4 | LED2.1 ("AR" → blue anode) | LED2.2 → R26 300R → /+9V_FLAG |
| /LED_2_R | 24 (3.3 V-only) | R39 1k | Q5 | LED2.3 ("AG" → red anode) | LED2.4 → R27 300R → /+9V_FLAG |
| /LED_2_G | 31 | R38 1k | Q6 | LED2.5 ("AB" → green anode) | LED2.6 → R28 300R → /+9V_FLAG |

All six Q emitters → GND. LED1 and LED2 are wired identically in schematic and PCB (0 pad-net mismatches; both use identical lib symbols `CLS6B-FKW_1`/`_2`, pins 1/3/5 left = "A", 2/4/6 right = "K").

**Polarity:** the Cree part's anodes (1/3/5) are on the NPN collectors and its cathodes (2/4/6) go through 300 Ω to `/+9V_FLAG`. That is reverse bias — the schematic graphic shows it too (triangles point from the Q side toward the 300R side). When a Q saturates the die sees ≈ V_FLAG − VCE(sat) = **5.5 V (9 V adapter) / 8.7 V (12 V)** reverse, vs **VR max 5 V** and the datasheet note "Continuous reverse voltage can cause LED damage". With Q off the anode floats (only IR ≤ 10 µA). **The LEDs cannot light in this circuit.** Rev-2 F-001/F-018 is therefore still open: the driver changed (GPIO → 1k → NPN) but the anode/cathode orientation did not.

**Colour mapping:** two independent label errors cancel. The custom symbol names pad 1 "AR", pad 3 "AG", pad 5 "AB" (and pad 4 "KR" instead of KG — copied from the stock KiCad `CLS6B-FKW` symbol, which has the same duplicated "KR"), but Cree's pad 1 is blue, 3 red, 5 green. The nets were wired /LED_x_B → pad 1, /LED_x_R → pad 3, /LED_x_G → pad 5 — so the GPIO net names *do* reach the right dice. Same wiring existed in rev 2 (checked against `kicad_out/rev2_netlist.net`).

**Footprint vs package:** CLS6B-FKW is a **4.7 × 1.5 × 1.3 mm single-row PLCC6** (datasheet p. 1 and p. 9; stock KiCad `LED_SMD:LED_Cree-PLCC6_4.7x1.5mm` pads at x = ±2.02, ±1.21, ±0.53 mm in one row). The board's custom `LED_RGB_5050-6_Retroactive Pin Out` is a two-column 5050 pattern: pads 1.1 × 2.0 mm at x = ±2.40, y = 0 / ±1.70 mm. The Cree part cannot be placed on it. The rev-3 BOM still has **no LED line** (rev-2 F-002), so which physical LED Trey intends is unknown — if it is a generic 5050 RGB, both the polarity and the colour mapping above depend on that part's pinout and are unverified.

**Driver numbers** (onsemi MMBT3904LT1: VCE(sat) ≤ 0.2 V at IC = 10 mA / IB = 1 mA, ≤ 0.3 V at 50/5 mA; VBE(sat) ≤ 0.85 V; hFE ≥ 100 at 10 mA, ≥ 30 at 100 mA; IC max 200 mA):
- Ib = (3.3 − 0.85)/1k = **2.45 mA** (2.6 mA with VBE 0.7 V). Guaranteed-saturation Ic at the datasheet's forced-β of 10 = 24 mA; at hFE(min) 30 = 74 mA.
- If the LEDs were forward-biased: Ic = (V_FLAG − Vf − 0.2)/300 Ω. At a 9 V adapter V_FLAG ≈ 5.7–5.9 V → **R 11–12 mA, G/B 8–9 mA** (Cree Vf avg 2.1/3.1/3.1 V; rated IF 30/20/20 mA) — Ic/Ib ≈ 3–5, well saturated; P(300R) = 43/24/22 mW vs 100 mW (0603). At a 12 V adapter V_FLAG ≈ 8.9–9.0 V → R 22 mA, G/B 19 mA; **P(300R) = 149 / 111 / 107 mW > 100 mW rating**.
- LED current also rides on the OLED load (shared R31/R32): ΔV_FLAG ≈ 0.15 V between OLED typ and max → ~0.5 mA per LED; negligible but the rail is no longer 9 V.

**3.3 V-only pins 24/25/30:** each now drives only R39/R37/R40 (1 kΩ) into a base; the collector side (and the 300R/+9V side) has no path to the GPIO. Worst-case pin voltage = VBE(sat) ≤ 0.85 V when sourcing; with the pin low, the base is at 0 V. Rev-2 F-018 item 3 (avalanche injection into non-tolerant pins) is **closed**. Pin 28 (also 3.3 V-only) drives J8.4 D/C at 3.3 V — fine.

Hygiene: 2 DRC `via_dangling` on /LED_2_R (167.75, 145.9) and /LED_2_B (168.53, 145.74) — stray vias on the driver nets.

## 5. Decoupling audit (`power_geom.py §B`, pad-centre → nearest same-net capacitor)

| Power pin | Net | Nearest cap | Distance | Other same-net caps | Verdict |
|---|---|---|---|---|---|
| A1.39 Daisy VIN | /DSY_VIN | C18 100 µF | 45.4 mm | — | bulk only; OK (Daisy has onboard input caps) |
| A1.38 Daisy 3V3_D | /+3V3_D | C1 100 nF | **110.9 mm** | none | **single 100 nF for the whole rail** (F-019 carry) |
| A1.21 Daisy 3V3_A | /+3V3_A | C5 100 nF | 38.2 mm | none | no bulk (F-031 carry) |
| U1.6 H11L1 | /+3V3_D | C1 100 nF | 8.6 mm | — | OK |
| U2.5 USBLC6 VBUS | /+5V_USB | none | — | — | OK (ESD clamp only, data-only USB) |
| U3.6 TPA6110A2 VDD | /+3V3_A | C5 100 nF | 5.6 mm | none | 0.1 µF ✓; **≥10 µF bulk still absent** (SLOS314B, F-031) |
| U4.5 MAX9814 VDD | Net-(U4-VDD) | C13 2.2 µF | 5.7 mm | — | OK (behind FB2) |
| U6.2 TPS62172 VIN | Net-(U6-EN) | C25 10 µF | 4.85 mm | — | OK (see §2 for loop) |
| U6.6 VOS | /+3V3_OLED | C26 22 µF | 5.9 mm | C24 100 µF @32.1, C23 100 nF @36.1 | OK |
| J8.2 OLED VDD | /+3V3_OLED | C23 100 nF | 5.3 mm | C24 100 µF @9.2, C26 22 µF @35.2 | OK — good local decoupling for the 345 mA display |
| P1.4 SD VDD | /+3V3_D | C1 100 nF | **120.2 mm** | none | **no local cap at the SD socket** (rev-2 asked for 100 nF + 10 µF) |

`/+3V3_D` trunk now: **249.4 mm total — 184.8 mm @ 0.3 mm (F.Cu) + 64.5 mm @ 0.3 mm (B.Cu) + 0.1 mm @ 0.2**, 8 vias, 0.41 Ω end-to-end (was 254 mm @ 0.1 mm, ~1.2 Ω). Width fixed; capacitance not. `/+3V3_A` still has 4.8 mm of 0.1 mm trace on B.Cu at (187.8, 155.7–159.1) near U4 (F-004 zero-margin remnant).

## 6. IPC-2221 ampacity (external, 1 oz, ΔT 10 °C: 0.1 mm → 0.45 A, 0.2 → 0.74 A, 0.3 → 1.00 A, 0.5 → 1.45 A) and DC resistance

| Net | Copper (mm @ width, layer) | Narrowest | Capacity @ narrowest | Est. load | R end-to-end | Verdict |
|---|---|---|---|---|---|---|
| Net-(D2-A)/(D3-A)/(SW1-A) (jack → bridge) | 13.9 / 10.7 / 26.1 @ 0.5 | 0.5 | 1.45 A | 0.38–0.50 A total | 14 / 10 / 26 mΩ | PASS |
| Net-(D2-K) → FB chain → Net-(D6-A) → D6 → FB6 | 12.0 + 1.7 + 1.7 + 12.3 + 1.7 @ 0.5 (B.Cu) | 0.5 | 1.45 A | 0.38–0.50 A | ~30 mΩ | PASS |
| Net-(C19-Pad1) (split node) | 21.2 @ 0.5 + **5.4 @ 0.2** | 0.2 | 0.74 A | 0.38–0.50 A | 34 mΩ | PASS (0.5 A ≈ 68 % of the 0.2 mm stub's limit) |
| Net-(C17-Pad1) → /DSY_VIN | 23.3 @ 0.5 ; 77.2 @ 0.5 (3 vias) | 0.5 | 1.45 A | 0.10–0.20 A (est.) | 23 + 76 mΩ | PASS |
| Net-(C20-Pad1) → /+9V_FLAG | 8.0 @ 0.2 ; 82.1 @ 0.5 (2 vias) | 0.2 | 0.74 A | 0.27–0.30 A | 20 + 81 mΩ | PASS |
| Net-(U6-EN) (FB7 → U6 VIN) | 7.2 @ 0.2 | 0.2 | 0.74 A | 0.22–0.25 A | 18 mΩ | PASS (datasheet asks "wide") |
| Net-(U6-SW) | 4.7 @ 0.2 | 0.2 | 0.74 A | 0.53 A peak / 0.375 A avg | 12 mΩ | PASS |
| /+3V3_OLED | 46.4 @ 0.5 + 4.0 @ 0.5 + **4.2 @ 0.2** | 0.2 | 0.74 A | 0.345–0.375 A | 60 mΩ (→ 22 mV drop) | PASS |
| /+3V3_D | 249.3 @ 0.3 + 0.1 @ 0.2 | 0.2 (0.1 mm long) | 1.00 A (0.3) | ~0.15 A peak (SD bursts) | 409 mΩ | PASS for heat; impedance → F-019 |
| /+3V3_A | 34.7 @ 0.5 + 5.6 @ 0.5 + 5.6 @ 0.3 + **4.8 @ 0.1** | 0.1 | 0.45 A | < 0.1 A | 73 mΩ | PASS (zero-margin width, F-004) |
| Net-(U4-VDD) | 11.9 @ 0.1 | 0.1 | 0.45 A | ~3 mA | 58 mΩ | PASS |
| /+5V_USB | 20.1 @ 0.3 | 0.3 | 1.00 A | ~0 | 33 mΩ | PASS |

Ferrites (LCSC C14709, 2 A, 50 mΩ): FB3/FB4/FB5/FB6 carry the whole board, **0.38–0.50 A** (§7) = 19–25 % of rating; FB7 0.22–0.25 A; FB2 ~3 mA. PASS. 3.3 Ω 2512 (1 W): R31/R32 dissipate 0.26–0.30 W, R29/R30 0.03–0.13 W. PASS.

## 7. Daisy VIN / rail voltage budget (`power_budget.py`; assumptions: Schottky 0.40 V each at these currents, bead 50 mΩ, Daisy VIN current 0.10–0.20 A **estimated**, OLED 345/375 mA, buck efficiency 0.88)

| Adapter | Daisy I | OLED | Bridge out | Node C19 | **/DSY_VIN** (Daisy 4–17 V) | **/+9V_FLAG** | U6 VIN (3–17 V) | I through FB3-6 |
|---|---|---|---|---|---|---|---|---|
| 9 V | 0.10 A | typ | 8.20 V | 7.72 V | **7.06 V** | 5.88 V | 5.87 V | 379 mA |
| 9 V | 0.20 A | max | 8.20 V | 7.70 V | **6.38 V** | 5.70 V | 5.69 V | 503 mA |
| 12 V | 0.10 A | typ | 11.20 V | 10.73 V | **10.07 V** | 8.98 V | 8.97 V | 365 mA |
| 12 V | 0.20 A | max | 11.20 V | 10.70 V | **9.38 V** | 8.87 V | 8.87 V | 477 mA |

- Daisy VIN sees three Schottky drops + 4 beads + **6.6 Ω (R29+R30)**: 6.4–7.1 V at a 9 V adapter — inside 4–17 V with ≥2.4 V margin even at 0.3 A. PASS.
- Reverse polarity: handled by the bridge; D6 adds nothing to it.
- `/+9V_FLAG` is a ~5.8 V rail at 9 V input; everything sized "for 9 V" on it (the 300 Ω LED resistors) is actually running at 5.8 V.

## 8. Findings

| ID | Class | Status | Finding | Evidence | Threshold source |
|---|---|---|---|---|---|
| R3-P2-01 | **VIOLATION** | confirmed (for the named part) | **LEDs still reverse-biased.** Cree pads 1/3/5 (anodes) are on Q1–Q6 collectors; pads 2/4/6 (cathodes) go via 300 Ω to /+9V_FLAG. LEDs cannot light; when a Q is on the die sees 5.5 V (9 V adapter) / 8.7 V (12 V) reverse vs VR max 5 V ("continuous reverse voltage can cause LED damage"). Rev-2 F-001/F-018 polarity bug carried through the new transistor stage unchanged. Fix: swap so cathode → collector, anode → R → supply (or move the 300R to the collector and tie anodes to the rail). | `sch_pcb_diff.py` chain table; schematic graphic (diode direction); Cree p. 9 pin drawing | Cree CLD-CT1475 rev 5 (pin table, VR = 5 V, note under electrical table) |
| R3-P2-02 | **VIOLATION** | plausible (needs Trey: which LED is actually bought) | **Footprint ≠ package.** CLS6B-FKW is 4.7×1.5×1.3 mm, 6 leads in one row (x = ±2.02, ±1.21, ±0.53); the custom `LED_RGB_5050-6_Retroactive Pin Out` is a 2-column 5050 pattern (1.1×2.0 pads at x = ±2.40, y = 0/±1.70). The named part cannot be placed on it. BOM still has no LED line (F-002), so the physical part is unknown; if it is a generic 5050, R3-P2-01/03 must be re-checked against that part's pinout. | `power_geom.py §D` pad table vs stock `LED_Cree-PLCC6_4.7x1.5mm` | Cree datasheet p. 1/p. 9 mechanical; stock KiCad footprint |
| R3-P2-03 | JUDGMENT | confirmed | Custom LED symbol pin labels are wrong for the named part (pad 1 "AR" = blue anode, 3 "AG" = red anode, 5 "AB" = green anode; pad 4 labelled "KR" twice — inherited from the stock KiCad symbol). Net names were wired so colours come out right (/LED_x_R → pad 3 = red, etc.) — two errors cancel. Fix the labels so the next edit doesn't "correct" only one of them. | chain table; both lib symbols `CLS6B-FKW_1/_2` identical | Cree p. 9 |
| R3-P2-04 | VIOLATION (conditional on a 12 V adapter) / ZERO-MARGIN at 9 V | plausible | 300 Ω 0603 (100 mW) LED resistors: at 12 V input (J1 jack is 12 V-rated, Daisy VIN allows 17 V) red = 22 mA → **149 mW**, G/B 19 mA → 107–111 mW. At the intended 9 V: 43/24/22 mW (PASS) but then LED currents are only 11–12 / 8–9 mA (40–60 % of rated) and track the OLED load through R31/R32. Resize for the real ~5.8 V rail or drive from 3.3 V. | `power_budget.py` scenario table | Cree Vf/IF; BOM 0603 rating; onsemi VCE(sat) |
| R3-P2-05 | JUDGMENT | confirmed | **No inrush limit** for 700 µF on the ~8 V side: 200 µF (C15+C19) sit behind only 0.2 Ω of bead DCR + 2–3 Schottkys → ~26 A (9 V) / ~36 A (12 V) peak from a stiff adapter, through diodes rated 9 A surge and beads rated 2 A; 23–44 mJ per plug-in / SW1 flip. Suggest an NTC or series R before C15, or fewer bulk caps (two 100 µF already filter each branch). | §3 | computed; BOM diode line (C727114) |
| R3-P2-06 | JUDGMENT | confirmed | Series-element audit: **D6 is redundant** (bridge already protects both polarities) and costs a third ~0.4 V drop plus ~0.2 W in a SOD-323 at 0.5 A; **four identical beads in series** (FB3/4/5/6) add 0.2 Ω and no additional HF attenuation worth the parts; the two 3.3 Ω π-filters make both downstream rails load-dependent (DSY_VIN 6.4–7.1 V, /+9V_FLAG 5.7–5.9 V at 9 V). Functionally OK (all within limits) — simplify. | §1, §7 | — |
| R3-P2-07 | PASS | confirmed | Daisy VIN: 6.4–7.1 V (9 V) / 9.4–10.1 V (12 V) vs 4–17 V; AGND/DGND tied (A1.20 + A1.40 on GND); reverse polarity handled by D2–D5; SD pull-ups 5×47k on /+3V3_D unchanged. F-021 re-verified. | §7; netlist | Daisy datasheet v1.0.5 as recorded in rev-2 PASS2 |
| R3-P2-08 | JUDGMENT | confirmed | TPS62172 layout is workable but loose: Cin+ 4.85 mm / Cin− 6.6 mm / Cout− 9.0 mm to the IC pins, VIN feed 0.2 mm wide (datasheet: "as close as possible… wide and short", "single point grounding at the thermal pad"). SW node 4.7 mm @ 0.2 mm (good), VOS at Cout (good), FB → AGND (good). Thermal vias Ø0.25 mm are below the project's own DRC min hole 0.30 (2 DRC errors) though inside JLCPCB's 0.15 mm PTH limit — either raise them to 0.30 or lower the rule. PG pull-up R33 serves nothing (harmless). | `power_geom.py §C`; `drc_asis.json` | SLVSAT8E §11.1; PASS1 fab limits |
| R3-P2-09 | PASS | confirmed | U6 sizing: OLED 345/375 mA vs 500 mA (69/75 %); L1 2.2 µH + 22 µF = datasheet "standard" combination; Cin 10 µF as recommended; IL(peak) 0.53 A vs L1 1.4 A; U6 VIN 5.7–9 V vs 3–17 V; J8 at default jumper (pins 3/15/18 NC; BS0/BS1 = GND → 4-wire SPI); /+3V3_OLED has 100 nF + 100 µF within 9.2 mm of J8.2. | §2, §5 | SLVSAT8E Tables 2/3, §9.2.2.4; NHD.txt l.244–250 |
| R3-P2-10 | JUDGMENT (F-019 carry) | confirmed | /+3V3_D: trunk widened 0.1 → 0.3 mm (249 mm, 0.41 Ω) **but still one 100 nF (C1) at the MIDI opto**; A1.38 → C1 = 110.9 mm, SD P1.4 → C1 = 120.2 mm, no cap at the SD socket. Half of F-019 done. Add 100 nF + 10 µF at P1 and 10 µF at A1.38. | §5 | IPC-2221 computed; rev-2 F-019 |
| R3-P2-11 | JUDGMENT (F-031 carry) | confirmed | TPA6110A2: C5 100 nF at 5.6 mm ✓, the datasheet's ≥10 µF near the amp is still absent; /+3V3_A has no bulk at all and keeps 4.8 mm of 0.1 mm trace. | §5, §6 | SLOS314B (rev-2 archive) |
| R3-P2-12 | PASS | confirmed | Copper: every power net is within IPC-2221 at ΔT 10 °C; narrowest loaded segments are the 0.2 mm stubs on Net-(C19-Pad1) (5.4 mm), Net-(C20-Pad1), Net-(U6-EN), /+3V3_OLED (4.2 mm) at ≤ 68 % of 0.74 A; all beads ≤ 25 % of 2 A; 3.3 Ω 2512s ≤ 0.30 W of 1 W; 300R at 9 V ≤ 43 mW. | §6 | IPC-2221 computed |
| R3-P2-13 | PASS | confirmed | 3.3 V-only pins 24/25/30 now see only a 1 kΩ base resistor (max ≈ VBE(sat) 0.85 V); the +9V_FLAG side has no path to the GPIO. Driver saturation: Ib 2.45 mA vs Ic ≤ 22 mA → Ic/Ib ≤ 9 (< 10 forced-β test condition). F-018 item 3 closed. Hygiene: 2 dangling vias on /LED_2_R and /LED_2_B. | §4 | onsemi MMBT3904LT1; rev-2 PASS2 pin list |
| R3-P2-14 | JUDGMENT | confirmed | ERC `power_pin_not_driven` on A1.39 VIN, U6.2 VIN, U4.5 VDD, #PWR01: diode/bead/resistor-fed rails with no PWR_FLAG (rev-2 F-024 carry, now three nets). Add PWR_FLAG on /DSY_VIN, Net-(U6-EN), Net-(U4-VDD). | `erc.json` | — |

## 9. Rev-2 finding status

| Rev-2 ID | Rev-3 status | Basis |
|---|---|---|
| F-001 | **OPEN** | Polarity unchanged: anodes (Cree 1/3/5) to the low side, cathodes to +9V via 300R — now through Q1–Q6 instead of directly from GPIOs. → R3-P2-01 |
| F-013 | **FIXED** | 110 PCB footprints = 110 symbols, 0 duplicate refdes (the 10 Ω R21 and the whole I2C OLED branch are gone). |
| F-014 | **FIXED** | LED2 pad nets identical in sch and pcb (378 pads, 0 mismatches); LED1 = LED2 wiring. |
| F-018 | **OPEN (2 of 3)** | Items 1–2 (cannot light; reverse voltage > VR) open → R3-P2-01. Item 3 (3.3 V-only pins exposed) **fixed** → R3-P2-13. |
| F-019 | **PARTIAL** | Trunk 0.1 → 0.3 mm done; still a single 100 nF, SD socket 120 mm from it with no local cap → R3-P2-10. |
| F-020 | **RESOLVED by redesign** | The /OLED_HOT branch (FB4/C14/C17/10R R21) no longer exists; display is on its own buck. Nothing left to back-annotate. |
| F-021 | **PASS (re-verified)** | VIN 6.4–7.1 V in range; AGND/DGND tied; 47k SD pull-ups; ampacity OK → R3-P2-07/12. |
| F-025 | **FIXED** | No duplicate R21; BOM R21 line (300R ×6) matches the six 300R positions. |
| F-031 | **OPEN** | No ≥10 µF on /+3V3_A near U3 → R3-P2-11. |

Carried but outside this pass: F-002 (LEDs still absent from the rev-3 BOM — now entangled with R3-P2-02), F-004 (0.1 mm remnants on /+3V3_A and Net-(U4-VDD)), F-024 (PWR_FLAGs → R3-P2-14).
