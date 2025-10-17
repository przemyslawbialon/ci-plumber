#!/bin/bash

set -e

echo "CI Plumber Installation Script"
echo "==============================="
echo ""

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
LAUNCH_AGENT_PATH="$HOME/Library/LaunchAgents/com.ciplumber.plist"

echo "Step 1: Checking Python3 installation..."
if ! command -v python3 &> /dev/null; then
    echo "Error: python3 is not installed. Please install Python 3 first."
    exit 1
fi
echo "✓ Python3 found: $(python3 --version)"
echo ""

echo "Step 2: Creating virtual environment..."
if [ ! -d "$SCRIPT_DIR/venv" ]; then
    python3 -m venv "$SCRIPT_DIR/venv"
    echo "✓ Virtual environment created"
else
    echo "✓ Virtual environment already exists"
fi
echo ""

echo "Step 3: Installing Python dependencies in virtual environment..."
source "$SCRIPT_DIR/venv/bin/activate"
pip install --upgrade pip
pip install -r "$SCRIPT_DIR/requirements.txt"
echo "✓ Dependencies installed in virtual environment"
echo ""

echo "Step 4: Checking configuration..."
if [ ! -f "$SCRIPT_DIR/config.yaml" ]; then
    echo "Warning: config.yaml not found. Creating from example..."
    cp "$SCRIPT_DIR/config.yaml.example" "$SCRIPT_DIR/config.yaml"
    echo "⚠️  Please edit config.yaml and add your GitHub token!"
fi
echo ""

echo "Step 5: Creating logs directory..."
mkdir -p "$SCRIPT_DIR/logs"
echo "✓ Logs directory created"
echo ""

echo "Step 6: Making script executable..."
chmod +x "$SCRIPT_DIR/ci_plumber.py"
echo "✓ Script is now executable"
echo ""

echo "Step 7: Testing manual run..."
echo "This will do a test run. Press Ctrl+C if you want to skip..."
sleep 2
"$SCRIPT_DIR/venv/bin/python" "$SCRIPT_DIR/ci_plumber.py" || echo "⚠️  Test run failed. Please check your configuration."
echo ""

echo "Step 8: Installing launchd service..."
if [ -f "$LAUNCH_AGENT_PATH" ]; then
    echo "Unloading existing service..."
    launchctl unload "$LAUNCH_AGENT_PATH" 2>/dev/null || true
fi

cp "$SCRIPT_DIR/com.ciplumber.plist" "$LAUNCH_AGENT_PATH"
launchctl load "$LAUNCH_AGENT_PATH"
echo "✓ Service installed and loaded"
echo ""

echo "==============================="
echo "Installation Complete!"
echo "==============================="
echo ""
echo "The CI Plumber will now run every hour automatically."
echo ""
echo "Useful commands:"
echo "  - View logs: tail -f $SCRIPT_DIR/logs/ci-plumber-\$(date +%Y-%m-%d).log"
echo "  - Manual run: $SCRIPT_DIR/venv/bin/python $SCRIPT_DIR/ci_plumber.py"
echo "  - Stop service: launchctl unload $LAUNCH_AGENT_PATH"
echo "  - Start service: launchctl load $LAUNCH_AGENT_PATH"
echo ""
echo "Don't forget to add your GitHub token to config.yaml!"

