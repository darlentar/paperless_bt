from pyproj import Transformer


def lamber93_to_gps(x: int, y: int) -> tuple[int, int]:
    lambert = Transformer.from_crs(
        """+proj=lcc +lat_1=49 +lat_2=44 +lat_0=46.5 +lon_0=3
+x_0=700000 +y_0=6600000 +ellps=GRS80 +towgs84=0,0,0,0,0,0,0
+units=m +no_defs""",
        "+proj=longlat +ellps=WGS84 +datum=WGS84 +no_defs",
    )
    return lambert.transform(x, y)
