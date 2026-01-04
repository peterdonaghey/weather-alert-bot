"""
Telegram bot for sending weather alerts.
Simplified version - only sends messages, no interactive commands.
"""

import asyncio
from typing import List, Dict, Any
from telegram import Bot
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


