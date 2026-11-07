# CLAUDE.md

Two unrelated boards live here (see the table at the top of `README.md`):

- **WavetableController / Manifold** (repo root): design review + rev-2 planning
  for Trey's Daisy Seed synth controller (KiCad 9, 2-layer). Read `README.md`
  first, then `analysis/FINAL_REPORT.md`. Do not re-derive findings that are
  already in `analysis/FINDINGS.md`.
- **ProtoBuild1 / Rev K iron block** (`boards/ProtoBuild1/`): a different
  product (Quad Eight tapped-inductor EQ section, KiCad 10, not yet fabbed).
  Read `boards/ProtoBuild1/README.md`, then its `analysis/FINAL_REPORT.md`;
  ledger IDs are `PB-F-nnn`. Its shipped KiCad files do not open in KiCad 9 —
  run `tools/kicad10_to_9.py boards/ProtoBuild1/source/kicad-project kicad_out/pb1_conv`
  first and work on the copy.

## Tooling (already installed in Claude Code on the web sessions)

The SessionStart hook runs `tools/kicad_env_setup.sh`, which provides:

- `kicad-cli` 9.0.9 and the `pcbnew` Python module (`python3 -c "import pcbnew"`)
- stock KiCad symbol/footprint libraries and user lib tables
- `freerouting` (headless autorouter, Java 25)

Useful commands:

```
tools/kicad_check.sh                         # ERC, DRC, netlist, Gerber, SVG, PDF -> kicad_out/WavetableController/
tools/kicad_check.sh kicad_out/pb1_conv ProtoBuild1   # same for the ProtoBuild1 converted copy
tools/kicad10_to_9.py SRC_DIR DST_DIR        # KiCad-9-loadable copy of a KiCad-10-content project
kicad-cli sch erc --format json -o erc.json WavetableController.kicad_sch
kicad-cli pcb drc --format json -o drc.json WavetableController.kicad_pcb
tools/autoroute.py IN.kicad_pcb OUT.kicad_pcb --passes 20
```

Expected noise: ~40 ERC/DRC library warnings naming Trey's private libs
(`Retroactive_Custom_Parts`, `Jack_3.5mm_CUI_RetroactiveCustom`,
`SOP-6_...(RetroactiveCustom)`). Footprints are embedded in the board file, so
these are harmless. Everything else ERC/DRC reports is a real finding.

## Rules

- Manifold: the checked-in `.kicad_pcb` is a stale copy with no GND pour. Never
  regenerate Gerbers from it and never treat routing on it as a design
  candidate. `Manifold_Gerb_LedFix/` is fab truth for copper.
- ProtoBuild1: `source/kicad-project/ProtoBuild1-zones-filled-kicad10-format.kicad_pcb`
  is the file the Gerbers came from (verified identical copper). The converted
  copies in `kicad_out/` are analysis-only; never present them as design files.
- Write scratch output to `kicad_out/` (git-ignored) or the session
  scratchpad, never next to the design files.
- Don't modify the design files unless asked. Rev-2 work should go on a
  branch with a clear commit message per change.
- Manifold has a duplicate refdes R21 (a known finding). Tools that require
  unique refs (Specctra export) need the temporary rename in
  `tools/autoroute.py`. ProtoBuild1 has no duplicate refs.
- Keep the two reviews separate: findings, data and scripts for ProtoBuild1 go
  under `boards/ProtoBuild1/analysis/`, never into the root `analysis/`.
