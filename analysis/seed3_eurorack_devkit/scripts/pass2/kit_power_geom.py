#!/usr/bin/env python3
"""Seed 3 Dev Kits (Eurorack Rev3 / Pedal Rev3) — Pass-2 power/decoupling geometry over board_dump.py JSON.

Usage: python3 -I kit_power_geom.py board.json euro|pedal
Sections:
  A. Rail copper per power net: track length by (layer,width), min width, vias,
     IPC-2221 external 1 oz ampacity at min width (dT 10 C), DC resistance at actual widths.
  B. IC power pin -> nearest same-net capacitor (straight line, pad centre to pad centre)
     and routed copper path length (graph walk over tracks/vias/pads).
  C. Routed path length from the Seed pin to each load on the Seed-fed rails.
  D. Signal nets: pad-to-pad routed length, vias, min width.
  E. Series-element placement (beads, diodes, 3R3) and LED pad table.
Derived from analysis/daisy_pod/scripts/pass2/pod_power_geom.py (same graph walker; known-answer checks there).
"""
import sys, json, math, heapq
from collections import defaultdict

RHO = 1.72e-8; T1OZ = 0.035
TOL = 0.02  # mm endpoint coincidence tolerance

CFG = {
 'euro': dict(
   power=['Net-(FB2-Pad1)', 'Net-(D1-A)', '+12V', 'Net-(C46-Pad1)', 'DSY_VIN', 'Net-(FB3-Pad1)', 'Net-(D2-K)', '-12V',
          '-10V_REF', '+3V3', '+3V3_A', '/Daisy/+5V_USB'],
   checks=[('A1','39','DSY_VIN','Seed VIN'), ('A1','38','+3V3','Seed 3V3_D out'), ('A1','21','+3V3_A','Seed 3V3_A out'),
           ('U7','4','+3V3','microSD VDD'), ('U11','6','+3V3','H11L1 Vcc'),
           ('U2','4','+3V3_A','MCP6004 VDD'), ('U12','16','+3V3_A','CD4051 VDD'),
           ('U1','8','+12V','TL072 U1 V+ (audio in)'), ('U1','4','-12V','TL072 U1 V-'),
           ('U13','8','+12V','TL072 U13 V+ (CV out)'), ('U13','4','-12V','TL072 U13 V-'),
           ('U15','8','+12V','TL072 U15 V+ (audio out)'), ('U15','4','-12V','TL072 U15 V-'),
           ('U3','2','-10V_REF','LM4040 anode (-10V ref)'), ('D1','1','+12V','D1 cathode = +12V node'),
           ('D2','2','-12V','D2 anode = -12V node'), ('R9','2','DSY_VIN','R9 -> DSY_VIN'),
           ('U14','5','/Daisy/+5V_USB','USBLC6 VBUS')],
   seed_rails=[('+3V3',('A1','38')), ('+3V3_A',('A1','21')), ('DSY_VIN',('A1','39'))],
   signal=['TAC_SW1','TAC_SW2','TOG_SW3_A','TOG_SW3_B','TOG_SW4','LED_R','LED_G','LED_B','LED_MONO_1',
           'GPIO_GATEIN_1','GPIO_GATEIN_2','/Daisy/CV_1_ADC','/Daisy/CV_2_ADC','/Daisy/CV_3_ADC','/Daisy/CV_4_ADC',
           '/Daisy/DAC_CV_1','/Daisy/DAC_CV_2','/Daisy/POT_MUX','/Daisy/MUX_CTRL_A','/Daisy/MUX_CTRL_B','/Daisy/MUX_CTRL_C',
           'POT_1','POT_8','MIDI_RX','MIDI_TX','MIDI_IN_4','MIDI_IN_5','Net-(D3-K)',
           '/Daisy/USB_OTG_HS_N','/Daisy/USB_OTG_HS_P','/Daisy/USB_IN_N','/Daisy/USB_IN_P','Net-(J7-CC1)','Net-(J7-CC2)',
           'SDMMC_CK','SDMMC_CMD','SDMMC_D0','SDMMC_D1','SDMMC_D2','SDMMC_D3',
           '/Daisy/CODEC_IN_L','/Daisy/CODEC_IN_R','/Daisy/CODEC_OUT_L','/Daisy/CODEC_OUT_R',
           'Net-(J_CV_IN_1-PadTIP)','Net-(J_GATE_IN_1-PadTIP)','Net-(Q1-B)','Net-(Q1-C)','Net-(LED1-RA)','Net-(LED2-A)'],
   series=['FB2','FB3','D1','D2','R5','R9','C39','C44','C46','C49','C50','C51','P1','A1','U3'],
   leds=['LED1','LED2']),
 'pedal': dict(
   power=['Net-(C20-Pad1)','Net-(FB10-Pad2)','Net-(FB4-Pad2)','Net-(D5-A)','Net-(D5-K)','+9V','Net-(C14-Pad1)','+9V_A',
          'Net-(C41-Pad1)','DSY_VIN','Net-(U2-ON{slash}~{OFF})','+5V','+5V_A','+3V3','+3V3_A','/Daisy/+5V_USB','Net-(U1A-+)'],
   checks=[('A1','39','DSY_VIN','Seed VIN'), ('A1','38','+3V3','Seed 3V3_D out'), ('A1','21','+3V3_A','Seed 3V3_A out'),
           ('U7','4','+3V3','microSD VDD'), ('U11','6','+3V3','H11L1 Vcc'),
           ('U3','8','+9V_A','OPA1652 U3 V+ (in L)'), ('U9','8','+9V_A','OPA1652 U9 V+ (in R)'), ('U10','8','+9V_A','OPA1652 U10 V+ (out)'),
           ('U2','1','Net-(U2-ON{slash}~{OFF})','LP2985 VIN'), ('U2','5','+5V','LP2985 VOUT'), ('U2','4','Net-(U2-BP)','LP2985 BP'),
           ('U1','8','+5V_A','MCP6002 VDD'), ('U1','3','Net-(U1A-+)','MCP6002 bias ref'),
           ('R6','2','DSY_VIN','R6 -> DSY_VIN'), ('D5','2','Net-(D5-A)','D5 anode node'), ('J8','2','Net-(C20-Pad1)','barrel jack +'),
           ('U14','5','/Daisy/+5V_USB','USBLC6 VBUS')],
   seed_rails=[('+3V3',('A1','38')), ('+3V3_A',('A1','21')), ('DSY_VIN',('A1','39')), ('+9V_A',('R55','2')), ('+5V',('U2','5'))],
   signal=['TAC_SW4','TAC_SW5','TOG_SW1_A','TOG_SW1_B','TOG_SW2','TOG_SW3','GPIO_FSW_1','GPIO_FSW_2',
           'LED_R','LED_G','LED_B','LED_MONO_1','POT_1','POT_2','POT_3','POT_4','POT_5','POT_6','ADC_EXPRESSION','EXPRESSION_IN_EXT',
           'MIDI_RX','MIDI_TX','MIDI_IN_4','MIDI_IN_5','Net-(R4-Pad2)',
           '/Daisy/USB_OTG_HS_N','/Daisy/USB_OTG_HS_P','/Daisy/USB_IN_N','/Daisy/USB_IN_P','Net-(J7-CC1)','Net-(J7-CC2)',
           'SDMMC_CK','SDMMC_CMD','SDMMC_D0','SDMMC_D1','SDMMC_D2','SDMMC_D3','SDMMC_DETECT',
           'CODEC_IN_L','CODEC_IN_R','CODEC_OUT_L','CODEC_OUT_R','AUDIO_IN_LEFT','AUDIO_OUT_LEFT',
           'Net-(LED1-A)','Net-(LED2-RA)','Net-(LED2-GA)','Net-(LED2-BA)'],
   series=['J8','FB10','FB4','FB5','D5','FB9','R30','R6','R48','R55','R57','FB1','U2','C20','C21','C13','C14','C41','C36','C23','C24','C27','C43','C15','C18','C19','A1'],
   leds=['LED1','LED2']),
}

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
    if layer not in p['layers'] and not (len(p['layers']) > 2): return False
    sx, sy = p['size']; sx /= 2; sy /= 2
    dx, dy = abs(pt[0]-p['pos'][0]), abs(pt[1]-p['pos'][1])
    return (dx <= sx+TOL and dy <= sy+TOL) or (dx <= sy+TOL and dy <= sx+TOL)

def net_graph(net, pads, tr, vi):
    g = defaultdict(list)
    def add(a, b, w): g[a].append((b, w)); g[b].append((a, w))
    pts = defaultdict(list)
    def pt_node(layer, xy):
        for n, q in pts[layer]:
            if d(q, xy) <= TOL: return n
        n = ('pt', layer, round(xy[0], 3), round(xy[1], 3)); pts[layer].append((n, xy)); return n
    for t in tr[net]:
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
        if not hit:
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

def main(path, kit):
    cfg = CFG[kit]
    dd = json.load(open(path)); pads, tr, vi = build(dd)
    bb = dd['bbox']
    print(f"Board bbox {bb} mm = {bb[2]-bb[0]:.1f} x {bb[3]-bb[1]:.1f}; copper layers {dd['copper_layers']}; {len(dd['footprints'])} footprints, {len(dd['tracks'])} tracks, {len(dd['vias'])} vias")
    for z in dd['zones']: print('  zone', z['net'], z['layers'], z['filled_area_mm2'], 'mm2', 'keepout' if z['is_keepout'] else '')
    print('\n=== A. RAIL COPPER ===')
    print('net | total_mm | by layer/width (mm@w) | min_w | vias | IPC2221 A@minw dT10 | R_total@actual(mOhm) | pads')
    for n in cfg['power']:
        ts = tr.get(n, [])
        byw = defaultdict(float)
        for t in ts: byw[(t['layer'], round(t['w'], 4))] += t['len']
        tot = sum(byw.values()); minw = min([w for _, w in byw] or [0])
        r = sum(rtrace(L, w) for (_, w), L in byw.items())*1000
        plist = ','.join(f"{p['ref']}.{p['num']}" for p in pads[n])
        print(f"{n} | {tot:.1f} | " + ', '.join(f'{L:.1f}@{w}({l})' for (l, w), L in sorted(byw.items())) +
              f" | {minw} | {len(vi.get(n, []))} | {ipc(minw) if minw else 0:.2f} | {r:.0f} | {plist}")

    print('\n=== B. POWER PIN -> NEAREST SAME-NET CAP (straight line) and routed path ===')
    for ref, num, net, what in cfg['checks']:
        try:
            g = net_graph(net, pads, tr, vi); i = find_pad(pads, net, ref, num); p = pads[net][i]
        except KeyError as e:
            print(f"{ref}.{num} {what} [{net}]: PAD NOT FOUND {e}"); continue
        caps = [(j, q) for j, q in enumerate(pads[net]) if q['ref'].startswith('C') and q['ref'][1:2].isdigit()]
        if not caps: print(f"{ref}.{num} {what} [{net}] ({p['fp_layer']}): NO CAPACITOR ON NET"); continue
        rows = []
        for j, q in caps:
            L, nv = shortest(g, ('pad', i), ('pad', j))
            rows.append((d(p['pos'], q['pos']), q, L, nv))
        rows.sort(key=lambda r: r[0])
        s = '; '.join(f"{q['ref']} {q['value']} straight {sl:.2f} mm, routed {L if L is None else round(L,2)} mm/{nv} via" for sl, q, L, nv in rows)
        print(f"{ref}.{num} {what} [{net}] ({p['fp_layer']}): {s}")

    print('\n=== C. ROUTED PATH FROM SOURCE PIN TO EACH LOAD ===')
    for net, src in cfg['seed_rails']:
        g = net_graph(net, pads, tr, vi); i = find_pad(pads, net, *src)
        for j, q in enumerate(pads[net]):
            if j == i: continue
            L, nv = shortest(g, ('pad', i), ('pad', j))
            print(f"{net}: {src[0]}.{src[1]} -> {q['ref']}.{q['num']} ({q['value']}, {q['fp_layer']}): straight {d(pads[net][i]['pos'], q['pos']):.1f} mm, routed {L if L is None else round(L,1)} mm, {nv} vias")

    print('\n=== D. SIGNAL NETS pad-to-pad ===')
    print('net | nodes | total copper mm | min w | vias | pad->pad routed (from first A1 pad or first pad)')
    for n in cfg['signal']:
        ts = tr.get(n, []); ws = [t['w'] for t in ts]
        g = net_graph(n, pads, tr, vi)
        ps = pads[n]
        if not ps: print(f"{n} | (no pads)"); continue
        src = next((k for k, p in enumerate(ps) if p['ref'] == 'A1'), 0)
        paths = []
        for k, p in enumerate(ps):
            if k == src: continue
            L, nv = shortest(g, ('pad', src), ('pad', k))
            paths.append(f"{ps[src]['ref']}.{ps[src]['num']}->{p['ref']}.{p['num']} {L if L is None else round(L,1)}mm/{nv}v")
        print(f"{n} | {','.join(p['ref']+'.'+p['num'] for p in ps)} | {sum(t['len'] for t in ts):.1f} | {min(ws) if ws else '-'} | {len(vi.get(n, []))} | " + '; '.join(paths))

    print('\n=== E. SERIES ELEMENTS / BULK CAPS / LED PADS ===')
    fps = {f['ref']: f for f in dd['footprints']}
    for r in cfg['series']:
        f = fps.get(r)
        if not f: print(r, 'NOT ON BOARD'); continue
        print(f"{r} {f['value']} {f['fpid']} {f['layer']} at {f['pos']} rot {f['rot']} pads " + ', '.join(f"{p['num']}:{p['net']}" for p in f['pads'][:6]))
    for r in cfg['leds']:
        f = fps.get(r)
        if f: print(r, f['fpid'], f['layer'], f['pos'], [(p['num'], p['net'], p['drill']) for p in f['pads']])
    print('\nVia drills:', sorted({v['drill'] for v in dd['vias']}), 'via dias:', sorted({v['dia'] for v in dd['vias']}))
    print('Track widths used:', sorted({round(t['w'],4) for t in dd['tracks']}))

if __name__ == '__main__': main(sys.argv[1], sys.argv[2])
