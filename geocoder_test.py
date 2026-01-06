import pytest

from geocoder import Geocoder, Location


def test_location_internal_state_stability():
    loc = Location(city_prompt="Warsaw, Poland")
    loc.coords = (41.8919, 12.5113) # Rome, Italy
    assert loc.city_name == "Rome, Italy"

    loc.city_name = "Los Angeles, USA"
    lat, lon = loc.coords
    assert lat == pytest.approx(34.0522, rel=0.0001)
    assert lon == pytest.approx(-118.2437, rel=0.0001)


def test_location_cache():
    geo = Geocoder()
    loc1 = Location(city_prompt="Warsaw, Poland")
    geo.fill_location_coords(loc1)
    assert geo.is_in_cache(loc1.city_name) is True
    assert loc1.coords[0] == pytest.approx(52.2297, rel=0.01)
    assert loc1.coords[1] == pytest.approx(21.0122, rel=0.01)

    loc2 = Location(latitude=52.2297, longitude=21.0122)
    geo.fill_location_city_name(loc2)
    assert geo.is_in_cache(coords=loc2.coords) is True
    assert loc2.city_name == "Warsaw, Poland"

def test_location_to_coords():
    loc = Location(city_prompt="Warsaw, Poland")
    lat, lon = loc.to_coords()
    assert lat == pytest.approx(52.2297, rel=0.01)
    assert lon == pytest.approx(21.0122, rel=0.01)

    loc = Location(latitude=34.0522, longitude=-118.2437)
    lat, lon = loc.to_coords()
    assert lat == pytest.approx(34.0522, rel=0.0001)
    assert lon == pytest.approx(-118.2437, rel=0.0001)

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
    assert coords == (52.2297, 21.0122)     # the test is not consistent
