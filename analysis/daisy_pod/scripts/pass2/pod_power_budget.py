#!/usr/bin/env python3
"""Daisy Pod Rev5 — LED drive / rail-load / amp-network arithmetic (python3 -I pod_power_budget.py).

LED topology (netlist): +3V3_D -> LED common anode (pad 2) ; cathode -> 1 k (R6-R11, 0402) -> Seed GPIO (sinks when low).
I = (V3V3 - Vf(I) - VOL(I)) / 1k.  Two Vf models per colour:
  'nominal'  : datasheet Vf at the 20 mA test current used as-is (what a quick review would do)
  'decade'   : Vf falls S volts per decade of current below the test current (AlInGaP red S=0.10 V/dec, InGaN G/B S=0.17 V/dec,
               n*kT/q*ln10 with n~1.7 / 2.9 — generic LED exponential-model slopes, ASSUMPTION, not from the Cree sheet)
VOL: STM32 output low ~ I * 25 ohm (Ron estimate, ASSUMPTION) - negligible here.
Vf sources: Cree CLS6B-FKW datasheet (same manufacturer RGB family, fetched 2026-10-09 in the rev-3 review) red 2.1 / green 3.1 / blue 3.1 V typ
            at 20 mA; max 2.6 / 3.8 / 3.8 V (the CLVBA-FKA sheet itself was unreachable 2026-10-12 — every mirror DNS-blocked).
"""
import math
V = 3.3; R = 1000.0; RON = 25.0
colours = {  # name: (Vf_typ, Vf_max, S V/decade, I_test mA, IF_max mA)
    'red':   (2.10, 2.60, 0.10, 20.0, 30.0),
    'green': (3.10, 3.80, 0.17, 20.0, 20.0),
    'blue':  (3.10, 3.80, 0.17, 20.0, 20.0),
}
def solve(vf_test, S, itest_mA, vdd=V):
    I = 1e-3  # A, start
    for _ in range(200):
        vf = vf_test - S*math.log10(itest_mA/(I*1e3)) if I > 0 else vf_test
        I_new = max((vdd - vf - I*RON)/R, 0.0)
        if I_new <= 0: return 0.0, vf
        I = 0.5*I + 0.5*I_new
    return I, vf
print('colour | Vf_typ | I nominal (mA) | I decade-model (mA) @Vf | I at Vf_max | % of IF_max (decade) | P(1k) mW | V_GPIO')
for c, (vt, vmax, S, it, ifmax) in colours.items():
    inom = max((V - vt)/R, 0)
    idec, vf = solve(vt, S, it)
    imax = max((V - vmax)/R, 0)
    print(f"{c} | {vt} | {inom*1e3:.2f} | {idec*1e3:.2f} @ {vf:.2f} V | {imax*1e3:.2f} | {idec/ (ifmax*1e-3)*100:.1f} % | {idec**2*R*1e3:.2f} | {idec*RON*1e3:.0f} mV")
# at 3.0 V (Daisy 3v3 rail sag) and with V3V3 = 3.3 for comparison with Trey's 300R/5.8 V drive
print('\nAll six on, decade model: total I =', round(sum(solve(v[0], v[2], v[3])[0] for v in colours.values())*2*1e3, 2), 'mA')
print('\nTrey rev 3 for comparison (R3-P2-04): /+9V_FLAG 5.8 V, 300 R, VCE(sat) 0.2 V, Wurth Vf R 2.0 / G,B 3.2 V ->',
      f"red {(5.8-2.0-0.2)/300*1e3:.1f} mA, G/B {(5.8-3.2-0.2)/300*1e3:.1f} mA")
# rail loads
print('\n+3V3_A loads: 2 x 10k pots =', round(2*3.3/10e3*1e3, 2), 'mA; TPA6110 Iq (SLOS314B typ ~2.5 mA, from rev-2 archive) ; P2.9 header')
print('+3V3_D loads: SD card (SD spec: up to 100 mA avg / 200 mA for UHS, order of magnitude), H11L1 Icc (datasheet 1.6 mA typ at 5 V, 270R pull-up adds 3.3/270 =',
      round(3.3/270*1e3, 1), 'mA when output low), 5 x 47k pull-ups (negligible), LEDs <=', round(sum(solve(v[0], v[2], v[3])[0] for v in colours.values())*2*1e3, 1), 'mA')
# TPA6110 network
Ri, Ci, Rf, Cb, Rb = 22e3, 470e-9, 33e3, 100e-9, 230e3
print('\nTPA6110: gain = Rf/Ri =', Rf/Ri, 'V/V; input HPF fc =', round(1/(2*math.pi*Ri*Ci), 1), 'Hz;',
      'Eq.6 bypass: Cb*230k =', round(Cb*Rb*1e3, 1), 'ms >= Ci*Ri =', round(Ci*Ri*1e3, 1), 'ms ->', Cb*Rb >= Ci*Ri)
for RL in (16, 32):
    print(f'  output 100uF into {RL} ohm: fc = {1/(2*math.pi*RL*100e-6):.0f} Hz')
# IPC-2221 / DC resistance for the measured +3V3_D copper
def ipc(w, dT=10, t=0.035):
    a=(w/0.0254)*(t/0.0254); return 0.048*dT**0.44*a**0.725
def rmm(w, t=0.035): return 1.72e-8/((w*1e-3)*(t*1e-3))  # ohm/m == mOhm/mm
for w in (0.2032, 0.254, 0.3, 0.4064):
    print(f'w {w} mm: IPC-2221 ext dT10 = {ipc(w):.2f} A, {rmm(w):.2f} mOhm/mm')
print('+3V3_D U1.38 -> farthest load P2.10 57.1 mm @0.4064 ->', round(57.1*rmm(0.4064)), 'mOhm; -> P1.4 35.3 mm ->', round(35.3*rmm(0.4064)), 'mOhm;',
      'Trey rev3 249 mm @0.3 ->', round(249*rmm(0.3)), 'mOhm')
