# Electrosmith reference files

Fetched 2026-10-12 from Electrosmith's public CDN (`daisy.nyc3.cdn.digitaloceanspaces.com/products/...`), which now hosts what the retired `electro-smith/Hardware` GitHub repo used to. Electrosmith's hardware files are published for reference; they are included here unmodified.

| Folder | File | What |
|---|---|---|
| daisy_pod | ES_Daisy_Pod_Rev5.pdf | Pod Rev5 schematic (Eagle export 2024-01-09, sheet date 2022-10-27) |
| daisy_pod | ES_Daisy_Pod_Rev5.sch / .brd | Eagle 9.6.2 schematic and board source |
| daisy_pod | BOM_ES_Daisy_Pod_Rev5.xlsx | Pod BOM, 24 lines |
| daisy_pod | Pod_databrief-3-13.pdf | product databrief |
| daisy_field | field_databrief-3-13.pdf, field-pinout-2.pdf | Field databrief and pinout |
| daisy_seed | ES_Daisy_Seed_Rev7.pdf | Seed Rev7 schematic |
| daisy_seed | Daisy_Seed_pinout.pdf | Seed pinout card |

**Not obtained:** the Daisy Field schematic (`ES_Daisy_Field_Rev4.pdf` / `.sch`, per 2021 forum references) and any Field board file. The CDN returns 403 for every Field schematic path tried, the Field is a discontinued product whose files are linked only from `daisy.audio/pages/legacy`, and that site, the Electrosmith forum, the Scribd mirror and the Wayback Machine are all unreachable from the review environment. The Seed datasheet v1.1.5 PDF on the same CDN also returns 403. Also not obtained for the Pod: Gerbers (never published); the `.brd` is the layout truth.

## Added 2026-10-12: Seed 3 dev kits and Seed 3 datasheet

Found via the daisyaudio GitHub organisation (the daisy.audio product pages themselves are blocked from this environment, but their README links point to the CDN and to public repos).

| Folder | What | Source |
|---|---|---|
| seed3_eurorack_devkit/Rev3 | KiCad project (**KiCad 10 format, version 20260206**; does not load in the KiCad 9.0.9 installed here), review PDFs (schematic + board), BOM CSVs, libs | github.com/daisyaudio/ES-Seed3-DevKit-Eurorack @ 651216a (2026-10-06) |
| seed3_eurorack_devkit/Rev2 | KiCad 9-format project of the previous revision (loads here) | same repo |
| seed3_eurorack_devkit/*.pdf, *.csv | Rev3 schematic PDF, Rev3 BOM, pinout | CDN `products/seed-3-euro/` |
| seed3_pedal_devkit/Rev3 | KiCad 9-format project (loads here), review PDFs | github.com/daisyaudio/ES-Seed3-DevKit-Pedal @ f79f932 (2026-10-06) |
| daisy_seed3/Daisy_Seed3_datasheet.pdf | Seed 3 datasheet v1.0 (2026-07-23), 38 pp; 3.3 V-only pins 24, 25, 28, 29, 30 | CDN `products/seed3/` |

Production folders were left out except the Eurorack Rev3 production set (Gerbers, drill, BOM, centroid, dated 2026-06-18), which is the fab truth for Rev3 and the only Rev3 copper readable without KiCad 10. Other production zips, STEP and EasyEDA JSON were left out to keep the repo small; the clones live in the session scratchpad. Both repos are MIT-licensed open-source hardware (LICENSE.txt copied).
