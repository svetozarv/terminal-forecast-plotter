import datetime as dt
from functools import singledispatch

import pandas as pd
import plotext
from numpy import ndarray

from api_session import (
    ApiSession,
    DailyWeatherForecast,
    HourlyWeatherForecast,
    IntervalicWeatherForecast,
)


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
        clear=True
    ):
        """
        Draw a few plots on a single canvas (for instance: both temp and humidity on a single plot).
        len(series) and len(labels) should be equal but don't have to. The shorter one will limit the result.

        :param series_of_data_measurements: Is in fact a list of lists of data measurements, which are properties of
        `weather_forecast`
        :type series_of_data_measurements: list[ndarray]
        :param labels: x axis' labels
        :type labels: list[str]
        :param title: title of the plot
        :type title: str
        :param clear: Whether to clear the plot or draw on 'dirty'
        :type clear: bool
        """
        plt = self.plt
        if clear:
            plt.clear_data()
            plt.clear_figure()
        plt.title(title)
        for single_series, label in zip(series_of_data_measurements, labels):
            x_labels = generate_labels(weather_forecast.time, weather_forecast.time_end, weather_forecast.interval)
            x_axis_indices = range(len(single_series))
            plt.plot(x_axis_indices, single_series, marker="braille", label=label)
            plt.xticks(ticks=x_axis_indices, labels=x_labels)
        plt.show()


# adapter for plotter
@singledispatch
def make_data_payload(weather_forecast: DailyWeatherForecast, params: dict[str]) -> tuple[list[ndarray], list[str]]:
    """
    :param params: is a list of requested from OpenMeteo API data (strings).
    Strings in params must be valid names of `weather_forecast`'s properties.
    """
    # edit the labels list to select the displayed data among requested
    # TODO: add ability to plot all the data, or let user decide
    labels = [
        "temperature_2m_max",
        "temperature_2m_min",
        "apparent_temperature_max",
        "apparent_temperature_min",
    ]
    # labels = params["daily"]
    # take all fields of weather_forecast and make plot for each of them
    series = obj_properties_from_strings(weather_forecast, params["daily"])
    return series, labels


@make_data_payload.register(HourlyWeatherForecast)
def _(weather_forecast: HourlyWeatherForecast, params: dict[str]) -> list[ndarray]:
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


def generate_labels(start_time: int, end_time: int, interval: int, dates_only=False) -> list[str]:
    """
    Splits `start_time - end_time` into intervals and returns a list of strings
    or labels like `12:00 19/12` or, if dates_only -> `19/12`.
    """
    data = pd.date_range(
        start=pd.to_datetime(start_time, unit="s", utc=True),
        end=pd.to_datetime(end_time, unit="s", utc=True),
        freq=pd.Timedelta(seconds=interval),
        inclusive="left",
    ).to_pydatetime().tolist()

    format = "%H:%M %d/%m" if not dates_only else "%d/%m"

    for i, date in enumerate(data):
        data[i] = dt.datetime.strftime(date, format)
    return data


if __name__ == "__main__":
    api = ApiSession()
    wf = api.get_hourly_forecast()
    res = generate_labels(wf.time, wf.time_end, wf.interval)
    print(res)
