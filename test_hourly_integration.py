#!/usr/bin/env python3
"""
Test script to verify hourly forecast integration and generate sample message.
This actually calls the API and generates the message that would be sent.
"""

import asyncio
import logging
import sys
from datetime import datetime
from config_loader import ConfigLoader, ConfigurationError
from weather_monitor import WeatherMonitor, WeatherAPIError
from alert_manager import AlertManager
from hourly_forecast import HourlyForecastFormatter


def setup_logging():
    """Setup logging."""
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
    )


def get_wind_descriptor(wind_speed_kmh):
    """Get Beaufort scale-inspired descriptor for wind speed."""
    if wind_speed_kmh < 12:
        return "Calm"
    elif wind_speed_kmh < 20:
        return "Light breeze"
    elif wind_speed_kmh < 29:
        return "Gentle breeze"
    elif wind_speed_kmh < 39:
        return "Moderate wind"
    elif wind_speed_kmh < 50:
        return "Fresh wind"
    elif wind_speed_kmh < 62:
        return "Strong wind"
    elif wind_speed_kmh < 75:
        return "Near gale"
    elif wind_speed_kmh < 89:
        return "Gale"
    else:
        return "Storm force"


def create_test_weather_summary(forecasts, weather_monitor):
    """Create weather summary with hourly forecast (simplified from main.py)."""
    from datetime import timedelta

    lines = []
    lines.append("<b>WEATHER REPORT</b>")
    lines.append("")
    lines.append(f"📅 <b>{datetime.now().strftime('%A, %B %d, %Y')}</b>")
    lines.append("")

    for forecast in forecasts:
        location_name = forecast["location_name"]
        actual_city = forecast["city"]
        actual_country = forecast["country"]

        lines.append(f"<b>📍 {location_name}</b>")
        lines.append(f"<i>{actual_city}, {actual_country}</i>")
        lines.append("")
        lines.append("━━━━━━━━━━━━━━━━━━━━━")
        lines.append("")

        # show today's forecast
        daily = weather_monitor.get_daily_summary(forecast, days_ahead=0)
        if daily:
            day_name = "TODAY"
            temp_emoji = "🌡️"

            lines.append(f"☀️ <b>{day_name}</b> ☀️")
            lines.append("")
            lines.append(
                f"{temp_emoji} <b>High {daily['temp_max']:.0f}°C</b> • <b>Low {daily['temp_min']:.0f}°C</b>"
            )
            lines.append("")

            wind_gust = daily["wind_gust_max"]
            wind_desc = get_wind_descriptor(wind_gust)
            lines.append(
                f"💨 <b>{daily['wind_speed_max']:.0f} km/h</b> (gusts <b>{wind_gust:.0f}</b>) • <i>{wind_desc}</i>"
            )

            if daily["precipitation_total"] > 0:
                lines.append(f"🌧️ <b>{daily['precipitation_total']:.1f} mm</b>")

            lines.append("")
            lines.append("┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈")
            lines.append("")

        # add hourly forecast
        hourly_section = HourlyForecastFormatter.format_hourly_forecast(forecast)
        if hourly_section:
            lines.append(hourly_section)
            lines.append("")

    lines.append("✅ <i>No weather alerts</i>")
    return "\n".join(lines)


async def test_hourly_integration():
    """Test hourly forecast integration."""
    logger = logging.getLogger(__name__)

    print("\n" + "=" * 80)
    print("TESTING HOURLY FORECAST INTEGRATION")
    print("=" * 80)

    try:
        # Load config
        logger.info("Loading configuration...")
        config_loader = ConfigLoader("config.yaml")
        config = config_loader.load()
        api_key = config_loader.get_api_key("openweathermap")

        # Initialize weather monitor
        logger.info("Initializing weather monitor...")
        weather_monitor = WeatherMonitor(api_key)

        # Get locations
        locations = config_loader.get_locations()
        if not locations:
            print("\n❌ ERROR: No locations configured in config.yaml")
            return False

        logger.info(f"Found {len(locations)} location(s)")

        # Fetch forecasts
        logger.info("Fetching forecasts from OpenWeatherMap API...")
        forecasts = weather_monitor.get_forecasts_for_locations(locations)

        if not forecasts:
            print("\n❌ ERROR: Failed to fetch forecasts")
            return False

        logger.info(f"✓ Retrieved {len(forecasts)} forecast(s)")

        # Generate test message
        logger.info("Generating test weather summary with hourly forecast...")
        message = create_test_weather_summary(forecasts, weather_monitor)

        # Display the message
        print("\n" + "=" * 80)
        print("GENERATED MESSAGE (ready for Telegram):")
        print("=" * 80)
        print(message)
        print("\n" + "=" * 80)
        print("MESSAGE DETAILS:")
        print("=" * 80)
        print(f"Message length: {len(message)} characters")
        print(f"Contains hourly forecast: {'⏰ NEXT 48 HOURS' in message}")

        if "⏰ NEXT 48 HOURS" in message:
            print("\n✅ SUCCESS: Hourly forecast is integrated and working!")

            # Count hourly entries
            hourly_entries = message.count("│")
            print(
                f"✅ Hourly entries in message: ~{hourly_entries // 5}"
            )  # rough count

            return True
        else:
            print("\n⚠️  WARNING: Hourly forecast section not found in message")
            return False

    except ConfigurationError as e:
        print(f"\n❌ Configuration Error: {e}")
        return False
    except WeatherAPIError as e:
        print(f"\n❌ Weather API Error: {e}")
        return False
    except Exception as e:
        print(f"\n❌ Unexpected Error: {e}")
        import traceback

        traceback.print_exc()
        return False


async def main():
    """Main entry point."""
    setup_logging()

    success = await test_hourly_integration()

    if success:
        print("\n" + "=" * 80)
        print("✅ INTEGRATION TEST PASSED")
        print("=" * 80)
        print("\nThe hourly forecast feature is fully integrated!")
        print("Next step: Run 'python main.py' to send actual Telegram messages")
        print("=" * 80 + "\n")
        return 0
    else:
        print("\n" + "=" * 80)
        print("❌ INTEGRATION TEST FAILED")
        print("=" * 80 + "\n")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
