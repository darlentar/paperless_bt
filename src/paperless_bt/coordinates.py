import math

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
