#!/usr/bin/env python3
"""Look up MPNs on JLCPCB's parts-search API (the only vendor catalogue reachable from the
review session; mouser/digikey/octopart are blocked). Saves raw JSON per keyword and prints
a compact table: LCSC code | model | brand | package | description | Basic/Extended | stock.
Usage: python3 -I jlc_lookup.py OUT_DIR MPN [MPN ...]"""
import sys, json, os, urllib.request, time
URL = "https://jlcpcb.com/api/overseas-pcb-order/v1/shoppingCart/smtGood/selectSmtComponentList"
out = sys.argv[1]; os.makedirs(out, exist_ok=True)
for kw in sys.argv[2:]:
    body = json.dumps({"keyword": kw, "currentPage": 1, "pageSize": 20}).encode()
    req = urllib.request.Request(URL, data=body, headers={"Content-Type": "application/json", "User-Agent": "curl/8"})
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            d = json.load(r)
    except Exception as e:
        print(f"## {kw}: ERROR {e}"); continue
    json.dump(d, open(os.path.join(out, kw.replace('/', '_').replace(',', '_') + ".json"), "w"), indent=1)
    lst = (d.get("data") or {}).get("componentPageInfo", {}).get("list", []) or []
    print(f"## {kw}: {len(lst)} hit(s)")
    for h in lst[:8]:
        print("   ", h.get("componentCode"), "|", h.get("componentModelEn"), "|", h.get("componentBrandEn"), "|",
              h.get("componentSpecificationEn"), "|", (h.get("describe") or "")[:110], "|", h.get("componentLibraryType"),
              "| stock", h.get("stockCount"))
    time.sleep(0.5)
