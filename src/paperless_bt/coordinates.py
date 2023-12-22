import math
from typing import Callable, Iterator, TypeVar

from pyproj import Transformer

EARTH_RADIUS = 6371e3


def compute_haversine(
    latitude1: float,
    latitude2: float,
    longitude1: float,
    longitude2: float,
) -> float:
    latitude1 = math.radians(latitude1)
    latitude2 = math.radians(latitude2)
    longitude1 = math.radians(longitude1)
    longitude2 = math.radians(longitude2)
    dlatidue = latitude2 - latitude1
    dlongitude = longitude2 - longitude1
    return (
        2
        * EARTH_RADIUS
        * math.asin(
            math.sqrt(
                (math.sin(dlatidue / 2) ** 2)
                + math.cos(latitude1)
                * math.cos(latitude2)
                * (math.sin(dlongitude / 2) ** 2)
            )
        )
    )


def lamber93_to_gps(x: int, y: int) -> tuple[int, int]:
    lambert = Transformer.from_crs(
        """+proj=lcc +lat_1=49 +lat_2=44 +lat_0=46.5 +lon_0=3
+x_0=700000 +y_0=6600000 +ellps=GRS80 +towgs84=0,0,0,0,0,0,0
+units=m +no_defs""",
        "+proj=longlat +ellps=WGS84 +datum=WGS84 +no_defs",
    )
    return lambert.transform(x, y)


T = TypeVar("T")


def nearest_from(
    target: tuple[float, float],
    choices: Iterator[T],
    choice_coordinates: Callable[[T], tuple[float, float]],
) -> T | None:
    try:
        nearest_choice = next(choices)
    # we had no values in the iterator
    except StopIteration:
        return None
    for choice in choices:
        nearest_choice_coordinates = choice_coordinates(nearest_choice)
        candidate_choice_coordinates = choice_coordinates(choice)
        nearest_to_search = compute_haversine(
            nearest_choice_coordinates[0],
            target[0],
            nearest_choice_coordinates[1],
            target[1],
        )
        candidate_to_search = compute_haversine(
            candidate_choice_coordinates[0],
            target[0],
            candidate_choice_coordinates[1],
            target[1],
        )
        if candidate_to_search < nearest_to_search:
            nearest_choice = choice
    return nearest_choice
