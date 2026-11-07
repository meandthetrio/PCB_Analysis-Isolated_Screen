import pcbnew, collections, math, csv, sys
b = pcbnew.LoadBoard(sys.argv[1]); mm = pcbnew.ToMM
pads=[]
for f in b.GetFootprints():
    for p in f.Pads():
        pos=p.GetPosition(); sz=p.GetSize(pcbnew.F_Cu) if hasattr(p,'GetSize') and 'layer' in str(p.GetSize.__doc__ or '') else p.GetSize()
        try: sz=p.GetSize(pcbnew.F_Cu)
        except TypeError: sz=p.GetSize()
        dr=p.GetDrillSize()
        pads.append(dict(ref=f.GetReference(), pad=p.GetNumber(), shape=p.GetShape(), attr=p.GetAttribute(), x=mm(pos.x), y=mm(pos.y), sx=mm(sz.x), sy=mm(sz.y), dx=mm(dr.x), dy=mm(dr.y), net=p.GetNetname(), fp=f.GetFPIDAsString()))
w = csv.DictWriter(open("pads.csv","w"), fieldnames=list(pads[0].keys())); w.writeheader(); w.writerows(pads)
pth=[p for p in pads if p['attr']==pcbnew.PAD_ATTRIB_PTH]; npth=[p for p in pads if p['attr']==pcbnew.PAD_ATTRIB_NPTH]
print(f"pads: {len(pads)} total, PTH {len(pth)}, NPTH {len(npth)}, SMD {len([p for p in pads if p['attr']==pcbnew.PAD_ATTRIB_SMD])}")
# annular ring per PTH pad: (min pad dimension - drill)/2  (drill may be oval: use max drill dim along min pad axis approx)
rings=collections.Counter(); worst=[]
for p in pth:
    ring=(min(p['sx'],p['sy'])-max(p['dx'],p['dy']))/2 if p['dx']>0 else None
    if ring is None: continue
    rings[(round(min(p['sx'],p['sy']),2), round(max(p['dx'],p['dy']),2), round(ring,3))]+=1
    worst.append((round(ring,3), p['ref'], p['pad'], p['fp'].split(':')[-1][:45]))
print("PTH annular rings (min pad dim, drill, ring): count")
for k,n in sorted(rings.items(), key=lambda kv: kv[0][2]): print(f"   pad {k[0]:.2f} / drill {k[1]:.2f} -> ring {k[2]:.3f} mm : {n} pads")
worst.sort(); print("smallest rings:", worst[:6])
# vias
vias=[t for t in b.GetTracks() if t.GetClass()=='PCB_VIA']
print("vias:", collections.Counter((round(mm(v.GetWidth(pcbnew.F_Cu)) if True else 0,2), round(mm(v.GetDrillValue()),2)) for v in vias), "-> via annular", [round((mm(v.GetWidth(pcbnew.F_Cu))-mm(v.GetDrillValue()))/2,3) for v in vias[:1]])
# hole-to-hole min distance (edge to edge)
holes=[(p['x'],p['y'],max(p['dx'],p['dy'])) for p in pads if p['dx']>0] + [(mm(v.GetPosition().x),mm(v.GetPosition().y),mm(v.GetDrillValue())) for v in vias]
best=(9e9,None)
for i in range(len(holes)):
    for j in range(i+1,len(holes)):
        d=math.hypot(holes[i][0]-holes[j][0],holes[i][1]-holes[j][1])-(holes[i][2]+holes[j][2])/2
        if d<best[0]: best=(d,(holes[i],holes[j]))
print(f"min hole-to-hole edge gap: {best[0]:.3f} mm between {best[1]}")
# drill inventory
print("PTH drills:", sorted(collections.Counter(round(max(p['dx'],p['dy']),2) for p in pth).items()), "| via drills:", collections.Counter(round(mm(v.GetDrillValue()),2) for v in vias), "| NPTH:", sorted(collections.Counter(round(max(p['dx'],p['dy']),2) for p in npth).items()))
# NPTH to nearest copper (pads / tracks) edge distance
tracks=[t for t in b.GetTracks() if t.GetClass()=='PCB_TRACK']
def seg_dist(px,py,x1,y1,x2,y2):
    dx,dy=x2-x1,y2-y1; L2=dx*dx+dy*dy
    t=0 if L2==0 else max(0,min(1,((px-x1)*dx+(py-y1)*dy)/L2)); return math.hypot(px-(x1+t*dx),py-(y1+t*dy))
for p in npth:
    dmin=(9e9,None)
    for q in pads:
        if q is p or q['attr']==pcbnew.PAD_ATTRIB_NPTH: continue
        d=math.hypot(p['x']-q['x'],p['y']-q['y'])-p['dx']/2-max(q['sx'],q['sy'])/2
        if d<dmin[0]: dmin=(d,f"pad {q['ref']}.{q['pad']}")
    for t in tracks:
        s,e=t.GetStart(),t.GetEnd(); d=seg_dist(p['x'],p['y'],mm(s.x),mm(s.y),mm(e.x),mm(e.y))-p['dx']/2-mm(t.GetWidth())/2
        if d<dmin[0]: dmin=(d,f"track net {t.GetNetname()}")
    print(f"NPTH {p['ref']} {p['dx']:.2f}mm at ({p['x']:.2f},{p['y']:.2f}) -> nearest copper {dmin[0]:.3f} mm ({dmin[1]}) [approx, pad outer-circle]")
# copper to board edge (board rect 0..170 x 0..130)
W,H=170.0,130.0
def edge_d(x,y,r): return min(x-r, y-r, W-x-r, H-y-r)
mp=min(((edge_d(p['x'],p['y'],max(p['sx'],p['sy'])/2),p['ref'],p['pad']) for p in pads if p['attr']!=pcbnew.PAD_ATTRIB_NPTH))
mt=min(((min(edge_d(mm(t.GetStart().x),mm(t.GetStart().y),mm(t.GetWidth())/2),edge_d(mm(t.GetEnd().x),mm(t.GetEnd().y),mm(t.GetWidth())/2)),t.GetNetname()) for t in tracks))
mv=min(((edge_d(mm(v.GetPosition().x),mm(v.GetPosition().y),mm(v.GetWidth(pcbnew.F_Cu))/2),v.GetNetname()) for v in vias))
print(f"copper-to-edge min: pads {mp}, tracks {mt}, vias {mv}")
# zone settings
for z in b.Zones():
    print(f"zone {z.GetNetname()} clearance {mm(z.GetLocalClearance()):.3f} minw {mm(z.GetMinThickness()):.3f} thermal gap {mm(z.GetThermalReliefGap()):.3f} spoke {mm(z.GetThermalReliefSpokeWidth()):.3f} pad_conn {z.GetPadConnection()} outline pts {z.Outline().Outline(0).PointCount()} bbox {mm(z.GetBoundingBox().GetWidth()):.1f}x{mm(z.GetBoundingBox().GetHeight()):.1f}")
    o=z.Outline().Outline(0); print("   outline:", [(round(mm(o.CPoint(i).x),2), round(mm(o.CPoint(i).y),2)) for i in range(o.PointCount())])
# netclass / design settings
ds=b.GetDesignSettings()
print(f"design settings: min track {mm(ds.m_TrackMinWidth)} min clr {mm(ds.m_MinClearance)} via {mm(ds.m_ViasMinSize)} hole {mm(ds.m_MinThroughDrill)} h2h {mm(ds.m_HoleToHoleMin)} edge {mm(ds.m_CopperEdgeClearance)} annular {mm(ds.m_MinThroughDrill)}")
nc = ds.m_NetSettings.GetDefaultNetclass()
print(f"default netclass: clearance {mm(nc.GetClearance())} track {mm(nc.GetTrackWidth())} via {mm(nc.GetViaDiameter())}/{mm(nc.GetViaDrill())}")
