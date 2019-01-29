import os
import time
import datetime
import collections
import numpy as np
import pandas as pd
from dateutil import relativedelta
from osgeo import gdal, osr
from calendar import monthrange
from osgeo import ogr
from girs.srs import srs_from_wkt
from girs.feat.geom import create_point, create_polygon
from girs.feat.layers import LayersWriter
from girs.rast.parameter import RasterParameters
from girs.rast.raster import RasterReader, RasterWriter
from girs.rastfeat.clip import clip_by_vector
from ftplib import FTP, error_perm
import pygrib

# See: https://data.nodc.noaa.gov/cgi-bin/iso?id=gov.noaa.ncdc:C00877
# https://www.ncei.noaa.gov/thredds/catalog/model-cfs-allfiles/cfsv2_forecast_mm_9mon/catalog.html


def _get_dirs(ftp, ftp_dir, valid_dir):
    lines = []
    ftp.cwd(ftp_dir)
    ftp.dir(lines.append)
    for line in lines:
        if line.startswith('d'):
            try:
                sub_dir = line.split()[-1]
                if valid_dir(sub_dir):
                    yield '/'.join([ftp_dir, sub_dir])
            except error_perm, _:
                print 'Folder {} not found'.format(ftp_dir)


def _ftp_files(ftp=None, ftp_dir=None, last_file=None):
    """

    :param ftp: ftp instance: ftplib.FTP()
    :param ftp_dir: root dir on the server (/modeldata/cfsv2_forecast_mm_9mon)
    :param last_file: last downloaded file (e.g., flxf.01.2011040100.201104.avrg.grib.grb2) as found on the local disk
    :return:
    """
    dt_y = dt_ym = dt_ymd = dt_ymdh = datetime.datetime(1900, 1, 1)
    suffix = '.avrg.grib.grb2'
    if last_file:
        dt = datetime.datetime.strptime(last_file.split('.')[2], '%Y%m%d%H%M')
        dt_y = datetime.datetime(dt.year, 1, 1)
        dt_ym = datetime.datetime(dt.year, dt.month, 1)
        dt_ymd = datetime.datetime(dt.year, dt.month, dt.day)
        dt_ymdh = datetime.datetime(dt.year, dt.month, dt.day, dt.hour)

    for y_dir in _get_dirs(ftp, ftp_dir, lambda d: datetime.datetime.strptime(d, '%Y') >= dt_y):
        for ym_dir in _get_dirs(ftp, y_dir, lambda d: datetime.datetime.strptime(d, '%Y%m') >= dt_ym):
            for ymd_dir in _get_dirs(ftp, ym_dir, lambda d: datetime.datetime.strptime(d, '%Y%m%d') >= dt_ymd
                                                            and d.endswith('01')):
                for ymdh_dir in _get_dirs(ftp, ymd_dir, lambda d: datetime.datetime.strptime(d, '%Y%m%d%H') >= dt_ymdh
                                                                  and d.endswith('00')):
                    prefix = 'flxf.01.{}'.format(os.path.basename(ymdh_dir))
                    lines = []
                    ftp.cwd(ymdh_dir)
                    ftp.dir(lines.append)
                    for line in lines:
                        if not line.startswith('d'):
                            f = os.path.basename(line.split()[-1])  # basename for link (l)
                            if f.startswith(prefix) and f.endswith(suffix):
                                ftp_file = '/'.join([ymdh_dir, f])
                                yield '/' + '/'.join([f for f in ftp_file.split('/') if f])


def download_cfsv2_reforecast_ts_9mon_prate(cfs_dir, email_address):
    """
    http://cfs.ncep.noaa.gov/cfsv2.info/CFSv2.Reforecast.Datasets.Whitepaper.doc

    Download from CFS Reforecast "High-Priority" Subset
    Product: Time Series from 9-Month Runs
    Grid/Scale: Various
    Period of Record: 12Dec1981-31Mar2011
    Model Cycle: 00Z, 06Z, 12Z, 18Z cycles, 1 out of 5 days
    Output Timestep: 6-Hourly, out ~9 months

    :param cfs_dir:
    :param email_address:
    :return:
    """
    #  ftp://nomads.ncdc.noaa.gov/modeldata/cfsv2_forecast_mm_9mon/
    ftp_host = 'nomads.ncdc.noaa.gov'
    ftp_dir = '/modeldata/cfs_reforecast_6-hourly_9mon_flxf/'
    ftp_timeout = 600
    ftp = None

    if not cfs_dir.endswith('/'):
        cfs_dir = cfs_dir + '/'

    if not os.path.isdir(cfs_dir):
        os.makedirs(cfs_dir)

    def f_cmp(f0, f1):
        fs0 = f0.split('.')
        fs1 = f1.split('.')
        if fs0[2] == fs1[2]:
            return fs0[3] > fs1[3]
        else:
            return fs0[2] > fs1[2]

    files = [files for _, _, files in os.walk(cfs_dir) if files]
    last_file = sorted([f for f_list in files for f in f_list if f.endswith('.grb2')], cmp=f_cmp)
    if last_file:
        last_file = max(last_file)
    else:
        last_file = None
    try:
        print 'FTP-login...'
        time0 = time.time()
        ftp = FTP(ftp_host, timeout=ftp_timeout)
        ftp.login('anonymous', email_address)
        print 'done in {} seconds'.format(time.time() - time0)
        for ftp_file in _ftp_files(ftp, ftp_dir, last_file=last_file):
            time0 = time.time()
            local_filename = ftp_file.replace(ftp_dir, cfs_dir)
            print 'Downloading {} to {}:'.format(ftp_file, local_filename),
            if not os.path.isdir(os.path.dirname(local_filename)):
                os.makedirs(os.path.dirname(local_filename))
            downloaded = True
            with open(local_filename, "wb") as bfile:
                try:
                    resp = ftp.retrbinary('RETR ' + ftp_file, callback=bfile.write)
                    resp = 'OK' if resp == '226 Transfer complete.' else resp
                    print '{}; {:.2f} seconds'.format(resp, time.time() - time0)
                except Exception, e:
                    print e
                    downloaded = False
            if not downloaded:
                if os.path.isfile(local_filename):
                    os.remove(local_filename)
                print 'in {} seconds (failed) '.format(time.time() - time0)
    finally:
        if ftp:
            ftp.close()


def extract_precipitation_from_grib2(f_in, f_out, layers=None, **kwargs):
    """Extracts band 31 ('PRATE') from r_in (grb2) and save it into a raster file (tif)

    :param f_in: directory of the monthly cfsr files
    :param f_out: directory of the monthly precipitation rasters
    :param layers:
    :param kwargs:  see clip_by_vector
    :return:
    """
    if not os.path.isdir(os.path.dirname(f_out)):
        os.makedirs(os.path.dirname(f_out))

    dt = datetime.datetime.strptime(os.path.basename(f_in).split('.')[2], '%Y%m%d%H')
    n_secs = monthrange(dt.year, dt.month)[1] * 86400  # Number of seconds in the month
    grbs = pygrib.open(f_in)
    grb = grbs.select(name='Precipitation rate')[0]
    assert grb['dataDate'] == int(dt.strftime('%Y%m%d'))
    assert grb['angleDivisor'] == 1000000
    assert grb['latitudeOfFirstGridPoint'] == 89277000
    assert grb['latitudeOfLastGridPoint'] == -89277000
    assert grb['longitudeOfFirstGridPoint'] == 0
    assert grb['longitudeOfLastGridPoint'] == 359062000
    assert grb['Ni'] == 384
    assert grb['Nj'] == 190
    lat0 = 89.27671288
    lat1 = -89.27671287810583
    lon0 = 0.0
    lon1 = 359.062000
    raster_y_size = 190
    raster_x_size = 384
    dx = (lon1 - lon0) / (raster_x_size - 1)
    dy = (lat0 - lat1) / (raster_y_size - 1)
    geo_trans = (-180.0 - dx/2.0, dx, 0.0, lat0 + dy/2.0, 0.0, -dy)
    arr = grb['values'] * 1#n_secs
    arr = np.append(arr[:, raster_x_size / 2:], arr[:, :raster_x_size / 2], axis=1)
    srs = 'GEOGCS["Coordinate System imported from GRIB file",DATUM["unknown",SPHEROID["Sphere",6371229,0]],' +\
          'PRIMEM["Greenwich",0],UNIT["degree",0.0174532925199433]]'
    number_of_bands = 1
    nodata = grb['missingValue']
    data_types = [gdal.GDT_Float64]
    rp = RasterParameters(raster_x_size, raster_y_size, geo_trans, srs, number_of_bands, nodata, data_types)

    if not layers:
        rp.driverShortName = 'GTiff'
        r_out = RasterWriter(rp, source=f_out)
        r_out.set_array(arr)
    else:
        rp.driverShortName = 'MEM'
        r_mem = RasterWriter(rp)
        r_mem.set_array(arr)
        r_mem.dataset.FlushCache()
        kwargs['output_raster'] = f_out
        clip_by_vector(r_mem, layers, **kwargs)


def extract_all_precipitation(cfsr_dir, prec_dir, layers=None, **kwargs):
    """Calls extract_precipitation for each grib2 file

    :param cfsr_dir: directory of the monthly cfsr files
    :param prec_dir: directory where extracted monthly precipitation rasters in tif-format are saved
    :param layers: used to clip the rasters if given
    :return:
    """
    if not os.path.isdir(prec_dir):
        os.makedirs(prec_dir)
    time00 = time.time()
    print 'Extracting precipitation from {}:'.format(cfsr_dir)
    for f_in in sorted([os.path.join(r, f) for r, d, ff in os.walk(cfsr_dir) for f in ff
                        if f. endswith('.avrg.grib.grb2')]):
        f_out = f_in.replace('flxf.01.', 'pdepth_cfs.').replace('.avrg.grib.grb2', '.tif')
        f_out = f_out.replace(cfsr_dir, prec_dir)
        if not os.path.isfile(f_out):
            time0 = time.time()
            print 'Extracting precipitation to {}:'.format(f_out),
            extract_precipitation_from_grib2(f_in, f_out, layers, **kwargs)
            print 'finished in {} seconds.'.format(time.time() - time0)
    print 'Extracting precipitation finished in {}:'.format(time.time() - time00),


def create_shapefile_centroids(prec_dir, shp):
    """Create a shapefile with id composed of lon and lat: 'P{:05d}_{:04d}'.format(int(lon*100), int(lat*100)), as well
    as the fields lon and lat

    :param prec_dir: folder where precipitation in tif-format is stored
    :param shp: output file name
    :return:
    """
    for r, d, f_list in os.walk(prec_dir):
        for f in [f for f in f_list if f.endswith('.tif')]:
            f = os.path.join(r, f)
            r = RasterReader(f)
            arr = r.get_array()
            nodata = r.get_nodata()
            apc = r.get_pixel_centroid_coordinates()
            lrs = LayersWriter(source=shp)
            lyr = lrs.create_layer('raster', prj=srs_from_wkt(r.get_coordinate_system()), geom=ogr.wkbPoint)
            lyr.CreateField(ogr.FieldDefn('id', ogr.OFTString))
            lyr.CreateField(ogr.FieldDefn('lon', ogr.OFTReal))
            lyr.CreateField(ogr.FieldDefn('lat', ogr.OFTReal))
            ldf = lyr.GetLayerDefn()
            for ir, row in enumerate(apc[:]):
                for ic, col in enumerate(row[:]):
                    v = arr[ir][ic]
                    if v != nodata:
                        feat = ogr.Feature(ldf)
                        x, y = col.tolist()
                        p = create_point(x, y)
                        feat.SetGeometry(p)
                        xx, yy = int(x * 100), int(y * 100)
                        fid = '{:05d}{}_{:04d}{}'.format(abs(xx), 'E' if xx >= 0 else 'W',
                                                         abs(yy), 'N' if yy >= 0 else 'S')
                        feat.SetField("id", fid)
                        feat.SetField("lon", x)
                        feat.SetField("lat", y)
                        lyr.CreateFeature(feat)
            return


def create_shapefile_polygons(prec_dir, shp):
    """Create a shapefile with id composed of lon and lat: 'P{:05d}_{:04d}'.format(int(lon*100), int(lat*100)), as well
    as the fields lon and lat

    :param prec_dir: folder where precipitation in tif-format is stored
    :param shp: output file name
    :return:
    """
    for r, d, f_list in os.walk(prec_dir):
        for f in [f for f in f_list if f.endswith('.tif')]:
            f = os.path.join(r, f)
            r = RasterReader(f)
            arr = r.get_array()
            nodata = r.get_nodata()
            apc = r.get_pixel_centroid_coordinates()
            dx, dy = r.get_pixel_size()
            dx, dy = dx / 2.0, dy / 2.0
            lrs = LayersWriter(source=shp)
            lyr = lrs.create_layer('raster', prj=srs_from_wkt(r.get_coordinate_system()), geom=ogr.wkbPolygon)
            lyr.CreateField(ogr.FieldDefn('id', ogr.OFTString))
            lyr.CreateField(ogr.FieldDefn('lon', ogr.OFTReal))
            lyr.CreateField(ogr.FieldDefn('lat', ogr.OFTReal))
            ldf = lyr.GetLayerDefn()
            for ir, row in enumerate(apc[:]):
                for ic, col in enumerate(row[:]):
                    v = arr[ir][ic]
                    if v != nodata:
                        feat = ogr.Feature(ldf)
                        x, y = col.tolist()
                        x_min = x - dx
                        x_max = x + dx
                        y_min = y - dy
                        y_max = y + dy
                        poly = [[(x_min, y_min), (x_max, y_min), (x_max, y_max), (x_min, y_max), (x_min, y_min)]]
                        p = create_polygon(poly)
                        feat.SetGeometry(p)
                        xx, yy = int(x * 100), int(y * 100)
                        fid = '{:05d}{}_{:04d}{}'.format(abs(xx), 'E' if xx >= 0 else 'W',
                                                         abs(yy), 'N' if yy >= 0 else 'S')
                        feat.SetField("id", fid)
                        feat.SetField("lon", x)
                        feat.SetField("lat", y)
                        lyr.CreateFeature(feat)
            return


def create_timeseries(prec_dir, ts_dir, forecast_months):
    """

    :param prec_dir: directory with sub-directories containing precipitation tif-files
    :param ts_dir: directory of resulting time-series
    :param forecast_months: number of forecast months
    :return:
    """
    ts_dir = os.path.join(ts_dir, '{:02d}_months_forecast'.format(forecast_months))
    if not os.path.isdir(ts_dir):
        os.makedirs(ts_dir)
    index = list()
    precipitation = collections.OrderedDict()  # 'pdepth_cfs_00months
    for r, d, f_list in os.walk(prec_dir):
        for f in [f for f in f_list if f.endswith('.tif')]:
            dt = f.split('.')[1:3]
            dt0 = datetime.datetime.strptime(dt[0], '%Y%m%d%H')
            dt1 = datetime.datetime.strptime(dt[1], '%Y%m')
            n_months = relativedelta.relativedelta(dt1, dt0).months
            if n_months != forecast_months:
                continue
            index.append(dt1)
            f = os.path.join(r, f)
            r = RasterReader(f)
            arr = r.get_array()
            nodata = r.get_nodata()
            apc = r.get_pixel_centroid_coordinates()
            for ir, row in enumerate(apc[:]):
                for ic, col in enumerate(row[:]):
                    x, y = col.tolist()
                    xx, yy = int(x * 100), int(y * 100)
                    fid = '{:05d}{}_{:04d}{}'.format(abs(xx), 'E' if xx >= 0 else 'W', abs(yy), 'N' if yy >= 0 else 'S')
                    if fid not in precipitation:
                        precipitation[fid] = list()
                    v = arr[ir][ic]
                    precipitation[fid].append(v if v != nodata else np.NaN)
    df = pd.DataFrame(precipitation, index=index)
    df = df.dropna(axis=1, how='all').round(0)
    if len(df) > 0:
        for c in df.columns:
            f_out = os.path.join(ts_dir, 'pdepth_cfsv2_{:02d}_months_{}.csv'.format(forecast_months, c))
            df1 = df[c]
            df1 = df1.dropna().round(0)
            df1.name = 'P'
            df1.index.name = 'Date'
            df1.to_csv(f_out, sep=';', header=True)

