"""Dump an Eagle 9 .sch to JSON: parts (name, library, deviceset, device, value, package) and nets (name -> [(part, pin)]). Run: python3 -I eagle_sch_netlist.py IN.sch OUT.json"""
import sys, json, xml.etree.ElementTree as ET
r=ET.parse(sys.argv[1]).getroot()
parts={p.get('name'):{'library':p.get('library'),'deviceset':p.get('deviceset'),'device':p.get('device'),'value':p.get('value'),'package':None} for p in r.findall('.//parts/part')}
# package via library deviceset/device
for lib in r.findall('.//libraries/library'):
    for ds in lib.findall('.//deviceset'):
        for dev in ds.findall('.//device'):
            for n,p in parts.items():
                if p['library']==lib.get('name') and p['deviceset']==ds.get('name') and p['device']==dev.get('name'): p['package']=dev.get('package')
nets={}
for sheet in r.findall('.//sheets/sheet'):
    for net in sheet.findall('.//nets/net'):
        nets.setdefault(net.get('name'),[])
        for pr in net.findall('.//pinref'): nets[net.get('name')].append((pr.get('part'),pr.get('pin')))
json.dump({'parts':parts,'nets':nets},open(sys.argv[2],'w'),indent=1)
print(len(parts),"parts",len(nets),"nets")
