"""Per-net copper geometry + copper-path verification from pcb_export.json.
Builds a graph of segments/vias/pads (endpoint coincidence, 1um tolerance; vias join layers; TH pads join layers),
reports: islands (copper connectivity ignoring zones), shortest copper path length between two named pads,
total track length, width breakdown, via count, longest dangling branch (stub). Zones are ignored, so GND is excluded."""
import sys, json, math, heapq
from collections import defaultdict
pcb=json.load(open(sys.argv[1]))
want=sys.argv[2].split(',') if len(sys.argv)>2 else None
TOL=0.002
def key(x,y,layer): return (round(x/TOL),round(y/TOL),layer)
pad_at={}
for fp in pcb['footprints']:
    for p in fp['pads']:
        if p['net']: pad_at.setdefault(p['net'],[]).append((fp['ref']+'.'+p['num'],p['x'],p['y'],p['layers'],p['type']))
out={}
for net,d in pcb['nets'].items():
    if net=='GND' or (want and net not in want): continue
    nodes={}; adj=defaultdict(list)
    def nid(k):
        if k not in nodes: nodes[k]=len(nodes)
        return nodes[k]
    def link(a,b,L):
        adj[a].append((b,L)); adj[b].append((a,L))
    for t in d['tracks']:
        if t['kind']=='seg':
            link(nid(key(t['x1'],t['y1'],t['layer'])),nid(key(t['x2'],t['y2'],t['layer'])),t['L'])
        else:
            link(nid(key(t['x'],t['y'],'F.Cu')),nid(key(t['x'],t['y'],'B.Cu')),0.0)
    padnode={}
    for name,x,y,layers,typ in pad_at.get(net,[]):
        ids=[nid(key(x,y,l)) for l in (layers if layers else ['F.Cu','B.Cu'])]
        for a in ids[1:]: link(ids[0],a,0.0)
        padnode[name]=ids[0]
    # a segment end landing anywhere on a pad (not exactly at its centre) - snap: join pad node to any node within pad radius-ish (0.9mm)
    for name,x,y,layers,typ in pad_at.get(net,[]):
        for k,i in list(nodes.items()):
            if k[2] in (layers or ['F.Cu','B.Cu']) and abs(k[0]*TOL-x)<0.9 and abs(k[1]*TOL-y)<0.9 and i!=padnode[name]:
                link(padnode[name],i,math.hypot(k[0]*TOL-x,k[1]*TOL-y))
    # T-junctions: a node lying on the interior of a same-layer segment (within half-width) joins that segment
    segs=[t for t in d['tracks'] if t['kind']=='seg']
    for k,i in list(nodes.items()):
        px,py=k[0]*TOL,k[1]*TOL
        for t in segs:
            if t['layer']!=k[2]: continue
            ax,ay,bx,by=t['x1'],t['y1'],t['x2'],t['y2']; L=t['L']
            if L<1e-6: continue
            u=((px-ax)*(bx-ax)+(py-ay)*(by-ay))/(L*L)
            if u<=0.001 or u>=0.999: continue
            cx,cy=ax+u*(bx-ax),ay+u*(by-ay)
            if math.hypot(px-cx,py-cy)<=t['w']/2+0.01:
                link(i,nid(key(ax,ay,t['layer'])),u*L); link(i,nid(key(bx,by,t['layer'])),(1-u)*L)
    # islands
    seen={}; comp=0
    for s in nodes.values():
        if s in seen: continue
        comp+=1; st=[s]; seen[s]=comp
        while st:
            u=st.pop()
            for v,_ in adj[u]:
                if v not in seen: seen[v]=comp; st.append(v)
    pad_islands={n:seen[i] for n,i in padnode.items()}
    # shortest path between the two "endpoint" pads = the pair with max path (report all pad pairs if <=4 pads)
    def dijkstra(src):
        dist={src:0.0}; pq=[(0.0,src)]
        while pq:
            dd,u=heapq.heappop(pq)
            if dd>dist[u]: continue
            for v,L in adj[u]:
                nd=dd+L
                if nd<dist.get(v,1e9): dist[v]=nd; heapq.heappush(pq,(nd,v))
        return dist
    paths={}
    names=list(padnode)
    for i,a in enumerate(names):
        dist=dijkstra(padnode[a])
        for b in names[i+1:]:
            if padnode[b] in dist: paths[f"{a}<->{b}"]=round(dist[padnode[b]],1)
    # stubs: leaf nodes (degree 1) that are not pads -> walk back until a junction
    padset=set(padnode.values()); stubs=[]
    for n,i in nodes.items():
        if len(adj[i])==1 and i not in padset:
            L=0; u=i; prev=None
            while len(adj[u])<=2 and u not in padset:
                nxt=[(v,l) for v,l in adj[u] if v!=prev]
                if not nxt: break
                v,l=nxt[0]; L+=l; prev,u=u,v
                if len(adj[u])!=2: break
            stubs.append(round(L,2))
    out[net]=dict(pads=len(padnode),islands=comp,pad_islands=pad_islands,total_len=round(d['len'],1),vias=d['vias'],
                  widths={k:round(v,1) for k,v in d['widths'].items()},paths=paths,stubs=sorted(stubs,reverse=True)[:5])
json.dump(out,open(sys.argv[3],'w'),indent=1)
for net,o in sorted(out.items()):
    isl='OK' if len(set(o['pad_islands'].values()))==1 else 'SPLIT:'+str(o['pad_islands'])
    print(f"{net:<24} pads={o['pads']} copper-islands={isl} len={o['total_len']:>6} vias={o['vias']} widths={o['widths']} stubs={o['stubs']}")
    for k,v in o['paths'].items(): print(f"     path {k}: {v} mm")
