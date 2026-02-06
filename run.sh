#!/usr/bin/env bash
set -e

echo "[AMNION] Boot sequence started..."

# Check python
if ! command -v python3 &>/dev/null; then
  echo "[ERROR] python3 not found"
  exit 1
fi

# Create venv if not exists
if [ ! -d ".venv" ]; then
  echo "[AMNION] Creating virtual environment..."
  python3 -m venv .venv
fi

# Activate venv
source .venv/bin/activate

# Install deps if requirements.txt exists
if [ -f "requirements.txt" ]; then
  echo "[AMNION] Installing dependencies..."
  pip install -r requirements.txt
else
  echo "[WARN] requirements.txt not found, skipping"
fi

# Check config
CONFIG_PATH="configs/default.yaml"

if [ ! -f "$CONFIG_PATH" ]; then
  echo "[ERROR] Config not found: $CONFIG_PATH"
  exit 1
fi

echo "[AMNION] Using config: $CONFIG_PATH"

# Run controller
python -m controller.amnion_controller --config "$CONFIG_PATH"
