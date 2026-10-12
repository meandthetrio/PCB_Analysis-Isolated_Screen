#!/usr/bin/env python3
"""Dump pad geometry (one representative footprint per footprint-id) and pad nets for selected refs.
Usage: python3 -I pad_dump.py BOARD.kicad_pcb [REF ...]"""
import sys, collections, pcbnew
b = pcbnew.LoadBoard(sys.argv[1]); want = set(sys.argv[2:])
seen = {}
for fp in b.GetFootprints():
    fid = fp.GetFPIDAsString()
    if fid not in seen: seen[fid] = fp
for fid, fp in sorted(seen.items()):
    pads = list(fp.Pads())
    if not pads or fid.startswith(('Resistor_SMD:R_0603', 'Capacitor_SMD:C_0603')): continue
    ox, oy = fp.GetPosition().x, fp.GetPosition().y
    rot = fp.GetOrientationDegrees()
    desc = []
    for p in pads:
        pos = p.GetPosition(); dx = pcbnew.ToMM(pos.x - ox); dy = pcbnew.ToMM(pos.y - oy)
        # rotate back to footprint frame
        import math
        a = math.radians(rot); rx = dx * math.cos(a) - dy * math.sin(a); ry = dx * math.sin(a) + dy * math.cos(a)
        kind = {pcbnew.PAD_ATTRIB_PTH: 'PTH', pcbnew.PAD_ATTRIB_SMD: 'SMD', pcbnew.PAD_ATTRIB_NPTH: 'NPTH', pcbnew.PAD_ATTRIB_CONN: 'CONN'}[p.GetAttribute()]
        s = p.GetSize(); d = p.GetDrillSize()
        desc.append(f"{p.GetNumber()}:{kind} ({rx:.2f},{ry:.2f}) {pcbnew.ToMM(s.x):.2f}x{pcbnew.ToMM(s.y):.2f}" + (f" drill {pcbnew.ToMM(d.x):.2f}" + (f"x{pcbnew.ToMM(d.y):.2f}" if d.y != d.x else '') if d.x else ''))
    print(f"## {fid}  (e.g. {fp.GetReference()}, {len(pads)} pads, paste F {sum(1 for p in pads if p.GetLayerSet().Contains(pcbnew.F_Paste))})")
    print('   ' + ' | '.join(desc[:24]) + (' ...' if len(desc) > 24 else ''))
if want:
    print('## pad nets')
    for fp in b.GetFootprints():
        if fp.GetReference() in want:
            print('  ', fp.GetReference(), fp.GetValue(), ' '.join(f"{p.GetNumber()}={p.GetNetname()}" for p in fp.Pads()))
