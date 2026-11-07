import pcbnew, math, re, collections, sys, os
b = pcbnew.LoadBoard(os.path.abspath(sys.argv[1])); mm = pcbnew.ToMM
W,H=170.0,130.0
fps = {f.GetReference(): f for f in b.GetFootprints()}
def bbox(f, layer=None):
    bb = f.GetBoundingBox(False, False)  # no text, no invisible
    return (mm(bb.GetLeft()), mm(bb.GetTop()), mm(bb.GetRight()), mm(bb.GetBottom()))
print("== terminal blocks: body bbox vs board edge (which edge is nearest, gap) and pad side")
for r,f in sorted(fps.items()):
    if not r.startswith('J'): continue
    l,t,rr,bt = bbox(f); px = [mm(p.GetPosition().x) for p in f.Pads()]; py=[mm(p.GetPosition().y) for p in f.Pads()]
    gaps = {'left':l, 'top':t, 'right':W-rr, 'bottom':H-bt}; edge=min(gaps, key=gaps.get)
    # pads centre vs body centre: entry side is the body side away from pads (MKDS: pins near the back)
    cx,cy=(l+rr)/2,(t+bt)/2; pcx,pcy=sum(px)/len(px),sum(py)/len(py)
    away = {'left': cx-pcx<0, 'top': cy-pcy<0, 'right': cx-pcx>0, 'bottom': cy-pcy>0}  # body centre displaced from pads toward that edge?
    print(f"   {r:4s} rot {f.GetOrientationDegrees():6.1f} bbox x[{l:6.1f},{rr:6.1f}] y[{t:6.1f},{bt:6.1f}] nearest edge {edge:6s} gap {gaps[edge]:5.2f} mm; body overhang toward {edge}: {away[edge]}")
print("\n== Q6 (heatsink HS1) neighbours within 12 mm of its body bbox")
q6=fps['Q6']; l,t,rr,bt=bbox(q6)
for r,f in fps.items():
    if r=='Q6': continue
    l2,t2,r2,b2=bbox(f); dx=max(l2-rr, l-r2, 0); dy=max(t2-bt, t-b2, 0); d=math.hypot(dx,dy)
    if d<12: print(f"   {r:5s} {f.GetFPIDAsString().split(':')[-1][:34]:34s} gap {d:5.2f} mm")
print("\n== L1 (custom coil footprint, no courtyard) neighbours within 3 mm of its bbox; L1 bbox:", [round(v,1) for v in bbox(fps['L1'])])
l,t,rr,bt=bbox(fps['L1'])
for r,f in fps.items():
    if r=='L1': continue
    l2,t2,r2,b2=bbox(f); dx=max(l2-rr, l-r2, 0); dy=max(t2-bt, t-b2, 0); d=math.hypot(dx,dy)
    if d<3: print(f"   {r:5s} gap {d:5.2f} mm")
print("\n== footprint bbox pairs overlapping (body outlines, excluding text):")
items=[(r,bbox(f)) for r,f in fps.items()]
ov=[]
for i in range(len(items)):
    for j in range(i+1,len(items)):
        (r1,(l1,t1,rr1,b1)),(r2,(l2,t2,rr2,b2))=items[i],items[j]
        if l1<rr2 and l2<rr1 and t1<b2 and t2<b1: ov.append((r1,r2,round(min(rr1,rr2)-max(l1,l2),2),round(min(b1,b2)-max(t1,t2),2)))
print("   ", ov if ov else "none")
print("\n== footprints whose bbox leaves the board:")
for r,(l,t,rr,bt) in items:
    if l<0 or t<0 or rr>W or bt>H: print(f"   {r} bbox {l:.1f},{t:.1f},{rr:.1f},{bt:.1f}")
# courtyard presence
nocy=[r for r,f in fps.items() if not any(g.GetLayer() in (pcbnew.F_CrtYd,pcbnew.B_CrtYd) for g in f.GraphicalItems())]
print("\n== footprints without courtyard:", nocy)
# silk text sizes
sz=collections.Counter()
for f in b.GetFootprints():
    ref=f.Reference(); sz[(round(mm(ref.GetTextHeight()),2), round(mm(ref.GetTextThickness()),2), ref.IsVisible())]+=1
print("== reference text (height, thickness, visible):", dict(sz))
