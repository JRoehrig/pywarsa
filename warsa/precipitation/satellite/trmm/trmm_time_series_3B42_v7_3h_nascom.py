__author__ = 'roehrig'

import datetime
import os


def create_time_series_from_rasters(raster_dir, lrs, layer_fieldname, time_series_filename):

    def get_datetime_from_raster_file(file_name):
        # 3B42.19980101.00.7.tif
        s = ''.join(os.path.basename(file_name).split('.')[1:3])
        return datetime.datetime.strptime(s, '%Y%m%d%H')

    warsa.precipytation.satellite.sarp_time_series.create_time_series_from_rasters(raster_dir, lrs, layer_fieldname, get_datetime_from_raster_file, time_series_filename)
