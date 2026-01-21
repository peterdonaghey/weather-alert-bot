#!/bin/bash

# Local test script - runs the bot locally to test subscribe/unsubscribe
# This processes pending messages and sends weather reports without GitHub Actions

set -e

echo "🧪 Testing weather bot locally..."
echo ""

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "❌ .env file not found. Run telegram-bot-setup.sh first."
    exit 1
fi

# Load environment variables
export $(cat .env | grep -v '^#' | xargs)

# Check required vars
if [ -z "$TELEGRAM_BOT_TOKEN" ]; then
    echo "❌ TELEGRAM_BOT_TOKEN not set in .env"
    exit 1
fi

echo "✅ Environment loaded"
echo ""

# Run the bot
echo "🚀 Running weather check..."
echo "   This will:"
echo "   - Process pending messages (subscribe/unsubscribe)"
echo "   - Send weather reports to all subscribers"
echo "   - Update subscribers.json locally"
echo ""

python main.py --log-level INFO

echo ""
echo "✅ Test complete!"
echo ""
echo "Check subscribers.json to see if your changes were saved:"
echo "  cat subscribers.json"
