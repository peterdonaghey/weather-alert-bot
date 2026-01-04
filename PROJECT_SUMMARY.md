# weather alert bot - project summary

**status:** ✅ complete and ready to use

**created:** january 4, 2026

---

## project overview

a python-based weather monitoring system that:
- checks weather forecasts daily via openweathermap api
- monitors multiple locations simultaneously  
- sends telegram notifications when configured weather conditions are detected
- supports multiple alert types (wind, storms, temperature, precipitation)
- includes reusable telegram bot boilerplate

---

## key features

✨ **multi-location monitoring** - track weather for unlimited locations
✨ **configurable alerts** - custom thresholds for each alert type
✨ **multiple alert types** - wind, storms, temperature, precipitation, weather conditions
✨ **day-ahead alerts** - get notified the day before bad weather
✨ **telegram notifications** - rich formatted messages with emoji
✨ **flexible scheduling** - built-in scheduler or cron/systemd
✨ **comprehensive logging** - detailed logs for debugging
✨ **error handling** - graceful failures, continues with other locations
✨ **interactive bot mode** - optional commands (/check, /status)

---

## project structure

```
weather-alert-bot/
├── main.py                     # main entry point
├── config.yaml                 # configuration file
├── requirements.txt            # python dependencies
├── env.example                 # environment variables template
│
├── config_loader.py            # configuration parsing
├── weather_monitor.py          # weather api integration
├── alert_manager.py            # alert checking logic
├── telegram_bot.py             # telegram bot implementation
├── logger_utils.py             # logging utilities
│
├── README.md                   # main documentation
├── setup_telegram_bot.md       # telegram bot setup guide
├── ERROR_HANDLING.md           # error handling documentation
│
├── quickstart.py               # quick setup helper
├── test_system.py              # system tests
│
├── setup_cron.sh               # cron job setup script
└── weather-alert-bot.service   # systemd service file
```

---

## quick start

### 1. install dependencies

```bash
cd weather-alert-bot
pip install -r requirements.txt
```

### 2. configure environment

```bash
# copy template
cp env.example .env

# edit with your keys
nano .env
```

required keys:
- `OPENWEATHER_API_KEY` - from https://openweathermap.org/
- `TELEGRAM_BOT_TOKEN` - from @botfather
- `TELEGRAM_CHAT_ID` - from @userinfobot

### 3. configure locations and alerts

edit `config.yaml`:

```yaml
locations:
  - name: "home"
    city: "london, uk"

alerts:
  wind:
    enabled: true
    threshold_kmh: 50
```

### 4. test the bot

```bash
# quick test
python quickstart.py

# or run full check
python main.py --check-now
```

---

## usage modes

### one-time check

```bash
python main.py --check-now
```

checks weather once and sends alerts if needed.

### scheduled mode (built-in)

```bash
python main.py
```

runs continuously with daily checks at configured time.

### interactive bot mode

```bash
python main.py --interactive
```

runs telegram bot with commands:
- `/start` - start bot
- `/check` - manual weather check
- `/status` - show configuration
- `/help` - show commands

### cron job (linux/mac)

```bash
./setup_cron.sh
```

sets up daily cron job.

### systemd service (linux)

```bash
sudo cp weather-alert-bot.service /etc/systemd/system/
sudo systemctl enable weather-alert-bot
sudo systemctl start weather-alert-bot
```

runs as background service.

---

## configuration options

### locations

```yaml
locations:
  - name: "city name"
    city: "london, uk"
  
  - name: "coordinates"
    lat: 51.5074
    lon: -0.1278
```

### alert types

**wind alerts**
```yaml
wind:
  enabled: true
  threshold_kmh: 50
  check_days_ahead: 1
```

**storm alerts**
```yaml
storm:
  enabled: true
  wind_gust_threshold_kmh: 70
  precipitation_threshold_mm: 20
  check_days_ahead: 1
```

**temperature alerts**
```yaml
temperature:
  enabled: true
  min_temp_c: 0
  max_temp_c: 35
  check_days_ahead: 1
```

**precipitation alerts**
```yaml
precipitation:
  enabled: true
  threshold_mm: 30
  check_days_ahead: 1
```

**weather condition alerts**
```yaml
weather_conditions:
  enabled: true
  alert_on:
    - "thunderstorm"
    - "snow"
  check_days_ahead: 1
```

### telegram settings

```yaml
telegram:
  bot_token: "${TELEGRAM_BOT_TOKEN}"
  chat_ids:
    - "${TELEGRAM_CHAT_ID}"
  message_format:
    use_markdown: true
    include_emoji: true
```

### schedule

```yaml
schedule:
  check_time: "08:00"
  timezone: "europe/lisbon"
```

---

## api keys

### openweathermap

1. sign up at https://openweathermap.org/
2. go to api keys
3. copy key to `.env`

**free tier includes:**
- 1,000 api calls/day
- 5-day forecast
- current weather

### telegram bot

see `setup_telegram_bot.md` for complete guide.

**quick steps:**
1. message @botfather on telegram
2. send `/newbot`
3. follow prompts
4. copy token to `.env`
5. get your chat id from @userinfobot

---

## monitoring and logs

### view logs

```bash
# real-time
tail -f weather_alert.log

# recent errors
tail -n 100 weather_alert.log | grep ERROR
```

### verbose mode

```bash
python main.py --check-now --verbose
```

### log levels

```bash
python main.py --check-now --log-level DEBUG
```

---

## testing

### system test

```bash
python test_system.py
```

checks:
- dependencies installed
- modules load correctly
- files present
- configuration valid

### quick test

```bash
python quickstart.py
```

interactive test of:
- telegram bot connection
- weather api
- basic functionality

---

## troubleshooting

### bot not sending messages

- verify `TELEGRAM_BOT_TOKEN` is correct
- verify `TELEGRAM_CHAT_ID` is correct
- ensure you've sent `/start` to bot
- check bot hasn't been blocked

### weather api errors

- verify `OPENWEATHER_API_KEY` is correct
- check location spelling
- verify internet connection
- check api rate limits

### no alerts triggered

- verify alert thresholds in config.yaml
- check forecast with `--check-now --verbose`
- ensure alerts are enabled

### configuration errors

- ensure .env file exists
- check yaml syntax in config.yaml
- verify all required fields present

---

## security

- ✅ api keys in environment variables (not in code)
- ✅ .env file should be in .gitignore
- ✅ never commit tokens to git
- ✅ use separate bot tokens for dev/prod
- ✅ rotate tokens if compromised

---

## extending the bot

### add new alert type

1. add configuration to `config.yaml`
2. add checking method to `alert_manager.py`
3. call method in `check_alerts()`

### add bot command

1. add handler method to `TelegramBotApp` class
2. register in `create_application()`

### add new data source

1. create new module (e.g., `met_office_api.py`)
2. implement similar interface to `WeatherMonitor`
3. update `main.py` to use new source

---

## reusable components

### telegram bot boilerplate

`setup_telegram_bot.md` contains complete guide and examples for:
- creating bots
- sending messages
- handling commands
- formatting messages
- working with buttons

copy these patterns for any telegram bot project.

### configuration system

`config_loader.py` provides:
- yaml configuration
- environment variable substitution
- validation
- error handling

reusable for any project needing configuration.

---

## project statistics

**total files:** 16
**total lines of code:** ~3,500+
**python modules:** 6 core + 3 utility
**documentation files:** 4
**configuration files:** 2

**dependencies:**
- python-telegram-bot
- requests
- pyyaml
- python-dotenv
- schedule

---

## future enhancements

potential improvements:

1. **web dashboard** - view alerts and configuration via web ui
2. **database storage** - store alert history
3. **multiple apis** - support weatherapi, met office, etc.
4. **machine learning** - predict alerts based on patterns
5. **notification channels** - email, sms, slack, discord
6. **location groups** - group alerts by region
7. **custom alert formulas** - complex conditions
8. **alert history** - track past alerts
9. **api endpoint** - rest api for alerts
10. **mobile app** - native mobile interface

---

## license

mit license - free to use, modify, and distribute.

---

## support

- **documentation:** see readme.md and setup guides
- **telegram setup:** see setup_telegram_bot.md
- **error handling:** see error_handling.md
- **quick start:** run quickstart.py
- **system test:** run test_system.py

---

## acknowledgments

**apis used:**
- openweathermap api for weather data
- telegram bot api for notifications

**libraries:**
- python-telegram-bot for telegram integration
- requests for http
- pyyaml for configuration
- schedule for task scheduling

---

**project complete! ✨**

ready to monitor weather and send alerts. enjoy your automated weather notifications!

---

*weather alert bot - keeping you informed about upcoming weather conditions*

