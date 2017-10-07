__author__ = 'roehrig'

import trmm_time_series_3B42RT_v7_3h_trmmopen


def create_time_series_from_rasters(raster_dir, lrs, layer_fieldname, time_series_filename, suffix='.tif'):
    trmm_time_series_3B42RT_v7_3h_trmmopen.create_time_series_from_rasters(raster_dir, lrs, layer_fieldname, time_series_filename, suffix)
