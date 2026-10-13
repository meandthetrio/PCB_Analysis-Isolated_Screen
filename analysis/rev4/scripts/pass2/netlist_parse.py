#!/usr/bin/env python3
"""Parse a KiCad 9 .net (s-expression) netlist and dump components + nets.

Usage: python3 -I netlist_parse.py NETLIST.net [--nets REGEX] [--json OUT]
Emits a complete table of every net and its (ref, pin, pinfunction) members,
and a component table (ref, value, footprint). Pure stdlib.
"""
import sys, re, json, argparse

def tokenize(s):
    tok, i, n = [], 0, len(s)
    while i < n:
        c = s[i]
        if c.isspace(): i += 1; continue
        if c in '()': tok.append(c); i += 1; continue
        if c == '"':
            j = i + 1; buf = []
            while j < n:
                if s[j] == '\\' and j + 1 < n: buf.append(s[j+1]); j += 2; continue
                if s[j] == '"': break
                buf.append(s[j]); j += 1
            tok.append(('STR', ''.join(buf))); i = j + 1; continue
        j = i
        while j < n and not s[j].isspace() and s[j] not in '()': j += 1
        tok.append(('STR', s[i:j])); i = j
    return tok

def parse(tok):
    stack = [[]]
    for t in tok:
        if t == '(': stack.append([])
        elif t == ')':
            l = stack.pop(); stack[-1].append(l)
        else: stack[-1].append(t[1])
    return stack[0][0]

def find(node, key):
    return [c for c in node if isinstance(c, list) and c and c[0] == key]

def load(path):
    root = parse(tokenize(open(path, encoding='utf-8').read()))
    comps = {}
    for comp in find(find(root, 'components')[0], 'comp'):
        ref = find(comp, 'ref')[0][1]
        val = find(comp, 'value'); fp = find(comp, 'footprint')
        comps[ref] = {'value': val[0][1] if val else '', 'footprint': fp[0][1] if fp else ''}
    nets = {}
    for net in find(find(root, 'nets')[0], 'net'):
        name = find(net, 'name')[0][1]
        members = []
        for node in find(net, 'node'):
            ref = find(node, 'ref')[0][1]; pin = find(node, 'pin')[0][1]
            pf = find(node, 'pinfunction'); pt = find(node, 'pintype')
            members.append((ref, pin, pf[0][1] if pf else '', pt[0][1] if pt else ''))
        nets[name] = members
    return comps, nets

if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('netlist'); ap.add_argument('--nets', default=None)
    ap.add_argument('--json', default=None); ap.add_argument('--comps', action='store_true')
    a = ap.parse_args()
    comps, nets = load(a.netlist)
    if a.json:
        json.dump({'components': comps, 'nets': nets}, open(a.json, 'w'), indent=1)
    if a.comps:
        print('REF | VALUE | FOOTPRINT')
        for r in sorted(comps, key=lambda x: (re.sub(r'\d+', '', x), int(re.sub(r'\D', '', x) or 0))):
            print(f"{r} | {comps[r]['value']} | {comps[r]['footprint']}")
    rx = re.compile(a.nets) if a.nets else None
    for name in sorted(nets):
        if rx and not rx.search(name): continue
        print(f"\nNET {name} ({len(nets[name])} nodes)")
        for ref, pin, pf, pt in sorted(nets[name]):
            print(f"   {ref}.{pin:<4} {pf:<18} {pt:<14} [{comps.get(ref,{}).get('value','')}]")
