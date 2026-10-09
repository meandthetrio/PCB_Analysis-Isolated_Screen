#!/usr/bin/env python3
"""Compare pad geometry of two library footprints (lib dir + name)."""
import sys, pcbnew
def dump(libdir, name):
    fp = pcbnew.FootprintLoad(libdir, name)
    print(f"== {name}  ({fp.GetLibDescription()[:90]})")
    for p in fp.Pads():
        s, c = p.GetSize(), p.GetPosition()
        print(f"  pad {p.GetNumber()}: size {pcbnew.ToMM(s.x):.3f}x{pcbnew.ToMM(s.y):.3f} mm at ({pcbnew.ToMM(c.x):+.3f},{pcbnew.ToMM(c.y):+.3f})")
    bb = fp.GetCourtyard(pcbnew.F_CrtYd).BBox()
    print(f"  courtyard {pcbnew.ToMM(bb.GetWidth()):.2f} x {pcbnew.ToMM(bb.GetHeight()):.2f} mm")
lib = '/usr/share/kicad/footprints/Inductor_SMD.pretty'
dump(lib, 'L_Murata_DFE201610P')
dump(lib, 'L_0805_2012Metric')
dump('/usr/share/kicad/footprints/Capacitor_SMD.pretty', 'C_0805_2012Metric_Pad1.18x1.45mm_HandSolder')
