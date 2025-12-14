import time
from dataclasses import dataclass

# https://open-meteo.com/en/docs
# 1. first version will be using terminal to communicate with user
# 2. settings will be saved to a file (with login and authentication?)
# 3. while executing a program, user's inputs will be parsed using input()

class WeatherApp:
    pass


class WeatherApp:
    def __init__(self):
        pass

    def _get_data_from_api(self, latitude, longitude, elevation, timezone, start_date, end_date):
        """
        a city/region or coordinates must be provided
        """
        pass

    

    def create_alert(self):
        """
        Save alert data to file (or internal data structure but saved on app close via del?)
        """
        pass
     

class TUI:
    def show_weather_info(self):
        """
        Output to the terminal
        """
        pass

    def create_alert_message(self):
        """
        Based on saved alerts, output a message in console
        """
        pass


@dataclass
class UserSettings:
    city: str
    alerts = []

    def save_alert(self):
        pass

    def save_prompt(self):
        pass

@dataclass
class Alert:
    """
    Alerts are mapped to cities
    """

    city: str
