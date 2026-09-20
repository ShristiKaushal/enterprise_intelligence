#!/usr/bin/env bash

# Enterprise Intelligence Platform — Quick Start for macOS / Linux
# Run from project root: ./start.sh

set -e

echo ""
echo "========================================"
echo "  Enterprise Intelligence Platform (Mac)"
echo "========================================"
echo ""

ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"
BACKEND_DIR="$ROOT_DIR/backend"
FRONTEND_DIR="$ROOT_DIR/frontend"

# 0. Select suitable Python version (prefer 3.11 or 3.13 over 3.14)
if command -v python3.11 &> /dev/null; then
    PYTHON_BIN="python3.11"
elif command -v python3.13 &> /dev/null; then
    PYTHON_BIN="python3.13"
else
    PYTHON_BIN="python3"
fi

# 1. Ensure .env exists
if [ ! -f "$ROOT_DIR/.env" ]; then
    echo "Creating .env from .env.example..."
    cp "$ROOT_DIR/.env.example" "$ROOT_DIR/.env"
fi

# 2. Virtual environment setup for backend
if [ ! -d "$BACKEND_DIR/venv" ]; then
    echo "Creating Python virtual environment using $PYTHON_BIN in backend/venv..."
    $PYTHON_BIN -m venv "$BACKEND_DIR/venv"
fi

source "$BACKEND_DIR/venv/bin/activate"

# Verify dependencies installed
if ! python -c "import fastapi" 2>/dev/null; then
    echo "Installing backend dependencies..."
    pip install --upgrade pip
    pip install -r "$BACKEND_DIR/requirements.txt"
fi

# 3. Verify frontend dependencies
if [ ! -d "$FRONTEND_DIR/node_modules" ]; then
    echo "Installing frontend dependencies..."
    (cd "$FRONTEND_DIR" && npm install)
fi

# 4. Launch Backend and Frontend
echo ""
echo "Starting Backend API (http://localhost:8000)..."
(cd "$BACKEND_DIR" && python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000) &
BACKEND_PID=$!

sleep 2

echo "Starting Frontend UI (http://localhost:5173)..."
(cd "$FRONTEND_DIR" && npm run dev) &
FRONTEND_PID=$!

cleanup() {
    echo ""
    echo "Shutting down platform services..."
    kill $BACKEND_PID 2>/dev/null || true
    kill $FRONTEND_PID 2>/dev/null || true
    exit 0
}

trap cleanup INT TERM EXIT

echo ""
echo "========================================"
echo "  Platform is live!"
echo "  • Web Interface: http://localhost:5173"
echo "  • Swagger API:   http://localhost:8000/api/docs"
echo "  • Demo Credentials: admin@eip.local / Admin@12345"
echo "========================================"
echo ""
echo "Press CTRL+C to stop all services."

wait
