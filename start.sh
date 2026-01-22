#!/bin/bash

# Script to run the bot (foreground or background)
# Usage: ./start.sh [background]

# Change to script directory
cd "$(dirname "$0")"

# Activate virtual environment
if [ ! -d "env" ]; then
    echo "❌ Virtual environment not found. Run setup.sh first."
    exit 1
fi

source env/bin/activate

# Check .env file
if [ ! -f ".env" ]; then
    echo "❌ .env file not found. Copy .env.example and configure it."
    exit 1
fi

# Create logs directory
mkdir -p logs

# Start bot
echo "🚀 Starting SHB Alert Bot..."

if [ "$1" = "background" ] || [ "$1" = "-d" ]; then
    # Run in background with nohup
    nohup python main.py > logs/bot.log 2>&1 &
    PID=$!
    echo $PID > logs/bot.pid
    echo "✅ Bot started in background (PID: $PID)"
    echo "📋 View logs: tail -f logs/bot.log"
    echo "🛑 Stop bot: ./stop.sh"
else
    # Run in foreground
    python main.py
fi
