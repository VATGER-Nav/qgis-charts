from coords import parse_es_coords
from pathlib import Path
from shapely import LinearRing, Polygon
import re
import geopandas as gpd
from hashlib import sha1

class Sectors:
    gdf = gpd.GeoDataFrame()
    __sectors = {}


    def __init__(self, source_dir: Path):
        self.source_dir = source_dir


    def parse(self) -> None:
        re_pattern = r"^(\w{4})·([^·]*)·(\d{3})·(\d{3})\s*(\S*) (\S*) (\S*) (\S*)$"

        with self.source_dir.open(mode="r", encoding="utf-8") as f:
            for line in f:
                match = re.search(re_pattern, line.strip())


                if match:
                    fir = match[1]
                    desig = match[2]
                    lvl_lower = int(match[3])
                    lvl_upper = int(match[4])
                    lvl_band = f"{lvl_lower}-{lvl_upper}"

                    if fir not in self.__sectors:
                        self.__sectors[fir] = {}

                    if desig not in self.__sectors[fir]:
                        self.__sectors[fir][desig] = {}

                    if lvl_band not in self.__sectors[fir][desig]:
                        self.__sectors[fir][desig][lvl_band] = {
                            "geometry": [],
                            "level_band": (lvl_lower, lvl_upper)
                        }

                    self.__sectors[fir][desig][lvl_band]["geometry"].append(
                        parse_es_coords(match[5], match[6])
                    )
        
        self.__to_geodataframe()


    def __to_geodataframe(self) -> None:
        data = []

        for fir in self.__sectors:
            for desig in self.__sectors[fir]:
                for lvl_band, sector in self.__sectors[fir][desig].items():
                    hash_obj = f"{desig}/{lvl_band}"
                    data.append({
                        "id": sha1(bytes(hash_obj, "utf-8")).hexdigest(),
                        "name": desig,
                        "level_lower": sector["level_band"][0],
                        "level_upper": sector["level_band"][1],
                        "geometry": Polygon(LinearRing(sector["geometry"]))
                    })    

        self.gdf = gpd.GeoDataFrame(data, crs="EPSG:4326")