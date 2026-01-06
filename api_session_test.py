import pytest
from api_session import ApiSession
# from helpers import *


def test_openmeteo_api_is_up():
    assert ApiSession()._make_api_call(None, None)

def test_change_location():
    session = ApiSession(52.2297, 21.0122)  # Warszawa

    weather = session.get_current_weather()
    assert weather.latitude == pytest.approx(52.2297, rel=0.01)
    assert weather.longitude == pytest.approx(21.0122, rel=0.01)

    session.change_default_location(41.8919, 12.5113)  # Rome
    weather = session.get_current_weather()
    assert weather.latitude == pytest.approx(41.8919, rel=0.01)
    assert weather.longitude == pytest.approx(12.5113, rel=0.01)

    weather = session.get_current_weather(48.8566, 2.3522)  # Paris
    weather_but_different = session.get_current_weather()
    assert weather.latitude == pytest.approx(48.8566, rel=0.01)
    assert weather.longitude == pytest.approx(2.3522, rel=0.01)
    # Default location should remain Rome

def test_cannot_change_location_to_none():
    session = ApiSession(52.2297, 21.0122)  # Warszawa

    with pytest.raises(ValueError):
        session.change_default_location(None, 21.0122)

    with pytest.raises(ValueError):
        session.change_default_location(52.2297, None)

    with pytest.raises(ValueError):
        session.change_default_location(None, None)

def test_cannot_modify_forecast_fields():
    session = ApiSession(52.2297, 21.0122)  # Warszawa
    current_weather = session.get_current_weather()

    with pytest.raises(AttributeError):
        current_weather.temperature_2m = 25.0

    with pytest.raises(AttributeError):
        current_weather.humidity_2m = 60.0