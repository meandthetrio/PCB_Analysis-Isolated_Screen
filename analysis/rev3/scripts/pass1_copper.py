#!/usr/bin/env python3
"""Pass 1 (rev 3) copper geometry extraction. Read-only on the board file.
Outputs: trace width histogram per net, via inventory, drill/annular inventory,
hole-to-hole, copper-to-edge, NPTH/PTH/via hole-to-copper, min copper clearance."""
import pcbnew, collections, math, sys, json
B=sys.argv[1] if len(sys.argv)>1 else '/home/user/PCB_Analysis-Isolated_Screen/rev3/WavetableController.kicad_pcb'
b=pcbnew.LoadBoard(B)
mm=pcbnew.ToMM
FCU,BCU=pcbnew.F_Cu,pcbnew.B_Cu
LN={FCU:'F.Cu',BCU:'B.Cu'}
out={}

# ---------- geometry helpers (all in mm) ----------
def d_pt_seg(p,a,b_):
    ax,ay=a; bx,by=b_; px,py=p
    dx,dy=bx-ax,by-ay; L2=dx*dx+dy*dy
    if L2==0: return math.hypot(px-ax,py-ay)
    t=max(0,min(1,((px-ax)*dx+(py-ay)*dy)/L2))
    return math.hypot(px-(ax+t*dx),py-(ay+t*dy))
def _ccw(a,b_,c): return (c[1]-a[1])*(b_[0]-a[0])>(b_[1]-a[1])*(c[0]-a[0])
def seg_intersect(a,b_,c,d):
    return _ccw(a,c,d)!=_ccw(b_,c,d) and _ccw(a,b_,c)!=_ccw(a,b_,d)
def d_seg_seg(a,b_,c,d):
    if a!=b_ and c!=d and seg_intersect(a,b_,c,d): return 0.0
    return min(d_pt_seg(a,c,d),d_pt_seg(b_,c,d),d_pt_seg(c,a,b_),d_pt_seg(d,a,b_))
def edges(poly):
    n=len(poly); return [(poly[i],poly[(i+1)%n]) for i in range(n)] if n>1 else [(poly[0],poly[0])]
def d_edges(E1,E2):
    best=1e9
    for a,b_ in E1:
        for c,d in E2:
            v=d_seg_seg(a,b_,c,d)
            if v<best:
                best=v
                if best==0: return 0.0
    return best
def bbox_of(E,r):
    xs=[p[0] for e in E for p in e]; ys=[p[1] for e in E for p in e]
    return (min(xs)-r,min(ys)-r,max(xs)+r,max(ys)+r)
def bb_gap(b1,b2):
    return max(b1[0]-b2[2], b2[0]-b1[2], b1[1]-b2[3], b2[1]-b1[3], 0)
def chain_pts(ch):
    return [(mm(ch.CPoint(i).x),mm(ch.CPoint(i).y)) for i in range(ch.PointCount())]

GC=1.0
class EdgeIndex:
    def __init__(s,E):
        s.g=collections.defaultdict(list)
        for e in E:
            (x0,y0),(x1,y1)=e
            for gx in range(int(min(x0,x1)//GC),int(max(x0,x1)//GC)+1):
                for gy in range(int(min(y0,y1)//GC),int(max(y0,y1)//GC)+1): s.g[(gx,gy)].append(e)
    def near(s,bb,pad=0.5):
        out=set()
        for gx in range(int((bb[0]-pad)//GC),int((bb[2]+pad)//GC)+1):
            for gy in range(int((bb[1]-pad)//GC),int((bb[3]+pad)//GC)+1): out.update(s.g.get((gx,gy),()))
        return out
class Item:
    __slots__=('kind','ref','net','netname','layer','E','r','bb','extra','idx')
    def __init__(s,kind,ref,net,netname,layer,E,r,extra=''):
        s.kind,s.ref,s.net,s.netname,s.layer,s.E,s.r,s.extra=kind,ref,net,netname,layer,E,r,extra
        s.bb=bbox_of(E,r); s.idx=EdgeIndex(E) if len(E)>200 else None
    def __repr__(s): return f"{s.kind} {s.ref} [{s.netname}] {s.layer}{(' '+s.extra) if s.extra else ''}"
def d_item(A,C):
    if A.idx is not None and C.idx is None: return d_edges(C.E,A.idx.near(C.bb))-A.r-C.r
    if C.idx is not None and A.idx is None: return d_edges(A.E,C.idx.near(A.bb))-A.r-C.r
    if A.idx is not None and C.idx is not None: return 1e9
    return d_edges(A.E,C.E)-A.r-C.r
    def __repr__(s): return f"{s.kind} {s.ref} [{s.netname}] {s.layer}{(' '+s.extra) if s.extra else ''}"

# ---------- board outline ----------
outline=pcbnew.SHAPE_POLY_SET()
b.GetBoardPolygonOutlines(outline)
out_polys=[]
for i in range(outline.OutlineCount()):
    out_polys.append(chain_pts(outline.Outline(i)))
    for h in range(outline.HoleCount(i)): out_polys.append(chain_pts(outline.Hole(i,h)))
edge_E=[e for p in out_polys for e in edges(p)]
bb=b.GetBoardEdgesBoundingBox()
out['outline']={'outlines':outline.OutlineCount(),'vertices':[len(p) for p in out_polys],
    'bbox_mm':[round(mm(bb.GetLeft()),3),round(mm(bb.GetTop()),3),round(mm(bb.GetRight()),3),round(mm(bb.GetBottom()),3)],
    'size_mm':[round(mm(bb.GetWidth()),3),round(mm(bb.GetHeight()),3)]}

# ---------- collect copper items ----------
items={FCU:[],BCU:[]}
holes=[]   # (kind, ref, netname, cx, cy, drill_x, drill_y, E(hole edges), r)
tracks=[]
for t in b.GetTracks():
    cls=t.GetClass()
    if cls=='PCB_VIA':
        c=t.GetPosition(); cx,cy=mm(c.x),mm(c.y); dia=mm(t.GetWidth()); drl=mm(t.GetDrillValue())
        for L in (FCU,BCU):
            items[L].append(Item('via',f'via@({cx:.3f},{cy:.3f})',t.GetNetCode(),t.GetNetname(),LN[L],[((cx,cy),(cx,cy))],dia/2,f'dia={dia} drill={drl}'))
        holes.append(('via',f'via@({cx:.3f},{cy:.3f})',t.GetNetname(),cx,cy,drl,drl,[((cx,cy),(cx,cy))],drl/2))
        tracks.append(('via',t.GetNetname(),None,dia,drl,0.0,cx,cy,cx,cy))
    else:
        s,e=t.GetStart(),t.GetEnd(); w=mm(t.GetWidth()); L=t.GetLayer()
        E=[((mm(s.x),mm(s.y)),(mm(e.x),mm(e.y)))]
        if cls=='PCB_ARC':
            # approximate arc by polyline
            n=12; pts=[]
            for k in range(n+1):
                p=t.GetArcMid() if k==n//2 else None
            try:
                ch=pcbnew.SHAPE_ARC(t.GetStart(),t.GetMid(),t.GetEnd(),0).ConvertToPolyline()
                P=chain_pts(ch); E=[(P[i],P[i+1]) for i in range(len(P)-1)]
            except Exception as ex: pass
        items[L].append(Item('track',f'track@({mm(s.x):.3f},{mm(s.y):.3f})-({mm(e.x):.3f},{mm(e.y):.3f})',t.GetNetCode(),t.GetNetname(),LN[L],E,w/2,f'w={w}'))
        tracks.append((cls,t.GetNetname(),LN[L],w,None,mm(t.GetLength()),mm(s.x),mm(s.y),mm(e.x),mm(e.y)))

pads=[]
ATTR={0:'PTH',1:'SMD',2:'CONN',3:'NPTH'}
for fp in b.GetFootprints():
    ref=fp.GetReference()
    for p in fp.Pads():
        attr=ATTR.get(int(p.GetAttribute()),str(p.GetAttribute()))
        pos=p.GetPosition(); cx,cy=mm(pos.x),mm(pos.y)
        ds=p.GetDrillSize(); dx,dy=mm(ds.x),mm(ds.y)
        name=f'{ref}.{p.GetNumber() or "-"}'
        rec={'ref':ref,'pad':p.GetNumber(),'attr':attr,'net':p.GetNetname(),'x':round(cx,3),'y':round(cy,3),'drill':[round(dx,3),round(dy,3)],'layers':[],'size':{}, 'paste':[], 'mask':[], 'shape':int(p.GetShape(FCU)) if hasattr(p,'GetShape') else None}
        for L in (FCU,BCU):
            if not p.IsOnLayer(L): continue
            try: poly=p.GetEffectivePolygon(L, pcbnew.ERROR_INSIDE)
            except TypeError:
                try: poly=p.GetEffectivePolygon(L)
                except TypeError: poly=p.GetEffectivePolygon()
            if poly.OutlineCount()==0: continue
            P=chain_pts(poly.Outline(0))
            if len(P)<2: continue
            try: sz=p.GetSize(L)
            except TypeError: sz=p.GetSize()
            rec['layers'].append(LN[L]); rec['size'][LN[L]]=[round(mm(sz.x),3),round(mm(sz.y),3)]
            # copper area check: NPTH pads with copper size == 0 are not copper
            if attr=='NPTH' and (mm(sz.x)<=dx+1e-6 and mm(sz.y)<=dy+1e-6):
                continue
            items[L].append(Item('pad',name,p.GetNetCode(),p.GetNetname(),LN[L],edges(P),0.0,attr))
        for L,nm in ((pcbnew.F_Paste,'F.Paste'),(pcbnew.B_Paste,'B.Paste')):
            if p.IsOnLayer(L): rec['paste'].append(nm)
        for L,nm in ((pcbnew.F_Mask,'F.Mask'),(pcbnew.B_Mask,'B.Mask')):
            if p.IsOnLayer(L): rec['mask'].append(nm)
        if dx>0:
            # hole shape: oval if dx!=dy -> segment of length |dx-dy| with width min
            if abs(dx-dy)<1e-6: hE=[((cx,cy),(cx,cy))]; hr=dx/2
            else:
                try:
                    hs=p.GetEffectiveHoleShape(); seg=hs.GetSeg(); A=(mm(seg.A.x),mm(seg.A.y)); Bp=(mm(seg.B.x),mm(seg.B.y)); hE=[(A,Bp)]; hr=mm(hs.GetWidth())/2
                except Exception:
                    hE=[((cx,cy),(cx,cy))]; hr=max(dx,dy)/2
            holes.append((attr,name,p.GetNetname(),cx,cy,dx,dy,hE,hr))
            # annular ring (min over copper layers): size - drill / 2 along each axis
            rings=[]
            for Lname,sz in rec['size'].items():
                if attr=='NPTH' and sz[0]<=dx+1e-6: continue
                rings.append(round(min((sz[0]-dx)/2,(sz[1]-dy)/2),4))
            rec['annular']=min(rings) if rings else None
        pads.append(rec)

# zone fill polygons
zones=[]
for z in b.Zones():
    for L in z.GetLayerSet().Seq():
        if L not in LN: continue
        fp=z.GetFilledPolysList(L)
        for i in range(fp.OutlineCount()):
            O=chain_pts(fp.Outline(i)); Hs=[chain_pts(fp.Hole(i,h)) for h in range(fp.HoleCount(i))]
            zones.append((z.GetNetname(),LN[L],i,O,Hs))
            E=edges(O)+[e for H in Hs for e in edges(H)]
            items[L].append(Item('zone',f'{z.GetNetname()}-fill#{i}',z.GetNetCode(),z.GetNetname(),LN[L],E,0.0,f'outlineverts={len(O)} holes={len(Hs)}'))
out['zone_fill']=[{'net':n,'layer':L,'idx':i,'outline_verts':len(O),'holes':len(Hs),'bbox':bbox_of(edges(O),0)} for n,L,i,O,Hs in zones]

# ---------- 1. trace width histogram per net ----------
hist=collections.defaultdict(lambda:[0,0.0])
seg01=[]
for cls,net,L,w,drl,length,x1,y1,x2,y2 in tracks:
    if cls=='via': continue
    hist[(net,round(w,3))][0]+=1; hist[(net,round(w,3))][1]+=length
    if w<=0.1001: seg01.append({'net':net,'layer':L,'len':round(length,3),'from':[round(x1,3),round(y1,3)],'to':[round(x2,3),round(y2,3)]})
widths=collections.defaultdict(lambda:[0,0.0])
for (net,w),(n,l) in hist.items(): widths[w][0]+=n; widths[w][1]+=l
out['width_totals']={str(w):{'segments':n,'length_mm':round(l,1)} for w,(n,l) in sorted(widths.items())}
out['width_per_net']=sorted([{'net':net,'width':w,'segments':n,'length_mm':round(l,1)} for (net,w),(n,l) in hist.items()],key=lambda r:(r['width'],-r['length_mm']))
out['segments_0p1']=seg01

# ---------- 2. via inventory ----------
vc=collections.Counter((round(dia,3),round(drl,3)) for cls,net,L,dia,drl,*_ in tracks if cls=='via')
out['vias']={f'dia={k[0]} drill={k[1]}':v for k,v in vc.items()}
out['via_nets']=collections.Counter(net for cls,net,*_ in tracks if cls=='via')

# ---------- 3. drill / annular inventory ----------
dr=collections.Counter()
for attr,name,net,cx,cy,dx,dy,hE,hr in holes: dr[(attr,round(dx,3),round(dy,3))]+=1
out['drills']={f'{k[0]} {k[1]}x{k[2]}':v for k,v in sorted(dr.items())}
pth=[p for p in pads if p['attr'] in ('PTH','NPTH') and p.get('annular') is not None]
out['annular_sorted']=sorted([{'pad':f"{p['ref']}.{p['pad']}",'net':p['net'],'xy':[p['x'],p['y']],'drill':p['drill'],'size':p['size'],'annular':p['annular']} for p in pth],key=lambda r:r['annular'])[:40]
out['annular_hist']=collections.Counter(p['annular'] for p in pth)
out['npth_by_ref']={f"{k[0]} {k[1]}":v for k,v in collections.Counter((p['ref'],tuple(p['drill'])) for p in pads if p['attr']=='NPTH').items()}

# ---------- 4. hole-to-hole ----------
h2h=[]
for i in range(len(holes)):
    for j in range(i+1,len(holes)):
        a=holes[i]; c=holes[j]
        if abs(a[3]-c[3])>5 or abs(a[4]-c[4])>5: continue
        d=d_edges(a[7],c[7])-a[8]-c[8]
        if d<1.0: h2h.append((round(d,4),a[0],a[1],c[0],c[1]))
h2h.sort(); out['hole_to_hole_under_1mm']=h2h[:40]
def cls2(a,c): return 'via-via' if a=='via' and c=='via' else ('pad-pad' if a!='via' and c!='via' else 'via-pad')
best={}
for d,a0,a1,c0,c1 in h2h:
    k=cls2(a0,c0); 
    if k not in best: best[k]=(d,a1,c1)
out['hole_to_hole_min_by_class']={k:list(v) for k,v in best.items()}

# ---------- 5. copper-to-edge ----------
edge_bb=bbox_of(edge_E,0)
e2c=[]
for L in (FCU,BCU):
    for it in items[L]:
        # prefilter: only items within 1.5 mm of the outline bbox edge or anywhere (outline is non-convex) -> compute always but skip if far from all edge segs via bbox
        d=1e9
        if it.idx is not None:
            for a,c in edge_E:
                eb=(min(a[0],c[0])-1,min(a[1],c[1])-1,max(a[0],c[0])+1,max(a[1],c[1])+1)
                for p,q in it.idx.near(eb,0):
                    v=d_seg_seg(p,q,a,c)
                    if v<d: d=v
        else:
          for a,c in edge_E:
            eb=(min(a[0],c[0]),min(a[1],c[1]),max(a[0],c[0]),max(a[1],c[1]))
            if bb_gap(it.bb,eb)>1.0: continue
            for p,q in it.E:
                v=d_seg_seg(p,q,a,c)
                if v<d: d=v
        d-=it.r
        if d<1.0: e2c.append((round(d,4),repr(it)))
e2c.sort(); out['copper_to_edge_under_1mm']=e2c[:60]

# ---------- 6. hole-to-copper (NPTH, PTH, via hole) vs other items ----------
h2c=[]
for attr,name,net,cx,cy,dx,dy,hE,hr in holes:
    hb=bbox_of(hE,hr)
    for L in (FCU,BCU):
        for it in items[L]:
            if it.ref==name: continue  # own pad copper
            if attr!='NPTH' and it.netname==net: continue  # same-net copper over a plated hole is the normal connection
            if bb_gap(hb,it.bb)>0.6: continue
            d=(d_edges(hE,it.idx.near(hb)) if it.idx is not None else d_edges(hE,it.E))-hr-it.r
            if d<0.45:
                h2c.append((round(d,4),attr,name,net,repr(it)))
h2c.sort(); out['hole_to_copper_under_0p45']=h2c[:80]

# ---------- 7. min copper clearance (different nets, same layer) ----------
clr=[]
CELL=2.0
for L in (FCU,BCU):
    its=items[L]
    grid=collections.defaultdict(list)
    for idx,it in enumerate(its):
        x0,y0,x1,y1=it.bb
        for gx in range(int(x0//CELL),int(x1//CELL)+1):
            for gy in range(int(y0//CELL),int(y1//CELL)+1): grid[(gx,gy)].append(idx)
    seen=set()
    for cell,lst in grid.items():
        for i in range(len(lst)):
            for j in range(i+1,len(lst)):
                a,c=lst[i],lst[j]
                if (a,c) in seen: continue
                seen.add((a,c))
                A,C=its[a],its[c]
                if A.net==C.net: continue
                if bb_gap(A.bb,C.bb)>0.35: continue
                d=d_item(A,C)
                if d<0.3: clr.append((round(d,4),repr(A),repr(C)))
clr.sort(); out['clearance_under_0p3']=clr[:160]
def pclass(s):
    k=s.split(' ')[0]; return k
cmin={}
for d,a,c in clr:
    k='-'.join(sorted((pclass(a),pclass(c))))
    if k not in cmin: cmin[k]=(d,a,c)
out['clearance_min_by_class']={k:list(v) for k,v in cmin.items()}
out['clearance_hist']=collections.Counter(round(d,2) for d,*_ in clr)

json.dump(out,open('pass1_copper.json','w'),indent=1,default=str)
# human summary
print('OUTLINE',out['outline'])
print('ZONE FILLS',[(z['net'],z['layer'],z['idx'],z['outline_verts'],z['holes'],[round(v,1) for v in z['bbox']]) for z in out['zone_fill']])
print('WIDTH TOTALS',out['width_totals'])
print('0.1mm SEGMENTS',len(seg01))
for r in out['width_per_net']:
    if r['width']<=0.1001: print('  ',r)
print('VIAS',out['vias'])
print('DRILLS',out['drills'])
print('ANNULAR HIST',sorted(out['annular_hist'].items()))
print('ANNULAR LOWEST'); [print('  ',r) for r in out['annular_sorted'][:16]]
print('NPTH BY REF',out['npth_by_ref'])
print('HOLE-TO-HOLE MIN BY CLASS',out['hole_to_hole_min_by_class'])
print('HOLE-TO-HOLE <1mm (first 12)'); [print('  ',r) for r in h2h[:12]]
print('COPPER-TO-EDGE <1mm (first 25)'); [print('  ',r) for r in e2c[:25]]
print('HOLE-TO-COPPER <0.45 (first 40)'); [print('  ',r) for r in h2c[:40]]
print('CLEARANCE HIST',sorted(out['clearance_hist'].items()))
print('CLEARANCE MIN BY CLASS'); [print('  ',k,v) for k,v in out['clearance_min_by_class'].items()]
print('CLEARANCE <0.3 (first 40)'); [print('  ',r) for r in clr[:40]]
