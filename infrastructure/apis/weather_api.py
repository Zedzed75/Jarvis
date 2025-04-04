"""
Weather API Client implementations for Jarvis

This module provides implementations for weather service APIs,
following the clean architecture patterns.
"""

import logging
import requests
from typing import Dict, Any, Optional
from datetime import datetime, timedelta

logger = logging.getLogger('jarvis.infrastructure.apis.weather')

class OpenWeatherMapClient:
    """
    Client for the OpenWeatherMap API
    """
    
    BASE_URL = "https://api.openweathermap.org/data/2.5"
    
    def __init__(self, api_key: str, units: str = "imperial"):
        """
        Initialize the OpenWeatherMap client
        
        Args:
            api_key: OpenWeatherMap API key
            units: Units system to use (imperial, metric)
        """
        self.api_key = api_key
        self.units = units
        logger.info("OpenWeatherMap client initialized")
    
    def get_current_weather(self, location: str) -> Optional[Dict[str, Any]]:
        """
        Get current weather for a location
        
        Args:
            location: City name or coordinates
            
        Returns:
            Weather data or None if request failed
        """
        try:
            url = f"{self.BASE_URL}/weather"
            params = {
                'q': location,
                'appid': self.api_key,
                'units': self.units
            }
            
            response = requests.get(url, params=params)
            
            if response.status_code == 200:
                data = response.json()
                logger.debug(f"Retrieved current weather for {location}")
                return data
            else:
                logger.error(f"Failed to get weather data: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"Error getting weather data: {e}")
            return None
    
    def get_forecast(self, location: str, days: int = 5) -> Optional[Dict[str, Any]]:
        """
        Get weather forecast for a location
        
        Args:
            location: City name or coordinates
            days: Number of days for forecast (max 5)
            
        Returns:
            Forecast data or None if request failed
        """
        try:
            url = f"{self.BASE_URL}/forecast"
            params = {
                'q': location,
                'appid': self.api_key,
                'units': self.units
            }
            
            response = requests.get(url, params=params)
            
            if response.status_code == 200:
                data = response.json()
                
                # Process the data to get a clean daily forecast
                # OpenWeatherMap free API returns 3-hour forecasts
                if days <= 5:
                    processed_data = self._process_forecast(data, days)
                    logger.debug(f"Retrieved {days}-day forecast for {location}")
                    return processed_data
                else:
                    logger.warning(f"Requested {days} days forecast but OpenWeatherMap free tier supports max 5 days")
                    processed_data = self._process_forecast(data, 5)
                    return processed_data
            else:
                logger.error(f"Failed to get forecast data: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"Error getting forecast data: {e}")
            return None
    
    def _process_forecast(self, data: Dict[str, Any], days: int) -> Dict[str, Any]:
        """
        Process the raw forecast data to get daily forecasts
        
        Args:
            data: Raw forecast data from API
            days: Number of days to include
            
        Returns:
            Processed forecast data
        """
        if 'list' not in data:
            return data
            
        forecasts = data['list']
        today = datetime.now().date()
        
        # Group forecasts by day
        daily_forecasts = {}
        
        for forecast in forecasts:
            # Convert timestamp to date
            timestamp = forecast.get('dt')
            if not timestamp:
                continue
                
            date = datetime.fromtimestamp(timestamp).date()
            
            # Skip if beyond requested days
            if (date - today).days >= days:
                continue
                
            # Use noon forecast for each day if available
            time = datetime.fromtimestamp(timestamp).time()
            
            if date not in daily_forecasts:
                daily_forecasts[date] = forecast
            elif abs(time.hour - 12) < abs(datetime.fromtimestamp(daily_forecasts[date]['dt']).time().hour - 12):
                # This forecast is closer to noon
                daily_forecasts[date] = forecast
        
        # Convert back to list format similar to original data
        result = {
            'city': data.get('city', {}),
            'daily': list(daily_forecasts.values())
        }
        
        return result


class WeatherAPIClient:
    """
    Client for WeatherAPI.com
    """
    
    BASE_URL = "https://api.weatherapi.com/v1"
    
    def __init__(self, api_key: str, units: str = "imperial"):
        """
        Initialize the WeatherAPI client
        
        Args:
            api_key: WeatherAPI.com API key
            units: Units system to use (imperial, metric)
        """
        self.api_key = api_key
        self.units = units
        logger.info("WeatherAPI client initialized")
    
    def get_current_weather(self, location: str) -> Optional[Dict[str, Any]]:
        """
        Get current weather for a location
        
        Args:
            location: City name or coordinates
            
        Returns:
            Weather data or None if request failed
        """
        try:
            url = f"{self.BASE_URL}/current.json"
            params = {
                'key': self.api_key,
                'q': location,
                'aqi': 'no'
            }
            
            response = requests.get(url, params=params)
            
            if response.status_code == 200:
                data = response.json()
                logger.debug(f"Retrieved current weather for {location}")
                return data
            else:
                logger.error(f"Failed to get weather data: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"Error getting weather data: {e}")
            return None
    
    def get_forecast(self, location: str, days: int = 3) -> Optional[Dict[str, Any]]:
        """
        Get weather forecast for a location
        
        Args:
            location: City name or coordinates
            days: Number of days for forecast (max 3 for free tier)
            
        Returns:
            Forecast data or None if request failed
        """
        try:
            url = f"{self.BASE_URL}/forecast.json"
            params = {
                'key': self.api_key,
                'q': location,
                'days': min(days, 3),  # Free tier only supports 3 days
                'aqi': 'no',
                'alerts': 'no'
            }
            
            response = requests.get(url, params=params)
            
            if response.status_code == 200:
                data = response.json()
                logger.debug(f"Retrieved {min(days, 3)}-day forecast for {location}")
                return data
            else:
                logger.error(f"Failed to get forecast data: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"Error getting forecast data: {e}")
            return None