__author__ = 'roehrig'

import zipfile
from os import walk
import os
import numpy as np
import pandas as pd
import ogr, osr
from netCDF4 import Dataset, num2date


"""
Public access:
ftp://wci.earth2observe.eu/data/primary/public/jrc/MSWEP_V1.0/
username:e2o_guest
password:oowee3WeifuY1aeb
"""

def create_shapefile(nc_file_name, longitudes, latitudes):

    sr = osr.SpatialReference()
    sr.ImportFromEPSG(4326)

    shp = os.path.splitext(nc_file_name)[0] + '.shp'
    driver = ogr.GetDriverByName('ESRI Shapefile')
    if os.path.isfile(shp) and os.stat(shp):
        driver.DeleteDataSource(shp)
    ds = driver.CreateDataSource(shp)

    layer = ds.CreateLayer('', sr, ogr.wkbPoint)
    layer.CreateField(ogr.FieldDefn('id', ogr.OFTString))
    layer.CreateField(ogr.FieldDefn('Latitude', ogr.OFTReal))
    layer.CreateField(ogr.FieldDefn('Longitude', ogr.OFTReal))

    ld = layer.GetLayerDefn()
    for lon in longitudes:
        str_lon = str(lon) + '_'
        for lat in latitudes:
            feat = ogr.Feature(ld)
            feat.SetField('id', str_lon + str(lat))
            feat.SetField('Longitude', lon)
            feat.SetField('Latitude', lat)
            point = ogr.Geometry(ogr.wkbPoint)
            point.AddPoint(lon, lat)
            feat.SetGeometry(point)
            layer.CreateFeature(feat)

    ds = layer = feat = point = None


def read(nc_dir, csv_dir, nc_file, xmin, xmax, ymin, ymax):
    ds = Dataset(os.path.join(nc_dir, nc_file), 'r')
    lon = np.squeeze(ds.variables['lon'])
    lat = np.squeeze(ds.variables['lat'])
    p = ds.variables[u'precipitation']
    t = ds.variables['time']
    # create_shapefile(nc_file, lon, lat)
    df = pd.DataFrame(index=num2date(t[:], t.units))
    a = p.shape
    cnt = len(p) * len(p[0])
    p = np.squeeze(p)
    for iLon, p0 in enumerate(p):
        if not (xmin < lon[iLon] < xmax):
            continue
        str_lon = str(lon[iLon])
        str_lon += 'W_' if str_lon.startswith('-') else 'E_'
        for iLat, p1 in enumerate(p0):
            if not (ymin < lat[iLat] < ymax):
                continue
            cnt -= 1
            if np.count_nonzero(~np.isnan(p1)) > 0:
                str_lat = str(lat[iLat])
                str_lat += 'S' if str_lat.startswith('-') else 'N'
                col_name = str_lon + str_lat
                df[col_name] = p1
                df[df[col_name]<-99999] = np.nan
                fn_prefix_full = os.path.join(csv_dir, 'mswep_' + col_name)
                fn_prefix_full_csv = fn_prefix_full + '.csv'
                if not os.path.isfile(fn_prefix_full_csv):
                    df.to_csv(fn_prefix_full_csv, sep=';', decimal='.', float_format='%.2f')
                else:
                    with open(fn_prefix_full_csv, 'a') as f:
                        df.to_csv(f, header=False, sep=';', decimal='.', float_format='%.2f')



                # fn_prefix_full_zip = fn_prefix_full + '.zip'
                # zf = zipfile.ZipFile(fn_prefix_full_zip, 'w', zipfile.ZIP_DEFLATED)
                # try:
                #     zf.write(fn_prefix_full_csv, os.path.relpath(fn_prefix_full_csv, nc_dir))
                # finally:
                #     zf.close()
                # os.remove(fn_prefix_full_csv)
                del df[col_name]


def read_all_daily(nc_dir, csv_dir, xmin, xmax, ymin, ymax):
    d = os.path.dirname(csv_dir)
    if not os.path.exists(d):
        os.makedirs(d)
    for nc_file in [f for f in os.listdir(nc_dir) if f.endswith('.nc')]:
        print 'Reading', nc_file
        read(nc_dir, csv_dir, nc_file, xmin, xmax, ymin, ymax)

def merge_to_xlsx(csv_dir, output_csv):
    df = None
    for csv_file in [f for f in os.listdir(csv_dir) if f.endswith('.csv')]:
        print 'Concatenating', csv_file
        if df is None:
            df = pd.read_csv(os.path.join(csv_dir, csv_file), sep=';', index_col=0, parse_dates=True)
        else:
            df1 = pd.read_csv(os.path.join(csv_dir, csv_file), sep=';', index_col=0, parse_dates=True)
            df = pd.concat([df, df1], axis=1)
    df.to_csv(output_csv, sep=';', decimal='.', float_format='%.2f')


"""
a daily file has 0.25 degree spatial resolution
For example the fiel 1979.nc:
- longitude: 1440 points
- latitude:  720 points
- daily prec.: 365 points
"""