# -*- coding: utf-8 -*-
"""
Created on Fri Dec  2 13:51:25 2022

@author: maartenvanormondt
"""

from tropical_cyclone import TropicalCyclone
from tropical_cyclone import holland2010, wind_radii_nederhoff
import matplotlib.pyplot as plt
import fiona

# Define a track
tc = TropicalCyclone(name="Rudolph")

# Read a track
fname = r'g:\02_forecasting\03_Ian\01_data\20221111_BTD\DelftDashboard\ian_best_track_ddb_removed_pc.cyc'
tc.from_ddb_cyc(fname)

# Cut low wind speeds
tc.low_wind_speeds_cut_off = float(1)
tc.cut_off_low_wind_speeds()

# Write again (as ddb_cyc)
fname = r'g:\02_forecasting\03_Ian\01_data\20221111_BTD\best_track_Python_4.cyc'
tc.write_track(fname, 'ddb_cyc')
tc.include_rainfall = True

# create spiderweb
fname = r'g:\02_forecasting\03_Ian\01_data\20221111_BTD\best_track4_withrain.spw'
tc.to_spiderweb(fname)

# Show track
tc.track.plot()
plt.show()

# Write out as shapefile
output = r'g:\02_forecasting\03_Ian\01_data\20221111_BTD\best_track.shp'
tc.track.to_file(output)

# and as geojson
output = r'g:\02_forecasting\03_Ian\01_data\20221111_BTD\best_track.json'
tc.track.to_file(output, driver="GeoJSON")

# convert units back and write out as cyc file
tc.convert_units_metric_imperial()
fname = r'g:\02_forecasting\03_Ian\01_data\20221111_BTD\best_track_Python_v5.cyc'
tc.write_track(fname, 'ddb_cyc')


# ## Writing spiderweb
# fname = r'g:\02_forecasting\03_Ian\01_data\20221111_BTD\best_track_Python_v2.spw'
# tc.to_spiderweb(fname)