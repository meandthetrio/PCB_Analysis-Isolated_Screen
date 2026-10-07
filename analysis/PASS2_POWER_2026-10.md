# Pass 2 — Power Distribution, Round 2 (2026-10 files)
**Date:** 2026-10-07 · **Truth checked:** `.kicad_sch` netlist for topology, `.kicad_pcb` for copper and distances (single truth, F-036), 2026-10-06 BOM for part ratings · **Status: COMPLETE** with a threshold caveat (§7).

## 1. Rail topology (from the netlist — all new since the fabbed board)

```
J1 9 V barrel ─ SW1 ─ D2–D5 Schottky bridge ─ Net-(D2-K) [C14 100n] ─ FB3 ─ FB4 ─ FB5 ─ Net-(D6-A) [C15 100µ, C16 100n]
   ─ D6 Schottky ─ FB6 ─ Net-(C19-Pad1) [C19 100µ]
        ├─ R29 3.3Ω ─ [C17 100µ] ─ R30 3.3Ω ─ /DSY_VIN [C18 100µ] ─ A1.39 Daisy VIN          (Daisy branch)
        └─ R31 3.3Ω ─ [C20 100µ] ─ R32 3.3Ω ─ /+9V_FLAG [C21, C22 100µ]                       (display + LED branch)
                                                  ├─ FB7 ─ U6 TPS62172 VIN=EN [C25 10µ] ─ SW ─ L1 2.2µH ─ /+3V3_OLED [C26 22µ … C24 100µ, C23 100n at J8] ─ J8.2 OLED VDD
                                                  │        FB ← R33 47k / R34 15k divider;  VOS ← /+3V3_OLED;  PG n/c
                                                  └─ R21, R24–R28 300Ω ─ LED1/LED2 cathodes (anodes on Daisy GPIO 24/25/26/27/30/31)   ← F-018 unchanged
A1.38 3v3 digital ─ /+3V3_D [C1 100n only] ─ P1 SD card, U1 MIDI opto, R7–R11 47k SD pull-ups, R4/R6
A1.21 3v3 analog  ─ /+3V3_A [C5 100n] ─ U3 TPA6110A2, FB2 ─ Net-(U4-VDD) [C13 2.2µ] ─ U4 MAX9814
USB VBUS ─ /+5V_USB ─ U2 ESD only (data-only USB, not-a-finding)
```
Round 1's `/+9V_FILT`, `/OLED_HOT`, FB4-as-OLED-feed and the I2C OLED are gone. The 9 V path is now a two-stage 3.3 Ω / 100 µF RC ladder per branch (f_c ≈ 480 Hz per stage) — the "noise fix" moved from the OLED branch into the main supply.

## 2. Current budget and voltage budget (computed; loads from the sources in §7)

| Load | Current | Source |
|---|---|---|
| Daisy Seed (VIN) | ≈ 100–140 mA (community bench figures; no official number) | §7 |
| NHD-2.7-12864WDW3 at 3.3 V | **345 mA typ / 375 mA max, 100 % pixels on**; 215 mA at 50 % | §7 (datasheet via search) |
| → TPS62172 input at V_IN ≈ 6 V, η ≈ 0.9 | **≈ 190–230 mA** (3.3 × 0.345…0.375 / (0.9 × 6)) | computed |
| LEDs if they worked (6 × 20 mA) | up to 120 mA | Cree abs max |
| **Main path (bridge, FB3–FB6, D6)** | **≈ 0.30 A typical, ≈ 0.49 A worst** | sum |

Voltage budget at the worst case (0.49 A main path, 9.0 V in): bridge 2 × ≈0.45 V, D6 ≈ 0.45 V, four beads × 0.45 Ω DCR × 0.49 A ≈ 0.9 V, then per branch 6.6 Ω × I. Daisy VIN ≈ 9 − 0.9 − 0.45 − 0.9 − 6.6 × 0.14 ≈ **5.8 V**; U6 VIN ≈ 9 − 2.25 − 6.6 × 0.23 ≈ **5.2 V**. Both above the Daisy's 5 V minimum (v1.1.5 datasheet; 4 V in v1.0.5) and the TPS62172's 3 V minimum, but the margin is thin for a nominal 9 V adapter sagging under load.

## 3. Findings

### F-049 — VIOLATION, confirmed: C25 (10 µF **6.3 V**, LCSC C1691) sits on the TPS62172 input node (~5–8.5 V)
`Net-(U6-EN)` = U6 VIN = FB7 output from `/+9V_FLAG`. Node voltage is 9 V minus the drops in §2: 5.2–8.5 V depending on load. BOM line "10uF 6.3V X5R ±20% 0603, C25, C1691" (Samsung CL10A106MQ8NNNC, 6.3 V). A ceramic at or above its rated voltage loses most of its capacitance and can fail short. **Fix:** 10 µF ≥ 16 V (0805 X5R/X7R) — this is the input cap the TPS6217x reference design calls for.

### F-050 — VIOLATION, plausible (bead rating from BOM, load from datasheet via search): FB3, FB4, FB5, FB6 (0603, **200 mA**, 450 mΩ, LCSC C1002) carry the whole board's 9 V current in series
All four beads are in the single path before the Daisy/display split, so each sees ≈ 0.30 A typical and ≈ 0.49 A with the display fully lit (+ LEDs). 150–245 % of rating: saturation (no filtering), heating, and 0.9 V of DCR drop. **Fix:** one bead rated ≥ 1 A (or delete three of the four; a single bead plus the RC ladder is already more filtering than the Round 1 board had).

### F-051 — VIOLATION, plausible: R31 / R32 (3.3 Ω, 0603, 100 mW) dissipate 95 mW at the display's typical current and up to 280 mW worst case
P = 3.3 Ω × I²: 0.19 A → 120 mW, 0.23 A → 175 mW, with LEDs 0.35 A → 400 mW. Over the 0603 rating whenever the display is on. R29/R30 (Daisy branch, 0.14 A → 65 mW) are inside rating but at 65 %. **Fix:** 1206 or 2512 1 Ω–3.3 Ω (≥ 0.5 W), or move the display branch off the RC ladder entirely (a buck does not need a 6.6 Ω series filter).

### F-052 — VIOLATION, confirmed: LED drive is unchanged from Round 1 (F-001/F-018 carry forward)
Netlist: LED anodes (symbol pins AR/AG/AB) on Daisy GPIO 24, 25, 26, 27, 30, 31; cathodes through 300 Ω to `/+9V_FLAG` (≈ 6–8.5 V). Permanently reverse-biased; reverse voltage 3–8.5 V vs the Cree CLS6B-FKW absolute maximum **V_R = 5 V**; pins 24, 25, 30 are on the datasheet's **3.3 V-only** list (24, 25, 28, 29, 30). Only the source net was renamed (`/+9V_FILT` → `/+9V_FLAG`). The LEDs are still absent from the BOM (F-002), so the physical boards will simply have no LEDs. Caveat: the physical pin-to-anode mapping of the Cree package is from the community KiCad symbol; the Cree PDF could not be fetched (§7). If the symbol were reversed the LEDs would instead be permanently on with no off state — broken either way. **Fix:** GPIO → ≈1 kΩ → LED → GND per the Daisy reference circuit.

### F-053 — JUDGMENT: TPS62172 (fixed 3.3 V) wired with an adjustable-version feedback divider
R33 47k / R34 15k on FB gives 0.8 V × (1 + 47/15) = 3.31 V — the TPS62170 (adjustable) topology. On the fixed TPS62172 the datasheet says FB is internally pulled down and should be tied to AGND; the divider is 53 µA of dead load, harmless, but it signals that the schematic was drawn for TPS62170 and the BOM says TPS62172 (C59873). Pick one: TPS62170 + divider, or TPS62172 with FB to GND and R33/R34 deleted. Other checks: EN tied to VIN (allowed), VOS to output ✓, PG floating (open-drain, OK), L1 2.2 µH / Cin 10 µF / Cout 22 µF match the reference LC. Layout: Cin 4.4 mm from VIN ✓; **SW → L1 8.3 mm** (long for the switch node; datasheet layout text not fetched); L1 → Cout 1.7 mm ✓; `/+3V3_OLED` 45 mm of 0.5 mm to J8 with C24 100 µF + C23 100 nF at the connector ✓. Cout C26 is 22 µF 6.3 V 0603 X5R — at 3.3 V DC bias expect roughly half the nominal capacitance (plausible, derating curve not fetched).

### F-054 — JUDGMENT: `/+3V3_D` decoupling is still one 100 nF (F-019 partially addressed)
Trunk is now 0.3 mm throughout (246 mm, 0.40 Ω end-to-end vs ≈ 1.2 Ω before), which fixes the resistive half of F-019. The capacitive half is unchanged: the only cap is C1 at the MIDI opto; the SD card VDD (P1.4) is **120 mm** from it and the Daisy 3v3 pin 111 mm. SD write bursts still see a long uncapped stub. **Fix:** 100 nF + 10 µF at P1.

### F-055 — Passes (cited)
- AGND (A1.20) and DGND (A1.40) both on GND ✓ (datasheet requirement).
- VIN stays inside the Daisy range in the §2 budget ✓ (5.8 V worst case vs 5–17 V).
- All 100 µF electrolytics (C3339) are **35 V** ✓ on 9 V nodes; C26 22 µF 6.3 V on 3.3 V ✓; C9/C13 2.2 µF 10 V, C12 4.7 µF 10 V on 3.3 V ✓.
- Rail copper: `/DSY_VIN`, `/+9V_FLAG`, D6/C19/C20 nets all 0.5 mm (IPC-2221 ≈ 1.45 A at ΔT 10 °C) ✓; `/+3V3_OLED` 0.5 mm ✓; `/+3V3_D` 0.3 mm (≈ 1.0 A) ✓; `/+3V3_A` 4.8 mm of 0.1 mm (0.45 A) feeding only U3/U4 ✓.
- GND: one zone on both layers, 225 stitching vias, 0 unconnected ✓ (F-006 closed). The 9 single-spoke pads (F-042) are electrically connected; the ones that matter for return current (U3-3 SHDN, C9-1, C10-1, R18-1 in the headphone amp; U1-5) carry < 100 mA — JUDGMENT: fix the spoke count in layout, no functional finding.
- Local decoupling present: U3 VDD ← C5 at 5.6 mm; U4 VDD ← C13 2.2 µF at 5.7 mm; U6 VIN ← C25 at 4.4 mm; J8 VDD ← C23 at 5.3 mm; A1 VIN ← C18 100 µF at 45 mm (bulk, fine) ✓.
- TPS62172 output current 0.5 A vs display max 0.375 A ✓ (75 % — leaves no room for the boost converter option on J8 pin 3, which is N/C here).

## 4. Rail copper summary (`.kicad_pcb`)

| Net | Copper | Series R | IPC-2221 ΔT10 | Est. load | Note |
|---|---|---|---|---|---|
| Net-(D6-A)/(C19)/(C20)/(C17) | 10–22 mm @ 0.5 | 10–22 mΩ | 1.45 A | 0.30–0.49 A | ferrites/resistors dominate (F-050/051) |
| /DSY_VIN | 76 mm @ 0.5, 3 vias | 75 mΩ | 1.45 A | 0.14 A | OK |
| /+9V_FLAG | 79 mm @ 0.5, 2 vias | 78 mΩ | 1.45 A | 0.23 A | OK |
| Net-(U6-EN) | 6.3 mm @ 0.2 | 15 mΩ | 0.74 A | 0.23 A | OK |
| Net-(U6-SW) | 6.8 mm @ 0.2 | — | 0.74 A | 0.5 A pk | SW node long (F-053) |
| /+3V3_OLED | 53 mm (45 @ 0.5) | 61 mΩ | 0.74 A | 0.375 A | 23 mV drop ✓ |
| /+3V3_D | 246 mm @ 0.3, 8 vias | 404 mΩ | 1.0 A | ≈0.15 A | 60 mV drop; no local caps (F-054) |
| /+3V3_A | 51 mm (40 @ 0.5) | 73 mΩ | 0.45 A | < 0.1 A | OK |

## 5. Round 1 power findings — status against Round 2
F-001/F-018 **persist** (F-052). F-019 **half fixed** (F-054). F-020 **closed** (OLED damper topology gone). F-021 passes re-verified (F-055). F-042 dispositioned (F-055).

## 6. Questions for Trey
- Q-R2-2: Was the display branch meant to share the 3.3 Ω/100 µF ladder? The buck tolerates ripple; the resistors do not tolerate 0.2–0.4 A.
- Q-R2-3: TPS62170 (adjustable) or TPS62172 (fixed)? The schematic says one, the BOM the other (F-053).
- Q-R2-4: Are the LEDs meant to be populated this round? If yes, F-052 must be fixed first.

## 7. Threshold provenance caveat
The egress policy blocked every datasheet host tried: `ti.com`, `daisy.audio`, `daisy.nyc3.cdn.digitaloceanspaces.com`, `electrokit.com`, `cree-led.com`, `downloads.cree-led.com`, `newhavendisplay.com`, `datasheet.octopart.com`. Values above come from search-engine extracts of those datasheets (TPS6217x: VIN 3–17 V, 0.5 A, fixed-version FB note, 10 µF/2.2 µH/22 µF reference; Daisy v1.1.5: VIN 5–17 V, 3.3 V-only pins 24/25/28/29/30; Cree CLS6B-FKW v5: V_R 5 V, I_F 30/20/20 mA, V_F 2.1/3.1/3.1 V; NHD-2.7-12864WDW3: 345/375 mA at 3.3 V) plus LCSC listings for C1691 (6.3 V), C59461 (6.3 V), C3339 (35 V), C1002 (200 mA). Findings that depend only on BOM + netlist (F-049, F-052 topology, F-053 divider) are **confirmed**; those that also depend on the display current (F-050, F-051) are **plausible** until the Newhaven PDF is read directly. Add those domains to the environment's allowed list to close them.
