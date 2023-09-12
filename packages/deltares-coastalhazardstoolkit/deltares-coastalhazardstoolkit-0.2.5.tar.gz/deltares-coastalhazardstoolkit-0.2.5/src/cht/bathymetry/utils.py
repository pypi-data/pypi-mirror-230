# -*- coding: utf-8 -*-
"""
Created on Wed Sep 21 13:48:55 2022

@author: ormondt
"""
import matplotlib.pyplot as plt
import geopandas as gpd
import shapely
from pyproj import Transformer

def get_isobaths(x, y, z, zc, crs):
   # Get depth contour at zc
   # Returns gdf with linestrings
   cnt = plt.contour(x, y, z, [zc])
   gdf_list = []
   for item in cnt.collections:
      for i in item.get_paths():
         v = i.vertices
         xcnt = v[:, 0]
         ycnt = v[:, 1]
         points = [(x,y) for x,y in zip(xcnt.ravel(), ycnt.ravel())]                
         line = shapely.geometry.LineString(points)
         d = {"geometry": line}
         gdf_list.append(d)
   if gdf_list:
      return gpd.GeoDataFrame(gdf_list, crs=crs)   
   else:
      return None

def add_buffer(gdf_in, buffer=0.0, simplify=0.0):
   # Get polygons around linestrings with buffer
   transformer1 = Transformer.from_crs(gdf_in.crs, 3857, always_xy=True)
   transformer2 = Transformer.from_crs(3857, gdf_in.crs, always_xy=True)
   gdf_list = []
   # Loop through geometries
   for j, feature in gdf_in.iterrows():
      line = shapely.ops.transform(transformer1.transform, feature.geometry)
      polygon = line.buffer(buffer)
      polygon = shapely.ops.transform(transformer2.transform, polygon)
      polygon = shapely.simplify(polygon, 0.01)
      gdf_list.append({"geometry": polygon})
   return gpd.GeoDataFrame(gdf_list, crs=gdf_in.crs)   

# def gdf2list(gdf_in):
#    gdf_out = []
#    for feature in gdf.iterrows():
#       gdf_out.append(GeoDataFrame.from_features([feature]))
#    return gdf_out
