#!/usr/bin/env python3
"""Make a KiCad-9-loadable COPY of a KiCad project whose files carry KiCad 10
library content (ProtoBuild1 is the case in point: KiCad 8 file headers with
KiCad 10 symbols/footprints inside; KiCad 9.0.9 refuses them with PARSE_ERROR).

Usage:  tools/kicad10_to_9.py SRC_PROJECT_DIR DST_DIR [BASENAME]

Never run this on the design files in place. The output is for ERC/DRC/
extraction in KiCad 9 only. What it changes (and nothing else):
  .kicad_sch : drops (in_pos_files ..) and (duplicate_pin_numbers_are_jumpers ..)
               from the embedded library symbols; replaces the embedded
               power:PWR_FLAG symbol with the KiCad 9 stock definition.
  .kicad_pcb : drops (duplicate_pad_numbers_are_jumpers ..) and the KiCad 10
               (point ...) fab-layer markers from footprints.
No copper, net, pad or footprint geometry is touched; verify with the
Gerber/netlist cross-checks in boards/*/analysis/scripts if in doubt.
"""
import os, re, shutil, subprocess, sys

def strip_token(s, tok):
    out, i = [], 0
    pat = re.compile(r'\(' + re.escape(tok) + r'[\s)]')
    while True:
        m = pat.search(s, i)
        if not m:
            out.append(s[i:]); break
        out.append(s[i:m.start()]); d = 0; j = m.start()
        while True:
            c = s[j]
            if c == '"':
                j += 1
                while s[j] != '"':
                    if s[j] == '\\': j += 1
                    j += 1
            elif c == '(': d += 1
            elif c == ')':
                d -= 1
                if d == 0: break
            j += 1
        i = j + 1
    return "".join(out)

def grab(s, i):
    d = 0; j = i
    while True:
        c = s[j]
        if c == '"':
            j += 1
            while s[j] != '"':
                if s[j] == '\\': j += 1
                j += 1
        elif c == '(': d += 1
        elif c == ')':
            d -= 1
            if d == 0: return s[i:j+1]
        j += 1

def stock_symbol(lib_path, name, prefix):
    lib = open(lib_path, encoding='utf-8').read()
    blk = grab(lib, lib.index(f'(symbol "{name}"\n'))
    return blk.replace(f'(symbol "{name}"', f'(symbol "{prefix}:{name}"', 1)

def convert_sch(src, dst):
    s = open(src, encoding='utf-8').read(); n0 = len(s)
    for tok in ('in_pos_files', 'duplicate_pin_numbers_are_jumpers'):
        s = strip_token(s, tok)
    if '(symbol "power:PWR_FLAG"' in s:
        old = grab(s, s.index('(symbol "power:PWR_FLAG"'))
        s = s.replace(old, stock_symbol('/usr/share/kicad/symbols/power.kicad_sym', 'PWR_FLAG', 'power'), 1)
    open(dst, 'w', encoding='utf-8').write(s)
    print(f"  sch: {os.path.basename(src)} -> {dst} ({n0} -> {len(s)} chars)")

def convert_pcb(src, dst):
    s = open(src, encoding='utf-8').read(); n0 = len(s)
    for tok in ('duplicate_pad_numbers_are_jumpers', 'point'):
        s = strip_token(s, tok)
    open(dst, 'w', encoding='utf-8').write(s)
    print(f"  pcb: {os.path.basename(src)} -> {dst} ({n0} -> {len(s)} chars)")

def main():
    if len(sys.argv) < 3:
        print(__doc__); sys.exit(2)
    src, dst = sys.argv[1], sys.argv[2]
    base = sys.argv[3] if len(sys.argv) > 3 else None
    os.makedirs(dst, exist_ok=True)
    for name in sorted(os.listdir(src)):
        p = os.path.join(src, name); q = os.path.join(dst, name)
        if base and not (name.startswith(base) or name.endswith('-lib-table') or name.endswith('.pretty') or name.endswith('.kicad_sym')):
            continue
        if name.endswith('.kicad_sch'): convert_sch(p, q)
        elif name.endswith('.kicad_pcb'):
            if 'kicad10-format' in name:
                print(f"  skip: {name} (native KiCad 10 file format, not readable by KiCad 9)"); continue
            convert_pcb(p, q)
        elif os.path.isdir(p): shutil.copytree(p, q, dirs_exist_ok=True)
        else: shutil.copy2(p, q)
    # smoke test
    for name in os.listdir(dst):
        q = os.path.join(dst, name)
        if name.endswith('.kicad_pcb'):
            r = subprocess.run(['kicad-cli', 'pcb', 'drc', '--format', 'json', '-o', os.path.join(dst, '_smoke_drc.json'), q], capture_output=True, text=True)
            print(f"  kicad-cli loads {name}: {'OK' if 'Failed' not in r.stdout + r.stderr else 'FAILED'}")
        if name.endswith('.kicad_sch'):
            r = subprocess.run(['kicad-cli', 'sch', 'erc', '--format', 'json', '-o', os.path.join(dst, '_smoke_erc.json'), q], capture_output=True, text=True)
            print(f"  kicad-cli loads {name}: {'OK' if 'Failed' not in r.stdout + r.stderr else 'FAILED'}")
    for f in ('_smoke_drc.json', '_smoke_erc.json'):
        if os.path.exists(os.path.join(dst, f)): os.remove(os.path.join(dst, f))

if __name__ == '__main__':
    main()
