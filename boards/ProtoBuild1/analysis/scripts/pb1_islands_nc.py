import re, math, sys, os
sys.path.insert(0, os.getcwd())
from pb1_gerber_pour import parse
G="upload_protobuild1/ProtoBuild1-autorouted/gerbers"
bcu,bregs=parse(f"{G}/ProtoBuild1-filled-B_Cu.gbr")
import pcbnew
b=pcbnew.LoadBoard("KICAD_OUT/pb1_conv/ProtoBuild1.kicad_pcb"); mm=pcbnew.ToMM
gnd=[(mm(p.GetPosition().x),mm(p.GetPosition().y),f"{f.GetReference()}.{p.GetNumber()}") for f in b.GetFootprints() for p in f.Pads() if p.GetNetname()=='GND']
gnd+=[(mm(v.GetPosition().x),mm(v.GetPosition().y),"via") for v in b.GetTracks() if v.GetClass()=='PCB_VIA' and v.GetNetname()=='GND']
def inside(pt,poly):
    x,y=pt; n=len(poly); ins=False; j=n-1
    for i in range(n):
        xi,yi=poly[i]; xj,yj=poly[j]
        if (yi>y)!=(yj>y) and x<(xj-xi)*(y-yi)/(yj-yi+1e-12)+xi: ins=not ins
        j=i
    return ins
print("== B.Cu pour regions: GND items inside each (islands without any are floating copper)")
for r in bregs:
    xs=[p[0] for p in r]; ys=[p[1] for p in r]
    hits=[g[2] for g in gnd if inside((g[0],g[1]),r)]
    print(f"   region bbox x[{min(xs):.1f},{max(xs):.1f}] y[{min(ys):.1f},{max(ys):.1f}] vertices {len(r):5d}: GND pads/vias inside: {len(hits)} {hits[:6]}")
