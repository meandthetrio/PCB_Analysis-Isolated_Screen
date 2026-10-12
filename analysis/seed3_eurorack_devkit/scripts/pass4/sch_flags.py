#!/usr/bin/env python3
"""Known-answer check for the netlist flags: parse the raw .kicad_sch sheet files (s-expression), list every placed
symbol instance (not lib_symbols) with its Reference, in_bom/on_board/dnp flags, and compare the set of
exclude_from_bom / dnp refs with what kicad-cli's netlist XML reports.
Usage: python3 -I sch_flags.py NETLIST.xml SHEET.kicad_sch [SHEET2.kicad_sch ...]"""
import sys, re
import xml.etree.ElementTree as ET

def tokenize(s):
    return re.findall(r'\(|\)|"(?:[^"\\]|\\.)*"|[^\s()"]+', s)
def parse(toks):
    stack = [[]]
    for t in toks:
        if t == '(': stack.append([])
        elif t == ')': x = stack.pop(); stack[-1].append(x)
        else: stack[-1].append(t[1:-1].replace('\\"', '"') if t.startswith('"') else t)
    return stack[0]
inst = {}
for path in sys.argv[2:]:
    tree = parse(tokenize(open(path, encoding='utf-8').read()))
    root = tree[0]
    for node in root:
        if isinstance(node, list) and node and node[0] == 'symbol':   # placed instance (lib_symbols is a separate node)
            d = dict(in_bom='yes', on_board='yes', dnp='no', ref=None, value=None, fp=None, file=path.split('/')[-1])
            for sub in node:
                if isinstance(sub, list) and sub:
                    if sub[0] in ('in_bom', 'on_board', 'dnp'): d[sub[0]] = sub[1]
                    if sub[0] == 'property' and len(sub) > 2:
                        if sub[1] == 'Reference': d['ref'] = sub[2]
                        if sub[1] == 'Value': d['value'] = sub[2]
                        if sub[1] == 'Footprint': d['fp'] = sub[2]
            inst.setdefault(d['ref'], []).append(d)
refs = {r for r in inst if r and not r.startswith('#')}
power = {r for r in inst if r and r.startswith('#')}
print(f'placed symbol instances: {sum(len(v) for v in inst.values())}; distinct non-power refs: {len(refs)}; power/flag symbols (#…): {len(power)}')
multi = {r: len(v) for r, v in inst.items() if r in refs and len(v) > 1}
print('refs with >1 instance (multi-unit or duplicates):', multi or 'none')
ex = sorted(r for r in refs if any(d['in_bom'] == 'no' for d in inst[r]))
ob = sorted(r for r in refs if any(d['on_board'] == 'no' for d in inst[r]))
dnp = sorted(r for r in refs if any(d['dnp'] == 'yes' for d in inst[r]))
print('sch in_bom=no:', ex); print('sch on_board=no:', ob); print('sch dnp=yes:', dnp)
nl = ET.parse(sys.argv[1]).getroot()
nrefs = set(); nex = set(); ndnp = set(); nob = set()
for c in nl.find('components'):
    nrefs.add(c.get('ref'))
    props = {p.get('name') for p in c.findall('property')}
    if 'exclude_from_bom' in props: nex.add(c.get('ref'))
    if 'dnp' in props: ndnp.add(c.get('ref'))
    if 'exclude_from_board' in props: nob.add(c.get('ref'))
print(f'netlist comps: {len(nrefs)}; sch refs not in netlist: {sorted(refs - nrefs)}; netlist refs not in sch: {sorted(nrefs - refs)}')
print('exclude_from_bom agree:', set(ex) == nex, '| dnp agree:', set(dnp) == ndnp, '| exclude_from_board agree:', set(ob) == nob)
unann = sorted(r for r in refs if r.endswith('?'))
print('unannotated refs:', unann or 'none')
