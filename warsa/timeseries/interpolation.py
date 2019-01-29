import numpy as np
import pandas as pd
from osgeo import ogr
import girs.feat.proc
from girs.feat.layers import LayersReader


def idw(points_in, fieldname_in, df_in, points_out, fieldname_out):
    # Extract point coordinates and corresponding ids of input and output layers
    try:
        points_in = LayersReader(points_in)
    except (RuntimeError, TypeError):
        pass
    try:
        points_out = LayersReader(points_out)
    except (RuntimeError, TypeError):
        pass
    feat_in = sorted([list(ogr.CreateGeometryFromWkb(f[0]).GetPoints()[0]) + [str(f[1])]
                      for f in points_in.get_geometries_and_field_values([fieldname_in])], key=lambda v: v[2])
    feat_out = sorted([list(ogr.CreateGeometryFromWkb(f[0]).GetPoints()[0]) + [str(f[1])]
                       for f in points_out.get_geometries_and_field_values([fieldname_out])], key=lambda v: v[2])

    # Read time series
    df_in.columns = [str(c) for c in df_in.columns]

    # Harmonize the features and time series
    # Remove columns from time series not contained in the input features list
    df_in = df_in[list(zip(*feat_in)[2])]
    # Remove input features list not contained in the time series
    feat_in = [f for f in feat_in if f[2] in df_in.columns]

    # Set gaps label for each row
    gap_labels = 'GAPLABELS'
    while gap_labels in df_in.columns:
        gap_labels += '0'
    df_in.is_copy = False  # TODO: deal with the warning
    df_in[gap_labels] = df_in.apply(lambda row: ''.join(['0' if np.isnan(v) else '1' for ir, v in enumerate(row)]), axis=1)

    # Get all patterns of weights  =[number of out_points, number of valid input points]
    combination_weights = {}
    xy_out = zip(*zip(*feat_out)[0:2])
    combinations = df_in[gap_labels].tolist()
    print 'Combinations:', len(combinations)
    for combination in set(combinations):
        if combination not in combination_weights:
            fin = [f for i, f in enumerate(feat_in) if combination[i] == '1']
            if fin:
                xy_in = zip(*zip(*fin)[0:2])
                z_in = np.diag([1]*len(fin)).tolist()
                combination_weights[combination] = girs.feat.proc.idw(xy_in=xy_in, z_in=z_in, xy_out=xy_out)
            else:
                combination_weights[combination] = None

    df_ts_out = pd.DataFrame(index=df_in.index)
    for col_idx, col_out in enumerate(zip(*feat_out)[2]):
        def weighted_sum(row):
            combination = row[-1]
            comb_weights = combination_weights[combination]
            if comb_weights is not None:
                idx_val = [i for i, v in enumerate(combination) if v == '1']
                recs = row[:-1]
                weights = np.zeros(len(recs))
                weights[idx_val] = comb_weights
                # print recs.tolist(), weights.tolist(), np.sum(recs * weights)
                return np.sum(recs * weights)
            else:
                return np.NaN
        df_ts_out[col_out] = df_in.apply(weighted_sum, axis=1)

    del df_in[gap_labels]
    return df_ts_out


def get_stations_weights(x, y, xx, yy, rbf_function='multiquadric', epsilon=None):
    n = len(x)
    z = np.zeros(n)
    zz = np.zeros(n)
    for i in range(n):
        z[i] = 1.0
        # zz[i] = Rbf(x, y, z, function=rbf_function, epsilon=epsilon)(xx, yy)
        z[i] = 0.0
    return zz


def ff(z, x, y, interpolation_dict):
    z.index = [int(i) for i in z.index]
    z0 = z.dropna()  # known values used for interpolation
    z1 = z[pd.isnull(z)]  # unknown values
    idx0 = z0.index.values
    idx1 = z1.index.values
    x0 = x[idx0]
    y0 = y[idx0]
    x1 = x[idx1]
    y1 = y[idx1]
    n0 = len(x0)
    n1 = len(x1)
    itp0 = (idx0 ** 2).sum()  # interpolator index
    if itp0 in interpolation_dict:
        w1 = interpolation_dict[itp0]
    else:
        w0 = np.zeros(n0)
        w1 = np.zeros((n0, n1))
        xy0 = np.vstack((x0, y0)).T
        xy1 = np.vstack((x1, y1)).T
        for i0 in range(n0):
            w0[i0] = 1.0  # set
            w1[i0] = girs.feat.proc.idw(xy_in=xy0, z_in=w0, xy_out=xy1)
            w0[i0] = 0.0  # reset
        interpolation_dict[itp0] = w1

    print 11111
    print idx1
    print 22222
    print z0
    print 33333
    print w1
    print 44444
    print z1
    print 55555
    for i, j in enumerate(idx1):
        z1[i] = z0 * w1[i]

    print x0
    print y0
    print z0
    print x1
    print y1
    print z1
    print w1
    print z1
    return z1


def fill_gaps_spatial(df_time_series, station_shp, station_id, layer_number=0):
    """
    Fill gaps in the given time series using data from the neighbour stations.
    :param df_time_series: pandas data frame with time series the column names must coincide with the station_ids. A gap
                           is np.nan
    :param stations_shp: layers of layer filename
    :param station_id: layer's field name containing unique station ids
    :param layer_number: layer number
    :return:
    """

    # Extract only rows containing one or more gaps (np.nan)
    df_ts = df_time_series[pd.isnull(df_time_series).any(axis=1)]
    df_ts.columns = [str(c) for c in df_ts.columns]
    # Map column names to indices
    # column_dict = {i**2: c for i, c in enumerate(df_ts.columns)}

    lrs = LayersReader(station_shp)
    df = lrs.data_frame(layer_number=layer_number)
    x = df['_GEOM_'].apply(lambda g: g.apply('GetX')).as_matrix()
    y = df['_GEOM_'].apply(lambda g: g.apply('GetY')).as_matrix()
    ids = [str(c) for c in lrs.get_field_values(station_id)[station_id].tolist()]
    # Check that ids are in both layer and time series
    assert len(set(ids).difference(set(df_ts.columns))) == 0
    # Sort the time series columns as in layers
    df_ts = df_ts.reindex_axis(ids, axis=1)
    interpolation_dict = dict()
    print df_ts.apply(ff, args=(x, y, interpolation_dict), axis=1)

    # for i in ids:
    #     df0 = df[df[stations_id] != i]
    # df1 = df[df[stations_id] == i]  # leave this out
    # x0 = df0['x'].as_matrix()
    # y0 = df0['y'].as_matrix()
    # x1 = df1['x'].as_matrix()
    # y1 = df1['y'].as_matrix()
    # z1 = get_stations_weights(x0, y0, x1, y1, epsilon=0.05 * d)
    # print i, z1, z1.sum()
    # df_ts0 = df_ts[[c for c in df_ts.columns if c != str(i)]]
    # df_ts0[str(i) + '_itrp'] = df_ts0.apply(lambda v0, w0: v0 * w0, args=(z1,), axis=1).sum(axis=1)
    # df_ts0[str(i)] = df_ts[str(i)]
    # print df_ts0
    # print df_ts0[str(i)].corr(df_ts0[str(i) + '_itrp'])
    # # ts_filename = os.path.join(get_precipitation_data_dir(), 'Timeseries', 'Observation','precipitation_all_1986-2015_interpolation0.csv')
    # # df.to_csv(ts_filename, sep=';')
    # df_ts0[[str(i), str(i) + '_itrp']].plot(kind='bar')
    # plt.show()


    # break
    # df = lrs.data_frame()
    # df = df[['_GEOM_', stations_id]]
    # df['x'] = df['_GEOM_'].apply(lambda g: g.apply('GetX'))
    # df['y'] = df['_GEOM_'].apply(lambda g: g.apply('GetY'))
    # n = len(df)
    # for id in df[stations_id]:
    #     df['value'] = 0
    #     # df['value'][df[stations_id] == id] = 1
    #     df.loc[df[stations_id] == id, 'value'] = 1
    #     print df
    #     zz = interpolate(df['x'], df['y'], df['value'], df['x'], df['y'])
    #     break



