#!/usr/bin/env python3
"""Quick Gerber/drill analysis for the WavetableController board."""
import re, math, sys, json
from collections import defaultdict

GDIR = "/Users/kyleriche/Desktop/PCB Analysis/Manifold_Gerb_LedFix"
PFX = GDIR + "/WavetableController-"

def parse_gerber(path):
    """Return dict: apertures {dcode: (shape, params, function)}, flashes [(x,y,dcode)],
    draws [(x1,y1,x2,y2,dcode)], regions count, bbox."""
    apertures = {}
    cur_func = None
    flashes, draws = [], []
    regions = 0
    x = y = 0.0
    cur_d = None
    in_region = False
    scale = 1e-6  # FSLAX46 -> 4.6, mm
    txt = open(path, encoding='utf-8', errors='replace').read()
    for line in txt.split('\n'):
        line = line.strip()
        if not line: continue
        m = re.match(r'%TA\.AperFunction,(.+?)\*%', line)
        if m: cur_func = m.group(1); continue
        if line.startswith('%TD'): continue
        m = re.match(r'%ADD(\d+)([A-Za-z_][A-Za-z0-9_]*),([-\d.X]+)\*%', line)
        if m:
            d, shape, params = int(m.group(1)), m.group(2), [float(v) for v in m.group(3).split('X')]
            apertures[d] = (shape, params, cur_func)
            continue
        if line == 'G36*': in_region = True; regions += 1; continue
        if line == 'G37*': in_region = False; continue
        m = re.match(r'D(\d+)\*$', line)
        if m and int(m.group(1)) >= 10:
            cur_d = int(m.group(1)); continue
        m = re.match(r'(?:G0[123])?X?(-?\d+)?Y?(-?\d+)?(?:I(-?\d+))?(?:J(-?\d+))?D0([123])\*', line)
        if m:
            nx = float(m.group(1))*scale if m.group(1) is not None else x
            ny = float(m.group(2))*scale if m.group(2) is not None else y
            op = m.group(5)
            if op == '3':
                flashes.append((nx, ny, cur_d))
            elif op == '1' and not in_region:
                draws.append((x, y, nx, ny, cur_d))
            x, y = nx, ny
    xs = [f[0] for f in flashes] + [d[0] for d in draws] + [d[2] for d in draws]
    ys = [f[1] for f in flashes] + [d[1] for d in draws] + [d[3] for d in draws]
    bbox = (min(xs), min(ys), max(xs), max(ys)) if xs else None
    return dict(apertures=apertures, flashes=flashes, draws=draws, regions=regions, bbox=bbox)

def parse_drill(path):
    tools = {}
    holes = []  # (x, y, dia)
    slots = []
    cur = None
    for line in open(path):
        line = line.strip()
        m = re.match(r'T(\d+)C([\d.]+)', line)
        if m: tools[int(m.group(1))] = float(m.group(2)); continue
        m = re.match(r'T(\d+)$', line)
        if m: cur = tools.get(int(m.group(1))); continue
        m = re.match(r'X(-?[\d.]+)Y(-?[\d.]+)$', line)
        if m and cur: holes.append((float(m.group(1)), float(m.group(2)), cur)); continue
        m = re.match(r'G00X(-?[\d.]+)Y(-?[\d.]+)', line)
        if m and cur:
            slots.append([(float(m.group(1)), float(m.group(2))), None, cur]); continue
        m = re.match(r'G01X(-?[\d.]+)Y(-?[\d.]+)', line)
        if m and slots and slots[-1][1] is None:
            slots[-1][1] = (float(m.group(1)), float(m.group(2)))
    return tools, holes, slots

def ap_size(ap):
    shape, p, func = ap
    if shape == 'C': return p[0]
    if shape in ('R', 'O'): return min(p[0], p[1])
    if shape == 'RoundRect': return None
    return None

def summarize_layer(name, g):
    aps = g['apertures']
    # trace widths: apertures used in draws with Conductor function or circle
    widths = defaultdict(int)
    for d in g['draws']:
        ap = aps.get(d[4])
        if ap and ap[0] == 'C':
            widths[ap[1][0]] += 1
    print(f"\n== {name} ==")
    print(f"  apertures: {len(aps)}, flashes: {len(g['flashes'])}, draw segments: {len(g['draws'])}, regions: {g['regions']}")
    if g['bbox']:
        b = g['bbox']
        print(f"  bbox: X {b[0]:.2f}..{b[2]:.2f}  Y {b[1]:.2f}..{b[3]:.2f}  ({b[2]-b[0]:.1f} x {b[3]-b[1]:.1f} mm)")
    if widths:
        print("  track widths used (mm: segment count):", {round(k,3): v for k, v in sorted(widths.items())})
    return widths

layers = {}
for lname in ['F_Cu', 'B_Cu', 'F_Mask', 'B_Mask', 'F_Paste', 'B_Paste', 'Edge_Cuts']:
    layers[lname] = parse_gerber(PFX + lname + '.gbr')
    summarize_layer(lname, layers[lname])

ptools, pholes, pslots = parse_drill(PFX + 'PTH.drl')
ntools, nholes, nslots = parse_drill(PFX + 'NPTH.drl')
print(f"\n== Drills ==")
from collections import Counter
pc = Counter(h[2] for h in pholes)
nc = Counter(h[2] for h in nholes)
print(f"  PTH: {len(pholes)} holes {dict(sorted(pc.items()))}, slots: {len(pslots)}")
print(f"  NPTH: {len(nholes)} holes {dict(sorted(nc.items()))}, slots: {len(nslots)} {[ (s[0],s[1],s[2]) for s in nslots]}")

# Edge cuts bbox vs drill coords (drill Y is negative of gerber? KiCad drill uses same coords but gerber Y here...)
eb = layers['Edge_Cuts']['bbox']
print(f"\n  Edge bbox: {eb}")
# check drill coordinate space: drills have negative Y, gerber Y range?
print("  sample PTH:", pholes[:3])

# Annular ring check: for each PTH hole find nearest flash on F_Cu and B_Cu
def flash_diameter(ap, dcode_params_needed=False):
    shape, p, func = ap
    if shape == 'C': return p[0]
    if shape in ('R','O'): return min(p[0], p[1])
    if shape == 'RoundRect': return None
    return None

def check_annular(holes, layer, aps_layer_name):
    g = layers[layer]
    aps = g['apertures']
    issues = []
    matched = 0
    min_ring = 99
    for (hx, hy, dia) in holes:
        # gerber coords: same X, Y sign? compare
        best = None; bestd = 1e9
        for (fx, fy, dc) in g['flashes']:
            dd = (fx-hx)**2 + (fy-hy)**2
            if dd < bestd: bestd = dd; best = (fx, fy, dc)
        dist = math.sqrt(bestd)
        if dist > 0.05:
            issues.append((hx, hy, dia, round(dist,3), 'no coincident pad flash'))
        else:
            matched += 1
            ap = aps.get(best[2])
            sz = flash_diameter(ap) if ap else None
            if sz is not None:
                ring = (sz - dia)/2
                min_ring = min(min_ring, ring)
                if ring < 0.13:
                    issues.append((hx, hy, dia, round(ring,3), f'small annular ring (pad {sz})'))
    return matched, min_ring, issues

for layer in ['F_Cu', 'B_Cu']:
    matched, min_ring, issues = check_annular(pholes, layer, layer)
    print(f"\n== PTH vs {layer}: matched {matched}/{len(pholes)}, min annular ring {min_ring:.3f} mm")
    for i in issues[:25]:
        print("   ", i)
    if len(issues) > 25: print(f"    ... {len(issues)-25} more")

# Via count: PTH 0.3mm = vias
print("\nPTH 0.3mm (via) count:", pc.get(0.3))

# NPTH holes vs copper flashes (should NOT have copper pads ideally, check clearance)
for layer in ['F_Cu','B_Cu']:
    g = layers[layer]
    for (hx,hy,dia) in nholes:
        for (fx,fy,dc) in g['flashes']:
            if abs(fx-hx)<0.01 and abs(fy-hy)<0.01:
                ap = g['apertures'][dc]
                print(f"NPTH at ({hx},{hy}) d{dia} has copper flash on {layer}: {ap}")

# Mask openings vs copper pads: SMD pads with no mask opening (tombstone risk none but check)
# For each paste flash, check mask flash nearby
for side in ['F','B']:
    paste = layers[f'{side}_Paste']['flashes']
    mask = layers[f'{side}_Mask']['flashes']
    missing = 0
    for (px,py,dc) in paste:
        ok = any(abs(mx-px)<0.05 and abs(my-py)<0.05 for (mx,my,mdc) in mask)
        if not ok: missing += 1
    print(f"{side} paste flashes: {len(paste)}, without matching mask opening: {missing}; mask flashes: {len(mask)}")
