__author__ = 'roehrig'

import os
import time

import numpy as np
import pandas as pd

from osgeo import ogr

from warsa.timeseries.timeseries import read_time_series, write_time_series
# from warsa.gis.rasters.raster import Raster
# from warsa.gis.features.feature import Layers
# from warsa.gis.rasters.zonal import zonal_stats


def print_verbose(msg, verbose=True, same_line=False):
    if verbose:
        if same_line:
            print msg,
        else:
            print msg
        return time.time()
    return None


def create_time_series_from_rasters_to_points(lrs, layer_fieldname, df, datetime_dict):
    try:
        lrs = Layers(lrs)
    except:
        pass

    world_coords = sorted(lrs.get_geometry_and_field_values([layer_fieldname]), key=lambda gv: gv[1])
    world_coords = [[ogr.CreateGeometryFromWkb(gv[0])] for gv in world_coords]
    world_coords = [(gv[0].GetX(), gv[0].GetY()) for gv in world_coords]

    t0 = time.time()

    def func0(row):
        if np.isnan(row.values.tolist()).any():
            rs_filename = datetime_dict[row.name]
            r = Raster(rs_filename)
            arr = r.get_array()
            pixel_coords = [r.world_to_pixel(x, y) for x, y in world_coords]
            arr = np.array([arr[i][j] for i, j in pixel_coords])  # TODO: check (i, j)
            arr[arr <= -999.0] = float('NaN')
            return arr

    df = df.apply(func0, axis=1)
    print_verbose(' done in {:.2f} seconds'.format(time.time()-t0))
    return df


def create_time_series_from_rasters_to_polygons(lrs, layer_fieldname, columns, df, datetime_dict):
    try:
        lrs = Layers(lrs)
    except:
        pass
    len_df = len(df)
    rs_filename = ''
    t0 = time.time()
    for i in xrange(len_df):
        if np.isnan(df.iloc[i].values.tolist()).any():
            rs_filename = datetime_dict[df.index[i].to_datetime()]
            zs = zonal_stats(lrs, rs_filename, layer_fieldname, ['mean'])
            df.iloc[i] = [zs[column][0][0] for column in columns]
        if i % 10 == 0:
            t0 = print_verbose('{} - {:d} of {:d}: {:.2f} seconds'.format(rs_filename, i, len_df, time.time()-t0))

    return df


def get_rasterized_files(rasters_dir, suffix='.tif'):
    filenames = []
    for root, dirs, files in os.walk(rasters_dir):
        if files:
            filenames += [root + '/' + f for f in files if f.endswith(suffix)]
    return sorted(filenames)


def create_time_series_from_rasters(raster_dir, lrs, layer_fieldname, get_datetime_from_raster_file,
                                    time_series_filename=None, suffix='.tif'):
    """
    :param raster_dir:
    :param lrs:
    :param layer_fieldname:
    :param get_datetime_from_raster_file:
    :param time_series_filename:
    :param suffix:
    :param to_millimeter:
    :return:
    """
    print_verbose('Create time series ' + time_series_filename)
    try:
        lrs = Layers(lrs)
    except:
        pass

    # get  geometry type
    is_point_geometry = lrs.is_geometry_point()

    # get the field values, which correspond to columns in the time series
    columns = list(sorted(zip(*lrs.get_field_values([layer_fieldname]))[0]))

    # create a dictionary {datetime: raster_file_name}
    rasterized_files = get_rasterized_files(raster_dir, suffix)
    datetime_dict = dict([(get_datetime_from_raster_file(rf), rf) for rf in rasterized_files])

    df = None
    if os.path.isfile(time_series_filename):
        # if a time series exists, then its columns must be equal the ones found above
        df = read_time_series(time_series_filename)
    if df is None or len(df)==0:
        df = pd.DataFrame(columns=columns, index=sorted(datetime_dict.keys()))

    if not is_point_geometry:
        df = create_time_series_from_rasters_to_polygons(lrs, layer_fieldname, columns, df, datetime_dict)
    else:
        df = create_time_series_from_rasters_to_points(lrs, layer_fieldname, df, datetime_dict)

    write_time_series(df, time_series_filename)

