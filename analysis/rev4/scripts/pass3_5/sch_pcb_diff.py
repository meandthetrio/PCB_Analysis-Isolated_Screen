"""Diff schematic netlist (netlist.json) against PCB pad connectivity (pcb_export.json).
Compares (ref,pin)->net for every pad; lists footprints/components only in one file; net membership diffs.
'unconnected-*' nets and empty PCB nets are both treated as 'no net'."""
import sys, json
from collections import defaultdict
nl=json.load(open(sys.argv[1])); pcb=json.load(open(sys.argv[2]))
def norm(n): return None if (not n or n.startswith('unconnected-')) else n
sch_pin={}
for net,nodes in nl['nets'].items():
    for ref,pin,fn,pt in nodes: sch_pin[(ref,pin)]=norm(net)
pcb_pin={}; pcb_fp={}
for fp in pcb['footprints']:
    pcb_fp[fp['ref']]=fp
    for p in fp['pads']:
        if p['type']=='NPTH' and not p['num']: continue
        key=(fp['ref'],p['num'])
        # multiple pads may share a number (e.g. TH + copies); keep first non-empty
        if key in pcb_pin and pcb_pin[key] is not None: continue
        pcb_pin[key]=norm(p['net'])
sch_refs=set(nl['comps']); pcb_refs=set(pcb_fp)
print("== components only in schematic:", sorted(sch_refs-pcb_refs))
print("== footprints only in PCB:", sorted(pcb_refs-sch_refs))
print("== value/footprint mismatches:")
for r in sorted(sch_refs&pcb_refs):
    c=nl['comps'][r]; f=pcb_fp[r]
    if c['value']!=f['value'] or c['fp']!=f['fpid']:
        print(f"   {r}: sch value={c['value']!r} fp={c['fp']!r} | pcb value={f['value']!r} fp={f['fpid']!r}")
# pad level diff
print("== pad-level net differences (ref,pin: sch -> pcb):")
diffs=0
allkeys=set(sch_pin)|{k for k in pcb_pin if k[0] in sch_refs}
for k in sorted(allkeys):
    s=sch_pin.get(k,'<no pin in sch>'); p=pcb_pin.get(k,'<no pad in pcb>')
    if s!=p:
        # mask pads with no number / NPTH
        diffs+=1; print(f"   {k}: {s} -> {p}")
print("   total differing pads:",diffs, "of", len(allkeys))
# net membership
sch_nets=defaultdict(set); pcb_nets=defaultdict(set)
for k,v in sch_pin.items():
    if v: sch_nets[v].add(k)
for k,v in pcb_pin.items():
    if v: pcb_nets[v].add(k)
print("== nets only in schematic:", sorted(set(sch_nets)-set(pcb_nets)))
print("== nets only in PCB:", sorted(set(pcb_nets)-set(sch_nets)))
print("== PCB nets with only one pad:", [(n,sorted(v)) for n,v in pcb_nets.items() if len(v)==1])
print("== PCB nets with pads but zero tracks and zero zone:", [n for n,v in pcb_nets.items() if pcb['nets'].get(n,{}).get('segments',0)==0 and n!='GND'])
print("== schematic nets with 2 nodes or fewer:")
for n,v in sorted(sch_nets.items()):
    if len(v)<=2: print("   ",n,sorted(v))
# tables of interest
def net_members(n): return sorted(sch_nets.get(n,set()))
print("\n== A1 (Daisy) pin -> net (schematic) ==")
for pin in sorted((k for k in sch_pin if k[0]=='A1'), key=lambda k:int(k[1])):
    fn=[x[2] for x in nl['nets'][next(nn for nn,nodes in nl['nets'].items() if any(r=='A1' and p==pin[1] for r,p,_,_ in nodes))] if x[0]=='A1' and x[1]==pin[1]][0]
    net=sch_pin[pin]
    others=[f"{r}.{p}" for r,p in (sch_nets.get(net,set()) - {pin})] if net else []
    print(f"  A1.{pin[1]:>2} {fn:<12} {str(net):<24} {' '.join(sorted(others))}")
print("\n== J8 (OLED) pin -> net ==")
for pin in sorted((k for k in sch_pin if k[0]=='J8'), key=lambda k:int(k[1])):
    net=sch_pin[pin]; others=[f"{r}.{p}" for r,p in (sch_nets.get(net,set())-{pin})] if net else []
    print(f"  J8.{pin[1]:>2} {str(net):<24} pcb={str(pcb_pin.get(pin)):<24} {' '.join(sorted(others))}")
for ref in ['Headphones1','ENCL1','ENCR1','Q1','Q2','Q3','Q4','Q5','Q6','U3','J7','J5','J4','P1','U6','L1','R29','R30','R31','R32','FB5','FB6','FB7','D6','R33','R35','R36','R37','R38','R39','R40','LED1','LED2','R4','R1','SW1','J1','FB2','FB3','FB4','U4']:
    print(f"\n== {ref} ({nl['comps'].get(ref,{}).get('value')}) ==")
    for pin in sorted((k for k in sch_pin if k[0]==ref), key=lambda k:(len(k[1]),k[1])):
        net=sch_pin[pin]; others=[f"{r}.{p}" for r,p in (sch_nets.get(net,set())-{pin})] if net else []
        print(f"  {ref}.{pin[1]:>3} {str(net):<26} {' '.join(sorted(others))}")
