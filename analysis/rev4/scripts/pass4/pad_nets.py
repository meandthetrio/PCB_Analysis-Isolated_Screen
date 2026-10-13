#!/usr/bin/env python3
"""Print pad->net for the given refs (or all THT footprints if none given)."""
import sys, pcbnew
b = pcbnew.LoadBoard(sys.argv[1]); want = set(sys.argv[2:])
for fp in sorted(b.GetFootprints(), key=lambda f: f.GetReference()):
    if want and fp.GetReference() not in want: continue
    if not want and not (fp.GetAttributes() & pcbnew.FP_THROUGH_HOLE): continue
    nets = sorted({(p.GetNumber(), p.GetNetname()) for p in fp.Pads()}, key=lambda t: (len(t[0]), t[0]))
    print(fp.GetReference(), fp.GetValue(), '|', ' '.join(f"{n}={net or 'NC'}" for n, net in nets))
