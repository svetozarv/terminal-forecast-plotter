from dataclasses import dataclass
from db_handler import Favourites, Alerts, DATABASE_FILENAME
from peewee import *

class DbHandler:
    db = SqliteDatabase(DATABASE_FILENAME)

    def __init__(self):
        self.db.connect()

    def save_city_to_favourties(self, city_name: str) -> bool:
        if city_name in self.get_favourites():
            return False
        city = Favourites(city_name=city_name)
        status = city.save()
        return True

    def create_temperature_alert(self, city_name: str, min_temp: float, max_temp: float = None) -> bool:
        if self.get_alert(city_name):
            return False
        alert = Alerts(city_name=city_name, min_temp_alert=min_temp, max_temp_alert=max_temp)
        status = alert.save()
        return True

    def get_alert(self, city_name: str) -> tuple[float, float] | None:
        alert = Alerts.get_or_none(Alerts.city_name == city_name)
        if not alert: return None
        return alert.min_temp_alert, alert.max_temp_alert

    def get_favourites(self) -> list[str]:
        cities = list(map(lambda favourite: favourite.city_name, Favourites.select()))
        return cities

    def erase(self):
        for query in Alerts.select():
            query.delete_instance()
        for query in Favourites.select():
            query.delete_instance()

    def __del__(self):
        # Have to close the connection and this is one way of doing it (through __del__)
        self.db.close()

# TODO: Consider the following desing:
# Favourite("Warszawa").save()
# Alert("Warszawa", ...).save()
# TemperatureAlert("Warszawa", -5, 30).save()
# WindSpeedAlert("Warszawa", 25).save()
# ???

if __name__ == "__main__":
    pass
