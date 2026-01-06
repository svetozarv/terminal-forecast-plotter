import pytest
import geocoder

from my_weather_app import MyWeatherApp, Plotter, make_data_payload


def test_cannot_change_last_api_call_coords():
    app = MyWeatherApp()
    app.get_current_weather()
    with pytest.raises(AttributeError):
        app.current_location = (123, 123)

def test_get_hourly_weather():
    app = MyWeatherApp()
    weather = app.get_hourly_forecast()
    assert app.current_location.to_coords() == (weather.latitude, weather.longitude)
