"""Inventory every placed symbol in a .kicad_sch: ref, value, footprint, lib_id, unit, dnp, in_bom,
and flag unannotated ones. Also lists lib_symbols (library definitions) separately so the two are not confused."""
import sys, json
import os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from sexp import parse, find_all, find1
doc = parse(open(sys.argv[1], encoding='utf-8').read())[0]
libsyms = find1(doc,'lib_symbols') or []
lib_defs=[]
for s in find_all(libsyms,'symbol'):
    props={p[1]:p[2] for p in find_all(s,'property')}
    lib_defs.append((s[1], props.get('Reference'), props.get('Value'), props.get('Footprint')))
placed=[]
for s in find_all(doc,'symbol'):
    lib_id=find1(s,'lib_id')[1]
    props={p[1]:p[2] for p in find_all(s,'property')}
    unit=find1(s,'unit',[None,None])[1]
    dnp=find1(s,'dnp',[None,'no'])[1]
    in_bom=find1(s,'in_bom',[None,'yes'])[1]
    at=find1(s,'at')
    uuid=find1(s,'uuid',[None,''])[1]
    placed.append(dict(ref=props.get('Reference'),value=props.get('Value'),fp=props.get('Footprint'),
                       lib_id=lib_id,unit=unit,dnp=dnp,in_bom=in_bom,at=at[1:3] if at else None,uuid=uuid))
out=sys.argv[2]
json.dump(dict(lib_defs=lib_defs,placed=placed),open(out,'w'),indent=1)
print(f"lib_symbols definitions: {len(lib_defs)}")
for d in lib_defs: print("  LIBDEF", d)
print(f"placed symbol instances: {len(placed)}")
unann=[p for p in placed if not p['ref'] or p['ref'].rstrip('?').rstrip('0123456789')==p['ref'] or p['ref'].endswith('?')]
print(f"unannotated placed instances (ref with no number or '?'): {len(unann)}")
for p in unann: print("  UNANN", p)
from collections import Counter
c=Counter(p['ref'] for p in placed)
print("placed refs with >1 instance (multi-unit or duplicates):")
for r,n in sorted(c.items()):
    if n>1: print("  ",r,n,[ (p['unit'],p['lib_id']) for p in placed if p['ref']==r])
print("power symbols:", sum(1 for p in placed if p['ref'] and p['ref'].startswith('#')))
print("DNP:",[p['ref'] for p in placed if p['dnp']=='yes'])
print("not in BOM (non-power):",[p['ref'] for p in placed if p['in_bom']=='no' and not p['ref'].startswith('#')])
