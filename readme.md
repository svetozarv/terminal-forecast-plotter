## What is this?
Terminal app that allows to see a plot of weather forecast for (almost) any place on Earth.

## How to run?
```python3 terminal_user_interface.py```
Of course, you need to install prerequisites first. (Guide will appear here soon.)

## How is implemented?
- `api_session.py` contains `ApiSession` class that implements the methods used to get data: `get_current_weather(lat, lon)`, `get_hourly_data(lat, lon)` and `get_daily_data(lat, lon)`. Latitude and longitude must be provided. These methods return objects of `CurrentWeather`, `HourlyWeather` and `DailyWeather` respectively, that represent the json returned by the [OpenMeteo API](https://open-meteo.com/en/docs).

- `database_orm.py` uses `peewee` to define database model

- `database_storage_manager.py` stores `DatabaseStorageManager` class that is responsible for CRUD operations on the database

- `my_weather_app.py` is the main API, combines `Plotter` and `ApiSession`.

- `plotter` uses [`plotext`](https://github.com/piccolomo/plotext) to draw plots in the terminal.

- `helpers.py` contains generic functions used in project.

- `terminal_user_interface` is a [`textual`](https://github.com/Textualize/textual) app that brings everything together.

- `geocoder.py` – module that contains 2 self explanatory functions: `city_name_to_coords()` and `coords_to_city_name()` Uses [geopy](https://geopy.readthedocs.io/en/stable/)'s [Nominatim](https://geopy.readthedocs.io/en/stable/#nominatim) to geocode coordinates and reverse the process. So called adapter between user who is writing city names and `ApiSession`, which operates exclusively on coordinates.

