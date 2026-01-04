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
from telegram_bot import TelegramNotifier, TelegramBotApp


def _create_weather_summary(forecasts, weather_monitor, use_emoji=True):
    """Create a summary message of weather forecasts."""
    from datetime import datetime, timedelta
    
    lines = []
    
    if use_emoji:
        lines.append("🌤️ *Weather Forecast*")
    else:
        lines.append("*Weather Forecast*")
    
    lines.append("")
    lines.append(f"📅 *{datetime.now().strftime('%A, %B %d, %Y')}*")
    lines.append("")
    
    for forecast in forecasts:
        location_name = forecast['location_name']
        actual_city = forecast['city']
        actual_country = forecast['country']
        
        if use_emoji:
            lines.append(f"📍 *{location_name}*")
        else:
            lines.append(f"*{location_name}*")
        
        # show actual location from API
        lines.append(f"_{actual_city}, {actual_country}_")
        lines.append("")
        
        # show next 3 days
        for days in range(1, 4):
            daily = weather_monitor.get_daily_summary(forecast, days_ahead=days)
            
            if daily:
                day_name = (datetime.now() + timedelta(days=days)).strftime('%A')
                lines.append(f"*{day_name}:*")
                lines.append(f"  🌡️  {daily['temp_min']:.0f}°C - {daily['temp_max']:.0f}°C")
                lines.append(f"  💨 {daily['wind_speed_max']:.0f} km/h" + 
                           (f" (gusts {daily['wind_gust_max']:.0f})" if daily['wind_gust_max'] > daily['wind_speed_max'] else ""))
                
                if daily['precipitation_total'] > 0:
                    lines.append(f"  🌧️  {daily['precipitation_total']:.1f} mm")
                
                conditions = ', '.join(daily['weather_conditions'])
                lines.append(f"  {conditions}")
                lines.append("")
        
        lines.append("")
    
    lines.append("✅ _No weather alerts_")
    
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
    verbose: bool = False
) -> int:
    """
    Check weather for all locations and send alerts if needed.
    
    Args:
        config_loader: Configuration loader instance
        verbose: Whether to print verbose output
        
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
            summary_message = _create_weather_summary(forecasts, weather_monitor, use_emoji)
            results = await notifier.send_message(summary_message, parse_mode='Markdown')
        
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


async def run_bot_interactive(config_loader: ConfigLoader):
    """
    Run bot in interactive mode with commands.
    
    Args:
        config_loader: Configuration loader instance
    """
    logger = logging.getLogger(__name__)
    
    try:
        # load configuration
        config = config_loader.load()
        telegram_config = config_loader.get_telegram_config()
        
        # initialize components
        api_key = config_loader.get_api_key('openweathermap')
        weather_monitor = WeatherMonitor(api_key)
        alert_manager = AlertManager(config_loader.get_alerts())
        
        # create bot app
        bot_app = TelegramBotApp(
            bot_token=telegram_config['bot_token'],
            weather_monitor=weather_monitor,
            alert_manager=alert_manager,
            config_loader=config_loader
        )
        
        logger.info("starting telegram bot in interactive mode...")
        logger.info("press ctrl+c to stop")
        
        await bot_app.run()
        
    except KeyboardInterrupt:
        logger.info("stopping bot...")
    except Exception as e:
        logger.error(f"error running bot: {e}", exc_info=True)
        sys.exit(1)


async def run_scheduled(config_loader: ConfigLoader):
    """
    Run scheduled checks based on configuration.
    
    Args:
        config_loader: Configuration loader instance
    """
    import schedule
    import time
    
    logger = logging.getLogger(__name__)
    
    try:
        config = config_loader.load()
        schedule_config = config_loader.get_schedule_config()
        
        if not schedule_config:
            logger.error("no schedule configuration found")
            sys.exit(1)
        
        check_time = schedule_config.get('check_time', '08:00')
        timezone = schedule_config.get('timezone', 'UTC')
        
        logger.info(f"scheduling daily check at {check_time} ({timezone})")
        
        # schedule the check
        def scheduled_check():
            logger.info("running scheduled weather check...")
            asyncio.run(check_weather_and_send_alerts(config_loader))
        
        schedule.every().day.at(check_time).do(scheduled_check)
        
        logger.info("scheduler started. press ctrl+c to stop")
        
        # run scheduler
        while True:
            schedule.run_pending()
            time.sleep(60)  # check every minute
            
    except KeyboardInterrupt:
        logger.info("stopping scheduler...")
    except Exception as e:
        logger.error(f"error in scheduler: {e}", exc_info=True)
        sys.exit(1)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="weather alert bot - monitor weather and send telegram alerts",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
examples:
  # run one-time check
  python main.py --check-now
  
  # run with scheduling
  python main.py
  
  # run interactive bot
  python main.py --interactive
  
  # run with verbose logging
  python main.py --check-now --verbose
"""
    )
    
    parser.add_argument(
        '--config',
        default='config.yaml',
        help='path to configuration file (default: config.yaml)'
    )
    
    parser.add_argument(
        '--check-now',
        action='store_true',
        help='run weather check immediately and exit'
    )
    
    parser.add_argument(
        '--interactive',
        action='store_true',
        help='run bot in interactive mode with commands'
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
        '--log-file',
        help='log file path (optional)'
    )
    
    args = parser.parse_args()
    
    # setup logging
    log_level = 'DEBUG' if args.verbose else args.log_level
    setup_logging(log_level, args.log_file)
    
    logger = logging.getLogger(__name__)
    logger.info("weather alert bot starting...")
    logger.info(f"configuration file: {args.config}")
    
    # load configuration
    try:
        config_loader = ConfigLoader(args.config)
    except Exception as e:
        logger.error(f"failed to initialize config loader: {e}")
        sys.exit(1)
    
    # run in appropriate mode
    try:
        if args.check_now:
            # one-time check
            alert_count = asyncio.run(
                check_weather_and_send_alerts(config_loader, verbose=args.verbose)
            )
            
            if alert_count < 0:
                logger.error("check failed")
                sys.exit(1)
            elif alert_count == 0:
                logger.info("check completed - no alerts")
            else:
                logger.info(f"check completed - {alert_count} alert(s) sent")
            
            sys.exit(0)
            
        elif args.interactive:
            # interactive bot mode
            asyncio.run(run_bot_interactive(config_loader))
            
        else:
            # scheduled mode
            asyncio.run(run_scheduled(config_loader))
            
    except KeyboardInterrupt:
        logger.info("shutting down...")
        sys.exit(0)
    except Exception as e:
        logger.error(f"fatal error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()

