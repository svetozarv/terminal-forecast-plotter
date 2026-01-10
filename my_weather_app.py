from functools import singledispatch, singledispatchmethod

import plotext
from numpy import ndarray
import logging
logging.getLogger("my_weather_app")
logging.basicConfig(filename='my_weather_app.log', level=logging.INFO, filemode="w+")

from api_session import (
    ApiSession,
    CurrentWeatherForecast,
    DailyWeatherForecast,
    HourlyWeatherForecast,
    IntervalicWeatherForecast,
    WeatherForecast,
)
from geocoder import Geocoder
from helpers import coords_to_str, datetime_to_labels


# TODO: Create interfaces for future extension??
class MyWeatherApp:
    """
    The main API. All the logic is listed here.
    """
    def __init__(self):
        self.__api = ApiSession()
        self.__geocoder = Geocoder()
        self.__current_coords = None

    # taking responsibility to convert from str to coords if necessary
    # this works great with caching system of Geocoder() since we have only one instance of
    # it taking care of every 'translation' during runtime
    def _fetch_weather(self, get_func, lat: float, lon: float) -> WeatherForecast:
        """Lat & lon can be None, in that case a random city will be picked."""
        self.__update_current_coords(weather := get_func(lat, lon))
        return weather

    def _resolve_location(self, location: str | tuple[float, float]) -> tuple[float, float]:
        """Convert city_name to coords if necessary"""
        if not location:  # pick a random city
            return None, None
        if isinstance(location, str):
            return self.__geocoder.convert_city_name_to_coords(location)
        return location

    def get_current_weather(self, location: str | tuple[float, float] = None) -> CurrentWeatherForecast:
        lat, lon = self._resolve_location(location)
        return self._fetch_weather(self.__api.get_current_weather, lat, lon)

    def get_hourly_forecast(self, location: str | tuple[float, float] = None) -> HourlyWeatherForecast:
        lat, lon = self._resolve_location(location)
        return self._fetch_weather(self.__api.get_hourly_forecast, lat, lon)

    def get_daily_forecast(self, location: str | tuple[float, float] = None) -> DailyWeatherForecast:
        lat, lon = self._resolve_location(location)
        return self._fetch_weather(self.__api.get_daily_forecast, lat, lon)

    @property  # user cannot change current location
    def current_coords(self):
        return self.__current_coords

    def current_city_name(self) -> str:
        return self.__geocoder.convert_coords_to_city_name(*self.__current_coords)

    def __update_current_coords(self, weather: WeatherForecast):
        """
        Updates the location specified during last api call
        """
        if not weather:
            raise ValueError("No weather data to update location from.")
        self.__current_coords = (weather.latitude, weather.longitude)

    def draw_daily_plot(self, plt: plotext, city_prompt: str):
        """city is expected to be a valid city_name f.e. `Warsaw, Poland`"""
        weather_forecast = self.get_daily_forecast(city_prompt)
        self.__draw_plot(plt, weather_forecast)

    def draw_hourly_plot(self, plt: plotext, city_prompt: str):
        weather_forecast = self.get_hourly_forecast(city_prompt)
        self.__draw_plot(plt, weather_forecast)

    def __draw_plot(self, plt: plotext, weather_forecast: IntervalicWeatherForecast):
        series, labels = make_data_payload(weather_forecast, self.__api.params)
        location = self.__geocoder.convert_coords_to_city_name(weather_forecast.latitude, weather_forecast.longitude)

        self.plotter = Plotter(plt)
        self.plotter.draw(weather_forecast, series, labels, title=location)


class Plotter:
    def __init__(self, plt: plotext):
        # plt.clear_terminal()
        # plt.theme("dark")
        self.plt = plt
        self.y_label = "°C"
        plt.xlabel("Time")
        plt.ylabel(self.y_label)

    def draw(
        self,
        weather_forecast: IntervalicWeatherForecast,
        series_of_data_measurements: list[ndarray],
        labels: list[str],
        title: str,
    ):
        """
        Draw a few plots on a sigle canvas (for instance: both temp and humidity on a single plot).
        len(series) and len(labels) should be equal.
        """
        plt = self.plt
        plt.clear_data()
        plt.clear_figure()
        plt.title(title)
        for single_series, label in zip(series_of_data_measurements, labels):
            x_labels = datetime_to_labels(weather_forecast.time, weather_forecast.time_end, weather_forecast.interval)
            x_axis_indices = range(len(single_series))
            plt.plot(x_axis_indices, single_series, marker="braille", label=label)
            plt.xticks(ticks=x_axis_indices, labels=x_labels)
        plt.show()


# adapter for plotter
@singledispatch
def make_data_payload(weather_forecast: DailyWeatherForecast, params: list[str]) -> list[ndarray]:
    # labels = params["daily"]
    labels = [  # edit the labels list to select the displayed data among requested
        "temperature_2m_max",
        "temperature_2m_min",
        "apparent_temperature_max",
        "apparent_temperature_min"
    ]
    # take all fields of weather_forecast and make plot for each of them
    series = obj_properties_from_strings(weather_forecast, params["daily"])
    return series, labels

@make_data_payload.register(HourlyWeatherForecast)
def _(weather_forecast: HourlyWeatherForecast, params: list[str]) -> list[ndarray]:
    # labels = params["hourly"]
    labels = [
        "temperature_2m",
        "apparent_temperature"
    ]
    series = obj_properties_from_strings(weather_forecast, params["hourly"])
    return series, labels

def obj_properties_from_strings(obj, ls: list[str]) -> list[any]:
    """
    Example: `["height", "width"]` -> `[obj.height, obj.width]`
    """
    properties = []
    for property_str in ls:
        properties.append(getattr(obj, property_str, None))
    return properties


if __name__ == "__main__":
    MyWeatherApp().draw_hourly_plot(plotext, "Amsterdam")
    # MyWeatherApp().draw_hourly_plot(plotext, "Zakopane")
