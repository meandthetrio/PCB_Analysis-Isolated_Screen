#!/usr/bin/env python3
"""Rev 3: per-fragment GND pour connectivity (which GND pads/vias each fill fragment touches)."""
import pcbnew, collections, sys
B=sys.argv[1] if len(sys.argv)>1 else '/home/user/PCB_Analysis-Isolated_Screen/rev3/WavetableController.kicad_pcb'
b=pcbnew.LoadBoard(B); mm=pcbnew.ToMM
FCU,BCU=pcbnew.F_Cu,pcbnew.B_Cu; LN={FCU:'F.Cu',BCU:'B.Cu'}
zone=[z for z in b.Zones() if not z.GetIsRuleArea()][0]
gnd=b.GetNetcodeFromNetname('GND')
gpads=[(f.GetReference()+'.'+p.GetNumber(),p) for f in b.GetFootprints() for p in f.Pads() if p.GetNetCode()==gnd]
gtracks=[t for t in b.GetTracks() if t.GetNetCode()==gnd and t.GetClass()!='PCB_VIA']
print('GND pads total',len(gpads),'PTH',sum(1 for n,p in gpads if p.GetAttribute()==0),'SMD',sum(1 for n,p in gpads if p.GetAttribute()==1))
print('GND vias',sum(1 for t in b.GetTracks() if t.GetClass()=='PCB_VIA' and t.GetNetCode()==gnd))
for L in (FCU,BCU):
    fp=zone.GetFilledPolysList(L)
    for i in range(fp.OutlineCount()):
        o=fp.Outline(i); poly=pcbnew.SHAPE_POLY_SET(o); bb=o.BBox()
        touch=[n for n,p in gpads if p.IsOnLayer(L) and poly.Collide(p.GetEffectiveShape(L),0)]
        pth=[n for n,p in gpads if p.IsOnLayer(L) and p.GetAttribute()==0 and poly.Collide(p.GetEffectiveShape(L),0)]
        trk=sum(1 for t in gtracks if t.GetLayer()==L and poly.Collide(t.GetEffectiveShape(L),0))
        print(f"{LN[L]} frag#{i} area={o.Area()/1e12:.1f}mm2 bbox=({mm(bb.GetLeft()):.1f},{mm(bb.GetTop()):.1f})-({mm(bb.GetRight()):.1f},{mm(bb.GetBottom()):.1f}) GNDpads={len(touch)} PTH(stitch-to-other-layer)={pth} tracks={trk} {'<<< ISLAND (no GND pad/track)' if not touch and not trk else ''}")
