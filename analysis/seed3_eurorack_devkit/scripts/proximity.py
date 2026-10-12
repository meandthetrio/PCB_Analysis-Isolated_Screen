"""Aggressor/victim proximity: for same-layer segment pairs between aggressor nets and victim nets, report the
minimum edge-to-edge gap and the parallel-run length at gap <= GAP mm. Also counts opposite-layer crossings."""
import sys, json, math
pcb=json.load(open(sys.argv[1])); agg=sys.argv[2].split(','); vic=sys.argv[3].split(','); GAP=float(sys.argv[4])
def segs(n): return [t for t in pcb['nets'].get(n,{}).get('tracks',[]) if t['kind']=='seg' and t['L']>0.01]
def seg_dist(a,b):
    # min distance between two segments (centerlines)
    def pd(px,py,ax,ay,bx,by):
        L2=(bx-ax)**2+(by-ay)**2; u=max(0,min(1,((px-ax)*(bx-ax)+(py-ay)*(by-ay))/L2)); return math.hypot(px-(ax+u*(bx-ax)),py-(ay+u*(by-ay)))
    return min(pd(a['x1'],a['y1'],b['x1'],b['y1'],b['x2'],b['y2']),pd(a['x2'],a['y2'],b['x1'],b['y1'],b['x2'],b['y2']),
               pd(b['x1'],b['y1'],a['x1'],a['y1'],a['x2'],a['y2']),pd(b['x2'],b['y2'],a['x1'],a['y1'],a['x2'],a['y2']))
def parallel_overlap(a,b):
    # projection overlap of b onto a's direction, if roughly parallel (<15 deg)
    ax,ay=a['x2']-a['x1'],a['y2']-a['y1']; bx,by=b['x2']-b['x1'],b['y2']-b['y1']
    la=math.hypot(ax,ay); lb=math.hypot(bx,by); cos=abs(ax*bx+ay*by)/(la*lb)
    if cos<math.cos(math.radians(15)): return 0.0
    ux,uy=ax/la,ay/la
    p=[((b['x1']-a['x1'])*ux+(b['y1']-a['y1'])*uy),((b['x2']-a['x1'])*ux+(b['y2']-a['y1'])*uy)]
    return max(0.0,min(la,max(p))-max(0.0,min(p)))
def cross(a,b):
    def ccw(ax,ay,bx,by,cx,cy): return (cx-ax)*(by-ay)-(bx-ax)*(cy-ay)
    return (ccw(a['x1'],a['y1'],a['x2'],a['y2'],b['x1'],b['y1'])*ccw(a['x1'],a['y1'],a['x2'],a['y2'],b['x2'],b['y2'])<0 and
            ccw(b['x1'],b['y1'],b['x2'],b['y2'],a['x1'],a['y1'])*ccw(b['x1'],b['y1'],b['x2'],b['y2'],a['x2'],a['y2'])<0)
rows=[]
for A in agg:
    for V in vic:
        mind=1e9; par=0.0; crossings=0
        for a in segs(A):
            for b in segs(V):
                if a['layer']==b['layer']:
                    g=seg_dist(a,b)-a['w']/2-b['w']/2
                    mind=min(mind,g)
                    if g<=GAP: par+=parallel_overlap(a,b)
                else:
                    if cross(a,b): crossings+=1
        if mind<1e8 and (mind<=GAP or crossings): rows.append((A,V,round(mind,3),round(par,1),crossings))
rows.sort(key=lambda r:(r[2],-r[3]))
print(f"{'aggressor':<16}{'victim':<18}{'min gap mm':>11}{'parallel@<=%.1fmm'%GAP:>20}{'xings':>7}")
for r in rows: print(f"{r[0]:<16}{r[1]:<18}{r[2]:>11}{r[3]:>20}{r[4]:>7}")
