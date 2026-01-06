import pytest

from geocoder import Geocoder


def test_coords_to_city_name():
    geo = Geocoder()
    assert geo.convert_coords_to_city_name(52.2297, 21.0122) == "Warsaw, Poland"
    assert geo.convert_coords_to_city_name(52.2797, 21.0622) == "Warsaw, Poland"
    assert geo.convert_coords_to_city_name(52.1897, 20.9722) == "Warsaw, Poland"
    assert geo.convert_coords_to_city_name(32.2097, 14.0022) != "Warsaw, Poland"

def test_city_name_to_coords():
    geo = Geocoder()
    coords = geo.convert_city_name_to_coords("Warszawa, Polska")
    assert coords[0] == pytest.approx(52.2297, rel=0.01)
    assert coords[1] == pytest.approx(21.0122, rel=0.01)

    coords = geo.convert_city_name_to_coords("Warsaw")
    assert coords[0] == pytest.approx(52.2297, rel=0.01)
    assert coords[1] == pytest.approx(21.0122, rel=0.01)

    coords = geo.convert_city_name_to_coords("Warszawa", "Polska")
    assert coords[0] == pytest.approx(52.2297, rel=0.01)
    assert coords[1] == pytest.approx(21.0122, rel=0.01)

    coords = geo.convert_city_name_to_coords("sdffffsdfsda")
    assert coords is None
