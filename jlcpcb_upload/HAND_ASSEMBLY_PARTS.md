# Hand-assembly parts — WavetableController "LedFix" revision

The 18 through-hole / hand-soldered parts that are intentionally absent from the
JLCPCB SMT BOM (finding F-026). Identities come from the schematic symbol fields,
the embedded footprint descriptions and 3D-model names in the `.kicad_pcb`.
Prices are distributor list prices in USD, looked up 2026-10-29; they move, so
treat them as a budget, not a quote. SMT parts are not listed here: JLCPCB prices
those inside the assembly quote.

| Ref(s) | Qty/board | Part (identity source) | Unit price, qty 1 | Small-qty break | Where | Notes |
|---|---|---|---|---|---|---|
| A1 | 1 | Electrosmith **Seed3** (board footprint is Daisy Seed Rev7 THT 2×20; Seed3 is stated pin-to-pin compatible) | $29.99 | $28.49 @100 | daisy.audio | **Out of stock, "restock en route."** The original Daisy Seed is no longer listed by Electrosmith; retailers show it sold out. Seed2 DFM ($29.99, in stock) is through-hole free and does **not** fit this footprint. |
| ENCL1, ENCR1 | 2 | Alps **EC11E15244G1** — 11 mm vertical, 15 PPR / 30 detent, push switch, 20 mm flat shaft (footprint: Alps EC11E vertical H20mm) | $1.90 | $1.85 @25 (Master Elec.) | LCSC, TME ($2.61), Master Electronics | Exact Alps code is not in the design files; any EC11E with switch and 20 mm shaft fits. US distributors (Digi-Key/Mouser) list the 18 PPR sibling EC11E18244A5 at $4.85. |
| J2 | 1 | HiLetgo 2.42" SSD1309 128×64 OLED module, I2C 4-pin (3D model "OLED 2.42 V1.1 SSD1309") | $11–26 | — | Amazon B0CFF5SD1T is a **2-pack** (price not captured); HiLetgo single on eBay $26.34; generic equivalents $10.89 (Spotpear) – $15.65 (eBay) | Plugs into the 1×4 2.54 mm header. Generic modules default to SPI and need the resistor jumper moved for I2C. Add ~$0.10–0.30 for a 1×4 socket if used. |
| J3–J7 | 5 | Same Sky (CUI) **SJ1-3525N** 3.5 mm TRS, right-angle THT, 2 internal switches (3D model name) | $1.23 | $1.045 @10, $0.979 @25, $0.867 @140 | Digi-Key CP1-3525N-ND, 5,254 in stock | Mouser ≈ $0.89 (aggregator snapshot); Future $0.60 @30 MOQ. |
| SW1 | 1 | CIT Relay & Switch **1101A4VQEA** SPDT slide, vertical right-angle PC pins (footprint name) | ≈ $3.15 (proxy) | $2.64 @10 (proxy) | Digi-Key lists siblings 1101A1VQEA ($3.15, 434 in stock) and 1101A2VQEA ($3.16) | The exact A4 actuator variant was found at **no** distributor; CIT quotes directly (actuator lengths 3.6–9.4 mm). Confirm actuator length against the panel before substituting A1/A2. |
| MK1 | 1 | PUI Audio **POM-2244P-C3310-2-R** electret mic | $3.07 | $2.34 @10, $1.81 @100 | Digi-Key 668-1415-ND, 1,325 in stock, 24-wk lead | Mouser ≈ $2.41 (aggregator). |
| C14 | 1 | 470 µF radial electrolytic, 10 mm can (e.g. Rubycon 35ZLQ470MEFC10X16, 35 V) | $0.82 | — | Digi-Key, 2,317 in stock | **On the fabbed LedFix boards this part has no holes**: the Gerbers carry an unconnected SMD electrolytic pattern instead, and the 470 µF was hand-wired as the OLED noise fix. The THT footprint (10 mm, 7.5 mm pitch) exists only in the stale `.kicad_pcb`. Voltage rating is uncritical (3.3 V rail). |
| TAC_SWITCH_1, _2 | 2 | C&K **PTS645SH95-2 LFS** 6×6 mm THT tact, 9.5 mm actuator (footprint: 6 mm THT H9.5) | $0.29 | $0.251 @10, $0.210 @100 | Digi-Key, 10,572 in stock | Symbol says "MEC 5E" but the footprint is a standard 6×6 THT pattern; any 6×6×9.5 THT tact fits. The SMT BOM's phantom S1/S2 line (C2835239) is the SMD version and does not fit. |
| TAC_SHIFT_L1, _R1 | 2 | Alps **SKHHLUA010** 6 mm right-angle THT tact (footprint description; 3D model "6x6x8 right angle") | ≈ $0.33 | $0.26 at volume | Mouser (aggregator snapshot, ~900 in stock) | Not stocked at Digi-Key; Avnet/Future quote 10k MOQ only. Any generic 6×6×8 right-angle tact with bracket pins fits (LCSC ≈ $0.05–0.10). |

Excluded on purpose: LED1/LED2 (Cree CLS6B-FKW, SMD). They are not in the SMT BOM
and the LED circuit is broken as wired (FINAL_REPORT Tier 1 #2); do not fit them.

## Per-board total (hand parts only)

| Scenario | Approx. total |
|---|---|
| Qty 1, cheapest sources (LCSC encoders, generic OLED) | ≈ $59 |
| Qty 1, US distributors + HiLetgo-branded OLED | ≈ $80 |
| 10 boards, per board | ≈ $58–75 |

Seed3 and the OLED module are ~70 % of the total; everything else is under $10
per board at any quantity. No hand part has a break below qty 10 except the jacks
and tact switches.

## Availability flags

1. **Seed3 out of stock** at Electrosmith with no date. Nothing else fits the A1
   footprint. Check stock before committing to a board run.
2. **SW1 exact part unobtainable** through distributors; needs a CIT quote or a
   sibling with the right actuator length.
3. **Mic lead time 24 weeks** if Digi-Key's 1,325 units run out.
4. Encoder and right-angle tact are cheapest from LCSC/TME; add shipping and
   minimums if ordering only a few.

## Sources (fetched 2026-10-29)

- Seed3 price/stock: https://daisy.audio/products/seed3 ; compatibility statement: https://docs.daisy.audio/hardware/Seed3/ ; Seed2 DFM: https://daisy.audio/products/daisy-seed2-dfm , https://docs.daisy.audio/hardware/Seed2-DFM/
- SJ1-3525N: https://www.digikey.com/en/products/detail/same-sky-formerly-cui-devices/SJ1-3525N/738687
- POM-2244P-C3310-2-R: https://www.digikey.com/en/products/detail/pui-audio-inc/POM-2244P-C3310-2-R/4303938
- 1101A1VQEA (sibling of SW1): https://www.digikey.com/en/products/detail/cit-relay-and-switch/1101A1VQEA/20512096 ; CIT 1000 series: https://www.citrelay.com/view_switch.php?series=1000
- PTS645SH95-2 LFS: https://www.digikey.com/en/products/detail/c-k/PTS645SH95-2-LFS/1146763
- EC11E15244G1: https://support.lcsc.com/product-detail/Rotary-Encoders_ALPSALPINE-EC11E15244G1_C370970.html , https://www.tme.com/mx/en/details/ec11e15244g1/incremental-type-encoders/alps/ , https://masterelectronics.com/en/alps-electric/ec11e15244g1-10113570.html
- SKHHLUA010: https://nz.element14.com/alps/skhhlua010/switch-tactile-6x6mm-horiz-blk/dp/2056830 , https://www.avnet.com/americas/product/alps-alpine/skhhlua010/evolve-175812/
- 470 µF 35 V 10 mm: https://www.digikey.com/en/products/detail/rubycon/35ZLQ470MEFC10X16/6049879
- OLED: https://www.amazon.com/HiLetgo-SSD1309-128x64-Display-Optional/dp/B0CFF5SD1T , https://www.ebay.com/itm/398110853010 , https://spotpear.com/index.php/index/product/detail/id/1392.html , https://www.ebay.com/itm/335543250746
