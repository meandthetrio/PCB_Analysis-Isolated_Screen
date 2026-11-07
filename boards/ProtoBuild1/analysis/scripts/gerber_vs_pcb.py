"""Compare copper draws in the KiCad-10-plotted Gerbers against segments in the v8 .kicad_pcb (text parse)."""
import re, sys, collections
def parse_gerber(path):
    txt = open(path).read()
    fs = re.search(r'%FSLAX(\d)(\d)Y', txt); dec = int(fs.group(2))
    scale = 10**dec
    aps = {}
    for m in re.finditer(r"%ADD(\d+)([A-Za-z_]+),([\d.]+)(?:X([\d.]+))?[^*]*\*%", txt):
        aps[m.group(1)] = (m.group(2), float(m.group(3)), float(m.group(4)) if m.group(4) else None)
    cur=None; x=y=0; draws=[]; flashes=[]; inreg=False; regions=0
    for line in txt.splitlines():
        if line.startswith('G36'): inreg=True; regions+=1; continue
        if line.startswith('G37'): inreg=False; continue
        m = re.match(r'D(\d+)\*$', line)
        if m and m.group(1) not in ('01','02','03'): cur=m.group(1); continue
        m = re.match(r'(?:X(-?\d+))?(?:Y(-?\d+))?D0([123])\*', line)
        if m:
            nx = int(m.group(1))/scale if m.group(1) else x
            ny = int(m.group(2))/scale if m.group(2) else y
            op = m.group(3)
            if op=='1' and not inreg: draws.append((x,-y,nx,-ny,aps[cur][1]))
            elif op=='3': flashes.append((nx,-ny,aps[cur]))
            x,y = nx,ny
    return draws, flashes, regions
def parse_pcb_segments(path):
    txt = open(path).read()
    segs = collections.defaultdict(list)
    for m in re.finditer(r'\(segment \(start ([-\d.]+) ([-\d.]+)\) \(end ([-\d.]+) ([-\d.]+)\) \(width ([\d.]+)\) \(layer "([^"]+)"\) \(net (\d+)\)', txt):
        x1,y1,x2,y2,w = map(float, m.groups()[:5]); segs[m.group(6)].append((x1,y1,x2,y2,w,int(m.group(7))))
    vias = [(float(a),float(b),float(c),float(d)) for a,b,c,d in re.findall(r'\(via \(at ([-\d.]+) ([-\d.]+)\) \(size ([\d.]+)\) \(drill ([\d.]+)\)', txt)]
    return segs, vias
def key(x1,y1,x2,y2,w):
    a=(round(x1,2),round(y1,2)); b=(round(x2,2),round(y2,2))
    return (min(a,b),max(a,b),round(w,2))
segs, vias = parse_pcb_segments(sys.argv[1])
print(f"PCB: segments F.Cu={len(segs['F.Cu'])} B.Cu={len(segs['B.Cu'])}, vias={len(vias)}")
for layer, gfile in (("F.Cu", sys.argv[2]), ("B.Cu", sys.argv[3])):
    draws, flashes, regions = parse_gerber(gfile)
    gk = collections.Counter(key(*d) for d in draws)
    pk = collections.Counter(key(*s[:5]) for s in segs[layer])
    only_g = gk - pk; only_p = pk - gk
    common = sum((gk & pk).values())
    widths = collections.Counter(round(d[4],2) for d in draws)
    print(f"{layer}: gerber draws={len(draws)} (widths {dict(widths)}), regions={regions}, flashes={len(flashes)}; pcb segs={len(segs[layer])}; exact matches={common}; gerber-only={sum(only_g.values())}; pcb-only={sum(only_p.values())}")
    for k,n in list(only_g.items())[:5]: print("    gerber-only:", k)
    for k,n in list(only_p.items())[:5]: print("    pcb-only   :", k)
    # pcb segment widths & lengths
    import math
    L = collections.defaultdict(float)
    for x1,y1,x2,y2,w,net in segs[layer]: L[round(w,2)] += math.hypot(x2-x1,y2-y1)
    print(f"    pcb trace length by width (mm): { {k:round(v,1) for k,v in L.items()} }")
