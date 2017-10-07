import bz2
import datetime
import gzip
import os
import tempfile
import zlib

import download
import numpy as np
from girs.rast.parameter import RasterParameters, get_parameters
from girs.rast.raster import RasterReader, RasterWriter
from girs.rast.resample import resample
from girs.rastfeat.clip import clip_by_vector
from netCDF4 import Dataset
from osgeo import gdal, osr


def default_get_raster_file_names(sarp_filename, raster_filename, suffix, overwrite):
    for s in suffix:
        if sarp_filename.endswith(s):
            raster_filename = raster_filename.replace(s, '.tif')
            return [raster_filename] if (overwrite or not os.path.isfile(raster_filename)) else None
    print sarp_filename, raster_filename, suffix, overwrite
    raise Exception('ERROR in rasterize_files')


class Rasterizer(object):

    def __init__(self, product_dir, output_raster_dir, suffix, clip_layer=None, resample_sizes=None,
                 overwrite=False, verbose=False):
        self.product_dir = os.path.normpath(product_dir)
        self.output_raster_dir = os.path.normpath(output_raster_dir)
        self.suffix = tuple(suffix)
        self.clip_layer = clip_layer
        self.resample_sizes = resample_sizes
        self.overwrite = overwrite
        self.verbose = verbose
        self.all_touched = False

    def get_local_files(self):
        filenames = []
        for root, dirs, files in os.walk(self.product_dir):
            if files:
                root = os.path.normpath(root)
                filenames += [os.path.join(root, f) for f in files if f.endswith(self.suffix)]
        return sorted(filenames)

    def get_rasters(self, product_filename):
        """A product file contains one or more rasters. For instance, a 30-minute product delivered once per hour
        contains two half-hour rasters per file

        This is the default method, which should be overloaded if the product_filename is not a tif file.
        It creates just a dataset copy of the product_filename.

        :param product_filename: full path name of th product file
        :return: list tuples [output_filename, RasterRead] objects
                output_filename is obtained from the product_filename by substituting product_dir by output_raster_dir
                output_dataset in in the memory (driver='MEM')
        """
        output_filename = os.path.relpath(product_filename, self.product_dir)
        output_filename = os.path.splitext(output_filename)
        if output_filename[1] in ['.gz', '.Z', 'bz2']:
            output_filename = os.path.splitext(output_filename[0])
        output_filename = os.path.join(self.output_raster_dir, output_filename[0]) + '.tif'
        result = []
        if self.overwrite or not os.path.isfile(output_filename):
            result.append([output_filename, RasterReader(product_filename)])
        for r in result:
            yield r

    @staticmethod
    def read_compressed_file(filename):
        s = os.path.splitext(filename)
        if '.bz2' in s[-1]:
            with open(filename, 'rb') as f:
                return bz2.decompress(f.read())
        elif '.gz' in s[-1]:
            gf = gzip.GzipFile(filename, 'rb')
            d = gf.read()
            gf.close()
            return d
        elif '.Z' in s[-1]:
            with open(filename) as f:
                return zlib.decompress(f.read())
        else:
            raise Exception('Rasterizer.read_compressed_file: file type unknown ({}).'.format(filename))

    def rasterize_folder(self, verbose=False, overwrite=False):
        gdal.PushErrorHandler('CPLQuietErrorHandler')
        self.verbose = verbose
        self.overwrite = overwrite
        product_filenames = self.get_local_files()
        print '{} product files found'.format(len(product_filenames))
        dt1 = datetime.datetime.now()
        n = len(str(len(product_filenames)))
        for i, product_filename in enumerate(product_filenames):
            if self.rasterize_file(product_filename):
                print '{} of {}: {}'.format(str(i+1).zfill(n), len(product_filenames), os.path.basename(product_filename))
        print 'done', '{:3.2f}'.format((datetime.datetime.now() - dt1).total_seconds()), 'seconds.'
        gdal.PopErrorHandler()

    def rasterize_file(self, input_filename):

        if not os.path.exists(self.output_raster_dir):
            os.makedirs(self.output_raster_dir)
        found = False
        for output_filename, input_raster in self.get_rasters(input_filename):  # also using yield
            output_dir1 = os.path.dirname(output_filename)  # in case there are sub-dirs
            if not os.path.isdir(output_dir1):
                os.makedirs(output_dir1)
            if self.resample_sizes:
                if self.clip_layer:
                    clip_by_vector(resample(input_raster, self.resample_sizes), self.clip_layer,
                                   output_raster=output_filename, driver='GTiff', all_touched=self.all_touched)
                else:
                    resample(input_raster, self.resample_sizes, output_raster=output_filename, driver='GTiff')
            else:
                if self.clip_layer:
                    clip_by_vector(input_raster, self.clip_layer, output_raster=output_filename, driver='GTiff',
                                   all_touched=self.all_touched)
                else:
                    self.save_as(input_raster, output_filename)
            found = True
        return found

    @staticmethod
    def open_raster(input_raster):
        compressed = False
        try:
            if input_raster.endswith('.zip'):
                dataset = gdal.Open('/vsizip/' + input_raster + '/' + os.path.basename(input_raster[:-4]))
                compressed = True
            elif input_raster.endswith('.gz'):
                dataset = gdal.Open('/vsigzip/' + input_raster)
                compressed = True
            else:
                dataset = gdal.Open(input_raster)
        except Exception:
            dataset = input_raster
        return dataset, compressed

    @staticmethod
    def create_dataset(raster_parameters, arr, output_filename):
        output_raster = RasterWriter(output_filename, raster_parameters)
        for i in range(raster_parameters.number_of_bands):
            if raster_parameters.nodata[i]:
                output_raster.set_array(arr, i+1)

        # output_raster.dataset.FlushCache()
        # driver_code = raster_parameters.driverShortName
        # driver = gdal.GetDriverByName(driver_code)
        # dataset_out = driver.Create(output_filename, raster_parameters.RasterXSize, raster_parameters.RasterYSize,
        #                             raster_parameters.number_of_bands, raster_parameters.data_types[0])
        # dataset_out.SetGeoTransform(raster_parameters.geo_trans)
        # dataset_out.SetProjection(raster_parameters.srs)
        # for i in range(raster_parameters.number_of_bands):
        #     if raster_parameters.nodata[i]:
        #         rb_out = dataset_out.GetRasterBand(i+1)
        #         rb_out.SetNoDataValue(raster_parameters.nodata[i])
        # dataset_out.GetRasterBand(1).WriteArray(arr)
        # dataset_out.FlushCache()
        return output_raster

    @staticmethod
    def save_as(input_raster, output_filename, zip=False):
        input_raster.copy(output_filename)


def get_config_dict():
    from warsa.precipitation.satellite.arc2.rasterize import ARC2AfricaBinRasterize, ARC2AfricaTifRasterize
    from warsa.precipitation.satellite.rfe.rasterize import RFE2AfricaBinRasterize, RFE2AfricaTifRasterize, \
        RFE2AsiaBinRasterize
    from warsa.precipitation.satellite.chirps.rasterize import Chirps20GlobalDaily05TifRasterize, \
        Chirps20GlobalDaily25TifRasterize
    from warsa.precipitation.satellite.cmorph.rasterize import CMorphV0x8km30minRasterize, CMorphV0x025deg3hlyRasterize,\
        CMorphV0x025degDailyRasterize, CMorphV1x8km30minRasterize, CMorphV1x025deg3hlyRasterize, \
        CMorphV1x025degDailyRasterize
    from warsa.precipitation.satellite.gpm.rasterize import GPMImerg3BHHRearlyRasterize, GPMImerg3BHHRlateRasterize, \
        GPMImerg3BHHRv03Rasterize, GPMImerg3BHHRv04Rasterize, GPMImerg3BMOv03Rasterize, GPMImerg3BMOv04Rasterize, \
        GPMImerg3Bv03Rasterize, GPMImergGIS3BDailyV03Rasterize, GPMImergGIS3BDailyV04Rasterize, \
        GPMImergGIS3BHHRv03Rasterize, GPMImergGIS3BHHRv04Rasterize, GPMImergGIS3BMOv03Rasterize, \
        GPMImergGIS3BMOv04Rasterize
    from warsa.precipitation.satellite.trmm.rasterize import TRMMnascom3B42RTv7x3hRasterize, \
        TRMMnascom3B42V7x3hRasterize, TRMMnascom3B42V7xDailyRasterize, TRMMopen3B40RTv7x3hRasterize, \
        TRMMopen3B41RTv7x3hRasterize, TRMMopen3B42RTv7x3hGISRasterize, TRMMopen3B42RTv7x3hRasterize, \
        TRMMopen3B42v7x3hGISRasterize, TRMMopen3B42v7x3hRasterize

    config_dict = {
        'ARC2Africa': {
            'BIN': ARC2AfricaBinRasterize,
            'TIF': ARC2AfricaTifRasterize
        },
        'RFE2': {
            'AFRICA_BIN': RFE2AfricaBinRasterize,
            'AFRICA_TIF': RFE2AfricaTifRasterize,
            'ASIA_BIN': RFE2AsiaBinRasterize
        },
        'Chirps20': {
            'GLOBAL_DAILY_05_TIF': Chirps20GlobalDaily05TifRasterize,
            'GLOBAL_DAILY_25_TIF': Chirps20GlobalDaily25TifRasterize
        },
        'CMorph': {
            'V0X_8KM_30MIN': CMorphV0x8km30minRasterize,
            'V0X_025DEG_3HLY_, Rasterize': CMorphV0x025deg3hlyRasterize,
            'V0X_025DEG_DAILY': CMorphV0x025degDailyRasterize,
            'V1X_8KM_30MIN': CMorphV1x8km30minRasterize,
            'V1X_025DEG_3HLY': CMorphV1x025deg3hlyRasterize,
            'V1X_025DEG_DAILY': CMorphV1x025degDailyRasterize
        },
        'GPMImerg': {
            '3B_HHR_V03': GPMImerg3BHHRv03Rasterize,
            '3B_HHR_V04': GPMImerg3BHHRv04Rasterize,
            '3B_MO_V03': GPMImerg3BMOv03Rasterize,
            '3B_MO_V04': GPMImerg3BMOv04Rasterize,
            '3B_HHR_EARLY': GPMImerg3BHHRearlyRasterize,
            '3B_HHR_LATE': GPMImerg3BHHRlateRasterize,
            'GIS_3B_HHR_V03': GPMImergGIS3BHHRv03Rasterize,
            'GIS_3B_DAILY_V03': GPMImergGIS3BDailyV03Rasterize,
            'GIS_3B_MO_V03': GPMImergGIS3BMOv03Rasterize,
            'GIS_3B_HHR_V04': GPMImergGIS3BHHRv04Rasterize,
            'GIS_3B_DAILY_V04': GPMImergGIS3BDailyV04Rasterize,
            'GIS_3B_MO_V04': GPMImergGIS3BMOv04Rasterize
        },
        'TRMMnascom': {
            '3B42RT_V7X_3H_NC4': TRMMnascom3B42RTv7x3hRasterize,
            '3B42RT_V7X_3H_BIN': None,
            '3B42_V7X_3H_HD5': TRMMnascom3B42V7x3hRasterize,
            '3B42_V7X_3H_HD5Z': None,
            '3B42_V7X_DAILY_NC4': TRMMnascom3B42V7xDailyRasterize,
            '3B42_V7X_DAILY_BIN': None
        },
        'TRMMopen': {
            '3B40RT_V7X_3H': TRMMopen3B40RTv7x3hRasterize,
            '3B41RT_V7X_3H': TRMMopen3B41RTv7x3hRasterize,
            '3B42RT_V7X_3H': TRMMopen3B42RTv7x3hRasterize,
            '3B42RT_V7X_3H_GIS': TRMMopen3B42RTv7x3hGISRasterize,
            '3B42_V7X_3H': TRMMopen3B42v7x3hRasterize,
            '3B42_V7X_3H_GIS': TRMMopen3B42v7x3hGISRasterize
        }
    }
    return config_dict


def rasterize_all(raster_root_dir, sarp_list, basin_filename=None, download_conf=None):
    # Use it only to get the download class.
    config_dict = get_config_dict()

    if not download_conf:
        download_conf = download.read_config()

    download_root_dir = download_conf.get('SatellitePrecipitationDownload', 'root_dir')
    for section, option, folder in download.get_download_folder(sarp_list, download_conf):
        download_dir = os.path.join(download_root_dir, folder)
        raster_dir = os.path.join(raster_root_dir, folder)
        rasterize_class = config_dict[section][option]
        rc = rasterize_class(download_dir, raster_dir, clip_layer=basin_filename)
        rc.all_touched = True
        rc.rasterize_folder(verbose=True)
