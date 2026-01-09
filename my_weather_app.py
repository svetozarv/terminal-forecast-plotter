from functools import singledispatch, singledispatchmethod

import plotext
from numpy import ndarray

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
    @singledispatchmethod
    def __get_any_weather(self, get_func, lat: float = None, lon: float = None) -> WeatherForecast:
        self.__update_current_coords(weather := get_func(lat, lon))
        return weather

    @__get_any_weather.register(str)
    def _(self, get_func, city_prompt: str) -> WeatherForecast:
        return self.__get_any_weather(get_func, *self.__geocoder.convert_city_name_to_coords(city_prompt))

    def get_current_weather(self, *args) -> CurrentWeatherForecast:
        self.__validate_args(*args)
        return self.__get_any_weather(self.__api.get_current_weather, *args)

    def get_hourly_forecast(self, *args) -> HourlyWeatherForecast:
        self.__validate_args(*args)
        return self.__get_any_weather(self.__api.get_hourly_forecast, *args)

    def get_daily_forecast(self, *args) -> DailyWeatherForecast:
        self.__validate_args(*args)
        return self.__get_any_weather(self.__api.get_daily_forecast, *args)

    def __validate_args(self, *args):
        """
        Valid args:
        - no args -> use current location
        - (lat: float, lon: float)
        - (city_name: str)
        """
        if len(args) == 0:
            return
        if len(args) == 1 and isinstance(args[0], str):
            return
        if len(args) == 2 and all(isinstance(arg, float) for arg in args):
            return
        raise ValueError(
            "Invalid arguments provided to get weather. "
            "Usage: get_weather(city_name: str) or get_weather(latitude: float, longitude: float)"
        )

    @property  # user cannot change current location
    def current_coords(self):
        return self.__current_coords

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
