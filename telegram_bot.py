"""
Telegram bot for sending weather alerts and handling commands.
Uses python-telegram-bot library (v20+).
"""

import asyncio
from typing import List, Dict, Any, Optional
from telegram import Bot, Update
from telegram.ext import Application, CommandHandler, ContextTypes
from telegram.error import TelegramError
import logging


logger = logging.getLogger(__name__)


class TelegramNotifier:
    """Sends weather alerts via Telegram."""
    
    def __init__(self, bot_token: str, chat_ids: List[str]):
        """
        Initialize Telegram notifier.
        
        Args:
            bot_token: Telegram bot token from BotFather
            chat_ids: List of chat IDs to send messages to
        """
        self.bot_token = bot_token
        self.chat_ids = chat_ids
        self.bot = None
        
        if not self.bot_token:
            raise ValueError("telegram bot token is required")
        
        if not self.chat_ids or len(self.chat_ids) == 0:
            raise ValueError("at least one chat_id is required")
    
    async def initialize(self):
        """Initialize the bot."""
        self.bot = Bot(token=self.bot_token)
        
        # verify bot token
        try:
            bot_info = await self.bot.get_me()
            logger.info(f"telegram bot initialized: @{bot_info.username}")
        except TelegramError as e:
            logger.error(f"failed to initialize telegram bot: {e}")
            raise
    
    async def send_message(
        self,
        message: str,
        parse_mode: str = 'Markdown',
        disable_notification: bool = False
    ) -> Dict[str, Any]:
        """
        Send message to all configured chat IDs.
        
        Args:
            message: Message text
            parse_mode: Message parse mode (Markdown, HTML, or None)
            disable_notification: Whether to send silently
            
        Returns:
            Dictionary with send results
        """
        if not self.bot:
            await self.initialize()
        
        results = {
            'success': [],
            'failed': []
        }
        
        for chat_id in self.chat_ids:
            try:
                await self.bot.send_message(
                    chat_id=chat_id,
                    text=message,
                    parse_mode=parse_mode,
                    disable_notification=disable_notification
                )
                results['success'].append(chat_id)
                logger.info(f"message sent to {chat_id}")
                
            except TelegramError as e:
                logger.error(f"failed to send message to {chat_id}: {e}")
                results['failed'].append({
                    'chat_id': chat_id,
                    'error': str(e)
                })
        
        return results
    
    async def send_alert(self, alert: 'Alert', use_emoji: bool = True) -> Dict[str, Any]:
        """
        Send weather alert.
        
        Args:
            alert: Alert object from AlertManager
            use_emoji: Whether to use emoji in message
            
        Returns:
            Dictionary with send results
        """
        message = alert.format_telegram_message(use_emoji=use_emoji)
        
        # use notification based on severity
        disable_notification = alert.severity in ['low', 'moderate']
        
        return await self.send_message(
            message=message,
            parse_mode='Markdown',
            disable_notification=disable_notification
        )
    
    async def send_alerts(
        self,
        alerts: List['Alert'],
        use_emoji: bool = True
    ) -> Dict[str, Any]:
        """
        Send multiple alerts.
        
        Args:
            alerts: List of Alert objects
            use_emoji: Whether to use emoji in messages
            
        Returns:
            Dictionary with send results
        """
        if not alerts:
            logger.info("no alerts to send")
            return {'success': [], 'failed': []}
        
        logger.info(f"sending {len(alerts)} alert(s)")
        
        all_results = {
            'success': [],
            'failed': []
        }
        
        for alert in alerts:
            results = await self.send_alert(alert, use_emoji=use_emoji)
            all_results['success'].extend(results['success'])
            all_results['failed'].extend(results['failed'])
            
            # small delay between messages
            await asyncio.sleep(0.5)
        
        return all_results
    
    async def close(self):
        """Close bot connection."""
        if self.bot:
            # in v20+, we don't need to explicitly close
            pass


class TelegramBotApp:
    """Interactive Telegram bot with commands."""
    
    def __init__(
        self,
        bot_token: str,
        weather_monitor: Optional[Any] = None,
        alert_manager: Optional[Any] = None,
        config_loader: Optional[Any] = None
    ):
        """
        Initialize bot application.
        
        Args:
            bot_token: Telegram bot token
            weather_monitor: WeatherMonitor instance (optional)
            alert_manager: AlertManager instance (optional)
            config_loader: ConfigLoader instance (optional)
        """
        self.bot_token = bot_token
        self.weather_monitor = weather_monitor
        self.alert_manager = alert_manager
        self.config_loader = config_loader
        self.application = None
    
    def create_application(self) -> Application:
        """Create and configure bot application."""
        self.application = Application.builder().token(self.bot_token).build()
        
        # add command handlers
        self.application.add_handler(CommandHandler("start", self.start_command))
        self.application.add_handler(CommandHandler("help", self.help_command))
        self.application.add_handler(CommandHandler("subscribe", self.subscribe_command))
        self.application.add_handler(CommandHandler("unsubscribe", self.unsubscribe_command))
        self.application.add_handler(CommandHandler("check", self.check_command))
        self.application.add_handler(CommandHandler("status", self.status_command))
        
        return self.application
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command."""
        from subscribers import is_subscribed
        
        chat_id = str(update.effective_chat.id)
        subscribed = is_subscribed(chat_id)
        
        message = (
            "🌤️ *weather alert bot*\n\n"
            "i monitor weather conditions and send daily weather summaries and alerts.\n\n"
            "*available commands:*\n"
            "  /subscribe - receive daily weather updates\n"
            "  /unsubscribe - stop receiving updates\n"
            "  /check - manually check weather now\n"
            "  /status - show current configuration\n"
            "  /help - show this help message\n\n"
        )
        
        if subscribed:
            message += "✅ you are subscribed to weather alerts"
        else:
            message += "send /subscribe to receive daily weather updates"
        
        await update.message.reply_text(message, parse_mode='Markdown')
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /help command."""
        await self.start_command(update, context)
    
    async def subscribe_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /subscribe command."""
        from subscribers import add_subscriber, get_subscribers
        
        chat_id = str(update.effective_chat.id)
        
        if add_subscriber(chat_id):
            message = (
                "✅ *subscribed!*\n\n"
                "you will now receive daily weather updates.\n\n"
                "use /unsubscribe to stop receiving updates."
            )
            await update.message.reply_text(message, parse_mode='Markdown')
            
            # log subscription
            import logging
            logger = logging.getLogger(__name__)
            logger.info(f"new subscriber: {chat_id} (total: {len(get_subscribers())})")
        else:
            message = "ℹ️ you are already subscribed!"
            await update.message.reply_text(message)
    
    async def unsubscribe_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /unsubscribe command."""
        from subscribers import remove_subscriber
        
        chat_id = str(update.effective_chat.id)
        
        if remove_subscriber(chat_id):
            message = (
                "👋 *unsubscribed*\n\n"
                "you will no longer receive weather updates.\n\n"
                "send /subscribe anytime to resubscribe."
            )
            await update.message.reply_text(message, parse_mode='Markdown')
            
            # log unsubscription
            import logging
            logger = logging.getLogger(__name__)
            logger.info(f"unsubscribed: {chat_id}")
        else:
            message = "ℹ️ you are not currently subscribed."
            await update.message.reply_text(message)
    
    async def check_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /check command to manually trigger weather check."""
        await update.message.reply_text("⏳ checking weather conditions...")
        
        try:
            if not self.weather_monitor or not self.alert_manager or not self.config_loader:
                await update.message.reply_text(
                    "❌ bot not fully configured. weather monitoring components not available."
                )
                return
            
            # fetch forecasts
            locations = self.config_loader.get_locations()
            forecasts = self.weather_monitor.get_forecasts_for_locations(locations)
            
            # check alerts
            alerts = self.alert_manager.check_all_locations(forecasts)
            
            if alerts:
                await update.message.reply_text(
                    f"⚠️ found {len(alerts)} alert(s). sending details..."
                )
                
                # send each alert
                for alert in alerts:
                    message = alert.format_telegram_message(use_emoji=True)
                    await update.message.reply_text(message, parse_mode='Markdown')
                    await asyncio.sleep(0.5)
            else:
                await update.message.reply_text(
                    "✅ no weather alerts at this time. all conditions within normal ranges."
                )
        
        except Exception as e:
            logger.error(f"error in check command: {e}")
            await update.message.reply_text(
                f"❌ error checking weather: {str(e)}"
            )
    
    async def status_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /status command to show configuration."""
        try:
            if not self.config_loader:
                await update.message.reply_text(
                    "❌ configuration not available."
                )
                return
            
            locations = self.config_loader.get_locations()
            alerts_config = self.config_loader.get_alerts()
            
            # build status message
            lines = ["📊 *current configuration*\n"]
            
            # locations
            lines.append(f"*locations:* {len(locations)}")
            for loc in locations:
                loc_str = loc.get('city', f"({loc.get('lat')}, {loc.get('lon')})")
                lines.append(f"  • {loc['name']}: {loc_str}")
            
            lines.append("")
            
            # enabled alerts
            enabled_alerts = [
                alert_type for alert_type, config in alerts_config.items()
                if isinstance(config, dict) and config.get('enabled', False)
            ]
            
            lines.append(f"*enabled alerts:* {len(enabled_alerts)}")
            for alert_type in enabled_alerts:
                lines.append(f"  • {alert_type}")
            
            message = "\n".join(lines)
            await update.message.reply_text(message, parse_mode='Markdown')
        
        except Exception as e:
            logger.error(f"error in status command: {e}")
            await update.message.reply_text(
                f"❌ error getting status: {str(e)}"
            )
    
    async def run(self):
        """Run bot application."""
        if not self.application:
            self.create_application()
        
        logger.info("starting telegram bot application...")
        await self.application.run_polling()
    
    async def stop(self):
        """Stop bot application."""
        if self.application:
            await self.application.stop()

