# CLAUDE.md

Design review + rev-2 planning for Trey's WavetableController board (KiCad 9,
2-layer, Daisy Seed synth controller). Read `README.md` first, then
`analysis/FINAL_REPORT.md`. Do not re-derive findings that are already in
`analysis/FINDINGS.md`.

## Tooling (already installed in Claude Code on the web sessions)

The SessionStart hook runs `tools/kicad_env_setup.sh`, which provides:

- `kicad-cli` 9.0.9 and the `pcbnew` Python module (`python3 -c "import pcbnew"`)
- stock KiCad symbol/footprint libraries and user lib tables
- `freerouting` (headless autorouter, Java 25)

Useful commands:

```
tools/kicad_check.sh                         # ERC, DRC, netlist, Gerber, SVG, PDF -> kicad_out/
kicad-cli sch erc --format json -o erc.json WavetableController.kicad_sch
kicad-cli pcb drc --format json -o drc.json WavetableController.kicad_pcb
tools/autoroute.py IN.kicad_pcb OUT.kicad_pcb --passes 20
```

Expected noise: ~40 ERC/DRC library warnings naming Trey's private libs
(`Retroactive_Custom_Parts`, `Jack_3.5mm_CUI_RetroactiveCustom`,
`SOP-6_...(RetroactiveCustom)`). Footprints are embedded in the board file, so
these are harmless. Everything else ERC/DRC reports is a real finding.

## Rules

- The checked-in `.kicad_pcb` is a stale copy with no GND pour. Never
  regenerate Gerbers from it and never treat routing on it as a design
  candidate. `Manifold_Gerb_LedFix/` is fab truth for copper.
- Write scratch output to `kicad_out/` (git-ignored) or the session
  scratchpad, never next to the design files.
- Don't modify the design files unless asked. Rev-2 work should go on a
  branch with a clear commit message per change.
- The board has a duplicate refdes R21 (a known finding). Tools that require
  unique refs (Specctra export) need the temporary rename in
  `tools/autoroute.py`.
