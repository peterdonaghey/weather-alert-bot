#!/bin/bash

# Simple Telegram Bot Setup Script
# This walks you through setting up a Telegram bot step by step

set -e

echo "================================================"
echo "  Telegram Bot Setup - Interactive Wizard"
echo "================================================"
echo ""

# Check if .env file exists
if [ -f ".env" ]; then
    echo "⚠️  .env file already exists."
    read -p "Do you want to overwrite it? (y/n): " overwrite
    if [ "$overwrite" != "y" ]; then
        echo "Setup cancelled."
        exit 0
    fi
    rm .env
fi

# Create .env file
touch .env

echo "Step 1: Create Your Bot with BotFather"
echo "======================================="
echo ""
echo "1. Open Telegram and search for: @BotFather"
echo "2. Start a chat and send: /newbot"
echo "3. BotFather will ask for a name (e.g., 'My Weather Bot')"
echo "4. Then it will ask for a username (must end in 'bot', e.g., 'my_weather_alert_bot')"
echo "5. BotFather will give you a token that looks like:"
echo "   123456789:ABCdefGHIjklMNOpqrsTUVwxyz-1234567890"
echo ""
read -p "Press ENTER when you've created your bot and have the token..."
echo ""

# Get bot token
while true; do
    read -p "Paste your bot token here: " BOT_TOKEN
    
    if [ -z "$BOT_TOKEN" ]; then
        echo "❌ Token cannot be empty. Please try again."
        continue
    fi
    
    if [[ ! "$BOT_TOKEN" =~ ^[0-9]+:[A-Za-z0-9_-]+$ ]]; then
        echo "❌ That doesn't look like a valid bot token."
        read -p "Try again? (y/n): " retry
        if [ "$retry" != "y" ]; then
            exit 1
        fi
        continue
    fi
    
    break
done

echo ""
echo "✅ Bot token saved!"
echo "TELEGRAM_BOT_TOKEN=$BOT_TOKEN" >> .env
echo ""

# Get chat ID
echo "Step 2: Get Your Chat ID"
echo "========================"
echo ""
echo "1. Open Telegram and search for: @userinfobot"
echo "2. Start a chat and click 'Start'"
echo "3. The bot will show you your ID (a number like: 123456789)"
echo ""
read -p "Press ENTER when you're ready..."
echo ""

while true; do
    read -p "Enter your chat ID: " CHAT_ID
    
    if [ -z "$CHAT_ID" ]; then
        echo "❌ Chat ID cannot be empty. Please try again."
        continue
    fi
    
    if [[ ! "$CHAT_ID" =~ ^-?[0-9]+$ ]]; then
        echo "❌ Chat ID should be a number (can be negative for groups)."
        read -p "Try again? (y/n): " retry
        if [ "$retry" != "y" ]; then
            exit 1
        fi
        continue
    fi
    
    break
done

echo ""
echo "✅ Chat ID saved!"
echo "TELEGRAM_CHAT_ID=$CHAT_ID" >> .env
echo ""

# Test the connection
echo "Step 3: Test the Connection"
echo "============================"
echo ""
read -p "Do you want to test the bot now? (y/n): " test_bot

if [ "$test_bot" = "y" ]; then
    echo ""
    echo "⏳ Sending test message..."
    
    # Send test message using curl
    TEXT="🎉 *Bot Setup Complete!*%0A%0AYour Telegram bot is now configured and working correctly."
    
    RESPONSE=$(curl -s -X POST "https://api.telegram.org/bot${BOT_TOKEN}/sendMessage" \
        -d "chat_id=${CHAT_ID}" \
        -d "text=${TEXT}" \
        -d "parse_mode=Markdown")
    
    if echo "$RESPONSE" | grep -q '"ok":true'; then
        echo "✅ Test message sent successfully!"
        echo ""
        echo "Check your Telegram - you should have received a message from your bot."
    else
        echo "❌ Failed to send message. Error:"
        echo "$RESPONSE" | grep -o '"description":"[^"]*"' || echo "Unknown error"
        echo ""
        echo "Common issues:"
        echo "  - Make sure you've started a chat with your bot (send /start)"
        echo "  - Double-check your bot token and chat ID"
    fi
fi

echo ""
echo "================================================"
echo "  ✨ Setup Complete!"
echo "================================================"
echo ""
echo "Your credentials have been saved to: .env"
echo ""
echo "What's in your .env file:"
echo "  TELEGRAM_BOT_TOKEN=$BOT_TOKEN"
echo "  TELEGRAM_CHAT_ID=$CHAT_ID"
echo ""
echo "⚠️  IMPORTANT: Never commit the .env file to git!"
echo ""
echo "Next steps:"
echo "  - Keep your .env file in this directory"
echo "  - Use these environment variables in your projects"
echo "  - To send messages, use the Telegram Bot API"
echo ""
echo "Quick test command:"
echo "  curl -X POST \"https://api.telegram.org/bot${BOT_TOKEN}/sendMessage\" \\"
echo "    -d \"chat_id=${CHAT_ID}\" \\"
echo "    -d \"text=Hello from bash!\""
echo ""

