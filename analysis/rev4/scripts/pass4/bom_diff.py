#!/usr/bin/env python3
"""Designator-level diff of two JLCPCB-format BOM .xls files (rev2 -> rev3)."""
import sys, xlrd, collections
def load(path):
    sh = xlrd.open_workbook(path).sheet_by_index(0)
    hdr = [str(sh.cell_value(0, c)).strip() for c in range(sh.ncols)]; ci = {h: i for i, h in enumerate(hdr)}
    m = {}
    for r in range(1, sh.nrows):
        d = str(sh.cell_value(r, ci['Designator']))
        fp = sh.cell_value(r, ci['Footprint']); fp = f"{int(fp):04d}" if isinstance(fp, float) else str(fp)
        for x in d.split(','):
            x = x.strip()
            if x: m[x] = (str(sh.cell_value(r, ci['JLCPCB Part #'])).strip(), fp)
    return m
a, b = load(sys.argv[1]), load(sys.argv[2])
print(f"rev2: {len(a)} designators; rev3: {len(b)} designators")
print("removed:", sorted(set(a) - set(b)))
print("added:  ", sorted(set(b) - set(a)))
print("changed LCSC/footprint:")
for k in sorted(set(a) & set(b)):
    if a[k] != b[k]: print(f"  {k}: {a[k]} -> {b[k]}")
