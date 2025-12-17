import time
from dataclasses import dataclass

import black
import isort
import matplotlib
import openmeteo_requests
import pandas as pd
import requests_cache
from openmeteo_requests.Client import WeatherApiResponse
from retry_requests import retry

# https://open-meteo.com/en/docs
# TODO: make private fields

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
        default_lat = cities["Warszawa"][0]
        default_lon = cities["Warszawa"][1]
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

    def _make_api_call(self, latitude, longitude) -> WeatherApiResponse:
        """
        Make a singe call (only one city/result) for provided args
        """
        # Update self.params if args are provided else use existing/saved values or default
        if latitude:
            self.params["latitude"] = latitude
        if longitude:
            self.params["longitude"] = longitude

        # Process first location. Add a for-loop for multiple locations or weather models
        responses = self.openmeteo.weather_api(self.url, params=self.params)
        response = responses[0]
        return response

    def get_current_weather(self, latitude=None, longitude=None, verbose=True):
        """
        Get (print) current weather
        """
        # TODO: add if statement, so there is no need to do it every time
        response = self._make_api_call(latitude, longitude)
        current = CurrentWeather(response)
        if verbose:
            current.print_info()
                    
    def get_hourly_data(self, latitude=None, longitude=None, verbose=True):
        """
        Get hourly data from the past 7 days.
        Used for plotting.
        """
        # TODO: add if statement, so there is no need to do it every time
        response = self._make_api_call(latitude, longitude)
        hourly = HourlyWeather(response)
        if verbose:
            hourly.print_info()

    def get_daily_data(self, latitude=None, longitude=None, verbose=True):
        """
        Get daily data from the past 7 days.
        Used for plotting.
        """
        # TODO: add if statement, so there is no need to do it every time
        response = self._make_api_call(latitude, longitude)
        daily = DailyWeather(response)
        if verbose:
            daily.print_info()


class Weather:
    """
    Represents a json object received during API call
    """
    def __init__(self, open_meteo_response: WeatherApiResponse):
        self.latitude = open_meteo_response.Latitude()
        self.longitude = open_meteo_response.Longitude()
        self.elevation = open_meteo_response.Elevation()
        self.timezone_diff_utc0 = open_meteo_response.UtcOffsetSeconds()

    def print_info(self):
        print(f"Coordinates: {self.latitude}°N {self.longitude}°E")
        print(f"Elevation: {self.elevation} m asl")
        print(f"Timezone difference to GMT+0: {self.timezone_diff_utc0}s")


class CurrentWeather(Weather):
    def __init__(self, open_meteo_response):
        super().__init__(open_meteo_response)
        response = open_meteo_response.Current()
        
        # Process current data. The order of variables needs to be the same as requested.
        self.time = response.Time()
        self.temperature_2m = response.Variables(0).Value()
        self.relative_humidity_2m = response.Variables(1).Value()
        self.apparent_temperature = response.Variables(2).Value()
        self.is_day = response.Variables(3).Value()
        self.wind_speed_10m = response.Variables(4).Value()
        self.wind_direction_10m = response.Variables(5).Value()
        self.precipitation = response.Variables(6).Value()
        self.cloud_cover = response.Variables(7).Value()
        self.surface_pressure = response.Variables(8).Value()

    def print_info(self):
        print("\n--------- Current weather ---------")
        super().print_info()
        print(f"\nCurrent time: {self.time}")
        print(f"Current temperature_2m: {self.temperature_2m}")
        print(f"Current relative_humidity_2m: {self.relative_humidity_2m}")
        print(f"Current apparent_temperature: {self.apparent_temperature}")
        print(f"Current is_day: {self.is_day}")
        print(f"Current wind_speed_10m: {self.wind_speed_10m}")
        print(f"Current wind_direction_10m: {self.wind_direction_10m}")
        print(f"Current precipitation: {self.precipitation}")
        print(f"Current cloud_cover: {self.cloud_cover}")
        print(f"Current surface_pressure: {self.surface_pressure}")


class HourlyWeather(Weather):
    def __init__(self, open_meteo_response):
        """
        Process hourly data. The order of variables needs to be the same as requested.
        """
        super().__init__(open_meteo_response)
        hourly = open_meteo_response.Hourly()
        
        self.time = hourly.Time()
        self.time_end = hourly.TimeEnd()
        self.interval = hourly.Interval()
        
        self.temperature_2m = hourly.Variables(0).ValuesAsNumpy()
        self.apparent_temperature = hourly.Variables(1).ValuesAsNumpy()
        self.relative_humidity_2m = hourly.Variables(2).ValuesAsNumpy()
        
    def print_info(self):
        super().print_info()
        hourly_data = {
            "date": pd.date_range(
                start=pd.to_datetime(self.time, unit="s", utc=True),
                end=pd.to_datetime(self.time_end, unit="s", utc=True),
                freq=pd.Timedelta(seconds=self.interval),
                inclusive="left",
            )
        }

        hourly_data["temperature_2m"] = self.temperature_2m
        hourly_data["apparent_temperature"] = self.apparent_temperature
        hourly_data["relative_humidity_2m"] = self.relative_humidity_2m

        hourly_dataframe = pd.DataFrame(data=hourly_data)
        print("\nHourly data\n", hourly_dataframe)


class DailyWeather(Weather):
    def __init__(self, open_meteo_response):
        super().__init__(open_meteo_response)
        daily = open_meteo_response.Daily()

        # TODO: Move to common part
        self.time = daily.Time()
        self.time_end = daily.TimeEnd()
        self.interval = daily.Interval()

        # Process daily data. The order of variables needs to be the same as requested.
        self.temperature_2m_max = daily.Variables(0).ValuesAsNumpy()
        self.temperature_2m_min = daily.Variables(1).ValuesAsNumpy()
        self.apparent_temperature_max = daily.Variables(2).ValuesAsNumpy()
        self.apparent_temperature_min = daily.Variables(3).ValuesAsNumpy()
        self.sunrise = daily.Variables(4).ValuesInt64AsNumpy()
        self.sunset = daily.Variables(5).ValuesInt64AsNumpy()
        self.daylight_duration = daily.Variables(6).ValuesAsNumpy()
        self.precipitation_hours = daily.Variables(7).ValuesAsNumpy()
        self.precipitation_sum = daily.Variables(8).ValuesAsNumpy()

    def print_info(self):
        super().print_info()

        daily_data = {
            "date": pd.date_range(
                start=pd.to_datetime(self.time, unit="s", utc=True),
                end=pd.to_datetime(self.time_end, unit="s", utc=True),
                freq=pd.Timedelta(seconds=self.interval),
                inclusive="left",
            )
        }

        daily_data["temperature_2m_max"] = self.temperature_2m_max
        daily_data["temperature_2m_min"] = self.temperature_2m_min
        daily_data["apparent_temperature_max"] = self.apparent_temperature_max
        daily_data["apparent_temperature_min"] = self.apparent_temperature_min
        daily_data["sunrise"] = self.sunrise
        daily_data["sunset"] = self.sunset
        daily_data["daylight_duration"] = self.daylight_duration
        daily_data["precipitation_hours"] = self.precipitation_hours
        daily_data["precipitation_sum"] = self.precipitation_sum

        daily_dataframe = pd.DataFrame(data=daily_data)
        print("\nDaily data\n", daily_dataframe)


if __name__ == "__main__":
    api = ApiSession()
    api.get_current_weather()
    api.get_hourly_data()
    api.get_daily_data()
