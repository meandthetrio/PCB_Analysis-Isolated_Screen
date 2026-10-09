#!/usr/bin/env python3
"""Dump a KiCad 9 .kicad_pcb to JSON via the pcbnew module.

Usage: python3 -I board_dump.py BOARD.kicad_pcb OUT.json
Emits footprints (ref, value, layer, pos, pads with number/name/net/pos/size/
shape/layers), tracks (net, layer, width, start, end, length), vias (net,
pos, drill, diameter, layers), zones (net, layer, filled area, outline bbox),
and net names. Units: mm.
"""
import sys, json
import pcbnew

def mm(v): return pcbnew.ToMM(v)

def main(path, out):
    b = pcbnew.LoadBoard(path)
    d = {'file': path, 'footprints': [], 'tracks': [], 'vias': [], 'zones': [], 'nets': {}}
    for code, net in b.GetNetInfo().NetsByNetcode().items():
        d['nets'][code] = net.GetNetname()
    for fp in b.GetFootprints():
        pos = fp.GetPosition()
        e = {'ref': fp.GetReference(), 'value': fp.GetValue(), 'fpid': fp.GetFPIDAsString(),
             'layer': b.GetLayerName(fp.GetLayer()), 'x': mm(pos.x), 'y': mm(pos.y),
             'rot': fp.GetOrientationDegrees(), 'pads': []}
        for p in fp.Pads():
            pp = p.GetPosition(); sz = p.GetSize()
            e['pads'].append({'num': p.GetNumber(), 'name': p.GetPinFunction(), 'net': p.GetNetname(),
                              'x': mm(pp.x), 'y': mm(pp.y), 'w': mm(sz.x), 'h': mm(sz.y),
                              'drill': mm(p.GetDrillSize().x), 'shape': int(p.GetShape()),
                              'attr': int(p.GetAttribute()),
                              'layers': [b.GetLayerName(l) for l in p.GetLayerSet().Seq()]})
        d['footprints'].append(e)
    for t in b.GetTracks():
        cls = t.GetClass()
        if cls == 'PCB_VIA':
            v = t.Cast(); p = v.GetPosition()
            d['vias'].append({'net': v.GetNetname(), 'x': mm(p.x), 'y': mm(p.y),
                              'drill': mm(v.GetDrillValue()), 'dia': mm(v.GetWidth()),
                              'layers': [b.GetLayerName(l) for l in v.GetLayerSet().Seq()]})
        elif cls == 'PCB_TRACK':
            s = t.GetStart(); en = t.GetEnd()
            d['tracks'].append({'net': t.GetNetname(), 'layer': b.GetLayerName(t.GetLayer()),
                                'w': mm(t.GetWidth()), 'x1': mm(s.x), 'y1': mm(s.y),
                                'x2': mm(en.x), 'y2': mm(en.y), 'len': mm(t.GetLength())})
        elif cls == 'PCB_ARC':
            s = t.GetStart(); en = t.GetEnd()
            d['tracks'].append({'net': t.GetNetname(), 'layer': b.GetLayerName(t.GetLayer()),
                                'w': mm(t.GetWidth()), 'x1': mm(s.x), 'y1': mm(s.y),
                                'x2': mm(en.x), 'y2': mm(en.y), 'len': mm(t.GetLength()), 'arc': True})
    for z in b.Zones():
        bb = z.GetBoundingBox()
        zi = {'net': z.GetNetname(), 'layers': [b.GetLayerName(l) for l in z.GetLayerSet().Seq()],
              'is_rule_area': z.GetIsRuleArea(), 'filled': z.IsFilled(),
              'bbox': [mm(bb.GetLeft()), mm(bb.GetTop()), mm(bb.GetRight()), mm(bb.GetBottom())],
              'min_thickness': mm(z.GetMinThickness()), 'clearance': mm(z.GetLocalClearance()),
              'filled_area_mm2': {}}
        for l in z.GetLayerSet().Seq():
            try:
                fa = z.GetFilledArea(l)
                zi['filled_area_mm2'][b.GetLayerName(l)] = fa / 1e12 if fa else 0
            except Exception:
                try:
                    zi['filled_area_mm2'][b.GetLayerName(l)] = z.GetFilledPolysList(l).Area() / 1e12
                except Exception as ex:
                    zi['filled_area_mm2'][b.GetLayerName(l)] = str(ex)
        d['zones'].append(zi)
    bb = b.GetBoardEdgesBoundingBox()
    d['board_bbox'] = [mm(bb.GetLeft()), mm(bb.GetTop()), mm(bb.GetRight()), mm(bb.GetBottom())]
    ds = b.GetDesignSettings()
    d['copper_layers'] = b.GetCopperLayerCount()
    json.dump(d, open(out, 'w'), indent=1)
    print(f"footprints={len(d['footprints'])} tracks={len(d['tracks'])} vias={len(d['vias'])} zones={len(d['zones'])} nets={len(d['nets'])}")
    for z in d['zones']: print(' zone', z['net'], z['layers'], 'rule_area' if z['is_rule_area'] else '', z['filled_area_mm2'])

if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
