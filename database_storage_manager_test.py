from database_storage_manager import DatabaseStorageManager


def test_save_city_to_favourites():
    dbh = DatabaseStorageManager()
    dbh.save_city_to_favourties("Warszawa")
    assert "Warszawa" in dbh.get_favourites()

def test_save_alert():
    dbh = DatabaseStorageManager()
    dbh.create_temperature_alert("Warszawa", -8, 30)
    assert dbh.get_alert("Warszawa") == (-8, 30)

def test_select_from_empty_db():
    dbh = DatabaseStorageManager()
    dbh.erase()   # need to make the db empty first
    assert dbh.get_favourites() == []
