#!/usr/bin/env bash
set -euo pipefail

CONFIG_DIR="configs"
TICKS="${TICKS:-3}"

# Prefer python3 if available
PY="${PYTHON:-python3}"
if ! command -v "$PY" >/dev/null 2>&1; then
  PY="python"
fi

if ! command -v "$PY" >/dev/null 2>&1; then
  echo "[ERROR] python/python3 not found"
  exit 1
fi

if [ ! -d "$CONFIG_DIR" ]; then
  echo "[ERROR] Config dir not found: $CONFIG_DIR"
  exit 1
fi

echo "[AMNION] Boot sequence started..."
echo "[AMNION] Using config dir: $CONFIG_DIR"
echo "[AMNION] Demo ticks: $TICKS"

# Run package entrypoint (controller/__main__.py)
"$PY" -m controller --config-dir "$CONFIG_DIR" --ticks "$TICKS"
