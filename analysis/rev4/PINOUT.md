# Rev 4 — Daisy Seed (A1) pin assignment

Source: rev-4 netlist (`kicad_out/rev4/netlist.net`, exported from
`rev4/WavetableController.kicad_sch`). Seed "D" names and STM32 pins are from the
Daisy Seed rev 5/7 pinout; physical pin = D+1 for pins 1–15, D+7 for pins 22–37.
Pins marked **3V3-only** (24, 25, 28, 29, 30) must never see 5 V.

| Seed pin | D name | STM32 | Seed function | Rev-4 net | Goes to | Role on the board |
|---|---|---|---|---|---|---|
| 1 | D0 | PB12 | USB_ID | /RES_SPI | J8.16 | OLED reset (output; no pull-up on board) |
| 2 | D1 | PC11 | SD_DATA_3 | /SD_D3 | P1.2, R10 | microSD DAT3 (10 k pull-up) |
| 3 | D2 | PC10 | SD_DATA_2 | /SD_D2 | P1.1, R11 | microSD DAT2 (10 k pull-up) |
| 4 | D3 | PC9 | SD_DATA_1 | /SD_D1 | P1.8, R7 | microSD DAT1 (10 k pull-up) |
| 5 | D4 | PC8 | SD_DATA_0 | /SD_D0 | P1.7, R8 | microSD DAT0 (10 k pull-up) |
| 6 | D5 | PD2 | SD_CMD | /SD_CMD | P1.3, R9 | microSD CMD (10 k pull-up) |
| 7 | D6 | PC12 | SD_CLK | /SD_CK | P1.5 | microSD CLK |
| 8 | D7 | PG10 | SPI1_CS | /CS_SPI | J8.17 | OLED chip select |
| 9 | D8 | PG11 | SPI1_SCK | /SCLK_SPI | J8.7 | OLED clock |
| 10 | D9 | PB4 | SPI1_POCI (MISO) | /TAC_SHIFT_R | TAC_SHIFT_R1 | Right shift button (input, pull-up; SPI1 must be TX-only) |
| 11 | D10 | PB5 | SPI1_PICO (MOSI) | /SD_IN_SPI | J8.8 | OLED data in |
| 12 | D11 | PB8 | I2C1_SCL | /ENCR_A | ENCR1.A, R34, C21 | Right encoder A (10 k + 10 nF at the encoder) |
| 13 | D12 | PB9 | I2C1_SDA | /ENCR_B | ENCR1.B, R41, C22 | Right encoder B |
| 14 | D13 | PB6 | USART1_TX | /USART1_TX | R1 | MIDI out (via R1) |
| 15 | D14 | PB7 | USART1_RX | /USART1_RX | U1.4, R6 | MIDI in (6N138 opto U1) |
| 16 | — | — | AUDIO_IN_1 | AUDIO_IN_L | J4.T | Line in L |
| 17 | — | — | AUDIO_IN_2 | AUDIO_MIC_IN_R | C12 | Mic preamp output (MK1 path), right channel |
| 18 | — | — | AUDIO_OUT_1 | AUDIO_OUT_L | J5.T, Headphones1.1 | Line out L / headphone pot |
| 19 | — | — | AUDIO_OUT_2 | AUDIO_OUT_R | J5.R, Headphones1.4 | Line out R / headphone pot |
| 20 | — | — | AGND | GND | plane | Analog ground |
| 21 | — | — | 3V3_A | /+3V3_A | FB2, U3, U4, C5 | 3.3 V analog rail (feeds mic preamp U3, headphone amp U4) |
| 22 | D15 | PC0 | ADC_0 | /ENCL_CLICK | ENCL1.S1 | Left encoder push switch |
| 23 | D16 | PA3 | ADC_1 | /TAC_SHIFT_L | TAC_SHIFT_L1 | Left shift button |
| 24 | D17 | PB1 | ADC_2 **3V3-only** | /LED_2_R | R39 → Q | LED2 red (low-side NPN driver) |
| 25 | D18 | PA7 | ADC_3 **3V3-only** | /LED_1_B | R37 → Q | LED1 blue |
| 26 | D19 | PA6 | ADC_4 | /LED_1_G | R35 → Q | LED1 green |
| 27 | D20 | PC1 | ADC_5 | /LED_1_R | R36 → Q | LED1 red |
| 28 | D21 | PC4 | ADC_6 **3V3-only** | /DC_SPI | J8.4 | OLED data/command |
| 29 | D22 | PA5 | DAC_OUT2 **3V3-only** | /ENCR_CLICK | ENCR1.S1 | Right encoder push switch |
| 30 | D23 | PA4 | DAC_OUT1 **3V3-only** | /LED_2_B | R40 → Q | LED2 blue |
| 31 | D24 | PA1 | SAI2_MCLK | /LED_2_G | R38 → Q | LED2 green |
| 32 | D25 | PA0 | SAI2_SD_B | /ENCL_B | ENCL1.B, R32, C20 | Left encoder B |
| 33 | D26 | PD11 | SAI2_SD_A | /ENCL_A | ENCL1.A, R31, C19 | Left encoder A |
| 34 | D27 | PG9 | SAI2_FS | /TAC_SWITCH_1 | TAC_SWITCH_1 | Tactile switch 1 |
| 35 | D28 | PA2 | SAI2_SCK | /TAC_SWITCH_2 | TAC_SWITCH_2 | Tactile switch 2 |
| 36 | D29 | PB14 | USB_HS_D- | /USB_IN_MCU_N | U2.6 → P2 | External USB-C D- (through USBLC6 ESD) |
| 37 | D30 | PB15 | USB_HS_D+ | /USB_IN_MCU_P | U2.4 → P2 | External USB-C D+ |
| 38 | — | — | 3V3_D | /+3V3_D | SD pull-ups, encoder pull-ups, C27/C28 | 3.3 V digital rail out of the Seed |
| 39 | — | — | VIN | /DSY_VIN | R30, C18 | 9 V (after FB5/bridge) into the Seed regulator |
| 40 | — | — | DGND | GND | plane | Digital ground |

## Firmware notes that follow from the table

- Every GPIO is a plain digital input or output; no alternate function other than
  SPI1 (OLED) and USART1 (MIDI) is in use. SAI2 and I2C1 pins are repurposed as GPIO.
- SPI1: configure TX-only. D9 (MISO) is the right shift button.
- All six LED lines drive low-side NPN transistors through base resistors:
  GPIO high = LED on.
- Encoder A/B lines have 10 k pull-ups to /+3V3_D and 10 nF to GND at the encoder;
  use the state-table decoder, not edge interrupts.
- Encoder clicks and tactile switches have no external pull-ups: enable the internal
  pull-up and treat low as pressed.
- SD card is 4-bit SDMMC (DAT0–3, CMD, CLK) with 10 k pull-ups on board.
- The OLED (J8) is powered from U6's /+3V3_OLED rail, not from the Seed.
