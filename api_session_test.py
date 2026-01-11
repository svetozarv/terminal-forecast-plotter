from unittest.mock import MagicMock, patch

import pytest

from api_session import (
    ApiSession,
    CurrentWeatherForecast,
    DailyWeatherForecast,
    HourlyWeatherForecast,
    WeatherForecastFactory,
)
# TODO: separate integration and unit (logic) tests


# mock api (variables -> Current -> response)
@pytest.fixture
def mock_response():
    # mock the specific variable values
    mock_var_temp = MagicMock()
    mock_var_temp.Value.return_value = 25.5
    mock_var_humidity = MagicMock()
    mock_var_humidity.Value.return_value = 60.0

    # mock the `current_weather` object holding these variables
    mock_current = MagicMock()

    # mock the .Variables() calls
    # matching the index order is mandatory
    def variable_side_effect(index):
        if index == 0: return mock_var_temp
        if index == 1: return mock_var_humidity
        return MagicMock(Value=lambda: 0.0)  # default for other values (don't care)

    mock_current.Variables.side_effect = variable_side_effect
    mock_current.Time.return_value = "2026-01-11"

    # mock the top-level Response object
    mock_response = MagicMock()
    mock_response.Current.return_value = mock_current
    mock_response.Latitude.return_value = 52.0
    mock_response.Longitude.return_value = 21.0
    mock_response.Elevation.return_value = 100.0
    mock_response.UtcOffsetSeconds.return_value = 3600
    return mock_response


@patch("api_session.openmeteo_requests.Client")
def test_get_current_weather_parsing(MockClient, mock_response):
    # is data parsed correctlyfrom the API response?
    mock_instance = MockClient.return_value
    mock_instance.weather_api.return_value = [mock_response]

    session = ApiSession(52.0, 21.0)
    weather = session.get_current_weather()

    assert weather.temperature_2m == 25.5
    assert weather.relative_humidity_2m == 60.0
    assert weather.latitude == 52.0
    mock_instance.weather_api.assert_called_once()


@patch("api_session.openmeteo_requests.Client")
def test_caching_mechanism(MockClient, mock_response):
    # calling the API twice for the same location -> one API call
    mock_instance = MockClient.return_value
    mock_instance.weather_api.return_value = [mock_response]

    session = ApiSession(52.0, 21.0)

    session.get_current_weather()   # call
    assert mock_instance.weather_api.call_count == 1

    session.get_current_weather()
    assert mock_instance.weather_api.call_count == 1  # cache hit

    session.get_current_weather(40.0, 10.0)
    assert mock_instance.weather_api.call_count == 2  # call


def test_openmeteo_api_is_up():
    assert ApiSession()._make_api_call(None, None)

def test_check_returning_types():
    session = ApiSession()
    current_weather = session.get_current_weather()
    hourly_forecast = session.get_hourly_forecast()
    daily_forecast = session.get_daily_forecast()
    assert isinstance(current_weather, CurrentWeatherForecast)
    assert isinstance(hourly_forecast, HourlyWeatherForecast)
    assert isinstance(daily_forecast, DailyWeatherForecast)

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
    # Default location should remain Rome
    assert weather_but_different.latitude == pytest.approx(41.8919, rel=0.01)
    assert weather_but_different.longitude == pytest.approx(12.5113, rel=0.01)


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
        current_weather.apparent_temperature = 60.0
