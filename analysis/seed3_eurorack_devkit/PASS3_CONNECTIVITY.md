# Seed3 Eurorack Dev Kit Rev3 — Pass 3: Connectivity / sch↔pcb / ERC
**Date:** 2026-10-12 · **Truth checked:** `reference/electrosmith/seed3_eurorack_devkit/Rev3/Seed3-DevKit-Eurorack-Rev3.kicad_sch` (root + sub-sheets `_1` Daisy, `_2` Peripherals, `_4` Power; `_3` is an empty 177-byte file not referenced by the root) vs `Seed3-DevKit-Eurorack-Rev3.kicad_pcb` (KiCad 10, format 20260206). Netlist/ERC/DRC exported with KiCad 10.0.7 into `kicad_out/euro3/` (`netlist.net`, `erc.json`, `drc.json`: **0 unconnected items, 0 schematic-parity items**); PCB connectivity via the `pcbnew` Python module 10.0.7. The production Gerbers (`Rev3/production/`, 2026-06-18) are the fab truth but were not needed for this pass (the `.kicad_pcb` carries the filled GND pours, 15,694 mm² F.Cu + 15,977 mm² B.Cu).
**Scripts** (`analysis/seed3_eurorack_devkit/scripts/`, run with `python3 -I`; the rev-3 pass-3/5 scripts, unchanged except where noted): `netlist_parse.py`, `pcb_export.py` (pcbnew), `sch_pcb_diff.py` (tail generalised: Seed pin table + per-ref tables from argv), `sch_inventory.py` (per sub-sheet), `chain_walk.py` (new: walks a signal path through 2-pin passives), `sd_budget.py` (new, Pass 5), `net_geometry.py` (`ALL` option), `proximity.py`, `prox_lists.py` (new).
**Threshold / reference sources:** Seed 3 datasheet v1.0 `reference/electrosmith/daisy_seed3/Daisy_Seed3_datasheet.txt` (pin table l.213–262, 3.3 V-only pins l.130–137, USB l.446, MIDI l.1883–1962, SD l.1787–1812, DAC l.1830); upstream README `README_upstream.md` (Hardware Reference pin map); libDaisy `src/eurorack_devkit.cpp/.h`, `src/daisy_seed.h`, `src/hid/midi.cpp`, `src/hid/midi.h`, `src/hid/switch3.h`, `src/hid/switch.h`, `src/hid/gatein.cpp`, `src/hid/led.cpp`, `src/hid/ctrl.cpp` (raw.githubusercontent.com `electro-smith/libDaisy@master`, fetched 2026-10-12, saved in the session scratchpad `kits_p3_5/dl/`); the kit repos (`daisyaudio/ES-Seed3-DevKit-Eurorack`, clone in scratchpad) contain **no firmware** — the board support lives in libDaisy. STM32H7 absolute-maximum figures, BJT V_BE and the MMA CA-033 3.3 V MIDI values are quoted **from memory (st.com / midi.org not fetched)** where used.

## Headline
1. **Schematic ↔ PCB fully consistent.** 139 components ↔ 139 footprints, 440 (part, pad) keys compared, **0 real differences** (the 19 "differences" are pad-less fiducials FD1–3 and the pot `CHASSIS1/2` pads that have no symbol pin), 125 nets in both, 0 duplicate refdes, 0 DNP parts, 0 value/footprint mismatches.
2. **ERC: 45 warnings are all library-path noise, the 5 errors are all missing-PWR_FLAG false positives.** The project contains no `PWR_FLAG` at all (`grep -c power:PWR_FLAG` = 0 on every sheet), so `+12V`, `-12V`, `GND`, `DSY_VIN` and `VBUS` — each fed through a diode / bead / 3R3 chain from the passive-typed power header or the USB receptacle — are reported as "not driven". Each chain was walked (`chain_walk.py`, §3); no wiring fault.
3. **All 31 Seed 3 GPIO are consumed; no expansion header exists.** Pin 1 (USB ID) is a tactile switch, so the kit's USB-C is a **CC-pull-down device port, data-only** (VBUS reaches only the USBLC6 clamp) — the same topology as the Pod and as Trey's rev 3. SD card detect is **not wired** (U7 CD1 carries an NC flag).
4. **Firmware pin map (libDaisy `eurorack_devkit.cpp`) matches the schematic on every pin**, including the toggle whose code comment says "wired opposite from expected" (it is: `sw3.Init(D7, D27)` with D7 = `TOG_SW3_B`, D27 = `TOG_SW3_A`). The README pin map also matches; only its signal names differ from the schematic's (`TOG_2_A/B`, `TOG_1` vs `TOG_SW3_A/B`, `TOG_SW4`). Two firmware cosmetics found in passing (§4).
5. **The five 3.3 V-only pins (24, 25, 28, 29, 30, datasheet l.132–137) are all bounded by design:** 24/25 are CV ADC inputs driven by an MCP6004 that runs on `+3V3_A`, 28 is a gate input pulled to `+3V3` through 10 k, 29/30 are the DAC outputs into TL072 inputs.
6. **Topologies Trey's rev 3 shares with this kit:** 47 k SD pull-ups on DAT/CMD only; USBLC6-2 with VBUS as clamp reference; 220 Ω + H11L1 + antiparallel diode + 270 Ω MIDI IN; MIDI OUT from pin 14 (`USART1_TX`). Where the kit differs: MIDI OUT/THRU use **10 Ω / 10 Ω** (datasheet l.1930–1931) where rev 3 uses 10 Ω / 33 Ω.

## 1. Schematic ↔ PCB netlist diff (`sch_pcb_diff.py euro/netlist.json euro/pcb.json`)
| Check | Result |
|---|---|
| Components (netlist) / footprints (pcb) | 139 / 139; only-in-sch = ∅, only-in-pcb = ∅ |
| Hierarchy | root `Seed3-DevKit-Eurorack-Rev3.kicad_sch` → `Daisy` (`_1`, 119 instances), `Peripherals` (`_2`, 71), `Power` (`_4`, 24); 214 placed symbol instances of which 65 power symbols; `_3.kicad_sch` exists on disk (177 bytes) but is not instantiated |
| Duplicate refdes / unannotated | none / none (`sch_inventory.py` per sheet) |
| DNP / not-in-BOM | DNP: **none**. `in_bom=no`: FD1–3 (fiducials), H1–4 (M3 slots), LOGO1 (OSHW), QR1 — all pad-less or mechanical |
| Value / footprint mismatch | none |
| Pad-level (part, pad) → net | 440 keys; 19 differ, all `<no pin in sch> → None`: FD1–3 (NPTH, pad number ''), VR1–8 `CHASSIS1/2` (pot body tabs, no symbol pin, no net) → **0 real differences** |
| Nets | 125 = 125 (names identical incl. the `/Daisy/…` sheet-local ones); PCB nets with 1 pad: none; nets with pads but no copper: none |
| `pcbnew` connectivity | `drc.json`: `unconnected_items = 0`, `schematic_parity = []`; `net_geometry.py`: every non-GND net is one copper island, `stubs=[]` on every net |
| GND | one net: `A1.20` AGND + `A1.40` DGND tied; jack sleeves, P1 GND1–6, J7 shell S1–S4 + A1/B12 + B1/A12, U7 pin 6 + MP1–4, LED cathodes, switch returns, 85 nodes in total |

Three sheets' worth of hierarchical labels reconcile: the `/Daisy/` prefixed nets (`CODEC_*`, `CV_n_ADC`, `DAC_CV_n`, `MUX_CTRL_*`, `POT_MUX`, `USB_*`, `+5V_USB`) are local labels on the Daisy sheet whose far ends are on the same sheet; global labels (`SDMMC_*`, `MIDI_*`, `LED_*`, `TAC_*`, `TOG_*`, `GPIO_GATEIN_*`, `POT_n`) cross sheets and resolve to one net each in both files.

## 2. Single-pin nets and open pins
`netlist_parse.py`: 21 single-node nets, **every one an `unconnected-…` net carrying a no-connect flag** (pintype `…+no_connect`):
| Pins | Disposition |
|---|---|
| H1–H4 pad 1 | M3 slot pads, isolated (not grounded) — same as the Pod (DP-P3-02) |
| J7 A8/B8 (SBU1/2) | USB 2.0-only receptacle, correct |
| `NORM` of J_AUDIO_IN_L1, J_AUDIO_OUT_L1/R1, J_CV_IN_1–4, J_CV_OUT_1/2, J_GATE_IN_1/2 (11) | jack switch contacts unused; **the one used contact is `J_AUDIO_IN_R1.NORM` ↔ `J_AUDIO_IN_L1.TIP`** = the input-R-normalled-to-L feature the README describes |
| SW4 pin 3 | ON-ON toggle used as SPST (pin 1 → GPIO, pin 2 → GND) |
| U3 pin 3 | LM4040 NC |
| U7 CD1 | **SD card detect not wired** (EU-P3-05) |
| U11 pin 3 | H11L1 NC |

## 3. ERC disposition (`kicad_out/euro3/erc.json`, 50 items)
| Count | Type | Items | Disposition |
|---|---|---|---|
| 21 | `footprint_link_issues` (warning) | 11 `EURO_JACK` → `Electrosmith-Interface:S_JACK`, 3 `STEREO_JACK_3.5MM`, P1 `EURO_PWR_HEADER_LOCK`, H1–4 + QR1 in lib `shnsly` | the designer's libraries (`/Users/stephenhensley/Developer/repos/ES_Eagle_L…`, `shnsly`) are not in this session's lib tables; footprints are embedded in the board (139/139 present) → noise |
| 17 | `lib_symbol_issues` (warning) | same symbols | same cause → noise |
| 7 | `lib_symbol_mismatch` (warning) | J7 `USB4110GFA`, U7 `TF-01A`, SW1/SW2 `TAC_SWITCH_PTH_SILK`, LED2 `LED`, Q1/Q2 `MMBT3904` | embedded copy differs from the stock library copy (cosmetic/graphic edits); pin→net checked by the diff above → noise |
| 1 | `power_pin_not_driven` A1 pin 39 `VIN` (error) | net `DSY_VIN` | walked: `P1.POS → FB2 → D1 (NSR1020) → +12V → R5 3R3 → C46 100 µF node → R9 3R3 → DSY_VIN (C49 100 µF) → A1.39` = datasheet Fig 1.2 (l.420–445) exactly. Every element is passive-typed, no PWR_FLAG → **false positive** |
| 1 | `power_pin_not_driven` #GND01 (error) | `GND` | GND enters only through P1 (passive pins) and the Seed's AGND/DGND (power-in) → no PWR_FLAG → **false positive** |
| 1 | `power_pin_not_driven` J7 A4/B9 `VBUS` (error) | `/Daisy/+5V_USB` | the net is J7 VBUS ↔ U14.5 only; **genuinely undriven on the board** (VBUS comes from the host); the kit is powered from P1 (README "The module is powered from the Eurorack power header (P1), not from USB") → false positive, design intent |
| 2 | `power_pin_not_driven` #PWR01 `+12V`, #PWR02 `-12V` (error) | Power sheet | fed from P1 through FB2/D1 and FB3/D2 (reverse-protection diodes, README "Reverse polarity protection: Yes") → **false positive** |

Net effect: 0 wiring errors. The Pedal kit, by contrast, carries 10 PWR_FLAGs and shows none of these (PD-P3-03).

## 4. Seed 3 pin usage (all 40 pins) and firmware map
Physical pin ↔ D-number from the datasheet Table 2 (l.213–262): **pin = D+1 for pins 1–15, pin = D+7 for pins 22–37** (identical to the Seed Rev 7 relation used in the Pod/rev-3 reports; datasheet l.24 "pin-to-pin compatible with the Seed pinout"). The kit's symbol is the stock `Electrosmith_Daisy_Seed_Rev4` (footprint `Module:Electrosmith_Daisy_Seed`), i.e. a Seed symbol is used for a Seed 3 — valid because of that compatibility; its pin names are what the netlist's `pinfunction` column shows. Firmware column = `eurorack_devkit.cpp` `Hardware::Init()` / `daisy_seed.h`. 3V3-only pins per datasheet l.132–137 are marked ★.

| Pin | Dn | STM32 | Kit net | Other end | Firmware (libDaisy) | Trey rev 3 |
|---|---|---|---|---|---|---|
| 1 | D0 | PB12 (USB_HS_ID) | `TAC_SW1` | SW1 (to GND) | `sw1.Init(D0)` ✓ | `/RES_SPI` (OLED reset) |
| 2–7 | D1–D6 | PC11/PC10/PC9/PC8/PD2/PC12 | `SDMMC_D3/D2/D1/D0/CMD/CK` | U7 + 47 k R51/R50/R54/R53/R52 (none on CK) | SDMMC1 fixed ✓ | same |
| 8 | D7 | PG10 (SPI1_NSS) | `TOG_SW3_B` | SW3 pin 3 | `sw3.Init(D7, D27)` pin a ✓ | `/CS_SPI` |
| 9 | D8 | PG11 (SPI1_SCK) | `LED_B` | R44 2 k → LED1.3 | `led1.Init(D9, D28, D8, false)` blue ✓ | `/SCLK_SPI` |
| 10 | D9 | PB4 (SPI1_MISO) | `LED_R` | R40 2 k → LED1.1 | led1 red ✓ | `/TAC_SHIFT_R` |
| 11 | D10 | PB5 (SPI1_MOSI) | `GPIO_GATEIN_1` | R23 100 R ← Q1 collector | `gate_in1.Init(D10)` ✓ | `/SD_IN_SPI` |
| 12 | D11 | PB8 (I2C1_SCL) | `LED_MONO_1` | R43 2 k → LED2 | `led2.Init(D11, false)` ✓ | `/ENCR_A` |
| 13 | D12 | PB9 (I2C1_SDA) | `TOG_SW4` | SW4 pin 1 | `sw4.Init(D12)` ✓ | `/ENCR_B` |
| 14 | D13 | PB6 (USART1_TX) | `MIDI_TX` | R59 10 R → MIDI OUT tip | `midi tx = D13` ✓ | `/USART1_TX` (MIDI OUT) |
| 15 | D14 | PB7 (USART1_RX) | `MIDI_RX` | U11.4, R3 270 R, R29 (thru) | `midi rx = D14` ✓ | `/USART1_RX` |
| 16/17 | — | audio in L/R | `/Daisy/CODEC_IN_L/R` | R63/R66 100 R ← TL072 U1 | audio ✓ | same (direct from jacks) |
| 18/19 | — | audio out L/R | `/Daisy/CODEC_OUT_L/R` | R67/R68 10 k → TL072 U15 | audio ✓ | same |
| 20 | — | AGND | `GND` | | | |
| 21 | — | +3V3A (out) | `+3V3_A` | VR1–8 ends, U12 VDD, U2 VDD, C6/C19 | | `/+3V3_A` |
| 22 | D15 | PC0 (ADC0) | `/Daisy/POT_MUX` | U12 CD4051 COM | `InitMux(D15, 8, D24, D25, D26)` ✓ | `/ENCL_CLICK` |
| 23 | D16 | PA3 (ADC1) | `/Daisy/CV_3_ADC` | U2C out + C16 | `adc[3]=D16` → `cv[2]` = CV 3 ✓ | `/TAC_SHIFT_L` |
| 24 ★ | D17 | PB1 (ADC2) | `/Daisy/CV_2_ADC` | U2B out + C15 | `adc[2]=D17` → CV 2 ✓ | LED line |
| 25 ★ | D18 | PA7 (ADC3) | `/Daisy/CV_1_ADC` | U2A out + C14 | `adc[1]=D18` → CV 1 ✓ | LED line |
| 26 | D19 | PA6 (ADC4) | `/Daisy/CV_4_ADC` | U2D out + C18 | `adc[4]=D19` → CV 4 ✓ | LED line |
| 27 | D20 | PC1 (ADC5) | `TAC_SW2` | SW2 | `sw2.Init(D20)` ✓ | LED line |
| 28 ★ | D21 | PC4 (ADC6) | `GPIO_GATEIN_2` | R31 100 R ← Q2 collector (R30 10 k → +3V3) | `gate_in2.Init(D21)` ✓ | `/DC_SPI` |
| 29 ★ | D22 | PA5 (DAC1_OUT2) | `/Daisy/DAC_CV_2` | U13.5 (+ input) | DAC ch 2 = CV Out 2 ✓ | `/ENCR_CLICK` |
| 30 ★ | D23 | PA4 (DAC1_OUT1) | `/Daisy/DAC_CV_1` | U13.3 (+ input) | DAC ch 1 = CV Out 1 ✓ | LED line |
| 31 | D24 | PA1 | `/Daisy/MUX_CTRL_A` | U12.11 (A) | mux A ✓ | LED line |
| 32 | D25 | PA0 | `/Daisy/MUX_CTRL_B` | U12.10 (B) | mux B ✓ | `/ENCL_B` |
| 33 | D26 | PD11 | `/Daisy/MUX_CTRL_C` | U12.9 (C) | mux C ✓ | `/ENCL_A` |
| 34 | D27 | PG9 | `TOG_SW3_A` | SW3 pin 1 | `sw3` pin b ✓ | button |
| 35 | D28 | PA2 | `LED_G` | R25 2 k → LED1.4 | led1 green ✓ | button |
| 36/37 | D29/D30 | PB14/PB15 (USB_HS D−/D+) | `/Daisy/USB_OTG_HS_N/P` | U14.4/6 | USB ✓ | same |
| 38 | — | +3V3D (out) | `+3V3` | 47 k pull-ups, U7 VDD, U11 VCC, R3 270 R, R6/R10 10 R (MIDI out/thru source), R19/R30 10 k, C1 | | `/+3V3_D` |
| 39 | — | VIN | `DSY_VIN` | R9 3R3 ← +12 V chain, C49 100 µF | | `/DSY_VIN` (9 V) |
| 40 | — | DGND | `GND` | | | |

- **Firmware vs schematic: 24 configurable assignments + 8 fixed-function pins, 32/32 match.** The order inside `InitMux(D15, 8, D24, D25, D26)` → A/B/C matches U12 pins 11/10/9 ↔ pins 31/32/33; `adc_config[1..4]` = D18, D17, D16, D19 so `cv[0..3]` = CV 1…4 in jack order; `led1.Init(D9, D28, D8)` = R, G, B ↔ pins 10, 35, 9.
- **Toggle "wired opposite from expected":** `Switch3::Read()` returns `POS_UP/LEFT` when pin *a* is low; the code passes `D7` (= `TOG_SW3_B`, SW3 pin 3) as pin a, so the firmware's LEFT is the schematic's "B" side. Consistent, documented in code, no hardware issue.
- **README vs schematic:** every Seed pin number in the README's Hardware Reference agrees with the netlist. Signal names differ (`TOG_2_A/TOG_2_B` = `TOG_SW3_A/B`, `TOG_1` = `TOG_SW4`); jack refdes (`J_CV_IN_1` …) agree.
- **Firmware cosmetics (not hardware):** `eurorack_devkit.cpp` `PrintAllControls()` prints the heading "Pedal DevKit Controls:" and its switch line has three `%s` for four arguments (`sw4` is passed but never printed). `sw3` (Switch3) has no `Debounce()`, by design.
- **Free pins: none.** Trey's rev 3 and this kit therefore cannot share a pin plan: the kit spends pins 8–13 (Trey's SPI1 + encoder-R pins) on a toggle, three LED channels, a gate and the mono LED.

## 5. USB-C, SD card detect, power entry
- **USB-C J7 (GCT USB4110GFA, 2.0-only receptacle):** CC1/CC2 → R1/R2 5k1 → GND (UFP, 5.1 k "Rd"); VBUS pads A4/B9 + B4/A9 → `/Daisy/+5V_USB` → **U14.5 only** (USBLC6-2SC6 VBUS clamp reference); D+ A6/B6 → U14.1, D− A7/B7 → U14.3, pass-through to U14.6/4 → Seed pins 37/36; SBU NC; shell S1–S4 on GND. **No USB ID** (Seed pin 1 is `TAC_SW1`), so the OTG_HS port is a device port by hardware; README calls it "the Seed3's external USB peripheral". This is datasheet Fig 1.3 (l.446) verbatim. **Data-only USB on a separately powered board = the Pod and the rev-3 topology** (DP-P3-05).
- **SD card detect:** U7 (TF-01A) `CD1` pad carries a no-connect flag; the socket's shell pads MP1–4 are on GND. No Seed pin is free to read it (§4). The Pedal kit does wire CD1 to D11 (PD-P3-05).
- **Power entry (for Pass 2, connectivity only):** P1 10-pin header POS1/POS2 → FB2 → D1 → `+12V`; NEG1/NEG2 → FB3 → D2 → `-12V`; `+12V → R5 3R3 → C46 100 µF → R9 3R3 → C49 100 µF → DSY_VIN` (datasheet Fig 1.2). `-10V_REF` for the CV offset comes from U3 LM4040DBZ-10 fed by R32 2 k from −12 V.

## 6. MIDI (3 × 3.5 mm TRS, `STEREO_JACK_3.5MM`)
| Jack | TIP | RING | SLEEVE | Type |
|---|---|---|---|---|
| J_MIDI_IN1 | `MIDI_IN_5` → U11.2 (opto cathode) ‖ D3 anode | `MIDI_IN_4` → R4 220 R → U11.1 (anode) ‖ D3 cathode | → C47 100 nF → GND (AC-coupled sleeve, datasheet Fig 7.3) | tip = DIN 5 (sink), ring = DIN 4 (source) = **TRS Type A** (RP-054 mapping from memory) |
| J_MIDI_OUT1 | ← R59 10 R ← `MIDI_TX` (pin 14) | ← R10 10 R ← `+3V3` | GND | Type A |
| J_MIDI_THRU1 | ← R29 10 R ← `MIDI_RX` (U11 output) | ← R6 10 R ← `+3V3` | GND | Type A, hardware thru from the opto output (datasheet l.1959–1962) |
- `MIDI_RX` = U11.4 with R3 270 R pull-up to `+3V3`; U11.6 VCC decoupled by C1 100 nF. Identical receiver to the Pod and to Trey's rev 3 (R5 220 Ω, U1 H11L1, D1, R6 270 Ω).
- **Output series values 10 Ω / 10 Ω** follow the Seed 3 datasheet (l.1930–1931 "through a 10Ω resistor … to 3.3V through a 10Ω resistor"). The MMA 3.3 V recommendation (CA-033, **from memory**) is 10 Ω from TX and 33 Ω from Vcc; Trey's rev 3 uses that pair. With 10/10 the loop current into a standard 220 Ω receiver is ≈ (3.3 − V_LED)/240 Ω ≈ 8–9 mA instead of ≈ 6–7 mA — within what every opto receiver accepts; JUDGMENT only (EU-P3-10).
- libDaisy default `MidiUartTransport::Config` is still `rx = PB7, tx = PB6` (`midi.cpp` l.10–17); `eurorack_devkit.cpp` sets the same pins explicitly, `mode = TX_RX` (`midi.h` l.71). No conflict: pin 14 carries nothing but `MIDI_TX` (contrast the Pod's DP-P3-08).

## 7. Other connectivity facts
- **LEDs** are **common-cathode** (`LED_RKBG` pin 2 and LED2 pin 1 on GND) with the GPIO sourcing through 2 k (R40/R25/R44, R43) → `led.Init(…, invert = false)` ✓. Opposite of the Pod (common anode, sink) and of Trey's rev 3 (NPN low-side from 9 V).
- **Pots** VR1–8 (P-10K-B-R, linear): pin 1 GND, pin 3 `+3V3_A`, wiper → CD4051 U12 channel (order: VR1 → X0 pin 13, VR2 → X1 pin 14, VR3 → X2 pin 15, VR4 → X3 pin 12, VR5 → X4 pin 1, VR6 → X5 pin 5, VR7 → X6 pin 2, VR8 → X7 pin 4) → COM → pin 22; U12 VDD = `+3V3_A`, VEE/VSS/INH (6/7/8) = GND. The README's `MUX_CH_0…7` = VR1…8 order is the X0…X7 order, confirmed.
- **CV inputs** (U2 MCP6004 on `+3V3_A`): jack → 100 k → inverting node; 33 k ‖ 1 nF feedback; 200 k from `-10V_REF`. Transfer −0.33·V_in + 1.65 V → **±5 V in = 3.3 … 0 V at the ADC (inverted)**; libDaisy `InitBipolarCv` sets `invert_ = true`, `scale 2`, `offset 0.5` ✓ consistent. Because the op-amp runs on `+3V3_A` the 3.3 V-only pins 24/25 can never see more than that rail.
- **Gate inputs:** jack → R17/R24 100 k → MMBT3904 base, R18/R28 1 M base–GND; collector R19/R30 10 k → `+3V3`, R23/R31 100 R → GPIO. Inverting → `GateIn::Init(pin, invert = true)` default ✓. Threshold ≈ V_BE·(1.1 M/1 M) ≈ 0.7 V at the jack (V_BE ≈ 0.65 V **from memory**); the README states "+0.4 V" — the README figure does not follow from the schematic values (EU-P3-11, JUDGMENT).
- **CV outputs:** DAC pins → U13 TL072 non-inverting, gain 1 + 62 k/120 k = 1.517 → 0–3.3 V → **0–5.0 V** ✓ README; R55/R60 100 R to the jacks. Firmware `DacHandle` with `buff_state = DISABLED` (unbuffered DAC output into a JFET-input TL072 — fine).
- **Audio:** in L/R: jack → 100 k → U1 TL072 inverting (10 k ‖ 330 pF) → 100 R → Seed (gain −0.1, 100 kΩ input impedance ✓ README); out L/R: Seed → 10 k → U15 inverting (100 k ‖ 33 pF) → 100 R → jack (gain −10, 100 Ω output ✓); R normalled to L ✓. Both ±12 V TL072 stages, so the Seed pins only ever see the divided-down signal on the input and drive a 10 k load on the output.

## Findings (Seed3 Eurorack Dev Kit Rev3, Pass 3)
| ID | Class | Status | Finding | Evidence | Source |
|---|---|---|---|---|---|
| EU-P3-01 | PASS | confirmed | Schematic ↔ PCB fully consistent: 139 ↔ 139 parts, 440 pad keys with 0 real net differences, 125 nets both sides, 0 duplicate refs, 0 DNP, 0 unconnected DRC items, every net a single copper island | §1 | `sch_pcb_diff.py`, `net_geometry.py`, `drc.json` |
| EU-P3-02 | PASS | confirmed | 21 single-pin nets, all NC-flagged and intentional (holes, SBU, 11 unused jack switch contacts, SW4.3, U3.3, U7.CD1, U11.3); the one used switch contact implements the R-normalled-to-L audio input | §2 | `netlist_parse.py` |
| EU-P3-03 | JUDGMENT (ERC hygiene) | confirmed | 5 `power_pin_not_driven` errors = no PWR_FLAG anywhere in the project (`+12V`, `-12V`, `GND`, `DSY_VIN`, `VBUS`); each chain walked and correct; 45 warnings are the designer's private library paths. Same hygiene gap as Trey's rev 3 (R3-P3-06, 4 missing PWR_FLAGs) | §3 | `erc.json`, `chain_walk.py` |
| EU-P3-04 | PASS (design fact) | confirmed | USB-C: CC1/CC2 5k1 to GND (device), VBUS → USBLC6 clamp only (data-only, board powered from P1), no USB ID (pin 1 = `TAC_SW1`), SBU NC, shell grounded = datasheet Fig 1.3 | §5 | datasheet l.446; README |
| EU-P3-05 | JUDGMENT | confirmed | SD card detect not wired (U7 `CD1` NC) and no Seed pin is free to take it; the Pedal kit wires CD to D11 — the Eurorack kit (like the Pod and Trey's rev 3, F-022) cannot detect card presence | §5 | netlist |
| EU-P3-06 | PASS | confirmed | Seed 3 pin table: all 40 pins on a net, 31/31 GPIO consumed, 0 free, no expansion header; 3.3 V-only pins 24/25 (MCP6004 on `+3V3_A`), 28 (10 k to `+3V3`), 29/30 (DAC → TL072 +in) all bounded ≤ 3.3 V | §4 | datasheet l.132–137, l.213–262 |
| EU-P3-07 | PASS | confirmed | libDaisy `eurorack_devkit.cpp` pin map matches the schematic 32/32 (24 configurable + SD/USB); mux A/B/C order, CV 1–4 order, R/G/B order and DAC channel ↔ jack all verified; `sw3.Init(D7, D27)` "wired opposite" is a documented, consistent inversion | §4 | libDaisy (fetched 2026-10-12) |
| EU-P3-08 | info | confirmed | README Hardware Reference matches the netlist on every pin number; its signal names `TOG_2_A/B`, `TOG_1` are the schematic's `TOG_SW3_A/B`, `TOG_SW4`. Firmware cosmetics: Eurorack `PrintAllControls()` titled "Pedal DevKit Controls" and drops `sw4` from its format string | §4 | README, libDaisy |
| EU-P3-09 | PASS | confirmed | MIDI: TRS Type A on all three jacks; IN = 220 R + H11L1 + NSR1020 antiparallel + 270 R pull-up, sleeve via 100 nF; OUT/THRU = 10 R/10 R from pin 14 / opto output; pin 14 carries only `MIDI_TX` (no Pod-style click conflict) | §6 | datasheet l.1883–1962; RP-054 from memory |
| EU-P3-10 | JUDGMENT | confirmed | MIDI OUT/THRU source resistors 10 Ω / 10 Ω per the Seed 3 datasheet vs the MMA 3.3 V pair 10 Ω / 33 Ω used by Trey's rev 3; ≈ 8–9 mA loop into a 220 Ω receiver, harmless but non-standard | §6 | datasheet l.1930–1931; CA-033 from memory |
| EU-P3-11 | JUDGMENT (doc) | plausible | Gate-input threshold: 100 k / 1 M BJT stage gives ≈ 0.7 V at the jack (V_BE from memory); README says "+0.4 V" | §7 | netlist values; README |
| EU-P3-12 | PASS | confirmed | LEDs common-cathode, GPIO sources through 2 k, `invert = false` in firmware; pots across GND/`+3V3_A` into a CD4051 whose channel order matches the README; CV in −0.33·V+1.65 V inverted = `InitBipolarCv`; CV out ×1.517 → 0–5 V; audio ×−0.1 in / ×−10 out, 100 k in / 100 Ω out | §7 | netlist values; libDaisy |
| EU-P3-13 | PASS | confirmed | Single ground (AGND + DGND tied, 85 nodes), M3 slots isolated, USB shell grounded (unlike the Pod's floating shell) | §1, §2 | netlist |
