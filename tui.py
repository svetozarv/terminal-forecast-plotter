# import pyTermTk as ptt
import time

import numpy as np
import plotext as plt

from helpers import *
from user import *
from weather_app import *


class TUI:
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
        pass

    def draw(self, weather_forecast: "DailyWeather", temperature, apparent_temperature) -> None:
        plt.clear_terminal()
        location = coords_to_city_name(weather_forecast.latitude, weather_forecast.longitude)
        plt.title(f"Temperuture plot for {location}")
        plt.theme("dark")
        plt.xlabel("Time")
        plt.ylabel("*C")

        time_start = weather_forecast.time
        time_end = weather_forecast.time_end

        x_axis_indices = range(len(temperature))
        x_labels = time_to_ticks(time_start, time_end, weather_forecast.interval)           #

        plt.plot(x_axis_indices, temperature, marker="braille", label="Temperature")
        plt.plot(x_axis_indices, apparent_temperature, marker="braille", label="Apparent temperature")
        plt.xticks(ticks=x_axis_indices, labels=x_labels, xside=2)
        plt.show()

    def draw_subplot():
        pass


if __name__ == "__main__":
    TUI().draw_plot()
