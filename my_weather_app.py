import argparse
import time
from functools import singledispatch, singledispatchmethod

import numpy as np
import plotext
from numpy import ndarray

import geocoder
import helpers
from api_session import ApiSession, DailyWeather, HourlyWeather, Weather


# TODO: Create interfaces for future extension??
class MyWeatherApp:
    """
    The main API. All the logic is listed here.
    """
    def __init__(self):
        self.api = ApiSession()
        # self.plotter = Plotter(plt)
        self.__current_coords = None

    def __update_current_coords(self, weather: Weather):
        """
        Updates the coords specified during last api call
        """
        self.__current_coords = (weather.latitude, weather.longitude)

    @property
    def current_coords(self):  # user cannot change current coords
        return self.__current_coords

    @singledispatchmethod
    def __get_any_forecast(self, latitude: float, longitude: float, func):
        """
        Higher order function as an attempt to follow DRY
        """
        weather = func(latitude, longitude)
        self.__update_current_coords(weather)
        return weather

    @__get_any_forecast.register(str)
    def _(self, city_name: str, func):
        if city_name:
            lat, lon = geocoder.city_name_to_coords(city_name)
        else:
            lat, lon = None, None
        weather = func(lat, lon)
        self.__update_current_coords(weather)
        return weather

    @singledispatchmethod
    def get_hourly_forecast(self, latitude: float = None, longitude: float = None):
        """
        latitude and longitude can be None
        in that case a random city will be chosen for demostration purposes
        """
        return self.__get_any_forecast(latitude, longitude, self.api.get_hourly_data)

    @get_hourly_forecast.register(str)
    def _(self, city_name: str = None):
        return self.__get_any_forecast(city_name, self.api.get_hourly_data)

    @singledispatchmethod
    def get_daily_forecast(self, latitude: float = None, longitude: float = None):
        """
        latitude and longitude can be None
        in that case a random city will be chosen for demostration purposes
        """
        return self.__get_any_forecast(latitude, longitude, self.api.get_daily_data)

    @get_daily_forecast.register(str)
    def _(self, city_name: str = None):
        return self.__get_any_forecast(city_name, self.api.get_daily_data)

    @singledispatchmethod
    def get_current_weather(self, latitude: float = None, longitude: float = None):
        """
        latitude and longitude can be None
        in that case a random city will be chosen for demostration purposes
        """
        return self.__get_any_forecast(latitude, longitude, self.api.get_current_weather)

    @get_current_weather.register(str)
    def _(self, city_name: str = None):
        return self.__get_any_forecast(city_name, self.api.get_current_weather)

    def draw_daily_plot(self, plt: plotext, city: str):
        weather_forecast = self.get_daily_forecast(city)
        self.__draw_plot(plt, weather_forecast)

    def draw_hourly_plot(self, plt: plotext, city: str):
        weather_forecast = self.get_hourly_forecast(city)
        self.__draw_plot(plt, weather_forecast)

    def __draw_plot(self, plt: plotext, weather_forecast: DailyWeather | HourlyWeather):
        location = geocoder.coords_to_city_name(weather_forecast.latitude, weather_forecast.longitude)
        coords = helpers.coords_to_str(weather_forecast.latitude, weather_forecast.longitude)

        # loop through fields of weather_forecast and make plot for each of them??
        series, labels = make_data_payload(weather_forecast, self.api.params)

        self.plotter = Plotter(plt)
        self.plotter.draw(weather_forecast, series, labels, title=location or coords)

    def create_alert_message(self):
        """
        Based on saved alerts, output a message in console
        """
        pass


class Plotter:
    def __init__(self, plt: plotext):
        # plt.clear_terminal()
        # plt.theme("dark")
        self.plt = plt
        self.y_label = "°C"
        plt.xlabel("Time")
        plt.ylabel(self.y_label)

    def draw(self, weather_forecast: DailyWeather, seq_of_series: list[ndarray], labels: list[str], title: str):
        """
        Draw few plots on a sigle canvas (for instance: both temp and humidity on a single plot).
        len(series) and len(labels) must be equal.
        seq_of_series is a list of ndarrays for the values to draw
        """
        plt = self.plt
        plt.clear_data()
        plt.clear_figure()
        plt.title(title)
        for single_series, label in zip(seq_of_series, labels):
            x_labels = helpers.datetime_to_labels(weather_forecast.time, weather_forecast.time_end, weather_forecast.interval)
            x_axis_indices = range(len(single_series))
            plt.plot(x_axis_indices, single_series, marker="braille", label=label)
            plt.xticks(ticks=x_axis_indices, labels=x_labels)
        plt.show()


# adapter for plotter
@singledispatch
def make_data_payload(weather_forecast: DailyWeather, params: list[str]) -> list[ndarray]:
    # edit the labels list to select the displayed data among requested
    # labels = params["daily"]
    labels = [
        "temperature_2m_max",
        "temperature_2m_min",
        "apparent_temperature_max",
        "apparent_temperature_min"
    ]
    series = obj_properties_from_strings(weather_forecast, params["daily"])
    return series, labels

@make_data_payload.register(HourlyWeather)
def _(weather_forecast: HourlyWeather, params: list[str]) -> list[ndarray]:
    # labels = params["hourly"]
    labels = [
        "temperature_2m",
        "apparent_temperature"
    ]
    series = obj_properties_from_strings(weather_forecast, params["hourly"])
    return series, labels

def obj_properties_from_strings(obj, ls: list[str]) -> list[any]:
    """
    `["height", "width"]` -> `[obj.height, obj.width]`
    """
    properties = []
    for property_str in ls:
        properties.append(getattr(obj, property_str, None))
    return properties


if __name__ == "__main__":
    MyWeatherApp().draw_hourly_plot(plotext, "Amsterdam")
