#!/usr/bin/env python3
"""
Example script showing how to use the hourly forecast feature.
This demonstrates how to integrate hourly forecasts into your bot.
"""

import asyncio
import logging
from config_loader import ConfigLoader
from weather_monitor import WeatherMonitor
from hourly_forecast import HourlyForecastFormatter


def setup_logging():
    """Setup basic logging."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )


def example_basic_usage():
    """Basic example: get and display hourly forecast."""
    print("\n" + "=" * 80)
    print("EXAMPLE 1: Basic Hourly Forecast Usage")
    print("=" * 80)

    try:
        # Load config
        config_loader = ConfigLoader("config.yaml")
        config = config_loader.load()
        api_key = config_loader.get_api_key("openweathermap")

        # Initialize weather monitor
        weather_monitor = WeatherMonitor(api_key)

        # Get forecast for first location
        locations = config_loader.get_locations()
        if not locations:
            print("No locations configured in config.yaml")
            return

        location = locations[0]
        print(f"\nFetching forecast for: {location['name']}")
        forecast = weather_monitor.get_forecast(location)

        # Get filtered hourly data
        hourly = HourlyForecastFormatter.get_filtered_hourly_forecast(forecast)
        print(f"Retrieved {len(hourly)} hourly forecast entries (filtered)")

        # Show first 3 entries
        print("\nFirst 3 hourly forecasts:")
        for i, entry in enumerate(hourly[:3]):
            time_str = entry["time"].strftime("%H:%M")
            temp = entry["temperature"]
            wind = entry["wind_speed_kmh"]
            condition = entry["weather"]
            print(f"  {i + 1}. {time_str} - {temp:.1f}°C, {wind:.1f}km/h, {condition}")

        print("\n✓ Basic usage works!")

    except Exception as e:
        print(f"✗ Error: {e}")


def example_formatted_output():
    """Example: Get formatted output ready for Telegram."""
    print("\n" + "=" * 80)
    print("EXAMPLE 2: Formatted Output for Telegram")
    print("=" * 80)

    try:
        # Load config
        config_loader = ConfigLoader("config.yaml")
        api_key = config_loader.get_api_key("openweathermap")

        # Initialize weather monitor
        weather_monitor = WeatherMonitor(api_key)

        # Get forecast
        locations = config_loader.get_locations()
        if not locations:
            print("No locations configured")
            return

        location = locations[0]
        forecast = weather_monitor.get_forecast(location)

        # Format for Telegram
        hourly_message = HourlyForecastFormatter.format_hourly_forecast(forecast)

        print("\nFormatted hourly forecast (for Telegram):")
        print(hourly_message)

        print("\n✓ Formatted output works!")

    except Exception as e:
        print(f"✗ Error: {e}")


def example_multiple_locations():
    """Example: Process hourly forecasts for multiple locations."""
    print("\n" + "=" * 80)
    print("EXAMPLE 3: Multiple Locations")
    print("=" * 80)

    try:
        # Load config
        config_loader = ConfigLoader("config.yaml")
        api_key = config_loader.get_api_key("openweathermap")

        # Initialize weather monitor
        weather_monitor = WeatherMonitor(api_key)

        # Get all locations
        locations = config_loader.get_locations()
        print(f"\nProcessing {len(locations)} location(s)...")

        for location in locations:
            print(f"\n  📍 {location['name']}")
            try:
                forecast = weather_monitor.get_forecast(location)
                hourly = HourlyForecastFormatter.get_filtered_hourly_forecast(forecast)
                print(f"     → {len(hourly)} hourly entries")
            except Exception as e:
                print(f"     → Error: {e}")

        print("\n✓ Multiple locations works!")

    except Exception as e:
        print(f"✗ Error: {e}")


def example_integration_with_main():
    """Example: How to integrate into main.py alerts."""
    print("\n" + "=" * 80)
    print("EXAMPLE 4: Integration Pattern")
    print("=" * 80)

    print("""
Integration example for main.py:

from hourly_forecast import HourlyForecastFormatter

# In your main alert sending logic:
alerts = alert_manager.check_all_locations(forecasts)

if alerts:
    # Send alerts as usual
    await notifier.send_alerts(alerts)
else:
    # Add hourly forecast to summary message
    lines = []
    lines.append("<b>WEATHER REPORT</b>")
    
    for forecast in forecasts:
        lines.append(f"<b>📍 {forecast['location_name']}</b>")
        
        # Add hourly forecast section
        hourly_section = HourlyForecastFormatter.format_hourly_forecast(forecast)
        lines.append(hourly_section)
    
    message = "\\n".join(lines)
    await notifier.send_message(message, parse_mode='HTML')
    """)

    print("✓ Integration example provided above")


if __name__ == "__main__":
    setup_logging()

    print("\n" + "=" * 80)
    print("HOURLY FORECAST FEATURE - EXAMPLES")
    print("=" * 80)
    print("\nThis script demonstrates how to use the new hourly forecast feature.")
    print("Make sure config.yaml is properly configured with locations.")

    # Run examples
    example_basic_usage()
    example_multiple_locations()
    example_formatted_output()
    example_integration_with_main()

    print("\n" + "=" * 80)
    print("All examples completed!")
    print("=" * 80 + "\n")
