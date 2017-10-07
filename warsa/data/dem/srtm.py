import os
import urllib2
import zipfile
import ftplib
import time
from os.path import basename, splitext

from warsa.utils import osu


def get_tile(lon_min, lon_max, lat_min, lat_max):
    """Return the tile indices for given latitude and longitude in WGS84

    :param lon_min: min. latitude
    :param lon_max: max. latitude
    :param lat_min: min. latitude
    :param lat_max: max. latitude
    :return: [idx_lon_min, idx_lon_max, idx_lat_min, idx_lat_max]
    """
    idx_lon_min = (lon_min + 180.0) / 5.0  # 72.0/360.0
    idx_lon_max = (lon_max + 180.0) / 5.0  # 72.0/360.0
    idx_lat_min = (lat_min + 60.0) / 5.0  # 24.0/120.0
    idx_lat_max = (lat_max + 60.0) / 5.0  # 24.0/120.0
    idx_lon_min = int(idx_lon_min) + 1
    idx_lon_max = int(idx_lon_max) + 1
    idx_lat_min = 24 - int(idx_lat_min)
    idx_lat_max = 24 - int(idx_lat_max)
    if idx_lon_min > idx_lon_max:
        idx_lon_min, idx_lon_max = idx_lon_max, idx_lon_min
    if idx_lat_min > idx_lat_max:
        idx_lat_min, idx_lat_max = idx_lat_max, idx_lat_min
    idx_lon_min = max(idx_lon_min, 0)
    idx_lon_max = max(idx_lon_max, 72)
    idx_lat_min = max(idx_lat_min, 0)
    idx_lat_max = max(idx_lat_max, 24)
    return idx_lon_min, idx_lon_max, idx_lat_min, idx_lat_max


def get_tile_names(srtm_source_dir, xmin, xmax, ymin, ymax, scale=0.0):
    if scale != 0.0:
        xmin -= (xmax - xmin) * scale
        xmax += (xmax - xmin) * scale
        ymin -= (ymax - ymin) * scale
        ymax += (ymax - ymin) * scale
    ix_min, ix_max, iy_min, iy_max = get_tile(xmin, xmax, ymin, ymax)

    srtm_files = []
    for i in range(ix_min, ix_max+1):
        for j in range(iy_max, iy_min+1):
            fn = os.path.join(srtm_source_dir, 'srtm_' + str(i).zfill(2) + '_' + str(j).zfill(2) + '.zip')
            if osu.file_exists(fn):
                srtm_files.append(fn)
    return srtm_files


def get_tile_names_by_layers(srtm_source_dir, layers_filename, scale=0.0):
    from warsa.gis.features import feature
    lrs = feature.Layers(layers_filename)
    xmin, xmax, ymin, ymax = lrs.get_extent()
    if scale != 0.0:
        xmin -= (xmax - xmin) * scale
        xmax += (xmax - xmin) * scale
        ymin -= (ymax - ymin) * scale
        ymax += (ymax - ymin) * scale
    ix_min, ix_max, iy_min, iy_max = get_tile(xmin, xmax, ymin, ymax)

    srtm_files = []
    for i in range(ix_min, ix_max+1):
        for j in range(iy_max, iy_min+1):
            fn = os.path.join(srtm_source_dir, 'srtm_' + str(i) + '_' + str(j) + '.zip')
            if osu.file_exists(fn):
                srtm_files.append(fn)
    return srtm_files


def copy_tile(srtm_file, srtm_target_dir):
    zf = zipfile.ZipFile(srtm_file)
    prefix = splitext(basename(srtm_file))[0]
    zf.extract(prefix + '.tif', srtm_target_dir)
    zf.extract(prefix + '.hdr', srtm_target_dir)
    zf.extract(prefix + '.tfw', srtm_target_dir)
    return os.path.join(srtm_target_dir, prefix + '.tif')


def copy_tiles(srtm_file, srtm_target_dir):
    result = []
    for srtm_file0 in srtm_file:
        result.append( copy_tile(srtm_file0, srtm_target_dir) )
    return result


def download_srtm_data(source, target, xmin, xmax, ymin, ymax):
    ix_min, ix_max, iy_min, iy_max = get_tile(xmin, xmax, ymin, ymax)
    filenames_to_download = []
    for ix in range(ix_min, ix_max + 1):
        ix_str = str(ix) if ix > 9 else '0' + str(ix)
        for iy in range(iy_min, iy_max + 1):
            iy_str = str(iy) if iy > 9 else '0' + str(iy)
            filenames_to_download.append('srtm_' + ix_str + '_' + iy_str + '.zip')
    print ix_min, ix_max, iy_min, iy_max, filenames_to_download
    for fn in filenames_to_download:
        serverfile = urllib2.urlopen(source + fn)
        downloaded_file = os.path.join(target, fn)
        output = open(downloaded_file, 'wb')
        output.write(serverfile.read())
        output.close()
        serverfile.close()
        print fn, 'downloaded...'


def get_srtm_3arc_v41(srtm_dir):
    return [f for f in os.listdir(srtm_dir) if f.endswith('.zip')] if os.path.isdir(srtm_dir) else []


def download_srtm_3arc_v41_from_cgiar(target_dir, url='srtm.csi.cgiar.org',
                                      source_dir='/SRTM_V41/SRTM_Data_GeoTiff/'):
    ftp = None
    try:
        ftp = ftplib.FTP(url)
        ftp.cwd(source_dir)
        source_files = []
        ftp.retrlines('LIST', source_files.append)
        source_files = set([d.split()[-1] for d in source_files] if os.path.isdir(target_dir) else [])
        target_files = set(f for f in os.listdir(target_dir) if f.endswith('.zip'))
        files_to_download = sorted(list(source_files - target_files))
        for i, file_name in enumerate(files_to_download):
            dt0 = time.time()
            print '{}: downloading {}'.format(i, file_name),
            with open(os.path.join(target_dir, file_name), 'wb') as srtm_file:
                ftp.retrbinary('RETR %s' % file_name, srtm_file.write)
            print ' done in {} seconds.'.format(time.time() - dt0)
    except Exception, e:
        print e
    finally:
        if ftp:
            ftp.close()


