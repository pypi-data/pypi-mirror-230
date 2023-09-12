"""
Example:

import datetime
import cht.observation_stations.observation_stations as obs

coops = obs.source("noaa_coops")
t0 = datetime.datetime(2015, 1, 1)
t1 = datetime.datetime(2015, 1, 10)
df = coops.get_data("9447130", t0, t1)

"""

import datetime
import geopandas as gpd
import shapely
import pandas as pd

class StationSource:
    def __init__(self):
        pass

    def list_stations(self):
        pass

    def get_meta_data(self):
        pass

    def get_data(self):
        pass

    def gdf(self):
        gdf_list = []
        # Loop through points
        for station in self.active_stations:
            name = station["name"]
            x = station["lon"]
            y = station["lat"]
            id = station["id"]
            point = shapely.geometry.Point(x, y)
            d = {"id": id, "name": name, "geometry": point}
            gdf_list.append(d)
        return gpd.GeoDataFrame(gdf_list, crs=4326)

def source(name):
    if name == "ndbc":
        from ._ndbc import Source
        return Source()
    elif name == "noaa_coops":
        from ._noaa_coops import Source
        return Source()
