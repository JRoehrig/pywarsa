import os
import time
import collections
import numpy as np
import pandas as pd
from osgeo import ogr
from girs.feat.layers import LayersReader
from girs.rast.raster import RasterReader
from girs.rastfeat.zonal import zonal_stats
from warsa.timeseries.timeseries import read_time_series, write_time_series


def print_verbose(msg, verbose=True, same_line=False):
    if verbose:
        if same_line:
            print msg,
        else:
            print msg
        return time.time()
    return None


def create_time_series_from_rasters_to_points(df_geo, df_ts, datetime_dict):
    """

    :param df_geo: station names as index and geometry-wkb as column '_GEOM_'
    :param df_ts: datetime as index and station names as columns
    :param datetime_dict: datetime as index and raster-filename as column
    :return:
    """
    t0 = time.time()
    print_verbose('Creating time series from satellites to points')
    print_verbose('Points: {}'.format(len(df_ts.columns)))
    print_verbose('Date / Time: {}'.format(len(df_ts)))
    df_geo = df_geo.apply(lambda rr: [(g.GetX(), g.GetY()) for g in [ogr.CreateGeometryFromWkb(gb) for gb in rr]])
    geo_dict = {'P' + k: v for k, v in df_geo['_GEOM_'].to_dict().items()}

    def func0(row):
        if np.isnan(row.values.tolist()).any():
            try:
                rs_filename = datetime_dict[row.name]
            except KeyError, e:
                raise e
            if row.name.day == 1:
                print_verbose('{}-{}: {}'.format(row.name.year, row.name.month, rs_filename))
            r = RasterReader(rs_filename)
            nodata = r.get_nodata()
            arr = r.get_array().astype(np.float32)
            pixel_coords = [r.world_to_pixel(*geo_dict[name]) for name in row.index]
            arr = np.array([arr[j][i] for i, j in pixel_coords])
            arr[arr == nodata] = np.nan
            return arr
        else:
            return row

    df_ts = df_ts.apply(func0, axis=1)
    print_verbose(' done in {:.2f} seconds'.format(time.time()-t0))
    return df_ts


def create_time_series_from_rasters_to_polygons(lrs, layer_fieldname, columns, df, datetime_dict):
    try:
        lrs = LayersReader(lrs)
    except:
        pass
    len_df = len(df)
    rs_filename = ''
    t0 = time.time()
    for i in xrange(len_df):
        if np.isnan(df.iloc[i].values.tolist()).any():
            rs_filename = datetime_dict[df.index[i].to_datetime()]
            zs = zonal_stats(lrs, rs_filename, layer_fieldname, ['mean'])
            df.iloc[i] = [zs[column][1][0] for column in columns]
        if i % 10 == 0:
            t0 = print_verbose('{} - {:d} of {:d}: {:.2f} seconds'.format(rs_filename, i, len_df, time.time()-t0))

    return df


def get_rasterized_files(rasters_dir, suffix='.tif'):
    filenames = []
    for root, dirs, files in os.walk(rasters_dir):
        if files:
            filenames += [root + '/' + f for f in files if f.endswith(suffix)]
    return sorted(filenames)


# def create_time_series_from_rasters_backup(raster_dir, lrs, layer_fieldname, get_datetime_from_raster_file,
#                                     time_series_filename=None, suffix='.tif'):
#     """
#     :param raster_dir:
#     :param lrs:
#     :param layer_fieldname:
#     :param get_datetime_from_raster_file:
#     :param time_series_filename:
#     :param suffix:
#     :param to_millimeter:
#     :return:
#     """
#     print_verbose('Create time series ' + time_series_filename)
#     try:
#         lrs = LayersReader(lrs)
#     except:
#         pass
#
#     # get  geometry type
#     is_point_geometry = lrs.is_geometry_point()
#
#     # get the field values, which correspond to columns in the time series
#     columns = list(sorted(zip(*lrs.get_field_values([layer_fieldname]))[0]))
#
#     # create a dictionary {datetime: raster_file_name}
#     rasterized_files = get_rasterized_files(raster_dir, suffix)
#     datetime_dict = dict([(get_datetime_from_raster_file(rf), rf) for rf in rasterized_files])
#
#     df = None
#     if os.path.isfile(time_series_filename):
#         # if a time series exists, then its columns must be equal the ones found above
#         df = read_time_series(time_series_filename)
#     if df is None or len(df) == 0:
#         df = pd.DataFrame(columns=columns, index=sorted(datetime_dict.keys()))
#
#     if not is_point_geometry:
#         df = create_time_series_from_rasters_to_polygons(lrs, layer_fieldname, columns, df, datetime_dict)
#     else:
#         df = create_time_series_from_rasters_to_points(lrs, layer_fieldname, df, datetime_dict)
#
#     write_time_series(df, time_series_filename)


def create_time_series(time_series_filename, raster_dir, layers, get_datetime_from_raster_file, **kwargs):
    """
    :param time_series_filename:
    :param raster_dir:
    :param layers:
    :param get_datetime_from_raster_file:
    :param kwargs:
        :key layer_fieldname:
        :key layer_number:
        :key raster_suffix:
        :key float_format:

    :return:
    """
    # raster_dir, lrs, layer_fieldname, get_datetime_from_raster_file, time_series_filename = None, suffix = '.tif'

    try:
        layers = LayersReader(layers)
    except:
        pass

    layer_fieldname = kwargs.pop('layer_fieldname', None)
    raster_suffix = kwargs.pop('raster_suffix', '')
    float_format = kwargs.pop('float_format', None)
    is_geometry_point = layers.is_geometry_point().all()
    is_geometry_polygon = layers.is_geometry_polygon().all()
    assert is_geometry_point or is_geometry_polygon

    # create a ordered dictionary {datetime: raster_file_name} sorted by key
    rasterized_files = get_rasterized_files(raster_dir, raster_suffix)
    datetime_dict = dict([(get_datetime_from_raster_file(rf), rf) for rf in rasterized_files])
    datetime_dict = collections.OrderedDict([(k, datetime_dict[k]) for k in sorted(datetime_dict.keys())])

    r = RasterReader(rasterized_files[0])
    layers = layers.transform(r)

    # get the field values, which correspond to columns in the time series
    if layer_fieldname:
        df_geo = layers.get_geometries_and_field_values([layer_fieldname]).set_index(layer_fieldname).sort_index()
        columns = df_geo.index.tolist()  # from layer_fieldname
    else:
        df_geo = layers.get_geometries().sort_index()
        columns = df_geo.index.tolist()  # FID

    df_ts = None
    if os.path.isfile(time_series_filename):
        # if a time series exists, then its columns must be equal the ones found above
        df_ts = read_time_series(time_series_filename)
    if df_ts is None or len(df_ts) == 0:
        df_ts = pd.DataFrame(columns=['P{}'.format(c) for c in columns], index=datetime_dict.keys())

    assert len(set(df_geo.index).difference(set([c[1:] for c in df_ts.columns]))) == 0

    if not is_geometry_point:
        df_ts = create_time_series_from_rasters_to_polygons(layers, layer_fieldname, columns, df_ts, datetime_dict)
    else:
        df_ts = create_time_series_from_rasters_to_points(df_geo, df_ts, datetime_dict)

    if isinstance(df_ts, pd.Series):
        df_ts = df_ts.to_frame()
        df_ts.columns = ['Precipitation']
    write_time_series(df_ts, time_series_filename, float_format=float_format)
    return df_ts

