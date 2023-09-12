import os
import xarray as xr
import matplotlib.pyplot as plt
import pandas as pd
import datetime

from cht.tide.tide_model import TideModel

path = "c:\\work\\delftdashboard\\data\\tidemodels\\fes2014_extrap"

tm = TideModel("fes2014", path)

lon = [-55.0, -40.0]
lat = [32.0, 33.0]

components = tm.get_components_at_points(lon, lat, component_names="all", format="dataframe")

t0 = datetime.datetime(2020, 5, 17)
t1 = datetime.datetime(2020, 5, 23)
dt = datetime.timedelta(minutes=10)
df = tm.get_timeseries(lon[0], lat[0], start=t0, end=t1, freq=dt, component_names=["M2"])

fig, axs = plt.subplots(figsize=(12, 4))
df["water_level"].plot()
plt.show()

pass