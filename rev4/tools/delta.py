"""Pad-flash delta old vs new + identify components using rev-1 .kicad_pcb footprint pad positions."""
import sys, math, collections
sys.path.insert(0, sys.argv[0].rsplit('/', 1)[0])
from gerb import *
import pcbnew
OLD, NEW = sys.argv[1], sys.argv[2]
Lo, *_ = load_set(OLD); Ln, pth, pslots, npth, nslots = load_set(NEW)

def sig(layer, d):
    sh, pr, fn, _ = layer.apertures[d]; return (sh, tuple(round(p, 3) for p in pr))
def flashset(layer):
    return {(round(x, 2), round(y, 2), sig(layer, d)) for (x, y, d) in layer.flashes if layer.apertures[d][2] != 'ViaPad'}

for lay in ['F_Cu', 'B_Cu']:
    o, n = flashset(Lo[lay]), flashset(Ln[lay])
    print(f"{lay}: old pads {len(o)}, new pads {len(n)}, unchanged {len(o & n)}, removed/moved {len(o - n)}, added/moved {len(n - o)}")

# rev-1 footprints: refdes -> pad centers (gerber coords: y negated)
b = pcbnew.LoadBoard("WavetableController.kicad_pcb")
fps = []
for fp in b.GetFootprints():
    pads = [(pcbnew.ToMM(p.GetPosition().x), -pcbnew.ToMM(p.GetPosition().y), p.GetNumber()) for p in fp.Pads()]
    fps.append((fp.GetReference(), fp.GetValue(), fp.GetFPID().GetLibItemName(), pcbnew.ToMM(fp.GetPosition().x), -pcbnew.ToMM(fp.GetPosition().y), pads))

# new pad centers (B_Cu + F_Cu, dedupe by position)
newpads = {}
for lay in ['B_Cu', 'F_Cu']:
    for (x, y, d) in Ln[lay].flashes:
        if Ln[lay].apertures[d][2] == 'ViaPad': continue
        newpads[(round(x, 2), round(y, 2))] = (lay, sig(Ln[lay], d))
newpts = list(newpads.keys()); tree = STRtree([Point(*p) for p in newpts])
def has_pad(x, y, tol=0.15):
    return len(tree.query(Point(x, y).buffer(tol))) > 0

print("\n## rev-1 footprints checked against new pad positions (all pads present at same coords => unmoved)")
unmoved, moved = [], []
for ref, val, lib, fx, fy, pads in fps:
    hits = sum(has_pad(x, y) for x, y, _ in pads)
    (unmoved if hits == len(pads) else moved).append((ref, val, lib, round(fx, 1), round(fy, 1), hits, len(pads)))
print(f"unmoved: {len(unmoved)}: " + ", ".join(r[0] for r in sorted(unmoved)))
print(f"moved/removed/changed ({len(moved)}):")
for r in sorted(moved): print(f"    {r[0]:14s} {r[1]:28s} rev1@({r[3]},{r[4]}) pads matched {r[5]}/{r[6]}")

# new pads not explained by any unmoved rev-1 footprint -> cluster into likely new/moved footprints
explained = set()
for ref, val, lib, fx, fy, pads in fps:
    if any(ref == u[0] for u in unmoved):
        for x, y, _ in pads:
            for i in tree.query(Point(x, y).buffer(0.15)): explained.add(newpts[i])
unexpl = [p for p in newpts if p not in explained]
# simple single-linkage clustering, 2.5mm
clusters = []
for p in unexpl:
    merged = None
    for c in clusters:
        if any(math.hypot(p[0]-q[0], p[1]-q[1]) < 2.5 for q in c):
            if merged is None: c.append(p); merged = c
            else: merged.extend(c); c.clear()
    if merged is None: clusters.append([p])
clusters = [c for c in clusters if c]
print(f"\n## unexplained new pads: {len(unexpl)} in {len(clusters)} clusters (likely new or relocated footprints)")
for c in sorted(clusters, key=lambda c: (-len(c))):
    xs = [p[0] for p in c]; ys = [p[1] for p in c]
    sigs = collections.Counter(f"{newpads[p][0]}:{newpads[p][1][0]}{newpads[p][1][1]}" for p in c)
    print(f"  n={len(c):3d} center=({sum(xs)/len(xs):.1f},{sum(ys)/len(ys):.1f}) span=({max(xs)-min(xs):.1f}x{max(ys)-min(ys):.1f}) {dict(sigs.most_common(3))}")

# encoder click pads: copper now?
print("\n## rev-1 fab-truth re-checks at rev-1 coordinates")
polys = {lay: Ln[lay].all_polys() for lay in ['F_Cu','B_Cu']}; trees = {lay: STRtree(polys[lay]) for lay in polys}
for ref in ['ENCL1', 'ENCR1']:
    for r in fps:
        if r[0] == ref:
            for x, y, num in r[5]:
                print(f'  {ref} pads: {[n for _,_,n in r[5]]}') if num==r[5][0][2] else None
                if num in ('S1', 'S2', 'SW1', 'SW2') or num.startswith('S'):
                    for lay in ['F_Cu','B_Cu']:
                        near = trees[lay].query(Point(x, y).buffer(1.6))
                        tracks = [i for i in near if i >= len(Ln[lay].pad_polys) and i < len(Ln[lay].pad_polys) + len(Ln[lay].track_polys)]
                        print(f"  {ref}.{num} at ({x:.2f},{y:.2f}) {lay}: pad present={has_pad(x,y)} copper features within 1.6mm={len(near)} tracks={len(tracks)}")
