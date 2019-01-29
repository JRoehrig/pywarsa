import os
import urllib2
import zipfile
import ftplib
import time
from osgeo import ogr
from cookielib import CookieJar
from urllib2 import urlopen
from bs4 import BeautifulSoup
from os.path import basename, splitext
from warsa.config import read_config, decrypt
from girs.feat.layers import LayersReader, LayersWriter, FieldDefinition
from girs.feat.geom import create_polygon
from girs.srs import get_srs


# =============================================================================
# SRTM 3 arc
# =============================================================================
def get_srtm_3arc_tile(lon_min, lon_max, lat_min, lat_max):
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


def get_srtm_3arc_tile_names(srtm_source_dir, xmin, xmax, ymin, ymax, scale=0.0):
    if scale != 0.0:
        xmin -= (xmax - xmin) * scale
        xmax += (xmax - xmin) * scale
        ymin -= (ymax - ymin) * scale
        ymax += (ymax - ymin) * scale
    ix_min, ix_max, iy_min, iy_max = get_srtm_3arc_tile(xmin, xmax, ymin, ymax)

    srtm_files = []
    for i in range(ix_min, ix_max+1):
        for j in range(iy_max, iy_min+1):
            fn = os.path.join(srtm_source_dir, 'srtm_' + str(i).zfill(2) + '_' + str(j).zfill(2) + '.zip')
            if os.path.isfile(fn):
                srtm_files.append(fn)
    return srtm_files


def get_srtm_3arc_tile_names_by_layers(srtm_source_dir, layers_filename, scale=0.0):
    lrs = LayersReader(layers_filename)
    xmin, xmax, ymin, ymax = lrs.get_extent()
    if scale != 0.0:
        xmin -= (xmax - xmin) * scale
        xmax += (xmax - xmin) * scale
        ymin -= (ymax - ymin) * scale
        ymax += (ymax - ymin) * scale
    ix_min, ix_max, iy_min, iy_max = get_srtm_3arc_tile(xmin, xmax, ymin, ymax)

    srtm_files = []
    for i in range(ix_min, ix_max+1):
        for j in range(iy_max, iy_min+1):
            fn = os.path.join(srtm_source_dir, 'srtm_' + str(i) + '_' + str(j) + '.zip')
            if os.path.isfile(fn):
                srtm_files.append(fn)
    return srtm_files


def copy_srtm_3arc_tile(srtm_file, srtm_target_dir):
    zf = zipfile.ZipFile(srtm_file)
    prefix = splitext(basename(srtm_file))[0]
    zf.extract(prefix + '.tif', srtm_target_dir)
    zf.extract(prefix + '.hdr', srtm_target_dir)
    zf.extract(prefix + '.tfw', srtm_target_dir)
    return os.path.join(srtm_target_dir, prefix + '.tif')


def copy_srtm_3arc_tiles(srtm_file, srtm_target_dir):
    result = []
    for srtm_file0 in srtm_file:
        result.append(copy_srtm_3arc_tile(srtm_file0, srtm_target_dir))
    return result


def download_srtm_3arc_data(source, target, xmin, xmax, ymin, ymax):
    ix_min, ix_max, iy_min, iy_max = get_srtm_3arc_tile(xmin, xmax, ymin, ymax)
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


def get_srtm_3arc(srtm_dir):
    return [f for f in os.listdir(srtm_dir) if f.endswith('.zip')] if os.path.isdir(srtm_dir) else []


def download_srtm_3arc(target_dir, url='srtm.csi.cgiar.org',
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


# =============================================================================
# SRTM 1 arc
# =============================================================================
def get_srtm_1arcsec_dir():
    config = read_config()
    srtm_dir = config.get('dem', 'dir')
    if not os.path.isdir(srtm_dir):
        os.makedirs(srtm_dir)
    return os.path.join(srtm_dir, 'srtm_1arcsec')


def get_srtm_1arcsec_url():
    # return 'https://e4ftl01.cr.usgs.gov/SRTM/SRTMGL1.003/2000.02.11/'
    # return 'https://e4ftl01.cr.usgs.gov//MODV6_Dal_D/SRTM/SRTMGL1.003/2000.02.11'
    return 'https://e4ftl01.cr.usgs.gov/MEASURES/SRTMGL1.003/2000.02.11/'


def get_srtm_1arcsec_shp():
    srtm_dir = get_srtm_1arcsec_dir()
    gis_dir = os.path.join(srtm_dir, 'gis')
    if not os.path.isdir(gis_dir):
        os.makedirs(gis_dir)
    return os.path.join(gis_dir, 'srtm_1arcsec.shp')


def create_srtm_1arcsec_layers():
    """Create a shapefile from global SRTM 1 arcsecond tiles.

    This function is intended to be called only once in a while, in case the SRTM data on server where changed.
    The resulting layer is the base for all queries.

    The file is saved im local SRTM dir under gis/srtm_1arcsec.shp

    :return:
    """
    srtm_url = get_srtm_1arcsec_url()
    srtm_shp = get_srtm_1arcsec_shp()

    response = urlopen(srtm_url)
    bs = BeautifulSoup(response.read(), 'lxml')
    response.close()
    filenames_source = [a.get('href') for a in bs.find_all('a', href=True)]
    filenames_source = [f for f in filenames_source if f.endswith('hgt.zip')]
    fields = [FieldDefinition("Filename", ogr.OFTString), FieldDefinition("Code", ogr.OFTString)]
    lrs = LayersWriter(['', ogr.wkbPolygon, get_srs(epsg=4326), fields], source=srtm_shp)
    for f in filenames_source:
        lat = float(f[1:3])
        if f[0] == 'S':
            lat = -lat
        lon = float(f[4:7])
        if f[3] == 'W':
            lon = -lon
        tile = [(lon, lat), (lon+1.0, lat), (lon+1.0, lat+1.0), (lon, lat+1.0), (lon, lat)]
        geom = create_polygon(tile)
        lrs.create_feature(geom=geom, Filename=f, Code=f[:7])
        if f[3] == 'W':
            tile = [(lon + 360.0, lat) for lon, lat in tile]
        else:
            tile = [(lon - 360.0, lat) for lon, lat in tile]
        geom = create_polygon(tile)
        lrs.create_feature(geom=geom, Filename=f, Code=f[:7])


def get_srtm_1arcsec_tile_name_from_point(lon, lat):
    """Return the tile indices for given latitude and longitude in WGS84

    :param lon: min. longitude
    :param lat: min. latitude
    :return: []
    """
    from girs.feat.geom import create_point
    lrs_srtm = LayersReader(get_srtm_1arcsec_shp())
    p = create_point(lon, lat)
    df = lrs_srtm.data_frame()
    df['HAS_POINT'] = df['_GEOM_'].apply(lambda g: g.apply('Contains', p))
    filenames = df[df['HAS_POINT']]['Filename'].values
    return filenames[0]


def get_srtm_1arcsec_tile_names_from_extent(lon_min, lon_max, lat_min, lat_max):
    """

    :param lon_min:
    :param lon_max:
    :param lat_min:
    :param lat_max:
    :return:
    """
    from girs.feat.geom import create_polygon
    lrs_srtm = LayersReader(get_srtm_1arcsec_shp())
    p = create_polygon([(lon_min, lat_min), (lon_max, lat_min), (lon_max, lat_max), (lon_min, lat_max),
                        (lon_min, lat_min)])
    df = lrs_srtm.data_frame()
    df['INTERSECTS'] = df['_GEOM_'].apply(lambda g: g.apply('Intersects', p))
    return df[df['INTERSECTS']]['Filename'].values.tolist()


def get_srtm_1arcsec_tile_names_from_layers(layers, **kwargs):
    """Return a list of the basenames of tiles intersecting layers

    :param layers:
    :type layers: LayersSet or filename
    :param kwargs:
        :key layer_number: (int) default is 0
    :return: list of the file names of the tiles intersecting the given layers
    :rtype: list
    """
    layer_number = kwargs.pop('layer_number', 0)
    lrs0 = LayersReader(get_srtm_1arcsec_shp())
    try:
        lrs1 = LayersReader(layers)
    except RuntimeError:
        lrs1 = layers
    return [f.GetField('Filename') for f in lrs0.spatial_filter(lrs1, layer_number=layer_number)]


def download_srtm_1arcsec_from_layers(layers, **kwargs):
    """

    :param layers:
    :param kwargs:
        :key layer_number: (int) default is 0
    :return:
    """
    srtm_filenames = get_srtm_1arcsec_tile_names_from_layers(layers, **kwargs)
    download_srtm_1arcsec_from_tile_names(srtm_filenames)


def download_srtm_1arcsec_from_tile_names(tilenames_source):
    """Download SRTM 1 arcsec files given in filenames_source

    Files are only downloaded if not found in the local SRTM directory

    :param tilenames_source: file names to download
    :type tilenames_source: list of str
    :return:
    """
    if not tilenames_source:
        return
    # See: https://wiki.earthdata.nasa.gov/display/EL/How+To+Access+Data+With+Python
    config = read_config()
    # srtm_url = 'https://e4ftl01.cr.usgs.gov/SRTM/SRTMGL1.003/2000.02.11/'
    # srtm_url = 'https://e4ftl01.cr.usgs.gov//MODV6_Dal_D/SRTM/SRTMGL1.003/2000.02.11'
    srtm_url = 'https://e4ftl01.cr.usgs.gov/MEASURES/SRTMGL1.003/2000.02.11/'
    srtm_usr = config.get('dem', '1arcsec_usr')
    srtm_pwd = config.get('dem', '1arcsec_pwd')
    srtm_dir = get_srtm_1arcsec_dir()

    tilenames_target = [f for f in os.listdir(srtm_dir) if f.endswith('hgt.zip')]
    tilenames_source = set(tilenames_source) - set(tilenames_target)
    print 'Downloading {} SRTM 1 arc files'.format(len(tilenames_source))

    usr, pwd = decrypt(srtm_usr, srtm_pwd)
    password_manager = urllib2.HTTPPasswordMgrWithDefaultRealm()
    password_manager.add_password(None, "https://urs.earthdata.nasa.gov", usr, pwd)
    cj = CookieJar()
    opener = urllib2.build_opener(
        urllib2.HTTPBasicAuthHandler(password_manager),
        # urllib2.HTTPHandler(debuglevel=1),    # Uncomment these two lines to see
        # urllib2.HTTPSHandler(debuglevel=1),   # details of the requests/responses
        urllib2.HTTPCookieProcessor(cj))
    urllib2.install_opener(opener)

    for i, filename_source in enumerate(tilenames_source):
        t0 = time.time()
        print '{}: downloading {}'.format(i+1, filename_source),
        file_url = srtm_url + filename_source
        req = urllib2.Request(file_url)
        response = None
        try:
            response = urllib2.urlopen(req)
            body = response.read()
            with open(os.path.join(srtm_dir, filename_source), 'wb') as f:
                f.write(body)
            print ' done in {} seconds'.format(time.time()-t0)
        finally:
            if response:
                response.close()


def download_srtm_1arcsec():
    """Download all SRTM 1 arcsec

    :return:
    """
    lrs = LayersReader(get_srtm_1arcsec_shp())
    tile_names = lrs.get_field_values('Filename')
    download_srtm_1arcsec_from_tile_names(tile_names)


def merge_srtm_1arcsec_from_layers(layers, **kwargs):
    """

    :param layers:
    :param kwargs:
    :return:
    """
    layer_number = kwargs.pop('layer_number', 0)
    download_srtm_1arcsec_from_layers(layers, layer_number=layer_number)
    tile_names = get_srtm_1arcsec_tile_names_from_layers(layers, layer_number=layer_number)
    return merge_srtm_1arcsec(tile_names, **kwargs)


def merge_srtm_1arcsec(tile_names, **kwargs):
    """

    :param tile_names
    :param kwargs:
        :key output_raster: (str)
    :return:
    """
    from girs.rast.proc import mosaic
    from girs.rast.raster import RasterReader
    output_raster = kwargs.pop('output_raster', None)

    d = get_srtm_1arcsec_dir()
    download_srtm_1arcsec_from_tile_names([f for f in tile_names if not os.path.isfile(os.path.join(d, f))])
    rasters = list()
    for tile_name in tile_names:
        member = '{0}.{2}'.format(*tile_name.split('.'))
        tile_name1 = os.path.join(d, tile_name)
        rasters.append(RasterReader(tile_name1, member=member))
    return mosaic(rasters, output_raster=output_raster)


if __name__ == '__main__':
    pass
    # print get_srtm_1arcsec_dir()
    # print get_srtm_1arcsec_url()
    # create_srtm_1arcsec_layers()
    # print get_srtm_1arcsec_tile_name_from_point(-67.5, -6.5)
    # print get_srtm_1arcsec_tile_names_from_extent(-67.5, -64.5, -6.5, -6.3)
    # download_srtm_1arcsec()
    merge_srtm_1arcsec(['S07W065.SRTMGL1.hgt.zip', 'S07W066.SRTMGL1.hgt.zip',
                        'S07W067.SRTMGL1.hgt.zip', 'S07W068.SRTMGL1.hgt.zip'], output_raster='D:/Temp/srtm.tif')
    # print get_srtm_1arcsec_tile_names_from_extent(-1.5, 1.5, -1.5, 1.5)
    # print get_srtm_1arcsec_tile_names_from_extent(179, -180, -1.5, 1.5)
    # create_srtm_1arcsec_layers()
    # create_srtm_1arcsec_layers(fmt='.json')
    # get_srtm_1arcsec_tile_names_from_layers('D:/tmp/girs/basin_stations/river_basins_wgs84.shp')
    # download_srtm_1arcsec_tile_names_from_layers('D:/tmp/girs/basin_stations/river_basins_wgs84.shp')
    # download_srtm_1arcsec_tile_names_from_layers('D:/sciebo/EasternVisayasIrrigation/data/gis/adm/region8_wgs84.shp')
    # download_srtm_1arc()
