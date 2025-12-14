import time
from dataclasses import dataclass
import openmeteo_requests
import requests_cache
from retry_requests import retry

# https://open-meteo.com/en/docs
# 1. first version will be using terminal to communicate with user
# 2. settings will be saved to a file (with login and authentication?)
# 3. while executing a program, user's inputs will be parsed using input()


class WeatherApp:
    def __init__(self):
        """
        Setup the Open-Meteo API client with cache and retry on error
        """
        self._url = "https://api.open-meteo.com/v1/forecast"
        self._cache_session = requests_cache.CachedSession('.cache', expire_after=3_600)
        self._retry_session = retry(self._cache_session, retries=5, backoff_factor=0.2)
        self._openmeteo = openmeteo_requests.Client(session=self._retry_session)

    def _get_data_from_api(self, latitude, longitude, elevation, timezone, start_date, end_date):
        """
        a city/region or coordinates must be provided
        """
        
        # Make sure all required weather variables are listed here
        # The order of variables in hourly or daily is important to assign them correctly below
        params = {
            "latitude": 52.52,
            "longitude": 13.41,
            "hourly": "temperature_2m",
        }
        responses = self._openmeteo.weather_api(self._url, params=params)

        # Process first location. Add a for-loop for multiple locations or weather models
        response = responses[0]
        print(f"Coordinates: {response.Latitude()}°N {response.Longitude()}°E")
        print(f"Elevation: {response.Elevation()} m asl")
        print(f"Timezone difference to GMT+0: {response.UtcOffsetSeconds()}s")

    def create_alert(self):
        """
        Save alert data to file (or internal data structure but saved on app close via del?)
        """
        pass
     

class TUI:
    def show_weather_info(self):
        """
        Output to the terminal
        """
        pass

    def create_alert_message(self):
        """
        Based on saved alerts, output a message in console
        """
        pass


@dataclass
class UserSettings:
    city: str
    alerts = []

    def save_alert(self):
        pass

    def save_prompt(self):
        pass

@dataclass
class Alert:
    """
    Alerts are mapped to cities
    """

    city: str
