from functools import singledispatch, singledispatchmethod

import plotext
from numpy import ndarray

from api_session import (
    ApiSession,
    CurrentWeatherForecast,
    IntervalicWeatherForecast,
    DailyWeatherForecast,
    HourlyWeatherForecast,
    WeatherForecast,
)
from geocoder import Geocoder, Location
from helpers import datetime_to_labels, coords_to_str


# TODO: Create interfaces for future extension??
class MyWeatherApp:
    """
    The main API. All the logic is listed here.
    """
    def __init__(self):
        self.__current_location = Location(city_prompt="Warszawa")  # default
        self.api = ApiSession(self.__current_location.coords[0], self.__current_location.coords[1])
        self.geocoder = Geocoder()

    def get_current_weather(self, location: Location = None) -> CurrentWeatherForecast:
        if location is None:
            lat, lon = None, None
        else:
            lat, lon = location.to_coords()
        self.__update_current_location(weather := self.api.get_current_weather(lat, lon))
        return weather

    def get_hourly_forecast(self, location: Location = None) -> HourlyWeatherForecast:
        if location is None:
            lat, lon = None, None
        else:
            lat, lon = location.to_coords()
        self.__update_current_location(weather := self.api.get_hourly_forecast(lat, lon))
        return weather

    def get_daily_forecast(self, location: Location = None) -> DailyWeatherForecast:
        if location is None:
            lat, lon = None, None
        else:
            lat, lon = location.to_coords()
        self.__update_current_location(weather := self.api.get_daily_forecast(lat, lon))
        return weather

    @property   # user cannot change current location
    def current_location(self):
        return self.__current_location

    def __update_current_location(self, weather: WeatherForecast):
        """
        Updates the location specified during last api call
        """
        if not weather:
            raise ValueError("No weather data to update location from.")
        self.__current_location.coords = (weather.latitude, weather.longitude)

    def draw_daily_plot(self, plt: plotext, city: str):
        weather_forecast = self.get_daily_forecast(Location(city_prompt=city))
        self.__draw_plot(plt, weather_forecast)

    def draw_hourly_plot(self, plt: plotext, city: str):
        weather_forecast = self.get_hourly_forecast(Location(city_prompt=city))
        self.__draw_plot(plt, weather_forecast)

    def __draw_plot(self, plt: plotext, weather_forecast: IntervalicWeatherForecast):
        # loop through fields of weather_forecast and make plot for each of them??
        series, labels = make_data_payload(weather_forecast, self.api.params)
        location = self.geocoder.convert_coords_to_city_name(weather_forecast.latitude, weather_forecast.longitude)

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
