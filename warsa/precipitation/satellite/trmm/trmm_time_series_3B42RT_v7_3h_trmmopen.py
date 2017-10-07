__author__ = 'roehrig'

import datetime
import os


def create_time_series_from_rasters(raster_dir, lrs, layer_fieldname, time_series_filename, suffix='.tif'):

    def datetime_from_raster(file_name):
        # 3B42RT.2001101603.7R2.tif
        s = os.path.basename(file_name).split('.')
        return datetime.datetime.strptime(s[1], '%Y%m%d%H')

    def to_millimeter(row):
        row[row <= -999.0] = float('NaN')
        return row * 0.03

    warsa.precipytation.satellite.sarp_time_series.create_time_series_from_rasters(raster_dir, lrs, layer_fieldname, datetime_from_raster, time_series_filename, suffix=suffix)