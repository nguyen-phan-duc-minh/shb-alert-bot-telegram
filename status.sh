#!/bin/bash

# Check bot status

echo "=== SHB Alert Bot Status ==="
echo ""

# Check if process is running
if pgrep -f "python main.py" > /dev/null; then
    PID=$(pgrep -f "python main.py")
    echo "✅ Bot is RUNNING (PID: $PID)"
    
    # Check health endpoint
    if command -v curl &> /dev/null; then
        echo ""
        echo "Health Check:"
        curl -s http://localhost:8080/health | python -m json.tool 2>/dev/null || echo "❌ Health check endpoint not responding"
    fi
else
    echo "❌ Bot is NOT running"
fi

echo ""
echo "Recent logs:"
if [ -f "logs/bot.log" ]; then
    tail -10 logs/bot.log
else
    echo "No logs found"
fi
