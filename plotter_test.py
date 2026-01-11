import pytest
from unittest.mock import MagicMock, call
import datetime as dt
import pandas as pd
from plotter import (
    Plotter,
    generate_labels,
    make_data_payload,
    DailyWeatherForecast,
    HourlyWeatherForecast,
)


def test_generate_labels_logic():
    # Start: 01/01/2023 12:00:00 UTC
    start_ts = 1672574400
    # End: 2 hours later
    end_ts = start_ts + 7200
    # Interval: 1 hour
    interval = 3600

    labels = generate_labels(start_ts, end_ts, interval)

    # expecting 2 labels: 12:00 and 13:00 (inclusive="left" usually drops the exact end time)
    assert len(labels) == 2
    assert labels[0] == "12:00 01/01"
    assert labels[1] == "13:00 01/01"


def test_make_data_payload_daily():
    # create a dummy DailyWeatherForecast (using MagicMock to avoid typing all 15 fields)
    mock_forecast = MagicMock(spec=DailyWeatherForecast)
    mock_forecast.temperature_2m_max = [10, 11]
    mock_forecast.temperature_2m_min = [1, 2]

    params = {"daily": ["temperature_2m_max", "temperature_2m_min"]}
    series, labels = make_data_payload(mock_forecast, params)

    assert len(series) == 2
    assert series[0] == [10, 11]
    assert series[1] == [1, 2]
    assert "temperature_2m_max" in labels


def test_plotter_calls_plotext_correctly():
    # mock plotext
    mock_plt = MagicMock()
    plotter = Plotter(mock_plt)

    # setup dummy
    mock_forecast = MagicMock()
    mock_forecast.time = 0
    mock_forecast.time_end = 3600
    mock_forecast.interval = 3600

    series_data = [[1, 2, 3], [4, 5, 6]]  # two lines to plot
    labels = ["Temp", "Wind"]
    title = "Warsaw Weather"

    plotter.draw(mock_forecast, series_data, labels, title)

    mock_plt.clear_data.assert_called_once()
    mock_plt.clear_figure.assert_called_once()
    mock_plt.title.assert_called_with("Warsaw Weather")
    assert mock_plt.plot.call_count == 2
    mock_plt.show.assert_called_once()
