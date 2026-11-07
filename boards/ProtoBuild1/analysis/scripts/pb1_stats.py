import sys, collections, pcbnew
for path in sys.argv[1:]:
    b = pcbnew.LoadBoard(path)
    bb = b.GetBoardEdgesBoundingBox()
    fps = list(b.GetFootprints())
    tracks = [t for t in b.GetTracks() if t.GetClass()=='PCB_TRACK']
    vias = [t for t in b.GetTracks() if t.GetClass()=='PCB_VIA']
    widths = collections.Counter(round(pcbnew.ToMM(t.GetWidth()),3) for t in tracks)
    layers = collections.Counter(b.GetLayerName(t.GetLayer()) for t in tracks)
    ds = b.GetDesignSettings()
    print(f"== {path.split('/')[-1]}")
    print(f"   pcbnew {pcbnew.Version()}: {len(fps)} footprints, {len(tracks)} tracks, {len(vias)} vias, {len(b.Zones())} zones, {b.GetNetCount()} nets, copper layers {b.GetCopperLayerCount()}")
    print(f"   board {pcbnew.ToMM(bb.GetWidth()):.2f} x {pcbnew.ToMM(bb.GetHeight()):.2f} mm, thickness {pcbnew.ToMM(ds.GetBoardThickness()):.2f}")
    print(f"   track widths (mm:count): {dict(sorted(widths.items()))}")
    print(f"   tracks per layer: {dict(layers)}")
    print(f"   via sizes: {collections.Counter((round(pcbnew.ToMM(v.GetWidth()),2), round(pcbnew.ToMM(v.GetDrillValue()),2)) for v in vias)}")
    print(f"   DRC mins: track {pcbnew.ToMM(ds.m_TrackMinWidth):.3f} clearance {pcbnew.ToMM(ds.m_MinClearance):.3f} via {pcbnew.ToMM(ds.m_ViasMinSize):.3f} hole {pcbnew.ToMM(ds.m_MinThroughDrill):.3f} h2h {pcbnew.ToMM(ds.m_HoleToHoleMin):.3f} edge {pcbnew.ToMM(ds.m_CopperEdgeClearance):.3f}")
    for z in b.Zones():
        print(f"   zone net='{z.GetNetname()}' layers={[b.GetLayerName(l) for l in z.GetLayerSet().Seq()]} filled={z.IsFilled()} keepout={z.GetIsRuleArea()} minw={pcbnew.ToMM(z.GetMinThickness()):.3f}")
    refs = collections.Counter(f.GetReference() for f in fps)
    dups = {r:c for r,c in refs.items() if c>1}
    print(f"   duplicate refs: {dups if dups else 'none'}")
    print(f"   refs: {' '.join(sorted(refs))}")
