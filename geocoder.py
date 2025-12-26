from geopy import Location
from geopy.exc import GeopyError
from geopy.geocoders import Nominatim

from helpers import coords_to_str, datetime_to_labels


def coords_to_city_name(latitude: float, longitude: float) -> str | None:
    """
    `52.2297, 21.0122` -> `Warszawa, Polska`
    """
    try:
        geolocator = Nominatim(user_agent="my_geopy_app")
        location = geolocator.reverse(str(latitude) + "," + str(longitude), language="en")
        address: dict = location.raw["address"]
        if address is None: return
    except (GeopyError, KeyError) as e:  # any GeoCoder exeption
        return
    return f"{address.get('city') or address.get('town') or ''}, {address.get('country')}"


def city_name_to_coords(city_name: str, country_name: str = None) -> tuple[float, float] | None:
    try:
        geolocator = Nominatim(user_agent="my_geopy_app")
        location = geolocator.geocode(f"{city_name}, {country_name if country_name else ''}", language="en")
        if location is None: return
    except GeopyError as e:
        return
    return (float(location.raw["lat"]), float(location.raw["lon"]))


if __name__ == "__main__":
    a = city_name_to_coords("Warszawa", "Polska")
    print(a)
