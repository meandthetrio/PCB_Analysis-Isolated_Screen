#!/usr/bin/env python3
"""Seed 3 dev kits (Eurorack / Pedal Rev3) — Pass 1 fill / connectivity / mask checks. Read-only (pcbnew, KiCad 9/10).
Zones, fill fragments and what they touch, fill-only GND pads, GND vias, how F-side GND pads reach the B plane
without GND vias (through which PTH pads), via tenting, pad mask margins, pad-to-pad gaps -> mask slivers,
J7 (USB-C) pad gaps vs its NPTH pegs, starved-thermal pads.  Run: python3 kit_pass1_fill.py <board.kicad_pcb>"""
import pcbnew, collections, math, sys
B = sys.argv[1]
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
def pad_edges(p, L): return edges(chain_pts(p.GetEffectivePolygon(L).Outline(0)))
def via_r(v, L):
    try: return v.GetWidth(L) / 2
    except TypeError: return v.GetWidth() / 2
outline = pcbnew.SHAPE_POLY_SET()
try: b.GetBoardPolygonOutlines(outline, False)
except TypeError: b.GetBoardPolygonOutlines(outline)
area = outline.Outline(0).Area() / 1e12
print('== board outline area mm2', round(area, 1), 'outlines', outline.OutlineCount(), 'cutouts', outline.HoleCount(0))
print('== zones')
zones = [z for z in b.Zones() if not z.GetIsRuleArea()]
for z in zones:
    bb = z.GetBoundingBox()
    print('  net', z.GetNetname(), [b.GetLayerName(L) for L in z.GetLayerSet().Seq()], 'priority', z.GetAssignedPriority(), 'min_thk', mm(z.GetMinThickness()),
          'clearance', mm(z.GetLocalClearance()), 'thermal gap/spoke', mm(z.GetThermalReliefGap()), mm(z.GetThermalReliefSpokeWidth()), 'pad_conn', z.GetPadConnection(),
          'island_removal', z.GetIslandRemovalMode(), 'outline verts', z.Outline().Outline(0).PointCount(), 'bbox', [round(mm(v), 2) for v in (bb.GetLeft(), bb.GetTop(), bb.GetRight(), bb.GetBottom())])
ra = [z for z in b.Zones() if z.GetIsRuleArea()] + [z for fp in b.GetFootprints() for z in fp.Zones()]
print('  rule areas (board + footprint):', len(ra), collections.Counter((z.GetParentFootprint().GetFPIDAsString() if z.GetParentFootprint() else 'board', tuple(b.GetLayerName(L) for L in z.GetLayerSet().Seq()), z.GetDoNotAllowZoneFills(), z.GetDoNotAllowVias(), z.GetDoNotAllowTracks()) for z in ra))
frags = []
for zi, z in enumerate(zones):
    for L in z.GetLayerSet().Seq():
        fp = z.GetFilledPolysList(L)
        for i in range(fp.OutlineCount()):
            frag = pcbnew.SHAPE_POLY_SET(); frag.AddOutline(fp.Outline(i))
            for h in range(fp.HoleCount(i)): frag.AddHole(fp.Hole(i, h), -1)
            frags.append((zi, L, i, frag, fp.Outline(i).Area() / 1e12, fp.HoleCount(i)))
print('== fill fragments')
gnd = b.GetNetcodeFromNetname('GND')
for zi, L, i, frag, a, nh in frags:
    bb = frag.BBox()
    tp = [n for n, p in pads if p.GetNetCode() == gnd and p.IsOnLayer(L) and p.GetBoundingBox().Intersects(bb) and frag.Collide(p.GetEffectivePolygon(L), 0)]
    tv = [(round(mm(v.GetPosition().x), 2), round(mm(v.GetPosition().y), 2)) for v in vias if v.GetNetCode() == gnd and bb.Contains(v.GetPosition()) and frag.Collide(pcbnew.SHAPE_CIRCLE(v.GetPosition(), int(via_r(v, L))), 0)]
    print(f'  zone{zi} {LN[L]} frag{i}: {a:.1f} mm2 ({100*a/area:.0f}% of board) holes-in-fill {nh} bbox {[round(mm(x),1) for x in (bb.GetLeft(),bb.GetTop(),bb.GetRight(),bb.GetBottom())]} GND pad-faces touching {len(tp)} GND vias touching {len(tv)} {tv if len(tv)<=6 else ""}')
for L in (FCU, BCU):
    gp = [(n, p) for n, p in pads if p.GetNetCode() == gnd and p.IsOnLayer(L)]
    nf = [n for n, p in gp if not any(fr.Collide(p.GetEffectivePolygon(L), 0) for zi, FL, i, fr, a, nh in frags if FL == L)]
    print(f'  {LN[L]} GND pad-faces {len(gp)}, not touching any fill: {len(nf)} {nf}')
c = b.GetConnectivity()
gpads = [(n, p) for n, p in pads if p.GetNetCode() == gnd]
only_fill = [n for n, p in gpads if len(c.GetConnectedTracks(p)) == 0]
print('== GND pads total', len(gpads), '| PTH', sum(1 for n, p in gpads if p.GetAttribute() == 0), '| SMD', sum(1 for n, p in gpads if p.GetAttribute() == 1), '| with no track at all (fill-only):', len(only_fill))
smd_f = [n for n, p in gpads if p.GetAttribute() == 1 and p.IsOnLayer(FCU)]; smd_b = [n for n, p in gpads if p.GetAttribute() == 1 and p.IsOnLayer(BCU)]
print('   SMD GND pads on F', len(smd_f), '| on B', len(smd_b), '| PTH GND pads (the only F<->B GND links if there are no GND vias):', sorted(collections.Counter(n.split('.')[0] for n, p in gpads if p.GetAttribute() == 0).items()))
gv = [v for v in vias if v.GetNetCode() == gnd]
print('== GND vias:', len(gv), 'of', len(vias), 'total; density', round(len(gv) / (area / 100), 3), 'per cm2; positions', sorted((round(mm(v.GetPosition().x), 1), round(mm(v.GetPosition().y), 1)) for v in gv))
print('   via nets (top):', collections.Counter(v.GetNetname() for v in vias).most_common(8))
print('== via tenting (on F.Mask, on B.Mask):', collections.Counter((v.IsOnLayer(pcbnew.F_Mask), v.IsOnLayer(pcbnew.B_Mask)) for v in vias), '| via sizes', collections.Counter((round(mm(via_r(v, FCU) * 2), 4), round(mm(v.GetDrillValue()), 3)) for v in vias))
# nearest F<->B GND link for each F-side SMD GND pad: nearest GND PTH pad (any footprint) by centre distance
pth_g = [(n, p) for n, p in gpads if p.GetAttribute() == 0]
far = []
for n, p in gpads:
    if p.GetAttribute() != 1: continue
    L = FCU if p.IsOnLayer(FCU) else BCU
    d = min(math.hypot(mm(p.GetPosition().x - q.GetPosition().x), mm(p.GetPosition().y - q.GetPosition().y)) for m, q in pth_g) if pth_g else 1e9
    dv = min([math.hypot(mm(p.GetPosition().x - v.GetPosition().x), mm(p.GetPosition().y - v.GetPosition().y)) for v in gv] or [1e9])
    far.append((round(min(d, dv), 1), n, LN[L]))
far.sort(reverse=True)
print('== SMD GND pads farthest from any layer-to-layer GND link (PTH GND pad or GND via), mm:', far[:12])
print('   histogram of that distance (mm, binned 5):', sorted(collections.Counter(int(d // 5) * 5 for d, *_ in far).items()))
mg = collections.Counter()
for n, p in pads:
    m = p.GetLocalSolderMaskMargin(); m = m.value() if hasattr(m, 'value') else m
    mg[None if m is None else round(mm(m), 4)] += 1
ds = b.GetDesignSettings()
print('== pad local solder-mask margin histogram (mm):', dict(mg), '| board mask expansion', mm(ds.m_SolderMaskExpansion), 'min width', mm(ds.m_SolderMaskMinWidth), '| paste margin', mm(ds.m_SolderPasteMargin), 'ratio', ds.m_SolderPasteMarginRatio)
gaps = []
for L in (FCU, BCU):
    P = [(n, p, pad_edges(p, L), p.GetBoundingBox()) for n, p in pads if p.IsOnLayer(L) and p.GetEffectivePolygon(L).OutlineCount()]
    for i in range(len(P)):
        for j in range(i + 1, len(P)):
            n1, p1, E1, b1 = P[i]; n2, p2, E2, b2 = P[j]
            bb = p1.GetBoundingBox(); bb.Inflate(pcbnew.FromMM(0.6))
            if not bb.Intersects(b2): continue
            d = d_edges(E1, E2)
            if d < 0.6: gaps.append((round(d, 4), n1, p1.GetNetname(), n2, p2.GetNetname(), LN[L]))
gaps.sort()
byfp = {}
for g in gaps:
    a = g[1].split('.')[0]; cc = g[3].split('.')[0]; k = a if a == cc else a + '/' + cc
    byfp[k] = min(byfp.get(k, 9), g[0])
print('== min pad-to-pad gap by footprint (<0.6 mm) = mask sliver at 1:1 mask (board expansion 0):')
for k, v in sorted(byfp.items(), key=lambda x: x[1])[:14]: print(f'   {k:22s} gap {v:.4f}')
print('   tightest different-net pad pairs:', [g for g in gaps if g[2] != g[4]][:6])
print('   pairs under 0.10 (JLC mask bridge):', [g for g in gaps if g[0] < 0.10])
print('   pairs under 0.20:', len([g for g in gaps if g[0] < 0.20]), '| different-net under 0.20:', len([g for g in gaps if g[0] < 0.20 and g[2] != g[4]]))
# J7 USB-C geometry
if 'J7' in fps:
    j7 = fps['J7']; print('== J7', j7.GetFPIDAsString(), 'at', (round(mm(j7.GetPosition().x), 3), round(mm(j7.GetPosition().y), 3)), 'rot', j7.GetOrientationDegrees())
    for p in j7.Pads():
        ds_ = p.GetDrillSize(); sz = p.GetSize(FCU) if p.IsOnLayer(FCU) else p.GetSize(BCU)
        print(f'   pad {p.GetNumber():8s} attr {p.GetAttribute()} net {p.GetNetname()[:28]:28s} at ({mm(p.GetPosition().x):.3f},{mm(p.GetPosition().y):.3f}) size {mm(sz.x):.3f}x{mm(sz.y):.3f} drill {mm(ds_.x):.3f}x{mm(ds_.y):.3f} mask {p.IsOnLayer(pcbnew.F_Mask)} paste {p.IsOnLayer(pcbnew.F_Paste)} tracks {len(c.GetConnectedTracks(p))} localmaskmargin {p.GetLocalSolderMaskMargin()}')
    print('   J7 pad gaps:', [g for g in gaps if g[1].startswith('J7.') and g[3].startswith('J7.')][:8])
# starved thermal candidates: GND pads with exactly one spoke -> list GND pads touching fill with 0 tracks and count of spokes unknown; print the two DRC-flagged
for n, p in gpads:
    if n in ('J7.A1/B12', 'J7.B1/A12'):
        print(f'   {n} connected tracks {len(c.GetConnectedTracks(p))} connected pads {[q.GetParentFootprint().GetReference()+"."+q.GetNumber() for q in c.GetConnectedPads(p)]}')
print('== rule-area keepouts inside jacks (fill/vias/tracks forbidden):', sorted(set(z.GetParentFootprint().GetReference() for fp in b.GetFootprints() for z in fp.Zones())))
