# -*- coding: utf-8 -*-
"""
Created on Fri Dec  2 13:51:25 2022

@author: maartenvanormondt
"""

from tropical_cyclone import TropicalCyclone, TropicalCycloneEnsemble
from tropical_cyclone import holland2010, wind_radii_nederhoff
import matplotlib.pyplot as plt
import fiona
import os
from datetime import datetime, timedelta

# Define a track
dir = os.path.dirname(r'd:\Git\CoastalHazardsToolkit\src\cht\tropical_cyclone')
tc = TropicalCyclone(name="Rudolph")

# Read a track
fname = r'g:\02_forecasting\03_Ian\01_data\20221111_BTD\DelftDashboard\ian_best_track_ddb_removed_pc.cyc'
tc.from_ddb_cyc(fname)
tc.account_for_forward_speed()
tc.estimate_missing_values()
tc.include_rainfall = True

# Forecasting
tc2         = TropicalCycloneEnsemble(name="DeMaria_test", TropicalCyclone=tc)
tc2.tstart  = datetime(2022,9,27,19,5,0)
tc2.tend    = datetime(2022,9,30,16,5,0)
tc2.compute_ensemble(10)

# Write out
fname = r'g:\02_forecasting\03_Ian\01_data\20221111_BTD\ensembles_withrain'
tc2.to_shapefile((fname))
tc2.to_spiderweb(fname)
tc2.make_figures(fname)