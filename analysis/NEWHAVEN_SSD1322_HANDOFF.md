# Handoff: Driving the Newhaven NHD-2.7-12864WDW3 OLED from a Daisy Pod (BAKER firmware)

**Audience:** whoever is doing the display bring-up and library work — human or AI
assistant. This document is self-contained: everything needed is in here, no other
project docs required. Facts below were verified against the NHD-2.7-12864WDW3
datasheet rev.6 (07/31/2024), Newhaven's official example code
(github.com/NewhavenDisplay/NHD-2.7-12864WD_Example), libDaisy's `daisy_pod.cpp`,
and the BAKER firmware source (branch `CUZ_AUG_WRAPUP`).

**Goal:** replace the HiLetgo 2.42" SSD1309 I2C OLED currently used by the BAKER
firmware with a Newhaven NHD-2.7-12864WDW3 (2.7", 128×64, white), first on a
breadboard with a Daisy Pod, ending with the BAKER UI running on the new screen.

---

## 1. The display — facts that drive every decision

| Fact | Value | Consequence |
|---|---|---|
| Controller | **SSD1322** (NOT SSD1309 — common misconception for this part) | Different init, different commands, different frame format |
| Interfaces | 8-bit parallel (6800/8080), 3-wire SPI, **4-wire SPI**. **No I2C mode exists** | The old I2C transport cannot be adapted; this is a bus change |
| Interface select | BS1 (pin 19), BS0 (pin 20) straps. 4-wire SPI = **both LOW** | Hardwire both to GND |
| Native mapping | 256×64 @ 4 bits/pixel grayscale; this 128×64 panel doubles every pixel horizontally (2 controller columns per visible pixel) | Full frame = **8,192 bytes** (vs 1,024 on the SSD1309) |
| Display window | Column addresses **0x1C–0x5B** (28–91), rows **0x00–0x3F** | Hardcode this window; wrong start column = shifted/wrapped image |
| SPI speed limit | t_cycle ≥ 300 ns → **~3.3 MHz max SCLK** | Full frame ≈ 20 ms. Same ballpark as the old 400 kHz I2C path — no refresh speedup, plan accordingly |
| SPI mode | Mode 0 (CPOL=0, CPHA=0), MSB first, write-only (no MISO) | TX-only SPI; MISO pin stays free for other use |
| Reset timing | /RES low ≥ 200 µs, then wait ≥ 200 µs before commands | |
| Logic | VDD 3.0–3.5 V, VIH = 0.8×VDD | Direct 3.3 V GPIO connection, no level shifting |
| Display on/off | 0xAF / 0xAE | Same opcodes as SSD1309 — screen-blank logic ports unchanged |
| Connector | 1×20 pin header, 2.54 mm pitch (Ø1.0 mm holes) | Breadboard-friendly; module also has 4× Ø2.5 mm mounting holes |

### Power — three module configurations (jumpers R4/R5/R7 on the module's PCB)

| Config | Jumpers | Supply | Current | Use when |
|---|---|---|---|---|
| **Default** (as shipped) | R4 closed | Single 3.3 V on pin 2 (VDD); onboard boost generates panel voltage | **345 mA typ / 375 mA max** @ 100% pixels | Quick start on the bench. **Do NOT power from the Daisy Seed's 3V3 pin — use an external 3.3 V supply rated ≥ 500 mA** |
| Option #1 | R5 closed | Boost fed from BC_VDD (pin 3), 3.0–5.5 V | ~200 mA @ 5 V | Not recommended (keeps the switching boost) |
| **Option #2** | R7 closed | Panel VCC (pin 15) = **14.5–15.5 V external** (typ 15.0 V), 60–70 mA; VDD only 180–300 µA | ~70 mA @ 15 V | The target architecture (no switching boost = no coil whine / audio noise). VDD can then come from the Pod's 3V3 |
| Power sequencing (Option #2) | | 3.3 V up first, then 15 V; reverse at power-down | | |

Recommended path: first light on **Default** config (no module rework, no 15 V supply
needed), then do the one-time rework (move the 0 Ω resistor from R4 to R7; photos on
datasheet p.5) and stay on **Option #2**.

## 2. Translation: the SSD1309 way → the SSD1322 way

If you already know how the HiLetgo/SSD1309 screen is driven, this table is the whole
migration in one place. Everything the old code does has an equivalent — nothing is
"kept as-is" except the drawing layer above the driver.

| Concept | SSD1309 (HiLetgo, today) | SSD1322 (Newhaven, target) |
|---|---|---|
| Bus | I2C @ 400 kHz, device address **0x3C** | 4-wire SPI ≤ ~3.3 MHz. No address — chip select instead |
| Command vs data | In-band prefix byte: `0x00` = command stream, `0x40` = data stream | **D/C GPIO level**: low = command, high = data. The prefix bytes disappear entirely |
| Pull-ups | I2C required them (the HiLetgo module silently provided them) | None. SPI needs no termination |
| Reset | HiLetgo handled it onboard (RC) — firmware never touched reset | **You must drive /RES**: low ≥ 200 µs, wait ≥ 200 µs, before any command |
| Framebuffer | 1bpp, 1,024 B, page layout (1 byte = 8 vertical pixels) | 4bpp grayscale stream, **8,192 B** (1 byte = one visible pixel = two doubled controller nibbles). Keep the 1bpp buffer and expand during transfer: bit → `0xFF`/`0x00` |
| Addressing | Page mode: `0x20 0x02`, then per page `0xB0\|page` + column pointer, 8 transfers of 128 B | One window then one stream: `0x15 0x1C 0x5B` (columns), `0x75 0x00 0x3F` (rows), `0x5C` (write RAM), then all 8,192 B linearly. **Column origin is 0x1C, not 0** |
| Display on/off | `0xAE` / `0xAF` | **Same** (`SetDisplayOn` logic ports unchanged) |
| Normal / inverse / all-on | `0xA6` / `0xA7` / `0xA5` | **Same opcodes** |
| Contrast | `0x81 val` | `0xC1 val` + master contrast `0xC7 val` |
| Clock / osc | `0xD5 val` | `0xB3 val` |
| Precharge | `0xD9 val` | Phase length `0xB1 val` + precharge voltage `0xBB val` |
| VCOMH | `0xDB val` | `0xBE val` |
| Multiplex ratio | `0xA8 0x3F` | `0xCA 0x3F` |
| Display offset / start line | `0xD3 val` / `0x40\|line` | `0xA2 val` / `0xA1 line` |
| Segment/COM remap (flip) | `0xA1`/`0xA0` and `0xC8`/`0xC0` | Single `0xA0 A B` two-arg command (`0x16 0x11` normal, `0x04 0x11` flipped 180°) |
| Charge pump | `0x8D` (module's boost did the panel voltage) | No such command — panel VCC is a hardware question (module boost jumper or external 15 V), not an init command |
| New, no SSD1309 equivalent | — | Command lock `0xFD 0x12` (unlock), function select `0xAB 0x01`, VSL `0xB4`, grayscale table `0xB8`/`0xB9` |
| Full-frame cost | 8 × (1+128) B over I2C ≈ 22 ms | 8,192 B over SPI ≈ 20 ms — **parity, not a speedup** |
| Old init lore | The 0xD5/0xD9 "noise" tweaks in the SSD1309 init | Do **not** carry over — start from the SSD1322 sequence in §5 verbatim |

## 3. Wiring

### 20-pin header (4-wire SPI; identical in both power configs except pins 2/15)

| Pin | Name | Connect to |
|---|---|---|
| 1 | VSS | GND |
| 2 | VDD | 3.3 V (see power table above for which supply) |
| 3 | BC_VDD | leave open |
| 4 | D/C | Daisy **D29** |
| 5, 6 | VSS | GND |
| 7 | SCLK | Daisy **D8** (SPI1 SCK) |
| 8 | SDIN | Daisy **D10** (SPI1 MOSI) |
| 9 | NC | — |
| 10–14 | VSS | GND |
| 15 | VCC | open (Default config) / **15.0 V** (Option #2) |
| 16 | /RES | Daisy **D30** |
| 17 | /CS | Daisy **D7** |
| 18 | /SHDN | leave open (internally pulled high) |
| 19 | BS1 | GND |
| 20 | BS0 | GND |

Decoupling at the header: 100 nF + ≥10 µF on VDD; for Option #2 also 100 nF + ≥100 µF
on VCC. Common ground between Pod, module, and bench supplies is mandatory.

### Why those Daisy pins, and what has to move in BAKER

SPI1 on the Daisy Seed is fixed: SCK = D8, MOSI = D10, MISO = D9 (unused here),
conventional CS = D7. BAKER's current breadboard rig already occupies some of these:

| Daisy pin | Current BAKER use (file:line) | Action |
|---|---|---|
| D7 | External encoder A (`controls.cpp:47`) | Move to **D11** (freed — old I2C SCL) |
| D8 | External encoder B (`controls.cpp:48`) | Move to **D12** (freed — old I2C SDA) |
| D9 | Right-shift button (`controls.cpp:52`) | **Stays** (MISO unused by write-only display) |
| D10 | Pod encoder click, re-inited by BAKER (`main.cpp:381`) | Move to **D0** |
| D11/D12 | I2C to the old OLED (`oled_pager.cpp:17-18`, `main.cpp:114-115`) | Freed by this port |

Pod carrier pins that are NOT available (claimed by the Pod itself, per libDaisy
`daisy_pod.cpp`): D13, D15, D17–D21, D23–D28, plus SD and audio. Free pins on this
setup: D0, D29, D30 (D0 = PB12 doubles as USB OTG ID — unused in USB device mode).

## 4. How BAKER's display stack works today (what you're porting)

- All drawing goes through one class: `OledPager` (`src/ui/oled_pager.{h,cpp}`),
  which subclasses libDaisy's `OneBitGraphicsDisplayImpl`. It owns **1bpp back/front
  buffers, 1,024 bytes, SSD1306 page layout** (byte = 8 vertical pixels, page-major:
  `pixel(x,y) = buf[x + (y>>3)*128] >> (y&7) & 1`).
- Transfer model: `BeginFrameTransfer()` copies back→front and arms; the main loop
  calls `TickTransferOnePage()` which kicks one 128-byte page over **I2C DMA** (8
  pages/frame, ~22 ms total), with an `dma_in_flight_` gate cleared by the DMA ISR.
  There's also `FlushFrameBlocking()` for already-blocking contexts and
  `SetDisplayOn()` (sends 0xAE/0xAF).
- Every UI screen (`src/ui/ui_screen_*.cpp`) draws only via this interface —
  **none of them change** in this port.
- Quirk: `main.cpp:39,103-117` also creates a libDaisy
  `OledDisplay<SSD130xI2c128x64Driver>`. `UIRender::Init` ignores it
  (`ui_render.cpp:35`), but today the pager free-rides on the SSD130x init it
  performs. **In the port, delete it** — with no I2C device present it only produces
  boot-time bus timeouts — and make the new pager own its full init.

So "the library" = a SSD1322/SPI transport + init + a frame pusher that expands the
existing 1bpp page-layout buffer into SSD1322 bytes, packaged behind `OledPager`'s
existing public API.

## 5. Build it in four phases

### Phase A — standalone blocking bring-up app (no BAKER code)

Own folder + Makefile (libDaisy example pattern), e.g. `tools/oled_bringup/`.
Complete skeleton:

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

// Datasheet p.15 init sequence, verbatim
static void OledInit()
{
    res.Write(false); System::DelayUs(250);   // /RES low >= 200us
    res.Write(true);  System::DelayUs(250);   // wait >= 200us before commands

    Cmd(0xAE);                                // display off
    Cmd(0xB3); Dat(0x91);                     // clock divide / osc freq
    Cmd(0xCA); Dat(0x3F);                     // mux ratio 64
    Cmd(0xA2); Dat(0x00);                     // display offset
    Cmd(0xAB); Dat(0x01);                     // internal VDD regulator
    Cmd(0xA0); Dat(0x16); Dat(0x11);          // remap (A[1]/A[4] flip orientation)
    Cmd(0xC7); Dat(0x0F);                     // master contrast
    Cmd(0xC1); Dat(0x9F);                     // contrast current
    Cmd(0xB1); Dat(0xF2);                     // phase length
    Cmd(0xBB); Dat(0x1F);                     // precharge voltage
    Cmd(0xB4); Dat(0xA0); Dat(0xFD);          // VSL
    Cmd(0xBE); Dat(0x04);                     // VCOMH
    Cmd(0xA6);                                // normal display
    Cmd(0xAF);                                // display on
}

// pagebuf: 1024 bytes, SSD1306 page layout (BAKER's OledPager format).
// Expansion: each 1-bit pixel -> ONE byte 0xFF/0x00. The byte's two 4-bit
// nibbles are the two horizontally-doubled controller pixels behind one
// visible pixel. 64 rows x 128 bytes = 8192 bytes per frame.
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
        SpiWrite(row, 128, true);             // ~21 ms/frame at 3.1 MHz
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
    scfg.nss            = SpiHandle::Config::NSS::SOFT;            // CS = our GPIO
    scfg.baud_prescaler = SpiHandle::Config::BaudPrescaler::PS_64; // ~1.6 MHz first
    scfg.pin_config.sclk = seed::D8;
    scfg.pin_config.mosi = seed::D10;
    // miso/nss unconfigured: TX-only with soft NSS
    spi.Init(scfg);

    OledInit();
    Cmd(0xA5);                 // smoke test: ALL PIXELS ON — no RAM writes involved
    System::Delay(1000);
    Cmd(0xA6);

    static uint8_t fb[1024];
    uint32_t t = 0;
    for(;;)
    {
        for(int i = 0; i < 1024; i++)         // page-layout checkerboard
            fb[i] = ((i + (t & 1)) & 1) ? 0xAA : 0x55;
        PushFrame(fb);
        t++;
        System::Delay(500);
    }
}
```

**Verification checklist, in order:**
1. `0xA5` all-on → uniform lit panel. Proves power, reset, init, and bus polarity
   before RAM addressing can be wrong. If dark: check /RES timing, BS straps, SPI mode.
2. Checkerboard → crisp single-visible-pixel squares. Smeared/double-wide squares
   mean the column window or nibble order is off (remap `0xA0` bit A[2] = nibble
   swap is the usual suspect).
3. 1-px border rectangle → orientation. To rotate 180°, use `0xA0` args `0x04, 0x11`
   (per Newhaven's example code).
4. Raise SPI to `PS_32` (~3.1 MHz — spec ceiling is ~3.3 MHz). Re-verify.
5. Measure supply current vs. datasheet (Default: ~345 mA @ 3.3 V; Option #2:
   ~60–70 mA @ 15 V). Leave the checkerboard toggling an hour as a soak test.

### Phase B — give it BAKER's shape

Wrap phase A in a class mirroring `OledPager`'s public API exactly: `Init`,
`BeginFrameTransfer`, `TickTransferOnePage`, `FlushFrameBlocking`, `SetDisplayOn`,
`SetTransferSuppressed`, `IsReady/IsTransferring/IsDisplayOn/IsTransferSuppressed`,
`Fill`, `DrawPixel`, `GetPixel`, `Width/Height/Update/UpdateFinished`, inheriting
`OneBitGraphicsDisplayImpl`. Keep the 1bpp back/front buffers verbatim; transfers may
stay blocking in this phase. Because the API matches, all BAKER screens can then be
exercised on the Pod unmodified.

### Phase C — async DMA chunking (restore today's non-blocking behavior)

- Chunk = 8 rows = 1,024 bytes; frame = 8 chunks (mirrors today's 8 pages).
- DMA source buffer in `DMA_BUFFER_MEM_SECTION` (the D2/cacheless section — same
  reasoning as the current pager's `s_dma_buf_`, grown from 129 B to 1 KB).
- Send the window commands (0x15/0x75/0x5C) blocking inside `BeginFrameTransfer`;
  after that the entire 8 KB frame is data, so **D/C stays high for the whole frame**
  and each `TickTransferOnePage` just expands 8 rows into the DMA buffer and kicks
  `SpiHandle::DmaTransmit`, with the completion callback clearing the in-flight gate
  (copy the existing `dma_in_flight_` / ISR-context pattern from `oled_pager.cpp`).

### Phase D — integrate into BAKER

1. Replace `OledPager`'s internals with phases B+C (or swap the class). A build flag
   (e.g. `BAKER_OLED_SSD1322`) keeps the HiLetgo/I2C build alive during transition.
2. Delete the `OledDisplay<SSD130xI2c128x64Driver>` block from `main.cpp:39,103-117`.
3. Apply the three pin moves from §3 (`controls.cpp:47-48`: 7→11, 8→12;
   `main.cpp:381`: 10→0).
4. Timing comments citing "~22 ms blocking on I2C" (`ui_render.h:22-27`) become
   ~20 ms on SPI — budgets hold; no UI code changes.

## 6. Known traps, collected

- It's an **SSD1322, not SSD1309**, and there is **no I2C** — don't try to adapt the
  old transport.
- **Never** power the Default-jumper module from the Daisy Seed's 3V3 pin (345 mA typ).
- SPI ceiling ~3.3 MHz → no refresh-rate win over the old I2C path (~20 ms/frame
  either way). Don't promise a snappier UI from the port alone.
- Pixel doubling: one visible pixel = one byte = two controller nibbles. Forgetting
  this halves/garbles the image.
- Column window starts at 0x1C, not 0. Rows are plain 0–0x3F.
- 3-wire SPI exists but uses 9-bit frames — skip it, use 4-wire.
- `/SHDN` (pin 18) only controls the onboard boost; in Option #2 it does nothing.
- In Option #2, bring VDD up before VCC, and drop VCC before VDD.

## 7. Later, once it works (not bring-up scope)

- **Dirty-rect partial updates**: SSD1322 windowed writes make small-region refresh
  cheap — a real latency win the SSD1309 page scheme never offered.
- **16-level grayscale**: the byte-per-pixel stream makes shades free at the
  transport level; needs a 4bpp back buffer + UI support to exploit.
- Experiment: /CS tied permanently low (SPI1 is exclusive to the display; SD is on
  SDMMC). If reliable, it frees D7 — which matters for pin budgeting on the eventual
  custom PCB.
