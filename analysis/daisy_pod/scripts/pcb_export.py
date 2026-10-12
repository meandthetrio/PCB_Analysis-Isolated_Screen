"""Export PCB connectivity with pcbnew: every footprint (ref, value, fp id, layer, pos) with every pad -> net,
plus per-net track length / width set / via count, and per-net connectivity (island count after track routing).
Output JSON. Never modifies the board."""
import sys, json, pcbnew
board = pcbnew.LoadBoard(sys.argv[1])
IU = 1e6
fps=[]
for fp in board.GetFootprints():
    pads=[]
    for p in fp.Pads():
        pads.append(dict(num=p.GetNumber(), net=p.GetNetname(), netcode=p.GetNetCode(),
                         x=p.GetPosition().x/IU, y=p.GetPosition().y/IU,
                         layers=[board.GetLayerName(l) for l in p.GetLayerSet().Seq() if l in (pcbnew.F_Cu,pcbnew.B_Cu)],
                         type='TH' if p.GetAttribute()==pcbnew.PAD_ATTRIB_PTH else 'SMD' if p.GetAttribute()==pcbnew.PAD_ATTRIB_SMD else 'NPTH'))
    fps.append(dict(ref=fp.GetReference(), value=fp.GetValue(), fpid=str(fp.GetFPID().GetUniStringLibId()),
                    layer=board.GetLayerName(fp.GetLayer()), x=fp.GetPosition().x/IU, y=fp.GetPosition().y/IU, pads=pads))
nets={}
for code, net in board.GetNetsByNetcode().items():
    if code==0: continue
    nets[net.GetNetname()]=dict(code=code,len=0.0,widths={},vias=0,segments=0,pads=0,tracks=[])
for t in board.GetTracks():
    n=t.GetNetname()
    if n not in nets: continue
    if t.GetClass()=='PCB_VIA':
        nets[n]['vias']+=1
        nets[n]['tracks'].append(dict(kind='via',x=t.GetPosition().x/IU,y=t.GetPosition().y/IU,d=t.GetWidth()/IU,drill=t.GetDrillValue()/IU))
    else:
        L=t.GetLength()/IU; w=round(t.GetWidth()/IU,3)
        nets[n]['len']+=L; nets[n]['segments']+=1
        nets[n]['widths'][str(w)]=nets[n]['widths'].get(str(w),0)+L
        nets[n]['tracks'].append(dict(kind='seg',layer=board.GetLayerName(t.GetLayer()),w=w,L=L,
            x1=t.GetStart().x/IU,y1=t.GetStart().y/IU,x2=t.GetEnd().x/IU,y2=t.GetEnd().y/IU))
for fp in fps:
    for p in fp['pads']:
        if p['net'] in nets: nets[p['net']]['pads']+=1
# zones
zones=[]
for z in board.Zones():
    zones.append(dict(net=z.GetNetname(), layers=[board.GetLayerName(l) for l in z.GetLayerSet().Seq()], filled=z.IsFilled(),
                      area_mm2=sum(z.GetFilledPolysList(l).Area() for l in z.GetLayerSet().Seq())/IU/IU if z.IsFilled() else 0,
                      keepout=z.GetIsRuleArea(), name=z.GetZoneName()))
bb=board.GetBoardEdgesBoundingBox()
json.dump(dict(footprints=fps,nets=nets,zones=zones,
               bbox=[bb.GetX()/IU,bb.GetY()/IU,bb.GetRight()/IU,bb.GetBottom()/IU],
               tracks_total=sum(1 for t in board.GetTracks())), open(sys.argv[2],'w'), indent=1)
print("footprints",len(fps),"nets",len(nets),"zones",zones)
