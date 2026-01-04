# weather alert bot

telegram bot that monitors weather conditions and sends daily forecasts with alerts when specific conditions are detected.

## features

- daily weather summaries via telegram
- customizable weather alerts (wind, rain, temperature, etc.)
- multi-location support
- auto-subscribe system - anyone who messages your bot gets added
- runs automatically via github actions (no server needed)

## quick setup

### 1. run the telegram bot setup script

```bash
./telegram-bot-setup.sh
```

this will walk you through:
- creating a telegram bot with @BotFather
- getting your chat ID
- saving credentials to `.env`

### 2. configure your locations and alerts

edit `config.yaml`:

```yaml
locations:
  - name: "Home"
    city: "London"
    
alerts:
  high_wind:
    enabled: true
    threshold: 50  # km/h
  heavy_rain:
    enabled: true
    threshold: 10  # mm/hour
```

### 3. test locally

```bash
python main.py --verbose
```

### 4. deploy to github actions

the bot runs automatically every day at 08:00 UTC via github actions.

when someone sends `/start` to your bot, they're automatically added to the subscriber list and committed to the repo by the github action.

## project structure

```
weather-alert-bot/
├── main.py              # main script
├── weather_monitor.py   # openweathermap integration
├── alert_manager.py     # alert logic
├── telegram_bot.py      # telegram notifications
├── auto_subscribe.py    # handles auto-subscribing users
├── subscribers.py       # manages subscribers.json
├── config_loader.py     # config parser
├── config.yaml          # your configuration
├── subscribers.json     # list of subscribed chat IDs
└── .github/workflows/   # github actions config
```

## alert types

- `high_wind` - sustained wind speed
- `wind_gusts` - wind gust speed
- `heavy_rain` - rainfall intensity
- `cold` - low temperature threshold
- `hot` - high temperature threshold
- `storm` - thunderstorms
- `snow` - snow conditions
- `poor_visibility` - fog/mist

## environment variables

required in `.env`:

- `OPENWEATHERMAP_API_KEY` - from openweathermap.org (free tier works)
- `TELEGRAM_BOT_TOKEN` - from @BotFather
- `GITHUB_TOKEN` - automatically provided by github actions

## api usage

using openweathermap free tier:
- 1,000 calls/day
- 5 day / 3 hour forecast
- 1 call per location per day

## how auto-subscribe works

1. github actions runs daily
2. checks telegram for new messages
3. adds any new chat IDs to `subscribers.json`
4. commits and pushes the updated file
5. sends weather updates to all subscribers

no need to run a server 24/7!
