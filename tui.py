import argparse
import time

import numpy as np
import plotext
import TermTk as ttk
from numpy import ndarray

from api_session import ApiSession, DailyWeather, HourlyWeather
from helpers import coords_to_city_name, datetime_to_labels
from user import *


# TODO: Create interfaces for future extension??
class TerminalUserInterface:
    """
    May rather be MyWeatherApp, than TUI
    All the logic will be listed here
    """
    def __init__(self):
        self.api = ApiSession()
        # self.plotter = Plotter(plt)

    def get_data(self):
        self.current_forecast = self.api.get_current_weather()
        self.daily_forecast = self.api.get_daily_data()
        self.hourly_forecast = self.api.get_hourly_data()

    def draw_plot(self, plt: plotext):
        self.get_data()
        plt.clear_data()
        plt.clear_figure()
        self.plotter = Plotter(plt)

        weather_forecast = self.hourly_forecast
        location = coords_to_city_name(weather_forecast.latitude, weather_forecast.longitude)

        # TODO: it looks bad. make with visitor??  is this a good approach?
        # TODO: introspection?? loop through fields of weather_forecast and make plot for each of them??
        hourly_temperature = getattr(weather_forecast, "temperature_2m", None)
        daily_temperature = getattr(weather_forecast, "temperature_2m_max", None)
        hourly_apparent_temperature = getattr(weather_forecast, "apparent_temperature", None)
        daily_apparent_temperature = getattr(weather_forecast, "apparent_temperature_max", None)
        temperature = hourly_temperature if not daily_temperature else daily_temperature
        apparent_temperature = hourly_apparent_temperature if not daily_apparent_temperature \
            else daily_apparent_temperature

        series = [temperature, apparent_temperature]
        labels = ["temperature", "apparent_temperature"]
        self.plotter.draw(weather_forecast, series, labels, location)

    def ask_for_weather(self):
        pass

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

    def mainloop(self):
        pass

class Plotter:
    def __init__(self, plt: plotext):
        # plt.clear_terminal()
        # plt.theme("dark")
        self.plt = plt
        plt.xlabel("Time")
        plt.ylabel("°C")

    def draw(self, weather_forecast: DailyWeather, series: list[ndarray], labels: list[str], location: str):
        """
        Draw len(series) plots on sigle canvas (for many data points, f.e. both temp and humidity on single plot)
        len(series) and len(labels) must be equal.
        """
        plt = self.plt
        plt.title(location)
        for single_series, label in zip(series, labels):
            x_labels = datetime_to_labels(weather_forecast.time, weather_forecast.time_end, weather_forecast.interval)
            x_axis_indices = range(len(single_series))
            plt.plot(x_axis_indices, single_series, marker="braille", label=label)
            plt.xticks(ticks=x_axis_indices, labels=x_labels)
        plt.show()


if __name__ == "__main__":
    TerminalUserInterface().draw_plot()
