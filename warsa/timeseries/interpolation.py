import numpy as np
import pandas as pd
from osgeo import ogr
from girs.feat.layers import LayersReader
from girs.feat import idw_interpolation


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
                      for f in points_in.get_geometry_and_field_values([fieldname_in])], key=lambda v: v[2])
    feat_out = sorted([list(ogr.CreateGeometryFromWkb(f[0]).GetPoints()[0]) + [str(f[1])]
                       for f in points_out.get_geometry_and_field_values([fieldname_out])], key=lambda v: v[2])

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
                combination_weights[combination] = idw_interpolation.idw(xy_in=xy_in, z_in=z_in, xy_out=xy_out)
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





