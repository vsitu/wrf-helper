import numpy as np
import netCDF4 as nc
from scipy.interpolate import griddata as gridd


class Level:
    def __init__(self, file_path = None):
        if file_path is not None:
            extension = file_path.split('.')[-1]
            print(f'File Format is {extension}')
            if extension == 'nc':
                self.read_nc(file_path)
            else:
                print(f'Format not supported: {extension}')
                return
        else: 
            pass 

    def read_nc(self, file_path:str):
        """
        If WRF output is netCDF4, use this
        """

        self.file_path = file_path 
        with nc.Dataset(file_path, 'r') as ds:
            self.ph = ds.variables['PH'][0,:,:,:]   # geopotential
            self.phb = ds.variables['PHB'][0,:,:,:] # perturbation geopotential
            self.hgt = ds.variables['HGT'][0,:,:]   # surface height (m)
            self.layer_sl = (self.ph + self.phb)/9.8  # layer height from sea level
            self.model_layers = self.ph.shape[0]

    def get_layer_height(self, layer_index:int):
        """
        Get the nth layer of the model. 

        Input: layer index, 0 is the bottom layer (close to ground surface)
        Return: height array
        """
        height = self.layer_sl[layer_index, :, :] - self.hgt 
        return height

    def get_height_layer(self, height:int, mode='local'):
        """
        Get the index of the layer which is closest to the given height.

        Input: 
            height: meters above the given surface
            mode: ['local', 'sea']
                'local' means height given is based on local ground surface
                'sea' means height given is based on sea level
        """
        # target is the layer height we use to find the closest model layer
        if mode=='sea':
            target = np.zeros_like(self.hgt) + height 
        elif mode=='local':
            target = self.hgt + height 
        
        diff = []
        for layer_index in range(self.model_layers):
            diff.append(np.sqrt(np.sum((target - self.layer_sl[layer_index,:,:])**2)/target.size))
        diff = np.array(diff)

        target_index = np.argmin(diff)
        return target_index