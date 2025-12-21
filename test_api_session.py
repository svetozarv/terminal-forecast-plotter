from api_session import *
from helpers import *


def test_coords_to_city_name():
    assert coords_to_city_name(52.2297, 21.0122) == "Warszawa, Polska"

def test_openmeteo_api_up():
    assert ApiSession()._make_api_call(None, None)
