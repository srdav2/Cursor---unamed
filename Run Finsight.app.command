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

# Start backend (Flask) in background with logging
cd "$ROOT_DIR"
if [ ! -d "backend/venv" ]; then
  python3 -m venv backend/venv
fi
source backend/venv/bin/activate
python -m pip install --upgrade pip >/dev/null
python -m pip install -r backend/requirements.txt >/dev/null
export FLASK_APP=backend/main.py
LOG_FILE="$ROOT_DIR/backend/server.log"
nohup python -m flask run --port 5000 >"$LOG_FILE" 2>&1 &

# Wait up to ~30s for backend to come up
ATTEMPTS=0
until curl -s --max-time 1 http://127.0.0.1:5000/api/status >/dev/null 2>&1; do
  ATTEMPTS=$((ATTEMPTS+1))
  if [ $ATTEMPTS -ge 30 ]; then
    break
  fi
  sleep 1
done

# Open frontend in default browser
open "$ROOT_DIR/frontend/index.html"

if curl -s --max-time 1 http://127.0.0.1:5000/api/status >/dev/null 2>&1; then
  echo "Backend is running. App opened in your browser."
else
  echo "Backend may still be starting. App opened in your browser."
  echo "If it remains disconnected, see logs in $LOG_FILE"
fi


