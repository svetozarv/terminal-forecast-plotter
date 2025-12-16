import time
from dataclasses import dataclass
import openmeteo_requests
from openmeteo_requests.Client import WeatherApiResponse
import requests_cache
from retry_requests import retry
import matplotlib
import isort
import black
import pandas as pd

# https://open-meteo.com/en/docs
# 1. first version will be using terminal to communicate with user
# 2. settings will be saved to a file

cities = {
    "London": (51.5074, -0.1278),
    "Paris": (48.8566, 2.3522),
    "New Jork": (40.7128, -74.0060),
    "Rio de Janeiro": (-22.9068, -43.1729),
    "Tokio": (35.6895, 139.6917),
    "Dubai": (25.2048, 55.2708),
    "Bangkok": (13.7563, 100.5018),
    "Kair": (30.0444, 31.2357),
    "Kapsztad": (-33.9249, 18.4241),
    "Sydney": (-33.8688, 151.2093),
    "Warszawa": (52.2297, 21.0122),
}


class ApiSession:
    def __init__(self, latitude=None, longitude=None):
        """
        Initialize API session
        latitude and longitude default values are Warsaw
        """
        default_lat = 52.2297
        default_lon = 21.0122
        if not isinstance(latitude, float) or not isinstance(longitude, float):
            latitude = default_lat
            longitude = default_lon

        # Setup the Open-Meteo API client with cache and retry on error
        self.cache_session = requests_cache.CachedSession(".cache", expire_after=3600)
        self.retry_session = retry(self.cache_session, retries=5, backoff_factor=0.2)
        self.openmeteo = openmeteo_requests.Client(session=self.retry_session)

        self.url = "https://api.open-meteo.com/v1/forecast"
        self.params = {
            "latitude": default_lat if not latitude else latitude,
            "longitude": default_lon if not longitude else longitude,
            "daily": [
                "temperature_2m_max",
                "temperature_2m_min",
                "apparent_temperature_max",
                "apparent_temperature_min",
                "sunrise",
                "sunset",
                "daylight_duration",
                "precipitation_hours",
                "precipitation_sum",
            ],
            "hourly": [
                "temperature_2m",
                "apparent_temperature",
                "relative_humidity_2m",
            ],
            "current": [
                "temperature_2m",
                "relative_humidity_2m",
                "apparent_temperature",
                "is_day",
                "wind_speed_10m",
                "wind_direction_10m",
                "precipitation",
                "cloud_cover",
                "surface_pressure",
            ],
            "timezone": "auto",
        }

    def make_api_call(self, latitude, longitude) -> WeatherApiResponse:
        """
        Make a singe call (only one city/result) for provided args
        """
        # Update self.params if args are provided else do nothing (use existing/saved values or default)
        if latitude:
            self.params["latitude"] = latitude
        if longitude:
            self.params["longitude"] = longitude

        # Process first location. Add a for-loop for multiple locations or weather models
        responses = self.openmeteo.weather_api(self.url, params=self.params)
        response = responses[0]
        return response

    def get_current_weather(self, latitude, longitude, verbose=True):
        """
        Get (print) current weather
        """
        # TODO: add if statement, so there is no need to do it every time
        response = self.make_api_call(latitude, longitude)
        if verbose:
            print(f"Coordinates: {response.Latitude()}°N {response.Longitude()}°E")
            print(f"Elevation: {response.Elevation()} m asl")
            print(f"Timezone difference to GMT+0: {response.UtcOffsetSeconds()}s")

        # Process current data. The order of variables needs to be the same as requested.
        current = response.Current()
        current_temperature_2m = current.Variables(0).Value()
        current_relative_humidity_2m = current.Variables(1).Value()
        current_apparent_temperature = current.Variables(2).Value()
        current_is_day = current.Variables(3).Value()
        current_wind_speed_10m = current.Variables(4).Value()
        current_wind_direction_10m = current.Variables(5).Value()
        current_precipitation = current.Variables(6).Value()
        current_cloud_cover = current.Variables(7).Value()
        current_surface_pressure = current.Variables(8).Value()

        if verbose:
            print(f"\nCurrent time: {current.Time()}")
            print(f"Current temperature_2m: {current_temperature_2m}")
            print(f"Current relative_humidity_2m: {current_relative_humidity_2m}")
            print(f"Current apparent_temperature: {current_apparent_temperature}")
            print(f"Current is_day: {current_is_day}")
            print(f"Current wind_speed_10m: {current_wind_speed_10m}")
            print(f"Current wind_direction_10m: {current_wind_direction_10m}")
            print(f"Current precipitation: {current_precipitation}")
            print(f"Current cloud_cover: {current_cloud_cover}")
            print(f"Current surface_pressure: {current_surface_pressure}")

    def get_hourly_data(self, latitude, longitude):
        """
        Get hourly data from the past 7 days.
        Used for plotting.
        """
        # TODO: add if statement, so there is no need to do it every time
        # Process hourly data. The order of variables needs to be the same as requested.
        response = self.make_api_call(latitude, longitude)
        hourly = response.Hourly()
        hourly_temperature_2m = hourly.Variables(0).ValuesAsNumpy()
        hourly_apparent_temperature = hourly.Variables(1).ValuesAsNumpy()
        hourly_relative_humidity_2m = hourly.Variables(2).ValuesAsNumpy()

        hourly_data = {
            "date": pd.date_range(
                start=pd.to_datetime(hourly.Time(), unit="s", utc=True),
                end=pd.to_datetime(hourly.TimeEnd(), unit="s", utc=True),
                freq=pd.Timedelta(seconds=hourly.Interval()),
                inclusive="left",
            )
        }

        hourly_data["temperature_2m"] = hourly_temperature_2m
        hourly_data["apparent_temperature"] = hourly_apparent_temperature
        hourly_data["relative_humidity_2m"] = hourly_relative_humidity_2m

        hourly_dataframe = pd.DataFrame(data=hourly_data)
        print("\nHourly data\n", hourly_dataframe)


class WeatherApp:
    def __init__(self):
        """
        Setup the Open-Meteo API client with cache and retry on error
        """
        self._url = "https://api.open-meteo.com/v1/forecast"
        self._cache_session = requests_cache.CachedSession(".cache", expire_after=3_600)
        self._retry_session = retry(self._cache_session, retries=5, backoff_factor=0.2)
        self._openmeteo = openmeteo_requests.Client(session=self._retry_session)

    def get_data_from_api(
        self,
        latitude,
        longitude,
        elevation=None,
        timezone=None,
        start_date=None,
        end_date=None,
    ):
        """
        Make a GET request of weather data for provided city
        """
        # Make sure all required weather variables are listed here
        # The order of variables in hourly or daily is important to assign them correctly below
        params = {
            "latitude": latitude,
            "longitude": longitude,
            "hourly": "temperature_2m",
        }
        responses_for_locations = self._openmeteo.weather_api(self._url, params=params)

        # Process first location. Add a for-loop for multiple locations or weather models
        response = responses_for_locations[0]
        print(f"Coordinates: {response.Latitude()}°N {response.Longitude()}°E")
        print(f"Elevation: {response.Elevation()} m asl")
        print(f"Timezone difference to GMT+0: {response.UtcOffsetSeconds()}s")
        return response

    def create_alert(self):
        """
        Save alert data to file (or internal data structure but saved on app close via del?)
        """
        pass

    def draw_plot(self):
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


if __name__ == "__main__":
    pass
