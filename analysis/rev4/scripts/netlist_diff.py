"""Diff two kicad XML netlists: components (ref/value/footprint) and nets (membership)."""
import sys, xml.etree.ElementTree as ET
def load(p):
    r = ET.parse(p).getroot()
    comps = {c.get('ref'): (c.findtext('value'), c.findtext('footprint') or '') for c in r.find('components')}
    nets = {}
    for n in r.find('nets'):
        nodes = frozenset(f"{nd.get('ref')}.{nd.get('pin')}" for nd in n)
        nets[n.get('name')] = nodes
    return comps, nets
a, b = sys.argv[1], sys.argv[2]
ca, na = load(a); cb, nb = load(b)
print(f"components: {a}: {len(ca)}  {b}: {len(cb)}")
print("  removed:", sorted(set(ca) - set(cb)))
print("  added:  ", [(r, cb[r][0], cb[r][1].split(':')[-1]) for r in sorted(set(cb) - set(ca), key=lambda s: (''.join(c for c in s if not c.isdigit()), int(''.join(c for c in s if c.isdigit()) or 0)))])
print("  changed value/footprint:")
for r in sorted(set(ca) & set(cb)):
    if ca[r] != cb[r]: print(f"    {r:8s} {ca[r][0]} [{ca[r][1].split(':')[-1]}]  ->  {cb[r][0]} [{cb[r][1].split(':')[-1]}]")
print(f"\nnets: {len(na)} -> {len(nb)}")
# match nets by membership overlap to detect renames
print("  nets only in A (removed):", sorted(set(na) - set(nb)))
print("  nets only in B (added):  ", sorted(set(nb) - set(na)))
print("  nets with changed membership (same name):")
for n in sorted(set(na) & set(nb)):
    if na[n] != nb[n]:
        print(f"    {n}: -{sorted(na[n]-nb[n])} +{sorted(nb[n]-na[n])}")
print("\n  full membership of added nets:")
for n in sorted(set(nb) - set(na)): print(f"    {n}: {sorted(nb[n])}")
print("\n  full membership of removed nets:")
for n in sorted(set(na) - set(nb)): print(f"    {n}: {sorted(na[n])}")
