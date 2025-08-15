#!/bin/bash
set -e

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

echo "🏦 Starting Bank Performance Dashboard..."

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed. Please install Python 3 and try again."
    read -p "Press any key to exit..."
    exit 1
fi

# Set up Python virtual environment if it doesn't exist
if [ ! -d "backend/venv" ]; then
    echo "📦 Setting up Python environment..."
    cd backend
    python3 -m venv venv
    cd ..
fi

# Activate virtual environment and install dependencies
echo "📋 Installing dependencies..."
source backend/venv/bin/activate
python -m pip install --upgrade pip > /dev/null 2>&1
python -m pip install -r backend/requirements.txt > /dev/null 2>&1

# Start the backend server in the background
echo "🚀 Starting backend server..."
cd backend
export FLASK_APP=main.py
nohup python -m flask run --host=0.0.0.0 --port=5000 > server.log 2>&1 &
FLASK_PID=$!
cd ..

# Wait for server to start
echo "⏳ Waiting for server to start..."
ATTEMPTS=0
until curl -s --max-time 1 http://127.0.0.1:5000/api/status > /dev/null 2>&1; do
    ATTEMPTS=$((ATTEMPTS+1))
    if [ $ATTEMPTS -ge 30 ]; then
        echo "❌ Server failed to start. Check backend/server.log for details."
        read -p "Press any key to exit..."
        exit 1
    fi
    sleep 1
done

echo "✅ Server is running!"
echo "🌐 Opening dashboard in your browser..."

# Open the dashboard in the default browser
open "http://127.0.0.1:5000"

echo ""
echo "📊 Dashboard is now running at: http://127.0.0.1:5000"
echo "📝 Server logs: backend/server.log"
echo ""
echo "💡 Select a bank and year from the dropdowns to see real financial data!"
echo ""
echo "To stop the server, close this terminal window or press Ctrl+C"

# Keep the script running so the server stays active
trap "echo '🛑 Shutting down server...'; kill $FLASK_PID 2>/dev/null; exit 0" SIGINT SIGTERM

# Wait for user to stop the server
wait
