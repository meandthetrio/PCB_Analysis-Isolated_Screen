"""Classify nets of a kit board into digital aggressors and analogue victims by name pattern; print two CSV lists."""
import sys, json, re
p=json.load(open(sys.argv[1])); nets=[n for n in p['nets'] if not n.startswith('unconnected')]
AGG=re.compile(r'(SDMMC|USB_|MIDI|LED|TAC_SW|TOG_SW|MUX_CTRL|GATEIN|FSW|SDMMC_DETECT|J7-CC|J_MIDI|J1[01]-|J1-[45]|Q[12]-|LED[12]-|R4-Pad2|D3-K)')
VIC=re.compile(r'(CODEC|CV_|POT|DAC_CV|AUDIO|U1A|U1B|U15A|U15B|U3A|U3B|U9A|U9B|U10A|U10B|C17-Pad1|C4-Pad1|C21-Pad1|C22-Pad1|C5-Pad2|C11-Pad2|C32-Pad2|C38-Pad2|R49-Pad1|R57-Pad1|EXPRESSION|AREF|U2[A-D]--|J_CV|J_AUDIO|J[2-6]-Pad|C29-Pad1|C7-Pad1|C3-Pad1|C48-Pad1|C6-Pad2|C10-Pad|C35-Pad1|C42-Pad2|\+3V3_A|-10V_REF|J6-PadR)')
agg=[n for n in nets if AGG.search(n)]; vic=[n for n in nets if VIC.search(n) and n not in agg]
agg.append('+3V3')
print(','.join(agg)); print(','.join(vic))
