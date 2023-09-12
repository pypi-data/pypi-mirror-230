import os
import xarray as xr
import pandas as pd
import numpy as np

def get_components(path, lon_lim, lat_lim, requested_names):

    # Return xarray dataset with x, y, HRe, HIm

    available_component_names = ["M2", "S2", "N2", "K2", "K1", "O1", "P1", "Q1", "SA", "SSA"]
    main_component_names      = ['M2','S2','N2','K2','K1','O1','P1','Q1','MF','MM','M4','MS4','MN4']

    if isinstance(requested_names, list):
        component_names = requested_names
    elif requested_names=="all":
        component_names = available_component_names
    elif requested_names=="main":
        component_names = main_component_names

    if lon_lim[0]<0.0:
        lon_lim[0] = lon_lim[0] + 360.0    
    if lon_lim[1]<0.0:
        lon_lim[1] = lon_lim[1] + 360.0    

    # Get lon/lat from m2
    file_name = os.path.join(path, "m2.nc")
    with xr.open_dataset(file_name) as ds:
        lon = ds["lon"].values[:]
        lat = ds["lat"].values[:]

    i0 = np.where(lat<lat_lim[0])[0][-1]
    i1 = np.where(lat>lat_lim[1])[0][0] + 1
    j0 = np.where(lon<lon_lim[0])[0][-1]
    j1 = np.where(lon>lon_lim[1])[0][0] + 1

    lats = lat[i0:i1]
    lons = lon[j0:j1]
    
    ncomps = len(component_names)

    hre = xr.DataArray(np.zeros((ncomps, len(lats), len(lons)), dtype=float), coords=[component_names, lats, lons], dims=["component", "lat", "lon"])
    him = xr.DataArray(np.zeros((ncomps, len(lats), len(lons)), dtype=float), coords=[component_names, lats, lons], dims=["component", "lat", "lon"])

    # Create xarray with all components

    for icomp, component in enumerate(component_names):

        file_name = os.path.join(path, component + ".nc")

        with xr.open_dataset(file_name) as ds:
            amp = 0.01 * ds["amplitude"].values[i0:i1, j0:j1].astype(float)
            phi = np.pi * ds["phase"].values[i0:i1, j0:j1].astype(float) / 180
            hre[icomp,:,:] = amp * np.cos(phi)
            him[icomp,:,:] = amp * np.sin(phi)

    ds = xr.Dataset()
    ds["hRe"] = hre
    ds["hIm"] = him

    return ds

# def get_components_at_points(path, lon, lat, requested_names):

#     available_component_names = ["M2", "S2", "K1", "O1"]
#     main_component_names      = ["M2", "S2", "K1", "O1"]

#     if isinstance(requested_names, list):
#         component_names = requested_names
#     elif requested_names=="all":
#         component_names = available_component_names
#     elif requested_names=="main":
#         component_names = main_component_names

#     lon = xr.DataArray(lon, dims="z")
#     lat = xr.DataArray(lat, dims="z")

#     npoints = len(lon)

#     component_sets = []

#     for ipoint in range(npoints):
#         dict = {'component': component_names,
#                 'amplitude': [0.0, 0.0, 0.0, 0.0],
#                 'phase': [0.0, 0.0, 0.0, 0.0]
#         }
#         component_sets.append(pd.DataFrame(dict).set_index("component"))

#     for component in component_names:

#         file_name = os.path.join(path, component + ".nc")

#         with xr.open_dataset(file_name) as ds:
#             amp = ds["amplitude"].astype(float).interp(lon=lon, lat=lat)
#             phi = ds["phase"].astype(float).interp(lon=lon, lat=lat)
#             for ipoint in range(npoints):
#                 component_sets[ipoint].loc[component, "amplitude"] = 0.01*amp.values[ipoint]
#                 component_sets[ipoint].loc[component, "phase"]     = phi.values[ipoint]

#     return component_sets
