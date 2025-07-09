#!/bin/bash

# AI Content Moderation API Startup Script

# Set environment variables
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# Default values
HOST=${HOST:-"0.0.0.0"}
PORT=${PORT:-8000}
WORKERS=${WORKERS:-1}
LOG_LEVEL=${LOG_LEVEL:-"info"}

echo "🚀 Starting AI Content Moderation API..."
echo "📍 Host: $HOST"
echo "🔌 Port: $PORT"
echo "👥 Workers: $WORKERS"
echo "📊 Log Level: $LOG_LEVEL"

# Check if virtual environment exists
if [ -f "venv/bin/activate" ]; then
    echo "🔧 Activating virtual environment..."
    source venv/bin/activate
fi

# Install dependencies if requirements.txt exists
if [ -f "requirements.txt" ]; then
    echo "📦 Installing dependencies..."
    pip install -r requirements.txt
fi

# Start the server
echo "🎯 Starting server..."
uvicorn app.main:app \
    --host $HOST \
    --port $PORT \
    --workers $WORKERS \
    --log-level $LOG_LEVEL \
    --reload
