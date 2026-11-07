import pcbnew, collections, math, sys
b = pcbnew.LoadBoard(sys.argv[1]); mm = pcbnew.ToMM
fps = {f.GetReference(): f for f in b.GetFootprints()}
pads = [(f.GetReference(), p.GetNumber(), p.GetNetname(), mm(p.GetPosition().x), mm(p.GetPosition().y)) for f in b.GetFootprints() for p in f.Pads()]
caps = [p for p in pads if p[0].startswith('C')]
# IC / transistor power pins: U1-U3 pin 4 (VN) and 8 (VP); Q4 (BD139) pin2 VP; Q5 (BD140) pin2 VN; Q6 pin? ; Q2 pin2 VP
targets = [p for p in pads if p[2] in ('VP','VN') and (p[0].startswith('U') or p[0].startswith('Q'))]
print("IC/transistor rail pins -> nearest same-net capacitor pad (straight-line, mm) and nearest GND-side pad of that cap")
for ref, pin, net, x, y in sorted(targets):
    best = min(((math.hypot(x-cx, y-cy), cref, cpin) for cref, cpin, cnet, cx, cy in caps if cnet == net), default=None)
    print(f"   {ref}.{pin:>2s} {net:3s} at ({x:6.1f},{y:6.1f}) -> nearest cap {best[1]}.{best[2]} {best[0]:5.1f} mm")
# rail copper: per net, total length by width on each layer and via count
tracks = [t for t in b.GetTracks()]
L = collections.defaultdict(lambda: collections.defaultdict(float)); V = collections.Counter()
for t in tracks:
    if t.GetClass()=='PCB_TRACK':
        L[t.GetNetname()][(b.GetLayerName(t.GetLayer()), round(mm(t.GetWidth()),2))] += mm(t.GetLength())
    elif t.GetClass()=='PCB_VIA': V[t.GetNetname()] += 1
print("\nnet copper (length mm by layer/width, vias) for rails and key nets:")
for net in ['VP','VN','VPIN','VNIN','GND','D','P','X','RST','TAP1','TAP2','TAP3','TAP4','N','OUT','IN','IN1','OUTJ','OUTX','Q6C','U1AO','U1BO','U3BO']:
    segs = L.get(net, {}); tot = sum(segs.values())
    print(f"   {net:6s} total {tot:6.1f} mm  {dict((f'{k[0]}/{k[1]}', round(v,1)) for k,v in segs.items())}  vias {V.get(net,0)}")
# which pads are on GND and whether GND is routed by track or only by pour
gnd_pads = [p for p in pads if p[2]=='GND']
print(f"\nGND pads: {len(gnd_pads)}; GND track length {sum(L['GND'].values()):.1f} mm; GND vias {V['GND']}")
# IPC-2221 external: I = 0.048 * dT^0.44 * A^0.725 (A in mil^2), for 0.4 mm x 35 um
def ipc(w_mm, t_um=35, dT=10):
    A = (w_mm/0.0254)*(t_um/25.4); return 0.048*(dT**0.44)*(A**0.725)
print(f"IPC-2221 external 1oz, dT 10C: 0.4 mm -> {ipc(0.4):.2f} A ; 0.25 -> {ipc(0.25):.2f} A ; 0.1 -> {ipc(0.1):.2f} A")
# resistance of 0.4mm 1oz trace per 100mm
rho=1.72e-8; print(f"0.4 mm x 35 um copper: {rho*0.1/(0.4e-3*35e-6)*1000:.1f} mOhm per 100 mm")
# footprint positions summary for key parts
for r in ['J3','D3','D4','C11','C13','C12','C14','U1','U2','U3','Q4','Q5','Q6','L1','R51','J13','J17','J8','J9','J15','J16','TP2','TP3','C15','R17','R18','H1','H2','H3','H4','J1','J2','J4','J5','J6','J7','J18','J10','J14','J11','J12']:
    f = fps.get(r)
    if f: print(f"   {r:4s} at ({mm(f.GetPosition().x):6.1f},{mm(f.GetPosition().y):6.1f}) rot {f.GetOrientationDegrees():5.1f} {f.GetFPIDAsString().split(':')[-1][:40]}")
