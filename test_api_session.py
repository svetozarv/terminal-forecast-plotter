from api_session import ApiSession
# from helpers import *


def test_openmeteo_api_up():
    assert ApiSession()._make_api_call(None, None)
