"""
Weather monitoring module using OpenWeatherMap API.
Fetches weather forecasts for multiple locations and processes forecast data.
"""

import requests
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import logging


logger = logging.getLogger(__name__)


class WeatherAPIError(Exception):
    """Raised when weather API request fails."""
    pass


class WeatherMonitor:
    """Monitors weather conditions using OpenWeatherMap API."""
    
    def __init__(self, api_key: str):
        """
        Initialize weather monitor.
        
        Args:
            api_key: OpenWeatherMap API key
        """
        self.api_key = api_key
        self.base_url = "https://api.openweathermap.org/data/2.5"
        
        if not self.api_key:
            raise WeatherAPIError("openweathermap api key is required")
    
    def get_forecast(self, location: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get weather forecast for a location.
        
        Args:
            location: Location dictionary with 'name' and either 'city' or 'lat'/'lon'
            
        Returns:
            Forecast data dictionary
            
        Raises:
            WeatherAPIError: If API request fails
        """
        try:
            # determine if we're using city or coordinates
            if 'lat' in location and 'lon' in location:
                lat = location['lat']
                lon = location['lon']
                logger.debug(f"fetching forecast for {location['name']} at ({lat}, {lon})")
            elif 'city' in location:
                # first, get coordinates for city
                coords = self._get_coordinates(location['city'])
                lat = coords['lat']
                lon = coords['lon']
                logger.debug(f"fetching forecast for {location['name']} ({location['city']})")
            else:
                raise WeatherAPIError(
                    f"location '{location['name']}' must have either 'city' or 'lat'/'lon'"
                )
            
            # fetch 5-day forecast
            forecast_url = f"{self.base_url}/forecast"
            params = {
                'lat': lat,
                'lon': lon,
                'appid': self.api_key,
                'units': 'metric'  # celsius, m/s
            }
            
            response = requests.get(forecast_url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            # parse and return forecast
            return self._parse_forecast(data, location['name'])
            
        except requests.exceptions.RequestException as e:
            logger.error(f"api request failed for {location['name']}: {e}")
            raise WeatherAPIError(f"failed to fetch forecast: {e}")
        except KeyError as e:
            logger.error(f"unexpected api response format: {e}")
            raise WeatherAPIError(f"unexpected api response format: {e}")
    
    def _get_coordinates(self, city: str) -> Dict[str, float]:
        """
        Get coordinates for a city using geocoding API.
        
        Args:
            city: City name (e.g., "London, UK")
            
        Returns:
            Dictionary with 'lat' and 'lon'
            
        Raises:
            WeatherAPIError: If geocoding fails
        """
        geo_url = "http://api.openweathermap.org/geo/1.0/direct"
        params = {
            'q': city,
            'limit': 1,
            'appid': self.api_key
        }
        
        try:
            response = requests.get(geo_url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if not data or len(data) == 0:
                raise WeatherAPIError(f"city not found: {city}")
            
            return {
                'lat': data[0]['lat'],
                'lon': data[0]['lon']
            }
            
        except requests.exceptions.RequestException as e:
            raise WeatherAPIError(f"geocoding failed: {e}")
    
    def _parse_forecast(self, data: Dict[str, Any], location_name: str) -> Dict[str, Any]:
        """
        Parse OpenWeatherMap forecast response.
        
        Args:
            data: Raw API response
            location_name: Name of the location
            
        Returns:
            Parsed forecast dictionary
        """
        forecasts = []
        
        for item in data['list']:
            forecast_time = datetime.fromtimestamp(item['dt'])
            
            # extract weather data
            forecast_entry = {
                'time': forecast_time,
                'temperature': item['main']['temp'],
                'feels_like': item['main']['feels_like'],
                'temp_min': item['main']['temp_min'],
                'temp_max': item['main']['temp_max'],
                'pressure': item['main']['pressure'],
                'humidity': item['main']['humidity'],
                'weather': item['weather'][0]['main'],
                'weather_description': item['weather'][0]['description'],
                'clouds': item['clouds']['all'],
                'wind_speed': item['wind']['speed'],  # m/s
                'wind_speed_kmh': item['wind']['speed'] * 3.6,  # convert to km/h
                'wind_deg': item['wind'].get('deg', 0),
                'wind_gust': item['wind'].get('gust', 0) * 3.6 if 'gust' in item['wind'] else 0,  # km/h
                'precipitation': 0,
                'precipitation_probability': item.get('pop', 0) * 100  # convert to percentage
            }
            
            # add precipitation data if available
            if 'rain' in item:
                forecast_entry['precipitation'] += item['rain'].get('3h', 0)
            if 'snow' in item:
                forecast_entry['precipitation'] += item['snow'].get('3h', 0)
            
            forecasts.append(forecast_entry)
        
        return {
            'location_name': location_name,
            'city': data['city']['name'],
            'country': data['city']['country'],
            'coordinates': {
                'lat': data['city']['coord']['lat'],
                'lon': data['city']['coord']['lon']
            },
            'forecasts': forecasts,
            'fetched_at': datetime.now()
        }
    
    def get_daily_summary(self, forecast: Dict[str, Any], days_ahead: int = 1) -> Dict[str, Any]:
        """
        Get summary of forecast for a specific day ahead.
        
        Args:
            forecast: Forecast data from get_forecast()
            days_ahead: Number of days ahead (0=today, 1=tomorrow, etc.)
            
        Returns:
            Daily summary with max/min values
        """
        target_date = datetime.now().date() + timedelta(days=days_ahead)
        
        # filter forecasts for target day
        day_forecasts = [
            f for f in forecast['forecasts']
            if f['time'].date() == target_date
        ]
        
        if not day_forecasts:
            return None
        
        # calculate summary statistics
        summary = {
            'date': target_date,
            'location_name': forecast['location_name'],
            'temp_min': min(f['temp_min'] for f in day_forecasts),
            'temp_max': max(f['temp_max'] for f in day_forecasts),
            'temp_avg': sum(f['temperature'] for f in day_forecasts) / len(day_forecasts),
            'wind_speed_max': max(f['wind_speed_kmh'] for f in day_forecasts),
            'wind_gust_max': max(f['wind_gust'] for f in day_forecasts),
            'precipitation_total': sum(f['precipitation'] for f in day_forecasts),
            'precipitation_probability_max': max(f['precipitation_probability'] for f in day_forecasts),
            'weather_conditions': list(set(f['weather'] for f in day_forecasts)),
            'hourly_forecasts': day_forecasts
        }
        
        return summary
    
    def get_forecasts_for_locations(self, locations: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Get forecasts for multiple locations.
        
        Args:
            locations: List of location dictionaries
            
        Returns:
            List of forecast data for each location
        """
        forecasts = []
        
        for location in locations:
            try:
                logger.info(f"fetching forecast for {location['name']}")
                forecast = self.get_forecast(location)
                forecasts.append(forecast)
            except WeatherAPIError as e:
                logger.error(f"failed to get forecast for {location['name']}: {e}")
                # continue with other locations
                continue
        
        return forecasts

