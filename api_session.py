import datetime as dt
import random

import openmeteo_requests
import pandas as pd
import requests_cache
from openmeteo_requests.Client import WeatherApiResponse
from retry_requests import retry

# https://open-meteo.com/en/docs
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
    def __init__(self, latitude: float = None, longitude: float = None):
        random_city = random.choice(list(cities.keys()))
        self.__default_lat = cities[random_city][0]
        self.__default_lon = cities[random_city][1]
        if not isinstance(latitude, float) or not isinstance(longitude, float):
            latitude = self.__default_lat
            longitude = self.__default_lon

        # Setup the Open-Meteo API client with cache and retry on error
        self.__cache_session = requests_cache.CachedSession(".cache", expire_after=3600)
        self.__retry_session = retry(self.__cache_session, retries=5, backoff_factor=0.2)
        self.__openmeteo = openmeteo_requests.Client(session=self.__retry_session)

        self.__url = "https://api.open-meteo.com/v1/forecast"
        self.__params = {
            "latitude": self.__default_lat if not latitude else latitude,
            "longitude": self.__default_lon if not longitude else longitude,
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

    @property
    def params(self):
        return self.__params

    def _make_api_call(self, latitude: float = None, longitude: float = None) -> WeatherApiResponse:
        """
        Make a singe call (only one city/result) for provided args
        """
        # Update self.__params if args are provided else use random values
        if not latitude or not longitude:
            random_city = random.choice(list(cities.keys()))
            # latitude = cities[random_city][0]
            latitude = self.__default_lat
            # longitude = cities[random_city][1]
            longitude = self.__default_lon
        self.__params["latitude"] = latitude
        self.__params["longitude"] = longitude

        # Process first location. Add a for-loop for multiple locations or weather models
        responses = self.__openmeteo.weather_api(self.__url, params=self.__params)
        response = responses[0]
        return response

    def get_current_weather(self, latitude: float = None, longitude: float = None, verbose=False) -> "CurrentWeather":
        """
        Get (print) current weather
        """
        response = self._make_api_call(latitude, longitude)
        current = CurrentWeather(response)
        if verbose:
            current.print_info()
        return current

    def get_hourly_data(self, latitude: float = None, longitude: float = None, verbose=False) -> "HourlyWeather":
        """
        Get hourly forecast of the next 7 days.
        Used for plotting.
        """
        response = self._make_api_call(latitude, longitude)
        hourly = HourlyWeather(response)
        if verbose:
            hourly.print_info()
        return hourly

    def get_daily_data(self, latitude: float = None, longitude: float = None, verbose=False) -> "DailyWeather":
        """
        Get daily forecast of the next 7 days.
        Used for plotting.
        """
        response = self._make_api_call(latitude, longitude)
        daily = DailyWeather(response)
        if verbose:
            daily.print_info()
        return daily


class Weather:
    """
    Represents a json object received during API call
    """
    def __init__(self, open_meteo_response: WeatherApiResponse):
        # TODO: make the fields unchangeable
        self.latitude = open_meteo_response.Latitude()
        self.longitude = open_meteo_response.Longitude()
        self.elevation = open_meteo_response.Elevation()
        self.timezone_diff_utc0 = open_meteo_response.UtcOffsetSeconds()

    def print_info(self):
        print(f"Coordinates: {self.latitude}°N {self.longitude}°E")
        print(f"Elevation: {self.elevation} m asl")
        print(f"Timezone difference to GMT+0: {self.timezone_diff_utc0}s")


class CurrentWeather(Weather):
    def __init__(self, open_meteo_response: WeatherApiResponse):
        super().__init__(open_meteo_response)
        response = open_meteo_response.Current()

        # Process current data. The order of variables needs to be the same as requested.
        # TODO: make the fields unchangeable
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
    def __init__(self, open_meteo_response: WeatherApiResponse):
        super().__init__(open_meteo_response)
        hourly = open_meteo_response.Hourly()

        # TODO: make the fields unchangeable
        self.time: int = hourly.Time()
        self.time_end: int = hourly.TimeEnd()
        self.interval: int = hourly.Interval()

        # Process hourly data. The order of variables needs to be the same as requested
        self.temperature_2m = hourly.Variables(0).ValuesAsNumpy()
        self.apparent_temperature = hourly.Variables(1).ValuesAsNumpy()
        self.relative_humidity_2m = hourly.Variables(2).ValuesAsNumpy()

    def print_info(self):
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

        print("\n--------- Hourly data ---------")
        super().print_info()
        print(hourly_dataframe)


class DailyWeather(Weather):
    def __init__(self, open_meteo_response: WeatherApiResponse):
        super().__init__(open_meteo_response)
        daily = open_meteo_response.Daily()

        # TODO: Move to common part
        # TODO: make the fields unchangeable
        self.time: int = daily.Time()
        self.time_end: int = daily.TimeEnd()
        self.interval: int = daily.Interval()

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

        print("\n--------- Daily data ---------")
        super().print_info()
        print(daily_dataframe)

if __name__ == "__main__":
    api = ApiSession()
    api.get_current_weather(verbose=True)
    api.get_daily_data(verbose=True)
    hourly = api.get_hourly_data(verbose=True)
    a = hourly.__dir__()
