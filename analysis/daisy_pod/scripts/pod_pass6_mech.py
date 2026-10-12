#!/usr/bin/env python3
"""Daisy Pod Rev5 (KiCad conversion) — Pass 6 mechanical / assembly extraction. Read-only.
Silk/text DRC decomposition (as-is and JLC runs), text inventory, courtyards, paste vs BOM, holes/mounting,
outline + cutouts, edge-mounted parts, controls geometry.
Run: python3 pod_pass6_mech.py [board.kicad_pcb] [drc_asis.json] [drc_jlc.json] [bom.txt]"""
import pcbnew, collections, json, re, sys, math
A = sys.argv
B = A[1] if len(A) > 1 else '/home/user/PCB_Analysis-Isolated_Screen/reference/electrosmith/daisy_pod/kicad/ES_Daisy_Pod_Rev5.kicad_pcb'
DRC = A[2] if len(A) > 2 else '/home/user/PCB_Analysis-Isolated_Screen/kicad_out/pod/drc_asis.json'
DRCJ = A[3] if len(A) > 3 else '/home/user/PCB_Analysis-Isolated_Screen/kicad_out/pod/drc_jlc_nc01.json'
BOM = A[4] if len(A) > 4 else '/home/user/PCB_Analysis-Isolated_Screen/kicad_out/pod/bom.txt'
b = pcbnew.LoadBoard(B); mm = pcbnew.ToMM
FCU, BCU = pcbnew.F_Cu, pcbnew.B_Cu
fps = {fp.GetReference(): fp for fp in b.GetFootprints()}
def side(fp): return 'B' if fp.IsFlipped() else 'F'
def bbmm(bb): return tuple(round(mm(v), 2) for v in (bb.GetLeft(), bb.GetTop(), bb.GetRight(), bb.GetBottom()))

# ---------- A. DRC silk/text decomposition
def decomp(path, label):
    d = json.load(open(path))
    print(f'=== A. {label}: {path.split("/")[-1]} —', dict(collections.Counter(v["type"] for v in d["violations"])), 'unconnected', len(d['unconnected_items']))
    for typ in ('text_height', 'text_thickness', 'silk_over_copper', 'silk_edge_clearance', 'silk_overlap', 'missing_courtyard', 'courtyards_overlap'):
        vs = [v for v in d['violations'] if v['type'] == typ]
        if not vs: continue
        refs = collections.Counter(); act = collections.Counter(); kinds = collections.Counter()
        for v in vs:
            m = re.search(r'actual ([\d.]+)', v['description'])
            if m: act[m.group(1)] += 1
            for i in v['items']:
                dsc = i['description']
                m = re.search(r' of (\S+)', dsc)
                refs[m.group(1) if m else ('board-text' if 'PCB text' in dsc else dsc[:25])] += 1
            kinds[tuple(sorted(re.sub(r"'[^']*'|\[.*?\]|\(.*?\)", '', i['description']).split(' on ')[0].strip()[:30] for i in v['items']))] += 1
        print(f'  {typ}: {len(vs)} | by ref: {sorted(refs.items(), key=lambda x: -x[1])}')
        if act: print('     actual values (mm):', sorted(act.items()))
        print('     item kinds:', kinds.most_common(6))
decomp(DRC, 'project-default rules')
decomp(DRCJ, 'JLC rules, netclass 0.1, all severities')

# ---------- B. text inventory (what will plot on silk)
print('=== B. text inventory')
rows = []
for fp in b.GetFootprints():
    for f in fp.GetFields():
        rows.append((fp.GetReference(), f.GetLayerName(), 'FIELD ' + f.GetName(), f.GetText()[:20], round(mm(f.GetTextHeight()), 3), round(mm(f.GetTextThickness()), 3), f.IsVisible()))
    for t in fp.GraphicalItems():
        if t.GetClass() == 'PCB_TEXT': rows.append((fp.GetReference(), t.GetLayerName(), 'TEXT', t.GetText()[:20], round(mm(t.GetTextHeight()), 3), round(mm(t.GetTextThickness()), 3), t.IsVisible()))
for d in b.GetDrawings():
    if d.GetClass() == 'PCB_TEXT': rows.append(('BOARD', d.GetLayerName(), 'TEXT', d.GetText()[:24], round(mm(d.GetTextHeight()), 3), round(mm(d.GetTextThickness()), 3), True))
silk = [r for r in rows if r[6] and 'Silk' in r[1]]
print('  visible silk texts:', len(silk), '| height<1.0:', sum(1 for r in silk if r[4] < 1.0), '| thickness<0.15:', sum(1 for r in silk if r[5] < 0.15), '| both OK:', sum(1 for r in silk if r[4] >= 1.0 and r[5] >= 0.15))
print('  height/thickness histogram of visible silk texts:', sorted(collections.Counter((r[4], r[5])) for r in [silk])[0].items() if False else sorted(collections.Counter((r[4], r[5]) for r in silk).items()))
print('  refdes visible on silk:', sum(1 for r in silk if r[2] == 'FIELD Reference'), 'hidden refdes:', [r[0] for r in rows if r[2] == 'FIELD Reference' and not r[6]])
print('  refdes height range:', min(r[4] for r in silk if r[2] == 'FIELD Reference'), '-', max(r[4] for r in silk if r[2] == 'FIELD Reference'))
print('  board-level silk texts:', [(r[1], r[3], r[4], r[5]) for r in silk if r[0] == 'BOARD'])
print('  footprint graphic texts on silk:', [(r[0], r[3], r[4], r[5]) for r in silk if r[2] == 'TEXT' and r[0] != 'BOARD'])
# silk stroke widths
fw = collections.Counter(); bw = collections.Counter()
for fp in b.GetFootprints():
    for g in fp.GraphicalItems():
        if 'Silk' in g.GetLayerName() and g.GetClass() == 'PCB_SHAPE': fw[round(mm(g.GetWidth()), 3)] += 1
for d in b.GetDrawings():
    if 'Silk' in d.GetLayerName() and d.GetClass() == 'PCB_SHAPE': bw[round(mm(d.GetWidth()), 3)] += 1
print('  footprint silk stroke widths:', sorted(fw.items()), '| board silk shapes:', sorted(bw.items()))

# ---------- C. courtyards
print('=== C. courtyards')
cy = {}; miss = []
for ref, fp in fps.items():
    L = pcbnew.B_CrtYd if side(fp) == 'B' else pcbnew.F_CrtYd
    c = fp.GetCourtyard(L)
    if c.OutlineCount() == 0: miss.append(ref)
    else: cy[ref] = (side(fp), c)
ov = []
refs = sorted(cy)
for i in range(len(refs)):
    for j in range(i + 1, len(refs)):
        a, c = cy[refs[i]], cy[refs[j]]
        if a[0] == c[0] and a[1].BBox().Intersects(c[1].BBox()) and a[1].Collide(c[1], 0): ov.append((refs[i], refs[j]))
print('  with courtyard (from Eagle tKeepout/bKeepout):', len(cy), '| missing:', len(miss), sorted(miss), '| overlaps among those present:', ov)

# ---------- D. paste vs BOM
print('=== D. paste vs BOM')
bom = {}
for line in open(BOM, encoding='utf-8', errors='replace'):
    parts = [x.strip() for x in line.split('|')]
    if len(parts) < 5 or parts[0] == 'Qty': continue
    for r_ in parts[4].split(): bom[r_] = (parts[1], parts[2])
paste = collections.defaultdict(lambda: [0, 0])
for fp in b.GetFootprints():
    for p in fp.Pads():
        if p.IsOnLayer(pcbnew.F_Paste): paste[fp.GetReference()][0] += 1
        if p.IsOnLayer(pcbnew.B_Paste): paste[fp.GetReference()][1] += 1
print('  BOM designators:', len(bom), '| F.Paste apertures', sum(v[0] for v in paste.values()), 'on', sum(1 for v in paste.values() if v[0]), 'footprints | B.Paste', sum(v[1] for v in paste.values()), 'on', sum(1 for v in paste.values() if v[1]), 'footprints')
print('  paste but NOT in BOM:', [(r_, side(fps[r_]), paste[r_], fps[r_].GetValue()[:24]) for r_ in sorted(paste) if r_ not in bom])
print('  in BOM but no paste:', [(r_, fps[r_].GetValue()[:24]) for r_ in sorted(bom) if r_ in fps and r_ not in paste])
print('  BOM refs with no footprint:', [r_ for r_ in bom if r_ not in fps])
print('  no paste and not in BOM (expected: fiducials, holes, logos, DNI):', [(r_, fps[r_].GetValue()[:22]) for r_ in sorted(fps) if r_ not in paste and r_ not in bom])
print('  side split:', collections.Counter(side(fp) for fp in b.GetFootprints()), '| F-side:', sorted(r_ for r_, fp in fps.items() if side(fp) == 'F'))
print('  pads with mask but no paste on SMD footprints (hand/no-paste pads):', [(fp.GetReference(), p.GetNumber()) for fp in b.GetFootprints() for p in fp.Pads() if p.GetAttribute() == 1 and not (p.IsOnLayer(pcbnew.F_Paste) or p.IsOnLayer(pcbnew.B_Paste))])
print('  U4 pads (paste layer, size):', [(p.GetNumber(), p.IsOnLayer(pcbnew.B_Paste), round(mm(p.GetSize(BCU).x), 2), round(mm(p.GetSize(BCU).y), 2)) for p in fps['U4'].Pads()])
print('  Eagle MPN attribute vs BOM MPN for LED1/LED2: Eagle .brd attribute MPN=CLVBA-FKA-CC1F1L1BB7R3R3 (see pod_eagle_brd.py); BOM:', bom.get('LED1'))

# ---------- E. holes / mounting
print('=== E. holes')
npth = collections.Counter(); pth_nonet = collections.Counter(); pth_net = collections.Counter()
for fp in b.GetFootprints():
    for p in fp.Pads():
        ds = p.GetDrillSize()
        if ds.x == 0: continue
        k = (fp.GetReference(), round(mm(ds.x), 3), round(mm(ds.y), 3))
        if p.GetAttribute() == 3: npth[k] += 1
        elif p.GetNetname() == '': pth_nonet[(k, round(mm(p.GetSize(FCU).x), 3))] += 1
        else: pth_net[k] += 1
print('  NPTH:', sorted(npth.items())); print('  PTH no net (ref, drill, pad):', sorted(pth_nonet.items())); print('  PTH with net:', sorted(pth_net.items()))
for h in ('H1', 'H2', 'H3', 'H4'):
    fp = fps[h]; p = list(fp.Pads())[0]; pos = p.GetPosition()
    print(f'  {h}: ({mm(pos.x):.3f},{mm(pos.y):.3f}) drill {mm(p.GetDrillSize().x)} pad {mm(p.GetSize(FCU).x)} net "{p.GetNetname()}" attr {p.GetAttribute()} footprint {fp.GetFPIDAsString()}')
H = {h: list(fps[h].Pads())[0].GetPosition() for h in ('H1', 'H2', 'H3', 'H4')}
print('  hole pattern (mm): H1-H2', round(mm(H['H2'].y - H['H1'].y), 3), 'H3-H4', round(mm(H['H4'].y - H['H3'].y), 3), 'H1-H3 dx', round(mm(H['H3'].x - H['H1'].x), 3), 'H2-H4 dx', round(mm(H['H4'].x - H['H2'].x), 3),
      '| edge distances: H1 left', round(mm(H['H1'].x), 3), 'H2 left/bottom', round(mm(H['H2'].x), 3), round(50 - mm(H['H2'].y), 3), 'H3 top/right', round(mm(H['H3'].y), 3), round(90 - mm(H['H3'].x), 3), 'H4 bottom/right', round(50 - mm(H['H4'].y), 3), round(90 - mm(H['H4'].x), 3))

# ---------- F. outline
print('=== F. outline')
ec = [(d.GetClass(), d.ShowShape(), [round(mm(v), 3) for v in (d.GetStart().x, d.GetStart().y, d.GetEnd().x, d.GetEnd().y)]) for d in b.GetDrawings() if d.GetLayerName() == 'Edge.Cuts']
print('  board-level Edge.Cuts:', ec)
fec = collections.Counter(fp.GetReference() for fp in b.GetFootprints() for g in fp.GraphicalItems() if g.GetLayerName() == 'Edge.Cuts')
print('  footprint Edge.Cuts items (Eagle Dimension layer in packages):', dict(fec))
outline = pcbnew.SHAPE_POLY_SET(); b.GetBoardPolygonOutlines(outline); obb = b.GetBoardEdgesBoundingBox()
o = outline.Outline(0)
print('  outline polygons', outline.OutlineCount(), 'area', round(o.Area() / 1e12, 1), 'bbox', bbmm(obb), 'size', round(mm(obb.GetWidth()), 3), 'x', round(mm(obb.GetHeight()), 3))
print('  outer vertices:', [(round(mm(o.CPoint(k).x), 3), round(mm(o.CPoint(k).y), 3)) for k in range(o.PointCount())])
for h in range(outline.HoleCount(0)):
    hh = outline.Hole(0, h); pts = [(mm(hh.CPoint(k).x), mm(hh.CPoint(k).y)) for k in range(hh.PointCount())]
    print(f'  cutout {h}: {hh.PointCount()} verts, bbox x {min(p[0] for p in pts):.3f}..{max(p[0] for p in pts):.3f} y {min(p[1] for p in pts):.3f}..{max(p[1] for p in pts):.3f}, size {max(p[0] for p in pts)-min(p[0] for p in pts):.3f} x {max(p[1] for p in pts)-min(p[1] for p in pts):.3f}, area {hh.Area()/1e12:.2f}')

# ---------- G. parts at / beyond the edge, controls
print('=== G. edge-mounted parts and controls')
for ref in ('P1', 'P5', 'J1', 'J2', 'J3', 'J4', 'P8', 'ENC_1', 'VR_1', 'VR_2', 'S2', 'S3', 'LED1', 'LED2', 'U1', 'P2', 'C62', 'C63'):
    fp = fps[ref]; bb = fp.GetBoundingBox(False, False); pos = fp.GetPosition()
    beyond = []
    if mm(bb.GetLeft()) < 0: beyond.append(f'left by {-mm(bb.GetLeft()):.2f}')
    if mm(bb.GetRight()) > 90: beyond.append(f'right by {mm(bb.GetRight())-90:.2f}')
    if mm(bb.GetTop()) < 0: beyond.append(f'top by {-mm(bb.GetTop()):.2f}')
    if mm(bb.GetBottom()) > 50: beyond.append(f'bottom by {mm(bb.GetBottom())-50:.2f}')
    pads_ = list(fp.Pads())
    pth = [(p.GetNumber(), round(mm(p.GetDrillSize().x), 2), round(mm(p.GetSize(FCU).x), 2), round(mm(p.GetSize(FCU).y), 2)) for p in pads_ if p.GetDrillSize().x > 0]
    print(f'  {ref:6s} {side(fp)} ({mm(pos.x):.2f},{mm(pos.y):.2f}) rot {fp.GetOrientationDegrees():.0f} {fp.GetFPIDAsString()[:40]} bbox {bbmm(bb)} beyond edge: {beyond or "no"} | pads {len(pads_)} holes {pth[:5]}')
# jack pitch, pot pitch
J = [mm(fps[j].GetPosition().y) for j in ('J1', 'J2', 'J3', 'J4')]
print('  jack centre pitch (mm):', [round(J[i + 1] - J[i], 3) for i in range(3)], '| pot centres', [(round(mm(fps[v].GetPosition().x), 2), round(mm(fps[v].GetPosition().y), 2)) for v in ('VR_1', 'VR_2')], 'pitch', round(mm(fps['VR_2'].GetPosition().x - fps['VR_1'].GetPosition().x), 2),
      '| LED pitch', round(mm(fps['LED2'].GetPosition().x - fps['LED1'].GetPosition().x), 2), '| switch pitch', round(mm(fps['S2'].GetPosition().x - fps['S3'].GetPosition().x), 2))
# Seed socket U1 pin rows
u1 = sorted(fps['U1'].Pads(), key=lambda p: int(p.GetNumber()))
print('  U1 Seed socket: pin1', (round(mm(u1[0].GetPosition().x), 3), round(mm(u1[0].GetPosition().y), 3)), 'pin20', (round(mm(u1[19].GetPosition().x), 3), round(mm(u1[19].GetPosition().y), 3)), 'pin21', (round(mm(u1[20].GetPosition().x), 3), round(mm(u1[20].GetPosition().y), 3)), 'pin40', (round(mm(u1[39].GetPosition().x), 3), round(mm(u1[39].GetPosition().y), 3)),
      'row spacing', round(mm(abs(u1[20].GetPosition().y - u1[0].GetPosition().y)), 3), 'pad', round(mm(u1[0].GetSize(FCU).x), 3), 'x', round(mm(u1[0].GetSize(FCU).y), 3))
print('  footprint attribute flags (exclude BOM/pos/board-only):', [(r_, fp.GetAttributes()) for r_, fp in fps.items() if fp.GetAttributes() & (pcbnew.FP_EXCLUDE_FROM_BOM | pcbnew.FP_EXCLUDE_FROM_POS_FILES | pcbnew.FP_BOARD_ONLY)])
