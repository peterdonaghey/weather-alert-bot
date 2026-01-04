"""
Alert manager for checking weather conditions and generating alerts.
Evaluates forecast data against configured thresholds.
"""

from typing import Dict, List, Any, Optional
from datetime import datetime
import logging


logger = logging.getLogger(__name__)


class Alert:
    """Represents a weather alert."""
    
    def __init__(
        self,
        location_name: str,
        alert_type: str,
        severity: str,
        message: str,
        details: Dict[str, Any],
        forecast_date: datetime
    ):
        """
        Initialize alert.
        
        Args:
            location_name: Name of location
            alert_type: Type of alert (wind, storm, temperature, etc.)
            severity: Alert severity (low, moderate, high, severe)
            message: Human-readable alert message
            details: Dictionary with alert details
            forecast_date: Date of forecast
        """
        self.location_name = location_name
        self.alert_type = alert_type
        self.severity = severity
        self.message = message
        self.details = details
        self.forecast_date = forecast_date
        self.created_at = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert alert to dictionary."""
        return {
            'location_name': self.location_name,
            'alert_type': self.alert_type,
            'severity': self.severity,
            'message': self.message,
            'details': self.details,
            'forecast_date': self.forecast_date.isoformat(),
            'created_at': self.created_at.isoformat()
        }
    
    def format_telegram_message(self, use_emoji: bool = True) -> str:
        """
        Format alert as Telegram message.
        
        Args:
            use_emoji: Whether to include emoji
            
        Returns:
            Formatted message string
        """
        # emoji mapping
        emoji_map = {
            'wind': '💨',
            'storm': '⛈️',
            'temperature': '🌡️',
            'precipitation': '🌧️',
            'weather_conditions': '⚠️'
        }
        
        severity_emoji = {
            'low': '🟢',
            'moderate': '🟡',
            'high': '🟠',
            'severe': '🔴'
        }
        
        lines = []
        
        # header with alert type
        if use_emoji:
            alert_emoji = emoji_map.get(self.alert_type, '⚠️')
            severity_indicator = severity_emoji.get(self.severity, '⚠️')
            lines.append(f"{alert_emoji} *{self.alert_type.upper()} ALERT* {severity_indicator}")
        else:
            lines.append(f"*{self.alert_type.upper()} ALERT* [{self.severity.upper()}]")
        
        lines.append("")
        
        # location and date
        date_str = self.forecast_date.strftime("%A, %B %d")
        lines.append(f"📍 *Location:* {self.location_name}")
        lines.append(f"📅 *Date:* {date_str}")
        lines.append("")
        
        # main message
        lines.append(f"*{self.message}*")
        lines.append("")
        
        # details
        if self.details:
            lines.append("*Details:*")
            for key, value in self.details.items():
                # format key nicely
                formatted_key = key.replace('_', ' ').title()
                
                # format value
                if isinstance(value, float):
                    formatted_value = f"{value:.1f}"
                else:
                    formatted_value = str(value)
                
                lines.append(f"  • {formatted_key}: {formatted_value}")
        
        return "\n".join(lines)


class AlertManager:
    """Manages alert checking and generation."""
    
    def __init__(self, alert_config: Dict[str, Any]):
        """
        Initialize alert manager.
        
        Args:
            alert_config: Alert configuration from config file
        """
        self.alert_config = alert_config
    
    def check_alerts(
        self,
        forecast_data: Dict[str, Any],
        days_ahead: int = 1
    ) -> List[Alert]:
        """
        Check forecast data for alert conditions.
        
        Args:
            forecast_data: Forecast data from WeatherMonitor
            days_ahead: Number of days ahead to check
            
        Returns:
            List of Alert objects
        """
        alerts = []
        
        # get daily summary for the target day
        from weather_monitor import WeatherMonitor
        monitor = WeatherMonitor(api_key="")  # dummy instance for method access
        daily_summary = monitor.get_daily_summary(forecast_data, days_ahead)
        
        if not daily_summary:
            logger.warning(
                f"no forecast data available for {days_ahead} day(s) ahead "
                f"for {forecast_data['location_name']}"
            )
            return alerts
        
        # check each alert type
        if self.alert_config.get('wind', {}).get('enabled', False):
            wind_alert = self._check_wind_alert(daily_summary)
            if wind_alert:
                alerts.append(wind_alert)
        
        if self.alert_config.get('storm', {}).get('enabled', False):
            storm_alert = self._check_storm_alert(daily_summary)
            if storm_alert:
                alerts.append(storm_alert)
        
        if self.alert_config.get('temperature', {}).get('enabled', False):
            temp_alert = self._check_temperature_alert(daily_summary)
            if temp_alert:
                alerts.append(temp_alert)
        
        if self.alert_config.get('precipitation', {}).get('enabled', False):
            precip_alert = self._check_precipitation_alert(daily_summary)
            if precip_alert:
                alerts.append(precip_alert)
        
        if self.alert_config.get('weather_conditions', {}).get('enabled', False):
            condition_alert = self._check_weather_conditions_alert(daily_summary)
            if condition_alert:
                alerts.append(condition_alert)
        
        return alerts
    
    def _check_wind_alert(self, daily_summary: Dict[str, Any]) -> Optional[Alert]:
        """Check for wind speed alerts."""
        wind_config = self.alert_config['wind']
        threshold = wind_config.get('threshold_kmh', 50)
        
        max_wind = daily_summary['wind_speed_max']
        max_gust = daily_summary['wind_gust_max']
        
        # check if wind exceeds threshold
        if max_wind >= threshold or max_gust >= threshold:
            # determine severity
            if max_wind >= threshold * 1.5 or max_gust >= threshold * 1.5:
                severity = 'severe'
            elif max_wind >= threshold * 1.2 or max_gust >= threshold * 1.2:
                severity = 'high'
            else:
                severity = 'moderate'
            
            message = f"high winds expected with gusts up to {max_gust:.0f} km/h"
            
            details = {
                'max_wind_speed_kmh': max_wind,
                'max_wind_gust_kmh': max_gust,
                'threshold_kmh': threshold
            }
            
            return Alert(
                location_name=daily_summary['location_name'],
                alert_type='wind',
                severity=severity,
                message=message,
                details=details,
                forecast_date=daily_summary['date']
            )
        
        return None
    
    def _check_storm_alert(self, daily_summary: Dict[str, Any]) -> Optional[Alert]:
        """Check for storm conditions (high wind + precipitation)."""
        storm_config = self.alert_config['storm']
        wind_threshold = storm_config.get('wind_gust_threshold_kmh', 70)
        precip_threshold = storm_config.get('precipitation_threshold_mm', 20)
        
        max_gust = daily_summary['wind_gust_max']
        total_precip = daily_summary['precipitation_total']
        
        # storm = high winds AND heavy precipitation
        if max_gust >= wind_threshold and total_precip >= precip_threshold:
            severity = 'severe'
            message = f"storm conditions expected with strong winds up to {max_gust:.0f} km/h and heavy precipitation ({total_precip:.1f} mm)"
            
            details = {
                'max_wind_gust_kmh': max_gust,
                'total_precipitation_mm': total_precip,
                'wind_threshold_kmh': wind_threshold,
                'precipitation_threshold_mm': precip_threshold
            }
            
            return Alert(
                location_name=daily_summary['location_name'],
                alert_type='storm',
                severity=severity,
                message=message,
                details=details,
                forecast_date=daily_summary['date']
            )
        
        return None
    
    def _check_temperature_alert(self, daily_summary: Dict[str, Any]) -> Optional[Alert]:
        """Check for temperature extreme alerts."""
        temp_config = self.alert_config['temperature']
        min_threshold = temp_config.get('min_temp_c')
        max_threshold = temp_config.get('max_temp_c')
        
        temp_min = daily_summary['temp_min']
        temp_max = daily_summary['temp_max']
        
        # check for extreme cold
        if min_threshold is not None and temp_min <= min_threshold:
            severity = 'high' if temp_min <= min_threshold - 5 else 'moderate'
            message = f"very cold temperatures expected with lows of {temp_min:.0f}°c"
            
            details = {
                'min_temperature_c': temp_min,
                'threshold_c': min_threshold
            }
            
            return Alert(
                location_name=daily_summary['location_name'],
                alert_type='temperature',
                severity=severity,
                message=message,
                details=details,
                forecast_date=daily_summary['date']
            )
        
        # check for extreme heat
        if max_threshold is not None and temp_max >= max_threshold:
            severity = 'high' if temp_max >= max_threshold + 5 else 'moderate'
            message = f"very hot temperatures expected with highs of {temp_max:.0f}°c"
            
            details = {
                'max_temperature_c': temp_max,
                'threshold_c': max_threshold
            }
            
            return Alert(
                location_name=daily_summary['location_name'],
                alert_type='temperature',
                severity=severity,
                message=message,
                details=details,
                forecast_date=daily_summary['date']
            )
        
        return None
    
    def _check_precipitation_alert(self, daily_summary: Dict[str, Any]) -> Optional[Alert]:
        """Check for heavy precipitation alerts."""
        precip_config = self.alert_config['precipitation']
        threshold = precip_config.get('threshold_mm', 30)
        
        total_precip = daily_summary['precipitation_total']
        precip_prob = daily_summary['precipitation_probability_max']
        
        if total_precip >= threshold:
            # determine severity
            if total_precip >= threshold * 2:
                severity = 'severe'
            elif total_precip >= threshold * 1.5:
                severity = 'high'
            else:
                severity = 'moderate'
            
            message = f"heavy precipitation expected ({total_precip:.1f} mm) with {precip_prob:.0f}% probability"
            
            details = {
                'total_precipitation_mm': total_precip,
                'probability_percent': precip_prob,
                'threshold_mm': threshold
            }
            
            return Alert(
                location_name=daily_summary['location_name'],
                alert_type='precipitation',
                severity=severity,
                message=message,
                details=details,
                forecast_date=daily_summary['date']
            )
        
        return None
    
    def _check_weather_conditions_alert(self, daily_summary: Dict[str, Any]) -> Optional[Alert]:
        """Check for specific weather condition alerts."""
        condition_config = self.alert_config['weather_conditions']
        alert_conditions = condition_config.get('alert_on', [])
        
        # normalize conditions to lowercase for comparison
        alert_conditions_lower = [c.lower() for c in alert_conditions]
        forecast_conditions = [c.lower() for c in daily_summary['weather_conditions']]
        
        # check if any alert condition matches
        matching_conditions = [
            c for c in forecast_conditions
            if any(alert_cond in c for alert_cond in alert_conditions_lower)
        ]
        
        if matching_conditions:
            severity = 'moderate'
            conditions_str = ", ".join(matching_conditions)
            message = f"adverse weather conditions expected: {conditions_str}"
            
            details = {
                'weather_conditions': matching_conditions,
                'alert_on': alert_conditions
            }
            
            return Alert(
                location_name=daily_summary['location_name'],
                alert_type='weather_conditions',
                severity=severity,
                message=message,
                details=details,
                forecast_date=daily_summary['date']
            )
        
        return None
    
    def check_all_locations(
        self,
        forecast_data_list: List[Dict[str, Any]]
    ) -> List[Alert]:
        """
        Check alerts for multiple locations.
        
        Args:
            forecast_data_list: List of forecast data from WeatherMonitor
            
        Returns:
            List of all alerts across locations
        """
        all_alerts = []
        
        for forecast_data in forecast_data_list:
            location_name = forecast_data['location_name']
            logger.info(f"checking alerts for {location_name}")
            
            # check each configured alert type for days ahead
            for alert_type, alert_config in self.alert_config.items():
                if not isinstance(alert_config, dict):
                    continue
                
                if not alert_config.get('enabled', False):
                    continue
                
                days_ahead = alert_config.get('check_days_ahead', 1)
                
                alerts = self.check_alerts(forecast_data, days_ahead)
                all_alerts.extend(alerts)
        
        logger.info(f"generated {len(all_alerts)} alert(s)")
        return all_alerts

