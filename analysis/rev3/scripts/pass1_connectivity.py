#!/usr/bin/env python3
"""Pass 1 (rev 3): starved thermals, dangling vias, zone islands, GND coverage per layer."""
import pcbnew, collections, math, sys, json
B=sys.argv[1] if len(sys.argv)>1 else '/home/user/PCB_Analysis-Isolated_Screen/rev3/WavetableController.kicad_pcb'
b=pcbnew.LoadBoard(B); mm=pcbnew.ToMM
FCU,BCU=pcbnew.F_Cu,pcbnew.B_Cu; LN={FCU:'F.Cu',BCU:'B.Cu'}
conn=b.GetConnectivity()
zone=[z for z in b.Zones() if not z.GetIsRuleArea()][0]
fill={L:zone.GetFilledPolysList(L) for L in (FCU,BCU)}
gnd=b.GetNetcodeFromNetname('GND')

def pad_by(ref,num):
    for fp in b.GetFootprints():
        if fp.GetReference()==ref:
            for p in fp.Pads():
                if p.GetNumber()==num: return p
def touches_fill(item,L):
    """does the item's copper shape on layer L collide with (touch) the zone fill on L"""
    sh=item.GetEffectiveShape(L)
    return fill[L].Collide(sh, 0)

print('=== starved thermal pads (DRC: 1 spoke) — independent connectivity check')
flag=[('TAC_SWITCH_1','3','F.Cu'),('U1','5','B.Cu'),('P2','A12','B.Cu'),('P2','B1','B.Cu'),('R18','1','B.Cu'),('C9','1','B.Cu'),('U3','3','B.Cu'),('C10','1','B.Cu')]
for ref,num,Ls in flag:
    p=pad_by(ref,num); L=FCU if Ls=='F.Cu' else BCU
    tr=[t for t in conn.GetConnectedTracks(p)]
    pads=[q for q in conn.GetConnectedPads(p)]
    trs=[f"{t.GetClass()} w={mm(t.GetWidth()):.2f} {b.GetLayerName(t.GetLayer()) if t.GetClass()!='PCB_VIA' else 'via'}" for t in tr]
    print(f"{ref}.{num} [{p.GetNetname()}] @({mm(p.GetPosition().x):.3f},{mm(p.GetPosition().y):.3f}) layers={[LN[l] for l in (FCU,BCU) if p.IsOnLayer(l)]} attr={p.GetAttribute()} touches_fill F={touches_fill(p,FCU) if p.IsOnLayer(FCU) else '-'} B={touches_fill(p,BCU) if p.IsOnLayer(BCU) else '-'} connected_tracks={len(tr)} {trs} connected_pads={[q.GetParentFootprint().GetReference()+'.'+q.GetNumber() for q in pads]}")

print('=== dangling vias')
for t in b.GetTracks():
    if t.GetClass()=='PCB_VIA':
        c=t.GetPosition(); x,y=mm(c.x),mm(c.y)
        if abs(x-167.75)<1.5 and abs(y-145.9)<1.5:
            tr=conn.GetConnectedTracks(t); pads=conn.GetConnectedPads(t)
            print(f"via [{t.GetNetname()}] @({x:.3f},{y:.3f}) dia={mm(t.GetWidth())} drill={mm(t.GetDrillValue())} tracks={[ (tt.GetClass(), b.GetLayerName(tt.GetLayer()), round(mm(tt.GetWidth()),2)) for tt in tr]} pads={[q.GetParentFootprint().GetReference()+'.'+q.GetNumber() for q in pads]}")
            # what is near on each layer
            for L in (FCU,BCU):
                near=[]
                for fp in b.GetFootprints():
                    for p in fp.Pads():
                        if p.IsOnLayer(L) and math.hypot(mm(p.GetPosition().x)-x, mm(p.GetPosition().y)-y)<2.5: near.append(f"{fp.GetReference()}.{p.GetNumber()}[{p.GetNetname()}]")
                print('   near on',LN[L],near)
# LED2 nets: full routing summary
print('=== LED_2_R / LED_2_B net items')
for nn in ('/LED_2_R','/LED_2_B'):
    code=b.GetNetcodeFromNetname(nn)
    segs=[t for t in b.GetTracks() if t.GetNetCode()==code]
    pads=[(fp.GetReference(),p.GetNumber(),'B' if fp.IsFlipped() else 'F') for fp in b.GetFootprints() for p in fp.Pads() if p.GetNetCode()==code]
    print(nn,'pads',pads,'tracks',[(t.GetClass(),b.GetLayerName(t.GetLayer()) if t.GetClass()!='PCB_VIA' else 'via',round(mm(t.GetStart().x),2),round(mm(t.GetStart().y),2),round(mm(t.GetEnd().x),2),round(mm(t.GetEnd().y),2)) for t in segs])

print('=== zone fill outlines / islands')
for L in (FCU,BCU):
    fp=fill[L]
    for i in range(fp.OutlineCount()):
        o=fp.Outline(i); bb=o.BBox()
        poly=pcbnew.SHAPE_POLY_SET(o)
        # count GND pads/vias whose centre is inside this outline
        n_pad=n_via=0; refs=set()
        for f in b.GetFootprints():
            for p in f.Pads():
                if p.GetNetCode()==gnd and p.IsOnLayer(L) and poly.Contains(p.GetPosition()): n_pad+=1; refs.add(f.GetReference())
        for t in b.GetTracks():
            if t.GetClass()=='PCB_VIA' and t.GetNetCode()==gnd and poly.Contains(t.GetPosition()): n_via+=1
        print(f"{LN[L]} outline#{i} verts={o.PointCount()} holes={fp.HoleCount(i)} area={o.Area()/1e12:.1f}mm2 bbox=({mm(bb.GetLeft()):.1f},{mm(bb.GetTop()):.1f})-({mm(bb.GetRight()):.1f},{mm(bb.GetBottom()):.1f}) GNDpads_inside={n_pad} GNDvias_inside={n_via} {'ISLAND?' if n_pad+n_via==0 else ''} refs={sorted(refs)[:8]}")

print('=== GND pad coverage per layer (pad copper touches the fill)')
tot=collections.Counter(); notouch=[]
for f in b.GetFootprints():
    for p in f.Pads():
        if p.GetNetCode()!=gnd: continue
        for L in (FCU,BCU):
            if not p.IsOnLayer(L): continue
            tot[(LN[L],'pads')]+=1
            t=touches_fill(p,L)
            if t: tot[(LN[L],'touch_fill')]+=1
            else:
                tr=conn.GetConnectedTracks(p)
                notouch.append((f.GetReference()+'.'+p.GetNumber(),LN[L],len(tr)))
print(dict(tot)); print('GND pads not touching fill on that layer (ref,layer,#tracks):',notouch)
gv=[t for t in b.GetTracks() if t.GetClass()=='PCB_VIA' and t.GetNetCode()==gnd]
print('GND vias',len(gv),'touch F',sum(1 for v in gv if touches_fill(v,FCU)),'touch B',sum(1 for v in gv if touches_fill(v,BCU)))
# GND tracks
gt=[t for t in b.GetTracks() if t.GetClass()!='PCB_VIA' and t.GetNetCode()==gnd]
print('GND track segments',len(gt),'total mm',round(sum(mm(t.GetLength()) for t in gt),1))
# unconnected / ratsnest
print('unconnected count (connectivity):',conn.GetUnconnectedCount(True) if hasattr(conn,'GetUnconnectedCount') else '?')
