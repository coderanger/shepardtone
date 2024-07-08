import math

import attrs

# Radius of the earth in km.
R = 6371


@attrs.define(frozen=True)
class Point:
    lat: float
    lon: float


@attrs.define(frozen=True)
class Box:
    top_left: Point
    bottom_right: Point


def haversine(theta: float) -> float:
    return math.sin(theta / 2) ** 2


def haversine_distance(a: Point, b: Point):
    """
    Calculate the great circle distance in kilometers between two points
    on the earth (specified in decimal degrees)
    """
    # convert decimal degrees to radians
    lon1, lat1, lon2, lat2 = map(math.radians, [a.lon, a.lat, b.lon, b.lat])

    # haversine formula
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    )
    c = 2 * math.asin(math.sqrt(a))
    return c * R


# THE JS CODE I'M STEALING
# https://math.stackexchange.com/questions/474602/reverse-use-of-haversine-formula
# const deltaLatitude = radius / R
# const deltaLongitude = 2 * Math.asin(Math.sqrt(haversine(radius / R) / (Math.cos(deg2rad(location.latitude)) ** 2)))

# return {
#     deltaLatitude: rad2deg(deltaLatitude),
#     deltaLongitude: rad2deg(deltaLongitude)
# }


def box_from_point_and_distance(center: Point, radius: float) -> Box:
    delta_lat = math.degrees(radius / R)
    delta_lon = math.degrees(
        2
        * math.asin(
            math.sqrt(haversine(radius / R) / (math.cos(math.radians(center.lat)) ** 2))
        )
    )
    return Box(
        top_left=Point(
            lat=center.lat - delta_lat,
            lon=center.lon - delta_lon,
        ),
        bottom_right=Point(
            lat=center.lat + delta_lat,
            lon=center.lon + delta_lon,
        ),
    )
