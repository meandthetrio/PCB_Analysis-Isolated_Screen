import re, math, sys, collections
G="upload_protobuild1/ProtoBuild1-autorouted/gerbers"
def parse(path):
    txt=open(path).read(); fs=re.search(r'%FSLAX(\d)(\d)Y',txt); scale=10**int(fs.group(2))
    aps={m.group(1):(m.group(2),m.group(3)) for m in re.finditer(r'%ADD(\d+)([A-Za-z_]+),([^*]*)\*%',txt)}
    cur=None;x=y=0;flashes=[];regions=[];reg=None
    for line in txt.splitlines():
        if line.startswith('G36'): reg=[]; continue
        if line.startswith('G37'): regions.append(reg); reg=None; continue
        m=re.match(r'D(\d+)\*$',line)
        if m and m.group(1) not in ('01','02','03'): cur=m.group(1); continue
        m=re.match(r'(?:X(-?\d+))?(?:Y(-?\d+))?D0([123])\*',line)
        if m:
            nx=int(m.group(1))/scale if m.group(1) else x; ny=int(m.group(2))/scale if m.group(2) else y; op=m.group(3)
            if reg is not None and op in('1','2'): reg.append((nx,-ny))
            elif op=='3': flashes.append((nx,-ny,aps[cur]))
            x,y=nx,ny
    return flashes,regions
# vias vs mask openings
fcu,_=parse(f"{G}/ProtoBuild1-filled-F_Cu.gbr"); fmask,_=parse(f"{G}/ProtoBuild1-filled-F_Mask.gbr"); bmask,_=parse(f"{G}/ProtoBuild1-filled-B_Mask.gbr")
bcu,bregs=parse(f"{G}/ProtoBuild1-filled-B_Cu.gbr")
via_fl=[f for f in fcu if f[2][0]=='C' and abs(float(f[2][1])-0.8)<1e-6]
print(f"F.Cu flashes {len(fcu)} of which 0.8mm (via-size) {len(via_fl)}; F.Mask openings {len(fmask)}; B.Mask {len(bmask)}")
mset={(round(x,2),round(y,2)) for x,y,a in fmask}
print("vias with F.Mask opening:", sum((round(x,2),round(y,2)) in mset for x,y,a in via_fl), "of", len(via_fl))
print("mask aperture sizes F:", collections.Counter(a for _,_,a in fmask).most_common(6))
# pour regions
print(f"B.Cu regions: {len(bregs)}, vertex counts {[len(r) for r in bregs]}")
for r in bregs:
    xs=[p[0] for p in r]; ys=[p[1] for p in r]; print(f"   region bbox x[{min(xs):.2f},{max(xs):.2f}] y[{min(ys):.2f},{max(ys):.2f}]")
# distance from pour edge to NPTH holes and board edge
npth=[(5,5,3.2),(165,5,3.2),(5,125,3.2),(165,125,3.2),(144.66,84.34,1.2),(124.34,104.66,1.2)]
def seg_d(px,py,a,b):
    x1,y1=a;x2,y2=b;dx,dy=x2-x1,y2-y1;L2=dx*dx+dy*dy;t=0 if L2==0 else max(0,min(1,((px-x1)*dx+(py-y1)*dy)/L2));return math.hypot(px-(x1+t*dx),py-(y1+t*dy))
for (hx,hy,hd) in npth:
    best=min(seg_d(hx,hy,r[i],r[(i+1)%len(r)]) for r in bregs for i in range(len(r)))
    print(f"   NPTH {hd}mm at ({hx},{hy}): pour edge {best-hd/2:.3f} mm from hole edge")
allpts=[p for r in bregs for p in r]
print(f"   pour to board edge: min x {min(p[0] for p in allpts):.2f}, max x {170-max(p[0] for p in allpts):.2f}, min y {min(p[1] for p in allpts):.2f}, max y {130-max(p[1] for p in allpts):.2f} (mm from edge)")
# approximate pour coverage via shoelace of the main region(s)
def area(r): return abs(sum(r[i][0]*r[(i+1)%len(r)][1]-r[(i+1)%len(r)][0]*r[i][1] for i in range(len(r))))/2
A=[area(r) for r in bregs]; print("   region areas mm2:", [round(a) for a in A], "sum", round(sum(A)), "of board", 170*130, f"= {sum(A)/(170*130)*100:.0f}% (outer polygons incl. holes' cutouts counted as filled)")
