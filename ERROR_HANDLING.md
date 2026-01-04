# Weather Alert Bot - Error Handling Guide

This document describes error handling strategies implemented throughout the weather alert bot.

## Error Handling Philosophy

The bot follows these principles:

1. **Fail gracefully** - Continue operating when possible, skip problematic data
2. **Log comprehensively** - All errors are logged with context
3. **User-friendly messages** - Clear error messages in Telegram notifications
4. **No silent failures** - All errors are logged and visible
5. **Recoverable errors** - Retry transient failures, skip unrecoverable ones

## Error Categories

### 1. Configuration Errors

**Module:** `config_loader.py`

**Errors:**
- Missing or invalid configuration file
- Missing required environment variables
- Invalid location coordinates
- Missing required configuration sections

**Handling:**
- Raise `ConfigurationError` with clear message
- Fail fast - don't start bot with invalid config
- Log detailed error information

**Example:**
```python
try:
    config_loader = ConfigLoader('config.yaml')
    config = config_loader.load()
except ConfigurationError as e:
    logger.error(f"configuration error: {e}")
    sys.exit(1)
```

### 2. Weather API Errors

**Module:** `weather_monitor.py`

**Errors:**
- API authentication failures (invalid key)
- Network timeouts
- Rate limiting
- Invalid location (city not found)
- API service unavailable

**Handling:**
- Raise `WeatherAPIError` with context
- Continue with other locations if one fails
- Log error details
- Implement timeouts to prevent hanging

**Example:**
```python
try:
    forecast = weather_monitor.get_forecast(location)
except WeatherAPIError as e:
    logger.error(f"failed to get forecast for {location['name']}: {e}")
    # Continue with other locations
    continue
```

### 3. Alert Processing Errors

**Module:** `alert_manager.py`

**Errors:**
- Missing forecast data
- Invalid alert configuration
- Data format mismatches

**Handling:**
- Skip problematic alerts
- Log warnings for configuration issues
- Return empty list if no valid alerts

**Example:**
```python
if not daily_summary:
    logger.warning(f"no forecast data for {location_name}")
    return []
```

### 4. Telegram API Errors

**Module:** `telegram_bot.py`

**Errors:**
- Invalid bot token
- Chat not found
- Bot blocked by user
- Network failures
- Rate limiting

**Handling:**
- Catch `TelegramError` exceptions
- Track success/failure per chat
- Continue sending to other chats if one fails
- Log detailed error information

**Example:**
```python
try:
    await bot.send_message(chat_id=chat_id, text=message)
    results['success'].append(chat_id)
except TelegramError as e:
    logger.error(f"failed to send to {chat_id}: {e}")
    results['failed'].append({'chat_id': chat_id, 'error': str(e)})
```

### 5. Scheduling Errors

**Module:** `main.py`

**Errors:**
- Invalid schedule configuration
- Timezone errors
- Scheduler interruptions

**Handling:**
- Validate schedule config on startup
- Catch KeyboardInterrupt for clean shutdown
- Log all scheduled runs

## Error Handling Patterns

### Pattern 1: Continue on Error

Used when processing multiple items (locations, alerts, chats):

```python
for location in locations:
    try:
        forecast = get_forecast(location)
        process_forecast(forecast)
    except Exception as e:
        logger.error(f"error processing {location['name']}: {e}")
        # Continue with next location
        continue
```

### Pattern 2: Fail Fast

Used for critical configuration or initialization errors:

```python
try:
    api_key = config_loader.get_api_key('openweathermap')
except ConfigurationError as e:
    logger.error(f"critical error: {e}")
    sys.exit(1)
```

### Pattern 3: Retry with Timeout

Used for network operations:

```python
response = requests.get(url, timeout=10)
response.raise_for_status()
```

### Pattern 4: Result Tracking

Used when sending to multiple recipients:

```python
results = {
    'success': [],
    'failed': []
}

for chat_id in chat_ids:
    try:
        await send_message(chat_id)
        results['success'].append(chat_id)
    except Exception as e:
        results['failed'].append({'chat_id': chat_id, 'error': str(e)})

return results
```

## Logging Best Practices

### Log Levels

- **DEBUG**: Detailed diagnostic information
  - API request/response details
  - Configuration parsing steps
  - Alert evaluation logic

- **INFO**: General informational messages
  - Bot starting/stopping
  - Forecasts fetched
  - Alerts generated and sent
  - Successful operations

- **WARNING**: Unexpected but handled situations
  - Missing optional configuration
  - Skipped items due to errors
  - Degraded functionality

- **ERROR**: Error conditions that prevent specific operations
  - Failed API requests
  - Failed message delivery
  - Invalid data

- **CRITICAL**: Severe errors that prevent bot operation
  - Invalid configuration
  - Missing credentials
  - Unrecoverable failures

### Log Message Format

Good log messages include:

1. **Context**: What operation was being performed
2. **Data**: Relevant identifiers (location name, chat ID, etc.)
3. **Error**: What went wrong
4. **Action**: What happens next

Example:
```python
logger.error(
    f"failed to send alert to chat {chat_id} "
    f"for location {location_name}: {error_message}. "
    f"continuing with other chats"
)
```

## Testing Error Handling

### Test Invalid Configuration

```bash
# Test missing config file
python main.py --config nonexistent.yaml --check-now

# Test invalid API key
# Edit .env with invalid key
python main.py --check-now
```

### Test Invalid Location

```yaml
# In config.yaml, add invalid location
locations:
  - name: "Invalid"
    city: "NonexistentCity12345"
```

### Test Telegram Errors

```bash
# Test invalid bot token
# Edit .env with invalid token
python main.py --check-now

# Test invalid chat ID
# Edit config.yaml with invalid chat_id
python main.py --check-now
```

### Test Network Failures

```bash
# Disconnect network and run
python main.py --check-now
```

## Monitoring and Debugging

### View Logs

```bash
# Real-time log viewing
tail -f weather_alert.log

# Search for errors
grep ERROR weather_alert.log

# View recent errors
tail -n 100 weather_alert.log | grep -E "(ERROR|CRITICAL)"
```

### Debug Mode

Run with verbose logging:

```bash
python main.py --check-now --verbose
```

Or set log level:

```bash
python main.py --check-now --log-level DEBUG
```

### Common Issues and Solutions

#### Issue: "Configuration file not found"
**Solution:** Ensure config.yaml exists in current directory or specify path with --config

#### Issue: "Environment variable 'OPENWEATHER_API_KEY' not found"
**Solution:** Create .env file with required variables (see env.example)

#### Issue: "City not found"
**Solution:** Check location spelling in config.yaml, try using coordinates instead

#### Issue: "Bot was blocked by the user"
**Solution:** Unblock bot in Telegram, send /start command

#### Issue: "Chat not found"
**Solution:** Verify chat ID is correct, ensure you've messaged the bot first

## Error Recovery Strategies

### Automatic Recovery

The bot implements these automatic recovery mechanisms:

1. **Skip failed locations** - Continue with other locations if one fails
2. **Partial message delivery** - Send to available chats even if some fail
3. **Graceful degradation** - Continue with available features if some fail

### Manual Recovery

If bot stops working:

1. **Check logs** - Review error messages
2. **Verify configuration** - Ensure config.yaml and .env are correct
3. **Test API keys** - Verify OpenWeatherMap and Telegram credentials
4. **Test network** - Ensure internet connectivity
5. **Restart bot** - Often resolves transient issues

## Future Improvements

Potential enhancements to error handling:

1. **Retry logic** - Automatic retry for transient failures
2. **Circuit breaker** - Temporarily disable failing services
3. **Health checks** - Periodic validation of configuration and credentials
4. **Alert on errors** - Send Telegram notification when critical errors occur
5. **Error metrics** - Track error rates and types for monitoring

