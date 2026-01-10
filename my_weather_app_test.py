import pytest

import geocoder
from api_session import WeatherForecast, CurrentWeatherForecast
from my_weather_app import MyWeatherApp, Plotter, make_data_payload


def test_get_any_weather_with_coords():
    app = MyWeatherApp()
    app.get_current_weather((52.2297, 21.0122))  # Warszawa coords
    app.get_current_weather("Warszawa")

    with pytest.raises(TypeError):
        app.get_current_weather(52.2297, 21.0122, 31.3462, -121.0366)  # with extra params
    with pytest.raises(TypeError):
        app.get_current_weather("Warszawa", "Polska")

def test_get_current_weather():
    app = MyWeatherApp()
    weather = app.get_current_weather()
    assert isinstance(weather, CurrentWeatherForecast)
    assert app.current_coords == (weather.latitude, weather.longitude)

def test_cannot_change_last_api_call_coords():
    app = MyWeatherApp()
    app.get_current_weather()
    with pytest.raises(AttributeError):
        app.current_coords = (123, 123)

def test_get_hourly_weather():
    app = MyWeatherApp()
    weather = app.get_hourly_forecast()
    assert app.current_coords == (weather.latitude, weather.longitude)
