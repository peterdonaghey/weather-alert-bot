# Agent Guidelines for weather-alert-bot

This document provides guidance for agentic coding tools operating on this repository.

## Project Overview

Weather Alert Bot is a Python-based Telegram bot that monitors weather conditions and sends alerts based on configured thresholds. It runs automatically via GitHub Actions with no server required.

**Stack:** Python 3.11+, OpenWeatherMap API, Telegram Bot API, YAML configuration, GitHub Actions

## Build, Lint, and Test Commands

### Running the Application

```bash
# Run the weather check with default logging
python main.py

# Run with verbose logging
python main.py --verbose

# Run with specific log level
python main.py --log-level DEBUG
```

### Testing

No automated test framework is currently configured. **To add tests:**
- Use `pytest` for test framework
- Create `tests/` directory at repository root
- Run tests: `pytest tests/` or `pytest tests/test_module.py`
- Run single test: `pytest tests/test_file.py::test_function_name`

### Dependencies

```bash
# Install dependencies
pip install -r requirements.txt

# Create a virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows
pip install -r requirements.txt
```

### Linting and Code Quality

No automated linting is currently configured. **Recommended setup:**

```bash
# Install linting tools
pip install ruff black pylint

# Format code
black *.py

# Check code style
ruff check .
```

## Code Style Guidelines

### Imports

- Use absolute imports: `from weather_monitor import WeatherMonitor`
- Order: standard library → third-party → local imports
- One import per line (from X import Y, Z is acceptable for multiple items)
- Avoid circular imports; use dependency injection when needed

**Example:**
```python
import asyncio
import logging
from typing import Dict, List, Any, Optional

from telegram import Bot
from telegram.error import TelegramError

from config_loader import ConfigLoader
from weather_monitor import WeatherMonitor
```

### Formatting

- Line length: 88 characters (Black default)
- Use 4 spaces for indentation (never tabs)
- One blank line between functions, two between classes
- Use trailing commas in multiline structures for git diffs

### Type Hints

- Always use type hints for function arguments and returns
- Required for all public methods
- Use `typing` module types: `Dict[str, Any]`, `List[int]`, `Optional[str]`
- Use `|` syntax only in comments; use `Union` or `Optional` for code compatibility with Python 3.11

**Example:**
```python
def process_alerts(alerts: List[Dict[str, Any]]) -> Optional[str]:
    """Process weather alerts and return summary."""
    pass
```

### Naming Conventions

- **Functions/methods:** `snake_case` (e.g., `get_forecast`, `process_alerts`)
- **Classes:** `PascalCase` (e.g., `WeatherMonitor`, `AlertManager`)
- **Constants:** `UPPER_SNAKE_CASE` (e.g., `DEFAULT_LOG_LEVEL`, `API_BASE_URL`)
- **Private members:** Prefix with `_` (e.g., `_get_wind_descriptor`, `_parse_config`)
- **Boolean/flag variables:** Prefix with `is_` or `has_` (e.g., `is_valid`, `has_alerts`)

### Documentation

- Use docstrings for all public functions and classes
- Format: Google style (3 quotes on separate lines)
- Include Args, Returns, and Raises sections

**Example:**
```python
def check_alert_conditions(weather_data: Dict, thresholds: Dict) -> List[Alert]:
    """
    Check weather data against configured thresholds.
    
    Args:
        weather_data: Weather forecast data
        thresholds: Alert threshold configuration
        
    Returns:
        List of triggered alerts
        
    Raises:
        ValueError: If weather data is invalid
    """
```

### Error Handling

- Define custom exceptions for domain-specific errors
- Custom exceptions should inherit from built-in exceptions
- Use specific exception types, not bare `except Exception:`
- Always log errors before re-raising

**Patterns:**
```python
class ConfigurationError(Exception):
    """Raised when configuration is invalid."""
    pass

class WeatherAPIError(Exception):
    """Raised when weather API request fails."""
    pass

try:
    data = fetch_weather()
except WeatherAPIError as e:
    logger.error(f"Failed to fetch weather: {e}")
    raise
```

### Logging

- Use module-level logger: `logger = logging.getLogger(__name__)`
- Log at appropriate levels: DEBUG, INFO, WARNING, ERROR
- Include context in log messages: `logger.error(f"Failed for {location}: {error}")`
- Never print directly; use logger instead

### Configuration

- Use `config.yaml` for user-facing configuration
- Use environment variables (`.env`) for secrets
- Use `ConfigLoader` class for loading and validation
- Validate configuration at startup; raise `ConfigurationError` if invalid

### Async Code

- Use `asyncio` for concurrent operations
- Main entry point may use `asyncio.run()` for async context
- Async functions should be named with `async_` prefix if needed for clarity
- Use type hints with `Coroutine` or async context managers

### Separation of Concerns

Current module responsibilities (maintain this structure):

- `main.py` - Entry point, orchestration, CLI argument parsing
- `weather_monitor.py` - OpenWeatherMap API integration
- `alert_manager.py` - Alert logic and severity evaluation
- `telegram_bot.py` - Telegram API integration
- `config_loader.py` - Configuration loading and validation
- `subscribers.py` - Subscriber list management
- `auto_subscribe.py` - Auto-subscription from Telegram messages

**Rule:** Each module should have one clear responsibility. New features should either extend existing modules or create new focused modules.

## Common Patterns

### Custom Exceptions
```python
try:
    result = operation()
except SpecificError as e:
    logger.error(f"Operation failed: {e}")
    raise
```

### Configuration Access
```python
config = ConfigLoader().load()
alerts_config = config.get('alerts', {})
```

### Logging with Context
```python
logger.info(f"Processing forecast for {location['name']}")
logger.debug(f"Threshold: {threshold}, Actual: {actual}")
```

## File Organization

All Python modules are in the root directory. Configuration files:
- `config.yaml` - User configuration
- `.env` - Secrets (never commit)
- `requirements.txt` - Dependencies
- `subscribers.json` - Subscriber list (checked in for persistence)

## Pre-commit Checks

Before committing code:
1. Verify all imports are used
2. Check for hardcoded secrets
3. Ensure type hints are present on public functions
4. Test the main workflow: `python main.py`
5. Update `requirements.txt` if dependencies change
