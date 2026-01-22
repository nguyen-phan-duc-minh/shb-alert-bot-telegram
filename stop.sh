#!/bin/bash

# Stop the bot

# Find and kill the process
if pgrep -f "python main.py" > /dev/null; then
    pkill -f "python main.py"
    echo "✅ Bot stopped"
else
    echo "ℹ️  Bot is not running"
fi
