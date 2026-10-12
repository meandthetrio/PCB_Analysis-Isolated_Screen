#!/usr/bin/env python3
"""Pass 4 (Seed3 dev kits): three-way join of the production BOM (KiCad jobset CSV export) <-> schematic
symbols (kicad-cli netlist XML, with exclude_from_bom / dnp / exclude_from_board properties) <-> board
footprints (pcbnew), plus the CDN procurement BOM (MPN/VPN/Assembly/DNP columns), pos.csv and the
production centroid.  Emits join.csv, bom_lines.csv, summary.txt, join_table.md in OUT_DIR.

Usage: python3 -I kit_join.py --tag EU --bom PROD_bom.csv --cdn CDN_bom.csv --netlist netlist.xml \
          --pcb board.kicad_pcb --pos pos.csv --centroid centroid.csv --out OUT_DIR
"""
import sys, re, csv, os, argparse, collections
import xml.etree.ElementTree as ET
import pcbnew

ap = argparse.ArgumentParser()
for a in ('--tag', '--bom', '--cdn', '--netlist', '--pcb', '--pos', '--centroid', '--out'):
    ap.add_argument(a, required=(a != '--cdn'))
A = ap.parse_args()
os.makedirs(A.out, exist_ok=True)

def split_refs(s):
    return [x for x in re.split(r'[\s,;]+', s.strip()) if x]

# ---------- production BOM (KiCad sch_export_bom CSV: Value,Reference,Footprint[,Qty][,AVL_Part_Number]) ----------
bom = []; bom_by_ref = {}; bom_dup = []
with open(A.bom, newline='', encoding='utf-8-sig') as f:
    rd = csv.DictReader(f)
    bom_hdr = rd.fieldnames
    for i, r in enumerate(rd, start=2):
        refs = split_refs(r['Reference'])
        line = dict(row=i, value=r['Value'].strip(), refs=refs, footprint=r['Footprint'].strip(),
                    qty=r.get('Qty', '').strip(), avl=r.get('AVL_Part_Number', '').strip(), n_refs=len(refs))
        line['qty_ok'] = (line['qty'] == '' or line['qty'] == str(len(refs)))
        line['multi_fp'] = (',' in line['footprint'])
        bom.append(line)
        for ref in refs:
            if ref in bom_by_ref: bom_dup.append(ref)
            bom_by_ref[ref] = line

# ---------- CDN procurement BOM (Designators,Qty,Value,Description,Package,CPN,MPN,MFG,VPN,Vendor,Sub OK,DNP,Assembly) ----------
cdn = []; cdn_by_ref = {}; cdn_dup = []
if A.cdn:
    with open(A.cdn, newline='', encoding='utf-8-sig') as f:
        rd = csv.DictReader(f)
        cdn_hdr = rd.fieldnames
        for i, r in enumerate(rd, start=2):
            refs = split_refs(r['Designators'])
            line = {k: (v or '').strip() for k, v in r.items()}
            line.update(row=i, refs=refs, n_refs=len(refs), qty_ok=(r['Qty'].strip() == str(len(refs))))
            cdn.append(line)
            for ref in refs:
                if ref in cdn_by_ref: cdn_dup.append(ref)
                cdn_by_ref[ref] = line

# ---------- schematic (netlist XML) ----------
sch = {}
root = ET.parse(A.netlist).getroot()
for c in root.find('components'):
    ref = c.get('ref')
    props = {p.get('name'): (p.get('value') if p.get('value') is not None else True) for p in c.findall('property')}
    fields = {fl.get('name'): (fl.text or '') for fl in c.findall('fields/field')}
    ls = c.find('libsource')
    sch[ref] = dict(value=(c.findtext('value') or ''), footprint=(c.findtext('footprint') or ''),
                    lib=ls.get('lib') if ls is not None else '', part=ls.get('part') if ls is not None else '',
                    ex_bom='exclude_from_bom' in props, dnp='dnp' in props, ex_board='exclude_from_board' in props,
                    sheet=props.get('Sheetname', ''), fields=fields,
                    npins=len(c.findall('.//pin')))

# ---------- board (pcbnew) ----------
board = pcbnew.LoadBoard(A.pcb)
pcb = {}; pcb_dup = []
def pad_class(w, h):
    """size class of a 2-terminal chip pad (mm), KiCad stock patterns"""
    a, b = sorted((round(w, 2), round(h, 2)))
    if (a, b) in ((0.6, 0.7), (0.7, 0.9), (0.56, 0.62)): return '0402'
    if 0.78 <= a <= 1.0 and 0.9 <= b <= 1.15: return '0603'
    if 1.0 <= a <= 1.3 and 1.3 <= b <= 1.55: return '0805'
    if 1.0 <= a <= 1.3 and 1.7 <= b <= 1.9: return '1206'
    if 1.3 <= a <= 1.5 and 2.5 <= b <= 2.7: return '1210'
    if 1.35 <= a <= 1.45 and 3.2 <= b <= 3.4: return '2512'
    return f'{a}x{b}'
for fp in board.GetFootprints():
    ref = fp.GetReference()
    if ref in pcb: pcb_dup.append(ref)
    pads = list(fp.Pads())
    pth = [p for p in pads if p.GetAttribute() == pcbnew.PAD_ATTRIB_PTH]
    smd = [p for p in pads if p.GetAttribute() == pcbnew.PAD_ATTRIB_SMD]
    npth = [p for p in pads if p.GetAttribute() == pcbnew.PAD_ATTRIB_NPTH]
    fpaste = sum(1 for p in pads if p.GetLayerSet().Contains(pcbnew.F_Paste))
    bpaste = sum(1 for p in pads if p.GetLayerSet().Contains(pcbnew.B_Paste))
    a = fp.GetAttributes()
    tech = 'THT' if pth else ('SMD' if smd else ('NPTH-only' if npth else 'no-pads'))
    geom = ''
    if len(smd) == 2 and not pth:
        s = smd[0].GetSize(); geom = pad_class(pcbnew.ToMM(s.x), pcbnew.ToMM(s.y))
    elif pth:
        d = collections.Counter(round(pcbnew.ToMM(p.GetDrillSize().x), 2) for p in pth)
        geom = 'PTH drill ' + '/'.join(f'{k}' for k in sorted(d))
    pcb[ref] = dict(value=fp.GetValue(), fpid=fp.GetFPIDAsString(), side='top' if fp.GetLayer() == pcbnew.F_Cu else 'bottom',
                    npads=len(pads), npth=len(pth), nsmd=len(smd), nnpth=len(npth), fpaste=fpaste, bpaste=bpaste,
                    tech=tech, geom=geom,
                    attr_smd=bool(a & pcbnew.FP_SMD), attr_tht=bool(a & pcbnew.FP_THROUGH_HOLE),
                    ex_bom=bool(a & pcbnew.FP_EXCLUDE_FROM_BOM), ex_pos=bool(a & pcbnew.FP_EXCLUDE_FROM_POS_FILES),
                    dnp=bool(a & pcbnew.FP_DNP),
                    x=round(pcbnew.ToMM(fp.GetPosition().x), 3), y=round(pcbnew.ToMM(fp.GetPosition().y), 3))

# ---------- pos.csv (kicad-cli, this session) and production centroid ----------
pos = {}
with open(A.pos, newline='', encoding='utf-8-sig') as f:
    for r in csv.DictReader(f): pos[r['Ref']] = r
cen = {}
with open(A.centroid, newline='', encoding='utf-8-sig') as f:
    cen_rd = csv.DictReader(f); cen_hdr = cen_rd.fieldnames
    for r in cen_rd: cen[r['Designator']] = r

# ---------- value / package helpers ----------
def norm_val(v):
    v = v.strip().upper().replace('Ω', 'R').replace('OHM', 'R').replace(' ', '')
    v = re.sub(r'^(\d+)R(\d+)$', r'\1R\2', v)
    return v
def val_token(v):
    """canonical R/C value: 100K -> 100K, 100k -> 100K, 10uF -> 10UF, 3R3 -> 3R3, 5K1 -> 5K1"""
    return norm_val(v)
SIZE_RE = re.compile(r'(0402|0603|0805|1206|1210|2512)')
def pkg_tokens(s):
    s = s.upper()
    t = set(SIZE_RE.findall(s))
    for k, pat in (('SOT-23-6', r'SOT-23-6'), ('SOT-23-5', r'SOT-23-5'), ('SOT-23', r'SOT-?23(?![-\d])'), ('SOD-323', r'SOD-?323'),
                   ('SOIC-8', r'(SO-?8|SOIC-?8)'), ('SOIC-14', r'(SO-?14|SOIC-?14)'), ('SOIC-16', r'(SO-?16|SOIC-?16)'),
                   ('DIP-6', r'DIP-?6'), ('6.3x7.7', r'6\.3X7\.7|D8\b'), ('4x5.8', r'4X5\.8'), ('USB-C', r'USB ?C|USB4110|TYPE-C'),
                   ('SD', r'SD'), ('5MM LED', r'5MM|D5\.0'), ('POT', r'POT'), ('TOGGLE', r'TOGGLE'), ('JACK', r'JACK'),
                   ('TACT', r'TAC|TL1105'), ('DIN', r'DIN|57PC5F'), ('BARREL', r'BARREL'), ('FOOTSW', r'FOOTSW|S02P'), ('HEADER', r'HEADER'),
                   ('SOM', r'SOM|SEED')):
        if re.search(pat, s): t.add(k)
    return t

# ---------- join ----------
rows = []
all_refs = sorted(set(bom_by_ref) | set(sch) | set(pcb) | set(cdn_by_ref) | set(pos) | set(cen),
                  key=lambda r: (re.match(r'[A-Za-z_]+', r).group(0), int(re.search(r'(\d+)', r).group(1)) if re.search(r'\d', r) else 0, r))
buckets = collections.defaultdict(list)
for ref in all_refs:
    b = bom_by_ref.get(ref); c = cdn_by_ref.get(ref); s = sch.get(ref); p = pcb.get(ref)
    in_b, in_s, in_p = b is not None, s is not None, p is not None
    if in_b and in_s and in_p: disp = 'ALL THREE'
    elif in_b and not in_s and not in_p: disp = 'BOM-only (phantom)'
    elif in_b and in_s and not in_p: disp = 'BOM+SCH not PCB'
    elif in_b and in_p and not in_s: disp = 'BOM+PCB not SCH'
    elif in_s and in_p:
        if s['ex_bom'] or p['ex_bom']:
            why = 'exclude-from-BOM flag'
        elif s['dnp'] or p['dnp']:
            why = 'DNP'
        elif p['tech'] == 'SMD' and (p['fpaste'] or p['bpaste']):
            why = 'SMD with paste -> GAP'
        elif p['tech'] == 'THT':
            why = 'THT -> hand/expected'
        else:
            why = 'pad-only/no-pads'
        disp = f'SCH+PCB not BOM: {why}'
    elif in_p: disp = 'PCB-only'
    elif in_s: disp = 'SCH-only'
    else: disp = 'CDN/pos/centroid-only'
    buckets[disp.split(':')[0] if not disp.startswith('SCH+PCB') else disp].append(ref)

    # checks
    vchk = pchk = cchk = '-'
    if in_b and in_s and in_p:
        sv, pv, bv = val_token(s['value']), val_token(p['value']), val_token(b['value'])
        if sv == pv == bv: vchk = 'OK'
        elif sv == pv == '~' and bv == '': vchk = 'OK (no value: sch/pcb "~", BOM empty)'
        else: vchk = f'MISMATCH sch={s["value"]} pcb={p["value"]} bom={b["value"]}'
        fps = {s['footprint'], p['fpid']} | set(x.strip() for x in b['footprint'].split(','))
        pchk = 'OK' if len({s['footprint'], p['fpid']}) == 1 and p['fpid'] in b['footprint'] else f'MISMATCH sch={s["footprint"]} pcb={p["fpid"]} bom={b["footprint"]}'
        if b['multi_fp']: pchk += ' (BOM line lists 2 footprints)'
    if c is not None and in_p:
        notes = []
        if c['Value'] and in_s and val_token(c['Value']) != val_token(s['value']):
            if val_token(c['Value']) in val_token(s['value']).replace('-', ''): notes.append(f'value cdn={c["Value"]} within sch={s["value"]} (reviewed OK)')
            else: notes.append(f'value cdn={c["Value"]} sch={s["value"]}')
        ct = pkg_tokens(c['Package'] + ' ' + c['CPN']); pt = pkg_tokens(p['fpid'] + ' ' + p['geom'])
        if ct & pt: pass
        elif ct and pt: notes.append(f'package cdn="{c["Package"]}"/{c["CPN"]} vs pcb {p["fpid"]} [{p["geom"]}]')
        asm = c['Assembly']
        if (asm == 'SMT' and p['tech'] != 'SMD') or (asm == 'PTH' and p['tech'] != 'THT'): notes.append(f'assembly={asm} but pcb tech={p["tech"]}')
        if c['DNP'].upper() == 'TRUE' and not (in_s and s['dnp']): notes.append('CDN DNP=TRUE but sch not DNP')
        if c['DNP'].upper() != 'TRUE' and in_s and s['dnp']: notes.append('sch DNP but CDN DNP=FALSE')
        cchk = 'OK' if not notes else '; '.join(notes)
    elif c is not None and not in_p:
        cchk = 'CDN ref not on board'
    rows.append(dict(ref=ref, disp=disp,
                     bom_row=b['row'] if b else '', bom_value=b['value'] if b else '', bom_fp=b['footprint'] if b else '', bom_avl=b['avl'] if b else '',
                     cdn_row=c['row'] if c else '', cdn_value=c['Value'] if c else '', cdn_pkg=c['Package'] if c else '', cdn_cpn=c['CPN'] if c else '',
                     cdn_mpn=c['MPN'] if c else '', cdn_mfg=c['MFG'] if c else '', cdn_vpn=c['VPN'] if c else '', cdn_vendor=c['Vendor'] if c else '',
                     cdn_dnp=c['DNP'] if c else '', cdn_asm=c['Assembly'] if c else '',
                     sch_value=s['value'] if s else '', sch_fp=s['footprint'] if s else '', sch_lib=f"{s['lib']}:{s['part']}" if s else '',
                     sch_ex_bom=s['ex_bom'] if s else '', sch_dnp=s['dnp'] if s else '', sch_ex_board=s['ex_board'] if s else '', sch_sheet=s['sheet'] if s else '',
                     pcb_value=p['value'] if p else '', pcb_fp=p['fpid'] if p else '', pcb_side=p['side'] if p else '', pcb_tech=p['tech'] if p else '',
                     pcb_pads=p['npads'] if p else '', pcb_pth=p['npth'] if p else '', pcb_smd=p['nsmd'] if p else '', pcb_fpaste=p['fpaste'] if p else '', pcb_bpaste=p['bpaste'] if p else '',
                     pcb_geom=p['geom'] if p else '', pcb_attr=('SMD' if p and p['attr_smd'] else 'THT' if p and p['attr_tht'] else 'unspec') if p else '',
                     pcb_ex_bom=p['ex_bom'] if p else '', pcb_ex_pos=p['ex_pos'] if p else '', pcb_dnp=p['dnp'] if p else '',
                     in_pos='Y' if ref in pos else '', in_centroid='Y' if ref in cen else '',
                     value_chk=vchk, pkg_chk=pchk, cdn_chk=cchk))

with open(os.path.join(A.out, 'join.csv'), 'w', newline='') as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)

# ---------- bom_lines.csv ----------
with open(os.path.join(A.out, 'bom_lines.csv'), 'w', newline='') as f:
    w = csv.writer(f); w.writerow(['source', 'row', 'value', 'footprint/package', 'qty', 'n_refs', 'qty_ok', 'refs', 'extra'])
    for l in bom: w.writerow(['production', l['row'], l['value'], l['footprint'], l['qty'], l['n_refs'], l['qty_ok'], ' '.join(l['refs']), l['avl']])
    for l in cdn: w.writerow(['cdn', l['row'], l['Value'], l['Package'], l['Qty'], l['n_refs'], l['qty_ok'], ' '.join(l['refs']), f"{l['CPN']} | {l['MPN']} | {l['MFG']} | {l['VPN']} | {l['Vendor']} | sub={l['Sub OK']} dnp={l['DNP']} asm={l['Assembly']}"])

# ---------- summary ----------
out = []
P = out.append
P(f'== {A.tag}: production BOM {os.path.basename(A.bom)}: {len(bom)} lines, {len(bom_by_ref)} designators, header {bom_hdr}')
P(f'   designators on two lines: {bom_dup or "none"}; Qty != n_refs: {[ (l["row"], l["qty"], l["n_refs"]) for l in bom if not l["qty_ok"]] or "none"}; lines with 2 footprints: {[(l["row"], l["value"], l["footprint"]) for l in bom if l["multi_fp"]] or "none"}')
if A.cdn:
    P(f'== CDN BOM {os.path.basename(A.cdn)}: {len(cdn)} lines, {len(cdn_by_ref)} designators, header {cdn_hdr}')
    P(f'   designators on two lines: {cdn_dup or "none"}; Qty != n_refs: {[(l["row"], l["Qty"], l["n_refs"]) for l in cdn if not l["qty_ok"]] or "none"}')
    P(f'   DNP column values: {dict(collections.Counter(l["DNP"] for l in cdn))}; Assembly: {dict(collections.Counter(l["Assembly"] for l in cdn))}; Vendor: {dict(collections.Counter(l["Vendor"] for l in cdn))}; Sub OK: {dict(collections.Counter(l["Sub OK"] for l in cdn))}')
    P(f'   VPN not an LCSC C-number while Vendor=LCSC: {[(l["row"], l["VPN"]) for l in cdn if l["Vendor"] == "LCSC" and not re.match(r"^C\d+$", l["VPN"])] or "none"}')
    P(f'   empty Value cells: {sum(1 for l in cdn if not l["Value"])}; empty Description: {sum(1 for l in cdn if not l["Description"])}; "Unknown Manufacturer": {[l["row"] for l in cdn if "Unknown" in l["MFG"]]}; MFG with trailing space: {[l["row"] for l in cdn if l["MFG"] != l["MFG"].strip() or (l.get("MFG","").endswith(" "))]}')
    P(f'   designators in CDN but not production BOM: {sorted(set(cdn_by_ref) - set(bom_by_ref)) or "none"}')
    P(f'   designators in production BOM but not CDN: {sorted(set(bom_by_ref) - set(cdn_by_ref)) or "none"}')
    diffs = []
    for ref in sorted(set(cdn_by_ref) & set(bom_by_ref)):
        cv, bv = cdn_by_ref[ref]['Value'], bom_by_ref[ref]['value']
        if cv and val_token(cv) != val_token(bv) and val_token(cv) not in val_token(bv).replace('-', ''): diffs.append(f'{ref}: cdn {cv} vs prod {bv}')
    P(f'   value differs between CDN and production BOM: {diffs or "none"}')
    P(f'   CDN Package/Assembly/DNP checks not OK (cdn_chk column): {[(r["ref"], r["cdn_chk"]) for r in rows if r["cdn_chk"] not in ("OK", "-")] or "none"}')
P(f'== schematic (netlist): {len(sch)} components; exclude_from_bom: {sorted(r for r in sch if sch[r]["ex_bom"])}; dnp: {sorted(r for r in sch if sch[r]["dnp"])}; exclude_from_board: {sorted(r for r in sch if sch[r]["ex_board"])}')
P(f'   sheets: {dict(collections.Counter(s["sheet"] for s in sch.values()))}')
P(f'   symbols with empty Footprint field: {sorted(r for r in sch if not sch[r]["footprint"]) or "none"}')
P(f'== board (pcbnew): {len(pcb)} footprints; duplicate refs: {pcb_dup or "none"}; tech: {dict(collections.Counter(p["tech"] for p in pcb.values()))}; sides: {dict(collections.Counter(p["side"] for p in pcb.values()))}')
P(f'   footprint attribute vs pad type: {dict(collections.Counter((("SMD" if p["attr_smd"] else "THT" if p["attr_tht"] else "unspec"), p["tech"]) for p in pcb.values()))}')
P(f'   unspec-attribute footprints: {sorted(r for r, p in pcb.items() if not p["attr_smd"] and not p["attr_tht"])}')
P(f'   exclude_from_bom: {sorted(r for r, p in pcb.items() if p["ex_bom"])}; exclude_from_pos: {sorted(r for r, p in pcb.items() if p["ex_pos"])}; DNP: {sorted(r for r, p in pcb.items() if p["dnp"])}')
P(f'   sch ex_bom vs pcb ex_bom disagree: {sorted(r for r in set(sch) & set(pcb) if sch[r]["ex_bom"] != pcb[r]["ex_bom"]) or "none"}')
P(f'== pos.csv (kicad-cli, session): {len(pos)} rows; production centroid: {len(cen)} rows, header {cen_hdr}')
P(f'   pos refs not in centroid: {sorted(set(pos) - set(cen)) or "none"}; centroid refs not in pos: {sorted(set(cen) - set(pos)) or "none"}')
P(f'   centroid rows with no production-BOM line: {sorted(r for r in cen if r not in bom_by_ref) or "none"}')
P(f'   production-BOM designators missing from centroid: {sorted(r for r in bom_by_ref if r not in cen) or "none"}')
P(f'   centroid Layer values: {dict(collections.Counter(r["Layer"] for r in cen.values()))}')
# centroid vs pcb consistency (value/package/side/xy offset)
offs = collections.Counter()
for r, c in cen.items():
    if r in pcb:
        p = pcb[r]
        if c['Val'] != p['value'] or c['Package'] != p['fpid'].split(':')[-1]: P(f'   centroid val/package differs from pcb: {r} {c["Val"]}/{c["Package"]} vs {p["value"]}/{p["fpid"]}')
        if c['Layer'] != p['side']: P(f'   centroid side differs: {r}')
        offs[(round(float(c['Mid X']) - p['x'], 3), round(float(c['Mid Y']) + p['y'], 3))] += 1
P(f'   centroid-vs-pcb XY offset (Mid X - pcb x, Mid Y + pcb y): {offs.most_common(3)} (constant => same drill/place origin for all)')
P('== buckets')
for k in sorted(buckets): P(f'   {k} ({len(buckets[k])}): {" ".join(buckets[k])}')
P(f'== value checks not OK: {[(r["ref"], r["value_chk"]) for r in rows if r["value_chk"] not in ("OK", "-")] or "none"}')
P(f'== package checks not OK: {[(r["ref"], r["pkg_chk"]) for r in rows if r["pkg_chk"] not in ("OK", "-")] or "none"}')
P(f'== paste pads but no production-BOM line: {[(r["ref"], r["pcb_fpaste"], r["pcb_bpaste"]) for r in rows if r["pcb_fp"] and (r["pcb_fpaste"] or r["pcb_bpaste"]) and not r["bom_row"]] or "none"}')
P(f'== production-BOM lines whose parts have no paste pads (THT / hand): {sorted(set(r["ref"] for r in rows if r["bom_row"] and r["pcb_fp"] and not (r["pcb_fpaste"] or r["pcb_bpaste"]))) or "none"}')
P(f'== THT parts on production BOM: {sorted(r["ref"] for r in rows if r["bom_row"] and r["pcb_tech"] == "THT")}')
P(f'== SMD parts on production BOM: {len([r for r in rows if r["bom_row"] and r["pcb_tech"] == "SMD"])}')
P(f'== pad-geometry class per BOM footprint: {dict(collections.Counter((r["pcb_fp"].split(":")[-1], r["pcb_geom"]) for r in rows if r["bom_row"] and r["pcb_geom"] and r["pcb_tech"] == "SMD"))}')
P(f'== A1 (Seed module): ' + str({k: rows[[r["ref"] for r in rows].index("A1")][k] for k in ("disp", "bom_value", "bom_fp", "cdn_value", "cdn_pkg", "cdn_cpn", "cdn_mpn", "cdn_mfg", "cdn_asm", "sch_value", "sch_fp", "pcb_fp", "pcb_tech", "pcb_pads", "pcb_geom")}))
open(os.path.join(A.out, 'summary.txt'), 'w').write('\n'.join(out) + '\n')
print('\n'.join(out))

# ---------- join_table.md ----------
with open(os.path.join(A.out, 'join_table.md'), 'w') as f:
    f.write('| Ref | Disposition | Prod BOM row: value / footprint | CDN row: MPN (mfg) / VPN / asm | Sch value / footprint / flags | PCB fp / side / tech / pads (paste F/B) / geom | pos | centroid | Value chk | Pkg chk | CDN chk |\n|---|---|---|---|---|---|---|---|---|---|---|\n')
    for r in rows:
        flags = ','.join(k for k, v in (('exBOM', r['sch_ex_bom']), ('DNP', r['sch_dnp']), ('exBoard', r['sch_ex_board'])) if v is True)
        f.write(f"| {r['ref']} | {r['disp']} | {('r%s: %s / %s' % (r['bom_row'], r['bom_value'], r['bom_fp'].split(':')[-1])) if r['bom_row'] else ''} | "
                f"{('r%s: %s (%s) / %s / %s' % (r['cdn_row'], r['cdn_mpn'], r['cdn_mfg'], r['cdn_vpn'], r['cdn_asm'])) if r['cdn_row'] else ''} | "
                f"{(r['sch_value'] + ' / ' + r['sch_fp'].split(':')[-1] + (' / ' + flags if flags else '')) if r['sch_fp'] or r['sch_value'] else ''} | "
                f"{(r['pcb_fp'].split(':')[-1] + ' / ' + r['pcb_side'] + ' / ' + r['pcb_tech'] + ' / ' + str(r['pcb_pads']) + ' (' + str(r['pcb_fpaste']) + '/' + str(r['pcb_bpaste']) + ') / ' + r['pcb_geom']) if r['pcb_fp'] else ''} | "
                f"{r['in_pos']} | {r['in_centroid']} | {r['value_chk']} | {r['pkg_chk']} | {r['cdn_chk']} |\n")
