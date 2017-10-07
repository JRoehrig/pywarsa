__author__ = 'roehrig'

import datetime
import os


def create_time_series_from_rasters(raster_dir, lrs, layer_fieldname, time_series_filename, suffix='.tif'):

    def datetime_from_raster(file_name):
        # 3B42RT.2000.03.01.00.tif
        s = '.'.join(os.path.basename(file_name).split('.')[1:5])
        return datetime.datetime.strptime(s, '%Y.%m.%d.%H')

    warsa.precipytation.satellite.sarp_time_series.create_time_series_from_rasters(raster_dir, lrs, layer_fieldname, datetime_from_raster, time_series_filename, suffix=suffix)

