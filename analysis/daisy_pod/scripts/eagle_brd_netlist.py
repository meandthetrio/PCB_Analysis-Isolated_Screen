"""Eagle 9 .brd -> JSON: elements (name, library, package, value, x, y, rot, layer-mirror) and signals (name -> [(element, pad)]),
plus per-signal wire length by layer/width and via count straight from the .brd (independent of the KiCad conversion).
Run: python3 -I eagle_brd_netlist.py IN.brd OUT.json"""
import sys, json, math, xml.etree.ElementTree as ET
r=ET.parse(sys.argv[1]).getroot()
els={}
for e in r.findall('.//board/elements/element'):
    els[e.get('name')]=dict(library=e.get('library'),package=e.get('package'),value=e.get('value'),x=float(e.get('x')),y=float(e.get('y')),rot=e.get('rot'))
sigs={}
for s in r.findall('.//board/signals/signal'):
    n=s.get('name'); d=sigs[n]=dict(contacts=[],wires={},vias=0,wire_len=0.0,polygons=0)
    for c in s.findall('contactref'): d['contacts'].append((c.get('element'),c.get('pad')))
    for w in s.findall('wire'):
        L=math.hypot(float(w.get('x2'))-float(w.get('x1')),float(w.get('y2'))-float(w.get('y1')))
        k=f"L{w.get('layer')}/w{w.get('width')}"; d['wires'][k]=round(d['wires'].get(k,0)+L,2); d['wire_len']+=L
    d['vias']=len(s.findall('via')); d['polygons']=len(s.findall('polygon')); d['wire_len']=round(d['wire_len'],2)
json.dump(dict(elements=els,signals=sigs),open(sys.argv[2],'w'),indent=1)
print(len(els),'elements',len(sigs),'signals')
