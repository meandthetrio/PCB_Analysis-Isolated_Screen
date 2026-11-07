# ProtoBuild1 — "Rev K iron block" (Quad Eight project)

**Unrelated to the Manifold / WavetableController board at the repo root.** This folder is a
self-contained design review of a second product that shares only the tooling and the
six-pass checklist.

**If you are Claude opening this fresh:** read `analysis/FINAL_REPORT.md` (tiered red flags +
questions for Trey), backed by the ledger `analysis/FINDINGS.md` (PB-F-001…PB-F-030). Do not
re-derive anything before checking those. Methodology and which-file-is-truth rules are in
`analysis/SOURCE_OF_TRUTH.md`.

## What the board is

A through-hole, 2-layer, 170 × 130 mm, ±15 V audio board: one section of a tapped-inductor
resonant EQ ("iron block"). Signal path: input jack → INPUT pot → NE5532 buffer → NE5532 DRIVE
stage (U1A inverting, U1B + U3B followers, 3 × 10 Ω share resistors) → node **D** → Q resistor
(SW2) → node **P** → tuning capacitor (SW1b) → node **X** → coil tap (SW1a) → RM10 tapped
inductor → 1 Ω sense (TP3) → GND. A discrete "Quad Eight" amplifier Q1–Q5 forms OUT = 2P − D,
then a bypass switch, OUTPUT pot, buffer and make-up stage drive the output jack. Q6 is a PNP
current source that can inject DC into X through SW4 to magnetise the core ("iron" bias).
Frequencies 100 / 200 / 400 / 800 Hz (188 / 94 / 47 / 23.5 mH against 13.3 / 6.8 / 3.3 / 1.68 µF).
All panel parts (3 pots, 1 dual pot, 2 rotary switches, 2 toggles) are off-board, wired to 18
screw-terminal blocks. The design has **not been fabricated yet**; JLCPCB is the intended fab.

## Folder contents

| Path | What it is |
|---|---|
| `source/` | The upload `ProtoBuild1-autorouted.zip` (7 Nov 2026) unpacked verbatim. `source/README-from-upload.md` is the author's own file list. |
| `source/kicad-project/` | `ProtoBuild1.kicad_sch`, `ProtoBuild1.kicad_pcb` (KiCad 8 file header, no zone fill), `ProtoBuild1-zones-filled-kicad10-format.kicad_pcb` (native KiCad 10 save, zone fill stored — **the file the Gerbers came from**), custom coil symbol + two footprints, project lib tables. |
| `source/gerbers/` | 7 Gerber layers + Excellon drill + job file, plotted by KiCad 10.0.8 on 2026-11-07. Candidate fab set, verified identical to the board file (Pass 0). |
| `source/reports/` | The author's KiCad 10 ERC / DRC text reports and the KiCad 10 netlist. |
| `source/ProtoBuild1-parts-list.xlsx` | Parts list with manufacturer numbers, DigiKey stock/prices (7 Nov 2026), and a "Trey has" column to fill in. |
| `analysis/` | The review: FINAL_REPORT, findings ledger, SOURCE_OF_TRUTH, pass plan, PASS0–6 reports, thresholds, extraction scripts, datasheet text extracts. |

## Opening the design files — read before you try

The `.kicad_sch` and `ProtoBuild1.kicad_pcb` are **not** KiCad 8 files despite their headers:
they are script-assembled from KiCad 10 library content. KiCad 10 opens them; **KiCad 9.0.9
refuses both with a parse error** (finding PB-F-001). In a KiCad 9 session run

```
tools/kicad10_to_9.py boards/ProtoBuild1/source/kicad-project kicad_out/pb1_conv
tools/kicad_check.sh kicad_out/pb1_conv ProtoBuild1
```

which writes a loadable *copy* (documented token strips only; copper and nets untouched, verified
by `analysis/scripts/gerber_vs_pcb.py`). Never edit the copy as if it were the design.

## Headline findings (details and evidence in analysis/)

- **The inductor is not connected.** The coil footprint's 12 pins and its breakout row carry no
  net; the circuit ends at five jumper pads. The board does nothing until hand-wired jumpers are
  added, and the jumper table is undefined until the coil's pinout is known. Deliberate, but the
  single biggest assembly landmine (PB-F-018).
- **TO-92 pads break the JLCPCB annular-ring minimum** (0.15 mm vs 0.18 mm absolute minimum) on
  all 9 pads of Q1–Q3, because the 1.27 mm-pitch `TO-92_Inline` footprint was used while the BOM
  specifies 2.54 mm formed-lead parts (PB-F-006).
- **BOM is short two terminal blocks** (J13 3-pos and J17 2-pos, the coil-lead blocks); the "41
  terminal positions" wiring plan should be 46 (PB-F-020).
- **KiCad version trap** — files only open in KiCad 10; the upload README says 9 or 10
  (PB-F-001). DRC constraints are empty in the project file, so the author's "DRC 0" only
  reflects the 0.2 mm netclass (PB-F-002).
- **Q6 bias current source** can reach ~80 mA / ~0.85 W, above the BOM's "50 mA / 0.6 W", and
  its slip-on heatsink has ~6 mm of clearance where the BOM asks for 10 mm (PB-F-015, PB-F-023).
- Copper, netlist and Gerbers are mutually consistent (100 % segment match, 57/57 nets), ERC has
  zero errors in KiCad 9 and 10, polarities and transistor pinouts all check out against the
  datasheets, every terminal block faces outward at an edge, and the tuning arithmetic lands on
  100.7 / 199 / 404 / 801 Hz.

**Open questions for Trey:** the coil's actual pin layout (Don-Audio drawing), whether the
mounting holes should bond to chassis ground, heatsink orientation on Q6, and which KiCad
version the working files will live in.
