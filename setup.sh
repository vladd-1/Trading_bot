#!/bin/bash

# Trading Bot Setup Script
# This script sets up a virtual environment and installs all dependencies

echo "=========================================="
echo "Trading Bot Setup"
echo "=========================================="

# Check if python3-venv is installed
if ! dpkg -l | grep -q python3.*-venv; then
    echo "Installing python3-venv..."
    sudo apt update
    sudo apt install -y python3-venv python3-full
fi

# Create virtual environment
echo "Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

echo ""
echo "=========================================="
echo "Setup Complete!"
echo "=========================================="
echo ""
echo "To activate the virtual environment, run:"
echo "  source venv/bin/activate"
echo ""
echo "To run the trading bot, use:"
echo "  python main.py"
echo ""
echo "To deactivate the virtual environment, run:"
echo "  deactivate"
echo ""
