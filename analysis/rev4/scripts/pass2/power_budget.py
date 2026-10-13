#!/usr/bin/env python3
"""Pass-2 rev-4 power budget: rail voltages, series drops, LED currents,
resistor dissipation, ferrite/resistor loading, inrush energy.

Usage: python3 -I power_budget.py
All inputs are listed as ASSUMPTIONS; datasheet-sourced ones are tagged.
Design case: 9 V barrel only (settled 2026-10-09/13). Topology from
kicad_out/rev4/netlist.net (rev-4 schematic, verified in PASS0):
  J1 -> bridge(D2..D5, two diodes in series per polarity) -> Net-(D2-K) [C14 100n]
     -> FB3 -> FB4 -> FB5 -> Net-(C15-Pad1) [C15 100u, C16 100n]
     -> FB6 -> /+9V_FLAG [C25 10u; U6 VIN+EN; 6x LED resistors; R29]
                 -> R29 3R3 -> Net-(C17-Pad1) [C17 100u] -> R30 3R3 -> /DSY_VIN [C18 100u] -> A1.39
  (rev 3's D6, FB7 and the R31/R32/C20-C22 filter are gone; C19-C22 are now 10 nF encoder caps)
"""
# ---- ASSUMPTIONS ----
V_ADAPTER = 9.0                   # design case, settled
VF_SCHOTTKY = 0.40                # bridge D2-D5 now SOD-123F; part not yet known (rev-4 BOM pending) -> 0.40 V kept from rev 3
R_FB = 0.050                      # LCSC C14709 ferrite DCR 50 mOhm (rev-3 BOM line); rev-4 BOM pending
R_SER = 3.3                       # R29, R30 (rev-3 BOM C2960677, 1 W 2512)
I_DAISY = {'low': 0.10, 'high': 0.20}   # Daisy Seed VIN current, ESTIMATE (as rev 3)
I_OLED_3V3 = {'typ': 0.345, 'max': 0.375}  # NHD-2.7-12864WDW3 IDD (NHD datasheet, rev-3 PASS2)
V_OLED = 3.3
EFF_BUCK = 0.88                   # TPS62172 SLVSAT8 Fig. 12/13 region
R_LED = {'R': 510.0, 'G': 390.0, 'B': 390.0}   # rev-4 values: R24/R27 510R (red), R21/R26 (blue) + R25/R28 (green) 390R
VF_LED = {'R': 2.0, 'G': 3.2, 'B': 3.2}        # Würth 150505M173300 datasheet typ Vf (settled fact, rev-3 R3-P2-04)
IF_RATED = 0.030                                # Würth IF 30 mA per die
VCE_SAT = 0.2; R_BASE = 1000.0; V_GPIO = 3.3; VBE = 0.85   # onsemi MMBT3904
P_0603 = 0.100; P_2512 = 1.0
N_LED_ON = 6

def ipc(width_mm, dT=10.0, t_mm=0.035):
    a = (width_mm/0.0254)*(t_mm/0.0254); return 0.048*dT**0.44*a**0.725

print('=== LED driver per channel ===')
ib = (V_GPIO - VBE)/R_BASE
print(f'Ib = {ib*1000:.2f} mA (VBE(sat) max); saturation Ic at forced beta 10: {ib*10*1000:.0f} mA')

for dk, idaisy in I_DAISY.items():
    for ok, ioled in I_OLED_3V3.items():
        i_led_total = N_LED_ON*0.012; i_u6 = 0
        for _ in range(30):
            i_flag_load = i_led_total + i_u6           # everything on /+9V_FLAG except the Daisy branch
            i_total = idaisy + i_flag_load             # through bridge, FB3..FB6
            v_bridge = V_ADAPTER - 2*VF_SCHOTTKY
            v_c15 = v_bridge - i_total*3*R_FB
            v_flag = v_c15 - i_total*R_FB
            v_c17 = v_flag - idaisy*R_SER
            v_dsy = v_c17 - idaisy*R_SER
            i_u6 = (V_OLED*ioled)/(EFF_BUCK*max(v_flag, 3.3))
            i_led = {c: max(0.0, (v_flag - VF_LED[c] - VCE_SAT)/R_LED[c]) for c in 'RGB'}
            i_led_total = 2*sum(i_led.values())
        p_led = {c: i_led[c]**2*R_LED[c] for c in 'RGB'}
        print(f"\n--- 9 V, I_daisy={idaisy} A ({dk}), OLED IDD={ioled} A ({ok}) ---")
        print(f"  bridge out {v_bridge:.2f} V | C15 node {v_c15:.2f} V | /+9V_FLAG (LED + U6 VIN) {v_flag:.2f} V (TPS62172 3-17 V) | C17 node {v_c17:.2f} V | DSY_VIN {v_dsy:.2f} V (Daisy 4-17 V)")
        print(f"  I_total {i_total*1000:.0f} mA through FB3/4/5/6 (2 A rated) | I_U6 {i_u6*1000:.0f} mA | I_LED(all 6 on) {i_led_total*1000:.0f} mA")
        print(f"  LED currents R/G/B: {i_led['R']*1000:.1f}/{i_led['G']*1000:.1f}/{i_led['B']*1000:.1f} mA (Würth IF 30 mA)")
        print(f"  P(R_LED) R/G/B: {p_led['R']*1000:.0f}/{p_led['G']*1000:.0f}/{p_led['B']*1000:.0f} mW vs 100 mW 0603 | P(R29/R30) {idaisy**2*R_SER*1000:.0f} mW vs 1 W")
        print(f"  Ic/Ib red/green: {i_led['R']/ib:.1f}/{i_led['G']/ib:.1f} (saturated if < 10)")

print('\n=== Inrush / stored energy (9 V) ===')
v = V_ADAPTER
e_total = 0.5*(3*100e-6)*(v-0.8)**2 + 0.5*10e-6*(v-0.8)**2
print(f"Bulk on the ~8 V side: C15, C17, C18 = 3 x 100 uF + C25 10 uF (rev 3: 7 x 100 uF); stored {e_total*1000:.1f} mJ")
print(f"Unlimited-path caps: C15 (100 uF) behind 3 beads + 2 Schottky; C25 (10 uF) behind 4 beads. Rev 3 had C15+C19 = 200 uF.")
for rb in (0.050, 0.200):
    print(f"  bead DCR {rb*1000:.0f} mOhm: Ipk ~ (V-2*0.4)/(3*{rb} + ESR 0.1 + adapter 0) = {(v-0.8)/(3*rb+0.1):.0f} A into C15 (stiff adapter)")
print(f"C17 limited to {(v-0.8)/3.3:.1f} A by R29; C18 by R29+R30 ({(v-0.8)/6.6:.1f} A).")
print('Bridge diodes D2-D5: now SOD-123F footprint; part/surge rating unknown until the rev-4 BOM arrives (rev 3: C727114 1N5817WS 1 A / 9 A IFSM).')

print('\n=== IPC-2221 external 1 oz, dT=10 C ===')
for w in [0.1, 0.2, 0.3, 0.5]: print(f"  {w} mm -> {ipc(w):.2f} A")
