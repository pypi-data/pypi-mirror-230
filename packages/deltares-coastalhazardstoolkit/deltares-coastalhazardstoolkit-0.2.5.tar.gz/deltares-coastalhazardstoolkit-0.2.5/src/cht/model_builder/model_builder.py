# -*- coding: utf-8 -*-
"""

build_beira_model.py

Script to set up large-scale Beira model with Quadtree and subgrid functionality

Let's see if this works ...

Created on Sat Jun 18 09:03:08 2022

@author: ormondt
"""

import os
from shapely.geometry import Polygon

from cht.bathymetry.bathymetry_database import bathymetry_database
from cht.misc.pli_file import read_pli_file
#from cht.misc import xmlkit as xml
from cht.misc.misc_tools import yaml2dict
from cht.misc.misc_tools import dict2yaml

class RefinementPolygon():
    def __init__(self, level, x=None, y=None, polygon=None):
        self.geometry = None
        self.refinement_level = level
        if not polygon:
            if x is None or y is None:
                print("ERROR! No coordinates provide for refinement polygon!")
                return
            else:                
                pts = []
                for ix, xp in enumerate(x):
                    xy = (x[ix], y[ix])            
                    pts.append(xy)
                self.geometry = Polygon(pts)        
        else:        
            self.geometry = polygon        

class MaskPolygon():
    def __init__(self, zmin=-99999.0, zmax=99999.0, x=None, y=None, polygon=None):
        self.geometry = None
        self.zmin = zmin
        self.zmax = zmax
        if not polygon:
            if x is None or y is None:
                print("ERROR! No coordinates provide for quadtree mask polygon!")
                return
            else:                
                pts = []
                for ix, xp in enumerate(x):
                    xy = (x[ix], y[ix])            
                    pts.append(xy)
                self.geometry = Polygon(pts)        
        else:        
            self.geometry = polygon        


class BathymetryDataset():
    def __init__(self,
                 name=None,
                 source=None,
                 zmin=-99999.0,
                 zmax=99999.0,
                 x=None,
                 y=None,
                 z=None,
                 crs=None,
                 offset=0.0,
                 polygon=None):
        # SubgridBathymetryDataset can either be from online source,
        # or a regular matrix
        self.name    = name
        self.source  = source
        self.zmin    = zmin
        self.zmax    = zmax
        self.x       = x
        self.y       = y
        self.z       = z
        self.offset  = offset
        self.polygon = polygon
        self.crs     = crs
        
        if name:
            self.type = "source"
            self.crs = bathymetry_database.get_crs(self.name)
        elif x:
            self.type = "array"
            
            
class BedRoughnessDataset():
    def __init__(self,
                 name=None,
                 source=None,
                 zlevel=0.0,
                 roughness_deep=0.024,
                 roughness_shallow=0.080,
                 x=None,
                 y=None,
                 z=None,
                 crs=None,
                 polygon=None):

        # BedRoughnessDataset can either be from online source,
        # or a regular matrix
        self.name    = name
        self.source  = source
        self.zlevel  = zlevel
        self.roughness_deep    = roughness_deep
        self.roughness_shallow = roughness_shallow
        self.x       = x
        self.y       = y
        self.polygon = polygon
        self.crs     = crs

        if name:
            self.type = "source"
            self.crs = bathymetry_database.get_crs(self.name)
        elif x:
            self.type = "array"
        else:
            self.type = "constant"

class ModelBuilder:
    def __init__(self,
                 file_name=None,
                 model_path=None,
                 data_path=None,
                 tile_path=None,
                 bathymetry_database_path=None):
        
        if not model_path:
            model_path = os.getcwd()
        if not data_path:
            data_path = os.getcwd()
        if not tile_path:
            tile_path = os.getcwd()
            
        self.model_path = model_path      
        self.data_path  = data_path
        self.tile_path  = tile_path
        self.bathymetry_database_path = bathymetry_database_path
        
        # Defaults                
        self.setup_config = {}        
        self.setup_config["input"]                            = {}                         
        self.setup_config["coordinates"]                      = {} 
        self.setup_config["coordinates"]["x0"]                = 0.0
        self.setup_config["coordinates"]["y0"]                = 0.0
        self.setup_config["coordinates"]["dx"]                = 0.1
        self.setup_config["coordinates"]["dx"]                = 0.1
        self.setup_config["coordinates"]["nmax"]              = 10
        self.setup_config["coordinates"]["mmax"]              = 10
        self.setup_config["coordinates"]["rotation"]          = 0.0
        self.setup_config["coordinates"]["crs"]               = "WGS 84"
        self.setup_config["quadtree"]                         = {}
        self.setup_config["quadtree"]["refinement_level"]     = []
        self.setup_config["mask"]                             = {}
        self.setup_config["mask"]["zmin"]                     = -99999.0
        self.setup_config["mask"]["zmax"]                     = 99999.0
        self.setup_config["mask"]["include_polygon"]          = []
        self.setup_config["mask"]["exclude_polygon"]          = []
        self.setup_config["mask"]["open_boundary_polygon"]    = []
        self.setup_config["mask"]["outflow_boundary_polygon"] = []
        # self.setup_config["wave_mask"]                             = {}
        # self.setup_config["wave_mask"]["zmin"]                     = -99999.0
        # self.setup_config["wave_mask"]["zmax"]                     = 99999.0
        # self.setup_config["wave_mask"]["include_polygon"]          = []
        # self.setup_config["wave_mask"]["exclude_polygon"]          = []
        # self.setup_config["wave_mask"]["open_boundary_polygon"]    = []
        self.setup_config["subgrid"]                          = {}
        self.setup_config["subgrid"]["nr_bins"]               = 5
        self.setup_config["subgrid"]["zmin"]                  = -99999.0
        self.setup_config["subgrid"]["max_gradient"]          = 5.0
        self.setup_config["subgrid"]["nr_subgrid_pixels"]     = 20
        self.setup_config["bathymetry"]                       = {}
        self.setup_config["bathymetry"]["dataset"]            = []
        self.setup_config["roughness"]                        = {}
        self.setup_config["roughness"]["dataset"]             = []
        self.setup_config["tiling"]                           = {}
        self.setup_config["tiling"]["zmin"]                   = -99999.0
        self.setup_config["tiling"]["zmax"]                   = 99999.0
        self.setup_config["tiling"]["zoom_range_min"]         = 0
        self.setup_config["tiling"]["zoom_range_max"]         = 10
        
        if file_name:
            self.read(file_name)
            self.prepare()

    def set_missing_config_values(self):

        if "input" not in self.setup_config:
            self.setup_config["input"] = {}
            
        self.setup_config["coordinates"]["mmax"] = int(self.setup_config["coordinates"]["mmax"])
        self.setup_config["coordinates"]["nmax"] = int(self.setup_config["coordinates"]["nmax"])
        
        if "bathymetry" not in self.setup_config:
            self.setup_config["bathymetry"] = {}
            self.setup_config["bathymetry"]["dataset"] = []
        if self.setup_config["bathymetry"]["dataset"]:
            for dataset in self.setup_config["bathymetry"]["dataset"]:
                if "source" not in dataset:
                    dataset["source"] = "delftdashboard"
                if "zmin" not in dataset:
                    dataset["zmin"] = -99999.0
                if "zmax" not in dataset:
                    dataset["zmax"] = 99999.0

        if "roughness" not in self.setup_config:
            self.setup_config["roughness"] = {}
        else:    
            if "dataset" in self.setup_config["roughness"]:
                for dataset in self.setup_config["roughness"]["dataset"]:
                    if "name" not in dataset:
                        dataset["name"] = None
                    if "source" not in dataset:
                        dataset["source"] = None
                    if "zlevel" not in dataset:
                        dataset["zlevel"] = 0.0
                    if "roughness_deep" not in dataset:
                        dataset["roughness_deep"] = 0.024
                    if "roughness_shallow" not in dataset:
                        dataset["roughness_shallow"] = 0.080

        if "mask" not in self.setup_config:
            self.setup_config["mask"] = {}
            self.setup_config["mask"]["zmin"] = -99999.0
            self.setup_config["mask"]["zmax"] = 99999.0
        else:
            if "zmin" not in self.setup_config["mask"]:
                self.setup_config["mask"]["zmin"] = -99999.0
            if "zmax" not in self.setup_config["mask"]:
                self.setup_config["mask"]["zmax"] = 99999.0

        if "include_polygon" not in self.setup_config["mask"]:
            self.setup_config["mask"]["include_polygon"] = []
        if self.setup_config["mask"]["include_polygon"]:
            for polygon in self.setup_config["mask"]["include_polygon"]:
                if "zmin" not in polygon:
                    polygon["zmin"] = -99999.0
                if "zmax" not in polygon:
                    polygon["zmax"] = 99999.0

        if "exclude_polygon" not in self.setup_config["mask"]:
            self.setup_config["mask"]["exclude_polygon"] = []
        if self.setup_config["mask"]["exclude_polygon"]:
            for polygon in self.setup_config["mask"]["exclude_polygon"]:
                if "zmin" not in polygon:
                    polygon["zmin"] = -99999.0
                if "zmax" not in polygon:
                    polygon["zmax"] = 99999.0

        if "open_boundary_polygon" not in self.setup_config["mask"]:
            self.setup_config["mask"]["open_boundary_polygon"] = []
        if self.setup_config["mask"]["open_boundary_polygon"]:
            for polygon in self.setup_config["mask"]["open_boundary_polygon"]:
                if "zmin" not in polygon:
                    polygon["zmin"] = -99999.0
                if "zmax" not in polygon:
                    polygon["zmax"] = 99999.0

        if "outflow_boundary_polygon" not in self.setup_config["mask"]:
            self.setup_config["mask"]["outflow_boundary_polygon"] = []
        if self.setup_config["mask"]["outflow_boundary_polygon"]:
            for polygon in self.setup_config["mask"]["outflow_boundary_polygon"]:
                if "zmin" not in polygon:
                    polygon["zmin"] = -99999.0
                if "zmax" not in polygon:
                    polygon["zmax"] = 99999.0


        if "wave_mask" not in self.setup_config:
            self.setup_config["wave_mask"] = {}
            # self.setup_config["wave_mask"]["zmin"] = -99999.0
            # self.setup_config["wave_mask"]["zmax"] = 99999.0
        else:
            if "zmin" not in self.setup_config["wave_mask"]:
                self.setup_config["wave_mask"]["zmin"] = -99999.0
            if "zmax" not in self.setup_config["wave_mask"]:
                self.setup_config["wave_mask"]["zmax"] = 99999.0

        if self.setup_config["wave_mask"]:
            if "include_polygon" not in self.setup_config["wave_mask"]:
                self.setup_config["wave_mask"]["include_polygon"] = []
            if self.setup_config["wave_mask"]["include_polygon"]:
                for polygon in self.setup_config["wave_mask"]["include_polygon"]:
                    if "zmin" not in polygon:
                        polygon["zmin"] = -99999.0
                    if "zmax" not in polygon:
                        polygon["zmax"] = 99999.0
    
            if "exclude_polygon" not in self.setup_config["wave_mask"]:
                self.setup_config["wave_mask"]["exclude_polygon"] = []
            if self.setup_config["wave_mask"]["exclude_polygon"]:
                for polygon in self.setup_config["wave_mask"]["exclude_polygon"]:
                    if "zmin" not in polygon:
                        polygon["zmin"] = -99999.0
                    if "zmax" not in polygon:
                        polygon["zmax"] = 99999.0
    
            if "open_boundary_polygon" not in self.setup_config["wave_mask"]:
                self.setup_config["wave_mask"]["open_boundary_polygon"] = []
            if self.setup_config["wave_mask"]["open_boundary_polygon"]:
                for polygon in self.setup_config["wave_mask"]["open_boundary_polygon"]:
                    if "zmin" not in polygon:
                        polygon["zmin"] = -99999.0
                    if "zmax" not in polygon:
                        polygon["zmax"] = 99999.0


        if "subgrid" not in self.setup_config:
            self.setup_config["subgrid"] = {}
        else:
            if "nr_bins" not in self.setup_config["subgrid"]:                
                self.setup_config["subgrid"]["nr_bins"]               = 5
            if "zmin" not in self.setup_config["subgrid"]:                
                self.setup_config["subgrid"]["zmin"]                  = -99999.0
            if "max_gradient" not in self.setup_config["subgrid"]:                
                self.setup_config["subgrid"]["max_gradient"]          = 5.0
            if "nr_subgrid_pixels" not in self.setup_config["subgrid"]:                
                self.setup_config["subgrid"]["nr_subgrid_pixels"]     = 20
            self.setup_config["subgrid"]["nr_bins"] = int(self.setup_config["subgrid"]["nr_bins"])
            self.setup_config["subgrid"]["nr_subgrid_pixels"] = int(self.setup_config["subgrid"]["nr_subgrid_pixels"])
                
        if "quadtree" not in self.setup_config:
            self.setup_config["quadtree"]                         = {}
        else:
            if "refinement_level" not in self.setup_config["quadtree"]:
                self.setup_config["quadtree"]["refinement_level"] = []
            for lev in self.setup_config["quadtree"]["refinement_level"]:
                lev["level"] = int(lev["level"])

        if "tiling" not in self.setup_config:
            self.setup_config["tiling"] = {}
        else:    
            if "zmin" not in self.setup_config["tiling"]:
                self.setup_config["tiling"]["zmin"] = -99999.0
            if "zmax" not in self.setup_config["tiling"]:
                self.setup_config["tiling"]["zmax"] =  99999.0
            if "zoom_range_min" not in self.setup_config["tiling"]:
                self.setup_config["tiling"]["zoom_range_min"] = 0
            if "zoom_range_max" not in self.setup_config["tiling"]:
                self.setup_config["tiling"]["zoom_range_max"] = 10
                
    def read(self, file_name):
        # Read config yml
        self.setup_config = yaml2dict(file_name)
        
    def save(self, file_name):
        from copy import deepcopy
        setup_config = deepcopy(self.setup_config)
        # Write config yml
        if len(self.setup_config["input"])==0:
            setup_config.pop("input")
        if len(self.setup_config["wave_mask"])==0:
            setup_config.pop("wave_mask")
        if len(self.setup_config["roughness"])==0:
            setup_config.pop("roughness")
        if len(self.setup_config["tiling"])==0:
            setup_config.pop("tiling")
        if len(self.setup_config["subgrid"])==0:
            setup_config.pop("subgrid")
        if len(self.setup_config["quadtree"])==0:
            setup_config.pop("quadtree")
        dict2yaml(file_name, setup_config)
        del setup_config
    
    def prepare(self):
        # Sets missing config values, initialize bathy database and load in polygons 
        
        self.set_missing_config_values()
    
        # Initialize bathymetry database
        bathymetry_database.initialize(self.bathymetry_database_path)
            
        # Refinement polygons
        self.refinement_polygons = []
        if "refinement_level" in self.setup_config["quadtree"]:
            for level in self.setup_config["quadtree"]["refinement_level"]:
                for file in level["file_list"]:
                    polygons = read_pli_file(os.path.join(self.data_path, file))
                    for p in polygons:
                        self.refinement_polygons.append(RefinementPolygon(level["level"],
                                                                          x=p.x,
                                                                          y=p.y))
            
        # Mask polygons        
        self.include_polygons = []
        for polygon in self.setup_config["mask"]["include_polygon"]:
            polygons = read_pli_file(os.path.join(self.data_path, polygon["file_name"]))
            # Polygon file may include multiple polygons
            for p in polygons:
                self.include_polygons.append(MaskPolygon(x=p.x,
                                                         y=p.y,
                                                         zmin=polygon["zmin"],
                                                         zmax=polygon["zmax"]))            
    
        self.exclude_polygons = []
        for polygon in self.setup_config["mask"]["exclude_polygon"]:
            polygons = read_pli_file(os.path.join(self.data_path, polygon["file_name"]))
            # Polygon file may include multiple polygons
            for p in polygons:
                self.exclude_polygons.append(MaskPolygon(x=p.x,
                                                         y=p.y,
                                                         zmin=polygon["zmin"],
                                                         zmax=polygon["zmax"]))            
        self.open_boundary_polygons = []
        for polygon in self.setup_config["mask"]["open_boundary_polygon"]:
            polygons = read_pli_file(os.path.join(self.data_path, polygon["file_name"]))
            # Polygon file may include multiple polygons
            for p in polygons:
                self.open_boundary_polygons.append(MaskPolygon(x=p.x,
                                                   y=p.y,
                                                   zmin=polygon["zmin"],
                                                   zmax=polygon["zmax"]))            
    
        self.outflow_boundary_polygons = []
        for polygon in self.setup_config["mask"]["outflow_boundary_polygon"]:
            polygons = read_pli_file(os.path.join(self.data_path, polygon["file_name"]))
            # Polygon file may include multiple polygons
            for p in polygons:
                self.outflow_boundary_polygons.append(MaskPolygon(x=p.x,
                                                                  y=p.y,
                                                                  zmin=polygon["zmin"],
                                                                  zmax=polygon["zmax"]))            

        # Wave mask polygons        
        if self.setup_config["wave_mask"]:
            self.wave_include_polygons = []
            for polygon in self.setup_config["wave_mask"]["include_polygon"]:
                polygons = read_pli_file(os.path.join(self.data_path, polygon["file_name"]))
                # Polygon file may include multiple polygons
                for p in polygons:
                    self.wave_include_polygons.append(MaskPolygon(x=p.x,
                                                             y=p.y,
                                                             zmin=polygon["zmin"],
                                                             zmax=polygon["zmax"]))            
        
            self.wave_exclude_polygons = []
            for polygon in self.setup_config["wave_mask"]["exclude_polygon"]:
                polygons = read_pli_file(os.path.join(self.data_path, polygon["file_name"]))
                # Polygon file may include multiple polygons
                for p in polygons:
                    self.wave_exclude_polygons.append(MaskPolygon(x=p.x,
                                                             y=p.y,
                                                             zmin=polygon["zmin"],
                                                             zmax=polygon["zmax"]))            
            self.wave_open_boundary_polygons = []
            for polygon in self.setup_config["wave_mask"]["open_boundary_polygon"]:
                polygons = read_pli_file(os.path.join(self.data_path, polygon["file_name"]))
                # Polygon file may include multiple polygons
                for p in polygons:
                    self.wave_open_boundary_polygons.append(MaskPolygon(x=p.x,
                                                       y=p.y,
                                                       zmin=polygon["zmin"],
                                                       zmax=polygon["zmax"]))            

                
        # Bathymetry and roughness
        self.bathymetry_list = []
        for dataset in self.setup_config["bathymetry"]["dataset"]:
            self.bathymetry_list.append(BathymetryDataset(name=dataset["name"],
                                                          source=dataset["source"],
                                                          zmin=dataset["zmin"],
                                                          zmax=dataset["zmax"]))
    
        self.roughness_list = []
        if "dataset" in self.setup_config["roughness"]:
            for dataset in self.setup_config["roughness"]["dataset"]:
                self.roughness_list.append(BedRoughnessDataset(name=dataset["name"],
                                                               source=dataset["source"],
                                                               zlevel=dataset["zlevel"],
                                                               roughness_deep=dataset["roughness_deep"],
                                                               roughness_shallow=dataset["roughness_shallow"]))
        
