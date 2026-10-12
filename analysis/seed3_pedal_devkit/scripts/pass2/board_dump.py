"""Dump the Daisy Pod Rev5 KiCad board (Eagle import) to JSON for python3 -I geometry scripts.
Run: python3 board_dump.py IN.kicad_pcb OUT.json  (needs the pcbnew module; no -I)"""
import sys, json, pcbnew
b = pcbnew.LoadBoard(sys.argv[1])
def mm(v): return round(pcbnew.ToMM(v), 4)
out = {"layers": {}, "footprints": [], "tracks": [], "vias": [], "zones": [], "bbox": None}
for lid in b.GetEnabledLayers().Seq():
    out["layers"][lid] = b.GetLayerName(lid)
cu = [lid for lid in b.GetEnabledLayers().CuStack()]
out["copper_layers"] = [b.GetLayerName(l) for l in cu]
bb = b.GetBoardEdgesBoundingBox()
out["bbox"] = [mm(bb.GetLeft()), mm(bb.GetTop()), mm(bb.GetRight()), mm(bb.GetBottom())]
for fp in b.GetFootprints():
    f = {"ref": fp.GetReference(), "value": fp.GetValue(), "fpid": fp.GetFPIDAsString(),
         "layer": b.GetLayerName(fp.GetLayer()), "pos": [mm(fp.GetPosition().x), mm(fp.GetPosition().y)],
         "rot": fp.GetOrientationDegrees(), "pads": []}
    for p in fp.Pads():
        f["pads"].append({"num": p.GetNumber(), "net": p.GetNetname(), "pos": [mm(p.GetPosition().x), mm(p.GetPosition().y)],
                          "size": [mm(p.GetSize().x), mm(p.GetSize().y)], "drill": mm(p.GetDrillSize().x),
                          "layers": [b.GetLayerName(l) for l in p.GetLayerSet().CuStack()],
                          "shape": int(p.GetShape())})
    out["footprints"].append(f)
for t in b.GetTracks():
    cls = t.GetClass()
    if cls == "PCB_VIA":
        out["vias"].append({"net": t.GetNetname(), "pos": [mm(t.GetPosition().x), mm(t.GetPosition().y)],
                            "drill": mm(t.GetDrillValue()), "dia": mm(t.GetWidth())})
    elif cls == "PCB_TRACK":
        out["tracks"].append({"net": t.GetNetname(), "layer": b.GetLayerName(t.GetLayer()), "w": mm(t.GetWidth()),
                              "a": [mm(t.GetStart().x), mm(t.GetStart().y)], "b": [mm(t.GetEnd().x), mm(t.GetEnd().y)],
                              "len": mm(t.GetLength())})
    elif cls == "PCB_ARC":
        out["tracks"].append({"net": t.GetNetname(), "layer": b.GetLayerName(t.GetLayer()), "w": mm(t.GetWidth()),
                              "a": [mm(t.GetStart().x), mm(t.GetStart().y)], "b": [mm(t.GetEnd().x), mm(t.GetEnd().y)],
                              "len": mm(t.GetLength()), "arc": True})
for z in b.Zones():
    zz = {"net": z.GetNetname(), "layers": [b.GetLayerName(l) for l in z.GetLayerSet().CuStack()],
          "filled_area_mm2": None, "is_keepout": z.GetIsRuleArea(), "name": z.GetZoneName()}
    try:
        tot = 0
        for l in z.GetLayerSet().CuStack():
            tot += pcbnew.ToMM(pcbnew.ToMM(z.GetFilledArea(l)))  # nm^2 -> mm^2 via two ToMM
        zz["filled_area_mm2"] = round(tot, 1)
    except Exception as e:
        zz["err"] = str(e)
    out["zones"].append(zz)
json.dump(out, open(sys.argv[2], "w"), indent=0)
print(len(out["footprints"]), "footprints", len(out["tracks"]), "tracks", len(out["vias"]), "vias", len(out["zones"]), "zones", out["copper_layers"], out["bbox"])
