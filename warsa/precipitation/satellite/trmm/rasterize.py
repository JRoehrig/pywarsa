import gzip
import os
import tempfile
import numpy as np
from girs.rast.parameter import RasterParameters, get_parameters
from netCDF4 import Dataset
from osgeo import gdal, osr
from warsa.precipitation.satellite.rasterize import Rasterizer


class TRMMnascom3B42RTv7x3hRasterize(Rasterizer):

    def __init__(self, product_dir, output_raster_dir, clip_layer=None, resample_sizes=None,
                 overwrite=False, verbose=False):

        super(TRMMnascom3B42RTv7x3hRasterize, self).__init__(product_dir, output_raster_dir, '.nc4', clip_layer,
                                                             resample_sizes, overwrite,  verbose)

    def get_rasters(self, product_filename):
        output_raster = product_filename[:-4] + '.tif'
        output_raster = output_raster.replace(self.product_dir, self.output_raster_dir)
        result = []
        if self.overwrite or not os.path.isfile(output_raster):
            rp_sds = get_parameters(gdal.Open(gdal.Open(product_filename, gdal.GA_ReadOnly).GetSubDatasets()[0][0]))
            rp_sds.driverShortName = 'MEM'
            arr = np.array(Dataset(product_filename, 'r', format="NETCDF4").variables[u'precipitation'] )
            arr[arr < 0] = rp_sds.nodata
            ds_out = self.create_dataset(rp_sds, arr, 'mem')
            result.append([output_raster, ds_out])
        for r in result:
            yield r


class TRMMnascom3B42V7x3hRasterize(Rasterizer):

    def __init__(self, product_dir, output_raster_dir, clip_layer=None, resample_sizes=None,
                 overwrite=False, verbose=False):

        super(TRMMnascom3B42V7x3hRasterize, self).__init__(product_dir, output_raster_dir, '.HDF', clip_layer,
                                                             resample_sizes, overwrite,  verbose)

    def get_rasters(self, product_filename):
        # nx, ny = 1440, 400

        output_raster = product_filename[:-4] + '.tif'
        output_raster = output_raster.replace(self.product_dir, self.output_raster_dir)
        results = []
        if self.overwrite or not os.path.isfile(output_raster):
            ds = gdal.Open(gdal.Open(product_filename).GetSubDatasets()[0][0])
            arr = ds.GetRasterBand(1).ReadAsArray()
            arr = np.rot90(arr)
            rp = get_parameters(ds)
            rp.RasterXSize, rp.RasterYSize = rp.RasterYSize, rp.RasterXSize
            rp.geo_trans = [-180.0,  0.25, 0, 50.0, 0, - 0.25]
            rp.set_driver_short_name('mem')
            rp.set_nodata(-9999.9)
            ds_out = self.create_dataset(rp, arr, 'mem')
            results.append([output_raster, ds_out])
            # arr = arr.reshape((ny, nx))
            # arr = np.append(arr[:, nx/2:], arr[:, :nx/2], axis=1)
            # arr = np.flipud(arr)
            # # for intensity: arr = arr / 3.0
            # tran = [-180.0, x_res, 0, 50.0, 0, -y_res]
            # srs = osr.SpatialReference()
            # # srs.ImportFromEPSG(4035)  # Authalic WGS84 like in the arc2 tif version
            # srs.ImportFromEPSG(4326)  # wgs1984
            # rp = RasterParameters(nx, ny, tran, srs.ExportToWkt(), 1, nodata, gdal.GDT_Float32)
        for r in results:
            yield r


class TRMMnascom3B42V7xDailyRasterize(Rasterizer):

    def __init__(self, product_dir, output_raster_dir, clip_layer=None, resample_sizes=None,
                 overwrite=False, verbose=False):

        super(TRMMnascom3B42V7xDailyRasterize, self).__init__(product_dir, output_raster_dir, '.HDF', clip_layer,
                                                             resample_sizes, overwrite,  verbose)

    def get_rasters(self, product_filename):
        # nx, ny = 1440, 400

        output_raster = product_filename[:-4] + '.tif'
        output_raster = output_raster.replace(self.product_dir, self.output_raster_dir)
        results = []
        if self.overwrite or not os.path.isfile(output_raster):
            ds = gdal.Open(gdal.Open(product_filename).GetSubDatasets()[0][0])
            arr = ds.GetRasterBand(1).ReadAsArray()
            arr = np.rot90(arr)
            rp = get_parameters(ds)
            rp.RasterXSize, rp.RasterYSize = rp.RasterYSize, rp.RasterXSize
            rp.geo_trans = [-180.0,  0.25, 0, 50.0, 0, - 0.25]
            rp.set_driver_short_name('mem')
            rp.set_nodata(-9999.9)
            ds_out = self.create_dataset(rp, arr, 'mem')
            results.append([output_raster, ds_out])
        for r in results:
            yield r


# =============================================================================
# TRMM trmmopen
# =============================================================================
class TRMMopen3B4xRTv7x3hRasterize(Rasterizer):
    def __init__(self, product_dir, output_raster_dir, clip_layer, resample_sizes, overwrite, verbose):
        super(TRMMopen3B4xRTv7x3hRasterize, self).__init__(product_dir, output_raster_dir, '.gz', clip_layer,
                                                           resample_sizes, overwrite,  verbose)

    def get_rasters(self, product_filename):
        nx, ny = 1440, 480
        x_res, y_res = 0.25, 0.25
        nodata = -999.0
        output_raster = '.'.join(os.path.basename(product_filename).split('.')[:-2]) + '.tif'
        output_raster = os.path.join(self.output_raster_dir, output_raster)
        results = []
        if self.overwrite or not os.path.isfile(output_raster):
            gf = gzip.GzipFile(product_filename, 'rb')
            try:
                d = gf.read()
                gf.close()
                arr = np.frombuffer(d, dtype='>h')
                arr = arr[1440:692640]  # arr[2880/2, 1440 + (1440 * 480)]
                arr = arr.astype(np.float32)
                # arr = arr * 0.03  # to store in 0.01 mm/h
                # Set high-latitude HQ+VAR precipitation values and highly ambiguous HQ values to nodata.
                arr[arr < 0] = nodata
                arr = arr.reshape((ny, nx))
                arr = np.append(arr[:, nx/2:], arr[:, :nx/2], axis=1)
                tran = [-180.0, x_res, 0, 60.0, 0, -y_res]
                srs = osr.SpatialReference()
                # srs.ImportFromEPSG(4035)  # Authalic WGS84 like in the arc2 tif version
                srs.ImportFromEPSG(4326)  # wgs1984
                rp = RasterParameters(nx, ny, tran, srs.ExportToWkt(), 1, nodata, gdal.GDT_Float32, 'mem')
                ds_out = self.create_dataset(rp, arr, 'mem')
                results.append([output_raster, ds_out])
            except Exception, e:
                print e.message, product_filename

        for r in results:
            yield r


class TRMMopen3B40RTv7x3hRasterize(TRMMopen3B4xRTv7x3hRasterize):
    def __init__(self, product_dir, output_raster_dir, clip_layer=None, resample_sizes=None,
                 overwrite=False, verbose=False):
        super(TRMMopen3B40RTv7x3hRasterize, self).__init__(product_dir, output_raster_dir, clip_layer,
                                                           resample_sizes, overwrite,  verbose)


class TRMMopen3B41RTv7x3hRasterize(TRMMopen3B4xRTv7x3hRasterize):
    def __init__(self, product_dir, output_raster_dir, clip_layer=None, resample_sizes=None,
                 overwrite=False, verbose=False):
        super(TRMMopen3B41RTv7x3hRasterize, self).__init__(product_dir, output_raster_dir, clip_layer,
                                                           resample_sizes, overwrite,  verbose)


class TRMMopen3B42RTv7x3hRasterize(TRMMopen3B4xRTv7x3hRasterize):
    def __init__(self, product_dir, output_raster_dir, clip_layer=None, resample_sizes=None,
                 overwrite=False, verbose=False):
        super(TRMMopen3B42RTv7x3hRasterize, self).__init__(product_dir, output_raster_dir, clip_layer,
                                                           resample_sizes, overwrite,  verbose)


class TRMMopen3B42RTv7x3hGISRasterize(Rasterizer):
    def __init__(self, product_dir, output_raster_dir, clip_layer=None, resample_sizes=None,
                 overwrite=False, verbose=False):
        super(TRMMopen3B42RTv7x3hGISRasterize, self).__init__(product_dir, output_raster_dir, '.tif', clip_layer,
                                                              resample_sizes, overwrite,  verbose)

    def get_rasters(self, product_filename):
        nodata = 999.0
        bn = os.path.basename(product_filename)
        output_raster = os.path.join(self.output_raster_dir, bn)
        results = []
        if self.overwrite or not os.path.isfile(output_raster):
            ds, _ = self.open_raster(product_filename)
            rp = get_parameters(ds)
            rp.set_nodata(nodata)
            rp.set_driver_short_name('mem')
            arr = ds.GetRasterBand(1).ReadAsArray() * 0.01
            # in mm: arr *= 3  # number of hours
            arr[arr < 0.0] = np.NaN
            ds_out = self.create_dataset(rp, arr, 'mem')
            results.append([output_raster, ds_out])
        for r in results:
            yield r


class TRMMopen3B42v7x3hRasterize(Rasterizer):
    def __init__(self, product_dir, output_raster_dir, clip_layer=None, resample_sizes=None,
                 overwrite=False, verbose=False):
        super(TRMMopen3B42v7x3hRasterize, self).__init__(product_dir, output_raster_dir, '.HDF.gz', clip_layer,
                                                         resample_sizes, overwrite,  verbose)
        self.tmp_filename = None

    def rasterize_file(self, input_filename):
        try:
            result = super(TRMMopen3B42v7x3hRasterize, self).rasterize_file(input_filename)
        finally:
            if self.tmp_filename:
                os.unlink(self.tmp_filename)
        return result

    def get_rasters(self, product_filename):
        # nx, ny = 1440, 400
        results = []
        output_raster = product_filename[:-4] + '.tif'
        output_raster = output_raster.replace(self.product_dir, self.output_raster_dir)
        tmp_file = tempfile.NamedTemporaryFile(prefix='TRMMopen3B42v7x3hRasterize', suffix='.HDF', delete=False)
        self.tmp_filename = tmp_file.name
        gf = gzip.GzipFile(product_filename, 'rb')
        tmp_file.write(gf.read())
        gf.close()
        tmp_file.close()
        if self.overwrite or not os.path.isfile(output_raster):
            ds0 = gdal.Open(self.tmp_filename)
            ds = gdal.Open(ds0.GetSubDatasets()[0][0])
            arr = ds.GetRasterBand(1).ReadAsArray()
            arr = np.rot90(arr)
            rp = get_parameters(ds)
            rp.RasterXSize, rp.RasterYSize = rp.RasterYSize, rp.RasterXSize
            rp.geo_trans = [-180.0,  0.25, 0, 50.0, 0, - 0.25]
            rp.set_driver_short_name('mem')
            rp.set_nodata(-9999.9)
            ds_out = self.create_dataset(rp, arr, 'mem')
            results.append([output_raster, ds_out])
        for r in results:
            yield r


class TRMMopen3B42v7x3hGISRasterize(Rasterizer):
    def __init__(self, product_dir, output_raster_dir, clip_layer=None, resample_sizes=None,
                 overwrite=False, verbose=False):
        super(TRMMopen3B42v7x3hGISRasterize, self).__init__(product_dir, output_raster_dir, '.tif', clip_layer,
                                                            resample_sizes, overwrite,  verbose)


