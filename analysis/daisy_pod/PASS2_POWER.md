# Pass 2 (Daisy Pod Rev5 reference) — Power Distribution, Decoupling, LED / Encoder / Button / Amp Circuits
**Date:** 2026-10-12 · **Subject:** Electrosmith Daisy Pod Rev5, the reference design Trey's WavetableController derives from · **Truth checked:** `kicad_out/pod/sch_netlist.json` (parsed from `reference/electrosmith/daisy_pod/ES_Daisy_Pod_Rev5.sch`, Eagle 9.6.2) for topology, cross-read against `ES_Daisy_Pod_Rev5.pdf` (`pdftotext -layout`); `reference/electrosmith/daisy_pod/kicad/ES_Daisy_Pod_Rev5.kicad_pcb` (KiCad 9 import of the `.brd`; copper, pads and tracks untouched by the import, GND zones filled by KiCad — the Eagle `.brd` remains the source of record) for every distance, width and length; `kicad_out/pod/bom.txt` for part numbers. Nothing under `reference/` was modified.

**Thresholds and their sources:**
- TI TPA6110A2 **SLOS314B** (Dec 2000, rev. Mar 2011) — fetched 2026-10-12 from ti.com, text in scratchpad `pod_p2/dl_ti/tpa6110a2.txt`. Quoted below. (Rev 2 cited the same document from an archive; this pass re-read it.)
- Cree **CLS6B-FKW** CLD-CT1475 rev 5 (scratchpad `dl/cree/HB-CLS6B-FKW.txt`, fetched 2026-10-09 in the rev-3 review) for RGB Vf: VF(avg) 2.1 / 3.1 / 3.1 V, VF(max) 2.6 / 3.8 / 3.8 V at IF = 20 mA; IR 10 µA at VR = 5 V. **Secondary source**: the Pod's actual LED is the Cree **CLVBA-FKA** (PLCC4); its datasheet could not be fetched — cree-led.com, assets.cree-led.com, mouser.com, digikey.com, farnell.com, arrow.com and alldatasheet.com are all DNS-blocked from this session. Same manufacturer, same AlInGaP red / InGaN green-blue dice; the pad assignment of the CLVBA is therefore **unverified** here (DP-P2-07).
- Bourns **PEC11J** encoder datasheet (scratchpad `pod_p4/dl/pec11j.txt`, fetched by the Pass-4 agent): "Suggested Filter Circuit" 10 kΩ pull-up + 10 kΩ series + 0.01 µF per channel at 5 VDC; contact bounce 2.0 ms max at 15 RPM; switch rating 10 mA at 5 VDC.
- onsemi **NSR1020MW2T3G** (scratchpad `pod_p4/dl/nsr1020.txt`): VR 20 V, VF 0.26 V max at 10 mA.
- Daisy Seed pin numbers: `reference/electrosmith/daisy_seed/Daisy_Seed_pinout.pdf` (D-index → physical pin: D15 = 22 … D30 = 37; 3V3_D = 38, VIN = 39, DGND = 40; AGND = 20, 3V3_A = 21). VIN 4–17 V, 3.3 V-only pins 24/25/28/29/30, no published 3v3 current limit: Daisy datasheet v1.0.5 as recorded in rev-2 `PASS2_POWER.md` (host blocked).
- STM32H750 GPIO current: **model memory** of DS12556 "Current characteristics" (IIO ±20 mA per pin absolute max) — st.com returned HTTP 503 twice. Flagged; only the 1.3 mA LED result depends on it, with a 15× margin.
- IPC-2221 external-trace formula, computed (1 oz, ΔT 10 °C): 0.2032 mm → 0.75 A, 0.254 → 0.89 A, 0.3 → 1.00 A, 0.4064 → 1.25 A. Cu ρ = 1.72e-8 Ω·m, 35 µm: 2.42 / 1.93 / 1.64 / 1.21 mΩ per mm.
- Yageo RC0402 power rating 1/16 W (62.5 mW), RC0603 1/10 W: standard series ratings, not fetched (only the 1.7 mW LED-resistor result depends on them).

**Scripts** (`analysis/daisy_pod/scripts/pass2/`): `board_dump.py` (pcbnew → JSON; run without `-I`), `pod_power_geom.py` (`python3 -I`; rail copper, pin → cap distances straight-line and routed by a graph walk over tracks/vias/pads, Seed-pin → load path lengths, signal-net pad-to-pad lengths, LED pad table), `pod_power_budget.py` (`python3 -I`; LED currents with two Vf models, rail loads, TPA6110 network arithmetic, IPC/DC-resistance table). Known-answer checks on the graph walker: `VIN` U1.39 → P2.11 routed 47.9 mm vs 48.0 mm total copper on a single-segment net; `USB_VBUS` 7.0 mm routed vs 6.2 mm straight; routed ≥ straight on every net except where a large pad (U15's 1.27 × 2.54 mm gull-wing) lets the track end inside the pad outline (U15.6 → C11: 2.1 routed vs 2.6 straight — pad-edge effect, both reported).

Board: 90.0 × 52.3 mm bounding box, 2 copper layers, 62 footprints, 615 track segments, 115 vias (drills 0.330 / 0.350 mm), GND zones F.Cu 2,656 mm² and B.Cu 3,247 + 14 mm² (KiCad fill).

---

## 1. Rail topology (from the Pod netlist, every node verified)

```
P5 Pod micro-USB  pin 1 VBUS ──► USB_VBUS ──► U7.5 (USBLC6-2 VBUS reference)   … and nothing else.
                  pins 2/3 D−/D+ ──► U7 ──► U1.36/37 (Seed GPIO29/30 = USB_HS pins)   pin 4 ID ──► U1.1 (GPIO0 USB_HS_ID)
                  shell pads CASING1-4: no net ("Leaving USB shield ungrounded" — sheet note)
P2 expansion header (value "M12_ALL_CIRCLE_DNI" = not fitted) pin 11 ──► VIN ──► U1.39 Seed VIN   (48.0 mm @ 0.4064 mm F.Cu, 0 vias)
                  pin 10 ──► +3V3_D ; pin 9 ──► +3V3_A ; pin 12 ──► GND ; pins 1-8 SPI/I2C/A1/A7
U1.38 Seed 3V3_D ──► +3V3_D: C11 100 nF (the only cap, at U15) · U15.6 H11L1 Vcc · R64 270R (USART1_RX pull-up)
                              · P1.4 microSD VDD · R1/R2/R3/R4/R16 47k SD pull-ups · LED1.2 + LED2.2 common anodes · P2.10
U1.21 Seed 3V3_A ──► +3V3_A: C60 100 nF (the only cap, at U4) · U4.6 TPA6110A2 VDD · VR_1.3 + VR_2.3 (10k pot tops) · P2.9
GND:  U1.20 AGND and U1.40 GND are the same net — one ground on the Pod. Also P1 VSS/SHIELD/B, J1-J4 sleeves, U4.2/U4.9 (pwr pad),
      U4.3 SHUTDOWN, C11.2/C56.1/C60.1, VR_x.1, ENC_1 C + pad D, S2/S3 pads 3-4, P5.5, U7.2, P2.12.
```

Answers to the scoping questions:
- **Is Seed VIN fed from the Pod's USB?** **No.** `USB_VBUS` has exactly two nodes: P5.1 and U7.5. `VIN` has exactly two nodes: U1.39 and P2.11, and P2 is a DNI header. The Pod board has **no power input of its own**: the Seed is powered through the Seed module's own micro-USB (its on-module 5 V → 3V3 regulators), or by whatever the user wires to P2.11. The Pod's P5 is a *second*, data-only USB port on the Seed's USB_HS pins — exactly the data-only USB topology Trey's board has (`/+5V_USB` → U2.5 only), which SOURCE_OF_TRUTH §7 records as deliberate. The reference design already does it.
- **What +3V3_D feeds:** SD socket, MIDI opto + its 270 Ω pull-up, the five 47 k SD pull-ups, both LED common anodes, header pin 10. **What +3V3_A feeds:** the headphone amp, the two 10 k control pots, header pin 9.
- **GND/AGND:** tied at the Seed (pins 20 + 40 on `GND`); the Pod has no separate analog ground.
- **No 9 V path.** The Pod has no barrel jack, no bridge, no series Schottky, no ferrite beads, no 3.3 Ω resistors and no bulk electrolytic on any supply. The only electrolytics on the board are C62/C63 (100 µF, 35 V, Panasonic D8) — headphone output coupling caps, not supply caps. The rev-3 inrush (R3-P2-05), series-element (R3-P2-06), bead/3.3 Ω budget (R3-P2-07/12) and TPS62172 (R3-P2-08/09) findings have **no counterpart** on the reference.

## 2. Decoupling audit (`pod_power_geom.py §B/§C`; straight = pad centre to pad centre, routed = copper path through tracks and vias)

| Power pin | Net | Nearest same-net cap | Straight | Routed / vias | Datasheet wording | Verdict |
|---|---|---|---|---|---|---|
| U4.6 TPA6110A2 VDD | +3V3_A | C60 100 nF 0402 | **3.1 mm** | 3.4 mm / 0 | "0.1 µF, placed as close as possible to the device VDD lead" (SLOS314B p. 14) | PASS |
| U4.1 TPA6110A2 BYPASS | N$39 | C56 100 nF 0402 | **2.8 mm** | 2.9 mm / 0 | "Connect to a 0.1 µF to 1 µF low ESR capacitor" (pin table p. 2) | PASS |
| U4 VDD — electrolytic | +3V3_A | none | — | — | "aluminum electrolytic capacitor of 10 µF or greater placed near the power amplifier is recommended" | **absent** (DP-P2-10) |
| U15.6 H11L1 Vcc | +3V3_D | C11 100 nF 0402 | 2.6 mm | 2.1 mm / 0 (pad-edge) | opto bypass "as close as possible" (generic) | PASS |
| P1.4 microSD VDD | +3V3_D | C11 (at the opto) | **35.8 mm** | **69.4 mm / 4 vias** | — (no cap at the socket) | **no local cap** (DP-P2-02) |
| U1.38 Seed 3V3_D | +3V3_D | C11 | 34.9 mm | 49.3 mm / 3 | — | single 100 nF on the rail (DP-P2-03) |
| U1.21 Seed 3V3_A | +3V3_A | C60 | 29.8 mm | 42.8 mm / 3 | — | single 100 nF on the rail |
| LED1.2 / LED2.2 anodes | +3V3_D | C11 | 43.3 / 32.3 mm | 58.9 / 78.9 mm | — | ≤ 4.4 mA total, irrelevant |
| U7.5 USBLC6 VBUS | USB_VBUS | none | — | — | ESD reference only, carries no load | PASS |
| U4.7 / U4.5 OUT1/OUT2 → C62/C63 | N$40 / N$41 | 100 µF | 9.6 / 15.1 mm | 23.7 / 18.4 mm | — | OK |

Seed pin → load, routed (`§C`): U1.38 → P1.4 **35.3 mm / 3 vias**; → U15.6 51.4 mm; → R64.1 46.8 mm; → LED1.2 24.8 mm; → LED2.2 44.7 mm; → P2.10 57.1 mm (farthest). U1.21 → U4.6 **46.2 mm / 3 vias**; → VR_2.3 45.5 mm; → VR_1.3 58.4 mm; → P2.9 10.2 mm.

## 3. Rail copper, ampacity, DC resistance (`§A`)

| Net | Copper (mm @ width, layer) | Min width | IPC-2221 A @ min | Est. load | R | Verdict |
|---|---|---|---|---|---|---|
| +3V3_D | **109.7 mm**: 48.4 @ 0.4064 (F) + 59.8 @ 0.4064 (B) + 1.5 @ 0.254 (B); 7 vias | 0.254 (1.5 mm stub) | 0.89 A (1.25 A on the 0.4064 trunk) | SD card bursts (order 0.1–0.2 A, SD spec not fetched) + H11L1 1.6 mA + 12.2 mA through R64 when the opto output is low + LEDs ≤ 4.4 mA + 47k pull-ups 0.35 mA ≈ **< 0.25 A** | 134 mΩ summed copper; **43 mΩ** U1.38 → P1.4, **69 mΩ** to the farthest pad | PASS |
| +3V3_A | 105.0 mm: 50.1 @ 0.4064 (F) + 51.6 @ 0.4064 (B) + 3.4 @ 0.254 (B); 5 vias | 0.254 | 0.89 A | pots 0.66 mA + TPA6110 IDD 1.5 mA typ / 3 mA max (SLOS314B) + headphone load current (tens of mA) | 56 mΩ U1.21 → U4.6 | PASS |
| VIN | 48.0 @ 0.4064 (F), 0 vias | 0.4064 | 1.25 A | 0 unless P2 is fitted | 58 mΩ | PASS |
| USB_VBUS | 7.4 @ 0.2032 (F) | 0.2032 | 0.75 A | ~0 (ESD reference) | 18 mΩ | PASS |
| N$39 BYPASS | 2.9 @ 0.254 (B) | — | — | µA | — | PASS |
| N$40 / N$41 amp outputs | 23.8 / 21.4 @ 0.254 | 0.254 | 0.89 A | ≤ 0.1 A peaks into 16 Ω | 46 / 41 mΩ | PASS |

The Pod's power traces are 16 mil (0.4064 mm) throughout, with 10 mil (0.254) and 8 mil (0.2032) for signals. Nothing on the Pod is near an IPC limit.

## 4. LED drive (`pod_power_budget.py`)

**Topology** (netlist + Eagle library `LED_RGB_SMT` device connects: symbol A → pad 2, R → pad 1, G → pad 4, B → pad 3): `+3V3_D` → LED pad 2 (common anode) → die → cathode pad → **1 kΩ 0402** (R6–R11) → Seed GPIO, which sinks when driven low. No transistor, no separate LED rail.

| GPIO net | Seed pin (D-index) | 3.3 V-only? | R | LED pad | GPIO → R routed | R → LED routed |
|---|---|---|---|---|---|---|
| LED_1_R | 27 (D20/ADC5) | no | R6 | LED1.1 | 2.4 mm | 48.8 mm (N$2) |
| LED_1_G | 26 (D19/ADC4) | no | R7 | LED1.4 | 4.5 mm | 41.9 mm (N$3) |
| LED_1_B | **25** (D18/ADC3) | **yes** | R8 | LED1.3 | 6.7 mm | 46.9 mm (N$4) |
| LED_2_R | **24** (D17/ADC2) | **yes** | R9 | LED2.1 | 42.8 mm | 5.6 mm (N$5) |
| LED_2_G | 31 (D24/ADC9) | no | R10 | LED2.4 | 9.1 mm | 18.2 mm (N$6) |
| LED_2_B | **30** (D23/ADC8) | **yes** | R11 | LED2.3 | 5.7 mm | 21.1 mm (N$7) |

These are the **same six Seed pins** Trey's rev 3 uses (/LED_1_B 25, /LED_1_R 27, /LED_1_G 26, /LED_2_B 30, /LED_2_R 24, /LED_2_G 31 — rev-3 PASS2 §4), so the Pod pin map was inherited intact. Three of them (24, 25, 30) are on the 3.3 V-only list; on the Pod the highest voltage any of them can see is `+3V3_D` through an LED (pin high-Z: anode at 3.3 V, pin pulled toward 3.3 V minus nothing — no current, no stress). **Harmless by construction**, as the brief expected.

**Current per colour** — I = (3.3 − Vf(I) − VOL)/1 kΩ, VOL = I × 25 Ω (STM32 Ron estimate, negligible):

| Colour | Vf typ @ 20 mA (CLS6B) | I, Vf held at typ | I, Vf corrected for low current (0.10 / 0.17 V per decade, AlInGaP / InGaN — generic slopes, assumption) | I at Vf **max** (2.6 / 3.8 / 3.8 V) | % of 20 mA rating | P(1k) | GPIO VOL |
|---|---|---|---|---|---|---|---|
| Red | 2.1 V | **1.20 mA** | 1.29 mA @ 1.98 V | 0.70 mA | 4–6 % | 1.7 mW (0402 62.5 mW) | 32 mV |
| Green | 3.1 V | **0.20 mA** | 0.47 mA @ 2.82 V | **0 mA** | 1–2.5 % | 0.2 mW | 12 mV |
| Blue | 3.1 V | **0.20 mA** | 0.47 mA @ 2.82 V | **0 mA** | 1–2.5 % | 0.2 mW | 12 mV |

- The 7 Oct review's statement ("green and blue in this LED need about 3.1 V just to turn on, and a Daisy pin gives 3.3 V, so they come out dim; red would be fine") is **confirmed quantitatively** for the reference design: red runs at ~1.2–1.3 mA (4–6 % of its 20 mA test current), green and blue at ~0.2–0.5 mA (1–2.5 %). All six on: **≤ 4.4 mA** from `+3V3_D`. Electrosmith ships this, so it is "bright enough for a status light" by their standard, with brightness and colour mixing done by PWM.
- **Zero margin on green/blue Vf:** supply 3.3 V against VF(avg) 3.1 V leaves 0.2 V across 1 kΩ. A die at the datasheet VF(max) (3.8 V on the CLS6B sheet; the CLVBA figure is unverified) would draw **nothing**. Bin-to-bin brightness variation of the G/B channels is therefore large on the Pod (DP-P2-06). Any 3v3 rail sag makes it worse (at 3.0 V: green/blue ≈ 0 with typ Vf).
- **GPIO loading:** 1.3 mA sink per pin vs ±20 mA absolute max (STM32H750 DS12556, model memory) → 15× margin; total 4.4 mA vs the ±140 mA package limit. PASS.
- **Resistor dissipation:** 1.7 mW max in a 1/16 W 0402 → 3 % of rating. PASS.
- **Pad assignment vs the CLVBA-FKA datasheet:** unverifiable from here (DP-P2-07). The Pod is a shipping product with the LEDs working, so the Electrosmith symbol (A = pad 2) is presumably right; it is recorded as unverified, not as a finding against the board.

## 5. Encoder and buttons

| Net | Part / pad | Seed pin (D-index) | Routed length / vias / width | External pull-up | RC |
|---|---|---|---|---|---|
| ENC_A | ENC_1.A | 33 (D26) | 60.8 mm / 4 / 0.2032 | none | none |
| ENC_B | ENC_1.B | 32 (D25) | 62.8 mm / 4 / 0.2032 | none | none |
| ENC_CLICK | ENC_1.E (push switch) | 14 (D13, USART1_TX) | 37.7 mm / 2 / 0.254 | none | none |
| TAC_SWITCH_1 | S3 pads 1+2 | 34 (D27) | 36.1 / 40.9 mm / 2 / 0.2032 | none | none |
| TAC_SWITCH_2 | S2 pads 1+2 | 35 (D28/ADC11) | 37.8 / 42.7 mm / 2 / 0.2032 | none | none |

ENC_1 common C and pad D, S2/S3 pads 3-4 → GND. Every one of these is a bare 2-node net (3 nodes where both switch pads share the net). Bourns' own PEC11J sheet draws a "Suggested Filter Circuit" (10 k pull-up, 10 k series, 0.01 µF per channel) and rates contact bounce at 2.0 ms max; the Pod omits all of it and relies on the STM32 internal pull-up and libDaisy's software debounce (`Switch::Init` default `PULLUP`, rev-3 PASS3 §3). Because the Pod is the libDaisy hardware target, this is the configuration the stock driver is written for. **JUDGMENT, works as shipped** (DP-P2-08). Note the click pin is 14 = USART1_TX: the Pod gives up MIDI OUT to get the encoder click (see §7).

## 6. Pots

VR_1 and VR_2 (Song Huei B10K): pin 3 → `+3V3_A`, pin 1 → GND, wiper → ADC. `POT_1` → VR_1.2 → **Seed pin 28** (D21/ADC6, a 3.3 V-only pin — fine for an ADC input bounded by 3V3_A), 31.1 mm / 1 via / 0.2032; `POT_2` → VR_2.2 → **Seed pin 22** (D15/ADC0), 30.9 mm / 1 via. (The brief's "pins 22/23" is half right: pin 23 is `A1`, routed to header P2.8, not a pot.) **No RC** at the ADC pins; the pot tops are 45.5 / 58.4 mm of 0.4064 mm copper from U1.21 with C60 as the only capacitor on the rail. Each pot draws 3.3 V / 10 k = 0.33 mA. PASS (DP-P2-09) — a 10 k wiper into the STM32 ADC with no filter cap is standard practice on Electrosmith boards; firmware averaging is expected. Trey's board has no control pots (only the dual volume pot), so there is no counterpart.

## 7. TPA6110A2 headphone amp — same checks as rev-3 R3-P2-11, now against the re-fetched SLOS314B

| Check | Pod | Datasheet | Verdict |
|---|---|---|---|
| 0.1 µF at VDD | C60, 3.1 mm from U4.6 | "typically 0.1 µF, placed as close as possible to the device VDD lead" | PASS |
| ≥ 10 µF electrolytic near the amp | **none** on `+3V3_A` (C60 is the only cap) | "a larger aluminum electrolytic capacitor of 10 µF or greater placed near the power amplifier is recommended" (p. 14) | **absent** — DP-P2-10 |
| BYPASS cap | C56 100 nF, 2.8 mm | "0.1 µF to 1 µF low ESR" | PASS |
| Eq. 6 start-up-pop relation | C(B)·230 k = 100 nF × 230 k = **23.0 ms** ≥ Ci·Ri = 470 nF × 22 k = **10.3 ms** | 1/(C(B)·230 kΩ) ≤ 1/(Ci·Ri) | PASS |
| Gain | Rf/Ri = 33 k / 22 k = **1.5 V/V** (sheet note "Gain = 33K/22K = 1.5 V/V") | Rf ≤ 50 kΩ keeps the input pole out of the loop | PASS |
| 5 pF across Rf | **not fitted** | "For values of Rf above 50 kΩ … a small compensation capacitor of approximately 5 pF should be placed in parallel with Rf" | **not required at 33 k** — PASS. This also means the Oct-7 item "5 pF across R14/R15" on Trey's board (same 33 k) is optional per the datasheet, not a requirement. |
| Input HPF | 470 nF / 22 k → 15.4 Hz | — | PASS |
| Output coupling | C62/C63 100 µF 35 V → fc 50 Hz into 32 Ω, 99 Hz into 16 Ω (Eq. 7) | 100 µF is the datasheet's typical | PASS |
| SHUTDOWN | U4.3 → GND | "Puts the device in a low quiescent current mode when held high" → low = running | PASS |
| GND / power pad | U4.2 + U4.9 → GND | — | PASS |
| Output bleed resistors | none | — | note: Trey's board adds R22/R23 10 k to GND (rev-3 netlist confirmed) — an improvement for plug-in pop |
| IDD | 1.5 mA typ / 3 mA max (SHUTDOWN = 0 V) | — | load figure used in §3 |

## 8. MIDI (IN only)

```
J1 TRS  Ring ──► R79 0R (fitted) ──► MIDI_IN_A ──► R63 220R ──► N$77 = U15.1 H11L1 anode (+ D5 cathode)
        Tip  ──► R83 0R (fitted) ──► MIDI_IN_B = U15.2 H11L1 cathode (+ D5 anode)      D5 NSR1020 anti-parallel = reverse protection
        Tip  ──► R78 "DNI 0R" ──► MIDI_IN_A      Ring ──► R84 "DNI 0R" ──► MIDI_IN_B    (fit R78/R84 instead → TRS Type B)
U15.4 OUT ──► USART1_RX ──► U1.15 (Seed pin 15, D14) with R64 270R pull-up to +3V3_D ; U15.6 Vcc, C11 100 nF at 2.6 mm
```
Ring sources through the 220 Ω into the opto anode, tip is the sink: with R79/R83 fitted the jack is **MIDI TRS Type A** (MMA RP-054: tip = DIN 5, ring = DIN 4). The sheet calls the opto input "MIDI_IN_A/B" and the DNI pair is the Type-B selector. R64 270 Ω is the H11L1's standard open-collector load (the H11L1 datasheet test condition uses RL = 270 Ω — model memory, not fetched; rev-2 F-029 recorded the same value as "textbook"). Run lengths: J1 → R79/R83 23.7–36.3 mm, U1.15 → U15.4 16.9 mm. **MIDI OUT does not exist on the Pod**: there is no USART1_TX net; Seed pin 14 (D13 = USART1_TX) is `ENC_CLICK`. Trey's MIDI OUT (USART1_TX → 10 Ω → tip, 3V3_D → 33 Ω → ring) is an addition over the reference, not a deviation. PASS (DP-P2-12).

## 9. Findings

| ID | Class | Status | Finding | Evidence | Threshold source |
|---|---|---|---|---|---|
| DP-P2-01 | PASS | confirmed | **The Pod has no on-board power input.** `USB_VBUS` = {P5.1, U7.5} only; `VIN` = {U1.39, P2.11} only and P2 is a DNI header. The Seed runs from its own module USB (or a user-wired P2.11). The Pod's P5 is a data-only second USB port — the same `/+5V_USB` → ESD-only topology Trey's board uses. One ground (Seed pins 20 + 40). USB shell deliberately unconnected (sheet note). | §1; `sch_netlist.json` | — |
| DP-P2-02 | JUDGMENT | confirmed | **No capacitor at the microSD socket.** P1.4 VDD's nearest cap is C11 at the MIDI opto: 35.8 mm straight / 69.4 mm routed (4 vias); U1.38 → P1.4 35.3 mm, 3 vias, 43 mΩ. Works as shipped (16 mil trunk, short board), but the SD card's write bursts see only the Seed's on-module regulator caps plus one 100 nF 36 mm away. The same omission on Trey's board (R3-P2-10) is inherited from the reference — and made worse by 3.4× the distance. | §2 | — (no cited rule; SD host guidance generically asks for a local 0.1 µF + bulk) |
| DP-P2-03 | JUDGMENT | confirmed | **One 100 nF (C11) decouples the whole `+3V3_D` rail** (SD, opto, 270 Ω pull-up, 47 k pull-ups, LEDs, header) and one 100 nF (C60) the whole `+3V3_A` rail (amp, pots, header). Neither rail has bulk on the Pod. Tolerable here because every load is ≤ 57 mm from the Seed on 16 mil copper (≤ 69 mΩ); it is the pattern Trey's layout copied onto a 165 × 102 mm board. | §2, §3 | — |
| DP-P2-04 | PASS | confirmed | Rail copper: `+3V3_D` 109.7 mm / `+3V3_A` 105.0 mm, essentially all 0.4064 mm (IPC-2221 1.25 A at ΔT 10 °C) with 1.5 / 3.4 mm stubs at 0.254 (0.89 A); loads < 0.25 A / < 0.1 A; end-to-end ≤ 69 mΩ. `VIN` 48 mm @ 0.4064, 0 vias. Nothing near a limit. | §3 | IPC-2221 computed |
| DP-P2-05 | JUDGMENT | confirmed | **LED drive is dim by design — the Oct-7 claim is confirmed.** Common anode on `+3V3_D`, 1 kΩ 0402 to a sinking GPIO: red 1.2–1.3 mA (4–6 % of 20 mA), green/blue 0.2–0.5 mA (1–2.5 %), ≤ 4.4 mA total. GPIO sink 1.3 mA vs ±20 mA abs max (15×); 1 k dissipates 1.7 mW of 62.5 mW. Pins 24/25/30 (3.3 V-only) never see more than 3V3_D — harmless. Same six Seed pins as Trey's rev 3. This is the "four-trace fix" the Oct-7 review described; the reference design shows it is acceptable for status indication with PWM colour mixing. | §4; `pod_power_budget.py` | Cree CLS6B Vf (secondary); STM32H750 IIO (model memory, flagged); Yageo 0402 rating (standard) |
| DP-P2-06 | **ZERO-MARGIN** | plausible (CLVBA-FKA sheet unreachable; CLS6B figures used) | Green/blue headroom: 3.3 V supply vs VF(avg) 3.1 V → 0.2 V across 1 k; at VF(max) 3.8 V the die draws **0 mA**. Green/blue brightness on the Pod depends on the Vf bin and on 3v3 rail accuracy; a high-Vf part is simply dark. Red (VF max 2.6 V) always lights. | §4 table, Vf-max column | Cree CLD-CT1475 rev 5 VF(max) (same-family secondary) |
| DP-P2-07 | JUDGMENT | plausible (unverifiable here) | LED pad assignment (A = pad 2, R = 1, G = 4, B = 3 per Electrosmith's Eagle device) could not be checked against the Cree CLVBA-FKA datasheet — all seven hosts tried are blocked. Recorded as unverified; the Pod ships with these LEDs working. Re-verify when the sheet is reachable (it is also the Vf source DP-P2-05/06 should be re-run against). | §4 | — |
| DP-P2-08 | JUDGMENT | confirmed | **Encoder and buttons have no pull-ups and no RC**: ENC_A/B 60.8 / 62.8 mm (4 vias), ENC_CLICK 37.7 mm, S2/S3 36–43 mm, all 2-node nets. Bourns' PEC11J sheet suggests 10 k / 10 k / 10 nF per channel and quotes 2 ms bounce; the Pod relies on the STM32 internal pull-up and libDaisy debounce. Works as shipped — it is what the stock driver targets. Trey's board does the same (R3-P3-03). | §5; `pod_power_geom.py §D` | Bourns PEC11J (fetched by Pass 4) |
| DP-P2-09 | PASS | confirmed | Pots VR_1/VR_2 10 k across `+3V3_A`/GND, wipers 31 mm (1 via) to Seed pins 28 (ADC6, 3.3 V-only — fine) and 22 (ADC0); no RC; 0.33 mA each. Standard Electrosmith practice. No counterpart on Trey's board (no control pots). | §6 | — |
| DP-P2-10 | JUDGMENT (datasheet-cited) | confirmed | **TPA6110A2 ≥ 10 µF electrolytic absent on the Pod too.** C60 100 nF at 3.1 mm satisfies the ceramic clause; SLOS314B's "aluminum electrolytic capacitor of 10 µF or greater placed near the power amplifier is recommended" is not met — `+3V3_A` has no bulk anywhere. Trey's rev 3 (R3-P2-11, 5.6 mm / no bulk) inherited this from the reference. | §7 | SLOS314B p. 14 (fetched 2026-10-12) |
| DP-P2-11 | PASS | confirmed | TPA6110A2 network per datasheet: BYPASS 100 nF (0.1–1 µF), Eq. 6 23.0 ms ≥ 10.3 ms, gain 1.5 V/V with Rf 33 k ≤ 50 k so the **5 pF compensation cap is not required** (the clause applies "for values of Rf above 50 kΩ" — this also downgrades the Oct-7 "5 pF across R14/R15" item on Trey's board to optional), SHUTDOWN grounded = running, 100 µF outputs (50 Hz @ 32 Ω). No output bleed resistors (Trey adds 10 k R22/R23 — improvement). | §7 | SLOS314B pp. 2, 14, Eq. 6/7 |
| DP-P2-12 | PASS | confirmed | MIDI IN: TRS Type A as fitted (R79/R83 0 Ω; R78/R84 DNI = Type-B option), 220 Ω R63, NSR1020 anti-parallel (VR 20 V), H11L1 with 270 Ω pull-up to `+3V3_D`, C11 at 2.6 mm; UART run 16.9 mm. **No MIDI OUT on the Pod** (pin 14 USART1_TX is the encoder click). Trey's IN stage matches; his OUT is an addition. | §8 | MIDI TRS Type A (MMA RP-054, model memory); onsemi NSR1020 (fetched); H11L1 RL 270 Ω (model memory) |
| DP-P2-13 | PASS / N/A | confirmed | **No 9 V path**: no barrel, bridge, series Schottky, beads, 3.3 Ω or supply electrolytics (the only electrolytics are the 100 µF audio coupling caps). Inrush, bead, 3.3 Ω-budget and buck-converter findings on Trey's board have no counterpart in the reference; they are the cost of adding the 345 mA OLED. | §1 | — |

## 10. Comparison — Pod reference vs WavetableController rev 3

| Item | Daisy Pod Rev5 (reference) | WavetableController rev 3 | Match / deviation | Improvement or regression? |
|---|---|---|---|---|
| LED drive topology & current | Common anode on `+3V3_D`, cathode → 1 k 0402 → GPIO sink. Red 1.2–1.3 mA, G/B 0.2–0.5 mA (0 at Vf max). Same Seed pins 24/25/26/27/30/31. | GPIO → 1 k → MMBT3904 low-side switch; LED → 300 Ω 0603 → `/+9V_FLAG` ≈ 5.8 V. Red 12 mA, G/B 8 mA (Würth Vf). | **Deviation** (12 extra parts + a second rail) | **Improvement in brightness** (≈10–20×) and bin-independence (5.8 V ≫ 3.8 V Vf max) — at the cost of the polarity/footprint/rail questions R3-P2-01/02/04 that the Pod's trivial circuit cannot have. The Pod proves the 1 k-to-3V3 fallback is viable if dim G/B is acceptable. |
| LED resistor dissipation | ≤ 1.7 mW in 1/16 W (3 %) | 43 mW red / 19–24 mW G/B in 0603 1/10 W (43 %); 101 mW if moved to the 7.7 V node | Deviation | Both within rating; Trey's margin is 14× thinner and depends on which node the LEDs end up on. |
| Encoder / button filtering | None: no pull-up, no RC; internal pull-up + libDaisy debounce; runs 37–63 mm, 8–10 mil | None (R3-P3-03); encoder clicks 170.6 / 190.6 mm, 0.3 mm, 6–10 vias | **Match** in topology | Neutral; Trey's runs are 3–5× longer for the same unfiltered input — the reference shows the stock driver copes, but the reference is a 90 mm board. |
| SD socket decoupling | None at P1; nearest C11 35.8 mm straight / 69 mm routed; Seed → P1.4 35.3 mm / 3 vias | None at P1; C1 120.2 mm; A1.38 → C1 110.9 mm (R3-P2-10) | **Match** (same omission) | **Regression** in distance (3.4×). R3-P2-10's "add 100 nF + 10 µF at P1" goes beyond the reference, which is why it is a judgment, not a violation. |
| `+3V3_D` trunk | 109.7 mm total copper, 0.4064 mm (16 mil), 7 vias, longest path 57 mm (69 mΩ); one 100 nF (C11) | 249 mm @ 0.3 mm, 8 vias, 0.41 Ω end-to-end; one 100 nF (C1) | Deviation in geometry, match in cap count | **Regression**: 2.3× the length, 26 % narrower, 6× the resistance, same single 100 nF. Rev 3's 0.1 → 0.3 mm fix brought the width to within 26 % of the reference. |
| `+3V3_A` | One 100 nF (C60) at the amp; pots + amp + header; U1.21 → U4.6 46 mm | One 100 nF (C5) at the amp, 38 mm from A1.21; + MAX9814 behind FB2/C13 2.2 µF; 4.8 mm of 0.1 mm trace (F-004) | Match in decoupling | Neutral (Trey adds a mic amp with its own filtering; the 0.1 mm remnant is his own zero-margin item). |
| TPA6110A2 decoupling | C60 100 nF 3.1 mm, C56 100 nF 2.8 mm; **no ≥ 10 µF** | C5 100 nF 5.6 mm, C4 BYPASS; **no ≥ 10 µF** (R3-P2-11) | **Match** | Neutral — both omit the datasheet electrolytic. The finding stands against both boards; Trey's is not worse than the reference. |
| TPA6110A2 network | 22 k / 33 k (1.5 V/V), 470 nF in, 100 µF out, SHUTDOWN = GND, volume pot at the amp input, no bleed R, no 5 pF (not required at 33 k) | Identical values and pot placement; + 10 k bleed R22/R23 on the outputs; no 5 pF | Match + one addition | **Improvement** (bleed resistors). The Oct-7 "add 5 pF" item is optional per SLOS314B for Rf = 33 k on both boards. |
| MIDI | IN only: Type A TRS (0 Ω selectors), 220 Ω, NSR1020, H11L1, 270 Ω pull-up; **no OUT** | IN identical (0 Ω / 220 Ω / H11L1 / D1 / 270 Ω); + OUT 10 Ω / 33 Ω (R4 1210 for short survival) | Match + addition | **Improvement** (MIDI OUT exists; R4 sized for an output short). |
| Power entry | **None on the Pod**: Seed powered by its own USB or P2.11; Pod USB VBUS → ESD reference only; no bulk caps, no beads, no diodes | 9 V barrel → Schottky bridge → FB3-5 → D6 → FB6 → two 3.3 Ω/100 µF π-filters → VIN ≈ 6.4–7.1 V and `/+9V_FLAG` ≈ 5.8 V; 700 µF; USB VBUS → ESD only | **Deviation by necessity** (the 345 mA OLED cannot run from the Seed's 3v3) | Mixed: the data-only USB matches the reference exactly; everything else (inrush R3-P2-05, redundant D6 / four beads R3-P2-06, load-dependent rails) is new surface area with no reference precedent — simplification there costs nothing in fidelity to the Pod. |
| Pots on ADC | 2 × 10 k to `+3V3_A`, no RC, 31 mm to pins 28 / 22 | no control pots | N/A | — |

**Where Trey's board matches the reference:** data-only USB, single-ground, 47 k SD pull-ups, one-100 nF-per-rail decoupling, no SD-socket cap, no encoder/button filtering, TPA6110A2 values and missing electrolytic, MIDI IN stage, the six LED pins.
**Where it deviates:** LED drive (brighter, more parts, more risk), 3V3_D trunk geometry (longer, narrower), power entry (barrel + bridge + filters, required by the OLED), additions (MIDI OUT, output bleed resistors, mic amp, OLED buck).
**Net:** the deviations that are regressions (trunk length/resistance, SD cap distance) are consequences of board size, not of circuit choices, and are the ones R3-P2-10 already targets; the deviations that are additions are improvements; the LED redesign is an improvement in output but is where every rev-3 VIOLATION in this domain lives.

## Summary (one line per finding)

- DP-P2-01 PASS — Pod has no power input of its own; USB VBUS feeds only the ESD clamp; VIN only via the DNI header; Seed runs from its own USB. Trey's data-only USB matches.
- DP-P2-02 JUDGMENT — no cap at the microSD socket; nearest 100 nF 36 mm straight / 69 mm routed (Trey: 120 mm).
- DP-P2-03 JUDGMENT — one 100 nF per rail, no bulk on `+3V3_D` or `+3V3_A`; tolerable on a 90 mm board, copied onto Trey's 165 mm one.
- DP-P2-04 PASS — 16 mil power copper, ≤ 69 mΩ end-to-end, loads < 20 % of IPC-2221 capacity.
- DP-P2-05 JUDGMENT — LED drive 3V3_D / 1 k / GPIO sink: red 1.2–1.3 mA, G/B 0.2–0.5 mA; "dim" confirmed; GPIO and resistor loading trivial; 3.3 V-only pins harmless.
- DP-P2-06 ZERO-MARGIN — green/blue Vf 3.1 V typ / 3.8 V max against a 3.3 V supply: a high-Vf bin draws 0 mA.
- DP-P2-07 JUDGMENT — CLVBA-FKA pad assignment and Vf unverified (datasheet hosts blocked); CLS6B figures used as a same-family proxy.
- DP-P2-08 JUDGMENT — encoder/buttons with no pull-up or RC despite Bourns' suggested filter; libDaisy target configuration; Trey matches.
- DP-P2-09 PASS — pots on `+3V3_A` to ADC pins 28/22, no RC, 31 mm; no counterpart on Trey's board.
- DP-P2-10 JUDGMENT — TPA6110A2 ≥ 10 µF electrolytic absent on the Pod as on Trey's board (SLOS314B re-fetched and quoted).
- DP-P2-11 PASS — TPA6110A2 bypass/Eq. 6/gain/SHUTDOWN/output caps per datasheet; 5 pF not required at Rf = 33 k (downgrades the Oct-7 item to optional); Trey's bleed resistors are an addition.
- DP-P2-12 PASS — MIDI IN Type A with 220 Ω / NSR1020 / H11L1 / 270 Ω; no MIDI OUT on the Pod; Trey's OUT is an addition.
- DP-P2-13 PASS/N/A — no 9 V path, no bulk supply caps, no beads: the rev-3 inrush, series-element and buck findings have no reference counterpart.
