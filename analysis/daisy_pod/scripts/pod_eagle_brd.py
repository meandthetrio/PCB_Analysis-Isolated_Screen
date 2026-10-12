#!/usr/bin/env python3
"""Daisy Pod Rev5 (Eagle 9.6.2 .brd) — read-only XML extraction for Pass 1 / Pass 6.
Design rules (mm), net classes, wire-width histogram per net, via inventory with the diameter Eagle
derives from rvViaOuter/rlMinViaOuter, polygons, package pads/SMDs with annular ring, text sizes,
objects on the layers the KiCad importer stripped, board dimensions, DNI values, GND airwires.
Run: python3 -I pod_eagle_brd.py [path/to/ES_Daisy_Pod_Rev5.brd]"""
import xml.etree.ElementTree as ET, collections, math, sys
B = sys.argv[1] if len(sys.argv) > 1 else '/home/user/PCB_Analysis-Isolated_Screen/reference/electrosmith/daisy_pod/ES_Daisy_Pod_Rev5.brd'
r = ET.parse(B).getroot(); brd = r.find('.//board')
lay = {l.get('number'): l.get('name') for l in r.find('.//layers')}
MIL = 0.0254
def val(s):
    s = s.strip()
    if ' ' in s: return [val(x) for x in s.split()]
    if s.endswith('mil'): return float(s[:-3]) * MIL
    if s.endswith('mm'): return float(s[:-2])
    if s.endswith('inch'): return float(s[:-4]) * 25.4
    try: return float(s)
    except ValueError: return s
dr = {p.get('name'): val(p.get('value')) for p in r.find('.//designrules').findall('param')}
print('== Eagle design rules (set "%s"), mm' % r.find('.//designrules').get('name'))
for k in ('mdWireWire', 'mdWirePad', 'mdWireVia', 'mdPadPad', 'mdPadVia', 'mdViaVia', 'mdSmdPad', 'mdSmdVia', 'mdSmdSmd',
          'mdCopperDimension', 'mdDrill', 'msWidth', 'msDrill', 'rvPadTop', 'rlMinPadTop', 'rlMaxPadTop', 'rvViaOuter',
          'rlMinViaOuter', 'rlMaxViaOuter', 'mlMinStopFrame', 'mlMaxStopFrame', 'mlViaStopLimit', 'mlMinCreamFrame',
          'mlMaxCreamFrame', 'slThermalIsolate', 'psElongationLong', 'mtCopper', 'mtIsolate'):
    print(f'  {k:18s} {dr.get(k)}')
print('== net classes:', [(c.get('name'), 'width', c.get('width'), 'drill', c.get('drill'), 'clearance', [x.get('value') for x in c.findall('clearance')]) for c in r.findall('.//classes/class')])

# ---- wires / vias / polygons
hist = collections.defaultdict(lambda: [0, 0.0]); tot = collections.defaultdict(lambda: [0, 0.0]); air = collections.Counter()
vias = collections.Counter(); vianet = collections.Counter(); polys = []
for s in brd.find('signals'):
    n = s.get('name')
    for w in s.findall('wire'):
        L = w.get('layer'); wd = float(w.get('width'))
        if L == '19': air[n] += 1; continue
        ln = math.hypot(float(w.get('x2')) - float(w.get('x1')), float(w.get('y2')) - float(w.get('y1')))
        hist[(n, wd)][0] += 1; hist[(n, wd)][1] += ln; tot[wd][0] += 1; tot[wd][1] += ln
    for v in s.findall('via'):
        d = float(v.get('drill')); dia = v.get('diameter')
        if dia is None:  # Eagle: ring = clamp(drill*rvViaOuter, rlMinViaOuter, rlMaxViaOuter)
            ring = min(max(d * dr['rvViaOuter'], dr['rlMinViaOuter']), dr['rlMaxViaOuter']); dia = d + 2 * ring
        else: dia = float(dia); ring = (dia - d) / 2
        vias[(d, round(dia, 4), round(ring, 4), v.get('extent'))] += 1; vianet[n] += 1
    for p in s.findall('polygon'):
        polys.append((n, lay.get(p.get('layer')), p.get('width'), p.get('isolate'), p.get('thermals'), p.get('rank'), p.get('orphans'), len(p.findall('vertex'))))
print('== copper wire widths (mm): {width: (segments, mm)}', {k: (v[0], round(v[1], 1)) for k, v in sorted(tot.items())})
print('== GND airwires (layer 19, polygon-connected pads, no stored fill):', dict(air))
byw = collections.defaultdict(list)
for (n, w), (c, l) in hist.items(): byw[w].append((n, c, round(l, 1)))
for w in sorted(byw): print(f'  width {w}: {len(byw[w])} nets ->', sorted(byw[w], key=lambda x: -x[2]))
print('== vias (drill, dia, ring, extent): count', dict(vias), '| per net', vianet.most_common(10))
print('== signal polygons (net, layer, width, isolate, thermals, rank, orphans, verts):', polys)

# ---- packages used, their pads/SMDs/texts and stripped-layer objects
STRIP = set(map(str, [17, 18, 23, 24, 37, 38] + list(range(41, 48)) + list(range(53, 61)) + list(range(88, 133)) + list(range(144, 256))))
els = brd.find('elements'); used = collections.Counter((e.get('library'), e.get('package')) for e in els)
libs = {}
for lib in brd.find('libraries'):
    for pk in lib.find('packages'): libs[(lib.get('name'), pk.get('name'))] = pk
print('== packages used (count): pads(drill, dia, shape -> ring) | smd | holes | stripped-layer objects | texts')
for key, pk in libs.items():
    if key not in used: continue
    pads = []
    for p in pk.findall('pad'):
        d = float(p.get('drill')); dia = p.get('diameter')
        if dia is None:
            ring = min(max(d * dr['rvPadTop'], dr['rlMinPadTop']), dr['rlMaxPadTop']); dia = d + 2 * ring
        else: dia = float(dia); ring = (dia - d) / 2
        shape = p.get('shape', 'round')
        pads.append((p.get('name'), d, round(dia, 4), shape, round(ring, 4)))
    smds = [(s.get('name'), s.get('dx'), s.get('dy'), lay.get(s.get('layer')), s.get('stop'), s.get('cream')) for s in pk.findall('smd')]
    holes = [h.get('drill') for h in pk.findall('hole')]
    strip = [(ch.tag, lay.get(ch.get('layer'), ch.get('layer'))) for ch in pk if ch.get('layer') in STRIP]
    texts = [(lay.get(t.get('layer')), t.get('size'), t.get('ratio'), t.text) for t in pk.findall('text')]
    dim = [(ch.tag, lay.get(ch.get('layer'))) for ch in pk if ch.get('layer') == '20']
    print(f'  {key[1]} x{used[key]}: pads {pads} | smd {len(smds)} {smds[:2]} {[s for s in smds if s[4] or s[5]]} | holes {holes} | STRIPPED {collections.Counter(strip)} | Dimension-layer items {len(dim)} | texts {texts}')
# ---- plain items
plain = brd.find('plain')
print('== plain items:', collections.Counter((e.tag, lay.get(e.get('layer'))) for e in plain))
for d in plain.findall('dimension'): print('  dimension', d.attrib)
for t in plain.findall('text'): print('  text', lay.get(t.get('layer')), 'size', t.get('size'), 'ratio', t.get('ratio', '8 (default)'), repr(t.text))
print('== elements with DNI in value / attributes, and element text (NAME) sizes:')
for e in els:
    at = {a.get('name'): a.get('value') for a in e.findall('attribute')}
    if 'DNI' in (e.get('value') or '') or any('DNI' in (v or '') or 'DNP' in (v or '') for v in at.values()):
        print('  ', e.get('name'), e.get('package'), e.get('value'), at)
ns = collections.Counter()
for e in els:
    for a in e.findall('attribute'):
        if a.get('name') == 'NAME': ns[(a.get('size'), lay.get(a.get('layer')))] += 1
print('  NAME attribute (size, layer) histogram:', sorted(ns.items()))
