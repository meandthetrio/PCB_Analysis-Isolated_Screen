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
