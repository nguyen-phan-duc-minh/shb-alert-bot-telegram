#!/bin/bash

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}=== SHB Alert Bot Setup ===${NC}\n"

# Check Python version
echo "Checking Python version..."
python3 --version
if [ $? -ne 0 ]; then
    echo -e "${RED}Error: Python 3 is not installed${NC}"
    exit 1
fi

# Create virtual environment
echo -e "\n${YELLOW}Creating virtual environment...${NC}"
python3 -m venv env

# Activate virtual environment
echo -e "${YELLOW}Activating virtual environment...${NC}"
source env/bin/activate

# Upgrade pip
echo -e "\n${YELLOW}Upgrading pip...${NC}"
pip install --upgrade pip

# Install requirements
echo -e "\n${YELLOW}Installing dependencies...${NC}"
pip install -r requirements.txt

# Create necessary directories
echo -e "\n${YELLOW}Creating directories...${NC}"
mkdir -p logs storage/backup

# Copy .env.example to .env if not exists
if [ ! -f .env ]; then
    echo -e "\n${YELLOW}Creating .env file from .env.example...${NC}"
    cp .env.example .env
    echo -e "${YELLOW}⚠️  Please edit .env and add your Telegram bot token and chat ID${NC}"
else
    echo -e "\n${GREEN}.env file already exists${NC}"
fi

# Create start script
echo -e "\n${YELLOW}Creating start script...${NC}"
cat > start.sh << 'EOF'
#!/bin/bash
cd "$(dirname "$0")"
source env/bin/activate
python main.py
EOF
chmod +x start.sh

# Create stop script
echo -e "${YELLOW}Creating stop script...${NC}"
cat > stop.sh << 'EOF'
#!/bin/bash
pkill -f "python main.py"
echo "Bot stopped"
EOF
chmod +x stop.sh

# Create status script
echo -e "${YELLOW}Creating status script...${NC}"
cat > status.sh << 'EOF'
#!/bin/bash
if pgrep -f "python main.py" > /dev/null; then
    echo "✅ Bot is running"
    echo "Health check: http://localhost:8080/health"
else
    echo "❌ Bot is not running"
fi
EOF
chmod +x status.sh

echo -e "\n${GREEN}=== Setup Complete! ===${NC}\n"
echo -e "${YELLOW}Next steps:${NC}"
echo "1. Edit .env file with your Telegram credentials:"
echo "   - TELEGRAM_BOT_TOKEN"
echo "   - TELEGRAM_CHAT_ID"
echo ""
echo "2. Start the bot:"
echo "   ./start.sh"
echo ""
echo "3. Check status:"
echo "   ./status.sh"
echo ""
echo "4. View health check:"
echo "   curl http://localhost:8080/health"
echo ""
echo "5. Stop the bot:"
echo "   ./stop.sh"
echo ""
echo -e "${GREEN}Happy trading! 📈${NC}"
