#!/bin/bash
# SessionStart hook for Claude Code on the web: make KiCad 9 usable headless
# (kicad-cli, pcbnew Python module, stock symbol/footprint libs, lib tables).
# Runs synchronously so kicad-cli is ready before the session starts.
set -euo pipefail

if [ "${CLAUDE_CODE_REMOTE:-}" != "true" ]; then
  exit 0
fi

SETUP="$CLAUDE_PROJECT_DIR/tools/kicad_env_setup.sh"
if [ "$(id -u)" -eq 0 ]; then
  "$SETUP"
else
  sudo -n "$SETUP"
fi
