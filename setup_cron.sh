#!/bin/bash
# Cron job setup script for weather alert bot

echo "setting up cron job for weather alert bot..."

# get current directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

# create cron job entry
CRON_ENTRY="0 8 * * * cd $SCRIPT_DIR && python3 main.py --check-now >> weather_alert.log 2>&1"

# check if cron job already exists
if crontab -l 2>/dev/null | grep -q "weather alert bot"; then
    echo "cron job already exists"
else
    # add cron job
    (crontab -l 2>/dev/null; echo "# weather alert bot"; echo "$CRON_ENTRY") | crontab -
    echo "cron job added successfully"
fi

echo ""
echo "current crontab:"
crontab -l

echo ""
echo "✅ setup complete!"
echo "the bot will run daily at 8:00 am"
echo ""
echo "to view logs: tail -f $SCRIPT_DIR/weather_alert.log"
echo "to remove cron job: crontab -e (then delete the weather alert bot lines)"

