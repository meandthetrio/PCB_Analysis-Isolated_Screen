import re,html,sys
src=open(sys.argv[1]).read()
def md_inline(s):
    s=html.escape(s); s=re.sub(r'\*\*(.+?)\*\*',r'<b>\1</b>',s); s=re.sub(r'`(.+?)`',r'<code>\1</code>',s); return s
sections=[];cur=None
for line in src.splitlines():
    if line.startswith('## '):
        cur={'title':line[3:].strip(),'rows':[],'hdr':None}; sections.append(cur); continue
    if cur is None or not line.startswith('|'): continue
    cells=[c.strip() for c in line.strip().strip('|').split('|')]
    if set(''.join(cells))<=set('-: '): continue
    if cur['hdr'] is None: cur['hdr']=cells; continue
    cur['rows'].append(cells)
def status_of(sec,row):
    h=[x.lower() for x in sec['hdr']]
    for key in ('rev 3 (9 oct) status','rev 3','9 oct status'):
        if key in h: return row[h.index(key)]
    return row[2] if len(row)>2 else ''
keep=[]
for sec in sections:
    if not sec['hdr'] or sec['title'].startswith('Items the 7 Oct review did not have'): continue
    rows=[r for r in sec['rows'] if not re.match(r'\**(done|fixed)',status_of(sec,r).strip().lower())]
    if rows: keep.append((sec['title'],sec['hdr'],rows))
newitems=[
 ("No ground stitching vias","244 vias, 0 on GND; the front pour is 15 fragments joined to the back plane only through component holes; 3 fragments hang on a single pad; 10 bottom-side GND pads on U2/U3/U4/U6 reach ground through one thin track","Add stitching vias every 10–15 mm and at every front-pour fragment and IC ground","Long ground returns under the audio and SPI runs: higher noise floor, weaker ground for the buck; single-pad fragments go floating if that joint cracks"),
 ("Eight single-spoke thermal reliefs","GND pads on TAC_SWITCH_1, U1, P2 (two), R18, C9, U3, C10 connect through one 0.5 mm spoke","Reduce the zone thermal gap or add a short GND track to each","Works today; one cracked spoke opens a ground pin"),
 ("No inrush limit","200 µF (C15 + C19) behind only the beads and Schottkys; 700 µF total","A few ohms or an NTC ahead of C15, or fewer bulk caps","About 26 A peak at plug-in or when SW1 is flipped, through diodes rated 9 A surge and 2 A beads; contact wear on SW1 and the barrel jack"),
 ("Display reset line floats","RES_SPI is a two-node net with no pull-up or RC","10 k from RES_SPI to +3V3_OLED","Undefined reset state until firmware drives it; a glitchy display at power-up"),
 ("Headphone pot is a linear taper","Headphones1 is B10k, signal on pin 1, GND on pin 3","A-taper part; confirm clockwise is louder with the PTD902 terminal order","Volume bunched at one end of the travel; possibly backwards"),
 ("Pot bushing outside the outline","Bushing exits 9 mm past the bottom edge, 16.75 mm from the headphone jack","Panel cut-out, or move the pot inboard","Panel does not fit without a cut-out"),
 ("\"Exclude from position files\" inconsistent","Set on J3–J7 only; 13 other through-hole parts and the LEDs are in the pick-and-place file","Set the flag on every hand-soldered part","15 no-match entries at JLCPCB upload bury the two that matter, the LEDs"),
 ("Reference designators repurposed since August","C14 was the 470 µF noise-fix cap, now 100 nF; C17 100 nF → 100 µF; C15 10 µF → 100 µF","A line in the change log","Old notes, rework instructions and photos naming C14, C15 or C17 point at the wrong part"),
]
keep.append(("New in the 9 October files",["Item","What was measured","Fix","Potential consequence if left"],[list(r) for r in newitems]))
css='@page{size:A4 landscape;margin:12mm}body{font:9.5pt/1.3 Helvetica,Arial,sans-serif;color:#111}h1{font-size:16pt;margin:0 0 4pt}h2{font-size:12pt;margin:14pt 0 4pt;page-break-after:avoid}p.lead{margin:0 0 6pt;color:#333}table{border-collapse:collapse;width:100%;table-layout:fixed;margin-bottom:6pt}th,td{border:1px solid #bbb;padding:3pt 4pt;vertical-align:top;font-size:8.5pt;word-wrap:break-word}th{background:#eee;text-align:left}code{font-family:Menlo,monospace;font-size:8pt}'
out=['<!doctype html><html><head><meta charset="utf-8"><title>Rev 3 status, open items</title><style>'+css+'</style></head><body>']
out.append('<h1>WavetableController Rev 3 status: open items only</h1>')
out.append('<p class="lead">Trey\'s 9 October files measured against the 7 October Rev 2 Design Review. Done items removed. Power is 9 V from the barrel jack. LED: Würth WL-SFTW 150505M173300 (datasheet supplied 9 Oct); its pinout is the mirror of the Cree part named on the schematic, and against it the wiring, colours and footprint are correct, so the earlier polarity finding and the 180° placement advice are withdrawn. The 7 Oct count of 225 ground stitching vias does not hold: the 9 Oct board has 244 vias, none on GND. Generated 2026-10-09.</p>')
for title,hdr,rows in keep:
    out.append(f'<h2>{html.escape(title)}</h2><table><tr>'+''.join(f'<th>{md_inline(h)}</th>' for h in hdr)+'</tr>')
    for r in rows:
        r=r+['']*(len(hdr)-len(r)); out.append('<tr>'+''.join(f'<td>{md_inline(c)}</td>' for c in r[:len(hdr)])+'</tr>')
    out.append('</table>')
out.append('</body></html>')
open(sys.argv[2],'w').write('\n'.join(out))
print([(t,len(r)) for t,h,r in keep])
