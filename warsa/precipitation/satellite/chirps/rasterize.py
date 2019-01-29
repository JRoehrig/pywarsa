from warsa.precipitation.satellite.rasterize import Rasterizer


class Chirps20GlobalDaily05TifRasterize(Rasterizer):

    def __init__(self, product_dir, output_raster_dir, **kwargs):
        super(Chirps20GlobalDaily05TifRasterize, self).__init__(product_dir, output_raster_dir, '.tif.gz', **kwargs)

    def get_rasters(self, product_filename):
        for raster in super(Chirps20GlobalDaily05TifRasterize, self).get_rasters(product_filename):
            r = raster[1].copy(name='', driver_short_name='MEM')  # a gz file can not be changed: make a copy
            r.set_nodata(-9999.0)
            raster[1] = r
            yield raster


class Chirps20GlobalDaily25TifRasterize(Rasterizer):

    def __init__(self, product_dir, output_raster_dir, **kwargs):
        super(Chirps20GlobalDaily25TifRasterize, self).__init__(product_dir, output_raster_dir, '.tif.gz', **kwargs)

    def get_rasters(self, product_filename):
        for raster in super(Chirps20GlobalDaily25TifRasterize, self).get_rasters(product_filename):
            r = raster[1].copy(name='', driver_short_name='MEM')  # a gz file can not be changed: make a copy
            r.set_nodata(-9999.0)
            raster[1] = r
            yield raster


class Chirps20GlobalMonthly05TifRasterize(Rasterizer):

    def __init__(self, product_dir, output_raster_dir, **kwargs):
        super(Chirps20GlobalMonthly05TifRasterize, self).__init__(product_dir, output_raster_dir, '.tif.gz', **kwargs)

    def get_rasters(self, product_filename):
        for raster in super(Chirps20GlobalMonthly05TifRasterize, self).get_rasters(product_filename):
            r = raster[1].copy(name='', driver_short_name='MEM')  # a gz file can not be changed: make a copy
            r.set_nodata(-9999.0)
            raster[1] = r
            yield raster

