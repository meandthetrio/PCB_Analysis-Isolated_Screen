#!/usr/bin/env python3
"""Schematic-vs-PCB consistency for the power/LED nets + duplicate refdes audit.

Usage: python3 -I sch_pcb_diff.py netlist.json board.json
netlist.json from netlist_parse.py --json ; board.json from board_dump.py.
Compares, for every pad, the net the PCB assigns vs the net the schematic
netlist assigns (by (ref,pin)); lists mismatches; lists duplicate references
in the PCB; prints the per-channel LED driver chain resolved against the Cree
CLD-CT1475 rev5 pin table (1 AB, 2 KB, 3 AR, 4 KR, 5 AG, 6 KG).
"""
import sys, json
from collections import Counter, defaultdict

CREE = {'1': 'BLUE anode', '2': 'BLUE cathode', '3': 'RED anode', '4': 'RED cathode', '5': 'GREEN anode', '6': 'GREEN cathode'}

def main(nl_path, bd_path):
    nl = json.load(open(nl_path)); bd = json.load(open(bd_path))
    sch = {}
    for net, members in nl['nets'].items():
        for ref, pin, *_ in members: sch[(ref, pin)] = net
    refs = Counter(f['ref'] for f in bd['footprints'])
    dups = {r: c for r, c in refs.items() if c > 1}
    print('PCB footprints:', len(bd['footprints']), ' schematic components:', len(nl['components']))
    print('Duplicate refdes in PCB:', dups if dups else 'NONE')
    only_pcb = sorted(set(refs) - set(nl['components'])); only_sch = sorted(set(nl['components']) - set(refs))
    print('Refs only in PCB:', only_pcb, ' only in schematic:', only_sch)
    mism = []; checked = 0
    for f in bd['footprints']:
        for p in f['pads']:
            if not p['num']: continue
            key = (f['ref'], p['num'])
            s = sch.get(key)
            pn = p['net'] or ''
            if s is None and pn == '': continue
            if s is None: s = ''
            if s.startswith('unconnected-'): s = ''
            checked += 1
            if s != pn: mism.append((f['ref'], p['num'], pn, s))
    print(f'Pads checked: {checked}; sch/pcb net mismatches: {len(mism)}')
    for m in mism: print('   MISMATCH', m)
    print('\nLED driver chains (schematic netlist; pad numbers resolved with Cree CLD-CT1475 rev5 pin table):')
    comps = nl['components']
    nets = nl['nets']
    bynet = defaultdict(list)
    for net, members in nets.items():
        for ref, pin, pf, pt in members: bynet[net].append((ref, pin, pf))
    for gpio_net in sorted(n for n in nets if n.startswith('/LED_')):
        a1 = [m for m in bynet[gpio_net] if m[0] == 'A1'][0]
        rb = [m for m in bynet[gpio_net] if m[0].startswith('R')][0]
        other_pin = '2' if rb[1] == '1' else '1'
        bnet = sch[(rb[0], other_pin)]
        q = [m for m in bynet[bnet] if m[0].startswith('Q')][0]
        cnet = sch[(q[0], '3')]
        led = [m for m in bynet[cnet] if m[0].startswith('LED')][0]
        # cathode side: same LED, pad num+1
        kpad = str(int(led[1]) + 1)
        knet = sch[(led[0], kpad)]
        rk = [m for m in bynet[knet] if m[0].startswith('R')][0]
        rk_other = '2' if rk[1] == '1' else '1'
        supply = sch[(rk[0], rk_other)]
        print(f"  {gpio_net:<9} A1.{a1[1]} ({a1[2]}) -> {rb[0]} {comps[rb[0]]['value']} -> {q[0]}.B ; {q[0]}.C -> {led[0]} pad {led[1]} [sym '{led[2]}' = Cree {CREE[led[1]]}] ; {led[0]} pad {kpad} [sym '{[m for m in bynet[knet] if m[0]==led[0]][0][2]}' = Cree {CREE[kpad]}] -> {rk[0]} {comps[rk[0]]['value']} -> {supply}")

if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
