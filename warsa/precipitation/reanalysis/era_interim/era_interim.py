__author__ = 'roehrig'

import os
import numpy as np
import pandas as pd
import ogr, osr
from netCDF4 import Dataset, num2date


def get_lon_lat(nc, bbox):
    lon_min, lat_min, lon_max, lat_max = bbox
    ds = Dataset(nc, 'r')
    latlon = []
    latlon_idx = []
    for i, lon in enumerate(np.squeeze(ds.variables[u'longitude'])):
        lon = float(lon)
        if lon_min <= lon <= lon_max:
            for j, lat in enumerate(np.squeeze(ds.variables[u'latitude'])):
                lat = float(lat)
                if lat_min <= lat <= lat_max:
                    latlon.append((lon, lat))
                    latlon_idx.append((i, j))
    return latlon, latlon_idx


def create_shapefile(lonlat, lonlat_idx, shp):
    sr = osr.SpatialReference()
    sr.ImportFromEPSG(4326)

    driver = ogr.GetDriverByName('ESRI Shapefile')
    if os.path.isfile(shp) and os.stat(shp):
        driver.DeleteDataSource(shp)
    ds = driver.CreateDataSource(shp)

    layer = ds.CreateLayer('', sr, ogr.wkbPoint)
    layer.CreateField(ogr.FieldDefn('Longitude', ogr.OFTReal))
    layer.CreateField(ogr.FieldDefn('Latitude', ogr.OFTReal))
    layer.CreateField(ogr.FieldDefn('LonIndex', ogr.OFTInteger))
    layer.CreateField(ogr.FieldDefn('LatIndex', ogr.OFTInteger))

    ld = layer.GetLayerDefn()
    for idx, (lon, lat) in enumerate(lonlat):
        lli = lonlat_idx[idx]
        feat = ogr.Feature(ld)
        feat.SetField('Longitude', lon)
        feat.SetField('Latitude', lat)
        feat.SetField('LonIndex', lli[0])
        feat.SetField('LatIndex', lli[1])
        point = ogr.Geometry(ogr.wkbPoint)
        point.AddPoint(lon, lat)
        feat.SetGeometry(point)
        layer.CreateFeature(feat)


def create_time_series(nc, indices, variables):
    ds = Dataset(nc, 'r')

    t = ds.variables['time']
    df = pd.DataFrame(index=num2date(t[:], t.units))

    for var in ds.variables:
        if var in variables:
            tp = ds.variables[var]
            for i in indices:
                i0, i1 = i[0], i[1]
                tp_ij = tp[:, i0, i1] * 1000.0
                df[var + str(i0) + '_' + str(i1)] = tp_ij
    return df


def test():
    nc = 'E:/Projects/RS/ECMWF/ERA-Interim/_grib2netcdf-atls17-95e2cf679cd58ee9b4db4dd119a05a8d-Ahj8Z1.nc'
    shp = 'E:/Projects/RS/ECMWF/ERA-Interim/_grib2netcdf-atls17-95e2cf679cd58ee9b4db4dd119a05a8d-Ahj8Z1.shp'
    csv = 'E:/Projects/RS/ECMWF/ERA-Interim/_grib2netcdf-atls17-95e2cf679cd58ee9b4db4dd119a05a8d-Ahj8Z1.csv'

    ds = Dataset(nc, 'r')
    print ds.variables

    bbox = [5.25, 49.5, 9.75, 52.5]
    lonlat, lonlat_idx = get_lon_lat(nc, bbox)
    # create_shapefile(lonlat, lonlat_idx, shp)

    df = create_time_series(nc, lonlat_idx, [u'tp'])
    df.to_csv(csv, sep=';')
    # ds = Dataset(fn, 'r')
    # print ds.variables
    # latlon = [(lon, lat) for lat in np.squeeze(ds.variables[u'latitude']) for lon in np.squeeze(ds.variables[u'longitude'])]

    # type = ds.variables['time']
    # df = pd.DataFrame(index=num2date(type[:], type.units))
    # print df
    # df_list = [pd.DataFrame(index=num2date(type[:], type.units)) for c in latlon]
    # for var in [u'tas', u'vas', u'huss', u'ps', u'uas', u'pr', u'rsds', u'rlds']:
    #     v = np.reshape(np.squeeze(ds.variables[var]), (7305, n))
    #     for i in range(n):
    #         df_list[i][var] = v[:, i]
    # for i, df in enumerate(df_list):
    #     ll = '_{0:.3f}'.format(latlon[i][0]) + '_{0:.3f}'.format(latlon[i][1])
    #     df.to_csv(os.path.splitext(fn)[0] + ll + '.csv', sep=';')
    # return df_list



test()