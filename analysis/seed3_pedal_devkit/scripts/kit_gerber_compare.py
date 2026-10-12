#!/usr/bin/env python3
"""Compare a KiCad-plotted Gerber/drill set against a production set, layer by layer (run with python3 -I).
Per Gerber: aperture table, D03 flash count, D01 draw count, G36 region count, and the exact set of
flash positions / draw endpoints (1 um) -> symmetric-difference counts. Per drill: tool list, hit counts, hit-set diff.
usage: kit_gerber_compare.py <plotted_dir> <production_gerber_dir> [name_suffix_map]"""
import re,sys,os,collections,glob
A,B=sys.argv[1],sys.argv[2]
def parse_gbr(p):
    ap={}; cur=None; fmt=5; sc=10; flash=collections.Counter(); draw=collections.Counter(); regions=0; fpos=set(); dseg=set(); last=None; inreg=False; polarity=collections.Counter(); hdr={}
    for line in open(p,encoding='utf-8',errors='replace'):
        line=line.strip()
        m=re.match(r'%ADD(\d+)([A-Za-z_]+),?([^*]*)\*%',line)
        if m: ap[int(m.group(1))]=(m.group(2),m.group(3)); continue
        m=re.match(r'%FSLAX(\d)(\d)',line)
        if m: fmt=int(m.group(2)); sc=10**(6-fmt); continue
        m=re.match(r'%TF\.(\w+),([^*]*)\*%',line)
        if m: hdr[m.group(1)]=m.group(2); continue
        if line.startswith('%LP'): polarity[line[3]]+=1; continue
        if line.startswith('G36'): inreg=True; regions+=1; continue
        if line.startswith('G37'): inreg=False; continue
        m=re.match(r'D(\d+)\*',line)
        if m and int(m.group(1))>=10: cur=int(m.group(1)); continue
        m=re.match(r'(?:G0[123])?X(-?\d+)Y(-?\d+)(?:I(-?\d+)J(-?\d+))?D0([123])\*',line)
        if m:
            x,y=int(m.group(1))*sc,int(m.group(2))*sc; op=m.group(5)   # scale to nm regardless of FS format
            if op=='3': flash[cur]+=1; fpos.add((cur,x,y))
            elif op=='1' and not inreg:
                draw[cur]+=1
                if last: dseg.add((cur,)+tuple(sorted([last,(x,y)])))
            last=(x,y)
    return dict(ap=ap,flash=flash,draw=draw,regions=regions,fpos=fpos,dseg=dseg,hdr=hdr,polarity=polarity,fmt=fmt)
def shift(d,ox,oy):
    d['fpos']=set((k,x-ox,y-oy) for k,x,y in d['fpos']); d['dseg']=set((k,(a[0]-ox,a[1]-oy),(b_[0]-ox,b_[1]-oy)) for k,a,b_ in d['dseg']); return d
def origin(d):  # min corner of all copper flash/draw coordinates -> removes the aux-origin offset between plots
    xs=[x for _,x,_ in d['fpos']]+[p[0] for _,a,b_ in d['dseg'] for p in (a,b_)]; ys=[y for _,_,y in d['fpos']]+[p[1] for _,a,b_ in d['dseg'] for p in (a,b_)]
    return min(xs),min(ys)
def apkey(ap):  # aperture by shape+params, independent of D-number
    return collections.Counter((s,p) for s,p in ap.values())
def layer_of(fn):
    m=re.search(r'-(F_Cu|B_Cu|F_Mask|B_Mask|F_Paste|B_Paste|F_Silkscreen|B_Silkscreen|Edge_Cuts|F_Fab|B_Fab|User_Drawings)\.',fn); return m.group(1) if m else None
fa={layer_of(f):f for f in glob.glob(A+'/*.g*') if layer_of(f)}; fb={layer_of(f):f for f in glob.glob(B+'/*.g*') if layer_of(f)}
OA=origin(parse_gbr(fa['F_Cu'])); OB=origin(parse_gbr(fb['F_Cu'])); print('origin (F_Cu min corner, nm): plot',OA,'production',OB,'| FS decimals plot/prod',parse_gbr(fa['F_Cu'])['fmt'],parse_gbr(fb['F_Cu'])['fmt'])
print(f'{"layer":14s} {"ap A/B":9s} {"ap-diff":7s} {"flash A/B":11s} {"draw A/B":11s} {"reg A/B":9s} {"flash-set diff":15s} {"draw-set diff":14s} note')
for L in ['F_Cu','B_Cu','F_Mask','B_Mask','F_Paste','B_Paste','F_Silkscreen','B_Silkscreen','Edge_Cuts','F_Fab','B_Fab','User_Drawings']:
    if L not in fa or L not in fb: print(L,'missing in',('plot' if L not in fa else 'production')); continue
    a=shift(parse_gbr(fa[L]),*OA); b=shift(parse_gbr(fb[L]),*OB)
    ka,kb=apkey(a['ap']),apkey(b['ap']); apd=sum((ka-kb).values())+sum((kb-ka).values())
    # map flash/draw sets to shape keys instead of D numbers
    def remap(s,ap): return set((ap.get(k,('?','')),)+tuple(rest) for k,*rest in s)
    fA,fB=remap(a['fpos'],a['ap']),remap(b['fpos'],b['ap']); dA,dB=remap(a['dseg'],a['ap']),remap(b['dseg'],b['ap'])
    print(f'{L:14s} {len(a["ap"]):>4d}/{len(b["ap"]):<4d} {apd:>7d} {sum(a["flash"].values()):>5d}/{sum(b["flash"].values()):<5d} {sum(a["draw"].values()):>5d}/{sum(b["draw"].values()):<5d} {a["regions"]:>4d}/{b["regions"]:<4d} {len(fA-fB):>6d}/{len(fB-fA):<6d}     {len(dA-dB):>6d}/{len(dB-dA):<6d}  ', 'IDENTICAL geometry' if not (fA^fB) and not (dA^dB) and a['regions']==b['regions'] else '')
    if apd: print('     aperture diff: plot-only',len(ka-kb),'prod-only',len(kb-ka),'(prod-only shapes are pad apertures -> production silk plotted with pad/mask subtraction)' if 'Silk' in L else dict(kb-ka))
    if (fA-fB) or (fB-fA):
        ex=list(fA-fB)[:3]+[('<-B',)+e for e in list(fB-fA)[:3]]; print('     flash examples (shape, x, y mm):',[(e[0][0],round(e[1]/1e6,3),round(e[2]/1e6,3)) if e[0]!='<-B' else ('prod-only',e[1][0],round(e[2]/1e6,3),round(e[3]/1e6,3)) for e in ex][:6])
# drill
def parse_drl(p):
    tools={}; cur=None; hits=collections.Counter(); hs=set(); slots=0
    for line in open(p,encoding='utf-8',errors='replace'):
        line=line.strip()
        m=re.match(r'T(\d+)C([\d.]+)',line)
        if m: tools[int(m.group(1))]=float(m.group(2)); continue
        m=re.match(r'T(\d+)$',line)
        if m: cur=int(m.group(1)); continue
        m=re.match(r'X(-?[\d.]+)Y(-?[\d.]+)(G85X(-?[\d.]+)Y(-?[\d.]+))?$',line)
        if m and cur:
            hits[tools[cur]]+=1; hs.add((tools[cur],round(float(m.group(1)),3),round(float(m.group(2)),3)))
            if m.group(3): slots+=1
    return tools,hits,hs,slots
da=glob.glob(A+'/*.drl')+glob.glob(A+'/**/*.drl',recursive=True); db=glob.glob(B+'/**/*.drl',recursive=True)+glob.glob(B+'/*.drl')
ta,ha,sa,sla=parse_drl(da[0]); tb,hb,sb,slb=parse_drl(db[0])
def dnorm(hs):
    mx=min(x for _,x,_ in hs); my=min(y for _,_,y in hs); return set((t,round(x-mx,3),round(y-my,3)) for t,x,y in hs)
sa,sb=dnorm(sa),dnorm(sb)
print('DRILL plot: tools',sorted(ta.values()),'hits',sum(ha.values()),'slots',sla,'| production: tools',sorted(tb.values()),'hits',sum(hb.values()),'slots',slb)
print('  per-tool hits plot',sorted(ha.items()),'\n  per-tool hits prod',sorted(hb.items()))
print('  hit-set diff plot-prod',len(sa-sb),'prod-plot',len(sb-sa), 'IDENTICAL' if sa==sb else '', list(sa-sb)[:5], list(sb-sa)[:5])
