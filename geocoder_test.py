import pytest

from geocoder import city_name_to_coords, coords_to_city_name


def test_coords_to_city_name():
    assert coords_to_city_name(52.2297, 21.0122) == "Warszawa, Polska"
    assert coords_to_city_name(52.2797, 21.0622) == "Warszawa, Polska"
    assert coords_to_city_name(52.1897, 20.9722) == "Warszawa, Polska"
    assert coords_to_city_name(32.2097, 14.0022) != "Warszawa, Polska"

def test_city_name_to_coords():
    coords = city_name_to_coords("Warszawa, Polska")
    assert coords[0] == pytest.approx(52.2297, rel=0.01)
    assert coords[1] == pytest.approx(21.0122, rel=0.01)

    coords = city_name_to_coords("Warszawa")
    assert coords[0] == pytest.approx(52.2297, rel=0.01)
    assert coords[1] == pytest.approx(21.0122, rel=0.01)

    coords = city_name_to_coords("Warszawa", "Polska")
    assert coords[0] == pytest.approx(52.2297, rel=0.01)
    assert coords[1] == pytest.approx(21.0122, rel=0.01)

    coords = city_name_to_coords("sdffffsdfsda")
    assert coords is None
