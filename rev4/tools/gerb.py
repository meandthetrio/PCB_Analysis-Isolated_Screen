"""Gerber (RS-274X, KiCad 9 dialect) + Excellon parser producing shapely geometry."""
import re, math
from shapely.geometry import Point, Polygon, LineString, box
from shapely.ops import unary_union, polygonize
from shapely.strtree import STRtree

SCALE = 1e-6

def aperture_shape(shape, params):
    if shape == 'C':
        return Point(0, 0).buffer(params[0] / 2, 32)
    if shape == 'R':
        return box(-params[0] / 2, -params[1] / 2, params[0] / 2, params[1] / 2)
    if shape == 'O':
        w, h = params[0], params[1]
        r = min(w, h) / 2
        return box(-w / 2 + r, -h / 2 + r, w / 2 - r, h / 2 - r).buffer(r, 32)
    if shape == 'RoundRect':
        r = params[0]; pts = [(params[i], params[i + 1]) for i in range(1, 9, 2)]
        return Polygon(pts).buffer(r, 32)
    raise ValueError(shape)

class Layer:
    def __init__(self, path):
        self.path = path
        self.apertures = {}      # dcode -> (shape, params, func, polygon)
        self.flashes = []        # (x, y, dcode)
        self.draws = []          # (x1,y1,x2,y2,dcode)  (arcs linearised into segments)
        self.regions = []        # Polygon
        self._parse(path)
        self._build()

    def _parse(self, path):
        func = None; x = y = 0.0; cur = None; in_region = False; verts = []; arc_mode = None
        for raw in open(path, encoding='utf-8', errors='replace'):
            line = raw.strip()
            if not line: continue
            m = re.match(r'%TA\.AperFunction,(.+?)\*%', line)
            if m: func = m.group(1); continue
            m = re.match(r'%ADD(\d+)([A-Za-z_][A-Za-z0-9_]*),([-\d.X]+)\*%', line)
            if m:
                d, shape, params = int(m.group(1)), m.group(2), [float(v) for v in m.group(3).split('X')]
                self.apertures[d] = (shape, params, func, aperture_shape(shape, params)); continue
            if line.startswith('%') or line.startswith('G04'): continue
            if line == 'G36*': in_region = True; verts = []; continue
            if line == 'G37*':
                in_region = False
                if len(verts) >= 3:
                    p = Polygon(verts)
                    if not p.is_valid: p = p.buffer(0)
                    self.regions.append(p)
                continue
            if line in ('G01*',): arc_mode = None; continue
            if line in ('G02*', 'G03*'): arc_mode = line[:3]; continue
            m = re.match(r'D(\d+)\*$', line)
            if m and int(m.group(1)) >= 10: cur = int(m.group(1)); continue
            m = re.match(r'(?:G0([123]))?(?:X(-?\d+))?(?:Y(-?\d+))?(?:I(-?\d+))?(?:J(-?\d+))?D0([123])\*$', line)
            if not m: continue
            if m.group(1): arc_mode = 'G0' + m.group(1) if m.group(1) in '23' else None
            nx = float(m.group(2)) * SCALE if m.group(2) is not None else x
            ny = float(m.group(3)) * SCALE if m.group(3) is not None else y
            op = m.group(6)
            if op == '3':
                self.flashes.append((nx, ny, cur))
            elif op == '1':
                pts = [(nx, ny)]
                if m.group(4) is not None and arc_mode:
                    cx, cy = x + float(m.group(4)) * SCALE, y + float(m.group(5)) * SCALE
                    r = math.hypot(x - cx, y - cy)
                    a0 = math.atan2(y - cy, x - cx); a1 = math.atan2(ny - cy, nx - cx)
                    if arc_mode == 'G02':   # clockwise
                        if a1 >= a0: a1 -= 2 * math.pi
                    else:
                        if a1 <= a0: a1 += 2 * math.pi
                    if abs(a1 - a0) < 1e-9: a1 = a0 + (-2 * math.pi if arc_mode == 'G02' else 2 * math.pi)
                    n = max(8, int(abs(a1 - a0) / (math.pi / 36)))
                    pts = [(cx + r * math.cos(a0 + (a1 - a0) * k / n), cy + r * math.sin(a0 + (a1 - a0) * k / n)) for k in range(1, n + 1)]
                px, py = x, y
                for (qx, qy) in pts:
                    if in_region: verts.append((qx, qy))
                    else: self.draws.append((px, py, qx, qy, cur))
                    px, py = qx, qy
                nx, ny = pts[-1]
            else:
                if in_region: verts = [(nx, ny)]
            x, y = nx, ny

    def _build(self):
        from shapely import affinity
        self.pad_polys = []     # (poly, dcode, func)
        for (x, y, d) in self.flashes:
            sh, pr, fn, poly = self.apertures[d]
            self.pad_polys.append((affinity.translate(poly, x, y), d, fn))
        self.track_polys = []   # (poly, width)
        self.track_lines = []
        for (x1, y1, x2, y2, d) in self.draws:
            sh, pr, fn, _ = self.apertures[d]
            w = pr[0] if sh == 'C' else max(pr[:2])
            ls = LineString([(x1, y1), (x2, y2)])
            self.track_lines.append((ls, w, d))
            self.track_polys.append((ls.buffer(w / 2, 16) if w > 0 else ls, w))

    def all_polys(self):
        return [p for p, _, _ in self.pad_polys] + [p for p, _ in self.track_polys] + list(self.regions)

def parse_drill(path):
    tools = {}; holes = []; slots = []; cur = None
    for line in open(path):
        line = line.strip()
        m = re.match(r'T(\d+)C([\d.]+)', line)
        if m: tools[int(m.group(1))] = float(m.group(2)); continue
        m = re.match(r'T(\d+)$', line)
        if m: cur = tools.get(int(m.group(1))); continue
        m = re.match(r'X(-?[\d.]+)Y(-?[\d.]+)$', line)
        if m and cur: holes.append((float(m.group(1)), float(m.group(2)), cur)); continue
        m = re.match(r'G00X(-?[\d.]+)Y(-?[\d.]+)', line)
        if m and cur: slots.append([(float(m.group(1)), float(m.group(2))), None, cur]); continue
        m = re.match(r'G01X(-?[\d.]+)Y(-?[\d.]+)', line)
        if m and slots and slots[-1][1] is None: slots[-1][1] = (float(m.group(1)), float(m.group(2)))
    return tools, holes, slots

def outline_polygons(edge_layer):
    lines = [ls for ls, w, d in edge_layer.track_lines]
    merged = unary_union(lines)
    polys = list(polygonize(merged))
    return polys

def load_set(d):
    pfx = f"{d}/WavetableController-"
    L = {n: Layer(pfx + n + '.gbr') for n in ['F_Cu', 'B_Cu', 'F_Mask', 'B_Mask', 'F_Paste', 'B_Paste', 'F_Silkscreen', 'B_Silkscreen', 'Edge_Cuts']}
    _, pth, pslots = parse_drill(pfx + 'PTH.drl')
    _, npth, nslots = parse_drill(pfx + 'NPTH.drl')
    return L, pth, pslots, npth, nslots
