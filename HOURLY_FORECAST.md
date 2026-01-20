# Hourly Forecast Feature

The weather alert bot now supports detailed 48-hour hourly forecasts using the OpenWeatherMap API.

## Overview

- **Hours 0-12:** Every hour (12 data points)
- **Hours 12-48:** Every 4 hours (9 data points)
- **Total:** ~21 data points instead of cramming all 48 hours

This smart filtering keeps the forecast readable while maintaining detail for the critical next 12 hours.

## Usage

### In a standalone script:

```python
from weather_monitor import WeatherMonitor
from hourly_forecast import HourlyForecastFormatter
import os

# Get API key from environment
api_key = os.getenv('OPENWEATHERMAP_API_KEY')
weather_monitor = WeatherMonitor(api_key)

# Get forecast for a location
location = {'name': 'London', 'city': 'London, UK'}
forecast = weather_monitor.get_forecast(location)

# Format hourly forecast for Telegram
hourly_text = HourlyForecastFormatter.format_hourly_forecast(forecast)
print(hourly_text)
```

### In main.py integration example:

```python
from hourly_forecast import HourlyForecastFormatter

# After getting forecasts
forecasts = weather_monitor.get_forecasts_for_locations(locations)

# For each forecast, you can add:
for forecast in forecasts:
    hourly_section = HourlyForecastFormatter.format_hourly_forecast(forecast)
    # Include hourly_section in your Telegram message
```

## API Information

- **Endpoint:** `/forecast` (currently used)
- **Data Points:** 3-hourly for 5 days (40 forecasts)
- **Free Tier:** Includes hourly data

All hourly data comes from the existing API calls - no additional API requests needed.

## Features

Each hourly forecast entry includes:
- **Time** (HH:MM format)
- **Temperature** (°C)
- **Wind Speed** (km/h)
- **Weather Condition** (with emoji)
- **Precipitation Probability** (%)

## Display Example

```
⏰ NEXT 48 HOURS (hourly → every 4 hours)

Time    │ Temp   │ Wind    │ Condition     │ Rain
────────┼────────┼─────────┼───────────────┼─────
  00:00 │  10.5°C │  15.2km/h │ ☀️ Clear        │  5%
  01:00 │  10.2°C │  14.8km/h │ ☀️ Clear        │  3%
  ...
  12:00 │  12.5°C │  18.5km/h │ ☁️ Cloudy       │ 20%
────────┼────────┼─────────┼───────────────┼─────
(switching to 4-hourly forecast)
────────┼────────┼─────────┼───────────────┼─────
  16:00 │  11.8°C │  22.0km/h │ 🌧️ Rainy        │ 60%
  20:00 │   9.5°C │  25.0km/h │ 🌧️ Rainy        │ 75%
  ...
```

## Methods

### HourlyForecastFormatter.format_hourly_forecast(forecast)
Returns a complete formatted Telegram message with the 48-hour hourly forecast.

### HourlyForecastFormatter.get_filtered_hourly_forecast(forecast)
Returns the raw filtered list of forecast entries without formatting.

### HourlyForecastFormatter.format_hourly_line(forecast_entry)
Formats a single hourly forecast entry as a table row.
