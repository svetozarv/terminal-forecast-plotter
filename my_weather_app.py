import argparse
import time

import numpy as np
import plotext
from numpy import ndarray
from functools import singledispatch

from api_session import ApiSession, DailyWeather, HourlyWeather
from helpers import coords_to_city_name, datetime_to_labels


# TODO: Create interfaces for future extension??
class MyWeatherApp:
    """
    All the logic will be listed here
    """
    def __init__(self):
        self.api = ApiSession()
        # self.plotter = Plotter(plt)

    @property
    def current_forecast(self):
        return self.api.get_current_weather()

    @property
    def hourly_forecast(self):
        return self.api.get_hourly_data()

    @property
    def daily_forecast(self):
        return self.api.get_daily_data()

    def draw_plot(self, plt: plotext):
        weather_forecast = self.hourly_forecast
        location = coords_to_city_name(weather_forecast.latitude, weather_forecast.longitude)

        # TODO: introspection?? loop through fields of weather_forecast and make plot for each of them??
        series = make_data_payload(weather_forecast)
        labels = ["temperature", "apparent_temperature"]
        
        self.plotter = Plotter(plt)
        self.plotter.draw(weather_forecast, series, labels, location)

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
            x_labels = datetime_to_labels(weather_forecast.time, weather_forecast.time_end, weather_forecast.interval)
            x_axis_indices = range(len(single_series))
            plt.plot(x_axis_indices, single_series, marker="braille", label=label)
            plt.xticks(ticks=x_axis_indices, labels=x_labels)
        plt.show()


# adapter for plotter
@singledispatch
def make_data_payload(weather_forecast: DailyWeather) -> list[ndarray]:
    series = []
    series.append(getattr(weather_forecast, "temperature_2m_max", None))
    series.append(getattr(weather_forecast, "temperature_2m_min", None))
    series.append(getattr(weather_forecast, "apparent_temperature_max", None))
    series.append(getattr(weather_forecast, "apparent_temperature_min", None))
    series.append(getattr(weather_forecast, "sunrise", None))
    series.append(getattr(weather_forecast, "sunset", None))
    series.append(getattr(weather_forecast, "daylight_duration", None))
    series.append(getattr(weather_forecast, "precipitation_hours", None))
    series.append(getattr(weather_forecast, "precipitation_sum", None))
    # TODO: labels = [params["daily"]]
    return series

@make_data_payload.register(HourlyWeather)
def _(weather_forecast: HourlyWeather) -> list[ndarray]:
    series = []
    # for label in labels:
    #    series.append(getattr(weather_forecast, label, None))
    series.append(getattr(weather_forecast, "temperature_2m", None))
    series.append(getattr(weather_forecast, "apparent_temperature", None))
    series.append(getattr(weather_forecast, "relative_humidity_2m", None))
    # TODO: labels = [params["horly"]]
    return series

if __name__ == "__main__":
    MyWeatherApp().draw_plot()
