from geopy.exc import GeopyError
from geopy.geocoders import Nominatim
import logging
logging.getLogger(__name__)
logging.basicConfig(filename='geocoder.log', level=logging.INFO)
# from helpers import coords_to_str

class Location:
    def __init__(self, latitude: float = None, longitude: float = None, city_prompt: str = None):
        if (not latitude or not longitude) and not city_prompt:
            raise ValueError("Either latitude and longitude or city_prompt must be provided.")
        self.__lat = latitude if latitude else None
        self.__lon = longitude if longitude else None
        self.__city_name = city_prompt if city_prompt else None
        self.geo = None

    def __init_geo(self):
        if self.geo is None:
            self.geo = Geocoder()

    @property
    def city_name(self) -> str:
        self.__init_geo()
        if self.__city_name:
            return self.__city_name
        self.__city_name = self.geo.convert_coords_to_city_name(self.__lat, self.__lon)
        return self.__city_name

    @city_name.setter
    def city_name(self, city_name: str):
        self.__init_geo()
        self.__city_name = city_name
        self.__lat, self.__lon = self.geo.convert_city_name_to_coords(city_name)

    @property
    def coords(self) -> tuple[float, float]:
        self.__init_geo()
        if self.__lat and self.__lon:
            return (self.__lat, self.__lon)
        self.__lat, self.__lon = self.geo.convert_city_name_to_coords(self.__city_name)
        return (self.__lat, self.__lon)

    @coords.setter
    def coords(self, coords: tuple[float, float]):
        self.__init_geo()
        self.__lat, self.__lon = coords
        self.__city_name = self.geo.convert_coords_to_city_name(self.__lat, self.__lon)

    def to_coords(self) -> tuple[float, float]:
        return (self.coords[0], self.coords[1])

    def print_info(self):
        print(f"Coordinates: {self.__lat}°N {self.__lon}°E")
        # print(f"Elevation: {self.elevation} m asl")
        # print(f"Timezone difference to GMT+0: {self.timezone_diff_utc0}s")


class Geocoder:
    def __init__(self):
        self.geolocator = Nominatim(user_agent="my_geopy_app123")
        self.cache = {}  # coords -> city_name
        self.cache_reverse = {}  # city_name -> coords

    def fill_location_coords(self, location: Location) -> None:
        """ Location must have city_name filled."""
        if self.is_in_cache(city_name=getattr(location, "city_name", None)):
            location.coords = self.cache_reverse[location.city_name]
            return
        location.coords = self.convert_city_name_to_coords(location.city_name)
        self.save_to_cache(location.city_name, location.coords)

    def fill_location_city_name(self, location: Location) -> None:
        """ Location must have coords filled. """
        if self.is_in_cache(coords=location.coords):
            location.city_name = self.cache[location.coords]
            return
        location.city_name = self.convert_coords_to_city_name(location.coords[0], location.coords[1])
        self.save_to_cache(location.city_name, location.coords)

    def is_in_cache(self, city_name: str = None, coords: tuple[float, float] = None) -> bool:
        """Better use keywords when calling this method."""
        if coords and coords in self.cache:
            return True
        if city_name and city_name in self.cache_reverse:
            return True
        return False

    def save_to_cache(self, city_name: str = None, coords: tuple[float, float] = None) -> None:
        if not city_name or not coords:
            raise ValueError("Either city_name or coords must be provided to save to cache.")
        self.cache[coords] = city_name
        self.cache_reverse[city_name] = coords

    def convert_coords_to_city_name(self, latitude: float, longitude: float) -> str | None:
        """
        Example: `52.2297, 21.0122` -> `Warszawa, Polska`
        """
        if (latitude, longitude) in self.cache:
            logging.info(f"Cache hit for coords: {self.cache[(latitude, longitude)]}, {(latitude, longitude)}")
            return self.cache[(latitude, longitude)]

        try:
            location = self.geolocator.reverse(f"{latitude}, {longitude}", language="en")
            logging.info(f"Geocoder made call: {location}")
            display_name = location.raw.get("display_name", f"{latitude}, {longitude}")
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
        self.save_to_cache(display_name, coords := (latitude, longitude))
        return display_name

    def convert_city_name_to_coords(self, city_name: str, country_name: str = None) -> tuple[float, float] | None:
        if city_name in self.cache:
            logging.info(f"Cache hit for coords: {self.cache[city_name]}, {city_name}")
            return self.cache[city_name]

        try:
            location = self.geolocator.geocode(f"{city_name}, {country_name if country_name else ''}", language="en")
            logging.info(f"Geocoder made call: {location}")
            if location is None: return None
        except GeopyError as e:
            return None
        coords = (float(location.raw["lat"]), float(location.raw["lon"]))
        self.save_to_cache(city_name, coords)
        return coords


if __name__ == "__main__":
    geolocator = Nominatim(user_agent="my_geopy_app")
    location = geolocator.geocode("Warszawa", language="en")
    print(location.raw)

    geo = Geocoder()
    fizz = geo.convert_city_name_to_coords("Warszawa", "Polska")
    print(f"Coodninates: {fizz}")
    buzz = geo.convert_city_name_to_coords("Zakopane")
    print(f"Coodninates: {buzz}")
