#!/usr/bin/env python3
"""Pass 4 (Daisy Pod Rev5): three-way join BOM .xlsx <-> Eagle .sch parts <-> Eagle .brd elements,
plus the KiCad conversion (pcbnew) for pad/paste/SMD-THT facts and pos.csv.
Emits join.csv, bom_lines.csv, summary.txt and join_table.md in OUT_DIR.
Usage: python3 -I pod_join.py BOM.xlsx SCH.sch BRD.brd BOARD.kicad_pcb POS.csv OUT_DIR
"""
import sys, re, csv, json, os, collections
import xml.etree.ElementTree as ET
import openpyxl, pcbnew

bom_x, sch_x, brd_x, pcb_x, pos_x, out = sys.argv[1:7]
os.makedirs(out, exist_ok=True)

# ---------- BOM ----------
wb = openpyxl.load_workbook(bom_x)
ws = wb.worksheets[0]
rows = list(ws.iter_rows(values_only=True))
hdr = [str(h).strip() for h in rows[0]]
assert hdr == ['Qty', 'IPN', 'MPN', 'Manufacturer', 'Designators', 'Vendor Link'], hdr
bom_lines = []
bom_by_ref = {}
dup_refs = []
for i, r in enumerate(rows[1:], start=2):
    if all(v is None for v in r):
        continue
    qty, ipn, mpn, mfr, des, vend = r
    refs = re.split(r'[\s,;]+', str(des).strip())
    refs = [x for x in refs if x]
    line = dict(row=i, qty=int(qty), ipn=str(ipn).strip(), mpn=str(mpn).strip(), mfr=str(mfr).strip(),
                mfr_raw=str(mfr), refs=refs, vendor=str(vend).strip(), n_refs=len(refs),
                qty_ok=(int(qty) == len(refs)))
    bom_lines.append(line)
    for ref in refs:
        if ref in bom_by_ref:
            dup_refs.append(ref)
        bom_by_ref[ref] = line

# ---------- Eagle schematic ----------
sr = ET.parse(sch_x).getroot()
sch = {}
pkg_of = {}
tech_attrs = {}
for lib in sr.findall('.//libraries/library'):
    for ds in lib.findall('.//devicesets/deviceset'):
        for dev in ds.findall('.//devices/device'):
            pkg_of[(lib.get('name'), ds.get('name'), dev.get('name') or '')] = dev.get('package')
            for t in dev.findall('.//technologies/technology'):
                at = {a.get('name'): a.get('value') for a in t.findall('attribute')}
                if at:
                    tech_attrs[(lib.get('name'), ds.get('name'), dev.get('name') or '', t.get('name') or '')] = at
for p in sr.findall('.//parts/part'):
    key = (p.get('library'), p.get('deviceset'), p.get('device') or '')
    sch[p.get('name')] = dict(lib=p.get('library'), deviceset=p.get('deviceset'), device=p.get('device') or '',
                              tech=p.get('technology') or '', value=p.get('value'), package=pkg_of.get(key),
                              lib_attrs=tech_attrs.get(key + (p.get('technology') or '',), {}))
# schematic-only symbol classes: no package => power/frame symbols
def sch_class(name, d):
    if d['package'] is None:
        return 'schematic-only symbol (no package): ' + d['deviceset']
    return None

# ---------- Eagle board ----------
br = ET.parse(brd_x).getroot()
brd = {}
for e in br.findall('.//elements/element'):
    at = {a.get('name'): a.get('value') for a in e.findall('attribute') if a.get('value')}
    brd[e.get('name')] = dict(lib=e.get('library'), package=e.get('package'), value=e.get('value') or '',
                              x=float(e.get('x')), y=float(e.get('y')), rot=e.get('rot') or 'R0', attrs=at)

# ---------- KiCad conversion ----------
board = pcbnew.LoadBoard(pcb_x)
kfp = {}
for f in board.GetFootprints():
    pads = list(f.Pads())
    smd = [p for p in pads if p.GetAttribute() == pcbnew.PAD_ATTRIB_SMD]
    pth = [p for p in pads if p.GetAttribute() == pcbnew.PAD_ATTRIB_PTH]
    npth = [p for p in pads if p.GetAttribute() == pcbnew.PAD_ATTRIB_NPTH]
    fpaste = [p for p in pads if p.GetLayerSet().Contains(pcbnew.F_Paste)]
    bpaste = [p for p in pads if p.GetLayerSet().Contains(pcbnew.B_Paste)]
    smd_nopaste = [p.GetNumber() for p in smd if not (p.GetLayerSet().Contains(pcbnew.F_Paste) or p.GetLayerSet().Contains(pcbnew.B_Paste))]
    sizes = sorted({(round(pcbnew.ToMM(p.GetSize().x), 3), round(pcbnew.ToMM(p.GetSize().y), 3)) for p in smd + pth})
    if smd and not pth:
        tech = 'SMD'
    elif pth and not smd:
        tech = 'THT'
    elif smd and pth:
        tech = 'SMD+THT'
    else:
        tech = 'no-pads' if not npth else 'NPTH-only'
    kfp[f.GetReference()] = dict(fp=str(f.GetFPID().GetLibItemName()), side='top' if f.GetLayer() == pcbnew.F_Cu else 'bottom',
                                 n_pads=len(pads), n_smd=len(smd), n_pth=len(pth), n_npth=len(npth),
                                 f_paste=len(fpaste), b_paste=len(bpaste), smd_nopaste=smd_nopaste, tech=tech,
                                 sizes=sizes, value=f.GetValue())

# ---------- pos.csv ----------
pos = {}
with open(pos_x, newline='') as fh:
    for r in csv.DictReader(fh):
        pos[r['Ref']] = r

# ---------- value / package consistency (BOM IPN+MPN vs sch value vs eagle package vs kicad pads) ----------
def norm_val(v):
    v = (v or '').upper().replace('DNI', '').strip()
    return v

def pkg_class(pkg):
    """Map an Eagle package name to a chip-size class token or None."""
    m = re.search(r'([RCL])?0?(0402|0603|0805|1206|1210|2512)', pkg or '')
    return m.group(2) if m else None

def pad_class(sizes, pkg):
    """Classify chip pads by their size (measured in the KiCad conversion)."""
    if not sizes or len(sizes) != 1:
        return None
    w, h = sizes[0]
    a = sorted((w, h))
    # pad sizes seen on this board: 0402 -> 0.6x0.7 / 0.7x0.9 ; 0603 -> 1.0x1.1 / 1.1x1.0
    if a[1] <= 0.95:
        return '0402'
    if a[1] <= 1.3:
        return '0603'
    return 'other'

def value_check(ref, line, s):
    """Scripted check that the BOM IPN/MPN describes the schematic value and package."""
    ipn = line['ipn'].upper(); mpn = line['mpn'].upper(); sv = norm_val(s['value']); pk = (s['package'] or '').upper()
    notes = []
    if ref[0] in 'RC' and ref[1:].isdigit():
        # passives: value token must be in IPN, and IPN size code must match Eagle package size code
        tok = sv.split()[-1] if sv else ''
        if tok and tok not in ipn:
            return 'MISMATCH', f'sch {sv} not in IPN {line["ipn"]}'
        ipn_sz = pkg_class(ipn); pkg_sz = pkg_class(pk)
        if ipn_sz != pkg_sz:
            return 'MISMATCH', f'IPN size {ipn_sz} vs package {pk}'
        # MPN size code
        m = re.search(r'(0402|0603)', mpn)
        if m and m.group(1) != pkg_sz:
            return 'MISMATCH', f'MPN size {m.group(1)} vs package {pk}'
        return 'OK', ''
    # others: IPN should equal the schematic value (Electrosmith uses the IPN as Eagle value)
    if ipn == sv or ipn.replace(' ', '') == sv.replace(' ', ''):
        return 'OK', 'IPN==sch value'
    if mpn == sv:
        return 'OK', 'MPN==sch value'
    # looser: all IPN words in value or vice versa
    if sv and (sv in ipn or ipn in sv):
        return 'OK', 'substring'
    return 'CHECK', f'IPN "{line["ipn"]}" vs sch value "{s["value"]}"'

# ---------- the join ----------
allrefs = sorted(set(bom_by_ref) | set(sch) | set(brd), key=lambda r: (re.sub(r'\d+', '', r), int(re.search(r'\d+', r).group()) if re.search(r'\d+', r) else 0, r))
join = []
for ref in allrefs:
    inb, ins, inr = ref in bom_by_ref, ref in sch, ref in brd
    s = sch.get(ref, {}); b = brd.get(ref, {}); k = kfp.get(ref, {}); line = bom_by_ref.get(ref)
    if inb and ins and inr:
        disp = 'ALL THREE'
    elif inb and not ins and not inr:
        disp = 'BOM-only (phantom)'
    elif inb and (ins != inr):
        disp = 'BOM + one of sch/brd'
    elif ins and inr:
        if 'DNI' in (b.get('value', '') + ' ' + (s.get('value') or '')).upper():
            disp = 'SCH+BRD not BOM: DNI -> expected'
        elif k.get('tech') == 'SMD' and (k.get('f_paste') or k.get('b_paste')):
            disp = 'SCH+BRD not BOM: SMD with paste -> assembly gap'
        elif k.get('tech') in ('THT', 'SMD+THT'):
            disp = 'SCH+BRD not BOM: THT -> hand-solder/expected'
        elif k.get('n_pads', 0) == 0:
            disp = 'SCH+BRD not BOM: no pads (graphic)'
        elif k.get('n_pth', 0) == 1 and k.get('n_pads') == 1:
            disp = 'SCH+BRD not BOM: mounting hole -> expected'
        else:
            disp = 'SCH+BRD not BOM: pad-only (fiducial) -> expected'
    elif ins:
        disp = 'SCH-only: ' + (sch_class(ref, s) or 'placed part missing from board!')
    elif inr:
        disp = 'BRD-only: ' + ('graphic/logo (no pads)' if k.get('n_pads', 0) == 0 else 'placed part missing from schematic!')
    vchk, vnote = ('-', '')
    if inb and ins:
        vchk, vnote = value_check(ref, line, s)
    # Eagle package vs KiCad footprint name vs pad class
    pkg_chk = '-'
    if ins and inr:
        pkg_chk = 'OK' if s.get('package') == b.get('package') == k.get('fp') else f'sch {s.get("package")} / brd {b.get("package")} / kicad {k.get("fp")}'
        pc = pad_class(k.get('sizes'), b.get('package')); sz = pkg_class(b.get('package'))
        if sz and pc and pc != sz:
            pkg_chk += f' PAD-CLASS {pc} vs {sz}'
    join.append(dict(ref=ref, disposition=disp, bom_row=line['row'] if line else '', bom_ipn=line['ipn'] if line else '',
                     bom_mpn=line['mpn'] if line else '', bom_mfr=line['mfr'] if line else '',
                     sch_value=s.get('value') or '', sch_package=s.get('package', ''), sch_lib_mpn=(s.get('lib_attrs') or {}).get('MPN', ''),
                     brd_package=b.get('package', ''), brd_value=b.get('value', ''), brd_attr_mpn=(b.get('attrs') or {}).get('MPN', ''),
                     kicad_fp=k.get('fp', ''), side=k.get('side', ''), tech=k.get('tech', ''), n_pads=k.get('n_pads', ''),
                     f_paste=k.get('f_paste', ''), b_paste=k.get('b_paste', ''), smd_nopaste=' '.join(k.get('smd_nopaste', [])),
                     pad_sizes=' '.join(f'{w}x{h}' for w, h in k.get('sizes', [])), in_pos='Y' if ref in pos else '',
                     value_chk=vchk, value_note=vnote, pkg_chk=pkg_chk))

with open(os.path.join(out, 'join.csv'), 'w', newline='') as fh:
    w = csv.DictWriter(fh, fieldnames=list(join[0].keys())); w.writeheader(); w.writerows(join)
with open(os.path.join(out, 'bom_lines.csv'), 'w', newline='') as fh:
    w = csv.DictWriter(fh, fieldnames=['row', 'qty', 'n_refs', 'qty_ok', 'ipn', 'mpn', 'mfr', 'mfr_raw', 'vendor', 'refs'])
    w.writeheader()
    for l in bom_lines:
        w.writerow({**{k: l[k] for k in ['row', 'qty', 'n_refs', 'qty_ok', 'ipn', 'mpn', 'mfr', 'mfr_raw', 'vendor']}, 'refs': ' '.join(l['refs'])})

# ---------- summary ----------
S = []
P = S.append
P(f"BOM: {len(bom_lines)} lines, {sum(l['n_refs'] for l in bom_lines)} designators, qty sum {sum(l['qty'] for l in bom_lines)}; designators on >1 line: {dup_refs or 'none'}")
P(f"Qty != designator count: {[(l['row'], l['ipn'], l['qty'], l['n_refs']) for l in bom_lines if not l['qty_ok']] or 'none'}")
P(f"Manufacturer cells with odd whitespace/spelling: {[(l['row'], l['mfr_raw']) for l in bom_lines if l['mfr_raw'] != l['mfr_raw'].strip() or l['mfr'] in ('Chemi-Co',)]}")
P(f"Vendor column values: {collections.Counter(l['vendor'] for l in bom_lines)}")
P(f"Schematic: {len(sch)} parts ({sum(1 for d in sch.values() if d['package'])} with a package, {sum(1 for d in sch.values() if not d['package'])} schematic-only symbols)")
P(f"Board: {len(brd)} elements; KiCad conversion: {len(kfp)} footprints; pos.csv rows: {len(pos)}")
P(f"Board refs with duplicate names: {[r for r, c in collections.Counter(e.get('name') for e in br.findall('.//elements/element')).items() if c > 1] or 'none'}")
P("")
buckets = collections.defaultdict(list)
for j in join:
    buckets[j['disposition']].append(j['ref'])
for d in sorted(buckets):
    P(f"[{len(buckets[d]):2d}] {d}: {' '.join(buckets[d])}")
P("")
P("Value/package checks on ALL-THREE rows that are not OK:")
for j in join:
    if j['disposition'] == 'ALL THREE' and (j['value_chk'] != 'OK' or j['pkg_chk'] != 'OK'):
        P(f"  {j['ref']}: value={j['value_chk']} {j['value_note']} | pkg={j['pkg_chk']}")
P("")
P("Footprints with paste pads but no BOM line: " + (' '.join(f"{j['ref']}({j['side']},F{j['f_paste']}/B{j['b_paste']})" for j in join if not j['bom_row'] and (j['f_paste'] or j['b_paste'])) or 'none'))
P("BOM lines whose footprint has NO paste pads (hand/THT): " + (' '.join(f"{j['ref']}({j['tech']})" for j in join if j['bom_row'] and not (j['f_paste'] or j['b_paste'])) or 'none'))
P("SMD pads without a paste layer: " + (' '.join(f"{j['ref']}:{j['smd_nopaste']}" for j in join if j['smd_nopaste']) or 'none'))
P("DNI markers (value contains DNI) : " + (' '.join(f"{j['ref']}(brd '{j['brd_value']}', sch '{j['sch_value']}', BOM row {j['bom_row'] or '-'})" for j in join if 'DNI' in (j['brd_value'] + j['sch_value']).upper()) or 'none'))
P("Library-attribute MPN differs from BOM MPN: " + (' '.join(f"{j['ref']}(lib {j['brd_attr_mpn'] or j['sch_lib_mpn']} vs BOM {j['bom_mpn']})" for j in join if j['bom_row'] and (j['brd_attr_mpn'] or j['sch_lib_mpn']) and (j['brd_attr_mpn'] or j['sch_lib_mpn']).upper() != j['bom_mpn'].upper()) or 'none'))
P("pos.csv rows without a BOM line: " + (' '.join(r for r in sorted(pos) if r not in bom_by_ref) or 'none'))
P("BOM refs missing from pos.csv: " + (' '.join(r for r in sorted(bom_by_ref) if r not in pos) or 'none'))
open(os.path.join(out, 'summary.txt'), 'w').write('\n'.join(S) + '\n')
print('\n'.join(S))

# ---------- markdown join table ----------
md = ['| Ref | Disposition | BOM row: MPN (mfr) | Sch value | Eagle package (sch=brd) | KiCad fp / side / tech | Pads (SMD paste F/B) | pos | Value chk | Pkg chk |',
      '|---|---|---|---|---|---|---|---|---|---|']
for j in join:
    bomc = f"r{j['bom_row']}: {j['bom_mpn']} ({j['bom_mfr']})" if j['bom_row'] else ''
    pk = j['sch_package'] if j['pkg_chk'] in ('OK', '-') or 'PAD-CLASS' in j['pkg_chk'] else j['pkg_chk']
    md.append(f"| {j['ref']} | {j['disposition']} | {bomc} | {j['sch_value'] or ''} | {pk or ''} | {j['kicad_fp']} / {j['side']} / {j['tech']} | {j['n_pads']} ({j['f_paste']}/{j['b_paste']}) | {j['in_pos']} | {j['value_chk']}{(' ' + j['value_note']) if j['value_chk'] not in ('OK', '-') else ''} | {j['pkg_chk']} |")
open(os.path.join(out, 'join_table.md'), 'w').write('\n'.join(md) + '\n')
