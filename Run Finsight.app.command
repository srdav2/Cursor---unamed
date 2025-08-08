#!/bin/zsh
set -e

ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"

# If Node is available, launch full desktop app (auto-starts backend)
if command -v npm >/dev/null 2>&1; then
  cd "$ROOT_DIR/desktop"
  npm install
  npm start
  exit 0
fi

# Beginner-friendly fallback (no Node needed): start backend and open UI in browser
echo "Node.js not found. Launching backend and opening the app in your browser..."

# Start backend (Flask) in background
cd "$ROOT_DIR"
if [ ! -d "backend/venv" ]; then
  python3 -m venv backend/venv
fi
source backend/venv/bin/activate
python -m pip install --upgrade pip >/dev/null
python -m pip install -r backend/requirements.txt >/dev/null
export FLASK_APP=backend/main.py
nohup python -m flask run --port 5000 >/dev/null 2>&1 &

# Open frontend in default browser
open "$ROOT_DIR/frontend/index.html"

echo "App is opening. If you see 'Backend: Disconnected' for more than ~10s, refresh the page."


