#!/usr/bin/env python3
"""Daisy Pod Rev5 — Pass-2 power/decoupling geometry over board_dump.py JSON.

Usage: python3 -I pod_power_geom.py board.json
Sections:
  A. Rail copper per power net: track length by (layer,width), min width, vias,
     IPC-2221 external 1 oz ampacity at min width (dT 10 C), DC resistance at actual widths.
  B. IC power pin -> nearest same-net capacitor (straight line, pad centre to pad centre)
     and routed copper path length (graph walk over tracks/vias/pads).
  C. Routed path length from the Seed pin to each load on +3V3_D / +3V3_A.
  D. Signal nets: pad-to-pad routed length, vias, min width (encoder, buttons, pots, LEDs, MIDI, VIN).
  E. LED1/LED2 pad table.
"""
import sys, json, math, heapq
from collections import defaultdict

RHO = 1.72e-8; T1OZ = 0.035
POWER_NETS = ['+3V3_D', '+3V3_A', 'USB_VBUS', 'VIN', 'N$39', 'N$40', 'N$41']
TOL = 0.02  # mm endpoint coincidence tolerance

def ipc(width_mm, dT=10.0, t=T1OZ):
    a = (width_mm/0.0254)*(t/0.0254)
    return 0.048*dT**0.44*a**0.725
def rtrace(L, w, t=T1OZ): return RHO*(L/1000)/((w/1000)*(t/1000))
def d(a, b): return math.hypot(a[0]-b[0], a[1]-b[1])

def build(dd):
    pads = defaultdict(list)
    for f in dd['footprints']:
        for p in f['pads']:
            q = dict(p); q['ref'] = f['ref']; q['value'] = f['value']; q['fp_layer'] = f['layer']
            pads[q['net']].append(q)
    tr = defaultdict(list); vi = defaultdict(list)
    for t in dd['tracks']: tr[t['net']].append(t)
    for v in dd['vias']: vi[v['net']].append(v)
    return pads, tr, vi

def pad_hit(p, pt, layer):
    """point lies within pad rectangle (axis-aligned approx, size swapped if rotated 90) on a layer the pad has"""
    if layer not in p['layers'] and not (len(p['layers']) > 2): return False
    sx, sy = p['size']; sx /= 2; sy /= 2
    # Eagle imports keep pad sizes in footprint-local orientation; accept either orientation
    dx, dy = abs(pt[0]-p['pos'][0]), abs(pt[1]-p['pos'][1])
    return (dx <= sx+TOL and dy <= sy+TOL) or (dx <= sy+TOL and dy <= sx+TOL)

def net_graph(net, pads, tr, vi):
    """Nodes: ('pad',i), ('via',i), ('pt',layer,x,y). Edges: track segments (weight=len), via (0), pad hits (0)."""
    g = defaultdict(list)
    def add(a, b, w): g[a].append((b, w)); g[b].append((a, w))
    pts = defaultdict(list)  # layer -> list of (node, xy)
    def pt_node(layer, xy):
        for n, q in pts[layer]:
            if d(q, xy) <= TOL: return n
        n = ('pt', layer, round(xy[0], 3), round(xy[1], 3)); pts[layer].append((n, xy)); return n
    for i, t in enumerate(tr[net]):
        a = pt_node(t['layer'], t['a']); b = pt_node(t['layer'], t['b']); add(a, b, t['len'])
    for i, v in enumerate(vi[net]):
        vn = ('via', i)
        for layer in ('F.Cu', 'B.Cu'):
            add(vn, pt_node(layer, v['pos']), 0.0)
    for i, p in enumerate(pads[net]):
        pn = ('pad', i); hit = False
        for layer in ('F.Cu', 'B.Cu'):
            for n, q in list(pts[layer]):
                if pad_hit(p, q, layer): add(pn, n, 0.0); hit = True
        if not hit:  # pad centre as a point (unrouted or direct pad-pad)
            for layer in p['layers'][:1] if len(p['layers']) <= 2 else ('F.Cu', 'B.Cu'):
                add(pn, pt_node(layer if layer in ('F.Cu','B.Cu') else 'F.Cu', p['pos']), 0.0)
    return g

def shortest(g, src, dst):
    dist = {src: 0.0}; pq = [(0.0, src)]; prev = {}
    while pq:
        dd_, n = heapq.heappop(pq)
        if n == dst: break
        if dd_ > dist.get(n, 1e9): continue
        for m, w in g[n]:
            nd = dd_ + w
            if nd < dist.get(m, 1e9): dist[m] = nd; prev[m] = n; heapq.heappush(pq, (nd, m))
    if dst not in dist: return None, 0
    vias = 0; n = dst
    while n in prev:
        if n[0] == 'via': vias += 1
        n = prev[n]
    return dist[dst], vias

def find_pad(pads, net, ref, num):
    for i, p in enumerate(pads[net]):
        if p['ref'] == ref and p['num'] == num: return i
    raise KeyError((net, ref, num))

def main(path):
    dd = json.load(open(path)); pads, tr, vi = build(dd)
    print(f"Board bbox {dd['bbox']} mm; copper layers {dd['copper_layers']}; {len(dd['footprints'])} footprints, {len(dd['tracks'])} tracks, {len(dd['vias'])} vias")
    print('\n=== A. RAIL COPPER ===')
    print('net | total_mm | by layer/width (mm@w) | min_w | vias | IPC2221 A@minw dT10 | R_total@actual(mOhm) | pads')
    for n in POWER_NETS:
        ts = tr.get(n, [])
        byw = defaultdict(float)
        for t in ts: byw[(t['layer'], round(t['w'], 4))] += t['len']
        tot = sum(byw.values()); minw = min([w for _, w in byw] or [0])
        r = sum(rtrace(L, w) for (_, w), L in byw.items())*1000
        plist = ','.join(f"{p['ref']}.{p['num']}" for p in pads[n])
        print(f"{n} | {tot:.1f} | " + ', '.join(f'{L:.1f}@{w}({l})' for (l, w), L in sorted(byw.items())) +
              f" | {minw} | {len(vi.get(n, []))} | {ipc(minw) if minw else 0:.2f} | {r:.0f} | {plist}")

    print('\n=== B. POWER PIN -> NEAREST SAME-NET CAP (straight line) and routed path ===')
    checks = [('U4', '6', '+3V3_A', 'TPA6110 VCC'), ('U4', '1', 'N$39', 'TPA6110 BYPASS'),
              ('U15', '6', '+3V3_D', 'H11L1 Vcc'), ('P1', '4', '+3V3_D', 'microSD VDD'),
              ('U1', '38', '+3V3_D', 'Seed 3V3_D out'), ('U1', '21', '+3V3_A', 'Seed 3V3_A out'),
              ('U7', '5', 'USB_VBUS', 'USBLC6 VBUS'), ('LED1', '2', '+3V3_D', 'LED1 anode'), ('LED2', '2', '+3V3_D', 'LED2 anode'),
              ('U4', '7', 'N$40', 'TPA OUT1 -> C62'), ('U4', '5', 'N$41', 'TPA OUT2 -> C63')]
    for ref, num, net, what in checks:
        g = net_graph(net, pads, tr, vi); i = find_pad(pads, net, ref, num); p = pads[net][i]
        caps = [(j, q) for j, q in enumerate(pads[net]) if q['ref'].startswith('C')]
        if not caps: print(f"{ref}.{num} {what} [{net}]: NO CAPACITOR ON NET"); continue
        rows = []
        for j, q in caps:
            L, nv = shortest(g, ('pad', i), ('pad', j))
            rows.append((d(p['pos'], q['pos']), q, L, nv))
        rows.sort(key=lambda r: r[0])
        s = '; '.join(f"{q['ref']} {q['value']} straight {sl:.2f} mm, routed {L if L is None else round(L,2)} mm/{nv} via" for sl, q, L, nv in rows)
        print(f"{ref}.{num} {what} [{net}] ({p['fp_layer']}): {s}")

    print('\n=== C. ROUTED PATH FROM SEED PIN TO EACH LOAD ===')
    for net, src in (('+3V3_D', ('U1', '38')), ('+3V3_A', ('U1', '21'))):
        g = net_graph(net, pads, tr, vi); i = find_pad(pads, net, *src)
        for j, q in enumerate(pads[net]):
            if j == i: continue
            L, nv = shortest(g, ('pad', i), ('pad', j))
            print(f"{net}: {src[0]}.{src[1]} -> {q['ref']}.{q['num']} ({q['value']}, {q['fp_layer']}): straight {d(pads[net][i]['pos'], q['pos']):.1f} mm, routed {L if L is None else round(L,1)} mm, {nv} vias")

    print('\n=== D. SIGNAL NETS pad-to-pad ===')
    sig = ['ENC_A', 'ENC_B', 'ENC_CLICK', 'TAC_SWITCH_1', 'TAC_SWITCH_2', 'POT_1', 'POT_2',
           'LED_1_R', 'LED_1_G', 'LED_1_B', 'LED_2_R', 'LED_2_G', 'LED_2_B', 'N$2', 'N$3', 'N$4', 'N$5', 'N$6', 'N$7',
           'USART1_RX', 'VIN', 'USB_VBUS', 'MIDI_IN_A', 'MIDI_IN_B', 'N$77', 'MIDI_IN_TIP', 'MIDI_IN_RING', 'A1', 'A7']
    print('net | nodes | total copper mm | min w | vias | pad->pad routed (from first U1 pad or first pad)')
    for n in sig:
        ts = tr.get(n, []); ws = [t['w'] for t in ts]
        g = net_graph(n, pads, tr, vi)
        ps = pads[n]
        src = next((k for k, p in enumerate(ps) if p['ref'] == 'U1'), 0)
        paths = []
        for k, p in enumerate(ps):
            if k == src: continue
            L, nv = shortest(g, ('pad', src), ('pad', k))
            paths.append(f"{ps[src]['ref']}.{ps[src]['num']}->{p['ref']}.{p['num']} {L if L is None else round(L,1)}mm/{nv}v")
        print(f"{n} | {','.join(p['ref']+'.'+p['num'] for p in ps)} | {sum(t['len'] for t in ts):.1f} | {min(ws) if ws else '-'} | {len(vi.get(n, []))} | " + '; '.join(paths))

    print('\n=== E. LED PADS ===')
    for f in dd['footprints']:
        if f['ref'] in ('LED1', 'LED2'):
            print(f['ref'], f['fpid'], f['layer'], f['pos'], [(p['num'], p['net'], p['pos'], p['size']) for p in f['pads']])
    print('\nVia drills:', sorted({v['drill'] for v in dd['vias']}), 'via dias:', sorted({v['dia'] for v in dd['vias']}))

if __name__ == '__main__': main(sys.argv[1])
