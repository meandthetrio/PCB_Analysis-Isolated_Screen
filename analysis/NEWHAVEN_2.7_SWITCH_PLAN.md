# Newhaven 2.7" (NHD-2.7-12864WDW3) vs. the Crystalfontz Rev-2 Plan

*Compiled 2026-09-11. Companion to `REV2_OLED_PLAN.md` (the Crystalfontz CFAL12864G-024W plan).
Sources: NHD-2.7-12864WDW3 datasheet rev.6 (07/31/2024), Newhaven's official example code
(github.com/NewhavenDisplay/NHD-2.7-12864WD_Example), and the BAKER firmware at branch
`CUZ_AUG_WRAPUP`. Status: DISCUSSION ONLY — no PCB or firmware files modified.*

---

## 0. Correction first

The Newhaven 2.7" is **not** an SSD1309 part. It is an **SSD1322** — a 256×64,
**4-bit grayscale** controller driving this 128×64 panel with each visible pixel doubled
horizontally. And the SSD1322 **has no I2C mode at all**: interfaces are 8-bit parallel
(6800/8080), 3-wire SPI, or 4-wire SPI, selected by the BS1/BS0 straps (4-wire SPI =
both low). So "switch the screen" here means **switching the bus, the controller
protocol, and the frame format**, not just the glass. The user's instinct that this is a
move to SPI is right — it's forced.

## 1. Side-by-side

| | Crystalfontz CFAL12864G-024W (current rev-2 plan) | Newhaven NHD-2.7-12864WDW3 |
|---|---|---|
| Form | Bare chip-on-glass panel | PCB **module** with metal bezel |
| Size / active area | 2.42", AA 55.01 × 27.49 mm | 2.7", AA 61.41 × 30.69 mm (VA 63.41 × 32.69) |
| Outline | Glass 60.5 × 37.0 × 2.15 mm | Module 82 × 47.5 mm, ~5.5 mm max thickness |
| Mounting | **None** — tape/gasket/bezel frame (see `screen mounting solution.md`) | **4× Ø2.5 mm corner holes** + bezel |
| Connection | 31-pin 0.5 mm FPC tail → ZIF connector; orientation + 18 mm reach risks | **1×20 pin header, 2.54 mm pitch** (Ø1.0 holes, 48.26 mm span) |
| Controller | SSD1309 (1bpp, 128×64 native) | SSD1322 (4bpp grayscale, 256×64 mapped) |
| Bus | I2C @ 0x3C (Daisy pins unchanged from HiLetgo) | SPI only (4-wire recommended); **no I2C** |
| Panel VCC | 12.5 / **13.0** / 13.5 V | 14.5 / **15.0** / 15.5 V |
| Panel current (100% on) | 15–22 mA @ 50% px; ~50 mA budget | **60 typ / 70 max mA** (VCC=15V, 100% on) |
| Logic VDD | 3.3 V + I2C pull-ups (F-027!) | 3.0–3.5 V, 180–300 µA in ext-VCC mode; **no pull-ups needed** |
| Boost converter | None anywhere (whole point of rev 2) | On module, but **bypassable via jumper** (move R4→R7): "Jumper Option #2", external VCC, boost unused |
| Support parts on our PCB | IREF 1MΩ, VCOMH 1µF, caps, straps, pull-ups | Already on module — our side is header + power filter |
| Full frame payload | 1,024 bytes (1bpp) | **8,192 bytes** (4bpp, pixel-doubled) |
| Bus ceiling | I2C 400 kHz → ~22 ms/frame | SPI t_cycle ≥ 300 ns → **≤ ~3.3 MHz** → ~20 ms/frame. Parity, not a speedup |
| Frame semantics | 8 pages, page addressing | Column/row window (col 0x1C–0x5B, row 0x00–0x3F) + RAM-write stream; partial windows possible |
| Extra capability | — | 16-level grayscale (future anti-aliased UI) |
| Approx. unit cost | ~$10–15 (check current) | ~$35–45 (check current) |

**Net:** the Newhaven keeps the rev-2 acoustic goal intact (boost bypassed → same
silent linear-regulator architecture), *demolishes* the two riskiest mechanical steps
(ZIF orientation, tail reach) and the F-027 pull-up landmine, and gives a bigger screen —
in exchange for a **harder power spec (15 V)**, **3 more MCU pins**, a board-wide pin
reshuffle, ~3× part cost, and a firmware transport/format rewrite.

## 2. Power — the one genuinely hard problem

The rev-2 premise was: 15 V adapter → Schottky bridge (−0.7 V) → ~14.3 V → LDO → 13.0 V.
**That collapses for the Newhaven: 14.3 V is below the panel's 14.5 V minimum.**

Options, best first:

1. **16 V adapter + low-drop screen branch.** Keep the existing bridge for the
   Daisy/audio side (16 − 0.7 ≈ 15.3 V; still under the Daisy's 17 V VIN max — verify
   against current Electrosmith datasheet). For the screen branch, bypass the bridge:
   tap the jack through a single Schottky (−0.3–0.4 V → ~15.6 V) or a P-FET ideal-diode
   (~15.9 V), then a true LDO set to 15.0 V. Headroom 0.6–0.9 V at ≤70 mA →
   ~40–65 mW in the LDO. Comfortable.
2. **16 V adapter, LDO after the existing bridge** (15.3 V → 15.0 V): only ~0.3 V
   headroom — below dropout for most LDOs at 70 mA. Marginal; avoid.
3. **18 V adapter**: bridge output ~17.3 V exceeds Daisy VIN max. Rejected.
4. **Jumper Option #1** (module boost fed from clean 5 V): reintroduces a
   content-dependent switcher — the exact rev-1 villain. Rejected.
5. Default jumper (single 3.3 V, boost on): 345 mA typ @ 3.3 V *and* the switcher.
   Doubly rejected.

Note: in external-VCC mode the module's `/SHDN` pin is a no-op (it only controls the
boost). VDD-before-VCC sequencing is still the polite order, so the rev-2 plan's
optional high-side P-FET on the screen VCC branch carries over unchanged — but see the
pin ledger below for what it costs now.

## 3. Pins — SPI must evict three signals

Board reality (from `WavetableController.kicad_pcb`, Daisy = A1):

- Hardware SPI1 pads: **9** (SCK/D8) = `/ENCR_B`, **11** (MOSI/D10) = `/ENCL_CLICK`,
  **8** (D7, conventional CS) = `/ENCR_A`. Pad **10** (MISO/D9) = `/TAC_SHIFT_R` —
  the display is write-only, MISO is not needed, so **TAC_SHIFT_R stays put**.
- Freed by dropping I2C: pads **12, 13**.
- Existing spares: pads **22, 28** (the last two, both ADC-capable).

Ledger: consumers = SCK(9), MOSI(11), CS(8), D/C(any), /RES(any), plus rehoming
ENCR_A, ENCR_B, ENCL_CLICK → **5 free-choice slots needed, 4 available (12, 13, 22, 28)**.
One short. Closers, pick one:

- **Tie /CS low** (recommended): SPI1 is exclusive to the display (SD card is on SDMMC),
  and the SSD1322 tolerates a grounded CS. Pad 8 then rehomes a displaced encoder signal.
- RC power-on reset on /RES instead of a GPIO — but rev-2 §8 wants firmware-driven
  re-init as EMI insurance, so keep /RES on a pin if possible.
- Reclaim `/USART1_TX` (pad 14) **only if** MIDI OUT is confirmed unused — verify first.

Even after closing the gap, **both last ADC-capable spares get consumed**, and the
optional VCC P-FET has no pin left unless one of the other closers is also taken. Sign
off deliberately (same warning as rev-2 §4, now binding).

Suggested layout: keep the displaced *digital* signals on 12/13 + pad 8, preserving one
ADC-capable pad if the ledger allows.

## 4. Module wiring table (4-wire SPI, Jumper Option #2)

On-module jumpers: **open R4, close R7** (0Ω move; one solder step per unit — a real,
if small, production cost). BC_VDD (pin 3) unused.

| Header pin | Signal | Goes to |
|---|---|---|
| 1 | VSS | GND |
| 2 | VDD | +3V3_D (180–300 µA) |
| 3 | NC (BC_VDD) | — |
| 4 | D/C | Daisy GPIO (from pin ledger) |
| 5, 6 | VSS | GND |
| 7 | SCLK | Daisy pad 9 (D8, SPI1 SCK) |
| 8 | SDIN | Daisy pad 11 (D10, SPI1 MOSI) |
| 9 | NC | — |
| 10–14 | VSS | GND |
| 15 | VCC | +15.0 V screen branch (ferrite bead + 100 nF + bulk **at the header**) |
| 16 | /RES | Daisy GPIO (10 k pull-down as in rev-2 plan) or RC |
| 17 | /CS | GND (tied low) or Daisy GPIO |
| 18 | /SHDN | — (N.C. in Option #2) |
| 19 | BS1 | GND |
| 20 | BS0 | GND |

Layout guidance from `REV2_OLED_PLAN.md` §7 still applies verbatim: screen power + SPI
stay out of the center audio corridor (x≈165–200); the one-way ferrite/bulk fence at the
connector still matters because row-scan current still flutters with content.

Mechanical: module screws to standoffs via 4× Ø2.5 holes; enclosure window sized to the
**66 × 33 mm bezel opening** (VA 63.41 × 32.69). The tape/foam/3D-bezel machinery in
`screen mounting solution.md` becomes unnecessary; a foam gasket ring against the metal
bezel is still nice for light/dust sealing. Enclosure CAD needs a fresh stack-height
check for module + header + PCB, but there is no FPC reach constraint anymore.

## 5. BAKER firmware port (branch `CUZ_AUG_WRAPUP`)

Good news: the UI stack is already isolated behind one class. Every screen draws through
`OledPager : OneBitGraphicsDisplayImpl` (`src/ui/oled_pager.{h,cpp}`) — 1bpp back/front
buffers, async one-page-per-tick I2C DMA at 0x3C, `~22 ms` full frame. `UIRender`
ignores the libDaisy display object entirely (`ui_render.cpp:35`). So the port is a
transport swap inside `OledPager` plus cleanup; **no `ui_screen_*` file changes**.

1. **Delete the vestigial libDaisy display** — `main.cpp:39,103–117`
   (`OledDisplay<SSD130xI2c128x64Driver>`): with no I2C device present its init would
   just time out at boot. `OledPager` currently free-rides on that init (it only sends
   0x20/0x02 itself); the new pager owns full init instead.
2. **Transport**: `SpiHandle` SPI1, TX-only, 8-bit, DMA; prescaler for **≤3.3 MHz**
   (t_cycle ≥ 300 ns). GPIOs: D/C (+ /RES, /CS if not strapped). `SendCommand` changes
   from I2C control-prefix bytes to D/C-low writes; data = D/C high.
3. **Init sequence** (datasheet p.15 / official example): /RES low ≥200 µs, high,
   ≥200 µs, then: `AE · B3 91 · CA 3F · A2 00 · AB 01 · A0 16 11 · C7 0F · C1 9F ·
   B1 F2 · BB 1F · B4 A0 FD · BE 04 · A6 · AF`. (`0xAE/0xAF` display off/on are the
   same as SSD1309, so `SetDisplayOn` logic is untouched.)
4. **Frame transfer**: replace 8×(1+128 B) pages with: window setup
   `0x15 1C 5B · 0x75 00 3F · 0x5C`, then stream **8,192 bytes**. Keep the exact
   `TickTransferOnePage` pacing structure with 8 chunks of 1,024 B (8 rows each);
   `s_dma_buf_` grows from 129 B to 1 KB in the same D2 DMA-safe section.
5. **1bpp → SSD1322 conversion** (done per-chunk while filling the DMA buffer): each
   1-bit pixel → **one byte** `0xFF`/`0x00` (two 4-bit nibbles = the two horizontally
   doubled controller pixels). 128 px row → 128 bytes.
6. **Pin remaps in firmware**: `controls.cpp:47–49` ext encoder `GetPin(7)/(8)` and
   `main.cpp:381` encoder click `GetPin(10)` move to wherever the pin ledger lands
   (`controls.cpp:52` rshift `GetPin(9)` stays); `oled_pager.cpp:17–18` I2C pins go away.
7. Unchanged: 60 Hz dirty-flag cadence, `FlushFrameBlocking`, boot logo, blank-screen
   suppression, `RenderNowAndFlushFullFrame`. Frame time lands ~20 ms — same as today,
   so no UX regression and no promised speedup.
8. **Later, optional**: SSD1322 windowed writes enable dirty-rect partial updates, and
   the 4-bit pipeline enables 16-level grayscale UI — both are follow-ups, not port
   blockers.

Estimated scope: one focused rewrite of `oled_pager.cpp` (+ a few lines in `main.cpp`,
`controls.cpp`), then bench bring-up. The rev-2 firmware notes about periodic re-init as
catastrophic-EMI recovery carry over.

## 6. Open questions before committing

1. 16 V adapter acceptable? (Labeling + the screen-branch rectifier change in §2.)
2. Verify Daisy VIN 17 V max against the current Electrosmith datasheet rev.
3. Which pin-ledger closer: CS-to-GND (recommended) vs RC reset vs USART1_TX reclaim?
4. Is the VCC P-FET worth its pin, or is /RES + periodic re-init enough?
5. Enclosure CAD: window at 66 × 33, new stack height, standoff positions for the 4 holes.
6. Confirm current module pricing/stock and the R4→R7 jumper rework step in production.
7. Bundle the standing rev-1 fixes (F-006, F-007, F-018, 0.1 mm traces) as per rev-2 §9.
