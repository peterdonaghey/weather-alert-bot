# weather alert telegram bot

a python-based weather monitoring system that checks forecast apis daily and sends telegram notifications when configured weather conditions are detected.

## features

- **multi-location support**: monitor multiple locations simultaneously
- **configurable alerts**: define custom thresholds for each alert type
- **multiple alert types**: wind, storms, temperature, precipitation
- **day-before alerts**: check tomorrow's forecast and alert today
- **telegram notifications**: rich formatted messages
- **error handling**: graceful failures with comprehensive logging

## quick start

### 1. setup telegram bot

follow the detailed guide in `setup_telegram_bot.md` to create your bot via botfather.

### 2. install dependencies

```bash
pip install -r requirements.txt
```

### 3. configure environment variables

```bash
cp .env.example .env
# edit .env with your api keys and chat ids
```

### 4. configure locations and alerts

edit `config.yaml` to set your locations and alert thresholds:

```yaml
locations:
  - name: "home"
    city: "london, uk"
  
  - name: "quinta"
    lat: 38.7223
    lon: -9.1393

alerts:
  wind:
    enabled: true
    threshold_kmh: 50
  
  storm:
    enabled: true
    wind_gust_threshold_kmh: 70
    precipitation_threshold_mm: 20
```

### 5. run the monitor

for a one-time check:

```bash
python main.py --check-now
```

to run with scheduler (daily checks):

```bash
python main.py
```

or set up as a cron job (see scheduling section below).

## configuration

### locations

specify locations by city name or coordinates:

```yaml
locations:
  - name: "city_name"
    city: "london, uk"
  
  - name: "coordinates"
    lat: 51.5074
    lon: -0.1278
```

### alert types

**wind alerts**
```yaml
alerts:
  wind:
    enabled: true
    threshold_kmh: 50
    check_days_ahead: 1
```

**storm alerts**
```yaml
alerts:
  storm:
    enabled: true
    wind_gust_threshold_kmh: 70
    precipitation_threshold_mm: 20
    check_days_ahead: 1
```

**temperature alerts**
```yaml
alerts:
  temperature:
    enabled: true
    min_temp_c: 0
    max_temp_c: 35
    check_days_ahead: 1
```

**precipitation alerts**
```yaml
alerts:
  precipitation:
    enabled: true
    threshold_mm: 30
    check_days_ahead: 1
```

## scheduling

### using the built-in scheduler

the script includes a scheduler that runs daily at the configured time:

```yaml
schedule:
  check_time: "08:00"
  timezone: "europe/lisbon"
```

run with: `python main.py`

### using cron (linux/mac)

```bash
# run daily at 8 am
0 8 * * * cd /path/to/weather-alert-bot && python main.py --check-now
```

### using systemd (linux)

create `/etc/systemd/system/weather-alert.service`:

```ini
[unit]
description=weather alert bot
after=network.target

[service]
type=simple
user=your_user
workingdirectory=/path/to/weather-alert-bot
execstart=/usr/bin/python3 main.py
restart=always

[install]
wantedby=multi-user.target
```

enable and start:
```bash
sudo systemctl enable weather-alert
sudo systemctl start weather-alert
```

## telegram bot commands

if you run the bot interactively, you can use these commands:

- `/start` - start the bot
- `/check` - manually trigger a weather check
- `/status` - show current configuration
- `/help` - show available commands

## api keys

### openweathermap

1. sign up at https://openweathermap.org/
2. go to api keys section
3. copy your api key
4. add to `.env` file

free tier includes:
- 1,000 calls/day
- 5-day forecast
- current weather

### telegram bot

follow `setup_telegram_bot.md` for detailed instructions.

## troubleshooting

### bot not sending messages

- verify telegram bot token in `.env`
- check chat id is correct (use @userinfobot)
- ensure bot has permission to message you (send `/start` first)

### weather api errors

- check api key is valid
- verify location coordinates/city names
- check api rate limits

### no alerts triggered

- verify alert thresholds in `config.yaml`
- check forecast data with `--check-now --verbose`
- ensure alerts are enabled

## project structure

```
weather-alert-bot/
├── config.yaml                 # main configuration
├── requirements.txt            # python dependencies
├── setup_telegram_bot.md       # telegram bot setup guide
├── main.py                     # main entry point
├── weather_monitor.py          # weather checking logic
├── telegram_bot.py             # telegram bot implementation
├── alert_manager.py            # alert condition checking
├── config_loader.py            # configuration parser
├── .env.example                # environment variables template
└── README.md                   # this file
```

## license

mit

