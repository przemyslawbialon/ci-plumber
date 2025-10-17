#!/bin/bash

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m'

echo -e "${CYAN}${BOLD}"
echo "╔════════════════════════════════════════════╗"
echo "║     CI Plumber Installation Script        ║"
echo "╚════════════════════════════════════════════╝"
echo -e "${NC}"

if [ -z "$MONDAY_PATH" ]; then
    echo -e "${YELLOW}⚠  Warning: MONDAY_PATH environment variable is not set.${NC}"
    echo -e "${YELLOW}   Please set it to your development directory (e.g., /Users/YourName/Development)${NC}"
    echo ""
    read -p "Enter your development path (or press Enter to use current directory): " INPUT_PATH
    
    if [ -z "$INPUT_PATH" ]; then
        MONDAY_PATH="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && cd .. && pwd )"
        echo -e "${CYAN}→ Using: $MONDAY_PATH${NC}"
    else
        MONDAY_PATH="$INPUT_PATH"
    fi
    echo ""
fi

SCRIPT_DIR="$MONDAY_PATH/ci-plumber"
LAUNCH_AGENT_PATH="$HOME/Library/LaunchAgents/com.ciplumber.plist"

echo -e "${BLUE}📂 Project path: ${BOLD}$SCRIPT_DIR${NC}"
echo ""

echo -e "${BOLD}[1/9]${NC} ${CYAN}🐍 Checking Python3 installation...${NC}"
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}✗ Error: python3 is not installed. Please install Python 3 first.${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Python3 found: $(python3 --version)${NC}"
echo ""

echo -e "${BOLD}[2/9]${NC} ${CYAN}📦 Creating virtual environment...${NC}"
if [ ! -d "$SCRIPT_DIR/venv" ]; then
    python3 -m venv "$SCRIPT_DIR/venv"
    echo -e "${GREEN}✓ Virtual environment created${NC}"
else
    echo -e "${GREEN}✓ Virtual environment already exists${NC}"
fi
echo ""

echo -e "${BOLD}[3/9]${NC} ${CYAN}📥 Installing Python dependencies in virtual environment...${NC}"
source "$SCRIPT_DIR/venv/bin/activate"
pip install --upgrade pip -q
pip install -r "$SCRIPT_DIR/requirements.txt" -q
echo -e "${GREEN}✓ Dependencies installed in virtual environment${NC}"
echo ""

echo -e "${BOLD}[4/9]${NC} ${CYAN}⚙️  Checking configuration...${NC}"
if [ ! -f "$SCRIPT_DIR/config.yaml" ]; then
    echo -e "${YELLOW}⚠  config.yaml not found. Creating from example...${NC}"
    cp "$SCRIPT_DIR/config.yaml.example" "$SCRIPT_DIR/config.yaml"
    echo -e "${YELLOW}⚠  Please edit config.yaml and add your GitHub token!${NC}"
else
    echo -e "${GREEN}✓ config.yaml exists${NC}"
fi
echo ""

echo -e "${BOLD}[5/9]${NC} ${CYAN}📝 Creating logs directory...${NC}"
mkdir -p "$SCRIPT_DIR/logs"
echo -e "${GREEN}✓ Logs directory created${NC}"
echo ""

echo -e "${BOLD}[6/9]${NC} ${CYAN}🔧 Making script executable...${NC}"
chmod +x "$SCRIPT_DIR/ci_plumber.py"
echo -e "${GREEN}✓ Script is now executable${NC}"
echo ""

echo -e "${BOLD}[7/9]${NC} ${CYAN}🧪 Testing manual run...${NC}"
echo -e "${YELLOW}→ This will do a test run. Press Ctrl+C if you want to skip...${NC}"
sleep 2
"$SCRIPT_DIR/venv/bin/python" "$SCRIPT_DIR/ci_plumber.py" || echo -e "${YELLOW}⚠  Test run failed. Please check your configuration.${NC}"
echo ""

echo -e "${BOLD}[8/9]${NC} ${CYAN}📄 Generating launchd plist file...${NC}"
if [ ! -f "$SCRIPT_DIR/com.ciplumber.plist.template" ]; then
    echo -e "${RED}✗ Error: com.ciplumber.plist.template not found!${NC}"
    exit 1
fi

sed "s|{{PROJECT_PATH}}|$SCRIPT_DIR|g" "$SCRIPT_DIR/com.ciplumber.plist.template" > "$SCRIPT_DIR/com.ciplumber.plist"
echo -e "${GREEN}✓ Generated com.ciplumber.plist${NC}"
echo -e "${BLUE}  → Path: $SCRIPT_DIR${NC}"
echo ""

echo -e "${BOLD}[9/9]${NC} ${CYAN}🚀 Installing launchd service...${NC}"
if [ -f "$LAUNCH_AGENT_PATH" ]; then
    echo -e "${YELLOW}→ Unloading existing service...${NC}"
    launchctl unload "$LAUNCH_AGENT_PATH" 2>/dev/null || true
fi

cp "$SCRIPT_DIR/com.ciplumber.plist" "$LAUNCH_AGENT_PATH"
launchctl load "$LAUNCH_AGENT_PATH"
echo -e "${GREEN}✓ Service installed and loaded${NC}"
echo ""

echo -e "${GREEN}${BOLD}"
echo "╔════════════════════════════════════════════╗"
echo "║          Installation Complete! 🎉        ║"
echo "╚════════════════════════════════════════════╝"
echo -e "${NC}"
echo -e "${GREEN}The CI Plumber will now run every hour automatically.${NC}"
echo ""
echo -e "${BOLD}Useful commands:${NC}"
echo -e "  ${CYAN}📊 View logs:${NC}"
echo -e "     tail -f $SCRIPT_DIR/logs/ci-plumber-\$(date +%Y-%m-%d).log"
echo ""
echo -e "  ${CYAN}▶️  Manual run:${NC}"
echo -e "     $SCRIPT_DIR/venv/bin/python $SCRIPT_DIR/ci_plumber.py"
echo ""
echo -e "  ${CYAN}⏸  Stop service:${NC}"
echo -e "     launchctl unload $LAUNCH_AGENT_PATH"
echo ""
echo -e "  ${CYAN}▶️  Start service:${NC}"
echo -e "     launchctl load $LAUNCH_AGENT_PATH"
echo ""
echo -e "${YELLOW}${BOLD}⚠  Don't forget to add your GitHub token to config.yaml!${NC}"

