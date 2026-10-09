#!/usr/bin/env python3
"""Pass 6 (rev 3): silk decomposition, courtyards, paste vs BOM, NPTH/mounting, outline, OLED module overlay, new-part placement."""
import pcbnew, collections, json, re, sys, math
B=sys.argv[1] if len(sys.argv)>1 else '/home/user/PCB_Analysis-Isolated_Screen/rev3/WavetableController.kicad_pcb'
DRC=sys.argv[2] if len(sys.argv)>2 else '/home/user/PCB_Analysis-Isolated_Screen/kicad_out/rev3/drc_asis.json'
BOM=sys.argv[3] if len(sys.argv)>3 else '/home/user/PCB_Analysis-Isolated_Screen/kicad_out/rev3/bom_rev3.txt'
b=pcbnew.LoadBoard(B); mm=pcbnew.ToMM
FCU,BCU=pcbnew.F_Cu,pcbnew.B_Cu
fps={fp.GetReference():fp for fp in b.GetFootprints()}
def bbmm(bb): return (round(mm(bb.GetLeft()),2),round(mm(bb.GetTop()),2),round(mm(bb.GetRight()),2),round(mm(bb.GetBottom()),2))
def side(fp): return 'B' if fp.IsFlipped() else 'F'

# ---------- A. silk DRC decomposition ----------
d=json.load(open(DRC))
cat=collections.Counter(); refs_hit=collections.Counter(); examples=collections.defaultdict(list)
def kind(desc):
    if desc.startswith('Polygon on') or desc.startswith('Rectangle on') or desc.startswith('Arc on') or desc.startswith('Circle on'): return 'board-artwork:'+desc.split(' on ')[-1]
    if desc.startswith('Line on') or desc.startswith('Bezier on'): return 'board-line:'+desc.split(' on ')[-1]
    if desc.startswith('Reference') or desc.startswith('Value') or desc.startswith("Field"): return 'refdes/value'
    if desc.startswith('Text'): return 'text'
    if 'of ' in desc and ('Line' in desc or 'Polygon' in desc or 'Arc' in desc or 'Circle' in desc or 'Rectangle' in desc): return 'footprint-silk'
    if desc.startswith('Pad') or desc.startswith('PTH pad') or desc.startswith('NPTH') or desc.startswith('SMD pad'): return 'pad'
    if desc.startswith('Track') or desc.startswith('Via') or desc.startswith('Zone'): return 'copper'
    if 'Edge.Cuts' in desc: return 'edge'
    return 'other:'+desc[:30]
for v in d['violations']:
    if not v['type'].startswith('silk'): continue
    ks=tuple(sorted(kind(i['description']) for i in v['items']))
    cat[(v['type'],ks)]+=1
    for i in v['items']:
        m=re.match(r"(?:Reference|Value) '([^']+)'",i['description'])
        if m: refs_hit[(v['type'],m.group(1))]+=1
        m=re.search(r" of (\S+)",i['description'])
        if m and kind(i['description'])=='footprint-silk': refs_hit[(v['type'],'fpsilk:'+m.group(1))]+=1
    if len(examples[(v['type'],ks)])<3: examples[(v['type'],ks)].append(' | '.join(f"{i['description']} @({i['pos']['x']:.2f},{i['pos']['y']:.2f})" for i in v['items']))
print('=== A. silk DRC decomposition')
for k,n in sorted(cat.items(),key=lambda x:-x[1]):
    print(n,k); [print('     e.g.',e) for e in examples[k][:2]]
print('refdes/footprint-silk involvement:',sorted(refs_hit.items(),key=lambda x:-x[1]))
# silk-over-copper: which pads?
pad_hits=collections.Counter()
for v in d['violations']:
    if v['type']=='silk_over_copper':
        pads=[i['description'] for i in v['items'] if kind(i['description'])=='pad']
        for p in pads: pad_hits[re.sub(r'\[.*?\]','',p).strip()]+=1
print('silk_over_copper pad targets:',sorted(pad_hits.items(),key=lambda x:-x[1])[:40])

# ---------- B. silk inventory ----------
print('=== B. silk drawings inventory')
inv=collections.Counter(); art_bb={}
for dr in b.GetDrawings():
    L=dr.GetLayerName()
    if 'Silk' not in L: continue
    inv[(L,dr.GetClass(),dr.ShowShape() if dr.GetClass()=='PCB_SHAPE' else 'text')]+=1
    bb=dr.GetBoundingBox()
    k=L; 
    if k not in art_bb: art_bb[k]=[mm(bb.GetLeft()),mm(bb.GetTop()),mm(bb.GetRight()),mm(bb.GetBottom())]
    else:
        a=art_bb[k]; a[0]=min(a[0],mm(bb.GetLeft())); a[1]=min(a[1],mm(bb.GetTop())); a[2]=max(a[2],mm(bb.GetRight())); a[3]=max(a[3],mm(bb.GetBottom()))
    if dr.GetClass()=='PCB_TEXT': print('  text:',L,repr(dr.GetText()),'h',mm(dr.GetTextHeight()),'thk',mm(dr.GetTextThickness()),'mirrored',dr.IsMirrored(),'@',bbmm(bb))
print(dict(inv)); print('silk artwork extents by layer',{k:[round(x,1) for x in v] for k,v in art_bb.items()})
# min line width of silk artwork
ws=collections.Counter(round(mm(dr.GetWidth()),3) for dr in b.GetDrawings() if 'Silk' in dr.GetLayerName() and dr.GetClass()=='PCB_SHAPE')
print('silk artwork stroke widths',sorted(ws.items()))
# footprint silk line widths
fws=collections.Counter()
for fp in b.GetFootprints():
    for g in fp.GraphicalItems():
        if 'Silk' in g.GetLayerName() and g.GetClass()=='PCB_SHAPE': fws[round(mm(g.GetWidth()),3)]+=1
print('footprint silk stroke widths',sorted(fws.items()))

# ---------- C. refdes texts ----------
print('=== C. refdes text (height/thickness/layer/visible) and overlap with pads / artwork')
art_shapes=[(dr.GetLayerName(),dr.GetBoundingBox()) for dr in b.GetDrawings() if 'Silk' in dr.GetLayerName()]
rows=[]; small=[]; onpad=[]; hidden=[]; wrongside=[]; underart=[]
allpads=[(fp.GetReference(),p) for fp in b.GetFootprints() for p in fp.Pads()]
for ref,fp in sorted(fps.items()):
    r=fp.Reference(); bb=r.GetBoundingBox()
    h,t=mm(r.GetTextHeight()),mm(r.GetTextThickness()); L=r.GetLayerName(); vis=r.IsVisible()
    rows.append((ref,side(fp),L,vis,h,t,bbmm(bb)))
    if not vis: hidden.append(ref)
    if h<1.0 or t<0.15: small.append((ref,h,t))
    if (side(fp)=='F' and L!='F.Silkscreen') or (side(fp)=='B' and L!='B.Silkscreen'): wrongside.append((ref,side(fp),L))
    # pad overlap (any footprint's pad on the same side, copper or mask)
    Lcu=FCU if L=='F.Silkscreen' else BCU
    for pref,p in allpads:
        if p.IsOnLayer(Lcu) and p.GetBoundingBox().Intersects(bb): onpad.append((ref,pref+'.'+p.GetNumber()))
    n_art=sum(1 for aL,ab in art_shapes if aL==L and ab.Intersects(bb))
    if n_art: underart.append((ref,n_art))
print('refdes hidden:',hidden); print('refdes below JLC 1.0mm height / 0.15mm line:',small)
print('refdes on wrong-side silk:',wrongside)
print('refdes bbox intersects a pad:',onpad)
print('refdes bbox intersects board silk artwork (same layer):',underart)
hs=collections.Counter((round(h,2),round(t,2)) for _,_,_,_,h,t,_ in rows); print('refdes size histogram (h,thk):',sorted(hs.items()))
for ref in ['J8','Headphones1','C15','C17','C18','C19','C20','C21','C22','C23','C24','C25','C26','U6','L1','Q1','Q2','Q3','Q4','Q5','Q6','R29','R30','R31','R32','R33','R35','R36','R37','R38','R39','R40','D6','FB5','FB6','FB7','C6','C7','MK1','SW1','LED1','LED2']:
    r=[x for x in rows if x[0]==ref][0]; print('  ',r)

# ---------- D. courtyards ----------
print('=== D. courtyard overlaps (own check) and missing courtyards')
cy={}
missing=[]
for ref,fp in fps.items():
    L=pcbnew.F_CrtYd if side(fp)=='F' else pcbnew.B_CrtYd
    c=fp.GetCourtyard(L)
    if c.OutlineCount()==0: missing.append(ref); continue
    cy[ref]=(side(fp),c)
ov=[]
refs=sorted(cy)
for i in range(len(refs)):
    for j in range(i+1,len(refs)):
        a,c=cy[refs[i]],cy[refs[j]]
        if a[0]!=c[0]: continue
        if a[1].BBox().Intersects(c[1].BBox()) and a[1].Collide(c[1],0): ov.append((refs[i],refs[j]))
print('missing courtyard:',missing); print('courtyard overlaps:',ov)
# courtyard to board edge
outline=pcbnew.SHAPE_POLY_SET(); b.GetBoardPolygonOutlines(outline)
obb=b.GetBoardEdgesBoundingBox()
print('courtyards outside the board bbox:',[ref for ref,(s,c) in cy.items() if not obb.Contains(c.BBox())])
# courtyard vs outline polygon (protruding)
prot=[]
for ref,(s,c) in cy.items():
    o=c.Outline(0)
    outside=sum(1 for k in range(o.PointCount()) if not outline.Contains(o.CPoint(k)))
    if outside: prot.append((ref,outside,o.PointCount()))
print('courtyard vertices outside outline polygon (ref, n_outside, n_total):',prot)

# ---------- E. paste vs BOM ----------
print('=== E. paste apertures vs BOM')
bom_refs={}
for line in open(BOM,encoding='utf-8',errors='replace'):
    parts=[x.strip() for x in line.split('|')]
    if len(parts)<4 or parts[1]=='Designator' or line.startswith('#'): continue
    for r in re.split(r'[,\s]+',parts[1]):
        if r: bom_refs[r]=parts[3]
paste=collections.defaultdict(lambda:[0,0])
for fp in b.GetFootprints():
    for p in fp.Pads():
        if p.IsOnLayer(pcbnew.F_Paste): paste[fp.GetReference()][0]+=1
        if p.IsOnLayer(pcbnew.B_Paste): paste[fp.GetReference()][1]+=1
print('F.Paste total',sum(v[0] for v in paste.values()),'B.Paste total',sum(v[1] for v in paste.values()))
print('footprints with paste but NOT in BOM:',[(r,side(fps[r]),v,fps[r].GetValue()[:20]) for r,v in sorted(paste.items()) if r not in bom_refs])
print('BOM refs with no footprint:',[r for r in bom_refs if r not in fps])
print('footprints with no paste (TH/hand):',[r for r in sorted(fps) if r not in paste])
print('F-side footprints:',[(r,fps[r].GetValue()[:16]) for r in sorted(fps) if side(fps[r])=='F'])
print('BOM refs present but footprint has no paste:',[r for r in bom_refs if r in fps and r not in paste])
# footprint attributes (exclude from BOM / pos)
attrs=[(r,fp.GetAttributes()) for r,fp in fps.items() if fp.GetAttributes()&(pcbnew.FP_EXCLUDE_FROM_BOM|pcbnew.FP_EXCLUDE_FROM_POS_FILES|pcbnew.FP_BOARD_ONLY)]
print('footprints flagged exclude-from-BOM/pos/board-only:',attrs)

# ---------- F. NPTH / mounting ----------
print('=== F. NPTH / mounting holes')
npth=collections.Counter(); pthl=collections.Counter()
for fp in b.GetFootprints():
    for p in fp.Pads():
        ds=p.GetDrillSize()
        if p.GetAttribute()==3: npth[(fp.GetReference(),round(mm(ds.x),2),round(mm(ds.y),2))]+=1
        elif p.GetAttribute()==0 and p.GetNetname()=='' : pthl[(fp.GetReference(),round(mm(ds.x),2))]+=1
print('NPTH by footprint:',sorted(npth.items())); print('no-net PTH by footprint:',sorted(pthl.items()))
print('footprints named like mounting holes:',[r for r in fps if 'MountingHole' in fps[r].GetFPIDAsString() or r.startswith('H')])

# ---------- G. outline ----------
print('=== G. outline')
ec=[dr for dr in b.GetDrawings() if dr.GetLayerName()=='Edge.Cuts']
print('Edge.Cuts items:',[(dr.GetClass(),dr.ShowShape(),dr.GetPointCount() if dr.ShowShape()=='Polygon' else '') for dr in ec])
print('outline polygons from GetBoardPolygonOutlines:',outline.OutlineCount(),'holes',[outline.HoleCount(i) for i in range(outline.OutlineCount())],'bbox',bbmm(obb),'size',round(mm(obb.GetWidth()),3),'x',round(mm(obb.GetHeight()),3))
o=outline.Outline(0); pts=[(round(mm(o.CPoint(k).x),3),round(mm(o.CPoint(k).y),3)) for k in range(o.PointCount())]
# find notches: vertices not on the bbox
L,T,R,Bt=mm(obb.GetLeft()),mm(obb.GetTop()),mm(obb.GetRight()),mm(obb.GetBottom())
inner=[p for p in pts if abs(p[0]-L)>0.01 and abs(p[0]-R)>0.01 and abs(p[1]-T)>0.01 and abs(p[1]-Bt)>0.01]
print('outline vertices:',len(pts),'vertices not on bbox (notches/corner rounding):',len(inner), 'x-range of inner verts',(min(p[0] for p in inner),max(p[0] for p in inner)) if inner else None,'y-range',(min(p[1] for p in inner),max(p[1] for p in inner)) if inner else None)
# cluster inner vertices
cl=collections.Counter((round(p[0]/10)*10,round(p[1]/10)*10) for p in inner); print('inner-vertex clusters (10mm bins):',sorted(cl.items()))

# ---------- H. J8 / OLED module overlay ----------
print('=== H. J8 OLED header and NHD-2.7-12864WDW3 module overlay')
j8=fps['J8']; pads=sorted(j8.Pads(),key=lambda p:int(p.GetNumber()))
p1,p20=pads[0],pads[-1]
P1=(mm(p1.GetPosition().x),mm(p1.GetPosition().y)); P20=(mm(p20.GetPosition().x),mm(p20.GetPosition().y))
print('J8 side',side(j8),'rot',j8.GetOrientationDegrees(),'pin1',P1,'pin20',P20,'pitch',round(math.hypot(P20[0]-P1[0],P20[1]-P1[1])/19,3),'courtyard bbox',bbmm(j8.GetCourtyard(pcbnew.F_CrtYd).BBox()) if j8.GetCourtyard(pcbnew.F_CrtYd).OutlineCount() else None, 'drill',mm(p1.GetDrillSize().x),'pad',mm(p1.GetSize(FCU).x))
print('J8 pad nets:',[(p.GetNumber(),p.GetNetname()) for p in pads])
cx=(P1[0]+P20[0])/2; cy_=(P1[1]+P20[1])/2
# Datasheet NHD-2.7-12864WDW3 mech drawing: PCB 82.0 x 47.5 mm; pin row 2.50 mm from the top edge; pin1 16.87 mm from left edge; pitch 2.54 (span 48.26) -> row centred (16.87+24.13=41.0=82/2)
W,H,ROW=82.0,47.5,2.5
cands={'module extends toward +y (down the board)':(cx-W/2,cy_-ROW,cx+W/2,cy_-ROW+H),
       'module extends toward -y (up / over rear jacks & edge)':(cx-W/2,cy_+ROW-H,cx+W/2,cy_+ROW)}
for name,(x0,y0,x1,y1) in cands.items():
    print(f"-- {name}: x {x0:.1f}..{x1:.1f}, y {y0:.1f}..{y1:.1f}")
    print('   beyond board bbox:', 'left' if x0<L else '', 'right' if x1>R else '', f'top by {T-y0:.1f}mm' if y0<T else '', f'bottom by {y1-Bt:.1f}mm' if y1>Bt else '')
    rect=pcbnew.BOX2I(pcbnew.VECTOR2I(pcbnew.FromMM(x0),pcbnew.FromMM(y0)),pcbnew.VECTOR2I(pcbnew.FromMM(x1-x0),pcbnew.FromMM(y1-y0)))
    hitsF=[(r,bbmm(fp.GetBoundingBox(False,False))) for r,fp in fps.items() if side(fp)=='F' and r!='J8' and fp.GetBoundingBox(False,False).Intersects(rect)]
    hitsB=[r for r,fp in fps.items() if side(fp)=='B' and fp.GetBoundingBox(False,False).Intersects(rect)]
    print('   F-side footprints under the module:',hitsF)
    print('   B-side footprints under the module (through-board, info only):',len(hitsB), [r for r in hitsB if r.startswith('J') or r.startswith('ENC') or r in ('P2','SW1','A1')])
    print('   audio corridor x165-200 overlap:', max(0,min(x1,200)-max(x0,165)),'mm of width')
# F-side part heights near J8
print('F-side parts bbox:',[(r,bbmm(fp.GetBoundingBox(False,False))) for r,fp in fps.items() if side(fp)=='F'])

# ---------- I. new parts: Headphones1, electrolytics, C23/C24 ----------
print('=== I. new part placement')
for ref in ['Headphones1','C15','C17','C18','C19','C20','C21','C22','C6','C7','C23','C24','J8','U6','L1']:
    fp=fps[ref]; c=cy.get(ref); bb=c[1].BBox() if c else fp.GetBoundingBox(False,False)
    # nearest other courtyard on same side
    best=(9e9,None)
    for r2,(s2,c2) in cy.items():
        if r2==ref or s2!=side(fp): continue
        # distance between courtyard bboxes
        a=bbmm(bb); d_=bbmm(c2.BBox())
        dx=max(d_[0]-a[2],a[0]-d_[2],0); dy=max(d_[1]-a[3],a[1]-d_[3],0); dist=math.hypot(dx,dy)
        if dist<best[0]: best=(dist,r2)
    e=min(mm(bb.GetLeft())-L, R-mm(bb.GetRight()), mm(bb.GetTop())-T, Bt-mm(bb.GetBottom()))
    print(f"{ref:12s} {side(fp)} @({mm(fp.GetPosition().x):.2f},{mm(fp.GetPosition().y):.2f}) rot={fp.GetOrientationDegrees():.0f} crtyd={bbmm(bb)} nearest_crtyd={best[1]}@{best[0]:.2f}mm edge_margin={e:.2f}mm pads={[(p.GetNumber(),p.GetNetname()) for p in fp.Pads()][:6]}")
hp=fps['Headphones1']
print('Headphones1 pads:',[(p.GetNumber(),p.GetNetname(),round(mm(p.GetPosition().x),2),round(mm(p.GetPosition().y),2),p.GetAttribute(),round(mm(p.GetDrillSize().x),2),round(mm(p.GetSize(BCU).x),2),round(mm(p.GetSize(BCU).y),2)) for p in hp.Pads()])
print('Headphones1 graphics layers:',collections.Counter(g.GetLayerName() for g in hp.GraphicalItems()))
print('J7 (PHONES jack) bbox',bbmm(fps['J7'].GetBoundingBox(False,False)),'ENCR1 bbox',bbmm(fps['ENCR1'].GetBoundingBox(False,False)))
