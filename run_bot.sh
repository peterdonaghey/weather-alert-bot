#!/bin/bash

# Quick script to run the bot in interactive mode for managing subscriptions

echo "starting weather alert bot in interactive mode..."
echo ""
echo "users can now:"
echo "  - send /subscribe to receive daily weather updates"
echo "  - send /unsubscribe to stop receiving updates"
echo "  - send /check to get weather now"
echo ""
echo "press ctrl+c to stop the bot"
echo ""

python main.py --interactive

