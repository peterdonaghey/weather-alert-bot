"""
Auto-subscribe module - processes pending Telegram messages and handles commands.
Works even when bot hasn't been running (messages are stored on Telegram servers).
"""

import asyncio
import logging
from telegram import Bot
from telegram.error import TelegramError
from subscribers import add_subscriber, remove_subscriber, get_subscribers, is_subscribed


logger = logging.getLogger(__name__)


async def set_bot_commands(bot_token: str):
    """
    Set bot commands to only include subscribe/unsubscribe.
    Removes unused commands like /check, /status, /help.
    """
    try:
        bot = Bot(token=bot_token)
        from telegram import BotCommand
        
        commands = [
            BotCommand("subscribe", "Receive daily weather updates"),
            BotCommand("unsubscribe", "Stop receiving updates"),
        ]
        
        await bot.set_my_commands(commands)
        logger.info("bot commands updated: subscribe, unsubscribe")
    except Exception as e:
        logger.warning(f"failed to update bot commands: {e}")


async def process_pending_messages(bot_token: str) -> int:
    """
    Process all pending messages and handle subscribe/unsubscribe commands.
    
    Args:
        bot_token: Telegram bot token
    
    Returns:
        Number of new subscribers added
    """
    bot = Bot(token=bot_token)
    new_subscribers = 0
    
    try:
        # set bot commands to only include subscribe/unsubscribe
        await set_bot_commands(bot_token)
        
        # delete webhook first to enable getUpdates mode
        await bot.delete_webhook()
        logger.info("webhook deleted to enable getUpdates mode")
        
        # get all pending updates (messages sent while bot was offline)
        updates = await bot.get_updates(limit=100, timeout=10)
        
        if not updates:
            logger.info("no pending messages")
            return 0
        
        logger.info(f"processing {len(updates)} pending message(s)")
        
        # process each update for commands
        for update in updates:
            if not update.message:
                continue
                
            chat_id = str(update.message.chat.id)
            message_text = update.message.text or ""
            
            # handle /subscribe command (including /start and /help)
            if message_text.lower().strip() in ["/subscribe", "/start", "/help", "subscribe", "start", "help"]:
                if is_subscribed(chat_id):
                    try:
                        await bot.send_message(
                            chat_id=chat_id,
                            text="✅ You're already subscribed! You'll receive daily weather updates.",
                            parse_mode="HTML"
                        )
                        logger.info(f"user {chat_id} already subscribed")
                    except TelegramError as e:
                        logger.warning(f"failed to send message to {chat_id}: {e}")
                else:
                    if add_subscriber(chat_id):
                        try:
                            await bot.send_message(
                                chat_id=chat_id,
                                text="✅ Subscribed! You'll receive daily weather updates at 7 AM UTC.",
                                parse_mode="HTML"
                            )
                            logger.info(f"subscribed new user: {chat_id}")
                            new_subscribers += 1
                        except TelegramError as e:
                            logger.warning(f"failed to send message to {chat_id}: {e}")
                            # still count as subscribed even if message failed
                            new_subscribers += 1
            
            # handle /check command (not implemented)
            elif message_text.lower().strip() in ["/check"]:
                try:
                    await bot.send_message(
                        chat_id=chat_id,
                        text="ℹ️ Weather updates are sent automatically at 7 AM UTC daily. Use /subscribe to ensure you receive them.",
                        parse_mode="HTML"
                    )
                except TelegramError as e:
                    logger.warning(f"failed to send message to {chat_id}: {e}")
            
            # handle /status command (not implemented)
            elif message_text.lower().strip() in ["/status"]:
                is_sub = is_subscribed(chat_id)
                status_text = "✅ You're subscribed" if is_sub else "❌ You're not subscribed"
                try:
                    await bot.send_message(
                        chat_id=chat_id,
                        text=f"{status_text}. Use /subscribe to receive updates or /unsubscribe to stop.",
                        parse_mode="HTML"
                    )
                except TelegramError as e:
                    logger.warning(f"failed to send message to {chat_id}: {e}")
            
            # handle /unsubscribe command
            elif message_text.lower().strip() in ["/unsubscribe", "/stop", "unsubscribe", "stop"]:
                if is_subscribed(chat_id):
                    if remove_subscriber(chat_id):
                        try:
                            await bot.send_message(
                                chat_id=chat_id,
                                text="👋 Unsubscribed. You won't receive weather updates anymore. Send /subscribe to re-enable.",
                                parse_mode="HTML"
                            )
                            logger.info(f"unsubscribed user: {chat_id}")
                        except TelegramError as e:
                            logger.warning(f"failed to send message to {chat_id}: {e}")
                else:
                    try:
                        await bot.send_message(
                            chat_id=chat_id,
                            text="ℹ️ You're not currently subscribed. Send /subscribe to start receiving updates.",
                            parse_mode="HTML"
                        )
                        logger.info(f"user {chat_id} tried to unsubscribe but wasn't subscribed")
                    except TelegramError as e:
                        logger.warning(f"failed to send message to {chat_id}: {e}")
            
            # auto-subscribe any other message (backward compatibility)
            elif message_text.strip():
                if not is_subscribed(chat_id):
                    if add_subscriber(chat_id):
                        try:
                            await bot.send_message(
                                chat_id=chat_id,
                                text="✅ You've been subscribed! Send /unsubscribe to stop receiving updates.",
                                parse_mode="HTML"
                            )
                            logger.info(f"auto-subscribed new user from message: {chat_id}")
                            new_subscribers += 1
                        except TelegramError as e:
                            logger.warning(f"failed to send message to {chat_id}: {e}")
                            new_subscribers += 1
        
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

