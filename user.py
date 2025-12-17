from dataclasses import dataclass
import matplotlib


class WeatherApp:
    def create_alert(self):
        """
        Save alert data to file (or internal data structure but saved on app close via del?)
        """
        pass

    def draw_plot(self):
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
    city: str
    latitude: float
    longitude: float
    coord_offset: float   # offset for which the alert is triggered

class TemperatureAlert(Alert):
    def __init_subclass__(cls):
        return super().__init_subclass__()
    
    def check_for

if __name__ == "__main__":
    pass
