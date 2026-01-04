"""
Auto-subscribe module - processes pending Telegram messages and adds new users.
Works even when bot hasn't been running (messages are stored on Telegram servers).
"""

import asyncio
import logging
from telegram import Bot
from subscribers import add_subscriber, get_subscribers


logger = logging.getLogger(__name__)


async def process_pending_messages(bot_token: str) -> int:
    """
    Process all pending messages and auto-subscribe new users.
    
    Args:
        bot_token: Telegram bot token
        
    Returns:
        Number of new subscribers added
    """
    bot = Bot(token=bot_token)
    new_subscribers = 0
    
    try:
        # get all pending updates (messages sent while bot was offline)
        updates = await bot.get_updates(limit=100, timeout=10)
        
        if not updates:
            logger.info("no pending messages")
            return 0
        
        logger.info(f"processing {len(updates)} pending message(s)")
        
        # extract unique chat IDs from all messages
        chat_ids = set()
        for update in updates:
            if update.message:
                chat_id = str(update.message.chat.id)
                chat_ids.add(chat_id)
        
        # add each chat ID as subscriber
        for chat_id in chat_ids:
            if add_subscriber(chat_id):
                logger.info(f"auto-subscribed new user: {chat_id}")
                new_subscribers += 1
            else:
                logger.debug(f"user already subscribed: {chat_id}")
        
        # mark all messages as processed by getting updates with offset
        if updates:
            last_update_id = updates[-1].update_id
            await bot.get_updates(offset=last_update_id + 1, limit=1)
            logger.debug(f"marked messages as read (offset: {last_update_id + 1})")
        
        if new_subscribers > 0:
            total = len(get_subscribers())
            logger.info(f"added {new_subscribers} new subscriber(s), total: {total}")
        
        return new_subscribers
        
    except Exception as e:
        logger.error(f"error processing pending messages: {e}", exc_info=True)
        return 0

