"""
OpenWeatherMap API service
"""
import logging
from typing import Optional, Tuple
import requests
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class WeatherService:
    """Service for fetching weather data from OpenWeatherMap"""
    
    BASE_URL = "http://api.openweathermap.org/data/2.5"
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize WeatherService
        
        Args:
            api_key: OpenWeatherMap API key (optional, will use from config if not provided)
        """
        from app.config import settings
        self.api_key = api_key or settings.openweather_api_key
        if not self.api_key:
            logger.warning("OpenWeatherMap API key not provided - weather features will be limited")
    
    def get_current_weather(self, city: str, country_code: str = "IN") -> Optional[dict]:
        """
        Fetch current weather for a city
        
        Args:
            city: City name
            country_code: Country code (default: "IN" for India)
        
        Returns:
            Dictionary with temperature and rain_probability, or None if failed
        """
        try:
            url = f"{self.BASE_URL}/weather"
            params = {
                "q": f"{city},{country_code}",
                "appid": self.api_key,
                "units": "metric"
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            # Extract temperature
            temperature = data.get("main", {}).get("temp")
            
            # Extract rain probability (from current weather)
            # OpenWeatherMap current weather doesn't provide probability,
            # so we check if it's currently raining
            rain_probability = 0.0
            if "rain" in data:
                rain_probability = 1.0
            elif "weather" in data and len(data["weather"]) > 0:
                # Check weather condition code for rain
                weather_id = data["weather"][0].get("id", 0)
                if 200 <= weather_id < 600:  # Rain/snow codes
                    rain_probability = 0.5
            
            result = {
                "temperature": temperature,
                "rain_probability": rain_probability
            }
            
            logger.info(f"Weather for {city}: temp={temperature}°C, rain_prob={rain_probability}")
            return result
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching current weather for {city}: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error fetching weather for {city}: {e}")
            return None
    
    def get_forecast(self, city: str, country_code: str = "IN", days: int = 1) -> Optional[dict]:
        """
        Fetch weather forecast for a city
        
        Args:
            city: City name
            country_code: Country code
            days: Number of days to forecast (default: 1)
        
        Returns:
            Dictionary with temperature and rain_probability for the forecast period
        """
        try:
            url = f"{self.BASE_URL}/forecast"
            params = {
                "q": f"{city},{country_code}",
                "appid": self.api_key,
                "units": "metric",
                "cnt": days * 8  # 8 forecasts per day (3-hour intervals)
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if "list" not in data or len(data["list"]) == 0:
                logger.warning(f"No forecast data for {city}")
                return None
            
            # Aggregate forecast data
            temperatures = []
            rain_probabilities = []
            
            for forecast in data["list"]:
                temp = forecast.get("main", {}).get("temp")
                if temp is not None:
                    temperatures.append(temp)
                
                # Check for rain in forecast
                if "rain" in forecast:
                    rain_probabilities.append(1.0)
                elif "weather" in forecast and len(forecast["weather"]) > 0:
                    weather_id = forecast["weather"][0].get("id", 0)
                    if 200 <= weather_id < 600:
                        rain_probabilities.append(0.5)
                    else:
                        rain_probabilities.append(0.0)
                else:
                    rain_probabilities.append(0.0)
            
            avg_temp = sum(temperatures) / len(temperatures) if temperatures else None
            max_rain_prob = max(rain_probabilities) if rain_probabilities else 0.0
            
            result = {
                "temperature": avg_temp,
                "rain_probability": max_rain_prob
            }
            
            logger.info(f"Forecast for {city}: avg_temp={avg_temp}°C, max_rain_prob={max_rain_prob}")
            return result
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching forecast for {city}: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error fetching forecast for {city}: {e}")
            return None
    
    def get_forecast(self, city: str, hours_ahead: int = 24, country_code: str = "IN") -> Optional[dict]:
        """
        Get weather forecast with hourly breakdown
        
        Args:
            city: City name
            hours_ahead: Number of hours to forecast
            country_code: Country code
        
        Returns:
            Dictionary with forecast list containing hourly data
        """
        if not self.api_key:
            return None
        
        try:
            url = f"{self.BASE_URL}/forecast"
            params = {
                "q": f"{city},{country_code}",
                "appid": self.api_key,
                "units": "metric"
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if "list" not in data or len(data["list"]) == 0:
                return None
            
            # Process forecast data into hourly format
            forecast_list = []
            current_time = datetime.now()
            
            for forecast in data["list"]:
                forecast_time = datetime.fromtimestamp(forecast.get("dt", 0))
                hours_diff = (forecast_time - current_time).total_seconds() / 3600
                
                if hours_diff > hours_ahead:
                    break
                
                temp = forecast.get("main", {}).get("temp")
                rain_prob = 0.0
                
                # Check for rain
                if "rain" in forecast:
                    rain_prob = min(forecast["rain"].get("3h", 0) / 3.0, 1.0)  # Normalize
                elif "weather" in forecast and len(forecast["weather"]) > 0:
                    weather_id = forecast["weather"][0].get("id", 0)
                    if 200 <= weather_id < 600:
                        rain_prob = 0.5
                
                forecast_list.append({
                    "hours_ahead": int(hours_diff),
                    "temperature": temp,
                    "rain_probability": rain_prob,
                    "timestamp": forecast_time.isoformat()
                })
            
            return {
                "city": city,
                "forecast": forecast_list
            }
            
        except Exception as e:
            logger.error(f"Error fetching hourly forecast: {e}")
            return None
    
    def get_weather_data(self, city: str, country_code: str = "IN", use_forecast: bool = True) -> Optional[dict]:
        """
        Get weather data (current or forecast)
        
        Args:
            city: City name
            country_code: Country code
            use_forecast: If True, use forecast; otherwise use current weather
        
        Returns:
            Dictionary with temperature and rain_probability
        """
        if use_forecast:
            return self.get_forecast(city, country_code, days=1)
        else:
            return self.get_current_weather(city, country_code)

