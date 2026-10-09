#!/usr/bin/env python3
"""Dump every footprint of a .kicad_pcb via pcbnew: ref, value, fpid, side, attr (SMD/THT),
exclude-from-BOM / exclude-from-POS flags, pad counts (SMD / THT), pads with paste (F/B), pad size summary.
Usage: python3 -I pcb_footprints.py BOARD.kicad_pcb > out.csv
"""
import sys, csv
import pcbnew

b = pcbnew.LoadBoard(sys.argv[1])
w = csv.writer(sys.stdout)
w.writerow(['ref', 'value', 'fpid', 'side', 'attr', 'excl_bom', 'excl_pos', 'dnp',
            'n_pads', 'n_smd_pads', 'n_tht_pads', 'n_fpaste_pads', 'n_bpaste_pads',
            'pad_sizes_mm', 'x_mm', 'y_mm'])
for fp in b.GetFootprints():
    attr = fp.GetAttributes()
    kind = 'SMD' if attr & pcbnew.FP_SMD else ('THT' if attr & pcbnew.FP_THROUGH_HOLE else 'UNSPECIFIED')
    excl_bom = bool(attr & pcbnew.FP_EXCLUDE_FROM_BOM)
    excl_pos = bool(attr & pcbnew.FP_EXCLUDE_FROM_POS_FILES)
    dnp = bool(attr & pcbnew.FP_DNP)
    n_smd = n_tht = n_fp = n_bp = 0
    sizes = set()
    for p in fp.Pads():
        pa = p.GetAttribute()
        if pa == pcbnew.PAD_ATTRIB_SMD:
            n_smd += 1
        elif pa == pcbnew.PAD_ATTRIB_PTH:
            n_tht += 1
        ls = p.GetLayerSet()
        if ls.Contains(pcbnew.F_Paste):
            n_fp += 1
        if ls.Contains(pcbnew.B_Paste):
            n_bp += 1
        if pa in (pcbnew.PAD_ATTRIB_SMD, pcbnew.PAD_ATTRIB_PTH):
            s = p.GetSize()
            sizes.add(f"{pcbnew.ToMM(s.x):.2f}x{pcbnew.ToMM(s.y):.2f}")
    pos = fp.GetPosition()
    w.writerow([fp.GetReference(), fp.GetValue(), fp.GetFPIDAsString(),
                'top' if fp.GetLayer() == pcbnew.F_Cu else 'bottom', kind, excl_bom, excl_pos, dnp,
                len(fp.Pads()), n_smd, n_tht, n_fp, n_bp, ' '.join(sorted(sizes)),
                f"{pcbnew.ToMM(pos.x):.3f}", f"{pcbnew.ToMM(pos.y):.3f}"])
