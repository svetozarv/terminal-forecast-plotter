from geopy import Location
from geopy.exc import GeopyError
from geopy.geocoders import Nominatim

from helpers import coords_to_str


class Geocoder:
    def __init__(self):
        self.geolocator = Nominatim(user_agent="my_geopy_app")
        self.cache = {}

    def coords_to_city_name(self, latitude: float, longitude: float) -> str | None:
        """
        Example: `52.2297, 21.0122` -> `Warszawa, Polska`
        """
        if (latitude, longitude) in self.cache:
            return self.cache[(latitude, longitude)]

        try:
            location = self.geolocator.reverse(f"{latitude}, {longitude}", language="en")
            display_name = location.raw.get("display_name", f"{latitude}, {longitude}")
        except GeopyError as e:  # any GeoCoder exeption
            return f"{latitude}, {longitude}"

        self.cache[(latitude, longitude)] = display_name
        return display_name

    def city_name_to_coords(self, city_name: str, country_name: str = None) -> tuple[float, float] | None:
        if city_name in self.cache:
            return self.cache[city_name]

        try:
            location = self.geolocator.geocode(f"{city_name}, {country_name if country_name else ''}", language="en")
            if location is None: return None
        except GeopyError as e:
            return None
        coords = (float(location.raw["lat"]), float(location.raw["lon"]))
        self.cache[city_name] = coords
        return coords


if __name__ == "__main__":
    geolocator = Nominatim(user_agent="my_geopy_app")
    location = geolocator.geocode("Warszawa", language="en")
    print(location.raw)

    geo = Geocoder()
    a = geo.city_name_to_coords("Warszawa", "Polska")
    print(f"Coodninates: {a}")
    a = geo.city_name_to_coords("Zakopane")
    print(f"Coodninates: {a}")
