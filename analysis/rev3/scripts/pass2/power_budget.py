#!/usr/bin/env python3
"""Pass-2 rev-3 power budget: rail voltages, series drops, LED currents,
resistor dissipation, ferrite/resistor loading, inrush energy.

Usage: python3 -I power_budget.py
All inputs are listed as ASSUMPTIONS at the top; datasheet-sourced ones are
tagged with their source. Topology from kicad_out/rev3/netlist.net (Pass-2 map):
  J1 -> bridge(D2..D5, two diodes in series per polarity) -> FB3->FB4->FB5 -> D6 -> FB6
     -> node N19 (C19) -> R29 3R3 -> C17 -> R30 3R3 -> /DSY_VIN (Daisy A1.39, C18)
                       -> R31 3R3 -> C20 -> R32 3R3 -> /+9V_FLAG (C21,C22; 6x300R LED; FB7 -> U6 VIN)
"""
# ---- ASSUMPTIONS ----
V_ADAPTER = [9.0, 12.0]           # 9 V = design intent (rev-2 SOURCE_OF_TRUTH); 12 V = J1 jack rating in BOM (C114916), Daisy VIN max 17 V
VF_SCHOTTKY = 0.40                # LCSC C727114 (BOM: '750mV@3A'); ~0.35-0.45 V at 0.1-0.5 A assumed
R_FB = 0.050                      # LCSC C14709 ferrite DCR 50 mOhm (BOM line)
R_SER = 3.3                       # R29..R32 (BOM C2960677, 1 W 2512)
I_DAISY = {'low': 0.10, 'high': 0.20}   # Daisy Seed VIN current, ESTIMATE (no datasheet figure available; rev-2 used ~0.10 A)
I_OLED_3V3 = {'typ': 0.345, 'max': 0.375}  # NHD-2.7-12864WDW3 IDD, VDD=3.3V 100% on, default jumper (NHD.txt l.245)
V_OLED = 3.3
EFF_BUCK = 0.88                   # TPS62172 efficiency VOUT=3.3 V, IOUT 0.3-0.5 A, VIN 6-12 V (SLVSAT8 Fig. 12/13 region, read ~85-90 %)
R_LED = 300.0                     # R21,R24..R28 0603 100 mW (BOM C23025)
VF_LED = {'R': 2.1, 'G': 3.0, 'B': 3.1}   # JLCPCB listing for Cree QLS6B-FKW (same PLCC6 family): Vf R 2.1 / G 3.0 / B 3.1 V; CLS6B-FKW datasheet unreachable -> ASSUMED
IF_RATED = {'R': 0.030, 'G': 0.020, 'B': 0.020}  # CLS6B-FKW IF max per WebSearch snippet of Mouser datasheet copy (30/20/20 mA)
VCE_SAT = 0.2                     # MMBT3904 VCE(sat) max at IC=10mA/IB=1mA (onsemi MMBT3904LT1 datasheet)
R_BASE = 1000.0; V_GPIO = 3.3; VBE = 0.85   # VBE(sat) max 0.85 V at 10 mA (onsemi)
P_0603 = 0.100; P_2512 = 1.0
N_LED_ON = 6

def ipc(width_mm, dT=10.0, t_mm=0.035):
    a = (width_mm/0.0254)*(t_mm/0.0254); return 0.048*dT**0.44*a**0.725

print('=== LED driver per channel (independent of rail voltage) ===')
ib = (V_GPIO - VBE)/R_BASE
print(f'Ib = ({V_GPIO}-{VBE})/{R_BASE:.0f} = {ib*1000:.2f} mA  (VBE(sat) max {VBE} V; with VBE typ 0.7 V: {(V_GPIO-0.7)/R_BASE*1000:.2f} mA)')
print(f'Guaranteed-saturation Ic at forced beta 10 (VCE(sat) test ratio, onsemi): {ib*10*1000:.0f} mA; at hFE(min)=30 @100mA: {ib*30*1000:.0f} mA')

for vad in V_ADAPTER:
    for dk, idaisy in I_DAISY.items():
        for ok, ioled in I_OLED_3V3.items():
            # iterate: LED current depends on +9V_FLAG which depends on total current
            i_led_total = N_LED_ON*0.015; i_u6 = 0
            for _ in range(20):
                i_branch_b = i_led_total + i_u6
                i_total = idaisy + i_branch_b
                v_bridge = vad - 2*VF_SCHOTTKY
                v_d6a = v_bridge - i_total*3*R_FB
                v_n19 = v_d6a - VF_SCHOTTKY - i_total*R_FB
                v_dsy = v_n19 - idaisy*2*R_SER
                v_flag = v_n19 - i_branch_b*2*R_SER
                v_u6in = v_flag - i_u6*R_FB
                i_u6 = (V_OLED*ioled)/(EFF_BUCK*max(v_u6in, 3.3))
                i_led = {c: max(0.0, (v_flag - VF_LED[c] - VCE_SAT)/R_LED) for c in 'RGB'}
                i_led_total = 2*sum(i_led.values())
            p_led = {c: i_led[c]**2*R_LED for c in 'RGB'}
            p_rser_b = (i_branch_b)**2*R_SER
            print(f"\n--- Vadapter={vad} V, I_daisy={idaisy} A ({dk}), OLED IDD={ioled} A ({ok}) ---")
            print(f"  bridge out {v_bridge:.2f} V | after FB3-5+D6+FB6 (node C19) {v_n19:.2f} V | DSY_VIN {v_dsy:.2f} V (Daisy 4-17 V) | +9V_FLAG {v_flag:.2f} V | U6 VIN {v_u6in:.2f} V (TPS62172 3-17 V)")
            print(f"  I_total {i_total*1000:.0f} mA through FB3/4/5/6 (2 A rated) | I_U6 {i_u6*1000:.0f} mA | I_LED(all 6 on) {i_led_total*1000:.0f} mA | branch-B (R31/R32) {i_branch_b*1000:.0f} mA")
            print(f"  LED currents R/G/B: {i_led['R']*1000:.1f}/{i_led['G']*1000:.1f}/{i_led['B']*1000:.1f} mA (rated {IF_RATED['R']*1000:.0f}/{IF_RATED['G']*1000:.0f}/{IF_RATED['B']*1000:.0f})")
            print(f"  P(300R) R/G/B: {p_led['R']*1000:.0f}/{p_led['G']*1000:.0f}/{p_led['B']*1000:.0f} mW vs 100 mW 0603 | P(R31/R32) {p_rser_b*1000:.0f} mW, P(R29/R30) {idaisy**2*R_SER*1000:.0f} mW vs 1 W")
            print(f"  Ic/Ib for red: {i_led['R']/ib:.1f} (saturated if < 10)")

print('\n=== Inrush / stored energy ===')
caps_9v = {'C15': 'after FB3-5, before D6', 'C19': 'after D6+FB6, no R', 'C17': 'behind R29', 'C18': 'behind R29+R30',
           'C20': 'behind R31', 'C21': 'behind R31+R32', 'C22': 'behind R31+R32'}
for vad in V_ADAPTER:
    e = 0.5*7*100e-6*(vad-0.8)**2
    print(f"Vadapter {vad} V: 7x100uF = 700 uF, stored {e*1000:.1f} mJ; unlimited-path caps C15+C19 = 200 uF, series R before them = 4 ferrites x 50 mOhm + 2-3 Schottky; Ipk ~ (V-3*0.4)/(0.2 Ohm + ESR 0.1 + adapter) -> {(vad-1.2)/0.3:.0f} A if adapter is stiff; C17/C20 limited to {(vad-1.2)/3.3:.1f} A by R29/R31 (2512 1 W, single-pulse)")
print('Bridge diodes LCSC C727114: BOM line says 1A average, 9A (IFSM) surge; D6 same part.')

print('\n=== IPC-2221 external 1 oz, dT=10 C ===')
for w in [0.1, 0.2, 0.3, 0.5]: print(f"  {w} mm -> {ipc(w):.2f} A")
