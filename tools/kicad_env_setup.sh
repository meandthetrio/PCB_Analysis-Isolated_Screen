#!/usr/bin/env bash
# Make KiCad 9 (+ Freerouting autorouter) usable headless on Ubuntu 24.04
# (Claude Code on the web / CI).
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
# Also installs Freerouting (https://github.com/freerouting/freerouting) as a
# headless autorouter: the release jar needs Java 25, so OpenJDK 25 is
# installed alongside the system Java and a `freerouting` wrapper on PATH
# pins it. Drive it via tools/autoroute.py (DSN export -> route -> SES import).
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

# ---- Freerouting -----------------------------------------------------------
FR_VERSION="${FREEROUTING_VERSION:-2.4.1}"
FR_DIR=/opt/freerouting
FR_JAR="$FR_DIR/freerouting-$FR_VERSION.jar"
FR_URL="https://github.com/freerouting/freerouting/releases/download/v$FR_VERSION/freerouting-$FR_VERSION.jar"

if ! ls -d /usr/lib/jvm/java-25-openjdk-* >/dev/null 2>&1; then
  apt-get update -qq
  apt-get install -y --no-install-recommends openjdk-25-jre-headless
fi
FR_JAVA="$(ls -d /usr/lib/jvm/java-25-openjdk-*/bin/java | head -1)"

mkdir -p "$FR_DIR"
if [ ! -s "$FR_JAR" ]; then
  curl -fsSL --retry 3 -o "$FR_JAR.part" "$FR_URL" && mv "$FR_JAR.part" "$FR_JAR"
fi
ln -sfn "$(basename "$FR_JAR")" "$FR_DIR/freerouting.jar"

cat > /usr/local/bin/freerouting <<WRAP
#!/usr/bin/env bash
# Headless Freerouting. Typical use:
#   freerouting -de board.dsn -do board.ses -mp 20
exec "$FR_JAVA" -jar "$FR_DIR/freerouting.jar" \\
  --gui.enabled=false \\
  --usage_and_diagnostic_data.disable_analytics_module=true \\
  "\$@"
WRAP
chmod +x /usr/local/bin/freerouting

echo "kicad-cli $(kicad-cli version) ready; lib tables in $CFG"
echo "freerouting $FR_VERSION ready at /usr/local/bin/freerouting (java: $FR_JAVA)"
