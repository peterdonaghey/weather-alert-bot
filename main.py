#!/usr/bin/env python3
"""
Weather Alert Bot - Main Entry Point

Monitors weather conditions and sends Telegram alerts based on configured thresholds.
"""

import asyncio
import argparse
import sys
import logging
from typing import Optional
from datetime import datetime

from config_loader import ConfigLoader, ConfigurationError
from weather_monitor import WeatherMonitor, WeatherAPIError
from alert_manager import AlertManager
from telegram_bot import TelegramNotifier


def _get_wind_descriptor(wind_speed_kmh):
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


def _get_weather_emoji(weather_conditions):
    """Get appropriate emoji for weather conditions."""
    conditions_lower = [w.lower() for w in weather_conditions]
    
    # priority order - most severe first
    if any('thunderstorm' in c or 'thunder' in c for c in conditions_lower):
        return '⛈️'
    elif any('snow' in c for c in conditions_lower):
        return '🌨️'
    elif any('rain' in c for c in conditions_lower):
        if any('heavy' in c for c in conditions_lower):
            return '🌧️'
        return '🌦️'
    elif any('drizzle' in c for c in conditions_lower):
        return '🌦️'
    elif any('cloud' in c for c in conditions_lower):
        return '☁️'
    elif any('clear' in c for c in conditions_lower):
        return '☀️'
    elif any('mist' in c or 'fog' in c for c in conditions_lower):
        return '🌫️'
    else:
        return '🌤️'


def _get_temp_color_emoji(temp):
    """Get color emoji based on temperature."""
    if temp >= 30:
        return '🔥'  # hot
    elif temp >= 20:
        return '🟠'  # warm
    elif temp >= 10:
        return '🟢'  # mild
    elif temp >= 0:
        return '🔵'  # cool
    else:
        return '🧊'  # freezing


def _create_temp_bar(temp_min, temp_max):
    """Create visual temperature bar."""
    # normalize to 0-10 scale (assume range -10 to 40)
    def normalize(t):
        return max(0, min(10, int((t + 10) / 5)))
    
    min_pos = normalize(temp_min)
    max_pos = normalize(temp_max)
    
    bar = ['░'] * 11
    for i in range(min_pos, max_pos + 1):
        bar[i] = '█'
    
    return ''.join(bar)


def _create_weather_summary(forecasts, weather_monitor, use_emoji=True, claude_config=None):
    """Create a summary message of weather forecasts."""
    from datetime import datetime, timedelta
    
    lines = []
    
    # header with ASCII art border
    lines.append("<b>WEATHER REPORT</b>")
    lines.append("")
    
    # generate claude commentary if enabled
    if claude_config and claude_config.get('enabled', False):
        # extract enhanced weather data for claude with more context
        weather_data_parts = []
        location_name = forecasts[0]['location_name'] if forecasts else "Unknown"
        
        # add contextual information
        now = datetime.now()
        day_of_week = now.strftime('%A')
        month = now.strftime('%B')
        is_weekend = now.weekday() >= 5
        
        context_info = f"Location: {location_name}, {day_of_week} in {month}"
        if is_weekend:
            context_info += " (weekend)"
        weather_data_parts.append(context_info)
        
        # collect weather data with trends
        prev_temp_max = None
        prev_wind = None
        
        for forecast in forecasts:
            for days in range(0, 3):
                daily = weather_monitor.get_daily_summary(forecast, days_ahead=days)
                if daily:
                    day_name = "Today" if days == 0 else (now + timedelta(days=days)).strftime('%A')
                    
                    # build day description with trends
                    day_desc = f"{day_name}: {daily['temp_min']:.0f}-{daily['temp_max']:.0f}°C"
                    
                    # add temperature trend
                    if prev_temp_max is not None:
                        temp_change = daily['temp_max'] - prev_temp_max
                        if abs(temp_change) >= 5:
                            trend = "warmer" if temp_change > 0 else "cooler"
                            day_desc += f" ({abs(temp_change):.0f}° {trend})"
                    prev_temp_max = daily['temp_max']
                    
                    # wind with descriptor
                    wind_gust = daily['wind_gust_max']
                    wind_desc = _get_wind_descriptor(wind_gust)
                    day_desc += f", wind {wind_gust:.0f}km/h ({wind_desc})"
                    
                    # add wind trend
                    if prev_wind is not None and abs(wind_gust - prev_wind) >= 15:
                        wind_trend = "increasing" if wind_gust > prev_wind else "decreasing"
                        day_desc += f" {wind_trend}"
                    prev_wind = wind_gust
                    
                    # precipitation
                    if daily['precipitation_total'] > 0:
                        day_desc += f", rain {daily['precipitation_total']:.1f}mm"
                    
                    # conditions
                    conditions = ', '.join(daily['weather_conditions'])
                    day_desc += f" ({conditions})"
                    
                    weather_data_parts.append(day_desc)
        
        weather_summary = "; ".join(weather_data_parts)
        
        # call claude api
        from claude_commentary import generate_weather_comment
        prompt_template = claude_config.get('prompt', '')
        comment = generate_weather_comment(weather_summary, prompt_template)
        
        if comment:
            lines.append(f"<i>💬 {comment}</i>")
            lines.append("")
    
    lines.append(f"📅 <b>{datetime.now().strftime('%A, %B %d, %Y')}</b>")
    lines.append("")
    
    for forecast in forecasts:
        location_name = forecast['location_name']
        actual_city = forecast['city']
        actual_country = forecast['country']
        
        lines.append(f"<b>📍 {location_name}</b>")
        lines.append(f"<i>{actual_city}, {actual_country}</i>")
        lines.append("")
        lines.append("━━━━━━━━━━━━━━━━━━━━━")
        lines.append("")
        
        # show today and next 2 days
        days_shown = 0
        for days in range(0, 4):
            if days_shown >= 3:
                break
                
            daily = weather_monitor.get_daily_summary(forecast, days_ahead=days)
            
            if daily:
                if days == 0:
                    day_name = "TODAY"
                else:
                    day_name = (datetime.now() + timedelta(days=days)).strftime('%A').upper()
                
                weather_emoji = _get_weather_emoji(daily['weather_conditions'])
                temp_emoji = _get_temp_color_emoji(daily['temp_max'])
                
                # day header with weather emoji
                lines.append(f"{weather_emoji} <b>{day_name}</b> {weather_emoji}")
                lines.append("")
                
                # temperature - HIGH first, then LOW with color indicator
                high_temp = daily['temp_max']
                low_temp = daily['temp_min']
                
                lines.append(f"🌡️ <b>High {high_temp:.0f}°C</b> {temp_emoji} • <b>Low {low_temp:.0f}°C</b>")
                
                # visual temperature bar
                temp_bar = _create_temp_bar(low_temp, high_temp)
                lines.append(f"<code>{temp_bar}</code> <i>{low_temp:.0f}° → {high_temp:.0f}°</i>")
                lines.append("")
                
                # wind with intensity indicators and description
                wind_speed = daily['wind_speed_max']
                wind_gust = daily['wind_gust_max']
                wind_desc = _get_wind_descriptor(wind_gust)
                
                if wind_gust > 40:
                    wind_emoji = '💨💨💨'
                elif wind_gust > 25:
                    wind_emoji = '💨💨'
                else:
                    wind_emoji = '💨'
                
                wind_text = f"{wind_emoji} <b>{wind_speed:.0f} km/h</b>"
                if wind_gust > wind_speed:
                    wind_text += f" (gusts <b>{wind_gust:.0f}</b>) • <i>{wind_desc}</i>"
                else:
                    wind_text += f" • <i>{wind_desc}</i>"
                lines.append(wind_text)
                
                # precipitation with visual indicator
                if daily['precipitation_total'] > 0:
                    precip = daily['precipitation_total']
                    if precip > 20:
                        precip_emoji = '🌧️🌧️🌧️'
                        intensity = 'Heavy'
                    elif precip > 10:
                        precip_emoji = '🌧️🌧️'
                        intensity = 'Moderate'
                    else:
                        precip_emoji = '💧'
                        intensity = 'Light'
                    
                    lines.append(f"{precip_emoji} <b>{precip:.1f} mm</b> <i>({intensity})</i>")
                
                lines.append("")
                lines.append("┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈")
                lines.append("")
                
                days_shown += 1
    
    lines.append("✅ <i>No weather alerts</i>")
    
    return "\n".join(lines)


# configure logging
def setup_logging(log_level: str = "INFO", log_file: Optional[str] = None):
    """Setup logging configuration."""
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    handlers = [logging.StreamHandler(sys.stdout)]
    
    if log_file:
        handlers.append(logging.FileHandler(log_file))
    
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format=log_format,
        handlers=handlers
    )


async def check_weather_and_send_alerts(
    config_loader: ConfigLoader,
    verbose: bool = False,
    dev_chat_id: Optional[str] = None
) -> int:
    """
    Check weather for all locations and send alerts if needed.
    
    Args:
        config_loader: Configuration loader instance
        verbose: Whether to print verbose output
        dev_chat_id: If set, only send to this chat ID (for testing)
        
    Returns:
        Number of alerts sent
    """
    logger = logging.getLogger(__name__)
    
    try:
        # load configuration
        logger.info("loading configuration...")
        config = config_loader.load()
        
        # first, process any pending telegram messages and auto-subscribe
        telegram_config = config_loader.get_telegram_config()
        bot_token = telegram_config['bot_token']
        
        logger.info("checking for new subscribers...")
        from auto_subscribe import process_pending_messages
        new_subs = await process_pending_messages(bot_token)
        
        if new_subs > 0:
            logger.info(f"auto-subscribed {new_subs} new user(s)")
        
        # get API key
        api_key = config_loader.get_api_key('openweathermap')
        
        # initialize weather monitor
        logger.info("initializing weather monitor...")
        weather_monitor = WeatherMonitor(api_key)
        
        # get locations
        locations = config_loader.get_locations()
        logger.info(f"monitoring {len(locations)} location(s)")
        
        # fetch forecasts
        logger.info("fetching weather forecasts...")
        forecasts = weather_monitor.get_forecasts_for_locations(locations)
        
        if not forecasts:
            logger.warning("no forecasts retrieved")
            return 0
        
        if verbose:
            logger.info(f"retrieved {len(forecasts)} forecast(s)")
        
        # initialize alert manager
        alerts_config = config_loader.get_alerts()
        alert_manager = AlertManager(alerts_config)
        
        # check for alerts
        logger.info("checking for alert conditions...")
        alerts = alert_manager.check_all_locations(forecasts)
        
        if verbose:
            logger.info(f"generated {len(alerts)} alert(s)")
        
        # log alerts
        for alert in alerts:
            logger.info(
                f"alert: {alert.alert_type} - {alert.location_name} - {alert.severity} - {alert.message}"
            )
        
        # initialize telegram notifier
        from subscribers import get_all_chat_ids
        
        telegram_config = config_loader.get_telegram_config()
        config_chat_ids = telegram_config.get('chat_ids', [])
        
        # if dev mode, only send to specified chat id
        if dev_chat_id:
            all_chat_ids = [dev_chat_id]
            logger.info(f"dev mode: sending only to {dev_chat_id}")
        else:
            # combine config chat IDs with subscribers
            all_chat_ids = get_all_chat_ids(config_chat_ids)
        
        if not all_chat_ids:
            logger.warning("no chat ids configured and no subscribers")
            return 0
        
        logger.info(f"sending to {len(all_chat_ids)} recipient(s)")
        
        notifier = TelegramNotifier(
            bot_token=telegram_config['bot_token'],
            chat_ids=all_chat_ids
        )
        
        use_emoji = telegram_config.get('message_format', {}).get('include_emoji', True)
        
        # send alerts if any
        if alerts:
            logger.info(f"sending {len(alerts)} alert(s) via telegram...")
            results = await notifier.send_alerts(alerts, use_emoji=use_emoji)
        else:
            logger.info("no alerts triggered - sending weather summary...")
            # create weather summary message
            claude_config = config_loader.get_claude_config()
            summary_message = _create_weather_summary(forecasts, weather_monitor, use_emoji, claude_config)
            results = await notifier.send_message(summary_message, parse_mode='HTML')
        
        # log results
        success_count = len(results['success'])
        failed_count = len(results['failed'])
        
        logger.info(f"messages sent successfully to {success_count} chat(s)")
        
        if failed_count > 0:
            logger.warning(f"failed to send to {failed_count} chat(s)")
            for failure in results['failed']:
                logger.error(f"  failed: {failure['chat_id']} - {failure['error']}")
        
        await notifier.close()
        
        return len(alerts)
        
    except ConfigurationError as e:
        logger.error(f"configuration error: {e}")
        return -1
    except WeatherAPIError as e:
        logger.error(f"weather api error: {e}")
        return -1
    except Exception as e:
        logger.error(f"unexpected error: {e}", exc_info=True)
        return -1


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="weather alert bot - monitor weather and send telegram alerts"
    )
    
    parser.add_argument(
        '--config',
        default='config.yaml',
        help='path to configuration file (default: config.yaml)'
    )
    
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='enable verbose logging'
    )
    
    parser.add_argument(
        '--log-level',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
        default='INFO',
        help='set logging level'
    )
    
    parser.add_argument(
        '--dev-chat-id',
        type=str,
        help='send only to this chat id (for testing without spamming subscribers)'
    )
    
    args = parser.parse_args()
    
    # setup logging
    log_level = 'DEBUG' if args.verbose else args.log_level
    setup_logging(log_level, None)
    
    logger = logging.getLogger(__name__)
    logger.info("weather alert bot starting...")
    logger.info(f"configuration file: {args.config}")
    
    # load configuration
    try:
        config_loader = ConfigLoader(args.config)
    except Exception as e:
        logger.error(f"failed to initialize config loader: {e}")
        sys.exit(1)
    
    # run check
    alert_count = asyncio.run(
        check_weather_and_send_alerts(
            config_loader, 
            verbose=args.verbose,
            dev_chat_id=args.dev_chat_id
        )
    )
    
    if alert_count < 0:
        logger.error("check failed")
        sys.exit(1)
    elif alert_count == 0:
        logger.info("check completed - no alerts")
    else:
        logger.info(f"check completed - {alert_count} alert(s) sent")
    
    sys.exit(0)


if __name__ == "__main__":
    main()

