"""Walk a signal chain through 2-pin passives from a starting pad: prints net -> part(value) -> net ... until a
multi-pin part or a rail. Usage: chain_walk.py netlist.json REF.PIN [maxdepth]"""
import sys, json
nl=json.load(open(sys.argv[1])); start=sys.argv[2]; maxd=int(sys.argv[3]) if len(sys.argv)>3 else 12
pin2net={}; net2nodes=nl['nets']
for net,nodes in net2nodes.items():
    for r,p,f,t in nodes: pin2net[(r,p)]=net
RAILS={'GND','+3V3','+3V3_A','+5V','+5V_A','+9V','+9V_A','+12V','-12V','DSY_VIN','-10V_REF'}
def passive(r): return r[0] in 'RCL' and not r.startswith('LED') or r.startswith('FB') or r[0]=='D'
def walk(ref,pin,depth,seen,indent=''):
    net=pin2net.get((ref,pin))
    if net is None or net in seen: return
    seen=seen|{net}
    nodes=[(r,p) for r,p,f,t in net2nodes[net] if not (r==ref and p==pin)]
    val=lambda r: nl['comps'].get(r,{}).get('value','')
    print(f"{indent}{ref}.{pin} -> [{net}] : " + ', '.join(f"{r}.{p}({val(r)})" for r,p in nodes[:12]) + (' ...' if len(nodes)>12 else ''))
    if net in RAILS or depth>=maxd: return
    for r,p in nodes:
        if passive(r):
            other=[pp for (rr,pp) in pin2net if rr==r and pp!=p]
            for op in other: walk(r,op,depth+1,seen,indent+'  ')
walk(*start.split('.'),0,frozenset())
