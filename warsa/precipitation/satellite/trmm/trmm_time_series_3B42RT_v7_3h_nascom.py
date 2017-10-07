__author__ = 'roehrig'

import datetime
import os


def create_time_series_from_rasters(raster_dir, lrs, layer_fieldname, time_series_filename, suffix='.tif'):

    def get_datetime_from_raster_file(file_name):
        # 3B42RT.2000.03.01.00.tif
        s = '.'.join(os.path.basename(file_name).split('.')[1:5])[:13]
        return datetime.datetime.strptime(s, '%Y.%m.%d.%H')

    def to_millimeter(row):
        row[row <= -999.0] = float('NaN')
        return row * 3

    warsa.precipytation.satellite.sarp_time_series.create_time_series_from_rasters(raster_dir, lrs, layer_fieldname, get_datetime_from_raster_file, time_series_filename, suffix=suffix)

