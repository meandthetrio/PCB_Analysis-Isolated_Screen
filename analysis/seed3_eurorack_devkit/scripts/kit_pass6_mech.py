#!/usr/bin/env python3
"""Seed 3 dev kits (Eurorack / Pedal Rev3) — Pass 6 mechanical / assembly extraction. Read-only (pcbnew, KiCad 9/10).
Silk/text DRC decomposition (as-is all-severity and JLC runs), text inventory, courtyards (+ overlapping pairs),
paste vs BOM (Electrosmith master CSV with DNP column and/or KiCad production CSV), holes / mounting pattern,
outline, parts beyond the edge, control pitches, Seed socket geometry, footprint attribute flags.
usage: kit_pass6_mech.py <board.kicad_pcb> <drc_asis.json> <drc_jlc.json> <bom.csv> [bom2.csv]"""
import pcbnew, collections, json, re, sys, math, csv
A = sys.argv; B, DRC, DRCJ = A[1], A[2], A[3]; BOMS = A[4:]
b = pcbnew.LoadBoard(B); mm = pcbnew.ToMM
FCU, BCU = pcbnew.F_Cu, pcbnew.B_Cu
fps = {fp.GetReference(): fp for fp in b.GetFootprints()}
def side(fp): return 'B' if fp.IsFlipped() else 'F'
def bbmm(bb): return tuple(round(mm(v), 2) for v in (bb.GetLeft(), bb.GetTop(), bb.GetRight(), bb.GetBottom()))
ob = b.GetBoardEdgesBoundingBox(); OL, OT, OR, OB = [mm(v) for v in (ob.GetLeft(), ob.GetTop(), ob.GetRight(), ob.GetBottom())]

# ---------- A. DRC silk/text decomposition
def decomp(path, label):
    d = json.load(open(path))
    print(f'=== A. {label}: {path.split("/")[-1]} —', dict(collections.Counter(v["type"] for v in d["violations"])), 'unconnected', len(d['unconnected_items']))
    for typ in ('text_height', 'text_thickness', 'silk_over_copper', 'silk_edge_clearance', 'silk_overlap', 'missing_courtyard', 'courtyards_overlap'):
        vs = [v for v in d['violations'] if v['type'] == typ]
        if not vs: continue
        refs = collections.Counter(); act = collections.Counter(); kinds = collections.Counter(); pairs = collections.Counter()
        for v in vs:
            m = re.search(r'actual ([\d.]+)', v['description'])
            if m: act[m.group(1)] += 1
            names = []
            for i in v['items']:
                dsc = i['description']
                m = re.search(r' of (\S+)', dsc) or re.search(r"Footprint (\S+)", dsc)
                nm = m.group(1) if m else ('board-text' if 'PCB text' in dsc or dsc.startswith('Text') else dsc.split(' on ')[0][:25])
                refs[nm] += 1; names.append(nm)
            pairs[tuple(sorted(set(names)))] += 1
            kinds[tuple(sorted(re.sub(r"'[^']*'|\[.*?\]|\(.*?\)", '', i['description']).split(' on ')[0].strip()[:28] for i in v['items']))] += 1
        print(f'  {typ}: {len(vs)} | by ref: {sorted(refs.items(), key=lambda x: -x[1])[:30]}')
        if act: print('     actual values (mm):', sorted(act.items())[:20])
        print('     item kinds:', kinds.most_common(5))
        if typ in ('silk_overlap', 'courtyards_overlap', 'silk_over_copper'): print('     pairs:', pairs.most_common(40))
decomp(DRC, 'project rules, all severities')
decomp(DRCJ, 'JLC rules (silk 0.15, text 1.0/0.15), netclass 0.1, all severities')

# ---------- B. text inventory
print('=== B. text inventory')
rows = []
for fp in b.GetFootprints():
    for f in fp.GetFields():
        rows.append((fp.GetReference(), f.GetLayerName(), 'FIELD ' + f.GetName(), f.GetText()[:22], round(mm(f.GetTextHeight()), 3), round(mm(f.GetTextThickness()), 3), f.IsVisible()))
    for t in fp.GraphicalItems():
        if t.GetClass() == 'PCB_TEXT': rows.append((fp.GetReference(), t.GetLayerName(), 'TEXT', t.GetText()[:22], round(mm(t.GetTextHeight()), 3), round(mm(t.GetTextThickness()), 3), t.IsVisible()))
for d in b.GetDrawings():
    if d.GetClass() == 'PCB_TEXT': rows.append(('BOARD', d.GetLayerName(), 'TEXT', d.GetText()[:30].replace('\n', '/'), round(mm(d.GetTextHeight()), 3), round(mm(d.GetTextThickness()), 3), True))
    if d.GetClass() == 'PCB_TEXTBOX': rows.append(('BOARD', d.GetLayerName(), 'TEXTBOX', d.GetText()[:30].replace('\n', '/'), round(mm(d.GetTextHeight()), 3), round(mm(d.GetTextThickness()), 3), True))
silk = [r for r in rows if r[6] and 'Silk' in r[1]]
print('  visible silk texts:', len(silk), '| height<1.0:', sum(1 for r in silk if r[4] < 1.0), '| thickness<0.15:', sum(1 for r in silk if r[5] < 0.15), '| both OK:', sum(1 for r in silk if r[4] >= 1.0 and r[5] >= 0.15), '| height<0.8 or thk<0.08 (project rule):', sum(1 for r in silk if r[4] < 0.8 or r[5] < 0.08))
print('  (height, thickness) histogram:', sorted(collections.Counter((r[4], r[5]) for r in silk).items()))
print('  refdes visible on silk:', sum(1 for r in silk if r[2] == 'FIELD Reference'), '| refdes hidden or not on silk:', sorted(r[0] for r in rows if r[2] == 'FIELD Reference' and not (r[6] and 'Silk' in r[1])))
print('  refdes (h,thk) histogram:', sorted(collections.Counter((r[4], r[5]) for r in silk if r[2] == 'FIELD Reference').items()))
print('  board-level silk texts:', [(r[1], r[3], r[4], r[5]) for r in silk if r[0] == 'BOARD'])
print('  footprint graphic texts on silk:', [(r[0], r[3], r[4], r[5]) for r in silk if r[2] == 'TEXT' and r[0] != 'BOARD'])
print('  silk texts under JLC 1.0/0.15:', [(r[0], r[3], r[4], r[5]) for r in silk if r[4] < 1.0 or r[5] < 0.15][:40])
fw = collections.Counter(); bw = collections.Counter(); bk = collections.Counter()
for fp in b.GetFootprints():
    for g in fp.GraphicalItems():
        if 'Silk' in g.GetLayerName() and g.GetClass() == 'PCB_SHAPE': fw[round(mm(g.GetWidth()), 3)] += 1
for d in b.GetDrawings():
    if 'Silk' in d.GetLayerName() and d.GetClass() == 'PCB_SHAPE': bw[round(mm(d.GetWidth()), 3)] += 1; bk[(d.GetLayerName(), d.ShowShape())] += 1
print('  footprint silk stroke widths:', sorted(fw.items()), '| board silk shapes widths:', sorted(bw.items()), 'kinds', dict(bk))

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
print('  with courtyard:', len(cy), '| missing:', len(miss), sorted(miss), '| overlapping pairs:', ov)
for r1, r2 in ov:
    print(f'    {r1} {fps[r1].GetFPIDAsString()} crtyd {bbmm(cy[r1][1].BBox())} <-> {r2} {fps[r2].GetFPIDAsString()} crtyd {bbmm(cy[r2][1].BBox())}')

# ---------- D. paste vs BOM
print('=== D. paste vs BOM')
def load_bom(path):
    out = {}; dnp = set(); meta = {}
    with open(path, encoding='utf-8-sig', errors='replace') as fh:
        rd = csv.DictReader(fh)
        for row in rd:
            k = 'Designators' if 'Designators' in row else 'Reference'
            refs_ = re.split(r'[ ,]+', (row.get(k) or '').strip())
            for r_ in refs_:
                if not r_: continue
                out[r_] = (row.get('Value', ''), row.get('MPN', row.get('AVL_Part_Number', row.get('Footprint', ''))), row.get('Assembly', ''))
                if str(row.get('DNP', '')).strip().upper() in ('TRUE', 'YES', '1', 'DNP'): dnp.add(r_)
        meta['columns'] = rd.fieldnames
    return out, dnp, meta
boms = []
for p in BOMS:
    bom, dnp, meta = load_bom(p); boms.append((p.split('/')[-1], bom, dnp))
    print(f'  BOM {p.split("/")[-1]}: {len(bom)} designators, columns {meta["columns"]}, DNP flagged: {sorted(dnp)}')
paste = collections.defaultdict(lambda: [0, 0])
for fp in b.GetFootprints():
    for p in fp.Pads():
        if p.IsOnLayer(pcbnew.F_Paste): paste[fp.GetReference()][0] += 1
        if p.IsOnLayer(pcbnew.B_Paste): paste[fp.GetReference()][1] += 1
print('  F.Paste apertures', sum(v[0] for v in paste.values()), 'on', sum(1 for v in paste.values() if v[0]), 'footprints | B.Paste', sum(v[1] for v in paste.values()), 'on', sum(1 for v in paste.values() if v[1]))
FL = {'excl_bom': pcbnew.FP_EXCLUDE_FROM_BOM, 'excl_pos': pcbnew.FP_EXCLUDE_FROM_POS_FILES, 'board_only': pcbnew.FP_BOARD_ONLY}
DNPF = getattr(pcbnew, 'FP_DNP', 0)
def flags(fp):
    a = fp.GetAttributes(); s = [k for k, v in FL.items() if a & v]
    if DNPF and a & DNPF: s.append('DNP')
    return ','.join(s)
for name, bom, dnp in boms:
    print(f'  -- vs {name}')
    print('     paste but NOT in BOM:', [(r_, paste[r_], fps[r_].GetValue()[:20], flags(fps[r_])) for r_ in sorted(paste) if r_ not in bom])
    print('     in BOM but no paste (THT / hand):', sorted((r_, fps[r_].GetValue()[:16]) for r_ in bom if r_ in fps and r_ not in paste))
    print('     BOM refs with no footprint:', sorted(r_ for r_ in bom if r_ not in fps))
    print('     footprints neither pasted nor in BOM:', sorted((r_, fps[r_].GetValue()[:16], flags(fps[r_])) for r_ in fps if r_ not in paste and r_ not in bom))
    print('     DNP in BOM but footprint has paste:', sorted(r_ for r_ in dnp if r_ in paste), '| DNP flags on footprints:', sorted(r_ for r_ in fps if 'DNP' in flags(fps[r_])))
if len(boms) == 2:
    a, b2 = boms[0][1], boms[1][1]
    print('  BOM-vs-BOM: only in first', sorted(set(a) - set(b2)), '| only in second', sorted(set(b2) - set(a)))
    diffv = [(r_, a[r_][0], b2[r_][0]) for r_ in a if r_ in b2 and a[r_][0].strip().upper() != b2[r_][0].strip().upper()]
    print('  value mismatches between BOMs:', diffv[:20])
print('  value mismatches board vs first BOM:', [(r_, fps[r_].GetValue()[:16], boms[0][1][r_][0][:16]) for r_ in boms[0][1] if r_ in fps and boms[0][1][r_][0].strip().upper() != fps[r_].GetValue().strip().upper()][:30])
print('  SMD pads with mask but no paste:', [(fp.GetReference(), p.GetNumber()) for fp in b.GetFootprints() for p in fp.Pads() if p.GetAttribute() == 1 and not (p.IsOnLayer(pcbnew.F_Paste) or p.IsOnLayer(pcbnew.B_Paste))])
print('  side split:', collections.Counter(side(fp) for fp in b.GetFootprints()), '| B-side parts:', sorted(r_ for r_, fp in fps.items() if side(fp) == 'B'))
print('  footprint attribute flags:', [(r_, flags(fp)) for r_, fp in fps.items() if flags(fp)])

# ---------- E. holes / mounting
print('=== E. holes')
npth = collections.Counter(); pth_nonet = collections.Counter(); pth_net = collections.Counter()
for fp in b.GetFootprints():
    for p in fp.Pads():
        ds = p.GetDrillSize()
        if ds.x == 0: continue
        k = (fp.GetReference(), round(mm(ds.x), 3), round(mm(ds.y), 3))
        if p.GetAttribute() == 3: npth[k] += 1
        elif p.GetNetname() == '': pth_nonet[(k, round(mm(p.GetSize(FCU).x), 3), round(mm(p.GetSize(FCU).y), 3))] += 1
        else: pth_net[k[1:]] += 1
print('  NPTH:', sorted(npth.items())); print('  PTH no net (ref, drill, pad):', sorted(pth_nonet.items())); print('  PTH with net by drill:', sorted(pth_net.items()))
H = {}
for h in ('H1', 'H2', 'H3', 'H4'):
    if h not in fps: continue
    fp = fps[h]; p = list(fp.Pads())[0]; pos = p.GetPosition(); H[h] = (mm(pos.x), mm(pos.y))
    print(f'  {h}: ({mm(pos.x):.3f},{mm(pos.y):.3f}) drill {mm(p.GetDrillSize().x)}x{mm(p.GetDrillSize().y)} pad {mm(p.GetSize(FCU).x)}x{mm(p.GetSize(FCU).y)} net "{p.GetNetname()}" attr {p.GetAttribute()} {fp.GetFPIDAsString()} edge L/T/R/B {mm(pos.x)-OL:.3f}/{mm(pos.y)-OT:.3f}/{OR-mm(pos.x):.3f}/{OB-mm(pos.y):.3f}')
if len(H) == 4:
    print('  hole pattern: dx(H1-H3)', round(H['H3'][0] - H['H1'][0], 3), 'dx(H2-H4)', round(H['H4'][0] - H['H2'][0], 3), 'dy(H1-H2)', round(H['H2'][1] - H['H1'][1], 3), 'dy(H3-H4)', round(H['H4'][1] - H['H3'][1], 3))
    vias = [t for t in b.GetTracks() if t.GetClass() == 'PCB_VIA']
    for h, (x, y) in H.items():
        dv = min(math.hypot(mm(v.GetPosition().x) - x, mm(v.GetPosition().y) - y) for v in vias)
        dp = min((math.hypot(mm(fp.GetPosition().x) - x, mm(fp.GetPosition().y) - y), fp.GetReference()) for fp in b.GetFootprints() if fp.GetReference() != h)
        print(f'    {h}: nearest via {dv:.2f} mm, nearest footprint {dp[1]} {dp[0]:.2f} mm')

# ---------- F. outline
print('=== F. outline')
ec = collections.Counter((d.ShowShape(), round(mm(d.GetWidth()), 3)) for d in b.GetDrawings() if d.GetLayerName() == 'Edge.Cuts')
arcs = [d for d in b.GetDrawings() if d.GetLayerName() == 'Edge.Cuts' and d.ShowShape() == 'Arc']
print('  board-level Edge.Cuts:', dict(ec), '| arc radii:', sorted(set(round(mm(a.GetRadius()), 3) for a in arcs)))
fec = collections.Counter(fp.GetReference() for fp in b.GetFootprints() for g in fp.GraphicalItems() if g.GetLayerName() == 'Edge.Cuts')
print('  footprint Edge.Cuts items:', dict(fec))
outline = pcbnew.SHAPE_POLY_SET()
try: b.GetBoardPolygonOutlines(outline, False)
except TypeError: b.GetBoardPolygonOutlines(outline)
o = outline.Outline(0)
print('  outline polygons', outline.OutlineCount(), 'area', round(o.Area() / 1e12, 1), 'bbox', (round(OL, 3), round(OT, 3), round(OR, 3), round(OB, 3)), 'size', round(OR - OL, 3), 'x', round(OB - OT, 3), 'cutouts', outline.HoleCount(0), 'thickness', mm(b.GetDesignSettings().GetBoardThickness()))

# ---------- G. parts at / beyond the edge, controls
print('=== G. edge-mounted parts and controls')
for ref, fp in sorted(fps.items(), key=lambda kv: kv[1].GetFPIDAsString()):
    bb = fp.GetBoundingBox(False, False); pos = fp.GetPosition()
    beyond = []
    if mm(bb.GetLeft()) < OL - 0.01: beyond.append(f'left by {OL-mm(bb.GetLeft()):.2f}')
    if mm(bb.GetRight()) > OR + 0.01: beyond.append(f'right by {mm(bb.GetRight())-OR:.2f}')
    if mm(bb.GetTop()) < OT - 0.01: beyond.append(f'top by {OT-mm(bb.GetTop()):.2f}')
    if mm(bb.GetBottom()) > OB + 0.01: beyond.append(f'bottom by {mm(bb.GetBottom())-OB:.2f}')
    pads_ = list(fp.Pads())
    nth = sum(1 for p in pads_ if p.GetAttribute() == 0)
    if beyond or nth or fp.GetFPIDAsString().split(':')[0] in ('USB4110GFA', 'TF-01A', 'Module'):
        pth = sorted(set((round(mm(p.GetDrillSize().x), 2), round(mm(p.GetDrillSize().y), 2), round(mm(p.GetSize(FCU).x), 2), round(mm(p.GetSize(FCU).y), 2)) for p in pads_ if p.GetDrillSize().x > 0))
        print(f'  {ref:14s} {side(fp)} ({mm(pos.x):7.2f},{mm(pos.y):7.2f}) rot {fp.GetOrientationDegrees():5.0f} {fp.GetFPIDAsString()[:46]:46s} bbox {bbmm(bb)} beyond: {", ".join(beyond) or "no"} | pads {len(pads_)} holes(drill,pad) {pth[:4]}')
# groups by footprint id -> pitch analysis
grp = collections.defaultdict(list)
for ref, fp in fps.items(): grp[fp.GetFPIDAsString()].append((round(mm(fp.GetPosition().x), 3), round(mm(fp.GetPosition().y), 3), ref))
for k, v in grp.items():
    if len(v) >= 2 and not k.startswith(('Resistor', 'Capacitor', 'Package', 'Diode', 'Fiducial')):
        xs = sorted(set(p[0] for p in v)); ys = sorted(set(p[1] for p in v))
        print(f'  group {k[:40]} n={len(v)}: x positions {xs} (pitches {[round(xs[i+1]-xs[i],2) for i in range(len(xs)-1)]}) | y positions {ys} (pitches {[round(ys[i+1]-ys[i],2) for i in range(len(ys)-1)]})')
if 'A1' in fps:
    u = sorted(fps['A1'].Pads(), key=lambda p: int(re.sub(r'\D', '', p.GetNumber()) or 0))
    print('  A1 Seed socket:', fps['A1'].GetFPIDAsString(), 'pads', len(u), 'pin1', (round(mm(u[0].GetPosition().x), 3), round(mm(u[0].GetPosition().y), 3)), 'pin20', (round(mm(u[19].GetPosition().x), 3), round(mm(u[19].GetPosition().y), 3)), 'pin21', (round(mm(u[20].GetPosition().x), 3), round(mm(u[20].GetPosition().y), 3)), 'pin40', (round(mm(u[39].GetPosition().x), 3), round(mm(u[39].GetPosition().y), 3)),
          'row spacing', round(mm(abs(u[20].GetPosition().x - u[0].GetPosition().x)), 3), 'pitch', round(mm(abs(u[1].GetPosition().y - u[0].GetPosition().y)), 3), 'pad', round(mm(u[0].GetSize(FCU).x), 3), 'x', round(mm(u[0].GetSize(FCU).y), 3), 'drill', round(mm(u[0].GetDrillSize().x), 3), 'attr', u[0].GetAttribute(), 'courtyard', bbmm(fps['A1'].GetCourtyard(pcbnew.F_CrtYd).BBox()) if fps['A1'].GetCourtyard(pcbnew.F_CrtYd).OutlineCount() else None, 'fab bbox', bbmm(fps['A1'].GetBoundingBox(False, False)))
    # parts whose centre lies inside A1's courtyard
    c = fps['A1'].GetCourtyard(pcbnew.F_CrtYd)
    inside = [r_ for r_, fp in fps.items() if r_ != 'A1' and c.OutlineCount() and c.Contains(fp.GetPosition())]
    print('  parts with centre inside A1 courtyard:', inside)
# tallest / big parts list
big = [(r_, fp.GetFPIDAsString().split(':')[-1][:26], (round(mm(fp.GetPosition().x), 1), round(mm(fp.GetPosition().y), 1))) for r_, fp in fps.items() if 'CP_Elec' in fp.GetFPIDAsString() or 'DIP' in fp.GetFPIDAsString() or 'LED_D5' in fp.GetFPIDAsString()]
print('  tall parts (electrolytics, DIP, 5 mm LEDs):', big)
