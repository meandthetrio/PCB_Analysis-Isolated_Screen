#!/usr/bin/env bash
# Smoke-test KiCad 9 against a project: ERC, DRC, netlist, Gerbers, SVG,
# schematic PDF, and the pcbnew Python API. Output goes to $OUT (default:
# ./kicad_out/<basename>, git-ignored). Exit non-zero if any step fails to run.
#
#   tools/kicad_check.sh                       # WavetableController (repo root)
#   tools/kicad_check.sh DIR BASENAME          # e.g. kicad_out/pb1_conv ProtoBuild1
#
# ERC/DRC *finding* violations is expected for these boards (see the analysis
# folders); this script only checks the tooling runs. ProtoBuild1's shipped
# files need tools/kicad10_to_9.py first (KiCad 9 cannot parse them as shipped).
set -euo pipefail
cd "$(dirname "$0")/.."
DIR="${1:-.}"
BASE="${2:-WavetableController}"
OUT="${OUT:-kicad_out/$BASE}"
mkdir -p "$OUT/gerbers"
SCH="$DIR/$BASE.kicad_sch"
PCB="$DIR/$BASE.kicad_pcb"
[ -f "$SCH" ] && [ -f "$PCB" ] || { echo "missing $SCH or $PCB"; exit 1; }

echo "== kicad-cli $(kicad-cli version) on $PCB"
kicad-cli sch erc  --format json --severity-all -o "$OUT/erc.json" "$SCH" 2>&1 | grep -v -i "cvpcb\|image handler" || true
kicad-cli sch export netlist --format kicadxml -o "$OUT/netlist.xml" "$SCH" >/dev/null
kicad-cli sch export pdf -o "$OUT/schematic.pdf" "$SCH" 2>&1 | grep -v -i "cvpcb\|image handler" || true
kicad-cli pcb drc  --format json --severity-all --all-track-errors -o "$OUT/drc.json" "$PCB" 2>&1 | grep -v -i "image handler" || true
kicad-cli pcb export gerbers -o "$OUT/gerbers/" "$PCB" >/dev/null
kicad-cli pcb export svg -o "$OUT/board.svg" --layers F.Cu,B.Cu,Edge.Cuts,F.SilkS --page-size-mode 2 "$PCB" >/dev/null

PCB="$PCB" python3 - "$OUT" <<'PY' 2>&1 | grep -v -i "image handler\|GetWidth called"
import json, sys, os, collections, pcbnew
out = sys.argv[1]
b = pcbnew.LoadBoard(os.path.abspath(os.environ["PCB"]))
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
echo "== freerouting: $(freerouting -h 2>&1 | grep -o 'Freerouting v[0-9.]*' || echo MISSING)"
echo "== outputs in $OUT/"; ls "$OUT"
