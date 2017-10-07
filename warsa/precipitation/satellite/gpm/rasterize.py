import os
import numpy as np
from girs.rast.parameter import RasterParameters, get_parameters
from osgeo import gdal, osr
from warsa.precipitation.satellite.rasterize import Rasterizer


class GPMImerg3Bv03Rasterize(Rasterizer):

    def __init__(self, subdataset_number, product_dir, output_raster_dir, suffix, clip_layer=None, resample_sizes=None,
                 overwrite=False, verbose=False):
        super(GPMImerg3Bv03Rasterize, self).__init__(product_dir, output_raster_dir, suffix,
                                                     clip_layer, resample_sizes, overwrite, verbose)
        self.subdataset_number = subdataset_number

    def get_rasters(self, product_filename):
        """From IMERG.doc
        The *grid* on which each field of values is presented is a 0.1degx0.1deg lat./lon. (Cylindrical Equal Distance)
        global array of points. It is size 3600x1800, with X (longitude) incrementing most rapidly West to East from
        the Dateline, and then Y (latitude) incrementing South to North from the southern edge as detailed in the
        metadata. Tenth-degree latitude and longitude values are at grid edges:

        First point center (89.95degS,179.95degW)
        Second point center (89.95degS,179.85degW)
        Last point center (89.95degN,179.95degE)

        The reference datum is WGS84.
        Note that the Day-1 IMERG precipitation estimates are filled with "missing" values outside the
        latitude band 60degN-S, while some of the additional data fields have values at the higher latitudes.

        :param product_filename: full path name of the product file
        :return: list of tuples (output_filename, output_dataset)
                output_filename is obtained from the product_filename by substituting product_dir by output_raster_dir
                output_dataset in in the memory (driver='MEM')
        """
        output_raster = product_filename[:-5] + '.tif'
        output_raster = output_raster.replace(self.product_dir, self.output_raster_dir)
        result = []
        if self.overwrite or not os.path.isfile(output_raster):
            hdf5_dataset = gdal.Open(product_filename, gdal.GA_ReadOnly)
            subdatasets = hdf5_dataset.GetSubDatasets()
            subdataset_name = subdatasets[self.subdataset_number][0]
            prec_dataset = gdal.Open(subdataset_name, gdal.GA_ReadOnly)
            raster_parameters = get_parameters(prec_dataset)
            raster_parameters.RasterXSize, raster_parameters.RasterYSize = \
                raster_parameters.RasterYSize, raster_parameters.RasterXSize
            raster_parameters.driverShortName = 'MEM'
            raster_parameters.geo_trans = [-180, 0.1, 0, 90, 0, -0.1]
            raster_parameters.set_nodata(-9999.9)
            output_dataset = self.create_dataset(raster_parameters, np.rot90(prec_dataset.ReadAsArray()), 'mem')
            result.append([output_raster, output_dataset])
        for r in result:
            yield r


class GPMImerg3BHHRv03Rasterize(GPMImerg3Bv03Rasterize):

    def __init__(self, product_dir, output_raster_dir, clip_layer=None, resample_sizes=None,
                 overwrite=False, verbose=False):
        super(GPMImerg3BHHRv03Rasterize, self).__init__(5, product_dir, output_raster_dir, '.HDF5',
                                                        clip_layer, resample_sizes, overwrite, verbose)


class GPMImerg3BMOv03Rasterize(GPMImerg3Bv03Rasterize):

    def __init__(self, product_dir, output_raster_dir, clip_layer=None, resample_sizes=None,
                 overwrite=False, verbose=False):
        super(GPMImerg3BMOv03Rasterize, self).__init__(1, product_dir, output_raster_dir, '.HDF5',
                                                       clip_layer, resample_sizes, overwrite, verbose)


class GPMImergGISRasterize(Rasterizer):

    def __init__(self, product_dir, output_raster_dir, clip_layer=None, resample_sizes=None,
                 overwrite=False, verbose=False):
        super(GPMImergGISRasterize, self).__init__(product_dir, output_raster_dir, '.tif',
                                                   clip_layer, resample_sizes, overwrite, verbose)

    def get_rasters(self, product_filename):
        for output, raster_in in super(GPMImergGISRasterize, self).get_rasters(product_filename):
            raster_in.set_nodata(-9999.9)
            srs = osr.SpatialReference()
            srs.ImportFromEPSG(4035)  # Authalic WGS84
            raster_in.set_projection(srs.ExportToWkt())
            yield output, raster_in


class GPMImergGIS3BHHRv03Rasterize(GPMImergGISRasterize):

    def __init__(self, product_dir, output_raster_dir, clip_layer=None, resample_sizes=None,
                 overwrite=False, verbose=False):
        super(GPMImergGIS3BHHRv03Rasterize, self).__init__(product_dir, output_raster_dir,
                                                           clip_layer, resample_sizes, overwrite, verbose)


class GPMImergGIS3BDailyV03Rasterize(GPMImergGISRasterize):

    def __init__(self, product_dir, output_raster_dir, clip_layer=None, resample_sizes=None,
                 overwrite=False, verbose=False):
        super(GPMImergGIS3BDailyV03Rasterize, self).__init__(product_dir, output_raster_dir,
                                                             clip_layer, resample_sizes, overwrite, verbose)


class GPMImergGIS3BMOv03Rasterize(GPMImergGISRasterize):

    def __init__(self, product_dir, output_raster_dir, clip_layer=None, resample_sizes=None,
                 overwrite=False, verbose=False):
        super(GPMImergGIS3BMOv03Rasterize, self).__init__(product_dir, output_raster_dir,
                                                          clip_layer, resample_sizes, overwrite, verbose)


class GPMImerg3BHHRv04Rasterize(GPMImerg3Bv03Rasterize):

    def __init__(self, product_dir, output_raster_dir, clip_layer=None, resample_sizes=None,
                 overwrite=False, verbose=False):
        super(GPMImerg3BHHRv04Rasterize, self).__init__(1, product_dir, output_raster_dir, '.HDF5',
                                                        clip_layer, resample_sizes, overwrite, verbose)


class GPMImerg3BMOv04Rasterize(GPMImerg3Bv03Rasterize):

    def __init__(self, product_dir, output_raster_dir, clip_layer=None, resample_sizes=None,
                 overwrite=False, verbose=False):
        super(GPMImerg3BMOv04Rasterize, self).__init__(1, product_dir, output_raster_dir, '.HDF5',
                                                       clip_layer, resample_sizes, overwrite, verbose)


class GPMImergGIS3BHHRv04Rasterize(GPMImergGISRasterize):

    def __init__(self, product_dir, output_raster_dir, clip_layer=None, resample_sizes=None,
                 overwrite=False, verbose=False):
        super(GPMImergGIS3BHHRv04Rasterize, self).__init__(product_dir, output_raster_dir,
                                                           clip_layer, resample_sizes, overwrite, verbose)


class GPMImergGIS3BDailyV04Rasterize(GPMImergGISRasterize):

    def __init__(self, product_dir, output_raster_dir, clip_layer=None, resample_sizes=None,
                 overwrite=False, verbose=False):
        super(GPMImergGIS3BDailyV04Rasterize, self).__init__(product_dir, output_raster_dir,
                                                             clip_layer, resample_sizes, overwrite, verbose)


class GPMImergGIS3BMOv04Rasterize(GPMImerg3Bv03Rasterize):

    def __init__(self, product_dir, output_raster_dir, clip_layer=None, resample_sizes=None,
                 overwrite=False, verbose=False):
        super(GPMImergGIS3BMOv04Rasterize, self).__init__(product_dir, output_raster_dir, '.tif',
                                                          clip_layer, resample_sizes, overwrite, verbose)


class GPMImerg3BHHRearlyRasterize(GPMImerg3Bv03Rasterize):

    def __init__(self, product_dir, output_raster_dir, clip_layer=None, resample_sizes=None,
                 overwrite=False, verbose=False):
        super(GPMImerg3BHHRearlyRasterize, self).__init__(1, product_dir, output_raster_dir, ['.RT-H5'],
                                                          clip_layer, resample_sizes, overwrite, verbose)


class GPMImerg3BHHRlateRasterize(GPMImerg3Bv03Rasterize):

    def __init__(self, product_dir, output_raster_dir, clip_layer=None, resample_sizes=None,
                 overwrite=False, verbose=False):
        super(GPMImerg3BHHRlateRasterize, self).__init__(1, product_dir, output_raster_dir, ['.RT-H5'],
                                                         clip_layer, resample_sizes, overwrite, verbose)


