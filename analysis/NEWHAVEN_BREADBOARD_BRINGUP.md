# Newhaven NHD-2.7-12864WDW3 — Breadboard Bring-Up on the Daisy Pod

*Compiled 2026-09-11. Companion to `NEWHAVEN_2.7_SWITCH_PLAN.md` (the board-respin view).
This doc covers the first-hardware phase: Daisy Pod + breadboard + the Newhaven module,
and the plan for building the SSD1322 library that BAKER will eventually use.
Pin numbers are libDaisy `Dx` names (what code uses); the custom-board tables in the
switch plan use physical pads, where pad = D + 1.*

---

## 1. The SPI pinout swap

### Where BAKER's wires sit today (Pod + breadboard, branch `CUZ_AUG_WRAPUP`)

| Seed pin | Current use | Source |
|---|---|---|
| D7 | External encoder A | `controls.cpp:47` |
| D8 | External encoder B | `controls.cpp:48` |
| D9 | Right-shift button | `controls.cpp:52` |
| D10 | Pod encoder click (moved off D13 to free MIDI TX) | `main.cpp:381` |
| D11 / D12 | I2C SCL / SDA → HiLetgo OLED | `oled_pager.cpp:17-18`, `main.cpp:114-115` |
| D22 | External encoder click | `controls.cpp:49` |
| D16 | Left-shift button | `controls.cpp:59` |

Pod carrier claims (libDaisy `daisy_pod.cpp`): D13, D15, D17–D21, D23–D28 + SD + audio.
Free pins on this setup: **D0, D29, D30** (D0 = PB12, doubles as USB OTG ID — unused in
device mode, fine as GPIO).

The SSD1322 has **no I2C**; 4-wire SPI needs SCK and MOSI on the hardware SPI1 pins
(D8, D10 — fixed), plus any-GPIO for /CS, D/C, /RES. MISO is never used (display is
write-only), so **D9 keeps the right-shift button**.

### The swap — three wires move, five go to the screen

| Signal | Old pin | New pin |
|---|---|---|
| External encoder A | D7 | **D11** (freed by dropping I2C) |
| External encoder B | D8 | **D12** (freed by dropping I2C) |
| Pod encoder click | D10 | **D0** |
| — OLED /CS | — | **D7** |
| — OLED SCLK | — | **D8** (SPI1 SCK) |
| — OLED SDIN | — | **D10** (SPI1 MOSI) |
| — OLED D/C | — | **D29** |
| — OLED /RES | — | **D30** |

Everything else (D9 rshift, D16 lshift, D22 ext click, knobs, LEDs, buttons, SD, MIDI
on D13/D14) stays put. Firmware-side, the same three lines change:
`controls.cpp:47-48` (7→11, 8→12) and `main.cpp:381` (10→0).

On the phase-1 standalone bring-up app (below) no controls exist at all, so only the
five OLED wires matter; do the encoder rewiring when BAKER itself moves over.

## 2. 20-pin header wiring (breadboard)

Fit a 1×20 2.54 mm header (module holes: Ø1.0 mm, 48.26 mm span — standard breadboard
pitch). Two power configurations; **signal wiring is identical in both**.

### Signals (both configurations)

| Header pin | Name | Wire to |
|---|---|---|
| 4 | D/C | Seed **D29** |
| 7 | SCLK | Seed **D8** |
| 8 | SDIN | Seed **D10** |
| 16 | /RES | Seed **D30** |
| 17 | /CS | Seed **D7** (GPIO now; the tie-low experiment comes later) |
| 19 | BS1 | **GND** } |
| 20 | BS0 | **GND** } BS1=0, BS0=0 → 4-wire SPI |
| 1, 5, 6, 10, 11, 12, 13, 14 | VSS | GND |
| 9 | NC | — |
| 3 | BC_VDD | — (leave open) |
| 18 | /SHDN | — (leave open; internally pulled high) |

Logic levels: VIH = 0.8×VDD, so with VDD = 3.3 V the Seed's 3.3 V GPIOs are directly
compatible. Common ground between Pod, module, and any bench supply is mandatory.

### Power configuration A — quick start (fresh module, default jumpers, boost ON)

For first light only. The onboard boost is the noise villain we're eliminating, but on
a breadboard nobody cares, and it needs **no module rework and no 15 V supply**.

- Pin 2 (VDD): **3.3 V from an external supply rated ≥ 500 mA** — datasheet: 345 mA
  typ / 375 mA max at 100 % pixels. **Do NOT power this from the Seed's 3V3 pin**; the
  Seed's regulator won't carry it.
- Pin 15 (VCC): leave open (module default: N.C.).
- Decoupling at the header: 100 nF + ≥10 µF on VDD.

### Power configuration B — representative test (Jumper Option #2, boost OFF)

The final architecture. Requires the one-time module rework: **move the 0Ω from R4 to
R7** (open R4, close R7 — jumpers pictured on datasheet p.5).

- Pin 2 (VDD): 3.3 V — now only 180–300 µA, so the **Pod's 3V3 pin is fine**.
- Pin 15 (VCC): **15.0 V bench supply** (spec 14.5–15.5 V), 60–70 mA max at 100 % on.
  Set a ~100 mA current limit for comfort.
- Decoupling at the header: 100 nF + ≥100 µF on VCC, 100 nF + 2.2 µF on VDD.
- Power-up order: 3.3 V first, then 15 V; reverse on power-down (VDD-before-VCC
  sequencing, same etiquette as the rev-2 plan).

Config A answers "does my code work"; config B answers "does the real architecture
work and how does it sound" — do A first, then rework the jumpers once, stay on B.

## 3. Building the SSD1322 library

### Shape of the finished thing

BAKER's UI never touches the bus: every screen draws through
`OledPager : OneBitGraphicsDisplayImpl` (1bpp back buffer, async chunked transfer).
So "the library" is: a thin SSD1322-over-SPI transport + init + a frame pusher that
expands 1bpp → SSD1322 bytes, packaged behind OledPager's existing public API. Build
it in four phases, each independently testable.

### Phase A — blocking hello (standalone app, no BAKER)

A minimal Daisy program: init SPI, reset, init sequence, push test patterns. Skeleton:

```cpp
#include "daisy_pod.h"
using namespace daisy;

DaisyPod hw;
SpiHandle spi;
GPIO cs, dc, res;

constexpr Pin PIN_CS  = seed::D7;
constexpr Pin PIN_DC  = seed::D29;
constexpr Pin PIN_RES = seed::D30;

static void SpiWrite(const uint8_t* buf, size_t n, bool is_data)
{
    dc.Write(is_data);
    cs.Write(false);
    spi.BlockingTransmit(const_cast<uint8_t*>(buf), n);
    cs.Write(true);
}
static void Cmd(uint8_t c) { SpiWrite(&c, 1, false); }
static void Dat(uint8_t d) { SpiWrite(&d, 1, true); }

static void OledInit()
{
    res.Write(false); System::DelayUs(250);   // /RES low >= 200us
    res.Write(true);  System::DelayUs(250);   // wait >= 200us before commands

    Cmd(0xAE);                                // display off
    Cmd(0xB3); Dat(0x91);                     // clock divide / osc freq
    Cmd(0xCA); Dat(0x3F);                     // mux ratio 64
    Cmd(0xA2); Dat(0x00);                     // display offset
    Cmd(0xAB); Dat(0x01);                     // internal VDD regulator
    Cmd(0xA0); Dat(0x16); Dat(0x11);          // remap (adjust A[1]/A[4] to flip)
    Cmd(0xC7); Dat(0x0F);                     // master contrast
    Cmd(0xC1); Dat(0x9F);                     // contrast current
    Cmd(0xB1); Dat(0xF2);                     // phase length
    Cmd(0xBB); Dat(0x1F);                     // precharge voltage
    Cmd(0xB4); Dat(0xA0); Dat(0xFD);          // VSL
    Cmd(0xBE); Dat(0x04);                     // VCOMH
    Cmd(0xA6);                                // normal display
    Cmd(0xAF);                                // display on
}

// pagebuf: 1024 bytes in SSD1306 page layout (OledPager's format:
// byte = 8 vertical pixels, page-major) -> SSD1322 4bpp stream.
// Each 1-bit pixel becomes ONE byte (0xFF/0x00): two 4-bit nibbles = the
// two horizontally-doubled controller pixels behind one visible pixel.
static void PushFrame(const uint8_t* pagebuf)
{
    Cmd(0x15); Dat(0x1C); Dat(0x5B);          // column window 28..91
    Cmd(0x75); Dat(0x00); Dat(0x3F);          // row window 0..63
    Cmd(0x5C);                                // write RAM
    uint8_t row[128];
    for(int y = 0; y < 64; y++)
    {
        const uint8_t* page = &pagebuf[(y >> 3) * 128];
        const uint8_t  mask = 1u << (y & 7);
        for(int x = 0; x < 128; x++)
            row[x] = (page[x] & mask) ? 0xFF : 0x00;
        SpiWrite(row, 128, true);             // 8192 bytes total ≈ 21 ms
    }
}

int main(void)
{
    hw.Init();
    cs.Init(PIN_CS, GPIO::Mode::OUTPUT);   cs.Write(true);
    dc.Init(PIN_DC, GPIO::Mode::OUTPUT);
    res.Init(PIN_RES, GPIO::Mode::OUTPUT); res.Write(true);

    SpiHandle::Config scfg;
    scfg.periph         = SpiHandle::Config::Peripheral::SPI_1;
    scfg.mode           = SpiHandle::Config::Mode::MASTER;
    scfg.direction      = SpiHandle::Config::Direction::TWO_LINES_TX_ONLY;
    scfg.datasize       = 8;
    scfg.clock_polarity = SpiHandle::Config::ClockPolarity::LOW;   // SPI mode 0
    scfg.clock_phase    = SpiHandle::Config::ClockPhase::ONE_EDGE;
    scfg.nss            = SpiHandle::Config::NSS::SOFT;            // CS is our GPIO
    scfg.baud_prescaler = SpiHandle::Config::BaudPrescaler::PS_64; // ~1.6 MHz first light
    scfg.pin_config.sclk = seed::D8;
    scfg.pin_config.mosi = seed::D10;
    // miso/nss left unconfigured - TX-only, soft NSS
    spi.Init(scfg);

    OledInit();
    Cmd(0xA5);                 // smoke test: ALL PIXELS ON, no RAM writes needed
    System::Delay(1000);
    Cmd(0xA6);

    static uint8_t fb[1024];
    uint32_t t = 0;
    for(;;)
    {
        for(int i = 0; i < 1024; i++)        // page-layout checkerboard
            fb[i] = ((i + (t & 1)) & 1) ? 0xAA : 0x55;
        PushFrame(fb);
        t++;
        System::Delay(500);
    }
}
```

Notes:
- `0xA5` (entire display on) right after init is the best first-light test — it proves
  power + reset + init + bus polarity before any RAM addressing can be wrong.
- Start at PS_64 (~1.6 MHz); once solid, move to **PS_32 (~3.1 MHz)** — the SSD1322
  serial spec floor is 300 ns/cycle (~3.3 MHz max), so that's the ceiling. Full frame
  lands ~20 ms, same ballpark as today's I2C path.
- Put this app in its own folder with its own Makefile (same pattern as libDaisy
  examples), e.g. `tools/oled_bringup/` in the BAKER repo, so it never entangles with
  the sampler build.

### Phase A verification checklist

1. `0xA5` all-on: uniform panel, no missing rows/columns → power + init good.
2. Checkerboard: crisp 1-visible-pixel squares. Vertical 1-px stripes prove the
   pixel-doubling expansion (each visible pixel = 2 controller columns) is aligned; a
   "double-wide or smeared" look means the column window or nibble order is off
   (0xA0 remap bit A[2] = nibble swap is the usual suspect).
3. Single-pixel border rectangle: proves x/y orientation. To rotate 180°, change
   `0xA0` args (official example: `0x04, 0x11` flips).
4. Measure supply current at 100 % on vs. dark — sanity vs. datasheet (config A:
   ~345 mA @3.3 V; config B: ~60–70 mA @15 V).
5. Leave the checkerboard toggling for an hour — thermal/EMI soak.

### Phase B — give it BAKER's shape

Wrap phase A into a class that mirrors `OledPager`'s public API exactly
(`Init`, `BeginFrameTransfer`, `TickTransferOnePage`, `FlushFrameBlocking`,
`SetDisplayOn` (0xAE/0xAF — same opcodes as SSD1309, logic unchanged),
`SetTransferSuppressed`, `Fill`, `DrawPixel`, `GetPixel`, the
`OneBitGraphicsDisplayImpl` inheritance). Keep the 1bpp back/front buffers verbatim.
Transfers can stay blocking in this phase. Because the API matches, all of BAKER's
`ui_screen_*` drawing code can be exercised on the Pod unmodified.

### Phase C — async DMA chunking

Port the pager's DMA discipline to SPI:
- Chunk = 8 rows = **1,024 bytes** (frame = 8 chunks, mirroring today's 8 pages).
- DMA source buffer in `DMA_BUFFER_MEM_SECTION` (grows from 129 B to 1 KB; same
  cacheless-D2 reasoning as the current `s_dma_buf_`).
- Window commands (0x15/0x75/0x5C) sent blocking at `BeginFrameTransfer`; the entire
  8 KB stream is then data, so **D/C stays high for the whole frame** — no mid-frame
  toggling, each `TickTransferOnePage` just expands 8 rows into the DMA buffer and
  kicks `SpiHandle::DmaTransmit` with the completion callback clearing the in-flight
  gate (same `dma_in_flight_` pattern, same ISR-context rules).

### Phase D — integrate into BAKER

1. Rewrite `OledPager` internals with phases B+C (or swap the class in). Consider a
   build flag (e.g. `BAKER_OLED_SSD1322`) so the HiLetgo/I2C build stays available
   during transition.
2. Delete the vestigial `OledDisplay<SSD130xI2c128x64Driver>` from
   `main.cpp:39,103-117` — with no I2C device it only adds boot-time timeouts, and the
   new pager owns its own init.
3. Apply the three control-pin moves from §1.
4. Re-check the two blocking paths' timing comments (`ui_render.h:22-27` says "~22 ms
   blocking on I2C" — becomes ~20 ms on SPI, so budgets hold).

### Later, once it works (not part of bring-up)

- **Dirty-rect partial updates**: SSD1322 windowed writes make small-region refresh
  cheap — a real latency win the SSD1309 page scheme never offered.
- **16-level grayscale**: the byte-per-pixel stream makes shades free at the transport
  level (`0x00`–`0xFF` per pixel); needs a 4bpp back buffer + UI support to exploit.
- CS-tied-low experiment (frees D7) — informs the custom-board pin ledger in
  `NEWHAVEN_2.7_SWITCH_PLAN.md` §3.
