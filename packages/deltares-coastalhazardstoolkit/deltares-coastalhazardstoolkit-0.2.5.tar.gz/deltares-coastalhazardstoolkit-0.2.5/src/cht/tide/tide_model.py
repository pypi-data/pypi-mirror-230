import importlib
import numpy as np
import xarray as xr
import pandas as pd

from cht.tide.predict import predict

class TideModel:
    def __init__(self, name, path):
        self.name = name
        self.path = path

    def list_components(self):
        pass    

    def get_components_at_points(self, lon, lat, component_names="all", format="xarray"):        

        # Returns list with DataFrames with tidal components

        if isinstance(lon, float):
            lon = [lon]
            lat = [lat]
        for ilon, long in enumerate(lon):
            if long<0.0:
                lon[ilon] = lon[ilon] + 360.0    
        npoints = len(lon)

        lon_lim = [min(lon), max(lon)]        
        lat_lim = [min(lat), max(lat)]        

        # Import 3D matrix with Real and Imag components 
        module = importlib.import_module(self.name)
        ds = module.get_components(self.path, lon_lim, lat_lim, component_names)

        # First interpolate Re and Im components to points
        da_lon = xr.DataArray(lon, dims="points")
        da_lat = xr.DataArray(lat, dims="points")
        hre = ds["hRe"].interp(lon=da_lon, lat=da_lat)
        him = ds["hIm"].interp(lon=da_lon, lat=da_lat)
        amp = np.sqrt(hre**2 + him**2)
        phi = np.arctan2(him, hre)
        phi = 180 * phi / np.pi 
        phi = xr.where(phi<0.0, phi + 360.0, phi)

        if format[0].lower() == "x":

            # XArray

            ds2 = xr.Dataset()
            ds2["amplitude"] = amp
            ds2["phase"]     = phi
            return ds2

        else:

            # Pandas DataFrame

            component_names = amp["component"].values

            component_sets = []
            for ipoint in range(npoints):
                dict = {'component': component_names,
                        'amplitude': [0.0] * len(component_names),
                        'phase': [0.0] * len(component_names)
                }
                component_sets.append(pd.DataFrame(dict).set_index("component"))

            for icomp, component in enumerate(component_names):
                for ipoint in range(npoints):
                    component_sets[ipoint].loc[component, "amplitude"] = amp.values[icomp, ipoint]
                    component_sets[ipoint].loc[component, "phase"]     = phi.values[icomp, ipoint]

            return component_sets

    def get_timeseries(self, lon, lat, start=None, end=None, freq=None, times=None, component_names="all"):
        if not times:
            if not freq:
                freq = datetime.timedelta(minutes=10)
            times = pd.date_range(start=start, end=end, freq=freq)
        # Time is pandas daterange
        components = self.get_components_at_points(lon, lat, component_names=component_names, format="dataframe")
        df = predict(components[0], times=times)               
        return df

# cmp = "SSA"
# file_name = os.path.join(path, cmp + ".nc")

# xlim = [-80.0 + 360.0, -50.0 + 360.0]
# ylim = [20.0, 50.0]

# with xr.open_dataset(file_name) as ds:

#     subset = ds.sel(lat=slice(ylim[0], ylim[1]),
#                     lon=slice(xlim[0], xlim[1]))
#     amp = subset["amplitude"]
#     phi = subset["phase"]
# #    ax = plt.axes()
#     amp.plot()
#     plt.show()
#     pass

