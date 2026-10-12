#!/usr/bin/env python3
"""Map project-vs-production Gerber differences to footprints (pcbnew). Production Gerbers were plotted from the
aux origin; the plot in kicad_out from the page origin. Both negate Y. usage: kit_gerber_diff_map.py <board> <plot_dir> <prod_dir> <aux_x> <aux_y>"""
import pcbnew, re, sys, glob, collections, math
B, A, P, AX, AY = sys.argv[1], sys.argv[2], sys.argv[3], float(sys.argv[4]), float(sys.argv[5])
b = pcbnew.LoadBoard(B); mm = pcbnew.ToMM
pads = [(f.GetReference(), p.GetNumber(), mm(p.GetPosition().x), mm(p.GetPosition().y)) for f in b.GetFootprints() for p in f.Pads()]
fps = [(f.GetReference(), mm(f.GetPosition().x), mm(f.GetPosition().y), f.GetValue()) for f in b.GetFootprints()]
def nearest(x, y, items):
    return min(items, key=lambda r: math.hypot(r[-3] - x, r[-2] - y) if len(r) == 4 and isinstance(r[1], str) else math.hypot(r[1] - x, r[2] - y))
def parse(p, ox, oy, ysign):
    ap = {}; cur = None; sc = 10; fl = set(); dr = set(); last = None; inreg = False
    for line in open(p, errors='replace'):
        line = line.strip()
        m = re.match(r'%ADD(\d+)([A-Za-z_]+),?([^*]*)\*%', line)
        if m: ap[int(m.group(1))] = (m.group(2), m.group(3)); continue
        m = re.match(r'%FSLAX(\d)(\d)', line)
        if m: sc = 10 ** (6 - int(m.group(2))); continue
        if line.startswith('G36'): inreg = True; continue
        if line.startswith('G37'): inreg = False; continue
        m = re.match(r'D(\d+)\*', line)
        if m and int(m.group(1)) >= 10: cur = int(m.group(1)); continue
        m = re.match(r'(?:G0[123])?X(-?\d+)Y(-?\d+)(?:I(-?\d+)J(-?\d+))?D0([123])\*', line)
        if m:
            x = int(m.group(1)) * sc / 1e6 + ox; y = ysign * int(m.group(2)) * sc / 1e6 + oy; op = m.group(5)
            if op == '3': fl.add((ap[cur], round(x, 4), round(y, 4)))
            elif op == '1' and not inreg and last: dr.add((ap[cur], tuple(sorted([last, (round(x, 4), round(y, 4))]))))
            last = (round(x, 4), round(y, 4))
    return fl, dr
for L in ('F_Cu', 'B_Cu'):
    fa = glob.glob(f'{A}/*-{L}.g*')[0]; fb = glob.glob(f'{P}/*-{L}.g*')[0]
    FA, DA = parse(fa, 0, 0, -1); FB, DB = parse(fb, AX, AY, -1)  # plot: board coords = (gx, -gy); prod: (gx+AX, AY-gy)
    po = FA - FB; pr = FB - FA
    print(f'== {L}: flashes plot-only {len(po)} prod-only {len(pr)} | draws plot-only {len(DA-DB)} prod-only {len(DB-DA)}')
    byref = collections.defaultdict(lambda: [0, 0])
    for s, x, y in po:
        r = min(pads, key=lambda q: math.hypot(q[2] - x, q[3] - y)); byref[r[0]][0] += 1
    for s, x, y in pr:
        r = min(pads, key=lambda q: math.hypot(q[2] - x, q[3] - y)); d = math.hypot(r[2] - x, r[3] - y); byref[r[0] + (f'(moved {d:.2f}mm)' if d > 0.01 else '')][1] += 1
    print('   by nearest footprint (plot-only, prod-only):', dict(byref))
    # draw diffs: nearest-neighbour distance from each plot-only segment to prod-only segments (midpoint)
    def mid(seg): (a, c) = seg[1]; return ((a[0] + c[0]) / 2, (a[1] + c[1]) / 2)
    PO = list(DA - DB); PR = list(DB - DA)
    if PO and PR:
        dists = []
        for s in PO:
            mx, my = mid(s); dists.append(min(math.hypot(mid(t)[0] - mx, mid(t)[1] - my) for t in PR))
        dists.sort(); print(f'   draw diffs: nearest prod-only segment midpoint distance: median {dists[len(dists)//2]:.4f} mm, 90% {dists[int(len(dists)*0.9)]:.4f}, max {dists[-1]:.3f}; widths plot-only', collections.Counter(s[0] for s in PO).most_common(3))
        far = [s for s, d in zip(PO, dists) if d > 0.5]
        fr = collections.Counter()
        for s in far:
            mx, my = mid(s); r = min(fps, key=lambda q: math.hypot(q[1] - mx, q[2] - my)); fr[r[0]] += 1
        print('   draw segments with no counterpart within 0.5 mm:', len(far), 'near footprints', fr.most_common(12))
# drill
da = glob.glob(f'{A}/**/*.drl', recursive=True)[0]; db = glob.glob(f'{P}/**/*.drl', recursive=True)[0]
def drl(p, ox, oy, ysign):
    tools = {}; cur = None; hs = set()
    for line in open(p, errors='replace'):
        line = line.strip(); m = re.match(r'T(\d+)C([\d.]+)', line)
        if m: tools[int(m.group(1))] = float(m.group(2)); continue
        m = re.match(r'T(\d+)$', line)
        if m: cur = int(m.group(1)); continue
        m = re.match(r'X(-?[\d.]+)Y(-?[\d.]+)', line)
        if m and cur: hs.add((tools[cur], round(float(m.group(1)) + ox, 3), round(ysign * float(m.group(2)) + oy, 3)))
    return hs
HA = drl(da, 0, 0, -1); HB = drl(db, AX, AY, -1)
print('== drill: plot-only', len(HA - HB), 'prod-only', len(HB - HA))
for tag, st in (('plot-only', HA - HB), ('prod-only', HB - HA)):
    out = collections.Counter()
    for t, x, y in st:
        r = min(pads + [('via', '', mm(v.GetPosition().x), mm(v.GetPosition().y)) for v in b.GetTracks() if v.GetClass() == 'PCB_VIA'], key=lambda q: math.hypot(q[2] - x, q[3] - y)); d = math.hypot(r[2] - x, r[3] - y)
        out[(t, r[0] if d < 0.01 else f'{r[0]} nearest {d:.2f}mm')] += 1
    print('  ', tag, sorted(out.items()))
