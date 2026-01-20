"""
Hourly forecast formatter for next 48 hours.
Provides detailed hourly weather data with smart filtering:
- Every hour for the next 12 hours
- Every 4 hours for hours 12-48
"""

from typing import Dict, List, Any
from datetime import datetime, timedelta
import logging


logger = logging.getLogger(__name__)


class HourlyForecastFormatter:
    """Formats hourly forecast data for display."""

    @staticmethod
    def get_filtered_hourly_forecast(forecast: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Get 48-hour forecast at 3-hourly intervals.
        The OpenWeatherMap API provides 3-hourly data, so we return all available forecasts
        for the next 48 hours (approximately 16 data points).

        Args:
            forecast: Forecast data from WeatherMonitor.get_forecast()

        Returns:
            List of 3-hourly forecast entries for next 48 hours
        """
        now = datetime.now()
        forty_eight_hours_later = now + timedelta(hours=48)

        filtered = []

        for f in forecast["forecasts"]:
            if f["time"] < now:
                continue
            elif f["time"] > forty_eight_hours_later:
                break
            else:
                filtered.append(f)

        return filtered

    @staticmethod
    def _get_condition_emoji(weather: str) -> str:
        """Get emoji for weather condition."""
        condition_lower = weather.lower()

        if "thunder" in condition_lower:
            return "⛈️"
        elif "snow" in condition_lower:
            return "🌨️"
        elif "rain" in condition_lower:
            return "🌧️"
        elif "cloud" in condition_lower:
            return "☁️"
        elif "clear" in condition_lower or "sunny" in condition_lower:
            return "☀️"
        else:
            return "🌤️"

    @staticmethod
    def _get_rainfall_visual(rainfall_mm: float) -> str:
        """Get visual indicator for rainfall."""
        if rainfall_mm >= 10:
            return "🌧️🌧️🌧️"
        elif rainfall_mm >= 5:
            return "🌧️🌧️"
        elif rainfall_mm > 0:
            return "💧"
        else:
            return "─"

    @staticmethod
    def format_hourly_line(forecast_entry: Dict[str, Any]) -> str:
        """
        Format a single hourly forecast as a compact line.

        Args:
            forecast_entry: Single forecast entry

        Returns:
            Formatted string for display
        """
        time_str = forecast_entry["time"].strftime("%H:%M")
        temp = forecast_entry["temperature"]
        feels_like = forecast_entry["feels_like"]
        wind = forecast_entry["wind_speed_kmh"]
        condition = forecast_entry["weather"]
        precip = forecast_entry["precipitation"]
        humidity = forecast_entry["humidity"]

        emoji = HourlyForecastFormatter._get_condition_emoji(condition)
        rain_visual = HourlyForecastFormatter._get_rainfall_visual(precip)

        # Format: HH:MM | Temp(feels) | Wind | Condition | Rain | Humidity
        return f"{time_str} │ {temp:5.1f}°({feels_like:4.1f}°) │ {wind:4.1f}km/h │ {emoji} {condition:8s} │ {rain_visual} {precip:4.1f}mm │ {humidity:2.0f}%"

    @staticmethod
    def format_hourly_forecast(forecast: Dict[str, Any]) -> str:
        """
        Create formatted hourly forecast section for the next 48 hours.
        Groups by day for better readability.

        Args:
            forecast: Forecast data from WeatherMonitor.get_forecast()

        Returns:
            Formatted hourly forecast string ready for Telegram
        """
        hourly = HourlyForecastFormatter.get_filtered_hourly_forecast(forecast)

        if not hourly:
            logger.warning(
                f"No hourly forecast available for {forecast['location_name']}"
            )
            return ""

        lines = []
        lines.append("")
        lines.append("<b>⏰ NEXT 48 HOURS (3-hourly breakdown)</b>")
        lines.append("")

        # Group by date
        current_date = None
        for h in hourly:
            forecast_date = h["time"].date()

            # Start new day section
            if forecast_date != current_date:
                if current_date is not None:
                    lines.append("")  # blank line between days

                current_date = forecast_date
                day_name = h["time"].strftime("%A, %b %d")
                lines.append(f"<b>📅 {day_name}</b>")
                lines.append(
                    "<code>Time │ Temp (feels) │ Wind   │ Condition │ Rain      │ Humid</code>"
                )
                lines.append(
                    "<code>─────┼──────────────┼────────┼───────────┼───────────┼──────</code>"
                )

            lines.append(
                "<code>" + HourlyForecastFormatter.format_hourly_line(h) + "</code>"
            )

        return "\n".join(lines)
