# Pass 0 — Environment & Baselines, Round 2 (2026-10 files)
**Status: COMPLETE** (2026-10-07). Governed by `SOURCE_OF_TRUTH.md`. Round 1 (2026-08) Pass 0 is recorded in `HIGH_LEVEL_PLAN.md`; this document is the Round 2 equivalent for the new file set.

## 1. Inputs received (2026-10-07)

| File | Where stored | Notes |
|---|---|---|
| `Manifold_Gerbs.zip` → 9 Gerber layers + PTH/NPTH drills + `.gbrjob` | `Manifold_Gerbs_2026-10/` | Plotted 2026-10-07 12:54 CDT, KiCad 9.0.4, project GUID unchanged |
| `WavetableController.kicad_pcb` (31.7 MB) | repo root | Replaces the Round 1 stale copy (archived) |
| `WavetableController.kicad_sch`, `.kicad_pro` | repo root | Replace Round 1 copies (archived) |
| `ManifoldRe_BOM_NEW - Excel Format.xls` | repo root | Saved 2026-10-06; 37 lines (was 31) |

Round 1 design files and BOM moved to `archive/rev1_2026-08/`. `Manifold_Gerb_LedFix/` (plotted 2026-07-22) is untouched — it remains the fab truth for the boards that physically exist.

**Open question for Trey (Q-R2-1):** has this 2026-10 Gerber set been sent to JLCPCB, or is it the pre-fab candidate? Until answered, Round 2 treats it as a candidate: fab-related passes check it, but "fab-proven" claims only apply to the LedFix set.

## 2. Environment

- `kicad-cli` 9.0.9 / `pcbnew` 9.0.9 (Claude Code on the web, via `tools/kicad_env_setup.sh`). Design plotted on 9.0.4 — the 0.0.5 version delta produced no content differences (§3).
- `analysis/gerber_analyze.py` now takes the Gerber directory as its first argument (defaults to `Manifold_Gerb_LedFix/`). Previously hard-coded to a Mac path.
- Scratchpad DRC copy with JLCPCB minimums (`min_track_width` 0.1, `min_clearance` 0.1) created per SOURCE_OF_TRUTH rule 4; design files untouched.
- `python3 -m xlrd` installed for the `.xls` BOM.

## 3. Provenance — RESOLVED (closes F-006 / F-015)

Round 1's defining problem was that the `.kicad_pcb` did not match the Gerbers (no GND pour). Test for Round 2: re-plot Gerbers and drills from the uploaded `.kicad_pcb` with `kicad-cli` and diff against the uploaded Gerbers.

| Layer | Result (header date/version lines stripped) |
|---|---|
| F_Cu, B_Cu, F_Mask, B_Mask, F_Paste, B_Paste, F_Silkscreen, Edge_Cuts | **byte-identical** |
| PTH.drl (330 holes), NPTH.drl (28 holes) | **identical hole/tool sets** (coordinate + tool), only header formatting differs |
| B_Silkscreen (1.1 M lines) | identical as a line multiset except one redundant aperture-select line (`D10*`) — plotter ordering, no geometry change |

**Verdict:** the uploaded `.kicad_pcb` is exactly the file that produced the uploaded Gerbers. Round 2 has a **single truth**: `.kicad_sch` ↔ `.kicad_pcb` ↔ Gerbers are one consistent design snapshot. The dual-truth rule from Round 1 no longer applies to these files (it still applies when comparing against the fabbed LedFix boards).

Supporting counts: 100 schematic components (netlist) = 100 PCB footprints; 0 unconnected items in DRC; no duplicate references in either file.

## 4. Parser validation (SOURCE_OF_TRUTH rule 5)

`gerber_analyze.py` run on the new set, checked against independent raw-file counts:

| Quantity | Parser | Raw file (`grep`/`%ADD` list) | Match |
|---|---|---|---|
| PTH holes | 330 (0.25×2, 0.3×225, 0.65×2, 0.8×4, 1.0×40, 1.1×48, 1.3×4, 1.85×5) | 330 | ✓ |
| NPTH holes | 28 (0.65×2, 1.2×25, 2.0×1) + 1 slot | 28 | ✓ |
| F_Cu regions | 15 | 15 `G36` | ✓ |
| B_Cu regions | 4 | 4 `G36` | ✓ |
| Copper aperture widths | 0.1/0.2/0.3/0.5 (tracks) | `%ADD` list 0.1…2.5 | ✓ |
| PTH↔pad match | 330/330 on both layers, min annular 0.150 mm | — | — |

The parser also handled the 28 MB back-silk file without modification. pcbnew cross-check: 929 track segments / 225 vias / 1 GND zone in the board file vs 225 × 0.3 mm via drills in the drill file ✓.

## 5. Baselines (new files, archived in `analysis/baseline_2026-10/`)

### ERC — `erc_2026-10.json`
46 violations (Round 1: 207): **20 error-severity**, 26 warnings.

| n | type | disposition (preliminary, Pass 3 confirms) |
|---|---|---|
| 15 | `pin_not_connected` | 10 × P2 USB-C SuperSpeed/SBU (intentional, as Round 1 F-024), 4 × J8 pins 3/9/15/18 (new OLED connector — check against NHD-2.7-12864WDW3 pinout), 1 × U6 PG (open-drain power-good, unused) |
| 4 | `power_pin_not_driven` | A1 VIN, U4 VDD, #PWR01, U6 VIN — same false-positive pattern as Round 1 (no PWR_FLAG); U6 VIN is new |
| 1 | `label_dangling` | `SWA` — F-022 unchanged |
| 19 | `footprint_link_issues` | Trey's private libs, expected |
| 6 | `lib_symbol_mismatch` | library hygiene |
| 1 | `multiple_net_names` | — |

### DRC, project rules as-is — `drc_stock_2026-10.json`
558 violations, **0 unconnected items** (Round 1: 249 + 53 unconnected), 0 schematic-parity issues.

| n | type | sev | note |
|---|---|---|---|
| 199 | `silk_overlap` | warn | front-panel artwork (now 3,900 polygons / 1.08 M points on B.Silkscreen — the reason the board file is 31.7 MB) |
| 199 | `silk_over_copper` | warn | same |
| 49 | `silk_edge_clearance` | warn | same |
| 61 + 17 | `lib_footprint_mismatch` / `lib_footprint_issues` | warn | private libs, expected |
| 17 | `clearance` | **error** | U3 (MSOP-8) and U4 (TDFN-14) pad-to-pad 0.15 mm vs 0.2 mm netclass — same as Round 1 F-009 (DRC config noise, not fab) |
| 9 | `starved_thermal` | **error** | GND pads with 1 thermal spoke (zone requires 2): ENCR1-C, TAC_SWITCH_1-3, U1-5, P2-A12, P2-B1, R18-1, C9-1, U3-3, C10-1 → **new, F-042** |
| 5 | `copper_edge_clearance` | **error** | 3 × `/+3V3_D` F.Cu tracks at 0.451 mm from the bottom edge (y ≈ 162.1) vs 0.5 mm project rule → **new, F-041**; 2 × SW1 pads at 0.41 mm (Round 1 F-010 notch, accepted) |
| 2 | `drill_out_of_range` | **error** | U6 (TPS62172 WSON) thermal vias 0.25 mm vs 0.3 mm project min hole → **new, F-040** |

### DRC, JLCPCB minimums on scratchpad copy — `drc_jlcpcb_min_2026-10.json`
**Identical to the stock run** (558 / 0). With `min_track_width` 0.1 and `min_clearance` 0.1 there are zero `track_width` violations: the remaining 0.1 mm traces are at the limit, not below it (same reading as Round 1 F-012).

### Board statistics (pcbnew)

| | Round 1 `.kicad_pcb` (stale) | LedFix Gerbers (fabbed) | **Round 2 `.kicad_pcb` = Gerbers** |
|---|---|---|---|
| Footprints | 79 | — | **100** |
| Track segments | 816 | — | **929** |
| Track widths (segments) | 0.1: 557, 0.2: 259 | 0.1: ~549, 0.2: ~266 | **0.1: 66, 0.2: 176, 0.3: 572, 0.5: 115** |
| Total track length | 4742 mm | — | 4868 mm |
| **0.1 mm track length** | **3850 mm** | ≈ same | **73 mm** |
| Vias (0.3/0.6) | 94 | 93 | **225** |
| GND zone | none (F-006) | B.Cu pour only | **1 zone, F.Cu + B.Cu, filled (19 polygons), min width 0.25, clearance 0.5** |
| Nets | 86 | — | 103 (sch netlist: 110) |
| Board | 165.3 × 101.8 | same | same (Edge_Cuts byte-identical to LedFix) |
| Unconnected (DRC) | 53 | — | **0** |

## 6. What changed since the fabbed board (for the later passes)

Derived from footprint/net diffs (`archive/rev1_2026-08/` vs root), to be verified pass-by-pass — these are observations, not findings yet:

- **Display architecture replaced.** I2C OLED path removed (J2, `/I2C_SCL`, `/I2C_SDA`, `/OLED_HOT`, `/+9V_FILT` gone). New: **J8 = Newhaven NHD-2.7-12864WDW3** (20-pin, F.Cu) on a 4-wire SPI (`/SCLK_SPI`, `/SD_IN_SPI`, `/CS_SPI`, `/DC_SPI`, `/RES_SPI`, 88–124 mm each, 0.3 mm), powered by a dedicated **TPS62172 buck (U6)** + L1 2.2 µH + C25 10 µF + C26 22 µF + R33/R34 feedback → `/+3V3_OLED`. This moots Round 1 F-027 (I2C pull-ups), F-019/F-020 (OLED_HOT damping), and the I2C assumptions in `REV2_OLED_PLAN.md`.
- **Power entry reworked:** `/DSY_VIN` net, D6 Schottky, `/+9V_FLAG` (LED resistors R21/R24–R28 now hang off `/+9V_FLAG` via FB7 — **LED polarity question F-001/F-018 must be re-checked in Pass 2**), 4 × 3.3 Ω (R29–R32) and 5 × 100 µF (C18–C22) added, FB5–FB7 added.
- **Headphones1** dual-gang 10 k pot added (new audio path for Pass 5).
- **Encoder clicks routed:** `/ENCL_CLICK` 170.6 mm / 6 vias, `/ENCR_CLICK` 190.6 mm / 10 vias, both 0.3 mm. F-007 fixed in layout; Pass 3 re-checks the Daisy pin assignment (pin 29 3.3V-only note).
- **Duplicate R21 gone** (F-013/F-020/F-025) — single R21 in both files.
- **Trace widths:** `/+3V3_D` is now 0.3 mm throughout (was 0.1 mm, 254 mm). Remaining 0.1 mm: GND 12.8 mm, U4 fan-out (VDD/MICBIAS/CT/TH/CG/MICIN/MICOUT/BIAS ≈ 46 mm), USART1_TX 5.9, +3V3_A 4.8, USB_IN_N 3.1, USB_IN_MCU_N 1.1 mm.
- **Silkscreen:** front-panel artwork moved from F.Silkscreen (956 kB → 20 kB) to B.Silkscreen (134 kB → 28 MB).
- **BOM:** +U5 DPAK regulator (C310413) — **no U5 exists in schematic or PCB**; +U6, L1, C25, C26, R29–R34, D6, FB5–FB7, C14/C15/C17–C24 added to existing lines. S1/S2 phantom (F-003) persists; LED1/LED2 still absent (F-002) while F_Paste still carries their 12 apertures.

## 7. Round 1 findings — preliminary status against the new files

| Finding | Preliminary status (confirm in the pass named) |
|---|---|
| F-004 / F-012 0.1 mm traces | largely addressed: 3850 → 73 mm (Pass 1) |
| F-005 DRC minimums zero | **unchanged** — `min_track_width` 0.0, `min_clearance` 0.0 in new `.kicad_pro` |
| F-006 no pour / F-015 timeline / F-017 via delta | **closed** (§3) |
| F-007 encoder clicks | fixed in layout (Pass 3) |
| F-008 P2 NPTH clearance 0.194 | footprint unchanged, re-measure (Pass 1) |
| F-009 U3/U4 0.15 mm pad gaps | unchanged, still config noise |
| F-010 SW1 notch | unchanged, accepted |
| F-013 / F-020 / F-025 dup R21 | **closed** |
| F-014 LED2 sch-vs-pcb | sch and pcb now consistent (0 parity issues) — which wiring won: Pass 3 |
| F-001 / F-018 LED drive | topology changed (`/+9V_FLAG`) — re-derive (Pass 2) |
| F-019 / F-027 OLED/I2C | mooted by SPI redesign; new U6 regulator to review (Pass 2/5) |
| F-022 SWA card detect | unchanged |
| F-002 / F-003 / F-034 BOM gaps | persist on first read (Pass 4) |

## 8. New findings opened in Pass 0
F-036 … F-045 in `FINDINGS.md`.
