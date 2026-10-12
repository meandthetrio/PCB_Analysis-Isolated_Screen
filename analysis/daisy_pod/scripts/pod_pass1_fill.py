#!/usr/bin/env python3
"""Daisy Pod Rev5 (KiCad conversion) — Pass 1 fill / connectivity / mask checks. Read-only.
Zones, fill fragments and what they touch, fill-only GND pads, GND vias, via tenting, pad mask margins,
pad-to-pad gaps and the resulting mask slivers, fiducial-to-fill gap, via-to-mounting-hole distance.
Run: python3 pod_pass1_fill.py [board.kicad_pcb]   (pcbnew script; no -I)"""
import pcbnew, collections, math, sys
B = sys.argv[1] if len(sys.argv) > 1 else '/home/user/PCB_Analysis-Isolated_Screen/reference/electrosmith/daisy_pod/kicad/ES_Daisy_Pod_Rev5.kicad_pcb'
b = pcbnew.LoadBoard(B); mm = pcbnew.ToMM
FCU, BCU = pcbnew.F_Cu, pcbnew.B_Cu; LN = {FCU: 'F.Cu', BCU: 'B.Cu'}
fps = {fp.GetReference(): fp for fp in b.GetFootprints()}
pads = [(f.GetReference() + '.' + p.GetNumber(), p) for f in b.GetFootprints() for p in f.Pads()]
vias = [t for t in b.GetTracks() if t.GetClass() == 'PCB_VIA']

def chain_pts(ch): return [(mm(ch.CPoint(i).x), mm(ch.CPoint(i).y)) for i in range(ch.PointCount())]
def d_pt_seg(p, a, c):
    ax, ay = a; bx, by = c; px, py = p; dx, dy = bx - ax, by - ay; L2 = dx * dx + dy * dy
    if L2 == 0: return math.hypot(px - ax, py - ay)
    t = max(0, min(1, ((px - ax) * dx + (py - ay) * dy) / L2)); return math.hypot(px - (ax + t * dx), py - (ay + t * dy))
def edges(P): n = len(P); return [(P[i], P[(i + 1) % n]) for i in range(n)]
def d_edges(E1, E2):
    best = 1e9
    for a, c in E1:
        for e, f in E2:
            v = min(d_pt_seg(a, e, f), d_pt_seg(c, e, f), d_pt_seg(e, a, c), d_pt_seg(f, a, c))
            if v < best: best = v
    return best
def pad_edges(p, L):
    poly = p.GetEffectivePolygon(L); return edges(chain_pts(poly.Outline(0)))
def via_r(v, L):
    try: return v.GetWidth(L) / 2
    except TypeError: return v.GetWidth() / 2

print('== zones')
zones = list(b.Zones())
for z in zones:
    bb = z.GetBoundingBox()
    print('  net', z.GetNetname(), [b.GetLayerName(L) for L in z.GetLayerSet().Seq()], 'priority', z.GetAssignedPriority(), 'min_thk', mm(z.GetMinThickness()),
          'clearance', mm(z.GetLocalClearance()), 'thermal gap/spoke', mm(z.GetThermalReliefGap()), mm(z.GetThermalReliefSpokeWidth()), 'pad_conn', z.GetPadConnection(),
          'island_removal', z.GetIslandRemovalMode(), 'outline verts', z.Outline().Outline(0).PointCount(), 'bbox', [round(mm(v), 2) for v in (bb.GetLeft(), bb.GetTop(), bb.GetRight(), bb.GetBottom())])
outline = pcbnew.SHAPE_POLY_SET(); b.GetBoardPolygonOutlines(outline)
area = outline.Outline(0).Area() / 1e12; print('  board outline area mm2', round(area, 1))
frags = []
for zi, z in enumerate(zones):
    for L in z.GetLayerSet().Seq():
        fp = z.GetFilledPolysList(L)
        for i in range(fp.OutlineCount()):
            frag = pcbnew.SHAPE_POLY_SET(); frag.AddOutline(fp.Outline(i))
            for h in range(fp.HoleCount(i)): frag.AddHole(fp.Hole(i, h), -1)
            frags.append((zi, L, i, frag, fp.Outline(i).Area() / 1e12))
print('== fill fragments')
for zi, L, i, frag, a in frags:
    bb = frag.BBox()
    tp = [n for n, p in pads if p.GetNetname() == 'GND' and p.IsOnLayer(L) and p.GetBoundingBox().Intersects(bb) and frag.Collide(p.GetEffectivePolygon(L), 0)]
    tv = [(round(mm(v.GetPosition().x), 2), round(mm(v.GetPosition().y), 2)) for v in vias if v.GetNetname() == 'GND' and bb.Contains(v.GetPosition()) and frag.Collide(pcbnew.SHAPE_CIRCLE(v.GetPosition(), int(via_r(v, L))), 0)]
    print(f'  zone{zi} {LN[L]} frag{i}: {a:.1f} mm2 ({100*a/area:.0f}% of board) bbox {[round(mm(x),1) for x in (bb.GetLeft(),bb.GetTop(),bb.GetRight(),bb.GetBottom())]} GND pads touching {len(tp)} {tp if len(tp)<=17 else ""} GND vias touching {len(tv)} {tv if len(tv)<=3 else ""}')
for L in (FCU, BCU):
    gp = [(n, p) for n, p in pads if p.GetNetname() == 'GND' and p.IsOnLayer(L)]
    nf = [n for n, p in gp if not any(fr.Collide(p.GetEffectivePolygon(L), 0) for zi, FL, i, fr, a in frags if FL == L)]
    print(f'  {LN[L]} GND pad-faces {len(gp)}, not touching any fill: {nf}')
c = b.GetConnectivity()
only_fill = [n for n, p in pads if p.GetNetname() == 'GND' and len(c.GetConnectedTracks(p)) == 0]
print('== GND pads with no track at all (fill-only):', len(only_fill), only_fill)
gv = [v for v in vias if v.GetNetname() == 'GND']
print('== GND vias:', len(gv), 'of', len(vias), 'total; density', round(len(gv) / (area / 100), 2), 'per cm2; positions', sorted((round(mm(v.GetPosition().x), 1), round(mm(v.GetPosition().y), 1)) for v in gv))
print('== via tenting (on F.Mask, on B.Mask):', collections.Counter((v.IsOnLayer(pcbnew.F_Mask), v.IsOnLayer(pcbnew.B_Mask)) for v in vias))
# pad local mask margin (Eagle mlMinStopFrame carried over per pad?)
mg = collections.Counter()
for n, p in pads:
    m = p.GetLocalSolderMaskMargin(); m = m.value() if hasattr(m, 'value') else m
    mg[None if m is None else round(mm(m), 4)] += 1
print('== pad local solder-mask margin histogram (mm):', dict(mg), '| board mask expansion', mm(b.GetDesignSettings().m_SolderMaskExpansion), 'min width', mm(b.GetDesignSettings().m_SolderMaskMinWidth))
# pad-to-pad gaps (same layer), mask sliver = gap - 2*margin
MARGIN = 0.0762
gaps = []
for L in (FCU, BCU):
    P = [(n, p, pad_edges(p, L), p.GetBoundingBox()) for n, p in pads if p.IsOnLayer(L) and p.GetEffectivePolygon(L).OutlineCount()]
    for i in range(len(P)):
        for j in range(i + 1, len(P)):
            n1, p1, E1, b1 = P[i]; n2, p2, E2, b2 = P[j]
            bb = p1.GetBoundingBox(); bb.Inflate(pcbnew.FromMM(0.8))
            if not bb.Intersects(b2): continue
            d = d_edges(E1, E2)
            if d < 0.8: gaps.append((round(d, 4), n1, p1.GetNetname(), n2, p2.GetNetname(), LN[L]))
gaps.sort()
byfp = {}
for g in gaps:
    a = g[1].split('.')[0]; cc = g[3].split('.')[0]; k = a if a == cc else a + '/' + cc
    byfp[k] = min(byfp.get(k, 9), g[0])
print('== min pad-to-pad gap by footprint (<0.8 mm), and mask sliver = gap - 2 x 0.0762:')
for k, v in sorted(byfp.items(), key=lambda x: x[1]): print(f'   {k:12s} gap {v:.4f}  sliver {v - 2*MARGIN:.4f}')
print('   tightest different-net pad pairs:', [g for g in gaps if g[2] != g[4]][:4])
# fiducials: gap from the 1 mm pad to the fill, and the mask polygon size
print('== fiducials')
for r_ in ('FD1', 'FD2', 'FD3', 'FD4', 'FD5', 'FD6'):
    fp = fps[r_]; p = list(fp.Pads())[0]; L = BCU if fp.IsFlipped() else FCU
    E = pad_edges(p, L); best = 9
    for zi, FL, i, fr, a in frags:
        if FL != L: continue
        for k in range(fr.OutlineCount()):
            O = chain_pts(fr.Outline(k))
            bb = fr.BBox()
            best = min(best, d_edges(E, [(O[q], O[(q + 1) % len(O)]) for q in range(len(O)) if abs(O[q][0] - mm(p.GetPosition().x)) < 3 and abs(O[q][1] - mm(p.GetPosition().y)) < 3]))
    g = [(gi.GetLayerName(), gi.ShowShape(), [round(mm(v), 3) for v in (gi.GetBoundingBox().GetLeft(), gi.GetBoundingBox().GetTop(), gi.GetBoundingBox().GetRight(), gi.GetBoundingBox().GetBottom())], round(mm(gi.GetWidth()), 3)) for gi in fp.GraphicalItems()]
    print(f'  {r_} {LN[L]} pad {mm(p.GetSize(L).x)} mm, pad layers {[b.GetLayerName(l) for l in p.GetLayerSet().Seq()]}, fill-to-pad gap {best:.4f} mm, mask graphic {g}')
# via / track proximity to mounting holes (Eagle vRestrict r=3.556 was stripped)
print('== mounting holes H1-H4: nearest via centre / nearest track end (Eagle vRestrict radius 3.556 mm, bKeepout/tKeepout 3.683 mm, stripped in conversion)')
for h in ('H1', 'H2', 'H3', 'H4'):
    cpos = fps[h].GetPosition()
    dv = min(math.hypot(mm(v.GetPosition().x - cpos.x), mm(v.GetPosition().y - cpos.y)) for v in vias)
    dt = min(min(math.hypot(mm(t.GetStart().x - cpos.x), mm(t.GetStart().y - cpos.y)), math.hypot(mm(t.GetEnd().x - cpos.x), mm(t.GetEnd().y - cpos.y))) for t in b.GetTracks() if t.GetClass() != 'PCB_VIA')
    print(f'  {h} ({mm(cpos.x):.3f},{mm(cpos.y):.3f}) nearest via {dv:.2f} mm, nearest track end {dt:.2f} mm')
# starved thermal: U7.2 and the other single-spoke candidates
print('== U7 pads (USBLC6) connections:', [(n, p.GetNetname(), len(c.GetConnectedTracks(p))) for n, p in pads if n.startswith('U7.')])
print('== footprint-level zones / rule areas:', [(fp.GetReference(), len(list(fp.Zones()))) for fp in b.GetFootprints() if len(list(fp.Zones()))], [(z.GetZoneName(), z.GetIsRuleArea()) for z in zones if z.GetIsRuleArea()])
