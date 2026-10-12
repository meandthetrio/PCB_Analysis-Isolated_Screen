#!/usr/bin/env python3
"""Seed 3 Dev Kits — Pass-2 power budget arithmetic (python3 -I, stdlib only).

Every number is derived from the netlist topology (kit_power_geom.py / netlist_parse.py output) plus the
assumptions listed in ASSUMPTIONS below.  Sources for the fixed figures are cited in the report.
Usage: python3 -I kit_power_budget.py euro|pedal
"""
import sys, math

ASSUMPTIONS = {
  'seed_vin_current_A': (0.10, 0.20, 0.30),   # Seed3 datasheet publishes no VIN current; rev-3 PASS2 used 0.10-0.20 A; 0.30 A = SD + USB device worst case
  'nsr1020_vf': {0.1: 0.33, 0.5: 0.44, 1.0: 0.54},   # onsemi NSR1020MW2T3G max VF at 100 mA / 500 mA / 1 A
  'bead_dcr_ohm': 0.20,          # Chilisin PBY160808T-601Y-N DCR 200 mOhm (BOM line; JLCPCB part page)
  'bead_rated_A': 1.0,           # JLCPCB part page for C108301
  'r3r3': 3.3, 'r3r3_W': 0.75,   # KOA SG73P2BTTD3R30F 1206 0.75 W (BOM)
  'tl072_icc_per_amp_mA': (1.4, 2.5),   # TI TL072 ICC typ/max per amplifier (datasheet)
  'opa1652_iq_per_amp_mA': (2.0, 2.5),  # TI OPA1652 IQ typ/max per amplifier
  'mcp600x_iq_per_amp_mA': 0.1,  # Microchip MCP6002/4 IQ 100 uA typ per amplifier (model memory; datasheet host blocked)
  'cd4051_iq_mA': 0.01,
  'lm4040_10_irmin_uA': 100.0,   # TI LM4040-N-10.0 IRMIN 100 uA
  'ldo_iq_mA': 0.9,              # LP2985 IGND max at 150 mA (new chip)
  'gpio_ron_ohm': 25.0,          # STM32H750 output stage estimate (model memory)
  # LED Vf at 20 mA (Kingbright WP154A4SUREQBFZGW / WP7113ID datasheets unreachable: model memory, flagged in report)
  'led_vf_20mA': {'red_AlGaInP': 1.95, 'green_InGaN': 3.3, 'blue_InGaN': 3.3, 'red_WP7113ID': 2.0},
  'led_vf_slope_per_decade': {'red_AlGaInP': 0.10, 'green_InGaN': 0.17, 'blue_InGaN': 0.17, 'red_WP7113ID': 0.10},
}

def vf_diode(i):
    """NSR1020 VF (max) interpolated in log(I) between the datasheet points."""
    pts = sorted(ASSUMPTIONS['nsr1020_vf'].items())
    if i <= pts[0][0]: return pts[0][1]
    for (i0, v0), (i1, v1) in zip(pts, pts[1:]):
        if i <= i1:
            return v0 + (v1 - v0) * (math.log(i) - math.log(i0)) / (math.log(i1) - math.log(i0))
    return pts[-1][1]

def led_current(vsup, R, vf20, slope):
    """GPIO sources through R into an LED to GND. Solve I = (vsup - I*Ron - Vf(I))/R with Vf(I) = vf20 + slope*log10(I/20mA)."""
    I = 1e-3
    for _ in range(200):
        vf = vf20 + slope * math.log10(max(I, 1e-6) / 0.020)
        I_new = max((vsup - I * ASSUMPTIONS['gpio_ron_ohm'] - vf) / R, 0.0)
        I = 0.5 * I + 0.5 * I_new
    vf = vf20 + slope * math.log10(max(I, 1e-6) / 0.020) if I > 0 else vf20
    return I, vf

def ipc(width_mm, dT=10.0, t=0.035):
    a = (width_mm/0.0254)*(t/0.0254); return 0.048*dT**0.44*a**0.725

def euro():
    print('=== EURORACK DEV KIT REV3 ===')
    print('Rail tree: P1 +12V -> FB2 -> D1 (NSR1020, series) -> +12V node [C39 100u, C50 10u, C2 100n] -> R5 3R3 -> [C46 100u] -> R9 3R3 -> DSY_VIN [C49 100u] -> A1.39')
    print('           P1 -12V -> FB3 -> D2 (series) -> -12V node [C44 100u, C51 10u, C33 100n]; +12V/-12V also feed U1/U13/U15 TL072 and R32 2k -> LM4040-10 (-10V_REF)')
    tl = ASSUMPTIONS['tl072_icc_per_amp_mA']
    i_tl_typ, i_tl_max = 6 * tl[0] / 1000, 6 * tl[1] / 1000     # 3 packages x 2 amps
    i_ref = (12 - 10) / 2000                                     # R32 from -12V to -10V_REF
    print(f'TL072 x3: {i_tl_typ*1000:.1f} mA typ / {i_tl_max*1000:.1f} mA max from each of +12V and -12V (no output load); LM4040 string {i_ref*1000:.2f} mA from -12V')
    # LM4040 operating current margin
    i_load_ref = 4 * (1.65 + 10) / 200e3   # four 200k resistors from -10V_REF to the 1.65 V summing nodes
    print(f'LM4040-10: IR = {i_ref*1e6:.0f} uA - load {i_load_ref*1e6:.0f} uA (4 x 200k to 1.65 V) = {(i_ref-i_load_ref)*1e6:.0f} uA vs IRMIN 100 uA (TI) -> margin {(i_ref-i_load_ref)/100e-6:.1f}x; at -12V -10 % (10.8 V): {((0.8/2000)-i_load_ref)*1e6:.0f} uA')
    print('\nDSY_VIN vs Seed current (Vin 12.0 V, FB2 0.2 ohm, D1 VF(max) interpolated, R5+R9 = 6.6 ohm):')
    print('I_seed | I_+12V total | V(+12V node) | V(C46) | DSY_VIN | P(R5)=P(R9) | P(D1) | I/rating FB2 | I/rating D1')
    for i_seed in ASSUMPTIONS['seed_vin_current_A']:
        i_tot = i_seed + i_tl_max + 0.010   # + CV-out/audio-out load allowance 10 mA
        v_node = 12.0 - i_tot * ASSUMPTIONS['bead_dcr_ohm'] - vf_diode(i_tot)
        v_c46 = v_node - i_seed * 3.3
        v_vin = v_c46 - i_seed * 3.3
        print(f'{i_seed:.2f} A | {i_tot*1000:.0f} mA | {v_node:.2f} V | {v_c46:.2f} V | {v_vin:.2f} V | {i_seed**2*3.3*1000:.0f} mW of 750 | {i_tot*vf_diode(i_tot)*1000:.0f} mW | {i_tot/ASSUMPTIONS["bead_rated_A"]*100:.0f} % | {i_tot/1.0*100:.0f} %')
    print('-12V rail: I = TL072 + LM4040 string = %.1f mA max -> D2 drop %.2f V, FB3 %.3f V -> -12V node = -%.2f V' % ((i_tl_max+i_ref)*1000, vf_diode(i_tl_max+i_ref), (i_tl_max+i_ref)*0.2, 12 - vf_diode(i_tl_max+i_ref) - (i_tl_max+i_ref)*0.2))
    # Inrush
    c_unlimited_pos = 100e-6 + 10e-6 + 0.1e-6
    c_pos_total = c_unlimited_pos + 100e-6 + 100e-6
    c_neg_total = 100e-6 + 10e-6 + 0.1e-6
    print(f'\nInrush: +12V side caps {c_pos_total*1e6:.0f} uF ({c_unlimited_pos*1e6:.0f} uF behind only FB2 + D1; C46/C49 behind 3.3/6.6 ohm); -12V side {c_neg_total*1e6:.0f} uF behind FB3 + D2')
    e = 0.5*c_pos_total*12**2 + 0.5*c_neg_total*12**2
    print(f'  stored energy at +/-12 V: {e*1000:.1f} mJ; peak into C39+C50 limited by FB2 DCR 0.2 ohm + D1 + cap ESR + bus Zout: ~{(12-0.5)/(0.2+0.1):.0f} A if the bus were stiff (it is not: Eurorack supplies current-limit)')
    print(f'  C46 charge peak {(12-0.5)/3.3:.1f} A through R5 (0.75 W 1206, single pulse); C49 peak {(12-0.5)/6.6:.1f} A')
    # CV in
    print('\nCV in (per channel): Vout = -(33k/100k) Vin - (33k/200k)(-10 V) = -0.33 Vin + 1.65 V')
    for vin in (-5, 0, 5, 10, -10, 12, -12):
        vo = -0.33*vin + 1.65
        vo_cl = min(max(vo, 0.0), 3.3)
        # summing node when clamped
        vnode = (vin/100e3 + (-10)/200e3 + vo_cl/33e3) / (1/100e3 + 1/200e3 + 1/33e3)
        print(f'  Vin {vin:+3d} V -> ideal {vo:+.2f} V, op-amp output {vo_cl:.2f} V (rails 0/3.3), summing node {vnode:+.2f} V, input current through 100k {abs(vin-vnode)/100e3*1e6:.0f} uA')
    print(f'  ADC-node LPF: 33k || 1nF -> fc {1/(2*math.pi*33e3*1e-9):.0f} Hz')
    # Gate in
    print('\nGate in: tip -> 100k -> base (1M to GND); collector 10k to +3V3, 100R to GPIO. Threshold Vin ~ 0.65 V x (1.1) + Ib*100k ~ %.2f V; at -12 V input the B-E junction is reverse-biased, current (12-6)/100k = %.0f uA (MMBT3904 VEBO 6 V abs max; current-limited)' % (0.65*1.1 + 0.65/10e3/100*100e3, (12-6)/100e3*1e6))
    # CV out
    g = 1 + 62e3/120e3
    print(f'\nCV out: TL072 non-inverting gain 1 + 62k/120k = {g:.3f} -> DAC 0..3.3 V -> {0:.2f}..{3.3*g:.2f} V, 100R series; 5 V into 100k load {5/100e3*1e3:.2f} mA; short to GND {5/100:.0f} mA (TL072 output short-circuit protected)')
    # Audio
    print(f'Audio in: gain -10k/100k = -0.1 -> 10 Vpp -> 1.0 Vpp ({10*0.1/2/math.sqrt(2):.2f} Vrms, {20*math.log10(10*0.1/2/math.sqrt(2)/1.0):.1f} dBFS at 1 Vrms = 0 dBFS); 20 Vpp -> 2 Vpp (abs max 3.6 Vpp); Seed abs max reached at {3.6/0.1:.0f} Vpp input; fc 10k||330pF = {1/(2*math.pi*10e3*330e-12)/1e3:.0f} kHz')
    print(f'Audio out: gain -100k/10k = -10 -> 0 dBFS 2.83 Vpp -> 28 Vpp (clips at TL072 VOM ~ +/-10.5 V on +/-12 V: ~21 Vpp); 10 Vpp out = 1 Vpp codec = {20*math.log10(1/2/math.sqrt(2)):.1f} dBFS; fc 100k||33pF = {1/(2*math.pi*100e3*33e-12)/1e3:.0f} kHz; 100R out')
    # MIDI
    print(f'\nMIDI out (3.3 V, 10R + 10R): loop current into a 220R + ~1.2 V opto receiver = {(3.3-1.2)/(10+10+220)*1000:.1f} mA; thru (same values from MIDI_RX node): H11L1 sinks 270R pull-up {3.3/270*1000:.1f} mA + thru loop {(3.3-1.2)/(240)*1000:.1f} mA = {(3.3/270+(3.3-1.2)/240)*1000:.1f} mA when low')
    leds()

def pedal():
    print('=== PEDAL DEV KIT REV3 ===')
    print('Rail tree: J8 (+ on pin 2, centre-negative) -> [C20 100n] -> FB10 -> FB4 -> FB5 -> [C21 100u, C22 100n] -> D5 NSR1020 (series) -> FB9 -> +9V [C13 100u]')
    print('   +9V -> R30 3R3 -> [C41 100u] -> R6 3R3 -> DSY_VIN [C36 100u] -> A1.39')
    print('   +9V -> R48 3R3 -> [C14 100u] -> R55 3R3 -> +9V_A [C23, C24 100u; C4, C17, C25 100n] -> U3/U9/U10 OPA1652 V+, R10 10k bias, R57 3R3 -> LP2985 VIN [C16 100n, C26 10u, C27 100u]')
    print('   LP2985 -> +5V [C15 10u MLCC, C18 10u, C43 100u] -> FB1 -> +5V_A [C19 10u, C2, C31 100n] -> U1 MCP6002 V+, R46 100R -> J6 ring (expression pot supply)')
    opa = ASSUMPTIONS['opa1652_iq_per_amp_mA']
    i_opa_typ, i_opa_max = 6*opa[0]/1000, 6*opa[1]/1000
    i_bias = 9.0/20e3
    i_5v = 2*ASSUMPTIONS['mcp600x_iq_per_amp_mA']/1000 + 5.0/10e3 + ASSUMPTIONS['ldo_iq_mA']/1000   # MCP6002 + 10k expression pot + LDO IGND
    i_ana_typ, i_ana_max = i_opa_typ + i_bias + i_5v, i_opa_max + i_bias + i_5v
    print(f'+9V_A branch: OPA1652 x3 = {i_opa_typ*1000:.0f}/{i_opa_max*1000:.0f} mA typ/max + bias divider {i_bias*1000:.2f} mA + LDO branch {i_5v*1000:.2f} mA (MCP6002 0.2 mA, 10k expression pot 0.5 mA, IGND) = {i_ana_typ*1000:.1f}/{i_ana_max*1000:.1f} mA')
    print('\nI_seed | I_total | V(D5 anode) | +9V | DSY_VIN | +9V_A | LP2985 VIN | P(R30)=P(R6) | P(D5) | I/FB rating | I/D5 rating')
    for i_seed in ASSUMPTIONS['seed_vin_current_A']:
        i_tot = i_seed + i_ana_max
        v_a = 9.0 - i_tot * 3 * ASSUMPTIONS['bead_dcr_ohm']
        v9 = v_a - vf_diode(i_tot) - i_tot * ASSUMPTIONS['bead_dcr_ohm']
        v_vin = v9 - i_seed * 6.6
        v9a = v9 - i_ana_max * 6.6
        v_ldo = v9a - i_5v * 3.3
        print(f'{i_seed:.2f} A | {i_tot*1000:.0f} mA | {v_a:.2f} V | {v9:.2f} V | {v_vin:.2f} V | {v9a:.2f} V | {v_ldo:.2f} V | {i_seed**2*3.3*1000:.0f} mW of 750 | {i_tot*vf_diode(i_tot)*1000:.0f} mW | {i_tot/ASSUMPTIONS["bead_rated_A"]*100:.0f} % | {i_tot/1.0*100:.0f} %')
    print(f'LP2985: Vin-Vout = ~3.3 V at {i_5v*1000:.1f} mA -> {3.3*i_5v*1000:.0f} mW in SOT-23-5 (RthJA 205 C/W -> +{3.3*i_5v*205:.1f} C); Iout {i_5v*1000:.1f} mA of 150 mA')
    # Inrush
    c_unl = 100e-6 + 0.1e-6 + 100e-6 + 0.1e-6   # C21, C22, C13, C20
    c_tot = c_unl + 100e-6*6 + 10e-6*3 + 0.1e-6*6
    print(f'\nInrush: 9 V side total ~{c_tot*1e6:.0f} uF; {c_unl*1e6:.0f} uF (C20, C21, C22, C13) behind only 4 beads (0.8 ohm DCR) + D5; C41/C14 behind 3.3 ohm; C36/C23/C24 behind 6.6; C27/C26 behind 9.9 ohm')
    print(f'  stored energy at 9 V: {0.5*c_tot*81*1000:.1f} mJ; peak into C21 ~ (9-0.5)/(0.6 ohm + ESR + adapter Zout) ~ {(9-0.5)/0.7:.0f} A from a stiff adapter (beads saturate; DCR remains); into C13 through D5 + FB9: {(9-0.5)/0.9:.0f} A; C41 via R30 {(8.5)/3.3:.1f} A')
    # expression
    vmax5 = 5.0*1.015
    print(f'\nExpression: J6 ring = +5V_A via 100R; tip -> 1M to GND -> MCP6002 buffer -> 10k/20k divider (x{20/30:.3f}) + 10nF -> A1.28 (ADC_6, pin 28 = 3.3 V-only). Max at pin: 5.00 V x 0.667 = {5*2/3:.3f} V; with LP2985 +1.5 % and VOH = VDD: {vmax5*2/3:.3f} V; divider fc {1/(2*math.pi*(10e3*20e3/30e3)*10e-9):.0f} Hz')
    print('Audio in: 1M || (AC-coupled 10u) -> OPA1652 unity buffer (100R/100pF) -> 3k3/4k7 divider x%.3f, 1nF -> fc %.0f kHz -> 10u -> inverting unity (10k/10k, 270pF -> fc %.0f kHz) -> 100R + 33nF (fc %.0f kHz) -> Seed AUDIO IN; chain biased at AREF = +9V_A/2 ~ 4.2 V (DC reaches the Seed pin; Seed input is AC coupled per datasheet Table 1 footnote)' % (4.7/8.0, 1/(2*math.pi*(3.3e3*4.7e3/8e3)*1e-9)/1e3, 1/(2*math.pi*10e3*270e-12)/1e3, 1/(2*math.pi*100*33e-9)/1e3))
    print('Audio out: Seed AUDIO OUT -> 10u -> 15k -> OPA1652 inverting x%.2f (33k || 100pF fc %.0f kHz) -> 100R -> 10u -> jack (10k bleed): 0 dBFS 2.83 Vpp -> %.1f Vpp (OPA1652 swing on 8.3 V single supply ~ 6.7 Vpp with 2k load, less into 10k||jack)' % (33/15, 1/(2*math.pi*33e3*100e-12)/1e3, 2.83*33/15))
    print(f'\nMIDI out/thru as Eurorack: loop {(3.3-1.2)/240*1000:.1f} mA; H11L1 sink when low {(3.3/270+(3.3-1.2)/240)*1000:.1f} mA (270R pull-up + thru loop). MIDI IN has NO anti-parallel diode across the H11L1 LED (Euro has D3).')
    leds()

def leds():
    print('\nLED currents (GPIO sources at 3.3 V through R into LED to GND; Vf model = Vf(20 mA) + slope*log10(I/20 mA)):')
    rows = [('RGB red (2k)', 2000, 'red_AlGaInP'), ('RGB green (2k)', 2000, 'green_InGaN'), ('RGB blue (2k)', 2000, 'blue_InGaN'),
            ('mono red WP7113ID (2k, Euro LED2)', 2000, 'red_WP7113ID'), ('mono red WP7113ID (1k, Pedal LED1)', 1000, 'red_WP7113ID')]
    for name, R, k in rows:
        vf20 = ASSUMPTIONS['led_vf_20mA'][k]; sl = ASSUMPTIONS['led_vf_slope_per_decade'][k]
        I, vf = led_current(3.3, R, vf20, sl)
        I_fixed = max((3.3 - vf20)/R, 0)
        print(f'  {name:36s}: Vf20 {vf20:.2f} V -> I {I*1000:.2f} mA at Vf {vf:.2f} V (Vf held at 20 mA value: {I_fixed*1000:.2f} mA); {I/0.020*100:.1f} % of 20 mA; P(R) {I*I*R*1000:.2f} mW; GPIO VOH drop {I*25*1000:.0f} mV')
    print('  3.0 V supply (rail sag) green/blue:', f'{led_current(3.0, 2000, 3.3, 0.17)[0]*1000:.2f} mA')

if __name__ == '__main__':
    {'euro': euro, 'pedal': pedal}[sys.argv[1]]()
