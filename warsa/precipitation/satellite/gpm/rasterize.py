import os
import time
import datetime
import numpy as np
from calendar import monthrange
from osgeo import gdal, osr
from girs.rast.parameter import get_parameters
from warsa.precipitation.satellite.rasterize import Rasterizer
from netCDF4 import Dataset
from girs.rast.parameter import RasterParameters


class GPMImerg3BRasterize(Rasterizer):
    """

    """

    def __init__(self, subdataset_number, product_dir, output_raster_dir, suffix, **kwargs):
        super(GPMImerg3BRasterize, self).__init__(product_dir, output_raster_dir, suffix, **kwargs)
        self.subdataset_number = subdataset_number

    def get_rasters(self, product_filename):
        """Return raster as precipitation depth (mm)

        From IMERG.doc
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
        output_raster = os.path.normpath(product_filename[:-6] + '.tif')
        output_raster = output_raster.replace(self.product_dir, self.output_raster_dir)
        result = []
        if self.overwrite or not os.path.isfile(output_raster):
            grid = Dataset(product_filename).groups['Grid']
            arr = grid.variables[u'precipitationCal'][:].data
            arr = np.rot90(arr)  # column to row based for numpy, and starting bottom left
            raster_x_size, raster_y_size = 3600, 1800
            srs = osr.SpatialReference()
            srs.ImportFromEPSG(4326)
            rp = RasterParameters(raster_x_size, raster_y_size, [-180, 0.1, 0, 90, 0, -0.1], srs, 1, -9999.9,
                                  gdal.GDT_Float32, driver_short_name='MEM')
            rp.set_coordinate_system(srs=srs.ExportToWkt())
            output_dataset = self.create_dataset(rp, arr)
            result.append([output_raster, output_dataset])
        for r in result:
            yield r

    # def get_rasters(self, product_filename):
    #     """Return raster as precipitation depth (mm)
    #
    #     From IMERG.doc
    #     The *grid* on which each field of values is presented is a 0.1degx0.1deg lat./lon. (Cylindrical Equal Distance)
    #     global array of points. It is size 3600x1800, with X (longitude) incrementing most rapidly West to East from
    #     the Dateline, and then Y (latitude) incrementing South to North from the southern edge as detailed in the
    #     metadata. Tenth-degree latitude and longitude values are at grid edges:
    #
    #     First point center (89.95degS,179.95degW)
    #     Second point center (89.95degS,179.85degW)
    #     Last point center (89.95degN,179.95degE)
    #
    #     The reference datum is WGS84.
    #     Note that the Day-1 IMERG precipitation estimates are filled with "missing" values outside the
    #     latitude band 60degN-S, while some of the additional data fields have values at the higher latitudes.
    #
    #     :param product_filename: full path name of the product file
    #     :return: list of tuples (output_filename, output_dataset)
    #             output_filename is obtained from the product_filename by substituting product_dir by output_raster_dir
    #             output_dataset in in the memory (driver='MEM')
    #     """
    #     output_raster = os.path.normpath(product_filename[:-6] + '.tif')
    #     output_raster = output_raster.replace(self.product_dir, self.output_raster_dir)
    #     result = []
    #     if self.overwrite or not os.path.isfile(output_raster):
    #         hdf5_dataset = gdal.Open(product_filename, gdal.GA_ReadOnly)
    #         subdatasets = hdf5_dataset.GetSubDatasets()
    #         del hdf5_dataset
    #         subdataset_name = subdatasets[self.subdataset_number][0]
    #         assert subdataset_name[-16:] == 'precipitationCal'
    #         try:
    #             prec_dataset = gdal.Open(subdataset_name, gdal.GA_ReadOnly)
    #         except RuntimeError, e:
    #             print subdatasets
    #             print subdataset_name
    #             raise e
    #         arr = prec_dataset.ReadAsArray()
    #         arr = np.rot90(arr)  # column to row based for numpy, and starting bottom left
    #         arr = self.rate_to_depth(arr, product_filename)
    #         raster_parameters = get_parameters(prec_dataset)
    #         raster_parameters.RasterXSize, raster_parameters.RasterYSize = \
    #             raster_parameters.RasterYSize, raster_parameters.RasterXSize
    #         raster_parameters.driverShortName = 'MEM'
    #         raster_parameters.geo_trans = [-180, 0.1, 0, 90, 0, -0.1]
    #         raster_parameters.set_nodata(-9999.9)
    #         srs = osr.SpatialReference()
    #         srs.ImportFromEPSG(4326)
    #         raster_parameters.set_coordinate_system(srs=srs.ExportToWkt())
    #         output_dataset = self.create_dataset(raster_parameters, arr)
    #         result.append([output_raster, output_dataset])
    #     for r in result:
    #         yield r
    #


class GPMImerg3BHHRRasterize(GPMImerg3BRasterize):
    """

    """

    def __init__(self, product_dir, output_raster_dir, suffix, **kwargs):
        super(GPMImerg3BHHRRasterize, self).__init__(5, product_dir, output_raster_dir, suffix, **kwargs)


class GPMImerg3BMORasterize(GPMImerg3BRasterize):
    """

    """

    def __init__(self, product_dir, output_raster_dir, suffix, **kwargs):
        super(GPMImerg3BMORasterize, self).__init__(1, product_dir, output_raster_dir, suffix, **kwargs)

    def rate_to_depth(self, arr, product_filename):
        # 3B-MO.MS.MRG.3IMERG.20140312-S000000-E235959.03.V04A.HDF5
        dt = datetime.datetime.strptime(product_filename.split('3IMERG.')[-1][:8], '%Y%m%d')
        return arr * monthrange(dt.year, dt.month)[1] * 24


class GPMImerg3BHHRearlyRasterize(GPMImerg3BHHRRasterize):

    def __init__(self, product_dir, output_raster_dir, **kwargs):
        super(GPMImerg3BHHRearlyRasterize, self).__init__(product_dir, output_raster_dir, ['.RT-H5'], **kwargs)


class GPMImerg3BHHRlateRasterize(GPMImerg3BHHRRasterize):

    def __init__(self, product_dir, output_raster_dir, **kwargs):
        super(GPMImerg3BHHRlateRasterize, self).__init__(product_dir, output_raster_dir, ['.RT-H5'], **kwargs)


class GPMImerg3BHHRv05Rasterize(GPMImerg3BHHRRasterize):

    def __init__(self, product_dir, output_raster_dir, **kwargs):
        super(GPMImerg3BHHRv05Rasterize, self).__init__(product_dir, output_raster_dir, '.HDF5', **kwargs)


class GPMImerg3BMOv05Rasterize(GPMImerg3BMORasterize):

    def __init__(self, product_dir, output_raster_dir, **kwargs):
        super(GPMImerg3BMOv05Rasterize, self).__init__(product_dir, output_raster_dir, '.HDF5', **kwargs)


# =============================================================================
# GIS
# =============================================================================
class GPMImergGISRasterize(Rasterizer):

    def __init__(self, product_dir, output_raster_dir, **kwargs):
        super(GPMImergGISRasterize, self).__init__(product_dir, output_raster_dir, '.tif', **kwargs)

    def get_rasters(self, product_filename):
        for output, raster_in in super(GPMImergGISRasterize, self).get_rasters(product_filename):
            raster_in.set_nodata(-9999.9)
            srs = osr.SpatialReference()
            srs.ImportFromEPSG(4035)  # Authalic WGS84
            raster_in.set_projection(srs.ExportToWkt())
            yield output, raster_in


class GPMImergGIS3BHHRv05Rasterize(GPMImergGISRasterize):

    def __init__(self, product_dir, output_raster_dir, **kwargs):
        super(GPMImergGIS3BHHRv05Rasterize, self).__init__(product_dir, output_raster_dir, **kwargs)


class GPMImergGIS3BHHRv04Rasterize(GPMImergGISRasterize):

    def __init__(self, product_dir, output_raster_dir, **kwargs):
        super(GPMImergGIS3BHHRv04Rasterize, self).__init__(product_dir, output_raster_dir, **kwargs)


class GPMImergGIS3BMOv05Rasterize(GPMImerg3BRasterize):

    def __init__(self, product_dir, output_raster_dir, **kwargs):
        super(GPMImergGIS3BMOv05Rasterize, self).__init__(product_dir, output_raster_dir, '.tif', **kwargs)


class GPMImergGIS3BDailyV05Rasterize(GPMImergGISRasterize):

    def __init__(self, product_dir, output_raster_dir, **kwargs):
        super(GPMImergGIS3BDailyV05Rasterize, self).__init__(product_dir, output_raster_dir, **kwargs)


class GPMImergGIS3BDailyV04Rasterize(GPMImergGISRasterize):

    def __init__(self, product_dir, output_raster_dir, **kwargs):
        super(GPMImergGIS3BDailyV04Rasterize, self).__init__(product_dir, output_raster_dir, **kwargs)


