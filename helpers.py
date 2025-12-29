# Generic functions used in project
import datetime as dt
import time

import pandas as pd

from api_session import *


def datetime_to_labels(start: time, end: time, interval: int, dates=False) -> list:
    """
    Removes year, timezone and milliseconds info from datetime obj.
    `2025-12-19 12:00:00+00:00` -> `12:00 19/12`
    if dates -> `19/12`
    """
    data = pd.date_range(
        start=pd.to_datetime(start, unit="s", utc=True),
        end=pd.to_datetime(end, unit="s", utc=True),
        freq=pd.Timedelta(seconds=interval),
        inclusive="left",
    ).to_pydatetime().tolist()

    format = "%H:%M %d/%m" if not dates else "%d/%m"

    for i, date in enumerate(data):
        data[i] = dt.datetime.strftime(date, format)
    return data


def coords_to_str(latitude: float, longitude: float) -> str:
    return f"{latitude}°N {longitude}°E"


if __name__ == "__main__":
    api = ApiSession()
    hourly = api.get_hourly_data()
    datetime_to_labels(hourly.time, hourly.time_end, hourly.interval)
