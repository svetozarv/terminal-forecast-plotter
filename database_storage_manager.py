from peewee import *

from database_orm import DATABASE_FILENAME, Alert


class DatabaseStorageManager:
    db = SqliteDatabase(DATABASE_FILENAME)

    def __init__(self, db_filename=DATABASE_FILENAME):
        self.db.connect()

    # def __init__(self, db: SqliteDatabase):
    #     self.db.connect()

    # def __init__(self, storage: AstractStorage):
    #     self.storage.connect()
    #
    # dbm = DatabaseStorageManager(sqlitedatabase)

    def save_city_to_favourties(self, city_name: str) -> bool:
        if city_name in self.get_favourites():
            return
        return Alert(city_name=city_name).save()

    def create_temperature_alert(self, city_name: str, min_temp: float, max_temp: float = None) -> bool:
        alert = Alert(city_name=city_name, min_temp=min_temp, max_temp=max_temp)
        return alert.save()

    def get_alert(self, city_name: str) -> tuple[float, float] | None:
        alert = Alert.get_or_none(Alert.city_name == city_name)
        if not alert: return None
        return alert.min_temp, alert.max_temp

    def get_alerts(self) -> list[tuple[str, float, float]]:
        return list(map(lambda a: (a.city_name, a.min_temp, a.max_temp), Alert.select()))

    def get_favourites(self) -> list[str]:
        return list(map(lambda favourite: favourite.city_name, Alert.select(Alert.city_name)))

    def erase(self):
        for query in Alert.select():
            query.delete_instance()

    def __del__(self):
        # Have to close the connection and this is one way of doing it (through __del__)
        self.db.close()


# TODO: Consider the following design:
# Favourite("Warszawa").save()
# Alert("Warszawa", ...).save()
# TemperatureAlert("Warszawa", -5, 30).save()
# WindSpeedAlert("Warszawa", 25).save()
# ???

if __name__ == "__main__":
    dbm = DatabaseStorageManager()
    dbm.get_alerts()
