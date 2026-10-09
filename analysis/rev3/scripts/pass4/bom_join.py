#!/usr/bin/env python3
"""Three-way join: JLCPCB BOM (.xls) <-> schematic symbols (sch_symbols.csv) <-> PCB footprints (pcb_footprints.csv).
Usage: python3 -I bom_join.py BOM.xls sch_symbols.csv pcb_footprints.csv OUT_DIR
Writes OUT_DIR/join.csv, OUT_DIR/join.md (markdown tables), OUT_DIR/bom_lines.csv, OUT_DIR/summary.txt
"""
import sys, csv, re, os, collections
import xlrd

bom_path, sch_path, pcb_path, out = sys.argv[1:5]
os.makedirs(out, exist_ok=True)

# ---------- BOM ----------
wb = xlrd.open_workbook(bom_path)
sh = wb.sheet_by_index(0)
hdr = [str(sh.cell_value(0, c)).strip() for c in range(sh.ncols)]
ci = {h: i for i, h in enumerate(hdr)}
bom_lines = []
for r in range(1, sh.nrows):
    comment = str(sh.cell_value(r, ci['Comment']))
    desig_raw = sh.cell_value(r, ci['Designator'])
    fp_raw = sh.cell_value(r, ci['Footprint'])
    lcsc = str(sh.cell_value(r, ci['JLCPCB Part #'])).strip()
    if isinstance(fp_raw, float):
        fp = f"{int(fp_raw):04d}"           # Excel turned "0603" into 603.0
        fp_note = 'numeric-cell'
    else:
        fp = str(fp_raw).strip(); fp_note = ''
    if not str(desig_raw).strip():
        continue
    desigs = [d.strip() for d in str(desig_raw).split(',') if d.strip()]
    spacing_oddity = ', ' in str(desig_raw) or ' ,' in str(desig_raw) or str(desig_raw) != str(desig_raw).strip()
    moji = bool(re.search(r'‚ÑÉ|Œ©|¬±|„ÄÅ|_~\+|/_', comment))
    bom_lines.append(dict(row=r + 1, comment=comment, desig_raw=str(desig_raw), desigs=desigs,
                          fp=fp, fp_note=fp_note, lcsc=lcsc, spacing_oddity=spacing_oddity, moji=moji))

bom_by_ref = collections.defaultdict(list)
for ln in bom_lines:
    for d in ln['desigs']:
        bom_by_ref[d].append(ln)

# ---------- SCH ----------
sch = {}
sch_units = collections.Counter()
for row in csv.DictReader(open(sch_path, encoding='utf-8')):
    if row['lib_id'].startswith('power:'):
        continue
    sch_units[row['ref']] += 1
    sch.setdefault(row['ref'], row)

# ---------- PCB ----------
pcb = collections.defaultdict(list)
for row in csv.DictReader(open(pcb_path, encoding='utf-8')):
    pcb[row['ref']].append(row)

# ---------- value normalisation ----------
def norm_value(v):
    """Turn a KiCad value like '5K1', '300R', '100NF', '2.2UF' into tokens expected in a JLCPCB comment."""
    v = v.strip()
    m = re.fullmatch(r'(\d+)([RKM])(\d+)', v, re.I)          # 5K1 -> 5.1k
    if m:
        num = f"{m.group(1)}.{m.group(3)}"; unit = m.group(2).upper()
        return f"{num}{'' if unit == 'R' else unit.lower()}Ω"
    m = re.fullmatch(r'([\d.]+)\s*([RKM])', v, re.I)          # 300R, 47K, 0R, 3.3R
    if m:
        unit = m.group(2).upper()
        return f"{m.group(1)}{'' if unit == 'R' else unit.lower()}Ω"
    m = re.match(r'([\d.]+)\s*([NUP])F', v, re.I)             # 100NF, 2.2UF, 10UF
    if m:
        return f"{m.group(1)}{m.group(2).lower()}F"
    m = re.match(r'([\d.]+)\s*UH', v, re.I)                   # 2.2UH ...
    if m:
        return f"{m.group(1)}uH"
    return v

# MPN/description expectations for ICs & non-value parts (verified against LCSC pages in this pass or rev 2)
ic_expect = {
    'H11L1': 'Logic Output Optoisolators', 'USBLC6-2P6': 'SOT-666 ESD', 'TPA6110A2DGN': 'MSOP-8-EP Audio',
    'MAX9814': 'TDFN-14-EP(3x3) Audio', 'TPS62172DSG': 'WSON-8-EP(2x2) DC-DC', 'MMBT3904': 'NPN', 'D_Schottky': 'Schottky',
    'FerriteBead': 'Ferrite Beads', 'Micro_SD_Card_Det2': 'MicroSD', 'USB_C31-S-RA-CS2-SMT-BK-T/R': 'Type-C',
    'Barrel_Jack': 'DC Power Jack',
}

def value_check(ref, sch_val, comment):
    if sch_val in ic_expect:
        return ('OK' if ic_expect[sch_val].lower() in comment.lower() else 'MISMATCH', ic_expect[sch_val])
    tok = norm_value(sch_val)
    c = comment.replace('Œ©', 'Ω').replace('¬±', '±')
    # treat 'uF' vs 'uF', case-insensitive; Ω may be mojibake'd
    pat = r'(?<![\d.])' + re.escape(tok).replace('Ω', '(Ω|Œ©)') + r'(?![\d])'
    ok = re.search(pat, c, re.I) is not None
    return ('OK' if ok else 'MISMATCH', tok)

def fp_class(fpid):
    f = fpid.split(':')[-1]
    for k in ('0603', '0805', '1210', '2512', '2012', '3225', '6332', '1608'):
        if k in f:
            return {'1608': '0603', '2012': '0805', '3225': '1210', '6332': '2512'}.get(k, k)
    return f

def fp_check(bom_fp, sch_fp, pcb_fp):
    """Compare BOM footprint column with the sch/pcb footprint names. Returns (status, note)."""
    if sch_fp != pcb_fp:
        return ('SCH!=PCB', f"sch={sch_fp} pcb={pcb_fp}")
    cls = fp_class(pcb_fp)
    b = bom_fp
    if re.fullmatch(r'\d{4}', b):
        return ('OK' if b == cls else 'MISMATCH', f"bom {b} vs pcb {cls}")
    key = {'SOD-323': 'SOD-323', 'SOT-23': 'SOT-23', 'SOT-666': 'SOT-666', 'SOP-6-2.54mm': 'SOP-6',
           'MSOP-8-EP': 'HVSSOP-8-1EP', 'TDFN-14-EP(3x3)': 'DFN-14-1EP_3x3mm', 'WSON-8-EP(2x2)': 'WSON-8-1EP_2x2mm',
           'SMD,D6.3xL7.7mm': 'CP_Elec_6.3x7.7'}.get(b)
    if key:
        return ('OK' if key in pcb_fp else 'MISMATCH', f"bom {b} vs pcb {pcb_fp.split(':')[-1]}")
    if b == 'SMD':
        return ('OK(generic)', f"bom 'SMD' vs pcb {pcb_fp.split(':')[-1]}")
    return ('?', f"bom {b} vs pcb {pcb_fp.split(':')[-1]}")

# ---------- known-answer self-test of the value checker ----------
assert value_check('R4', '33R', '... 33Ω 500mW ...')[0] == 'OK'
assert value_check('R4', '33R', '... 330Ω 500mW ...')[0] == 'MISMATCH'
assert value_check('R4', '33R', '... 3.3Ω 500mW ...')[0] == 'MISMATCH'
assert value_check('R16', '5K1', '... 5.1kΩ ...')[0] == 'OK'
assert value_check('R16', '5K1', '... 51kΩ ...')[0] == 'MISMATCH'
assert value_check('C1', '100NF', '100nF 25V')[0] == 'OK'
assert value_check('C1', '100NF', '1000nF 25V')[0] == 'MISMATCH'
assert value_check('C6', '100UF', '100uF 2000hrs')[0] == 'OK'
assert value_check('R7', '47K', '47kŒ© 75V')[0] == 'OK'
assert value_check('R2', '0R', '0Œ© 100mW')[0] == 'OK'
assert value_check('R29', '3.3R', '1W 200V 3.3Ω')[0] == 'OK'
assert value_check('R29', '3.3R', '1W 200V 33Ω')[0] == 'MISMATCH'
assert value_check('L1', '2.2UH DFE201610P-2R2M=P2', '2.2uH 2A')[0] == 'OK'
assert value_check('U6', 'TPS62172DSG', 'WSON-8-EP(2x2) DC-DC Converters')[0] == 'OK'
assert value_check('U6', 'TPS62172DSG', 'SOT-23 LDO')[0] == 'MISMATCH'

# ---------- join ----------
all_refs = sorted(set(bom_by_ref) | set(sch) | set(pcb), key=lambda s: (re.sub(r'\d+$', '', s), int(re.search(r'(\d+)$', s).group(1)) if re.search(r'\d+$', s) else 0))
rows = []
for ref in all_refs:
    b = bom_by_ref.get(ref, []); s = sch.get(ref); p = pcb.get(ref, [])
    in_b, in_s, in_p = bool(b), s is not None, bool(p)
    if in_b and in_s and in_p: disp = 'ALL THREE'
    elif in_b and not in_s and not in_p: disp = 'BOM-ONLY (phantom)'
    elif in_s and in_p and not in_b:
        disp = 'SCH+PCB not BOM: ' + ('SMD -> assembly gap' if p[0]['attr'] == 'SMD' else 'THT -> hand-solder')
    elif in_p and not in_s: disp = 'PCB-ONLY' + (' (+BOM)' if in_b else '')
    elif in_s and not in_p: disp = 'SCH-ONLY' + (' (+BOM)' if in_b else '')
    else: disp = '?'
    vchk = fchk = ('', '')
    if in_b and in_s and in_p:
        vchk = value_check(ref, s['value'], b[0]['comment'])
        fchk = fp_check(b[0]['fp'], s['footprint'], p[0]['fpid'])
    elif in_s and in_p and s['footprint'] != p[0]['fpid']:
        fchk = ('SCH!=PCB', f"sch={s['footprint']} pcb={p[0]['fpid']}")
    elif in_s and in_p and s['value'] != p[0]['value']:
        vchk = ('SCH!=PCB value', f"sch={s['value']} pcb={p[0]['value']}")
    rows.append(dict(ref=ref, disposition=disp,
                     bom_lines=';'.join(f"row{x['row']}:{x['lcsc']}" for x in b), bom_fp=b[0]['fp'] if b else '',
                     bom_comment=(b[0]['comment'][:60] if b else ''),
                     sch_value=s['value'] if s else '', sch_fp=s['footprint'] if s else '',
                     pcb_value=p[0]['value'] if p else '', pcb_fp=p[0]['fpid'] if p else '',
                     pcb_side=p[0]['side'] if p else '', pcb_attr=p[0]['attr'] if p else '',
                     pcb_count=len(p), paste=('F' if p and int(p[0]['n_fpaste_pads']) else '') + ('B' if p and int(p[0]['n_bpaste_pads']) else ''),
                     value_check=vchk[0], value_note=vchk[1], fp_check=fchk[0], fp_note=fchk[1]))

with open(f"{out}/join.csv", 'w', newline='') as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
with open(f"{out}/bom_lines.csv", 'w', newline='') as f:
    w = csv.writer(f); w.writerow(['row', 'lcsc', 'fp', 'fp_note', 'designator_raw', 'n_desig', 'spacing_oddity', 'mojibake', 'comment'])
    for ln in bom_lines:
        w.writerow([ln['row'], ln['lcsc'], ln['fp'], ln['fp_note'], ln['desig_raw'], len(ln['desigs']), ln['spacing_oddity'], ln['moji'], ln['comment']])

# ---------- summary ----------
S = []
S.append(f"BOM: {len(bom_lines)} lines, {sum(len(l['desigs']) for l in bom_lines)} designators, {len(bom_by_ref)} unique")
S.append(f"SCH: {len(sch)} symbols (non-power); multi-unit refs: {[r for r, n in sch_units.items() if n > 1]}")
S.append(f"PCB: {sum(len(v) for v in pcb.values())} footprints, {len(pcb)} unique refs; duplicate refs: {[r for r, v in pcb.items() if len(v) > 1]}")
dup_bom = {r: [l['row'] for l in ls] for r, ls in bom_by_ref.items() if len(ls) > 1}
S.append(f"BOM designators appearing on >1 line: {dup_bom}")
S.append(f"BOM lines with spacing oddities in Designator: {[l['row'] for l in bom_lines if l['spacing_oddity']]}")
S.append(f"BOM lines with mojibake in Comment: {len([l for l in bom_lines if l['moji']])}/{len(bom_lines)} rows {[l['row'] for l in bom_lines if l['moji']]}")
S.append(f"BOM Footprint cells stored as numbers (0603->603.0 etc.): {[l['row'] for l in bom_lines if l['fp_note']]}")
S.append(f"BOM LCSC numbers used on >1 line: { {k: v for k, v in collections.Counter(l['lcsc'] for l in bom_lines).items() if v > 1} }")
S.append(f"BOM designators that are not valid-looking refs: {[d for d in bom_by_ref if not re.fullmatch(r'[A-Za-z_]+[0-9]+', d)]}")
S.append('')
disp_count = collections.Counter(r['disposition'] for r in rows)
for d, n in sorted(disp_count.items()):
    S.append(f"{n:4d}  {d}: " + ' '.join(r['ref'] for r in rows if r['disposition'] == d))
S.append('')
S.append("Value check != OK: " + ', '.join(f"{r['ref']}({r['value_check']}: {r['value_note']} | {r['bom_comment'][:40]})" for r in rows if r['value_check'] not in ('OK', '')))
S.append("Footprint check != OK: " + ', '.join(f"{r['ref']}({r['fp_check']}: {r['fp_note']})" for r in rows if r['fp_check'] not in ('OK', '', 'OK(generic)')))
S.append("Footprint check generic: " + ', '.join(f"{r['ref']}({r['fp_note']})" for r in rows if r['fp_check'] == 'OK(generic)'))
S.append("SCH value != PCB value: " + ', '.join(f"{r['ref']}(sch={r['sch_value']} pcb={r['pcb_value']})" for r in rows if r['sch_value'] and r['pcb_value'] and r['sch_value'] != r['pcb_value']))
S.append("SCH fp != PCB fp: " + ', '.join(f"{r['ref']}" for r in rows if r['sch_fp'] and r['pcb_fp'] and r['sch_fp'] != r['pcb_fp']))
S.append("Paste pads but no BOM line: " + ', '.join(f"{r['ref']}({r['paste']},{r['pcb_side']})" for r in rows if r['paste'] and not r['bom_lines']))
S.append("BOM line but no paste pads: " + ', '.join(f"{r['ref']}" for r in rows if r['bom_lines'] and r['pcb_count'] and not r['paste']))
S.append("PCB excl-from-BOM / excl-from-POS / DNP flags: " + ', '.join(f"{ref}:{'bom' if p[0]['excl_bom']=='True' else ''}{'/pos' if p[0]['excl_pos']=='True' else ''}{'/dnp' if p[0]['dnp']=='True' else ''}" for ref, p in sorted(pcb.items()) if 'True' in (p[0]['excl_bom'], p[0]['excl_pos'], p[0]['dnp'])))
open(f"{out}/summary.txt", 'w').write('\n'.join(S) + '\n')
print('\n'.join(S))

# ---------- markdown join table ----------
md = ["| Ref | Disposition | BOM line (row:LCSC) | BOM fp | Sch value | Sch footprint | PCB footprint | Side/Tech | Paste | Value chk | Fp chk |",
      "|---|---|---|---|---|---|---|---|---|---|---|"]
for r in rows:
    md.append(f"| {r['ref']} | {r['disposition']} | {r['bom_lines']} | {r['bom_fp']} | {r['sch_value']} | {r['sch_fp'].split(':')[-1]} | "
              f"{r['pcb_fp'].split(':')[-1]} | {r['pcb_side']}/{r['pcb_attr']} | {r['paste'] or '-'} | {r['value_check'] or '-'} | {r['fp_check'] or '-'}{(' ('+r['fp_note']+')') if r['fp_check'] not in ('OK','','OK(generic)') else ''} |")
open(f"{out}/join.md", 'w').write('\n'.join(md) + '\n')
