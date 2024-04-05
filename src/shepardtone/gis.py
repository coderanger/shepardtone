import math

import attrs

# Radius of the earth in km
R = 6371


@attrs.define
class Point:
    lat: float
    lon: float


@attrs.define
class Box:
    top_left: Point
    bottom_right: Point


def haversine(theta: float) -> float:
    return math.sin(theta / 2) ** 2


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
