#!/usr/bin/env python3
"""Pass-2 power geometry measurements over board_dump.py JSON.

Usage: python3 -I power_geom.py board.json
Sections:
  A. Rail copper: per power net, track length per (layer,width), min width, vias,
     IPC-2221 external 1oz ampacity at the min width (dT=10C), DC resistance of
     the total routed length at min width (worst case) and at actual widths.
  B. IC power pins -> nearest same-net capacitor (straight-line pad-to-pad).
  C. U6 TPS62172 loop: pad-to-pad distances Cin->VIN/PGND, Cout->VOS/L1,
     L1->SW, thermal vias under EP, SW-node copper length.
  D. LED1/LED2 pad table (pad number/name/net/position) and driver chain.
  E. Series element placement (bridge, ferrites, D6, 3.3R chain, bulk caps).
"""
import sys, json, math
from collections import defaultdict

COPPER_RHO = 1.72e-8   # ohm.m, Cu
OZ1_T_MM = 0.035       # 1 oz copper
POWER_NETS = ['/DSY_VIN', '/+9V_FLAG', '/+3V3_OLED', '/+3V3_D', '/+3V3_A', '/+5V_USB',
              'Net-(D2-K)', 'Net-(FB3-Pad2)', 'Net-(FB4-Pad2)', 'Net-(D6-A)', 'Net-(D6-K)',
              'Net-(C19-Pad1)', 'Net-(C17-Pad1)', 'Net-(C20-Pad1)', 'Net-(U6-EN)', 'Net-(U6-SW)',
              'Net-(U4-VDD)', 'Net-(D2-A)', 'Net-(D3-A)', 'Net-(SW1-A)']

def ipc2221_external_A(width_mm, dT=10.0, t_mm=OZ1_T_MM):
    # IPC-2221 external: I = 0.048 * dT^0.44 * A^0.725, A in mil^2
    a_mil2 = (width_mm / 0.0254) * (t_mm / 0.0254)
    return 0.048 * dT**0.44 * a_mil2**0.725

def r_trace(len_mm, width_mm, t_mm=OZ1_T_MM):
    return COPPER_RHO * (len_mm / 1000) / ((width_mm / 1000) * (t_mm / 1000))

def dist(a, b): return math.hypot(a['x'] - b['x'], a['y'] - b['y'])

def main(path):
    d = json.load(open(path))
    fps = {f['ref']: f for f in d['footprints']}
    pads_by_net = defaultdict(list)
    for f in d['footprints']:
        for p in f['pads']:
            p = dict(p); p['ref'] = f['ref']; p['value'] = f['value']
            pads_by_net[p['net']].append(p)
    tracks_by_net = defaultdict(list)
    for t in d['tracks']: tracks_by_net[t['net']].append(t)
    vias_by_net = defaultdict(list)
    for v in d['vias']: vias_by_net[v['net']].append(v)

    print('=== A. RAIL COPPER (tracks only; GND zone separate) ===')
    print('net | total_mm | by layer/width (mm@w) | min_w | vias | IPC2221 A@minw dT10 | R_total@actual(mOhm) | R_if_all_at_minw(mOhm)')
    for n in POWER_NETS:
        ts = tracks_by_net.get(n, [])
        if not ts: print(f'{n} | NO TRACKS | pads={[(p["ref"],p["num"]) for p in pads_by_net.get(n,[])]}'); continue
        byw = defaultdict(float)
        for t in ts: byw[(t['layer'], round(t['w'], 3))] += t['len']
        tot = sum(byw.values()); minw = min(w for _, w in byw)
        r_act = sum(r_trace(L, w) for (_, w), L in byw.items()) * 1000
        print(f"{n} | {tot:.1f} | " + ', '.join(f'{L:.1f}@{w}({l})' for (l, w), L in sorted(byw.items())) +
              f" | {minw} | {len(vias_by_net.get(n,[]))} | {ipc2221_external_A(minw):.2f} A | {r_act:.0f} | {r_trace(tot,minw)*1000:.0f}")

    print('\n=== B. IC POWER PIN -> NEAREST SAME-NET CAPACITOR (straight line pad centre to pad centre) ===')
    targets = [('A1','39'),('A1','38'),('A1','21'),('U1','6'),('U2','5'),('U3','6'),('U4','5'),('U6','2'),('U6','6'),('J8','2'),('P1','4')]
    print('pin | net | nearest cap (value) | dist mm | all same-net caps (value@mm)')
    for ref, num in targets:
        pad = next((p for p in fps[ref]['pads'] if p['num'] == num), None)
        if not pad: print(ref, num, 'NOT FOUND'); continue
        caps = [p for p in pads_by_net[pad['net']] if p['ref'].startswith('C')]
        caps = sorted(caps, key=lambda c: dist(c, pad))
        s = ', '.join(f"{c['ref']}({c['value']})@{dist(c,pad):.1f}" for c in caps)
        near = f"{caps[0]['ref']}({caps[0]['value']})@{dist(caps[0],pad):.1f}" if caps else 'NONE'
        print(f"{ref}.{num} {pad['name']} | {pad['net']} | {near} | {s}")

    print('\n=== C. U6 TPS62172 LOOP GEOMETRY ===')
    def pad(ref, num): return next(p for p in fps[ref]['pads'] if p['num'] == num)
    for r in ['U6', 'C25', 'C26', 'L1', 'R33', 'C23', 'C24', 'FB7', 'J8']:
        f = fps[r]; print(f"{r} {f['value']} layer={f['layer']} at ({f['x']:.2f},{f['y']:.2f}) rot={f['rot']}")
    for r in ['U6', 'L1', 'C25', 'C26']:
        for p in fps[r]['pads']:
            print(f"   {r}.{p['num']:<3} {p['name']:<5} {p['net']:<16} ({p['x']:.2f},{p['y']:.2f}) {p['w']:.2f}x{p['h']:.2f} {p['layers'][0]}")
    pairs = [('Cin+ C25.1 -> U6.2 VIN', pad('C25','1'), pad('U6','2')),
             ('Cin- C25.2 -> U6.1 PGND', pad('C25','2'), pad('U6','1')),
             ('Cout+ C26.1 -> U6.6 VOS', pad('C26','1'), pad('U6','6')),
             ('Cout+ C26.1 -> L1.2', pad('C26','1'), pad('L1','2')),
             ('Cout- C26.2 -> U6.1 PGND', pad('C26','2'), pad('U6','1')),
             ('L1.1 -> U6.7 SW', pad('L1','1'), pad('U6','7')),
             ('C23 100n -> J8.2 VDD', pad('C23','2'), pad('J8','2')),
             ('C24 100u -> J8.2 VDD', pad('C24','1'), pad('J8','2')),
             ('C26 -> J8.2 VDD', pad('C26','1'), pad('J8','2')),
             ('U6.6 VOS -> J8.2 VDD', pad('U6','6'), pad('J8','2'))]
    for name, a, b in pairs: print(f"   {name}: {dist(a,b):.2f} mm")
    ep = pad('U6', '9'); u6 = fps['U6']
    tv = [v for v in d['vias'] if v['net'] == 'GND' and abs(v['x'] - ep['x']) <= 1.2 and abs(v['y'] - ep['y']) <= 1.2]
    print(f"   EP pad U6.9 at ({ep['x']:.2f},{ep['y']:.2f}) {ep['w']:.2f}x{ep['h']:.2f}; GND vias within 1.2mm box: {len(tv)} -> " +
          ', '.join(f"({v['x']:.2f},{v['y']:.2f}) drill {v['drill']} dia {v['dia']}" for v in tv))
    allv_near = [v for v in d['vias'] if abs(v['x'] - u6['x']) <= 4 and abs(v['y'] - u6['y']) <= 4]
    print(f"   all vias within 4mm of U6: {len(allv_near)}: " + ', '.join(f"{v['net']}({v['x']:.1f},{v['y']:.1f},d{v['drill']})" for v in allv_near))
    for n in ['Net-(U6-SW)', 'Net-(U6-EN)', '/+3V3_OLED']:
        ts = tracks_by_net[n]; print(f"   {n}: {len(ts)} segs, {sum(t['len'] for t in ts):.2f} mm, widths {sorted(set(round(t['w'],2) for t in ts))}, layers {sorted(set(t['layer'] for t in ts))}, vias {len(vias_by_net[n])}")
    # distance from U6 (switcher) to sensitive stuff
    for r in ['U3', 'U4', 'MK1', 'A1', 'J7']:
        print(f"   U6 -> {r}: {dist(fps['U6'], fps[r]):.1f} mm")

    print('\n=== D. LED FOOTPRINT PAD TABLE + DRIVER CHAIN ===')
    for r in ['LED1', 'LED2']:
        f = fps[r]; print(f"{r} {f['value']} {f['fpid']} layer={f['layer']} at ({f['x']:.2f},{f['y']:.2f}) rot={f['rot']}")
        for p in sorted(f['pads'], key=lambda p: int(p['num'])):
            print(f"   pad {p['num']} name={p['name']:<3} net={p['net']:<24} rel=({p['x']-f['x']:+.2f},{p['y']-f['y']:+.2f}) abs=({p['x']:.2f},{p['y']:.2f}) {p['w']:.2f}x{p['h']:.2f}")
    print('Q / base R / collector R placement:')
    for r in ['Q1','Q2','Q3','Q4','Q5','Q6','R35','R36','R37','R38','R39','R40','R21','R24','R25','R26','R27','R28']:
        f = fps[r]; print(f"   {r} {f['value']:<9} {f['layer']:<5} ({f['x']:.1f},{f['y']:.1f}) pads: " + ', '.join(f"{p['num']}:{p['net']}" for p in f['pads']))

    print('\n=== E. SERIES POWER-CHAIN PLACEMENT ===')
    for r in ['J1','SW1','D2','D3','D4','D5','C14','FB3','FB4','FB5','C15','C16','D6','FB6','C19','R29','C17','R30','C18','R31','C20','R32','C21','C22','FB7','FB2','A1']:
        f = fps[r]; print(f"   {r:<4} {f['value']:<22} {f['layer']:<5} ({f['x']:6.1f},{f['y']:6.1f}) pads: " + ', '.join(f"{p['num']}:{p['net']}" for p in f['pads']))
    print(f"   board bbox {d['board_bbox']}")

if __name__ == '__main__':
    main(sys.argv[1])
