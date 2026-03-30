#!/bin/bash

# Silver Tier Setup Script
# Installs Playwright and prepares WhatsApp watcher

echo "=========================================="
echo "Silver Tier Setup - WhatsApp Watcher"
echo "=========================================="
echo ""

# Check Python version
echo "📋 Checking Python version..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "   Python version: $python_version"
echo ""

# Install Playwright
echo "📦 Installing Playwright..."
pip install playwright
if [ $? -eq 0 ]; then
    echo "   ✅ Playwright installed"
else
    echo "   ❌ Failed to install Playwright"
    exit 1
fi
echo ""

# Install Playwright browsers
echo "🌐 Installing Playwright browsers (Chromium)..."
echo "   This may take a few minutes..."
playwright install chromium
if [ $? -eq 0 ]; then
    echo "   ✅ Chromium browser installed"
else
    echo "   ❌ Failed to install Chromium"
    exit 1
fi
echo ""

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p Watchers/whatsapp_session
mkdir -p Logs
echo "   ✅ Directories created"
echo ""

# Verify installation
echo "✅ Verifying installation..."
python3 -c "from playwright.sync_api import sync_playwright; print('   ✅ Playwright import successful')"
echo ""

echo "=========================================="
echo "✅ Silver Tier Setup Complete!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Run: python3 Watchers/whatsapp_watcher.py"
echo "2. Scan QR code with your phone"
echo "3. Wait for messages to be detected"
echo ""
echo "See SILVER_TIER_SETUP.md for detailed instructions"
echo ""
