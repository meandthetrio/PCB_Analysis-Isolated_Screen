import sys, math, collections
sys.path.insert(0, sys.argv[0].rsplit('/', 1)[0])
from gerb import *
d = sys.argv[1]
L, pth, pslots, npth, nslots = load_set(d)
outl = outline_polygons(L['Edge_Cuts'])
outl.sort(key=lambda p: -p.area)
board = outl[0]
print(f"# Geometry checks on {d}")
print(f"outline polygons: {len(outl)}; main {board.bounds} area {board.area:.0f} mm2; others: {[round(p.area,2) for p in outl[1:]]}")

# ---- 1. annular rings
print("\n## 1. Annular rings (PTH drill vs copper pad on each layer); JLCPCB 2L: abs min 0.18, recommended 0.25")
rows = []
for layer in ['F_Cu', 'B_Cu']:
    tree = STRtree([p for p, _, _ in L[layer].pad_polys])
    for (x, y, dia) in pth:
        pt = Point(x, y)
        idx = tree.query(pt.buffer(0.01))
        best = None
        for i in idx:
            poly, dc, fn = L[layer].pad_polys[i]
            if poly.contains(pt):
                ring = poly.exterior.distance(pt) - dia / 2
                if best is None or ring < best[0]: best = (ring, dc, fn, poly)
        rows.append((layer, x, y, dia, best))
nopad = [(l, x, y, dia) for (l, x, y, dia, b) in rows if b is None]
print(f"holes with no containing pad: {len(nopad)}  {nopad[:10]}")
rings = [(b[0], l, x, y, dia, b[2]) for (l, x, y, dia, b) in rows if b]
rings.sort()
vias = [r for r in rings if r[5] == 'ViaPad']; comp = [r for r in rings if r[5] != 'ViaPad']
vc = collections.Counter((r[4], round(r[0]*2 + r[4], 2)) for r in vias)
print(f"vias (ViaPad) drill/pad combos: {dict(vc)}  -> JLCPCB via min 0.15 hole / 0.25 dia; min via ring seen {min(r[0] for r in vias):.3f}")
c = collections.Counter()
for r in comp:
    c['<0.18 VIOLATION' if r[0] < 0.18 - 1e-6 else ('<0.25 below-recommended' if r[0] < 0.25 - 1e-6 else '>=0.25 ok')] += 1
print("component PTH pads:", dict(c))
for r in comp:
    if r[0] < 0.25 - 1e-6: print(f"  ring={r[0]:.3f} {r[1]} ({r[2]:.3f},{r[3]:.3f}) drill={r[4]} {r[5]}")

# ---- 2. NPTH to copper
print("\n## 2. NPTH to copper (JLCPCB NPTH-to-track 0.2mm)")
for layer in ['F_Cu', 'B_Cu']:
    polys = L[layer].all_polys(); tree = STRtree(polys)
    for (x, y, dia) in npth:
        pt = Point(x, y); near = tree.query(pt.buffer(dia / 2 + 0.3))
        dmin = min((polys[i].distance(pt) - dia / 2 for i in near), default=9)
        if dmin < 0.2: print(f"  {layer} NPTH ({x:.3f},{y:.3f}) d={dia}: copper at {dmin:.3f} mm {'VIOLATION' if dmin < 0.2 else ''}")
    for s in nslots:
        (x1, y1), (x2, y2), dia = s
        ls = LineString([(x1, y1), (x2, y2)]); near = tree.query(ls.buffer(dia / 2 + 0.3))
        dmin = min((polys[i].distance(ls) - dia / 2 for i in near), default=9)
        if dmin < 0.2: print(f"  {layer} NPTH slot ({x1},{y1})-({x2},{y2}) d={dia}: copper at {dmin:.3f} mm")

# ---- 3. copper to edge
print("\n## 3. Copper to board edge (JLCPCB >=0.2mm routed)")
edge = board.exterior
for layer in ['F_Cu', 'B_Cu']:
    hits = []
    for p in L[layer].all_polys():
        if not board.covers(p):
            hits.append(('OUTSIDE/crossing', p.representative_point(), p.bounds))
            continue
        dd = p.distance(edge)
        if dd < 0.2: hits.append((f'{dd:.3f}', p.representative_point(), p.bounds))
    print(f"  {layer}: {len(hits)} features closer than 0.2mm or crossing")
    for h in hits[:20]: print(f"     {h[0]} at ({h[1].x:.2f},{h[1].y:.2f}) bounds {tuple(round(v,2) for v in h[2])}")

# ---- 4. hole to hole
print("\n## 4. Hole-to-hole edge spacing (JLCPCB via-via 0.2, pad hole-hole 0.45)")
allh = [(x, y, dia, 'via' if dia <= 0.3 else 'pad') for (x, y, dia) in pth] + [(x, y, dia, 'npth') for (x, y, dia) in npth]
pts = [Point(x, y) for (x, y, _, _) in allh]; tree = STRtree(pts)
bad = []
for i, (x, y, dia, k) in enumerate(allh):
    for j in tree.query(pts[i].buffer(dia / 2 + 1.5)):
        if j <= i: continue
        x2, y2, dia2, k2 = allh[j]
        gap = math.hypot(x - x2, y - y2) - dia / 2 - dia2 / 2
        lim = 0.2 if (k == 'via' and k2 == 'via') else 0.45
        if gap < lim: bad.append((round(gap, 3), lim, (x, y, dia, k), (x2, y2, dia2, k2)))
bad.sort()
print(f"  {len(bad)} pairs below limit"); [print("   ", b) for b in bad[:25]]

# ---- 5. silkscreen
print("\n## 5. Silkscreen")
for layer, mask in [('F_Silkscreen', 'F_Mask'), ('B_Silkscreen', 'B_Mask')]:
    S = L[layer]
    widths = collections.Counter()
    for ls, w, dcode in S.track_lines: widths[w] += ls.length
    print(f"  {layer}: draws={len(S.draws)} regions={len(S.regions)} line length by width: " + ", ".join(f"{w}:{l:.0f}mm" for w, l in sorted(widths.items())))
    feats = [p for p, _ in S.track_polys] + list(S.regions)
    outside = [p for p in feats if not board.covers(p)]
    ob = unary_union(outside).bounds if outside else None
    print(f"    features outside/crossing outline: {len(outside)}  bounds={ob and tuple(round(v,2) for v in ob)}")
    # silk vs mask openings (exposed copper)
    masks = [p for p, _, _ in L[mask].pad_polys]; mt = STRtree(masks)
    over = 0; near = 0
    for p in feats:
        for i in mt.query(p.buffer(0.15)):
            dd = masks[i].distance(p)
            if dd == 0: over += 1; break
            elif dd < 0.15: near += 1; break
    print(f"    silk features touching a mask opening: {over}; within 0.15mm: {near}  (JLCPCB pad-to-silk 0.15)")
    area_regions = sum(p.area for p in S.regions)
    print(f"    region fill area {area_regions:.0f} mm2; region bbox {unary_union(S.regions).bounds if S.regions else None}")

# ---- 6. pours
print("\n## 6. Copper regions (pours)")
for layer in ['F_Cu', 'B_Cu']:
    print(f"  {layer}: {len(L[layer].regions)} regions, total {sum(p.area for p in L[layer].regions):.0f} mm2 of board {board.area:.0f} mm2")
    for p in sorted(L[layer].regions, key=lambda p: -p.area)[:8]:
        print(f"     area={p.area:8.1f} bbox={tuple(round(v,1) for v in p.bounds)}")

# ---- 7. residual narrow tracks
print("\n## 7. Track widths (JLCPCB min 0.1, ±20%)")
for layer in ['F_Cu', 'B_Cu']:
    w = collections.defaultdict(float); narrow = []
    for ls, wd, dc in L[layer].track_lines:
        w[wd] += ls.length
        if wd < 0.2: narrow.append((round(ls.length, 2), tuple(round(v, 2) for v in ls.bounds)))
    print(f"  {layer}: " + ", ".join(f"{k}mm:{v:.0f}mm" for k, v in sorted(w.items())))
    print(f"    segments <0.2mm: {len(narrow)}; " + "; ".join(f"len {a} at {b}" for a, b in sorted(narrow, reverse=True)[:12]))

# ---- 8. copper-copper gaps below 0.1 (fab violation regardless of net)
print("\n## 8. Copper-to-copper gaps 0 < g < 0.10 mm (JLCPCB min spacing 0.1); also 0.10-0.127 for info")
for layer in ['F_Cu', 'B_Cu']:
    polys = L[layer].all_polys(); tree = STRtree(polys); found = []
    for i, p in enumerate(polys):
        for j in tree.query(p.buffer(0.13)):
            if j <= i: continue
            g = p.distance(polys[j])
            if 1e-4 < g < 0.13: found.append((round(g, 4), tuple(round(v, 2) for v in p.intersection(polys[j].buffer(g + 0.01)).bounds)))
    found.sort()
    viol = [f for f in found if f[0] < 0.1 - 1e-6]
    print(f"  {layer}: {len(viol)} gaps <0.10 (violations), {len(found) - len(viol)} gaps 0.10-0.13")
    for f in found[:15]: print("    ", f)
