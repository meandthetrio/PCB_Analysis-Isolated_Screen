"""Parse a KiCad .net (s-expression netlist): components (ref,value,footprint) and nets (name -> [(ref,pin)])."""
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from sexp import parse, find_all, find1
doc=parse(open(sys.argv[1],encoding='utf-8').read())[0]
comps={}
for c in find_all(find1(doc,'components'),'comp'):
    comps[find1(c,'ref')[1]]=dict(value=find1(c,'value',[None,''])[1],fp=find1(c,'footprint',[None,''])[1])
nets={}
for n in find_all(find1(doc,'nets'),'net'):
    name=find1(n,'name')[1]
    nodes=[(find1(x,'ref')[1],find1(x,'pin')[1],find1(x,'pinfunction',[None,''])[1],find1(x,'pintype',[None,''])[1]) for x in find_all(n,'node')]
    nets[name]=nodes
json.dump(dict(comps=comps,nets=nets),open(sys.argv[2],'w'),indent=1)
print("components",len(comps),"nets",len(nets))
print("single-node nets:",[ (k,v) for k,v in nets.items() if len(v)==1])
