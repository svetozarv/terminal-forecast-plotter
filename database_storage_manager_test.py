from peewee import SqliteDatabase, Model
from database_storage_manager import DatabaseStorageManager

MOCK_DATABASE_FILENAME = "user_settings_test.db"

# decorator
def initialize_mock_db(func, models_to_be_accessed: list[Model]):
    def deco():
        test_db = SqliteDatabase(':memory:')
        test_db.bind(models_to_be_accessed)
        with test_db:
            test_db.create_tables(models_to_be_accessed)
            func()
    return deco

def test_save_city_to_favourites():
    dbh = DatabaseStorageManager()
    dbh.save_city_to_favourties("Warszawa")
    assert "Warszawa" in dbh.get_favourites()

def test_save_alert():
    dbh = DatabaseStorageManager()
    dbh.create_temperature_alert("Warszawa", -8, 30)
    assert dbh.get_alert("Warszawa") == (-8, 30)

# def test_existing_alert():
#     dbh = DatabaseStorageManager()
#     dbh.create_temperature_alert("Warszawa", -8, 30)
#     dbh.create_temperature_alert("Warszawa", -10, 20)
#     assert dbh.get_alert("Warszawa") == (-10, 20)

def test_select_from_empty_db():
    dbh = DatabaseStorageManager()
    dbh.erase()   # need to make the db empty first
    assert dbh.get_favourites() == []
