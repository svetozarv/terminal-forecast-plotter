import pytest
from geocoder import Geocoder
# TODO: separate integration and unit (logic) tests
# mock parsing and caching logic


def test_geo_cache():
    geo = Geocoder()
    coords = geo.convert_city_name_to_coords("Warsaw, Poland")
    assert geo._is_in_cache("Warsaw, Poland") is True
    assert geo._is_in_cache("Warszawa") is False
    assert geo._is_in_cache("warsaw, poland") is False
    assert coords[0] == pytest.approx(52.2297, rel=0.01)
    assert coords[1] == pytest.approx(21.0122, rel=0.01)

    city_name = geo.convert_coords_to_city_name(latitude=52.2297, longitude=21.0122)
    assert geo._is_in_cache(city_name=city_name) is True
    assert city_name == "Warsaw, Poland"


def test_coords_to_city_name():
    geo = Geocoder()
    assert geo.convert_coords_to_city_name(52.2297, 21.0122) == "Warsaw, Poland"
    assert geo.convert_coords_to_city_name(52.2797, 21.0622) == "Warsaw, Poland"
    assert geo.convert_coords_to_city_name(52.1897, 20.9722) == "Warsaw, Poland"
    assert geo.convert_coords_to_city_name(32.2097, 14.0022) != "Warsaw, Poland"


def test_city_name_to_coords():
    geo = Geocoder()

    coords = geo.convert_city_name_to_coords("sdffffsdfsda")
    assert coords is None

    coords = geo.convert_city_name_to_coords("Warszawa, Polska")
    assert coords[0] == pytest.approx(52.2297, rel=0.01)
    assert coords[1] == pytest.approx(21.0122, rel=0.01)

    coords = geo.convert_city_name_to_coords("Warsaw")
    assert coords[0] == pytest.approx(52.2297, rel=0.01)
    assert coords[1] == pytest.approx(21.0122, rel=0.01)

    coords = geo.convert_city_name_to_coords("Warszawa", "Polska")
    assert coords[0] == pytest.approx(52.2297, rel=0.01)
    assert coords[1] == pytest.approx(21.0122, rel=0.01)


def test_reverse_geocoding_ocean_location():
    geo = Geocoder()

    # return "Soul Buoy" or lat lon
    # test that it doesn't crash
    result = geo.convert_coords_to_city_name(0.0, 0.0)
    assert result is not None
    assert isinstance(result, str)


def test_unicode_city_names():
    geo = Geocoder()
    coords = geo.convert_city_name_to_coords("東京")  # 'Tokyo' in kanji
    assert coords is not None
    # Tokyo coords approx: 35.68, 139.76
    assert coords[0] == pytest.approx(35.67, abs=0.1)
    assert coords[1] == pytest.approx(139.75, abs=0.1)


def test_address_parsing_fallback():
    # testing if we get town or village if there is no city
    geo = Geocoder()
    # 'Hallstatt' is a market town in Austria might return 'town' instead of 'city'
    coords = geo.convert_city_name_to_coords("Hallstatt, Austria")
    assert coords is not None

    # Reverse
    name = geo.convert_coords_to_city_name(coords[0], coords[1])
    assert "Austria" in name
