"""Render Gerber layers to SVG (optionally a crop) and rasterize with headless Chromium."""
import sys, subprocess, os
sys.path.insert(0, sys.argv[0].rsplit('/', 1)[0])
from gerb import *
from shapely.ops import unary_union
d, out = sys.argv[1], sys.argv[2]
crop = [float(v) for v in sys.argv[3].split(',')] if len(sys.argv) > 3 and sys.argv[3] else None  # xmin,ymin,xmax,ymax (gerber coords)
layers = sys.argv[4].split(',') if len(sys.argv) > 4 else ['B_Cu', 'F_Cu', 'B_Silkscreen', 'F_Silkscreen', 'Edge_Cuts']
px_per_mm = float(sys.argv[5]) if len(sys.argv) > 5 else 8
colors = {'F_Cu': ('#c83232', 0.75), 'B_Cu': ('#3264c8', 0.6), 'F_Silkscreen': ('#f0e68c', 0.9), 'B_Silkscreen': ('#30d030', 0.8),
          'Edge_Cuts': ('#ffff00', 1.0), 'F_Mask': ('#800080', 0.5), 'B_Mask': ('#800080', 0.5), 'F_Paste': ('#aaaaaa', 0.8), 'B_Paste': ('#aaaaaa', 0.8)}
pfx = f"{d}/WavetableController-"
geoms = {}
for n in layers:
    L = Layer(pfx + n + '.gbr')
    polys = L.all_polys()
    if n == 'Edge_Cuts': polys = [ls.buffer(0.1) for ls, w, dc in L.track_lines]
    if crop:
        win = box(*crop); polys = [p for p in polys if p.intersects(win)]
    geoms[n] = polys
if crop: xmin, ymin, xmax, ymax = crop
else:
    b = unary_union([unary_union(v) for v in geoms.values()]).bounds; xmin, ymin, xmax, ymax = b
W, H = (xmax - xmin) * px_per_mm, (ymax - ymin) * px_per_mm
def path(p):
    s = ''
    for ring in [p.exterior] + list(p.interiors):
        pts = list(ring.coords)
        s += 'M' + ' L'.join(f"{(x - xmin) * px_per_mm:.2f},{(ymax - y) * px_per_mm:.2f}" for x, y in pts) + ' Z '
    return s
svg = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W:.0f}" height="{H:.0f}" viewBox="0 0 {W:.0f} {H:.0f}"><rect width="100%" height="100%" fill="#111"/>']
for n in layers:
    col, op = colors[n]
    svg.append(f'<g fill="{col}" fill-opacity="{op}" fill-rule="evenodd" stroke="none">')
    for p in geoms[n]:
        if p.is_empty: continue
        if p.geom_type == 'MultiPolygon':
            for q in p.geoms: svg.append(f'<path d="{path(q)}"/>')
        elif p.geom_type == 'Polygon': svg.append(f'<path d="{path(p)}"/>')
    svg.append('</g>')
# mm grid labels every 10 mm
svg.append('<g stroke="#555" stroke-width="0.5" fill="#aaa" font-size="10">')
import math
for gx in range(int(math.ceil(xmin / 10)) * 10, int(xmax) + 1, 10):
    X = (gx - xmin) * px_per_mm; svg.append(f'<line x1="{X}" y1="0" x2="{X}" y2="{H}"/><text x="{X + 2}" y="12">{gx}</text>')
for gy in range(int(math.ceil(ymin / 10)) * 10, int(ymax) + 1, 10):
    Y = (ymax - gy) * px_per_mm; svg.append(f'<line x1="0" y1="{Y}" x2="{W}" y2="{Y}"/><text x="2" y="{Y - 2}">{gy}</text>')
svg.append('</g></svg>')
open(out + '.svg', 'w').write('\n'.join(svg))
chrome = '/opt/pw-browsers/chromium-1194/chrome-linux/chrome'
subprocess.run([chrome, '--headless=new', '--no-sandbox', '--disable-gpu', '--hide-scrollbars', f'--window-size={int(W)},{int(H)}', f'--screenshot={out}.png', 'file://' + os.path.abspath(out + '.svg')], capture_output=True)
print(out + '.png', int(W), int(H))
