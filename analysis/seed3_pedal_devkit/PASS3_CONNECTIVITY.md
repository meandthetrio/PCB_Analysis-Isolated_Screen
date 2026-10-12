# Seed3 Pedal Dev Kit Rev3 — Pass 3: Connectivity / sch↔pcb / ERC
**Date:** 2026-10-12 · **Truth checked:** `reference/electrosmith/seed3_pedal_devkit/Rev3/ES-Seed3-DevKit-Pedal-Rev3.kicad_sch` (root + sub-sheets named `ES-Seed3-DevKit-Pedal-Rev1_1…4.kicad_sch` = Daisy, Peripherals, Audio IO, Power — the Rev1 file names are kept across revisions) vs `ES-Seed3-DevKit-Pedal-Rev3.kicad_pcb` (KiCad 9 format 20241229, loads in both KiCad 9 and 10). Netlist/ERC/DRC exported with KiCad 10.0.7 into `kicad_out/pedal3/` (`drc.json`: **0 unconnected items, 0 schematic-parity items**); PCB connectivity via `pcbnew` 10.0.7. Note the upstream README links a **Rev4** BOM and the repo clone holds a Rev4 folder; the files reviewed here are Rev3 (the review PDFs in the repo are Rev3). Where the README's refdes disagree with Rev3, the Rev4 schematic in the clone was grep-checked too.
**Scripts** (`analysis/seed3_pedal_devkit/scripts/`, same set as the Eurorack kit): `netlist_parse.py`, `pcb_export.py`, `sch_pcb_diff.py`, `sch_inventory.py`, `chain_walk.py`, `net_geometry.py`, `proximity.py`, `prox_lists.py`, `sd_budget.py`.
**Threshold / reference sources:** Seed 3 datasheet `Daisy_Seed3_datasheet.txt` (pin table l.213–262, 3.3 V-only pins l.130–137, expression circuit Fig 4.5 l.1762, MIDI Fig 7.1/7.4/7.6 l.1883–1962, SD l.1787–1812); upstream README `README_upstream.md`; libDaisy `src/pedal_devkit.cpp/.h`, `src/daisy_seed.h`, `src/hid/midi.cpp`, `src/hid/switch.h`, `src/hid/switch3.h`, `src/hid/led.cpp` (fetched 2026-10-12); kit repo (`daisyaudio/ES-Seed3-DevKit-Pedal`) contains no firmware. STM32H7 absolute-maximum (V_DD + 0.3 V on non-5 V-tolerant pins) and the H11L1 LED reverse-voltage rating are quoted **from memory (st.com / onsemi not fetched)**.

## Headline
1. **Schematic ↔ PCB fully consistent.** 150 components ↔ 150 footprints, 460 (part, pad) keys, **0 real differences** (29 nominal ones are pad-less fiducials, DIN-jack shell pads `P$6/P$7`, pot `CHASSIS` pads and the mounting-hole symbol pin `B3,5` vs pad `1` naming); 136 schematic nets = 132 PCB nets + 4 pad-less `unconnected-(Hn-MOUNT)` nets; 0 duplicate refdes, 0 DNP.
2. **ERC is effectively clean:** 7 library-path warnings and 2 `pin_to_pin` warnings caused by the PWR_FLAGs the designer placed on the USBLC6's GND and VBUS pins (typed "bidirectional" in that symbol). This project *does* use PWR_FLAGs (10 of them), which is why it shows none of the Eurorack kit's five `power_pin_not_driven` errors.
3. **Pin plan: 30 of 31 GPIO used; pin 13 (D12, I2C1_SDA) is the only free pin and carries an NC flag.** No expansion header. **SD card detect is wired** (U7 `CD1` → pin 12 = D11) and libDaisy `pedal_devkit.cpp` reads it (`sd_detect.Init(seed::D11)`, internal pull-up) — the only board in the reference set that can see a card.
4. **Firmware pin map matches the schematic 30/30** (6 pots, expression, 7 switches, 2 footswitches, SD detect, 4 LEDs, MIDI, SD, USB). **The README's switch refdes do not match the schematic** (README `SW3/SW4/SW6` for tactile 1/2 and toggle 3 = schematic `SW4/SW5/SW3`; the Rev4 schematic in the clone also uses SW1–SW5), while every pin number agrees. The README omits the SD-detect line that the firmware supports.
5. **The 3.3 V-only pins:** 24/25 are pot wipers on `+3V3_A` (bounded); 29/30 are a toggle and a footswitch to GND (bounded); **pin 28 (PC4) is the expression ADC, fed from a 5 V MCP6002 follower through a 10 k / 20 k divider that tops out at 5.0 × 20/30 = 3.33 V** — the Seed 3 datasheet's own Fig 4.5 circuit, designed to end exactly at the rail (ZERO-MARGIN, PD-P3-07).
6. **MIDI IN has no antiparallel diode across the opto LED** (U11.1 net = R4 only); the Pod, the Eurorack kit and Trey's rev 3 all have one; the Seed 3 datasheet's Fig 7.1 omits it. JUDGMENT (PD-P3-09). DIN pinout (4 = source, 5 = sink) is correct on all three jacks; OUT/THRU use 10 Ω / 10 Ω.

## 1. Schematic ↔ PCB netlist diff (`sch_pcb_diff.py pedal/netlist.json pedal/pcb.json`)
| Check | Result |
|---|---|
| Components / footprints | 150 / 150; only-in-sch = ∅, only-in-pcb = ∅ |
| Hierarchy | root → `Daisy` (`_1`, 31 instances), `Peripherals` (`_2`, 72), `Audio IO` (`_3`, 81), `Power` (`_4`, 42); 226 placed instances incl. 66 power symbols |
| Duplicate refdes / unannotated | none / none |
| DNP / not-in-BOM | DNP: **none**. `in_bom=no`: FD1–3, H1–4, LOGO1, QR1 |
| Value / footprint mismatch | none |
| Pad-level (part, pad) → net | 460 keys; 29 differ, all pad-less or naming: FD1–3 (NPTH ''), H1–4 (pad `1` on the PCB vs symbol pin `B3,5` — the KiCad `MountingHole_Pad` symbol pin name vs the stock footprint pad number; both sides are on no net), J1/J10/J11 `P$6/P$7` (DIN shell pads, no symbol pin), VR1–6 `CHASSIS1/2` → **0 real differences** |
| Nets | schematic 136 = PCB 132 + the 4 `unconnected-(Hn-MOUNT-PadB3,5)` nets that have no pad; PCB nets with 1 pad: none; nets with pads but no copper: none |
| `pcbnew` connectivity | `unconnected_items = 0`, `schematic_parity = []`; every non-GND net one copper island, `stubs=[]` |
| GND | one net (AGND + DGND tied): 6 × ¼" jack sleeves, DIN pin 2 + shells (J1/J11 direct; J10 via C34/C47), J7 shell + GND pads, barrel J8.1, footswitch pin 1s, U7 pin 6 + MP1–4, op-amp V− (single-supply, U1/U3/U9/U10 pin 4), 97 nodes; pours 16,650 mm² F.Cu + 17,445 mm² B.Cu |

## 2. Single-pin nets and open pins
33 single-node nets, all `unconnected-…` with no-connect flags:
| Pins | Disposition |
|---|---|
| **A1 pin 13 (`I2C1_SDA`, D12)** | the one free GPIO; NC-flagged (PD-P3-06) |
| H1–H4 `MOUNT` | isolated mounting holes |
| J1/J10/J11 P1, P3 | DIN pins 1/3 unused (MIDI uses 2/4/5) |
| J2–J5 `R`, `RN`, `SN` (and J3/J5 `TN`) | ¼" jacks used TS: ring/ring-normal/sleeve-normal unused; **`TN` of J2/J4 (inputs) and J6 (expression) are used** — tip-normal → R64/R65/R68 10 k → GND grounds an unplugged input through 10 k |
| J6 `RN`, `SN` | expression jack: ring carries +5 V_A via R46 100 R, tip is the wiper |
| J7 A8/B8 | USB SBU |
| J8 pin 3 | barrel-jack switch contact unused |
| SW2/SW3 pin 3 | ON-ON toggles used as SPST |
| U11 pin 3 | H11L1 NC |

## 3. ERC disposition (`kicad_out/pedal3/erc.json`, 9 items)
| Count | Type | Items | Disposition |
|---|---|---|---|
| 1 + 1 | `footprint_link_issues`, `lib_symbol_issues` (warning) | QR1 in lib `shnsly` | private library not in this session's tables; footprint embedded → noise |
| 5 | `lib_symbol_mismatch` (warning) | SW2 `TOGGLE_ON-ON_PIP3`, SW4/SW5 `TAC_SWITCH_PTH_SILK`, U7 `TF-01A`, LED1 `LED` | embedded copy ≠ library copy (graphics); pin→net verified by the diff → noise |
| 2 | `pin_to_pin` (warning) | U14 pin 2 `GND` ↔ `#FLG02`; U14 pin 5 `VBUS` ↔ `#FLG03` | PWR_FLAGs placed on the USBLC6-2SC6's GND and VBUS pins, which its symbol types *bidirectional*; "Bidirectional ↔ Power output" is KiCad's default warning. Harmless; the flags are what suppresses the `power_pin_not_driven` errors the Eurorack kit shows |
- 0 errors. The project carries 10 PWR_FLAGs (3 on the Daisy sheet, 2 on Peripherals, 5 on Power).

## 4. Seed 3 pin usage (all 40 pins) and firmware map
Pin ↔ D-number: pin = D+1 (1–15), D+7 (22–37), datasheet l.213–262. Symbol is the stock `Electrosmith_Daisy_Seed_Rev4` (pin-compatible, datasheet l.24). Firmware = `pedal_devkit.cpp` `Hardware::Init()`. ★ = 3.3 V-only pin (datasheet l.132–137).

| Pin | Dn | STM32 | Kit net | Other end | Firmware (libDaisy) | README | Trey rev 3 |
|---|---|---|---|---|---|---|---|
| 1 | D0 | PB12 (USB_HS_ID) | `TAC_SW4` | SW4 (to GND) | `sw4.Init(D0)` ✓ | "Tactile switch 1 **SW3** TAC_SW1 D0" (refdes ≠) | `/RES_SPI` |
| 2–7 | D1–D6 | SDMMC1 | `SDMMC_D3/D2/D1/D0/CMD/CK` | U7 + 47 k R51/R50/R54/R53/R52 | fixed ✓ | ✓ | same |
| 8 | D7 | PG10 (SPI1_NSS) | `TOG_SW1_B` | SW1 pin 3 | `sw1.Init(D7, D8)` pin a ✓ ("wired opposite") | TOG_2_B D7 ✓ | `/CS_SPI` |
| 9 | D8 | PG11 (SPI1_SCK) | `TOG_SW1_A` | SW1 pin 1 | sw1 pin b ✓ | TOG_2_A D8 ✓ | `/SCLK_SPI` |
| 10 | D9 | PB4 (SPI1_MISO) | `TOG_SW2` | SW2 pin 1 | `sw2.Init(D9)` ✓ | TOG_1 D9 ✓ | `/TAC_SHIFT_R` |
| 11 | D10 | PB5 (SPI1_MOSI) | `GPIO_FSW_1` | FSW_1 pin 2 (pin 1 GND) | `fsw_1.Init(D10)` ✓ | ✓ | `/SD_IN_SPI` |
| 12 | D11 | PB8 (I2C1_SCL) | **`SDMMC_DETECT`** | U7 `CD1` | `sd_detect.Init(D11)` ✓ | not documented | `/ENCR_A` |
| 13 | D12 | PB9 (I2C1_SDA) | **none (NC)** | — | unused | — | `/ENCR_B` |
| 14 | D13 | PB6 (USART1_TX) | `MIDI_TX` | R59 10 R → J11.5 | `midi tx = D13` ✓ | ✓ | `/USART1_TX` |
| 15 | D14 | PB7 (USART1_RX) | `MIDI_RX` | U11.4, R3 270 R, R29 (thru) | `midi rx = D14` ✓ | ✓ | `/USART1_RX` |
| 16/17 | — | audio in L/R | `CODEC_IN_L/R` | R72/R27 100 R ← OPA1652 + C37/C12 33 nF | | ✓ | same |
| 18/19 | — | audio out L/R | `CODEC_OUT_L/R` | C48/C3 10 µF → 15 k → OPA1652 | | ✓ | same |
| 20 | — | AGND | `GND` | | | | |
| 21 | — | +3V3A | `+3V3_A` | VR1–6 pin 3 only | | | `/+3V3_A` |
| 22–27 | D15–D20 | PC0/PA3/PB1★/PA7★/PA6/PC1 | `POT_1 … POT_6` | VR1–6 wipers | `adc_cfg[0..5] = D15…D20` ✓ | ✓ | `/ENCL_CLICK`, `/TAC_SHIFT_L`, LED, LED, LED, LED |
| 28 ★ | D21 | PC4 (ADC6) | `ADC_EXPRESSION` | R17 10 k ← U1 follower; R60 20 k + C46 10 nF to GND | `adc_cfg[6] = D21` ✓ | ✓ | `/DC_SPI` |
| 29 ★ | D22 | PA5 (DAC1_OUT2) | `TOG_SW3` | SW3 pin 1 (to GND) | `sw3.Init(D22)` ✓ | "Toggle switch 3 **SW6** TOG_3 D22" (refdes ≠) | `/ENCR_CLICK` |
| 30 ★ | D23 | PA4 (DAC1_OUT1) | `GPIO_FSW_2` | FSW_2 pin 2 | `fsw_2.Init(D23)` ✓ | ✓ | LED |
| 31 | D24 | PA1 | `LED_MONO_1` | R43 1 k → LED1 | `led1.Init(D24, false)` ✓ | ✓ | LED |
| 32 | D25 | PA0 | `LED_R` | R40 2 k → LED2.1 | `led2.Init(D25, D27, D26, false)` red ✓ | ✓ | `/ENCL_B` |
| 33 | D26 | PD11 | `LED_B` | R44 2 k → LED2.3 | blue ✓ | ✓ | `/ENCL_A` |
| 34 | D27 | PG9 | `LED_G` | R25 2 k → LED2.4 | green ✓ | ✓ | button |
| 35 | D28 | PA2 | `TAC_SW5` | SW5 | `sw5.Init(D28)` ✓ | "Tactile switch 2 **SW4** TAC_SW2 D28" (refdes ≠) | button |
| 36/37 | D29/D30 | PB14/PB15 | `/Daisy/USB_OTG_HS_N/P` | U14.4/6 | ✓ | ✓ | same |
| 38 | — | +3V3D | `+3V3` | 47 k pull-ups, U7 VDD, U11 VCC, R3 270 R, R28/R61 10 R, C1 | | | `/+3V3_D` |
| 39 | — | VIN | `DSY_VIN` | R6 3R3 ← +9 V chain, C36 100 µF | | | `/DSY_VIN` |
| 40 | — | DGND | `GND` | | | | |

- **Firmware vs schematic: 30/30 match** (sw1 pair, sw2, sw3, sw4, sw5, fsw_1/2, sd_detect, 6 pots, expression, 4 LED channels, MIDI rx/tx, + SD 6 and USB 2 fixed). `led2.Init(D25, D27, D26)` is (R, G, B) = pins 32, 34, 33 ✓. `sw1.Init(D7, D8)` makes `TOG_SW1_B` the firmware's "left" side (same documented inversion as the Eurorack kit).
- **README vs schematic:** all Seed pin numbers agree. Refdes disagree for the tactile switches and toggle 3 (README SW3/SW4/SW6 vs schematic SW4/SW5/SW3; the Rev4 schematic in the scratchpad clone also has SW1–SW5 with the same net names, so the README refdes match neither revision — PD-P3-08, doc). README signal names `TOG_2_A/B`, `TOG_1`, `TOG_3`, `TAC_SW1/2` are the schematic's `TOG_SW1_A/B`, `TOG_SW2`, `TOG_SW3`, `TAC_SW4/5`. The README's MIDI jack refdes (J11 out, J10 in, J1 thru), audio jacks J2/J4/J3/J5, J6, J8 and VR1–6 all agree.
- **Pin 13 is free** — a Seed 3 Pedal kit could host one extra GPIO (e.g. a card-detect-style input or an I2C bus with pin 12 if SD detect were given up).

## 5. USB-C, SD card detect, power entry
- **USB-C J7:** identical to the Eurorack kit — CC1/CC2 → R1/R2 5k1 → GND (device), VBUS → **U14.5 only** (data-only; the kit is powered from the barrel jack, README "Power: 9V DC barrel jack"), D+/D− A6/B6, A7/B7 → U14 1/3 → 6/4 → Seed 37/36, SBU NC, shell grounded. No USB ID (pin 1 = `TAC_SW4`). = datasheet Fig 1.3.
- **SD card detect:** U7 `CD1` → `SDMMC_DETECT` → A1.12 (D11); no external pull-up — libDaisy `Switch` default `PULLUP` + `POLARITY_INVERTED` (`sd_detect.Pressed()` = "SD Card Detected"), so the switch is read as closed-to-ground; the socket's other contact is its grounded shell (MP1–4; TF-01A datasheet not fetched, switch sense inferred from the firmware polarity). 76.3 mm, 3 vias, **0.202 mm** — the only 0.2 mm trace on the board (Pass 5).
- **Power entry (connectivity only; Pass 2 owns the values):** J8 barrel (pin 1 GND, pin 2 → C20 100 nF + FB10) → FB10 → FB4 → FB5 (three beads in series) → D5 NSR1020 (C21 100 µF, C22 100 nF) → FB9 → `+9V` → R30 3R3 → C41 node → R6 3R3 → `DSY_VIN` (C36 100 µF) = datasheet Fig 1.1; `+9V → R48 3R3 → C14 → … → +9V_A` for the audio op-amps; U2 LP2985-5.0 → `+5V` → FB1 → `+5V_A` (MCP6002, expression ring). Single-supply audio with `AREF_AUDIO_IN_BIAS` (U1A follower of a 10 k/10 k divider of `+9V_A`).

## 6. MIDI (3 × 5-pin DIN, `57PC5F`)
| Jack | Pin 4 | Pin 5 | Pin 2 / shell | Check |
|---|---|---|---|---|
| J10 IN | `MIDI_IN_4` → R4 220 R → U11.1 (anode) | `MIDI_IN_5` → U11.2 (cathode) | pin 2 → C34 100 nF → GND; GND1/GND2 → C47 100 nF → GND (AC-coupled, datasheet Fig 7.2) | DIN 4 = source, 5 = sink ✓; **no antiparallel diode** across U11's LED |
| J11 OUT | ← R61 10 R ← `+3V3` | ← R59 10 R ← `MIDI_TX` (pin 14) | GND | ✓ datasheet Fig 7.4 (10 R / 10 R) |
| J1 THRU | ← R28 10 R ← `+3V3` | ← R29 10 R ← `MIDI_RX` (opto output) | GND | ✓ Fig 7.6 |
- `MIDI_RX` = U11.4 with R3 270 R pull-up; C1 100 nF on U11.6. The opto LED has only the 220 R in series; a reversed or hot-plugged source applies the loop's open-circuit voltage to the LED in reverse (H11L1 LED V_R rating ≈ 3 V, **from memory**). The Pod (D5), the Eurorack kit (D3) and Trey's rev 3 (D1) all fit an NSR1020 for this; this kit follows the datasheet's Fig 7.1, which has none. JUDGMENT PD-P3-09.
- libDaisy default MIDI pins (PB7/PB6) = the kit's; pin 14 carries only `MIDI_TX`.

## 7. Other connectivity facts
- **LEDs** common cathode (LED1.1, LED2.2 on GND); GPIO → R43 **1 k** (mono red), R40/R25/R44 **2 k** (RGB) → anodes; `invert = false` ✓.
- **Pots** VR1–6 (P-10K-B-R): pin 1 GND, pin 3 `+3V3_A`, wipers straight to pins 22–27 (no mux, no RC). `+3V3_A` (pin 21) feeds **only** the six pots — no other analogue rail consumer (the audio op-amps run on `+9V_A`, the expression follower on `+5V_A`).
- **Expression (J6 TRS):** ring → R46 100 R → `+5V_A` (supplies the pedal's pot), tip → `EXPRESSION_IN_EXT` → U1B MCP6002 follower (+ input; R18 1 M to GND), `TN` → R68 10 k → GND; follower output → R17 10 k → `ADC_EXPRESSION` with R60 20 k + C46 10 nF to GND → pin 28. **Max ADC voltage = V_OH(5 V rail) × 20/30 ≈ 3.3 V** on a non-5 V-tolerant pin (datasheet l.135 "Pin 28 D21 PC4"): the datasheet's own Fig 4.5 values (10 k / 20 k / 10 nF / 1 M, l.1762). With 1 % resistors the worst case is 5.0 × 20.2/30.1 = 3.36 V, inside V_DD + 0.3 V (STM32 abs-max for non-FT pins, **from memory**) but above the 3.3 V operating range of datasheet Table 3 (l.280). ZERO-MARGIN PD-P3-07.
- **Footswitches** FSW_1/2 (M12 SPST): pin 1 GND, pin 2 → GPIO; no pull-up, no RC (internal PULLUP). **Toggles** SW1 (ON-OFF-ON, pins 1/3 → GPIO, pin 2 GND), SW2/SW3 (ON-ON as SPST, pin 3 NC).
- **Audio jacks** J2/J4 inputs: tip → C29/C7 10 µF (AC-coupled) → 1 M to `AREF_AUDIO_IN_BIAS` (≈ 4.5 V) = 1 MΩ input impedance ✓ README; outputs J3/J5: 100 R + 10 µF + 10 k bleed = 100 Ω ✓.

## Findings (Seed3 Pedal Dev Kit Rev3, Pass 3)
| ID | Class | Status | Finding | Evidence | Source |
|---|---|---|---|---|---|
| PD-P3-01 | PASS | confirmed | Schematic ↔ PCB fully consistent: 150 ↔ 150 parts, 460 pad keys with 0 real differences, 132 copper nets (+4 pad-less hole nets), 0 duplicate refs, 0 DNP, 0 unconnected DRC items, every net one copper island | §1 | `sch_pcb_diff.py`, `drc.json` |
| PD-P3-02 | PASS | confirmed | 33 single-pin nets, all NC-flagged and intentional (free pin 13, holes, DIN 1/3, unused ¼" jack contacts, SBU, J8.3, toggle pin 3, U11.3); the used tip-normal contacts ground unplugged inputs through 10 k | §2 | `netlist_parse.py` |
| PD-P3-03 | PASS (ERC) | confirmed | 0 ERC errors; 7 library-path warnings; 2 `pin_to_pin` warnings are PWR_FLAGs on the USBLC6's bidirectional-typed GND/VBUS pins. 10 PWR_FLAGs present — the hygiene the Eurorack kit and rev 3 (R3-P3-06) lack | §3 | `erc.json` |
| PD-P3-04 | PASS (design fact) | confirmed | USB-C: CC 5k1 device port, VBUS → USBLC6 clamp only (data-only, 9 V barrel powered), no USB ID, SBU NC, shell grounded; same block as the Eurorack kit | §5 | datasheet Fig 1.3 |
| PD-P3-05 | PASS | confirmed | **SD card detect wired**: U7 `CD1` → pin 12 (D11), libDaisy `sd_detect` Switch with internal pull-up, inverted polarity; 76 mm / 3 vias / 0.2 mm. The only board in the reference set (Pod, Eurorack kit, rev 3 F-022) that can read card presence | §5 | `pedal_devkit.cpp` |
| PD-P3-06 | PASS | confirmed | Seed 3 pin table: 39/40 pins on a net, pin 13 (D12) free and NC-flagged, no expansion header; 30/30 firmware assignments match the schematic | §4 | datasheet l.213–262; libDaisy |
| PD-P3-07 | ZERO-MARGIN | confirmed (values) / abs-max from memory | Expression ADC on 3.3 V-only pin 28 (PC4) fed by a 5 V-rail MCP6002 follower through 10 k / 20 k: full-scale = 3.33 V nominal, 3.36 V worst case at 1 % — at/above the 3.3 V operating range, inside V_DD + 0.3 V abs-max (from memory). This is the datasheet's Fig 4.5 circuit verbatim; a 22 k lower leg or 3.3 V_A reference would give margin | §7 | datasheet l.132–137, l.1762; README "Expression input TRS" |
| PD-P3-08 | info (doc) | confirmed | README switch refdes (`SW3`, `SW4`, `SW6`) ≠ schematic (`SW4`, `SW5`, `SW3`) in both Rev3 and Rev4 files; pins agree. README omits the SD-detect line (D11) that the firmware uses | §4 | README; Rev4 clone grep |
| PD-P3-09 | JUDGMENT | confirmed | MIDI IN opto LED has no antiparallel diode (U11.1 net = R4 only) — the Pod (D5), the Eurorack kit (D3) and rev 3 (D1) all fit an NSR1020; the Seed 3 datasheet Fig 7.1 omits it. Reverse-polarity / hot-plug protection of the H11L1 LED rests on the 220 R alone (H11L1 V_R from memory) | §6 | netlist; datasheet l.1883 |
| PD-P3-10 | PASS | confirmed | DIN MIDI pinout correct on all three jacks (4 source / 5 sink), 270 R pull-up on the opto output, IN sleeve + shell AC-coupled (100 nF), OUT/THRU 10 R/10 R per datasheet (vs rev 3's 10/33, see EU-P3-10) | §6 | datasheet l.1930–1962 |
| PD-P3-11 | PASS | confirmed | LEDs common cathode (1 k mono / 2 k RGB), `invert = false`; pots direct to ADC pins 22–27 on `+3V3_A` (that rail's only load); footswitches/toggles to GND with internal pull-ups; 3.3 V-only pins 24/25/29/30 bounded by the pots and switches | §7 | netlist; libDaisy |
| PD-P3-12 | PASS | confirmed | Audio I/O: 1 MΩ AC-coupled inputs biased to `AREF_AUDIO_IN_BIAS`, 100 Ω outputs with 10 k bleed, single-supply OPA1652 on `+9V_A`; expression ring supplies +5 V_A through 100 R; unplugged inputs grounded through 10 k by the tip-normal contact | §2, §7 | netlist |
| PD-P3-13 | PASS | confirmed | Single ground (97 nodes), mounting holes isolated, USB shell and DIN shells grounded (J10's via 100 nF) | §1 | netlist |
