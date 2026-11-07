# Extraction scripts used in the ProtoBuild1 review

All run against the KiCad-9 converted copy produced by `tools/kicad10_to_9.py` (never the
shipped files, which KiCad 9 cannot parse). Replace `SCRATCH_DIR` with a scratch folder holding
the unpacked upload at `SCRATCH_DIR/upload_protobuild1/ProtoBuild1-autorouted/`, and `KICAD_OUT`
with the repo's `kicad_out/`.

| Script | Produces |
|---|---|
| `strip_tokens.py` | the token-bisect used to find why KiCad 9 rejects the files (PB-F-001); also the `strip_token` helper |
| `sexpr_check.py` | paren-balance / encoding sanity check for s-expression files |
| `sexp.py` | minimal KiCad s-expression parser used by the netlist/BOM scripts |
| `pb1_stats.py` | board summary: size, footprints, track widths, vias, zones, DRC minimums, duplicate refs |
| `pb1_fab_extract.py` | `pads.csv`, annular rings, hole-to-hole, NPTH-to-copper, copper-to-edge, zone settings (Pass 1) |
| `gerber_vs_pcb.py` | Gerber draw ↔ board segment exact-match cross-check per layer (Pass 0) |
| `pb1_gerber_pour.py` | mask openings vs vias, pour regions, pour-to-NPTH and pour-to-edge distances (Pass 1/6) |
| `pb1_islands_nc.py` | which pour regions contain GND items (superseded by the KiCad 9 refill test in PASS1) |
| `pb1_power_extract.py` | decoupling distances, per-net copper length/width/vias, IPC-2221 capacity (Pass 2) |
| `pb1_bom_xcheck.py` | parts list ↔ netlist three-way join with alias mapping (Pass 4) |
| `pb1_mech_extract.py` | terminal-block edge orientation, heatsink/coil clearances, bbox overlaps, silk text sizes (Pass 6) |
