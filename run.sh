#!/usr/bin/env bash
# ===================================================================
#  AriTyper launcher for Linux and macOS
#
#  Usage:   ./run.sh          (or:  bash run.sh)
#
#  On first run this creates a private virtual environment and
#  installs the dependencies. Later runs go straight to launching.
#
#  Windows users: use run.bat or run.ps1 instead.
# ===================================================================
set -euo pipefail

cd "$(dirname "$0")"

VENV_DIR=".venv"
VENV_PY="$VENV_DIR/bin/python"
STAMP="$VENV_DIR/.deps-installed"
APP="arityper_activated.py"

echo
echo "  ============================================"
echo "    AriTyper - free, no license key needed"
echo "  ============================================"
echo

# ---- 1. Find a Python interpreter to bootstrap with ----------------
BOOT_PY=""
for candidate in python3 python; do
    if command -v "$candidate" >/dev/null 2>&1; then
        BOOT_PY="$candidate"
        break
    fi
done

if [ -z "$BOOT_PY" ]; then
    echo "  [ERROR] Python was not found on this computer."
    echo
    echo "  Install Python 3.8 or newer, then run ./run.sh again."
    echo "    Debian/Ubuntu/Kali:  sudo apt install python3 python3-venv python3-tk"
    echo "    macOS (Homebrew):    brew install python-tk"
    echo
    exit 1
fi

# ---- 2. Create the virtual environment (first run only) -----------
if [ ! -x "$VENV_PY" ]; then
    echo "  [1/3] Creating virtual environment..."
    if ! "$BOOT_PY" -m venv "$VENV_DIR"; then
        echo
        echo "  [ERROR] Could not create the virtual environment."
        echo "  On Debian/Ubuntu/Kali you may need:  sudo apt install python3-venv"
        echo
        exit 1
    fi
else
    echo "  [1/3] Virtual environment ready."
fi

# ---- 3. Install dependencies (first run only) ---------------------
if [ ! -f "$STAMP" ]; then
    echo "  [2/3] Installing dependencies - first run only, please wait..."
    # Upgrading pip is a nicety, not a requirement - never fail the run over it.
    "$VENV_PY" -m pip install --upgrade pip --quiet || true
    if ! "$VENV_PY" -m pip install -r requirements.txt --quiet; then
        echo
        echo "  [ERROR] Installing dependencies failed."
        echo "  Check your internet connection, then run ./run.sh again."
        echo
        exit 1
    fi
    echo installed > "$STAMP"
else
    echo "  [2/3] Dependencies ready."
fi

# ---- 4. Launch -----------------------------------------------------
echo "  [3/3] Launching AriTyper..."
echo
echo "  Keep this window open while you use the app."
echo "  Close the AriTyper window to quit."
echo

exec "$VENV_PY" "$APP"
