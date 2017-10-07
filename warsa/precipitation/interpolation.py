__author__ = 'roehrig'

import numpy as np
import pandas as pd
from osgeo import ogr

# from warsa.gis.features.feature import Layers
# from warsa.gis.features.interpolation.idw import idw


def idw_time_series_interpolation(point_lrs_in, field_name_in, df_ts_in, point_lrs_out, field_name_out):
    # Extract point coordinates and corresponding ids of input and output layers
    try:
        point_lrs_in = Layers(point_lrs_in)
    except TypeError:
        pass
    try:
        point_lrs_out = Layers(point_lrs_out)
    except TypeError:
        pass
    feat_in = sorted([list(ogr.CreateGeometryFromWkb(f[0]).GetPoints()[0]) + [str(f[1])] for f in point_lrs_in.get_geometry_and_field_values([field_name_in])], key=lambda v: v[2])
    feat_out = sorted([list(ogr.CreateGeometryFromWkb(f[0]).GetPoints()[0]) + [str(f[1])] for f in point_lrs_out.get_geometry_and_field_values([field_name_out])], key=lambda v: v[2])

    # Read time series
    df_ts_in.columns = [str(c) for c in df_ts_in.columns]

    # Harmonize the features and time series
    # Remove columns from time series not contained in the input features list
    df_ts_in = df_ts_in[list(zip(*feat_in)[2])]
    # Remove input features list not contained in the time series
    feat_in = [f for f in feat_in if f[2] in df_ts_in.columns]

    # Set gaps label for each row
    gap_labels = 'GAPLABELS'
    while gap_labels in df_ts_in.columns:
        gap_labels += '0'
    df_ts_in.is_copy = False  # TODO: deal with the warning
    df_ts_in[gap_labels] = df_ts_in.apply(lambda row: ''.join(['0' if np.isnan(v) else '1' for ir, v in enumerate(row)]), axis=1)

    # Get all patterns of weights  =[number of out_points, number of valid input points]
    combination_weights = {}
    xy_out = zip(*zip(*feat_out)[0:2])
    for combination in set(df_ts_in[gap_labels].tolist()):
        if combination not in combination_weights:
            fin = [f for i, f in enumerate(feat_in) if combination[i] == '1']
            if fin:
                combination_weights[combination] = idw(zip(*zip(*fin)[0:2]), np.diag([1]*len(fin)).tolist(), xy_out)
            else:
                combination_weights[combination] = None

    df_ts_out = pd.DataFrame(index=df_ts_in.index)
    for col_idx, col_out in enumerate(zip(*feat_out)[2]):
        def weighted_sum(row):
            comb = combination_weights[row[-1]]
            if comb is not None:
                weights = comb[col_idx]
                gap_indices = [ig for ig, gc in enumerate(row[-1]) if gc == '0']
                for gi in gap_indices:
                    weights = np.insert(weights, gi, 0.0)
                return np.sum(row[:-1] * weights)
            else:
                return np.NaN
        df_ts_out[col_out] = df_ts_in.apply(weighted_sum, axis=1)

    del df_ts_in[gap_labels]
    return df_ts_out





