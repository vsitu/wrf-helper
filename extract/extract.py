from asyncore import write
from scipy.interpolate import griddata as gridd
import numpy as np
import netCDF4 as nc
from osgeo import gdal, osr 
import os, sys
import datetime as dt 

class Extractor:
    def __init__(self):
        return
    
    def one_step_extract(self, info):
        fpath, geo_desc, mission_id, nodata = info 
        self.read(file_path = fpath)
        output_flist, output_vnames = self.extract_all(
            geo_desc=geo_desc, mission_id=mission_id, nodata=nodata
        )
        return output_flist, output_vnames

    def read(self, file_path):
        self.file_path = file_path 

        # variables
        normal_var = ['T2', 'PSFC', 'U10', 'V10', 'SWUPB', 'SWDNB', 'SNOWC', 'SNOWH']
        calc_var = ['QVAPOR']
        accu_var = ['RAINNC']
        cloud_var = ['CLDFRA']
        soil_var = ['TSLB', 'SMOIS']
        wv_var = ['U', 'V', 'XLAT_U', 'XLONG_U', 'XLAT_V', 'XLONG_V']

        # read variables
        with nc.Dataset(file_path, 'r') as ds:
            self.normvar = {}
            for vname in normal_var:
                # print(vname, ds.variables[vname][:].shape)
                self.normvar[vname] = ds.variables[vname][0,:,:]
            
            self.windvar = {}
            for vname in wv_var:
                self.windvar[vname] = ds.variables[vname][:]
                
            self.soilvar = {}
            for vname in soil_var:
                self.soilvar[vname] = ds.variables[vname][:]

            self.mesh = {
                'lats':ds.variables['XLAT'][0,:,:],
                'lons':ds.variables['XLONG'][0,:,:]
                }
            
    def extract(self, varname, geo_desc):
        '''
        will determine which group varname belongs to
        '''
        if varname in self.normvar.keys():
            mx, my, outarr = self._resample(self.normvar[varname], geo_desc, self.mesh)
        elif varname in self.soilvar.keys():
            mx, my, outarr1 = self._resample(self.soilvar[varname][0,0,:,:], geo_desc, self.mesh)
            outarr = np.zeros_like(outarr1)
            outarr = outarr[np.newaxis, :,:]
            for i in range(1, self.soilvar[varname].shape[1]):
                mx, my, temp = self._resample(varname, geo_desc, self.mesh)
                outarr = np.concat([outarr, temp], axis = 0)
        return mx, my, outarr 

    def extract_all(self, geo_desc, mission_id, 
                    nodata = -9999):
        self.res = geo_desc[4]
        output_list = []
        vname_list = []
        # get normal var
        normvar_dict = self.extract_norm(geo_desc)
        normkey = list(normvar_dict.keys())
        for key in normkey:
            arr = normvar_dict[key]
            fpath = self._export_tif(arr=arr, varname=key, 
                        geo_desc=geo_desc, mission_id=mission_id, 
                        nodata_value=nodata)
            output_list.append(fpath) 
            vname_list.append(key)

        # get soil var
        soilvar_dict = self.extract_soil(geo_desc)
        soilkey = list(soilvar_dict.keys())
        for key in soilkey:
            arr = soilvar_dict[key]
            fpath = self._export_tif(arr=arr, varname=key, 
                        geo_desc=geo_desc, mission_id=mission_id, 
                        nodata_value=nodata)
            output_list.append(fpath) 
            vname_list.append(key)
        return output_list, vname_list


    
    def extract_norm(self, geo_desc):
        self.normvar2 = {}
        normvar = list(self.normvar.keys())
        for vname in normvar:
            mx, my, self.normvar2[vname] = self._resample(self.normvar[vname], geo_desc, self.mesh)
        self.mx = mx; self.my = my
        return self.normvar2
        
    def extract_wind(self, geo_desc, layer:int):
        umesh = {
                'lats':self.windvar['XLAT_U'][0,:,:],
                'lons':self.windvar['XLONG_U'][0,:,:]
                }
        vmesh = {
                'lats':self.windvar['XLAT_V'][0,:,:],
                'lons':self.windvar['XLONG_V'][0,:,:]
                }
        self.umx, self.umy, self.wv_ua = self._resample(self.windvar['U'][0,layer,:,:], 
                                              geo_desc, umesh)
        self.vmx, self.vmy, self.wv_va = self._resample(self.windvar['V'][0,layer,:,:], 
                                              geo_desc, vmesh)
        return {'U':self.wv_ua,'V':self.wv_va}
        
    def extract_soil(self, geo_desc):
        self.soilvar2 = {}
        soilkey = list(self.soilvar.keys())
        soil_dict = {}
        for vname in soilkey:
            for layer in range(4):
                out_key = f'{vname}{layer}'
                smx, smy, soil_dict[out_key] = self._resample(self.soilvar[vname][0,layer,:,:], 
                                                    geo_desc, self.mesh)
        return soil_dict

    def _export_tif(self, arr, varname, geo_desc, mission_id, nodata_value):
        self.res = geo_desc[4]
        ref_height, ref_width = arr.shape

        compress = ["COMPRESS=LZW"] 
        datatype = gdal.GDT_Float32 
        if len(arr.shape) != 2:
            raise ValueError('input array not 2D')

        # get output path
        workdir = os.path.dirname(self.file_path)
        fname_in = os.path.basename(self.file_path) 
        fname = '_'.join([mission_id, fname_in, varname]) + '.tif'
        write_path = os.path.join(workdir, fname)

        # geotrans
        a,x,y,b,res = geo_desc 
        ref_geotrans = [a, res, 0, b, 0, -1*res]

        # if output file exists, remove it
        if os.path.exists(write_path):
            os.remove(write_path)
        out_ds = gdal.GetDriverByName("GTiff").Create(
            write_path, ref_width, ref_height, 1, datatype, compress
            )
        srs = osr.SpatialReference()
        srs.ImportFromEPSG(4326)
        out_ds.SetProjection(srs.ExportToWkt())
        out_ds.SetGeoTransform(ref_geotrans)
        out_ds.GetRasterBand(1).WriteArray(arr)
        out_ds.GetRasterBand(1).SetNoDataValue(nodata_value)
        out_ds.FlushCache()
        out_ds = None

        return write_path

    def _resample(self, wind_data, new_geodesc, old_mesh_dict):
        old_meshx = old_mesh_dict['lons']; old_meshy = old_mesh_dict['lats']
        wind1d = wind_data.ravel()
        L,R,D,U,res = new_geodesc
        xval = np.arange(L, R+res, res); yval = np.arange(D, U+res, res)
        meshx, meshy = np.meshgrid(xval, yval)
        old_x = old_meshx.ravel(); old_y = old_meshy.ravel()
        old_mesh = np.stack([old_x, old_y])
        output = gridd(old_mesh.T, wind1d, (meshx, meshy), method = 'linear')
        return meshx, meshy, output