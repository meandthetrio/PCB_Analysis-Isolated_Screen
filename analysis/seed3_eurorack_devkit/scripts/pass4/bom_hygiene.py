#!/usr/bin/env python3
"""Raw-cell hygiene scan of a CDN-format procurement BOM (and, optionally, a KiCad production BOM):
BOM marker, trailing/double spaces, non-ASCII, designator ordering, CPN-vs-Description tolerance conflicts,
Package vocabulary, CPN/MPN/VPN/MFG anomalies, value-case splits in the production BOM.
Usage: python3 -I bom_hygiene.py CDN.csv [PROD.csv]"""
import sys, csv, re, collections
raw = open(sys.argv[1], 'rb').read()
print(f'{sys.argv[1].split("/")[-1]}: {len(raw)} bytes; UTF-8 BOM marker: {raw.startswith(b"\xef\xbb\xbf")}; CRLF lines: {raw.count(b"\r\n")}; LF-only lines: {raw.count(b"\n") - raw.count(b"\r\n")}')
rows = list(csv.DictReader(open(sys.argv[1], newline='', encoding='utf-8-sig')))
def natkey(r):
    m = re.match(r'([A-Za-z_]+)(\d*)', r); return (m.group(1), int(m.group(2) or 0), r)
for i, r in enumerate(rows, start=2):
    notes = []
    for k, v in r.items():
        if v != v.strip(): notes.append(f'{k} has leading/trailing whitespace {v!r}')
        if '  ' in v: notes.append(f'{k} has double space {v!r}')
        if any(ord(ch) > 127 for ch in v): notes.append(f'{k} non-ASCII: {"".join(sorted(set(ch for ch in v if ord(ch) > 127)))}')
    refs = r['Designators'].split()
    if refs != sorted(refs, key=natkey): notes.append(f'designators not in natural order: {" ".join(refs)} (string-sorted: {refs == sorted(refs)})')
    if r['Vendor'] == 'LCSC' and not re.match(r'^C\d+$', r['VPN']): notes.append(f'Vendor=LCSC but VPN={r["VPN"]!r}')
    if r['Vendor'] not in ('LCSC', 'JLCPCB') and r['VPN'] == r['MPN'] and r['MPN']: notes.append(f'VPN == MPN ({r["Vendor"]}): no vendor SKU')
    if not r['VPN']: notes.append('empty VPN')
    if not r['Vendor']: notes.append('empty Vendor')
    if 'Unknown' in r['MFG']: notes.append(f'MFG={r["MFG"]!r}')
    if 'Unknown' in r['Package']: notes.append(f'Package={r["Package"]!r}')
    tolc = re.findall(r'(\d+)%', r['CPN']); told = re.findall(r'±(\d+)%', r['Description'])
    if tolc and told and tolc[0] != told[0]: notes.append(f'tolerance CPN {tolc[0]}% vs Description ±{told[0]}%')
    if r['CPN'] and r['MPN'] and r['CPN'].upper() == r['MPN'].upper(): notes.append('CPN == MPN')
    if r['CPN'] and r['MPN'] and r['CPN'].split()[0].upper() not in r['MPN'].upper() and re.match(r'^[A-Z0-9-]+$', r['CPN'].split()[0]) and r['CPN'].split()[0] not in ('USB', 'FB', 'OPTO', 'DIN', 'MIDI', 'MINI', 'P-10K-B-R', '100UF', '10UF', '3R3', '2X5', '5MM', '9MM', 'LP2985-5V', 'MICRO'): notes.append(f'CPN names a different part than MPN: {r["CPN"]!r} vs {r["MPN"]!r}')
    if notes: print(f'  row {i} [{r["Designators"][:22]}]: ' + '; '.join(notes))
print('  Package vocabulary:', sorted(set(r['Package'] for r in rows)))
print('  MFG vocabulary:', sorted(set(r['MFG'] for r in rows)))
if len(sys.argv) > 2:
    prod = list(csv.DictReader(open(sys.argv[2], newline='', encoding='utf-8-sig')))
    print(f'{sys.argv[2].split("/")[-1]}: {len(prod)} lines; columns {list(prod[0].keys())}')
    byval = collections.defaultdict(list)
    for r in prod: byval[(r['Value'].upper(), r['Footprint'])].append((r['Value'], r['Reference']))
    for k, v in byval.items():
        if len(v) > 1: print(f'  value/footprint split across lines by case: {k[0]} {k[1].split(":")[-1]}: {v}')
    print('  empty Value cells:', [r['Reference'][:40] for r in prod if not r['Value']])
    print('  lines with 2+ footprints:', [(r['Value'], r['Footprint']) for r in prod if ',' in r['Footprint']])
    print('  line order (sort_field Value, asc):', [r['Value'] for r in prod][:12], '...')
