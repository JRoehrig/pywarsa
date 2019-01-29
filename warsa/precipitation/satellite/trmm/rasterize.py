import os
import gzip
import tempfile
import numpy as np
from osgeo import gdal, osr
from netCDF4 import Dataset
from girs.srs import srs_from_epsg
from girs.rast.raster import RasterWriter
from girs.rast.parameter import RasterParameters, get_parameters
from warsa.precipitation.satellite.rasterize import Rasterizer


class TRMMnascom3B42RTv7x3hRasterize(Rasterizer):

    def __init__(self, product_dir, output_raster_dir, **kwargs):

        super(TRMMnascom3B42RTv7x3hRasterize, self).__init__(product_dir, output_raster_dir, suffix='.nc4', **kwargs)

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

    def __init__(self, product_dir, output_raster_dir, **kwargs):

        super(TRMMnascom3B42V7x3hRasterize, self).__init__(product_dir, output_raster_dir, '.HDF', **kwargs)

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

    def __init__(self, product_dir, output_raster_dir, **kwargs):

        super(TRMMnascom3B42V7xDailyRasterize, self).__init__(product_dir, output_raster_dir, '.HDF', **kwargs)

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
    def __init__(self, product_dir, output_raster_dir, **kwargs):
        super(TRMMopen3B4xRTv7x3hRasterize, self).__init__(product_dir, output_raster_dir, '.gz', **kwargs)

    def get_rasters(self, product_filename):
        """

        :param product_filename:
        :return:
        """
        """
            algorithm_ID=3B42RT 
            algorithm_version=07.00 
            granule_ID=3B42RT.2000030100.7R2.bin 
            header_byte_length=2880 
            file_byte_length=(char2880)_header+(int2)x1440x480x2_data+(int1)x1440x480_data+(int2)x1440x480_data 
            nominal_YYYYMMDD=20000301 
            nominal_HHMMSS=000000 
            begin_YYYYMMDD=20000229 
            begin_HHMMSS=223000 
            end_YYYYMMDD=20000301 
            end_HHMMSS=013000 
            creation_date=20121109 
            west_boundary=0E 
            east_boundary=360E 
            north_boundary=60N 
            south_boundary=60S 
            origin=northwest 
            number_of_latitude_bins=480 
            number_of_longitude_bins=1440 
            grid=0.25x0.25_deg_lat/lon 
            first_box_center=59.875N,0.125E 
            second_box_center=59.875N,0.375E 
            last_box_center=59.875S,359.875E 
            number_of_variables=4 
            variable_name=precipitation,precipitation_error,source,uncal_precipitation 
            variable_units=mm/hr,mm/hr,source_number,mm/hr 
            variable_scale=100,100,1,100 
            variable_type=signed_integer2,signed_integer2,signed_integer1,signed_integer2 
            byte_order=big_endian 
            flag_value=-31999 
            flag_name=insufficient_observations 
            contact_name=TSDIS_Helpdesk 
            contact_address=NASA/GSFC_Code_610.2_Greenbelt_MD_20771_USA 
            contact_telephone=301-614-5184 
            contact_facsimile=301-614-5575 
            contact_email=helpdesk@pps-mail.nascom.nasa.gov 
            run_latency=LAST
        """
        nx, ny = 1440, 480
        x_res, y_res = 0.25, 0.25
        nodata = -999.0
        output_raster = '.'.join(os.path.basename(product_filename).split('.')[:-2]) + '.tif'
        f = output_raster.split('.')[1]
        output_raster = os.path.join(self.output_raster_dir, f[:4], f[4:6], output_raster)
        results = []
        if self.overwrite or not os.path.isfile(output_raster):
            gf = gzip.GzipFile(product_filename, 'rb')
            try:
                d = gf.read()
                gf.close()
                arr = np.frombuffer(d, dtype='>i2')
                arr = arr[1440:692640]  # arr[2880/2, 1440 + (1440 * 480)]
                arr = arr.astype(np.float32)
                arr = arr * 0.03  # 3 hourly data scaled by 100 to depth (mm) in the time interval
                # Set high-latitude HQ+VAR precipitation values and highly ambiguous HQ values to nodata.
                arr[arr < 0] = nodata
                arr = arr.reshape((ny, nx))
                arr = np.append(arr[:, nx/2:], arr[:, :nx/2], axis=1)
                tran = [-180.0, x_res, 0, 60.0, 0, -y_res]
                srs = osr.SpatialReference()
                srs.ImportFromEPSG(4326)  # wgs1984
                rp = RasterParameters(nx, ny, tran, srs.ExportToWkt(), 1, nodata, gdal.GDT_Float32, 'mem')
                ds_out = self.create_dataset(rp, arr)
                results.append([output_raster, ds_out])
            except Exception, e:
                print e.message, product_filename

        for r in results:
            yield r


class TRMMopen3B40RTv7x3hRasterize(TRMMopen3B4xRTv7x3hRasterize):
    def __init__(self, product_dir, output_raster_dir, **kwargs):
        super(TRMMopen3B40RTv7x3hRasterize, self).__init__(product_dir, output_raster_dir, **kwargs)


class TRMMopen3B41RTv7x3hRasterize(TRMMopen3B4xRTv7x3hRasterize):
    def __init__(self, product_dir, output_raster_dir, **kwargs):
        super(TRMMopen3B41RTv7x3hRasterize, self).__init__(product_dir, output_raster_dir, **kwargs)


class TRMMopen3B42RTv7x3hRasterize(TRMMopen3B4xRTv7x3hRasterize):
    def __init__(self, product_dir, output_raster_dir, **kwargs):
        super(TRMMopen3B42RTv7x3hRasterize, self).__init__(product_dir, output_raster_dir, **kwargs)


class TRMMopen3B42RTv7x3hGISRasterize(Rasterizer):
    def __init__(self, product_dir, output_raster_dir, **kwargs):
        super(TRMMopen3B42RTv7x3hGISRasterize, self).__init__(product_dir, output_raster_dir, '.tif', **kwargs)

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
    def __init__(self, product_dir, output_raster_dir, **kwargs):
        super(TRMMopen3B42v7x3hRasterize, self).__init__(product_dir, output_raster_dir, suffix='.HDF.gz', **kwargs)

    def get_rasters(self, product_filename):
        # nx, ny = 1440, 400
        results = []
        output_raster = product_filename[:-4] + '.tif'
        output_raster = output_raster.replace(self.product_dir, self.output_raster_dir)
        if self.overwrite or not os.path.isfile(output_raster):
            tmp_file = tempfile.NamedTemporaryFile(prefix='TRMMopen3B42v7x3hRasterize', suffix='.HDF', delete=False)
            gf = gzip.GzipFile(product_filename, 'rb')
            tmp_file.write(gf.read())
            gf.close()
            tmp_file.close()
            ds0 = gdal.Open(tmp_file.name)
            ds = gdal.Open(ds0.GetSubDatasets()[0][0])
            rp = get_parameters(ds)
            arr = ds.GetRasterBand(1).ReadAsArray()
            arr = np.rot90(arr)
            del ds
            del ds0
            rp.RasterXSize, rp.RasterYSize = rp.RasterYSize, rp.RasterXSize
            rp.geo_trans = [-180.0,  0.25, 0, 50.0, 0, - 0.25]
            rp.set_driver_short_name('mem')
            rp.set_nodata(-9999.9)
            rp.set_coordinate_system(srs_from_epsg(4326).ExportToWkt())
            rst = RasterWriter(rp)
            rst.set_array(array=arr)
            results.append([output_raster, rst])
            os.unlink(tmp_file.name)
        for r in results:
            yield r


class TRMMopen3B42v7x3hGISRasterize(Rasterizer):
    def __init__(self, product_dir, output_raster_dir, **kwargs):
        super(TRMMopen3B42v7x3hGISRasterize, self).__init__(product_dir, output_raster_dir, '.tif', **kwargs)


