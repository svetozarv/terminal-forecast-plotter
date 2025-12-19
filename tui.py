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
        self.hourly_weather = self.api.get_hourly_data()

    def ask_for_weather(self):
        pass

    def show_weather_info(self):
        """
        Output to the terminal
        """
        pass

    def draw_plot(self):
        plt.clear_terminal()
        plt.title(f"Temperuture plot for {coords_to_str(self.hourly_weather.latitude, self.hourly_weather.longitude)}")
        plt.theme("dark")
        temperature = self.hourly_weather.temperature_2m
        apparent_temperature = self.hourly_weather.apparent_temperature
        time = self.hourly_weather.time
        time_end = self.hourly_weather.time_end
        plt.xlabel("Time")
        ticks = time_to_ticks(time, time_end, self.hourly_weather.interval, dates=True)
        # labels = [i for i in range()]
        # plt.xticks(ticks=ticks, labels=labels)
        # keys = 
        # values = 
        plt.plot(ticks, temperature, marker="braille", label="temperature", )
        plt.plot(apparent_temperature, marker="braille", label="apparent_temperature")
        plt.show()
        print(plt.plot.__doc__)

    def create_alert_message(self):
        """
        Based on saved alerts, output a message in console
        """
        pass


class Plotter:
    def __init__(self):
        pass

    def draw(self):
        pass

if __name__ == "__main__":
    TUI().draw_plot()
