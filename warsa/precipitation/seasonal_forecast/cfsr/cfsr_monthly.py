import os
import time
import datetime
import numpy as np
from osgeo import osr
from calendar import monthrange
from girs.rast.raster import RasterReader, RasterWriter
from girs.rastfeat.clip import clip_by_vector
from ftplib import FTP, error_perm


def ftp_files(ftp=None, ftp_dir=None, last_file=None, prefix=''):
    """flxf01.gdas.197901.grb2
    """
    last_ym = '000000' if not last_file else last_file.split('.')[-2]
    lines = []
    ftp.cwd(ftp_dir)
    ftp.dir(lines.append)
    for line in lines:
        if line.startswith('d'):
            try:
                ym = line.split()[-1]
                datetime.datetime.strptime(ym, '%Y%m')  # except if not a valid folder
                if ym >= last_ym:
                    ftp_dir0 = '/'.join([ftp_dir, ym])
                    lines = []
                    try:
                        ftp.cwd(ftp_dir0)
                        ftp.dir(lines.append)
                    except error_perm, _:
                        print 'Folder {} not found'.format(ftp_dir0)
                    suffix = '{}.grb2'.format(ym)
                    for line0 in lines:
                        if not line0.startswith('d'):
                            f = os.path.basename(line0.split()[-1])  # basename for link (l)
                            if f.startswith(prefix) and f.endswith(suffix) and f.split('.')[-2] > last_ym:
                                ftp_file = '/'.join([ftp_dir0, f])
                                yield '/' + '/'.join([f for f in ftp_file.split('/') if f])
            except ValueError:
                pass


def download_cfsr_hp_monthly_means_flxf(cfsr_dir):
    ftp_host = 'nomads.ncdc.noaa.gov'
    ftp_dir = '/CFSR/HP_monthly_means/'
    ftp_timeout = 600
    ftp = None
    try:
        print 'FTP-login...'
        time0 = time.time()
        ftp = FTP(ftp_host, timeout=ftp_timeout)
        ftp.login()
        print 'done in {} seconds'.format(time.time() - time0)
        for ftp_file in ftp_files(ftp, ftp_dir, prefix='flxf'):
            time0 = time.time()
            local_filename = ftp_file.replace('/CFSR/HP_monthly_means', cfsr_dir)
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


def extract_precipitation(r_in, r_out, layers=None, layer_number=0):
    """Extracts band 31 ('PRATE') from r_in (grb2) and save it into a raster file (tif)

    :param r_in: directory of the monthly cfsr files
    :param r_out: directory of the monthly precipitation rasters
    :param layers:
    :param layer_number:
    :return:
    """
    if not os.path.isdir(os.path.dirname(r_out)):
        os.makedirs(os.path.dirname(r_out))

    ym = r_out.split('.')[-2]
    n_secs = monthrange(int(ym[:4]), int(ym[4:]))[1] * 86400  # Number of seconds in the month

    r = RasterReader(r_in)
    b = r.get_band(31)
    assert b.GetMetadata_Dict()['GRIB_ELEMENT'] == 'PRATE'
    raster_parameters = r.get_parameters()
    raster_parameters.number_of_bands = 1
    arr = r.get_array(31) * n_secs
    nx = raster_parameters.RasterXSize
    arr = np.append(arr[:, nx / 2:], arr[:, :nx / 2], axis=1)

    tran = list(raster_parameters.geo_trans)
    tran[0] = -180.0 + tran[0]
    raster_parameters.geo_trans = tran

    srs = osr.SpatialReference()
    srs.ImportFromEPSG(4326)  # EPSG:4326
    raster_parameters.srs = srs.ExportToWkt()

    if not layers:
        raster_parameters.driverShortName = 'GTiff'
        r0 = RasterWriter(raster_parameters, source=r_out)
        r0.set_array(arr, 1)
        r0.dataset.FlushCache()
    else:
        raster_parameters.driverShortName = 'MEM'
        r_mem = RasterWriter(raster_parameters)
        r_mem.set_array(arr, 1)
        r_mem.dataset.FlushCache()
        clip_by_vector(r_mem, layers, layer_number=layer_number, output_raster=r_out)


def extract_all_precipitation(cfsr_dir, prec_dir, layers):
    """Calls extract_precipitation for each grib2 file

    :param cfsr_dir: directory of the monthly cfsr files
    :param prec_dir: directory of the monthly precipitation rasters
    :param layers:
    :return:
    """
    if not os.path.isdir(prec_dir):
        os.makedirs(prec_dir)
    for d_in in [os.path.join(cfsr_dir, path) for path in os.listdir(cfsr_dir) if os.path.isdir(os.path.join(cfsr_dir, path))]:
        for f_in in [f_in for f_in in os.listdir(d_in) if f_in.startswith('flxf')]:
            time0 = time.time()
            r_out = d_in.replace(cfsr_dir, prec_dir)
            f_out = f_in.replace('flxf', 'pdepth_cfsr').replace('.gdas', '').replace('.grb2', '.tif')
            f_in = os.path.join(d_in, f_in)
            f_out = os.path.join(r_out, f_out)
            if not os.path.isfile(f_out):
                print 'Extracting precipitation from {} to {}:'.format(f_in, f_out),
                extract_precipitation(f_in, f_out, layers)
                print 'finished in {} seconds.'.format(time.time() - time0)


if __name__ == '__main__':
    cfsr_d0 = '/media/win/DATA/GFS/cfsrmon'
    prec_d0 = '/media/win/DATA/GFS/cfsrmon_prec'
    shp = '/media/win/Projects/SaoFranciscoWaterAvailability/Data/GIS/02-Processed/Hydrography/' + \
          'BASE HIDROGRAFICA OTTOCODIFICADA DA BACIA DO RIO SAO FRANCISCO/GEOFT_BHO_AREACONTRIBUICAO_otto3_wgs84.shp'
    # download_flxf(cfsr_d0)
    # extract_all_precipitation(cfsr_d0, prec_d0, shp)
    r = RasterReader('/media/win/DATA/CFS/flxf1983010106.01.1983010100.grb2')
    print r.info()
    arr = r.get_array(31)
    print arr.max()

