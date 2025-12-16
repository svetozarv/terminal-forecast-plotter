from weather_app import *

def test_get_data_from_api():
    app = WeatherApp()
    print("run")
    assert app.get_data_from_api(*cities["London"]).text == 0
