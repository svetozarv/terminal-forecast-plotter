import logging

from geopy.exc import GeopyError
from geopy.geocoders import Nominatim

logging.getLogger("geocoder")
logging.basicConfig(filename='geocoder.log', level=logging.INFO, filemode="w+")

class Geocoder:
    def __init__(self):
        self.geolocator = Nominatim(user_agent="my_geopy_app")
        self.__cache = {}           # coords -> city_name  |  might as well be a separate class
        self.__cache_reverse = {}   # city_name -> coords

    def convert_coords_to_city_name(self, latitude: float, longitude: float) -> str | None:
        """
        Example: `52.2297, 21.0122` -> `Warszawa, Polska`
        """
        # quick lookup in cache
        if self._is_in_cache(coords=(latitude, longitude)):
            logging.info(f"Cache hit for coords: [{(latitude, longitude)}] -> [{self.__cache[(latitude, longitude)]}]")
            return self.__get_from_cache(coords=(latitude, longitude))

        try:
            location = self.geolocator.reverse(f"{latitude}, {longitude}", language="en", exactly_one=True)
            display_name = location.raw.get("display_name", f"{latitude}, {longitude}")
            logging.info(f"Geocoder made call: {(latitude, longitude)} -> {display_name}")
            address: dict = location.raw.get("address", None)
        except GeopyError as e:  # any GeoCoder exeption
            return f"{latitude}, {longitude}"

        city_name = address.get("city", address.get("town", address.get("village", None)))
        country_name = address.get("country", None)
        display_name = (
            f"{city_name}, {country_name}"
            if city_name and country_name
            else display_name or f"{latitude}, {longitude}"
        )
        self.__save_to_cache(display_name, (latitude, longitude))
        return display_name

    def convert_city_name_to_coords(self, city_name: str, country_name: str = None) -> tuple[float, float] | None:
        """
        Example: `warszawa` -> `52.2297, 21.0122`
        """
        # quick lookup in cache
        if self._is_in_cache(city_name=city_name):
            logging.info(f"Cache hit for coords: [{city_name}] -> [{self.__cache_reverse[city_name]}]")
            return self.__get_from_cache(city_name=city_name)

        try:
            location = self.geolocator.geocode(f"{city_name}, {country_name if country_name else ''}", language="en")
            if location is None: return None
        except GeopyError as e:
            return None
        coords = (float(location.raw["lat"]), float(location.raw["lon"]))
        logging.info(f"Geocoder made call: {city_name} -> {coords}")
        self.__save_to_cache(city_name, coords)
        return coords

    # "protected" method, used in tests
    def _is_in_cache(self, city_name: str = None, coords: tuple[float, float] = None) -> bool:
        """Better use keywords when calling this method."""
        if coords and coords in self.__cache:
            return True
        if city_name and city_name in self.__cache_reverse:
            return True
        return False

    def __save_to_cache(self, city_name: str = None, coords: tuple[float, float] = None) -> None:
        if city_name is None or coords is None:
            raise ValueError("Both city_name and coords must be provided to save to cache.")
        self.__cache[coords] = city_name
        self.__cache_reverse[city_name] = coords

    def __get_from_cache(self, city_name: str = None, coords: tuple[float, float] = None) -> str | tuple[float, float]:
        if city_name:
            return self.__cache_reverse[city_name]
        if coords:
            return self.__cache[coords]


if __name__ == "__main__":
    geolocator = Nominatim(user_agent="my_geopy_app")
    location = geolocator.geocode("Warszawa", language="en")
    print(location.raw)
    location = geolocator.reverse("52.2333742, 21.0711489", language="en")
    print(location.raw)

    geo = Geocoder()
    fizz = geo.convert_city_name_to_coords("Warszawa", "Polska")
    fizz = geo.convert_city_name_to_coords("Warszawa", "Polska")  # cache hit
    fizz = geo.convert_city_name_to_coords("Warsaw", "Poland")
    print(f"Coodninates: {fizz}")
    buzz = geo.convert_city_name_to_coords("Zakopane")
    buzz = geo.convert_city_name_to_coords("zakopane")
    buzz = geo.convert_city_name_to_coords("Zakopane")  # cache hit
    print(f"Coodninates: {buzz}")
