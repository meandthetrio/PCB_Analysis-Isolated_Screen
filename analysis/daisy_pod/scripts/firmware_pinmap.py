"""libDaisy Pod pin constants vs the Rev5 schematic. Reads sch_full.json (eagle_sch_full.py), libDaisy src/daisy_pod.cpp
(seed::Dn constants), src/daisy_seed.h (Dn -> STM32 port/pin) and src/hid/midi.cpp (MIDI UART default pins).
Derives the physical-pin <-> Dn relation from the Seed symbol's own pin names "GPIOn(...)" and checks every constant.
Run: python3 -I firmware_pinmap.py sch_full.json daisy_pod.cpp daisy_seed.h midi.cpp"""
import sys, json, re
sch=json.load(open(sys.argv[1])); pod=open(sys.argv[2]).read(); seedh=open(sys.argv[3]).read(); midi=open(sys.argv[4]).read()
padnet={}
for n,m in sch['nets'].items():
    for x in m: padnet[(x['part'],x['pad'])]=n
u1=sorted(sch['parts']['U1']['pins'],key=lambda p:int(p['pad']))
# physical pin -> Dn from symbol pin name
phys2d={}
for p in u1:
    m=re.match(r'GPIO(\d+)\((.*)\)',p['pin'])
    if m: phys2d[int(p['pad'])]=(int(m.group(1)),m.group(2))
print("physical pin -> D-index relation (from symbol names):")
for pin,(d,fn) in phys2d.items(): print(f"  pin {pin:>2} = D{d:<2} ({fn})  offset {pin-d}")
d2port={int(a):(b,int(c)) for a,b,c in re.findall(r'constexpr Pin D(\d+)\s*=\s*Pin\(PORT([A-K]),\s*(\d+)\)',seedh)}
consts={k:int(v) for k,v in re.findall(r'constexpr Pin (\w+)\s*=\s*seed::D(\d+);',pod.split('/*')[0])}
d2phys={d:pin for pin,(d,_) in phys2d.items()}
expect={'SW_1_PIN':'TAC_SWITCH_1','SW_2_PIN':'TAC_SWITCH_2','ENC_A_PIN':'ENC_A','ENC_B_PIN':'ENC_B','ENC_CLICK_PIN':'ENC_CLICK',
        'LED_1_R_PIN':'LED_1_R','LED_1_G_PIN':'LED_1_G','LED_1_B_PIN':'LED_1_B','LED_2_R_PIN':'LED_2_R','LED_2_G_PIN':'LED_2_G','LED_2_B_PIN':'LED_2_B',
        'KNOB_1_PIN':'POT_1','KNOB_2_PIN':'POT_2'}
print("\nlibDaisy daisy_pod.cpp constant -> Dn -> STM32 -> Seed pin -> schematic net")
ok=True
for k,d in consts.items():
    pin=d2phys[d]; net=padnet[('U1',str(pin))]; port='P%s%d'%d2port[d]
    good=(net==expect.get(k)); ok&=good
    print(f"  {k:<14} D{d:<2} {port:<5} pin {pin:>2} {phys2d[pin][1]:<16} net={net:<14} {'OK' if good else 'MISMATCH (expected '+expect.get(k,'?')+')'}")
m=re.search(r'rx\s*=\s*Pin\(PORT([A-K]),\s*(\d+)\);\s*tx\s*=\s*Pin\(PORT([A-K]),\s*(\d+)\)',midi)
rxp,rxn,txp,txn=m.groups()
port2d={v:k for k,v in d2port.items()}
for lab,(p,n) in (('MIDI rx',(rxp,int(rxn))),('MIDI tx',(txp,int(txn)))):
    d=port2d[(p,n)]; pin=d2phys[d]; print(f"  {lab:<14} D{d:<2} P{p}{n:<4} pin {pin:>2} {phys2d[pin][1]:<16} net={padnet[('U1',str(pin))]}")
# fixed-function pins
for pin in (2,3,4,5,6,7,36,37,1):
    d=phys2d[pin][0]; print(f"  fixed          D{d:<2} P{d2port[d][0]}{d2port[d][1]:<4} pin {pin:>2} {phys2d[pin][1]:<16} net={padnet[('U1',str(pin))]}")
print("\nall Pod constants match:",ok)
