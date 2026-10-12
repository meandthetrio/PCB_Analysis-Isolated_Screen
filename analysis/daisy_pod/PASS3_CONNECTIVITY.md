# Daisy Pod Rev5 — Pass 3: Connectivity / sch↔brd / ERC-equivalent
**Date:** 2026-10-12 · **Truth checked:** `reference/electrosmith/daisy_pod/ES_Daisy_Pod_Rev5.sch` (Eagle 9.6.2, intent) vs `ES_Daisy_Pod_Rev5.brd` (Eagle, source of record for copper), with the KiCad 9.0.9 conversion `daisy_pod/kicad/ES_Daisy_Pod_Rev5.kicad_pcb` used only for `pcbnew` connectivity/geometry and DRC (`kicad_out/pod/drc_asis.json`: **0 unconnected items**). Schematic PDF (`ES_Daisy_Pod_Rev5.pdf`, sheet date 2022-10-27) read via `pdftotext` for the designer notes. No ERC tool exists for Eagle here; the equivalent checks are scripted.
**Scripts** (`analysis/daisy_pod/scripts/`, run with `python3 -I`): `eagle_sch_full.py` (sch → parts with gate/pin→pad map, symbol pin lists, nets with pad numbers), `eagle_brd_netlist.py` (brd → elements, `<signal>/<contactref>` netlist, wire length by layer/width, via count), `sch_brd_diff.py` (three-way sch/brd/KiCad pad-level diff), `erc_equiv.py` (single-pin nets, pins on no net, Seed pin usage, power-net sources, look-alike names), `firmware_pinmap.py` (libDaisy constants vs schematic nets).
**Threshold / reference sources:** libDaisy `src/daisy_pod.cpp`, `src/daisy_seed.h`, `src/hid/midi.cpp`, `src/hid/midi.h`, `src/per/uart.cpp`, `src/hid/encoder.cpp`, `src/hid/switch.h`, `src/hid/led.cpp` (raw.githubusercontent.com, fetched 2026-10-12); Seed Rev7 schematic `reference/electrosmith/daisy_seed/ES_Daisy_Seed_Rev7.pdf` (VIN/VBUS diode-OR); Pod BOM `BOM_ES_Daisy_Pod_Rev5.xlsx` (read from the xlsx XML); STM32H7 I/O absolute-maximum current is quoted **from memory (not fetched — st.com unreachable from this session)** where used.

## Headline
1. **Schematic, Eagle board and KiCad conversion are fully consistent.** 58 packaged schematic parts ↔ 62 board elements (the 4 extras are pad-less logo/branding packages `U$2/U$3/U$4/U$7`); all **192 (part, pad) → net assignments identical** in all three files; 0 duplicate refdes; 0 net renames. The KiCad conversion can be trusted for Pass 5 geometry.
2. **ERC-equivalent is clean.** No single-pin nets; all 40 Seed pins are on a net; every pin on no net is a switch contact, mounting tab or shield that the designer left open on purpose (the schematic carries the note "Leaving USB shield ungrounded"). The only inherited oddity is the SD card-detect pair (SWA open, SWB grounded) — the exact origin of Trey's F-022.
3. **Firmware pin map matches 13/13** libDaisy `DaisyPod` constants plus the 9 fixed-function pins (SD, USB, ID); the physical-pin ↔ `Dn` relation is **pin = D+1 for pins 1–15 and D+7 for pins 22–37**, read from the Seed symbol's own pin names (confirms the rev-3 worker's finding).
4. **One real hardware/firmware conflict (DP-P3-08):** the encoder click sits on Seed pin 14 = D13 = **PB6 = USART1_TX**, and libDaisy's default `MidiUartTransport::Config` claims **PB6 as MIDI TX** in `TX_RX` mode; `DaisyPod::Init()` calls `InitMidi()` after `InitEncoder()`, so PB6 is re-initialised as an alternate-function push-pull output. The switch then shorts an idle-high UART TX to GND when pressed. Trey's rev 3 does not inherit this (clicks on pins 22/29, pin 14 is a real MIDI OUT).
5. **The Pod is powered only through the Seed's own micro-USB.** `VIN` (Seed pin 39) goes nowhere but the DNI header P2.11; the Pod's own micro-AB P5 has VBUS tied only to the TVS (U7.5) — **data-only by design**. Trey's "USB-C data-only" choice is inherited Pod topology, not an oversight.
6. **BOM ≠ schematic on the MIDI polarity jumpers (DP-P3-12):** R78/R84 are `DNI 0R` in the schematic but the published BOM lists all four 0 Ω (R78 R79 R83 R84, qty 4). Fitting all four shorts tip to ring and the opto LED to itself — MIDI IN would be dead. Hand to Pass 4.

## 1. Schematic ↔ board ↔ KiCad netlist diff (`sch_brd_diff.py`)
| Check | Result |
|---|---|
| Schematic parts | 85 = 58 with a package + 27 symbol-only (§2) |
| Board elements | 62 = the 58 packaged parts + `U$2` (TONNE_9X13MM logo), `U$3` (CE mark), `U$4` (DAISY_POD_BRANDING_2), `U$7` (ES_TEXT_3X30MM) — silk/doc-layer packages with no pads, not in the schematic (normal Eagle practice) |
| KiCad footprints | 62, same set as the board |
| Packaged parts only in sch / only in brd | none / only the 4 logos |
| Duplicate refdes | none (sch, brd, KiCad) |
| Value / package mismatch | none; FD1–6 and H1–4 carry no schematic value but the board shows the package name as value — cosmetic |
| Pad-level (part, pad) → net | **192 in each file, 0 differences, 0 renames, 0 merged nets** (sch↔brd, brd↔KiCad, sch↔KiCad). Eagle multi-pad connects (`U4` GND "2 9", `P1` SHIELD "P1 P2 P3 P4", `ENC_1` tabs) expand to one entry per pad |
| Nets | 64 in each file; same names everywhere (`N$nn` auto-names preserved by the KiCad importer) |
| `pcbnew` connectivity | `drc_asis.json`: `unconnected_items = 0`; Pass-5 copper walk: every non-GND net is one island (`net_geometry.py`) |
| GND | one net, 50 schematic nodes (23 GND symbols + 27 part pins incl. `U1.AGND` pin 20 + `U1.GND` pin 40, P1 VSS + SHIELD + SWB, U4 GND + PowerPAD, P5.5); KiCad fill 2,656 mm² F.Cu + 3,261 mm² B.Cu |

**Parser validation:** per-net total wire length from the Eagle `.brd` (`eagle_brd_netlist.py`, independent parser) agrees with the KiCad `pcbnew` export to 0.1 mm on every net (e.g. `SD_D1` 24.16 vs 24.2 mm, `USB_OTG_FS_D+` 59.30 vs 59.3 mm, `ENC_B` 62.84 vs 62.8 mm); pad counts per net identical. The Eagle layer map is 1 = Top (F.Cu), 16 = Bottom (B.Cu).

## 2. Schematic parts with no footprint — disposition
| Parts | Count | What | Disposition |
|---|---|---|---|
| `FRAME1`, `FRAME2` | 2 | A3L-LOC sheet frames | drawing only — OK |
| `GND1…GND74` (Electrosmith-Power / supply1 / SparkFun libs) | 23 | GND symbols, all on the single `GND` net | OK (three libraries' GND symbols mixed — cosmetic) |
| `SUPPLY1`, `SUPPLY2` | 2 | `+3V3_A` supply symbols | OK |
| `FD1–FD6` | 6 | 1 mm fiducials — packaged, no pins on any net | OK (assembly) |
| `H1–H4` | 4 | 3.2 mm mounting pads, `MOUNT` pin on no net | OK — **not grounded** (board hole pads isolated; chassis ground not used) |

## 3. ERC-equivalent (`erc_equiv.py`)
| Check | Result | Disposition |
|---|---|---|
| Nets with a single pin | **none** | — |
| Pins on no net | `J1–J4` NC1/NC2 (jack switch contacts, pads 4/10); `ENC_1` mounting tabs GND1–GND6 (two symbol pins "G"); `P5` CASING1–4 (USB shell); `P1` pin A (`SWA`); `H1–H4` MOUNT | All intentional. Jack switch contacts unused (no insertion detect anywhere). Encoder tabs and USB shell left floating: schematic note "Leaving USB shield ungrounded" (sheet 1, by P5) — a deliberate EMC/ground-loop choice; encoder body therefore also ungrounded (JUDGMENT, cosmetic) |
| Seed pins on a net | **40 / 40** | 9 of them reach only the DNI header P2 (pins 8–13 SPI1/I2C1, 23 `A1`, 29 `A7`, 39 `VIN`) → **8 GPIO are free on an assembled Pod** (D7–D12, D16, D22) |
| `+3V3_A` sources | `U1.+3V3_A` (Seed pin 21, Seed LDO output) → VR_1.3, VR_2.3, U4.VCC, C60, P2.9 | driven ✓ (analogue rail feeds both knob pots and the headphone amp) |
| `+3V3_D` sources | `U1.+3V3_D` (pin 38, Seed buck) → 47 k pull-ups R1–R4/R16, P1.VDD, U15.V + R64 + C11, LED1.A, LED2.A, P2.10 | driven ✓ |
| `VIN` | `U1.V_IN` (pin 39) ↔ `P2.11` **only** | **Not driven on the Pod.** Seed Rev7 sheet: `V_IN → D1 → UNREGULATED_VCC` and `USB VBUS → D2 → UNREGULATED_VCC` (diode-OR, so VIN is an input and does not back-feed P2.11). The assembled Pod is powered solely through the Seed's own micro-USB; P2.11 is an optional external-supply entry |
| `USB_VBUS` | `P5.1` ↔ `U7.VBUS` only | Pod's micro-AB is **data-only**; VBUS serves only as the USBLC6 clamp reference. No fuse/no load — fine |
| USB ID | `P5.4` ↔ `U1.1` = D0 = PB12 (OTG_HS_ID), 79.4 mm, 4 vias | Correct for a micro-AB receptacle; schematic note: "Type A or Type B is determined by state of ID pin. For A tie ID to GND; for B leave ID floating". Host/OTG role is firmware-selectable |
| SD card detect | `P1` pin A (`SWA`) on no net; pin B (`SWB`) on GND | **Card presence unreadable** — identical to Trey's F-022; Trey inherited it from the Pod |
| Look-alike net names | only the intended differential pairs (`USB_OTG_FS_D+/−`, `USB_OTG_FS_D_IN_+/−`) | none spurious |
| Packaged parts with no net | FD1–6, H1–4 | fiducials / holes |

## 4. Firmware pin map vs schematic (`firmware_pinmap.py`)
Relation derived from the Seed symbol's pin names `GPIOn(function)` on pads 1–40: **pins 1–15 → D0–D14 (pin = D+1); pins 22–37 → D15–D30 (pin = D+7)**; pins 16–21 and 38–40 are audio/power. Validated against libDaisy `daisy_seed.h` on the fixed-function pins (D1–D6 = PC11/PC10/PC9/PC8/PD2/PC12 = SDMMC1, D29/D30 = PB14/PB15 = USB_HS D−/D+, D0 = PB12 = ID).

| libDaisy constant (`daisy_pod.cpp`) | Dn | STM32 | Seed pin | Symbol function | Schematic net | Match |
|---|---|---|---|---|---|---|
| `SW_1_PIN` | D27 | PG9 | 34 | SAI2_FS_B | `TAC_SWITCH_1` (S3) | ✓ |
| `SW_2_PIN` | D28 | PA2 | 35 | ADC11 | `TAC_SWITCH_2` (S2) | ✓ |
| `ENC_A_PIN` | D26 | PD11 | 33 | SAI2_SD_A | `ENC_A` | ✓ |
| `ENC_B_PIN` | D25 | PA0 | 32 | ADC10 | `ENC_B` | ✓ |
| `ENC_CLICK_PIN` | D13 | **PB6** | 14 | **USART1_TX** | `ENC_CLICK` | ✓ (but see §5) |
| `LED_1_R/G/B_PIN` | D20/D19/D18 | PC1/PA6/PA7 | 27/26/25 | ADC5/4/3 | `LED_1_R/G/B` | ✓ |
| `LED_2_R/G/B_PIN` | D17/D24/D23 | PB1/PA1/PA4 | 24/31/30 | ADC2/ADC9/ADC8-DAC1 | `LED_2_R/G/B` | ✓ |
| `KNOB_1_PIN` | D21 | PC4 | 28 | ADC6 | `POT_1` (VR_1) | ✓ |
| `KNOB_2_PIN` | D15 | PC0 | 22 | ADC0 | `POT_2` (VR_2) | ✓ |
| MIDI RX (`midi.cpp` default) | D14 | PB7 | 15 | USART1_RX | `USART1_RX` (U15.OUT) | ✓ |
| MIDI TX (`midi.cpp` default) | D13 | PB6 | 14 | USART1_TX | **`ENC_CLICK`** | conflict → §5 |
| SDMMC1 D3/D2/D1/D0/CMD/CK | D1–D6 | PC11/PC10/PC9/PC8/PD2/PC12 | 2–7 | SDMMC1_* | `SD_D3…SD_CK` (P1) | ✓ |
| USB D−/D+ | D29/D30 | PB14/PB15 | 36/37 | USB_HS_D−/D+ | `USB_OTG_FS_D−/D+` (via U7) | ✓ |
| USB ID | D0 | PB12 | 1 | USB_HS_ID | `USB_OTG_FS_ID` (P5.4) | ✓ |

Note the commented-out legacy block in `daisy_pod.cpp` (Rev1/Rev2 pinouts) is dead code; only the `seed::Dn` constants are live. The Pod's switch, encoder and knob pins carry **no external pull-ups or RC** (all 2-/3-node nets); libDaisy supplies `GPIO::Pull::PULLUP` on A/B (`encoder.cpp`) and on the click/buttons (`switch.h` default `PULLUP`), with `Polarity::INVERTED`.

## 5. Encoder click on USART1_TX vs libDaisy MIDI (DP-P3-08)
Facts, each from a file read this session:
- Schematic: `ENC_CLICK` = `ENC_1.2` (pad E) ↔ `U1.14` "GPIO13(USART1_TX)"; `ENC_1.1` (pad D) and `ENC_1.C` on GND. 38.6 mm, 2 vias, no other parts on the net.
- `daisy_seed.h`: `D13 = Pin(PORTB, 6)`. `midi.cpp`: `MidiUartTransport::Config::Config()` sets `periph = USART_1`, `rx = Pin(PORTB, 7)`, **`tx = Pin(PORTB, 6)`**. `midi.h` `MidiUartTransport::Init`: `uart_config.mode = TX_RX`, `pin_config.tx = config.tx`. `uart.cpp` `InitPins()`: `if(config_.pin_config.tx.port != PORTX)` → `HAL_GPIO_Init(..., GPIO_MODE_AF_PP, NOPULL)` on the TX pin.
- `daisy_pod.cpp`: `Init()` order is `InitButtons → InitEncoder → InitLeds → InitKnobs → InitMidi`; `InitMidi()` uses the default `MidiUartHandler::Config` unmodified.

Consequence: after `DaisyPod::Init()`, PB6 is a USART1_TX alternate-function push-pull output (UART idle = high), while `Encoder::sw_` still reads the same pin through the GPIO input data register (which does reflect the pin level in AF mode — the click therefore still *appears* to work). Pressing the encoder shorts the driven-high output to GND through the switch; the current is set only by the GPIO driver's source impedance and exceeds the STM32H7 per-pin absolute maximum (20 mA, **from memory of DS12556, not fetched**). Any `pod.midi.SendMessage()` also toggles the click line. Class **VIOLATION (hardware–firmware, cross-domain)**, status **plausible**: the firmware path is verified in source, the electrical consequence is computed, not measured; no matching libDaisy issue was found (GitHub search "pod encoder click midi tx" / "pod midi encoder": 0 relevant results, 2026-10-12). Fix is one line in firmware (`midi_config.transport_config.tx = Pin()` i.e. `PORTX`, or `mode = RX`) or, in hardware, moving the click off pin 14. **Trey's rev 3 is immune:** clicks on pins 22 (PC0) and 29 (PA5), pin 14 is a dedicated `/USART1_TX` to the MIDI OUT jack (rev-3 Pass 3 §3).

## 6. Expansion header P2 (DNI, 1×12, `M12_ALL_CIRCLE_DNI`, absent from BOM)
| P2 pin | Net | Seed pin | STM32 | Trey rev-3 use of the same Seed pin |
|---|---|---|---|---|
| 1 | `SPI_NSS` | 8 | PG10 (SPI1_NSS) | `/CS_SPI` → OLED J8.17 |
| 2 | `SPI_SCK` | 9 | PG11 (SPI1_SCK) | `/SCLK_SPI` → J8.7 |
| 3 | `SPI_MISO` | 10 | PB4 (SPI1_MISO) | `/TAC_SHIFT_R` (GPIO; OLED is write-only) |
| 4 | `SPI_MOSI` | 11 | PB5 (SPI1_MOSI) | `/SD_IN_SPI` → J8.8 |
| 5 | `I2C_SCL` | 12 | PB8 (I2C1_SCL) | `/ENCR_A` |
| 6 | `I2C_SDA` | 13 | PB9 (I2C1_SDA) | `/ENCR_B` |
| 7 | `A7` | 29 | PA5 (ADC7/DAC2) | `/ENCR_CLICK` |
| 8 | `A1` | 23 | PA3 (ADC1) | `/TAC_SHIFT_L` |
| 9 | `+3V3_A` | 21 | — | `/+3V3_A` |
| 10 | `+3V3_D` | 38 | — | `/+3V3_D` |
| 11 | `VIN` | 39 | — | `/DSY_VIN` (fed from the 9 V barrel chain) |
| 12 | `GND` | 20/40 | — | GND |

Confirmed: Trey's OLED uses exactly the Pod's P2 SPI1 pins (8/9/11) plus pin 1 (`/RES_SPI`, Pod `USB_OTG_FS_ID`) and pin 28 (`/DC_SPI`, Pod `POT_1`). Every other Pod assignment Trey kept verbatim: SD pins 2–7, MIDI RX 15, audio 16–19, LEDs 24–27/30/31, encoder A/B 32/33, buttons 34/35, USB 36/37 (rev-3 `A1` pad→net list extracted with `pcbnew` this session). Traces on P2 are 9–28 mm, 0.254 mm, 0–1 via; no pull-ups on I2C (expected for an unpopulated header).

## 7. Other connectivity facts
- LEDs are **common-anode to `+3V3_D`** (LED1.2/LED2.2 = pin A) with the R/G/B cathodes through 1 k (R6–R11) to the GPIOs — GPIO low = on, consistent with `led1.Init(..., invert = true)` in `daisy_pod.cpp`. This is the opposite topology to Trey's (NPN low-side drivers from +9 V).
- Headphone volume pot P8 (Alps RK10J12R0A0B, 5 terminals): `P$1` GND (common), `P$2`/`P$3` wipers L/R → C53/C54, `P$5`/`P$4` ends on `AUDIO_OUT_L/R`; pads `P$6/P$7` are mounting lugs on no net. Same at-the-amp-input topology Trey used.
- MIDI IN polarity select: `J1.RING → R79 (0 Ω, fitted) → MIDI_IN_A → R63 220 Ω → U15.A ∥ D5.C`; `J1.TIP → R83 (0 Ω, fitted) → MIDI_IN_B → U15.C ∥ D5.A`; `R78`/`R84` (DNI) are the crossed alternates. With the fitted pair, ring = current source side (DIN pin 4), tip = sink (DIN pin 5) = **TRS "Type A"** (MMA RP-054 mapping quoted **from memory; midi.org unreachable**).
- No MIDI OUT exists on the Pod (no net on pin 14 other than `ENC_CLICK`; no second jack).

## 8. BOM vs schematic (connectivity consequence; full BOM audit is Pass 4)
| Item | Schematic | BOM xlsx (24 lines) | Consequence |
|---|---|---|---|
| R78, R84 | value `DNI 0R` | listed: "4 × 0R R0603 … R79 R83 R78 R84" | If all four are fitted: `MIDI_IN_TIP` and `MIDI_IN_RING` are both joined to both `MIDI_IN_A` and `MIDI_IN_B` → tip ≡ ring, opto LED + R63 shorted → **MIDI IN dead** (and the sender's loop shorted, ~5 mA, harmless). The BOM has no DNI column |
| P2 | `DNI` | absent | consistent |
| All other 56 packaged parts (excl. FD/H) | — | present, refs match | consistent |

## Findings (Daisy Pod, Pass 3)
| ID | Class | Status | Finding | Evidence | Source |
|---|---|---|---|---|---|
| DP-P3-01 | PASS | confirmed | Eagle sch ↔ Eagle brd ↔ KiCad conversion fully consistent: 58 packaged parts in all three (+4 pad-less logo packages on the board), 192/192 pad-nets identical, 0 duplicate refs, 0 renames; Eagle and pcbnew wire lengths agree to 0.1 mm | `sch_brd_diff.py`, `eagle_brd_netlist.py` | — |
| DP-P3-02 | PASS | confirmed | 27 symbol-only parts (2 frames, 23 GND, 2 supply) and 10 pad-only parts (6 fiducials, 4 holes) dispositioned; holes not grounded (cosmetic) | §2 | — |
| DP-P3-03 | PASS | confirmed | ERC-equivalent: 0 single-pin nets, 40/40 Seed pins on nets, all open pins intentional (jack switch contacts, encoder tabs, USB shell per schematic note, SWA) | `erc_equiv.py` | — |
| DP-P3-04 | JUDGMENT | confirmed | SD card detect: `SWA` open, `SWB` on GND — card presence unreadable; **origin of Trey's F-022** (inherited verbatim) | §3 | — |
| DP-P3-05 | PASS (design fact) | confirmed | `VIN` undriven on the Pod (pin 39 ↔ DNI P2.11 only); Pod is powered through the Seed's own micro-USB (Seed Rev7: VBUS→D2, V_IN→D1 diode-OR); Pod P5 VBUS feeds only the TVS — **data-only USB is inherited Pod topology**, the origin of Trey's design choice | §3, Seed Rev7 sheet | `ES_Daisy_Seed_Rev7.pdf` |
| DP-P3-06 | PASS | confirmed | USB ID: P5.4 ↔ Seed pin 1 (PB12 OTG_HS_ID), 79.4 mm/4 vias; role selectable per schematic note; D+/D− through U7 USBLC6-2 pins 1→6 / 3→4 (pass-through pairs) | §3, Pass 5 §2 | schematic note; USBLC6 pinout from memory |
| DP-P3-07 | PASS | confirmed | libDaisy Pod pin map matches the schematic 13/13 (+9 fixed-function pins); physical pin = D+1 (pins 1–15) / D+7 (pins 22–37), from the Seed symbol pin names | `firmware_pinmap.py` | libDaisy `daisy_pod.cpp`, `daisy_seed.h` (secondary source) |
| DP-P3-08 | VIOLATION (hardware–firmware, cross-domain) | plausible | `ENC_CLICK` on pin 14 = PB6 = USART1_TX; libDaisy's default MIDI transport sets `tx = PB6`, `mode = TX_RX`, and `DaisyPod::Init()` runs `InitMidi()` after `InitEncoder()` → PB6 becomes an AF push-pull output; pressing the encoder shorts the idle-high TX to GND (exceeds STM32 per-pin abs-max 20 mA, from memory); MIDI TX traffic toggles the click line. One-line firmware fix (`tx = PORTX` / `mode = RX`). Trey's rev 3 is immune (clicks on 22/29) | §5 | libDaisy `midi.cpp` l.10–17, `midi.h` Init, `uart.cpp` `InitPins`, `daisy_pod.cpp` l.75–87; STM32 abs-max not fetched |
| DP-P3-09 | PASS | confirmed | P2 (DNI) exposes SPI1 ×4, I2C1 ×2, A7 (pin 29), A1 (pin 23), 3V3_A/3V3_D/VIN/GND; Trey's OLED SPI uses the Pod's pins 8/9/11, with 1 and 28 for RES/DC; all other Seed assignments kept verbatim from the Pod | §6 | rev-3 `A1` pad→net extract |
| DP-P3-10 | JUDGMENT | confirmed | Encoder mounting tabs (GND1–6) and USB shell (CASING1–4) floating; USB shell is a documented choice ("Leaving USB shield ungrounded"); H1–H4 isolated | §3 | schematic note |
| DP-P3-11 | PASS | confirmed | Single GND: AGND (pin 20) + DGND (pin 40) tied, P1 VSS + shield + SWB on GND, U4 PowerPAD on GND; no separate analogue ground | §1 | — |
| DP-P3-12 | VIOLATION (BOM ≠ schematic) | confirmed (files) / consequence inferred | BOM lists all four MIDI polarity jumpers (R78 R79 R83 R84, qty 4) while the schematic marks R78/R84 `DNI 0R`; populating all four shorts tip↔ring and the opto LED → MIDI IN dead. Hand to Pass 4 | §8 | `BOM_ES_Daisy_Pod_Rev5.xlsx`, `.sch` part values |
| DP-P3-13 | PASS | confirmed | LED topology: common anode on `+3V3_D`, cathodes via 1 k to GPIO (sink), matches `led.Init(invert=true)`; no 3.3V-only-pin concern (GPIO sees ≤ 3.3 V) | §7 | libDaisy `daisy_pod.cpp`, `led.cpp` |
| DP-P3-14 | PASS (design fact) | confirmed | No MIDI OUT on the Pod; MIDI IN polarity = TRS Type A with the fitted 0 Ω pair (R79/R83), Type B by swapping to R78/R84 | §7 | RP-054 mapping from memory (midi.org unreachable) |
