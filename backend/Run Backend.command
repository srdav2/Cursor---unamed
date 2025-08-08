#!/bin/zsh
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$SCRIPT_DIR/.."
cd "$PROJECT_ROOT"

echo "Starting backend in: $PROJECT_ROOT"

# Kill any existing flask runs on 5000 (best-effort)
pkill -f "flask run" >/dev/null 2>&1 || true

# Create venv if missing
if [ ! -d "backend/venv" ]; then
  echo "Creating virtual environment ..."
  python3 -m venv backend/venv
fi

source backend/venv/bin/activate
python -m pip install --upgrade pip >/dev/null
echo "Installing requirements ..."
python -m pip install -r backend/requirements.txt >/dev/null

export FLASK_APP=backend/main.py
echo "Running Flask on http://127.0.0.1:5000 ..."
python -m flask run --port 5000


