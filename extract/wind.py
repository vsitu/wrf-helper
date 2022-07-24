import numpy as np
import netCDF4 as nc
from scipy.interpolate import griddata as gridd


class Wind:
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
            self.u = ds.variables['U'][:]
            self.v = ds.variables['V'][:]
            lonsu = ds.variables['XLONG_U'][:]
            latsu = ds.variables['XLAT_U'][:]
            lonsv = ds.variables['XLONG_V'][:]
            latsv = ds.variables['XLAT_V'][:]
            self.xmeshu = lonsu[0,:,:]
            self.ymeshu = latsu[0,:,:]
            self.xmeshv = lonsv[0,:,:]
            self.ymeshv = latsv[0,:,:]

            self.model_layers = self.u.shape[0]

    def resample(self, new_geodesc, wind_data, old_meshx, old_meshy):
        """
        U and V components of the wind can have different grid settings. 
        Use this to resample them to the same grid
        new_geodesc: [L, R, D, U, resolution]. 
            L, R, D, U are Left,Right,Lower and Upper boundaries of the new box.
            resolution is the resolution to resample to. 
            All in "degrees"
        wind_data: U or V wind component. One 2-d array at a time.
        old_meshx, old_meshy: the old meshgrid for U or V wind array

        Output: new_meshgridx, new_meshgridy, new_wind_array

        example: 
            u = ds.variables['U'][:]
            lonsu = ds.variables['XLONG_U'][:]
            latsu = ds.variables['XLAT_U'][:]
            xmeshu = lonsu[0,:,:]
            ymeshu = latsu[0,:,:]
            meshx, meshy, windu_new = wind_resample(u[0,0,:,:], geodesc, xmeshu, ymeshu)

        """
        wind1d = wind_data.ravel()
        L,R,D,U,res = new_geodesc
        xval = np.arange(L+res,R+res, res); yval = np.arange(D, U+res, res)
        meshx, meshy = np.meshgrid(xval, yval)
        old_x = old_meshx.ravel(); old_y = old_meshy.ravel()
        old_mesh = np.stack([old_x, old_y])
        output = gridd(old_mesh.T, wind1d, (meshx, meshy), method = 'linear')
        return meshx, meshy, output

    def extract(self, new_geodesc):
        """
        Extract wind velocity (wind speed + wind direction).
        Input: new_geodesc: [L, R, D, U, resolution]
        Return: wind speed, wind direction
        """
        if (self.u is None) or (self.v is None):
            raise ValueError('Load U and V first')

        u_new_1 = self.resample(new_geodesc=new_geodesc, wind_data=self.u[0,i,:,:], old_meshx=self.xmeshu, old_meshy=self.ymeshu)
        u_new = np.zeros((self.model_layers, u_new_1.shape[0], u_new_1.shape[1]))
        v_new = np.zeros((self.model_layers, u_new_1.shape[0], u_new_1.shape[1]))
        for i in range(self.model_layers):
            a, b, windu_1 = self.resample(new_geodesc=new_geodesc, wind_data=self.u[0,i,:,:], old_meshx=self.xmeshu, old_meshy=self.ymeshu) 
            a, b, windv_1 = self.resample(new_geodesc=new_geodesc, wind_data=self.v[0,i,:,:], old_meshx=self.xmeshv, old_meshy=self.ymeshv) 
            u_new[i,:,:] = windu_1 
            v_new[i,:,:] = windv_1 

        wv = np.sqrt(u_new **2 + v_new **2)
        wdir = np.where(u_new==0, 0, 1)   #avoid U=0
        wdir = np.where(u_new > 0, 90 - np.arctan(v_new/u_new) * 180/np.pi, wdir)
        wdir = np.where(u_new < 0, 90 - np.arctan(v_new/u_new) * 180/np.pi + 180, wdir)
        
        return wv, wdir 
