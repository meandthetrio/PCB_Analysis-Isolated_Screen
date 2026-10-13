#!/usr/bin/env python3
"""Parse placed symbol instances (not lib_symbols) from a .kicad_sch.
Emits one row per symbol instance: ref, unit, lib_id, value, footprint, in_bom, on_board, dnp, uuid.
Usage: python3 -I sch_symbols.py FILE.kicad_sch > out.csv
"""
import sys, csv, re

def tokenize(s):
    tok = re.compile(r'"(?:[^"\\]|\\.)*"|\(|\)|[^\s()"]+')
    for m in tok.finditer(s):
        t = m.group(0)
        if t.startswith('"'):
            yield ('str', bytes(t[1:-1], 'utf-8').decode('unicode_escape', errors='replace'))
        else:
            yield ('atom', t)

def parse(tokens):
    stack = [[]]
    for kind, t in tokens:
        if kind == 'atom' and t == '(':
            stack.append([])
        elif kind == 'atom' and t == ')':
            node = stack.pop()
            stack[-1].append(node)
        else:
            stack[-1].append(t)
    return stack[0]

def prop(node, name):
    for c in node:
        if isinstance(c, list) and c and c[0] == 'property' and len(c) > 2 and c[1] == name:
            return c[2]
    return None

def kv(node, key):
    for c in node:
        if isinstance(c, list) and c and c[0] == key and len(c) > 1:
            return c[1]
    return None

def main():
    src = open(sys.argv[1], encoding='utf-8').read()
    tree = parse(tokenize(src))
    root = tree[0]
    assert root[0] == 'kicad_sch'
    w = csv.writer(sys.stdout)
    w.writerow(['ref', 'unit', 'lib_id', 'value', 'footprint', 'in_bom', 'on_board', 'dnp', 'uuid'])
    for node in root:
        if isinstance(node, list) and node and node[0] == 'symbol':
            # top-level placed symbol instance (lib_symbols is a separate container)
            w.writerow([prop(node, 'Reference'), kv(node, 'unit'), kv(node, 'lib_id'),
                        prop(node, 'Value'), prop(node, 'Footprint'),
                        kv(node, 'in_bom'), kv(node, 'on_board'), kv(node, 'dnp'), kv(node, 'uuid')])

main()
