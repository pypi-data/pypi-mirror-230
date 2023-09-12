from cht.meteo.meteo import MeteoSource, MeteoGrid
from datetime import datetime
from pyproj import CRS

def download_meteo(path, lon, lat, start_time, end_time):
    
    #Determine to dowload wind and/or rainfall data
    # if self.attrs.template == "Historical_offshore":
    #     if self.attrs.wind.source == "map" and self.attrs.rainfall.source == "map":
    #         params = ["wind","barometric_pressure","precipitation"]
    #     elif self.attrs.wind.source == "map" and self.attrs.rainfall.source != "map":
    #         params = ["wind", "barometric_pressure"]
    #     elif self.attrs.wind.source != "map" and self.attrs.rainfall.source == "map":
    #         params = ["precipitation"]
    # elif self.attrs.template == "Historical_nearshore":
    #     if self.attrs.wind.source == "map" and self.attrs.rainfall.source == "map":
    #         params = ["wind","precipitation"]
    #     elif self.attrs.wind.source == "map" and self.attrs.rainfall.source != "map":
    #         params = ["wind"]
    #     elif self.attrs.wind.source != "map" and self.attrs.rainfall.source == "map":
    #         params = ["precipitation"]         
    
    params = ["wind","barometric_pressure","precipitation"]
    # lon = site.attrs.lon
    # lat = site.attrs.lat  

    #Download the actual datasets
    gfs_source = MeteoSource("gfs_anl_0p50",
                             "gfs_anl_0p50_04",
                             "hindcast",
                             delay=None)

    # Create subset
    name = "gfs_anl_0p50_us_southeast"
    gfs_conus = MeteoGrid(name=name,
                            source=gfs_source,
                            parameters=params,
                            path=path,
                            x_range=[lon - 10, lon + 10],
                            y_range=[lat - 10, lat + 10],
                            crs=CRS.from_epsg(4326))

    # Download and collect data
    t0 = datetime.strptime(start_time, "%Y%m%d %H%M%S")
    t1 = datetime.strptime(end_time, "%Y%m%d %H%M%S")
    time_range = [t0, t1]

    gfs_conus.download(time_range)
    gfs_conus.collect(time_range)

    return gfs_conus

path = r"c:\work\checkouts\git\CoastalHazardsToolkit\src\cht\tropical_cyclone\gfs"
lon = -70.0
lat = 30.0
t0 = "20221001 000000"
t1 = "20221002 000000"

val = download_meteo(path, lon, lat, t0, t1)
pass