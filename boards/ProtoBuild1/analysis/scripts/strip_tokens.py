import re, subprocess, sys, os
def tokens(s): return set(re.findall(r'\((\w+)[\s)]', s))
def strip_token(s, tok):
    # remove every balanced s-expression starting with (tok
    out=[]; i=0; pat=re.compile(r'\('+re.escape(tok)+r'[\s)]')
    while True:
        m=pat.search(s,i)
        if not m: out.append(s[i:]); break
        out.append(s[i:m.start()]); d=0; j=m.start()
        while True:
            c=s[j]
            if c=='"':
                j+=1
                while s[j]!='"':
                    if s[j]=='\\': j+=1
                    j+=1
            elif c=='(': d+=1
            elif c==')':
                d-=1
                if d==0: break
            j+=1
        i=j+1
    return "".join(out)
def test_pcb(text, name="_strip.kicad_pcb"):
    open(name,"w").write(text)
    r = subprocess.run([sys.executable,"-c",f"import pcbnew; b=pcbnew.LoadBoard('{name}'); print('RESULT', 'OK' if b else 'FAIL', 0 if b is None else len(b.GetFootprints()), 0 if b is None else len(b.GetTracks()))"],capture_output=True,text=True)
    m=re.search(r'RESULT.*', r.stdout); return m.group(0) if m else "CRASH"
def test_sch(text, name="_strip.kicad_sch"):
    open(name,"w").write(text)
    if os.path.exists("_strip.xml"): os.remove("_strip.xml")
    subprocess.run(["kicad-cli","sch","export","netlist","--format","kicadxml","-o","_strip.xml",name],capture_output=True,text=True)
    return "RESULT OK" if os.path.exists("_strip.xml") else "RESULT FAIL"
def run(kind, path, refpath, test):
    s=open(path).read(); ref=open(refpath).read()
    cand = sorted(tokens(s)-tokens(ref))
    print(f"\n#### {kind}: {os.path.basename(path)}  candidate tokens (in file, absent from KiCad-9 reference): {cand}")
    allstripped = s
    for t in cand: allstripped = strip_token(allstripped, t)
    print("  strip ALL candidates ->", test(allstripped))
    if 'OK' in test(allstripped):
        needed=[]
        for t in cand:
            trial = s
            for u in cand:
                if u!=t: trial = strip_token(trial, u)
            if 'FAIL' in test(trial): needed.append(t)
        print("  tokens that individually must be stripped:", needed)
        return needed
    return None
res = {}
res['sch'] = run("SCH", "ProtoBuild1.kicad_sch", "../../WavetableController.kicad_sch", test_sch)
res['pcb8'] = run("PCB-v8", "ProtoBuild1.kicad_pcb", "../../WavetableController.kicad_pcb", test_pcb)
# v10 file: downgrade version number then strip
s10 = open("ProtoBuild1-zones-filled-kicad10-format.kicad_pcb").read()
s10d = s10.replace("(version 20260206)", "(version 20241229)", 1).replace('(generator_version "10.0")', '(generator_version "9.0")', 1)
open("_pb1_v10_downgraded.kicad_pcb","w").write(s10d)
res['pcb10'] = run("PCB-v10 (version downgraded to 20241229)", "_pb1_v10_downgraded.kicad_pcb", "../../WavetableController.kicad_pcb", test_pcb)
print("\nSUMMARY", res)
for f in ("_strip.kicad_pcb","_strip.kicad_sch","_strip.xml"):
    if os.path.exists(f): os.remove(f)
