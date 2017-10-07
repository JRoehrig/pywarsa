__author__ = 'roehrig'

import datetime
import os


def create_time_series_from_rasters(raster_dir, lrs, layer_fieldname, time_series_filename):

    def datetime_from_raster_file(file_name):
        # CMORPH_V1.0_RAW_0.25deg-3HLY_1998010100.tif
        try:
            return datetime.datetime.strptime(os.path.splitext(file_name)[0].split('_')[-1], '%Y%m%d%H%M')
        except:
            print file_name, os.path.splitext(file_name)[0].split('_')[-1]
            raise Exception

    warsa.precipytation.satellite.sarp_time_series.create_time_series_from_rasters(raster_dir, lrs, layer_fieldname, datetime_from_raster_file, time_series_filename)
