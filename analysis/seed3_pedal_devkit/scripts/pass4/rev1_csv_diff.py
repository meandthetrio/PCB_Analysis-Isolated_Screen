#!/usr/bin/env python3
"""Identify the stray `Seed3-Pedal-DevKit-Rev1.csv` (KiCad legacy bom_csv_grouped_by_value format, ';'-separated)
and diff its designators/values/footprints against a Rev3 join.csv.
Usage: python3 -I rev1_csv_diff.py REV1.csv JOIN.csv LABEL"""
import sys, csv, re, collections
rows = list(csv.reader(open(sys.argv[1], encoding='utf-8-sig'), delimiter=';'))
hdr = rows[0]; body = [r for r in rows[1:] if r and r[0].strip()]
r1 = {}
for r in body:
    for ref in re.split(r'[\s,]+', r[1].strip()):
        if ref: r1[ref] = dict(fp=r[2], value=r[4], line=r[0])
print(f'{sys.argv[1].split("/")[-1]}: header {hdr}; {len(body)} lines; {len(r1)} designators; qty==n_refs on all lines: {all(int(r[3]) == len(re.split(r"[\s,]+", r[1].strip())) for r in body)}')
j = {r['ref']: r for r in csv.DictReader(open(sys.argv[2]))}
j3 = {k: v for k, v in j.items() if v['pcb_fp']}
common = sorted(set(r1) & set(j3)); only1 = sorted(set(r1) - set(j3)); only3 = sorted(set(j3) - set(r1))
print(f'vs {sys.argv[3]} board ({len(j3)} footprints): common {len(common)}, Rev1-only {len(only1)}, Rev3-only {len(only3)}')
print('  Rev1-only:', ' '.join(f"{r}({r1[r]['value']})" for r in only1))
print('  Rev3-only:', ' '.join(f"{r}({j3[r]['pcb_value']})" for r in only3))
diff = [(r, r1[r]['value'], j3[r]['pcb_value'], r1[r]['fp'], j3[r]['pcb_fp'].split(':')[-1]) for r in common if r1[r]['value'].upper() != j3[r]['pcb_value'].upper() or r1[r]['fp'] != j3[r]['pcb_fp'].split(':')[-1]]
print(f'  common designators whose value or footprint differs ({len(diff)}):')
for d in diff: print('    ', d)
