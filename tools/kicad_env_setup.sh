#!/usr/bin/env bash
# Make KiCad 9 usable headless on Ubuntu 24.04 (Claude Code on the web / CI).
#
# Installs kicad-cli + the pcbnew Python module (package "kicad"), the stock
# symbol and footprint libraries (so ERC/DRC don't emit ~190 "library not
# found" warnings), and copies KiCad's default library tables into the user
# config dir, which apt does not do for headless (no-GUI-first-run) use.
#
# Skipped on purpose: kicad-packages3d (multi-GB 3D models, not needed for
# ERC/DRC/exports) and Trey's private libs (Retroactive_Custom_Parts,
# Jack_3.5mm_CUI_RetroactiveCustom, SOP-6_3.8x4.1mm_P2.54mm(RetroactiveCustom))
# which only exist on his machine. Footprints are embedded in the .kicad_pcb,
# so the resulting ~35 lib_footprint_* / footprint_link_* warnings are noise.
#
# Usage: sudo tools/kicad_env_setup.sh        (idempotent)
# Verify: tools/kicad_check.sh
set -euo pipefail
export DEBIAN_FRONTEND=noninteractive

if ! command -v kicad-cli >/dev/null || [ ! -d /usr/share/kicad/symbols ] || [ ! -d /usr/share/kicad/footprints ]; then
  apt-get update -qq
  apt-get install -y --no-install-recommends kicad kicad-symbols kicad-footprints
fi

KICAD_VER="$(kicad-cli version | cut -d. -f1,2)"   # e.g. 9.0
CFG="${HOME}/.config/kicad/${KICAD_VER}"
mkdir -p "$CFG"
for t in sym-lib-table fp-lib-table; do
  # Only overwrite an empty/absent table; keep a user-customised one.
  if [ ! -s "$CFG/$t" ] || ! grep -q '(lib ' "$CFG/$t"; then
    cp "/usr/share/kicad/template/$t" "$CFG/$t"
  fi
done

echo "kicad-cli $(kicad-cli version) ready; lib tables in $CFG"
