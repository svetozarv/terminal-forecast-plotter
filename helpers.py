import datetime as dt
import time
from functools import singledispatch

import pandas as pd
from geopy import Location
from geopy.exc import GeopyError
from geopy.geocoders import Nominatim
from numpy import ndarray

from api_session import *


# visitor/adapter for plotter
@singledispatch
def make_data_payload(weather_forecast: DailyWeather):
    pass

# @make_data_payload.register()
# def _(weather_forecast: HourlyWeather):
#     pass

def coords_to_city_name(latitude: float, longitude: float) -> str:
    """
    `52.2297, 21.0122` -> `Warszawa, Polska`
    """
    try:
        geolocator = Nominatim(user_agent="my_geopy_app")
        location = geolocator.reverse(str(latitude) + "," + str(longitude))
        address: dict = location.raw['address']
    except GeopyError as e:     # any GeoCoder exeption
        return coords_to_str(latitude, longitude)
    return f"{address['city']}, {address['country']}"


def city_name_to_coords(city_name: str) -> tuple[float, float]:
    raise NotImplementedError()     # TODO


def datetime_to_labels(start: time, end: time, interval: int, dates=False) -> list:
    """
    `2025-12-25 18:00:00+00:00` -> `12:00 19/12`
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


def to_datetime(time: int) -> time:
    """
    Ex. 1766139300 -> 23:00:00
    """
    dt_time = pd.to_datetime(time, unit="s", utc=True)
    # dt_time.strftime
    return dt_time.time()


def coords_to_str(latitude: float, longitude: float) -> str:
    return f"{latitude}°N {longitude}°E"


if __name__ == "__main__":
    api = ApiSession()
    hourly = api.get_hourly_data()
    datetime_to_labels(hourly.time, hourly.time_end, hourly.interval)
