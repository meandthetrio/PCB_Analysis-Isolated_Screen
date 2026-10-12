"""Three-way netlist diff for the Daisy Pod: Eagle .sch (sch_full.json) vs Eagle .brd (brd_netlist.json) vs KiCad conversion
(pcb_export.json). Compares part sets, duplicate refs, and the (part,pad)->net partition pad by pad; reports net-name
differences separately from connectivity differences. Run: python3 -I sch_brd_diff.py sch_full.json brd_netlist.json pcb_export.json"""
import sys, json
from collections import Counter, defaultdict
sch=json.load(open(sys.argv[1])); brd=json.load(open(sys.argv[2])); pcb=json.load(open(sys.argv[3]))
# --- parts
sch_parts={r:p for r,p in sch['parts'].items()}
no_fp={r:p for r,p in sch_parts.items() if not p['package']}
sch_fp={r:p for r,p in sch_parts.items() if p['package']}
brd_el=brd['elements']; kic={fp['ref']:fp for fp in pcb['footprints']}
print("schematic parts:",len(sch_parts),"| with package:",len(sch_fp),"| symbol-only:",len(no_fp),sorted(no_fp))
print("brd elements:",len(brd_el),"| kicad footprints:",len(pcb['footprints']))
print("only in sch (with package):",sorted(set(sch_fp)-set(brd_el)))
print("only in brd:",sorted(set(brd_el)-set(sch_fp)))
print("only in kicad vs brd:",sorted(set(kic)-set(brd_el)),"| brd not in kicad:",sorted(set(brd_el)-set(kic)))
dups=[r for r,c in Counter(fp['ref'] for fp in pcb['footprints']).items() if c>1]
print("duplicate refs in kicad:",dups)
# value / package mismatch sch vs brd
for r in sorted(set(sch_fp)&set(brd_el)):
    s=sch_fp[r]; b=brd_el[r]
    if s['package']!=b['package'] or (s['value'] or '')!=(b['value'] or ''):
        print("  value/package mismatch",r,s['value'],s['package'],'|',b['value'],b['package'])
# --- pad -> net maps
sch_pn={}
for n,m in sch['nets'].items():
    for x in m:
        for pad in (x['pad'] or '').split():   # Eagle multi-pad connects: "2 9", "P1 P2 P3 P4", "GND1 GND4 GND6"
            sch_pn[(x['part'],pad)]=n
brd_pn={}
for n,s in brd['signals'].items():
    for el,pad in s['contacts']: brd_pn[(el,pad)]=n
kic_pn={}
for fp in pcb['footprints']:
    for p in fp['pads']:
        if p['net']: kic_pn[(fp['ref'],p['num'])]=p['net']
def compare(A,B,na,nb):
    print(f"\n== {na} ({len(A)} pad-nets) vs {nb} ({len(B)} pad-nets)")
    onlyA=sorted(set(A)-set(B)); onlyB=sorted(set(B)-set(A))
    print(f" pads only in {na}:",onlyA)
    print(f" pads only in {nb}:",onlyB)
    # connectivity: map net names A->B by majority vote, then check every common pad
    vote=defaultdict(Counter)
    for k in set(A)&set(B): vote[A[k]][B[k]]+=1
    name_map={a:c.most_common(1)[0][0] for a,c in vote.items()}
    renamed={a:b for a,b in name_map.items() if a!=b}
    print(" net renames:",renamed)
    bad=[(k,A[k],B[k]) for k in sorted(set(A)&set(B)) if name_map[A[k]]!=B[k]]
    print(f" connectivity differences: {len(bad)}")
    for b in bad: print("   ",b)
    # partition check: two B nets mapped from one A net, or two A nets to one B net
    inv=Counter(name_map.values()); merged=[b for b,c in inv.items() if c>1]
    print(" nets merged in",nb,":",merged)
compare(sch_pn,brd_pn,'sch','brd')
compare(brd_pn,kic_pn,'brd','kicad')
compare(sch_pn,kic_pn,'sch','kicad')
# single-pin nets & pin counts
print("\n== schematic nets by pin count")
for n,m in sorted(sch['nets'].items(), key=lambda kv: len(kv[1])):
    if len(m)<=2: print(f"  {n}: {len(m)} pins {[x['part']+'.'+x['pin'] for x in m]}")
