import datetime as dt
import logging
import random
from dataclasses import dataclass

import openmeteo_requests
import pandas as pd
import requests_cache
from openmeteo_requests.Client import WeatherApiResponse
from retry_requests import retry

# https://open-meteo.com/en/docs
# a dictionary of some major cities for random selection
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
        """
        Initialize API session with provided coordinates (randomly chosen if not provided)
        """
        if not latitude or not longitude:  # coords wasn't provided, pick a random city
            random_city = random.choice(list(cities.keys()))
            latitude, longitude = cities[random_city]
        elif not isinstance(latitude, float) or not isinstance(longitude, float):  # coords provided, validate
            raise ValueError("Latitude and Longitude must be float values.")
        logging.debug(f"Default city for API session: ({latitude}, {longitude})")
        self.change_default_location(latitude, longitude)

        # Setup the Open-Meteo API client with cache and retry on error
        self.__cache_session = requests_cache.CachedSession(".cache", expire_after=3600)
        self.__retry_session = retry(self.__cache_session, retries=5, backoff_factor=0.2)
        self.__openmeteo = openmeteo_requests.Client(session=self.__retry_session)

        self.__url = "https://api.open-meteo.com/v1/forecast"
        self.__params = {
            "latitude": latitude,
            "longitude": longitude,
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

        self._last_response: WeatherApiResponse | None = None # типо атрибут если у тебя ласт респонса нет, то мы идем к следующему блоку, а если есть то мы его чекаем параметрами которыми ты написал
        self._last_lat: float | None = None
        self._last_lon: float | None = None
    @property
    def params(self):
        return self.__params

    def change_default_location(self, latitude: float, longitude: float):
        if not isinstance(latitude, float) or not isinstance(longitude, float):
            raise ValueError("Latitude and Longitude must be float values.")
        self.__default_lat = latitude
        self.__default_lon = longitude

    def __change_target_location(self, latitude: float, longitude: float):
        if not isinstance(latitude, float) or not isinstance(longitude, float):
            raise ValueError("Latitude and Longitude must be float values.")
        self.__params["latitude"] = latitude
        self.__params["longitude"] = longitude

    def _make_api_call(self, latitude: float = None, longitude: float = None) -> WeatherApiResponse:
        """
        Make a single call (only one city/result) for provided coords.
        If coords are not provided, default coords will be used (set during initialization).
        """
        # Update self.__params if args are provided else use default values
        if not latitude or not longitude:
            latitude = self.__default_lat
            longitude = self.__default_lon

        if self._last_response is not None:
            if self._last_lat == latitude and self._last_lon == longitude:
                return self._last_response

        self.__change_target_location(latitude, longitude)

        # Process first location. Add a for-loop for multiple locations or weather models
        responses = self.__openmeteo.weather_api(self.__url, params=self.__params)
        self._last_response = responses[0]
        self._last_lat = latitude
        self._last_lon = longitude
        return self._last_response

        # здесь реюзаем ласт респонс в случае если его нет ты делаешь новый колл

    def get_current_weather(
        self, latitude: float = None, longitude: float = None, verbose=False
    ) -> "CurrentWeatherForecast":
        """
        Get (print) current weather
        """
        response = self._make_api_call(latitude, longitude)
        current = WeatherForecastFactory.create_current_weather_forecast(response)
        if verbose:
            current.print_info()
        return current

    def get_hourly_forecast(
        self, latitude: float = None, longitude: float = None, verbose=False
    ) -> "HourlyWeatherForecast":
        """
        Get hourly forecast of the next 7 days.
        Used for plotting.
        """
        response = self._make_api_call(latitude, longitude)
        hourly = WeatherForecastFactory.create_hourly_weather_forecast(response)
        if verbose:
            hourly.print_info()
        return hourly

    def get_daily_forecast(
        self, latitude: float = None, longitude: float = None, verbose=False
    ) -> "DailyWeatherForecast":
        """
        Get daily forecast of the next 7 days.
        Used for plotting.
        """
        response = self._make_api_call(latitude, longitude)
        daily = WeatherForecastFactory.create_daily_weather_forecast(response)
        if verbose:
            daily.print_info()
        return daily

# These classes represent received weather data (JSON response parsed to dataclasses)
@dataclass(frozen=True)
class WeatherForecast:  # or Position?
    latitude: float
    longitude: float
    elevation: float
    timezone_diff_utc0: int

    def print_info(self):   # or to_datasframe()?
        print(f"Latitude: {self.latitude}°N")
        print(f"Longitude: {self.longitude}°E")
        print(f"Elevation: {self.elevation} m asl")
        print(f"Timezone difference to GMT+0: {self.timezone_diff_utc0}s")


@dataclass(frozen=True)
class CurrentWeatherForecast(WeatherForecast):
    time: str
    temperature_2m: float
    relative_humidity_2m: float
    apparent_temperature: float
    is_day: int
    wind_speed_10m: float
    wind_direction_10m: float
    precipitation: float
    cloud_cover: float
    surface_pressure: float

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


@dataclass(frozen=True)
class IntervalicWeatherForecast(WeatherForecast):
    time: int
    time_end: int
    interval: int


@dataclass(frozen=True)
class HourlyWeatherForecast(IntervalicWeatherForecast):
    temperature_2m: pd.Series
    apparent_temperature: pd.Series
    relative_humidity_2m: pd.Series

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


@dataclass(frozen=True)
class DailyWeatherForecast(IntervalicWeatherForecast):
    temperature_2m_max: pd.Series
    temperature_2m_min: pd.Series
    apparent_temperature_max: pd.Series
    apparent_temperature_min: pd.Series
    sunrise: pd.Series
    sunset: pd.Series
    daylight_duration: pd.Series
    precipitation_hours: pd.Series
    precipitation_sum: pd.Series

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


class WeatherForecastFactory:
    @staticmethod
    def create_current_weather_forecast(open_meteo_response: WeatherApiResponse) -> "CurrentWeatherForecast":
        return CurrentWeatherFactory.create(open_meteo_response)

    @staticmethod
    def create_hourly_weather_forecast(open_meteo_response: WeatherApiResponse) -> "HourlyWeatherForecast":
        return HourlyWeatherForecastFactory.create(open_meteo_response)

    @staticmethod
    def create_daily_weather_forecast(open_meteo_response: WeatherApiResponse) -> "DailyWeatherForecast":
        return DailyWeatherForecastFactory.create(open_meteo_response)


class CurrentWeatherFactory:
    @staticmethod
    def create(open_meteo_response: WeatherApiResponse) -> "CurrentWeatherForecast":
        current = open_meteo_response.Current()
        return CurrentWeatherForecast(
            # Process current data. The order of variables needs to be the same as requested.
            latitude=open_meteo_response.Latitude(),
            longitude=open_meteo_response.Longitude(),
            elevation=open_meteo_response.Elevation(),
            timezone_diff_utc0=open_meteo_response.UtcOffsetSeconds(),
            time=current.Time(),
            temperature_2m=current.Variables(0).Value(),
            relative_humidity_2m=current.Variables(1).Value(),
            apparent_temperature=current.Variables(2).Value(),
            is_day=current.Variables(3).Value(),
            wind_speed_10m=current.Variables(4).Value(),
            wind_direction_10m=current.Variables(5).Value(),
            precipitation=current.Variables(6).Value(),
            cloud_cover=current.Variables(7).Value(),
            surface_pressure=current.Variables(8).Value(),
        )

class HourlyWeatherForecastFactory:
    @staticmethod
    def create(open_meteo_response: WeatherApiResponse) -> "HourlyWeatherForecast":
        hourly = open_meteo_response.Hourly()
        return HourlyWeatherForecast(
            # Process hourly data. The order of variables needs to be the same as requested.
            latitude=open_meteo_response.Latitude(),
            longitude=open_meteo_response.Longitude(),
            elevation=open_meteo_response.Elevation(),
            timezone_diff_utc0=open_meteo_response.UtcOffsetSeconds(),
            time=hourly.Time(),
            time_end=hourly.TimeEnd(),
            interval=hourly.Interval(),
            temperature_2m=hourly.Variables(0).ValuesAsNumpy(),
            apparent_temperature=hourly.Variables(1).ValuesAsNumpy(),
            relative_humidity_2m=hourly.Variables(2).ValuesAsNumpy(),
        )

class DailyWeatherForecastFactory:
    @staticmethod
    def create(open_meteo_response: WeatherApiResponse) -> "DailyWeatherForecast":
        daily = open_meteo_response.Daily()
        return DailyWeatherForecast(
            # Process daily data. The order of variables needs to be the same as requested.
            latitude=open_meteo_response.Latitude(),
            longitude=open_meteo_response.Longitude(),
            elevation=open_meteo_response.Elevation(),
            timezone_diff_utc0=open_meteo_response.UtcOffsetSeconds(),
            time=daily.Time(),
            time_end=daily.TimeEnd(),
            interval=daily.Interval(),
            temperature_2m_max=daily.Variables(0).ValuesAsNumpy(),
            temperature_2m_min=daily.Variables(1).ValuesAsNumpy(),
            apparent_temperature_max=daily.Variables(2).ValuesAsNumpy(),
            apparent_temperature_min=daily.Variables(3).ValuesAsNumpy(),
            sunrise=daily.Variables(4).ValuesInt64AsNumpy(),
            sunset=daily.Variables(5).ValuesInt64AsNumpy(),
            daylight_duration=daily.Variables(6).ValuesAsNumpy(),
            precipitation_hours=daily.Variables(7).ValuesAsNumpy(),
            precipitation_sum=daily.Variables(8).ValuesAsNumpy(),
        )

if __name__ == "__main__":
    api = ApiSession()
    current = api.get_current_weather(verbose=True)
    daily = api.get_daily_forecast(verbose=True)
    hourly = api.get_hourly_forecast(verbose=True)
    a = hourly.__dir__()
