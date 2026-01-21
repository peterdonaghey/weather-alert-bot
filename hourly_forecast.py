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
        Format a single hourly forecast as a compact, mobile-friendly line.

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

        # Mobile-friendly format: compact with emojis, no fixed-width columns
        # Format: HH:MM 🌡️ Temp(Feels) 💨 Wind 🌧️ Rain 💧 Humid Condition
        parts = [
            f"<b>{time_str}</b>",
            f"🌡️ {temp:.0f}°({feels_like:.0f}°)",
            f"💨 {wind:.0f}km/h",
        ]
        
        # Only show rain if > 0
        if precip > 0:
            parts.append(f"{rain_visual} {precip:.1f}mm")
        
        parts.append(f"💧 {humidity:.0f}%")
        parts.append(f"{emoji} {condition}")
        
        return " • ".join(parts)

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

            # Mobile-friendly format - no code blocks, wraps naturally
            lines.append(HourlyForecastFormatter.format_hourly_line(h))

        return "\n".join(lines)
