# telegram bot setup guide

this guide walks you through creating a telegram bot from scratch and configuring it for the weather alert system.

## table of contents

1. [creating your bot with botfather](#creating-your-bot-with-botfather)
2. [getting your chat id](#getting-your-chat-id)
3. [configuring environment variables](#configuring-environment-variables)
4. [testing your bot](#testing-your-bot)
5. [bot commands reference](#bot-commands-reference)
6. [troubleshooting](#troubleshooting)
7. [reusable boilerplate](#reusable-boilerplate)

---

## creating your bot with botfather

botfather is telegram's official bot for creating and managing bots.

### step 1: find botfather

1. open telegram on your phone or desktop
2. search for `@BotFather` in the search bar
3. start a chat with botfather by clicking **start**

### step 2: create new bot

1. send the command `/newbot` to botfather
2. botfather will ask for a name for your bot
   - **name**: this is the display name (e.g., "weather alert bot")
   - this can be anything and can contain spaces
3. botfather will ask for a username
   - **username**: must end in "bot" (e.g., "my_weather_alert_bot")
   - must be unique across all telegram bots
   - cannot contain spaces
   - if your username is taken, try adding numbers or underscores

### step 3: save your bot token

after creating the bot, botfather will give you a **bot token**. it looks like this:

```
123456789:ABCdefGHIjklMNOpqrsTUVwxyz-1234567890
```

**⚠️ important:** 
- keep this token **secret**
- anyone with this token can control your bot
- never commit it to git or share it publicly

### step 4: optional bot configuration

you can customize your bot with these botfather commands:

- `/setdescription` - set bot description (shown in chat)
- `/setabouttext` - set about text (shown in bot profile)
- `/setuserpic` - set bot profile picture
- `/setcommands` - set command menu

example commands to set:

```
start - start the bot
help - show help message
check - manually check weather
status - show current configuration
```

---

## getting your chat id

your chat id is needed so the bot knows where to send messages.

### method 1: using userinfobot (easiest)

1. search for `@userinfobot` in telegram
2. start a chat and click **start**
3. the bot will immediately show your chat id
4. copy the number (e.g., `123456789`)

### method 2: using your bot

1. start a chat with your newly created bot
2. send any message (e.g., `/start`)
3. go to this url in your browser (replace `YOUR_BOT_TOKEN`):
   ```
   https://api.telegram.org/botYOUR_BOT_TOKEN/getUpdates
   ```
4. look for `"chat":{"id":123456789}` in the json response
5. that number is your chat id

### for group chats

to send alerts to a group:

1. add your bot to the group
2. send a message in the group
3. use method 2 above to get the group chat id
4. group chat ids are usually negative numbers (e.g., `-123456789`)

---

## configuring environment variables

### step 1: create .env file

in your project directory, copy the example file:

```bash
cp env.example .env
```

### step 2: edit .env file

open `.env` in a text editor and add your tokens:

```bash
# openweathermap api key
OPENWEATHER_API_KEY=your_openweather_api_key_here

# telegram bot token from @botfather
TELEGRAM_BOT_TOKEN=123456789:ABCdefGHIjklMNOpqrsTUVwxyz-1234567890

# your telegram chat id from @userinfobot
TELEGRAM_CHAT_ID=123456789
```

### for multiple chat ids

if you want to send alerts to multiple people/groups, use comma-separated values:

```bash
TELEGRAM_CHAT_ID=123456789,987654321,-111222333
```

then update `config.yaml`:

```yaml
telegram:
  bot_token: "${TELEGRAM_BOT_TOKEN}"
  chat_ids:
    - "123456789"
    - "987654321"
    - "-111222333"
```

---

## testing your bot

### quick test with python

create a test file `test_bot.py`:

```python
import asyncio
from telegram import Bot

async def test_bot():
    bot_token = "YOUR_BOT_TOKEN"
    chat_id = "YOUR_CHAT_ID"
    
    bot = Bot(token=bot_token)
    
    # test connection
    me = await bot.get_me()
    print(f"bot username: @{me.username}")
    
    # send test message
    await bot.send_message(
        chat_id=chat_id,
        text="🎉 bot is working!"
    )
    print("message sent successfully!")

asyncio.run(test_bot())
```

run it:

```bash
python test_bot.py
```

if you receive the message, your bot is configured correctly!

### test with main application

run a quick check:

```bash
python main.py --check-now
```

---

## bot commands reference

when running the bot interactively, users can use these commands:

### `/start`
- starts the bot and shows welcome message
- displays available commands
- shows your chat id

### `/help`
- shows help message with all commands

### `/check`
- manually triggers weather check
- sends alerts if conditions are met
- useful for testing

### `/status`
- shows current configuration
- lists monitored locations
- lists enabled alert types

---

## troubleshooting

### bot not responding

**problem:** bot doesn't respond to commands

**solutions:**
1. verify bot token is correct in `.env` file
2. make sure you clicked "start" in the bot chat
3. check bot hasn't been deleted in botfather
4. verify bot application is running

### messages not received

**problem:** bot sends messages but you don't receive them

**solutions:**
1. verify chat id is correct
2. check you haven't blocked the bot
3. for groups: ensure bot is still a member
4. check telegram notification settings

### "unauthorized" error

**problem:** `telegram.error.Unauthorized: Forbidden: bot was blocked by the user`

**solutions:**
1. unblock the bot in telegram
2. send `/start` to the bot again
3. verify correct chat id

### "bad request" error

**problem:** `telegram.error.BadRequest: Chat not found`

**solutions:**
1. verify chat id is correct (check for typos)
2. ensure bot has been started in that chat
3. for groups: make sure bot is added to the group

### rate limiting

**problem:** bot stops sending messages after many alerts

**solutions:**
1. telegram limits: 30 messages/second per chat
2. add delays between messages (already implemented)
3. batch multiple alerts into one message

---

## reusable boilerplate

use this boilerplate for creating any telegram bot quickly.

### minimal bot example

```python
import asyncio
from telegram import Update, Bot
from telegram.ext import Application, CommandHandler, ContextTypes

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """handle /start command"""
    await update.message.reply_text("hello! i'm your bot.")

async def main():
    # create bot application
    app = Application.builder().token("YOUR_BOT_TOKEN").build()
    
    # add command handlers
    app.add_handler(CommandHandler("start", start))
    
    # run bot
    await app.run_polling()

if __name__ == "__main__":
    asyncio.run(main())
```

### notification bot example

```python
import asyncio
from telegram import Bot

async def send_notification(bot_token: str, chat_id: str, message: str):
    """send a notification via telegram"""
    bot = Bot(token=bot_token)
    
    try:
        await bot.send_message(
            chat_id=chat_id,
            text=message,
            parse_mode='Markdown'
        )
        print("notification sent!")
    except Exception as e:
        print(f"error: {e}")

# usage
bot_token = "YOUR_BOT_TOKEN"
chat_id = "YOUR_CHAT_ID"
message = "*hello!* this is a _formatted_ message."

asyncio.run(send_notification(bot_token, chat_id, message))
```

### bot with multiple commands

```python
import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

class MyBot:
    def __init__(self, token: str):
        self.token = token
        self.app = None
    
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text(
            "welcome! use /help to see commands."
        )
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        help_text = """
available commands:
/start - start the bot
/help - show this message
/info - get info
"""
        await update.message.reply_text(help_text)
    
    async def info(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        chat_id = update.effective_chat.id
        await update.message.reply_text(f"your chat id: {chat_id}")
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """handle non-command messages"""
        text = update.message.text
        await update.message.reply_text(f"you said: {text}")
    
    def setup(self):
        """setup bot handlers"""
        self.app = Application.builder().token(self.token).build()
        
        # add handlers
        self.app.add_handler(CommandHandler("start", self.start))
        self.app.add_handler(CommandHandler("help", self.help_command))
        self.app.add_handler(CommandHandler("info", self.info))
        self.app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))
    
    async def run(self):
        """run the bot"""
        self.setup()
        await self.app.run_polling()

# usage
async def main():
    bot = MyBot("YOUR_BOT_TOKEN")
    await bot.run()

if __name__ == "__main__":
    asyncio.run(main())
```

---

## additional resources

- [official telegram bot api documentation](https://core.telegram.org/bots/api)
- [python-telegram-bot library docs](https://docs.python-telegram-bot.org/)
- [python-telegram-bot examples](https://docs.python-telegram-bot.org/en/stable/examples.html)
- [botfather commands reference](https://core.telegram.org/bots#6-botfather)

---

## security best practices

1. **never commit tokens to git**
   - use `.env` files
   - add `.env` to `.gitignore`
   - use environment variables in production

2. **rotate tokens if compromised**
   - use `/revoke` in botfather
   - generate new token with `/newbot`
   - update all configurations

3. **validate user permissions**
   - check user ids before processing commands
   - implement admin-only commands
   - whitelist allowed chat ids

4. **rate limiting**
   - implement cooldowns for commands
   - prevent spam/abuse
   - telegram has built-in limits

5. **error handling**
   - catch and log all exceptions
   - don't expose sensitive info in errors
   - provide user-friendly error messages

---

## quick reference card

| action | command/method |
|--------|----------------|
| create bot | talk to @botfather, use `/newbot` |
| get chat id | talk to @userinfobot |
| send message | `bot.send_message(chat_id, text)` |
| markdown formatting | `parse_mode='Markdown'` |
| html formatting | `parse_mode='HTML'` |
| silent message | `disable_notification=True` |
| command handler | `CommandHandler("name", function)` |
| message handler | `MessageHandler(filters.TEXT, function)` |
| run bot | `app.run_polling()` |

---

## formatting cheat sheet

### markdown (recommended)

```
*bold*
_italic_
[link](http://example.com)
`code`
```pre-formatted code block```
```

### html

```html
<b>bold</b>
<i>italic</i>
<a href="http://example.com">link</a>
<code>code</code>
<pre>pre-formatted</pre>
```

### emoji

use unicode emoji directly:
- ⚠️ warning
- ✅ success
- ❌ error
- 📍 location
- 🌡️ temperature
- 💨 wind
- 🌧️ rain
- ⛈️ storm

---

**happy bot building! 🤖**

