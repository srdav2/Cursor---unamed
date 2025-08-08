#!/bin/zsh
set -e
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR/desktop"
if ! command -v npm >/dev/null 2>&1; then
  echo "Node.js is required. Install from https://nodejs.org and re-run."; exit 1
fi
npm install
npm start


