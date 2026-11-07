import sys, re, openpyxl, collections
sys.path.insert(0,"SCRATCH_DIR")
from sexp import parse, find, first
S="SCRATCH_DIR/upload_protobuild1/ProtoBuild1-autorouted"
root = parse(open(f"{S}/reports/ProtoBuild1-netlist.net").read())
sch = {}
for c in find(first(root,'components'),'comp'):
    ref=first(c,'ref')[1]; val=first(c,'value')[1]; fp=first(c,'footprint',[None,''])[1]
    sch[ref]=(val,fp)
# alias map from schematic values "10k [R1a]" -> R1a
alias = {}
for ref,(val,fp) in sch.items():
    m = re.search(r'\[([^\]]+)\]', val)
    if m:
        for a in m.group(1).split('/'): alias[a.strip()] = ref
print("aliases:", alias)
wb = openpyxl.load_workbook(f"{S}/ProtoBuild1-parts-list.xlsx", data_only=True); ws = wb.worksheets[0]
bom = []; section=None
for r in ws.iter_rows(min_row=5, values_only=True):
    if r[0] is None: continue
    if r[1] is None and r[2] is None: section = r[0]; continue
    bom.append(dict(section=section, refs=str(r[0]), qty=r[1], value=r[2], desc=r[3], fp=r[4], mfr=r[5], mpn=r[6]))
print(f"BOM lines: {len(bom)}")
def expand(refs):
    out=[]
    for tok in re.split(r'[,;]\s*', refs):
        tok=tok.strip()
        m = re.match(r'^([A-Za-z]+)(\d+)\s*-\s*([A-Za-z]+)?(\d+)$', tok)   # ranges like C17-C22
        if m:
            p=m.group(1); a=int(m.group(2)); b=int(m.group(4)); out += [f"{p}{i}" for i in range(a,b+1)]
        else: out.append(tok)
    return out
bom_refs = collections.OrderedDict()
for line in bom:
    for ref in expand(line['refs']):
        ref2 = alias.get(ref, ref)
        bom_refs.setdefault(ref2, []).append(line)
sch_refs = set(sch); b_refs=set(bom_refs)
print("\nBOM refs with no schematic symbol:", sorted(b_refs - sch_refs))
print("Schematic refs absent from BOM:", sorted(sch_refs - b_refs, key=lambda r:(re.match(r'[A-Za-z]+',r).group(0), int(re.search(r'\d+',r).group(0)) if re.search(r'\d+',r) else 0)))
print("\nRefs on more than one BOM line:", {r:[l['refs'] for l in ls] for r,ls in bom_refs.items() if len(ls)>1})
# value comparison
def norm(v):
    v=str(v).lower().replace('ω','').replace('Ω','').replace(' ','').replace('µ','u').replace('μ','u')
    v=re.sub(r'\[.*?\]','',v)
    m=re.match(r'^([\d.]+)(k|m|u|n|p|r)?([\d]*)',v)
    return v
print("\nvalue check (BOM value vs schematic value), only mismatches/odd ones:")
for ref, ls in bom_refs.items():
    if ref not in sch: continue
    sval = sch[ref][0]; bval = ls[0]['value']
    s1 = re.sub(r'\s*\[.*?\]','',sval).lower().replace(' ','')
    b1 = str(bval).lower().replace(' ','').replace('ω','').replace('µ','u').replace('kΩ','k')
    # normalise 1k5 <-> 1.5k, 2k4 <-> 2.4k, 10u <-> 10uf, 100n <-> 0.1uf
    def canon(x):
        x = x.replace('kω','k').replace('ω','')
        m = re.match(r'^(\d+)([kmunpr])(\d+)$', x)
        if m: x = f"{m.group(1)}.{m.group(3)}{m.group(2)}"
        x = re.sub(r'^([\d.]+)(k|m|u|n|p|r)?(f|v|w|ohm|film|c0g|log|lin)?.*$', lambda m: (m.group(1)+(m.group(2) or '')), x)
        if x.endswith('r'): x=x[:-1]
        if re.match(r'^0\.1u$', x): x='100n'
        return x
    cs, cb = canon(s1), canon(b1)
    flag = "" if cs==cb else "  <-- CHECK"
    if flag or ref in ('C5','R17','R18','R15','R51','Rs','C36','C35'): print(f"   {ref:5s} sch='{sval}'  bom='{bval}' (line '{ls[0]['refs']}')  canon {cs} vs {cb}{flag}")
# footprint sanity: BOM footprint text vs schematic footprint
print("\nBOM footprint text vs schematic footprint (first 12 lines):")
for line in bom[:40]:
    refs = expand(line['refs']); r0 = alias.get(refs[0], refs[0])
    if r0 in sch: print(f"   {line['refs'][:22]:22s} bom:'{str(line['fp'])[:60]:60s}' sch:'{sch[r0][1].split(':')[-1][:55]}'")
# terminal block counts
print("\nterminal blocks in schematic:", collections.Counter(sch[r][1].split(':')[-1][:38] for r in sch if r.startswith('J')))
print("BOM J rows:", [(l['refs'], l['qty'], l['desc']) for l in bom if l['refs'].startswith('J')])
