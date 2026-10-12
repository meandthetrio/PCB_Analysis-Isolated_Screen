"""ERC-equivalent for an Eagle schematic dumped by eagle_sch_full.py: nets with one pin, pins on no net (per part),
Seed (U1) pin usage, power-net sources, look-alike net names, parts with no package. Run: python3 -I erc_equiv.py sch_full.json"""
import sys, json, re, itertools
sch=json.load(open(sys.argv[1]))
nets=sch['nets']; parts=sch['parts']
print("== nets with a single pin:",[n for n,m in nets.items() if len(m)<2] or 'none')
padnet={}
for n,m in nets.items():
    for x in m: padnet[(x['part'],x['pad'])]=n
print("== pins on no net:")
for r,p in sorted(parts.items()):
    nc=[q['pin']+'/'+str(q['pad']) for q in p['pins'] if (r,q['pad']) not in padnet]
    if nc: print(f"  {r:<6} {p['package'] or '(no package)':<28} {nc}")
print("== Seed U1 pins:",sum(1 for q in parts['U1']['pins'] if ('U1',q['pad']) in padnet),"of",len(parts['U1']['pins']),"on a net")
dni=[r for r,p in parts.items() if 'DNI' in (p['value'] or '')]
print("   pins whose only other node is a DNI part:")
for q in sorted(parts['U1']['pins'],key=lambda q:int(q['pad'])):
    n=padnet.get(('U1',q['pad']))
    others={x['part'] for x in nets[n] if x['part']!='U1' and not parts[x['part']]['library'].endswith('Power')}
    if others and others<=set(dni): print(f"   pin {q['pad']:>2} {q['pin']:<20} net {n:<10} -> only {sorted(others)}")
print("== power nets and their members:")
for n in ('+3V3_A','+3V3_D','VIN','USB_VBUS','GND'):
    mem=[x['part']+'.'+x['pin'] for x in nets[n] if not parts[x['part']]['library'].endswith('Power') and x['part']!='GND']
    print(f"  {n:<9} {len(nets[n])} nodes: {mem if n!='GND' else str(len(mem))+' part pins'}")
print("== look-alike net names (case/underscore/sign-insensitive):")
norm=lambda s: re.sub(r'[\s_\-+]','',s).upper()
groups={}
for n in nets: groups.setdefault(norm(n),[]).append(n)
print("  ",[g for g in groups.values() if len(g)>1] or 'none')
pairs=[(a,b) for a,b in itertools.combinations(sorted(nets),2) if a!=b and (a.replace('_IN_','_')==b or a.rstrip('-+')==b.rstrip('-+'))]
print("   near-identical pairs:",pairs or 'none')
print("== symbol-only parts (no package):",sorted(r for r,p in parts.items() if not p['package']))
print("== packaged parts with no pads on a net:",[r for r,p in parts.items() if p['package'] and not any((r,q['pad']) in padnet for q in p['pins'])])
