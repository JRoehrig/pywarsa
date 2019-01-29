import bz2
import os
import tarfile
import numpy as np
from girs.rast.parameter import RasterParameters
from girs.rast.raster import RasterWriter
from osgeo import gdal, osr
from warsa.precipitation.satellite.rasterize import Rasterizer


class CMorphRasterize(Rasterizer):

    @staticmethod
    def rasterize_block(arr, nx, ny, x_res, y_res):
        nodata = -999.0
        arr = np.flipud(arr.reshape((ny, nx)))  # bottom up
        arr = np.append(arr[:, nx/2:], arr[:, :nx/2], axis=1)
        arr[arr < 0] = nodata
        arr[arr > 998] = nodata
        tran = [-180.0, x_res, 0, 60.0, 0, -y_res]
        srs = osr.SpatialReference()
        # srs.ImportFromEPSG(4326)  # EPSG:4326
        srs.ImportFromEPSG(4035)  # Authalic WGS84
        raster_parameters = RasterParameters(nx, ny, tran, srs.ExportToWkt(), 1, [nodata], gdal.GDT_Float32,
                                             driver_short_name='MEM')
        raster_out = RasterWriter(raster_parameters)
        raster_out.set_array(arr, 1)
        return raster_out

    def get_raster_datasets_3hly(self, product_filename):
        nx, ny = 1440, 480
        x_res, y_res = 0.25, 0.25  # = 360/1440, 120/480
        raster_filename = os.path.splitext(os.path.relpath(product_filename, self.product_dir))[0]
        raster_filename = os.path.join(self.output_raster_dir, raster_filename)
        raster_file_names = [None]*8
        for i, hour in enumerate(range(0, 24, 3)):
            rfn = raster_filename + str(hour).zfill(2) + '.tif'
            if self.overwrite or not os.path.isfile(rfn):
                raster_file_names[i] = os.path.normpath(rfn)
        results = []
        if raster_file_names.count(None) < 8:
            # rain depth. For rain intensity arr = arr / 3.0
            arr = np.frombuffer(self.read_compressed_file(product_filename), dtype='<f4')
            results = [[raster_file_names[i], self.rasterize_block(arr[i*691200:(i+1)*691200], nx, ny, x_res, y_res)]
                       for i, rfn in enumerate(raster_file_names) if rfn]
        for r in results:
            yield r

    def get_raster_datasets_daily(self, product_filename):
        nx, ny = 1440, 480
        x_res, y_res = 0.25, 0.25  # = 360/1440, 120/480
        results = []
        raster_filename = os.path.splitext(os.path.relpath(product_filename, self.product_dir))[0] + '.tif'
        raster_filename = os.path.join(self.output_raster_dir, raster_filename)
        if self.overwrite or not os.path.isfile(raster_filename):
            arr = np.frombuffer(self.read_compressed_file(product_filename), dtype='<f4')
            # rain depth. For rain intensity arr = arr / 24.0
            results.append([raster_filename, self.rasterize_block(arr, nx, ny, x_res, y_res)])
        for r in results:
            yield r


class CMorphV0x8km30minRasterize(CMorphRasterize):

    def __init__(self, product_dir, output_raster_dir, **kwargs):
        super(CMorphV0x8km30minRasterize, self).__init__(product_dir, output_raster_dir, ('.gz', '.bz2'), **kwargs)

    def get_rasters(self, product_filename):

        nx, ny = 4948, 1649
        x_res = 0.07275666936135812449474535165724  # = 360/4948 8km
        y_res = 0.07277137659187386294724075197089  # = 120/1649 (ca. 8km)

        raster_filename = os.path.splitext(os.path.relpath(product_filename, self.product_dir))[0]
        raster_filename = os.path.join(self.output_raster_dir, raster_filename)
        raster_filename0 = raster_filename + '00.tif'
        raster_filename1 = raster_filename + '30.tif'
        if not self.overwrite and os.path.isfile(raster_filename0):
            raster_filename0 = None
        if not self.overwrite and os.path.isfile(raster_filename1):
            raster_filename1 = None

        result = []
        if raster_filename0 or raster_filename1:
            # rain intensity in mm/h. For rain depth arr = arr * 0.5
            arr = np.frombuffer(self.read_compressed_file(product_filename), dtype='<f4')
            if raster_filename0:
                result.append((raster_filename0, self.rasterize_block(arr[0:8159252], nx, ny, x_res, y_res)))
            if raster_filename1:
                result.append((raster_filename1, self.rasterize_block(arr[8159252:16318504], nx, ny, x_res, y_res)))
        for r in result:
            yield r


class CMorphV0x025deg3hlyRasterize(CMorphRasterize):

    def __init__(self, product_dir, output_raster_dir, **kwargs):
        super(CMorphV0x025deg3hlyRasterize, self).__init__(product_dir, output_raster_dir, ('.gz', '.bz2'), **kwargs)

    def get_rasters(self, product_filename):
        return self.get_raster_datasets_3hly(product_filename)


class CMorphV0x025degDailyRasterize(CMorphRasterize):

    def __init__(self, product_dir, output_raster_dir, **kwargs):
        super(CMorphV0x025degDailyRasterize, self).__init__(product_dir, output_raster_dir, ('.gz', '.bz2'), **kwargs)

    def get_rasters(self, product_filename):
        return self.get_raster_datasets_daily(product_filename)


class CMorphV1x8km30minRasterize(CMorphRasterize):

    def __init__(self, product_dir, output_raster_dir, **kwargs):
        super(CMorphV1x8km30minRasterize, self).__init__(product_dir, output_raster_dir, '.tar', **kwargs)

    def get_rasters(self, product_filename):

        nx, ny = 4948, 1649
        x_res = 0.07275666936135812449474535165724  # = 360/4948 8km
        y_res = 0.07277137659187386294724075197089  # = 120/1649 (ca. 8km)

        with tarfile.open(product_filename) as tar:
            tar_members = [member.name for member in tar.getmembers() if member.isfile()]
            for tar_member in tar_members:
                suffix = os.path.splitext(tar_member)[1]
                tm = os.path.join(self.output_raster_dir, tar_member)
                raster_filename0 = tm.replace(suffix, '00.tif')
                raster_filename1 = tm.replace(suffix, '30.tif')
                if not self.overwrite and os.path.isfile(raster_filename0):
                    raster_filename0 = None
                if not self.overwrite and os.path.isfile(raster_filename1):
                    raster_filename1 = None
                if not (raster_filename0 or raster_filename1):
                    continue
                # rain depth. For rain intensity arr = arr / 0.5
                arr = np.frombuffer(bz2.decompress(tar.extractfile(tar_member).read()), dtype='<f4')
                result = []
                if raster_filename0:
                    result.append((raster_filename0, self.rasterize_block(arr[0:8159252], nx, ny, x_res, y_res)))
                if raster_filename1:
                    result.append((raster_filename1, self.rasterize_block(arr[8159252:16318504], nx, ny, x_res, y_res)))
                for r in result:
                    yield r


class CMorphV1x025deg3hlyRasterize(CMorphRasterize):

    def __init__(self, product_dir, output_raster_dir, **kwargs):
        super(CMorphV1x025deg3hlyRasterize, self).__init__(product_dir, output_raster_dir, ('.gz', '.bz2'), **kwargs)

    def get_rasters(self, product_filename):
        return self.get_raster_datasets_3hly(product_filename)


class CMorphV1x025degDailyRasterize(CMorphRasterize):

    def __init__(self, product_dir, output_raster_dir, **kwargs):
        super(CMorphV1x025degDailyRasterize, self).__init__(product_dir, output_raster_dir, ('.gz', '.bz2'), **kwargs)

    def get_rasters(self, product_filename):
        return self.get_raster_datasets_daily(product_filename)


# def read_compressed_file(source):
#     s = os.path.splitext(source)
#     if '.bz2' in s[-1]:
#         with open(source, 'rb') as f:
#             return bz2.decompress(f.read())
#     elif '.gz' in s[-1]:
#         gf = gzip.GzipFile(source, 'rb')
#         d = gf.read()
#         gf.close()
#         return d
#     elif '.Z' in s[-1]:
#         with open(source) as f:
#             return zlib.decompress(f.read())
#     else:
#         raise Exception('cmorph_rasterize.read_compressed_file: file type unknown ' + str(source))
#
#
# def rasterize_cmorph_block(arr, nx, ny, x_res, y_res, target=None, driver=None):
#     nodata = -999.0
#     arr = arr.reshape((ny, nx))
#     arr = np.flipud(arr)  # bottom up
#     arr = np.append(arr[:, nx/2:], arr[:, :nx/2], axis=1)
#     arr[arr < 0] = nodata
#     arr[arr > 998] = nodata
#     tran = [-180.0, x_res, 0, 60.0, 0, -y_res]
#     proj = srs_from_epsg('EPSG:4326')
#
#     if target:
#         rp = RasterParameters(nx, ny, tran, proj.ExportToWkt(), 1, [nodata], gdal.GDT_Float32, driver_short_name=driver)
#         r = Raster(target, rp)
#     else:
#         rp = RasterParameters(nx, ny, tran, proj.ExportToWkt(), 1, [nodata], gdal.GDT_Float32)
#         r = Raster('mem', rp)
#     r.set_array(arr)
#     r.dataset.FlushCache()
#     return r