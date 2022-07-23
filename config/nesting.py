import numpy as np

import geopandas as gpd
import cartopy.crs as ccrs
from shapely.geometry import Polygon

import pandas as pd
import os, sys
import time
import datetime as dt

rearth = 6378
cearth = rearth * np.pi * 2

class Box:
    def __init__(self, geo_desc:list, box_num=1):
        """
        Make a bounding box
        geo_desc: [lon, lat, x_size, y_size, x_res, y_res]
            lon, lat: central longitude and latitude
            x_size, y_size: x (longitude) and y (latitude) size of the box, in pixels
            x_res, y_res: resolution in x and y direction
        box_num: int
            for reference only
        """
        self.lon, self.lat, self.sizex, self.sizey, self.dx, self.dy = geo_desc
        self.box_num = box_num
        self.make(geo_desc)
        self.coords = self.coords()
        self.polygon = self.polygon()
        return

    def make(self, geo_desc:list):

        # extract parameters from list
        d1_lon, d1_lat, d1sizex, d1sizey, d1x, d1y = geo_desc
        # get north and south boundaries (latitude in degrees)
        self.north = d1_lat + (d1sizey / 2 * d1y / 1000)/cearth * 360
        self.south = d1_lat - (d1sizey / 2 * d1y / 1000)/cearth * 360
        # get longitude (in degrees) for 4 corners of the box
        self.east_n = d1_lon + (d1sizex / 2 * d1x / 1000) /(cearth* np.cos(np.pi / 180 * self.north)) * 360
        self.east_s = d1_lon + (d1sizex / 2 * d1x / 1000) /(cearth* np.cos(np.pi / 180 * self.south)) * 360
        self.west_n = d1_lon - (d1sizex / 2 * d1x / 1000) /(cearth* np.cos(np.pi / 180 * self.north)) * 360
        self.west_s = d1_lon - (d1sizex / 2 * d1x / 1000) /(cearth* np.cos(np.pi / 180 * self.south)) * 360

    def coords(self):
        return([self.north, self.south, 
            self.east_n, self.east_s, 
            self.west_n, self.west_s])

    def polygon(self):
        polygon = [(self.west_s, self.south), 
        (self.west_n, self.north), 
        (self.east_n, self.north), 
        (self.east_s, self.south), 
        (self.west_s, self.south)]
        return(polygon)


class Nest():
    def __init__(self):
        self.parent_list = []
        self.i_list = []
        self.j_list = []

    def status(self):
        return([self.box_num_list, self.i_list, self.j_list])

    def nest(self, d01, d02):
        """
        Nest d02 in d01
        d02 and d01 should both be "Box" class objects
        """

        d1_coords = d01.coords()
        d2_coords = d02.coords()

        print(d1_coords, d2_coords)
        if (d02.west_s < d01.west_s) or (d02.west_n < d01.west_n):
            print(f'D02: {d02.west_s}, {d02.west_n}')
            print(f'D01: {d01.west_s}, {d01.west_n}')
            raise ValueError ('D02 utside of D01 border: West')
        if (d02.east_s > d01.east_s) or (d02.east_n > d01.east_n):
            print(f'D02: {d02.east_s}, {d02.east_n}')
            print(f'D01: {d01.east_s}, {d01.east_n}')
            raise ValueError ('D02 utside of D01 border: East')
        if (d02.south < d01.south):
            print(f'D02: {d02.south}')
            print(f'D01: {d01.south}')
            raise ValueError ('D02 utside of D01 border: South')
        if (d02.north > d01.north):
            print(f'D02: {d02.north}')
            print(f'D01: {d01.north}')
            raise ValueError ('D02 utside of D01 border: North')
            
        # print('d1 north south eastn easts westn wests  ',d1_coords)
        # print('d2 north south eastn easts westn wests  ',d2_coords)
        
        j_parent_start = (d02.south - d01.south)/360 * cearth * 1000 / d01.dy   #y offset, in pixels

        bound_west = d01.lon - (d01.sizex / 2 * d01.dx / 1000) /(cearth * np.cos(np.pi / 180 * d02.south)) * 360
        print('bound 1 west',bound_west)
        i_parent_start = (d02.west_s - bound_west)/360 * (cearth * np.cos(np.pi / 180 * d02.south)) * 1000 / d01.dx   #x offset, in pixels
        print(i_parent_start, j_parent_start)
        
        self.parent_list.append([d01.box_num])
        self.i_list.append(i_parent_start)
        self.j_list.append(j_parent_start)

        return ((d01.box_num, d02.box_num), (i_parent_start, j_parent_start))
