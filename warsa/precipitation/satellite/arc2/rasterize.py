import gzip
import os
import numpy as np
from osgeo import gdal, osr
from warsa.precipitation.satellite.rasterize import Rasterizer
from girs.rast.parameter import RasterParameters


class ARC2RFE2BinRasterize(Rasterizer):

    def __init__(self, product_dir, nx, ny, x0, y0, output_raster_dir, **kwargs):
        super(ARC2RFE2BinRasterize, self).__init__(product_dir, output_raster_dir, '.gz', **kwargs)
        self.nx = nx
        self.ny = ny
        self.x0 = x0
        self.y0 = y0

    def get_rasters(self, product_filename):
        """Overloads Rasterizer.get_raster_datasets

        from ftp://ftp.cpc.ncep.noaa.gov/fews/AFR_CLIM/ARC2/ARC2_readme.txt:

        Files consist of binary-formated grids at a 0.1 degree resolution and one day's temporal domain is from 0600
        GMT through 0600 GMT. Spatial extent of all estimates spans 20.0W-55.0E and 40.0S-40.0N.

        Daily data files are written in compressed binary data format (big endian) and consist of
        one record (one array) of floating point rainfall estimates in mm.  For decompression, please use
        the gzip (gunzip) utility.  Each daily array equals 751*801 elements, corresponding to 751 pixels
        in the x direction, and 801 pixels in the y direction.  After reshaping to a 0.1 degree grid,
        this will yield a spatial domain of -40S to 40N in latitude, and -20W to 55E in longitude
        encompassing the Africa continent.  Missing data is denoted as -999.0.

        The center of the pixels span 20.0W-55.0E and 40.0S-40.0N. Raster left and top are 20.05W and 40.05N
        respectively. 0.05deg is a half pixel length.
        Uncompressed file size: 2406204 bytes
        float size = 2406204 / (751*801) = 4

        :param product_filename: full path name of th product file
        :return: list of tuples (output_filename, output_dataset)
                output_filename is obtained from the product_filename by substituting product_dir by output_raster_dir
        """

        x_res = y_res = 0.1
        with gzip.GzipFile(product_filename, 'rb') as gf:
            s_data = gf.read()
            assert len(s_data) == self.nx * self.ny * 4
        arr = np.fromstring(s_data, dtype='>f4').astype('<f4')
        arr = np.flipud(arr.reshape((self.ny, self.nx)))
        nodata = -999.0
        arr[arr < 0] = nodata
        geo_trans = [-20.05, x_res, 0, 40.05, 0, -y_res]
        srs = osr.SpatialReference()
        srs.ImportFromEPSG(4035)  # Authalic WGS84 like in the arc2 tif version
        raster_parameters = RasterParameters(self.nx, self.ny, geo_trans, srs.ExportToWkt(), 1, [nodata],
                                             gdal.GDT_Float32, driver_short_name='MEM')
        raster_filename = os.path.join(self.output_raster_dir, os.path.splitext(os.path.basename(product_filename))[0])
        return [(raster_filename + '.tif', self.create_dataset(raster_parameters, arr, 'mem'))]


class ARC2AfricaBinRasterize(ARC2RFE2BinRasterize):
    def __init__(self, product_dir, output_raster_dir, **kwargs):
        super(ARC2AfricaBinRasterize, self).__init__(product_dir, 751, 801, -20.05, 40.05, output_raster_dir, **kwargs)


class ARC2AfricaTifRasterize(Rasterizer):
    def __init__(self, product_dir, output_raster_dir, **kwargs):
        super(ARC2AfricaTifRasterize, self).__init__(product_dir, output_raster_dir, '.tif.zip', **kwargs)


