#!/bin/sh
# DRC of a Seed 3 dev-kit project against JLCPCB 2-layer minimums, on a scratch copy (reference files untouched).
# usage: kit_drc_jlc.sh <board.kicad_pcb> <scratch_dir> [netclass_clearance=0.1]
# writes <scratch_dir>/drc_asis.json (project's own rules, all severities) and <scratch_dir>/drc_jlc_nc<cl>.json
# JLC rules per capabilities page fetched 2026-10-12: track 0.1, clearance 0.1, copper-edge 0.2, hole clearance 0.2,
# hole-to-hole 0.2 (via; pad 0.45 checked separately by script), via ring 0.05 (dia>=hole+0.1), via dia 0.25, hole 0.15,
# silk clearance 0.15, text 1.0/0.15, mask-to-copper 0 (1:1), min connection 0.1
set -e
PCB=${1:?board}; OUT=${2:?scratch dir}; CL=${3:-0.1}
DIR=$(dirname "$PCB"); BASE=$(basename "$PCB" .kicad_pcb); mkdir -p "$OUT/prj"
cp "$PCB" "$DIR/$BASE.kicad_pro" "$OUT/prj/"; [ -f "$DIR/$BASE.kicad_prl" ] && cp "$DIR/$BASE.kicad_prl" "$OUT/prj/"
for t in fp-lib-table sym-lib-table; do [ -f "$DIR/$t" ] && cp "$DIR/$t" "$OUT/prj/"; done; [ -d "$DIR/libs" ] && cp -r "$DIR/libs" "$OUT/prj/"
cd "$OUT/prj"
# 1. as-is rules, all severities (so ignored silk/courtyard classes are counted too)
python3 -I - "$OUT/prj/$BASE.kicad_pro" "$OUT/prj/asis.kicad_pro" <<'PY'
import json,sys
j=json.load(open(sys.argv[1])); sev=j['board']['design_settings'].get('rule_severities',{})
for k,v in list(sev.items()):
    if v=='ignore': sev[k]='warning'
json.dump(j,open(sys.argv[2],'w'),indent=2)
PY
mkdir -p asis && cp "$BASE.kicad_pcb" asis/ && cp asis.kicad_pro "asis/$BASE.kicad_pro" && for t in fp-lib-table sym-lib-table; do [ -f $t ] && cp $t asis/; done; [ -d libs ] && cp -r libs asis/
(cd asis && kicad-cli pcb drc --severity-all --format json -o "$OUT/drc_asis.json" "$BASE.kicad_pcb" >/dev/null 2>&1)
# 2. JLC rules + netclass clearance CL
python3 -I - "$OUT/prj/$BASE.kicad_pro" "$CL" <<'PY'
import json,sys
p=sys.argv[1]; cl=float(sys.argv[2]); j=json.load(open(p))
j['board']['design_settings']['rules'].update({'min_track_width':0.1,'min_clearance':0.1,'min_copper_edge_clearance':0.2,'min_hole_clearance':0.2,'min_hole_to_hole':0.2,'min_via_annular_width':0.05,'min_via_diameter':0.25,'min_through_hole_diameter':0.15,'min_silk_clearance':0.15,'min_text_height':1.0,'min_text_thickness':0.15,'min_connection':0.1,'solder_mask_to_copper_clearance':0.0})
for c in j['net_settings']['classes']: c['clearance']=cl
sev=j['board']['design_settings'].get('rule_severities',{})
for k,v in list(sev.items()):
    if v=='ignore': sev[k]='warning'
json.dump(j,open(p,'w'),indent=2)
PY
kicad-cli pcb drc --severity-all --format json -o "$OUT/drc_jlc_nc${CL}.json" "$BASE.kicad_pcb" >/dev/null 2>&1
for f in "$OUT/drc_asis.json" "$OUT/drc_jlc_nc${CL}.json"; do python3 -I - "$f" <<'PY'
import json,sys,collections
d=json.load(open(sys.argv[1])); print(sys.argv[1].split('/')[-1], d.get('kicad_version'), sorted(collections.Counter((v['type'],v['severity']) for v in d['violations']).items(),key=lambda x:-x[1]),'unconnected',len(d['unconnected_items']))
PY
done
