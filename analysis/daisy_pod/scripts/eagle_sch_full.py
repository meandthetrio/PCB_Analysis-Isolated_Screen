"""Eagle 9 .sch -> JSON with pad numbers. For every part: library/deviceset/device/value/package and the gate+pin -> pad map
(from <connects>), the full symbol pin list (name, direction) so unconnected pins can be found, and nets as
[(part, gate, pin, pad)]. Run: python3 -I eagle_sch_full.py IN.sch OUT.json"""
import sys, json, xml.etree.ElementTree as ET
r=ET.parse(sys.argv[1]).getroot()
libs={}
for lib in r.findall('.//schematic/libraries/library'):
    L=libs[lib.get('name')]={'symbols':{},'devicesets':{}}
    for sym in lib.findall('symbols/symbol'):
        L['symbols'][sym.get('name')]=[dict(name=p.get('name'),direction=p.get('direction','io'),function=p.get('function')) for p in sym.findall('pin')]
    for ds in lib.findall('devicesets/deviceset'):
        gates={g.get('name'):g.get('symbol') for g in ds.findall('gates/gate')}
        devs={}
        for dev in ds.findall('devices/device'):
            conn={}
            for c in dev.findall('connects/connect'):
                conn[(c.get('gate'),c.get('pin'))]=c.get('pad')
            devs[dev.get('name')]=dict(package=dev.get('package'),connects={g+'|'+p:pad for (g,p),pad in conn.items()})
        L['devicesets'][ds.get('name')]=dict(gates=gates,devices=devs,prefix=ds.get('prefix'))
parts={}
for p in r.findall('.//schematic/parts/part'):
    lib=libs[p.get('library')]; ds=lib['devicesets'][p.get('deviceset')]; dev=ds['devices'][p.get('device')]
    pins=[]
    for g,sym in ds['gates'].items():
        for pin in lib['symbols'][sym]:
            pins.append(dict(gate=g,pin=pin['name'],pad=dev['connects'].get(g+'|'+pin['name']),direction=pin['direction']))
    parts[p.get('name')]=dict(library=p.get('library'),deviceset=p.get('deviceset'),device=p.get('device'),value=p.get('value'),
                              package=dev['package'],prefix=ds['prefix'],pins=pins)
nets={}
for sheet in r.findall('.//schematic/sheets/sheet'):
    for net in sheet.findall('nets/net'):
        n=net.get('name'); nets.setdefault(n,[])
        for seg in net.findall('segment'):
            for pr in seg.findall('pinref'):
                part=pr.get('part'); g=pr.get('gate'); pin=pr.get('pin')
                pad=next((x['pad'] for x in parts[part]['pins'] if x['gate']==g and x['pin']==pin),None)
                nets[n].append(dict(part=part,gate=g,pin=pin,pad=pad))
            for lab in seg.findall('label'): pass
json.dump(dict(parts=parts,nets=nets),open(sys.argv[2],'w'),indent=1)
print(len(parts),'parts',len(nets),'nets')
