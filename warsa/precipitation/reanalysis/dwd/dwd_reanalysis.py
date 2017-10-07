__author__ = 'roehrig'
# ftp://ftp.dwd.de/pub/data/gpcc/full_data/full_data_v7_05.nc.gz

import os
import numpy as np
import pandas as pd
from netCDF4 import Dataset, num2date
import ogr
import osr


class FullDataV0705(object):

    def __init__(self, filename,
                 min_lon=-180.0, max_lon=180.0, min_lat=-90.0, max_lat=90.0):
        self.filename = filename
        self.min_lon = min_lon
        self.max_lon = max_lon
        self.min_lat = min_lat
        self.max_lat = max_lat
        self._time = None
        self._longitudes = None
        self._latitudes = None
        self._precipitations = None
        self.dataset = Dataset(self.filename, 'r')

    def get_time(self):
        if self._time is None:
            t = self.dataset.variables['time']
            self._time = num2date(t[:], t.units)
        return self._time

    def get_longitudes(self):
        if self._longitudes is None:
            self._longitudes = self.dataset.variables['lon'][:]
        return self._longitudes

    def get_latitudes(self):
        if self._latitudes is None:
            self._latitudes = self.dataset.variables['lat'][:]
        return self._latitudes

    def get_precipitations(self):
        if self._precipitations is None:
            p = np.squeeze(self.dataset.variables[u'p'])  # time, lat, lon
            lon = self.get_longitudes()
            lat = self.get_latitudes()
            i_lon = np.where((lon <= self.max_lon) & (lon >= self.min_lon))[0]
            i_lat = np.where((lat <= self.max_lat) & (lat >= self.min_lat))[0]
            p = p[:, i_lat[0]:i_lat[-1]+1, i_lon[0]:i_lon[-1]+1]
            self._precipitations = p.swapaxes(0, 2)  # lon, lat, t
        return self._precipitations

    def create_shapefile(self, filename=None):
        if not filename:
            f = os.path.splitext(os.path.basename(self.filename))[0] + '.shp'
            d = os.path.join(os.path.dirname(self.filename), 'gis')
            filename = os.path.join(d, f)
            if not os.path.isdir(d):
                os.mkdir(d)
        sr = osr.SpatialReference()
        sr.ImportFromEPSG(4326)
        driver = ogr.GetDriverByName('ESRI Shapefile')
        if os.path.isfile(filename) and os.stat(filename):
            driver.DeleteDataSource(filename)
        ds = driver.CreateDataSource(filename)

        layer = ds.CreateLayer('', sr, ogr.wkbPoint)
        layer.CreateField(ogr.FieldDefn('id', ogr.OFTString))
        layer.CreateField(ogr.FieldDefn('Latitude', ogr.OFTReal))
        layer.CreateField(ogr.FieldDefn('Longitude', ogr.OFTReal))

        ld = layer.GetLayerDefn()
        for lon in self.get_longitudes():
            str_lon = str(lon) + '_'
            for lat in self.get_latitudes():
                feat = ogr.Feature(ld)
                feat.SetField('id', str_lon + str(lat))
                feat.SetField('Longitude', lon)
                feat.SetField('Latitude', lat)
                point = ogr.Geometry(ogr.wkbPoint)
                point.AddPoint(lon, lat)
                feat.SetGeometry(point)
                layer.CreateFeature(feat)

        ds = layer = feat = point = None

    def get_column_names_and_values(self):
        lon = self.get_longitudes()
        lat = self.get_latitudes()
        i_lon = np.where((lon <= self.max_lon) & (lon >= self.min_lon))[0]
        i_lat = np.where((lat <= self.max_lat) & (lat >= self.min_lat))[0]
        for iLon, pLon in enumerate(self.get_precipitations()):
            lon0 = lon[i_lon[iLon]]
            str_lon = ("%06.2f"%-lon0 + 'E') if lon0 < 0.0 else ("%06.2f"%lon0 + 'W')
            for iLat, pLat in enumerate(pLon):
                if np.sum(pLat > -99999) > 0:  # any value < -99999
                    lat0 = lat[i_lat[iLat]]
                    str_lat = ("%05.2f"%-lat0 + 'S') if lat0 < 0.0 \
                        else ("%05.2f"%lat0 + 'N')
                    col_name = str_lon + '_' +  str_lat
                    yield (col_name, pLat)

    def to_data_frame(self):
        df = pd.DataFrame(index=num2date(self.get_time()[:], self.dataset.variables['time'].units))
        for col_name, precipitations in self.get_column_names_and_values():
            df[col_name] = precipitations
            df[df[col_name]<-99999] = np.nan
        return df

    def to_csv(self, output_dir=None, sep=';', compression=None):
        prefix = os.path.splitext(os.path.basename(self.filename))[0] + '_'
        if not output_dir:
            output_dir = os.path.join(os.path.dirname(self.filename), 'csv')
        if not os.path.isdir(output_dir):
            os.mkdir(output_dir)
        df = pd.DataFrame(index=self.get_time())
        df.index.name = 'Date'
        for col_name, precipitations in self.get_column_names_and_values():
            df['P' + col_name] = precipitations
            filename = os.path.join(output_dir, prefix + col_name + '.csv')
            if compression == 'gzip':
                filename += '.gz'
            elif compression == 'bz2':
                filename += '.bz2'
            df.to_csv(filename, sep=sep, compression=compression)
            del df['P' + col_name]


