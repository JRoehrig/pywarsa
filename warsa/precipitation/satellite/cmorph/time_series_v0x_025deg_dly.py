__author__ = 'roehrig'

import datetime
import os


def create_time_series_from_rasters(raster_dir, lrs, layer_fieldname, time_series_filename):

    def datetime_from_raster(file_name):
        # CMORPH_V0.x_RAW_0.25deg-DLY_00Z_20140601.tif
        return datetime.datetime.strptime(os.path.splitext(file_name)[0].split('_')[-1], '%Y%m%d')

    warsa.precipytation.satellite.sarp_time_series.create_time_series_from_rasters(raster_dir, lrs, layer_fieldname, datetime_from_raster, time_series_filename)
