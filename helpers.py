import time
import datetime as dt
import pandas as pd
from weather_app import *


def coords_to_str(latitude: float, longitude: float) -> str:
    return f"{latitude}°N {longitude}°E"


def time_to_ticks(start: time, end: time, interval: int, dates=False) -> list:
    """ """
    # -> 12:27 19-12
    data = pd.date_range(
        start=pd.to_datetime(start, unit="s", utc=True),
        end=pd.to_datetime(end, unit="s", utc=True),
        freq=pd.Timedelta(seconds=interval),
        inclusive="left",
    ).to_pydatetime().tolist()
    for i, date in enumerate(data):
        data[i] = dt.datetime.strftime(date, "%H:%M %d/%m")
        if dates:
            data[i] = dt.datetime.strftime(date, "%d/%m/%Y")
    return data


def to_datetime(time: int) -> time:
    """
    Ex. 1766139300 -> 23:00:00
    """
    dt_time = pd.to_datetime(time, unit="s", utc=True)
    # dt_time.strftime
    return dt_time.time()




if __name__ == "__main__":
    api = ApiSession()
    hourly = api.get_hourly_data()
    time_to_ticks(hourly.time, hourly.time_end, hourly.interval)
