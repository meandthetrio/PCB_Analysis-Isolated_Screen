# CLAUDE.md

Design review + rev-2 planning for Trey's WavetableController board (KiCad 9,
2-layer, Daisy Seed synth controller). Read `README.md` first, then
`analysis/HIGH_LEVEL_PLAN.md` (Round 2 section at the end tells you which pass
is next; the user runs one pass per session). Round 1's output is
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

- Root `.kicad_pcb`/`.kicad_sch`/`.kicad_pro` are the Round 2 (2026-10) files
  and are the verified source of `Manifold_Gerbs_2026-10/` (F-036). The Round 1
  copy in `archive/rev1_2026-08/` is a stale no-pour file: never plot from it.
  `Manifold_Gerb_LedFix/` is fab truth for the boards that physically exist.
- Write scratch output to `kicad_out/` (git-ignored) or the session
  scratchpad, never next to the design files.
- Don't modify the design files unless asked. Rev-2 work should go on a
  branch with a clear commit message per change.
- The Round 1 board has a duplicate refdes R21 (F-013); the Round 2 board does
  not. `tools/autoroute.py` still carries the temporary rename for the archived
  file.
- Round 2 baselines (ERC/DRC JSON) live in `analysis/baseline_2026-10/`.
  `analysis/gerber_analyze.py DIR` takes the Gerber folder as an argument.
