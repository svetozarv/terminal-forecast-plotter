from user_settings import *


def test_save_city_to_favourites():
    dbh = DbHandler()
    dbh.save_city_to_favourties("Warszawa")
    assert dbh.get_favourites()[0] == "Warszawa"

def test_save_alert():
    dbh = DbHandler()
    dbh.create_temperature_alert("Warszawa", -8, 30)
    assert dbh.get_alert("Warszawa") == (-8, 30)

def test_select_from_empty_db():
    dbh = DbHandler()
    dbh.erase()   # need to make the db empty first
    assert dbh.get_favourites() == []
