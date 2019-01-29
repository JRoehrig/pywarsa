import bz2
import datetime
import gzip
import os
import zlib
from osgeo import gdal
from girs.rast.raster import RasterReader, RasterWriter
from girs.rast.proc import resample
from girs.rastfeat.clip import clip_by_vector


def default_get_raster_file_names(sarp_filename, raster_filename, suffix, overwrite):
    for s in suffix:
        if sarp_filename.endswith(s):
            raster_filename = raster_filename.replace(s, '.tif')
            return [raster_filename] if (overwrite or not os.path.isfile(raster_filename)) else None
    print sarp_filename, raster_filename, suffix, overwrite
    raise Exception('ERROR in rasterize_files')


class Rasterizer(object):

    def __init__(self, product_dir, output_raster_dir, suffix, **kwargs):
        """

        :param product_dir:
        :param output_raster_dir:
        :param suffix:
        :param **kwargs
            :key layers:
            :key layer_number:
            :key resample_sizes:
            :key all_touched: default False
            :key overwrite:
            :key verbose:
        """
        self.product_dir = os.path.normpath(product_dir)
        self.output_raster_dir = os.path.normpath(output_raster_dir)
        if isinstance(suffix, basestring):
            self.suffix = tuple([suffix])
        else:
            self.suffix = tuple(suffix)
        self.layers = kwargs.pop('layers', None)
        self.layer_number = kwargs.pop('layer_number', 0)
        self.extension = kwargs.pop('extension', None)
        self.resample_sizes = kwargs.pop('resample_sizes', None)
        self.overwrite = kwargs.pop('overwrite', None)
        self.verbose = kwargs.pop('verbose', None)
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
            rst = RasterReader(product_filename).copy()
            result.append([output_filename, rst])
        for r in result:
            yield r

    @staticmethod
    def read_compressed_file(filename):
        try:
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
        except IOError, e:
            print 'Unable to read file {}'.format(filename)
            raise e

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
                if self.layers:
                    clip_by_vector(resample(input_raster, self.resample_sizes), self.layers,
                                   output_raster=output_filename, driver='GTiff', all_touched=self.all_touched,
                                   layer_number=self.layer_number)
                else:
                    resample(input_raster, self.resample_sizes, output_raster=output_filename, driver='GTiff')
            else:
                if self.layers:
                    clip_by_vector(input_raster, self.layers, output_raster=output_filename, driver='GTiff',
                                   all_touched=self.all_touched, layer_number=self.layer_number)
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
    def create_dataset(raster_parameters, arr, output_filename=None):
        r_out = RasterWriter(raster_parameters, output_filename)
        for i in range(raster_parameters.number_of_bands):
            if raster_parameters.nodata[i]:
                r_out.set_array(arr, i+1)
        return r_out

    @staticmethod
    def save_as(input_raster, output_filename, zip=False):
        input_raster.copy(output_filename)

