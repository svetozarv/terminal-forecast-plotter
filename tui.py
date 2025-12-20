import argparse
import time

import numpy as np
import plotext as plt
import TermTk as ttk
from numpy import ndarray

from helpers import coords_to_city_name, time_to_ticks
from user import *
from weather_app import ApiSession, DailyWeather, HourlyWeather


# TODO: Create interfaces for future extension??
class TerminalUserInterface:
    """
    May rather be MyWeatherApp, than TUI
    All the logic will be listed here
    """
    def __init__(self):
        self.api = ApiSession()
        self.plotter = Plotter()
        self.hourly_weather = self.api.get_hourly_data()
        self.daily_weather = self.api.get_daily_data()

    def draw_plot(self):
        self.plotter.draw(self.hourly_weather)

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


class Plotter:
    def __init__(self):
        plt.clear_terminal()
        plt.theme("dark")
        plt.xlabel("Time")
        plt.ylabel("°C")

    def draw(self, weather_forecast: DailyWeather | HourlyWeather) -> None:
        # TODO: it looks bad. make with visitor??
        # is this a good approach?
        if isinstance(weather_forecast, DailyWeather):
            self.__draw_daily(weather_forecast)
        elif isinstance(weather_forecast, HourlyWeather):
            self.__draw_hourly(weather_forecast)
        else:
            raise TypeError(
                f"Cannot draw plots for this type of data {type(weather_forecast)}"
            )

    def __draw_daily(self, weather_forecast: DailyWeather):
        pass

    def __draw_hourly(self, weather_forecast: HourlyWeather):
        location = coords_to_city_name(
            weather_forecast.latitude, weather_forecast.longitude
        )
        plt.title(f"Temperuture plot for {location}")

        # TODO: introspection?? loop through fields of weather_forecast and make plot for each of them??
        hourly_temperature = getattr(weather_forecast, "temperature_2m", None)
        daily_temperature = getattr(weather_forecast, "temperature_2m_max", None)
        hourly_apparent_temperature = getattr(weather_forecast, "apparent_temperature", None)
        daily_apparent_temperature = getattr(weather_forecast, "apparent_temperature_max", None)

        temperature = hourly_temperature if not daily_temperature else daily_temperature
        apparent_temperature = hourly_apparent_temperature if not daily_apparent_temperature else daily_apparent_temperature


        # make func to plot 1 value, f.i. temp and then add loop here to make plots for all values
        x_axis_indices = range(len(temperature))
        x_labels = time_to_ticks(
            weather_forecast.time, weather_forecast.time_end, weather_forecast.interval
        )

        plt.plot(x_axis_indices, temperature, marker="braille", label="Temperature")
        plt.plot(
            x_axis_indices,
            apparent_temperature,
            marker="braille",
            label="Apparent temperature",
        )
        plt.xticks(ticks=x_axis_indices, labels=x_labels)
        plt.show()

    def draw_subplot():
        pass


if __name__ == "__main__":
    TerminalUserInterface().draw_plot()
