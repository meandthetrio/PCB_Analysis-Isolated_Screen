#!/usr/bin/env python3
"""Generate JLCPCB-ready BOM + hand-solder list from the rev-4 KiCad files.
Inputs: kicad_out/rev4/sch_symbols.csv, kicad_out/rev4/pcb_footprints.csv, the LCSC map from Trey's rev-4 BOM.
Outputs (CSV, UTF-8, no BOM mark): rev4/order/BOM_JLCPCB_SMT.csv, rev4/order/HAND_SOLDER.csv, rev4/order/BOM_check.txt
"""
import csv, re, json, collections, sys
sch = {r['ref']: r for r in csv.DictReader(open('kicad_out/rev4/sch_symbols.csv')) if not r['ref'].startswith('#')}
pcb = {r['ref']: r for r in csv.DictReader(open('kicad_out/rev4/pcb_footprints.csv'))}
# ref -> LCSC from Trey's rev-4 BOM (bom_lines.csv), designators split on comma/whitespace
lcsc_of = {}
for r in csv.DictReader(open('kicad_out/rev4/pass4/bom_lines.csv')):
    for d in re.split(r'[,\s]+', r['designator_raw'].strip()):
        if d: lcsc_of[d] = r['lcsc']
# verified part data (JLCPCB part pages, fetched 2026-10-13)
PARTS = {
 'C385198':  ('NSR1020MW2T3G', 'onsemi', 'SOD-323', 'Schottky 20V 1A (MIDI-in protection)'),
 'C169541':  ('1N5817W', 'Shandong Jingdao', 'SOD-123FL', 'Schottky 20V 1A, IFSM 25A (bridge)'),
 'C21189':   ('0603WAF0000T5E', 'UNI-ROYAL', '0603', '0R jumper'),
 'C1226':    ('0603WAJ0221T5E', 'UNI-ROYAL', '0603', '220R 5% 100mW'),
 'C20082':   ('H11L1SR2M', 'onsemi', 'SOP-6', 'Optoisolator, logic output (MIDI in)'),
 'C22966':   ('0603WAF2700T5E', 'UNI-ROYAL', '0603', '270R 1% 100mW'),
 'C1590':    ('CL10B104KA8NNNC', 'Samsung', '0603', '100nF 25V X7R'),
 'C114218':  ('DM3AT-SF-PEJM5', 'Hirose', 'SMD', 'microSD socket, push-push'),
 'C25600':   ('0603WAJ0473T5E', 'UNI-ROYAL', '0603', '47k 5% 100mW'),
 'C130212':  ('TPA6110A2DGNR', 'Texas Instruments', 'MSOP-8-EP', 'Headphone amplifier 150mW x2'),
 'C23344':   ('0603WAJ0223T5E', 'UNI-ROYAL', '0603', '22k 5% 100mW'),
 'C1623':    ('CL10B474KA8NNNC', 'Samsung', '0603', '470nF 25V X7R'),
 'C4216':    ('0603WAF3302T5E', 'UNI-ROYAL', '0603', '33k 1% 100mW'),
 'C3339':    ('RVT1V101M0607', 'Honor', 'SMD,D6.3xL7.7mm', '100uF 35V electrolytic'),
 'C53059594':('USBLC6-2P6', 'YTL', 'SOT-666', 'USB ESD protection'),
 'C393939':  ('TYPE-C16PIN', 'SHOU HAN', 'SMD', 'USB-C receptacle 16P, right angle'),
 'C23186':   ('0603WAF5101T5E', 'UNI-ROYAL', '0603', '5.1k 1% 100mW (USB CC)'),
 'C41714':   ('MAX9814ETD+T', 'Analog Devices', 'TDFN-14-EP(3x3)', 'Mic amplifier with AGC'),
 'C14709':   ('BLM18PG121SN1D', 'Murata', '0603', 'Ferrite bead 120R@100MHz 2A'),
 'C1607':    ('CL10A225KP8NNNC', 'Samsung', '0603', '2.2uF 10V X5R'),
 'C14675':   ('RC0603FR-07100KL', 'YAGEO', '0603', '100k 1% 100mW'),
 'C22807':   ('0603WAF1503T5E', 'UNI-ROYAL', '0603', '150k 1% 100mW'),
 'C4190':    ('0603WAF2201T5E', 'UNI-ROYAL', '0603', '2.2k 1% 100mW'),
 'C1705':    ('CL10A475KP8NNNC', 'Samsung', '0603', '4.7uF 10V X5R'),
 'C114916':  ('DC-050-T20', 'SOFNG', 'SMD', 'DC barrel jack 2.0/6.4mm, 12V 3A'),
 'C22369937':('RCA0310KJLF', 'HKR', '0603', '10k 5% 100mW'),
 'C22859':   ('0603WAF100JT5E', 'UNI-ROYAL', '0603', '10R 1% 100mW (MIDI out)'),
 'C2907549': ('FRC1210J330 TS', 'FOJAN', '1210', '33R 5% 500mW (MIDI out)'),
 'C23151':   ('0603WAF3900T5E', 'UNI-ROYAL', '0603', '390R 1% 100mW (LED green/blue)'),
 'C2960677': ('FRC2512J3R3 TS', 'FOJAN', '2512', '3.3R 5% 1W'),
 'C59873':   ('TPS62172DSGR', 'Texas Instruments', 'WSON-8-EP(2x2)', 'Buck 3.3V 500mA (OLED rail)'),
 'C237554':  ('DFE201610P-2R2M=P2', 'Murata', '0806 (2016)', '2.2uH 1.4A power inductor'),
 'C15850':   ('CL21A106KAYNNNE', 'Samsung', '0805', '10uF 25V X5R'),
 'C45783':   ('CL21A226MAQNNNE', 'Samsung', '0805', '22uF 25V X5R'),
 'C14676':   ('RC0603JR-071KL', 'YAGEO', '0603', '1k 5% 100mW (LED base)'),
 'C20526':   ('MMBT3904', 'JSCJ', 'SOT-23', 'NPN 40V 200mA (LED driver)'),
 'C23193':   ('0603WAF5100T5E', 'UNI-ROYAL', '0603', '510R 1% 100mW (LED red)'),
 'C57112':   ('0603B103K500NT', 'Fenghua', '0603', '10nF 50V X7R (encoder filter)'),
}
def natkey(r):
    m = re.match(r'([A-Za-z_]+)(\d*)', r); return (m.group(1), int(m.group(2) or 0))
lines = collections.OrderedDict(); check = []
smd_refs = sorted([r for r, p in pcb.items() if p['attr'] == 'SMD'], key=natkey)
tht_refs = sorted([r for r, p in pcb.items() if p['attr'] != 'SMD'], key=natkey)
for r in smd_refs:
    if r in ('LED1', 'LED2'): continue          # hand-soldered Würth, see HAND_SOLDER.csv
    if r not in lcsc_of: check.append(f"SMD part {r} ({sch[r]['value']}) has no LCSC number in Trey's BOM"); continue
    lines.setdefault(lcsc_of[r], []).append(r)
for r in lcsc_of:
    if r not in pcb: check.append(f"BOM designator {r} not on the board")
    elif pcb[r]['attr'] != 'SMD': check.append(f"BOM designator {r} is THT on the board")
# sanity: all refs on one line share value + footprint class in the schematic
for l, refs in lines.items():
    vals = {sch[r]['value'] for r in refs}; fps = {sch[r]['footprint'] for r in refs}
    if len(vals) > 1 or len(fps) > 1: check.append(f"{l}: mixed values/footprints {vals} {fps} on {refs}")
    for r in refs:
        if sch[r]['footprint'] != pcb[r]['fpid']: check.append(f"{r}: sch footprint {sch[r]['footprint']} != pcb {pcb[r]['fpid']}")
with open('rev4/order/BOM_JLCPCB_SMT.csv', 'w', newline='', encoding='utf-8') as f:
    w = csv.writer(f); w.writerow(['Comment', 'Designator', 'Footprint', 'JLCPCB Part #'])
    for l, refs in sorted(lines.items(), key=lambda kv: natkey(kv[1][0])):
        mpn, mfr, pkg, desc = PARTS[l]; val = sch[refs[0]]['value']
        w.writerow([f"{desc} | {mpn} ({mfr}) | sch value {val}", ','.join(sorted(refs, key=natkey)), pkg, l])
HAND = {
 'LED1': ('Würth WL-SFTW 150505M173300 RGB LED', 'top, SMD hand-solder; pads 1/3/5 cathodes to Q collectors, 2/4/6 anodes via R to +9V_FLAG; chamfered corner = pin 1'),
 'LED2': ('Würth WL-SFTW 150505M173300 RGB LED', 'as LED1'),
 'A1': ('Electrosmith Daisy Seed (Rev4)', 'bottom; 2 x 20 header rows'),
 'C23': ('100nF axial THT', 'bottom; /+3V3_OLED decoupling at J8'),
 'C24': ('100uF radial THT 6.3mm', 'bottom; /+3V3_OLED bulk at J8; observe polarity'),
 'ENCL1': ('Alps vertical rotary encoder with switch, H20mm', 'top'),
 'ENCR1': ('Alps vertical rotary encoder with switch, H20mm', 'top'),
 'Headphones1': ('Bourns PTD902-2015K-B103 dual 10k pot (B/linear)', 'bottom; bushing exits the bottom edge 9mm outside the outline'),
 'J3': ('3.5mm TRS jack, CUI (MIDI OUT)', 'bottom; panel'), 'J4': ('3.5mm TRS jack, CUI (AUDIO IN)', 'bottom; panel'),
 'J5': ('3.5mm TRS jack, CUI (AUDIO OUT)', 'bottom; panel'), 'J6': ('3.5mm TRS jack, CUI (MIDI IN)', 'bottom; panel'),
 'J7': ('3.5mm TRS jack, CUI (PHONES)', 'bottom; panel'),
 'J8': ('1x20 2.54mm header for NHD-2.7-12864WDW3 OLED', 'top; display not mounted in this build (Kyle 2026-10-13)'),
 'MK1': ('Electret microphone POM-2244P-C3310-2-R', 'top; observe polarity (pad 1 = GND)'),
 'SW1': ('Slide switch DigiKey 1101A4VQEA (silver 5A contacts)', 'bottom; power on/off'),
 'TAC_SHIFT_L1': ('90-degree tactile switch', 'bottom edge'), 'TAC_SHIFT_R1': ('90-degree tactile switch', 'bottom edge'),
 'TAC_SWITCH_1': ('6mm tactile switch, H9.5mm', 'top'), 'TAC_SWITCH_2': ('6mm tactile switch, H9.5mm', 'top'),
}
with open('rev4/order/HAND_SOLDER.csv', 'w', newline='', encoding='utf-8') as f:
    w = csv.writer(f); w.writerow(['Designator', 'Part', 'Schematic value', 'KiCad footprint', 'Side', 'Qty', 'Notes'])
    for r in sorted(tht_refs + ['LED1', 'LED2'], key=natkey):
        part, note = HAND.get(r, (sch[r]['value'], ''))
        w.writerow([r, part, sch[r]['value'], pcb[r]['fpid'].split(':')[-1], pcb[r]['side'], 1, note])
n_smt = sum(len(v) for v in lines.values())
summary = [f"SMT lines: {len(lines)}; SMT designators: {n_smt}; hand-solder designators: {len(tht_refs) + 2}; total footprints on board: {len(pcb)}",
           f"coverage: {n_smt} + {len(tht_refs) + 2} = {n_smt + len(tht_refs) + 2} of {len(pcb)}"]
summary += check or ['no inconsistencies']
open('rev4/order/BOM_check.txt', 'w').write('\n'.join(summary) + '\n'); print('\n'.join(summary))
