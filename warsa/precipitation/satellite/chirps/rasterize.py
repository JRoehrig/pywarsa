from warsa.precipitation.satellite.rasterize import Rasterizer


class Chirps20GlobalDaily05TifRasterize(Rasterizer):

    def __init__(self, product_dir, output_raster_dir, clip_layer=None, resample_sizes=None,
                 overwrite=False, verbose=False):
        super(Chirps20GlobalDaily05TifRasterize, self).__init__(product_dir, output_raster_dir, '.tif.gz',
                                                                clip_layer, resample_sizes, overwrite, verbose)

    def get_rasters(self, product_filename):
        output = super(Chirps20GlobalDaily05TifRasterize, self).get_rasters(product_filename).next()
        output[1].GetRasterBand(1).SetNoDataValue(-9999.0)
        yield output


class Chirps20GlobalDaily25TifRasterize(Rasterizer):

    def __init__(self, product_dir, output_raster_dir, clip_layer=None, resample_sizes=None,
                 overwrite=False, verbose=False):
        super(Chirps20GlobalDaily25TifRasterize, self).__init__(product_dir, output_raster_dir, '.tif.gz',
                                                                clip_layer, resample_sizes, overwrite, verbose)

    def get_rasters(self, product_filename):
        raster = super(Chirps20GlobalDaily25TifRasterize, self).get_rasters(product_filename).next()
        raster[1].set_nodata(-9999.0)
        yield raster


