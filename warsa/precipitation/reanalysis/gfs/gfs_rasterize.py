# import gdal
#
# from warsa.gis.rasters.raster import Raster
# from warsa.gis.projections.projection import srs_from_epsg
#
#
# r = Raster('C:/Temp/gfs/gfs4/gfs_4_20160322_1200_000.grb2')
#
# nodata = 9999.0
# nx, ny = 720, 361
# x_res, y_res = 0.5, 0.5
# arr = r.get_array(191)
# arr = arr.reshape((ny, nx))
# tran = [-0.25, x_res, 0.0, 90.25, 0.0, -y_res]
# proj = srs_from_epsg('EPSG:4326')
# r = Raster('C:/Temp/test1.tif', nx, ny, 1, gdal.GDT_Float32, tran, proj.ExportToWkt(), nodata=nodata)
# r.set_array(arr)
# r.dataset.FlushCache()
