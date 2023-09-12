from typing import Tuple

from cached_property import cached_property

import reverse_geocoder as rg
from haversine import haversine, Unit

HAVERSINE_CACHE = {}


class GPSPoint:
    """
    GPSPoint is an object containing geospatial data in three directions.

    Should be used instead of tuples of (lat, lng) or whatever since
    sometimes libraries expect (lng, lat)
    """

    def __del__(self):
        attrs_to_del = ["reverse_geo", "content_hash"]

        for attr in attrs_to_del:
            try:
                delattr(self, attr)
            except AttributeError:
                pass

    def __init__(self, lat: float, lng: float, elevation=None):
        """

        :param lat:
        :param lng:
        :kwarg elevation: Optional elevation in metres
        """
        self.lat = lat
        self.lng = lng
        self.elevation = elevation

    def __eq__(self, oth):
        return self.lat == oth.lat and self.lng == oth.lng

    @staticmethod
    def parse(obj):
        if isinstance(obj, list):
            return GPSPoint(obj[0], obj[1])

        if isinstance(obj, GPSPoint):
            return obj

        if isinstance(obj, dict):
            return GPSPoint(
                obj["lat"], obj["lng"], elevation=obj.get("elevation", None)
            )

        raise NotImplementedError(f"Can't parse gps from type {type(obj)}")

    def distance_from(self, point) -> float:
        """

        :param point: GPSPoint or tuple of (lat, lng)
        :rtype: float
        :return: Distance between points in metres
        """
        if isinstance(point, GPSPoint):
            point = point.point

        key = hash((self.point, point))
        if key not in HAVERSINE_CACHE:
            HAVERSINE_CACHE[key] = haversine(self.point, point, unit=Unit.METERS)

        return HAVERSINE_CACHE[key]

    def serialize(self) -> dict:
        return {"lat": self.lat, "lng": self.lng, "elevation": self.elevation}

    @cached_property
    def reverse_geo(self):
        # TODO: make a cache for this for "close enough" positions if we end
        # up using this frequently
        data = dict(rg.search((self.lat, self.lng), mode=1)[0])
        del data["lat"]
        del data["lon"]
        data["place_1"] = data.pop("name", None)
        data["place_2"] = data.pop("admin1", None)
        data["place_3"] = data.pop("admin2", None)
        return data

    @cached_property
    def content_hash(self) -> int:
        """
        A content hash that will act as an id for the data, handy for caching
        """
        input_string = f"{self.lat} {self.lng} {self.elevation}"
        encoded_int = 0

        for char in input_string:
            encoded_int = (encoded_int << 8) + ord(char)
            encoded_int %= 1000000000

        return encoded_int

    @property
    def point(self) -> Tuple[float, float]:
        """

        :rtype: tuple
        :return: tuple of (lat, lng)
        """
        return (self.lat, self.lng)

    @property
    def is_populated(self) -> bool:
        """
        Is the gps data populated. Often when there is no satelite
        or starting up this will not be populated.

        Does not consider elevation since it's not important

        :rtype: bool
        """
        return (
            self.lat
            and self.lng
            and isinstance(self.lat, (int, float))
            and isinstance(self.lng, (int, float))
        )
