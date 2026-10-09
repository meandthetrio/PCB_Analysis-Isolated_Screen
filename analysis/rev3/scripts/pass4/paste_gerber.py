#!/usr/bin/env python3
"""Count paste openings in a KiCad Gerber paste layer and attribute each to the nearest
pcb SMD pad (from pcbnew). Reports: flash count per aperture, total openings, and the
set of footprint refs whose pads received paste.
Usage: python3 -I paste_gerber.py BOARD.kicad_pcb F_PASTE.gtp B_PASTE.gbp
"""
import sys, re, collections
import pcbnew

def parse_gerber(path):
    """Return list of (x_mm, y_mm, aperture) for D03 flashes, and count of G36 regions."""
    txt = open(path, encoding='utf-8', errors='replace').read()
    m = re.search(r'%FS[LT]A?X(\d)(\d)Y(\d)(\d)\*%', txt)
    xi, xd = int(m.group(1)), int(m.group(2))
    unit = re.search(r'%MO(MM|IN)\*%', txt).group(1)
    scale = 10 ** xd
    if unit == 'IN':
        scale /= 25.4
    flashes = []
    regions = 0
    cur_ap = None
    x = y = 0.0
    for line in txt.splitlines():
        if line.startswith('G36'):
            regions += 1
        m = re.match(r'(?:G0[123])?D(\d+)\*$', line)
        if m and int(m.group(1)) >= 10:
            cur_ap = int(m.group(1)); continue
        m = re.match(r'(?:G0[123])?(?:X(-?\d+))?(?:Y(-?\d+))?(?:I-?\d+)?(?:J-?\d+)?D0?(\d)\*$', line)
        if m:
            if m.group(1) is not None: x = int(m.group(1)) / scale
            if m.group(2) is not None: y = int(m.group(2)) / scale
            if m.group(3) == '3':
                flashes.append((x, y, cur_ap))
    return flashes, regions

board = pcbnew.LoadBoard(sys.argv[1])
pads = []  # (x, y, ref, layer)
for fp in board.GetFootprints():
    for p in fp.Pads():
        ls = p.GetLayerSet()
        c = p.GetPosition()
        if ls.Contains(pcbnew.F_Paste):
            pads.append((pcbnew.ToMM(c.x), -pcbnew.ToMM(c.y), fp.GetReference(), 'F'))
        if ls.Contains(pcbnew.B_Paste):
            pads.append((pcbnew.ToMM(c.x), -pcbnew.ToMM(c.y), fp.GetReference(), 'B'))

for layer, path in (('F', sys.argv[2]), ('B', sys.argv[3])):
    flashes, regions = parse_gerber(path)
    lp = [p for p in pads if p[3] == layer]
    hit = collections.Counter(); unmatched = 0
    for fx, fy, ap in flashes:
        best = min(lp, key=lambda p: (p[0]-fx)**2 + (p[1]-fy)**2) if lp else None
        if best and (best[0]-fx)**2 + (best[1]-fy)**2 < 0.25**2:
            hit[best[2]] += 1
        else:
            unmatched += 1
    print(f"{layer}_Paste: {len(flashes)} flashes, {regions} G36 regions; pcb paste pads on this side: {len(lp)}; "
          f"unmatched flashes: {unmatched}")
    print(f"  refs with paste ({len(hit)}): " + ' '.join(f"{r}:{n}" for r, n in sorted(hit.items())))
