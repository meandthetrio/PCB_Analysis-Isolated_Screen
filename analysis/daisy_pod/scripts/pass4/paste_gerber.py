#!/usr/bin/env python3
"""Count paste openings in KiCad-plotted paste Gerbers (D03 flashes AND G36/G37 regions, which KiCad
uses for rotated rectangular pads) and attribute each to the nearest paste pad in the pcbnew board.
Usage: python3 -I paste_gerber.py BOARD.kicad_pcb F_PASTE.gtp B_PASTE.gbp"""
import sys, re, collections
import pcbnew

def parse(path):
    txt = open(path, encoding='utf-8', errors='replace').read()
    m = re.search(r'%FS[LT]A?X(\d)(\d)Y(\d)(\d)\*%', txt); scale = 10 ** int(m.group(2))
    if re.search(r'%MO(MM|IN)\*%', txt).group(1) == 'IN': scale /= 25.4
    openings = []  # (x, y, kind)
    x = y = 0.0; region = None
    for line in txt.splitlines():
        if line.startswith('G36'):
            region = []; continue
        if line.startswith('G37'):
            if region:
                xs = [p[0] for p in region]; ys = [p[1] for p in region]
                openings.append(((min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2, 'region'))
            region = None; continue
        m = re.match(r'(?:G0[123])?(?:X(-?\d+))?(?:Y(-?\d+))?(?:I-?\d+)?(?:J-?\d+)?D0?(\d)\*$', line)
        if m:
            if m.group(1) is not None: x = int(m.group(1)) / scale
            if m.group(2) is not None: y = int(m.group(2)) / scale
            if region is not None and m.group(3) in ('1', '2'):
                region.append((x, y))
            elif m.group(3) == '3':
                openings.append((x, y, 'flash'))
    return openings

board = pcbnew.LoadBoard(sys.argv[1])
pads = []
for fp in board.GetFootprints():
    for p in fp.Pads():
        ls = p.GetLayerSet(); c = p.GetPosition()
        for layer, lid in (('F', pcbnew.F_Paste), ('B', pcbnew.B_Paste)):
            if ls.Contains(lid):
                pads.append((pcbnew.ToMM(c.x), -pcbnew.ToMM(c.y), fp.GetReference(), layer))
for layer, path in (('F', sys.argv[2]), ('B', sys.argv[3])):
    ops = parse(path); lp = [p for p in pads if p[3] == layer]
    hit = collections.Counter(); unmatched = []
    for ox, oy, kind in ops:
        best = min(lp, key=lambda p: (p[0] - ox) ** 2 + (p[1] - oy) ** 2)
        if (best[0] - ox) ** 2 + (best[1] - oy) ** 2 < 0.25 ** 2: hit[best[2]] += 1
        else: unmatched.append((round(ox, 3), round(oy, 3), kind))
    kinds = collections.Counter(k for *_, k in ops)
    print(f"{layer}_Paste: {len(ops)} openings ({dict(kinds)}); pcbnew paste pads on this side: {len(lp)}; unmatched: {unmatched or 0}")
    pads_per_ref = collections.Counter(p[2] for p in lp)
    print("  per ref (gerber/pcbnew): " + ' '.join(f"{r}:{hit[r]}/{pads_per_ref[r]}" for r in sorted(pads_per_ref)))
    short = [r for r in pads_per_ref if hit[r] != pads_per_ref[r]]
    print("  refs where gerber count != pcbnew paste pad count:", short or 'none')
