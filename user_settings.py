from dataclasses import dataclass
import matplotlib


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
    
    # def check_for

if __name__ == "__main__":
    pass
