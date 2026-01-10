"""
Configuration loader for weather alert bot.
Loads and validates configuration from YAML file with environment variable substitution.
"""

import os
import re
import yaml
from typing import Dict, List, Any, Optional
from dotenv import load_dotenv


class ConfigurationError(Exception):
    """Raised when configuration is invalid."""
    pass


class ConfigLoader:
    """Loads and validates configuration from YAML file."""
    
    def __init__(self, config_path: str = "config.yaml"):
        """
        Initialize configuration loader.
        
        Args:
            config_path: Path to configuration file
        """
        self.config_path = config_path
        self.config = None
        load_dotenv()
    
    def load(self) -> Dict[str, Any]:
        """
        Load configuration from file.
        
        Returns:
            Dictionary containing configuration
            
        Raises:
            ConfigurationError: If configuration is invalid
        """
        if not os.path.exists(self.config_path):
            raise ConfigurationError(f"configuration file not found: {self.config_path}")
        
        with open(self.config_path, 'r') as f:
            raw_config = yaml.safe_load(f)
        
        if not raw_config:
            raise ConfigurationError("configuration file is empty")
        
        # substitute environment variables
        self.config = self._substitute_env_vars(raw_config)
        
        # validate configuration
        self._validate()
        
        return self.config
    
    def _substitute_env_vars(self, obj: Any) -> Any:
        """
        Recursively substitute environment variables in configuration.
        Supports ${VAR_NAME} syntax.
        
        Args:
            obj: Configuration object (dict, list, str, etc.)
            
        Returns:
            Object with environment variables substituted
        """
        if isinstance(obj, dict):
            return {k: self._substitute_env_vars(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._substitute_env_vars(item) for item in obj]
        elif isinstance(obj, str):
            # find all ${VAR_NAME} patterns
            pattern = re.compile(r'\$\{([^}]+)\}')
            matches = pattern.findall(obj)
            
            result = obj
            for var_name in matches:
                var_value = os.getenv(var_name)
                if var_value is None:
                    raise ConfigurationError(
                        f"environment variable '{var_name}' not found"
                    )
                result = result.replace(f'${{{var_name}}}', var_value)
            
            return result
        else:
            return obj
    
    def _validate(self):
        """
        Validate configuration structure and values.
        
        Raises:
            ConfigurationError: If configuration is invalid
        """
        if not isinstance(self.config, dict):
            raise ConfigurationError("configuration must be a dictionary")
        
        # validate locations
        if 'locations' not in self.config:
            raise ConfigurationError("'locations' section is required")
        
        if not isinstance(self.config['locations'], list):
            raise ConfigurationError("'locations' must be a list")
        
        if len(self.config['locations']) == 0:
            raise ConfigurationError("at least one location must be configured")
        
        for i, location in enumerate(self.config['locations']):
            self._validate_location(location, i)
        
        # validate alerts
        if 'alerts' not in self.config:
            raise ConfigurationError("'alerts' section is required")
        
        if not isinstance(self.config['alerts'], dict):
            raise ConfigurationError("'alerts' must be a dictionary")
        
        # validate telegram settings
        if 'telegram' not in self.config:
            raise ConfigurationError("'telegram' section is required")
        
        telegram_config = self.config['telegram']
        if 'bot_token' not in telegram_config:
            raise ConfigurationError("'telegram.bot_token' is required")
        
        if 'chat_ids' not in telegram_config:
            raise ConfigurationError("'telegram.chat_ids' is required")
        
        if not isinstance(telegram_config['chat_ids'], list):
            raise ConfigurationError("'telegram.chat_ids' must be a list")
        
        if len(telegram_config['chat_ids']) == 0:
            raise ConfigurationError("at least one chat_id must be configured")
    
    def _validate_location(self, location: Dict[str, Any], index: int):
        """
        Validate a location configuration.
        
        Args:
            location: Location configuration dictionary
            index: Location index for error messages
            
        Raises:
            ConfigurationError: If location is invalid
        """
        if not isinstance(location, dict):
            raise ConfigurationError(f"location {index} must be a dictionary")
        
        if 'name' not in location:
            raise ConfigurationError(f"location {index} must have a 'name'")
        
        # location must have either city OR (lat AND lon)
        has_city = 'city' in location
        has_coords = 'lat' in location and 'lon' in location
        
        if not has_city and not has_coords:
            raise ConfigurationError(
                f"location {index} ('{location['name']}') must have either "
                "'city' or both 'lat' and 'lon'"
            )
        
        # validate coordinates if present
        if has_coords:
            try:
                lat = float(location['lat'])
                lon = float(location['lon'])
                
                if not (-90 <= lat <= 90):
                    raise ConfigurationError(
                        f"location {index} ('{location['name']}') has invalid "
                        f"latitude: {lat} (must be between -90 and 90)"
                    )
                
                if not (-180 <= lon <= 180):
                    raise ConfigurationError(
                        f"location {index} ('{location['name']}') has invalid "
                        f"longitude: {lon} (must be between -180 and 180)"
                    )
            except (ValueError, TypeError):
                raise ConfigurationError(
                    f"location {index} ('{location['name']}') has invalid "
                    "lat/lon values (must be numbers)"
                )
    
    def get_locations(self) -> List[Dict[str, Any]]:
        """Get list of configured locations."""
        if self.config is None:
            raise ConfigurationError("configuration not loaded")
        return self.config['locations']
    
    def get_alerts(self) -> Dict[str, Any]:
        """Get alert configuration."""
        if self.config is None:
            raise ConfigurationError("configuration not loaded")
        return self.config['alerts']
    
    def get_telegram_config(self) -> Dict[str, Any]:
        """Get Telegram configuration."""
        if self.config is None:
            raise ConfigurationError("configuration not loaded")
        return self.config['telegram']
    
    def get_schedule_config(self) -> Optional[Dict[str, Any]]:
        """Get schedule configuration if present."""
        if self.config is None:
            raise ConfigurationError("configuration not loaded")
        return self.config.get('schedule')
    
    def get_claude_config(self) -> Optional[Dict[str, Any]]:
        """Get Claude AI configuration if present."""
        if self.config is None:
            raise ConfigurationError("configuration not loaded")
        return self.config.get('claude')
    
    def get_api_key(self, service: str) -> str:
        """
        Get API key for a service.
        
        Args:
            service: Service name (e.g., 'openweathermap')
            
        Returns:
            API key
            
        Raises:
            ConfigurationError: If API key not found
        """
        if self.config is None:
            raise ConfigurationError("configuration not loaded")
        
        # check environment variable first
        env_var_name = f"{service.upper()}_API_KEY"
        api_key = os.getenv(env_var_name)
        
        if api_key:
            return api_key
        
        # check in config file
        if 'api_keys' in self.config and service in self.config['api_keys']:
            return self.config['api_keys'][service]
        
        raise ConfigurationError(
            f"API key for '{service}' not found. "
            f"Set {env_var_name} environment variable or add to config file"
        )

