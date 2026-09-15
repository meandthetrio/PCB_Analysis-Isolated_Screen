#!/usr/bin/env bash
# Smoke-test KiCad 9 against this project: ERC, DRC, netlist, Gerbers, SVG,
# schematic PDF, and the pcbnew Python API. Output goes to $OUT (default:
# ./kicad_out, git-ignored). Exit non-zero if any step fails to run.
# Note: ERC/DRC *finding* violations is expected for this board (see
# analysis/FINAL_REPORT.md); this script only checks the tooling runs.
set -euo pipefail
cd "$(dirname "$0")/.."
OUT="${OUT:-kicad_out}"
mkdir -p "$OUT/gerbers"
SCH=WavetableController.kicad_sch
PCB=WavetableController.kicad_pcb

echo "== kicad-cli $(kicad-cli version)"
kicad-cli sch erc  --format json --severity-all -o "$OUT/erc.json" "$SCH" 2>&1 | grep -v -i cvpcb || true
kicad-cli sch export netlist --format kicadxml -o "$OUT/netlist.xml" "$SCH" >/dev/null
kicad-cli sch export pdf -o "$OUT/schematic.pdf" "$SCH" 2>&1 | grep -v -i cvpcb || true
kicad-cli pcb drc  --format json --severity-all --all-track-errors -o "$OUT/drc.json" "$PCB"
kicad-cli pcb export gerbers -o "$OUT/gerbers/" "$PCB" >/dev/null
kicad-cli pcb export svg -o "$OUT/board.svg" --layers F.Cu,B.Cu,Edge.Cuts,F.SilkS --page-size-mode 2 "$PCB" >/dev/null

python3 - "$OUT" <<'PY'
import json, sys, collections, pcbnew
out = sys.argv[1]
b = pcbnew.LoadBoard("WavetableController.kicad_pcb")
bb = b.GetBoardEdgesBoundingBox()
print(f"== pcbnew {pcbnew.Version()}: {len(b.GetFootprints())} footprints, "
      f"{len(b.GetTracks())} tracks, {len(b.Zones())} zones, {b.GetNetCount()} nets, "
      f"board {pcbnew.ToMM(bb.GetWidth()):.1f} x {pcbnew.ToMM(bb.GetHeight()):.1f} mm")
def summ(vs): return collections.Counter((v['type'], v['severity']) for v in vs).most_common()
erc = json.load(open(f"{out}/erc.json")); drc = json.load(open(f"{out}/drc.json"))
print("== ERC"); [print(f"   {n:4d}  {t} ({s})") for (t, s), n in summ(v for sh in erc['sheets'] for v in sh['violations'])]
print("== DRC"); [print(f"   {n:4d}  {t} ({s})") for (t, s), n in summ(drc['violations'])]
print(f"   {len(drc['unconnected_items']):4d}  unconnected items")
PY
echo "== outputs in $OUT/"; ls "$OUT"
