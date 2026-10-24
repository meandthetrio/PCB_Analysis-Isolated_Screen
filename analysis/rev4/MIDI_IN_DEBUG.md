# Rev 4 — MIDI IN (J6) bench checklist

**Symptom:** MIDI in through a DIN adapter does nothing on the rev-4 boards. Continuity and voltage checks look right.

**What the files say:** the rev-4 MIDI-in stage is the Daisy Pod's MIDI-in stage part for part — 0 Ω links R2/R3, 220 Ω R5, NSR1020 antiparallel diode D1 (LCSC C385198), H11L1 opto U1 (C20082, onsemi H11L1SR2M), 270 Ω pull-up R6 to +3V3_D, TRS **Type A** wiring (ring = DIN pin 4, tip = DIN pin 5), Seed pin 15 (D14, USART1_RX). It is identical in rev 2, rev 3 and rev 4, and D1 / U1 polarity is correct in the board file. So the fault is in assembly, the adapter, or firmware. Work the list in order.

---

## 1. Loopback with a plain stereo 3.5 mm cable (no DIN adapter)

- **Do:** connect MIDI OUT (J3) straight to MIDI IN (J6) with an ordinary TRS-to-TRS cable. Run firmware that echoes or logs incoming MIDI and send any message.
- **Why:** the out stage pushes ≈ 8 mA through the in stage, so this exercises the whole receiver path without any adapter in the loop.
- **Pass:** hardware is fine; suspect the DIN adapter type (see questions) or the sending device.
- **Fail:** continue with step 2.

## 2. Check D1 orientation (meter in diode mode)

- **Do:** red probe on U1 pin 1 (the R5 end of D1), black probe on U1 pin 2 (the R3 end of D1).
- **Expect:** **1.1 – 1.3 V** — the opto LED's forward drop. Reversed probes should read **0.3 – 0.4 V** from D1.
- **Fault:** about **0.3 V in both directions** means D1 was placed backwards and is shunting the opto LED. The receiver is dead but every continuity check passes. This is the classic JLCPCB placement-rotation error and the one item left for Trey to verify in the order package.
- **Fix:** lift D1 and refit it rotated 180°, or leave it off for a quick test (MIDI in works without it; it only protects against reversed cables).

## 3. Static drive test

- **Do:** take 3.3 V from the board (Seed pin 38 or either end of R6's 3V3 side), through a **220 – 470 Ω** resistor, onto the **J6 ring pad** (R2 pad 1). Tie the **J6 tip pad** (R3 pad 1) to **GND**.
- **Expect:** U1 pin 4 — also R6 pad 1 and Seed pin 15 — drops from **3.3 V to under 0.4 V**.
- **If it does not drop:** measure across R5. About **1 V** means LED current is flowing, so U1 itself is the problem (dead, rotated, or not wetted on the gull-wing pads — the custom SOP-6 footprint lands the leads at the outer edge of the pads). Near **0 V** means no current: open R2/R5 or a bad jack solder joint.
- **Then swap the polarity** (3.3 V to tip, GND to ring). If pin 4 only drops this way, the jack footprint has tip and ring swapped and the board is effectively **Type B** — use a Type B adapter or swap the R2/R3 routing on the next spin.

## 4. Idle voltages at U1 (nothing plugged in)

| Pin | Expect | If wrong |
|---|---|---|
| U1 pin 6 (Vcc) | 3.3 V | +3V3_D not reaching U1 — trace or pad |
| U1 pin 5 (GND) | 0 V | GND pad not soldered |
| U1 pin 4 (Vo) | 3.3 V via R6 | 0 V = output stuck low (U1 rotated or dead), or R6 open |
| U1 pins 1–2 | 0 V across | any DC here means something is driving the LED |

## 5. Firmware

- Confirm the build initialises MIDI on **USART1, RX = D14 (Seed pin 15), TX = D13 (Seed pin 14)**, the same pins the Pod uses, and not USB MIDI.
- Nothing moved between the Pod and rev 4 for MIDI, so a Pod MIDI setup reused unchanged should work. The H11L1 output is inverting and open-collector, idle high through R6 — standard UART idle, no inversion flag needed.
- Sanity check with step 1 (loopback) running: with notes being sent, a meter on Seed pin 15 should read slightly **below 3.3 V** (the average of a mostly-high UART line); a steady 3.3 V means no data is arriving at the Seed.

---

## Three questions that narrow this fast

1. **Which DIN-to-TRS adapter, and did the same one work on the Pod?** The Pod is Type A like this board. A Type B adapter (Arturia, Novation, some Korg) reverse-biases the opto LED: MIDI in is silent while every static measurement looks perfect.
2. **Does MIDI OUT work through the same adapter?** If out works and in does not, jack polarity is consistent and the fault is downstream of J6 (steps 2–4).
3. **Was MIDI in ever tested on a rev-2 board?** If it worked there, the custom jack and SOP-6 footprints are proven and only assembly and adapter remain.

*Sources: rev-4 netlist (`kicad_out/rev4/netlist.net`), rev-4 board pads/silk (`rev4/WavetableController.kicad_pcb`), rev-4 BOM, Pod review (`analysis/daisy_pod/`, DP-P2-12).*
