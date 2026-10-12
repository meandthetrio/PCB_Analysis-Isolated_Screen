#!/bin/sh
# DRC of the Daisy Pod Rev5 conversion against JLCPCB 2-layer minimums, on a scratch copy (design files untouched).
# usage: pod_drc_jlc.sh <scratch_dir> [netclass_clearance=0.1]
# writes <scratch_dir>/drc_jlc_nc<cl>.json ; rules per JLCPCB capabilities page (fetched 2026-10-12):
# track 0.1, clearance 0.1, edge 0.2, hole clearance 0.2, hole-to-hole 0.5 (pad), via annular 0.13, via dia 0.5, hole 0.3, silk 0.15, text 1.0/0.15
set -e
SRC=/home/user/PCB_Analysis-Isolated_Screen/reference/electrosmith/daisy_pod/kicad
OUT=${1:?scratch dir}; CL=${2:-0.1}; mkdir -p "$OUT/prj"
cp "$SRC"/ES_Daisy_Pod_Rev5.kicad_pcb "$SRC"/ES_Daisy_Pod_Rev5.kicad_pro "$SRC"/ES_Daisy_Pod_Rev5.kicad_prl "$OUT/prj/"
python3 -I - "$OUT/prj/ES_Daisy_Pod_Rev5.kicad_pro" "$CL" <<'PY'
import json,sys
p=sys.argv[1]; cl=float(sys.argv[2]); j=json.load(open(p))
j['board']['design_settings']['rules'].update({'min_track_width':0.1,'min_clearance':0.1,'min_copper_edge_clearance':0.2,'min_hole_clearance':0.2,'min_hole_to_hole':0.5,'min_via_annular_width':0.13,'min_via_diameter':0.5,'min_through_hole_diameter':0.3,'min_silk_clearance':0.15,'min_text_height':1.0,'min_text_thickness':0.15,'min_connection':0.1})
for c in j['net_settings']['classes']: c['clearance']=cl
sev=j['board']['design_settings'].get('rule_severities',{})
for k,v in list(sev.items()):
    if v=='ignore': sev[k]='warning'
json.dump(j,open(p,'w'),indent=2)
PY
cd "$OUT/prj" && kicad-cli pcb drc --severity-all --format json -o "$OUT/drc_jlc_nc${CL}.json" ES_Daisy_Pod_Rev5.kicad_pcb >/dev/null
python3 -I - "$OUT/drc_jlc_nc${CL}.json" <<'PY'
import json,sys,collections
d=json.load(open(sys.argv[1])); print(sorted(collections.Counter((v['type'],v['severity']) for v in d['violations']).items(),key=lambda x:-x[1]),'unconnected',len(d['unconnected_items']))
PY
